"""
Generic, dependency-light helpers split out of report_utils.py (Bolt b19,
mcp/reports/report_utils.py split for the Code Quality & Modularity Gate's
1000-line file cap). report_utils.py re-exports everything here so every
existing `from report_utils import X` call site keeps working unchanged.

Nothing in this file depends on report_utils.py itself, yfinance, or any of
the other new sibling submodules -- it's the leaf layer every other piece
(pricing, US/India position loading, KPIs) builds on: filesystem/snapshot
helpers, CSV field parsing, calendar/date math, display formatting, and the
email/HTML report-output helpers.
"""
import calendar
import csv
import math
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from routines.email_report import send_email

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
STATEMENTS_DIR = DATA_DIR / "statements"
LOGS_DIR = PROJECT_ROOT / "logs"
SNAPSHOT_FILE = DATA_DIR / "portfolio_snapshot.yaml"
TO_EMAIL = "ravjdpr@gmail.com"
FROM_EMAIL = "onboarding@resend.dev"

_ACCOUNT_FILES = {
    "A": "Individual_XXX232_Transactions_*.csv",
    "B": "Contributory_XXX275_Transactions_*.csv",
    "C": "Designated_Bene_Individual_XXX634_Transactions_*.csv",  # fixed: actual filename prefix
}

# Files to NEVER load for premium calculations.
# The Empower consolidated export mixes 14+ accounts (Robinhood IRAs, 401k mutual funds,
# Traditional/Roth IRAs) in a different CSV format (Date,Account,Description,Category,Tags,Amount).
# Parsing it as Schwab transactions produces garbage premium data.
_EXCLUDED_FILE_STEMS = {
    "2026-01-01 thru 2026-04-25 transactions",  # Empower all-account export
}


def ensure_logs_dir() -> Path:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR


def load_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_FILE.exists():
        return {}
    with SNAPSHOT_FILE.open() as f:
        return yaml.safe_load(f) or {}


def latest_file(pattern: str) -> Path | None:
    matches = sorted(STATEMENTS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def load_account_transactions() -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for account, pattern in _ACCOUNT_FILES.items():
        path = latest_file(pattern)
        if not path:
            result[account] = []
            continue
        with path.open(newline="", encoding="utf-8-sig") as f:
            result[account] = list(csv.DictReader(f))
    return result


def parse_amount(raw: Any) -> float:
    text = str(raw or "").replace("$", "").replace(",", "").strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def parse_qty(raw: Any) -> int:
    text = str(raw or "0").replace(",", "").replace('"', '').strip()
    try:
        return int(float(text))
    except ValueError:
        return 0


def parse_txn_date(raw: str) -> date | None:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(raw).strip(), fmt).date()
        except Exception:
            continue
    return None


def month_window(target: date) -> tuple[date, date]:
    first = target.replace(day=1)
    last = target.replace(day=calendar.monthrange(target.year, target.month)[1])
    return first, last


def previous_month(target: date) -> date:
    prev = target.replace(day=1) - timedelta(days=1)
    return prev.replace(day=1)


def month_name(target: date) -> str:
    return target.strftime("%B %Y")


def month_days(target: date) -> int:
    return calendar.monthrange(target.year, target.month)[1]


def project_value(current_value: float, as_of: date) -> float:
    elapsed = max(1, as_of.day)
    return current_value / elapsed * month_days(as_of)


def fmt_money(value: Any) -> str:
    try:
        num = float(value)
    except Exception:
        return "—"
    return f"${num:,.0f}"


def fmt_inr(value: Any) -> str:
    try:
        num = float(value)
    except Exception:
        return "—"
    return f"₹{num:,.0f}"


def safe_div(n: float, d: float) -> float:
    return n / d if d else 0.0


def compute_rsi(prices, period: int = 14) -> float | None:
    try:
        delta = prices.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, math.nan)
        value = (100 - (100 / (1 + rs))).iloc[-1]
        return round(float(value), 1) if value == value else None
    except Exception:
        return None


def save_html(prefix: str, html: str, report_day: date | None = None) -> Path:
    ensure_logs_dir()
    report_day = report_day or date.today()
    path = LOGS_DIR / f"{prefix}_{report_day.isoformat()}.html"
    path.write_text(html, encoding="utf-8")
    return path


def maybe_send(subject: str, html: str) -> dict[str, Any]:
    api_key = os.getenv("RESEND_API_KEY", "")
    if not api_key:
        return {"success": False, "error": "RESEND_API_KEY not set"}
    return send_email(
        to_email=TO_EMAIL,
        subject=subject,
        html_body=html,
        from_email=FROM_EMAIL,
        api_key=api_key,
    )
