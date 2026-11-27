"""
Capstone 12-Slide PowerPoint Presentation Generator
Bluestock Fintech Mutual Fund Analytics Platform

Generates Bluestock_MF_Presentation.pptx with 12 executive slides:
1. Title
2. Problem & Objective
3. Data Sources
4. Architecture & ETL Design
5. EDA Highlights (1/2)
6. EDA Highlights (2/2)
7. Performance Metrics (1/2)
8. Performance Metrics (2/2)
9. Dashboard Screenshots (1/2)
10. Dashboard Screenshots (2/2)
11. Key Findings & Recommendations
12. Thank You
"""

import logging
from pathlib import Path
from typing import List

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = BASE_DIR / "reports" / "figures"
OUT_PPTX = BASE_DIR / "Bluestock_MF_Presentation.pptx"

# Brand Palette
NAVY = RGBColor(15, 23, 42)       # #0f172a
SLATE = RGBColor(30, 41, 59)      # #1e293b
SKY = RGBColor(56, 189, 248)      # #38bdf8
BLUE = RGBColor(3, 105, 161)      # #0369a1
EMERALD = RGBColor(16, 185, 129)  # #10b981
DARK_TEXT = RGBColor(30, 41, 59)
MUTED = RGBColor(100, 116, 139)
WHITE = RGBColor(255, 255, 255)
LIGHT_BG = RGBColor(248, 250, 252)


