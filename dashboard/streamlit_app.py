"""
Bluestock Fintech — Streamlit Interactive Web App (Bonus B2)
4-Page Mutual Fund Analytics Dashboard with Interactive Slicers on Every Page.

Run with:
    streamlit run dashboard/streamlit_app.py
"""

import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bluestock_mf.db"

st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics",
    page_icon="📈",
    layout="wide",
)


@st.cache_data
def load_warehouse():
    """Loads tables from SQLite warehouse."""
    conn = sqlite3.connect(DB_PATH)
    df_perf = pd.read_sql_query(
        """
        SELECT p.amfi_code, p.scheme_name, p.fund_house, p.category, f.sub_category,
               p.risk_grade, p.sharpe_ratio, p.return_3yr_pct, p.std_dev_ann_pct,
               p.expense_ratio_pct, p.aum_crore, p.alpha
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        """,
        conn,
    )
    df_aum = pd.read_sql_query("SELECT * FROM fact_aum", conn)
    df_aum["year"] = pd.to_datetime(df_aum["date"]).dt.year
    df_sip = pd.read_sql_query("SELECT * FROM fact_monthly_sip ORDER BY month", conn)
    df_tx = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
    df_holdings = pd.read_sql_query("SELECT * FROM fact_portfolio_holdings", conn)
    conn.close()
    return df_perf, df_aum, df_sip, df_tx, df_holdings


def main():
    """Renders the 4-page Streamlit BI application."""
    df_perf, df_aum, df_sip, df_tx, df_holdings = load_warehouse()

    st.sidebar.title("Bluestock MF Analytics")
    page = st.sidebar.radio(
        "Navigate Page",
        [
            "1. Executive & AUM Overview",
            "2. Scheme Performance & Alpha",
            "3. Investor Demographics & Geography",
            "4. Risk Metrics & Fund Recommender",
        ],
    )

    if page.startswith("1."):
        st.title("Executive & AMC AUM Overview")
        years = sorted(df_aum["year"].unique(), reverse=True)
        sel_year = st.sidebar.selectbox("Slicer 1: Calendar Year", years)
        sel_amcs = st.sidebar.multiselect(
            "Slicer 2: Fund Houses (AMC)", sorted(df_aum["fund_house"].unique()),
            default=sorted(df_aum["fund_house"].unique()),
        )
        sub_aum = df_aum[(df_aum["year"] == sel_year) & (df_aum["fund_house"].isin(sel_amcs))]
        latest_dt = sub_aum["date"].max()
        sub_aum = sub_aum[sub_aum["date"] == latest_dt]

        c1, c2, c3 = st.columns(3)
        c1.metric("Selected Industry AUM", f"₹{sub_aum['aum_lakh_crore'].sum():.2f}L Cr")
        c2.metric("Peak Monthly SIP", f"₹{df_sip['sip_inflow_crore'].max():,.0f} Cr")
        c3.metric("Active Schemes", f"{len(df_perf)}")

        col_a, col_b = st.columns(2)
        col_a.plotly_chart(px.bar(sub_aum, x="fund_house", y="aum_lakh_crore", title="AMC AUM (₹ Lakh Cr)"), use_container_width=True)
        col_b.plotly_chart(px.area(df_sip, x="month", y="sip_inflow_crore", title="Monthly SIP Inflows (₹ Cr)"), use_container_width=True)

    elif page.startswith("2."):
        st.title("Scheme Performance & Risk-Return Frontier")
        sel_cats = st.sidebar.multiselect("Slicer 1: Category", df_perf["category"].unique(), default=df_perf["category"].unique())
        sel_risk = st.sidebar.multiselect("Slicer 2: Risk Grade", df_perf["risk_grade"].unique(), default=df_perf["risk_grade"].unique())
        sub = df_perf[df_perf["category"].isin(sel_cats) & df_perf["risk_grade"].isin(sel_risk)]

        st.plotly_chart(
            px.scatter(sub, x="std_dev_ann_pct", y="return_3yr_pct", size="aum_crore", color="sub_category",
                       hover_name="scheme_name", title="Volatility vs 3-Year Return"),
            use_container_width=True,
        )
        st.dataframe(sub.sort_values("sharpe_ratio", ascending=False), use_container_width=True)

    elif page.startswith("3."):
        st.title("Investor Demographics & Geographic Penetration")
        sel_tier = st.sidebar.multiselect("Slicer 1: City Tier", df_tx["city_tier"].unique(), default=df_tx["city_tier"].unique())
        sel_type = st.sidebar.multiselect("Slicer 2: Transaction Type", df_tx["transaction_type"].unique(), default=df_tx["transaction_type"].unique())
        sub_tx = df_tx[df_tx["city_tier"].isin(sel_tier) & df_tx["transaction_type"].isin(sel_type)]

        by_state = sub_tx.groupby("state")["amount_inr"].sum().reset_index()
        by_state["crore"] = by_state["amount_inr"] / 1e7
        st.plotly_chart(px.bar(by_state.sort_values("crore").tail(12), x="crore", y="state", orientation="h", title="Investment by State (₹ Cr)"), use_container_width=True)

    else:
        st.title("Risk Analytics & Fund Recommender")
        risk_choice = st.sidebar.selectbox("Slicer 1: Risk Appetite", ["Low", "Moderate", "High"])
        sub_cats = st.sidebar.multiselect("Slicer 2: Sub-Category", df_perf["sub_category"].unique(), default=df_perf["sub_category"].unique())
        risk_map = {"Low": ["Low"], "Moderate": ["Moderate", "Moderately High"], "High": ["High", "Very High"]}
        recs = df_perf[df_perf["risk_grade"].isin(risk_map[risk_choice]) & df_perf["sub_category"].isin(sub_cats)]
        st.subheader(f"Top Recommended Schemes for {risk_choice} Risk")
        st.dataframe(recs.sort_values("sharpe_ratio", ascending=False).head(5), use_container_width=True)


if __name__ == "__main__":
    main()
