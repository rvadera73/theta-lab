"""Thin wrappers around the existing report engine (mcp/reports,
scripts/realized_pnl.py) and the raw YAML trackers. No report-generation
logic lives here -- every function below calls something that already
exists and just reshapes it into JSON for the dashboard. See
docs/DASHBOARD_PLAN.md (Phase 1: read-only dashboard).
"""
import sys
import os
from collections import defaultdict
import yaml


def _to_native(obj):
    """Recursively convert numpy/pandas scalar types to plain Python so
    FastAPI's JSON encoder doesn't choke on them -- _compute_account_status
    sums pandas columns internally and can hand back numpy.float64/int64.
    """
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    if hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    return obj

CODE_ROOT = "/app"
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp", "reports"))
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp", "analysis"))
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp"))
sys.path.insert(0, os.path.join(CODE_ROOT, "scripts"))

# The report engine (mcp/reports/*.py, scripts/open_positions_loader_v2.py)
# hardcodes this exact absolute host path for data/logs, not a CWD-relative
# one -- confirmed live 2026-09-25 ("No objects to concatenate" when data/
# was mounted at /app/data instead). docker-compose.yml mounts the real
# data/logs volumes here to match, so those modules work completely
# unmodified inside the container.
DATA_ROOT = "/home/rahulvadera/projects/theta-lab"

_report_generator = None


def _get_generator():
    # Cached at module scope, not per-request -- __init__ loads every
    # position file and fetches live prices for ~90 tickers (real network
    # calls), which is too slow to redo on every dashboard hit. A
    # dedicated "refresh" endpoint (Phase 1 stretch / Phase 4 scheduler)
    # invalidates this when fresher data is wanted.
    global _report_generator
    if _report_generator is None:
        from unified_master_report_production import UnifiedReportProduction
        _report_generator = UnifiedReportProduction()
    return _report_generator


def refresh_generator():
    global _report_generator
    _report_generator = None
    return _get_generator()


def get_account_status():
    gen = _get_generator()
    status = gen._compute_account_status()
    return _to_native([
        {"account": name, **dict(data.items())}
        for name, data in status.items()
    ])


# Sector hints for Watchlist candidates sourced from run_screener (which
# already knows each candidate's sector) -- gather_watchlist_rows has no
# other way to learn a not-yet-held ticker's sector, since ticker_sector_map
# is only ever built from held positions.
_WATCHLIST_SECTOR_HINTS = {
    "DELL": "Technology", "HPE": "Technology",
    "SCHW": "Financial Services", "BAC": "Financial Services", "MUFG": "Financial Services",
    "PBR": "Energy", "OXY": "Energy",
    "TGT": "Consumer Cyclical", "ETN": "Industrials", "DE": "Industrials",
}


def _merge_watchlist_notes(watchlist_rows, tracked_rows):
    """In-place merges each tracked Watchlist row's own free-text "notes"
    onto its matching scored watchlist row (keyed by symbol/ticker)."""
    notes_by_symbol = {row["symbol"]: row.get("notes", "") for row in tracked_rows}
    for r in watchlist_rows:
        r["notes"] = notes_by_symbol.get(r["ticker"], "")


def _realized_perf_row(ticker, pnl, closed_count, held_by_ticker):
    row = held_by_ticker.get(ticker, {})
    return {
        "ticker": ticker, "realized_pnl_90d": pnl, "closed_count_90d": closed_count,
        "composite_rank": row.get("rank"), "composite_score": row.get("score"),
        "conviction": row.get("conviction"), "conviction_rank": row.get("conviction_rank"),
        "yield_pct": row.get("yield_pct"), "yield_rank": row.get("yield_rank"),
        "flags": row.get("flags"), "tail_risk": row.get("tail_risk"),
    }


def _realized_performance_views(held_by_ticker, realized):
    """Splits realized_pnl_by_ticker()'s flat "ranked" list into the 3 views
    the dashboard shows side by side: top performers, real realized losses,
    and held names with zero realized activity in the window at all (see
    get_composite_scores' own docstring for why these stay 3 separate lists
    rather than one blended ranking)."""
    top_performers = [_realized_perf_row(t, pnl, cc, held_by_ticker) for t, pnl, cc in realized["ranked"][:15]]

    losses = [_realized_perf_row(t, pnl, cc, held_by_ticker) for t, pnl, cc in realized["ranked"] if pnl < 0]
    losses.sort(key=lambda r: r["realized_pnl_90d"])  # worst (most negative) first

    realized_tickers = {t for t, _pnl, _cc in realized["ranked"]}
    no_activity = [_realized_perf_row(t, 0.0, 0, held_by_ticker) for t in held_by_ticker if t not in realized_tickers]
    # Best-ranked-but-still-inactive first (most worth a second look --
    # good forward score, yet nothing realized in 90 days); unranked
    # (missing yield/conviction data) sort to the end.
    no_activity.sort(key=lambda r: r["composite_rank"] if r["composite_rank"] is not None else 9999)

    return top_performers, losses, no_activity


