"""
Regression tests for dashboard/backend/app/sequencer.py's two ADR 0001
step-1/step-2 fixes:

1. `_SEVERITY_RANK` gained a `CLOSE_RESTAGGER` entry (previously missing
   entirely -- it silently fell to the same default rank as `WATCH_CLOSE`,
   a time-bound forced action ranked identically to a merely-watched one).
2. `_tier2_rows()` now skips any watchlist row carrying a truthy `error`
   key (e.g. "no_expiry_in_75-135_dte_window") instead of surfacing it as
   noise like "ENTER TGT: score=None".

The _tier2_rows() check mocks services.get_composite_scores() with a
minimal fake shape -- it must NOT hit real network/live data.

No pytest dependency -- run directly: python3 tests/test_sequencer_severity.py
"""
import sys
from pathlib import Path
from unittest import mock

_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "dashboard" / "backend"
sys.path.insert(0, str(_BACKEND))

from app import sequencer  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


print("_SEVERITY_RANK: CLOSE_RESTAGGER")

check("_SEVERITY_RANK has a CLOSE_RESTAGGER entry at all (previously missing entirely)",
      "CLOSE_RESTAGGER" in sequencer._SEVERITY_RANK,
      f"got keys={list(sequencer._SEVERITY_RANK.keys())}")
check("_SEVERITY_RANK['CLOSE_RESTAGGER'] == 2",
      sequencer._SEVERITY_RANK.get("CLOSE_RESTAGGER") == 2,
      f"got {sequencer._SEVERITY_RANK.get('CLOSE_RESTAGGER')}")
check("CLOSE_RESTAGGER (2) ranks strictly ahead of WATCH_CLOSE (3) -- time-bound beats market-driven",
      sequencer._SEVERITY_RANK["CLOSE_RESTAGGER"] < sequencer._SEVERITY_RANK["WATCH_CLOSE"],
      f"CLOSE_RESTAGGER={sequencer._SEVERITY_RANK['CLOSE_RESTAGGER']} "
      f"WATCH_CLOSE={sequencer._SEVERITY_RANK['WATCH_CLOSE']}")
check("CUT_RESTAGGER/CLOSE_NOW (0) still rank ahead of CLOSE_RESTAGGER (2) -- a real hard stop "
      "still outranks a forced-but-not-yet-critical close",
      sequencer._SEVERITY_RANK["CUT_RESTAGGER"] < sequencer._SEVERITY_RANK["CLOSE_RESTAGGER"],
      f"got {sequencer._SEVERITY_RANK}")

print("\n_tier2_rows(): rows carrying an error key are excluded, not surfaced as noise")

_FAKE_COMPOSITE_SCORES = {
    "watchlist": [
        {"ticker": "TGT", "error": "no_expiry_in_75-135_dte_window"},
        {"ticker": "GOODCO", "score": 1.23, "iv_rank": 55.0, "yield_pct": 12.0, "conviction": 7,
         "gates_fired": [], "is_new": True},
        {"ticker": "ALSOBAD", "error": "empty_option_chain"},
    ],
    "held": [],
}

with mock.patch.object(sequencer.services, "get_composite_scores",
                        return_value=_FAKE_COMPOSITE_SCORES):
    rows = sequencer._tier2_rows()

tickers = [r["ticker"] for r in rows]
check("errored watchlist rows (TGT, ALSOBAD) are excluded from _tier2_rows()",
      "TGT" not in tickers and "ALSOBAD" not in tickers, f"got tickers={tickers}")
check("a genuinely scoreable watchlist row (GOODCO) still comes through",
      "GOODCO" in tickers, f"got tickers={tickers}")
check("exactly one row survives out of the three fake watchlist entries",
      len(rows) == 1, f"got {len(rows)} rows: {rows}")

print("\nADR 0005: _is_actionable_leg()/_coverage_rank() prefer the real "
      "per-leg `coverage` field over the stale pooled `covered` boolean")

