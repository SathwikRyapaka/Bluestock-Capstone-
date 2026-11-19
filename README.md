# Bluestock Fintech — Mutual Fund Analytics Platform
### End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-darkblue.svg)
![Status](https://img.shields.io/badge/Status-Day%201%20Complete-success.svg)

---

## 📌 Project Overview
Bluestock Fintech is democratising investment analytics for retail and institutional investors in India. This capstone project builds an enterprise-grade Mutual Fund Analytics Platform that ingests publicly available AMFI data and live API feeds, transforms them through a robust ETL pipeline, normalises data into a relational schema, and generates analytical insights and interactive visual dashboards.

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
│   ├── raw/                  # Raw ingested AMFI CSVs + Live mfapi.in feeds
│   └── processed/            # Cleaned, standardized datasets (Day 2 onwards)
│
├── notebooks/                # Jupyter exploration and analytics notebooks
│   └── 01_data_ingestion_and_exploration.ipynb
│
├── sql/                      # DDL schemas, migrations, and analytical queries
│
├── dashboard/                # BI dashboards (Power BI / Tableau / Streamlit)
│
├── reports/                  # Data quality audits, markdown summaries, and documentation
│   └── data_quality_summary.md
│
├── data_ingestion.py         # Batch ingestion, profiling, and AMFI code validation
├── live_nav_fetch.py         # Live NAV ingestion pipeline from mfapi.in REST API
├── requirements.txt          # Project dependencies
├── .gitignore                # Git ignore rules (excluding .db files & checkpoints)
└── README.md                 # Project documentation
```

---

## 🚀 Day 1 Deliverables & Completed Tasks

### 1. Environment & Architecture Setup
- Built standardised directory structure (`data/raw/`, `data/processed/`, `notebooks/`, `sql/`, `dashboard/`, `reports/`).
- Configured dependencies in `requirements.txt` (`pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `sqlalchemy`, `requests`, `scipy`, `jupyter`).

### 2. Multi-Dataset Ingestion & Quality Audit (`data_ingestion.py`)
- Ingested all 10 mutual fund datasets from AMFI and market sources:
  1. `01_fund_master.csv` (40 schemes x 15 columns)
  2. `02_nav_history.csv` (46,000 records x 3 columns)
  3. `03_aum_by_fund_house.csv` (90 records x 5 columns)
  4. `04_monthly_sip_inflows.csv` (48 months x 6 columns)
  5. `05_category_inflows.csv` (144 records x 3 columns)
  6. `06_industry_folio_count.csv` (21 records x 6 columns)
  7. `07_scheme_performance.csv` (40 schemes x 19 metrics)
  8. `08_investor_transactions.csv` (32,778 transactions x 13 columns)
  9. `09_portfolio_holdings.csv` (322 stock allocations x 8 columns)
  10. `10_benchmark_indices.csv` (8,050 market index records x 3 columns)
- Profiled `.shape`, `.dtypes`, missing values, and potential anomalies.
- Generated [`reports/data_quality_summary.md`](reports/data_quality_summary.md).

### 3. Live NAV Ingestion Pipeline (`live_nav_fetch.py`)
- Built a REST API ingestion pipeline connecting to `https://api.mfapi.in/mf/`.
- Successfully fetched historical and live daily NAVs for:
  - **HDFC Top 100 Direct** (`125497`)
  - **SBI Bluechip Fund** (`119551`)
  - **ICICI Prudential Bluechip** (`120503`)
  - **Nippon India Large Cap** (`118632`)
  - **Axis Bluechip Fund** (`119092`)
  - **Kotak Bluechip Fund** (`120841`)
- Stored raw fetched data in `data/raw/` in individual and consolidated CSV formats.

### 4. Fund Master Exploration & AMFI Code Architecture
- Explored 10 Fund Houses, 2 Broad Categories (Equity & Debt), 12 Sub-Categories, and 5 SEBI Riskometer grades.
- Documented AMFI scheme code structural hierarchy (6-digit primary key mapping across AMCs, RTAs, and stock exchanges, distinguishing Direct vs. Regular and Growth vs. IDCW options).
- **Referential Integrity Audit:** Confirmed that **100% of AMFI scheme codes** in `fund_master` exist in `nav_history` with zero orphaned records.

---

## 🛠 Quickstart Guide

### 1. Installation
Clone the repository and install required packages:
```bash
git clone https://github.com/SathwikRyapaka/Bluestock-Capstone-.git
cd Bluestock-Capstone-
pip install -r requirements.txt
```

### 2. Ingest and Validate Data
Run the full ingestion and data quality audit:
```bash
python data_ingestion.py
```

### 3. Fetch Live NAV from mfapi.in
Fetch live NAV feeds for target schemes:
```bash
python live_nav_fetch.py
```

### 4. Run Interactive Notebook
```bash
jupyter notebook notebooks/01_data_ingestion_and_exploration.ipynb
```

---

## 📅 Next Phase (Day 2 Preview)
- Data cleaning pipeline (handling dates, holiday NAV forward-fills, and transaction sanitisation).
- Star schema relational database design (`dim_fund`, `fact_nav`, `fact_transactions`, `fact_performance`).
- Loading cleaned records into SQLite / PostgreSQL database.
- Writing 10 core analytical SQL queries.
