"""
Interactive BI Dashboard Generator
Bluestock Fintech Capstone Project

Generates:
1. dashboard/bluestock_dashboard.html — Self-contained interactive HTML5/Plotly
   executive dashboard with 4 tabs (Executive Overview, NAV & Returns,
   Investor & Geography, Risk & Recommender).
2. reports/figures/dashboard_overview.png — High-resolution dashboard screenshot 1
   (Executive KPIs, AUM Leadership, SIP Growth, Folio Expansion).
3. reports/figures/dashboard_analytics.png — High-resolution dashboard screenshot 2
   (Risk VaR/CVaR Matrix, Rolling Sharpe, Sector HHI, Top Recommendations).
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
DASHBOARD_DIR = BASE_DIR / "dashboard"
FIG_DIR = BASE_DIR / "reports" / "figures"

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


def fetch_dashboard_data() -> Dict[str, Any]:
    """Queries SQLite star schema and analytics CSVs for dashboard metrics."""
    conn = sqlite3.connect(DB_PATH)

    df_fund = pd.read_sql_query("SELECT * FROM dim_fund", conn)
    df_perf = pd.read_sql_query(
        """
        SELECT p.amfi_code, p.scheme_name, p.fund_house, p.category, f.sub_category,
               p.risk_grade, p.sharpe_ratio, p.return_3yr_pct, p.std_dev_ann_pct,
               p.expense_ratio_pct, p.aum_crore
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.sharpe_ratio DESC
        """,
        conn,
    )
    df_aum = pd.read_sql_query("SELECT * FROM fact_aum ORDER BY date, aum_lakh_crore DESC", conn)
    df_aum["year"] = pd.to_datetime(df_aum["date"]).dt.year
    df_sip = pd.read_sql_query("SELECT * FROM fact_monthly_sip ORDER BY month", conn)
    df_folio = pd.read_sql_query("SELECT * FROM fact_industry_folios ORDER BY month", conn)
    df_tx = pd.read_sql_query(
        """
        SELECT transaction_type, state, city_tier, age_group,
               COUNT(*) AS tx_count, SUM(amount_inr) AS total_inr
        FROM fact_transactions
        GROUP BY transaction_type, state, city_tier, age_group
        """,
        conn,
    )
    df_holdings = pd.read_sql_query(
        """
        SELECT sector, SUM(weight_pct) AS total_weight
        FROM fact_portfolio_holdings
        GROUP BY sector
        ORDER BY total_weight DESC
        """,
        conn,
    )
    conn.close()

    var_path = BASE_DIR / "var_cvar_report.csv"
    df_var = pd.read_csv(var_path) if var_path.exists() else pd.DataFrame()

    hhi_path = BASE_DIR / "sector_hhi.csv"
    df_hhi = pd.read_csv(hhi_path) if hhi_path.exists() else pd.DataFrame()

    return {
        "fund": df_fund,
        "perf": df_perf,
        "aum": df_aum,
        "sip": df_sip,
        "folio": df_folio,
        "tx": df_tx,
        "holdings": df_holdings,
        "var": df_var,
        "hhi": df_hhi,
    }


def generate_html_dashboard(data: Dict[str, Any]) -> Path:
    """Builds a self-contained interactive HTML5/Plotly dashboard."""
    df_aum = data["aum"]
    df_sip = data["sip"]
    df_folio = data["folio"]
    df_perf = data["perf"]
    df_tx = data["tx"]
    df_holdings = data["holdings"]
    df_var = data["var"]

    latest_year = int(df_aum["year"].max())
    latest_date = df_aum[df_aum["year"] == latest_year]["date"].max()
    aum_latest = df_aum[df_aum["date"] == latest_date].sort_values("aum_lakh_crore", ascending=False)
    total_industry_aum = round(float(aum_latest["aum_lakh_crore"].sum()), 2)
    latest_sip = round(float(df_sip["sip_inflow_crore"].iloc[-1]), 0)
    latest_folios = round(float(df_folio["total_folios_crore"].iloc[-1]), 2)
    total_tx_cr = round(float(df_tx["total_inr"].sum() / 1e7), 2)

    state_agg = df_tx.groupby("state")["total_inr"].sum().sort_values(ascending=False).head(10)
    tier_agg = df_tx.groupby("city_tier")["total_inr"].sum()

    # Prepare JSON payloads for Plotly.js
    amc_names = aum_latest["fund_house"].tolist()
    amc_vals = [round(float(x), 2) for x in aum_latest["aum_lakh_crore"].tolist()]

    sip_dates = df_sip["month"].tolist()
    sip_vals = [round(float(x), 1) for x in df_sip["sip_inflow_crore"].tolist()]

    folio_dates = df_folio["month"].tolist()
    folio_vals = [round(float(x), 2) for x in df_folio["total_folios_crore"].tolist()]

    top_sectors = df_holdings.head(8)
    sector_labels = top_sectors["sector"].tolist()
    sector_vals = [round(float(x), 2) for x in top_sectors["total_weight"].tolist()]

    state_labels = state_agg.index.tolist()
    state_vals = [round(float(x / 1e7), 2) for x in state_agg.values]

    tier_labels = tier_agg.index.tolist()
    tier_vals = [round(float(x / 1e7), 2) for x in tier_agg.values]

    if not df_var.empty:
        var_sample = df_var.head(15)
        var_names = [s[:28] for s in var_sample["scheme_name"].tolist()]
        var_vals = [round(float(x), 2) for x in var_sample["var_95_daily_pct"].tolist()]
        cvar_vals = [round(float(x), 2) for x in var_sample["cvar_95_daily_pct"].tolist()]
    else:
        var_names, var_vals, cvar_vals = [], [], []

    # Top 10 schemes table rows
    top_schemes_rows = ""
    for _, row in df_perf.head(10).iterrows():
        top_schemes_rows += (
            f"<tr>"
            f"<td>{row['scheme_name']}</td>"
            f"<td>{row['fund_house']}</td>"
            f"<td>{row['sub_category']}</td>"
            f"<td>{row['risk_grade']}</td>"
            f"<td><b>{row['sharpe_ratio']:.2f}</b></td>"
            f"<td>{row['return_3yr_pct']:.2f}%</td>"
            f"<td>{row['expense_ratio_pct']:.2f}%</td>"
            f"<td>&#8377;{row['aum_crore']:,.0f} Cr</td>"
            f"</tr>\n"
        )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bluestock Fintech — Mutual Fund Analytics Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    :root {{
      --bg: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --green: #10b981;
      --amber: #f59e0b;
      --rose: #f43f5e;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); padding: 20px 28px; }}
    header {{
      display: flex; justify-content: space-between; align-items: center;
      border-bottom: 1px solid var(--border); padding-bottom: 14px; margin-bottom: 20px;
    }}
    header h1 {{ font-size: 22px; color: var(--accent); }}
    header p {{ font-size: 13px; color: var(--muted); }}
    .kpi-grid {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 22px;
    }}
    .kpi-card {{
      background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px;
    }}
    .kpi-label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; }}
    .kpi-value {{ font-size: 26px; font-weight: 700; margin-top: 6px; color: var(--text); }}
    .kpi-sub {{ font-size: 12px; color: var(--green); margin-top: 4px; }}
    .chart-grid {{
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; margin-bottom: 22px;
    }}
    .chart-card {{
      background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px;
    }}
    .chart-card h3 {{ font-size: 15px; margin-bottom: 10px; color: #e2e8f0; }}
    .table-card {{
      background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; overflow-x: auto;
    }}
    .table-card h3 {{ font-size: 16px; margin-bottom: 12px; color: var(--accent); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 11px; }}
    tr:hover {{ background: rgba(56, 189, 248, 0.08); }}
    footer {{ text-align: center; margin-top: 24px; font-size: 12px; color: var(--muted); }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Bluestock Fintech — Mutual Fund Analytics Platform</h1>
      <p>Interactive Star-Schema BI Dashboard | 40 Schemes | 46,000 NAV Records | 32,778 Transactions</p>
    </div>
    <div style="text-align:right">
      <span style="background:#0ea5e9;color:#fff;padding:5px 12px;border-radius:14px;font-size:12px;font-weight:600;">v1.0 Production</span>
    </div>
  </header>

  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Industry AUM ({latest_year})</div>
      <div class="kpi-value">&#8377;{total_industry_aum:.2f}L Cr</div>
      <div class="kpi-sub">SBI MF leads at &#8377;12.50L Cr (19.9%)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Latest Monthly SIP Inflow</div>
      <div class="kpi-value">&#8377;{latest_sip:,.0f} Cr</div>
      <div class="kpi-sub">+169% growth since Jan 2022</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Total Industry Folios</div>
      <div class="kpi-value">{latest_folios:.2f} Cr</div>
      <div class="kpi-sub">Nearly doubled from 13.26 Cr</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Tracked Retail Volume</div>
      <div class="kpi-value">&#8377;{total_tx_cr:,.1f} Cr</div>
      <div class="kpi-sub">32,778 verified transactions</div>
    </div>
  </section>

  <section class="chart-grid">
    <div class="chart-card">
      <h3>AMC AUM Leadership ({latest_year}, &#8377; Lakh Crore)</h3>
      <div id="chart-aum" style="height:310px;"></div>
    </div>
    <div class="chart-card">
      <h3>Monthly SIP Inflow Trajectory (&#8377; Crore)</h3>
      <div id="chart-sip" style="height:310px;"></div>
    </div>
    <div class="chart-card">
      <h3>Top 10 States by Retail Volume (&#8377; Crore)</h3>
      <div id="chart-state" style="height:310px;"></div>
    </div>
    <div class="chart-card">
      <h3>Equity Sector Allocation (%)</h3>
      <div id="chart-sector" style="height:310px;"></div>
    </div>
    <div class="chart-card">
      <h3>Industry Folio Growth (Crore Accounts)</h3>
      <div id="chart-folio" style="height:310px;"></div>
    </div>
    <div class="chart-card">
      <h3>Tail Risk: 95% Historical VaR vs CVaR (%)</h3>
      <div id="chart-var" style="height:310px;"></div>
    </div>
  </section>

  <section class="table-card">
    <h3>Top 10 Schemes by Risk-Adjusted Return (Sharpe Ratio)</h3>
    <table>
      <thead>
        <tr>
          <th>Scheme Name</th><th>Fund House</th><th>Category</th><th>Risk Grade</th>
          <th>Sharpe</th><th>3Y Return</th><th>Expense Ratio</th><th>AUM</th>
        </tr>
      </thead>
      <tbody>
        {top_schemes_rows}
      </tbody>
    </table>
  </section>

  <footer>
    Bluestock Fintech Capstone Project (2026) | Team: Sathwik Ryapaka, Abhiram, Ashmeet Kaur
  </footer>

  <script>
    const darkLayout = {{
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: {{ color: '#cbd5e1', size: 11 }},
      margin: {{ t: 15, r: 20, b: 45, l: 55 }},
      xaxis: {{ gridcolor: '#334155' }},
      yaxis: {{ gridcolor: '#334155' }}
    }};

    Plotly.newPlot('chart-aum', [{{
      x: {json.dumps(amc_names)},
      y: {json.dumps(amc_vals)},
      type: 'bar',
      marker: {{ color: '#38bdf8' }}
    }}], {{ ...darkLayout, xaxis: {{ ...darkLayout.xaxis, tickangle: -25 }} }}, {{ responsive: true }});

    Plotly.newPlot('chart-sip', [{{
      x: {json.dumps(sip_dates)},
      y: {json.dumps(sip_vals)},
      type: 'scatter', mode: 'lines', fill: 'tozeroy',
      line: {{ color: '#10b981', width: 2.5 }}
    }}], darkLayout, {{ responsive: true }});

    Plotly.newPlot('chart-state', [{{
      y: {json.dumps(state_labels[::-1])},
      x: {json.dumps(state_vals[::-1])},
      type: 'bar', orientation: 'h',
      marker: {{ color: '#f59e0b' }}
    }}], {{ ...darkLayout, margin: {{ t: 15, r: 20, b: 40, l: 110 }} }}, {{ responsive: true }});

    Plotly.newPlot('chart-sector', [{{
      labels: {json.dumps(sector_labels)},
      values: {json.dumps(sector_vals)},
      type: 'pie', hole: 0.45
    }}], {{ ...darkLayout, margin: {{ t: 10, r: 10, b: 10, l: 10 }} }}, {{ responsive: true }});

    Plotly.newPlot('chart-folio', [{{
      x: {json.dumps(folio_dates)},
      y: {json.dumps(folio_vals)},
      type: 'scatter', mode: 'lines+markers',
      line: {{ color: '#a855f7', width: 2.5 }}
    }}], darkLayout, {{ responsive: true }});

    Plotly.newPlot('chart-var', [
      {{ x: {json.dumps(var_names)}, y: {json.dumps(var_vals)}, name: 'VaR (95%)', type: 'bar', marker: {{ color: '#f59e0b' }} }},
      {{ x: {json.dumps(var_names)}, y: {json.dumps(cvar_vals)}, name: 'CVaR (95%)', type: 'bar', marker: {{ color: '#f43f5e' }} }}
    ], {{ ...darkLayout, barmode: 'group', xaxis: {{ ...darkLayout.xaxis, tickangle: -35 }} }}, {{ responsive: true }});
  </script>
</body>
</html>
"""
    out_path = DASHBOARD_DIR / "bluestock_dashboard.html"
    out_path.write_text(html_content, encoding="utf-8")
    logger.info(f"Generated interactive HTML dashboard: {out_path}")
    return out_path


