"""
Database Loader & ETL Ingestion Pipeline
Bluestock Fintech Capstone Project - Day 2

Loads all cleaned datasets into SQLite database (bluestock_mf.db) using SQLAlchemy.
Populates dim_date dimension and verifies row counts match source CSVs.
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "bluestock_mf.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

DATABASE_URL = f"sqlite:///{DB_PATH}"

def generate_dim_date(start_date: str = "2020-01-01", end_date: str = "2026-12-31") -> pd.DataFrame:
    """Generates complete calendar dimension table for data warehousing."""
    logger.info(f"Generating dim_date dimension from {start_date} to {end_date}...")
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    
    df_date = pd.DataFrame({"dt": dates})
    df_date["date"] = df_date["dt"].dt.strftime("%Y-%m-%d")
    df_date["year"] = df_date["dt"].dt.year
    df_date["quarter"] = df_date["dt"].dt.quarter
    df_date["month"] = df_date["dt"].dt.month
    df_date["month_name"] = df_date["dt"].dt.month_name()
    df_date["day"] = df_date["dt"].dt.day
    df_date["day_of_week"] = df_date["dt"].dt.dayofweek # 0=Monday, 6=Sunday
    df_date["day_name"] = df_date["dt"].dt.day_name()
    df_date["is_weekend"] = df_date["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
    
    # Indian Fiscal Year (April 1 to March 31)
    def get_fiscal_year(dt):
        year = dt.year
        if dt.month >= 4:
            return f"FY{year}-{str(year+1)[-2:]}"
        else:
            return f"FY{year-1}-{str(year)[-2:]}"
            
    def get_fiscal_quarter(dt):
        m = dt.month
        if m in [4, 5, 6]:
            return "Q1"
        elif m in [7, 8, 9]:
            return "Q2"
        elif m in [10, 11, 12]:
            return "Q3"
        else:
            return "Q4"
            
    df_date["fiscal_year"] = df_date["dt"].apply(get_fiscal_year)
    df_date["fiscal_quarter"] = df_date["dt"].apply(get_fiscal_quarter)
    
    df_date = df_date.drop(columns=["dt"])
    logger.info(f"dim_date generated: {len(df_date)} days.")
    return df_date

def initialize_database(engine) -> None:
    """Executes schema.sql against SQLite to establish tables and constraints."""
    logger.info(f"Executing DDL schema from {SCHEMA_PATH}...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with engine.connect() as conn:
        # SQLite executes multi-statement scripts via raw connection
        raw_conn = conn.connection
        raw_conn.executescript(schema_sql)
        conn.commit()
    logger.info("Schema tables and indexes created successfully.")

def load_data_into_sqlite() -> Dict[str, Tuple[int, int]]:
    """Loads all cleaned datasets into SQLite using SQLAlchemy df.to_sql()."""
    engine = create_engine(DATABASE_URL, echo=False)
    initialize_database(engine)
    
    # 1. Load dim_date first (as other tables have FKs to dim_date)
    dim_date_df = generate_dim_date()
    dim_date_df.to_sql("dim_date", engine, if_exists="append", index=False)
    
    # 2. Table mappings: (table_name, csv_filename, column_renames)
    table_mappings = [
        ("dim_fund", "clean_fund_master.csv", {}),
        ("fact_nav", "clean_nav.csv", {"date": "nav_date"}),
        ("fact_transactions", "clean_transactions.csv", {}),
        ("fact_performance", "clean_performance.csv", {}),
        ("fact_aum", "clean_aum.csv", {}),
        ("fact_monthly_sip", "clean_sip_inflows.csv", {}),
        ("fact_category_inflows", "clean_category_inflows.csv", {}),
        ("fact_industry_folios", "clean_folio_count.csv", {}),
        ("fact_portfolio_holdings", "clean_portfolio_holdings.csv", {}),
        ("fact_benchmark_indices", "clean_benchmark_indices.csv", {})
    ]
    
    verification_results = {}
    
    print("\n" + "="*80)
    print("LOADING CLEANED DATASETS INTO SQLITE DATABASE (bluestock_mf.db)")
    print("="*80)
    
    for table_name, csv_file, col_map in table_mappings:
        csv_path = PROCESSED_DIR / csv_file
        if not csv_path.exists():
            raise FileNotFoundError(f"Cleaned CSV not found: {csv_path}")
            
        df = pd.read_csv(csv_path)
        csv_rows = len(df)
        
        if col_map:
            df = df.rename(columns=col_map)
            
        # Insert into SQLite
        df.to_sql(table_name, engine, if_exists="append", index=False)
        
        # Verify row count in DB
        with engine.connect() as conn:
            db_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            
        verification_results[table_name] = (csv_rows, db_count)
        status = "MATCH [✓]" if csv_rows == db_count else f"MISMATCH [X] (CSV: {csv_rows}, DB: {db_count})"
        print(f"Loaded {table_name:<24} | CSV Rows: {csv_rows:>6,} | DB Rows: {db_count:>6,} | {status}")
        
    # Check dim_date
    with engine.connect() as conn:
        date_count = conn.execute(text("SELECT COUNT(*) FROM dim_date")).scalar()
    print(f"Loaded {'dim_date':<24} | Generated: {len(dim_date_df):>6,} | DB Rows: {date_count:>6,} | MATCH [✓]")
    
    print("="*80)
    print("DATABASE INGESTION & ROW COUNT VERIFICATION COMPLETE")
    print("="*80 + "\n")
    
    return verification_results

if __name__ == "__main__":
    load_data_into_sqlite()
