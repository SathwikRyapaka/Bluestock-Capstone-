"""
Advanced Analytics & Risk Metrics Generator
Bluestock Fintech Capstone Project - Day 6

Computes:
1. Historical VaR (95%) and CVaR (Expected Shortfall) for all 40 schemes.
2. Rolling 90-day Sharpe ratio time series and high-resolution chart.
3. Investor cohort analysis (2024 vs 2025 cohorts).
4. SIP continuity analysis for 6+ SIP investors with churn flags (>35 day gap).
5. Sector concentration Herfindahl-Hirschman Index (HHI).
Exports: var_cvar_report.csv, rolling_sharpe_chart.png, cohort_analysis.csv, sip_continuity.csv, sector_hhi.csv.
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
REPORTS_DIR = BASE_DIR / "reports"

def get_connection():
    """Opens and returns a SQLite database connection."""
    return sqlite3.connect(DB_PATH)

def compute_var_cvar() -> pd.DataFrame:
    """
    Computes Historical VaR (95%) and CVaR (Expected Shortfall) for all 40 schemes.
    VaR (95%) = 5th percentile of daily return distribution.
    CVaR (95%) = Mean of returns below the 5th percentile threshold.
    """
    logger.info("Computing Historical VaR (95%) and CVaR for all 40 schemes...")
    conn = get_connection()
    
    query = """
        SELECT n.amfi_code, f.scheme_name, f.fund_house, f.category, f.sub_category, f.risk_category, n.nav_date, n.daily_return
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        ORDER BY n.amfi_code, n.nav_date;
    """
    df_nav = pd.read_sql_query(query, conn)
    conn.close()
    
    results = []
    for code, group in df_nav.groupby("amfi_code"):
        # Exclude initial day return (0.0) from diff
        returns = group["daily_return"].iloc[1:].dropna().values
        meta = group.iloc[0]
        
        var_95 = np.percentile(returns, 5)
        tail_losses = returns[returns <= var_95]
        cvar_95 = tail_losses.mean() if len(tail_losses) > 0 else var_95
        
        ann_vol = returns.std() * np.sqrt(252)
        min_ret = returns.min()
        max_ret = returns.max()
        mean_ret = returns.mean()
        
        results.append({
            "amfi_code": str(code),
            "scheme_name": meta["scheme_name"],
            "fund_house": meta["fund_house"],
            "category": meta["category"],
            "sub_category": meta["sub_category"],
            "risk_category": meta["risk_category"],
            "var_95_daily_pct": round(float(var_95), 4),
            "cvar_95_daily_pct": round(float(cvar_95), 4),
            "annualized_volatility_pct": round(float(ann_vol), 4),
            "mean_daily_return_pct": round(float(mean_ret), 4),
            "min_daily_return_pct": round(float(min_ret), 4),
            "max_daily_return_pct": round(float(max_ret), 4)
        })
        
    df_res = pd.DataFrame(results).sort_values("var_95_daily_pct", ascending=True).reset_index(drop=True)
    
    # Save outputs
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df_res.to_csv(BASE_DIR / "var_cvar_report.csv", index=False)
    df_res.to_csv(REPORTS_DIR / "var_cvar_report.csv", index=False)
    logger.info(f"Saved var_cvar_report.csv ({len(df_res)} schemes).")
    return df_res

def compute_and_plot_rolling_sharpe() -> pd.DataFrame:
    """
    Computes Rolling 90-day Sharpe ratio for 5 key mutual fund schemes:
    rolling_sharpe = returns.rolling(90).mean() / returns.rolling(90).std() * sqrt(252)
    Plots and exports rolling_sharpe_chart.png.
    """
    logger.info("Computing Rolling 90-day Sharpe ratio for 5 key schemes...")
    conn = get_connection()
    
    target_schemes = {
        "119551": "SBI Bluechip",
        "120503": "ICICI Bluechip",
        "118632": "Nippon Large Cap",
        "119092": "Axis Bluechip",
        "120841": "Kotak Bluechip"
    }
    
    codes_str = "','".join(target_schemes.keys())
    query = f"""
        SELECT n.amfi_code, f.scheme_name, n.nav_date, n.daily_return
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        WHERE n.amfi_code IN ('{codes_str}')
        ORDER BY n.amfi_code, n.nav_date;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df["nav_date"] = pd.to_datetime(df["nav_date"])
    
    plt.figure(figsize=(14, 7))
    sns.set_theme(style="whitegrid")
    
    rolling_records = []
    
    for code, label in target_schemes.items():
        sub = df[df["amfi_code"] == code].sort_values("nav_date").copy()
        sub["roll_mean"] = sub["daily_return"].rolling(90).mean()
        sub["roll_std"] = sub["daily_return"].rolling(90).std()
        sub["rolling_sharpe"] = (sub["roll_mean"] / sub["roll_std"]) * np.sqrt(252)
        
        # Plot line
        plt.plot(sub["nav_date"], sub["rolling_sharpe"], label=f"{label} ({code})", linewidth=1.8, alpha=0.9)
        
        valid = sub.dropna(subset=["rolling_sharpe"])
        rolling_records.append({
            "amfi_code": code,
            "scheme": label,
            "mean_rolling_sharpe": round(valid["rolling_sharpe"].mean(), 2),
            "min_rolling_sharpe": round(valid["rolling_sharpe"].min(), 2),
            "max_rolling_sharpe": round(valid["rolling_sharpe"].max(), 2),
            "latest_rolling_sharpe": round(valid["rolling_sharpe"].iloc[-1], 2)
        })
        
    plt.axhline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.7, label="Zero Sharpe Threshold")
    plt.axhline(1.0, color="green", linestyle=":", linewidth=1.2, alpha=0.7, label="Good Threshold (Sharpe = 1.0)")
    
    plt.title("Rolling 90-Day Annualized Sharpe Ratio Comparison (Top 5 Flagship Funds)", fontsize=14, weight="bold", pad=15)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Annualized Sharpe Ratio (90-Day Window)", fontsize=12)
    plt.legend(loc="upper left", frameon=True, framealpha=0.9)
    plt.ylim(-4.5, 7.5)
    plt.tight_layout()
    
    chart_path1 = BASE_DIR / "rolling_sharpe_chart.png"
    chart_path2 = REPORTS_DIR / "rolling_sharpe_chart.png"
    plt.savefig(chart_path1, dpi=120)
    plt.savefig(chart_path2, dpi=120)
    plt.close()
    
    logger.info(f"Saved rolling_sharpe_chart.png to {chart_path1} and {chart_path2}")
    return pd.DataFrame(rolling_records)

