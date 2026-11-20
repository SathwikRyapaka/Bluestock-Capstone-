# Bluestock Fintech — Mutual Fund Analytics Platform
### End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite3-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-darkblue.svg)
![Status](https://img.shields.io/badge/Status-Day%202%20Complete-success.svg)

---

## 📌 Project Overview
Bluestock Fintech is democratising investment analytics for retail and institutional investors in India. This capstone project builds an enterprise-grade Mutual Fund Analytics Platform that ingests publicly available AMFI data and live API feeds, transforms them through a robust ETL pipeline, normalises data into a relational Star Schema, and generates analytical insights and interactive visual dashboards.

---

## 👥 Project Team & Contributors
- **Sathwik Ryapaka (SR)** — Data Analyst Intern
- **Abhiram (AB)** — Data Analyst Intern
- **Ashmeet Kaur (AK)** — Data Analyst Intern

---

## 🗂 Project Directory Structure
```text
Bluestock-Capstone/
│
├── data/
│   ├── raw/                  # 10 raw AMFI CSVs + Live mfapi.in API feeds
│   └── processed/            # 10 cleaned & validated CSVs
│       ├── 01_clean_fund_master.csv / clean_fund_master.csv
│       ├── 02_clean_nav_history.csv / clean_nav.csv
│       ├── 03_clean_aum_by_fund_house.csv / clean_aum.csv
│       ├── 04_clean_monthly_sip_inflows.csv / clean_sip_inflows.csv
│       ├── 05_clean_category_inflows.csv / clean_category_inflows.csv
│       ├── 06_clean_industry_folio_count.csv / clean_folio_count.csv
│       ├── 07_clean_scheme_performance.csv / clean_performance.csv
│       ├── 08_clean_investor_transactions.csv / clean_transactions.csv
│       ├── 09_clean_portfolio_holdings.csv / clean_portfolio_holdings.csv
│       └── 10_clean_benchmark_indices.csv / clean_benchmark_indices.csv
│
├── notebooks/                # Jupyter exploration and analytical notebooks
│   ├── 01_data_ingestion_and_exploration.ipynb
│   └── 02_data_cleaning_and_database.ipynb
│
├── sql/                      # DDL schemas, migrations, and analytical queries
│   ├── schema.sql
│   └── queries.sql
│
├── dashboard/                # BI dashboards (Power BI / Tableau / Streamlit)
│
├── reports/                  # Data quality audits, markdown summaries, and reports
│   └── data_quality_summary.md
│
├── data_ingestion.py         # Batch ingestion, profiling, and AMFI code validation
├── live_nav_fetch.py         # Live NAV ingestion pipeline from mfapi.in REST API
├── data_cleaning.py          # Data cleaning and transformation pipeline
├── load_to_sqlite.py         # Star schema database loader with SQLAlchemy
├── bluestock_mf.db           # SQLite Relational Database (Star Schema)
├── schema.sql                # Star schema DDL definition
├── queries.sql               # 10 business analytical SQL queries with results
├── data_dictionary.md        # Comprehensive data dictionary for all tables
├── requirements.txt          # Project dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

---

## 🚀 Progress & Deliverables

### Day 1: Project Setup + Data Ingestion (ETL)
- Built standardised directory structure (`data/raw/`, `data/processed/`, `notebooks/`, `sql/`, `dashboard/`, `reports/`).
- Ingested all 10 mutual fund datasets from AMFI and market sources.
- Built live NAV REST API ingestion pipeline (`live_nav_fetch.py`) fetching real-time feeds from `mfapi.in`.
- Documented AMFI scheme code structural hierarchy and verified 100% referential integrity.
- Published [`reports/data_quality_summary.md`](reports/data_quality_summary.md) and [`notebooks/01_data_ingestion_and_exploration.ipynb`](notebooks/01_data_ingestion_and_exploration.ipynb).

---

### Day 2: Data Cleaning + SQL Database Design
- **1. Data Cleaning Pipeline ([`data_cleaning.py`](data_cleaning.py)):**
  - **`nav_history`:** Parsed dates to datetime, sorted by `amfi_code` + `date`, forward-filled missing NAV values per scheme, verified zero duplicates, validated `NAV > 0`, and computed `daily_return` (%). Produced `clean_nav.csv` (46,000 rows).
  - **`investor_transactions`:** Standardised `transaction_type` (`SIP`, `Lumpsum`, `Redemption`), validated `amount_inr > 0`, formatted dates to ISO `YYYY-MM-DD`, validated KYC enum status (`Verified` 92%, `Pending` 8%). Produced `clean_transactions.csv` (32,778 rows).
  - **`scheme_performance`:** Ensured all 11 return and risk metrics are numeric, verified `expense_ratio_pct` within 0.1%–2.5%, flagged anomalies (e.g., Liquid funds with high Sharpe due to low volatility). Produced `clean_performance.csv` (40 schemes).
  - **All Remaining Datasets Cleaned:** Exported all 10 datasets into [`data/processed/`](data/processed/).
- **2. Relational Star Schema ([`schema.sql`](schema.sql)):**
  - Designed normalized dimensional model with explicit primary and foreign keys:
    - **Dimensions:** `dim_fund`, `dim_date` (2,557 days with calendar & Indian fiscal year attributes).
    - **Core Facts:** `fact_nav` (46,000 rows), `fact_transactions` (32,778 rows), `fact_performance` (40 rows), `fact_aum` (90 rows).
    - **Supporting Facts:** `fact_monthly_sip`, `fact_category_inflows`, `fact_industry_folios`, `fact_portfolio_holdings`, `fact_benchmark_indices`.
    - Performance optimization indexes created for analytical speed.
- **3. Automated SQLite Loader ([`load_to_sqlite.py`](load_to_sqlite.py)):**
  - Loaded all datasets into `bluestock_mf.db` using SQLAlchemy `create_engine()` + `df.to_sql()`.
  - Confirmed **100% exact row count match** between source CSVs and database tables.
- **4. Analytical SQL Queries ([`queries.sql`](queries.sql)):**
  - Authored and verified 10 core analytical queries with business context:
    1. Top 5 Funds by AUM
    2. Average NAV per Month Across Industry
    3. Monthly SIP Inflow YoY Growth
    4. Investor Transactions & Volume Breakdown by Indian State
    5. Funds with Expense Ratio < 1.0%
    6. Top 5 Schemes by Risk-Adjusted Sharpe Ratio
    7. Geographic Inclusivity: T30 vs B30 Demographics & Ticket Sizes
    8. AMC Market Share & AUM Leadership (Dec 2025 Snapshot)
    9. Portfolio Sector Allocation & Market Capitalization Concentration
    10. Cash Inflow Dynamics: Systematic vs Discretionary vs Redemptions
- **5. Comprehensive Data Dictionary ([`data_dictionary.md`](data_dictionary.md)):**
  - Documented entity relationships (Mermaid diagram), data types, constraints, business definitions, and official data sources for every column.

---

## 🛠 Quickstart Guide

### 1. Installation
Clone repository and install requirements:
```bash
git clone https://github.com/SathwikRyapaka/Bluestock-Capstone-.git
cd Bluestock-Capstone-
pip install -r requirements.txt
```

### 2. Run Data Ingestion & Cleaning
```bash
# Day 1 Batch Ingestion & Validation
python data_ingestion.py

# Day 1 Live NAV Fetch
python live_nav_fetch.py

# Day 2 Data Cleaning Pipeline
python data_cleaning.py
```

### 3. Build SQLite Database
```bash
python load_to_sqlite.py
```

### 4. Execute Analytical Queries
```bash
sqlite3 bluestock_mf.db < queries.sql
```

---

## 📅 Next Phase (Day 3 Preview)
- Exploratory Data Analysis (EDA) on NAV and AUM distributions.
- Advanced correlation, rolling volatility, and drawdowns.
- Interactive visualizations and time-series trend breakdowns.
