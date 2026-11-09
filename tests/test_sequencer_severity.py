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

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
