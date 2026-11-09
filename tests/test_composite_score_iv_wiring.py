"""
Regression tests for mcp/reports/composite_score.py's ADR 0001 step-6
re-wiring: `score_population()` now fetches `real_yields_for_iv =
get_cached_batch_yield(...)` BEFORE building `ctx_by_ticker`, extracts each
ticker's real IV via `_real_iv()` (checks call side then put side), and
passes it as `current_iv=` into `get_cached_symbol_context()` -- instead of
every live caller silently letting iv_rank.get_iv_rank() fall back to its
own HV-proxy. The later `real_yields = get_cached_batch_yield(...)` call was
replaced with `real_yields = real_yields_for_iv` (reuse, not a second
fetch) -- this suite directly tests that "called only once" claim.

Both get_cached_batch_yield and get_cached_symbol_context are mocked here --
this is a pure wiring test (are the right values passed to the right
calls, the right number of times), not a live-data test (that's
tests/test_symbol_context.py's job for symbol_context.py itself, and
tests/test_decision_engine.py's for the scoring formula's own math).

No pytest dependency -- run directly: python3 tests/test_composite_score_iv_wiring.py
"""
import sys
from pathlib import Path
from unittest import mock

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "reports"))
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp"))

import composite_score  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# A minimal scoreable population -- one real ticker, no tail-risk flags,
# built the same way gather_held_rows()/gather_watchlist_rows() would.
raw_rows = [
    composite_score._raw_row(
        "AAA1", yield_pct=10.0, conviction=5.0, target_upside_pct=5.0,
        verticals=[], sector="Technology",
    ),
    composite_score._raw_row(
        "BBB1", yield_pct=8.0, conviction=4.0, target_upside_pct=3.0,
        verticals=[], sector="Industrials",
    ),
]

# AAA1's real IV comes from the CALL side (0.42); BBB1's call side is None
# so it must fall through to the PUT side (0.31) -- exercises both branches
# of _real_iv().
_FAKE_YIELDS = {
    "AAA1": {"call": {"iv": 0.42}, "put": {"iv": 0.40}},
    "BBB1": {"call": {"iv": None}, "put": {"iv": 0.31}},
}

_FAKE_CTX = {"beta": 1.0, "iv_rank": 50.0, "iv_entry_signal": False,
             "dividend_yield_pct": 0.0, "gates_fired": [],
             "market_cap": None, "debt_to_equity": None,
             "profit_margin_pct": None, "analyst_count": None,
             "analyst_rating_mean": None}


def _fake_get_cached_symbol_context(ticker, current_iv=None, **kwargs):
    return dict(_FAKE_CTX)


with mock.patch.object(composite_score, "get_cached_batch_yield",
                        return_value=_FAKE_YIELDS) as mock_batch_yield, \
     mock.patch.object(composite_score, "get_cached_symbol_context",
                        side_effect=_fake_get_cached_symbol_context) as mock_ctx:
    result = composite_score.score_population(
        raw_rows, high_exposure_sectors=set(), sensitivity_confidence="weak", macro_stage="GREEN",
    )

print("get_cached_batch_yield call count")
check("get_cached_batch_yield is called exactly ONCE per score_population() invocation "
      "(reused for real_yields, not fetched a second time)",
      mock_batch_yield.call_count == 1, f"got {mock_batch_yield.call_count} calls")

print("\nget_cached_symbol_context current_iv wiring")

calls_by_ticker = {c.args[0]: c.kwargs.get("current_iv") for c in mock_ctx.call_args_list}
check("get_cached_symbol_context was called for both tickers",
      set(calls_by_ticker.keys()) == {"AAA1", "BBB1"}, f"got {calls_by_ticker}")
check("AAA1 (call-side iv present) passes current_iv=0.42 (the CALL side's real iv, checked first)",
      calls_by_ticker.get("AAA1") == 0.42, f"got {calls_by_ticker.get('AAA1')}")
check("BBB1 (call-side iv is None) falls through to the PUT side, current_iv=0.31",
      calls_by_ticker.get("BBB1") == 0.31, f"got {calls_by_ticker.get('BBB1')}")

print("\nreal_yields reuse -- real_put_yield_pct/real_call_yield_pct still populated from the same fetch")

by_ticker = {r["ticker"]: r for r in result}
# _FAKE_YIELDS entries have no "annualized_yield_pct" key, so these resolve
# to None -- the point here is just that the SAME real_yields_for_iv dict
# feeds these fields (no second, divergent get_cached_batch_yield result).
check("score_population() still populates real_put_yield_pct/real_call_yield_pct fields",
      "real_put_yield_pct" in by_ticker["AAA1"] and "real_call_yield_pct" in by_ticker["AAA1"],
      f"got {by_ticker['AAA1']}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