def compute_investor_cohorts() -> pd.DataFrame:
    """
    Investor cohort analysis: Groups investors by first transaction year (2024 / 2025).
    Computes investor count, average SIP amount, total invested volume, and top preferred fund.
    """
    logger.info("Performing investor cohort analysis...")
    conn = get_connection()
    
    query = """
        SELECT t.investor_id, t.transaction_date, t.amfi_code, f.scheme_name, t.transaction_type, t.amount_inr
        FROM fact_transactions t
        JOIN dim_fund f ON t.amfi_code = f.amfi_code;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df["tx_date"] = pd.to_datetime(df["transaction_date"])
    df["tx_year"] = df["tx_date"].dt.year
    
    first_year = df.groupby("investor_id")["tx_year"].min().reset_index()
    first_year.columns = ["investor_id", "cohort_year"]
    df = df.merge(first_year, on="investor_id")
    
    cohort_list = []
    for cohort, c_df in df.groupby("cohort_year"):
        n_investors = c_df["investor_id"].nunique()
        total_amt = c_df["amount_inr"].sum()
        avg_per_inv = total_amt / n_investors
        
        sip_sub = c_df[c_df["transaction_type"] == "SIP"]
        avg_sip = sip_sub["amount_inr"].mean() if not sip_sub.empty else 0
        total_sips = len(sip_sub)
        
        lump_sub = c_df[c_df["transaction_type"] == "Lumpsum"]
        total_lumpsums = len(lump_sub)
        
        # Most popular fund by transaction volume
        fund_vols = c_df.groupby(["amfi_code", "scheme_name"])["amount_inr"].sum().reset_index()
        top_fund = fund_vols.sort_values("amount_inr", ascending=False).iloc[0]
        
        cohort_list.append({
            "cohort_year": cohort,
            "investor_count": n_investors,
            "total_transactions": len(c_df),
            "total_invested_crore": round(total_amt / 1e7, 2),
            "avg_invested_per_investor_inr": round(avg_per_inv, 2),
            "avg_sip_amount_inr": round(avg_sip, 2),
            "total_sip_transactions": total_sips,
            "total_lumpsum_transactions": total_lumpsums,
            "top_preferred_amfi_code": top_fund["amfi_code"],
            "top_preferred_scheme": top_fund["scheme_name"],
            "top_scheme_volume_crore": round(top_fund["amount_inr"] / 1e7, 2)
        })
        
    df_cohort = pd.DataFrame(cohort_list)
    df_cohort.to_csv(BASE_DIR / "cohort_analysis.csv", index=False)
    df_cohort.to_csv(REPORTS_DIR / "cohort_analysis.csv", index=False)
    logger.info(f"Saved cohort_analysis.csv ({len(df_cohort)} cohorts).")
    return df_cohort

def compute_sip_continuity() -> pd.DataFrame:
    """
    SIP Continuity Analysis:
    For investors with 6+ SIP transactions, computes average gap between transactions.
    Flags investors with average gap > 35 days as 'at-risk'.
    """
    logger.info("Performing SIP continuity and churn risk analysis...")
    conn = get_connection()
    
    query = """
        SELECT investor_id, transaction_date, amount_inr, state, city_tier
        FROM fact_transactions
        WHERE transaction_type = 'SIP'
        ORDER BY investor_id, transaction_date;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df["tx_date"] = pd.to_datetime(df["transaction_date"])
    
    investors = []
    for inv_id, grp in df.groupby("investor_id"):
        if len(grp) >= 6:
            grp = grp.sort_values("tx_date")
            gaps = grp["tx_date"].diff().dt.days.dropna()
            
            avg_gap = gaps.mean()
            max_gap = gaps.max()
            min_gap = gaps.min()
            std_gap = gaps.std() if len(gaps) > 1 else 0
            
            is_at_risk = 1 if avg_gap > 35.0 else 0
            
            investors.append({
                "investor_id": inv_id,
                "state": grp.iloc[0]["state"],
                "city_tier": grp.iloc[0]["city_tier"],
                "sip_count": len(grp),
                "total_sip_inr": grp["amount_inr"].sum(),
                "avg_sip_inr": round(grp["amount_inr"].mean(), 2),
                "avg_gap_days": round(avg_gap, 2),
                "min_gap_days": int(min_gap) if len(gaps) else 0,
                "max_gap_days": int(max_gap) if len(gaps) else 0,
                "std_gap_days": round(std_gap, 2),
                "is_at_risk": is_at_risk,
                "churn_status": "At-Risk" if is_at_risk else "Active/Consistent"
            })
            
    df_sip = pd.DataFrame(investors).sort_values("avg_gap_days", ascending=False).reset_index(drop=True)
    df_sip.to_csv(BASE_DIR / "sip_continuity.csv", index=False)
    df_sip.to_csv(REPORTS_DIR / "sip_continuity.csv", index=False)
    logger.info(f"Saved sip_continuity.csv ({len(df_sip)} eligible investors). At-risk: {(df_sip['is_at_risk']==1).sum()}")
    return df_sip

