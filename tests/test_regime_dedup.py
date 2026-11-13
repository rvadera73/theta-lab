"""
Tests for the regime-dedup Bolt (GitHub issues #60, #55).

Issue #60 -- _get_closes(), _moving_average(), and the bull/bear-signal
classification tree were duplicated character-for-character between
mcp/analysis/regime.py (US) and mcp/analysis/india_regime.py (India). They
are now extracted into mcp/analysis/regime_common.py and both files import
from there instead of defining their own copies.

Issue #55 -- regime.py's module docstring claimed a four-tier VIX
breakpoint scheme ("TRANSITIONING: VIX 20-25", "BEAR_SIDEWAYS: VIX > 25")
that contradicts the real two-threshold config (vix_bull_threshold=20.0,
vix_pause_threshold=35.0; a 20-35 reading is NEUTRAL, not bear-leaning).
The docstring was rewritten; this file does not re-test prose, but the VIX
NEUTRAL-zone case below pins down the real (accurately-documented) behavior
the docstring now describes.

This file proves two things:
  1. regime.py and india_regime.py now share ONE implementation of
     _get_closes / _moving_average / the classification tree -- identity
     checks against regime_common, not just "equal behavior" -- and no
     longer define their own copies in source.
  2. detect_regime() and detect_india_regime() still classify EXACTLY like
     the pre-refactor duplicated code for the same signal combinations --
     every branch of the shared classification tree, plus each market's
     own genuine (preserved, non-shared) difference: US's CAUTIOUS_BULL
     downgrade and India's INDIA_REGIME_OVERRIDE env-var override.

No pytest dependency -- run directly: python3 tests/test_regime_dedup.py
"""
import os
import sys
from pathlib import Path
from unittest import mock

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp"))
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))

import regime  # noqa: E402
import india_regime  # noqa: E402
import regime_common  # noqa: E402
from config import Regime  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# Issue #60: ONE shared implementation, not two copies
# ---------------------------------------------------------------------------
print("\nregime.py and india_regime.py share ONE implementation (issue #60)")

check("regime._get_closes IS regime_common.get_closes (same function object)",
      regime._get_closes is regime_common.get_closes)
check("india_regime._get_closes IS regime_common.get_closes (same function object)",
      india_regime._get_closes is regime_common.get_closes)
check("regime._moving_average IS regime_common.moving_average (same function object)",
      regime._moving_average is regime_common.moving_average)
check("india_regime._moving_average IS regime_common.moving_average (same function object)",
      india_regime._moving_average is regime_common.moving_average)
check("regime.classify_tech_regime IS regime_common.classify_tech_regime (same function object)",
      regime.classify_tech_regime is regime_common.classify_tech_regime)
check("india_regime.classify_tech_regime IS regime_common.classify_tech_regime (same function object)",
      india_regime.classify_tech_regime is regime_common.classify_tech_regime)

_regime_src = (_ROOT / "mcp" / "analysis" / "regime.py").read_text()
_india_src = (_ROOT / "mcp" / "analysis" / "india_regime.py").read_text()
check("regime.py source no longer defines its own _get_closes",
      "def _get_closes" not in _regime_src)
check("india_regime.py source no longer defines its own _get_closes",
      "def _get_closes" not in _india_src)
check("regime.py source no longer defines its own _moving_average",
      "def _moving_average" not in _regime_src)
check("india_regime.py source no longer defines its own _moving_average",
      "def _moving_average" not in _india_src)
check("regime.py source imports from regime_common",
      "from regime_common import" in _regime_src)
check("india_regime.py source imports from regime_common",
      "from regime_common import" in _india_src)

# Genuine, non-shared differences must still be local to each file.
check("regime.py still has its own CAUTIOUS_BULL downgrade logic",
      "CAUTIOUS_BULL" in _regime_src and "caution_reasons" in _regime_src)
check("india_regime.py still has its own env-var trader override",
      "INDIA_REGIME_OVERRIDE" in _india_src)
