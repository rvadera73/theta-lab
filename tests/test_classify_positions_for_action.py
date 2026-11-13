"""
Regression tests for mcp/reports/unified_master_report_production.py's
_classify_positions_for_action() (ADR 0005 sibling fix, 2026-11-12).

This method feeds raw ticker lists directly into THREE sections (Section 3
Top-5 Action Items, Section 7's Close Now/Monitor lists, the Weekly
Execution Plan's Reduce/Manage bucket) as literal "CLOSE {ticker}"/"TRIM
{ticker}" commands -- unlike suggestion_for() (same class), which already
has a covered-call carve-out. Before this fix, a fully-covered-only ticker
(RED heat, low conviction, no naked calls, no real puts) still landed in
close_/trim_ here and got recommended for closing/trimming in those three
sections, even though suggestion_for()'s own label for the identical ticker
would correctly say "covered call(s) only, no naked/strangle risk."

Builds a minimal UnifiedReportProduction instance via object.__new__ (skips
the real __init__, which does full 8-account loading + live Yahoo fetches)
and injects only the attributes _classify_positions_for_action() and its
_naked_covered_calls()/_get_conviction_summary() dependencies actually
read: self.metrics, self.open_positions, self.equity_positions.

No pytest dependency -- run directly: python3 tests/test_classify_positions_for_action.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "reports"))

from unified_master_report_production import UnifiedReportProduction

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def _make_instance(metrics, open_positions_rows, equity_positions):
    inst = object.__new__(UnifiedReportProduction)
    inst.metrics = metrics
    inst.open_positions = pd.DataFrame(open_positions_rows)
    inst.equity_positions = equity_positions
    return inst


# ---------------------------------------------------------------------------
# A fully covered-only ticker (SONO's real pattern: RED heat, no naked
# calls, no real puts) must be excluded from close_/trim_ regardless of
# conviction -- the exact bug class this fix addresses.
# ---------------------------------------------------------------------------
print("Covered-only RED/low-conviction ticker is excluded from close/trim")

sono_like = _make_instance(
    metrics={"SONO": {"heat_status": "RED", "conviction": 4.5}},
    open_positions_rows=[{"ticker": "SONO", "option_type": "CALL", "net_quantity": 4, "account_name": "F1"}],
    equity_positions={"F1": {"SONO": 400}},
)
naked, covered, total_calls, total_puts = sono_like._naked_covered_calls("SONO")
check("fixture is genuinely fully covered (naked==0, covered>0)",
      naked == 0 and covered > 0, f"naked={naked} covered={covered}")

classified = sono_like._classify_positions_for_action()
close_t = {t for t, _ in classified['close']}
trim_t = {t for t, _ in classified['trim']}
check("covered-only ticker excluded from close/trim even at conviction<5 (would-be CLOSE)",
      "SONO" not in close_t and "SONO" not in trim_t,
      f"close={close_t} trim={trim_t}")

# Same fixture but at a higher conviction (5<=conv<7, would-be TRIM) --
# must still be excluded, proving the exclusion doesn't depend on which
# conviction band it would have landed in.
sono_like_trim_band = _make_instance(
    metrics={"SONO": {"heat_status": "RED", "conviction": 6.5}},
    open_positions_rows=[{"ticker": "SONO", "option_type": "CALL", "net_quantity": 4, "account_name": "F1"}],
    equity_positions={"F1": {"SONO": 400}},
)
classified2 = sono_like_trim_band._classify_positions_for_action()
close_t2 = {t for t, _ in classified2['close']}
trim_t2 = {t for t, _ in classified2['trim']}
check("covered-only ticker excluded from trim at conviction=6.5 (the realistic SONO-adjacent case)",
      "SONO" not in close_t2 and "SONO" not in trim_t2,
      f"close={close_t2} trim={trim_t2}")

# ---------------------------------------------------------------------------
# A genuinely naked call, RED heat, low conviction -- must still classify
# CLOSE/TRIM exactly as before. This fix must not introduce a false
# negative for real risk.
# ---------------------------------------------------------------------------
print("\nGenuinely naked-call RED/low-conviction ticker still classifies CLOSE/TRIM")

naked_ticker = _make_instance(
    metrics={"XYZ": {"heat_status": "RED", "conviction": 4.5}},
    open_positions_rows=[{"ticker": "XYZ", "option_type": "CALL", "net_quantity": 3, "account_name": "A"}],
    equity_positions={},
)
naked2, covered2, _, _ = naked_ticker._naked_covered_calls("XYZ")
check("XYZ fixture is genuinely naked (naked==3, covered==0)",
      naked2 == 3 and covered2 == 0, f"naked={naked2} covered={covered2}")
close_t3 = {t for t, _ in naked_ticker._classify_positions_for_action()['close']}
check("real naked RED/low-conviction ticker still correctly classified CLOSE",
      "XYZ" in close_t3, f"close={close_t3}")

# ---------------------------------------------------------------------------
# A covered call WITH a real separate short put on the same name (the OKTA
# pattern -- a covered call plus genuine put-side assignment risk) must NOT
# be excluded -- the put-side risk is real and distinct from the covered
# call. This is the precise reason the fix checks total_puts<=0, not just
# naked<=0.
# ---------------------------------------------------------------------------
print("\nCovered call + a real separate short put is NOT excluded (real put-side risk)")

okta_like = _make_instance(
    metrics={"OKTA": {"heat_status": "RED", "conviction": 4.5}},
    open_positions_rows=[
        {"ticker": "OKTA", "option_type": "CALL", "net_quantity": 2, "account_name": "A"},
        {"ticker": "OKTA", "option_type": "PUT", "net_quantity": 3, "account_name": "A"},
    ],
    equity_positions={"A": {"OKTA": 200}},
)
naked3, covered3, _, puts3 = okta_like._naked_covered_calls("OKTA")
check("OKTA fixture: calls fully covered (naked==0) but 3 real short puts open",
      naked3 == 0 and covered3 == 2 and puts3 == 3, f"naked={naked3} covered={covered3} puts={puts3}")
close_t4 = {t for t, _ in okta_like._classify_positions_for_action()['close']}
check("covered call + real put-side risk is still correctly classified CLOSE "
      "(total_puts>0 means the covered>0/naked<=0/total_puts<=0 carve-out does not apply)",
      "OKTA" in close_t4, f"close={close_t4}")

# ---------------------------------------------------------------------------
# A pure stock-only RED/low-conviction ticker (zero calls, zero puts at
# all) must NOT be excluded -- it has nothing to do with covered calls, and
# the naive "naked<=0 and total_puts<=0" exclusion a less careful fix would
# use incorrectly catches this case too (covered==naked==total_puts==0 is
# also true here). Regression check for the refined covered>0 guard.
# ---------------------------------------------------------------------------
print("\nPure stock-only RED/low-conviction ticker (no options at all) still classifies CLOSE/TRIM")

stock_only = _make_instance(
    metrics={"PURESTOCK": {"heat_status": "RED", "conviction": 4.5}},
    open_positions_rows=[{"ticker": "OTHERTICKER", "option_type": "PUT", "net_quantity": -1, "account_name": "A"}],
    equity_positions={"A": {"PURESTOCK": 500}},
)
naked4, covered4, _, puts4 = stock_only._naked_covered_calls("PURESTOCK")
check("PURESTOCK fixture has zero calls and zero puts (covered==naked==total_puts==0)",
      naked4 == 0 and covered4 == 0 and puts4 == 0, f"naked={naked4} covered={covered4} puts={puts4}")
close_t5 = {t for t, _ in stock_only._classify_positions_for_action()['close']}
check("a pure stock-only position (no calls/puts at all) is NOT excluded by the "
      "covered-call carve-out -- it stays eligible for CLOSE on its own stock merits",
      "PURESTOCK" in close_t5, f"close={close_t5}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
