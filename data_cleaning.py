"""
Data Cleaning & Transformation Pipeline
Bluestock Fintech Capstone Project - Day 2 ETL Pipeline

Cleans, validates, and standardizes all 10 mutual fund datasets:
1. nav_history: Parse dates, sort amfi_code+date, ffill missing NAV, remove duplicates, validate NAV > 0, compute daily_return.
2. investor_transactions: Standardize transaction types, validate amount > 0, ISO date formats, check KYC enums.
3. scheme_performance: Validate numeric returns, flag anomalies (negative Sharpe, high expense), verify expense_ratio range.
4. Remaining datasets: Clean dates, strip whitespace, cast data types.
Outputs: 10 cleaned CSVs in data/processed/.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def clean_nav_history() -> pd.DataFrame:
    """
    Cleans nav_history.csv:
    - Parses dates to datetime format
    - Sorts by amfi_code + date
    - Forward-fills missing NAV values per scheme
    - Removes duplicate entries
    - Validates NAV > 0
    - Calculates daily_return (%)
    """
    logger.info("Cleaning 02_nav_history.csv...")
    file_path = RAW_DIR / "02_nav_history.csv"
    df = pd.read_csv(file_path)
    
    initial_rows = len(df)
    
    # 1. Parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isnull().any():
        logger.warning(f"Dropping {df['date'].isnull().sum()} rows with invalid dates in NAV history")
        df = df.dropna(subset=["date"])
        
    # 2. Remove duplicates
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    
    # 3. Sort by amfi_code and date
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    
    # 4. Forward fill missing NAV per scheme
    df["nav"] = df.groupby("amfi_code")["nav"].ffill().bfill()
    
    # 5. Validate NAV > 0
    df = df[df["nav"] > 0]
    
    # 6. Compute daily return %
    df["daily_return"] = df.groupby("amfi_code")["nav"].pct_change().fillna(0) * 100
    df["daily_return"] = df["daily_return"].round(4)
    
    # Format date to ISO string YYYY-MM-DD
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    logger.info(f"NAV History cleaned: {initial_rows} -> {len(df)} rows. Zero duplicates, NAV > 0 verified.")
    return df

def clean_investor_transactions() -> pd.DataFrame:
    """
    Cleans investor_transactions.csv:
    - Standardizes transaction_type (SIP/Lumpsum/Redemption)
    - Validates amount_inr > 0
    - Standardizes transaction_date to ISO YYYY-MM-DD
    - Validates and checks KYC status enum values (Verified, Pending)
    - Trims whitespace across string columns
    """
    logger.info("Cleaning 08_investor_transactions.csv...")
    file_path = RAW_DIR / "08_investor_transactions.csv"
    df = pd.read_csv(file_path)
    
    initial_rows = len(df)
    
    # 1. Strip whitespace
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
        
    # 2. Standardize transaction_type
    tx_map = {
        "sip": "SIP",
        "SIP": "SIP",
        "lumpsum": "Lumpsum",
        "Lumpsum": "Lumpsum",
        "Lump Sum": "Lumpsum",
        "redemption": "Redemption",
        "Redemption": "Redemption"
    }
    df["transaction_type"] = df["transaction_type"].map(tx_map).fillna(df["transaction_type"].str.capitalize())
    
    # 3. Validate amount > 0
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df = df[df["amount_inr"] > 0]
    
    # 4. Fix date formats
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["transaction_date"])
    
    # 5. Check KYC status enum
    valid_kyc = {"Verified", "Pending"}
    df["kyc_status"] = df["kyc_status"].apply(lambda x: x if x in valid_kyc else "Pending")
    
    # 6. City tier standardization
    valid_tiers = {"T30", "B30"}
    df["city_tier"] = df["city_tier"].apply(lambda x: x if x in valid_tiers else ("T30" if "30" in str(x) else "B30"))
    
    # 7. Deduplicate if exact duplicate rows exist
    df = df.drop_duplicates()
    
    logger.info(f"Transactions cleaned: {initial_rows} -> {len(df)} rows. All amounts > 0, KYC and dates validated.")
    return df

def clean_scheme_performance() -> pd.DataFrame:
    """
    Cleans scheme_performance.csv:
    - Validates all return and ratio values are numeric
    - Checks expense_ratio range (0.1% – 2.5%)
    - Flags anomalies (e.g., negative Sharpe ratio or extreme volatility)
    """
    logger.info("Cleaning 07_scheme_performance.csv...")
    file_path = RAW_DIR / "07_scheme_performance.csv"
    df = pd.read_csv(file_path)
    
    # 1. Strip whitespace
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()
        
    # 2. Ensure numeric types
    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct",
        "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct",
        "max_drawdown_pct", "aum_crore", "expense_ratio_pct"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            
    # 3. Check expense ratio range (0.1% - 2.5%)
    invalid_expense = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
    if not invalid_expense.empty:
        logger.warning(f"Found {len(invalid_expense)} funds with expense ratio outside 0.1% - 2.5% range")
    else:
        logger.info("All scheme expense ratios verified within 0.1% - 2.5% boundary.")
        
    # 4. Flag anomalies
    # Anomaly conditions:
    # - Negative Sharpe ratio
    # - Sharpe ratio > 5.0 (typical in liquid funds due to near-zero std dev)
    # - Drawdown deeper than -30%
    anomaly_flags = []
    anomaly_reasons = []
    
    for _, row in df.iterrows():
        reasons = []
        if row["sharpe_ratio"] < 0:
            reasons.append("Negative Sharpe Ratio")
        elif row["sharpe_ratio"] > 5.0:
            reasons.append(f"Unusually High Sharpe ({row['sharpe_ratio']}) due to Low Volatility ({row['std_dev_ann_pct']}%)")
            
        if row["max_drawdown_pct"] < -30.0:
            reasons.append(f"High Drawdown ({row['max_drawdown_pct']}%)")
            
        if reasons:
            anomaly_flags.append(1)
            anomaly_reasons.append("; ".join(reasons))
        else:
            anomaly_flags.append(0)
            anomaly_reasons.append("Normal")
            
    df["anomaly_flag"] = anomaly_flags
    df["anomaly_description"] = anomaly_reasons
    
    logger.info(f"Scheme performance cleaned: {len(df)} schemes. {sum(anomaly_flags)} anomalies flagged.")
    return df

def clean_fund_master() -> pd.DataFrame:
    """Cleans 01_fund_master.csv."""
    logger.info("Cleaning 01_fund_master.csv...")
    file_path = RAW_DIR / "01_fund_master.csv"
    df = pd.read_csv(file_path)
    
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()
        
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df["exit_load_pct"] = pd.to_numeric(df["exit_load_pct"], errors="coerce")
    df["min_sip_amount"] = pd.to_numeric(df["min_sip_amount"], errors="coerce")
    df["min_lumpsum_amount"] = pd.to_numeric(df["min_lumpsum_amount"], errors="coerce")
    
    df = df.drop_duplicates(subset=["amfi_code"])
    logger.info(f"Fund master cleaned: {len(df)} schemes.")
    return df

def clean_aum_by_fund_house() -> pd.DataFrame:
    """Cleans 03_aum_by_fund_house.csv."""
    logger.info("Cleaning 03_aum_by_fund_house.csv...")
    file_path = RAW_DIR / "03_aum_by_fund_house.csv"
    df = pd.read_csv(file_path)
    
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["fund_house"] = df["fund_house"].astype(str).str.strip()
    df["aum_lakh_crore"] = pd.to_numeric(df["aum_lakh_crore"], errors="coerce")
    df["aum_crore"] = pd.to_numeric(df["aum_crore"], errors="coerce")
    df["num_schemes"] = pd.to_numeric(df["num_schemes"], errors="coerce").astype(int)
    
    df = df.sort_values(["fund_house", "date"]).reset_index(drop=True)
    df = df.drop_duplicates(subset=["fund_house", "date"])
    logger.info(f"AUM by Fund House cleaned: {len(df)} records.")
    return df

def clean_monthly_sip_inflows() -> pd.DataFrame:
    """Cleans 04_monthly_sip_inflows.csv."""
    logger.info("Cleaning 04_monthly_sip_inflows.csv...")
    file_path = RAW_DIR / "04_monthly_sip_inflows.csv"
    df = pd.read_csv(file_path)
    
    df["month"] = df["month"].astype(str).str.strip()
    df["sip_inflow_crore"] = pd.to_numeric(df["sip_inflow_crore"], errors="coerce")
    df["active_sip_accounts_crore"] = pd.to_numeric(df["active_sip_accounts_crore"], errors="coerce")
    df["new_sip_accounts_lakh"] = pd.to_numeric(df["new_sip_accounts_lakh"], errors="coerce")
    df["sip_aum_lakh_crore"] = pd.to_numeric(df["sip_aum_lakh_crore"], errors="coerce")
    df["yoy_growth_pct"] = pd.to_numeric(df["yoy_growth_pct"], errors="coerce")
    
    df = df.sort_values("month").reset_index(drop=True)
    logger.info(f"Monthly SIP Inflows cleaned: {len(df)} months.")
    return df

def clean_category_inflows() -> pd.DataFrame:
    """Cleans 05_category_inflows.csv."""
    logger.info("Cleaning 05_category_inflows.csv...")
    file_path = RAW_DIR / "05_category_inflows.csv"
    df = pd.read_csv(file_path)
    
    df["month"] = df["month"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce")
    
    df = df.sort_values(["category", "month"]).reset_index(drop=True)
    logger.info(f"Category Inflows cleaned: {len(df)} records.")
    return df

def clean_industry_folio_count() -> pd.DataFrame:
    """Cleans 06_industry_folio_count.csv."""
    logger.info("Cleaning 06_industry_folio_count.csv...")
    file_path = RAW_DIR / "06_industry_folio_count.csv"
    df = pd.read_csv(file_path)
    
    df["month"] = df["month"].astype(str).str.strip()
    for c in ["total_folios_crore", "equity_folios_crore", "debt_folios_crore", "hybrid_folios_crore", "others_folios_crore"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        
    df = df.sort_values("month").reset_index(drop=True)
    logger.info(f"Industry Folio Count cleaned: {len(df)} records.")
    return df

def clean_portfolio_holdings() -> pd.DataFrame:
    """Cleans 09_portfolio_holdings.csv."""
    logger.info("Cleaning 09_portfolio_holdings.csv...")
    file_path = RAW_DIR / "09_portfolio_holdings.csv"
    df = pd.read_csv(file_path)
    
    df["amfi_code"] = df["amfi_code"].astype(str)
    for c in ["stock_symbol", "stock_name", "sector"]:
        df[c] = df[c].astype(str).str.strip()
        
    df["weight_pct"] = pd.to_numeric(df["weight_pct"], errors="coerce")
    df["market_value_cr"] = pd.to_numeric(df["market_value_cr"], errors="coerce")
    df["current_price_inr"] = pd.to_numeric(df["current_price_inr"], errors="coerce")
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    df = df.sort_values(["amfi_code", "weight_pct"], ascending=[True, False]).reset_index(drop=True)
    logger.info(f"Portfolio Holdings cleaned: {len(df)} records.")
    return df

def clean_benchmark_indices() -> pd.DataFrame:
    """Cleans 10_benchmark_indices.csv."""
    logger.info("Cleaning 10_benchmark_indices.csv...")
    file_path = RAW_DIR / "10_benchmark_indices.csv"
    df = pd.read_csv(file_path)
    
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["index_name"] = df["index_name"].astype(str).str.strip()
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    
    df = df.sort_values(["index_name", "date"]).reset_index(drop=True)
    df = df.drop_duplicates(subset=["index_name", "date"])
    logger.info(f"Benchmark Indices cleaned: {len(df)} records.")
    return df

def clean_and_save_all() -> Dict[str, pd.DataFrame]:
    """Runs cleaning pipeline for all 10 datasets and saves them to data/processed/."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    cleaned_data = {
        "fund_master": clean_fund_master(),
        "nav_history": clean_nav_history(),
        "aum_by_fund_house": clean_aum_by_fund_house(),
        "monthly_sip_inflows": clean_monthly_sip_inflows(),
        "category_inflows": clean_category_inflows(),
        "industry_folio_count": clean_industry_folio_count(),
        "scheme_performance": clean_scheme_performance(),
        "investor_transactions": clean_investor_transactions(),
        "portfolio_holdings": clean_portfolio_holdings(),
        "benchmark_indices": clean_benchmark_indices()
    }
    
    # Save standard numbered filenames and canonical deliverable names
    name_mapping = {
        "fund_master": ("01_clean_fund_master.csv", "clean_fund_master.csv"),
        "nav_history": ("02_clean_nav_history.csv", "clean_nav.csv"),
        "aum_by_fund_house": ("03_clean_aum_by_fund_house.csv", "clean_aum.csv"),
        "monthly_sip_inflows": ("04_clean_monthly_sip_inflows.csv", "clean_sip_inflows.csv"),
        "category_inflows": ("05_clean_category_inflows.csv", "clean_category_inflows.csv"),
        "industry_folio_count": ("06_clean_industry_folio_count.csv", "clean_folio_count.csv"),
        "scheme_performance": ("07_clean_scheme_performance.csv", "clean_performance.csv"),
        "investor_transactions": ("08_clean_investor_transactions.csv", "clean_transactions.csv"),
        "portfolio_holdings": ("09_clean_portfolio_holdings.csv", "clean_portfolio_holdings.csv"),
        "benchmark_indices": ("10_clean_benchmark_indices.csv", "clean_benchmark_indices.csv")
    }
    
    print("\n" + "="*80)
    print("SAVING 10 CLEANED DATASETS TO data/processed/")
    print("="*80)
    
    for key, (num_name, can_name) in name_mapping.items():
        df = cleaned_data[key]
        p1 = PROCESSED_DIR / num_name
        p2 = PROCESSED_DIR / can_name
        df.to_csv(p1, index=False)
        df.to_csv(p2, index=False)
        print(f"[✓] Saved {num_name:<34} ({df.shape[0]:>6,} rows x {df.shape[1]:>2} cols)")
        
    print("="*80)
    print("ALL 10 DATASETS SUCCESSFULLY CLEANED AND EXPORTED")
    print("="*80 + "\n")
    return cleaned_data

if __name__ == "__main__":
    clean_and_save_all()
