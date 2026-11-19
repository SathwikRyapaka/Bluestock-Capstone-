# Bluestock Mutual Fund Analytics Platform - Data Quality Summary (Day 1)

**Date:** 19 November 2026  
**Phase:** Day 1 - Data Ingestion & Quality Audit  
**Team:** SR (Sathwik Ryapaka), AB (Abhiram), AK (Ashmeet Kaur)  

---

## 1. Executive Summary
All 10 required CSV datasets have been successfully ingested and audited. The dataset collection provides comprehensive coverage of fund master metadata, daily NAV history (4.5+ years), AMC AUM distributions, industry SIP trends, investor demographic transactions, portfolio constituent holdings, and benchmark index histories.

## 2. Dataset Ingestion Overview

| # | Dataset Name | File Name | Rows | Columns | Status |
|---|--------------|-----------|------|---------|--------|
| 1 | fund_master | `01_fund_master.csv` | 40 | 15 | Verified Clean |
| 2 | nav_history | `02_nav_history.csv` | 46,000 | 3 | 1 Item(s) Flagged |
| 3 | aum_by_fund_house | `03_aum_by_fund_house.csv` | 90 | 5 | Verified Clean |
| 4 | monthly_sip_inflows | `04_monthly_sip_inflows.csv` | 48 | 6 | 1 Item(s) Flagged |
| 5 | category_inflows | `05_category_inflows.csv` | 144 | 3 | Verified Clean |
| 6 | industry_folio_count | `06_industry_folio_count.csv` | 21 | 6 | Verified Clean |
| 7 | scheme_performance | `07_scheme_performance.csv` | 40 | 19 | Verified Clean |
| 8 | investor_transactions | `08_investor_transactions.csv` | 32,778 | 13 | 1 Item(s) Flagged |
| 9 | portfolio_holdings | `09_portfolio_holdings.csv` | 322 | 8 | Verified Clean |
| 10 | benchmark_indices | `10_benchmark_indices.csv` | 8,050 | 3 | Verified Clean |

## 3. Referential Integrity & AMFI Code Validation

- **Total Fund Master Schemes:** 40
- **Schemes Represented in NAV History:** 40
- **Codes in Fund Master Missing in NAV History:** 0
- **Orphaned Codes in Investor Transactions:** 0

> **Validation Result:** [PASS] Every AMFI scheme code present in `fund_master` exists in `nav_history`. Perfect 1:N referential relationship confirmed.

## 4. Key Fund Master Dimensions

- **Unique Fund Houses (10):** Aditya Birla Sun Life MF, Axis Mutual Fund, DSP Mutual Fund, HDFC Mutual Fund, ICICI Prudential MF, Kotak Mahindra MF, Mirae Asset MF, Nippon India MF, SBI Mutual Fund, UTI Mutual Fund
- **Categories (2):** Debt, Equity
- **Sub-Categories (12):** ELSS, Flexi Cap, Gilt, Index, Index/ETF, Large & Mid Cap, Large Cap, Liquid, Mid Cap, Short Duration, Small Cap, Value
- **Risk Grades (5):** High, Low, Moderate, Moderately High, Very High

## 5. Identified Data Anomalies & Recommendations for Day 2 Cleaning

### `02_nav_history.csv`
- Date column is stored as string/object, needs parsing to datetime

### `04_monthly_sip_inflows.csv`
- Missing values in 'yoy_growth_pct': 12 rows (25.0%)

### `08_investor_transactions.csv`
- Transaction date is stored as string/object

## 6. Action Items for Day 2 (Data Cleaning & SQL Database Design)
1. **Date Standardisation:** Convert string dates across `nav_history`, `investor_transactions`, `benchmark_indices`, and `fund_master` into standard `YYYY-MM-DD` ISO format.
2. **Missing Holiday Handling:** Implement calendar forward-fill (`ffill`) on `nav_history` to handle market holidays and weekends.
3. **Transaction KYC Validation:** Verify clean categorisation for investor demographics and KYC flags.
4. **Relational Database Design:** Load clean data into normalized SQLite star schema (`dim_fund`, `fact_nav`, `fact_transactions`, `fact_performance`).