def get_composite_scores():
    """Composite risk-adjusted scores for every held ticker AND every
    tracked Watchlist symbol, scored TOGETHER as one population (see
    mcp/reports/composite_score.py's module docstring for the full z-score
    formula) -- so a new candidate's rank/z-scores reflect genuine standing
    against everything already held, not a separate standalone number."""
    from composite_score import compute_composite_scores
    from realized_performance import realized_pnl_by_ticker
    from . import watchlist as _watchlist

    gen = _get_generator()
    gen.get_priority_actions()  # ensure self.metrics/premium_yields/ticker_sector_map are populated

    tracked = _watchlist.list_watchlist(tracked_only=True)
    result = compute_composite_scores(gen, [row["symbol"] for row in tracked], _WATCHLIST_SECTOR_HINTS)
    _merge_watchlist_notes(result["watchlist"], tracked)

    # Real, realized (FIFO-matched) 90-day P&L per ticker -- a SEPARATE
    # result from the composite score above, never blended into it. Past
    # realized outcome and the current forward-looking composite score
    # answer different questions (see realized_performance.py's module
    # docstring) -- shown side by side on the dashboard, not merged into
    # one ranked list.
    held_by_ticker = {r["ticker"]: r for r in result["held"]}
    realized = realized_pnl_by_ticker(days=90)
    top_performers, losses, no_activity = _realized_performance_views(held_by_ticker, realized)

    return _to_native({
        "held": result["held"],
        "watchlist": result["watchlist"],
        "regime": result["regime"],
        "macro_stage": result["macro_stage"],
        "severity_smoothed": result["severity_smoothed"],
        "high_exposure_sectors": result["high_exposure_sectors"],
        "sensitivity_confidence": result["sensitivity_confidence"],
        "realized_top_performers_90d": top_performers,
        "realized_losses_90d": losses,
        "realized_no_activity_90d": no_activity,
        "realized_cutoff": realized["cutoff"],
    })


def get_ytd_summary():
    from realized_pnl import get_realized_summary
    return get_realized_summary()


def get_monthly_by_account():
    from realized_pnl import get_realized_monthly_by_account
    return get_realized_monthly_by_account()


def _load_yaml(rel_path):
    path = os.path.join(DATA_ROOT, rel_path)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def get_active_decisions():
    data = _load_yaml("data/active_decisions.yaml") or {}
    return data.get("decisions", [])


def get_india_plan():
    return _load_yaml("data/india_6month_plan.yaml")


def get_us_priority_actions():
    """The bottom-up CLOSE/TRIM/ENTER-only list (see
    UnifiedReportProduction.get_priority_actions) -- deliberately NOT the
    full 92-ticker Sector Heat table. ledger.sync_all() syncs only this
    into the Action Tracker so it doesn't fill up with routine WATCH/HOLD
    noise when the book is stable (verified live 2026-09-25: 3 items out
    of 92 tickers on a normal day)."""
    gen = _get_generator()
    return _to_native(gen.get_priority_actions())


def get_position_heat():
    """Position Heat (per LEG) -- different from the per-TICKER 'Technical
    Heat' elsewhere on this dashboard (get_composite_scores,
    get_us_priority_actions, Sector Heat all read UnifiedReportProduction's
    RSI/Bollinger/52-week-range scoring). Reuses
    analysis.heat_scanner.assess_portfolio_heat (the scan_position_heat MCP
    tool's own engine) to score each OPEN OPTION LEG by cost-to-close-vs-
    premium ratio, DTE, and strike distance -- confirmed 2026-10-12: a real
    position, META $670P, was RED and 62% underwater here while invisible
    to every other dashboard view (none of them read this computation).

    Reuses report_utils.load_us_positions() -- the SAME file-based loader
    (Schwab from transaction CSVs, Fidelity/Robinhood/Vanguard from CSV/PDF
    exports, Yahoo-backfilled prices) mcp/server.py's scan_position_heat
    tool handler already uses -- NOT scripts/open_positions_loader_v2.py
    (used by UnifiedReportProduction), which has no premium_received/
    current_mark fields at all.
    """
    import asyncio
    from report_utils import load_us_positions
    from heat_scanner import assess_portfolio_heat
    from regime import detect_regime

    us_data = asyncio.run(load_us_positions())
    positions = us_data.get("positions", [])
    account_sources = us_data.get("account_sources", {})
    regime_str = detect_regime().get("regime", "CAUTIOUS_BULL")

    legs, context, cost_to_close_by_key, premium_received_by_key = _build_legs_and_context(positions, account_sources)

    if not legs:
        return _to_native({"by_color": {"RED": [], "YELLOW": [], "GREEN": [], "UNKNOWN": []},
                            "counts": {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0},
                            "regime": regime_str, "top_actions": []})

    result = assess_portfolio_heat(legs, regime_str)

    # _annotate_heat_rows() returns a deduplicated list (the second row for
    # a cross-account-collision key is dropped, not just left un-annotated)
    # -- the return value MUST be used, not discarded, or the dropped
    # duplicate's un-annotated twin stays in by_color with no "account"
    # field at all. That un-annotated row previously formed a phantom
    # (symbol, None) position-group in _group_positions_by_symbol_account()
    # below and leaked straight into get_leg_decisions() -> decision_engine,
    # double-counting the same real contract's premium/cost-to-close in the
    # portfolio rollup -- confirmed real, recurring collision (NVO $40C,
    # 2026-10-15), not hypothetical.
    for color, color_rows in result.get("by_color", {}).items():
        result["by_color"][color] = _annotate_heat_rows(
            color_rows, context, cost_to_close_by_key, premium_received_by_key
        )
    result["top_actions"] = _annotate_heat_rows(
        result.get("top_actions", []), context, cost_to_close_by_key, premium_received_by_key
    )

    result["sector_rollup"] = _build_sector_rollup(result.get("by_color", {}), cost_to_close_by_key)
    result["positions"] = _group_positions_by_symbol_account(result.get("by_color", {}))

    return _to_native(result)


def _key(symbol, strike, expiry, opt_type):
    return (symbol, round(float(strike), 4), expiry, opt_type)


