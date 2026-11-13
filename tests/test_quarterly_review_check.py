"""
Regression tests for dashboard/backend/app/quarterly_review_check.py --
written for issue #51: this file used to hardcode the literal account label
"Account A (232)" (duplicating services._ACCOUNT_A_NAME -- see services.py's
own definition at module scope) and a literal doc filename
"quarterly_portfolio_direction_us_2026-Q3.md" (not derived from the current
quarter at all). Both drift silently: a services.py account-label rename
would make _current_margin_utilization() match nothing forever (drift-based
review-due detection permanently disabled, zero error anywhere), and any
quarter after 2026-Q3 would point the flagged Action Tracker item at a
filename that no longer exists.

This file confirms:
  1. _current_margin_utilization() matches services._ACCOUNT_A_NAME itself,
     not a separate hardcoded copy of it -- proven by reassigning
     services._ACCOUNT_A_NAME to a different label and checking the match
     still succeeds against a get_account_status() row carrying that label.
  2. check_and_flag_if_due()'s created Action Tracker item cites the doc
     filename for the REAL current quarter (via date.today()), not a frozen
     2026-Q3 literal -- proven by patching date.today() (quarterly_review_
     check.py's own `date` import) to a date in a different quarter/year and
     checking the created item's description names that quarter's filename.

Uses an ISOLATED temp SQLite file for ledger/cache state (same pattern as
tests/test_ledger_sync_all.py and tests/test_account_state.py) -- never the
real production DB_PATH.

No pytest dependency -- run directly: python3 tests/test_quarterly_review_check.py
"""
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "dashboard" / "backend"
sys.path.insert(0, str(_BACKEND))

from app import cache, ledger, services, quarterly_review_check as qrc  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def _fresh_db():
    tmp_dir = tempfile.mkdtemp(prefix="theta_lab_test_quarterly_review_check_")
    return tmp_dir, os.path.join(tmp_dir, "test_dashboard_actions.db")


def _cleanup_db(tmp_dir, tmp_db_path):
    try:
        os.remove(tmp_db_path)
    except OSError:
        pass
    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass


def _all_rows():
    conn = ledger._conn()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM action_items").fetchall()]
    finally:
        conn.close()


class _FixedDate(date):
    """A date subclass whose today() always returns a fixed value --
    quarterly_review_check.py does `from datetime import datetime, date` at
    module scope and calls date.today() directly, so patching
    qrc.date = _FixedDate (with a fixed .today()) is sufficient; there is no
    reload involved."""
    _fixed = date(2026, 11, 13)

    @classmethod
    def today(cls):
        return cls._fixed


# ---------------------------------------------------------------------------
# Scenario 1: _current_margin_utilization() matches services._ACCOUNT_A_NAME
# itself, not a separate hardcoded copy -- proven by renaming the constant.
# ---------------------------------------------------------------------------
print("_current_margin_utilization() -- matches services._ACCOUNT_A_NAME, not a hardcoded copy")

_orig_account_a_name = services._ACCOUNT_A_NAME
_orig_get_account_status = services.get_account_status
try:
    services._ACCOUNT_A_NAME = "Account A (RENAMED-999)"
    services.get_account_status = lambda: [
        {"account": "Account A (RENAMED-999)", "utilization": 42.5},
        {"account": "Account B (111)", "utilization": 10.0},
    ]
    util = qrc._current_margin_utilization()
    check("matches the renamed label via services._ACCOUNT_A_NAME, returns its utilization",
          util == 42.5, f"got {util}")

    services.get_account_status = lambda: [
        {"account": "Account A (232)", "utilization": 99.9},  # old literal, no longer the real label
        {"account": "Account B (111)", "utilization": 10.0},
    ]
    util2 = qrc._current_margin_utilization()
    check("does NOT fall back to matching the old hardcoded literal once the label has moved on",
          util2 is None, f"got {util2}")
