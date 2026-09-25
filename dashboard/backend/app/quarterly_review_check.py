"""Flags when the Quarterly Portfolio Direction docs are due for a real
review -- never rewrites them (that needs actual judgment from a live
session, the same way the original was written; no background job can do
that). Two real, honest triggers, neither of which requires parsing free-
form prose for numbers (too fragile to trust):

  1. Time-based: 7+ days since the doc's own stated "Refreshed"/"Generated"
     date (same threshold and same date-parsing convention already used
     client-side in us.html/india.html's parseQuarterlyDate).
  2. Drift-based: Account A's real margin utilization has moved by more
     than 15 percentage points since the last time this check ran --
     tracked as a live number snapshot (computed_cache table), not by
     reading the doc's own text.

When either fires, creates ONE real Action Tracker item via
ledger.create_manual_item (idempotent on title -- re-checking never
duplicates it; it only clears when the trader actually reviews the doc
and marks it resolved in the Action Tracker).
"""
import re
from datetime import datetime, date

from . import cache
from . import ledger
from . import services

DRIFT_THRESHOLD_PCT = 15.0
STALE_DAYS_THRESHOLD = 7


def _parse_quarterly_date(text: str):
    m = re.search(r"Refreshed\s+(\d{4}-\d{2}-\d{2})", text)
    if not m:
        m = re.search(r"Generated:?\**\s*(\d{4}-\d{2}-\d{2})", text)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y-%m-%d").date()


def _days_stale(market: str) -> int | None:
    text = services.get_quarterly_direction(market)
    doc_date = _parse_quarterly_date(text)
    if not doc_date:
        return None
    return (date.today() - doc_date).days


def _current_margin_utilization():
    for row in services.get_account_status():
        if row.get("account") == "Account A (232)":
            return row.get("utilization")
    return None


def check_and_flag_if_due():
    stale_days = _days_stale("us")
    current_util = _current_margin_utilization()
    last_util, _ = cache.get_cached("quarterly_review_last_margin_util")
    drifted = (
        current_util is not None and last_util is not None
        and abs(current_util - last_util) >= DRIFT_THRESHOLD_PCT
    )

    if current_util is not None:
        cache.set_cached("quarterly_review_last_margin_util", current_util)

    if stale_days is not None and stale_days >= STALE_DAYS_THRESHOLD:
        reason = f"{stale_days} days since last refresh (threshold {STALE_DAYS_THRESHOLD}d)"
    elif drifted:
        reason = f"Account A margin utilization moved {last_util:.0f}% -> {current_util:.0f}% since last check"
    else:
        return  # nothing to flag

    ledger.create_manual_item(
        "US", "Quarterly Review",
        "Quarterly Portfolio Direction review due",
        f"{reason}. This needs real judgment (market direction call, portfolio-state "
        f"rewrite) from a live session -- not something a background job can do. "
        f"See logs/quarterly_portfolio_direction_us_2026-Q3.md.",
    )
