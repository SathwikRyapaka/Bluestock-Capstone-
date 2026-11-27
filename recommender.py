"""
Mutual Fund Recommendation Engine
Bluestock Fintech Capstone Project - Day 6

Recommends top mutual fund schemes based on investor risk appetite and Sharpe ratio.
Usage:
    python recommender.py --risk Moderate --top 3
    or interactive mode:
    python recommender.py
"""

import sys
import argparse
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
PROCESSED_PERF_PATH = BASE_DIR / "data" / "processed" / "clean_performance.csv"
PROCESSED_FUND_PATH = BASE_DIR / "data" / "processed" / "clean_fund_master.csv"

# Risk appetite mapping to database risk_grade / risk_category
RISK_MAPPING = {
    "low": ["Low"],
    "moderate": ["Moderate", "Moderately High"],
    "high": ["High", "Very High"],
    "very high": ["Very High"]
}

def load_data() -> pd.DataFrame:
    """Loads fund performance and master metadata from SQLite DB or CSV fallback."""
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT 
                p.amfi_code,
                f.scheme_name,
                f.fund_house,
                f.category,
                f.sub_category,
                f.plan,
                p.risk_grade,
                p.sharpe_ratio,
                p.sortino_ratio,
                p.return_1yr_pct,
                p.return_3yr_pct,
                p.return_5yr_pct,
                p.alpha,
                p.beta,
                p.std_dev_ann_pct,
                p.max_drawdown_pct,
                p.aum_crore,
                p.expense_ratio_pct,
                p.morningstar_rating
            FROM fact_performance p
            JOIN dim_fund f ON p.amfi_code = f.amfi_code;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    elif PROCESSED_PERF_PATH.exists() and PROCESSED_FUND_PATH.exists():
        df_perf = pd.read_csv(PROCESSED_PERF_PATH)
        df_fund = pd.read_csv(PROCESSED_FUND_PATH)
        df = pd.merge(df_perf, df_fund[["amfi_code", "sub_category"]], on="amfi_code")
        return df
    else:
        raise FileNotFoundError("Neither bluestock_mf.db nor processed CSVs were found.")

def recommend_funds(risk_appetite: str = "Moderate", top_n: int = 3) -> pd.DataFrame:
    """
    Recommends top N mutual fund schemes for a given risk appetite ordered by Sharpe Ratio.
    
    Args:
        risk_appetite: 'Low', 'Moderate', or 'High'
        top_n: Number of funds to recommend (default: 3)
        
    Returns:
        DataFrame containing recommended schemes with performance and risk metrics
    """
    df = load_data()
    risk_key = risk_appetite.strip().lower()
    
    if risk_key not in RISK_MAPPING:
        valid_options = ", ".join(k.capitalize() for k in RISK_MAPPING.keys())
        raise ValueError(f"Invalid risk appetite '{risk_appetite}'. Expected one of: {valid_options}")
        
    target_grades = RISK_MAPPING[risk_key]
    filtered_df = df[df["risk_grade"].isin(target_grades)].copy()
    
    if filtered_df.empty:
        return filtered_df
        
    # Sort primarily by Sharpe Ratio descending, secondarily by 3-Yr Return
    recommended = filtered_df.sort_values(
        by=["sharpe_ratio", "return_3yr_pct"],
        ascending=[False, False]
    ).head(top_n).reset_index(drop=True)
    
    # Generate tailored investment rationales
    rationales = []
    for _, row in recommended.iterrows():
        if row["category"] == "Debt":
            reason = f"High capital safety with superior Sharpe ({row['sharpe_ratio']:.2f}) and minimal volatility ({row['std_dev_ann_pct']:.1f}%)."
        elif row["sub_category"] in ["Large Cap", "Flexi Cap"]:
            reason = f"Steady wealth compounding: {row['return_3yr_pct']:.1f}% 3-Yr CAGR with alpha of +{row['alpha']:.2f}% over benchmark."
        else:
            reason = f"High growth trajectory ({row['return_3yr_pct']:.1f}% CAGR) with outstanding risk-adjusted return (Sharpe {row['sharpe_ratio']:.2f})."
        rationales.append(reason)
        
    recommended["investment_rationale"] = rationales
    recommended["rank"] = range(1, len(recommended) + 1)
    
    cols_order = [
        "rank", "amfi_code", "scheme_name", "fund_house", "sub_category",
        "risk_grade", "sharpe_ratio", "return_3yr_pct", "expense_ratio_pct",
        "aum_crore", "investment_rationale"
    ]
    return recommended[cols_order]

def display_recommendations(df_rec: pd.DataFrame, risk_appetite: str):
    """Formats and prints the recommendation table to console."""
    print("\n" + "="*110)
    print(f"BLUESTOCK FINTECH — MUTUAL FUND RECOMMENDATION ENGINE")
    print(f"Client Profile: {risk_appetite.upper()} Risk Appetite | Top {len(df_rec)} Optimal Scheme Allocations")
    print("="*110)
    
    if df_rec.empty:
        print("[!] No matching schemes found.")
        return

    for _, row in df_rec.iterrows():
        print(f"\n[Rank #{row['rank']}] {row['scheme_name']}")
        print(f"  • AMC:             {row['fund_house']}")
        print(f"  • AMFI Scheme Code:{row['amfi_code']}")
        print(f"  • Category / Risk: {row['sub_category']} ({row['risk_grade']} Risk)")
        print(f"  • Sharpe Ratio:    {row['sharpe_ratio']:.2f} (Industry benchmark: >1.0 is Good)")
        print(f"  • 3-Year CAGR:     {row['return_3yr_pct']:.2f}%")
        print(f"  • Expense Ratio:   {row['expense_ratio_pct']:.2f}%")
        print(f"  • Fund AUM:        Rs. {row['aum_crore']:,.0f} Crore")
        print(f"  • Rationale:       {row['investment_rationale']}")
        print("-" * 110)
        
    print("="*110 + "\n")

def main():
    """Parses CLI arguments or prompts interactively to display top mutual fund recommendations."""
    parser = argparse.ArgumentParser(description="Bluestock Mutual Fund Recommender")
    parser.add_argument(
        "--risk",
        type=str,
        default=None,
        help="Investor risk appetite: Low, Moderate, High, or 'Very High'"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of recommendations to generate (default: 3)"
    )
    args = parser.parse_args()
    
    risk_input = args.risk
    if not risk_input:
        if sys.stdin.isatty():
            print("\nSelect your Risk Appetite Profile:")
            print("  1. Low (Capital Preservation, Liquid/Debt Funds)")
            print("  2. Moderate (Balanced Growth, Large Cap & Hybrid Funds)")
            print("  3. High (Aggressive Wealth Creation, Mid & Small Cap Funds)")
            choice = input("\nEnter choice [1-3 or Low/Moderate/High] (Default: Moderate): ").strip()
            
            choice_map = {"1": "Low", "2": "Moderate", "3": "High"}
            risk_input = choice_map.get(choice, choice if choice else "Moderate")
        else:
            risk_input = "Moderate"
            
    try:
        recommendations = recommend_funds(risk_input, top_n=args.top)
        display_recommendations(recommendations, risk_input)
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