_common_src = (_ROOT / "mcp" / "analysis" / "regime_common.py").read_text()
check("regime_common.py does NOT implement the CAUTIOUS_BULL downgrade itself (US-only logic)",
      "caution_reasons" not in _common_src and "Regime.CAUTIOUS_BULL" not in _common_src)
check("regime_common.py does NOT implement the env-var override itself (India-only logic)",
      "os.getenv" not in _common_src and "os.environ" not in _common_src)


# ---------------------------------------------------------------------------
# regime_common.classify_tech_regime(): full classification tree
# ---------------------------------------------------------------------------
print("\nregime_common.classify_tech_regime(): full classification tree")

_tree_cases = [
    (3, 0, Regime.BULL, "bull>=3 and bear==0 -> BULL"),
    (5, 0, Regime.BULL, "bull>3 and bear==0 -> still BULL"),
    (5, 3, Regime.BEAR_SIDEWAYS, "bear>=3 -> BEAR_SIDEWAYS even with high bull_signals"),
    (0, 3, Regime.BEAR_SIDEWAYS, "bear>=3, bull=0 -> BEAR_SIDEWAYS"),
    (2, 0, Regime.TRANSITIONING, "bull>bear, bull<3, bear==0 -> TRANSITIONING"),
    (2, 1, Regime.TRANSITIONING, "bull>bear, bull<3, bear>0 -> TRANSITIONING"),
    (3, 1, Regime.TRANSITIONING, "bull>=3 but bear!=0 falls through to bull>bear -> TRANSITIONING"),
    (1, 1, Regime.BEAR_SIDEWAYS, "bull==bear -> else branch -> BEAR_SIDEWAYS"),
    (0, 0, Regime.BEAR_SIDEWAYS, "no signals at all -> else branch -> BEAR_SIDEWAYS"),
    (1, 2, Regime.BEAR_SIDEWAYS, "bear>bull, bear<3 -> else branch -> BEAR_SIDEWAYS"),
]
for bull, bear, expected, label in _tree_cases:
    got = regime_common.classify_tech_regime(bull, bear)
    check(f"classify_tech_regime({bull}, {bear}) -> {expected.value}  [{label}]",
          got == expected, f"got {got}")


# ---------------------------------------------------------------------------
# regime_common.get_closes() / moving_average()
# ---------------------------------------------------------------------------
print("\nregime_common.get_closes() / moving_average()")


class _FakeColumn:
    def __init__(self, values):
        self._values = values

    def tolist(self):
        return self._values


class _FakeFrame:
    def __init__(self, values):
        self._values = values

    def __getitem__(self, key):
        assert key == "Close"
        return _FakeColumn(self._values)


class _FakeTicker:
    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, period="1y"):
        return _FakeFrame([1.0, 2.0, 3.0, 4.0, 5.0])


def _raiser(symbol):
    raise RuntimeError("network down")


with mock.patch.object(regime_common.yf, "Ticker", _FakeTicker):
    closes = regime_common.get_closes("TEST", "1y")
check("get_closes() returns the Close column as a list",
      closes == [1.0, 2.0, 3.0, 4.0, 5.0], f"got {closes}")

with mock.patch.object(regime_common.yf, "Ticker", _raiser):
    closes_err = regime_common.get_closes("TEST", "1y")
check("get_closes() returns [] on any fetch error instead of raising",
      closes_err == [], f"got {closes_err}")

check("moving_average() returns 0.0 when there isn't enough history yet",
      regime_common.moving_average([1.0, 2.0], 5) == 0.0)
check("moving_average() averages exactly `window` closes",
      regime_common.moving_average([1.0, 2.0, 3.0, 4.0, 5.0], 5) == 3.0)
check("moving_average() uses only the LAST `window` closes, not earlier ones",
      regime_common.moving_average([100.0, 1.0, 2.0, 3.0], 3) == 2.0)


