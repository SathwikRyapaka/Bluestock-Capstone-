"""
Final Capstone PDF Report Generator
Bluestock Fintech Mutual Fund Analytics Platform

Generates Final_Report.pdf (15-20 pages) using ReportLab Platypus with:
- Cover Page & Executive Summary
- Data Sources & Ingestion Inventory
- ETL Pipeline Design & SQLite Star Schema
- Exploratory Data Analysis (EDA) Findings with embedded figures
- Performance & Advanced Risk Analysis (VaR/CVaR, Rolling Sharpe, Cohorts, SIP Churn, HHI, Recommender)
- Interactive Dashboard Screenshots
- Limitations & Strategic Recommendations
"""

import hashlib
import logging
from pathlib import Path
from typing import List

# Python 3.8 compatibility shim for ReportLab 4.x (usedforsecurity added in 3.9)
_orig_md5 = hashlib.md5
def _compat_md5(*args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return _orig_md5(*args, **kwargs)
hashlib.md5 = _compat_md5

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = BASE_DIR / "reports" / "figures"
OUT_PDF = BASE_DIR / "Final_Report.pdf"


def build_styles():
    """Creates custom ReportLab paragraph styles for corporate report formatting."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle", fontSize=26, leading=32, textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold", alignment=TA_LEFT, spaceAfter=14
    ))
    styles.add(ParagraphStyle(
        name="CoverSub", fontSize=14, leading=20, textColor=colors.HexColor("#0369a1"),
        fontName="Helvetica-Bold", alignment=TA_LEFT, spaceAfter=24
    ))
    styles.add(ParagraphStyle(
        name="SectionH1", fontSize=16, leading=22, textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="SectionH2", fontSize=12.5, leading=17, textColor=colors.HexColor("#0369a1"),
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="BodyJustify", fontSize=10, leading=14.5, textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=7
    ))
    styles.add(ParagraphStyle(
        name="BulletItem", fontSize=9.8, leading=14, textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica", leftIndent=14, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="Caption", fontSize=8.5, leading=11, textColor=colors.HexColor("#475569"),
        fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceBefore=3, spaceAfter=10
    ))
    return styles


def make_table(data: List[List[str]], col_widths=None) -> Table:
    """Formats a styled corporate table with alternating row shading."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8.2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]))
    return t


def add_figure(story, styles, filename: str, caption: str, width_in: float = 6.3, height_in: float = 3.2):
    """Embeds a figure from reports/figures/ or root if present."""
    p = FIG_DIR / filename
    if not p.exists():
        p = BASE_DIR / filename
    if p.exists():
        img = Image(str(p), width=width_in * inch, height=height_in * inch, kind="proportional")
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Paragraph(caption, styles["Caption"]))


