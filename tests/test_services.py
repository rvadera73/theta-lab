"""
Characterization tests for dashboard/backend/app/services.py (Bolt b16).

services.py had ZERO test coverage before this file despite being the thin
JSON-reshaping layer every dashboard route (main.py), the cache refresh cycle
(cache.py), the priority sequencer (sequencer.py), the ledger sync
(ledger.py), and the leg_decisions MCP tool (mcp/analysis/leg_decisions_tool.py)
all depend on. These tests pin down the REAL current behavior of the
functions this Bolt is about to refactor for Code Quality Gate compliance
(get_composite_scores, get_position_heat, get_today_plan,
get_cash_margin_forecast, analyze_watchlist_symbol), plus light coverage of
the surrounding thin wrappers, BEFORE any refactor -- run against the
CURRENT, unmodified code and confirmed green first.

Every heavy external dependency (live Yahoo/network fetches, the ~90s
UnifiedReportProduction reload, sqlite account_state, the real 8-account
position loader) is mocked at the real module boundary -- this suite never
hits the network, never touches the real DATA_ROOT, and never calls the real
report engine. Where services.py does a LOCAL import inside a function body
(e.g. `from composite_score import compute_composite_scores`), that import
re-reads the attribute off the already-imported module object at call time,
so patching the real module's attribute (mock.patch.object(composite_score,
"compute_composite_scores", ...)) is what actually takes effect -- same
pattern tests/test_composite_score_iv_wiring.py and
tests/test_sequencer_severity.py already use.

get_position_heat's fixture (below) is deliberately built to exercise a real,
previously-undetected behavior: _annotate()'s "collapse duplicate
cross-account contract" logic (services.py's own comment: "Collapse to one
row per colliding key") computes a deduped list but then DISCARDS it --
`_annotate(color_rows)` and `_annotate(result.get("top_actions", []))` never
assign the return value back anywhere. A duplicate row landing in the SAME
color bucket as its sibling is NOT removed from the final output; it is left
in place without the merged annotation fields (no "covered"/"account"/
"sector"/etc.), which means it falls into its own "(symbol, None)"
position-group downstream. This is a pre-existing characterization of
CURRENT behavior (confirmed by reading the source, not assumed) --
preserved as-is by this refactor's scope (behavior preservation, not a bug
hunt), and flagged in the PR description for follow-up.

ADR 0005 UPDATE (2026-11-12): this fixture's AAPL $200 CALL collision (fully
COVERED in account A via its 100 shares, NAKED in account B which holds none)
now lands in TWO DIFFERENT color buckets -- GREEN for A's copy (coverage now
bypasses the naked ladder entirely), RED for B's copy -- since coverage is
computed per-POSITION/per-account (real, confirmed behavior: coverage
doesn't cross accounts), not from the merged display annotation. Each
bucket's dedup pass only ever sees ONE occurrence of this key, so both
copies get fully annotated here; the "bare duplicate in the same bucket"
characterization above is still true of the dedup function itself (and still
real), just no longer demonstrated by THIS specific fixture now that the two
colliding rows score differently. See the updated assertions below.

No pytest dependency -- run directly: python3 tests/test_services.py
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest import mock

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

from app import services  # noqa: E402
from app import account_state  # noqa: E402
from app import sequencer  # noqa: E402
from app import watchlist  # noqa: E402
import composite_score  # noqa: E402
import realized_performance  # noqa: E402
import report_utils  # noqa: E402
import regime  # noqa: E402
import symbol_context  # noqa: E402
import decision_engine  # noqa: E402
import accounts_config  # noqa: E402
import enhanced_metrics  # noqa: E402
import iv_rank  # noqa: E402
import premium_yield  # noqa: E402
import trend_verticals  # noqa: E402
import sector_analysis  # noqa: E402
from pnl import Position, OptionLeg  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# _to_native
# ---------------------------------------------------------------------------
print("_to_native() -- numpy/pandas scalar -> plain Python recursive conversion")

import numpy as np  # noqa: E402

nested = {
    "a": np.float64(3.25),
    "b": [np.int64(7), {"c": np.float64(1.5)}],
    "d": (np.int64(2), "plain"),
    "e": "unchanged",
}
converted = services._to_native(nested)
check("numpy float64 nested in a dict becomes a plain python float",
      type(converted["a"]) is float and converted["a"] == 3.25, f"got {converted['a']!r} ({type(converted['a'])})")
check("numpy int64 nested inside a list becomes a plain python int",
      type(converted["b"][0]) is int and converted["b"][0] == 7, f"got {converted['b'][0]!r}")
check("numpy scalar nested inside a dict nested inside a list is converted too",
      type(converted["b"][1]["c"]) is float and converted["b"][1]["c"] == 1.5, f"got {converted['b'][1]['c']!r}")
check("tuples are converted into a list, element-wise",
      converted["d"] == [2, "plain"] and type(converted["d"][0]) is int, f"got {converted['d']!r}")
check("plain strings pass through unchanged", converted["e"] == "unchanged", f"got {converted['e']!r}")

# ---------------------------------------------------------------------------
# get_account_status
# ---------------------------------------------------------------------------
print("\nget_account_status() -- reshapes _compute_account_status() + converts numpy")

_fake_status = {
    "Account A (232)": {"cash": np.float64(45000.0), "equity_pct": np.float64(62.5)},
    "Account B (901)": {"cash": np.float64(12000.0), "equity_pct": np.float64(80.0)},
}
_fake_gen = mock.Mock()
_fake_gen._compute_account_status.return_value = _fake_status

with mock.patch.object(services, "_get_generator", return_value=_fake_gen):
    result = services.get_account_status()

check("returns one row per account, each carrying its own 'account' name",
      [r["account"] for r in result] == ["Account A (232)", "Account B (901)"], f"got {result}")
check("each row flattens the account's own dict fields alongside 'account'",
      result[0]["cash"] == 45000.0 and result[0]["equity_pct"] == 62.5, f"got {result[0]}")
check("numpy floats from _compute_account_status are converted to plain python floats",
      type(result[0]["cash"]) is float, f"got {type(result[0]['cash'])}")

# ---------------------------------------------------------------------------
# get_composite_scores
# ---------------------------------------------------------------------------
print("\nget_composite_scores() -- merges watchlist notes + splits realized perf into "
      "top performers / losses / no-activity")

_fake_composite = {
    "held": [
        {"ticker": "AAPL", "rank": 1, "score": 2.5, "conviction": 8, "conviction_rank": 1,
         "yield_pct": 12.0, "yield_rank": 2, "flags": [], "tail_risk": "low"},
        {"ticker": "MSFT", "rank": 2, "score": 1.8, "conviction": 6, "conviction_rank": 3,
         "yield_pct": 9.0, "yield_rank": 4, "flags": ["EARNINGS_RISK"], "tail_risk": "medium"},
        {"ticker": "GOOGL", "rank": 5, "score": 0.9, "conviction": 4, "conviction_rank": 5,
         "yield_pct": 3.0, "yield_rank": 6, "flags": [], "tail_risk": None},
        {"ticker": "IBM"},  # no rank at all -- exercises the "unranked sorts last" branch
    ],
    "watchlist": [
        {"ticker": "DELL", "is_new": True, "rank": 3, "score": 1.2},
    ],
    "regime": "CAUTIOUS_BULL",
    "macro_stage": "GREEN",
    "severity_smoothed": 0.3,
    "high_exposure_sectors": ["Technology"],
    "sensitivity_confidence": "confirmed",
}
_fake_tracked_watchlist = [{"symbol": "DELL", "notes": "watching for entry"}]
_fake_realized = {
    "cutoff": "2026-08-12",
    "ranked": [("AAPL", 500.0, 3), ("MSFT", -200.0, 2)],
}

with mock.patch.object(services, "_get_generator", return_value=mock.Mock()), \
     mock.patch.object(composite_score, "compute_composite_scores", return_value=_fake_composite) as mock_compute, \
     mock.patch.object(watchlist, "list_watchlist", return_value=_fake_tracked_watchlist) as mock_watchlist, \
     mock.patch.object(realized_performance, "realized_pnl_by_ticker", return_value=_fake_realized) as mock_realized:
    cs = services.get_composite_scores()

check("compute_composite_scores was handed the tracked watchlist's own tickers",
      mock_compute.call_args.args[1] == ["DELL"], f"got {mock_compute.call_args}")
check("list_watchlist was called with tracked_only=True",
      mock_watchlist.call_args.kwargs.get("tracked_only") is True or mock_watchlist.call_args.args == (True,),
      f"got {mock_watchlist.call_args}")
check("held/watchlist/regime/macro_stage pass through unmodified",
      cs["held"] == _fake_composite["held"] and cs["regime"] == "CAUTIOUS_BULL" and cs["macro_stage"] == "GREEN",
      f"got held={cs['held']}, regime={cs['regime']}")
check("the tracked watchlist's real notes are merged onto the matching composite watchlist row",
      cs["watchlist"][0]["notes"] == "watching for entry", f"got {cs['watchlist'][0]}")
check("realized_cutoff passes through from realized_pnl_by_ticker(days=90) unchanged",
      cs["realized_cutoff"] == "2026-08-12" and mock_realized.call_args.kwargs.get("days") == 90,
      f"got cutoff={cs['realized_cutoff']}, call={mock_realized.call_args}")

top = {r["ticker"]: r for r in cs["realized_top_performers_90d"]}
check("realized_top_performers_90d has one row per ranked ticker, carrying its real composite fields",
      top["AAPL"]["realized_pnl_90d"] == 500.0 and top["AAPL"]["composite_rank"] == 1
      and top["AAPL"]["composite_score"] == 2.5 and top["AAPL"]["conviction"] == 8,
      f"got {top.get('AAPL')}")
check("a negative-pnl ticker still appears in top performers (it's realized, not filtered there)",
      "MSFT" in top and top["MSFT"]["realized_pnl_90d"] == -200.0, f"got {top.get('MSFT')}")

check("realized_losses_90d contains exactly the tickers with pnl < 0",
      [r["ticker"] for r in cs["realized_losses_90d"]] == ["MSFT"], f"got {cs['realized_losses_90d']}")

no_activity_tickers = [r["ticker"] for r in cs["realized_no_activity_90d"]]
check("realized_no_activity_90d contains exactly the held tickers absent from realized['ranked']",
      set(no_activity_tickers) == {"GOOGL", "IBM"}, f"got {no_activity_tickers}")
check("no_activity is sorted best-composite-rank-first, with an unranked ticker (IBM, no 'rank' key) sorting last",
      no_activity_tickers == ["GOOGL", "IBM"], f"got {no_activity_tickers}")
check("a no-activity row reports realized_pnl_90d=0.0 / closed_count_90d=0, not a missing/None value",
      cs["realized_no_activity_90d"][0]["realized_pnl_90d"] == 0.0
      and cs["realized_no_activity_90d"][0]["closed_count_90d"] == 0,
      f"got {cs['realized_no_activity_90d'][0]}")

# ---------------------------------------------------------------------------
# get_position_heat -- the big one. See module docstring for the fixture's
# deliberate cross-account collision + zero-premium-skip + strangle-pairing
# design, and the discovered "duplicate row never actually removed" behavior.
# ---------------------------------------------------------------------------
print("\nget_position_heat() -- coverage/strangle/cross-account annotate, sector rollup, position grouping")


def _fake_symbol_context(symbol, **kwargs):
    sectors = {"AAPL": "Technology", "MSFT": "Communication Services"}
    return {
        "sector": sectors.get(symbol), "gates_fired": [],
        "dividend_rate": 0.5, "next_ex_dividend_date": "2026-12-01",
        "current_iv": 0.3,
    }


def _fake_extended_hours(symbol, price):
    return {"live_price": price, "live_price_source": "regular_close",
            "overnight_move_pct": 0.0, "gates_fired": []}


def _build_fixture_positions():
    aapl_a = Position(
        symbol="AAPL", account="A", shares=100, stock_cost_basis=150.0, current_price=190.0,
        option_legs=[
            OptionLeg(description="AAPL 200C", strike=200.0, expiry="2026-12-18", option_type="CALL",
                      quantity=-1, premium_received=5.0, current_mark=3.0, dte=40),
            OptionLeg(description="AAPL 205C", strike=205.0, expiry="2026-12-18", option_type="CALL",
                      quantity=-1, premium_received=4.0, current_mark=2.5, dte=40),
            OptionLeg(description="AAPL 180P", strike=180.0, expiry="2026-12-18", option_type="PUT",
                      quantity=-1, premium_received=3.0, current_mark=1.0, dte=40),
        ],
    )
    # Same exact contract (AAPL $200 CALL exp 2026-12-18) held in a SECOND
    # account with zero covering shares -- the real cross-account collision
    # case services.py's own comments describe (confirmed real case: NVO
    # $40C 03/19/2027 in two accounts).
    aapl_b = Position(
        symbol="AAPL", account="B", shares=0, stock_cost_basis=0.0, current_price=190.0,
        option_legs=[
            OptionLeg(description="AAPL 200C (acct B)", strike=200.0, expiry="2026-12-18", option_type="CALL",
                      quantity=-1, premium_received=5.0, current_mark=3.0, dte=40),
        ],
    )
    msft_a = Position(
        symbol="MSFT", account="A", shares=0, stock_cost_basis=0.0, current_price=350.0,
        option_legs=[
            OptionLeg(description="MSFT 300P", strike=300.0, expiry="2027-01-15", option_type="PUT",
                      quantity=-1, premium_received=2.0, current_mark=0.5, dte=100),
        ],
    )
    # Zero premium -- assess_portfolio_heat "can't compute loss_multiple
    # against a zero premium" -- must be excluded entirely, never reach
    # context/legs/cost_to_close_by_key at all.
    tgt_a = Position(
        symbol="TGT", account="A", shares=0, stock_cost_basis=0.0, current_price=140.0,
        option_legs=[
            OptionLeg(description="TGT 150C zero-prem", strike=150.0, expiry="2026-11-20", option_type="CALL",
                      quantity=-1, premium_received=0.0, current_mark=1.0, dte=10),
        ],
    )
    return [aapl_a, aapl_b, msft_a, tgt_a]


async def _fake_load_us_positions():
    return {
        "positions": _build_fixture_positions(),
        "account_sources": {
            "A": {"source": "schwab_api", "as_of": "2026-11-09", "days_stale": 0},
            "B": {"source": "csv_export", "as_of": "2026-11-05", "days_stale": 4},
        },
    }


with mock.patch.object(report_utils, "load_us_positions", _fake_load_us_positions), \
     mock.patch.object(report_utils, "extended_hours_context", side_effect=_fake_extended_hours), \
     mock.patch.object(regime, "detect_regime", return_value={"regime": "CAUTIOUS_BULL"}), \
     mock.patch.object(symbol_context, "get_cached_symbol_context", side_effect=_fake_symbol_context):
    heat = services.get_position_heat()

check("regime threads through from regime.detect_regime()", heat["regime"] == "CAUTIOUS_BULL", f"got {heat['regime']}")
check("the zero-premium TGT leg never reaches the heat engine at all (excluded, not zeroed)",
      heat["counts"]["RED"] + heat["counts"]["YELLOW"] + heat["counts"]["GREEN"] + heat["counts"]["UNKNOWN"] == 5,
      f"got counts={heat['counts']}")
# ADR 0005: AAPL/A's $200 CALL is now fully COVERED (A's 100 shares back its
# 1 contract) -> GREEN/HOLD_TO_ASSIGNMENT, no longer RED. 3 of the 5 real
# legs land RED (205 CALL naked + 180 PUT cash-secured, both close-to-strike
# DTE<=45; 200 CALL naked in account B, same strike-proximity math); 1
# (MSFT put, deep OTM + profit target) lands YELLOW; 1 (the covered 200
# CALL) lands GREEN.
check("3 of 5 real legs RED, 1 (MSFT put) YELLOW, 1 (AAPL/A's covered 200 CALL) GREEN",
      heat["counts"]["RED"] == 3 and heat["counts"]["YELLOW"] == 1 and heat["counts"]["GREEN"] == 1,
      f"got {heat['counts']}")

red_rows = heat["by_color"]["RED"]
green_rows = heat["by_color"]["GREEN"]
check("the colliding AAPL $200 CALL no longer produces a same-bucket duplicate -- "
      "account A's copy (COVERED) and account B's copy (NAKED) now score into DIFFERENT "
      "color buckets, so each bucket's dedup pass sees only one occurrence of this key "
      "and fully annotates it (the pre-existing 'bare duplicate' bug -- see module "
      "docstring -- is real but not exercised by this particular collision any more)",
      len(red_rows) == 3 and len(green_rows) == 1, f"got RED={len(red_rows)} GREEN={len(green_rows)}")

aapl_200_red = next(r for r in red_rows if r["symbol"] == "AAPL" and r["strike"] == 200.0)
check("account B's $200 CALL copy: scored NAKED (0 covering shares in B) -> RED/ROLL_CALL",
      aapl_200_red["coverage"] == "NAKED" and aapl_200_red["action"] == "ROLL_CALL",
      f"got {aapl_200_red}")
check("account B's copy still gets the POOLED display annotation across both accounts "
      "(1 of 2 contracts covered overall, conservative AND-combine -- a known, accepted "
      "cosmetic mismatch against its own GREEN sibling's coverage, out of this Bolt's scope)",
      aapl_200_red["covered"] is False and aapl_200_red["covered_contracts"] == 1
      and aapl_200_red["total_contracts"] == 2 and aapl_200_red["multi_account_contract"] is True
      and aapl_200_red["account"] == "A+B",
      f"got {aapl_200_red}")

aapl_200_green = green_rows[0]
check("account A's $200 CALL copy: scored COVERED (A's 100 shares fully back it) -> "
      "GREEN/HOLD_TO_ASSIGNMENT, the ADR 0005 behavior this test exists to prove",
      aapl_200_green["symbol"] == "AAPL" and aapl_200_green["strike"] == 200.0
      and aapl_200_green["coverage"] == "COVERED" and aapl_200_green["action"] == "HOLD_TO_ASSIGNMENT",
      f"got {aapl_200_green}")
check("the GREEN copy ALSO gets the same pooled display annotation (same key, same context entry)",
      aapl_200_green["covered"] is False and aapl_200_green["covered_contracts"] == 1
      and aapl_200_green["total_contracts"] == 2 and aapl_200_green["account"] == "A+B",
      f"got {aapl_200_green}")

aapl_205_row = next(r for r in red_rows if r["symbol"] == "AAPL" and r["strike"] == 205.0)
check("the non-colliding AAPL $205 CALL (2nd contract, no covering shares left) is correctly "
      "scored NAKED and annotated naked",
      aapl_205_row["coverage"] == "NAKED" and aapl_205_row["covered"] is False
      and aapl_205_row["covered_contracts"] == 0 and aapl_205_row["total_contracts"] == 1
      and aapl_205_row["account"] == "A",
      f"got {aapl_205_row}")

aapl_put_row = next(r for r in red_rows if r["symbol"] == "AAPL" and r["strike"] == 180.0)
check("a short PUT scores CASH_SECURED_PUT, and its display 'covered' is still None "
      "(not a meaningful concept for puts), not False/True",
      aapl_put_row["coverage"] == "CASH_SECURED_PUT" and aapl_put_row["covered"] is None,
      f"got {aapl_put_row}")
check("the put is correctly marked strangle=True (paired with AAPL/A's own calls, same expiry)",
      aapl_put_row["strangle"] is True, f"got {aapl_put_row}")

msft_row = heat["by_color"]["YELLOW"][0]
check("MSFT's put (single account, no collision) is fully annotated with its own sector",
      msft_row["sector"] == "Communication Services" and msft_row["account"] == "A", f"got {msft_row}")

sr = heat["sector_rollup"]
check("sector_rollup buckets all 3 Technology RED rows together, GREEN counted separately",
      sr["Technology"]["RED"] == 3 and sr["Technology"]["GREEN"] == 1, f"got {sr}")
check("Technology's RED cost-to-close sums the 3 RED legs' unique contract keys "
      "(205 CALL 2.5 + 200 CALL[[B's key, shared with A's now-GREEN copy]] 3.0 + 180 PUT 1.0) -- "
      "unchanged from before ADR 0005 since the rollup already summed by unique key, not row count",
      sr["Technology"]["red_cost_to_close"] == 6.5, f"got {sr['Technology']}")
check("Communication Services (MSFT, YELLOW) never contributes to any RED cost-to-close total",
      sr["Communication Services"]["red_cost_to_close"] == 0.0 and sr["Communication Services"]["YELLOW"] == 1,
      f"got {sr['Communication Services']}")

positions = heat["positions"]
groups_by_key = {(p["symbol"], p["account"]): p for p in positions}
check("grouping is by (symbol, account) -- 3 groups now (no more phantom (AAPL, None) group: "
      "both colliding rows got the same 'A+B' merged account annotation, in different colors, "
      "so they group TOGETHER rather than one falling into an unannotated phantom group)",
      set(groups_by_key.keys()) == {("AAPL", "A"), ("AAPL", "A+B"), ("MSFT", "A")},
      f"got {sorted(groups_by_key.keys(), key=str)}")
check("the (AAPL, 'A') group collects the 205 CALL and 180 PUT -- is_stagger True, "
      "naked_leg_count 1 (just the naked 205 CALL), worst_color RED",
      groups_by_key[("AAPL", "A")]["leg_count"] == 2 and groups_by_key[("AAPL", "A")]["is_stagger"] is True
      and groups_by_key[("AAPL", "A")]["naked_leg_count"] == 1
      and groups_by_key[("AAPL", "A")]["worst_color"] == "RED",
      f"got {groups_by_key[('AAPL', 'A')]}")
check("the (AAPL, 'A+B') group now holds BOTH colliding 200 CALL copies (one RED/NAKED, "
      "one GREEN/COVERED) -- worst_color is RED (the group's worst leg wins), naked_leg_count "
      "2 because that field still reads the OLD pooled 'covered' display annotation (False for "
      "both rows), not the new per-leg 'coverage' scoring field -- a known, accepted divergence "
      "between the two, out of this Bolt's scope",
      groups_by_key[("AAPL", "A+B")]["leg_count"] == 2 and groups_by_key[("AAPL", "A+B")]["worst_color"] == "RED"
      and groups_by_key[("AAPL", "A+B")]["naked_leg_count"] == 2,
      f"got {groups_by_key[('AAPL', 'A+B')]}")
check("positions are ordered worst-color-first -- both RED AAPL groups ahead of the YELLOW MSFT group",
      [p["symbol"] for p in positions][-1] == "MSFT" and positions[-1]["worst_color"] == "YELLOW",
      f"got {[(p['symbol'], p['account'], p['worst_color']) for p in positions]}")

# Empty-book edge case: must hit the early "no legs at all" return shape exactly.
async def _fake_load_empty():
    return {"positions": [], "account_sources": {}}


with mock.patch.object(report_utils, "load_us_positions", _fake_load_empty), \
     mock.patch.object(regime, "detect_regime", return_value={"regime": "BULL"}):
    empty_heat = services.get_position_heat()

check("an empty book returns the exact documented empty shape (all 4 color buckets present, zero counts)",
      empty_heat == {"by_color": {"RED": [], "YELLOW": [], "GREEN": [], "UNKNOWN": []},
                      "counts": {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0},
                      "regime": "BULL", "top_actions": []},
      f"got {empty_heat}")

# ---------------------------------------------------------------------------
# get_position_heat() -- SAME-bucket cross-account collision (both copies
# NAKED, unlike the AAPL $200 CALL fixture above where coverage differs and
# the two copies land in different buckets). Real bug found 2026-11-12: the
# un-annotated duplicate (no "account" field at all) stayed in by_color
# instead of being dropped, forming a phantom (symbol, None) position-group
# that leaked into get_leg_decisions() -> decision_engine, double-counting
# the same real contract's dollars in the portfolio rollup. Confirmed real,
# recurring collision pattern (NVO $40C, 2026-10-15), not hypothetical.
# ---------------------------------------------------------------------------
print("\nget_position_heat() -- same-bucket cross-account collision (identical naked "
      "contract in two accounts) is deduplicated, not left as a phantom duplicate")


def _build_same_bucket_collision_positions():
    # Same strike/price/premium/mark/dte as the AAPL/A 205C leg above
    # (already proven RED by that test) -- reused here to avoid re-deriving
    # the threshold math, just on a different symbol/accounts to isolate
    # this collision from the AAPL fixture above.
    msft_naked_a = Position(
        symbol="MSFT", account="A", shares=0, stock_cost_basis=0.0, current_price=190.0,
        option_legs=[
            OptionLeg(description="MSFT 205C (acct A)", strike=205.0, expiry="2026-12-18", option_type="CALL",
                      quantity=-1, premium_received=4.0, current_mark=2.5, dte=40),
        ],
    )
    msft_naked_c = Position(
        symbol="MSFT", account="C", shares=0, stock_cost_basis=0.0, current_price=190.0,
        option_legs=[
            OptionLeg(description="MSFT 205C (acct C)", strike=205.0, expiry="2026-12-18", option_type="CALL",
                      quantity=-1, premium_received=4.0, current_mark=2.5, dte=40),
        ],
    )
    return [msft_naked_a, msft_naked_c]


async def _fake_load_same_bucket_collision():
    return {
        "positions": _build_same_bucket_collision_positions(),
        "account_sources": {
            "A": {"source": "schwab_api", "as_of": "2026-11-09", "days_stale": 0},
            "C": {"source": "schwab_api", "as_of": "2026-11-09", "days_stale": 0},
        },
    }


with mock.patch.object(report_utils, "load_us_positions", _fake_load_same_bucket_collision), \
     mock.patch.object(report_utils, "extended_hours_context", side_effect=_fake_extended_hours), \
     mock.patch.object(regime, "detect_regime", return_value={"regime": "CAUTIOUS_BULL"}), \
     mock.patch.object(symbol_context, "get_cached_symbol_context", side_effect=_fake_symbol_context):
    collision_heat = services.get_position_heat()

check("both copies score RED individually (heat_scanner has no account concept, "
      "scores each leg on its own merits) -- counts reflects the raw per-leg scoring",
      collision_heat["counts"]["RED"] == 2, f"got {collision_heat['counts']}")
collision_red_rows = collision_heat["by_color"]["RED"]
check("the SAME-bucket collision is deduplicated to exactly ONE row, not left as a "
      "bare/un-annotated duplicate",
      len(collision_red_rows) == 1, f"got {len(collision_red_rows)} rows: {collision_red_rows}")
check("the surviving row carries the merged multi-account annotation (account='A+C'), "
      "proving it's the real, fully-annotated row, not a leftover bare one",
      collision_red_rows[0].get("account") == "A+C" and collision_red_rows[0].get("multi_account_contract") is True,
      f"got {collision_red_rows[0]}")

collision_positions = collision_heat["positions"]
collision_keys = {(p["symbol"], p["account"]) for p in collision_positions}
check("exactly one MSFT position-group exists, keyed by the merged 'A+C' account -- "
      "no phantom (MSFT, None) group from the dropped duplicate",
      collision_keys == {("MSFT", "A+C")}, f"got {collision_keys}")

collision_decisions = services.get_leg_decisions(heat=collision_heat)["decisions"]
check("decision_engine receives exactly ONE MSFT record for this real contract held "
      "across 2 accounts -- not two, which would double-count its premium/margin in "
      "the portfolio rollup",
      len(collision_decisions) == 1 and collision_decisions[0]["symbol"] == "MSFT",
      f"got {len(collision_decisions)} decisions: {collision_decisions}")

# ---------------------------------------------------------------------------
# get_leg_decisions
# ---------------------------------------------------------------------------
print("\nget_leg_decisions() -- projects get_position_heat()'s legs through decision_engine, "
      "reuses a passed-in heat instead of reloading")

_heat_fixture = {
    "positions": [
        {"symbol": "OKTA", "account": "A", "legs": [{"id": "leg1"}]},
        {"symbol": "ZS", "account": "A", "legs": [{"id": "leg2"}, {"id": "leg3"}]},
    ],
}
_fake_decisions = [mock.Mock(to_dict=mock.Mock(return_value={"id": lid})) for lid in ("leg1", "leg2", "leg3")]
_fake_rollup = {"total_margin_estimate": 1234.5, "concentration_gates": []}

with mock.patch.object(decision_engine, "build_decisions", return_value=_fake_decisions) as mock_build, \
     mock.patch.object(decision_engine, "portfolio_rollup", return_value=_fake_rollup) as mock_rollup, \
     mock.patch.object(services, "get_position_heat") as mock_get_heat:
    out = services.get_leg_decisions(heat=_heat_fixture)

check("a passed-in 'heat' is reused -- get_position_heat() is NOT called a second time",
      mock_get_heat.call_count == 0, f"called {mock_get_heat.call_count} times")
check("legs are flattened across every position, in order, before being handed to build_decisions",
      mock_build.call_args.args[0] == [{"id": "leg1"}, {"id": "leg2"}, {"id": "leg3"}],
      f"got {mock_build.call_args}")
check("portfolio_rollup receives the exact decisions list build_decisions returned",
      mock_rollup.call_args.args[0] == _fake_decisions, f"got {mock_rollup.call_args}")
check("the final payload is {'decisions': [d.to_dict() ...], 'rollup': ...}",
      out == {"decisions": [{"id": "leg1"}, {"id": "leg2"}, {"id": "leg3"}], "rollup": _fake_rollup},
      f"got {out}")

with mock.patch.object(decision_engine, "build_decisions", return_value=[]) as mock_build2, \
     mock.patch.object(decision_engine, "portfolio_rollup", return_value={}), \
     mock.patch.object(services, "get_position_heat", return_value=_heat_fixture) as mock_get_heat2:
    services.get_leg_decisions()

check("omitting 'heat' triggers exactly one fresh get_position_heat() load",
      mock_get_heat2.call_count == 1, f"called {mock_get_heat2.call_count} times")

# ---------------------------------------------------------------------------
# get_priority_sequence_cacheable
# ---------------------------------------------------------------------------
print("\nget_priority_sequence_cacheable() -- thin delegation to sequencer.build_priority_sequence()")

_fake_sequence = [{"tier": 0, "symbol": "OKTA"}]
with mock.patch.object(sequencer, "build_priority_sequence", return_value=_fake_sequence) as mock_seq:
    seq_out = services.get_priority_sequence_cacheable()
check("returns build_priority_sequence()'s result unmodified", seq_out == _fake_sequence, f"got {seq_out}")
check("build_priority_sequence is called with no arguments", mock_seq.call_args == mock.call(), f"got {mock_seq.call_args}")

# ---------------------------------------------------------------------------
# set_account_state
# ---------------------------------------------------------------------------
print("\nset_account_state() -- thin passthrough to account_state.set_state")

with mock.patch.object(account_state, "set_state") as mock_set_state:
    rv = services.set_account_state("A", cash=5000.0, equity_pct=61.2)
check("forwards the account + every kwarg unchanged", mock_set_state.call_args == mock.call("A", cash=5000.0, equity_pct=61.2),
      f"got {mock_set_state.call_args}")
check("returns None (no recompute happens here)", rv is None, f"got {rv!r}")

# ---------------------------------------------------------------------------
# _get_symbol_sector
# ---------------------------------------------------------------------------
print("\n_get_symbol_sector() -- thin wrapper over sector_analysis.get_symbol_sector")

with mock.patch.object(sector_analysis, "get_symbol_sector", return_value="Technology") as mock_sector:
    sect = services._get_symbol_sector("AAPL")
check("returns sector_analysis.get_symbol_sector()'s result unmodified and calls it with the given ticker",
      sect == "Technology" and mock_sector.call_args == mock.call("AAPL"), f"got {sect}, call={mock_sector.call_args}")

# ---------------------------------------------------------------------------
# analyze_watchlist_symbol
# ---------------------------------------------------------------------------
print("\nanalyze_watchlist_symbol() -- combined heat/IV-rank/sector/verticals/yield view")

with mock.patch.object(premium_yield, "get_yield_on_capital",
                        return_value={"price": 187.5, "call": {"iv": 0.42}, "put": {"iv": 0.31}}) as mock_yield, \
     mock.patch.object(enhanced_metrics, "get_ticker_metrics",
                        return_value={"heat_status": "NEUTRAL", "heat_reason": "no signal", "conviction": 7, "rsi": 55.0}) as mock_metrics, \
     mock.patch.object(iv_rank, "get_iv_rank", return_value={"iv_rank": 48.0, "entry_signal": True}) as mock_ivrank, \
     mock.patch.object(services, "_get_symbol_sector", return_value="Technology"), \
     mock.patch.object(trend_verticals, "get_verticals_for_ticker", return_value=["AI/Pick-and-Shovel"]):
    aws = services.analyze_watchlist_symbol("  aapl ")

check("ticker is normalized (upper-cased, stripped) before every downstream call",
      aws["symbol"] == "AAPL" and mock_metrics.call_args.args[0] == "AAPL" and mock_ivrank.call_args.args[0] == "AAPL",
      f"got symbol={aws['symbol']}, metrics call={mock_metrics.call_args}")
check("the price resolved by get_yield_on_capital is reused directly (no separate yfinance fallback call)",
      aws["price"] == 187.5 and mock_metrics.call_args.args[1] == 187.5, f"got {aws['price']}")
check("the real current IV is read from the CALL side first when present",
      mock_ivrank.call_args.kwargs.get("current_iv") == 0.42, f"got {mock_ivrank.call_args}")
check("heat/conviction/rsi/iv_rank/verticals/sector are all merged into one flat result",
      aws["heat_status"] == "NEUTRAL" and aws["conviction"] == 7 and aws["rsi"] == 55.0
      and aws["iv_rank"] == 48.0 and aws["iv_entry_signal"] is True
      and aws["sector"] == "Technology" and aws["verticals"] == ["AI/Pick-and-Shovel"],
      f"got {aws}")
check("the full yield_on_capital payload is passed through under 'yield_on_capital'",
      aws["yield_on_capital"]["price"] == 187.5, f"got {aws['yield_on_capital']}")

print("\nanalyze_watchlist_symbol() -- no resolvable price at all (yield fetch and yfinance fallback both empty)")

import yfinance as yf  # noqa: E402


class _EmptyHist:
    def __len__(self):
        return 0


class _FakeEmptyTicker:
    def __init__(self, symbol):
        pass

    def history(self, **kwargs):
        return _EmptyHist()


with mock.patch.object(premium_yield, "get_yield_on_capital", return_value={"price": None}), \
     mock.patch.object(yf, "Ticker", side_effect=_FakeEmptyTicker) as mock_yf_ticker, \
     mock.patch.object(enhanced_metrics, "get_ticker_metrics") as mock_metrics_unused, \
     mock.patch.object(iv_rank, "get_iv_rank", return_value={"iv_rank": None, "entry_signal": None}), \
     mock.patch.object(services, "_get_symbol_sector", return_value="Unknown"), \
     mock.patch.object(trend_verticals, "get_verticals_for_ticker", return_value=[]):
    aws_no_price = services.analyze_watchlist_symbol("ZZZZ")

check("a live yfinance fallback is attempted when get_yield_on_capital resolves no price",
      mock_yf_ticker.call_count == 1, f"called {mock_yf_ticker.call_count} times")
check("when NEITHER source resolves a price, get_ticker_metrics is never called and heat/conviction/rsi are all None",
      mock_metrics_unused.call_count == 0 and aws_no_price["heat_status"] is None
      and aws_no_price["conviction"] is None, f"got {aws_no_price}")
check("price stays None end to end", aws_no_price["price"] is None, f"got {aws_no_price['price']}")

# ---------------------------------------------------------------------------
# get_today_plan
# ---------------------------------------------------------------------------
print("\nget_today_plan() -- cash/equity-aware reordering over an already-cached priority sequence")

_full_sequence = [
    {"tier": 0, "tier_source": "position_heat", "symbol": "OKTA"},
    {"tier": 0, "tier_source": "composite", "ticker": "NFLX"},
    {"tier": 1, "tier_source": "position_heat", "symbol": "GEV", "account": "Account A (232)", "leg_count": 1,
     "legs": [{"type": "CALL", "action": "HARVEST_RESTAGGER", "covered": True, "strangle": False,
               "strike": 180.0, "expiry": "2026-12-18", "reason": "Profit target hit"}]},
    {"tier": 1, "tier_source": "position_heat", "symbol": "ZS", "account": "Account A (232)", "leg_count": 1,
     "legs": [{"type": "CALL", "action": "CUT_RESTAGGER", "covered": False, "strangle": True,
               "strike": 150.0, "expiry": "2026-12-18", "reason": "Hard stop - loss multiple exceeded"}]},
    {"tier": 2, "ticker": "DELL", "score": 1.2, "rank": 3, "population_size": 50, "iv_rank": 60.0},
]

with mock.patch.object(account_state, "get_state",
                        return_value={"cash": 30000.0, "equity_pct": 70.0, "days_stale": 1}):
    plan = services.get_today_plan(full_sequence=_full_sequence)

check("cash below the documented $50K floor marks the day as cash/equity-stressed",
      plan["cash_or_equity_stressed"] is True, f"got {plan}")
check("exactly one context note fires (cash only -- equity_pct and days_stale are both within bounds)",
      len(plan["context_notes"]) == 1 and "Cash" in plan["context_notes"][0], f"got {plan['context_notes']}")
check("total_sequenced reports the full input sequence length, not the trimmed plan length",
      plan["total_sequenced"] == 5, f"got {plan['total_sequenced']}")

sections = [item["section"] for item in plan["plan"]]
check("plan order is GATE, GATE, CASH RELIEF FIRST, MANAGE HARD STOPS x2, NEW ENTRY CANDIDATES",
      sections == ["GATE", "GATE", "CASH RELIEF FIRST", "MANAGE HARD STOPS", "MANAGE HARD STOPS",
                   "NEW ENTRY CANDIDATES"], f"got {sections}")

gate_actions = [item["action"] for item in plan["plan"] if item["section"] == "GATE"]
check("a position_heat-sourced tier-0 row is labeled by its 'symbol'; a composite-sourced one by its 'ticker'",
      gate_actions == ["Review gate on OKTA", "Review gate on NFLX"], f"got {gate_actions}")

relief_item = next(item for item in plan["plan"] if item["section"] == "CASH RELIEF FIRST")
check("cash relief surfaces the profitable HARVEST_RESTAGGER call (GEV), not the hard-stop CUT_RESTAGGER one (ZS)",
      "GEV" in relief_item["action"] and "$180" in relief_item["action"], f"got {relief_item}")

hard_stop_items = [item for item in plan["plan"] if item["section"] == "MANAGE HARD STOPS"]
geV_item = next(i for i in hard_stop_items if "GEV" in i["action"])
zs_item = next(i for i in hard_stop_items if "ZS" in i["action"])
check("a covered call's hard-stop line carries no strangle note",
      "[strangle-paired" not in geV_item["why"], f"got {geV_item['why']}")
check("a naked-but-strangle-paired call gets the explicit strangle-pairing caveat appended",
      "[strangle-paired" in zs_item["why"], f"got {zs_item['why']}")

entry_item = next(item for item in plan["plan"] if item["section"] == "NEW ENTRY CANDIDATES")
check("a tier-2 new-entry candidate's line reports score/rank/population/iv_rank",
      entry_item["action"] == "ENTER DELL" and "score=1.2" in entry_item["why"] and "rank 3/50" in entry_item["why"],
      f"got {entry_item}")

print("\nget_today_plan() -- not cash/equity-stressed: no CASH RELIEF FIRST section even with a HARVEST_RESTAGGER call")

with mock.patch.object(account_state, "get_state",
                        return_value={"cash": 200000.0, "equity_pct": 90.0, "days_stale": 1}):
    plan2 = services.get_today_plan(full_sequence=_full_sequence)
check("no stress -> no context notes, no CASH RELIEF FIRST section",
      plan2["cash_or_equity_stressed"] is False and plan2["context_notes"] == []
      and "CASH RELIEF FIRST" not in [i["section"] for i in plan2["plan"]], f"got {plan2}")

print("\nget_today_plan() -- equity floor breach + stale account state both surface their own notes")

with mock.patch.object(account_state, "get_state",
                        return_value={"cash": 100000.0, "equity_pct": 30.0, "days_stale": 5}):
    plan3 = services.get_today_plan(full_sequence=[])
check("equity below the 50% bear-regime floor is flagged even when cash itself is fine",
      plan3["cash_or_equity_stressed"] is True and any("Equity" in n for n in plan3["context_notes"]),
      f"got {plan3['context_notes']}")
check("account state older than 3 days gets its own staleness note",
      any("old" in n for n in plan3["context_notes"]), f"got {plan3['context_notes']}")

print("\nget_today_plan() -- no account state on file yet")

with mock.patch.object(account_state, "get_state", return_value=None):
    plan4 = services.get_today_plan(full_sequence=[])
check("a missing account state reports the explicit 'inactive' note, not a crash or stress flag",
      plan4["cash_or_equity_stressed"] is False and "inactive" in plan4["context_notes"][0],
      f"got {plan4}")

# ---------------------------------------------------------------------------
# get_cash_margin_forecast
# ---------------------------------------------------------------------------
print("\nget_cash_margin_forecast() -- Account A crash-scenario cash + DTE-bucket/expiry-concentration forecast")

import pandas as pd  # noqa: E402
from datetime import date, timedelta  # noqa: E402

_today = date.today()
_ACCT_A = "Account A (232)"
_opt_df = pd.DataFrame([
    {"account_name": _ACCT_A, "ticker": "NEARTICK", "option_type": "C", "net_quantity": -2,
     "expiry_date": (_today + timedelta(days=30)).isoformat()},
    {"account_name": _ACCT_A, "ticker": "CORETICK", "option_type": "P", "net_quantity": -3,
     "expiry_date": (_today + timedelta(days=70)).isoformat()},
    {"account_name": _ACCT_A, "ticker": "MIDTICK", "option_type": "C", "net_quantity": -1,
     "expiry_date": (_today + timedelta(days=150)).isoformat()},
    {"account_name": _ACCT_A, "ticker": "FARTICK", "option_type": "P", "net_quantity": -4,
     "expiry_date": (_today + timedelta(days=210)).isoformat()},
    {"account_name": _ACCT_A, "ticker": "UNKTICK", "option_type": "C", "net_quantity": -1,
     "expiry_date": "not-a-real-date"},
    # Wrong account -- must be filtered out entirely.
    {"account_name": "Account B (901)", "ticker": "OTHERACCT", "option_type": "C", "net_quantity": -5,
     "expiry_date": (_today + timedelta(days=30)).isoformat()},
    # Not an option (stock position) -- must be filtered out by the option_type isin(['C','P']) check.
    {"account_name": _ACCT_A, "ticker": "STOCKPOS", "option_type": "S", "net_quantity": 100,
     "expiry_date": None},
])
_fake_gen2 = mock.Mock()
_fake_gen2.open_positions = _opt_df
_fake_gen2.prices = {"NEARTICK": 100.0, "CORETICK": 50.0, "MIDTICK": 75.0, "FARTICK": 40.0, "UNKTICK": 20.0}
_fake_gen2.option_requirements = {_ACCT_A: 50000.0}
_fake_accounts_config = {_ACCT_A: {"capacity": 900000.0, "capacity_as_of": "2026-10-01"}}

with mock.patch.object(services, "_get_generator", return_value=_fake_gen2), \
     mock.patch.object(accounts_config, "ACCOUNTS_CONFIG", _fake_accounts_config), \
     mock.patch.object(account_state, "get_state", return_value={"emergency_reserve": 160000.0, "days_stale": 2}):
    forecast = services.get_cash_margin_forecast()

check("total_notional only sums Account A's real option rows (60500 = 20000+15000+7500+16000+2000)",
      forecast["total_notional"] == 60500.0, f"got {forecast['total_notional']}")
check("opt_req/capacity/capacity_as_of pass through from the generator/config unchanged",
      forecast["opt_req"] == 50000.0 and forecast["capacity"] == 900000.0
      and forecast["capacity_as_of"] == "2026-10-01", f"got {forecast}")
check("stress_low/stress_high use the documented 15%/20% * 18%-of-notional model",
      forecast["stress_low"] == 60500.0 * 0.15 * 0.18 and forecast["stress_high"] == 60500.0 * 0.20 * 0.18,
      f"got low={forecast['stress_low']}, high={forecast['stress_high']}")
check("a real account_state.emergency_reserve is used (not the stale $140K/$200K fallback literal)",
      forecast["emergency_reserve"] == 160000.0 and forecast["reserve_days_stale"] == 2,
      f"got {forecast['emergency_reserve']}, stale={forecast['reserve_days_stale']}")
check("reserve_covers_stress compares the real reserve against stress_high",
      forecast["reserve_covers_stress"] is True, f"got {forecast['reserve_covers_stress']}")

buckets_by_label = {b["label"]: b for b in forecast["dte_buckets"]}
check("all 4 DTE buckets are always present even though one real bucket boundary is close",
      set(buckets_by_label.keys()) == {"Near (<60 DTE)", "Core (60-135 DTE)", "Mid (135-195 DTE)", "Far (195+ DTE)"},
      f"got {list(buckets_by_label.keys())}")
check("the Near bucket (33.1% of book) is well over its 10-15% target -> 'heavy'",
      buckets_by_label["Near (<60 DTE)"]["status"] == "heavy", f"got {buckets_by_label['Near (<60 DTE)']}")
check("the Core bucket (24.8% of book) is under its 35-40% target -> 'light'",
      buckets_by_label["Core (60-135 DTE)"]["status"] == "light", f"got {buckets_by_label['Core (60-135 DTE)']}")
check("the Mid bucket (12.4% of book) is under its 20-24% target -> 'light'",
      buckets_by_label["Mid (135-195 DTE)"]["status"] == "light", f"got {buckets_by_label['Mid (135-195 DTE)']}")
check("the Far bucket (26.4% of book) is over its 10-15% target -> 'heavy'",
      buckets_by_label["Far (195+ DTE)"]["status"] == "heavy", f"got {buckets_by_label['Far (195+ DTE)']}")

top_dates_by_notional = sorted(forecast["top_expiry_dates"], key=lambda d: -d["notional"])
check("an unparseable expiry_date (UNKTICK) is simply dropped from the top-expiry-dates view "
      "(groupby excludes NaT keys) while still counting toward total_notional",
      len(forecast["top_expiry_dates"]) == 4, f"got {forecast['top_expiry_dates']}")
check("the single-date concentration status buckets correctly: >25% over, 20-25% edge, else ok",
      top_dates_by_notional[0]["status"] == "over"
      and any(d["status"] == "edge" for d in top_dates_by_notional)
      and any(d["status"] == "ok" for d in top_dates_by_notional),
      f"got {top_dates_by_notional}")

print("\nget_cash_margin_forecast() -- no account_state on file -> falls back to the documented $140K reserve")

with mock.patch.object(services, "_get_generator", return_value=_fake_gen2), \
     mock.patch.object(accounts_config, "ACCOUNTS_CONFIG", _fake_accounts_config), \
     mock.patch.object(account_state, "get_state", return_value=None):
    forecast2 = services.get_cash_margin_forecast()
check("emergency_reserve falls back to 140000 and reserve_days_stale is None when no state is on file",
      forecast2["emergency_reserve"] == 140000 and forecast2["reserve_days_stale"] is None,
      f"got {forecast2['emergency_reserve']}, {forecast2['reserve_days_stale']}")

# ---------------------------------------------------------------------------
# get_report_text / extract_section_from_text / extract_markdown_section
# ---------------------------------------------------------------------------
print("\nget_report_text() -- dispatches to the right UnifiedReportProduction method, rejects unknown types")

_fake_gen3 = mock.Mock()
_fake_gen3.generate_daily_report.return_value = "DAILY REPORT TEXT"
with mock.patch.object(services, "_get_generator", return_value=_fake_gen3):
    check("'daily' dispatches to generate_daily_report()", services.get_report_text("daily") == "DAILY REPORT TEXT",
          f"got {services.get_report_text('daily')!r}")
    try:
        services.get_report_text("nonsense")
        check("an unknown report_type raises ValueError", False, "no exception raised")
    except ValueError as exc:
        check("an unknown report_type raises ValueError naming the bad value", "nonsense" in str(exc), f"got {exc}")

print("\nextract_section_from_text() -- pure substring extraction by heading markers")

_sample_text = "intro\n## Section 1: A\nbody A\n## Section 2: B\nbody B\n## Section 3: C\nbody C"
check("explicit end_marker cuts exactly between the two markers",
      services.extract_section_from_text(_sample_text, "## Section 1: A", "## Section 2: B") == "## Section 1: A\nbody A",
      repr(services.extract_section_from_text(_sample_text, "## Section 1: A", "## Section 2: B")))
check("omitted end_marker cuts at the next '## ' heading",
      services.extract_section_from_text(_sample_text, "## Section 2: B") == "## Section 2: B\nbody B",
      repr(services.extract_section_from_text(_sample_text, "## Section 2: B")))
check("the last section with no following heading runs to the end of the text",
      services.extract_section_from_text(_sample_text, "## Section 3: C") == "## Section 3: C\nbody C",
      repr(services.extract_section_from_text(_sample_text, "## Section 3: C")))
check("a marker that isn't in the text returns the documented not-found placeholder",
      services.extract_section_from_text(_sample_text, "## Nope") == "_Section not found: ## Nope_",
      repr(services.extract_section_from_text(_sample_text, "## Nope")))

print("\nextract_markdown_section() -- extract_section_from_text() over a report_type's full generated text")

with mock.patch.object(services, "get_report_text", return_value=_sample_text) as mock_get_text:
    section = services.extract_markdown_section("weekly", "## Section 2: B")
check("fetches the named report_type's text and extracts the requested section from it",
      section == "## Section 2: B\nbody B" and mock_get_text.call_args == mock.call("weekly"), f"got {section}")

# ---------------------------------------------------------------------------
# get_quarterly_direction / get_active_decisions / get_india_plan (DATA_ROOT readers)
# ---------------------------------------------------------------------------
print("\nget_quarterly_direction() / get_active_decisions() / get_india_plan() -- real DATA_ROOT file reads")

_tmp_data_root = tempfile.mkdtemp(prefix="theta_lab_test_services_data_root_")
_original_data_root = services.DATA_ROOT
try:
    services.DATA_ROOT = _tmp_data_root
    os.makedirs(os.path.join(_tmp_data_root, "logs"), exist_ok=True)
    os.makedirs(os.path.join(_tmp_data_root, "data"), exist_ok=True)

    with open(os.path.join(_tmp_data_root, "logs", "quarterly_portfolio_direction_us_2026-01.md"), "w") as f:
        f.write("# January direction (stale)")
    with open(os.path.join(_tmp_data_root, "logs", "quarterly_portfolio_direction_us_2026-06.md"), "w") as f:
        f.write("# June direction (current)")

    check("picks the lexicographically (= chronologically) latest quarterly doc when more than one exists",
          services.get_quarterly_direction("us") == "# June direction (current)",
          repr(services.get_quarterly_direction("us")))
    check("a market with no quarterly doc on disk returns the documented not-found message",
          "No quarterly portfolio direction doc found for market 'india'" in services.get_quarterly_direction("india"),
          repr(services.get_quarterly_direction("india")))

    with open(os.path.join(_tmp_data_root, "data", "active_decisions.yaml"), "w") as f:
        f.write("decisions:\n  - ticker: AAPL\n    note: trim into strength\n")
    check("get_active_decisions() reads the real decisions list out of active_decisions.yaml",
          services.get_active_decisions() == [{"ticker": "AAPL", "note": "trim into strength"}],
          repr(services.get_active_decisions()))

    check("get_india_plan() returns None when india_6month_plan.yaml doesn't exist on disk at all",
          services.get_india_plan() is None, repr(services.get_india_plan()))
finally:
    services.DATA_ROOT = _original_data_root
    shutil.rmtree(_tmp_data_root, ignore_errors=True)

check("get_active_decisions() returns [] (not a crash) when the yaml file is entirely absent",
      (lambda: (
          setattr(services, "DATA_ROOT", tempfile.mkdtemp(prefix="theta_lab_test_services_empty_")),
          services.get_active_decisions(),
      )[1])() == [],
      "expected [] for a totally empty DATA_ROOT")
services.DATA_ROOT = _original_data_root

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
