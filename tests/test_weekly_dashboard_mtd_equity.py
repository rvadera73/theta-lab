"""
Regression tests for month_to_date_equity_change handling in
mcp/routines/weekly_dashboard.py (GitHub issue #52).

Real bug this guards against: month_to_date_equity_change is a fully
manual weekly field -- scripts/update_snapshot.py writes a placeholder
every time it regenerates the snapshot, and the trader is supposed to
hand-edit in the real number afterward. weekly_dashboard.py used to read
it back through TWO DIFFERENT silent fallbacks depending on code path: a
hardcoded magic guess of -15000 when CSVs were present, or 0 in the
GitHub-Actions snapshot-only fallback path. If the manual edit was ever
skipped, the dashboard silently reported either a fabricated -$15K swing
or a silently-wrong $0, with no flag anywhere that the number was never
actually entered.

The fix: scripts/update_snapshot.py now writes `None` (YAML null) as the
"not entered yet" placeholder instead of 0 (0 is a legitimate real value --
no stock price movement -- and must not be confused with "never entered").
mcp/routines/weekly_dashboard.py resolves the field through one shared
function, _resolve_mtd_equity_change(), so both the CSV-present path and
the snapshot-only fallback path behave identically: a not-entered value
contributes $0 to the combined total AND surfaces an explicit
"not entered this week" note, while a real entered value (including a
real 0) passes through unchanged with no note and no guessing.

No pytest dependency -- run directly: python3 tests/test_weekly_dashboard_mtd_equity.py
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp"))
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp" / "models"))

from routines.weekly_dashboard import (  # noqa: E402
    _resolve_mtd_equity_change,
    _MTD_EQUITY_NOT_ENTERED_NOTE,
)
from analysis.metrics import monthly_target_tracker  # noqa: E402

failures = []


def check(label, condition, detail):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# 1. _resolve_mtd_equity_change() contract -- the single function both read
#    paths must call, so "not entered" behaves identically everywhere.
# ---------------------------------------------------------------------------
print("_resolve_mtd_equity_change() unit cases")

value, entered, note = _resolve_mtd_equity_change({})
check(
    "missing key -> not entered, value 0.0, note present",
    (value, entered) == (0.0, False) and note == _MTD_EQUITY_NOT_ENTERED_NOTE,
    f"got ({value}, {entered}, {note!r})",
)

value, entered, note = _resolve_mtd_equity_change({"month_to_date_equity_change": None})
check(
    "explicit null placeholder -> not entered, value 0.0, note present",
    (value, entered) == (0.0, False) and note == _MTD_EQUITY_NOT_ENTERED_NOTE,
    f"got ({value}, {entered}, {note!r})",
)

check(
    "the old -15000 magic constant is gone",
    value != -15000,
    "resolver still returns the removed magic guess for a missing/null field",
)

# A REAL entered value of exactly 0 must NOT be mistaken for "not entered" --
# this is the actual distinction the 0-vs-0-placeholder bug collapsed.
value, entered, note = _resolve_mtd_equity_change({"month_to_date_equity_change": 0})
check(
    "real entered 0 -> entered=True, value 0.0, no note",
    (value, entered, note) == (0.0, True, ""),
    f"got ({value}, {entered}, {note!r})",
)

value, entered, note = _resolve_mtd_equity_change({"month_to_date_equity_change": -3200.5})
check(
    "real entered non-zero value passes through unchanged",
    (value, entered, note) == (-3200.5, True, ""),
    f"got ({value}, {entered}, {note!r})",
)

# ---------------------------------------------------------------------------
# 2. Both weekly_dashboard.py code paths must behave IDENTICALLY given the
#    same snapshot state -- same equity_change_entered flag, same note text,
#    same $0 contribution to the combined total when not entered.
# ---------------------------------------------------------------------------
print("\nCSV-present path vs snapshot-only fallback path -- same snapshot state")


def run_csv_path(snapshot, transactions):
    """Mirrors weekly_dashboard.run_weekly_dashboard()'s `if transactions:` branch."""
    mtd_equity_value, equity_entered, equity_note = _resolve_mtd_equity_change(snapshot)
    mt = monthly_target_tracker(
        transactions,
        unrealized_equity_change=mtd_equity_value,
        target_monthly=100_000,
    )
    mt["equity_change_entered"] = equity_entered
    mt["interpretation"] = mt.get("interpretation", "") + equity_note
    return mt


