"""
Bonus B5: Automated Weekly HTML Email Performance Report Generator
Bluestock Fintech Capstone Project

Generates a responsive HTML weekly performance summary email from fund_scorecard.csv
and var_cvar_report.csv -> reports/weekly_performance_email.html.
Supports optional SMTP dispatch via --send using environment variables:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_TO
"""

import argparse
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
OUT_HTML = REPORTS_DIR / "weekly_performance_email.html"


def build_weekly_email_html() -> str:
    """Builds the formatted weekly performance summary HTML body."""
    sc_path = BASE_DIR / "fund_scorecard.csv"
    var_path = BASE_DIR / "var_cvar_report.csv"

    df_sc = pd.read_csv(sc_path).head(5) if sc_path.exists() else pd.DataFrame()
    df_var = pd.read_csv(var_path).head(3) if var_path.exists() else pd.DataFrame()

    top_rows = ""
    for _, r in df_sc.iterrows():
        top_rows += (
            f"<tr><td>#{int(r['overall_rank'])}</td><td>{r['scheme_name']}</td>"
            f"<td>{r['cagr_3yr_pct']:.2f}%</td><td>{r['sharpe_ratio']:.2f}</td>"
            f"<td><b>{r['scorecard_0_100']:.1f}</b></td></tr>"
        )

    risk_rows = ""
    for _, r in df_var.iterrows():
        risk_rows += (
            f"<tr><td>{r['scheme_name']}</td><td>{r['sub_category']}</td>"
            f"<td style='color:#dc2626;'>{r['var_95_daily_pct']:.2f}%</td>"
            f"<td style='color:#dc2626;'>{r['cvar_95_daily_pct']:.2f}%</td></tr>"
        )

    html = f"""<!DOCTYPE html>
<html>
<body style="font-family:Segoe UI,Arial,sans-serif;background:#f8fafc;padding:24px;color:#0f172a;">
  <div style="max-width:680px;margin:0 auto;background:#ffffff;border:1px solid #cbd5e1;border-radius:10px;overflow:hidden;">
    <div style="background:#0f172a;color:#ffffff;padding:20px 24px;">
      <h2 style="margin:0;color:#38bdf8;">Bluestock Fintech — Weekly Mutual Fund Summary</h2>
      <p style="margin:4px 0 0;font-size:13px;color:#94a3b8;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    <div style="padding:20px 24px;">
      <h3 style="color:#0369a1;margin-top:0;">Top 5 Funds by Composite Scorecard</h3>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead><tr style="background:#f1f5f9;text-align:left;">
          <th style="padding:8px;">Rank</th><th style="padding:8px;">Scheme</th>
          <th style="padding:8px;">3Y CAGR</th><th style="padding:8px;">Sharpe</th><th style="padding:8px;">Score</th>
        </tr></thead>
        <tbody>{top_rows}</tbody>
      </table>

      <h3 style="color:#0369a1;margin-top:22px;">Highest Tail-Risk Alerts (95% Daily VaR / CVaR)</h3>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead><tr style="background:#f1f5f9;text-align:left;">
          <th style="padding:8px;">Scheme</th><th style="padding:8px;">Category</th>
          <th style="padding:8px;">VaR 95%</th><th style="padding:8px;">CVaR 95%</th>
        </tr></thead>
        <tbody>{risk_rows}</tbody>
      </table>
      <p style="font-size:12px;color:#64748b;margin-top:20px;">
        Automated weekly digest from Bluestock Mutual Fund Analytics Platform (v1.0).
      </p>
    </div>
  </div>
</body>
</html>"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    logger.info(f"Generated weekly HTML email report: {OUT_HTML}")
    return html


def send_email(html_body: str) -> None:
    """Dispatches the HTML email via SMTP using environment configuration."""
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    recipient = os.environ.get("EMAIL_TO")

    if not all([host, user, password, recipient]):
        raise EnvironmentError("Missing SMTP_HOST, SMTP_USER, SMTP_PASS, or EMAIL_TO env vars.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Bluestock Fintech — Weekly Mutual Fund Performance Summary"
    msg["From"] = user
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [recipient], msg.as_string())
    logger.info(f"Sent weekly email report to {recipient}")


def main() -> None:
    """Generates the weekly HTML report and optionally sends via SMTP."""
    parser = argparse.ArgumentParser(description="Bluestock Weekly HTML Email Report Generator")
    parser.add_argument("--send", action="store_true", help="Send via SMTP using env vars")
    args = parser.parse_args()

    html = build_weekly_email_html()
    if args.send:
        send_email(html)


if __name__ == "__main__":
    main()
