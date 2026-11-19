"""
Live NAV Data Fetcher for Mutual Fund Analytics Platform
Bluestock Fintech Capstone Project - Day 1 ETL Pipeline

Fetches real-time and historical NAV data from mfapi.in REST API.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Base API URL
MFAPI_BASE_URL = "https://api.mfapi.in/mf"

# Key schemes to fetch as mandated by Day 1 tasks
TARGET_SCHEMES = {
    125497: "HDFC Top 100 Direct",
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

def fetch_scheme_nav(scheme_code: int, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch NAV data and metadata for a specific AMFI scheme code from mfapi.in.
    
    Args:
        scheme_code: AMFI scheme code (e.g., 125497)
        timeout: Request timeout in seconds
        
    Returns:
        Parsed JSON dictionary response
    """
    url = f"{MFAPI_BASE_URL}/{scheme_code}"
    logger.info(f"Fetching NAV data from: {url}")
    
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    
    data = response.json()
    if data.get("status") != "SUCCESS" and "data" not in data:
        raise ValueError(f"Failed to retrieve valid data for scheme code {scheme_code}: {data}")
        
    return data

def parse_and_save_nav(
    scheme_code: int,
    raw_data: Dict[str, Any],
    output_dir: Path
) -> pd.DataFrame:
    """
    Parses mfapi.in JSON response and saves it as a raw CSV file.
    
    Args:
        scheme_code: AMFI code
        raw_data: JSON dictionary from mfapi.in
        output_dir: Directory to save the CSV file
        
    Returns:
        DataFrame containing parsed NAV data
    """
    meta = raw_data.get("meta", {})
    records = raw_data.get("data", [])
    
    fund_house = meta.get("fund_house", "Unknown")
    scheme_type = meta.get("scheme_type", "")
    scheme_category = meta.get("scheme_category", "")
    scheme_name = meta.get("scheme_name", f"Scheme {scheme_code}")
    
    logger.info(f"Scheme: {scheme_name} | Fund House: {fund_house} | Records: {len(records)}")
    
    df = pd.DataFrame(records)
    if df.empty:
        logger.warning(f"No records found for scheme {scheme_code}")
        return df

    # Add metadata columns
    df["amfi_code"] = scheme_code
    df["scheme_name"] = scheme_name
    df["fund_house"] = fund_house
    df["scheme_category"] = scheme_category
    df["scheme_type"] = scheme_type
    
    # Standardize column order
    df = df[["amfi_code", "date", "nav", "scheme_name", "fund_house", "scheme_category", "scheme_type"]]
    
    # Save to CSV
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_scheme_slug = "".join(c if c.isalnum() else "_" for c in scheme_name.lower())[:30].strip("_")
    filename = f"live_nav_{scheme_code}_{clean_scheme_slug}.csv"
    output_path = output_dir / filename
    
    df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df)} rows to: {output_path}")
    
    # Also save standard numbered or canonical scheme file for ease of reference
    canonical_path = output_dir / f"live_nav_{scheme_code}.csv"
    df.to_csv(canonical_path, index=False)
    
    return df

def fetch_and_save_all(
    schemes: Optional[Dict[int, str]] = None,
    output_dir: Optional[Path] = None
) -> Dict[int, pd.DataFrame]:
    """
    Fetches and saves NAV data for all target schemes.
    
    Args:
        schemes: Dictionary mapping scheme codes to scheme labels
        output_dir: Path to raw data directory
        
    Returns:
        Dictionary of DataFrames keyed by scheme code
    """
    if schemes is None:
        schemes = TARGET_SCHEMES
        
    if output_dir is None:
        output_dir = Path("data/raw")
        
    results = {}
    combined_dfs = []
    
    print("\n" + "="*80)
    print("LIVE NAV FETCHER - MFAPI.IN (AMFI INDIA)")
    print("="*80)
    
    for code, label in schemes.items():
        try:
            print(f"\n[+] Fetching {label} (AMFI Code: {code})...")
            raw_json = fetch_scheme_nav(code)
            df = parse_and_save_nav(code, raw_json, output_dir)
            results[code] = df
            
            if not df.empty:
                latest_record = df.iloc[0]
                oldest_record = df.iloc[-1]
                print(f"    - Success: {len(df)} historical NAV records retrieved.")
                print(f"    - Latest NAV: Rs. {latest_record['nav']} (Date: {latest_record['date']})")
                print(f"    - Earliest NAV: Rs. {oldest_record['nav']} (Date: {oldest_record['date']})")
                combined_dfs.append(df)
        except Exception as e:
            logger.error(f"Error fetching scheme {code} ({label}): {e}")
            print(f"    - FAILED: {e}")
            
    if combined_dfs:
        combined = pd.concat(combined_dfs, ignore_index=True)
        combined_file = output_dir / "live_nav_combined_schemes.csv"
        combined.to_csv(combined_file, index=False)
        print(f"\n[✓] Saved consolidated NAV file ({len(combined)} rows) to: {combined_file}")
        
    print("\n" + "="*80)
    print("LIVE NAV INGESTION COMPLETE")
    print("="*80 + "\n")
    return results

if __name__ == "__main__":
    fetch_and_save_all()
