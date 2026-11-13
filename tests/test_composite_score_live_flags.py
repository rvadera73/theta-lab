"""
Regression test for mcp/reports/composite_score.py's _raw_row() flag
resolution (2026-11-13 fix).

Real bug: _raw_row() determined a ticker's tail-risk/quality flags by
reading screener_universe.py's QUALITY_FLAGS_BY_SYMBOL directly -- a
static, hand-curated dict with NO expiry, completely bypassing
analysis/flags_engine.py's TTL-based live re-evaluation that every OTHER
caller (analysis.strategy_engine.check_flags, used by research_symbol/
scan_sector/run_screener/dry_run_order) already goes through.

Confirmed live 2026-11-13: BE's GOING_CONCERN flag in data/flags_cache.json
was seeded 2026-05-03 with a 30-day TTL (flags_engine.FLAG_TTL_DAYS) --
expired 2026-06-02 -- while screener_universe.py's US_FLAGS_BY_SYMBOL still
hardcodes it with no expiry at all. Real current fundamentals (Q2 2026
revenue +165% YoY, $196M net income to common vs -$43M prior year, raised
FY26 guidance to $3.9-4.2B, $2.49B cash vs $2.60B recourse debt) mean the
live yfinance-based evaluator would never re-plant GOING_CONCERN today --
yet composite_score.py kept BE permanently "tail-risk disqualified" on the
Watchlist five months after the flag should have cleared, because it never
asked the live evaluator at all.

Fix: _raw_row() now calls analysis.strategy_engine.check_flags(ticker) --
the same delegate-to-flags_engine-with-TTL-cache path every other live
caller uses -- instead of reading QUALITY_FLAGS_BY_SYMBOL directly.

No pytest dependency -- run directly: python3 tests/test_composite_score_live_flags.py
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


print("A ticker statically flagged GOING_CONCERN in screener_universe.py "
      "(BE's real registry entry) is NOT disqualified once the live "
      "evaluator reports it clear -- proves _raw_row() consults the live "
      "flags_engine path, not the frozen static dict directly")

with mock.patch.object(composite_score, "check_flags",
                        return_value={"hard_blocks": [], "warnings": ["SPECULATIVE_STORY"]}) as mock_check:
    row = composite_score._raw_row(
        "BE", yield_pct=20.0, conviction=5.0, target_upside_pct=10.0,
        verticals=["Clean Energy"], sector="Industrials",
    )

check("check_flags was called for the real ticker (not bypassed)",
      mock_check.call_args.args == ("BE",), f"got {mock_check.call_args}")
check("BE is NOT tail-risk once the live evaluator clears GOING_CONCERN, "
      "even though screener_universe.py's static registry still lists it",
      row["tail_risk"] is False, f"got tail_risk={row['tail_risk']}")
check("the surviving non-tail warning (SPECULATIVE_STORY) is still carried through",
      row["flags"] == ["SPECULATIVE_STORY"], f"got flags={row['flags']}")

print("\nA genuine, currently-active hard block still disqualifies "
      "(this fix must not make the tail-risk gate toothless)")

with mock.patch.object(composite_score, "check_flags",
                        return_value={"hard_blocks": ["ACCOUNTING_RISK"], "warnings": []}):
    row2 = composite_score._raw_row(
        "ZZZ1", yield_pct=15.0, conviction=3.0, target_upside_pct=-20.0,
        verticals=[], sector="Technology",
    )
check("a real, live-confirmed hard block still sets tail_risk=True",
      row2["tail_risk"] is True, f"got tail_risk={row2['tail_risk']}")

print("\nPERMANENT_EXIT-by-config still disqualifies even with zero live flags "
      "(unchanged pre-existing behavior, not touched by this fix)")

with mock.patch.object(composite_score, "check_flags",
                        return_value={"hard_blocks": [], "warnings": []}):
    row3 = composite_score._raw_row(
        next(iter(composite_score.PERMANENT_EXITS)), yield_pct=5.0, conviction=2.0,
        target_upside_pct=None, verticals=[], sector="Other",
    )
check("a config.PERMANENT_EXITS ticker is still tail-risk with no live flags at all",
      row3["tail_risk"] is True, f"got tail_risk={row3['tail_risk']}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
