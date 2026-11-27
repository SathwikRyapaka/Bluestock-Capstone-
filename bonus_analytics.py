"""
Bonus B3 & B4: Monte Carlo 5-Year NAV Simulation & Markowitz Efficient Frontier
Bluestock Fintech Capstone Project

B3: Projects 5-year NAV growth (1,000 Geometric Brownian Motion paths over 1,260 trading days)
    with P5, P25, P50, P75, P95 uncertainty bands -> monte_carlo_5yr.png.
B4: Computes Markowitz Efficient Frontier for 5 selected funds using scipy.optimize.minimize
    (Minimum Variance & Maximum Sharpe portfolios) -> efficient_frontier.png & markowitz_weights.csv.
Also exports Bonus_Analytics.ipynb.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
REPORTS_DIR = BASE_DIR / "reports"
FIG_DIR = REPORTS_DIR / "figures"

TRADING_DAYS = 252
RISK_FREE_RATE = 0.065


def run_monte_carlo_5yr(
    amfi_code: str = "119551", n_sims: int = 1000, horizon_years: int = 5
) -> pd.DataFrame:
    """
    Bonus B3: Runs 1,000 GBM Monte Carlo paths over 5 years (1,260 trading days)
    and plots P5/P25/P50/P75/P95 uncertainty bands.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT n.nav_date, n.nav, f.scheme_name
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        WHERE n.amfi_code = ?
        ORDER BY n.nav_date
        """,
        conn,
        params=(amfi_code,),
    )
    conn.close()

    scheme_name = df["scheme_name"].iloc[0]
    log_ret = np.log(df["nav"] / df["nav"].shift(1)).dropna()
    mu = float(log_ret.mean())
    sigma = float(log_ret.std())
    s0 = float(df["nav"].iloc[-1])

    n_steps = horizon_years * TRADING_DAYS
    rng = np.random.default_rng(42)
    shocks = rng.normal(
        loc=(mu - 0.5 * sigma ** 2),
        scale=sigma,
        size=(n_steps, n_sims),
    )
    paths = np.vstack([np.ones((1, n_sims)) * s0, s0 * np.exp(np.cumsum(shocks, axis=0))])

    days = np.arange(n_steps + 1) / TRADING_DAYS
    p5 = np.percentile(paths, 5, axis=1)
    p25 = np.percentile(paths, 25, axis=1)
    p50 = np.percentile(paths, 50, axis=1)
    p75 = np.percentile(paths, 75, axis=1)
    p95 = np.percentile(paths, 95, axis=1)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(days, paths[:, :35], color="#94a3b8", alpha=0.18, linewidth=0.8)
    ax.fill_between(days, p5, p95, color="#38bdf8", alpha=0.20, label="5th–95th Percentile Band")
    ax.fill_between(days, p25, p75, color="#0284c7", alpha=0.32, label="25th–75th Percentile Band")
    ax.plot(days, p50, color="#0f172a", linewidth=2.5, label=f"Median 5Y Projected NAV: Rs. {p50[-1]:.2f}")
    ax.plot(days, p95, color="#10b981", linestyle="--", linewidth=1.6, label=f"P95 Upside: Rs. {p95[-1]:.2f}")
    ax.plot(days, p5, color="#f43f5e", linestyle="--", linewidth=1.6, label=f"P5 Downside: Rs. {p5[-1]:.2f}")

    ax.set_title(
        f"5-Year Monte Carlo NAV Projection ({n_sims:,} GBM Paths)\n"
        f"{scheme_name} (Starting NAV: Rs. {s0:.2f})",
        fontsize=13, fontweight="bold", pad=10,
    )
    ax.set_xlabel("Projection Horizon (Years)", fontsize=11)
    ax.set_ylabel("Projected NAV (Rs.)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)

    fig.savefig(BASE_DIR / "monte_carlo_5yr.png", dpi=150, bbox_inches="tight")
    fig.savefig(FIG_DIR / "monte_carlo_5yr.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    summary = pd.DataFrame({
        "year": [0, 1, 2, 3, 4, 5],
        "p5_nav": [round(float(p5[y * TRADING_DAYS]), 2) for y in range(6)],
        "p50_median_nav": [round(float(p50[y * TRADING_DAYS]), 2) for y in range(6)],
        "p95_nav": [round(float(p95[y * TRADING_DAYS]), 2) for y in range(6)],
    })
    logger.info(f"Monte Carlo 5Y complete for {scheme_name}: P5={p5[-1]:.2f}, P50={p50[-1]:.2f}, P95={p95[-1]:.2f}")
    return summary


def run_markowitz_frontier() -> pd.DataFrame:
    """
    Bonus B4: Computes Markowitz Efficient Frontier for 5 selected funds
    (Large Cap, Mid Cap, Small Cap, Flexi Cap, Gilt).
    """
    selected_codes = ["119551", "120505", "119598", "120841", "119120"]
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"""
        SELECT n.nav_date, f.scheme_name, n.nav
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        WHERE n.amfi_code IN ({",".join("?" * len(selected_codes))})
        ORDER BY n.nav_date
        """,
        conn,
        params=selected_codes,
    )
    conn.close()

    piv = df.pivot(index="nav_date", columns="scheme_name", values="nav").sort_index()
    ret = piv.pct_change().dropna()
    mean_ret = ret.mean() * TRADING_DAYS
    cov_mat = ret.cov() * TRADING_DAYS
    n_assets = len(mean_ret)

    def port_stats(weights):
        p_ret = float(np.dot(weights, mean_ret))
        p_vol = float(np.sqrt(np.dot(weights.T, np.dot(cov_mat, weights))))
        p_sharpe = (p_ret - RISK_FREE_RATE) / p_vol
        return p_ret, p_vol, p_sharpe

    bounds = tuple((0.0, 1.0) for _ in range(n_assets))
    cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    init_w = np.ones(n_assets) / n_assets

    opt_sharpe = minimize(lambda w: -port_stats(w)[2], init_w, method="SLSQP", bounds=bounds, constraints=cons)
    opt_minvol = minimize(lambda w: port_stats(w)[1], init_w, method="SLSQP", bounds=bounds, constraints=cons)

    # Random portfolios for cloud visualization
    rng = np.random.default_rng(7)
    rand_vols, rand_rets, rand_sharpes = [], [], []
    for _ in range(3000):
        w = rng.random(n_assets)
        w /= w.sum()
        r, v, s = port_stats(w)
        rand_rets.append(r * 100)
        rand_vols.append(v * 100)
        rand_sharpes.append(s)

    ms_ret, ms_vol, ms_sh = port_stats(opt_sharpe.x)
    mv_ret, mv_vol, mv_sh = port_stats(opt_minvol.x)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    sc = ax.scatter(rand_vols, rand_rets, c=rand_sharpes, cmap="viridis", alpha=0.45, s=14)
    plt.colorbar(sc, ax=ax, label="Sharpe Ratio")
    ax.scatter(ms_vol * 100, ms_ret * 100, color="#f43f5e", marker="*", s=320,
               label=f"Max Sharpe Portfolio (Sharpe: {ms_sh:.2f}, Ret: {ms_ret*100:.1f}%, Vol: {ms_vol*100:.1f}%)")
    ax.scatter(mv_vol * 100, mv_ret * 100, color="#38bdf8", marker="D", s=160,
               label=f"Min Variance Portfolio (Sharpe: {mv_sh:.2f}, Ret: {mv_ret*100:.1f}%, Vol: {mv_vol*100:.1f}%)")

    ax.set_title("Markowitz Efficient Frontier — 5-Fund Portfolio Optimization", fontsize=13.5, fontweight="bold", pad=10)
    ax.set_xlabel("Annualized Portfolio Volatility (%)", fontsize=11)
    ax.set_ylabel("Annualized Expected Return (%)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)

    fig.savefig(BASE_DIR / "efficient_frontier.png", dpi=150, bbox_inches="tight")
    fig.savefig(FIG_DIR / "efficient_frontier.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    weights_df = pd.DataFrame({
        "scheme_name": mean_ret.index,
        "max_sharpe_weight_pct": np.round(opt_sharpe.x * 100, 2),
        "min_variance_weight_pct": np.round(opt_minvol.x * 100, 2),
        "ann_return_pct": np.round(mean_ret.values * 100, 2),
    })
    weights_df.to_csv(BASE_DIR / "markowitz_weights.csv", index=False)
    weights_df.to_csv(REPORTS_DIR / "markowitz_weights.csv", index=False)
    logger.info(f"Markowitz Frontier complete: Max Sharpe={ms_sh:.2f}, Min Vol={mv_vol*100:.2f}%")
    return weights_df


def build_bonus_notebook() -> None:
    """Generates Bonus_Analytics.ipynb documenting B1–B5 implementations."""
    import nbformat as nbf

    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        nbf.v4.new_markdown_cell(
            "# Bluestock Fintech — Bonus Challenges (B1–B5)\n\n"
            "- **B1:** Weekday 8 PM Scheduled ETL (`scripts/schedule_etl_cron.py`)\n"
            "- **B2:** 4-Page Interactive Streamlit App (`dashboard/streamlit_app.py`)\n"
            "- **B3:** 5-Year Monte Carlo NAV Simulation (`monte_carlo_5yr.png`)\n"
            "- **B4:** Markowitz Efficient Frontier Portfolio Optimization (`efficient_frontier.png`)\n"
            "- **B5:** Automated Weekly HTML Email Report (`scripts/email_weekly_report.py`)"
        ),
        nbf.v4.new_code_cell(
            "from IPython.display import Image, display\n"
            "from bonus_analytics import run_monte_carlo_5yr, run_markowitz_frontier\n\n"
            "mc_summary = run_monte_carlo_5yr()\n"
            "mc_summary"
        ),
        nbf.v4.new_code_cell("display(Image(filename='monte_carlo_5yr.png'))"),
        nbf.v4.new_code_cell("weights_df = run_markowitz_frontier()\nweights_df"),
        nbf.v4.new_code_cell("display(Image(filename='efficient_frontier.png'))"),
    ]
    nbf.write(nb, str(BASE_DIR / "Bonus_Analytics.ipynb"))
    nbf.write(nb, str(BASE_DIR / "notebooks" / "Bonus_Analytics.ipynb"))
    logger.info("Saved Bonus_Analytics.ipynb.")


def main() -> None:
    """Executes Bonus B3 Monte Carlo, Bonus B4 Markowitz Optimization, and builds Bonus_Analytics.ipynb."""
    run_monte_carlo_5yr()
    run_markowitz_frontier()
    build_bonus_notebook()


if __name__ == "__main__":
    main()
