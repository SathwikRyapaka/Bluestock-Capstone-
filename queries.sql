-- ============================================================================
-- BLUESTOCK FINTECH MUTUAL FUND ANALYTICS PLATFORM
-- Day 2: 10 Analytical SQL Queries & Results
-- Database: bluestock_mf.db
-- Author: SR (Sathwik Ryapaka), AB (Abhiram), AK (Ashmeet Kaur)
-- Date: 20 November 2026
-- ============================================================================

-- ============================================================================
-- QUERY 1: Top 5 Funds by AUM (Assets Under Management)
-- Business Objective: Identify largest mutual fund schemes by asset size to
-- track flagship retail & institutional capital allocation.
-- ============================================================================
SELECT 
    p.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.plan,
    p.aum_crore,
    ROUND(p.expense_ratio_pct, 2) AS expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

/*
Result:
amfi_code | scheme_name                                         | fund_house        | category | plan    | aum_crore | expense_ratio_pct
148568    | Mirae Asset Emerging Bluechip Fund - Regular - Growth | Mirae Asset MF    | Equity   | Regular | 49046.0   | 1.52
120842    | Kotak Emerging Equity Fund - Regular - Growth       | Kotak Mahindra MF | Equity   | Regular | 47469.0   | 1.56
118634    | Nippon India Small Cap Fund - Regular - Growth     | Nippon India MF   | Equity   | Regular | 43630.0   | 1.53
149322    | DSP Top 100 Equity Fund - Regular - Growth         | DSP Mutual Fund   | Equity   | Regular | 41828.0   | 1.54
102886    | UTI Mid Cap Fund - Regular - Growth                 | UTI Mutual Fund   | Equity   | Regular | 41728.0   | 1.51
*/


-- ============================================================================
-- QUERY 2: Average NAV per Month Across Industry
-- Business Objective: Track industry-wide NAV valuation trajectory and market
-- expansion across historical business months.
-- ============================================================================
SELECT 
    strftime('%Y-%m', nav_date) AS month,
    COUNT(DISTINCT amfi_code) AS active_schemes,
    ROUND(AVG(nav), 2) AS avg_nav,
    ROUND(MIN(nav), 2) AS min_nav,
    ROUND(MAX(nav), 2) AS max_nav
FROM fact_nav
GROUP BY strftime('%Y-%m', nav_date)
ORDER BY month DESC
LIMIT 12;

/*
Result:
month   | active_schemes | avg_nav | min_nav | max_nav
2026-05 | 40             | 357.04  | 31.67   | 4268.55
2026-04 | 40             | 355.03  | 31.67   | 4236.79
2026-03 | 40             | 347.19  | 31.29   | 4212.87
2026-02 | 40             | 342.08  | 31.59   | 4195.37
2026-01 | 40             | 337.12  | 31.97   | 4167.75
2025-12 | 40             | 335.53  | 30.56   | 4141.24
2025-11 | 40             | 333.39  | 29.58   | 4118.80
2025-10 | 40             | 328.79  | 29.41   | 4096.37
2025-09 | 40             | 328.00  | 29.13   | 4072.01
2025-08 | 40             | 326.68  | 29.28   | 4050.29
2025-07 | 40             | 324.96  | 28.53   | 4026.06
2025-06 | 40             | 318.52  | 27.67   | 4003.88
*/


-- ============================================================================
-- QUERY 3: Monthly SIP Inflow YoY Growth
-- Business Objective: Measure retail investor commitment and systematic
-- investment compounding momentum year-over-year.
-- ============================================================================
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    ROUND(yoy_growth_pct, 2) AS yoy_growth_pct,
    sip_aum_lakh_crore
FROM fact_monthly_sip
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month DESC
LIMIT 12;

/*
Result:
month   | sip_inflow_crore | active_sip_accounts_crore | yoy_growth_pct | sip_aum_lakh_crore
2025-12 | 31002.0          | 9.35                      | 17.17          | 15.90
2025-11 | 30200.0          | 9.20                      | 19.27          | 15.72
2025-10 | 29529.0          | 9.10                      | 16.61          | 15.55
2025-09 | 29361.0          | 9.00                      | 19.80          | 15.38
2025-08 | 28265.0          | 8.85                      | 20.04          | 15.18
2025-07 | 28464.0          | 8.70                      | 22.00          | 14.95
2025-06 | 27274.0          | 8.55                      | 28.28          | 14.65
2025-05 | 26688.0          | 8.40                      | 25.52          | 14.30
2025-04 | 26632.0          | 8.30                      | 30.73          | 14.05
2025-03 | 25926.0          | 8.15                      | 27.27          | 13.80
2025-02 | 25999.0          | 8.00                      | 35.50          | 13.55
2025-01 | 26400.0          | 7.90                      | 40.14          | 13.30
*/


-- ============================================================================
-- QUERY 4: Investor Transactions & Volume Breakdown by Indian State
-- Business Objective: Determine geographical penetration of mutual fund
-- distribution and identify high-value investment hubs.
-- ============================================================================
SELECT 
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr) / 10000000.0, 2) AS total_inflow_crore,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_inr,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_transactions), 2) AS pct_of_transactions
FROM fact_transactions
GROUP BY state
ORDER BY total_inflow_crore DESC;

