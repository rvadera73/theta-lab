"""
Cross-check regression test: services.py's _leg_coverage_and_strangle_expiries()
and heat_scanner.py's _call_coverage_by_id() are two SEPARATE, hand-written
implementations of the identical ADR 0005 share-allocation algorithm (sort
CALL legs by strike ascending, consume owned shares in that order, mark
covered/partial/naked). They currently agree by careful construction, but
nothing enforces that -- a future bug fix or behavior change to one (e.g.
handling fractional/odd-lot shares, or changing the strike-ascending
tiebreak rule) would not automatically propagate to the other, silently
reintroducing exactly the kind of dashboard-vs-report disagreement ADR
0005 spent real effort removing.

This test runs ONE shared, real multi-leg, partially-covered Position
fixture through BOTH implementations and asserts they classify every CALL
leg identically. It is a cross-check, not a correctness proof of either
implementation alone -- if both are wrong in the same way, this test
would still pass; its job is only to catch the two drifting APART.

No pytest dependency -- run directly: python3 tests/test_coverage_allocation_cross_check.py
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "dashboard" / "backend"
for _p in (
    _BACKEND,
    _ROOT / "mcp" / "reports",
    _ROOT / "mcp" / "analysis",
    _ROOT / "mcp",
    _ROOT / "scripts",
):
    sys.path.insert(0, str(_p))

from pnl import Position, OptionLeg  # noqa: E402
from heat_scanner import _call_coverage_by_id  # noqa: E402
from app import services  # noqa: E402

_leg_coverage_and_strangle_expiries = services._leg_coverage_and_strangle_expiries

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def _svc_coverage_string(cov_entry):
    """Mirrors services.py's own _process_position_legs() classification
    (not re-derived here -- this is the exact same if/elif/else it uses to
    turn a _leg_coverage_and_strangle_expiries() entry into the 'coverage'
    string ADR 0005 feeds into heat_scanner.assess_portfolio_heat())."""
    if not cov_entry["naked"]:
        return "COVERED"
    if cov_entry["covered_contracts"] > 0:
        return "PARTIAL"
    return "NAKED"


print("services.py vs heat_scanner.py: identical coverage allocation on a shared fixture")

# 250 shares: fully covers the 1-contract $10 strike, partially covers the
# 2-contract $15 strike (1 of 2), leaves the $20 strike fully naked --
# exercises all three coverage states in one position, same fixture shape
# fork 2's audit proposed.
pos = Position(
    symbol="XYZ", account="A", shares=250, stock_cost_basis=100.0, current_price=18.0,
    option_legs=[
        OptionLeg(description="XYZ 10C", strike=10.0, expiry="2027-06-18", option_type="CALL",
                  quantity=-1, premium_received=200.0, current_mark=800.0, dte=60),
        OptionLeg(description="XYZ 15C (1 of 2)", strike=15.0, expiry="2027-06-18", option_type="CALL",
                  quantity=-2, premium_received=150.0, current_mark=400.0, dte=60),
        OptionLeg(description="XYZ 20C", strike=20.0, expiry="2027-06-18", option_type="CALL",
                  quantity=-1, premium_received=100.0, current_mark=150.0, dte=60),
    ],
)

svc_cov, _ = _leg_coverage_and_strangle_expiries(pos)
hs_cov = _call_coverage_by_id(pos)

mismatches = []
for lg in pos.option_legs:
    svc_entry = svc_cov.get(id(lg))
    hs_value = hs_cov.get(id(lg))
    svc_value = _svc_coverage_string(svc_entry) if svc_entry else None
    if svc_value != hs_value:
        mismatches.append((lg.strike, svc_value, hs_value))

check("the $10 strike (fully covered) agrees between both implementations",
      not any(m[0] == 10.0 for m in mismatches), f"got mismatches={mismatches}")
check("the $15 strike (partially covered, 1 of 2) agrees between both implementations",
      not any(m[0] == 15.0 for m in mismatches), f"got mismatches={mismatches}")
check("the $20 strike (fully naked) agrees between both implementations",
      not any(m[0] == 20.0 for m in mismatches), f"got mismatches={mismatches}")
check("no mismatches at all across the fixture's 3 CALL legs",
      len(mismatches) == 0, f"got {mismatches}")

# Sanity-check the fixture actually exercises all 3 states (a cross-check
# that silently agrees because both sides returned the SAME WRONG thing
# for every leg would be worthless).
hs_values = {lg.strike: hs_cov.get(id(lg)) for lg in pos.option_legs}
check("the fixture itself genuinely exercises COVERED/PARTIAL/NAKED, not a degenerate case",
      hs_values == {10.0: "COVERED", 15.0: "PARTIAL", 20.0: "NAKED"}, f"got {hs_values}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
