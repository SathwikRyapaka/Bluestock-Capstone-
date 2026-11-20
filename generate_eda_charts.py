"""
Exploratory Data Analysis (EDA) Visualization Generator
Bluestock Fintech Capstone Project - Day 3

Generates 16 publication-quality analytical charts:
1. Daily NAV normalized trends (40 schemes) highlighting 2023 Bull Run & 2024 Corrections
2. Category average cumulative return comparison
3. AUM growth grouped bar chart by AMC (2022-2025) highlighting SBI's ₹12.5L Cr
4. AMC market share distribution
5. Monthly SIP inflow time series with ₹31,002 Cr milestone annotation
6. SIP YoY growth rate trajectory
7. Category-wise net inflow monthly heatmap
8. Investor age demographic distribution
9. SIP amount boxplot by age bracket
10. Gender split and income distribution
11. Geographic distribution of SIP inflows by Indian state
12. T30 vs B30 city tier penetration and volume
13. Industry folio count growth (13.26 Cr to 26.12 Cr) with asset class breakdown
14. Pairwise daily return correlation matrix heatmap across 10 selected funds
15. Equity portfolio aggregate sector allocation donut chart
16. Top 10 individual stock allocations across mutual fund portfolios

Exports: High-resolution PNGs to reports/figures/ and reports/.
"""

import os
import sqlite3
import logging
from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
FIG_DIR = BASE_DIR / "reports" / "figures"
REPORTS_DIR = BASE_DIR / "reports"