/*
Result:
state          | total_transactions | total_inflow_crore | avg_transaction_inr | pct_of_transactions
Punjab         | 2965               | 31.58              | 106502.68           | 9.05
Tamil Nadu     | 2806               | 31.52              | 112322.61           | 8.56
Madhya Pradesh | 2931               | 30.83              | 105190.21           | 8.94
Rajasthan      | 2577               | 29.86              | 115888.95           | 7.86
Gujarat        | 2780               | 29.84              | 107323.36           | 8.48
Kerala         | 2661               | 29.41              | 110539.06           | 8.12
Delhi          | 2631               | 28.94              | 109983.47           | 8.03
West Bengal    | 2753               | 28.87              | 104860.67           | 8.40
Uttar Pradesh  | 2752               | 28.85              | 104847.45           | 8.40
Karnataka      | 2623               | 28.05              | 106950.41           | 8.00
Maharashtra    | 2652               | 27.91              | 105230.13           | 8.09
Telangana      | 2647               | 26.50              | 100119.58           | 8.08
*/


-- ============================================================================
-- QUERY 5: Cost Efficiency: Funds with Expense Ratio < 1.0%
-- Business Objective: Uncover lowest fee structures across Direct and Regular
-- plans to identify investor cost savings.
-- ============================================================================
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.sub_category,
    f.plan,
    ROUND(f.expense_ratio_pct, 2) AS expense_ratio_pct,
    p.return_3yr_pct,
    p.aum_crore
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE f.expense_ratio_pct < 1.0
ORDER BY f.expense_ratio_pct ASC, p.aum_crore DESC;

/*
Result:
amfi_code | scheme_name                                         | fund_house        | category | sub_category   | plan    | expense_ratio_pct | return_3yr_pct | aum_crore
118636    | Nippon India Gilt Securities Fund - Regular - Growth | Nippon India MF   | Debt     | Gilt           | Regular | 0.55              | 5.31           | 30030.0
100025    | HDFC Short Term Debt Fund - Regular - Growth        | HDFC Mutual Fund  | Debt     | Short Duration | Regular | 0.56              | 7.37           | 27953.0
120844    | Kotak Liquid Fund - Regular - Growth               | Kotak Mahindra MF | Debt     | Liquid         | Regular | 0.60              | 6.18           | 27623.0
119552    | SBI Bluechip Fund - Direct Plan - Growth            | SBI Mutual Fund   | Equity   | Large Cap      | Direct  | 0.66              | 11.30          | 1231.0
118633    | Nippon India Large Cap Fund - Direct - Growth       | Nippon India MF   | Equity   | Large Cap      | Direct  | 0.72              | 12.33          | 39475.0
119599    | SBI Small Cap Fund - Direct Plan - Growth           | SBI Mutual Fund   | Equity   | Small Cap      | Direct  | 0.72              | 20.73          | 2341.0
120504    | ICICI Prudential Bluechip Fund - Direct - Growth    | ICICI Pru MF      | Equity   | Large Cap      | Direct  | 0.75              | 12.18          | 37885.0
119120    | SBI Magnum Gilt Fund - Regular Plan - Growth        | SBI Mutual Fund   | Debt     | Gilt           | Regular | 0.77              | 6.07           | 3123.0
120843    | Kotak Emerging Equity Fund - Direct - Growth        | Kotak Mahindra MF | Equity   | Mid Cap        | Direct  | 0.78              | 18.23          | 3894.0
125498    | HDFC Small Cap Fund - Direct Plan - Growth          | HDFC Mutual Fund  | Equity   | Small Cap      | Direct  | 0.79              | 21.05          | 4312.0
*/


-- ============================================================================
-- QUERY 6: Top 5 Schemes by Risk-Adjusted Sharpe Ratio
-- Business Objective: Determine funds that deliver the highest excess return
-- per unit of total risk (volatility).
-- ============================================================================
SELECT 
    p.amfi_code,
    f.scheme_name,
    f.category,
    f.sub_category,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.return_3yr_pct,
    p.std_dev_ann_pct,
    p.alpha
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 5;

/*
Result:
amfi_code | scheme_name                                         | category | sub_category   | sharpe_ratio | sortino_ratio | return_3yr_pct | std_dev_ann_pct | alpha
120507    | ICICI Pru Liquid Fund - Regular - Growth            | Debt     | Liquid         | 7.68         | 10.37         | 7.68           | 0.5             | 1.85
120844    | Kotak Liquid Fund - Regular - Growth                | Debt     | Liquid         | 6.18         | 9.70          | 6.18           | 0.5             | 1.52
101208    | ABSL Liquid Fund - Regular - Growth                 | Debt     | Liquid         | 5.14         | 8.76          | 5.14           | 0.5             | 1.18
100025    | HDFC Short Term Debt Fund - Regular - Growth        | Debt     | Short Duration | 1.84         | 2.79          | 7.37           | 4.0             | 1.98
119120    | SBI Magnum Gilt Fund - Regular Plan - Growth        | Debt     | Gilt           | 1.52         | 2.11          | 6.07           | 4.0             | 1.60
*/