# ---------------------------------------------------------------------------
# Helpers to build deterministic closes series with exact target
# current/MA50/MA200 (or current/5-day-avg) values, so detect_regime() /
# detect_india_regime() behavior can be pinned down exactly.
# ---------------------------------------------------------------------------

def _vix_series(current, avg5=None):
    """5+ closes whose last value is `current` and whose last-5 average is
    `avg5` (defaults to a flat VIX, i.e. avg5 == current)."""
    if avg5 is None:
        avg5 = current
    other = (avg5 * 5 - current) / 4
    return [other, other, other, other, current]


def _index_series(current, ma50, ma200):
    """200 closes whose last value is `current`, whose last-50 average is
    `ma50`, and whose full (last-200) average is `ma200`."""
    last49 = (ma50 * 50 - current) / 49
    first150 = (ma200 * 200 - ma50 * 50) / 150
    return [first150] * 150 + [last49] * 49 + [current]


def _approx(a, b, tol=1e-6):
    return abs(a - b) < tol


# ---------------------------------------------------------------------------
# detect_regime() (US) -- behavior preserved across every branch
# ---------------------------------------------------------------------------
print("\ndetect_regime() (US): behavior preserved across every branch")

_US_CASES = [
    dict(
        label="clean BULL: VIX low+flat, SPX above both MAs, not stretched -> BULL (no caution)",
        vix=_vix_series(current=10.0, avg5=10.0),
        spx=_index_series(current=4100.0, ma50=4000.0, ma200=3900.0),
        expected_technical=Regime.BULL,
        expected_final=Regime.BULL,
    ),
    dict(
        label="BULL technicals but VIX 16-20 -> CAUTIOUS_BULL downgrade",
        vix=_vix_series(current=18.0, avg5=18.0),
        spx=_index_series(current=4100.0, ma50=4000.0, ma200=3900.0),
        expected_technical=Regime.BULL,
        expected_final=Regime.CAUTIOUS_BULL,
    ),
    dict(
        label="BULL technicals + VIX<16 but SPX >12% above 200d MA -> CAUTIOUS_BULL downgrade",
        vix=_vix_series(current=10.0, avg5=10.0),
        spx=_index_series(current=4600.0, ma50=4500.0, ma200=4000.0),
        expected_technical=Regime.BULL,
        expected_final=Regime.CAUTIOUS_BULL,
    ),
    dict(
        label="VIX NEUTRAL zone (20-35, issue #55's real behavior) + MA bull -> TRANSITIONING",
        vix=_vix_series(current=25.0, avg5=25.0),
        spx=_index_series(current=4100.0, ma50=4000.0, ma200=3900.0),
        expected_technical=Regime.TRANSITIONING,
        expected_final=Regime.TRANSITIONING,
    ),
    dict(
        label="VIX>35 bear + SPX below both MAs -> BEAR_SIDEWAYS",
        vix=_vix_series(current=40.0, avg5=40.0),
        spx=_index_series(current=3800.0, ma50=4000.0, ma200=4100.0),
        expected_technical=Regime.BEAR_SIDEWAYS,
        expected_final=Regime.BEAR_SIDEWAYS,
    ),
    dict(
        label="VIX bull (+1) vs MA MIXED (+1 bear) tie -> else branch -> BEAR_SIDEWAYS",
        vix=_vix_series(current=10.0, avg5=10.0),
        spx=_index_series(current=4000.0, ma50=3950.0, ma200=4100.0),
        expected_technical=Regime.BEAR_SIDEWAYS,
        expected_final=Regime.BEAR_SIDEWAYS,
    ),
]

