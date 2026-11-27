"""
Data Ingestion and Exploration Pipeline
Bluestock Fintech Capstone Project - Day 1 ETL Pipeline

Loads all 10 mutual fund datasets, inspects structures, flags data quality anomalies,
explores fund master taxonomy, and validates AMFI code referential integrity.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

# Path configurations
BASE_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATASETS_DIR = BASE_DIR / "Datasets"
REPORTS_DIR = BASE_DIR / "reports"

# Canonical dataset filenames
DATASET_FILES = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv"
}

def resolve_dataset_path(filename: str) -> Path:
    """Finds dataset in data/raw or Datasets folder."""
    raw_path = DATA_RAW_DIR / filename
    if raw_path.exists():
        return raw_path
    
    # Try finding matching file in Datasets directory
    for f in DATASETS_DIR.glob(f"*{filename}"):
        return f
        
    raise FileNotFoundError(f"Cannot find dataset file {filename} in {DATA_RAW_DIR} or {DATASETS_DIR}")

def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Loads all 10 datasets into a dictionary of DataFrames."""
    dfs = {}
    print("\n" + "="*80)
    print("STEP 1: LOADING ALL 10 DATASETS")
    print("="*80)
    
    for key, filename in DATASET_FILES.items():
        filepath = resolve_dataset_path(filename)
        df = pd.read_csv(filepath)
        dfs[key] = df
        print(f"Loaded '{key}' ({filename}) - Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
        
    return dfs

def inspect_datasets(dfs: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
    """
    Prints .shape, .dtypes, and .head() for each dataset and notes anomalies.
    Returns anomaly metadata dictionary.
    """
    print("\n" + "="*80)
    print("STEP 2: DATASET INSPECTION (.shape, .dtypes, .head) & ANOMALY DETECTION")
    print("="*80)
    
    anomalies = {}
    
    for key, df in dfs.items():
        filename = DATASET_FILES[key]
        print(f"\n" + "-"*80)
        print(f"DATASET: {key} ({filename})")
        print(f"-"*80)
        print(f"[Shape]: {df.shape[0]:,} rows, {df.shape[1]} columns")
        
        print("\n[Data Types & Missing Values]:")
        col_info = pd.DataFrame({
            "Dtype": df.dtypes.astype(str),
            "Null_Count": df.isnull().sum(),
            "Null_Pct (%)": (df.isnull().sum() / len(df) * 100).round(2),
            "Unique_Values": df.nunique()
        })
        print(col_info.to_string())
        
        print("\n[First 5 Rows (.head())]:")
        print(df.head().to_string())
        
        # Anomaly detection logic
        dataset_anomalies = []
        
        # 1. Null check
        null_cols = col_info[col_info["Null_Count"] > 0]
        if not null_cols.empty:
            for col, row in null_cols.iterrows():
                dataset_anomalies.append(f"Missing values in '{col}': {int(row['Null_Count'])} rows ({row['Null_Pct (%)']}%)")
                
        # 2. Duplicate check
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            dataset_anomalies.append(f"Duplicate rows detected: {dup_count} rows ({dup_count/len(df)*100:.2f}%)")
            
        # 3. Domain specific anomalies
        if key == "nav_history":
            if "nav" in df.columns:
                neg_nav = (df["nav"] <= 0).sum()
                if neg_nav > 0:
                    dataset_anomalies.append(f"Non-positive NAV values detected: {neg_nav} rows")
            if "date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["date"]):
                dataset_anomalies.append("Date column is stored as string/object, needs parsing to datetime")
                
        elif key == "investor_transactions":
            if "amount_inr" in df.columns:
                neg_amt = (df["amount_inr"] <= 0).sum()
                if neg_amt > 0:
                    dataset_anomalies.append(f"Non-positive transaction amounts: {neg_amt} rows")
            if "transaction_date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["transaction_date"]):
                dataset_anomalies.append("Transaction date is stored as string/object")
                
        elif key == "fund_master":
            if "amfi_code" in df.columns:
                dup_codes = df["amfi_code"].duplicated().sum()
                if dup_codes > 0:
                    dataset_anomalies.append(f"Duplicate amfi_code entries in fund master: {dup_codes}")
                    
        elif key == "scheme_performance":
            if "sharpe_ratio" in df.columns:
                neg_sharpe = (df["sharpe_ratio"] < 0).sum()
                if neg_sharpe > 0:
                    dataset_anomalies.append(f"Schemes with negative Sharpe Ratio: {neg_sharpe} (requires risk flag)")
                    
        anomalies[key] = {
            "shape": df.shape,
            "columns": list(df.columns),
            "anomalies": dataset_anomalies
        }
        
        print("\n[Identified Anomalies & Observations]:")
        if dataset_anomalies:
            for a in dataset_anomalies:
                print(f"  * {a}")
        else:
            print("  * No significant anomalies found (clean dataset).")
            
    return anomalies

def explore_fund_master(fm_df: pd.DataFrame) -> Dict[str, Any]:
    """Explores fund master metadata taxonomy and explains AMFI scheme code structure."""
    print("\n" + "="*80)
    print("STEP 3: EXPLORE FUND MASTER TAXONOMY & AMFI SCHEME CODE ARCHITECTURE")
    print("="*80)
    
    unique_fund_houses = fm_df["fund_house"].dropna().unique()
    unique_categories = fm_df["category"].dropna().unique()
    unique_sub_categories = fm_df["sub_category"].dropna().unique()
    unique_risk_grades = fm_df["risk_category"].dropna().unique() if "risk_category" in fm_df.columns else []
    
    print(f"\n1. Fund Houses ({len(unique_fund_houses)} Total):")
    for fh in sorted(unique_fund_houses):
        count = (fm_df["fund_house"] == fh).sum()
        print(f"   - {fh} ({count} schemes)")
        
    print(f"\n2. Broad Categories ({len(unique_categories)} Total):")
    for cat in sorted(unique_categories):
        count = (fm_df["category"] == cat).sum()
        print(f"   - {cat} ({count} schemes)")
        
    print(f"\n3. Sub-Categories ({len(unique_sub_categories)} Total):")
    for scat in sorted(unique_sub_categories):
        count = (fm_df["sub_category"] == scat).sum()
        print(f"   - {scat} ({count} schemes)")
        
    print(f"\n4. Risk Grades / SEBI Riskometer ({len(unique_risk_grades)} Total):")
    for rg in sorted(unique_risk_grades):
        count = (fm_df["risk_category"] == rg).sum()
        print(f"   - {rg} ({count} schemes)")
        
    print("\n5. AMFI Scheme Code Structure & Ecosystem Analysis:")
    amfi_explanation = """
   ===================================================================================
   WHAT IS AN AMFI SCHEME CODE?
   - AMFI (Association of Mutual Funds in India) assigns a standardized unique 
     identifier (typically a 6-digit integer, e.g., 125497) to every mutual fund 
     scheme and plan in India.
   - Purpose: Acts as the definitive Primary Key across RTAs (Registrar and Transfer 
     Agents like CAMS & KFintech), AMCs, stock exchange platforms (BSE StAR MF, 
     NSE NMF II), aggregators (mfapi.in), and distributors.
   
   ANATOMY & ATTRIBUTES ENCODED:
   1. Scheme Identity: Uniquely identifies the portfolio / mandate (e.g., HDFC Top 100).
   2. Plan Type: Distinguishes between 'Direct' (lower expense ratio) and 'Regular' 
      (includes distributor commission). Direct and Regular plans of the EXACT same 
      underlying portfolio have DIFFERENT AMFI codes (e.g. 125497 for Direct vs 
      100377 for Regular).
   3. Option Type: Distinguishes between 'Growth' (capital appreciation reinvested) 
      and 'IDCW' (Income Distribution cum Capital Withdrawal / dividend payout or 
      reinvestment). Each option has a distinct AMFI code.
   4. ISIN Mapping: Each AMFI code maps 1:1 with an International Securities Identification 
      Number (ISIN) formatted as 'INF...' for demat and depository clearing (NSDL/CDSL).
   ===================================================================================
    """
    print(amfi_explanation)
    
    return {
        "fund_houses": sorted(unique_fund_houses.tolist()),
        "categories": sorted(unique_categories.tolist()),
        "sub_categories": sorted(unique_sub_categories.tolist()),
        "risk_grades": sorted(unique_risk_grades.tolist()) if len(unique_risk_grades) else []
    }

def validate_amfi_codes(dfs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Validates referential integrity of AMFI codes between fund_master and other tables."""
    print("\n" + "="*80)
    print("STEP 4: AMFI CODE VALIDATION & REFERENTIAL INTEGRITY CHECK")
    print("="*80)
    
    fm_codes = set(dfs["fund_master"]["amfi_code"].astype(str).str.strip().unique())
    nav_codes = set(dfs["nav_history"]["amfi_code"].astype(str).str.strip().unique())
    perf_codes = set(dfs["scheme_performance"]["amfi_code"].astype(str).str.strip().unique())
    tx_codes = set(dfs["investor_transactions"]["amfi_code"].astype(str).str.strip().unique())
    holdings_codes = set(dfs["portfolio_holdings"]["amfi_code"].astype(str).str.strip().unique())
    
    print(f"\nUnique AMFI codes in fund_master:         {len(fm_codes)}")
    print(f"Unique AMFI codes in nav_history:         {len(nav_codes)}")
    print(f"Unique AMFI codes in scheme_performance:  {len(perf_codes)}")
    print(f"Unique AMFI codes in investor_transactions: {len(tx_codes)}")
    print(f"Unique AMFI codes in portfolio_holdings:    {len(holdings_codes)}")
    
    # Check 1: Does every code in fund_master exist in nav_history?
    missing_in_nav = fm_codes - nav_codes
    extra_in_nav = nav_codes - fm_codes
    
    print("\n[Validation Results: fund_master vs nav_history]")
    if not missing_in_nav:
        print("  [✓] PASS: 100% of AMFI codes in fund_master exist in nav_history.")
    else:
        print(f"  [X] FAIL: {len(missing_in_nav)} codes in fund_master missing from nav_history: {missing_in_nav}")
        
    if not extra_in_nav:
        print("  [✓] PASS: No orphaned AMFI codes in nav_history (all belong to fund_master).")
    else:
        print(f"  [!] Note: {len(extra_in_nav)} codes in nav_history are not in fund_master: {extra_in_nav}")
        
    # Check 2: Performance table validation
    missing_in_perf = fm_codes - perf_codes
    print("\n[Validation Results: fund_master vs scheme_performance]")
    if not missing_in_perf:
        print("  [✓] PASS: All fund_master schemes have performance metrics.")
    else:
        print(f"  [!] Note: {len(missing_in_perf)} fund_master schemes missing in scheme_performance: {missing_in_perf}")

    # Check 3: Investor transactions validation
    missing_tx = tx_codes - fm_codes
    print("\n[Validation Results: investor_transactions vs fund_master]")
    if not missing_tx:
        print("  [✓] PASS: All investor transaction scheme codes resolve to fund_master.")
    else:
        print(f"  [X] WARNING: {len(missing_tx)} transaction codes do not exist in fund_master: {missing_tx}")

    return {
        "fm_codes_count": len(fm_codes),
        "nav_codes_count": len(nav_codes),
        "missing_in_nav": list(missing_in_nav),
        "extra_in_nav": list(extra_in_nav),
        "missing_in_perf": list(missing_in_perf),
        "orphaned_tx_codes": list(missing_tx)
    }

def generate_data_quality_report(
    anomalies: Dict[str, Dict[str, Any]],
    fm_stats: Dict[str, Any],
    validation: Dict[str, Any]
):
    """Generates a markdown Data Quality Summary report in reports/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / "data_quality_summary.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Bluestock Mutual Fund Analytics Platform - Data Quality Summary (Day 1)\n\n")
        f.write("**Date:** 19 November 2026  \n")
        f.write("**Phase:** Day 1 - Data Ingestion & Quality Audit  \n")
        f.write("**Team:** SR (Sathwik Ryapaka), AB (Abhiram), AK (Ashmeet Kaur)  \n\n")
        f.write("---\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write("All 10 required CSV datasets have been successfully ingested and audited. ")
        f.write("The dataset collection provides comprehensive coverage of fund master metadata, ")
        f.write("daily NAV history (4.5+ years), AMC AUM distributions, industry SIP trends, ")
        f.write("investor demographic transactions, portfolio constituent holdings, and benchmark index histories.\n\n")
        
        f.write("## 2. Dataset Ingestion Overview\n\n")
        f.write("| # | Dataset Name | File Name | Rows | Columns | Status |\n")
        f.write("|---|--------------|-----------|------|---------|--------|\n")
        
        for idx, (key, filename) in enumerate(DATASET_FILES.items(), 1):
            info = anomalies[key]
            rows, cols = info["shape"]
            anomaly_cnt = len(info["anomalies"])
            status = "Verified Clean" if anomaly_cnt == 0 else f"{anomaly_cnt} Item(s) Flagged"
            f.write(f"| {idx} | {key} | `{filename}` | {rows:,} | {cols} | {status} |\n")
            
        f.write("\n## 3. Referential Integrity & AMFI Code Validation\n\n")
        f.write(f"- **Total Fund Master Schemes:** {validation['fm_codes_count']}\n")
        f.write(f"- **Schemes Represented in NAV History:** {validation['nav_codes_count']}\n")
        f.write(f"- **Codes in Fund Master Missing in NAV History:** {len(validation['missing_in_nav'])}\n")
        f.write(f"- **Orphaned Codes in Investor Transactions:** {len(validation['orphaned_tx_codes'])}\n\n")
        
        if len(validation['missing_in_nav']) == 0:
            f.write("> **Validation Result:** [PASS] Every AMFI scheme code present in `fund_master` exists in `nav_history`. Perfect 1:N referential relationship confirmed.\n\n")
        else:
            f.write(f"> **Validation Result:** [FLAG] Missing codes: {validation['missing_in_nav']}\n\n")

        f.write("## 4. Key Fund Master Dimensions\n\n")
        f.write(f"- **Unique Fund Houses ({len(fm_stats['fund_houses'])}):** {', '.join(fm_stats['fund_houses'])}\n")
        f.write(f"- **Categories ({len(fm_stats['categories'])}):** {', '.join(fm_stats['categories'])}\n")
        f.write(f"- **Sub-Categories ({len(fm_stats['sub_categories'])}):** {', '.join(fm_stats['sub_categories'])}\n")
        f.write(f"- **Risk Grades ({len(fm_stats['risk_grades'])}):** {', '.join(fm_stats['risk_grades'])}\n\n")

        f.write("## 5. Identified Data Anomalies & Recommendations for Day 2 Cleaning\n\n")
        for key, info in anomalies.items():
            if info["anomalies"]:
                f.write(f"### `{DATASET_FILES[key]}`\n")
                for a in info["anomalies"]:
                    f.write(f"- {a}\n")
                f.write("\n")
                
        f.write("## 6. Action Items for Day 2 (Data Cleaning & SQL Database Design)\n")
        f.write("1. **Date Standardisation:** Convert string dates across `nav_history`, `investor_transactions`, `benchmark_indices`, and `fund_master` into standard `YYYY-MM-DD` ISO format.\n")
        f.write("2. **Missing Holiday Handling:** Implement calendar forward-fill (`ffill`) on `nav_history` to handle market holidays and weekends.\n")
        f.write("3. **Transaction KYC Validation:** Verify clean categorisation for investor demographics and KYC flags.\n")
        f.write("4. **Relational Database Design:** Load clean data into normalized SQLite star schema (`dim_fund`, `fact_nav`, `fact_transactions`, `fact_performance`).\n")

    print(f"\n[✓] Data Quality Summary saved to: {report_file}")

def main():
    """Executes Day 1 data ingestion, anomaly inspection, AMFI validation, and quality report generation."""
    dfs = load_all_datasets()
    anomalies = inspect_datasets(dfs)
    fm_stats = explore_fund_master(dfs["fund_master"])
    validation = validate_amfi_codes(dfs)
    generate_data_quality_report(anomalies, fm_stats, validation)
    print("\n" + "="*80)
    print("DAY 1 DATA INGESTION & AUDIT COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