finally:
    services._ACCOUNT_A_NAME = _orig_account_a_name
    services.get_account_status = _orig_get_account_status


# ---------------------------------------------------------------------------
# Scenario 2: _current_quarter_doc_filename() derives from the real current
# date, for several different quarters/years -- not a frozen literal.
# ---------------------------------------------------------------------------
print("\n_current_quarter_doc_filename() -- derived from the current date")

cases = [
    (date(2026, 11, 13), "us", "quarterly_portfolio_direction_us_2026-Q4.md"),  # Nov -> Q4
    (date(2027, 1, 5), "us", "quarterly_portfolio_direction_us_2027-Q1.md"),    # Jan -> Q1, new year
    (date(2026, 8, 1), "india", "quarterly_portfolio_direction_india_2026-Q3.md"),  # Aug -> Q3
    (date(2026, 4, 30), "us", "quarterly_portfolio_direction_us_2026-Q2.md"),   # Apr -> Q2
]
_orig_date = qrc.date
try:
    for fixed_today, market, expected in cases:
        class _D(date):
            _fixed = fixed_today

            @classmethod
            def today(cls):
                return cls._fixed

        qrc.date = _D
        got = qrc._current_quarter_doc_filename(market)
        check(f"{fixed_today.isoformat()} market={market!r} -> {expected}",
              got == expected, f"got {got}")
finally:
    qrc.date = _orig_date


# ---------------------------------------------------------------------------
# Scenario 3: check_and_flag_if_due()'s created item cites the CURRENT
# quarter's filename end-to-end (not 2026-Q3 frozen), when the stale-days
# trigger fires.
# ---------------------------------------------------------------------------
print("\ncheck_and_flag_if_due() -- created item cites the real current-quarter filename")

tmp_dir, tmp_db = _fresh_db()
_orig_ledger_db_path = ledger.DB_PATH
_orig_cache_db_path = cache.DB_PATH  # cache.py does `from .ledger import DB_PATH` -- its own
                                      # bound name, separate from ledger.DB_PATH (same gotcha
                                      # test_account_state.py documents for account_state.py)
ledger.DB_PATH = tmp_db
cache.DB_PATH = tmp_db
_orig_days_stale = qrc._days_stale
_orig_margin_util = qrc._current_margin_utilization
_orig_qrc_date = qrc.date
try:
    qrc.date = _FixedDate  # fixes "today" to 2026-11-13 -> Q4
    qrc._days_stale = lambda market: 10  # over STALE_DAYS_THRESHOLD (7) -- forces the stale-based trigger
    qrc._current_margin_utilization = lambda: None  # keep the drift branch out of play

    qrc.check_and_flag_if_due()

    rows = _all_rows()
    check("check_and_flag_if_due() creates exactly one Action Tracker item",
          len(rows) == 1, f"got {len(rows)}: {rows}")
    description = rows[0]["description"] if rows else ""
    check("created item's description cites the real CURRENT quarter's filename (2026-Q4, not 2026-Q3)",
          "quarterly_portfolio_direction_us_2026-Q4.md" in description,
          f"got description={description!r}")
    check("created item's description does NOT cite the stale hardcoded 2026-Q3 literal",
          "2026-Q3" not in description, f"got description={description!r}")

    # Re-running with the same (still-stale) inputs must not duplicate the
    # item -- create_manual_item is idempotent on (market, title).
    qrc.check_and_flag_if_due()
    rows2 = _all_rows()
    check("re-running with the same stale inputs does not duplicate the item",
          len(rows2) == 1, f"got {len(rows2)}: {rows2}")
finally:
    qrc._days_stale = _orig_days_stale
    qrc._current_margin_utilization = _orig_margin_util
    qrc.date = _orig_qrc_date
    ledger.DB_PATH = _orig_ledger_db_path
    cache.DB_PATH = _orig_cache_db_path
    _cleanup_db(tmp_dir, tmp_db)


print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
