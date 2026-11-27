# Power BI Desktop Setup Guide (`bluestock_mf_dashboard.pbix`)

> **Note:** Microsoft Power BI Desktop (`PBIDesktop.exe`) is a Windows GUI application and is not installed in the automated build environment, so `.pbix` binary packaging must be saved inside Power BI Desktop. All 4 visual pages, `Dashboard.pdf`, `bluestock_theme.json`, and the interactive HTML/Streamlit dashboards have been generated automatically.

## 1. Connect Power BI to Data
1. Open **Power BI Desktop** -> **Get Data** -> **Text/CSV** (or **ODBC** using SQLite3 ODBC Driver pointing to `bluestock_mf.db`).
2. Import the 8 core cleaned CSVs from `data/processed/`:
   - `clean_fund_master.csv` (`dim_fund`)
   - `clean_nav.csv` (`fact_nav`)
   - `clean_aum.csv` (`fact_aum`)
   - `clean_sip_inflows.csv` (`fact_monthly_sip`)
   - `clean_category_inflows.csv` (`fact_category_inflows`)
   - `clean_folio_count.csv` (`fact_industry_folios`)
   - `clean_performance.csv` (`fact_performance`)
   - `clean_transactions.csv` (`fact_transactions`)
3. In **Model View**, create relationships:
   - `dim_fund[amfi_code]` (1) -> (*) `fact_nav[amfi_code]`
   - `dim_fund[amfi_code]` (1) -> (1) `fact_performance[amfi_code]`
   - `dim_fund[amfi_code]` (1) -> (*) `fact_transactions[amfi_code]`
   - `dim_date[date]` (1) -> (*) `fact_nav[nav_date]`, `fact_transactions[transaction_date]`, `fact_aum[date]`

## 2. Apply Bluestock Theme
- Go to **View** -> **Themes** -> **Browse for themes** -> select `dashboard/bluestock_theme.json`.

## 3. Recommended DAX Measures
```dax
Total_AUM_Lakh_Cr = SUM(fact_aum[aum_lakh_crore])
Peak_Monthly_SIP_Cr = MAX(fact_monthly_sip[sip_inflow_crore])
Total_Folios_Cr = MAX(fact_industry_folios[total_folios_crore])
Total_Tx_Cr = DIVIDE(SUM(fact_transactions[amount_inr]), 10000000)
Avg_SIP_Ticket = CALCULATE(AVERAGE(fact_transactions[amount_inr]), fact_transactions[transaction_type] = "SIP")
```

## 4. Export `.pbix`
- Build Pages 1–4 matching `dashboard/page1_industry_overview.png` through `dashboard/page4_sip_market_trends.png`, configure Drill-Through on `amfi_code` from Page 2 Scorecard to NAV Detail, and save as `dashboard/bluestock_mf_dashboard.pbix`.