FIG_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Visual styling
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_fig(fig, filename):
    p1 = FIG_DIR / filename
    p2 = REPORTS_DIR / filename
    fig.savefig(p1, dpi=150, bbox_inches="tight")
    fig.savefig(p2, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {filename}")

# -----------------------------------------------------------------------------
# 1. NAV TRENDS & MARKET REGIMES
# -----------------------------------------------------------------------------
def plot_nav_trends():
    logger.info("Plotting Chart 1: NAV Trends & Market Regimes...")
    conn = get_connection()
    df_nav = pd.read_sql_query("""
        SELECT n.amfi_code, f.scheme_name, f.category, f.sub_category, n.nav_date, n.nav
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        ORDER BY n.amfi_code, n.nav_date;
    """, conn)
    conn.close()

    df_nav["nav_date"] = pd.to_datetime(df_nav["nav_date"])

    # Rebase each fund's NAV to 100 on start date (2022-01-03)
    piv = df_nav.pivot(index="nav_date", columns="scheme_name", values="nav")
    rebased = (piv / piv.iloc[0]) * 100

    fig, ax = plt.subplots(figsize=(15, 7))

    # Plot all 40 lines with low opacity
    for col in rebased.columns:
        ax.plot(rebased.index, rebased[col], color="#2b5c8f", alpha=0.18, linewidth=1.0)

    # Highlight average equity vs debt
    equity_cols = [c for c in rebased.columns if "Liquid" not in c and "Gilt" not in c and "Debt" not in c]
    debt_cols = [c for c in rebased.columns if c not in equity_cols]

    eq_avg = rebased[equity_cols].mean(axis=1)
    debt_avg = rebased[debt_cols].mean(axis=1)

    ax.plot(rebased.index, eq_avg, color="#0052cc", linewidth=3.0, label="Equity Schemes Average (Rebased)")
    ax.plot(rebased.index, debt_avg, color="#00875a", linewidth=2.5, linestyle="--", label="Debt/Liquid Average (Rebased)")

    # Highlight 2023 Bull Run (March 2023 to Dec 2023)
    ax.axvspan(pd.Timestamp("2023-03-20"), pd.Timestamp("2023-12-31"), color="#36b37e", alpha=0.15, label="2023 Market Rally (+28%)")
    # Highlight 2024 Market Volatility / Corrections (May-June 2024 & Oct 2024)
    ax.axvspan(pd.Timestamp("2024-05-01"), pd.Timestamp("2024-06-15"), color="#ffab00", alpha=0.20, label="2024 Election Volatility")
    ax.axvspan(pd.Timestamp("2024-10-01"), pd.Timestamp("2024-11-15"), color="#ff5630", alpha=0.15, label="Late 2024 FII Outflow Consolidation")

    ax.set_title("Mutual Fund NAV Trajectory across 40 Schemes (2022–2026)\nHighlighting 2023 Bull Run and 2024 Market Volatility Regimes", fontsize=14, weight="bold", pad=12)
    ax.set_ylabel("Normalized NAV (Base = 100 on Jan 2022)", fontsize=11)
    ax.set_xlabel("Date", fontsize=11)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", frameon=True, framealpha=0.95)
    save_fig(fig, "01_nav_trend_all_schemes.png")

    # Chart 2: Category Average Trajectory
    logger.info("Plotting Chart 2: Category Average Performance...")
    fig2, ax2 = plt.subplots(figsize=(13, 6))
    subcats = df_nav.groupby(["sub_category", "nav_date"])["nav"].mean().reset_index()
    sub_piv = subcats.pivot(index="nav_date", columns="sub_category", values="nav")
    sub_rebased = (sub_piv / sub_piv.iloc[0]) * 100

    palette = sns.color_palette("tab10", n_colors=len(sub_rebased.columns))
    for i, col in enumerate(sub_rebased.columns):
        lw = 2.5 if col in ["Large Cap", "Small Cap", "Mid Cap", "Liquid"] else 1.2
        ls = "-" if col in ["Large Cap", "Small Cap", "Mid Cap"] else "--"
        ax2.plot(sub_rebased.index, sub_rebased[col], label=col, linewidth=lw, linestyle=ls, color=palette[i])

    ax2.set_title("Cumulative NAV Growth by Sub-Category (2022–2026)", fontsize=14, weight="bold", pad=12)
    ax2.set_ylabel("Normalized NAV (Base = 100)", fontsize=11)
    ax2.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    save_fig(fig2, "02_nav_category_performance.png")

# -----------------------------------------------------------------------------
# 2. AUM GROWTH & AMC LEADERSHIP
# -----------------------------------------------------------------------------
def plot_aum_growth():
    logger.info("Plotting Chart 3: AUM Growth by AMC...")
    conn = get_connection()
    df_aum = pd.read_sql_query("""
        SELECT strftime('%Y', date) AS year, date, fund_house, aum_lakh_crore, aum_crore
        FROM fact_aum
        WHERE date IN ('2022-03-31', '2023-03-31', '2024-03-31', '2025-12-31')
        ORDER BY year, aum_crore DESC;
    """, conn)
    conn.close()

    fig, ax = plt.subplots(figsize=(14, 7))
    palette = {"2022": "#b3d4fc", "2023": "#4c9aff", "2024": "#0052cc", "2025": "#0747a6"}
    
    # Sort AMC by 2025 AUM
    order_amc = df_aum[df_aum["year"] == "2025"].sort_values("aum_lakh_crore", ascending=False)["fund_house"].tolist()

    sns.barplot(data=df_aum, x="fund_house", y="aum_lakh_crore", hue="year", order=order_amc, palette=palette, ax=ax)
    
    # Annotate SBI's ₹12.5L Cr dominance
    ax.annotate("SBI MF Dominance:\n₹12.50 Lakh Cr (+106.6%)",
                xy=(0, 12.5), xytext=(1.2, 11.5),
                arrowprops=dict(facecolor="#ff5630", shrink=0.08, width=1.5, headwidth=8),
                fontsize=10, weight="bold", color="#bf2600",
                bbox=dict(boxstyle="round,pad=0.4", fc="#ffebe6", ec="#ff5630", lw=1))

    ax.set_title("AUM Growth Trajectory for Top 10 Indian AMCs (2022–2025)\nDemonstrating SBI Mutual Fund's ₹12.5 Lakh Crore Market Dominance", fontsize=14, weight="bold", pad=12)
    ax.set_ylabel("Assets Under Management (₹ Lakh Crore)", fontsize=11)
    ax.set_xlabel("Mutual Fund House (AMC)", fontsize=11)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(title="Calendar Year", loc="upper right", frameon=True)
    save_fig(fig, "03_aum_growth_by_amc.png")

    # Chart 4: Market share pie
    logger.info("Plotting Chart 4: AMC Market Share Distribution...")
    df_2025 = df_aum[df_aum["year"] == "2025"].sort_values("aum_crore", ascending=False)
    fig4, ax4 = plt.subplots(figsize=(9, 7))
    colors = sns.color_palette("Blues_r", n_colors=len(df_2025))
    explode = [0.08 if i == 0 else 0 for i in range(len(df_2025))]

    wedges, texts, autotexts = ax4.pie(
        df_2025["aum_crore"], labels=df_2025["fund_house"], autopct="%1.1f%%",
        startangle=140, colors=colors, explode=explode, pctdistance=0.8,
        textprops=dict(color="#333333")
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_weight("bold")
    ax4.set_title("Mutual Fund AMC Market Share Distribution (December 2025 Snapshot)", fontsize=13, weight="bold")
    save_fig(fig4, "04_amc_market_share_pie.png")

# -----------------------------------------------------------------------------
# 3. SIP INFLOW TRAJECTORY & RECORD MILESTONES
# -----------------------------------------------------------------------------
def plot_sip_inflows():
    logger.info("Plotting Chart 5: SIP Inflows & Record Milestones...")
    conn = get_connection()
    df_sip = pd.read_sql_query("""
        SELECT month, sip_inflow_crore, active_sip_accounts_crore, yoy_growth_pct, sip_aum_lakh_crore
        FROM fact_monthly_sip
        ORDER BY month;
    """, conn)
    conn.close()

    df_sip["date"] = pd.to_datetime(df_sip["month"] + "-01")

    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Inflow line & area fill
    ax1.plot(df_sip["date"], df_sip["sip_inflow_crore"], color="#0052cc", linewidth=2.8, label="Monthly SIP Inflows (₹ Cr)")
    ax1.fill_between(df_sip["date"], df_sip["sip_inflow_crore"], color="#deebff", alpha=0.5)

    # Annotate Dec 2025 All-Time High
    ath = df_sip.iloc[-1]
    ax1.scatter([ath["date"]], [ath["sip_inflow_crore"]], color="#ff5630", s=90, zorder=5)
    ax1.annotate(f"All-Time High:\n₹{ath['sip_inflow_crore']:,.0f} Crore (Dec 2025)",
                 xy=(ath["date"], ath["sip_inflow_crore"]),
                 xytext=(pd.Timestamp("2024-06-01"), 30000),
                 arrowprops=dict(facecolor="#ff5630", shrink=0.08, width=1.5, headwidth=7),
                 fontsize=10, weight="bold", color="#bf2600",
                 bbox=dict(boxstyle="round,pad=0.4", fc="#ffebe6", ec="#ff5630", lw=1))

    # Secondary axis for Active SIP accounts
    ax2 = ax1.twinx()
    ax2.plot(df_sip["date"], df_sip["active_sip_accounts_crore"], color="#00875a", linestyle="--", linewidth=2.2, label="Active SIP Accounts (Crore)")
    ax2.grid(False)

    ax1.set_title("Indian Mutual Fund Monthly SIP Inflow Trend (Jan 2022 – Dec 2025)\nCrossing All-Time High of ₹31,002 Crore & 9.35 Crore Contributing Accounts", fontsize=14, weight="bold", pad=12)
    ax1.set_ylabel("Monthly SIP Inflow (₹ Crore)", color="#0052cc", fontsize=11)
    ax2.set_ylabel("Active SIP Accounts (Crore)", color="#00875a", fontsize=11)
    ax1.set_xlabel("Month", fontsize=11)
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True)
    save_fig(fig, "05_monthly_sip_inflows_trend.png")

    # Chart 6: SIP YoY Growth Rate
    logger.info("Plotting Chart 6: SIP YoY Growth...")
    fig6, ax6 = plt.subplots(figsize=(13, 5))
    df_growth = df_sip.dropna(subset=["yoy_growth_pct"])
    colors = ["#36b37e" if v >= 20 else "#4c9aff" for v in df_growth["yoy_growth_pct"]]

    ax6.bar(df_growth["date"], df_growth["yoy_growth_pct"], width=20, color=colors, alpha=0.85)
    ax6.axhline(df_growth["yoy_growth_pct"].mean(), color="#ff5630", linestyle="--", linewidth=1.5,
                label=f"Average YoY Growth ({df_growth['yoy_growth_pct'].mean():.1f}%)")

    ax6.set_title("Year-over-Year (YoY) Growth in Monthly SIP Inflows (2023–2025)", fontsize=13, weight="bold", pad=10)
    ax6.set_ylabel("YoY Growth (%)", fontsize=11)
    ax6.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax6.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax6.legend(loc="upper right", frameon=True)
    save_fig(fig6, "06_sip_yoy_growth_trend.png")

# -----------------------------------------------------------------------------
# 4. CATEGORY INFLOW HEATMAP
# -----------------------------------------------------------------------------
def plot_category_heatmap():
    logger.info("Plotting Chart 7: Category Inflow Heatmap...")
    conn = get_connection()
    df_cat = pd.read_sql_query("""
        SELECT month, category, net_inflow_crore
        FROM fact_category_inflows
        ORDER BY month, category;
    """, conn)
    conn.close()

    piv = df_cat.pivot(index="category", columns="month", values="net_inflow_crore")

    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(piv, cmap="YlGnBu", cbar_kws={"label": "Net Inflow (₹ Crore)"}, linewidths=0.5, linecolor="#eeeeee", ax=ax)
    ax.set_title("Category-Wise Net Monthly Mutual Fund Inflows Heatmap (2022–2025)\nIllustrating Massive Retail Capital Rotation into Small Cap, Mid Cap & Flexi Cap", fontsize=14, weight="bold", pad=12)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Fund Category", fontsize=11)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "07_category_inflow_heatmap.png")

# -----------------------------------------------------------------------------
# 5. INVESTOR DEMOGRAPHICS & GEOGRAPHY
# -----------------------------------------------------------------------------
def plot_investor_demographics():
    logger.info("Plotting Charts 8-12: Investor Demographics & Geography...")
    conn = get_connection()
    df_tx = pd.read_sql_query("""
        SELECT investor_id, state, city_tier, age_group, gender, annual_income_lakh, transaction_type, amount_inr
        FROM fact_transactions;
    """, conn)
    conn.close()

    # Chart 8: Age Group Distribution Donut
    fig8, ax8 = plt.subplots(figsize=(8, 6))
    age_counts = df_tx.drop_duplicates("investor_id")["age_group"].value_counts()
    colors = sns.color_palette("mako", n_colors=len(age_counts))

    wedges, texts, autotexts = ax8.pie(
        age_counts, labels=age_counts.index, autopct="%1.1f%%",
        startangle=140, colors=colors, pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_weight("bold")
    ax8.set_title("Investor Demographic Age Distribution\n(4,803 Unique Investors)", fontsize=13, weight="bold")
    save_fig(fig8, "08_investor_age_distribution.png")

    # Chart 9: SIP Amount by Age Bracket Boxplot
    fig9, ax9 = plt.subplots(figsize=(12, 6))
    sip_tx = df_tx[df_tx["transaction_type"] == "SIP"]
    age_order = ["18-25", "26-35", "36-45", "46-55", "56+"]
    sns.boxplot(data=sip_tx, x="age_group", y="amount_inr", order=age_order, palette="viridis", showfliers=False, ax=ax9)
    ax9.set_title("Monthly SIP Ticket Size Distribution by Investor Age Bracket", fontsize=13, weight="bold", pad=10)
    ax9.set_xlabel("Age Bracket", fontsize=11)
    ax9.set_ylabel("SIP Amount (₹)", fontsize=11)
    save_fig(fig9, "09_sip_amount_by_age_boxplot.png")

    # Chart 10: Gender Split & Income
    fig10, (ax10a, ax10b) = plt.subplots(1, 2, figsize=(14, 5))
    gender_counts = df_tx.drop_duplicates("investor_id")["gender"].value_counts()
    ax10a.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", colors=["#4c9aff", "#ff7452"],
              startangle=90, wedgeprops=dict(width=0.5, edgecolor="white"))
    ax10a.set_title("Investor Gender Breakdown", fontsize=12, weight="bold")

    sns.histplot(df_tx.drop_duplicates("investor_id")["annual_income_lakh"], bins=15, kde=True, color="#0052cc", ax=ax10b)
    ax10b.set_title("Investor Annual Income Distribution (₹ Lakh)", fontsize=12, weight="bold")
    ax10b.set_xlabel("Annual Income (₹ Lakh)")
    save_fig(fig10, "10_investor_gender_income_split.png")

    # Chart 11: Geographic SIP Inflows by State
    fig11, ax11 = plt.subplots(figsize=(12, 6))
    state_totals = df_tx.groupby("state")["amount_inr"].sum().sort_values(ascending=True) / 1e7
    sns.barplot(x=state_totals.values, y=state_totals.index, palette="mako", ax=ax11)
    ax11.set_title("Total Capital Invested by Indian State (₹ Crore)", fontsize=13, weight="bold", pad=10)
    ax11.set_xlabel("Total Investment (₹ Crore)", fontsize=11)
    ax11.set_ylabel("State", fontsize=11)
    save_fig(fig11, "11_geographic_sip_inflows_state.png")

    # Chart 12: T30 vs B30 Split
    fig12, ax12 = plt.subplots(figsize=(8, 6))
    tier_vol = df_tx.groupby("city_tier")["amount_inr"].sum()
    ax12.pie(tier_vol, labels=["Beyond Top 30 (B30)", "Top 30 Metros (T30)"], autopct="%1.1f%%",
             colors=["#36b37e", "#0052cc"], startangle=140, explode=[0.05, 0],
             wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2))
    ax12.set_title("Capital Allocation by City Tier\nT30 (₹231.9 Cr) vs B30 (₹120.2 Cr)", fontsize=13, weight="bold")
    save_fig(fig12, "12_city_tier_t30_b30_split.png")

