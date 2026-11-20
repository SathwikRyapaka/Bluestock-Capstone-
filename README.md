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
├── generate_eda_charts.py    # Exploratory data analysis 16-chart generator
├── generate_advanced_analytics.py # Advanced analytics & risk metrics generator
├── recommender.py            # Quantitative fund recommendation engine
├── bluestock_mf.db           # SQLite Relational Database (Star Schema)
├── schema.sql                # Star schema DDL definition
├── queries.sql               # 10 business analytical SQL queries with results
├── data_dictionary.md        # Comprehensive data dictionary for all tables
├── EDA_Analysis.ipynb        # Exploratory Data Analysis notebook (16+ charts)
├── Advanced_Analytics.ipynb  # Advanced analytics notebook with 5 insights
├── var_cvar_report.csv       # Historical VaR (95%) and CVaR for all 40 schemes
├── rolling_sharpe_chart.png  # 90-day rolling Sharpe ratio visualization
├── cohort_analysis.csv       # Investor vintage cohort metrics
├── sip_continuity.csv        # SIP gap and churn risk analytics
├── sector_hhi.csv            # Sector concentration HHI scores
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
  - Designed normalized dimensional model with explicit primary and foreign keys (`dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, plus supporting facts).
- **3. Automated SQLite Loader ([`load_to_sqlite.py`](load_to_sqlite.py)):**
  - Loaded all datasets into `bluestock_mf.db` with 100% exact row count match.
- **4. Analytical SQL Queries ([`queries.sql`](queries.sql)):**
  - Authored and verified 10 core analytical queries with business context.
- **5. Comprehensive Data Dictionary ([`data_dictionary.md`](data_dictionary.md)):**
  - Documented entity relationships (Mermaid diagram), data types, constraints, and business definitions.

---

### Day 3: Exploratory Data Analysis (EDA)
- **1. Publication-Quality Chart Engine ([`generate_eda_charts.py`](generate_eda_charts.py)):**
  - Generated **16 high-resolution analytical figures** exported to [`reports/figures/`](reports/figures/):
    1. `01_nav_trend_all_schemes.png`: Daily NAV trajectories (40 schemes) highlighting the 2023 Bull Run and 2024 Market Volatility.
    2. `02_nav_category_performance.png`: Small Cap (+118.4%), Mid Cap (+92.1%), Large Cap (+54.2%), and Liquid category comparisons.
    3. `03_aum_growth_by_amc.png`: Grouped AUM bar chart highlighting SBI Mutual Fund's ₹12.50L Crore market leadership.
    4. `04_amc_market_share_pie.png`: AMC market footprint distribution (SBI 19.92%, ICICI Pru 17.12%, HDFC 14.82%).
    5. `05_monthly_sip_inflows_trend.png`: Monthly SIP inflow time series annotating the ₹31,002 Crore all-time high (Dec 2025).
    6. `06_sip_yoy_growth_trend.png`: Annualized SIP velocity sustaining positive YoY growth across all months (avg +27.6%).
    7. `07_category_inflow_heatmap.png`: High-density Seaborn heatmap tracking capital rotation into Mid/Small/Flexi Cap.
    8. `08_investor_age_distribution.png`: Retail age demographic breakdown (millennial age 26–35 dominance at 35.4%).
    9. `09_sip_amount_by_age_boxplot.png`: SIP installment ticket size boxplot across age brackets (peak median ₹12,450 for age 36–45).
    10. `10_investor_gender_income_split.png`: Investor gender split and income distribution.
    11. `11_geographic_sip_inflows_state.png`: Capital inflow bar chart across 12 Indian states (Punjab, Tamil Nadu, MP leading).
    12. `12_city_tier_t30_b30_split.png`: T30 (₹231.9 Cr) vs B30 (₹120.2 Cr) capital allocation comparison.
    13. `13_industry_folio_growth.png`: Industry folio count doubling from 13.26 Cr to 26.12 Cr accounts.
    14. `14_nav_return_correlation_matrix.png`: Pairwise Pearson return correlation matrix across 10 diverse schemes.
    15. `15_sector_allocation_donut.png`: Portfolio concentration across sectors (Banking 23.2%, IT 14.2%, Pharma 12.8%).
    16. `16_top_equity_stock_holdings.png`: Top 10 underlying stock allocations by portfolio market value.
- **2. Interactive EDA Notebook ([`EDA_Analysis.ipynb`](EDA_Analysis.ipynb)):**
  - Fully self-contained notebook featuring code, Plotly interactive visualizations, and **10 structured EDA business findings**.

---

### Advanced Analytics + Risk Metrics (Day 6)
- **1. Historical VaR (95%) & Conditional VaR (Expected Shortfall):**
  - Computed for all 40 schemes. Documented tail loss severity in [`var_cvar_report.csv`](var_cvar_report.csv). Small Cap schemes show highest downside exposure (VaR: -2.69%, CVaR: -3.24%).
- **2. Dynamic Rolling 90-Day Sharpe Ratio:**
  - Evaluated rolling Sharpe trends over 1,061 rolling windows for 5 key schemes (SBI Bluechip, ICICI Bluechip, Nippon Large Cap, Axis Bluechip, Kotak Bluechip).
  - Visualized and exported to [`rolling_sharpe_chart.png`](rolling_sharpe_chart.png).
- **3. Investor Cohort Analysis ([`cohort_analysis.csv`](cohort_analysis.csv)):**
  - Grouped investors by first transaction year (2024 vs 2025). 2024 cohort accounts for ₹349.11 Cr across 4,803 investors; 2025 cohort demonstrates higher average SIP size (₹13,505).
- **4. SIP Continuity & Churn Risk ([`sip_continuity.csv`](sip_continuity.csv)):**
  - Tracked installment gap intervals for 1,362 investors with 6+ SIPs. Flagged 1,332 investors with average gap > 35 days as "At-Risk".
- **5. Simple Fund Recommender ([`recommender.py`](recommender.py)):**
  - Interactive and CLI tool recommending top 3 funds by Sharpe ratio within matching risk categories (`Low`, `Moderate`, `High`).
- **6. Sector HHI Concentration ([`sector_hhi.csv`](sector_hhi.csv)):**
  - Computed Herfindahl-Hirschman Index across 34 equity funds. Axis Bluechip has the highest HHI (2,967.69) due to a 48.7% IT weighting.
- **7. Advanced Analytics Notebook ([`Advanced_Analytics.ipynb`](Advanced_Analytics.ipynb)):**
  - Contains complete code, interactive plots, and 5 detailed business insights.

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
