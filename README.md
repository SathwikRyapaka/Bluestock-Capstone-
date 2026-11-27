# Bluestock Fintech — Mutual Fund Analytics Platform
### End-to-End Data Engineering, ETL Pipeline, Risk Analytics & Interactive BI Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite3-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-darkblue.svg)
![Release](https://img.shields.io/badge/Release-v1.0-success.svg)

---

## 📌 Project Overview
Bluestock Fintech is democratising investment analytics for retail and institutional investors in India. This capstone project delivers an end-to-end **Mutual Fund Analytics Platform** that ingests AMFI historical datasets and live `mfapi.in` REST feeds, cleans and normalises them into an 11-table **SQLite Star Schema**, generates **16 publication-quality EDA visualizations**, computes institutional **risk metrics (Historical VaR/CVaR, Rolling 90-day Sharpe, Sector HHI, SIP Churn)**, and serves an **interactive HTML5 BI Dashboard** alongside a **Sharpe-optimized Fund Recommender**.

---

## 👥 Project Team
- **Sathwik Ryapaka (SR)** — Data Analyst Intern
- **Abhiram (AB)** — Data Analyst Intern
- **Ashmeet Kaur (AK)** — Data Analyst Intern

---

## 📊 Dataset Descriptions (10 Core Sources + Live API)

| Dataset | Rows | Description |
| :--- | :---: | :--- |
| `01_fund_master.csv` | 40 | Master scheme metadata: AMFI code, AMC, SEBI category/sub-category, plan, expense ratio, exit load. |
| `02_nav_history.csv` | 46,000 | Daily NAV time series (2022–2026) across all 40 schemes; cleaned with holiday forward-fill & `daily_return`. |
| `03_aum_by_fund_house.csv` | 90 | Annual Assets Under Management (AUM) by AMC in ₹ Lakh Crore and ₹ Crore (2022–2025). |
| `04_monthly_sip_inflows.csv` | 48 | Monthly industry SIP inflows (₹ Cr), active SIP accounts (Cr), and YoY growth (Jan 2022 – Dec 2025). |
| `05_category_inflows.csv` | 144 | Monthly net mutual fund inflows across 12 SEBI categories. |
| `06_industry_folio_count.csv` | 21 | Quarterly/periodic industry folio expansion across Equity, Debt, Hybrid, and Others (13.26 Cr → 26.12 Cr). |
| `07_scheme_performance.csv` | 40 | Scheme-level 1Y/3Y/5Y CAGR, Alpha, Beta, Sharpe, Sortino, Max Drawdown, and Morningstar rating. |
| `08_investor_transactions.csv` | 32,778 | Retail transaction logs (`SIP`, `Lumpsum`, `Redemption`), state, T30/B30 city tier, age, gender, KYC status. |
| `09_portfolio_holdings.csv` | 322 | Underlying equity stock holdings, sector weights (%), and market value (₹ Cr). |
| `10_benchmark_indices.csv` | 8,050 | Daily benchmark index values (Nifty 50, Nifty Midcap 150, Nifty Smallcap 250, TRI). |
| **Live Feed (`mfapi.in`)** | Dynamic | Real-time JSON NAV feed via `live_nav_fetch.py` for 6 flagship schemes (`125497`, `119551`, `120503`, `118632`, `119092`, `120841`). |

---

## 🗂 Repository Structure
```text
Bluestock-Capstone/
├── data/
│   ├── raw/                        # 10 raw AMFI CSVs + live mfapi.in CSVs
│   └── processed/                  # 10 cleaned & standardized CSVs
├── dashboard/
│   ├── generate_dashboard.py       # Interactive HTML5/Plotly dashboard & preview generator
│   └── bluestock_dashboard.html    # Self-contained BI dashboard (open in any browser)
├── notebooks/
│   ├── 01_data_ingestion_and_exploration.ipynb
│   ├── 02_data_cleaning_and_database.ipynb
│   ├── EDA_Analysis.ipynb
│   └── Advanced_Analytics.ipynb
├── reports/
│   ├── figures/                    # 16 EDA PNGs + 2 dashboard screenshots
│   ├── data_quality_summary.md     # Day 1 AMFI integrity & anomaly audit
│   ├── generate_final_report.py    # 16-page Final_Report.pdf generator
│   └── generate_presentation.py    # 12-slide PowerPoint generator
├── sql/
│   ├── schema.sql                  # SQLite Star Schema DDL (11 tables + indexes)
│   └── queries.sql                 # 10 analytical SQL queries
├── run_pipeline.py                 # Master end-to-end execution script
├── data_ingestion.py               # Batch ingestion & AMFI validation
├── live_nav_fetch.py               # Live mfapi.in REST API fetcher
├── data_cleaning.py                # Cleaning & feature engineering
├── load_to_sqlite.py               # SQLAlchemy Star Schema warehouse loader
├── generate_eda_charts.py          # 16-chart EDA engine
├── generate_advanced_analytics.py  # VaR/CVaR, Rolling Sharpe, Cohorts, Churn, HHI
├── recommender.py                  # CLI & importable Fund Recommendation Engine
├── bluestock_mf.db                 # SQLite Star Schema Warehouse
├── Final_Report.pdf                # 16-page Executive Capstone Report
├── Bluestock_MF_Presentation.pptx  # 12-slide Executive Presentation
├── data_dictionary.md              # Full warehouse schema & business definitions
└── requirements.txt                # Python dependencies
```

---

## 🛠 Setup & How to Run the ETL Pipeline

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/SathwikRyapaka/Bluestock-Capstone-.git
cd Bluestock-Capstone-
pip install -r requirements.txt
```

### 2. Run the Master Pipeline (`run_pipeline.py`)
Execute the complete end-to-end pipeline (Ingestion → Live API → Cleaning → SQLite Load → EDA Charts → Risk Analytics → Dashboard → Recommender):
```bash
# Full run (requires internet for mfapi.in)
python run_pipeline.py

# Offline / fast run (skips live mfapi.in REST calls)
python run_pipeline.py --skip-live-api
```

### 3. Run Individual Stages or Recommender
```bash
# Run Mutual Fund Recommender for Low / Moderate / High risk
python recommender.py --risk Moderate --top 3

# Execute analytical SQL queries
sqlite3 bluestock_mf.db < queries.sql
```

---

## 📈 How to Open the Interactive Dashboard
1. Ensure the pipeline or dashboard generator has run:
   ```bash
   python dashboard/generate_dashboard.py
   ```
2. Open [`dashboard/bluestock_dashboard.html`](dashboard/bluestock_dashboard.html) directly in **Google Chrome, Edge, or Firefox** (no local server required).
3. Explore interactive KPI cards, AMC AUM bars, Monthly SIP trajectory, State-wise retail inflows, Sector Allocation donut, and 95% VaR/CVaR comparisons.

---

## 🏆 Final Capstone Deliverables
- **Master Report:** [`Final_Report.pdf`](Final_Report.pdf) (16 pages covering Executive Summary, ETL Design, 16 EDA Figures, Risk Metrics, Dashboard Screenshots, Limitations & Recommendations)
- **Executive Deck:** [`Bluestock_MF_Presentation.pptx`](Bluestock_MF_Presentation.pptx) (12 slides)
- **Warehouse & Dictionary:** [`bluestock_mf.db`](bluestock_mf.db), [`schema.sql`](schema.sql), [`queries.sql`](queries.sql), [`data_dictionary.md`](data_dictionary.md)
- **Notebooks:** [`EDA_Analysis.ipynb`](EDA_Analysis.ipynb) & [`Advanced_Analytics.ipynb`](Advanced_Analytics.ipynb)
- **Risk Reports:** [`var_cvar_report.csv`](var_cvar_report.csv), [`rolling_sharpe_chart.png`](rolling_sharpe_chart.png), [`cohort_analysis.csv`](cohort_analysis.csv), [`sip_continuity.csv`](sip_continuity.csv), [`sector_hhi.csv`](sector_hhi.csv)