# -----------------------------------------------------------------------------
# 6. FOLIO EXPANSION, CORRELATION & SECTOR HOLDINGS
# -----------------------------------------------------------------------------
def plot_folios_correlation_and_holdings():
    logger.info("Plotting Charts 13-16: Folios, Correlation & Sector Holdings...")
    conn = get_connection()

    # Chart 13: Industry Folios
    df_folio = pd.read_sql_query("SELECT month, total_folios_crore, equity_folios_crore, debt_folios_crore, hybrid_folios_crore FROM fact_industry_folios ORDER BY month;", conn)
    df_folio["date"] = pd.to_datetime(df_folio["month"] + "-01")

    fig13, ax13 = plt.subplots(figsize=(13, 6))
    ax13.plot(df_folio["date"], df_folio["total_folios_crore"], marker="o", color="#0747a6", linewidth=2.8, label="Total Folios (Crore)")
    ax13.plot(df_folio["date"], df_folio["equity_folios_crore"], marker="s", color="#00875a", linewidth=2.0, label="Equity Folios (Crore)")
    ax13.plot(df_folio["date"], df_folio["hybrid_folios_crore"], marker="^", color="#ffab00", linewidth=1.8, label="Hybrid Folios (Crore)")
    ax13.plot(df_folio["date"], df_folio["debt_folios_crore"], marker="x", color="#ff5630", linewidth=1.8, label="Debt Folios (Crore)")

    # Milestone markers
    f_first = df_folio.iloc[0]
    f_last = df_folio.iloc[-1]
    ax13.annotate(f"Jan 2022: {f_first['total_folios_crore']} Cr", xy=(f_first["date"], f_first["total_folios_crore"]),
                  xytext=(f_first["date"], f_first["total_folios_crore"] + 2.5),
                  arrowprops=dict(facecolor="#0747a6", shrink=0.08, width=1, headwidth=6), fontsize=9, weight="bold")
    ax13.annotate(f"Dec 2025: {f_last['total_folios_crore']} Cr (+97%)", xy=(f_last["date"], f_last["total_folios_crore"]),
                  xytext=(pd.Timestamp("2024-06-01"), f_last["total_folios_crore"] - 1),
                  arrowprops=dict(facecolor="#0747a6", shrink=0.08, width=1, headwidth=6), fontsize=9, weight="bold")

    ax13.set_title("Mutual Fund Folio Count Expansion Across Asset Classes (2022–2025)\nDoubling from 13.26 Crore to 26.12 Crore Folios", fontsize=14, weight="bold", pad=12)
    ax13.set_ylabel("Folio Count (Crore Accounts)", fontsize=11)
    ax13.set_xlabel("Date", fontsize=11)
    ax13.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax13.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax13.legend(loc="upper left", frameon=True)
    save_fig(fig13, "13_industry_folio_growth.png")

    # Chart 14: Return Correlation Matrix (10 Selected Funds)
    df_ret = pd.read_sql_query("""
        SELECT n.amfi_code, f.scheme_name, n.nav_date, n.daily_return
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        WHERE n.amfi_code IN ('119551', '120503', '118632', '119092', '120841', '119598', '120505', '148568', '119120', '120507')
        ORDER BY n.amfi_code, n.nav_date;
    """, conn)
    piv_ret = df_ret.pivot(index="nav_date", columns="scheme_name", values="daily_return")
    corr = piv_ret.corr()

    fig14, ax14 = plt.subplots(figsize=(11, 9))
    short_labels = [c[:22] + ".." if len(c) > 22 else c for c in corr.columns]
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", vmin=-0.2, vmax=1.0,
                xticklabels=short_labels, yticklabels=short_labels, cbar_kws={"label": "Pearson Correlation"}, ax=ax14)
    ax14.set_title("Pairwise Daily Return Correlation Matrix (10 Selected Funds)", fontsize=13, weight="bold", pad=12)
    ax14.set_xticklabels(ax14.get_xticklabels(), rotation=35, ha="right", fontsize=9)
    ax14.set_yticklabels(ax14.get_yticklabels(), fontsize=9)
    save_fig(fig14, "14_nav_return_correlation_matrix.png")

    # Chart 15: Sector Allocation Donut
    df_holdings = pd.read_sql_query("""
        SELECT sector, SUM(market_value_cr) AS total_cr
        FROM fact_portfolio_holdings
        GROUP BY sector
        ORDER BY total_cr DESC;
    """, conn)
    conn.close()

    fig15, ax15 = plt.subplots(figsize=(9, 7))
    colors15 = sns.color_palette("Spectral", n_colors=len(df_holdings))
    wedges, texts, autotexts = ax15.pie(
        df_holdings["total_cr"], labels=df_holdings["sector"], autopct="%1.1f%%",
        startangle=140, colors=colors15, pctdistance=0.8,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_weight("bold")
    ax15.set_title("Aggregate Equity Mutual Fund Sector Allocation\nDominance of Banking (23.2%) and Technology (14.2%)", fontsize=13, weight="bold")
    save_fig(fig15, "15_sector_allocation_donut.png")

    # Chart 16: Top 10 Equity Stock Allocations
    conn2 = get_connection()
    df_stocks = pd.read_sql_query("""
        SELECT stock_symbol, stock_name, sector, SUM(market_value_cr) AS total_cr
        FROM fact_portfolio_holdings
        GROUP BY stock_symbol, stock_name, sector
        ORDER BY total_cr DESC
        LIMIT 10;
    """, conn2)
    conn2.close()

    fig16, ax16 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_stocks, x="total_cr", y="stock_name", palette="viridis", ax=ax16)
    ax16.set_title("Top 10 Underlying Stock Holdings by Portfolio Market Value (₹ Crore)", fontsize=13, weight="bold", pad=10)
    ax16.set_xlabel("Aggregated Value Across Funds (₹ Crore)", fontsize=11)
    ax16.set_ylabel("Stock Name", fontsize=11)
    save_fig(fig16, "16_top_equity_stock_holdings.png")

def main():
    print("\n" + "="*80)
    print("RUNNING EXPLORATORY DATA ANALYSIS (EDA) CHART ENGINE")
    print("="*80)
    plot_nav_trends()
    plot_aum_growth()
    plot_sip_inflows()
    plot_category_heatmap()
    plot_investor_demographics()
    plot_folios_correlation_and_holdings()
    print("="*80)
    print("ALL 16 EDA CHARTS GENERATED & EXPORTED SUCCESSFULLY")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
