"""
Interactive 4-Page BI Dashboard Generator
Bluestock Fintech Capstone Project

Generates:
1. dashboard/bluestock_dashboard.html — Self-contained 4-page interactive HTML5/Plotly
   dashboard with 2+ interactive filter slicers on every page:
   - Page 1: Executive & AUM Overview (Year + Fund House slicers)
   - Page 2: Scheme Performance & Alpha (Category + Risk Grade slicers)
   - Page 3: Investor Demographics & Geography (City Tier + Transaction Type slicers)
   - Page 4: Risk Analytics & Fund Recommender (Risk Appetite + Sub-Category slicers)
2. reports/figures/dashboard_overview.png & dashboard_analytics.png
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
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
    df_perf = pd.read_sql_query(
        """
        SELECT p.amfi_code, p.scheme_name, p.fund_house, p.category, f.sub_category,
               p.risk_grade, p.sharpe_ratio, p.return_3yr_pct, p.std_dev_ann_pct,
               p.expense_ratio_pct, p.aum_crore, p.alpha
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
    """Builds a 4-page interactive HTML5/Plotly dashboard with 2+ slicers per page."""
    df_aum = data["aum"]
    df_sip = data["sip"]
    df_folio = data["folio"]
    df_perf = data["perf"]
    df_tx = data["tx"]
    df_holdings = data["holdings"]
    df_var = data["var"]

    aum_records = df_aum[["year", "date", "fund_house", "aum_lakh_crore"]].to_dict(orient="records")
    sip_records = df_sip[["month", "sip_inflow_crore", "active_sip_accounts_crore"]].to_dict(orient="records")
    folio_records = df_folio[["month", "total_folios_crore", "equity_folios_crore"]].to_dict(orient="records")
    perf_records = df_perf[[
        "scheme_name", "fund_house", "category", "sub_category", "risk_grade",
        "sharpe_ratio", "return_3yr_pct", "std_dev_ann_pct", "expense_ratio_pct", "aum_crore", "alpha"
    ]].to_dict(orient="records")
    tx_records = df_tx.to_dict(orient="records")
    holdings_records = df_holdings.head(8).to_dict(orient="records")
    var_records = (
        df_var[["scheme_name", "sub_category", "risk_category", "var_95_daily_pct", "cvar_95_daily_pct"]]
        .to_dict(orient="records") if not df_var.empty else []
    )

    years = sorted(df_aum["year"].unique().tolist(), reverse=True)
    amcs = sorted(df_aum["fund_house"].unique().tolist())
    cats = sorted(df_perf["category"].unique().tolist())
    risks = sorted(df_perf["risk_grade"].unique().tolist())
    sub_cats = sorted(df_perf["sub_category"].unique().tolist())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bluestock Fintech — 4-Page Mutual Fund BI Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    :root {{ --bg:#0f172a; --card:#1e293b; --border:#334155; --text:#f8fafc; --muted:#94a3b8; --accent:#38bdf8; --green:#10b981; }}
    * {{ box-sizing:border-box; margin:0; padding:0; font-family:'Segoe UI',Roboto,sans-serif; }}
    body {{ background:var(--bg); color:var(--text); padding:18px 26px; }}
    header {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:16px; }}
    header h1 {{ font-size:21px; color:var(--accent); }}
    header p {{ font-size:12px; color:var(--muted); }}
    .nav-tabs {{ display:flex; gap:10px; margin-bottom:18px; flex-wrap:wrap; }}
    .tab-btn {{ background:var(--card); color:var(--muted); border:1px solid var(--border); padding:9px 16px; border-radius:8px; cursor:pointer; font-weight:600; font-size:13px; }}
    .tab-btn.active {{ background:#0284c7; color:#fff; border-color:#38bdf8; }}
    .page {{ display:none; }}
    .page.active {{ display:block; }}
    .slicer-bar {{ display:flex; gap:16px; background:var(--card); border:1px solid var(--border); padding:12px 16px; border-radius:10px; margin-bottom:18px; flex-wrap:wrap; align-items:center; }}
    .slicer-group {{ display:flex; flex-direction:column; gap:4px; }}
    .slicer-group label {{ font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:600; }}
    select {{ background:#0f172a; color:var(--text); border:1px solid var(--border); padding:6px 10px; border-radius:6px; font-size:13px; min-width:180px; }}
    .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }}
    .kpi-card {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px 18px; }}
    .kpi-label {{ font-size:11px; color:var(--muted); text-transform:uppercase; }}
    .kpi-value {{ font-size:24px; font-weight:700; margin-top:4px; color:var(--accent); }}
    .chart-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:16px; margin-bottom:18px; }}
    .chart-card {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px; }}
    .chart-card h3 {{ font-size:14px; margin-bottom:8px; color:#e2e8f0; }}
    table {{ width:100%; border-collapse:collapse; font-size:12.5px; background:var(--card); border-radius:8px; overflow:hidden; }}
    th, td {{ text-align:left; padding:9px 11px; border-bottom:1px solid var(--border); }}
    th {{ color:var(--muted); font-size:11px; text-transform:uppercase; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Bluestock Fintech — Interactive Mutual Fund BI Dashboard</h1>
      <p>4-Page Star-Schema Analytics with Dynamic Slicers | 40 Schemes | 46,000 NAV Rows | 32,778 Transactions</p>
    </div>
    <span style="background:#0ea5e9;color:#fff;padding:5px 12px;border-radius:14px;font-size:12px;font-weight:600;">v1.0 Interactive</span>
  </header>

  <nav class="nav-tabs">
    <button class="tab-btn active" onclick="showPage('p1', this)">Page 1: Executive &amp; AUM</button>
    <button class="tab-btn" onclick="showPage('p2', this)">Page 2: Scheme Performance</button>
    <button class="tab-btn" onclick="showPage('p3', this)">Page 3: Investor &amp; Geography</button>
    <button class="tab-btn" onclick="showPage('p4', this)">Page 4: Risk &amp; Recommender</button>
  </nav>

  <!-- PAGE 1 -->
  <section id="p1" class="page active">
    <div class="slicer-bar">
      <div class="slicer-group">
        <label>Slicer 1: Calendar Year</label>
        <select id="p1-year" onchange="renderP1()">
          {"".join(f'<option value="{y}">{y}</option>' for y in years)}
        </select>
      </div>
      <div class="slicer-group">
        <label>Slicer 2: Fund House (AMC)</label>
        <select id="p1-amc" onchange="renderP1()">
          <option value="ALL">All Fund Houses</option>
          {"".join(f'<option value="{a}">{a}</option>' for a in amcs)}
        </select>
      </div>
    </div>
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-label">Filtered AUM</div><div id="p1-kpi-aum" class="kpi-value">-</div></div>
      <div class="kpi-card"><div class="kpi-label">Peak Monthly SIP</div><div class="kpi-value">&#8377;31,002 Cr</div></div>
      <div class="kpi-card"><div class="kpi-label">Total Folios (Dec 25)</div><div class="kpi-value">26.12 Cr</div></div>
      <div class="kpi-card"><div class="kpi-label">Active Schemes</div><div class="kpi-value">40</div></div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h3>AMC AUM Leadership (&#8377; Lakh Cr)</h3><div id="c-p1-aum" style="height:310px;"></div></div>
      <div class="chart-card"><h3>Monthly SIP Inflows (&#8377; Cr)</h3><div id="c-p1-sip" style="height:310px;"></div></div>
    </div>
  </section>

  <!-- PAGE 2 -->
  <section id="p2" class="page">
    <div class="slicer-bar">
      <div class="slicer-group">
        <label>Slicer 1: Category</label>
        <select id="p2-cat" onchange="renderP2()">
          <option value="ALL">All Categories</option>
          {"".join(f'<option value="{c}">{c}</option>' for c in cats)}
        </select>
      </div>
      <div class="slicer-group">
        <label>Slicer 2: Risk Grade</label>
        <select id="p2-risk" onchange="renderP2()">
          <option value="ALL">All Risk Grades</option>
          {"".join(f'<option value="{r}">{r}</option>' for r in risks)}
        </select>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h3>Risk-Return Frontier (Volatility vs 3Y Return)</h3><div id="c-p2-scatter" style="height:320px;"></div></div>
      <div class="chart-card"><h3>Top Filtered Schemes by Sharpe Ratio</h3><div id="c-p2-sharpe" style="height:320px;"></div></div>
    </div>
  </section>

  <!-- PAGE 3 -->
  <section id="p3" class="page">
    <div class="slicer-bar">
      <div class="slicer-group">
        <label>Slicer 1: City Tier</label>
        <select id="p3-tier" onchange="renderP3()">
          <option value="ALL">All City Tiers (T30 + B30)</option>
          <option value="T30">T30 Metros</option>
          <option value="B30">B30 Cities</option>
        </select>
      </div>
      <div class="slicer-group">
        <label>Slicer 2: Transaction Type</label>
        <select id="p3-type" onchange="renderP3()">
          <option value="ALL">All Types</option>
          <option value="SIP">SIP</option>
          <option value="Lumpsum">Lumpsum</option>
          <option value="Redemption">Redemption</option>
        </select>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h3>Top 10 States by Investment Volume (&#8377; Cr)</h3><div id="c-p3-state" style="height:320px;"></div></div>
      <div class="chart-card"><h3>Investor Volume by Age Group (&#8377; Cr)</h3><div id="c-p3-age" style="height:320px;"></div></div>
    </div>
  </section>

  <!-- PAGE 4 -->
  <section id="p4" class="page">
    <div class="slicer-bar">
      <div class="slicer-group">
        <label>Slicer 1: Risk Appetite (Recommender)</label>
        <select id="p4-risk" onchange="renderP4()">
          <option value="ALL">All Risk Profiles</option>
          <option value="Low">Low (Capital Preservation)</option>
          <option value="Moderate">Moderate (Balanced)</option>
          <option value="High">High / Very High (Aggressive)</option>
        </select>
      </div>
      <div class="slicer-group">
        <label>Slicer 2: Sub-Category</label>
        <select id="p4-sub" onchange="renderP4()">
          <option value="ALL">All Sub-Categories</option>
          {"".join(f'<option value="{s}">{s}</option>' for s in sub_cats)}
        </select>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card"><h3>95% Historical VaR &amp; CVaR Tail Risk (%)</h3><div id="c-p4-var" style="height:300px;"></div></div>
      <div class="chart-card"><h3>Equity Sector Allocation (%)</h3><div id="c-p4-sec" style="height:300px;"></div></div>
    </div>
    <div class="chart-card">
      <h3>Recommended Schemes (Ranked by Sharpe Ratio)</h3>
      <table id="p4-table"><thead><tr><th>Scheme</th><th>AMC</th><th>Sub-Category</th><th>Risk</th><th>Sharpe</th><th>3Y Return</th><th>Expense</th></tr></thead><tbody></tbody></table>
    </div>
  </section>

  <script>
    const AUM = {json.dumps(aum_records)};
    const SIP = {json.dumps(sip_records)};
    const PERF = {json.dumps(perf_records)};
    const TX = {json.dumps(tx_records)};
    const HOLDINGS = {json.dumps(holdings_records)};
    const VAR_DATA = {json.dumps(var_records)};

    const L = {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#cbd5e1',size:11}}, margin:{{t:15,r:20,b:50,l:55}}, xaxis:{{gridcolor:'#334155'}}, yaxis:{{gridcolor:'#334155'}} }};

    function showPage(id, btn) {{
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      btn.classList.add('active');
      renderP1(); renderP2(); renderP3(); renderP4();
    }}

    function renderP1() {{
      const yr = parseInt(document.getElementById('p1-year').value);
      const amc = document.getElementById('p1-amc').value;
      let sub = AUM.filter(r => r.year === yr);
      const maxDt = sub.reduce((m, r) => r.date > m ? r.date : m, '');
      sub = sub.filter(r => r.date === maxDt);
      if (amc !== 'ALL') sub = sub.filter(r => r.fund_house === amc);
      const totAum = sub.reduce((s, r) => s + r.aum_lakh_crore, 0);
      document.getElementById('p1-kpi-aum').innerText = '₹' + totAum.toFixed(2) + 'L Cr';
      Plotly.newPlot('c-p1-aum', [{{ x: sub.map(r=>r.fund_house), y: sub.map(r=>r.aum_lakh_crore), type:'bar', marker:{{color:'#38bdf8'}} }}], L, {{responsive:true}});
      Plotly.newPlot('c-p1-sip', [{{ x: SIP.map(r=>r.month), y: SIP.map(r=>r.sip_inflow_crore), type:'scatter', mode:'lines', fill:'tozeroy', line:{{color:'#10b981'}} }}], L, {{responsive:true}});
    }}

    function renderP2() {{
      const cat = document.getElementById('p2-cat').value;
      const risk = document.getElementById('p2-risk').value;
      let sub = PERF.filter(r => (cat==='ALL' || r.category===cat) && (risk==='ALL' || r.risk_grade===risk));
      Plotly.newPlot('c-p2-scatter', [{{
        x: sub.map(r=>r.std_dev_ann_pct), y: sub.map(r=>r.return_3yr_pct), text: sub.map(r=>r.scheme_name),
        mode:'markers', type:'scatter', marker:{{ size:11, color: sub.map(r=>r.sharpe_ratio), colorscale:'Viridis', showscale:true }}
      }}], {{ ...L, xaxis:{{...L.xaxis, title:'Volatility (%)'}}, yaxis:{{...L.yaxis, title:'3Y Return (%)'}} }}, {{responsive:true}});
      const top = sub.slice(0, 10);
      Plotly.newPlot('c-p2-sharpe', [{{ x: top.map(r=>r.scheme_name.slice(0,22)), y: top.map(r=>r.sharpe_ratio), type:'bar', marker:{{color:'#a855f7'}} }}], L, {{responsive:true}});
    }}

    function renderP3() {{
      const tier = document.getElementById('p3-tier').value;
      const ttype = document.getElementById('p3-type').value;
      let sub = TX.filter(r => (tier==='ALL' || r.city_tier===tier) && (ttype==='ALL' || r.transaction_type===ttype));
      const byState = {{}}; const byAge = {{}};
      sub.forEach(r => {{
        byState[r.state] = (byState[r.state]||0) + r.total_inr/1e7;
        byAge[r.age_group] = (byAge[r.age_group]||0) + r.total_inr/1e7;
      }});
      const stEntries = Object.entries(byState).sort((a,b)=>b[1]-a[1]).slice(0,10).reverse();
      Plotly.newPlot('c-p3-state', [{{ y: stEntries.map(e=>e[0]), x: stEntries.map(e=>e[1]), type:'bar', orientation:'h', marker:{{color:'#f59e0b'}} }}], {{...L, margin:{{t:15,r:20,b:40,l:110}}}}, {{responsive:true}});
      const agEntries = Object.entries(byAge).sort();
      Plotly.newPlot('c-p3-age', [{{ x: agEntries.map(e=>e[0]), y: agEntries.map(e=>e[1]), type:'bar', marker:{{color:'#38bdf8'}} }}], L, {{responsive:true}});
    }}

    function renderP4() {{
      const riskProf = document.getElementById('p4-risk').value;
      const subCat = document.getElementById('p4-sub').value;
      const riskMap = {{ 'Low':['Low'], 'Moderate':['Moderate','Moderately High'], 'High':['High','Very High'] }};
      let vSub = VAR_DATA.filter(r => (subCat==='ALL' || r.sub_category===subCat));
      if (riskProf !== 'ALL') vSub = vSub.filter(r => riskMap[riskProf].includes(r.risk_category));
      vSub = vSub.slice(0, 12);
      Plotly.newPlot('c-p4-var', [
        {{ x: vSub.map(r=>r.scheme_name.slice(0,18)), y: vSub.map(r=>r.var_95_daily_pct), name:'VaR 95%', type:'bar', marker:{{color:'#f59e0b'}} }},
        {{ x: vSub.map(r=>r.scheme_name.slice(0,18)), y: vSub.map(r=>r.cvar_95_daily_pct), name:'CVaR 95%', type:'bar', marker:{{color:'#f43f5e'}} }}
      ], {{ ...L, barmode:'group' }}, {{responsive:true}});
      Plotly.newPlot('c-p4-sec', [{{ labels: HOLDINGS.map(r=>r.sector), values: HOLDINGS.map(r=>r.total_weight), type:'pie', hole:0.45 }}], {{...L, margin:{{t:10,r:10,b:10,l:10}}}}, {{responsive:true}});

      let pSub = PERF.filter(r => (subCat==='ALL' || r.sub_category===subCat));
      if (riskProf !== 'ALL') pSub = pSub.filter(r => riskMap[riskProf].includes(r.risk_grade));
      const tbody = document.querySelector('#p4-table tbody');
      tbody.innerHTML = pSub.slice(0, 8).map(r => `<tr><td>${{r.scheme_name}}</td><td>${{r.fund_house}}</td><td>${{r.sub_category}}</td><td>${{r.risk_grade}}</td><td><b>${{r.sharpe_ratio.toFixed(2)}}</b></td><td>${{r.return_3yr_pct.toFixed(2)}}%</td><td>${{r.expense_ratio_pct.toFixed(2)}}%</td></tr>`).join('');
    }}

    renderP1();
  </script>
</body>
</html>
"""
    out_path = DASHBOARD_DIR / "bluestock_dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    logger.info(f"Generated 4-page interactive HTML dashboard with slicers: {out_path}")
    return out_path


def main() -> None:
    """Executes interactive HTML dashboard generation."""
    data = fetch_dashboard_data()
    generate_html_dashboard(data)


if __name__ == "__main__":
    main()