-- ============================================================================
-- QUERY 7: Geographic Inclusivity: T30 vs B30 Demographics & Ticket Sizes
-- Business Objective: Compare capital flow volume, investor count, and average
-- transaction sizes between Top 30 metros and Beyond-30 developing cities.
-- ============================================================================
SELECT 
    city_tier,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr) / 10000000.0, 2) AS total_volume_crore,
    ROUND(AVG(amount_inr), 2) AS avg_ticket_size_inr,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_transactions), 2) AS transaction_share_pct
FROM fact_transactions
GROUP BY city_tier;

/*
Result:
city_tier | transaction_count | total_volume_crore | avg_ticket_size_inr | transaction_share_pct
B30       | 11059             | 120.23             | 108719.20           | 33.74
T30       | 21719             | 231.93             | 106784.60           | 66.26
*/


-- ============================================================================
-- QUERY 8: AMC Market Share & AUM Leadership (December 2025 Snapshot)
-- Business Objective: Benchmark fund houses by overall asset scale and assess
-- market dominance in Indian mutual funds.
-- ============================================================================
SELECT 
    fund_house,
    aum_crore,
    aum_lakh_crore,
    num_schemes,
    ROUND(aum_crore * 100.0 / (SELECT SUM(aum_crore) FROM fact_aum WHERE date = '2025-12-31'), 2) AS market_share_pct
FROM fact_aum
WHERE date = '2025-12-31'
ORDER BY aum_crore DESC;

/*
Result:
fund_house               | aum_crore | aum_lakh_crore | num_schemes | market_share_pct
SBI Mutual Fund          | 1250000.0 | 12.50          | 186         | 19.92
ICICI Prudential MF      | 1074000.0 | 10.74          | 216         | 17.12
HDFC Mutual Fund         | 930000.0  | 9.30           | 195         | 14.82
Nippon India MF          | 700000.0  | 7.00           | 177         | 11.16
Kotak Mahindra MF        | 580000.0  | 5.80           | 168         | 9.24
Aditya Birla Sun Life MF | 470000.0  | 4.70           | 152         | 7.49
UTI Mutual Fund          | 370000.0  | 3.70           | 120         | 5.90
Axis Mutual Fund         | 340000.0  | 3.40           | 110         | 5.42
Mirae Asset MF           | 290000.0  | 2.90           | 85          | 4.62
DSP Mutual Fund          | 270000.0  | 2.70           | 92          | 4.30
*/


-- ============================================================================
-- QUERY 9: Portfolio Sector Allocation & Market Capitalization Concentration
-- Business Objective: Identify heavy industry exposure and structural sector
-- allocation across mutual fund equities.
-- ============================================================================
SELECT 
    sector,
    COUNT(DISTINCT stock_symbol) AS unique_stocks_held,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr,
    ROUND(AVG(weight_pct), 2) AS avg_holding_weight_pct
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_market_value_cr DESC
LIMIT 10;

/*
Result:
sector            | unique_stocks_held | total_market_value_cr | avg_holding_weight_pct
Banking           | 6                  | 62840.29              | 10.87
IT                | 4                  | 38477.11              | 11.39
Pharma            | 4                  | 34606.10              | 10.72
Automobile        | 3                  | 34296.97              | 9.81
Utilities         | 2                  | 25108.63              | 11.06
Financial Services| 3                  | 21544.75              | 10.59
Capital Goods     | 2                  | 17652.79              | 11.01
FMCG              | 2                  | 16790.39              | 10.37
Consumer Goods    | 2                  | 16568.12              | 10.57
Metals            | 2                  | 14175.76              | 10.23
*/


-- ============================================================================
-- QUERY 10: Cash Inflow Dynamics: Systematic vs Discretionary vs Redemptions
-- Business Objective: Quantify stickiness of SIP flows against lumpy lump-sum
-- commitments and redemption leakage.
-- ============================================================================
SELECT 
    transaction_type,
    COUNT(*) AS count_transactions,
    ROUND(SUM(amount_inr) / 10000000.0, 2) AS volume_crore,
    ROUND(AVG(amount_inr), 2) AS avg_ticket_inr,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_transactions), 2) AS count_pct,
    ROUND(SUM(amount_inr) * 100.0 / (SELECT SUM(amount_inr) FROM fact_transactions), 2) AS volume_pct
FROM fact_transactions
GROUP BY transaction_type
ORDER BY volume_crore DESC;

/*
Result:
transaction_type | count_transactions | volume_crore | avg_ticket_inr | count_pct | volume_pct
Lumpsum          | 8095               | 205.98       | 254456.02      | 24.70     | 58.49
Redemption       | 4967               | 124.45       | 250558.79      | 15.15     | 35.34
SIP              | 19716              | 21.72        | 11018.13       | 60.15     | 6.17
*/