def run_snapshot_only_path(snapshot):
    """Mirrors weekly_dashboard.run_weekly_dashboard()'s `else:` (GitHub Actions) branch."""
    mtd_premium = snapshot.get("month_to_date_premium", 0)
    mtd_equity, equity_entered, equity_note = _resolve_mtd_equity_change(snapshot)
    combined = mtd_premium + mtd_equity
    pct = combined / 100_000 * 100
    return {
        "pct_of_target": round(pct, 1),
        "combined_total": combined,
        "net_options_premium": mtd_premium,
        "unrealized_equity_change": mtd_equity,
        "equity_change_entered": equity_entered,
        "target_monthly": 100_000,
        "remaining_to_target": max(0, 100_000 - combined),
        "signal": "ON TRACK" if pct >= 80 else ("WATCH" if pct >= 50 else "BEHIND"),
        "interpretation": (
            f"MTD: ${combined:,.0f} of $100,000 target ({pct:.1f}%). From snapshot."
            + equity_note
        ),
    }


NO_TRANSACTIONS = []  # premium contribution is 0 on the CSV path with no rows

# Case A: never entered this week (fresh snapshot regen -- null placeholder).
snap_not_entered = {"month_to_date_premium": 12_000, "month_to_date_equity_change": None}
mt_csv = run_csv_path(snap_not_entered, NO_TRANSACTIONS)
mt_snap = run_snapshot_only_path(snap_not_entered)

check(
    "not-entered: both paths report equity_change_entered=False",
    mt_csv["equity_change_entered"] is False and mt_snap["equity_change_entered"] is False,
    f"csv={mt_csv['equity_change_entered']} snapshot={mt_snap['equity_change_entered']}",
)
check(
    "not-entered: both paths treat equity contribution as $0",
    mt_csv["unrealized_equity_change"] == 0.0 and mt_snap["unrealized_equity_change"] == 0.0,
    f"csv={mt_csv['unrealized_equity_change']} snapshot={mt_snap['unrealized_equity_change']}",
)
check(
    "not-entered: both paths surface the identical explicit note",
    _MTD_EQUITY_NOT_ENTERED_NOTE in mt_csv["interpretation"]
    and _MTD_EQUITY_NOT_ENTERED_NOTE in mt_snap["interpretation"],
    f"csv={mt_csv['interpretation']!r} snapshot={mt_snap['interpretation']!r}",
)
check(
    "not-entered: combined total on the snapshot-only path is premium-only (no guess added)",
    mt_snap["combined_total"] == 12_000,
    f"got {mt_snap['combined_total']}",
)

# Case B: a real value was entered this week, including a real $0.
# (whole-dollar values -- monthly_target_tracker's own pre-existing
# round(value, 0) on this field, unrelated to this fix, would otherwise
# make a fractional value compare unequal between the two paths)
for real_value in (0, -4100.0, 8_250.0):
    snap_entered = {"month_to_date_premium": 12_000, "month_to_date_equity_change": real_value}
    mt_csv = run_csv_path(snap_entered, NO_TRANSACTIONS)
    mt_snap = run_snapshot_only_path(snap_entered)

    check(
        f"entered value {real_value}: both paths report equity_change_entered=True",
        mt_csv["equity_change_entered"] is True and mt_snap["equity_change_entered"] is True,
        f"csv={mt_csv['equity_change_entered']} snapshot={mt_snap['equity_change_entered']}",
    )
    check(
        f"entered value {real_value}: both paths pass the real value through unchanged",
        mt_csv["unrealized_equity_change"] == float(real_value)
        and mt_snap["unrealized_equity_change"] == float(real_value),
        f"csv={mt_csv['unrealized_equity_change']} snapshot={mt_snap['unrealized_equity_change']}",
    )
    check(
        f"entered value {real_value}: no 'not entered' note on either path",
        _MTD_EQUITY_NOT_ENTERED_NOTE not in mt_csv["interpretation"]
        and _MTD_EQUITY_NOT_ENTERED_NOTE not in mt_snap["interpretation"],
        f"csv={mt_csv['interpretation']!r} snapshot={mt_snap['interpretation']!r}",
    )
    check(
        f"entered value {real_value}: snapshot-only combined total includes the real equity change",
        mt_snap["combined_total"] == 12_000 + real_value,
        f"got {mt_snap['combined_total']}",
    )

# ---------------------------------------------------------------------------
# 3. scripts/update_snapshot.py writes the null sentinel, not 0, for the
#    not-yet-entered placeholder -- the write side of the contract.
# ---------------------------------------------------------------------------
print("\nscripts/update_snapshot.py write-side placeholder")

_update_snapshot_src = (_ROOT / "scripts" / "update_snapshot.py").read_text()
check(
    "write side no longer hardcodes 0 as the month_to_date_equity_change placeholder",
    '"month_to_date_equity_change": 0,' not in _update_snapshot_src,
    "found the old 0 placeholder literal still present",
)
check(
    "write side writes the None/null not-entered sentinel",
    '"month_to_date_equity_change": None,' in _update_snapshot_src,
    "did not find the None sentinel literal",
)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
