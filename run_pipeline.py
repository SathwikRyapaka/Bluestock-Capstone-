"""
Master Pipeline Execution Script
Bluestock Fintech Capstone Project

Orchestrates the end-to-end Mutual Fund Analytics Platform workflow:
1. Day 1: Batch Data Ingestion & AMFI Integrity Audit (data_ingestion.py)
2. Day 1 (Optional): Live NAV REST API Fetch from mfapi.in (live_nav_fetch.py)
3. Day 2: Data Cleaning & Standardization (data_cleaning.py)
4. Day 2: SQLite Star Schema Loading & Verification (load_to_sqlite.py)
5. Day 3: Exploratory Data Analysis 16-Chart Generation (generate_eda_charts.py)
6. Day 6: Advanced Risk Metrics & Cohort Analytics (generate_advanced_analytics.py)
7. Dashboard: Interactive HTML5 Dashboard & Screenshots (dashboard/generate_dashboard.py)
8. Recommender: Sample Fund Recommendations (recommender.py)

Usage:
    python run_pipeline.py
    python run_pipeline.py --skip-live-api
"""

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def run_step(step_name: str, command: List[str]) -> float:
    """Executes a pipeline stage as a subprocess and returns elapsed seconds."""
    logger.info(f"Starting stage: {step_name}")
    start = time.perf_counter()
    result = subprocess.run(command, cwd=BASE_DIR)
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        raise RuntimeError(f"Stage '{step_name}' failed with exit code {result.returncode}")
    logger.info(f"Completed stage: {step_name} ({elapsed:.2f}s)")
    return elapsed


def main() -> None:
    """Parses CLI flags and executes the full Bluestock analytics pipeline."""
    parser = argparse.ArgumentParser(description="Run Bluestock Mutual Fund Analytics Pipeline")
    parser.add_argument(
        "--skip-live-api",
        action="store_true",
        help="Skip live mfapi.in API calls (useful for offline/sandbox verification)"
    )
    args = parser.parse_args()

    py = sys.executable
    stages: List[Tuple[str, List[str]]] = [
        ("1. Batch Data Ingestion & Quality Audit", [py, "data_ingestion.py"]),
    ]
    if not args.skip_live_api:
        stages.append(("2. Live NAV Fetch (mfapi.in)", [py, "live_nav_fetch.py"]))

    stages.extend([
        ("3. Data Cleaning & Standardization", [py, "data_cleaning.py"]),
        ("4. SQLite Star Schema Warehouse Load", [py, "load_to_sqlite.py"]),
        ("5. EDA Visualization Suite (16 Charts)", [py, "generate_eda_charts.py"]),
        ("6. Advanced Risk & Cohort Analytics", [py, "generate_advanced_analytics.py"]),
        ("7. Interactive BI Dashboard & Previews", [py, "dashboard/generate_dashboard.py"]),
        ("8. Mutual Fund Recommender Check", [py, "recommender.py", "--risk", "Moderate", "--top", "3"]),
    ])

    total_start = time.perf_counter()
    timings = []
    for name, cmd in stages:
        elapsed = run_step(name, cmd)
        timings.append((name, elapsed))

    total_elapsed = time.perf_counter() - total_start
    logger.info("=" * 70)
    logger.info(f"FULL PIPELINE COMPLETED SUCCESSFULLY in {total_elapsed:.2f}s")
    for name, sec in timings:
        logger.info(f"  - {name}: {sec:.2f}s")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
