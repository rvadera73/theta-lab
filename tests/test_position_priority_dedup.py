"""
Regression tests for the Bolt that fixed GitHub issue #61: three duplicated
functions across mcp/reports/weekly_report.py, mcp/reports/india_weekly_report.py,
and mcp/analysis/pnl.py (`_dte_label`, the shared prefix of `_priority`, and
`_dte_from_expiry`) are now extracted into mcp/analysis/position_priority.py.

This file proves three things:
  1. The extracted shared module (`_dte_label`, `priority_prefix`,
     `_dte_from_expiry`) behaves exactly like the original duplicated code,
     branch by branch, using lightweight duck-typed stub positions so every
     branch (including the roll-threshold MONITOR branch, which is currently
     unreachable through real config -- see note below) is independently
     exercisable regardless of mcp/config.py's real thresholds.
  2. weekly_report.py's `_priority()` (US) and india_weekly_report.py's
     `_priority()` (India) -- now both thin wrappers around the shared
     `priority_prefix()` plus their own market-specific fallback -- still
     produce the exact same (priority, label, reason) tuples real Position/
     OptionLeg objects and mcp/config.py's REAL thresholds produced before
     this refactor (the loss-flag/DTE-urgency/profit-target/permanent-exit/
     WEAK/EXTENDED/final-WATCH paths, for both markets).
  3. The module is genuinely SHARED, not copy-pasted into a third location:
     weekly_report.py, india_weekly_report.py, and pnl.py all reference the
     exact same function objects from analysis.position_priority (`is`
     identity, not just equal behavior).

No pytest dependency -- run directly: python3 tests/test_position_priority_dedup.py
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "reports"))
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp"))

import weekly_report  # noqa: E402
import india_weekly_report  # noqa: E402
from analysis.pnl import Position, OptionLeg  # noqa: E402
from analysis import position_priority as pp  # noqa: E402
from analysis import pnl as pnl_module  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# 1a. _dte_label() -- all four label bands, at and off each boundary
# ---------------------------------------------------------------------------
print("position_priority._dte_label()")

check("dte=7 (URGENT boundary) -> URGENT band",
      pp._dte_label(7) == "⚠️ 7d — URGENT", pp._dte_label(7))
check("dte=8 (just past URGENT) -> act-soon band",
      pp._dte_label(8) == "🔶 8d — act soon", pp._dte_label(8))
check("dte=21 (act-soon boundary) -> act-soon band",
      pp._dte_label(21) == "🔶 21d — act soon", pp._dte_label(21))
check("dte=22 (just past act-soon) -> watch band",
      pp._dte_label(22) == "🟡 22d — watch", pp._dte_label(22))
check("dte=45 (watch boundary) -> watch band",
      pp._dte_label(45) == "🟡 45d — watch", pp._dte_label(45))
check("dte=46 (just past watch) -> plain green band",
      pp._dte_label(46) == "🟢 46d", pp._dte_label(46))
check("dte=0 -> URGENT band (not a crash)",
      pp._dte_label(0) == "⚠️ 0d — URGENT", pp._dte_label(0))

# ---------------------------------------------------------------------------
# 1b. _dte_from_expiry() -- future/past/garbage
# ---------------------------------------------------------------------------
print("\nposition_priority._dte_from_expiry()")
from datetime import date, timedelta  # noqa: E402

_today = date(2026, 11, 13)
_future = (_today + timedelta(days=10)).isoformat()
_past = (_today - timedelta(days=5)).isoformat()

check("future expiry computes a positive DTE",
      pp._dte_from_expiry(_future, _today) == 10, pp._dte_from_expiry(_future, _today))
check("past expiry computes a negative DTE (not clamped to 0)",
      pp._dte_from_expiry(_past, _today) == -5, pp._dte_from_expiry(_past, _today))
check("garbage expiry string returns 0 instead of crashing",
      pp._dte_from_expiry("not-a-date", _today) == 0)
check("None expiry returns 0 instead of crashing",
      pp._dte_from_expiry(None, _today) == 0)


# ---------------------------------------------------------------------------
# 2. priority_prefix() -- every branch, via duck-typed stubs (independent of
#    mcp/config.py's real thresholds, so this pins the BRANCH ORDER itself).
# ---------------------------------------------------------------------------
print("\nposition_priority.priority_prefix() -- branch coverage via stubs")


class _StubLeg:
    def __init__(self, dte):
        self.dte = dte


class _StubPosition:
    """Duck-typed stand-in for analysis.pnl.Position -- only implements the
    surface priority_prefix() actually touches (option_legs + the three
    signal methods), so every branch can be driven independently of real
    loss_flag()/profit_take_signal()/roll_signal() threshold math."""

    def __init__(self, option_legs=None, loss=None, profit=None, roll=None):
        self.option_legs = option_legs or []
        self._loss = loss if loss is not None else {"flag": False}
        self._profit = profit if profit is not None else {"signal": False}
        self._roll = roll if roll is not None else {"signal": False}

    def loss_flag(self):
        return self._loss

    def profit_take_signal(self, regime_str):
        return self._profit

    def roll_signal(self):
        return self._roll


r = pp.priority_prefix(
    _StubPosition(option_legs=[_StubLeg(30)], loss={"flag": True, "multiplier": 2.5}),
    "BEAR_SIDEWAYS",
)
check("loss flag wins regardless of DTE/profit/roll",
      r == (1, "URGENT", "Mark 2.5x premium — flag and review"), r)

r = pp.priority_prefix(_StubPosition(option_legs=[_StubLeg(5)]), "BEAR_SIDEWAYS")
check("leg DTE <= 7 (no loss flag) -> priority 1 URGENT, expiry-specific reason",
      r == (1, "URGENT", "Expires in 5 days — decide now"), r)

r = pp.priority_prefix(_StubPosition(option_legs=[_StubLeg(15)]), "BEAR_SIDEWAYS")
check("leg DTE in (7, 21] -> priority 2 URGENT, within-21-DTE reason",
      r == (2, "URGENT", "Within 21 DTE — roll or close"), r)

r = pp.priority_prefix(
    _StubPosition(option_legs=[_StubLeg(30)], profit={"signal": True, "pct_captured": 55}),
    "BEAR_SIDEWAYS",
)
check("profit signal (DTE > 21, no loss) -> priority 2 REVIEW",
      r == (2, "REVIEW", "At profit target (55% captured)"), r)

r = pp.priority_prefix(
    _StubPosition(option_legs=[_StubLeg(30)], roll={"signal": True}), "BEAR_SIDEWAYS",
)
check("roll signal (DTE > 21, no loss/profit) -> priority 3 MONITOR "
      "(this exact combination is unreachable through real mcp/config.py "
      "thresholds today, since roll_dte_threshold == the inline 21-DTE "
      "check above it -- preserved here as a real, independently-testable "
      "branch of the original code, unchanged by this refactor)",
      r == (3, "MONITOR", "Approaching roll threshold"), r)

r = pp.priority_prefix(_StubPosition(option_legs=[_StubLeg(30)]), "BEAR_SIDEWAYS")
check("no condition matches -> None (caller continues with its own checks)",
      r is None, r)

r = pp.priority_prefix(_StubPosition(option_legs=[]), "BEAR_SIDEWAYS")
check("no option legs at all, no signals -> None",
      r is None, r)


# ---------------------------------------------------------------------------
# 3. weekly_report._priority() (US) -- real Position/OptionLeg + real
#    mcp/config.py thresholds, end to end through the shared module.
# ---------------------------------------------------------------------------
print("\nweekly_report._priority() -- US, real Position + real config")


def _pos(symbol, legs=None, shares=0):
    return Position(symbol=symbol, account="A", shares=shares,
                     stock_cost_basis=0.0, current_price=100.0,
                     option_legs=legs or [])


def _leg(dte, premium_received=0.0, current_mark=0.0, option_type="PUT", strike=100.0):
    return OptionLeg(description="", strike=strike, expiry="2099-01-01",
                      option_type=option_type, quantity=-1,
                      premium_received=premium_received, current_mark=current_mark,
                      dte=dte)


pos = _pos("ZZZZ", legs=[_leg(dte=60, premium_received=1000.0, current_mark=2500.0)])
pri = weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("US: mark 2.5x premium -> loss flag wins (priority 1 URGENT)",
      pri == (1, "URGENT", "Mark 2.5x premium — flag and review"), pri)

pos = _pos("ZZZZ", legs=[_leg(dte=5)])
pri = weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("US: leg expires in 5 days -> priority 1 URGENT",
      pri == (1, "URGENT", "Expires in 5 days — decide now"), pri)

pos = _pos("ZZZZ", legs=[_leg(dte=15)])
pri = weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("US: leg at 15 DTE -> priority 2 URGENT (within 21 DTE)",
      pri == (2, "URGENT", "Within 21 DTE — roll or close"), pri)

pos = _pos("ZZZZ", legs=[_leg(dte=30, premium_received=1000.0, current_mark=400.0)])
pri = weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("US: 60% of max premium captured (BEAR_SIDEWAYS target 40-50%) -> priority 2 REVIEW",
      pri == (2, "REVIEW", "At profit target (60.0% captured)"), pri)

pos = _pos("MRNA", legs=[_leg(dte=30, premium_received=1000.0, current_mark=800.0)])
pri = weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("US: MRNA (real config.PERMANENT_EXITS entry), no other signal -> priority 2 REVIEW, permanent-exit reason",
      pri == (2, "REVIEW", "On permanent exit list — accelerate exit"), pri)

pos = _pos("NOT_ON_ANY_LIST", legs=[_leg(dte=30, premium_received=1000.0, current_mark=800.0)])
pri = weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("US: no signal, not a permanent exit -> final fallback priority 5 WATCH",
      pri == (5, "WATCH", "No immediate action needed"), pri)


# ---------------------------------------------------------------------------
# 4. india_weekly_report._priority() -- India-specific layer (permanent
#    exits + WEAK/EXTENDED verdicts) on top of the same shared prefix.
# ---------------------------------------------------------------------------
print("\nindia_weekly_report._priority() -- India, real Position + real config")

pos = _pos("RELIANCE", legs=[_leg(dte=60, premium_received=1000.0, current_mark=2500.0)])
pri = india_weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("India: mark 2.5x premium -> loss flag wins (priority 1 URGENT), same as US",
      pri == (1, "URGENT", "Mark 2.5x premium — flag and review"), pri)

pos = _pos("RELIANCE", legs=[_leg(dte=5)])
pri = india_weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("India: leg expires in 5 days -> priority 1 URGENT, same as US",
      pri == (1, "URGENT", "Expires in 5 days — decide now"), pri)

# India's real INDIA_PERMANENT_EXITS is empty in mcp/config.py today -- add a
# symbol to the live module attribute for this one check, then restore it,
# so this exercises India's OWN permanent-exit branch (not the US one) with
# zero risk of leaking state into any other test/process.
_orig_india_exits = india_weekly_report.INDIA_PERMANENT_EXITS
india_weekly_report.INDIA_PERMANENT_EXITS = ["INDIATC"]
try:
    pos = _pos("INDIATC", legs=[_leg(dte=30, premium_received=1000.0, current_mark=800.0)])
    pri = india_weekly_report._priority(pos, "BEAR_SIDEWAYS")
    check("India: symbol on INDIA_PERMANENT_EXITS, no other signal -> priority 2 REVIEW",
          pri == (2, "REVIEW", "On permanent exit list — accelerate exit"), pri)
finally:
    india_weekly_report.INDIA_PERMANENT_EXITS = _orig_india_exits

# _verdict_reason() (routines/india_us_evening_report.py) reads a few keys
# unconditionally (heat_reason/rsi/position_52w) -- a minimal real-shaped
# metrics dict, not an empty one, to exercise it without crashing.
_metrics = {"heat_reason": "neutral", "rsi": 50.0, "position_52w": 40.0}

pos = _pos("WEAKCO", legs=[_leg(dte=30, premium_received=1000.0, current_mark=800.0)])
pos._verdict = "WEAK"
pos._conviction_metrics = _metrics
pri = india_weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("India: WEAK verdict (no other signal, not a permanent exit) -> priority 4, label WEAK",
      pri[0] == 4 and pri[1] == "WEAK" and isinstance(pri[2], str), pri)

pos = _pos("EXTCO", legs=[_leg(dte=30, premium_received=1000.0, current_mark=800.0)])
pos._verdict = "EXTENDED"
pos._conviction_metrics = _metrics
pri = india_weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("India: EXTENDED verdict -> priority 5, label EXTENDED (not the generic WATCH reason)",
      pri[0] == 5 and pri[1] == "EXTENDED" and isinstance(pri[2], str), pri)

pos = _pos("PLAINCO", legs=[_leg(dte=30, premium_received=1000.0, current_mark=800.0)])
pri = india_weekly_report._priority(pos, "BEAR_SIDEWAYS")
check("India: no signal, no verdict, not a permanent exit -> final fallback priority 5 WATCH",
      pri == (5, "WATCH", "No immediate action needed"), pri)


# ---------------------------------------------------------------------------
# 5. Genuinely shared, not copy-pasted: both report modules AND pnl.py
#    reference the exact same function objects from the new module.
# ---------------------------------------------------------------------------
print("\nShared-module identity (not copy-pasted into a third location)")

check("weekly_report.priority_prefix IS position_priority.priority_prefix",
      weekly_report.priority_prefix is pp.priority_prefix)
check("india_weekly_report.priority_prefix IS position_priority.priority_prefix",
      india_weekly_report.priority_prefix is pp.priority_prefix)
check("weekly_report._dte_label IS position_priority._dte_label",
      weekly_report._dte_label is pp._dte_label)
check("india_weekly_report._dte_label IS position_priority._dte_label",
      india_weekly_report._dte_label is pp._dte_label)
check("india_weekly_report._dte_from_expiry IS position_priority._dte_from_expiry",
      india_weekly_report._dte_from_expiry is pp._dte_from_expiry)
check("pnl._dte_from_expiry IS position_priority._dte_from_expiry "
      "(pnl.py's own broker parsers import the shared implementation too)",
      pnl_module._dte_from_expiry is pp._dte_from_expiry)


# ---------------------------------------------------------------------------
if failures:
    print(f"\n{len(failures)} check(s) FAILED:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

print("\nAll checks passed.")
