"""
Bonus B1: Weekday 8 PM Scheduled ETL Automation
Bluestock Fintech Capstone Project

Generates:
1. scripts/bluestock_etl.cron — Linux/macOS cron entry (0 20 * * 1-5)
2. scripts/register_windows_task.ps1 — Windows Task Scheduler registration script (Mon-Fri 20:00)
3. Supports --run-now to execute live_nav_fetch.py + incremental pipeline immediately.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent


def generate_schedule_configs() -> None:
    """Writes cron and Windows Task Scheduler definitions for weekday 8:00 PM ETL runs."""
    py_exec = sys.executable
    cron_line = (
        "# Bluestock Mutual Fund ETL: Auto-fetch live NAVs from mfapi.in every weekday at 8:00 PM\n"
        f"0 20 * * 1-5 cd \"{BASE_DIR}\" && \"{py_exec}\" live_nav_fetch.py && \"{py_exec}\" run_pipeline.py --skip-live-api >> reports/cron_etl.log 2>&1\n"
    )
    cron_path = SCRIPTS_DIR / "bluestock_etl.cron"
    cron_path.write_text(cron_line, encoding="utf-8")

    ps1_script = (
        "# Register Windows Scheduled Task for Weekday 8:00 PM NAV Fetch & ETL\n"
        f"$Action = New-ScheduledTaskAction -Execute \"{py_exec}\" -Argument \"run_pipeline.py\" -WorkingDirectory \"{BASE_DIR}\"\n"
        "$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 8:00PM\n"
        "Register-ScheduledTask -TaskName \"Bluestock_MF_Weekday_ETL\" -Action $Action -Trigger $Trigger -Force\n"
        "Write-Host \"Registered Bluestock_MF_Weekday_ETL for Mon-Fri at 8:00 PM\"\n"
    )
    ps1_path = SCRIPTS_DIR / "register_windows_task.ps1"
    ps1_path.write_text(ps1_script, encoding="utf-8")
    logger.info(f"Generated cron config ({cron_path}) and Windows Task script ({ps1_path}).")


def main() -> None:
    """Generates schedule configs and optionally runs the ETL job immediately."""
    parser = argparse.ArgumentParser(description="Bluestock Weekday 8 PM ETL Scheduler")
    parser.add_argument("--run-now", action="store_true", help="Execute live NAV fetch immediately")
    args = parser.parse_args()

    generate_schedule_configs()
    if args.run_now:
        logger.info("Executing live_nav_fetch.py...")
        subprocess.run([sys.executable, str(BASE_DIR / "live_nav_fetch.py")], check=True)


if __name__ == "__main__":
    main()