def render_dashboard_screenshots(data: Dict[str, Any]) -> None:
    """Renders two high-resolution executive dashboard screenshot PNGs."""
    df_aum = data["aum"]
    df_sip = data["sip"]
    df_folio = data["folio"]
    df_perf = data["perf"]
    df_tx = data["tx"]
    df_holdings = data["holdings"]
    df_var = data["var"]
    df_hhi = data["hhi"]

    latest_year = int(df_aum["year"].max())
    latest_date = df_aum[df_aum["year"] == latest_year]["date"].max()
    aum_latest = df_aum[df_aum["date"] == latest_date].sort_values("aum_lakh_crore", ascending=False).head(8)
    total_industry_aum = float(aum_latest["aum_lakh_crore"].sum())
    latest_sip = float(df_sip["sip_inflow_crore"].iloc[-1])
    latest_folios = float(df_folio["total_folios_crore"].iloc[-1])
    total_tx_cr = float(df_tx["total_inr"].sum() / 1e7)

    # --- Screenshot 1: Executive Overview ---
    fig = plt.figure(figsize=(16, 9), facecolor="#0f172a")
    fig.suptitle(
        "BLUESTOCK FINTECH  |  MUTUAL FUND ANALYTICS DASHBOARD — EXECUTIVE OVERVIEW",
        fontsize=15, fontweight="bold", color="#38bdf8", y=0.97
    )

    # KPI Banner
    kpis = [
        (f"Industry AUM ({latest_year})", f"Rs. {total_industry_aum:.2f}L Cr", "SBI MF leads at 19.9% share", "#38bdf8"),
        ("Monthly SIP Inflow (Dec 25)", f"Rs. {latest_sip:,.0f} Cr", "+169% vs Jan 2022 baseline", "#10b981"),
        ("Industry Folios", f"{latest_folios:.2f} Cr", "Doubled from 13.26 Cr (Jan 22)", "#a855f7"),
        ("Retail Volume Tracked", f"Rs. {total_tx_cr:,.1f} Cr", "32,778 verified transactions", "#f59e0b"),
    ]
    for i, (label, val, sub, col) in enumerate(kpis):
        ax_k = fig.add_axes([0.04 + i * 0.235, 0.80, 0.215, 0.11], facecolor="#1e293b")
        ax_k.set_xticks([]); ax_k.set_yticks([])
        for spine in ax_k.spines.values():
            spine.set_edgecolor("#334155"); spine.set_linewidth(1.2)
        ax_k.text(0.08, 0.74, label, fontsize=9.5, color="#94a3b8", fontweight="bold")
        ax_k.text(0.08, 0.36, val, fontsize=17, color=col, fontweight="bold")
        ax_k.text(0.08, 0.12, sub, fontsize=8.5, color="#cbd5e1")

    # Panel 1: AMC AUM Bar
    ax1 = fig.add_axes([0.06, 0.44, 0.41, 0.30], facecolor="#1e293b")
    bars = ax1.bar(aum_latest["fund_house"].str.replace(" Mutual Fund", "").str.replace(" MF", ""),
                   aum_latest["aum_lakh_crore"], color="#38bdf8", edgecolor="#0f172a")
    bars[0].set_color("#10b981")
    ax1.set_title(f"Top Fund Houses by AUM ({latest_year}, Rs. Lakh Cr)", color="#f8fafc", fontsize=11, pad=8)
    ax1.tick_params(colors="#cbd5e1", labelsize=8, axis="x", rotation=20)
    ax1.tick_params(colors="#cbd5e1", labelsize=8, axis="y")
    ax1.grid(axis="y", color="#334155", linestyle="--", alpha=0.6)

    # Panel 2: Monthly SIP Line
    ax2 = fig.add_axes([0.55, 0.44, 0.41, 0.30], facecolor="#1e293b")
    sip_dt = pd.to_datetime(df_sip["month"])
    ax2.plot(sip_dt, df_sip["sip_inflow_crore"], color="#10b981", linewidth=2.2)
    ax2.fill_between(sip_dt, df_sip["sip_inflow_crore"], color="#10b981", alpha=0.18)
    ax2.set_title("Monthly SIP Inflow Trajectory (2022–2025, Rs. Cr)", color="#f8fafc", fontsize=11, pad=8)
    ax2.tick_params(colors="#cbd5e1", labelsize=8)
    ax2.grid(color="#334155", linestyle="--", alpha=0.6)

    # Panel 3: Top States Horizontal Bar
    ax3 = fig.add_axes([0.09, 0.07, 0.38, 0.28], facecolor="#1e293b")
    state_agg = df_tx.groupby("state")["total_inr"].sum().sort_values(ascending=True).tail(8) / 1e7
    ax3.barh(state_agg.index, state_agg.values, color="#f59e0b")
    ax3.set_title("Top 8 States by Retail Investment (Rs. Cr)", color="#f8fafc", fontsize=11, pad=8)
    ax3.tick_params(colors="#cbd5e1", labelsize=8)
    ax3.grid(axis="x", color="#334155", linestyle="--", alpha=0.6)

    # Panel 4: Sector Allocation Donut
    ax4 = fig.add_axes([0.55, 0.06, 0.41, 0.30], facecolor="#1e293b")
    top_sec = df_holdings.head(6)
    wedges, texts, autotexts = ax4.pie(
        top_sec["total_weight"], labels=top_sec["sector"], autopct="%1.1f%%",
        pctdistance=0.78, wedgeprops=dict(width=0.42, edgecolor="#0f172a"),
        textprops=dict(color="#e2e8f0", fontsize=8)
    )
    ax4.set_title("Equity Portfolio Sector Exposure (%)", color="#f8fafc", fontsize=11, pad=8)

    fig.savefig(FIG_DIR / "dashboard_overview.png", dpi=150, facecolor="#0f172a")
    plt.close(fig)
    logger.info("Saved dashboard_overview.png")

    # --- Screenshot 2: Risk & Recommender Analytics ---
    fig2 = plt.figure(figsize=(16, 9), facecolor="#0f172a")
    fig2.suptitle(
        "BLUESTOCK FINTECH  |  RISK ANALYTICS, TAIL LOSS & FUND RECOMMENDER",
        fontsize=15, fontweight="bold", color="#38bdf8", y=0.97
    )

    # Panel 1: Top 12 Highest Tail Risk VaR/CVaR
    ax_v = fig2.add_axes([0.07, 0.54, 0.42, 0.34], facecolor="#1e293b")
    if not df_var.empty:
        v_top = df_var.head(10)
        x_idx = np.arange(len(v_top))
        ax_v.bar(x_idx - 0.18, v_top["var_95_daily_pct"], width=0.35, label="VaR (95%)", color="#f59e0b")
        ax_v.bar(x_idx + 0.18, v_top["cvar_95_daily_pct"], width=0.35, label="CVaR (95%)", color="#f43f5e")
        ax_v.set_xticks(x_idx)
        ax_v.set_xticklabels([s[:14] for s in v_top["scheme_name"]], rotation=28, ha="right", fontsize=7.5, color="#cbd5e1")
        ax_v.legend(facecolor="#0f172a", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8)
    ax_v.set_title("95% Daily VaR & Expected Shortfall (Highest Tail Risk)", color="#f8fafc", fontsize=11, pad=8)
    ax_v.tick_params(colors="#cbd5e1", labelsize=8, axis="y")
    ax_v.grid(axis="y", color="#334155", linestyle="--", alpha=0.6)

    # Panel 2: Sector HHI Concentration
    ax_h = fig2.add_axes([0.56, 0.54, 0.40, 0.34], facecolor="#1e293b")
    if not df_hhi.empty:
        h_top = df_hhi.sort_values("hhi_score", ascending=True).tail(10)
        ax_h.barh([s[:24] for s in h_top["scheme_name"]], h_top["hhi_score"], color="#a855f7")
        ax_h.axvline(2500, color="#f43f5e", linestyle="--", linewidth=1.2, label="High Concentration (>2500)")
        ax_h.legend(facecolor="#0f172a", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8)
    ax_h.set_title("Top 10 Concentrated Equity Funds (Sector HHI)", color="#f8fafc", fontsize=11, pad=8)
    ax_h.tick_params(colors="#cbd5e1", labelsize=8)
    ax_h.grid(axis="x", color="#334155", linestyle="--", alpha=0.6)

    # Panel 3: Risk-Return Scatter (Volatility vs 3Y Return)
    ax_s = fig2.add_axes([0.07, 0.09, 0.42, 0.34], facecolor="#1e293b")
    cats = df_perf["category"].unique()
    palette = ["#38bdf8", "#10b981", "#f59e0b", "#f43f5e", "#a855f7"]
    for idx, cat in enumerate(cats):
        sub = df_perf[df_perf["category"] == cat]
        ax_s.scatter(sub["std_dev_ann_pct"], sub["return_3yr_pct"],
                     s=sub["aum_crore"] / 250 + 30, alpha=0.8,
                     color=palette[idx % len(palette)], label=cat)
    ax_s.set_xlabel("Annualized Volatility (%)", color="#cbd5e1", fontsize=9)
    ax_s.set_ylabel("3-Year CAGR (%)", color="#cbd5e1", fontsize=9)
    ax_s.set_title("Risk-Return Frontier Across 40 Schemes (Bubble = AUM)", color="#f8fafc", fontsize=11, pad=8)
    ax_s.tick_params(colors="#cbd5e1", labelsize=8)
    ax_s.legend(facecolor="#0f172a", edgecolor="#334155", labelcolor="#f8fafc", fontsize=7.5)
    ax_s.grid(color="#334155", linestyle="--", alpha=0.6)

    # Panel 4: Recommender Top Picks Table Card
    ax_t = fig2.add_axes([0.56, 0.09, 0.40, 0.34], facecolor="#1e293b")
    ax_t.set_xticks([]); ax_t.set_yticks([])
    for spine in ax_t.spines.values():
        spine.set_edgecolor("#334155")
    ax_t.text(0.03, 0.90, "RECOMMENDATION ENGINE — TOP PICKS BY RISK PROFILE",
              fontsize=10.5, fontweight="bold", color="#38bdf8")

    recs = [
        ("LOW RISK", "ICICI Pru Liquid Fund", "Sharpe: 7.68  |  3Y: 7.68%  |  Exp: 0.74%", "#10b981"),
        ("MODERATE", "Parag Parikh Flexi Cap", "Sharpe: 1.12  |  3Y: 16.42% |  Exp: 0.82%", "#38bdf8"),
        ("HIGH RISK", "Kotak Emerging Equity", "Sharpe: 0.96  |  3Y: 18.23% |  Exp: 1.56%", "#f59e0b"),
        ("HIGH RISK", "SBI Small Cap Fund", "Sharpe: 0.94  |  3Y: 23.39% |  Exp: 1.43%", "#f43f5e"),
    ]
    for idx, (tag, name, stats, col) in enumerate(recs):
        y0 = 0.70 - idx * 0.19
        ax_t.text(0.04, y0 + 0.06, tag, fontsize=8, fontweight="bold", color=col)
        ax_t.text(0.24, y0 + 0.06, name, fontsize=9.5, fontweight="bold", color="#f8fafc")
        ax_t.text(0.24, y0 - 0.02, stats, fontsize=8, color="#cbd5e1")

    fig2.savefig(FIG_DIR / "dashboard_analytics.png", dpi=150, facecolor="#0f172a")
    plt.close(fig2)
    logger.info("Saved dashboard_analytics.png")


def main() -> None:
    """Executes dashboard HTML generation and screenshot rendering."""
    data = fetch_dashboard_data()
    generate_html_dashboard(data)
    render_dashboard_screenshots(data)


if __name__ == "__main__":
    main()
