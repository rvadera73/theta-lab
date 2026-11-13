"""
Regression tests for issue #53: mcp/config.py's PORTFOLIO dict
(total_aum/target_monthly_combined/active_options_aum_estimate) was a
hand-typed snapshot with no recorded as-of date, so nothing could ever tell
a current figure from a stale one. The fix adds an explicit PORTFOLIO['as_of']
date and a shared report_utils.portfolio_staleness_lines() helper (consumed
by weekly_report.py, monthly_objectives_report.py, and india_weekly_report.py
instead of each file re-implementing the same date-math) that emits a
visible warning once that date is more than report_utils.PORTFOLIO_STALENESS_DAYS
(75) days old.

Per `git log -S'total_aum' -- mcp/config.py`, these three figures were
introduced in commit 472c257 (2026-04-30) and have never been edited since --
that is the real as_of date used (not a fabricated "today", which would
overstate freshness). As of this test being written, that date is already
well past the 75-day threshold, so the real (unmocked) PORTFOLIO is a live
positive case for the warning firing -- not just a mocked fixture.

No pytest dependency -- run directly: python3 tests/test_portfolio_staleness.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "reports"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "analysis"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp"))

import report_utils  # noqa: E402
import config  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# config.PORTFOLIO -- as_of field exists and is a real, parseable date
# ---------------------------------------------------------------------------
print("config.PORTFOLIO['as_of']")

check("PORTFOLIO has an 'as_of' key", "as_of" in config.PORTFOLIO, f"got keys {list(config.PORTFOLIO.keys())}")
try:
    from datetime import datetime as _dt
    _parsed = _dt.strptime(config.PORTFOLIO.get("as_of", ""), "%Y-%m-%d").date()
    parse_ok = True
except Exception as exc:  # noqa: BLE001
    parse_ok = False
    _parsed = None
check("PORTFOLIO['as_of'] parses as a real YYYY-MM-DD date", parse_ok, f"got {config.PORTFOLIO.get('as_of')!r}")

# ---------------------------------------------------------------------------
# report_utils.portfolio_staleness_lines() -- core date-math
# ---------------------------------------------------------------------------
print("\nreport_utils.portfolio_staleness_lines()")

_today_str = date.today().isoformat()
_fresh_str = (date.today() - timedelta(days=10)).isoformat()
_old_str = (date.today() - timedelta(days=report_utils.PORTFOLIO_STALENESS_DAYS + 1)).isoformat()
_boundary_str = (date.today() - timedelta(days=report_utils.PORTFOLIO_STALENESS_DAYS)).isoformat()

with mock.patch.object(report_utils, "PORTFOLIO", {"as_of": _today_str}):
    lines = report_utils.portfolio_staleness_lines()
check("a PORTFOLIO dated today produces no warning", lines == [], f"got {lines}")

with mock.patch.object(report_utils, "PORTFOLIO", {"as_of": _fresh_str}):
    lines = report_utils.portfolio_staleness_lines()
check("a PORTFOLIO 10 days old (well under the threshold) produces no warning", lines == [], f"got {lines}")

with mock.patch.object(report_utils, "PORTFOLIO", {"as_of": _boundary_str}):
    lines = report_utils.portfolio_staleness_lines()
check(f"a PORTFOLIO exactly {report_utils.PORTFOLIO_STALENESS_DAYS} days old (the boundary) "
      "does not yet warn (strictly-greater-than check)",
      lines == [], f"got {lines}")

with mock.patch.object(report_utils, "PORTFOLIO", {"as_of": _old_str}):
    lines = report_utils.portfolio_staleness_lines()
check(f"a PORTFOLIO {report_utils.PORTFOLIO_STALENESS_DAYS + 1} days old (just past the boundary) warns visibly",
      len(lines) == 1 and "PORTFOLIO" in lines[0] and "old" in lines[0], f"got {lines}")
check("the warning names the specific stale fields so it's actionable, not generic",
      len(lines) == 1 and "total_aum" in lines[0] and "target_monthly_combined" in lines[0],
      f"got {lines}")

with mock.patch.object(report_utils, "PORTFOLIO", {}):
    lines = report_utils.portfolio_staleness_lines()
check("a PORTFOLIO with no 'as_of' key at all warns (never silently skips the check)",
      len(lines) == 1 and "no" in lines[0].lower() and "as_of" in lines[0], f"got {lines}")

with mock.patch.object(report_utils, "PORTFOLIO", {"as_of": "not-a-date"}):
    lines = report_utils.portfolio_staleness_lines()
check("a malformed 'as_of' value warns instead of raising",
      len(lines) == 1 and "malformed" in lines[0].lower(), f"got {lines}")

# ---------------------------------------------------------------------------
# The REAL (unmocked) config.PORTFOLIO -- demonstrates the fix against live
# data, not just a mocked fixture. as_of 2026-04-30 is the real git-blame
# date these figures were last touched (never edited since), which is
# already well past the 75-day threshold as of this test running.
# ---------------------------------------------------------------------------
print("\nreal (unmocked) config.PORTFOLIO against the real current date")

real_lines = report_utils.portfolio_staleness_lines()
check("the real PORTFOLIO['as_of'] (2026-04-30, its real last-edited date) is currently "
      "over the 75-day threshold, so the real helper call warns -- this is the exact "
      "silent-staleness gap issue #53 reported, now surfaced instead of hidden",
      len(real_lines) == 1 and "2026-04-30" in real_lines[0], f"got {real_lines}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