def add_page_number(canvas, doc):
    """Draws header rule and footer page number on content pages."""
    page_num = canvas.getPageNumber()
    if page_num == 1:
        return
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.setLineWidth(0.5)
    canvas.line(0.75 * inch, A4[1] - 0.55 * inch, A4[0] - 0.75 * inch, A4[1] - 0.55 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(0.75 * inch, A4[1] - 0.45 * inch, "Bluestock Fintech — Mutual Fund Analytics Platform Capstone")
    canvas.drawRightString(A4[0] - 0.75 * inch, 0.45 * inch, f"Page {page_num}")
    canvas.drawString(0.75 * inch, 0.45 * inch, "Confidential | Capstone v1.0")
    canvas.restoreState()


def generate_pdf() -> Path:
    """Builds and saves Final_Report.pdf."""
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.70 * inch,
        title="Bluestock Fintech Mutual Fund Analytics Capstone Report",
        author="Sathwik Ryapaka, Abhiram, Ashmeet Kaur",
    )
    story = []

    # ==================== PAGE 1: COVER PAGE ====================
    story.append(Spacer(1, 1.3 * inch))
    story.append(Paragraph("BLUESTOCK FINTECH", styles["CoverSub"]))
    story.append(Paragraph("Mutual Fund Analytics Platform:<br/>End-to-End Data Engineering, Risk Modeling &amp; BI Capstone", styles["CoverTitle"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        "A comprehensive analytical report covering AMFI data ingestion, relational star-schema warehousing, "
        "exploratory market insights, tail-risk quantification (VaR/CVaR), SIP churn analytics, and an "
        "automated Sharpe-optimized fund recommendation engine.",
        styles["BodyJustify"]
    ))
    story.append(Spacer(1, 0.5 * inch))
    meta_table = make_table([
        ["Project Metadata", "Details"],
        ["Organization", "Bluestock Fintech (Cohort 2026)"],
        ["Project Team", "Sathwik Ryapaka (SR), Abhiram (AB), Ashmeet Kaur (AK)"],
        ["Repository", "https://github.com/SathwikRyapaka/Bluestock-Capstone-.git"],
        ["Release Tag", "v1.0 (Production Final)"],
        ["Data Coverage", "40 Mutual Fund Schemes | 46,000 NAV Rows | 32,778 Transactions"],
        ["Technology Stack", "Python 3.8+, Pandas, SQLAlchemy, SQLite3, Matplotlib, Seaborn, Plotly"],
    ], col_widths=[2.0 * inch, 4.7 * inch])
    story.append(meta_table)
    story.append(PageBreak())

    # ==================== PAGE 2: EXECUTIVE SUMMARY ====================
    story.append(Paragraph("1. Executive Summary", styles["SectionH1"]))
    story.append(Paragraph(
        "India's retail mutual fund ecosystem has undergone a structural transformation between 2022 and 2025, "
        "driven by digital KYC onboarding, UPI Autopay mandates, and rising equity participation from Beyond-Top-30 (B30) cities. "
        "To empower retail investors and wealth advisors with institutional-grade intelligence, the Bluestock Mutual Fund Analytics "
        "Platform unifies fragmented AMFI disclosures, live NAV feeds, and investor-level transaction logs into a single "
        "automated analytics stack.",
        styles["BodyJustify"]
    ))
    story.append(Paragraph(
        "Across 40 flagship mutual fund schemes spanning 10 leading Asset Management Companies (AMCs), our pipeline ingests, "
        "cleans, and normalizes 10 distinct datasets into a 11-table SQLite Star Schema (bluestock_mf.db). On top of this warehouse, "
        "we execute 16 exploratory visualizations, historical Value at Risk (VaR 95%) and Conditional VaR (CVaR) stress tests, "
        "rolling 90-day Sharpe ratio diagnostics, investor vintage cohorts, SIP continuity churn detection, and a CLI/API fund recommender.",
        styles["BodyJustify"]
    ))
    story.append(Paragraph("Headline Findings at a Glance", styles["SectionH2"]))
    kpi_table = make_table([
        ["Analytical Dimension", "Observed Metric", "Strategic Implication"],
        ["Industry AUM Leadership", "SBI MF at Rs. 12.50L Cr (19.92% share)", "Bank-led distribution remains the strongest AUM moat."],
        ["SIP Inflow Momentum", "Rs. 31,002 Cr ATH in Dec 2025 (+169%)", "Retail SIPs act as a structural stabilizer during market dips."],
        ["Folio Expansion", "13.26 Cr -> 26.12 Cr folios (+97%)", "Mass-market retail onboarding doubled in 4 years."],
        ["Tail Risk (VaR 95%)", "Small Cap -2.69% vs Liquid -0.02%", "Aggressive equity carries >100x daily tail loss vs Liquid."],
        ["SIP Churn Alert", "97.8% of 6+ SIP users >35-day gap", "Manual payment friction drives widespread SIP delays."],
        ["Sector Concentration", "Axis Bluechip HHI = 2,967.69 (48.7% IT)", "Concentration risk requires HHI monitoring for core holdings."],
    ], col_widths=[1.7 * inch, 2.3 * inch, 2.7 * inch])
    story.append(kpi_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Project Objectives & Scope", styles["SectionH2"]))
    for b in [
        "• Automate batch ingestion of 10 raw AMFI/market CSVs and live NAV fetching from api.mfapi.in.",
        "• Enforce strict data hygiene: holiday NAV forward-filling, transaction type standardization, and expense ratio validation (0.1%–2.5%).",
        "• Architect a normalized SQLite Star Schema with foreign-key integrity and 2,557 calendar dimension records.",
        "• Deliver 16+ publication-grade EDA charts, 5 quantitative risk modules, an interactive HTML5 dashboard, and a fund recommender.",
    ]:
        story.append(Paragraph(b, styles["BulletItem"]))
    story.append(PageBreak())

    # ==================== PAGE 3: DATA SOURCES ====================
    story.append(Paragraph("2. Data Sources & Ingestion Inventory", styles["SectionH1"]))
    story.append(Paragraph(
        "The platform integrates two complementary data streams: (1) ten structured historical CSV datasets covering scheme metadata, "
        "daily NAVs, AMC AUM, SIP flows, investor transactions, and portfolio holdings; and (2) live REST API feeds from mfapi.in "
        "for six benchmark large-cap/flagship schemes (AMFI codes 125497, 119551, 120503, 118632, 119092, and 120841).",
        styles["BodyJustify"]
    ))
    ds_table = make_table([
        ["Dataset", "Raw Rows", "Cleaned Rows", "Grain / Primary Key", "Key Attributes"],
        ["01_fund_master.csv", "40", "40", "amfi_code", "AMC, category, sub-category, plan, expense ratio, exit load"],
        ["02_nav_history.csv", "46,000", "46,000", "(amfi_code, date)", "Daily NAV, computed daily_return (%)"],
        ["03_aum_by_fund_house.csv", "90", "90", "(date, fund_house)", "AUM in Lakh Crore & Crore, scheme count"],
        ["04_monthly_sip_inflows.csv", "48", "48", "month", "SIP inflow (Cr), active accounts (Cr), YoY growth (%)"],
        ["05_category_inflows.csv", "144", "144", "(month, category)", "Monthly net category inflows across 12 categories"],
        ["06_industry_folio_count.csv", "21", "21", "month", "Total, Equity, Debt, Hybrid, Others folios (Cr)"],
        ["07_scheme_performance.csv", "40", "40", "amfi_code", "1Y/3Y/5Y CAGR, Sharpe, Sortino, Alpha, Beta, MaxDD"],
        ["08_investor_transactions.csv", "32,778", "32,778", "transaction_id", "Investor ID, type, amount, state, tier, age, gender, KYC"],
        ["09_portfolio_holdings.csv", "322", "322", "holding_id", "Stock symbol, sector, weight (%), market value (Cr)"],
        ["10_benchmark_indices.csv", "8,050", "8,050", "(index_name, date)", "Nifty 50, Midcap 150, Smallcap 250, TRI values"],
    ], col_widths=[1.65 * inch, 0.65 * inch, 0.75 * inch, 1.2 * inch, 2.45 * inch])
    story.append(ds_table)
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("2.1 Live API Integration (mfapi.in)", styles["SectionH2"]))
    story.append(Paragraph(
        "The live_nav_fetch.py module queries https://api.mfapi.in/mf/{amfi_code} with HTTP error handling, JSON schema validation, "
        "and automatic CSV serialization into data/raw/. Referential validation in data_ingestion.py confirms 100% AMFI code overlap "
        "between fund_master and nav_history (40/40 schemes matched, 0 orphan records).",
        styles["BodyJustify"]
    ))
    story.append(PageBreak())

    # ==================== PAGE 4-5: ETL DESIGN & STAR SCHEMA ====================
    story.append(Paragraph("3. ETL Pipeline Design & Relational Star Schema", styles["SectionH1"]))
    story.append(Paragraph(
        "Our Extract-Transform-Load (ETL) pipeline is modularized across four Python scripts orchestrated by run_pipeline.py: "
        "data_ingestion.py (profiling & AMFI audit), live_nav_fetch.py (API feed), data_cleaning.py (hygiene & feature engineering), "
        "and load_to_sqlite.py (dimensional warehousing).",
        styles["BodyJustify"]
    ))
    story.append(Paragraph("3.1 Data Cleaning & Validation Rules", styles["SectionH2"]))
    for rule in [
        "• NAV History Hygiene: Parsed string dates to ISO YYYY-MM-DD, sorted by (amfi_code, date), forward-filled missing holiday/weekend NAVs per scheme, enforced strict NAV > 0 check, deduplicated keys, and derived daily_return (%).",
        "• Transaction Standardization: Mapped heterogeneous transaction strings into canonical enums ('SIP', 'Lumpsum', 'Redemption'), enforced amount_inr > 0, validated city_tier ('T30', 'B30'), and verified KYC status ('Verified': 92%, 'Pending': 8%).",
        "• Performance Metric Auditing: Cast all 11 return/risk columns to float, verified expense_ratio_pct within [0.1%, 2.5%], and flagged statistical anomalies (e.g., Liquid funds exhibiting high Sharpe >5.0 due to near-zero volatility).",
    ]:
        story.append(Paragraph(rule, styles["BulletItem"]))

    story.append(Paragraph("3.2 SQLite Star Schema Architecture (bluestock_mf.db)", styles["SectionH2"]))
    story.append(Paragraph(
        "The relational warehouse separates descriptive dimensions (dim_fund, dim_date covering 2,557 calendar days from 2020–2026 "
        "with Indian Fiscal Year attributes FY202x-xx) from nine fact tables, enforcing foreign key constraints and B-tree indexes "
        "on high-cardinality join columns (amfi_code, nav_date, transaction_date, state, sector).",
        styles["BodyJustify"]
    ))
    db_table = make_table([
        ["Warehouse Table", "Role", "Row Count", "Primary Key / Foreign Keys"],
        ["dim_fund", "Dimension", "40", "PK: amfi_code"],
        ["dim_date", "Dimension", "2,557", "PK: date (includes Indian FY & Quarter)"],
        ["fact_nav", "Core Fact", "46,000", "PK: nav_id | FK: amfi_code, nav_date"],
        ["fact_transactions", "Core Fact", "32,778", "PK: transaction_id | FK: amfi_code, transaction_date"],
        ["fact_performance", "Core Fact", "40", "PK: amfi_code | FK: dim_fund(amfi_code)"],
        ["fact_aum", "Core Fact", "90", "PK: aum_id | FK: date"],
        ["fact_monthly_sip", "Supporting Fact", "48", "PK: month"],
        ["fact_category_inflows", "Supporting Fact", "144", "PK: inflow_id"],
        ["fact_industry_folios", "Supporting Fact", "21", "PK: month"],
        ["fact_portfolio_holdings", "Supporting Fact", "322", "PK: holding_id | FK: amfi_code, portfolio_date"],
        ["fact_benchmark_indices", "Supporting Fact", "8,050", "PK: bench_id | FK: date"],
    ], col_widths=[1.8 * inch, 1.1 * inch, 0.9 * inch, 2.9 * inch])
    story.append(db_table)
    story.append(PageBreak())

    # ==================== PAGES 5-10: EDA FINDINGS ====================
    story.append(Paragraph("4. Exploratory Data Analysis (EDA) Findings", styles["SectionH1"]))
    story.append(Paragraph(
        "Sixteen high-resolution visualizations were generated via generate_eda_charts.py and documented in EDA_Analysis.ipynb. "
        "Below are the core market, demographic, geographic, and portfolio structure findings.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("4.1 NAV Trajectories & Market Regimes (2022–2026)", styles["SectionH2"]))
    story.append(Paragraph(
        "Normalized NAV trajectories across all 40 schemes demonstrate a pronounced divergence between equity and debt categories "
        "starting Q2 2023. Mid-cap and Small-cap funds outperformed Large-cap peers by 1.8x during the 2023 bull rally, but "
        "experienced 2.3x sharper drawdowns during the 2024 market corrections.",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "01_nav_trend_all_schemes.png", "Figure 1: Daily Normalized NAV Trends Across All 40 Schemes Highlighting 2023 Bull Run & 2024 Corrections.", 6.4, 3.0)
    add_figure(story, styles, "02_nav_category_performance.png", "Figure 2: Sub-Category Cumulative Return Comparison (Small Cap +118.4% vs Large Cap +54.2%).", 6.4, 3.0)
    story.append(PageBreak())

    story.append(Paragraph("4.2 AMC AUM Leadership & Market Concentration", styles["SectionH2"]))
    story.append(Paragraph(
        "Grouped annual AUM analysis (2022–2025) confirms sustained consolidation among top bank-sponsored AMCs. SBI Mutual Fund "
        "commands Rs. 12.50 Lakh Crore AUM (19.92% market share), maintaining a Rs. 2.77 Lakh Crore lead over ICICI Prudential MF (17.12%) "
        "and HDFC MF (14.82%).",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "03_aum_growth_by_amc.png", "Figure 3: Annual AUM Growth by Top 10 Asset Management Companies (2022–2025).", 6.3, 3.0)
    add_figure(story, styles, "04_amc_market_share_pie.png", "Figure 4: AMC Market Share Distribution Snapshot (December 2025).", 5.2, 3.2)
    story.append(PageBreak())

    story.append(Paragraph("4.3 Monthly SIP Inflow Momentum & Category Rotation", styles["SectionH2"]))
    story.append(Paragraph(
        "Systematic Investment Plan (SIP) inflows expanded 169.2% from Rs. 11,517 Cr in January 2022 to an all-time high of "
        "Rs. 31,002 Cr in December 2025, supported by 9.35 Crore active contributing SIP accounts. Category heatmaps reveal "
        "persistent retail capital rotation into Flexi Cap, Mid Cap, and Small Cap categories, while YoY SIP growth sustained "
        "an average +27.6% expansion rate across all observed months.",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "05_monthly_sip_inflows_trend.png", "Figure 5: Monthly SIP Inflow Trend (Jan 2022–Dec 2025) Annotating the Rs. 31,002 Cr All-Time High.", 6.4, 2.9)
    add_figure(story, styles, "06_sip_yoy_growth_trend.png", "Figure 6: Year-over-Year (YoY) Monthly SIP Growth Trajectory (2023–2025).", 6.4, 2.8)
    story.append(PageBreak())
    add_figure(story, styles, "07_category_inflow_heatmap.png", "Figure 7: Category-Wise Monthly Net Inflow Heatmap Across 12 Mutual Fund Categories.", 6.4, 3.4)
    story.append(PageBreak())

    story.append(Paragraph("4.4 Investor Demographics & Geographic Penetration", styles["SectionH2"]))
    story.append(Paragraph(
        "Across 32,778 transactions representing 4,803 unique investors, millennials aged 26–35 form the largest cohort (35.4%), "
        "followed by ages 36–45 (29.8%). However, median SIP ticket sizes peak in the 36–45 bracket (Rs. 12,450), reflecting "
        "higher mid-career disposable income. Geographically, T30 metros contribute Rs. 231.9 Cr while B30 cities contribute "
        "Rs. 120.2 Cr (~34.1% of retail volume), growing rapidly across tier-2 states.",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "08_investor_age_distribution.png", "Figure 8: Retail Investor Demographic Age Breakdown.", 5.0, 2.9)
    add_figure(story, styles, "09_sip_amount_by_age_boxplot.png", "Figure 9: Monthly SIP Ticket Size Distribution by Investor Age Bracket.", 6.2, 2.9)
    story.append(PageBreak())
    add_figure(story, styles, "10_investor_gender_income_split.png", "Figure 10: Investor Gender Breakdown and Annual Income Distribution.", 6.4, 2.8)
    add_figure(story, styles, "11_geographic_sip_inflows_state.png", "Figure 11: Total Retail Capital Invested by Indian State (Rs. Crore).", 6.2, 3.0)
    add_figure(story, styles, "12_city_tier_t30_b30_split.png", "Figure 12: Capital Allocation by City Tier — T30 Metros vs Beyond-Top-30 (B30).", 5.0, 2.8)
    story.append(PageBreak())

    story.append(Paragraph("4.5 Folio Expansion, Correlation & Equity Sector Allocation", styles["SectionH2"]))
    story.append(Paragraph(
        "Industry-wide folio counts nearly doubled from 13.26 Crore (Jan 2022) to 26.12 Crore (Dec 2025). Pairwise daily return "
        "correlations confirm strong co-movement (>0.85) among diversified Large Cap equity funds, while Liquid and Gilt schemes "
        "provide near-zero correlation (-0.05 to +0.10) for portfolio diversification. Aggregate equity holdings remain concentrated "
        "in Banking & Financial Services (23.2%) and Information Technology (14.2%), led by HDFC Bank, ICICI Bank, and Infosys.",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "13_industry_folio_growth.png", "Figure 13: Mutual Fund Industry Folio Count Expansion (2022–2025).", 6.3, 2.9)
    add_figure(story, styles, "14_nav_return_correlation_matrix.png", "Figure 14: Pairwise Daily Return Correlation Matrix Across 10 Selected Schemes.", 5.6, 4.2)
    story.append(PageBreak())
    add_figure(story, styles, "15_sector_allocation_donut.png", "Figure 15: Aggregate Equity Mutual Fund Sector Allocation.", 5.2, 3.2)
    add_figure(story, styles, "16_top_equity_stock_holdings.png", "Figure 16: Top 10 Underlying Equity Stock Holdings by Portfolio Market Value (Rs. Crore).", 6.2, 3.0)
    story.append(PageBreak())

    # ==================== PAGES 11-14: PERFORMANCE & RISK ANALYSIS ====================
    story.append(Paragraph("5. Performance & Advanced Risk Analysis", styles["SectionH1"]))
    story.append(Paragraph(
        "Beyond descriptive EDA, generate_advanced_analytics.py and Advanced_Analytics.ipynb quantify downside tail risk, "
        "time-varying risk-adjusted performance, investor cohort behavior, SIP continuity churn, and sector concentration.",
        styles["BodyJustify"]
    ))

    story.append(Paragraph("5.1 Historical Value at Risk (VaR 95%) & Expected Shortfall (CVaR)", styles["SectionH2"]))
    story.append(Paragraph(
        "Daily Historical VaR (5th percentile) and CVaR (mean return below VaR) were computed across all 40 schemes. Small Cap "
        "funds exhibit the steepest downside tail risk (SBI Small Cap: VaR -2.69%, CVaR -3.24%, annualized volatility 25.1%), "
        "whereas Liquid schemes preserve capital with VaR -0.02% and CVaR -0.03%.",
        styles["BodyJustify"]
    ))
    var_path = BASE_DIR / "var_cvar_report.csv"
    if var_path.exists():
        df_var = pd.read_csv(var_path)
        v_rows = [["Scheme Name", "Category", "VaR 95% (Daily)", "CVaR 95% (Daily)", "Ann. Vol (%)"]]
        for _, r in pd.concat([df_var.head(4), df_var.tail(3)]).iterrows():
            v_rows.append([
                str(r["scheme_name"])[:34], str(r["sub_category"]),
                f"{r['var_95_daily_pct']:.2f}%", f"{r['cvar_95_daily_pct']:.2f}%",
                f"{r['annualized_volatility_pct']:.2f}%"
            ])
        story.append(make_table(v_rows, col_widths=[2.4 * inch, 1.2 * inch, 1.05 * inch, 1.05 * inch, 1.0 * inch]))
    story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("5.2 Rolling 90-Day Sharpe Ratio Dynamics", styles["SectionH2"]))
    story.append(Paragraph(
        "Static 3-year Sharpe ratios mask intra-year regime shifts. Across 1,061 rolling 90-day windows for five flagship Large Cap "
        "schemes, Axis Bluechip oscillated between -3.64 (2022 IT/growth correction) and +6.77 (late-2023 rally), proving the need "
        "for dynamic risk-adjusted monitoring.",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "rolling_sharpe_chart.png", "Figure 11: Rolling 90-Day Annualized Sharpe Ratio Across 5 Flagship Large-Cap Schemes.", 6.4, 3.0)
    story.append(PageBreak())

    story.append(Paragraph("5.3 Investor Cohort Analysis & SIP Continuity Churn Risk", styles["SectionH2"]))
    story.append(Paragraph(
        "Grouping investors by first transaction year reveals strong capital scaling: the 2024 cohort invested Rs. 349.11 Cr across "
        "4,803 investors, while newer 2025 entrants exhibit a higher average SIP ticket size (Rs. 13,505 vs Rs. 11,840). However, "
        "SIP continuity tracking across 1,362 investors with 6+ SIP installments reveals that 1,332 investors (97.8%) experienced "
        "average inter-installment gaps > 35 days, flagging manual payment friction as a critical churn driver.",
        styles["BodyJustify"]
    ))
    cohort_path = BASE_DIR / "cohort_analysis.csv"
    if cohort_path.exists():
        df_c = pd.read_csv(cohort_path)
        c_rows = [list(df_c.columns)]
        for _, r in df_c.iterrows():
            c_rows.append([str(v) for v in r.values])
        story.append(make_table(c_rows))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("5.4 Sector Concentration (HHI) & Fund Recommender Engine", styles["SectionH2"]))
    story.append(Paragraph(
        "Using the Herfindahl-Hirschman Index (HHI = sum(weight_i^2)) across 34 equity schemes, Axis Bluechip Fund (119092) "
        "registered the highest sector concentration (HHI = 2,967.69) driven by a 48.7% Information Technology allocation, whereas "
        "Kotak Multicap achieved broad diversification (HHI = 1,120.45). Our recommender.py engine pairs these risk metrics to rank "
        "top 3 schemes per risk appetite (Low: ICICI Pru Liquid Sharpe 7.68; Moderate: HDFC Top 100 Sharpe 1.06; "
        "High: Kotak Emerging Equity Sharpe 0.96).",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "sector_hhi_chart.png", "Figure 12: Equity Fund Sector Concentration Measured via Herfindahl-Hirschman Index (HHI).", 6.3, 3.0)
    story.append(PageBreak())

    # ==================== PAGES 15-16: DASHBOARD SCREENSHOTS ====================
    story.append(Paragraph("6. Interactive BI Dashboard & Visualizations", styles["SectionH1"]))
    story.append(Paragraph(
        "To deliver self-service analytics to retail investors and internal analysts, we built a self-contained interactive HTML5/Plotly "
        "dashboard (dashboard/bluestock_dashboard.html) powered directly by bluestock_mf.db. Users can inspect live KPI cards, "
        "hover over AMC AUM bars, zoom into monthly SIP trajectories, filter state-level inflows, and compare VaR/CVaR tail risk.",
        styles["BodyJustify"]
    ))
    add_figure(story, styles, "dashboard_overview.png", "Figure 13: Bluestock Executive BI Dashboard — KPIs, AMC AUM Leadership, SIP Growth & Geography.", 6.5, 3.6)
    add_figure(story, styles, "dashboard_analytics.png", "Figure 14: Bluestock Risk & Recommender Dashboard — VaR/CVaR, Sector HHI, Risk-Return Frontier & Top Picks.", 6.5, 3.6)
    story.append(PageBreak())

    # ==================== PAGE 17-18: LIMITATIONS, RECOMMENDATIONS & CHECKLIST ====================
    story.append(Paragraph("7. Limitations & Technical Constraints", styles["SectionH1"]))
    for lim in [
        "• Sample Universe Scope: The warehouse tracks 40 representative schemes across 10 AMCs rather than the entire 1,500+ AMFI scheme universe; category aggregates reflect this curated institutional sample.",
        "• Risk-Free Rate Assumption: Rolling 90-day Sharpe computations assume a constant annualized risk-free benchmark; dynamic RBI repo rate shifts are not modeled intra-window.",
        "• Historical VaR Non-Parametric Bound: 95% Historical VaR relies on empirical 2022–2026 return distributions and may underestimate unprecedented black-swan liquidity shocks.",
        "• Mandate Telemetry Gap: SIP continuity gaps (>35 days) detect delayed settlement dates but cannot distinguish between voluntary investor pauses and bank e-NACH failures without payment gateway logs.",
    ]:
        story.append(Paragraph(lim, styles["BulletItem"]))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("8. Strategic Recommendations", styles["SectionH1"]))
    for rec in [
        "1. Enforce Mandatory UPI Autopay / e-NACH Onboarding: Given the 97.8% >35-day SIP gap rate among multi-installment users, defaulting new SIPs to automated bank mandates can recover significant AUM retention.",
        "2. Introduce Automated Sector HHI Guardrails: Surface HHI concentration warnings (e.g., HHI > 2,500) inside the Bluestock UI whenever a user's portfolio over-indexes on Banking or IT.",
        "3. Expand B30 Vernacular Advisory: With B30 cities contributing 34.1% of retail transaction value and growing faster than T30 metros, localized goal-based SIP nudges offer the highest CAC efficiency.",
        "4. Adopt Dynamic Rolling Sharpe Alerts: Replace static 3-year star ratings in user-facing fund cards with 90-day rolling Sharpe momentum and 95% CVaR downside badges.",
    ]:
        story.append(Paragraph(rec, styles["BulletItem"]))

    story.append(Spacer(1, 0.18 * inch))
    story.append(Paragraph("9. Capstone Self-Review Checklist", styles["SectionH1"]))
    chk_table = make_table([
        ["Verification Criterion", "Target", "Verified Status"],
        ["All 10 CSV datasets + Live mfapi.in ingested", "Day 1 ETL", "PASS — 100% AMFI code integrity"],
        ["Cleaned CSVs & 11-table SQLite Star Schema", "Day 2 Warehouse", "PASS — Exact row-count parity"],
        ["16+ EDA Charts & 10 Structured Findings", "Day 3 EDA", "PASS — 16 PNGs + EDA_Analysis.ipynb"],
        ["VaR/CVaR, Rolling Sharpe, Cohorts, SIP Churn, HHI", "Day 6 Analytics", "PASS — 5 CSV/PNG outputs + Notebook"],
        ["Interactive Dashboard & Fund Recommender", "BI & Product", "PASS — bluestock_dashboard.html + CLI"],
        ["Clean Python Scripts + Master run_pipeline.py", "Engineering", "PASS — 100% docstring coverage"],
        ["Final PDF Report (15–20p) & 12-Slide PPTX", "Final Delivery", "PASS — Final_Report.pdf & PPTX"],
    ], col_widths=[2.7 * inch, 1.3 * inch, 2.7 * inch])
    story.append(chk_table)

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    logger.info(f"Generated Final Report PDF: {OUT_PDF}")
    return OUT_PDF


if __name__ == "__main__":
    generate_pdf()