def compute_sector_hhi() -> pd.DataFrame:
    """
    Sector Concentration Analysis:
    For each equity fund, computes Herfindahl-Hirschman Index (HHI) of sector weights.
    HHI = sum(weight_i^2). High HHI indicates portfolio concentration.
    """
    logger.info("Computing Sector Concentration HHI for equity funds...")
    conn = get_connection()
    
    query = """
        SELECT h.amfi_code, f.scheme_name, f.fund_house, f.sub_category, h.sector, h.weight_pct
        FROM fact_portfolio_holdings h
        JOIN dim_fund f ON h.amfi_code = f.amfi_code
        WHERE f.category = 'Equity'
        ORDER BY h.amfi_code, h.weight_pct DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    hhi_list = []
    for code, grp in df.groupby("amfi_code"):
        meta = grp.iloc[0]
        sector_weights = grp.groupby("sector")["weight_pct"].sum()
        hhi = (sector_weights ** 2).sum()
        
        top_sector = sector_weights.idxmax()
        top_weight = sector_weights.max()
        
        # Concentration Tier
        if hhi >= 2500:
            conc_level = "High Concentration"
        elif hhi >= 1500:
            conc_level = "Moderate Concentration"
        else:
            conc_level = "Diversified"
            
        hhi_list.append({
            "amfi_code": str(code),
            "scheme_name": meta["scheme_name"],
            "fund_house": meta["fund_house"],
            "sub_category": meta["sub_category"],
            "hhi_score": round(float(hhi), 2),
            "concentration_tier": conc_level,
            "num_sectors": len(sector_weights),
            "top_sector": top_sector,
            "top_sector_weight_pct": round(float(top_weight), 2)
        })
        
    df_hhi = pd.DataFrame(hhi_list).sort_values("hhi_score", ascending=False).reset_index(drop=True)
    df_hhi.to_csv(BASE_DIR / "sector_hhi.csv", index=False)
    df_hhi.to_csv(REPORTS_DIR / "sector_hhi.csv", index=False)
    
    # Save HHI Plot
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    sns.barplot(data=df_hhi.head(10), x="hhi_score", y="scheme_name", palette="rocket")
    plt.axvline(2500, color="red", linestyle="--", label="High Concentration Benchmark (HHI = 2500)")
    plt.title("Top 10 Concentrated Equity Mutual Funds by Sector HHI", fontsize=13, weight="bold")
    plt.xlabel("Herfindahl-Hirschman Index (HHI)", fontsize=11)
    plt.ylabel("Scheme Name", fontsize=11)
    plt.legend(loc="lower right")
    plt.tight_layout()
    
    hhi_chart_path = REPORTS_DIR / "sector_hhi_chart.png"
    plt.savefig(hhi_chart_path, dpi=120)
    plt.savefig(BASE_DIR / "sector_hhi_chart.png", dpi=120)
    plt.close()
    
    logger.info(f"Saved sector_hhi.csv ({len(df_hhi)} equity funds) and sector_hhi_chart.png.")
    return df_hhi

def run_all():
    """Executes all Day 6 advanced analytics and risk metric computations."""
    print("\n" + "="*80)
    print("RUNNING ADVANCED ANALYTICS & RISK METRICS PIPELINE")
    print("="*80)
    
    df_var = compute_var_cvar()
    print(f"\n[✓] Historical VaR/CVaR computed for {len(df_var)} schemes. Saved to var_cvar_report.csv.")
    
    df_sharpe = compute_and_plot_rolling_sharpe()
    print(f"[✓] Rolling 90-day Sharpe computed for 5 funds. Chart saved to rolling_sharpe_chart.png.")
    
    df_cohort = compute_investor_cohorts()
    print(f"[✓] Investor cohort analysis complete. Saved to cohort_analysis.csv.")
    
    df_sip = compute_sip_continuity()
    print(f"[✓] SIP continuity analysis complete ({len(df_sip)} investors). Saved to sip_continuity.csv.")
    
    df_hhi = compute_sector_hhi()
    print(f"[✓] Sector concentration HHI complete ({len(df_hhi)} funds). Saved to sector_hhi.csv.")
    
    print("\n" + "="*80)
    print("ALL ADVANCED ANALYTICS TASKS PROCESSED SUCCESSFULLY")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_all()
