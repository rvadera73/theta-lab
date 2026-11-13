"""
Regression tests for mcp/reports/unified_master_report_production.py's
_naked_covered_calls() (ADR 0005 systematic-audit fix, 2026-11-12).

Real bug: shares and short calls were summed GLOBALLY across every
account holding the ticker, instead of per account. Shares and a short
call must sit in the SAME brokerage account to actually back each other
(the exact rule services.py's own _leg_coverage_and_strangle_expiries()
already follows for the dashboard's per-leg scoring) -- a naked call sold
in Account A with 0 shares in A could read as "covered" using shares
owned in a completely different Account B that holds no calls at all.

Builds a minimal UnifiedReportProduction instance via object.__new__ (skips
the real __init__, which does full 8-account loading + live Yahoo fetches)
and injects only self.open_positions / self.equity_positions, the two
attributes this method actually reads.

No pytest dependency -- run directly: python3 tests/test_naked_covered_calls.py
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


def _make_instance(open_positions_rows, equity_positions):
    inst = object.__new__(UnifiedReportProduction)
    inst.open_positions = pd.DataFrame(open_positions_rows)
    inst.equity_positions = equity_positions
    return inst


# ---------------------------------------------------------------------------
# The real bug: shares in Account B must not back a naked call sold in
# Account A.
# ---------------------------------------------------------------------------
print("Shares in one account do not cover a naked call sold in a different account")

cross_account = _make_instance(
    open_positions_rows=[
        {"ticker": "MULTI", "option_type": "CALL", "net_quantity": 3, "account_name": "A"},
    ],
    equity_positions={"B": {"MULTI": 300}},  # shares live in B, calls sold in A
)
naked, covered, calls, puts = cross_account._naked_covered_calls("MULTI")
check("3 calls sold in A with 0 shares in A read as fully NAKED, "
      "not covered by B's 300 shares",
      naked == 3 and covered == 0, f"naked={naked} covered={covered}")
check("calls/puts totals (cross-account, used for messaging elsewhere) are unaffected",
      calls == 3 and puts == 0, f"calls={calls} puts={puts}")

# ---------------------------------------------------------------------------
# Same-account coverage must still work exactly as before -- the common,
# correct case this fix must not regress.
# ---------------------------------------------------------------------------
print("\nSame-account coverage still works correctly (no regression)")

same_account = _make_instance(
    open_positions_rows=[
        {"ticker": "SAME", "option_type": "CALL", "net_quantity": 2, "account_name": "A"},
    ],
    equity_positions={"A": {"SAME": 200}},  # shares AND calls both in A
)
naked2, covered2, calls2, _ = same_account._naked_covered_calls("SAME")
check("2 calls fully covered by 200 shares in the SAME account -> naked=0, covered=2",
      naked2 == 0 and covered2 == 2, f"naked={naked2} covered={covered2}")

# ---------------------------------------------------------------------------
# Mixed real multi-account book: Account A fully covers its own calls,
# Account C sells naked calls with no shares at all. Totals must sum each
# account's own correct result, not blend across them.
# ---------------------------------------------------------------------------
print("\nMixed multi-account book: each account's own coverage sums correctly")

mixed = _make_instance(
    open_positions_rows=[
        {"ticker": "MIX", "option_type": "CALL", "net_quantity": 1, "account_name": "A"},
        {"ticker": "MIX", "option_type": "CALL", "net_quantity": 2, "account_name": "C"},
    ],
    equity_positions={"A": {"MIX": 100}},  # A: 1 call fully covered; C: 2 calls, 0 shares -> naked
)
naked3, covered3, calls3, _ = mixed._naked_covered_calls("MIX")
check("A's 1 call is covered (100 shares in A) and C's 2 calls are naked (0 shares in C) "
      "-> naked=2, covered=1 (not naked=0/covered=3, which global aggregation would wrongly give)",
      naked3 == 2 and covered3 == 1, f"naked={naked3} covered={covered3}")
check("calls total still sums across both accounts (1+2=3)", calls3 == 3, f"got {calls3}")

# ---------------------------------------------------------------------------
# A ticker with no option positions at all must not raise (empty groupby).
# ---------------------------------------------------------------------------
print("\nA ticker with zero option positions returns zeros, not a crash")

none_at_all = _make_instance(
    open_positions_rows=[{"ticker": "OTHER", "option_type": "CALL", "net_quantity": 1, "account_name": "A"}],
    equity_positions={},
)
naked4, covered4, calls4, puts4 = none_at_all._naked_covered_calls("NOTHELD")
check("a ticker absent from open_positions returns naked=covered=calls=puts=0, not a crash",
      naked4 == 0 and covered4 == 0 and calls4 == 0 and puts4 == 0,
      f"naked={naked4} covered={covered4} calls={calls4} puts={puts4}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