def set_slide_bg(slide, color: RGBColor):
    """Sets solid background color for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, title: str, subtitle: str = ""):
    """Adds a standardized corporate top banner and title to a content slide."""
    set_slide_bg(slide, LIGHT_BG)
    banner = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(1.05))
    banner.fill.solid()
    banner.fill.fore_color.rgb = NAVY
    banner.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.18), Inches(11.5), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = WHITE

    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(12)
        p2.font.color.rgb = SKY


def add_footer(slide, page_num: int):
    """Adds a consistent footer with slide number."""
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(7.05), Inches(12.1), Inches(0.35))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = f"Bluestock Fintech Mutual Fund Analytics Capstone  |  v1.0  |  Slide {page_num} of 12"
    p.font.size = Pt(10)
    p.font.color.rgb = MUTED
    p.alignment = PP_ALIGN.RIGHT


def add_bullets(slide, left: float, top: float, width: float, height: float, items: List[str], font_size: int = 15):
    """Adds formatted bullet points to a slide."""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = DARK_TEXT
        p.space_after = Pt(10)


def add_image_safe(slide, filename: str, left: float, top: float, width: float, height: float):
    """Inserts an image from reports/figures/ or root if it exists."""
    p = FIG_DIR / filename
    if not p.exists():
        p = BASE_DIR / filename
    if p.exists():
        slide.shapes.add_picture(str(p), Inches(left), Inches(top), width=Inches(width), height=Inches(height))


def generate_presentation() -> Path:
    """Builds and saves Bluestock_MF_Presentation.pptx (12 slides)."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --- SLIDE 1: TITLE ---
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, NAVY)
    accent_bar = s1.shapes.add_shape(1, Inches(0.8), Inches(1.8), Inches(0.12), Inches(3.8))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = SKY
    accent_bar.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "BLUESTOCK FINTECH  |  CAPSTONE PROJECT 2026"
    p0.font.size = Pt(15)
    p0.font.bold = True
    p0.font.color.rgb = SKY
    p0.space_after = Pt(14)

    p1 = tf.add_paragraph()
    p1.text = "Mutual Fund Analytics Platform"
    p1.font.size = Pt(42)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = "End-to-End ETL Pipeline, Star Schema Warehouse, Risk Modeling & BI Dashboard"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(32)

    p3 = tf.add_paragraph()
    p3.text = "Team: Sathwik Ryapaka (SR)  •  Abhiram (AB)  •  Ashmeet Kaur (AK)"
    p3.font.size = Pt(15)
    p3.font.color.rgb = EMERALD
    p3.space_after = Pt(6)

    p4 = tf.add_paragraph()
    p4.text = "GitHub: https://github.com/SathwikRyapaka/Bluestock-Capstone-.git  |  Tag: v1.0"
    p4.font.size = Pt(13)
    p4.font.color.rgb = RGBColor(148, 163, 184)

    # --- SLIDE 2: PROBLEM & OBJECTIVE ---
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Problem Statement & Project Objectives", "Bridging the Retail Mutual Fund Analytics Gap in India")
    add_bullets(s2, 0.7, 1.4, 5.7, 5.2, [
        "Industry Challenges:",
        "• Fragmented AMFI NAV feeds, AUM disclosures, and transaction logs.",
        "• Retail investors rely on static 3Y returns, ignoring tail risk (VaR/CVaR).",
        "• High SIP installment drop-off / manual payment friction goes undetected.",
        "• Hidden sector concentration in popular equity schemes (e.g., >45% IT).",
    ], font_size=15)
    add_bullets(s2, 6.8, 1.4, 5.8, 5.2, [
        "Core Project Objectives:",
        "• Automate batch + live API (mfapi.in) ETL into a normalized Star Schema.",
        "• Perform 16-chart EDA across NAV, AUM, SIPs, demographics, and holdings.",
        "• Quantify 95% VaR/CVaR, 90-day Rolling Sharpe, Cohorts, and HHI.",
        "• Deliver an interactive BI Dashboard and Sharpe-based Fund Recommender.",
    ], font_size=15)
    add_footer(s2, 2)

    # --- SLIDE 3: DATA SOURCES ---
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Data Sources & Ingestion Inventory", "10 Historical CSV Datasets + Live mfapi.in REST API Feeds")
    add_bullets(s3, 0.7, 1.35, 11.9, 5.4, [
        "• Fund Master & Performance (40 Schemes, 10 AMCs): Expense ratios, exit loads, Sharpe, Sortino, Alpha, Beta.",
        "• Daily NAV History (46,000 Rows, 2022–2026): Holiday-adjusted time series + Live API fetch for 6 benchmark schemes.",
        "• Macro Industry Flows: AMC AUM (90 rows), Monthly SIP Inflows (48 months), Category Net Inflows (144 rows), Folios (21 periods).",
        "• Investor Transactions (32,778 Rows): SIP/Lumpsum/Redemption, T30 vs B30 city tier, state, age, gender, KYC status.",
        "• Portfolio Holdings & Benchmarks (322 Holdings + 8,050 Index Rows): Stock-level weights, sectors, Nifty 50 / Midcap / Smallcap.",
        "• Data Quality Audit: 100% AMFI scheme code referential integrity verified between fund_master and nav_history.",
    ], font_size=15)
    add_footer(s3, 3)

    # --- SLIDE 4: ARCHITECTURE ---
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "System Architecture & Star Schema Design", "Modular Python ETL Pipeline Backed by 11-Table SQLite Warehouse")
    add_bullets(s4, 0.7, 1.35, 5.8, 5.3, [
        "Master Pipeline (run_pipeline.py):",
        "1. data_ingestion.py — Profiling & AMFI validation",
        "2. live_nav_fetch.py — mfapi.in JSON ingestion",
        "3. data_cleaning.py — Holiday ffill, KYC & enum checks",
        "4. load_to_sqlite.py — SQLAlchemy Star Schema load",
        "5. generate_eda_charts.py — 16 EDA figures",
        "6. generate_advanced_analytics.py — Risk & Cohorts",
        "7. dashboard/generate_dashboard.py — HTML5 BI",
    ], font_size=14)
    add_bullets(s4, 6.8, 1.35, 5.8, 5.3, [
        "SQLite Star Schema (bluestock_mf.db):",
        "• Dimensions: dim_fund (40), dim_date (2,557 days w/ Indian FY)",
        "• Core Facts: fact_nav (46,000), fact_transactions (32,778), fact_performance (40), fact_aum (90)",
        "• Supporting Facts: fact_monthly_sip, fact_category_inflows, fact_industry_folios, fact_portfolio_holdings, fact_benchmark_indices",
        "• Performance: B-tree indexes on amfi_code, nav_date, state, sector; 100% CSV-to-DB row parity.",
    ], font_size=14)
    add_footer(s4, 4)

    # --- SLIDE 5: EDA HIGHLIGHTS 1/2 ---
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "EDA Highlights (1/2): NAV Regimes & AMC Dominance", "2023 Bull Rally vs 2024 Corrections & SBI MF Market Leadership")
    add_image_safe(s5, "01_nav_trend_all_schemes.png", 0.5, 1.35, 6.0, 3.6)
    add_image_safe(s5, "03_aum_growth_by_amc.png", 6.8, 1.35, 6.0, 3.6)
    add_bullets(s5, 0.6, 5.15, 12.1, 1.7, [
        "• Small & Mid Cap schemes outperformed Large Cap by 1.8x in the 2023 rally but saw 2.3x sharper 2024 pullbacks.",
        "• SBI Mutual Fund dominates at Rs. 12.50 Lakh Crore AUM (19.92% share), leading ICICI Pru (17.12%) and HDFC (14.82%).",
    ], font_size=14)
    add_footer(s5, 5)

    # --- SLIDE 6: EDA HIGHLIGHTS 2/2 ---
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "EDA Highlights (2/2): SIP Momentum & Sector Exposure", "Record Rs. 31,002 Cr Monthly SIPs & Banking/IT Portfolio Concentration")
    add_image_safe(s6, "05_monthly_sip_inflows_trend.png", 0.5, 1.35, 6.2, 3.6)
    add_image_safe(s6, "15_sector_allocation_donut.png", 7.1, 1.35, 5.5, 3.6)
    add_bullets(s6, 0.6, 5.15, 12.1, 1.7, [
        "• Monthly SIP inflows surged +169.2% from Rs. 11,517 Cr (Jan 2022) to an all-time high of Rs. 31,002 Cr (Dec 2025).",
        "• Equity portfolios allocate 23.2% to Banking & 14.2% to IT; Folios nearly doubled (13.26 Cr -> 26.12 Cr); Millennials (26–35) = 35.4%.",
    ], font_size=14)
    add_footer(s6, 6)

    # --- SLIDE 7: PERFORMANCE METRICS 1/2 ---
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Performance & Risk Metrics (1/2): VaR & Rolling Sharpe", "Quantifying Tail Loss Severity and Dynamic Risk-Adjusted Alpha")
    add_image_safe(s7, "rolling_sharpe_chart.png", 0.5, 1.35, 6.3, 3.7)
    add_bullets(s7, 7.1, 1.4, 5.6, 5.1, [
        "Historical VaR (95%) & CVaR:",
        "• Small Cap carries highest 1-day tail risk (SBI Small Cap: VaR -2.69%, CVaR -3.24%, Vol 25.1%).",
        "• Liquid schemes preserve capital (VaR -0.02%, CVaR -0.03%).",
        "Rolling 90-Day Sharpe Dynamics:",
        "• Evaluated across 1,061 rolling windows for 5 flagship Large Cap funds.",
        "• Axis Bluechip swung from -3.64 (2022) to +6.77 (2023), proving static 3Y Sharpe hides regime risk.",
    ], font_size=14)
    add_footer(s7, 7)

    # --- SLIDE 8: PERFORMANCE METRICS 2/2 ---
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Performance & Risk Metrics (2/2): Churn, HHI & Recommender", "Behavioral SIP Gaps, Sector Concentration & Automated Fund Selection")
    add_image_safe(s8, "sector_hhi_chart.png", 0.5, 1.35, 6.2, 3.7)
    add_bullets(s8, 7.0, 1.4, 5.7, 5.2, [
        "• SIP Continuity Churn: 97.8% of 6+ SIP investors (1,332 of 1,362) had >35-day gaps, signaling manual payment friction.",
        "• Investor Cohorts: 2024 cohort invested Rs. 349.11 Cr; 2025 cohort raised avg SIP size to Rs. 13,505.",
        "• Sector HHI: Axis Bluechip highest at 2,967.69 (48.7% IT); Kotak Multicap most diversified (1,120.45).",
        "• Fund Recommender (recommender.py): Ranks top 3 funds by Sharpe per risk tier (Low: ICICI Pru Liquid 7.68; Mod: HDFC Top 100 1.06; High: Kotak Emerging 0.96).",
    ], font_size=14)
    add_footer(s8, 8)

    # --- SLIDE 9: DASHBOARD SCREENSHOT 1/2 ---
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Interactive BI Dashboard (1/2): Executive Overview", "Self-Contained HTML5/Plotly Dashboard Powered by bluestock_mf.db")
    add_image_safe(s9, "dashboard_overview.png", 0.8, 1.25, 11.7, 5.65)
    add_footer(s9, 9)

    # --- SLIDE 10: DASHBOARD SCREENSHOT 2/2 ---
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Interactive BI Dashboard (2/2): Risk & Recommender", "Tail-Risk VaR/CVaR Comparison, HHI Concentration & Risk-Return Frontier")
    add_image_safe(s10, "dashboard_analytics.png", 0.8, 1.25, 11.7, 5.65)
    add_footer(s10, 10)

    # --- SLIDE 11: KEY FINDINGS & RECOMMENDATIONS ---
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Key Findings & Strategic Recommendations", "Actionable Product & Distribution Roadmap for Bluestock Fintech")
    add_bullets(s11, 0.7, 1.4, 11.9, 5.3, [
        "1. Mandate UPI Autopay / e-NACH by Default: Eliminating manual SIP friction addresses the 97.8% >35-day installment gap rate.",
        "2. Embed Sector HHI Guardrails in Portfolio UI: Alert investors when fund-level HHI exceeds 2,500 (e.g., >45% single-sector tilt).",
        "3. Target B30 Cities with Vernacular Advisory: B30 already drives 34.1% of tracked retail volume and is expanding faster than T30 metros.",
        "4. Replace Static Star Ratings with Rolling Sharpe & CVaR Badges: Surface 90-day momentum and 95% tail-loss metrics for transparency.",
        "5. Scale Fund Recommender API: Integrate recommender.py into onboarding flows for instant Low/Moderate/High risk matching.",
    ], font_size=15)
    add_footer(s11, 11)

    # --- SLIDE 12: THANK YOU ---
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12, NAVY)
    tb12 = s12.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(3.2))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    q0 = tf12.paragraphs[0]
    q0.text = "Thank You!"
    q0.font.size = Pt(46)
    q0.font.bold = True
    q0.font.color.rgb = WHITE
    q0.alignment = PP_ALIGN.CENTER
    q0.space_after = Pt(16)

    q1 = tf12.add_paragraph()
    q1.text = "Questions & Discussion"
    q1.font.size = Pt(22)
    q1.font.color.rgb = SKY
    q1.alignment = PP_ALIGN.CENTER
    q1.space_after = Pt(28)

    q2 = tf12.add_paragraph()
    q2.text = "GitHub: https://github.com/SathwikRyapaka/Bluestock-Capstone-.git  |  Release: v1.0"
    q2.font.size = Pt(14)
    q2.font.color.rgb = EMERALD
    q2.alignment = PP_ALIGN.CENTER
    q2.space_after = Pt(8)

    q3 = tf12.add_paragraph()
    q3.text = "Sathwik Ryapaka (SR)  •  Abhiram (AB)  •  Ashmeet Kaur (AK)"
    q3.font.size = Pt(14)
    q3.font.color.rgb = RGBColor(148, 163, 184)
    q3.alignment = PP_ALIGN.CENTER

    prs.save(str(OUT_PPTX))
    logger.info(f"Generated 12-slide presentation: {OUT_PPTX} (slides={len(prs.slides)})")
    return OUT_PPTX


if __name__ == "__main__":
    generate_presentation()
