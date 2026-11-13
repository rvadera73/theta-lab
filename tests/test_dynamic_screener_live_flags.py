"""
Regression test for mcp/reports/dynamic_screener.py's _score_candidate()
live hard-block check (2026-11-13 fix, GitHub issue #49).

Real bug: _score_candidate() -- behind the LIVE run_screener/
screen_new_entries MCP tools, which can hand back an active ENTER_NOW
recommendation -- only ever excluded a ticker via `symbol in
PERMANENT_EXITS` (config.py's hardcoded 4-name list: MRNA, PYPL, SMCI,
INMD). It never called analysis.strategy_engine.check_flags /
analysis.flags_engine.check_flags_live, and never consulted
screener_universe.py's QUALITY_FLAGS_BY_SYMBOL registry at all -- static
or live. A ticker carrying a real hard-block flag (ACCOUNTING_RISK/
DELISTING_RISK/GOING_CONCERN/HALTED/PERMANENT_EXIT) in the flag registry,
but not separately hand-added to PERMANENT_EXITS, could get an active
ENTER_NOW recommendation from the live screener with zero flag check --
worse than the sibling composite_score.py bug fixed in PR #47 (that one
over-blocked a ranking display by reading a FROZEN static dict; this one
under-blocked a live buy recommendation by reading nothing at all).

Fix: _score_candidate() now also calls analysis.strategy_engine.check_flags
(the same live, TTL-cached path composite_score.py's _raw_row() uses as of
#47, and research_symbol/scan_sector/run_screener/dry_run_order already
used) early, and excludes any ticker with a non-empty "hard_blocks" list the
SAME way it already excludes a PERMANENT_EXITS ticker (returns None, so the
candidate never enters the ranked/returned population at all).
PERMANENT_EXITS is kept as an additional, redundant, config-driven check --
not removed, not the only check anymore.

No pytest dependency -- run directly: python3 tests/test_dynamic_screener_live_flags.py
"""
import sys
from pathlib import Path
from unittest import mock

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "reports"))
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp"))

import dynamic_screener  # noqa: E402
import factor_screener  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def _meta(symbol, sector="Tech", tier=2, preferred_strategy="CSP"):
    return {
        "symbol": symbol,
        "sector": sector,
        "tier": tier,
        "preferred_strategy": preferred_strategy,
        "min_capital": 5000,
        "notes": "test entry",
        "flags": [],
    }


_CLEAN_SNAPSHOT = {"current": 150.0, "rsi": 45.0, "pct_off_high": -10.0}
_IV_LOOKUP = {"ZFLAG1": {"iv_rank": 50.0, "iv_pct": 50.0, "current_iv": 0.30},
              "ZCLEAN1": {"iv_rank": 50.0, "iv_pct": 50.0, "current_iv": 0.30}}


def _call(symbol, hard_blocks, sector="Tech", in_permanent_exits_lookup=None):
    """Runs _score_candidate for `symbol` with check_flags mocked to return
    `hard_blocks`, and every other live dependency (technical_snapshot,
    upcoming_earnings, the factor_screener fundamentals path) mocked/forced
    out so the test is deterministic and makes no network calls -- only the
    hard-block exclusion path under test is live."""
    meta = _meta(symbol, sector=sector)
    iv_lookup = _IV_LOOKUP if in_permanent_exits_lookup is None else in_permanent_exits_lookup
    with mock.patch.object(dynamic_screener, "check_flags",
                           return_value={"hard_blocks": hard_blocks, "warnings": []}) as mock_check, \
         mock.patch.object(dynamic_screener, "technical_snapshot", return_value=dict(_CLEAN_SNAPSHOT)), \
         mock.patch.object(dynamic_screener, "upcoming_earnings", return_value=[]), \
         mock.patch.object(factor_screener, "get_factors", side_effect=Exception("no network in test")):
        result = dynamic_screener._score_candidate(
            meta, regime="BULL", current_symbols=[], heavy_sectors=[], india=False, iv_lookup=iv_lookup,
        )
    return result, mock_check


print("A ticker NOT in PERMANENT_EXITS but with a mocked live hard_block "
      "from check_flags is excluded -- the SAME way a PERMANENT_EXITS "
      "ticker already was, proving _score_candidate() now consults the "
      "live flag evaluator at all (it never did before this fix)")

result1, mock_check1 = _call("ZFLAG1", hard_blocks=["ACCOUNTING_RISK"])
check("check_flags was called for the real, non-exempt ticker",
      mock_check1.call_args is not None and mock_check1.call_args.args == ("ZFLAG1",),
      f"got {mock_check1.call_args}")
check("a ticker with a live hard_block is excluded (returns None), "
      "matching PERMANENT_EXITS treatment",
      result1 is None, f"got {result1}")

print("\nA clean ticker (check_flags reports no hard_blocks) with no other "
      "exclusion reason still scores normally -- this fix must not make "
      "the screener toothless for everything")

result2, mock_check2 = _call("ZCLEAN1", hard_blocks=[])
check("check_flags was called for the clean ticker too",
      mock_check2.call_args is not None and mock_check2.call_args.args == ("ZCLEAN1",),
      f"got {mock_check2.call_args}")
check("a clean ticker is NOT excluded (returns a candidate dict)",
      result2 is not None, f"got {result2}")
if result2 is not None:
    check("the clean ticker's candidate dict carries the expected symbol",
          result2.get("symbol") == "ZCLEAN1", f"got {result2.get('symbol')}")
    check("the clean ticker scores ENTER_NOW under these favorable mocked "
          "conditions (IVR 50, BULL regime, Tech sector, no earnings)",
          result2.get("signal") == "ENTER_NOW", f"got signal={result2.get('signal')}")

print("\nPERMANENT_EXITS-by-config tickers are still excluded even when "
      "check_flags reports zero live flags -- unchanged pre-existing "
      "behavior, not touched by this fix (config.PERMANENT_EXITS stays as "
      "an additional, redundant check)")

exit_symbol = next(iter(dynamic_screener.PERMANENT_EXITS))
result3, mock_check3 = _call(exit_symbol, hard_blocks=[])
check(f"a config.PERMANENT_EXITS ticker ({exit_symbol}) is still excluded "
      "with zero live flags at all",
      result3 is None, f"got {result3}")
check("check_flags was never even called for a PERMANENT_EXITS ticker "
      "(the config check still short-circuits first, as before)",
      not mock_check3.called, f"call_args={mock_check3.call_args}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
