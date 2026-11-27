"""
Power BI Dashboard Page Renderer & PDF Exporter
Bluestock Fintech Capstone Project

Renders the 4 Power BI-style dashboard pages from bluestock_mf.db & fund_scorecard.csv:
1. Page 1 — Industry Overview (KPIs, AUM Trend 2022–2025, AUM by AMC)
2. Page 2 — Fund Performance (Return vs StdDev Scatter, Scorecard Table, NAV vs Benchmark, Slicers)
3. Page 3 — Investor Analytics (State Bar, Tx Type Donut, Age vs Avg SIP, Monthly Tx Volume, Slicers)
4. Page 4 — SIP & Market Trends (Dual-Axis SIP + Nifty 50, Category Heatmap, Top 5 FY25 Categories)

Exports:
- dashboard/page1_industry_overview.png
- dashboard/page2_fund_performance.png
- dashboard/page3_investor_analytics.png
- dashboard/page4_sip_market_trends.png
- Dashboard.pdf (root & dashboard/Dashboard.pdf)
- dashboard/bluestock_theme.json
"""

import hashlib
import json
import logging
import sqlite3
from pathlib import Path

# Python 3.8 compatibility shim for ReportLab 4.x
_orig_md5 = hashlib.md5
def _compat_md5(*args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return _orig_md5(*args, **kwargs)
hashlib.md5 = _compat_md5

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
DASH_DIR = BASE_DIR / "dashboard"
FIG_DIR = BASE_DIR / "reports" / "figures"

DASH_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

BG = "#0f172a"
CARD = "#1e293b"
BORDER = "#334155"
SKY = "#38bdf8"
GREEN = "#10b981"
AMBER = "#f59e0b"
ROSE = "#f43f5e"
PURPLE = "#a855f7"
TEXT = "#f8fafc"
MUTED = "#94a3b8"


def draw_slicer_strip(fig, slicers_text: str):
    """Draws a Power BI-style slicer header strip across the top of a page."""
    ax = fig.add_axes([0.03, 0.87, 0.94, 0.05], facecolor=CARD)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.text(0.015, 0.45, f"INTERACTIVE SLICERS:   {slicers_text}", fontsize=9.5, color=SKY, fontweight="bold", va="center")


def render_all_pages():
    """Generates the 4 dashboard page PNGs and combines them into Dashboard.pdf."""
    conn = sqlite3.connect(DB_PATH)
    df_aum = pd.read_sql_query("SELECT * FROM fact_aum ORDER BY date", conn)
    df_sip = pd.read_sql_query("SELECT * FROM fact_monthly_sip ORDER BY month", conn)
    df_folio = pd.read_sql_query("SELECT * FROM fact_industry_folios ORDER BY month", conn)
    df_perf = pd.read_sql_query(
        """
        SELECT p.*, f.sub_category
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        """,
        conn,
    )
    df_nav = pd.read_sql_query(
        "SELECT amfi_code, nav_date, nav FROM fact_nav WHERE amfi_code IN ('119551','120504') ORDER BY nav_date",
        conn,
    )
    df_bench = pd.read_sql_query(
        "SELECT date, close_value FROM fact_benchmark_indices WHERE index_name='NIFTY50' ORDER BY date",
        conn,
    )
    df_tx = pd.read_sql_query(
        "SELECT transaction_date, transaction_type, amount_inr, state, city_tier, age_group FROM fact_transactions",
        conn,
    )
    df_cat = pd.read_sql_query("SELECT month, category, net_inflow_crore FROM fact_category_inflows ORDER BY month", conn)
    conn.close()

    df_score = pd.read_csv(BASE_DIR / "fund_scorecard.csv") if (BASE_DIR / "fund_scorecard.csv").exists() else pd.DataFrame()

    # ==================== PAGE 1: INDUSTRY OVERVIEW ====================
    fig1 = plt.figure(figsize=(16, 9), facecolor=BG)
    fig1.suptitle("BLUESTOCK MF DASHBOARD  |  PAGE 1: INDUSTRY OVERVIEW", fontsize=15, fontweight="bold", color=SKY, y=0.965)
    draw_slicer_strip(fig1, "[Year: 2022–2025]    |    [Fund House (AMC): All 10 AMCs]    |    [Category: Equity & Debt]")

    df_aum["dt"] = pd.to_datetime(df_aum["date"])
    aum_by_dt = df_aum.groupby("dt")["aum_lakh_crore"].sum().reset_index()
    latest_dt = df_aum["dt"].max()
    aum_latest = df_aum[df_aum["dt"] == latest_dt].sort_values("aum_lakh_crore", ascending=False)

    kpis1 = [
        ("Tracked AMC AUM (2025)", f"Rs. {aum_latest['aum_lakh_crore'].sum():.2f}L Cr", "SBI MF #1 at Rs. 12.50L Cr", SKY),
        ("Peak Monthly SIP", f"Rs. {df_sip['sip_inflow_crore'].max():,.0f} Cr", "Dec 2025 All-Time High", GREEN),
        ("Total Industry Folios", f"{df_folio['total_folios_crore'].iloc[-1]:.2f} Cr", "+97% vs Jan 2022 (13.26 Cr)", PURPLE),
        ("Tracked Schemes", f"{len(df_perf)} Core", "Across 10 Leading AMCs", AMBER),
    ]
    for i, (lbl, val, sub, col) in enumerate(kpis1):
        axk = fig1.add_axes([0.03 + i * 0.24, 0.72, 0.22, 0.12], facecolor=CARD)
        axk.set_xticks([]); axk.set_yticks([])
        for sp in axk.spines.values():
            sp.set_edgecolor(BORDER)
        axk.text(0.07, 0.73, lbl, fontsize=9, color=MUTED, fontweight="bold")
        axk.text(0.07, 0.36, val, fontsize=17, color=col, fontweight="bold")
        axk.text(0.07, 0.12, sub, fontsize=8.5, color=TEXT)

    ax1a = fig1.add_axes([0.05, 0.10, 0.43, 0.54], facecolor=CARD)
    ax1a.plot(aum_by_dt["dt"], aum_by_dt["aum_lakh_crore"], marker="o", color=GREEN, linewidth=2.5)
    ax1a.fill_between(aum_by_dt["dt"], aum_by_dt["aum_lakh_crore"], color=GREEN, alpha=0.18)
    ax1a.set_title("Industry AUM Growth Trend (2022–2025, Rs. Lakh Cr)", color=TEXT, fontsize=11, pad=8)
    ax1a.tick_params(colors=MUTED, labelsize=8.5)
    ax1a.grid(color=BORDER, linestyle="--", alpha=0.6)

    ax1b = fig1.add_axes([0.54, 0.12, 0.43, 0.52], facecolor=CARD)
    ax1b.barh(aum_latest["fund_house"].str.replace(" Mutual Fund", "")[::-1], aum_latest["aum_lakh_crore"][::-1], color=SKY)
    ax1b.set_title("AUM by Asset Management Company (Rs. Lakh Cr)", color=TEXT, fontsize=11, pad=8)
    ax1b.tick_params(colors=MUTED, labelsize=8.5)
    ax1b.grid(axis="x", color=BORDER, linestyle="--", alpha=0.6)

    p1_path = DASH_DIR / "page1_industry_overview.png"
    fig1.savefig(p1_path, dpi=150, facecolor=BG)
    fig1.savefig(FIG_DIR / "page1_industry_overview.png", dpi=150, facecolor=BG)
    plt.close(fig1)

    # ==================== PAGE 2: FUND PERFORMANCE ====================
    fig2 = plt.figure(figsize=(16, 9), facecolor=BG)
    fig2.suptitle("BLUESTOCK MF DASHBOARD  |  PAGE 2: FUND PERFORMANCE & SCORECARD", fontsize=15, fontweight="bold", color=SKY, y=0.965)
    draw_slicer_strip(fig2, "[Fund House: All]    |    [Category: Equity / Debt]    |    [Plan: Regular / Direct]    |    [Drill-Through: Fund -> NAV Detail]")

    ax2a = fig2.add_axes([0.05, 0.46, 0.43, 0.36], facecolor=CARD)
    for idx, cat in enumerate(df_perf["category"].unique()):
        sub = df_perf[df_perf["category"] == cat]
        ax2a.scatter(sub["return_3yr_pct"], sub["std_dev_ann_pct"], s=sub["aum_crore"] / 260 + 35,
                     alpha=0.82, color=[SKY, GREEN, AMBER][idx % 3], label=cat)
    ax2a.set_xlabel("3-Year Return (%)", color=MUTED, fontsize=9)
    ax2a.set_ylabel("Annualized StdDev (%)", color=MUTED, fontsize=9)
    ax2a.set_title("Return (X) vs Risk/StdDev (Y) | Bubble = AUM", color=TEXT, fontsize=11)
    ax2a.tick_params(colors=MUTED, labelsize=8)
    ax2a.legend(facecolor=BG, edgecolor=BORDER, labelcolor=TEXT, fontsize=8)
    ax2a.grid(color=BORDER, linestyle="--", alpha=0.6)

    ax2b = fig2.add_axes([0.54, 0.46, 0.43, 0.36], facecolor=CARD)
    nav_piv = df_nav.pivot(index="nav_date", columns="amfi_code", values="nav").sort_index()
    nav_piv.index = pd.to_datetime(nav_piv.index)
    nav_reb = (nav_piv / nav_piv.iloc[0]) * 100
    df_bench["dt"] = pd.to_datetime(df_bench["date"])
    b_sub = df_bench.set_index("dt")["close_value"]
    b_reb = (b_sub / b_sub.iloc[0]) * 100
    ax2b.plot(nav_reb.index, nav_reb["119551"], color=SKY, linewidth=2, label="SBI Bluechip (119551)")
    ax2b.plot(nav_reb.index, nav_reb["120504"], color=GREEN, linewidth=2, label="ICICI Bluechip Direct (120504)")
    ax2b.plot(b_reb.index, b_reb, color=AMBER, linestyle="--", linewidth=1.8, label="NIFTY 50 Benchmark")
    ax2b.set_title("Normalized NAV Trajectory vs NIFTY 50 (Base=100)", color=TEXT, fontsize=11)
    ax2b.tick_params(colors=MUTED, labelsize=8)
    ax2b.legend(facecolor=BG, edgecolor=BORDER, labelcolor=TEXT, fontsize=8)
    ax2b.grid(color=BORDER, linestyle="--", alpha=0.6)

    ax2c = fig2.add_axes([0.05, 0.06, 0.92, 0.33], facecolor=CARD)
    ax2c.set_xticks([]); ax2c.set_yticks([])
    for sp in ax2c.spines.values():
        sp.set_edgecolor(BORDER)
    ax2c.text(0.015, 0.88, "TOP FUND SCORECARD TABLE (0–100 COMPOSITE SCORE)", fontsize=10.5, fontweight="bold", color=SKY)
    if not df_score.empty:
        headers = f"{'Rank':<5} {'Scheme Name':<44} {'Category':<12} {'3Y CAGR':>8} {'Sharpe':>8} {'Alpha':>8} {'MaxDD':>8} {'Score':>7}"
        ax2c.text(0.015, 0.74, headers, fontsize=8.5, fontweight="bold", color=AMBER, family="monospace")
        for r_idx, (_, r) in enumerate(df_score.head(6).iterrows()):
            line = (
                f"#{int(r['overall_rank']):<4} {str(r['scheme_name'])[:42]:<44} {str(r['sub_category']):<12} "
                f"{r['cagr_3yr_pct']:>7.2f}% {r['sharpe_ratio']:>8.2f} {r['alpha_ann_pct']:>7.2f}% "
                f"{r['max_drawdown_pct']:>7.2f}% {r['scorecard_0_100']:>7.2f}"
            )
            ax2c.text(0.015, 0.60 - r_idx * 0.105, line, fontsize=8.5, color=TEXT, family="monospace")

    p2_path = DASH_DIR / "page2_fund_performance.png"
    fig2.savefig(p2_path, dpi=150, facecolor=BG)
    fig2.savefig(FIG_DIR / "page2_fund_performance.png", dpi=150, facecolor=BG)
    plt.close(fig2)

    # ==================== PAGE 3: INVESTOR ANALYTICS ====================
    fig3 = plt.figure(figsize=(16, 9), facecolor=BG)
    fig3.suptitle("BLUESTOCK MF DASHBOARD  |  PAGE 3: INVESTOR ANALYTICS & DEMOGRAPHICS", fontsize=15, fontweight="bold", color=SKY, y=0.965)
    draw_slicer_strip(fig3, "[State: All States]    |    [Age Group: All Brackets]    |    [City Tier: T30 & B30]")

    ax3a = fig3.add_axes([0.08, 0.48, 0.40, 0.34], facecolor=CARD)
    st_tot = (df_tx.groupby("state")["amount_inr"].sum() / 1e7).sort_values().tail(8)
    ax3a.barh(st_tot.index, st_tot.values, color=AMBER)
    ax3a.set_title("Transaction Amount by Top 8 States (Rs. Cr)", color=TEXT, fontsize=11)
    ax3a.tick_params(colors=MUTED, labelsize=8)
    ax3a.grid(axis="x", color=BORDER, linestyle="--", alpha=0.6)

    ax3b = fig3.add_axes([0.55, 0.48, 0.41, 0.34], facecolor=CARD)
    tx_split = df_tx.groupby("transaction_type")["amount_inr"].sum()
    ax3b.pie(tx_split.values, labels=tx_split.index, autopct="%1.1f%%", colors=[SKY, GREEN, ROSE],
             wedgeprops=dict(width=0.45, edgecolor=BG), textprops=dict(color=TEXT, fontsize=9))
    ax3b.set_title("Transaction Mix: SIP / Lumpsum / Redemption", color=TEXT, fontsize=11)

    ax3c = fig3.add_axes([0.06, 0.08, 0.42, 0.32], facecolor=CARD)
    age_sip = df_tx[df_tx["transaction_type"] == "SIP"].groupby("age_group")["amount_inr"].mean().sort_index()
    ax3c.bar(age_sip.index, age_sip.values, color=PURPLE)
    ax3c.set_title("Age Group vs Average SIP Amount (Rs.)", color=TEXT, fontsize=11)
    ax3c.tick_params(colors=MUTED, labelsize=8.5)
    ax3c.grid(axis="y", color=BORDER, linestyle="--", alpha=0.6)

    ax3d = fig3.add_axes([0.55, 0.08, 0.41, 0.32], facecolor=CARD)
    df_tx["ym"] = pd.to_datetime(df_tx["transaction_date"]).dt.to_period("M").astype(str)
    m_vol = df_tx.groupby("ym")["amount_inr"].sum() / 1e7
    ax3d.plot(m_vol.index, m_vol.values, color=SKY, linewidth=2.2, marker="o", markersize=3)
    ax3d.set_title("Monthly Transaction Volume (Rs. Cr)", color=TEXT, fontsize=11)
    ax3d.tick_params(colors=MUTED, labelsize=7.5, axis="x", rotation=35)
    ax3d.tick_params(colors=MUTED, labelsize=8, axis="y")
    ax3d.grid(color=BORDER, linestyle="--", alpha=0.6)

    p3_path = DASH_DIR / "page3_investor_analytics.png"
    fig3.savefig(p3_path, dpi=150, facecolor=BG)
    fig3.savefig(FIG_DIR / "page3_investor_analytics.png", dpi=150, facecolor=BG)
    plt.close(fig3)

    # ==================== PAGE 4: SIP & MARKET TRENDS ====================
    fig4 = plt.figure(figsize=(16, 9), facecolor=BG)
    fig4.suptitle("BLUESTOCK MF DASHBOARD  |  PAGE 4: SIP & MARKET TRENDS", fontsize=15, fontweight="bold", color=SKY, y=0.965)
    draw_slicer_strip(fig4, "[Period: 2022–2025]    |    [Benchmark: NIFTY 50]    |    [Category Filter: All 12 SEBI Categories]")

    ax4a = fig4.add_axes([0.06, 0.49, 0.89, 0.33], facecolor=CARD)
    df_sip["dt"] = pd.to_datetime(df_sip["month"] + "-01")
    ax4a.bar(df_sip["dt"], df_sip["sip_inflow_crore"], width=20, color=SKY, alpha=0.75, label="Monthly SIP Inflow (Rs. Cr)")
    ax4a.set_ylabel("SIP Inflow (Rs. Cr)", color=SKY, fontsize=9.5)
    ax4a.tick_params(colors=MUTED, labelsize=8)
    ax4a_r = ax4a.twinx()
    b_m = df_bench.set_index("dt")["close_value"].resample("MS").mean()
    b_m = b_m[b_m.index <= df_sip["dt"].max()]
    ax4a_r.plot(b_m.index, b_m.values, color=AMBER, linewidth=2.3, label="NIFTY 50 Monthly Avg")
    ax4a_r.set_ylabel("NIFTY 50 Index", color=AMBER, fontsize=9.5)
    ax4a_r.tick_params(colors=AMBER, labelsize=8)
    ax4a.set_title("Dual-Axis: Monthly SIP Inflows (Bar) vs NIFTY 50 (Line)", color=TEXT, fontsize=11)

    ax4b = fig4.add_axes([0.06, 0.09, 0.50, 0.32], facecolor=CARD)
    piv_c = df_cat.pivot(index="category", columns="month", values="net_inflow_crore")
    sns.heatmap(piv_c, cmap="YlGnBu", cbar=False, ax=ax4b)
    ax4b.set_title("Category Net Inflow Heatmap", color=TEXT, fontsize=11)
    ax4b.tick_params(colors=MUTED, labelsize=7.5)
    ax4b.set_xlabel(""); ax4b.set_ylabel("")

    ax4c = fig4.add_axes([0.62, 0.09, 0.33, 0.32], facecolor=CARD)
    fy25 = df_cat[df_cat["month"] >= "2024-04"].groupby("category")["net_inflow_crore"].sum().sort_values().tail(5)
    ax4c.barh(fy25.index, fy25.values, color=GREEN)
    ax4c.set_title("Top 5 Categories by Net Inflow (FY25, Rs. Cr)", color=TEXT, fontsize=11)
    ax4c.tick_params(colors=MUTED, labelsize=8)
    ax4c.grid(axis="x", color=BORDER, linestyle="--", alpha=0.6)

    p4_path = DASH_DIR / "page4_sip_market_trends.png"
    fig4.savefig(p4_path, dpi=150, facecolor=BG)
    fig4.savefig(FIG_DIR / "page4_sip_market_trends.png", dpi=150, facecolor=BG)
    plt.close(fig4)

    # ==================== COMBINE INTO Dashboard.pdf ====================
    for out_pdf in [BASE_DIR / "Dashboard.pdf", DASH_DIR / "Dashboard.pdf"]:
        c = canvas.Canvas(str(out_pdf), pagesize=landscape(A4))
        w, h = landscape(A4)
        for img_p in [p1_path, p2_path, p3_path, p4_path]:
            c.drawImage(str(img_p), 0, 0, width=w, height=h, preserveAspectRatio=True, anchor="c")
            c.showPage()
        c.save()
    logger.info("Exported 4 page PNGs and 4-page Dashboard.pdf.")

    # ==================== POWER BI THEME JSON ====================
    theme = {
        "name": "Bluestock Fintech Dark Theme",
        "dataColors": ["#38BDF8", "#10B981", "#F59E0B", "#A855F7", "#F43F5E", "#0284C7"],
        "background": "#0F172A",
        "foreground": "#F8FAFC",
        "tableAccent": "#38BDF8",
    }
    (DASH_DIR / "bluestock_theme.json").write_text(json.dumps(theme, indent=2), encoding="utf-8")
    logger.info("Saved dashboard/bluestock_theme.json.")


if __name__ == "__main__":
    render_all_pages()
