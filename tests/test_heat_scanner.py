"""
Characterization tests for mcp/analysis/heat_scanner.py (Bolt b7).

heat_scanner.py had ZERO test coverage before this file, despite being the
engine behind every live heat/action-tracker/decision-engine call (scored by
cost-to-close-vs-premium multiple, strike distance, and DTE -- see the file's
own module docstring and the 2026-10-15 "RED regardless of DTE" bug comment
at lines 78-93). These tests lock down the REAL current thresholds read from
mcp/config.py's HEAT_THRESHOLDS/HEAT_REGIME_ACTIONS (not round guessed
numbers) and the real leg-dict shape fed by dashboard/backend/app/services.py
and mcp/analysis/heat_from_positions()'s own construction of that shape.

Coverage note on "covered"/"naked"/"partial" (UPDATED by ADR 0005,
2026-11-12): heat_scanner.py now DOES take a `coverage` classification
(NAKED/COVERED/PARTIAL/CASH_SECURED_PUT) as a scoring input -- see the
"ADR 0005: coverage-aware severity" section below. decision_engine.py
(tests/test_decision_engine.py) still independently re-derives the same
classification from services.py's post-hoc `covered`/`covered_contracts`
annotation for its own LegDecisionRecord.coverage field -- the two are
computed from the same underlying per-position share/contract data
(services.py's _leg_coverage_and_strangle_expiries) and should never
disagree, but this file is the one that actually exercises heat_scanner's
own `coverage` parameter and the color/action branches it drives.

REAL BUG FOUND AND FIXED (see heat_scanner.py, heat_from_positions()): the
"no open legs" shortcut return was missing the "UNKNOWN" bucket that
assess_portfolio_heat() always includes, and both format_heat_block() and
format_heat_html() index heat["by_color"]["UNKNOWN"] directly with no
default -- so any no-open-legs week crashed real report generation
(weekly_report.py, monthly_objectives_report.py both pipe heat_from_positions()
straight into one of those formatters). Fixed + regression-tested below.

ISSUE FOUND AND FIXED BY BOLT b11 (2026-11-10):
mcp/config.py's HEAT_THRESHOLDS used to set "yellow" equal to "red" (0.08) for
both "call" and "put", instead of sitting between "green" (0.15) and "red"
(0.08) as the inline comments describe ("yellow: stock 85-92% of strike
(8-15% cushion)"). Because of this, heat_scanner.py line ~109
(`elif self.distance_pct < yellow_dist:`) was unreachable dead code: anything
with distance_pct < 0.08 already matched the RED/YELLOW branches above it,
and 0.08 was as far as this comparison could ever reach. Net effect: a leg
with 8-15% cushion to strike, no profit/loss trigger, and DTE > 21 reported
GREEN, not the documented YELLOW. This also meant the regime "call_tighten"
demotion (which only promotes already-YELLOW calls to RED) could not catch
such a leg via this path either.

Bolt b11 restored "yellow" to the documented midpoint (0.115) between green
(0.15) and red (0.08) in mcp/config.py. The `dead_branch_leg` check below was
updated accordingly (now expects the real, documented YELLOW/PREPARE_ROLL
classification instead of the old dead-branch GREEN). See
tests/test_heat_thresholds.py for the direct regression test.

No pytest dependency -- run directly: python3 tests/test_heat_scanner.py
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp"))

from heat_scanner import (  # noqa: E402
    LegHeat,
    LegContract,
    LegPricing,
    assess_portfolio_heat,
    heat_from_positions,
    format_heat_block,
    format_heat_html,
)
from pnl import Position, OptionLeg  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def leg(symbol, option_type, strike, dte, current_price, premium_received,
        cost_to_close, expiry="2027-06-18", coverage="NAKED"):
    return LegHeat(
        contract=LegContract(symbol=symbol, option_type=option_type, strike=strike,
                              expiry=expiry, coverage=coverage),
        pricing=LegPricing(premium_received=premium_received,
                            cost_to_close=cost_to_close, current_price=current_price),
        dte=dte,
    )


def leg_dict(symbol, option_type, strike, dte, current_price,
             premium_received, cost_to_close, expiry="2027-06-18", coverage="NAKED"):
    return {
        "symbol": symbol, "option_type": option_type, "strike": strike,
        "dte": dte, "expiry": expiry, "premium_received": premium_received,
        "cost_to_close": cost_to_close, "current_price": current_price,
        "coverage": coverage,
    }


# Real thresholds from mcp/config.py HEAT_THRESHOLDS, read here so the
# fixtures below are visibly derived from the real config, not guessed:
#   call/put red = 0.08, yellow = 0.115 (Bolt b11 fix -- see note above),
#   loss_cut_multiplier = 2.0, early_warning_multiple = 1.5,
#   profit_target_pct = 0.40, RED_DTE_WINDOW = 45 (in heat_scanner.py itself)

# ---------------------------------------------------------------------------
# LegHeat: GREEN
# ---------------------------------------------------------------------------
print("GREEN / HOLD")

green_leg = leg("GRN", "CALL", strike=130, dte=60, current_price=100,
                premium_received=500, cost_to_close=350)
check("30% cushion, 30% pnl captured, 0.7x loss multiple, 60 DTE -> GREEN",
      green_leg.color == "GREEN", f"got {green_leg.color}")
check("GREEN leg action is HOLD", green_leg.action == "HOLD", f"got {green_leg.action}")
check("GREEN reason mentions cushion and DTE",
      "cushion" in green_leg.reason and "60d" in green_leg.reason,
      f"got {green_leg.reason!r}")

# ---------------------------------------------------------------------------
# LegHeat: YELLOW -- each reachable branch and action
# ---------------------------------------------------------------------------
print("\nYELLOW branches")

# pnl_pct >= profit_target_pct (0.40) -> YELLOW / HARVEST_RESTAGGER
harvest_leg = leg("HRV", "CALL", strike=125, dte=90, current_price=100,
                   premium_received=500, cost_to_close=200)
check("60% profit captured (>= 40% target) -> YELLOW",
      harvest_leg.color == "YELLOW", f"got {harvest_leg.color}")
check("profit-target hit -> HARVEST_RESTAGGER",
      harvest_leg.action == "HARVEST_RESTAGGER", f"got {harvest_leg.action}")
check("HARVEST_RESTAGGER reason names the real profit % and re-entry DTE "
      "(dte=90 -> reentry = max(180, 90+75) = 180)",
      "60%" in harvest_leg.reason and "180d" in harvest_leg.reason,
      f"got {harvest_leg.reason!r}")

# loss_multiple >= early_warning_multiple (1.5) but < loss_cut (2.0) -> YELLOW / WATCH_CLOSE
watch_leg = leg("WCH", "CALL", strike=120, dte=90, current_price=100,
                 premium_received=500, cost_to_close=750)
check("loss multiple exactly 1.5x (early-warning, below 2.0x hard stop) -> YELLOW",
      watch_leg.color == "YELLOW", f"got {watch_leg.color}")
check("1.5x multiple -> WATCH_CLOSE", watch_leg.action == "WATCH_CLOSE",
      f"got {watch_leg.action}")
check("WATCH_CLOSE reason cites the multiple and the 2.0x hard-stop threshold",
      "1.5x" in watch_leg.reason and "2x" in watch_leg.reason,
      f"got {watch_leg.reason!r}")

# dte <= 21, far from strike, no pnl/loss trigger -> YELLOW / CLOSE_RESTAGGER
close_restagger_leg = leg("CLR", "CALL", strike=130, dte=15, current_price=100,
                           premium_received=500, cost_to_close=400)
check("far from strike but DTE=15 (<=21 gamma window) -> YELLOW",
      close_restagger_leg.color == "YELLOW", f"got {close_restagger_leg.color}")
check("DTE<=21 drives CLOSE_RESTAGGER", close_restagger_leg.action == "CLOSE_RESTAGGER",
      f"got {close_restagger_leg.action}")
check("CLOSE_RESTAGGER reason mentions gamma risk zone",
      "gamma risk zone" in close_restagger_leg.reason,
      f"got {close_restagger_leg.reason!r}")

# distance_pct < red_dist (0.08) but DTE > 45 ("time is working") -> YELLOW, not RED.
# This is the exact 2026-10-15 regression documented in heat_scanner.py lines
# 78-93: strike proximity alone must NOT be RED-urgent when real time remains.
time_working_leg = leg("TMW", "PUT", strike=94, dte=90, current_price=100,
                        premium_received=500, cost_to_close=400)
check("6% cushion (< 8% red threshold) but 90 DTE (> 45d window) -> YELLOW not RED "
      "(2026-10-15 regression: 'time is working')",
      time_working_leg.color == "YELLOW", f"got {time_working_leg.color}")
check("no pnl/loss trigger and DTE > 21 -> PREPARE_ROLL",
      time_working_leg.action == "PREPARE_ROLL", f"got {time_working_leg.action}")
check("PREPARE_ROLL reason names the strike and suggests rolling lower for a PUT",
      "94" in time_working_leg.reason and "lower and further out" in time_working_leg.reason,
      f"got {time_working_leg.reason!r}")

# Same strike proximity, but DTE <= 45 -> this one IS RED (loss_cut-independent
# strike-proximity rule), confirming the DTE window boundary itself.
red_dte_window_leg = leg("RDW", "PUT", strike=94, dte=45, current_price=100,
                          premium_received=500, cost_to_close=400)
check("same 6% cushion but DTE=45 (inside the <=45 RED_DTE_WINDOW) -> RED",
      red_dte_window_leg.color == "RED", f"got {red_dte_window_leg.color}")

# FIXED BY BOLT b11: distance_pct inside the documented 8-11.5% "yellow"
# band (config.py comments) now correctly reports YELLOW/PREPARE_ROLL, now
# that config.py's "yellow" threshold (0.115) sits between "red" (0.08) and
# "green" (0.15) instead of equaling "red" -- this previously-dead branch
# (heat_scanner.py's `elif self.distance_pct < yellow_dist:`) is reachable
# again. Before the fix this leg reported GREEN (see the module docstring's
# "ISSUE FOUND AND FIXED BY BOLT b11" note for the full history).
dead_branch_leg = leg("DBB", "CALL", strike=110, dte=90, current_price=100,
                       premium_received=500, cost_to_close=400)
check("10% cushion (inside documented 8-11.5% yellow band per config.py comments), "
      "no pnl/loss/DTE trigger -> YELLOW (Bolt b11 fix)",
      dead_branch_leg.color == "YELLOW", f"got {dead_branch_leg.color}")
check("10% cushion with no pnl/loss trigger and DTE > 21 -> PREPARE_ROLL",
      dead_branch_leg.action == "PREPARE_ROLL", f"got {dead_branch_leg.action}")

# ---------------------------------------------------------------------------
# LegHeat: RED -- each reachable branch and action
# ---------------------------------------------------------------------------
print("\nRED branches")

# ADR 0005: the hard-stop multiple is now DTE-gated the same as strike
# proximity -- dte=30 (<=45 RED_DTE_WINDOW) is the genuinely-urgent case.
cut_leg = leg("CUT", "CALL", strike=200, dte=30, current_price=100,
              premium_received=500, cost_to_close=1200)
check("loss multiple 2.4x (>= 2.0x hard stop) with DTE=30 (<=45 window) -> RED",
      cut_leg.color == "RED", f"got {cut_leg.color}")
check("hard-stop multiple -> CUT_RESTAGGER", cut_leg.action == "CUT_RESTAGGER",
      f"got {cut_leg.action}")
check("CUT_RESTAGGER reason states the real cost-to-close and premium dollars",
      "$1,200" in cut_leg.reason and "$500" in cut_leg.reason,
      f"got {cut_leg.reason!r}")

close_now_leg = leg("CLN", "CALL", strike=130, dte=5, current_price=100,
                     premium_received=500, cost_to_close=300)
check("DTE=5 (<=7) -> RED regardless of distance/multiple",
      close_now_leg.color == "RED", f"got {close_now_leg.color}")
check("DTE<=7 and multiple below hard stop -> CLOSE_NOW (not CUT_RESTAGGER)",
      close_now_leg.action == "CLOSE_NOW", f"got {close_now_leg.action}")

roll_call_leg = leg("RLC", "CALL", strike=105, dte=30, current_price=100,
                     premium_received=500, cost_to_close=600)
check("5% cushion (< 8% red) with DTE=30 (<=45 window) -> RED",
      roll_call_leg.color == "RED", f"got {roll_call_leg.color}")
check("RED CALL, multiple below hard stop, DTE > 7 -> ROLL_CALL",
      roll_call_leg.action == "ROLL_CALL", f"got {roll_call_leg.action}")

roll_put_leg = leg("RLP", "PUT", strike=95, dte=30, current_price=100,
                    premium_received=500, cost_to_close=600)
check("5% cushion with DTE=30 -> RED (PUT)", roll_put_leg.color == "RED",
      f"got {roll_put_leg.color}")
check("RED PUT, multiple below hard stop, DTE > 7 -> ROLL_OR_CUT_PUT",
      roll_put_leg.action == "ROLL_OR_CUT_PUT", f"got {roll_put_leg.action}")

# ---------------------------------------------------------------------------
# ADR 0005: coverage-aware severity (2026-11-12)
# ---------------------------------------------------------------------------
print("\nADR 0005: coverage-aware severity")

# Real incident this ADR fixes: a NAKED-ladder leg this deep ITM/high-multiple
# (loss_multiple 10.8x, distance -57%) would have been RED/CUT_RESTAGGER
# regardless of coverage before this change. A COVERED call with the exact
# same numbers must now be GREEN/HOLD_TO_ASSIGNMENT -- coverage bypasses the
# naked ladder entirely, it's not just a smaller RED threshold.
covered_deep_itm = leg("OKT", "CALL", strike=80, dte=127, current_price=187,
                        premium_received=3055, cost_to_close=32902, coverage="COVERED")
check("COVERED call, 10.8x loss-multiple, deep ITM, 127 DTE -> GREEN (not RED)",
      covered_deep_itm.color == "GREEN", f"got {covered_deep_itm.color}")
check("COVERED + GREEN -> HOLD_TO_ASSIGNMENT (not CUT_RESTAGGER)",
      covered_deep_itm.action == "HOLD_TO_ASSIGNMENT", f"got {covered_deep_itm.action}")
check("HOLD_TO_ASSIGNMENT reason says no action needed / working as designed",
      "no action needed" in covered_deep_itm.reason.lower(), f"got {covered_deep_itm.reason!r}")

# Same COVERED leg, but inside the dte<=21 roll-decision window -> YELLOW.
covered_near_expiry = leg("OKT", "CALL", strike=80, dte=15, current_price=187,
                           premium_received=3055, cost_to_close=32902, coverage="COVERED")
check("COVERED call, same deep-ITM numbers, DTE=15 (<=21) -> YELLOW",
      covered_near_expiry.color == "YELLOW", f"got {covered_near_expiry.color}")
check("COVERED + YELLOW -> ROLL_CALL_OR_ASSIGN", covered_near_expiry.action == "ROLL_CALL_OR_ASSIGN",
      f"got {covered_near_expiry.action}")

# Same COVERED leg, inside the dte<=7 gamma/pin window -> RED.
covered_pin_risk = leg("OKT", "CALL", strike=80, dte=5, current_price=187,
                        premium_received=3055, cost_to_close=32902, coverage="COVERED")
check("COVERED call, same deep-ITM numbers, DTE=5 (<=7) -> RED (pin risk, not naked loss)",
      covered_pin_risk.color == "RED", f"got {covered_pin_risk.color}")
check("COVERED + RED -> CLOSE_OR_ASSIGN (not CUT_RESTAGGER)",
      covered_pin_risk.action == "CLOSE_OR_ASSIGN", f"got {covered_pin_risk.action}")

# PARTIAL coverage (some contracts covered, uncovered ones carry real risk)
# stays on the NAKED ladder -- same deep-ITM/high-multiple numbers as above
# must still reach RED at dte<=45, unlike the fully-COVERED case.
partial_leg = leg("PRT", "CALL", strike=80, dte=30, current_price=187,
                   premium_received=3055, cost_to_close=32902, coverage="PARTIAL")
check("PARTIAL coverage with dte=30 (<=45) stays on the naked ladder -> RED",
      partial_leg.color == "RED", f"got {partial_leg.color}")
check("PARTIAL + RED -> CUT_RESTAGGER (same as NAKED)", partial_leg.action == "CUT_RESTAGGER",
      f"got {partial_leg.action}")

# The hard-stop DTE-gating extension: same 2.4x multiple as cut_leg above but
# DTE=90 (>45) -> YELLOW/THESIS_WATCH, not RED/CUT_RESTAGGER. This is the
# exact regression this ADR intentionally supersedes (see cut_leg above,
# now fixed at dte=30 to keep testing the still-reachable RED path).
thesis_watch_leg = leg("TWL", "CALL", strike=200, dte=90, current_price=100,
                        premium_received=500, cost_to_close=1200)
check("NAKED, loss multiple 2.4x, DTE=90 (>45 window) -> YELLOW (not RED)",
      thesis_watch_leg.color == "YELLOW", f"got {thesis_watch_leg.color}")
check("past hard-stop but long DTE -> THESIS_WATCH", thesis_watch_leg.action == "THESIS_WATCH",
      f"got {thesis_watch_leg.action}")
check("THESIS_WATCH reason cites the real multiple, DTE, and the Roll Decision Framework",
      "2.4x" in thesis_watch_leg.reason and "90d DTE" in thesis_watch_leg.reason
      and "Roll Decision Framework" in thesis_watch_leg.reason,
      f"got {thesis_watch_leg.reason!r}")

# call_tighten regime demotion must NOT touch a COVERED call -- see
# _apply_call_tighten's ADR 0005 docstring. Same distance_pct/DTE as the
# existing CAUTIOUS_BULL demotion test below (tighten_leg), but COVERED.
covered_tighten_leg = leg_dict("CTGT", "CALL", 106, 90, 100, 500, 400, coverage="COVERED")
covered_cautious_result = assess_portfolio_heat([covered_tighten_leg], "CAUTIOUS_BULL")
check("COVERED call under CAUTIOUS_BULL (call_tighten=True) is NOT demoted to RED",
      covered_cautious_result["counts"]["RED"] == 0, f"got {covered_cautious_result['counts']}")
check("COVERED call under CAUTIOUS_BULL stays GREEN (dte=90, > 21d roll window)",
      covered_cautious_result["counts"]["GREEN"] == 1, f"got {covered_cautious_result['counts']}")

# ---------------------------------------------------------------------------
# LegHeat: UNKNOWN (no live price) -- distinct from "safe"
# ---------------------------------------------------------------------------
print("\nUNKNOWN (no live price)")

no_price_zero = leg("NPZ", "PUT", strike=100, dte=60, current_price=0,
                     premium_received=500, cost_to_close=200)
check("current_price=0 -> UNKNOWN, not GREEN", no_price_zero.color == "UNKNOWN",
      f"got {no_price_zero.color}")
check("UNKNOWN action is NO_PRICE", no_price_zero.action == "NO_PRICE",
      f"got {no_price_zero.action}")
check("UNKNOWN reason explicitly says not to treat as safe",
      "not" in no_price_zero.reason.lower() and "safe" in no_price_zero.reason.lower(),
      f"got {no_price_zero.reason!r}")
check("UNKNOWN leg still computes a stagger re-entry DTE (max(180, dte+75))",
      no_price_zero.stagger_dte == 180, f"got {no_price_zero.stagger_dte}")

no_price_none = leg("NPN", "PUT", strike=100, dte=200, current_price=None,
                     premium_received=500, cost_to_close=200)
check("current_price=None (missing field) -> also UNKNOWN, not a crash",
      no_price_none.color == "UNKNOWN", f"got {no_price_none.color}")
check("UNKNOWN stagger_dte for long-dated leg uses dte+75 (275), not the 180 floor",
      no_price_none.stagger_dte == 275, f"got {no_price_none.stagger_dte}")

# ---------------------------------------------------------------------------
# Edge case: zero premium_received -- does heat_scanner crash or handle it?
# (services.py filters premium<=0 BEFORE calling into heat_scanner.py -- see
# dashboard/backend/app/services.py get_position_heat(), "assess_portfolio_heat
# can't compute loss_multiple against a zero premium". This test proves
# heat_scanner.py's OWN arithmetic also guards the division, so a caller that
# does NOT pre-filter -- e.g. a future direct MCP/test caller -- still gets a
# well-defined zero, not a ZeroDivisionError.)
# ---------------------------------------------------------------------------
print("\nZero premium_received (upstream normally filters this; heat_scanner itself must not crash)")

zero_prem_leg = leg("ZPR", "CALL", strike=110, dte=90, current_price=100,
                     premium_received=0, cost_to_close=100)
check("zero premium does not raise ZeroDivisionError",
      True, "construction above would have raised if unguarded")
check("zero premium -> pnl_pct defined as 0.0 (guarded, not NaN/inf)",
      zero_prem_leg.pnl_pct == 0.0, f"got {zero_prem_leg.pnl_pct}")
check("zero premium -> loss_multiple defined as 0.0 (guarded, not inf)",
      zero_prem_leg.loss_multiple == 0.0, f"got {zero_prem_leg.loss_multiple}")

# ---------------------------------------------------------------------------
# Edge case: a leg dict missing a required field crashes with a clear
# TypeError (not a silent miscalculation) -- documented current behavior.
# ---------------------------------------------------------------------------
print("\nMissing required field -> explicit TypeError, not silent bad data")

incomplete = leg_dict("INC", "CALL", 110, 90, 100, 500, 400)
del incomplete["expiry"]
try:
    LegHeat(**incomplete)
    check("missing 'expiry' field raises TypeError", False, "no exception raised")
except TypeError:
    check("missing 'expiry' field raises TypeError", True)
except Exception as e:  # pragma: no cover - diagnostic only
    check("missing 'expiry' field raises TypeError", False, f"raised {type(e).__name__} instead")

# ---------------------------------------------------------------------------
# assess_portfolio_heat(): zero legs
# ---------------------------------------------------------------------------
print("\nassess_portfolio_heat: zero legs")

empty_result = assess_portfolio_heat([], "BULL")
check("zero legs -> all counts are 0",
      all(v == 0 for v in empty_result["counts"].values()), f"got {empty_result['counts']}")
check("zero legs -> all by_color buckets empty",
      all(len(v) == 0 for v in empty_result["by_color"].values()), f"got {empty_result['by_color']}")
check("zero legs -> protocol reports no RED positions",
      "No RED positions" in empty_result["protocol"], f"got {empty_result['protocol']!r}")
check("zero legs -> top_actions empty", empty_result["top_actions"] == [], f"got {empty_result['top_actions']}")
check("zero legs -> stagger_capacity empty", empty_result["stagger_capacity"] == {},
      f"got {empty_result['stagger_capacity']}")

# ---------------------------------------------------------------------------
# assess_portfolio_heat(): RED sort order + top_actions composition
# ---------------------------------------------------------------------------
print("\nassess_portfolio_heat: RED sort order (loss_multiple desc) + top_actions")

# dte=30 (<=45 RED_DTE_WINDOW) so these stay genuinely RED under ADR 0005 --
# this test is about sort order, not the DTE-gating behavior (see the
# dedicated ADR 0005 section above for that).
red_a = leg_dict("RA", "CALL", 200, 30, 100, 500, 1000)   # mult 2.0
red_b = leg_dict("RB", "CALL", 200, 30, 100, 500, 2500)   # mult 5.0
red_c = leg_dict("RC", "CALL", 200, 30, 100, 500, 1500)   # mult 3.0
yellow_one = leg_dict("YA", "CALL", 120, 90, 100, 500, 750)   # mult 1.5 -> WATCH_CLOSE
green_one = leg_dict("GA", "CALL", 130, 60, 100, 500, 350)    # GREEN

mixed = assess_portfolio_heat([red_a, red_b, red_c, yellow_one, green_one], "BULL")
check("counts: 3 RED, 1 YELLOW, 1 GREEN",
      mixed["counts"]["RED"] == 3 and mixed["counts"]["YELLOW"] == 1 and mixed["counts"]["GREEN"] == 1,
      f"got {mixed['counts']}")
red_symbols = [r["symbol"] for r in mixed["by_color"]["RED"]]
check("RED legs sorted by loss_multiple descending (RB 5.0x, RC 3.0x, RA 2.0x)",
      red_symbols == ["RB", "RC", "RA"], f"got {red_symbols}")
top_action_colors = [a["color"] for a in mixed["top_actions"]]
top_action_symbols = [a["symbol"] for a in mixed["top_actions"]]
check("top_actions = RED (sorted) then YELLOW, GREEN excluded entirely",
      top_action_colors == ["RED", "RED", "RED", "YELLOW"] and top_action_symbols[:3] == ["RB", "RC", "RA"]
      and "GA" not in top_action_symbols,
      f"got colors={top_action_colors} symbols={top_action_symbols}")

# ---------------------------------------------------------------------------
# assess_portfolio_heat(): regime-driven call-tightening demotion
# ---------------------------------------------------------------------------
print("\nassess_portfolio_heat: regime call_tighten demotes near-strike YELLOW calls to RED")

tighten_leg = leg_dict("TGT", "CALL", 106, 90, 100, 500, 400)  # distance 6%, DTE 90 -> YELLOW baseline

bull_result = assess_portfolio_heat([tighten_leg], "BULL")
check("under BULL (call_tighten=False) the leg stays YELLOW",
      bull_result["counts"]["YELLOW"] == 1 and bull_result["counts"]["RED"] == 0,
      f"got {bull_result['counts']}")
bull_action = bull_result["by_color"]["YELLOW"][0]["action"]
check("under BULL its action is the ordinary PREPARE_ROLL",
      bull_action == "PREPARE_ROLL", f"got {bull_action}")

cautious_result = assess_portfolio_heat([tighten_leg], "CAUTIOUS_BULL")
check("under CAUTIOUS_BULL (call_tighten=True), a YELLOW call with <12% cushion is demoted to RED",
      cautious_result["counts"]["RED"] == 1 and cautious_result["counts"]["YELLOW"] == 0,
      f"got {cautious_result['counts']}")
demoted = cautious_result["by_color"]["RED"][0]
check("demoted leg's action becomes ROLL_CALL", demoted["action"] == "ROLL_CALL", f"got {demoted['action']}")
check("demoted leg's reason explains the AI-bull tighten", "AI-bull tighten" in demoted["reason"],
      f"got {demoted['reason']!r}")

# ---------------------------------------------------------------------------
# assess_portfolio_heat(): protocol message variants
# ---------------------------------------------------------------------------
print("\nassess_portfolio_heat: protocol messages")

red_put_leg = leg_dict("RPU", "PUT", 95, 30, 100, 500, 1200)  # mult 2.4 -> RED PUT
protocol_result = assess_portfolio_heat([tighten_leg, red_put_leg], "CAUTIOUS_BULL")
check("scale_back regime with RED call(s) -> protocol tells to pause new strangles",
      "PAUSE new strangles" in protocol_result["protocol"], f"got {protocol_result['protocol']!r}")
check("protocol counts the RED call(s) needing immediate action",
      "call(s) need immediate action" in protocol_result["protocol"],
      f"got {protocol_result['protocol']!r}")
check("protocol separately flags the RED put(s)",
      "1 put(s) need action" in protocol_result["protocol"], f"got {protocol_result['protocol']!r}")

# ---------------------------------------------------------------------------
# ADR 0005: protocol message must not misattribute a COVERED call's own-
# expiry RED/YELLOW state as naked/melt-up risk (previously missing --
# _apply_call_tighten() got this exemption, _build_protocol_message() did
# not).
# ---------------------------------------------------------------------------
print("\nassess_portfolio_heat: COVERED-call RED/YELLOW must not read as naked melt-up risk")

covered_red_leg = leg_dict("CVRD", "CALL", 50, 5, 100, 400, 1800, coverage="COVERED")     # dte<=7 -> RED/CLOSE_OR_ASSIGN
covered_yellow_leg = leg_dict("CVRDY", "CALL", 50, 15, 100, 400, 1800, coverage="COVERED")  # dte<=21 -> YELLOW/ROLL_CALL_OR_ASSIGN

covered_protocol = assess_portfolio_heat([covered_red_leg], "CAUTIOUS_BULL")
check("a COVERED call's own-expiry RED is NOT reported as 'AI melt-up risk'",
      "AI melt-up risk" not in covered_protocol["protocol"], f"got {covered_protocol['protocol']!r}")
check("a book whose only RED leg is a COVERED call still reads 'No RED positions' "
      "(not silent -- by_color['RED'] is non-empty but red_calls/red_puts are both empty)",
      "No RED positions" in covered_protocol["protocol"], f"got {covered_protocol['protocol']!r}")

covered_yellow_protocol = assess_portfolio_heat([covered_yellow_leg], "CAUTIOUS_BULL")
check("a COVERED call's own-expiry YELLOW does not trigger 'PAUSE new strangles'",
      "PAUSE new strangles" not in covered_yellow_protocol["protocol"],
      f"got {covered_yellow_protocol['protocol']!r}")

mixed_protocol = assess_portfolio_heat([covered_red_leg, red_put_leg], "CAUTIOUS_BULL")
check("a COVERED RED call alongside a real RED put: the put is still flagged",
      "1 put(s) need action" in mixed_protocol["protocol"], f"got {mixed_protocol['protocol']!r}")
check("a COVERED RED call alongside a real RED put: no melt-up risk attributed to the covered call",
      "AI melt-up risk" not in mixed_protocol["protocol"], f"got {mixed_protocol['protocol']!r}")

# ---------------------------------------------------------------------------
# assess_portfolio_heat(): stagger_capacity per symbol (calls only)
# ---------------------------------------------------------------------------
print("\nassess_portfolio_heat: stagger_capacity per symbol")

stop_leg = leg_dict("STOPME", "CALL", 200, 30, 100, 500, 1200)      # RED call (dte=30, <=45 window)
full_1 = leg_dict("FULLME", "CALL", 130, 60, 100, 500, 350, expiry="2027-01-01")
full_2 = leg_dict("FULLME", "CALL", 135, 60, 100, 500, 350, expiry="2027-02-01")
full_3 = leg_dict("FULLME", "CALL", 140, 60, 100, 500, 350, expiry="2027-03-01")  # 3 GREEN calls
harvest_first = leg_dict("HARVESTME", "CALL", 125, 90, 100, 500, 200)  # YELLOW (profit target)
open_leg = leg_dict("OPENME", "CALL", 130, 60, 100, 500, 350)          # 1 GREEN call
put_only = leg_dict("PUTSYM", "PUT", 95, 90, 100, 500, 300)            # PUT -- must not appear in stagger_capacity

stagger_result = assess_portfolio_heat(
    [stop_leg, full_1, full_2, full_3, harvest_first, open_leg, put_only], "BULL"
)
sc = stagger_result["stagger_capacity"]
check("RED call symbol gets a STOP capacity message", sc.get("STOPME", "").startswith("STOP"),
      f"got {sc.get('STOPME')!r}")
check("3 GREEN calls on one symbol -> FULL", sc.get("FULLME", "").startswith("FULL"),
      f"got {sc.get('FULLME')!r}")
check("a YELLOW (profit-target) call -> HARVEST_FIRST", sc.get("HARVESTME", "").startswith("HARVEST_FIRST"),
      f"got {sc.get('HARVESTME')!r}")
check("a single GREEN call -> OPEN", sc.get("OPENME", "").startswith("OPEN"), f"got {sc.get('OPENME')!r}")
check("stagger_capacity is calls-only -- PUT-only symbol never appears",
      "PUTSYM" not in sc, f"got keys={list(sc.keys())}")

# ---------------------------------------------------------------------------
# ADR 0005: stagger_capacity must not let a COVERED call block or consume
# naked stagger capacity (previously missing -- same exemption
# _apply_call_tighten()/_build_protocol_message() already have).
# ---------------------------------------------------------------------------
print("\nassess_portfolio_heat: COVERED calls excluded from stagger_capacity entirely")

covered_stagger_result = assess_portfolio_heat([covered_red_leg], "BULL")
check("a COVERED call's own-expiry RED does not block new naked stagger capacity "
      "on the same symbol (the symbol doesn't appear at all -- no naked calls to gate)",
      "CVRD" not in covered_stagger_result["stagger_capacity"],
      f"got {covered_stagger_result['stagger_capacity']}")

# 2 real naked GREEN calls + 1 COVERED GREEN call on the same symbol must
# read as 2 naked slots used (OPEN), not 3 (FULL) -- the covered call must
# not consume naked stagger capacity either.
mixed_stagger_cov = leg_dict("MIXSYM", "CALL", 140, 60, 100, 500, 350, expiry="2027-04-01", coverage="COVERED")
mixed_stagger_naked1 = leg_dict("MIXSYM", "CALL", 130, 60, 100, 500, 350, expiry="2027-01-01")
mixed_stagger_naked2 = leg_dict("MIXSYM", "CALL", 135, 60, 100, 500, 350, expiry="2027-02-01")
mixed_stagger_result = assess_portfolio_heat(
    [mixed_stagger_cov, mixed_stagger_naked1, mixed_stagger_naked2], "BULL"
)
msc = mixed_stagger_result["stagger_capacity"]
check("a COVERED call does not count toward the 3-call stagger FULL cap -- "
      "2 naked + 1 covered reads as 2 naked GREEN calls (OPEN), not FULL",
      msc.get("MIXSYM", "").startswith("OPEN"), f"got {msc.get('MIXSYM')!r}")

# ---------------------------------------------------------------------------
# heat_from_positions(): real Position/OptionLeg objects, zero-premium filter
# ---------------------------------------------------------------------------
print("\nheat_from_positions: Position/OptionLeg wiring + zero-premium filter")

pos = Position(
    symbol="PNL1", account="A", shares=0, stock_cost_basis=0.0, current_price=100.0,
    option_legs=[
        OptionLeg(description="zero prem", strike=110, expiry="2027-06-18",
                   option_type="CALL", quantity=-1, premium_received=0.0,
                   current_mark=50.0, dte=90),
        OptionLeg(description="real leg", strike=130, expiry="2027-06-18",
                   option_type="CALL", quantity=-1, premium_received=500.0,
                   current_mark=350.0, dte=60),
    ],
)
hp_result = heat_from_positions([pos], "BULL")
check("zero-premium_received leg is filtered out (heat_from_positions skips it)",
      hp_result["counts"]["RED"] + hp_result["counts"]["YELLOW"] + hp_result["counts"]["GREEN"]
      + hp_result["counts"]["UNKNOWN"] == 1,
      f"got {hp_result['counts']}")
direct_equiv = assess_portfolio_heat(
    [leg_dict("PNL1", "CALL", 130, 60, 100.0, 500.0, 350.0)], "BULL"
)
check("heat_from_positions' surviving leg matches an equivalent direct assess_portfolio_heat call",
      hp_result["by_color"]["GREEN"][0]["action"] == direct_equiv["by_color"]["GREEN"][0]["action"],
      f"got {hp_result['by_color']['GREEN']} vs {direct_equiv['by_color']['GREEN']}")

# ---------------------------------------------------------------------------
# heat_from_positions(): no open legs -- the fixed crash bug
# ---------------------------------------------------------------------------
print("\nheat_from_positions: no open legs (regression test for the crash fix)")

empty_pos = Position(symbol="NONE1", account="A", shares=100,
                      stock_cost_basis=50.0, current_price=55.0, option_legs=[])
no_legs_result = heat_from_positions([empty_pos], "BULL")
check("no-open-legs result includes the UNKNOWN bucket in by_color (the fixed bug)",
      "UNKNOWN" in no_legs_result["by_color"], f"got keys={list(no_legs_result['by_color'].keys())}")
check("no-open-legs result includes the UNKNOWN count", "UNKNOWN" in no_legs_result["counts"],
      f"got keys={list(no_legs_result['counts'].keys())}")
check("no-open-legs protocol message is the explicit 'no open legs' message",
      no_legs_result["protocol"] == "No open legs to assess.", f"got {no_legs_result['protocol']!r}")

# Before the fix, EITHER of the next two calls raised KeyError: 'UNKNOWN' --
# both are real production call chains (weekly_report.py / monthly_objectives_report.py).
try:
    block = format_heat_block(no_legs_result, "No-Leg Week")
    html = format_heat_html(no_legs_result)
    check("format_heat_block() on a no-open-legs result does not raise", True)
    check("format_heat_html() on a no-open-legs result does not raise", True)
    check("format_heat_block output still reports 0/0/0 counts",
          "0 RED" in block and "0 YELLOW" in block and "0 GREEN" in block, f"got {block!r}")
except KeyError as e:
    check("format_heat_block()/format_heat_html() on a no-open-legs result does not raise", False,
          f"raised KeyError: {e}")

# ---------------------------------------------------------------------------
# format_heat_block / format_heat_html: smoke test against a full, mixed result
# ---------------------------------------------------------------------------
print("\nformat_heat_block / format_heat_html: smoke test over RED/YELLOW/GREEN/UNKNOWN")

full_legs = [red_a, yellow_one, green_one,
             leg_dict("UNK1", "PUT", 100, 60, 0, 500, 200)]  # current_price=0 -> UNKNOWN
full_result = assess_portfolio_heat(full_legs, "BULL")

block_text = format_heat_block(full_result, "Smoke Test Portfolio")
check("format_heat_block runs without raising and returns a non-empty string",
      isinstance(block_text, str) and len(block_text) > 0)
check("format_heat_block includes the RED leg's real action verb (CUT_RESTAGGER)",
      "CUT_RESTAGGER" in block_text, f"block missing CUT_RESTAGGER:\n{block_text}")
check("format_heat_block includes the YELLOW leg's action verb (WATCH_CLOSE)",
      "WATCH_CLOSE" in block_text, f"block missing WATCH_CLOSE:\n{block_text}")
check("format_heat_block surfaces the UNKNOWN bucket with its no-price caveat",
      "UNKNOWN" in block_text and "no price" in block_text.lower(), f"block missing UNKNOWN:\n{block_text}")
check("format_heat_block shows stagger capacity per symbol",
      "Stagger Capacity" in block_text, f"block missing stagger capacity:\n{block_text}")

html_text = format_heat_html(full_result)
check("format_heat_html runs without raising and returns a non-empty string",
      isinstance(html_text, str) and len(html_text) > 0)
check("format_heat_html includes a table row for every assessed leg (RED+YELLOW+GREEN+UNKNOWN=4)",
      html_text.count("<tr style=") == 4, f"got {html_text.count('<tr style=')} rows")
check("format_heat_html includes the RED action verb", "CUT_RESTAGGER" in html_text,
      f"html missing CUT_RESTAGGER:\n{html_text}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