# Same cross-account-collision pattern as tests/test_services.py's AAPL
# $200 CALL fixture: the real per-leg `coverage` says COVERED, but the
# pooled, cross-account-AND-combined `covered` annotation (services.py)
# disagrees because an identical contract is naked in a different account.
collision_covered_red_leg = {
    "type": "CALL", "color": "RED", "action": "CLOSE_OR_ASSIGN",
    "coverage": "COVERED", "covered": False, "covered_contracts": 0,
}
check("a RED leg with coverage='COVERED' is NOT actionable even when the "
      "pooled `covered` annotation disagrees (reads False)",
      not sequencer._is_actionable_leg(collision_covered_red_leg),
      f"leg={collision_covered_red_leg}")
check("_coverage_rank ranks it as COVERED (2), not NAKED (0)",
      sequencer._coverage_rank(collision_covered_red_leg) == 2,
      f"got {sequencer._coverage_rank(collision_covered_red_leg)}")

# The mirror case: coverage='NAKED' but the stale pooled annotation happens
# to read covered=True (the same collision, opposite direction) -- a real
# naked call must still be actionable and rank as naked, not covered.
collision_naked_red_leg = {
    "type": "CALL", "color": "RED", "action": "CUT_RESTAGGER",
    "coverage": "NAKED", "covered": True, "covered_contracts": 1,
}
check("a RED leg with coverage='NAKED' IS actionable even when the pooled "
      "`covered` annotation disagrees (reads True)",
      sequencer._is_actionable_leg(collision_naked_red_leg),
      f"leg={collision_naked_red_leg}")
check("_coverage_rank ranks it as NAKED (0), not COVERED (2)",
      sequencer._coverage_rank(collision_naked_red_leg) == 0,
      f"got {sequencer._coverage_rank(collision_naked_red_leg)}")

# PARTIAL ranks with NAKED (its uncovered portion is real risk).
partial_leg = {"type": "CALL", "color": "RED", "coverage": "PARTIAL"}
check("PARTIAL ranks with NAKED (0), not COVERED",
      sequencer._coverage_rank(partial_leg) == 0, f"got {sequencer._coverage_rank(partial_leg)}")

# A pre-ADR-0005 leg with no `coverage` key at all must still fall back to
# the old boolean-keyed behavior -- this module's own backward-compat path.
pre_adr0005_covered_leg = {"type": "CALL", "color": "YELLOW", "covered": True}
check("a leg with no `coverage` key falls back to the old `covered` boolean "
      "(still excluded from Tier 1 when covered=True)",
      not sequencer._is_actionable_leg(pre_adr0005_covered_leg),
      f"leg={pre_adr0005_covered_leg}")

print("\n_tier1_rows(): a same-account COVERED position group is excluded "
      "from Tier 1 even when the pooled `covered` annotation disagrees")

_FAKE_POSITION_HEAT_COLLISION = {
    "positions": [
        {"symbol": "AAPL", "account": "A", "legs": [collision_covered_red_leg]},
        {"symbol": "ZZZZ", "account": "B", "legs": [collision_naked_red_leg]},
    ],
}
with mock.patch.object(sequencer.services, "get_position_heat",
                        return_value=_FAKE_POSITION_HEAT_COLLISION), \
     mock.patch.object(sequencer.services, "get_composite_scores",
                        return_value={"held": []}):
    tier1 = sequencer._tier1_rows()

tier1_symbols = [r["symbol"] for r in tier1]
check("the fully-covered AAPL group (real coverage=COVERED, stale covered=False) "
      "is excluded from Tier 1",
      "AAPL" not in tier1_symbols, f"got symbols={tier1_symbols}")
check("the genuinely naked ZZZZ group (real coverage=NAKED, stale covered=True) "
      "still appears in Tier 1",
      "ZZZZ" in tier1_symbols, f"got symbols={tier1_symbols}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