for case in _US_CASES:
    def _fake_get_closes(symbol, period="1y", _case=case):
        if symbol == "^VIX":
            return _case["vix"]
        if symbol == "^GSPC":
            return _case["spx"]
        raise AssertionError(f"unexpected symbol {symbol}")

    with mock.patch.object(regime, "_get_closes", side_effect=_fake_get_closes):
        result = regime.detect_regime()

    check(f"[US] {case['label']} -- technical_regime",
          result["technical_regime"] == case["expected_technical"].value,
          f"got {result['technical_regime']}, full={result}")
    check(f"[US] {case['label']} -- regime (final)",
          result["regime"] == case["expected_final"].value,
          f"got {result['regime']}, full={result}")


# ---------------------------------------------------------------------------
# detect_india_regime() -- behavior preserved, India's own thresholds/override
# ---------------------------------------------------------------------------
print("\ndetect_india_regime(): behavior preserved, India-specific override intact")

_INDIA_CASES = [
    dict(
        label="India VIX low+flat, Nifty above both MAs -> BULL, no override",
        vix=_vix_series(current=10.0, avg5=10.0),
        nifty=_index_series(current=21000.0, ma50=20500.0, ma200=20000.0),
        override=None,
        expected_technical=Regime.BULL,
        expected_final=Regime.BULL,
    ),
    dict(
        label="India VIX neutral zone (15-25) + Nifty bull -> TRANSITIONING",
        vix=_vix_series(current=20.0, avg5=20.0),
        nifty=_index_series(current=21000.0, ma50=20500.0, ma200=20000.0),
        override=None,
        expected_technical=Regime.TRANSITIONING,
        expected_final=Regime.TRANSITIONING,
    ),
    dict(
        label="India VIX>25 bear + Nifty below both MAs -> BEAR_SIDEWAYS",
        vix=_vix_series(current=30.0, avg5=30.0),
        nifty=_index_series(current=19000.0, ma50=20000.0, ma200=20500.0),
        override=None,
        expected_technical=Regime.BEAR_SIDEWAYS,
        expected_final=Regime.BEAR_SIDEWAYS,
    ),
    dict(
        label="Technical BULL but INDIA_REGIME_OVERRIDE=BEAR_SIDEWAYS forces override",
        vix=_vix_series(current=10.0, avg5=10.0),
        nifty=_index_series(current=21000.0, ma50=20500.0, ma200=20000.0),
        override="BEAR_SIDEWAYS",
        expected_technical=Regime.BULL,
        expected_final=Regime.BEAR_SIDEWAYS,
    ),
]

for case in _INDIA_CASES:
    def _fake_get_closes(symbol, period="1y", _case=case):
        if symbol == "^INDIAVIX":
            return _case["vix"]
        if symbol == "^NSEI":
            return _case["nifty"]
        raise AssertionError(f"unexpected symbol {symbol}")

    env = {"INDIA_REGIME_OVERRIDE": case["override"]} if case["override"] else {"INDIA_REGIME_OVERRIDE": ""}
    with mock.patch.object(india_regime, "_get_closes", side_effect=_fake_get_closes), \
         mock.patch.dict(os.environ, env):
        result = india_regime.detect_india_regime()

    check(f"[India] {case['label']} -- technical_regime",
          result["technical_regime"] == case["expected_technical"].value,
          f"got {result['technical_regime']}, full={result}")
    check(f"[India] {case['label']} -- regime (final)",
          result["regime"] == case["expected_final"].value,
          f"got {result['regime']}, full={result}")

# India's own rule: new_entries_allowed = final_regime != BEAR_SIDEWAYS.
# Re-run the BEAR_SIDEWAYS case to check that flag specifically.
with mock.patch.object(india_regime, "_get_closes",
                        side_effect=lambda symbol, period="1y": (
                            _INDIA_CASES[2]["vix"] if symbol == "^INDIAVIX" else _INDIA_CASES[2]["nifty"]
                        )), \
     mock.patch.dict(os.environ, {"INDIA_REGIME_OVERRIDE": ""}):
    _bear_result = india_regime.detect_india_regime()
check("India new_entries_allowed is False when final regime is BEAR_SIDEWAYS",
      _bear_result["new_entries_allowed"] is False, f"got {_bear_result}")


print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