def _leg_coverage_and_strangle_expiries(pos):
    """Per-position prep for _process_position_legs(): (1) covered-call
    allocation -- real owned shares in THIS account/symbol, consumed by its
    own call legs only (coverage doesn't cross accounts -- the shares and
    the short call must sit in the same brokerage account), calls sorted by
    strike ascending so the most likely to be assigned draws on shares
    first; (2) strangle pairing -- a put + call sharing an expiry is one
    coordinated structure, not two unrelated alarms (matches this book's own
    strategy docs). Returns ({id(leg): {...}}, {shared expiries})."""
    shares_remaining = pos.shares or 0
    calls_sorted = sorted(
        (lg for lg in pos.option_legs if lg.option_type == "CALL"),
        key=lambda lg: lg.strike,
    )
    leg_coverage = {}
    for lg in calls_sorted:
        contracts = abs(lg.quantity)
        covered = min(shares_remaining // 100, contracts)
        shares_remaining -= covered * 100
        leg_coverage[id(lg)] = {
            "covered_contracts": int(covered),
            "total_contracts": int(contracts),
            "naked": covered < contracts,
        }

    puts_by_expiry = defaultdict(list)
    calls_by_expiry = defaultdict(list)
    for lg in pos.option_legs:
        (calls_by_expiry if lg.option_type == "CALL" else puts_by_expiry)[lg.expiry].append(lg)
    strangle_expiries = set(puts_by_expiry) & set(calls_by_expiry)

    return leg_coverage, strangle_expiries


def _build_leg_context_entry(pos, lg, signals: dict):
    """The initial per-contract context dict (see _build_legs_and_context's
    docstring for why this is keyed by contract identity, not by leg).
    `signals` bundles leg_ctx/eh_ctx/strangle_expiries/source_info so this
    stays within the 4-param limit."""
    leg_ctx, eh_ctx = signals["leg_ctx"], signals["eh_ctx"]
    return {
        "account": pos.account,
        "accounts": set(),  # every account holding this exact contract -- see _annotate_heat_rows()'s dedup
        "covered": True,  # AND-combined below; True is the identity for AND
        "covered_contracts": 0, "total_contracts": 0,
        "strangle": lg.expiry in signals["strangle_expiries"],
        "data_source": signals["source_info"].get("source"),
        "data_as_of": signals["source_info"].get("as_of"),
        "days_stale": signals["source_info"].get("days_stale"),
        "sector": leg_ctx.get("sector"),
        # OVERNIGHT_MOVE (ADR 0004) folded into the same gates_fired list
        # symbol_context.py's HIGH_LEVERAGE/EARNINGS_RISK/ILLIQUID already
        # populate -- one list, one convention.
        "gates_fired": leg_ctx.get("gates_fired", []) + eh_ctx["gates_fired"],
        "dividend_rate": leg_ctx.get("dividend_rate"),
        "next_ex_dividend_date": leg_ctx.get("next_ex_dividend_date"),
        # iv_rank/current_iv_pct were computed here all along but never
        # passed through to the leg dict (ADR 0001 step 7) --
        # decision_engine.py's portfolio Greeks rollup needs a vol input per
        # leg; current_iv_pct is real when a caller upstream supplied one
        # (step 6), else iv_rank's own HV-proxy fallback. Renamed from
        # `current_iv` (issue #56) -- this is iv_rank.get_iv_rank()'s
        # PERCENTAGE output, which used to share its name with that same
        # function's unrelated fractional `current_iv` INPUT parameter.
        "current_iv_pct": leg_ctx.get("current_iv_pct"),
        # Extended-hours overnight-move signal (ADR 0004) -- live_price is
        # the current pre-market/after-hours/regular quote; overnight_move_pct
        # compares it to pos.current_price (the regular close margin/P&L math
        # uses, unchanged by this).
        "live_price": eh_ctx["live_price"],
        "live_price_source": eh_ctx["live_price_source"],
        "overnight_move_pct": eh_ctx["overnight_move_pct"],
    }


def _process_position_legs(pos, account_sources, acc: dict):
    """One position's option legs -> acc["legs"] (for assess_portfolio_heat)
    plus acc["context"]/cost/premium lookups (for _annotate_heat_rows),
    keyed by (symbol, strike, expiry, option_type) -- see
    _build_legs_and_context's docstring for why a leg key can collide
    across two accounts. `acc` bundles all 4 outputs so this stays within
    the 4-param limit; premium_received_by_key specifically is needed
    because decision_engine.py wants the real premium directly, not one
    re-derived from cost_to_close/loss_multiple (undefined when
    loss_multiple is 0, i.e. GREEN legs -- ADR 0001 step 3)."""
    from report_utils import extended_hours_context
    from symbol_context import get_cached_symbol_context

    leg_coverage, strangle_expiries = _leg_coverage_and_strangle_expiries(pos)
    source_info = account_sources.get(pos.account, {})

    for lg in pos.option_legs:
        premium = abs(lg.premium_received or 0)
        if premium <= 0:
            continue  # assess_portfolio_heat can't compute loss_multiple against a zero premium

        # ADR 0005: coverage now feeds heat_scanner's color/action scoring
        # itself, not just a post-hoc annotation (see _merge_context_onto_row
        # below, unchanged) -- computed from the SAME per-position cov this
        # function already derives below, so the two can never disagree.
        cov = leg_coverage.get(id(lg))
        if lg.option_type == "PUT":
            coverage = "CASH_SECURED_PUT"
        elif not cov["naked"]:
            coverage = "COVERED"
        elif cov["covered_contracts"] > 0:
            coverage = "PARTIAL"
        else:
            coverage = "NAKED"

        acc["legs"].append({
            "symbol": pos.symbol, "option_type": lg.option_type, "strike": lg.strike,
            "dte": lg.dte, "expiry": lg.expiry, "premium_received": premium,
            "cost_to_close": abs(lg.current_mark or 0), "current_price": pos.current_price,
            "coverage": coverage,
        })
        k = _key(pos.symbol, lg.strike, lg.expiry, lg.option_type)
        acc["cost_to_close_by_key"][k] = abs(lg.current_mark or 0)
        acc["premium_received_by_key"][k] = premium

        # Same-day-cached gate/parameter bundle + ADR 0004 extended-hours
        # overnight-move signal -- per-leg (not per-position) so the
        # earnings/DTE gate uses THIS leg's own DTE. See
        # _build_leg_context_entry()'s docstring for the full rationale.
        leg_ctx = get_cached_symbol_context(pos.symbol, dte=lg.dte)
        eh_ctx = extended_hours_context(pos.symbol, pos.current_price)
        signals = {"leg_ctx": leg_ctx, "eh_ctx": eh_ctx,
                   "strangle_expiries": strangle_expiries, "source_info": source_info}
        entry = acc["context"].setdefault(k, _build_leg_context_entry(pos, lg, signals))

        entry["accounts"].add(pos.account)
        if lg.option_type == "CALL":
            entry["covered"] = entry["covered"] and not cov["naked"]
            entry["covered_contracts"] += cov["covered_contracts"]
            entry["total_contracts"] += cov["total_contracts"]
        else:
            entry["covered"] = None  # not a meaningful concept for puts -- cash-secured by account design, checked separately


def _build_legs_and_context(positions, account_sources):
    """Builds the flat per-leg `legs` list assess_portfolio_heat() scores,
    plus the per-contract context/cost/premium lookups _annotate_heat_rows()
    merges back on afterward -- real position-context (strangle pairing, data
    staleness, cross-account covered_contracts/total_contracts/strangle
    display fields) heat_scanner.py itself has no concept of. As of ADR 0005,
    heat_scanner.py DOES take a per-leg `coverage` classification (NAKED/
    COVERED/PARTIAL/CASH_SECURED_PUT) as a scoring input -- computed once in
    _process_position_legs() below and fed in via the `legs` list, so this
    and the richer post-hoc `covered`/`covered_contracts` context can never
    disagree about whether a given leg is covered. A leg identifier can
    collide across two accounts holding the identical contract; when it
    happens the two accounts' context is combined rather than picked
    arbitrarily (conservative: covered only if EVERY account holding it has
    enough shares) -- this collision handling is display-only (_annotate_heat_rows)
    and does not affect the coverage each leg was actually SCORED with."""
    acc = {"legs": [], "context": {}, "cost_to_close_by_key": {}, "premium_received_by_key": {}}
    for pos in positions:
        _process_position_legs(pos, account_sources, acc)
    return acc["legs"], acc["context"], acc["cost_to_close_by_key"], acc["premium_received_by_key"]


def _merge_context_onto_row(row, ctx, cost_to_close_by_key, premium_received_by_key):
    """Merges one pooled context entry onto its matching heat row in place.
    top_actions rows use "option_type"; by_color rows use "type" --
    heat_scanner.py's own two output shapes genuinely differ (confirmed by
    source), not something to "fix" here."""
    opt_type = row.get("type") or row.get("option_type")
    key = _key(row["symbol"], row["strike"], row["expiry"], opt_type)
    row["covered"] = ctx["covered"]
    row["covered_contracts"] = ctx["covered_contracts"] if opt_type == "CALL" else None
    row["total_contracts"] = ctx["total_contracts"] if opt_type == "CALL" else None
    row["strangle"] = ctx["strangle"]
    row["account"] = ctx["account"] if len(ctx["accounts"]) == 1 else "+".join(sorted(ctx["accounts"]))
    row["multi_account_contract"] = len(ctx["accounts"]) > 1
    row["data_source"] = ctx["data_source"]
    row["data_as_of"] = ctx["data_as_of"]
    row["days_stale"] = ctx["days_stale"]
    row["sector"] = ctx["sector"]
    row["gates_fired"] = ctx["gates_fired"]
    row["dividend_rate"] = ctx.get("dividend_rate")
    row["next_ex_dividend_date"] = ctx.get("next_ex_dividend_date")
    row["current_iv_pct"] = ctx.get("current_iv_pct")
    row["live_price"] = ctx.get("live_price")
    row["live_price_source"] = ctx.get("live_price_source")
    row["overnight_move_pct"] = ctx.get("overnight_move_pct")
    row["cost_to_close"] = cost_to_close_by_key.get(key, 0.0)
    row["premium_received"] = premium_received_by_key.get(key, 0.0)


def _annotate_heat_rows(rows, context, cost_to_close_by_key, premium_received_by_key):
    """Cross-account collision de-dup -- real bug found 2026-10-15: the
    identical contract (symbol+strike+expiry+type) held in TWO accounts
    (confirmed real case: NVO $40C 03/19/2027) produces two separate
    heat_scanner.py rows (LegHeat has no account field), both pointing at
    the SAME pooled context entry. Collapses to one row per colliding key,
    explicitly labeled as spanning multiple accounts (row["account"] reads
    "A+B" via _merge_context_onto_row's multi_account_contract handling).

    The caller MUST use this function's return value in place of its input
    list -- a second real bug, found 2026-11-12: both of get_position_heat()'s
    call sites discarded the deduplicated `deduped` list, leaving the
    un-annotated duplicate row (no "account" field at all) still in
    by_color/top_actions. That un-annotated row formed a phantom
    (symbol, None) position-group downstream and leaked into
    get_leg_decisions() -> decision_engine, double-counting the same real
    contract's dollars in the portfolio rollup. Fixed at the call site, not
    here -- this function's own dedup logic was already correct.
    """
    seen_keys: set[tuple] = set()
    deduped = []
    for row in rows:
        opt_type = row.get("type") or row.get("option_type")
        if not opt_type:
            deduped.append(row)
            continue
        key = _key(row["symbol"], row["strike"], row["expiry"], opt_type)
        if context.get(key):
            if key in seen_keys:
                continue  # pooled contract already represented by an earlier row
            seen_keys.add(key)
            _merge_context_onto_row(row, context[key], cost_to_close_by_key, premium_received_by_key)
        deduped.append(row)
    return deduped


def _build_sector_rollup(by_color, cost_to_close_by_key):
    """"Which sector is actually bleeding right now," computed straight from
    these same real per-leg costs, not a second, differently-sourced sector
    view (the existing per-ticker Sector Heat on this dashboard reads
    enhanced_metrics.py's RSI/trend data; this reads real open-position
    cost-to-close instead -- complementary, not a duplicate)."""
    sector_rollup: dict[str, dict] = {}
    for color, color_rows in by_color.items():
        for row in color_rows:
            sec = row.get("sector") or "Unknown"
            bucket = sector_rollup.setdefault(sec, {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0, "red_cost_to_close": 0.0})
            bucket[color] = bucket.get(color, 0) + 1
            if color == "RED":
                opt_type = row.get("type") or row.get("option_type")
                cost = cost_to_close_by_key.get(_key(row["symbol"], row["strike"], row["expiry"], opt_type), 0.0)
                bucket["red_cost_to_close"] = round(bucket["red_cost_to_close"] + cost, 2)
    return sector_rollup


_POSITION_COLOR_RANK = {"RED": 0, "YELLOW": 1, "UNKNOWN": 2, "GREEN": 3}


def _group_positions_by_symbol_account(by_color):
    """Grouped positions -- one record per real (symbol, account) position,
    not per leg. Real gap found 2026-10-13: ZS/ANET-style multi-leg
    "stagger" campaigns the trader manages as one structure instead
    surfaced as independent-looking by_color alerts with no sign they
    belong together. Coverage doesn't cross accounts, so (symbol, account)
    is the correct grouping key, not symbol alone -- every leg's own full
    numbers stay in "legs", grouping only changes presentation/ranking."""
    groups: dict[tuple, dict] = {}
    for color, color_rows in by_color.items():
        for row in color_rows:
            key = (row["symbol"], row.get("account"))
            g = groups.setdefault(key, {
                "symbol": row["symbol"], "account": row.get("account"),
                "sector": row.get("sector"), "legs": [],
            })
            g["legs"].append(row)

    positions = []
    for (symbol, account), g in groups.items():
        g["legs"].sort(key=lambda r: _POSITION_COLOR_RANK.get(r.get("color"), 2))
        worst = g["legs"][0]
        g["worst_color"] = worst.get("color")
        g["worst_action"] = worst.get("action")
        g["leg_count"] = len(g["legs"])
        g["is_stagger"] = len(g["legs"]) > 1
        g["total_cost_to_close"] = round(sum(abs(lg.get("cost_to_close") or 0) for lg in g["legs"]), 2)
        g["naked_leg_count"] = sum(1 for lg in g["legs"] if lg.get("covered") is False)
        g["gates_fired"] = sorted({gate for lg in g["legs"] for gate in (lg.get("gates_fired") or [])})
        positions.append(g)
    positions.sort(key=lambda g: _POSITION_COLOR_RANK.get(g["worst_color"], 2))
    return positions


def get_leg_decisions(heat: dict | None = None):
    """LegDecisionRecord for every open short leg + portfolio rollup (ADR
    0001) -- completeness-by-construction vs. one-off scripts that checked a
    fixed symbol list and missed a newly-naked leg (real case, 2026-11-03:
    OKTA $140C). Projects get_position_heat()'s already-computed legs through
    decision_engine.py rather than a second position load.

    `heat`, if the caller already has a fresh get_position_heat() result
    (e.g. cache.py's refresh cycle), is reused directly instead of a second
    ~90s live reload + Yahoo fetch (found in review 2026-11-05 -- cache.py
    was paying this cost twice every cycle). Omitted, it does a fresh load.
    """
    from decision_engine import build_decisions, portfolio_rollup

    if heat is None:
        heat = get_position_heat()
    legs = [lg for p in heat.get("positions", []) for lg in p["legs"]]
    decisions = build_decisions(legs)
    rollup = portfolio_rollup(decisions)
    return _to_native({
        "decisions": [d.to_dict() for d in decisions],
        "rollup": rollup,
    })


def get_priority_sequence_cacheable():
    """Thin wrapper so sequencer.build_priority_sequence() -- 60-90s to
    reload all 8 accounts + ~85 live Yahoo prices -- gets computed ONCE per
    cache.refresh_all() cycle, not live per-request. Real bug found
    2026-10-15: /api/us/today called this directly and timed out (15s+)
    every time; the account-state lookup it also needs is a trivial SQLite
    read and was never the slow part."""
    from . import sequencer
    return sequencer.build_priority_sequence()


_CASH_FLOOR = 50_000.0
_EQUITY_FLOOR_PCT = 50.0


def _build_context_notes(state):
    """Cash/equity-floor + staleness notes off the trader-reported account
    state (see get_today_plan's docstring). Returns (notes, is_stressed)."""
    if not state:
        return (["No account state on file yet -- cash/equity-aware sequencing is inactive until you report one"],
                 False)
    notes = []
    stressed = False
    if state.get("cash") is not None and state["cash"] < _CASH_FLOOR:
        stressed = True
        notes.append(f"Cash ${state['cash']:,.0f} is below your documented ${_CASH_FLOOR:,.0f} floor")
    if state.get("equity_pct") is not None and state["equity_pct"] < _EQUITY_FLOOR_PCT:
        stressed = True
        notes.append(f"Equity {state['equity_pct']:.0f}% is below your documented {_EQUITY_FLOOR_PCT:.0f}% bear-regime floor")
    if state.get("days_stale", 0) > 3:
        notes.append(f"Account state is {state['days_stale']}d old -- re-check before relying on this")
    return notes, stressed


def _strangle_note(lg):
    """Real fix 2026-10-16 (trader correction): a 'naked' CALL that's
    actually strangle-paired (a cash-secured PUT sold alongside it on the
    same name/expiry) is Account A's own documented, intentional strategy,
    not an isolated naked emergency (confirmed real case: META/ANET/CRWD's
    naked calls were all strangle legs before this fix)."""
    if lg.get("type") == "CALL" and lg.get("covered") is False and lg.get("strangle"):
        return " [strangle-paired -- hedged by the put leg, not an isolated naked call]"
    return ""


def _build_gate_items(tier0):
    return [
        {"section": "GATE",
         "action": f"Review gate on {r['symbol'] if r['tier_source'] == 'position_heat' else r.get('ticker')}",
         "why": "Gate fired -- address before anything else, regardless of severity/score.", "ref": r}
        for r in tier0
    ]


def _build_cash_relief_items(tier1, context_notes):
    """Margin-relief-first, meant to be called ONLY when cash/equity is
    actually stressed -- same logic already used live for GEV/MA/ULTA on
    2026-10-15: among profitable (HARVEST_RESTAGGER) calls, largest
    strike/collateral first, since that's real margin relief at the least
    cost to close."""
    relief_candidates = [
        (r, lg) for r in tier1 if r["tier_source"] == "position_heat"
        for lg in r["legs"] if lg.get("type") == "CALL" and lg.get("action") == "HARVEST_RESTAGGER"
    ]
    relief_candidates.sort(key=lambda pair: -(pair[1].get("strike") or 0))
    return [
        {
            "section": "CASH RELIEF FIRST",
            "action": f"Close {r['symbol']} ${lg['strike']:.0f} CALL ({r['account']}, exp {lg['expiry']})",
            "why": f"{'; '.join(context_notes)}. Profitable and large strike -- real margin relief before cutting hard-stop losses below.",
            "detail": lg["reason"],
            "ref": r,
        }
        for r, lg in relief_candidates[:5]
    ]


def _build_hard_stop_items(tier1):
    items = []
    for r in tier1[:10]:
        worst = r["legs"][0]
        items.append({
            "section": "MANAGE HARD STOPS",
            "action": f"{worst['action']} {r['symbol']} ({r['account']}, {r['leg_count']} leg(s))",
            "why": worst["reason"] + _strangle_note(worst),
            "ref": r,
        })
    return items


def _build_new_entry_items(tier2):
    return [
        {
            "section": "NEW ENTRY CANDIDATES",
            "action": f"ENTER {r['ticker']}",
            "why": f"score={r.get('score')} (rank {r.get('rank')}/{r.get('population_size')}), iv_rank={r.get('iv_rank')}",
            "ref": r,
        }
        for r in tier2[:5]
    ]


def get_today_plan(full_sequence=None):
    """The single 'what do I actually do right now' view, built 2026-10-15
    directly off the trader's own complaint: every other tab is correct
    math/facts in isolation (Position Heat's severity, the composite
    score's ranking) but none of them know about each other or about the
    one real-world thing that changes what matters right now -- current
    cash/equity state, which this system can never compute itself (see
    account_state.py's docstring). This is a genuine synthesis, not a
    fourth independently-computed list: it takes the already-cached
    priority sequence (see get_priority_sequence_cacheable) and the
    trader-reported account state, and REORDERS around whichever is
    actually binding today. full_sequence is optional ONLY for direct/
    diagnostic calls -- the real API route always passes the cached one in.
    """
    from . import account_state as acct_state

    state = acct_state.get_state("A")
    if full_sequence is None:
        full_sequence = get_priority_sequence_cacheable()
    context_notes, cash_or_equity_stressed = _build_context_notes(state)

    tier0 = [r for r in full_sequence if r["tier"] == 0]
    tier1 = [r for r in full_sequence if r["tier"] == 1]
    tier2 = [r for r in full_sequence if r["tier"] == 2]

    plan = _build_gate_items(tier0)
    if cash_or_equity_stressed:
        plan += _build_cash_relief_items(tier1, context_notes)
    plan += _build_hard_stop_items(tier1)
    plan += _build_new_entry_items(tier2)

    return _to_native({
        "account_state": state,
        "context_notes": context_notes,
        "cash_or_equity_stressed": cash_or_equity_stressed,
        "total_sequenced": len(full_sequence),
        "plan": plan,
    })


def set_account_state(account: str, **fields):
    """Updates the trader-reported numbers only -- does NOT recompute the
    expensive priority sequence itself (same 60-90s trap as the GET route;
    see get_priority_sequence_cacheable's docstring). The API route passes
    the already-cached sequence into get_today_plan() after calling this."""
    from . import account_state as acct_state
    acct_state.set_state(account, **fields)


def _get_symbol_sector(ticker: str) -> str:
    """Thin wrapper -- the real implementation moved to
    sector_analysis.get_symbol_sector() so mcp/analysis/symbol_context.py
    can share it too instead of a second drifting copy."""
    from sector_analysis import get_symbol_sector
    return get_symbol_sector(ticker)


def _resolve_watchlist_price(ticker, yield_data):
    """Price first from get_yield_on_capital's own cheap fetch (reused, not a
    third separate call); falls back to a direct yfinance history call only
    when that resolves nothing."""
    price = yield_data.get("price")
    if price is not None:
        return price
    import yfinance as yf
    hist = yf.Ticker(ticker).history(period="1d")
    return float(hist["Close"].iloc[-1]) if len(hist) else None


def _resolve_real_iv(yield_data):
    """Real current IV from the yield fetch above (ADR 0001 step 6, call
    side checked first) instead of silently falling back to iv_rank's
    HV-proxy the way this call used to."""
    for side in ("call", "put"):
        side_data = yield_data.get(side)
        if side_data and side_data.get("iv") is not None:
            return side_data["iv"]
    return None


def analyze_watchlist_symbol(ticker: str) -> dict:
    """The combined view the trader asked for: heat/conviction (the SAME
    treatment real positions get via enhanced_metrics.get_ticker_metrics),
    sector + trend-vertical tags, IV Rank, and annualized yield-on-capital --
    combined per the trader's explicit direction, not two disconnected
    checks."""
    from enhanced_metrics import get_ticker_metrics
    from iv_rank import get_iv_rank
    from premium_yield import get_yield_on_capital
    from trend_verticals import get_verticals_for_ticker

    ticker = ticker.upper().strip()
    yield_data = get_yield_on_capital(ticker)
    price = _resolve_watchlist_price(ticker, yield_data)
    metrics = get_ticker_metrics(ticker, price, option_type=None) if price else {"error": "no_price"}
    iv = get_iv_rank(ticker, current_iv=_resolve_real_iv(yield_data))
    sector = _get_symbol_sector(ticker)
    verticals = get_verticals_for_ticker(ticker)

    return _to_native({
        "symbol": ticker,
        "price": price,
        "sector": sector,
        "verticals": verticals,
        "heat_status": metrics.get("heat_status"),
        "heat_reason": metrics.get("heat_reason"),
        "conviction": metrics.get("conviction"),
        "rsi": metrics.get("rsi"),
        "iv_rank": iv.get("iv_rank"),
        "iv_entry_signal": iv.get("entry_signal"),
        "yield_on_capital": yield_data,
    })


_REPORT_METHODS = {
    "daily": "generate_daily_report",
    "weekly": "generate_weekly_report",
    "biweekly": "generate_biweekly_report",
    "monthly": "generate_monthly_report",
}


def get_report_text(report_type: str) -> str:
    """The full report text generate_all_reports() writes to logs/*.md --
    used internally by extract_markdown_section() below, not surfaced raw
    to the dashboard any more (see docs/DASHBOARD_PLAN.md's "Rejected
    approaches" -- a raw-text dump per report type just moved the reports'
    own duplication into a dropdown instead of removing it).
    """
    method_name = _REPORT_METHODS.get(report_type)
    if not method_name:
        raise ValueError(f"Unknown report_type '{report_type}' (expected one of {list(_REPORT_METHODS)})")
    gen = _get_generator()
    return getattr(gen, method_name)()


def extract_section_from_text(text: str, start_marker: str, end_marker: str = None) -> str:
    """Pulls one section's markdown out of a full report by its own real
    heading text instead of re-deriving it -- how Sector Heat / Risk & Macro
    / India's 6-Month Plan reach the dashboard as ONE deduplicated section
    while still tracing back to the report engine's own computation.
    start_marker is matched as a substring (no need for the full heading
    incl. dynamic counts); end_marker, if omitted, cuts at the next "## "
    heading or end of text."""
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return f"_Section not found: {start_marker}_"
    search_from = start_idx + len(start_marker)
    if end_marker:
        end_idx = text.find(end_marker, search_from)
    else:
        end_idx = text.find("\n## ", search_from)
    section = text[start_idx:end_idx] if end_idx != -1 else text[start_idx:]
    return section.strip()


def extract_markdown_section(report_type: str, start_marker: str, end_marker: str = None) -> str:
    """extract_section_from_text() over a US report_type's full text."""
    return extract_section_from_text(get_report_text(report_type), start_marker, end_marker)


_ACCOUNT_A_NAME = "Account A (232)"
_DTE_BUCKET_TARGETS = {'near': (10, 15), 'core': (35, 40), 'mid': (20, 24), 'far': (10, 15)}
_DTE_BUCKET_LABELS = {'near': 'Near (<60 DTE)', 'core': 'Core (60-135 DTE)', 'mid': 'Mid (135-195 DTE)', 'far': 'Far (195+ DTE)'}


def _dte_bucket(dte):
    import pandas as pd
    if pd.isna(dte):
        return 'unknown'
    if dte < 60:
        return 'near'
    if dte < 135:
        return 'core'
    if dte < 195:
        return 'mid'
    return 'far'


def _load_account_a_options(gen, today):
    """Account A's real open option positions with notional/DTE/bucket
    columns added -- the same real per-leg data
    unified_master_report_production.py's Section 6 already computes from
    (see get_cash_margin_forecast's docstring)."""
    import pandas as pd
    opt = gen.open_positions[
        (gen.open_positions['account_name'] == _ACCOUNT_A_NAME) &
        (gen.open_positions['option_type'].isin(['C', 'P']))
    ].copy()
    opt['px'] = opt['ticker'].map(gen.prices).fillna(0)
    opt['notional'] = opt['px'] * opt['net_quantity'].abs() * 100
    opt['expiry_dt'] = pd.to_datetime(opt['expiry_date'], errors='coerce')
    opt['dte'] = (opt['expiry_dt'] - pd.Timestamp(today)).dt.days
    opt['bucket'] = opt['dte'].apply(_dte_bucket)
    return opt


def _build_dte_buckets(opt, total_n):
    by_bucket = opt.groupby('bucket')['notional'].sum()
    buckets = []
    for b in ['near', 'core', 'mid', 'far']:
        pct = (by_bucket.get(b, 0) / total_n * 100) if total_n else 0
        lo, hi = _DTE_BUCKET_TARGETS[b]
        status = "ok" if lo <= pct <= hi else ("light" if pct < lo else "heavy")
        buckets.append({"label": _DTE_BUCKET_LABELS[b], "pct": round(pct, 1), "target_lo": lo, "target_hi": hi, "status": status})
    return buckets


def _build_top_expiry_dates(opt, total_n):
    by_date = opt.groupby(opt['expiry_dt'].dt.date)['notional'].sum().sort_values(ascending=False)
    top_dates = []
    for d, n in by_date.head(5).items():
        pct = n / total_n * 100 if total_n else 0
        top_dates.append({"date": str(d), "notional": round(float(n), 2), "pct": round(pct, 1),
                           "status": "over" if pct > 25 else ("edge" if pct > 20 else "ok")})
    return top_dates


def _resolve_cash_reserve_info():
    """Emergency reserve -- was hardcoded to a stale $200K literal (ADR
    0001, found 2026-11-03), then replaced with a live read from
    account_state.py falling back to a second hardcoded guess ($140K,
    issue #54) when account_state had no real figure on file. That second
    fallback repeated the exact bug ADR 0001 fixed one layer up: a guessed
    dollar figure silently standing in for real data, with
    reserve_days_stale reporting None (no staleness signal at all) even
    though the number itself was never real.

    Per ADR 0001's own precedent (account_state.py's `days_stale is None`
    already means "no data on file" elsewhere, e.g. get_today_plan's
    "inactive" branch), the correct behavior is to surface "unavailable"
    explicitly rather than substitute a guess. Returns (emergency_reserve,
    reserve_days_stale) -- emergency_reserve is None when account_state has
    never recorded a real value, and callers must treat that as
    "unavailable", never as $0 or a safe-by-default number."""
    from . import account_state as acct_state
    a_state = acct_state.get_state("A") or {}
    emergency_reserve = a_state.get("emergency_reserve")
    return emergency_reserve, a_state.get("days_stale")


def get_cash_margin_forecast():
    """Crash-scenario cash requirement + expiry-curve concentration for
    Account A (the only margin account) -- the SAME formulas
    unified_master_report_production.py's Section 6 already computes
    (18%-of-notional model, 15-20% stress range, near/core/mid/far DTE
    bands, single-date cliff check), reshaped as structured JSON instead
    of only being reachable as report text. Verified against the report's
    own live output 2026-09-25 (this and Section 6 must always agree,
    since they're the identical computation over the same live position
    data -- see docs/DASHBOARD_PLAN.md's "no rewrite" boundary).
    """
    from datetime import date
    from accounts_config import ACCOUNTS_CONFIG

    gen = _get_generator()
    today = date.today()

    opt = _load_account_a_options(gen, today)
    total_n = opt['notional'].sum()
    buckets = _build_dte_buckets(opt, total_n)
    top_dates = _build_top_expiry_dates(opt, total_n)

    opt_req = gen.option_requirements.get(_ACCOUNT_A_NAME, 0)
    stress_low = total_n * 0.15 * 0.18
    stress_high = total_n * 0.20 * 0.18
    emergency_reserve, reserve_days_stale = _resolve_cash_reserve_info()
    # issue #54: no real account_state figure on file -> surface "unavailable"
    # explicitly (None), never a guessed dollar amount compared as if it were real.
    reserve_covers_stress = emergency_reserve >= stress_high if emergency_reserve is not None else None

    return _to_native({
        "as_of": today.isoformat(),
        "total_notional": total_n,
        "opt_req": opt_req,
        "stress_low": stress_low,
        "stress_high": stress_high,
        "operating_cash_target": 100000,
        "emergency_reserve": emergency_reserve,
        "reserve_days_stale": reserve_days_stale,
        "reserve_covers_stress": reserve_covers_stress,
        "capacity": ACCOUNTS_CONFIG[_ACCOUNT_A_NAME].get('capacity'),
        "capacity_as_of": ACCOUNTS_CONFIG[_ACCOUNT_A_NAME].get('capacity_as_of'),
        "dte_buckets": buckets,
        "top_expiry_dates": top_dates,
    })


def get_pnl_trend():
    """MTD/YTD (from get_realized_summary, already period-computed) plus a
    QTD figure derived from the same monthly-by-account data
    get_realized_monthly_by_account() already returns -- no new premium
    computation, just a different rollup window over numbers that already
    exist.
    """
    from datetime import date
    from realized_pnl import get_realized_summary, get_realized_monthly_by_account

    summary = get_realized_summary()
    monthly = get_realized_monthly_by_account()
    today = date.today()
    quarter_start_month = ((today.month - 1) // 3) * 3 + 1
    qtd_months = {f"{today.year}-{m:02d}" for m in range(quarter_start_month, today.month + 1)}

    portfolio_qtd = 0.0
    per_account_qtd = {}
    for label, months in monthly.items():
        acct_qtd = sum(v for m, v in months.items() if m in qtd_months)
        per_account_qtd[label] = acct_qtd
        portfolio_qtd += acct_qtd

    return {
        **summary,
        "portfolio_qtd_realized": portfolio_qtd,
        "per_account_qtd": per_account_qtd,
    }


_india_report_cache = None


def get_india_report_text(force_refresh: bool = False) -> str:
    """The full India weekly report -- same treatment as get_report_text():
    a real generator's output, cached (live yfinance/statement-parsing work)
    rather than re-run per hit. Called with empty credentials, same as
    india_weekly_report.py's own __main__ demo -- real behavior for this
    trader (statements-only, no live Breeze session token), not a stub."""
    global _india_report_cache
    if _india_report_cache is None or force_refresh:
        import asyncio
        from india_weekly_report import generate_india_weekly_report
        _india_report_cache = asyncio.run(generate_india_weekly_report("", "", ""))
    return _india_report_cache


def refresh_india_report():
    return get_india_report_text(force_refresh=True)


def get_india_6month_check() -> str:
    """The '## 6-MONTH PLAN TRACKING' section, extracted from the real
    India report text (see extract_section_from_text) -- not
    re-implemented, since _check_6month_plan needs the same
    positions/regime_signals the full report generation already gathers.
    """
    return extract_section_from_text(get_india_report_text(), "## 6-MONTH PLAN TRACKING")


def get_india_market_signals() -> str:
    """The '## Market Signals' section (regime, India VIX, Nifty vs
    moving averages) -- same extraction approach as the 6-month check."""
    return extract_section_from_text(get_india_report_text(), "## Market Signals")


def get_quarterly_direction(market: str) -> str:
    """The hand-authored quarterly strategic doc -- NOT auto-regenerated
    like the 4 cadence reports (a real, periodic review, not a live
    computation), so this just reads the latest one on disk rather than
    calling a generator function. Picks the highest dated
    quarterly_portfolio_direction_{market}_*.md if more than one exists.
    """
    import glob
    pattern = os.path.join(DATA_ROOT, "logs", f"quarterly_portfolio_direction_{market}_*.md")
    matches = sorted(glob.glob(pattern))
    if not matches:
        return f"_No quarterly portfolio direction doc found for market '{market}'._"
    with open(matches[-1]) as f:
        return f.read()
