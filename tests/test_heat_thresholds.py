"""
Regression test for Bolt b11: mcp/config.py HEAT_THRESHOLDS "yellow" fix.

Prior bug: HEAT_THRESHOLDS["yellow"] was set equal to HEAT_THRESHOLDS["red"]
(0.08) for both "call" and "put", instead of sitting between "green" (0.15)
and "red" (0.08) as the inline comments in mcp/config.py describe. That made
heat_scanner.py's LegHeat.__post_init__ distance-driven YELLOW branch
(`elif self.distance_pct < yellow_dist:`) unreachable dead code: anything
with distance_pct < 0.08 was already consumed by the RED / "time is working"
YELLOW branches above it in the if/elif chain, so a comparison against a
yellow threshold equal to 0.08 could never fire. Net effect: a leg with
8-11.5% cushion to strike, no profit/loss trigger, and DTE > 21 incorrectly
reported GREEN instead of the documented YELLOW "prepare to roll/harvest"
state.

This test proves two things directly against the real call path
(LegHeat.__post_init__ in mcp/analysis/heat_scanner.py), not just the raw
config values:
  (a) HEAT_THRESHOLDS["yellow"] (call and put) is now strictly between
      "red" and "green" -- not equal to either.
  (b) A synthetic leg whose distance_pct falls inside the new yellow band
      actually classifies as YELLOW (with action PREPARE_ROLL) via LegHeat,
      for both CALL and PUT legs.

No pytest dependency -- run directly: python3 tests/test_heat_thresholds.py
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp"))

from config import HEAT_THRESHOLDS  # noqa: E402
from heat_scanner import LegHeat, LegContract, LegPricing  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def leg(symbol, option_type, strike, dte, current_price, premium_received,
        cost_to_close, expiry="2027-06-18"):
    return LegHeat(
        contract=LegContract(symbol=symbol, option_type=option_type, strike=strike,
                              expiry=expiry),
        pricing=LegPricing(premium_received=premium_received,
                            cost_to_close=cost_to_close, current_price=current_price),
        dte=dte,
    )


# ---------------------------------------------------------------------------
# (a) HEAT_THRESHOLDS["yellow"] sits strictly between "red" and "green"
# ---------------------------------------------------------------------------
print("HEAT_THRESHOLDS: yellow is a real midpoint, not a copy of red")

for side in ("call", "put"):
    thresholds = HEAT_THRESHOLDS[side]
    green, yellow, red = thresholds["green"], thresholds["yellow"], thresholds["red"]

    check(f"{side}: yellow ({yellow}) != red ({red})", yellow != red,
          f"yellow equals red -- the copy-paste bug is back")
    check(f"{side}: yellow ({yellow}) != green ({green})", yellow != green,
          f"yellow equals green")
    check(f"{side}: red ({red}) < yellow ({yellow}) < green ({green})",
          red < yellow < green,
          f"got red={red}, yellow={yellow}, green={green} -- not strictly ordered")

check("call and put yellow thresholds match (symmetric by design)",
      HEAT_THRESHOLDS["call"]["yellow"] == HEAT_THRESHOLDS["put"]["yellow"],
      f"call={HEAT_THRESHOLDS['call']['yellow']} put={HEAT_THRESHOLDS['put']['yellow']}")

check("yellow is the documented midpoint 0.115 between green (0.15) and red (0.08)",
      HEAT_THRESHOLDS["call"]["yellow"] == 0.115,
      f"got {HEAT_THRESHOLDS['call']['yellow']}")

# ---------------------------------------------------------------------------
# (b) A leg inside the new yellow band actually classifies YELLOW via LegHeat
# ---------------------------------------------------------------------------
print("\nLegHeat: a leg inside the new yellow band classifies YELLOW end-to-end")

red_dist = HEAT_THRESHOLDS["call"]["red"]
yellow_dist = HEAT_THRESHOLDS["call"]["yellow"]
# Midpoint of the band itself, e.g. (0.08, 0.115) -> ~0.0975 cushion.
band_mid_pct = (red_dist + yellow_dist) / 2

# CALL: stock price such that distance_pct == band_mid_pct, well inside
# 21+ DTE, no profit-target or loss-multiple trigger -- isolates the
# distance-driven YELLOW branch specifically.
call_strike = 100.0
call_price = call_strike / (1 + band_mid_pct)
call_leg = leg("YBC", "CALL", strike=call_strike, dte=90, current_price=call_price,
               premium_received=500, cost_to_close=400)
check(f"CALL leg with distance_pct={call_leg.distance_pct:.4f} (inside ({red_dist}, {yellow_dist}) "
      "band) -> YELLOW", call_leg.color == "YELLOW", f"got {call_leg.color}")
check("CALL leg in the yellow band -> PREPARE_ROLL action",
      call_leg.action == "PREPARE_ROLL", f"got {call_leg.action}")

# PUT: symmetric construction -- stock above the put strike by band_mid_pct.
put_strike = 100.0
put_price = put_strike * (1 + band_mid_pct)
put_leg = leg("YBP", "PUT", strike=put_strike, dte=90, current_price=put_price,
              premium_received=500, cost_to_close=400)
check(f"PUT leg with distance_pct={put_leg.distance_pct:.4f} (inside ({red_dist}, {yellow_dist}) "
      "band) -> YELLOW", put_leg.color == "YELLOW", f"got {put_leg.color}")
check("PUT leg in the yellow band -> PREPARE_ROLL action",
      put_leg.action == "PREPARE_ROLL", f"got {put_leg.action}")

# Sanity boundary check: just inside red (distance_pct just under red_dist,
# DTE <= 45) still classifies RED -- proves the fix did not touch the red
# boundary itself.
just_red_price = call_strike / (1 + (red_dist - 0.005))
just_red_leg = leg("JRD", "CALL", strike=call_strike, dte=30, current_price=just_red_price,
                    premium_received=500, cost_to_close=400)
check("sanity: distance just inside red_dist with DTE<=45 is still RED (red boundary untouched)",
      just_red_leg.color == "RED", f"got {just_red_leg.color}")

# Sanity boundary check: just outside yellow (distance_pct just above
# yellow_dist), no other trigger, DTE > 21 -> GREEN, proving the yellow band
# has a real upper edge rather than swallowing everything.
just_green_price = call_strike / (1 + (yellow_dist + 0.005))
just_green_leg = leg("JGR", "CALL", strike=call_strike, dte=90, current_price=just_green_price,
                      premium_received=500, cost_to_close=400)
check("sanity: distance just outside yellow_dist, no other trigger, DTE>21 -> GREEN",
      just_green_leg.color == "GREEN", f"got {just_green_leg.color}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
