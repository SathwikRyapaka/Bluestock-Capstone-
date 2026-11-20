-- ============================================================================
-- BLUESTOCK FINTECH MUTUAL FUND ANALYTICS PLATFORM
-- SQLite Star Schema DDL Definition
-- Database: bluestock_mf.db
-- Phase: Day 2 - Data Engineering & Relational Warehouse Architecture
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. DIMENSION TABLES
-- ----------------------------------------------------------------------------

-- Dimension: Fund Master (dim_fund)
DROP TABLE IF EXISTS dim_fund;
CREATE TABLE dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    launch_date TEXT,
    benchmark TEXT NOT NULL,
    expense_ratio_pct REAL NOT NULL,
    exit_load_pct REAL NOT NULL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- Dimension: Date Dimension (dim_date)
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend INTEGER NOT NULL,
    fiscal_year TEXT NOT NULL,
    fiscal_quarter TEXT NOT NULL
);

-- ----------------------------------------------------------------------------
-- 2. CORE FACT TABLES
-- ----------------------------------------------------------------------------

-- Fact: Daily NAV History (fact_nav)
DROP TABLE IF EXISTS fact_nav;
CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    nav_date TEXT NOT NULL,
    nav REAL NOT NULL CHECK(nav > 0),
    daily_return REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (nav_date) REFERENCES dim_date(date) ON DELETE CASCADE,
    UNIQUE(amfi_code, nav_date)
);

-- Fact: Investor Transactions (fact_transactions)
DROP TABLE IF EXISTS fact_transactions;
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    amfi_code TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount_inr REAL NOT NULL CHECK(amount_inr > 0),
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    city_tier TEXT NOT NULL CHECK(city_tier IN ('T30', 'B30')),
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT NOT NULL CHECK(kyc_status IN ('Verified', 'Pending')),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date) ON DELETE CASCADE
);

-- Fact: Scheme Performance & Risk Metrics (fact_performance)
DROP TABLE IF EXISTS fact_performance;
CREATE TABLE fact_performance (
    amfi_code TEXT PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    plan TEXT NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL CHECK(expense_ratio_pct BETWEEN 0.1 AND 2.5),
    morningstar_rating INTEGER,
    risk_grade TEXT,
    anomaly_flag INTEGER DEFAULT 0,
    anomaly_description TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE
);

-- Fact: AUM by Fund House (fact_aum)
DROP TABLE IF EXISTS fact_aum;
CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL NOT NULL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER NOT NULL,
    FOREIGN KEY (date) REFERENCES dim_date(date) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 3. SUPPORTING FACT TABLES
-- ----------------------------------------------------------------------------

-- Fact: Monthly SIP Inflows (fact_monthly_sip)
DROP TABLE IF EXISTS fact_monthly_sip;
CREATE TABLE fact_monthly_sip (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL NOT NULL,
    active_sip_accounts_crore REAL NOT NULL,
    new_sip_accounts_lakh REAL NOT NULL,
    sip_aum_lakh_crore REAL NOT NULL,
    yoy_growth_pct REAL
);

-- Fact: Category Net Inflows (fact_category_inflows)
DROP TABLE IF EXISTS fact_category_inflows;
CREATE TABLE fact_category_inflows (
    inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    category TEXT NOT NULL,
    net_inflow_crore REAL NOT NULL
);

-- Fact: Industry Folio Counts (fact_industry_folios)
DROP TABLE IF EXISTS fact_industry_folios;
CREATE TABLE fact_industry_folios (
    month TEXT PRIMARY KEY,
    total_folios_crore REAL NOT NULL,
    equity_folios_crore REAL NOT NULL,
    debt_folios_crore REAL NOT NULL,
    hybrid_folios_crore REAL NOT NULL,
    others_folios_crore REAL NOT NULL
);

-- Fact: Portfolio Holdings (fact_portfolio_holdings)
DROP TABLE IF EXISTS fact_portfolio_holdings;
CREATE TABLE fact_portfolio_holdings (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL NOT NULL,
    market_value_cr REAL NOT NULL,
    current_price_inr REAL NOT NULL,
    portfolio_date TEXT NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (portfolio_date) REFERENCES dim_date(date) ON DELETE CASCADE
);

-- Fact: Benchmark Indices (fact_benchmark_indices)
DROP TABLE IF EXISTS fact_benchmark_indices;
CREATE TABLE fact_benchmark_indices (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL NOT NULL,
    FOREIGN KEY (date) REFERENCES dim_date(date) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 4. PERFORMANCE OPTIMIZATION INDEXES
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_nav_amfi_date ON fact_nav(amfi_code, nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_date ON fact_nav(nav_date);
CREATE INDEX IF NOT EXISTS idx_tx_amfi_date ON fact_transactions(amfi_code, transaction_date);
CREATE INDEX IF NOT EXISTS idx_tx_state ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_tx_city_tier ON fact_transactions(city_tier);
CREATE INDEX IF NOT EXISTS idx_tx_type ON fact_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_aum_fund_house ON fact_aum(fund_house, date);
CREATE INDEX IF NOT EXISTS idx_holdings_amfi ON fact_portfolio_holdings(amfi_code);
CREATE INDEX IF NOT EXISTS idx_holdings_sector ON fact_portfolio_holdings(sector);
CREATE INDEX IF NOT EXISTS idx_bench_name_date ON fact_benchmark_indices(index_name, date);
