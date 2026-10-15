"""Thin wrappers around the existing report engine (mcp/reports,
scripts/realized_pnl.py) and the raw YAML trackers. No report-generation
logic lives here -- every function below calls something that already
exists and just reshapes it into JSON for the dashboard. See
docs/DASHBOARD_PLAN.md (Phase 1: read-only dashboard).
"""
import sys
import os
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


def get_composite_scores():
    """Composite risk-adjusted scores for every held ticker AND every tracked
    Watchlist symbol, scored TOGETHER as one population (see mcp/reports/
    composite_score.py's module docstring for the full z-score formula and
    its revision history) -- so a new candidate's rank and z-scores reflect
    genuine standing against everything already held, not a separate
    standalone number. This is the real gap the trader flagged (a technical
    screener's "new names" don't mean anything until scored the same way,
    against the same population, as what's already held).
    """
    from composite_score import compute_composite_scores
    from realized_performance import realized_pnl_by_ticker
    from . import watchlist as _watchlist

    gen = _get_generator()
    gen.get_priority_actions()  # ensure self.metrics/premium_yields/ticker_sector_map are populated

    tracked = _watchlist.list_watchlist(tracked_only=True)
    notes_by_symbol = {row["symbol"]: row.get("notes", "") for row in tracked}
    result = compute_composite_scores(gen, [row["symbol"] for row in tracked], _WATCHLIST_SECTOR_HINTS)
    for r in result["watchlist"]:
        r["notes"] = notes_by_symbol.get(r["ticker"], "")

    # Real, realized (FIFO-matched) 90-day P&L per ticker -- a SEPARATE
    # result from the composite score above, never blended into it. Past
    # realized outcome and the current forward-looking composite score
    # answer different questions (see realized_performance.py's module
    # docstring) -- shown side by side on the dashboard, not merged into
    # one ranked list.
    held_by_ticker = {r["ticker"]: r for r in result["held"]}
    realized = realized_pnl_by_ticker(days=90)

    def _row(ticker, pnl, closed_count):
        row = held_by_ticker.get(ticker, {})
        return {
            "ticker": ticker, "realized_pnl_90d": pnl, "closed_count_90d": closed_count,
            "composite_rank": row.get("rank"), "composite_score": row.get("score"),
            "conviction": row.get("conviction"), "conviction_rank": row.get("conviction_rank"),
            "yield_pct": row.get("yield_pct"), "yield_rank": row.get("yield_rank"),
            "flags": row.get("flags"), "tail_risk": row.get("tail_risk"),
        }

    top_performers = [_row(t, pnl, cc) for t, pnl, cc in realized["ranked"][:15]]

    # Laggards -- the symmetric opposite view, never blended into the top-
    # performers list above: real realized LOSSES (not just "lowest
    # profit"), plus currently-held names with ZERO realized activity at
    # all in the window (no close means no FIFO match, so they never
    # appear in realized["ranked"] to begin with -- capital sitting in a
    # position with literally no completed, measurable result yet, which
    # is a different and arguably more important "laggard" signal than a
    # small realized loss).
    losses = [_row(t, pnl, cc) for t, pnl, cc in realized["ranked"] if pnl < 0]
    losses.sort(key=lambda r: r["realized_pnl_90d"])  # worst (most negative) first

    realized_tickers = {t for t, _pnl, _cc in realized["ranked"]}
    no_activity = [_row(t, 0.0, 0) for t in held_by_ticker if t not in realized_tickers]
    # Best-ranked-but-still-inactive first (most worth a second look --
    # good forward score, yet nothing realized in 90 days); unranked
    # (missing yield/conviction data) sort to the end.
    no_activity.sort(key=lambda r: r["composite_rank"] if r["composite_rank"] is not None else 9999)

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
    """Position Heat (per LEG) -- a different concept from the per-TICKER
    'Technical Heat' everywhere else on this dashboard (get_composite_scores,
    get_us_priority_actions, Sector Heat all read UnifiedReportProduction's
    self.metrics, which scores a stock's own RSI/Bollinger/52-week-range
    extendedness). This instead reuses analysis.heat_scanner.assess_portfolio_heat
    -- the engine behind the scan_position_heat MCP tool -- which scores each
    individual OPEN OPTION LEG by cost-to-close-vs-premium ratio, DTE, and
    strike distance: "is this specific trade in trouble," not "is this stock
    technically extended." The two never conflict because they were never
    wired together: this dashboard never showed the per-leg signal at all
    before this function existed (confirmed 2026-10-12 -- a real position,
    META $670P, was RED and 62% underwater here while invisible to every
    other dashboard view, including the Action Tracker, because none of
    them read this computation).

    Reuses report_utils.load_us_positions() -- the SAME file-based loader
    (Schwab reconstructed from transaction CSVs, no live broker API; Fidelity/
    Robinhood/Vanguard from their CSV/PDF exports; prices backfilled live from
    Yahoo) that mcp/server.py's scan_position_heat tool handler already uses,
    so this is the identical real signal already proven this session, not a
    second, parallel computation of "what's open" built from a different
    loader (scripts/open_positions_loader_v2.py, used by UnifiedReportProduction,
    has no premium_received/current_mark fields at all -- this data only
    exists via load_us_positions()'s Position/OptionLeg objects).
    """
    import asyncio
    from collections import defaultdict
    from report_utils import load_us_positions
    from heat_scanner import assess_portfolio_heat
    from regime import detect_regime
    from symbol_context import get_cached_symbol_context

    us_data = asyncio.run(load_us_positions())
    positions = us_data.get("positions", [])
    account_sources = us_data.get("account_sources", {})
    regime_str = detect_regime().get("regime", "CAUTIOUS_BULL")

    # Real position-context annotations heat_scanner.py itself has no concept
    # of (confirmed by source -- zero references to "covered"/"shares"
    # anywhere in that file): per-leg coverage, strangle pairing, and data
    # staleness. Computed here and merged into assess_portfolio_heat's output
    # afterward, keyed by (symbol, strike, expiry, option_type) -- a leg
    # identifier can collide across two accounts holding the identical
    # contract, a known rare edge case; when it happens the two accounts'
    # context is combined rather than picked arbitrarily, which is
    # conservative (a leg shows covered only if EVERY account holding it has
    # enough shares).
    context: dict[tuple, dict] = {}
    cost_to_close_by_key: dict[tuple, float] = {}

    def _key(symbol, strike, expiry, opt_type):
        return (symbol, round(float(strike), 4), expiry, opt_type)

    legs = []
    for pos in positions:
        # Covered-call allocation: real owned shares in THIS account/symbol,
        # consumed by its own call legs only (coverage doesn't cross
        # accounts in practice -- the shares and the short call have to sit
        # in the same brokerage account to actually be "covered"). Calls
        # sorted by strike ascending so the most likely to be assigned
        # (closest to/through the money) draws on available shares first.
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

        # Strangle pairing: a put + call on the same underlying/account
        # sharing an expiry is one coordinated structure, not two unrelated
        # alarms -- matches how this book's own strategy docs already treat
        # strangles.
        puts_by_expiry = defaultdict(list)
        calls_by_expiry = defaultdict(list)
        for lg in pos.option_legs:
            (calls_by_expiry if lg.option_type == "CALL" else puts_by_expiry)[lg.expiry].append(lg)
        strangle_expiries = set(puts_by_expiry) & set(calls_by_expiry)

        source_info = account_sources.get(pos.account, {})

        for lg in pos.option_legs:
            premium = abs(lg.premium_received or 0)
            if premium <= 0:
                continue  # assess_portfolio_heat can't compute loss_multiple against a zero premium
            legs.append({
                "symbol": pos.symbol,
                "option_type": lg.option_type,
                "strike": lg.strike,
                "dte": lg.dte,
                "expiry": lg.expiry,
                "premium_received": premium,
                "cost_to_close": abs(lg.current_mark or 0),
                "current_price": pos.current_price,
            })
            cost_to_close_by_key[_key(pos.symbol, lg.strike, lg.expiry, lg.option_type)] = abs(lg.current_mark or 0)

            # Shared gate/parameter bundle (symbol_context.py) -- cached
            # per symbol per day, so calling it per-leg (not per-position)
            # costs nothing extra after the first leg of a symbol, and lets
            # the earnings-within-window gate use THIS leg's own DTE rather
            # than a position-level average that could mask a near-dated
            # leg's real exposure.
            leg_ctx = get_cached_symbol_context(pos.symbol, dte=lg.dte)

            cov = leg_coverage.get(id(lg))
            k = _key(pos.symbol, lg.strike, lg.expiry, lg.option_type)
            entry = context.setdefault(k, {
                "account": pos.account,
                "accounts": set(),  # every account holding this exact contract -- see _annotate()'s dedup
                "covered": True,  # AND-combined below; True is the identity for AND
                "covered_contracts": 0, "total_contracts": 0,
                "strangle": lg.expiry in strangle_expiries,
                "data_source": source_info.get("source"),
                "data_as_of": source_info.get("as_of"),
                "days_stale": source_info.get("days_stale"),
                "sector": leg_ctx.get("sector"),
                "gates_fired": leg_ctx.get("gates_fired", []),
            })
            entry["accounts"].add(pos.account)
            if lg.option_type == "CALL":
                entry["covered"] = entry["covered"] and not cov["naked"]
                entry["covered_contracts"] += cov["covered_contracts"]
                entry["total_contracts"] += cov["total_contracts"]
            else:
                entry["covered"] = None  # not a meaningful concept for puts -- cash-secured by account design, checked separately

    if not legs:
        return _to_native({"by_color": {"RED": [], "YELLOW": [], "GREEN": [], "UNKNOWN": []},
                            "counts": {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0},
                            "regime": regime_str, "top_actions": []})

    result = assess_portfolio_heat(legs, regime_str)

    def _annotate(rows):
        # top_actions rows use "option_type"; by_color rows use "type" --
        # heat_scanner.py's own two output shapes genuinely differ (confirmed
        # directly against its source, not assumed), not something to "fix"
        # there since it's pre-existing, relied-on-elsewhere behavior.
        #
        # Cross-account collision de-dup -- real bug found 2026-10-15: when
        # the identical contract (symbol+strike+expiry+type) is held in TWO
        # accounts (confirmed real case: NVO $40C 03/19/2027, 2 contracts in
        # Account A + 1 in Account B), heat_scanner.py's LegHeat has no
        # account field at all, so both accounts' legs produce separate
        # output rows that then both get annotated from the SAME pooled
        # context entry -- showing as two apparently-identical "duplicate"
        # rows, both mislabeled with whichever account happened to populate
        # the context first. The underlying pooled math (combined
        # covered/total contracts) is intentional and correct -- see the
        # context-building comment above -- but showing it twice is not.
        # Collapse to one row per colliding key, explicitly labeled as
        # spanning multiple accounts instead of silently wrong.
        seen_keys: set[tuple] = set()
        deduped = []
        for row in rows:
            opt_type = row.get("type") or row.get("option_type")
            if not opt_type:
                deduped.append(row)
                continue
            key = _key(row["symbol"], row["strike"], row["expiry"], opt_type)
            ctx = context.get(key)
            if ctx:
                if key in seen_keys:
                    continue  # pooled contract already represented by an earlier row
                seen_keys.add(key)
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
                row["cost_to_close"] = cost_to_close_by_key.get(key, 0.0)
            deduped.append(row)
        return deduped

    for color_rows in result.get("by_color", {}).values():
        _annotate(color_rows)
    _annotate(result.get("top_actions", []))

    # Sector rollup -- "which sector is actually bleeding right now," computed
    # straight from these same real per-leg costs, not a second, differently-
    # sourced sector view (the existing per-ticker Sector Heat on this
    # dashboard reads enhanced_metrics.py's RSI/trend data; this reads real
    # open-position cost-to-close instead -- complementary, not a duplicate).
    sector_rollup: dict[str, dict] = {}
    for color, color_rows in result.get("by_color", {}).items():
        for row in color_rows:
            sec = row.get("sector") or "Unknown"
            bucket = sector_rollup.setdefault(sec, {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0, "red_cost_to_close": 0.0})
            bucket[color] = bucket.get(color, 0) + 1
            if color == "RED":
                opt_type = row.get("type") or row.get("option_type")
                cost = cost_to_close_by_key.get(_key(row["symbol"], row["strike"], row["expiry"], opt_type), 0.0)
                bucket["red_cost_to_close"] = round(bucket["red_cost_to_close"] + cost, 2)
    result["sector_rollup"] = sector_rollup

    # Grouped positions -- one record per real (symbol, account) position,
    # not per leg. Real gap found 2026-10-13: ZS (3 legs: 1 naked call + 2
    # puts) and ANET (8 legs across 2 accounts) are deliberate multi-leg
    # "stagger" campaigns the trader manages as one structure, but by_color
    # surfaced each leg as its own independent-looking alert with no sign
    # they belong together. Coverage genuinely doesn't cross accounts (a
    # call in Account A can only be covered by shares actually in Account
    # A -- see the per-leg allocation above), so (symbol, account) is the
    # correct real-world grouping key, not symbol alone. Every leg's own
    # full numbers stay in "legs" -- grouping changes presentation/ranking
    # only, nothing is hidden or averaged away.
    groups: dict[tuple, dict] = {}
    for color, color_rows in result.get("by_color", {}).items():
        for row in color_rows:
            key = (row["symbol"], row.get("account"))
            g = groups.setdefault(key, {
                "symbol": row["symbol"], "account": row.get("account"),
                "sector": row.get("sector"), "legs": [],
            })
            g["legs"].append(row)

    _COLOR_RANK = {"RED": 0, "YELLOW": 1, "UNKNOWN": 2, "GREEN": 3}
    positions = []
    for (symbol, account), g in groups.items():
        g["legs"].sort(key=lambda r: _COLOR_RANK.get(r.get("color"), 2))
        worst = g["legs"][0]
        g["worst_color"] = worst.get("color")
        g["worst_action"] = worst.get("action")
        g["leg_count"] = len(g["legs"])
        g["is_stagger"] = len(g["legs"]) > 1
        g["total_cost_to_close"] = round(sum(abs(lg.get("cost_to_close") or 0) for lg in g["legs"]), 2)
        g["naked_leg_count"] = sum(1 for lg in g["legs"] if lg.get("covered") is False)
        g["gates_fired"] = sorted({gate for lg in g["legs"] for gate in (lg.get("gates_fired") or [])})
        positions.append(g)
    positions.sort(key=lambda g: _COLOR_RANK.get(g["worst_color"], 2))
    result["positions"] = positions

    return _to_native(result)


def get_priority_sequence_cacheable():
    """Thin wrapper so sequencer.build_priority_sequence() -- which reloads
    all 8 accounts' positions AND fetches ~85 live Yahoo prices via
    get_position_heat()/get_composite_scores(), 60-90s -- gets computed ONCE
    per cache.refresh_all() cycle like every other expensive US entry,
    instead of live per-request. Real bug found 2026-10-15: /api/us/today
    called this directly on every request and timed out (15s+) every time,
    leaving the page stuck on "Loading..." forever -- the account-state
    lookup it also needs is a trivial SQLite read and was never the slow
    part; only this was."""
    from . import sequencer
    return sequencer.build_priority_sequence()


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

    CASH_FLOOR = 50_000.0
    EQUITY_FLOOR_PCT = 50.0

    state = acct_state.get_state("A")
    if full_sequence is None:
        full_sequence = get_priority_sequence_cacheable()

    context_notes = []
    cash_or_equity_stressed = False
    if state:
        if state.get("cash") is not None and state["cash"] < CASH_FLOOR:
            cash_or_equity_stressed = True
            context_notes.append(f"Cash ${state['cash']:,.0f} is below your documented ${CASH_FLOOR:,.0f} floor")
        if state.get("equity_pct") is not None and state["equity_pct"] < EQUITY_FLOOR_PCT:
            cash_or_equity_stressed = True
            context_notes.append(
                f"Equity {state['equity_pct']:.0f}% is below your documented {EQUITY_FLOOR_PCT:.0f}% bear-regime floor"
            )
        if state.get("days_stale", 0) > 3:
            context_notes.append(f"Account state is {state['days_stale']}d old -- re-check before relying on this")
    else:
        context_notes.append("No account state on file yet -- cash/equity-aware sequencing is inactive until you report one")

    tier0 = [r for r in full_sequence if r["tier"] == 0]
    tier1 = [r for r in full_sequence if r["tier"] == 1]
    tier2 = [r for r in full_sequence if r["tier"] == 2]

    plan = []
    for r in tier0:
        label = r["symbol"] if r["tier_source"] == "position_heat" else r.get("ticker")
        plan.append({"section": "GATE", "action": f"Review gate on {label}", "why": "Gate fired -- address before anything else, regardless of severity/score.", "ref": r})

    # Margin-relief-first, ONLY when cash/equity is actually stressed --
    # same logic already used live for GEV/MA/ULTA on 2026-10-15: among
    # profitable (HARVEST_RESTAGGER) calls, largest strike/collateral first,
    # since that's real margin relief at the least cost to close.
    if cash_or_equity_stressed:
        relief_candidates = []
        for r in tier1:
            if r["tier_source"] != "position_heat":
                continue
            for lg in r["legs"]:
                if lg.get("type") == "CALL" and lg.get("action") == "HARVEST_RESTAGGER":
                    relief_candidates.append((r, lg))
        relief_candidates.sort(key=lambda pair: -(pair[1].get("strike") or 0))
        for r, lg in relief_candidates[:5]:
            plan.append({
                "section": "CASH RELIEF FIRST",
                "action": f"Close {r['symbol']} ${lg['strike']:.0f} CALL ({r['account']}, exp {lg['expiry']})",
                "why": f"{'; '.join(context_notes)}. Profitable and large strike -- real margin relief before cutting hard-stop losses below.",
                "detail": lg["reason"],
                "ref": r,
            })

    for r in tier1[:10]:
        legs = r["legs"]
        worst = legs[0]
        plan.append({
            "section": "MANAGE HARD STOPS",
            "action": f"{worst['action']} {r['symbol']} ({r['account']}, {r['leg_count']} leg(s))",
            "why": worst["reason"],
            "ref": r,
        })

    for r in tier2[:5]:
        plan.append({
            "section": "NEW ENTRY CANDIDATES",
            "action": f"ENTER {r['ticker']}",
            "why": f"score={r.get('score')} (rank {r.get('rank')}/{r.get('population_size')}), iv_rank={r.get('iv_rank')}",
            "ref": r,
        })

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


def analyze_watchlist_symbol(ticker: str) -> dict:
    """The combined view the trader asked for: heat/conviction (the SAME
    enhanced_metrics.get_ticker_metrics real positions get -- no separate,
    lesser treatment for a candidate not yet held), sector + trend-vertical
    tags, IV Rank (richness relative to the stock's OWN history), and
    annualized yield-on-capital (opportunity cost vs. other candidates for
    the same capital) -- combined, per the trader's explicit direction,
    not treated as two separate, disconnected checks.
    """
    from enhanced_metrics import get_ticker_metrics
    from iv_rank import get_iv_rank
    from premium_yield import get_yield_on_capital
    from trend_verticals import get_verticals_for_ticker

    ticker = ticker.upper().strip()

    # Price first (from a cheap history call inside get_yield_on_capital's
    # own fetch, but get_ticker_metrics needs it passed in) -- reuse
    # premium_yield's own live fetch rather than a third separate call.
    yield_data = get_yield_on_capital(ticker)
    price = yield_data.get("price")
    if price is None:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="1d")
        price = float(hist["Close"].iloc[-1]) if len(hist) else None

    metrics = get_ticker_metrics(ticker, price, option_type=None) if price else {"error": "no_price"}
    iv = get_iv_rank(ticker)
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
    heading text, rather than re-deriving that section's content with new
    logic. This is how Sector Heat / Risk & Macro / India's 6-Month Plan
    reach the dashboard as ONE deduplicated section (shown once) while
    still tracing back to the exact same computation the report engine
    already does -- no second, drifting implementation of that logic.

    start_marker: exact heading text to search for (e.g. "## Section 6:")
    -- matched as a substring so a caller doesn't need the full heading
    including its dynamic counts. end_marker: exact next-heading text; if
    omitted, cuts at the next line starting with "## " (a level-2 heading)
    after start_marker, or end of text if there isn't one.
    """
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
    import pandas as pd
    from datetime import date
    from accounts_config import ACCOUNTS_CONFIG

    gen = _get_generator()
    today = date.today()
    acct_a_name = "Account A (232)"

    opt = gen.open_positions[
        (gen.open_positions['account_name'] == acct_a_name) &
        (gen.open_positions['option_type'].isin(['C', 'P']))
    ].copy()
    opt['px'] = opt['ticker'].map(gen.prices).fillna(0)
    opt['notional'] = opt['px'] * opt['net_quantity'].abs() * 100
    opt['expiry_dt'] = pd.to_datetime(opt['expiry_date'], errors='coerce')
    opt['dte'] = (opt['expiry_dt'] - pd.Timestamp(today)).dt.days
    total_n = opt['notional'].sum()

    def bucket(dte):
        if pd.isna(dte):
            return 'unknown'
        if dte < 60:
            return 'near'
        if dte < 135:
            return 'core'
        if dte < 195:
            return 'mid'
        return 'far'

    opt['bucket'] = opt['dte'].apply(bucket)
    by_bucket = opt.groupby('bucket')['notional'].sum()
    targets = {'near': (10, 15), 'core': (35, 40), 'mid': (20, 24), 'far': (10, 15)}
    labels = {'near': 'Near (<60 DTE)', 'core': 'Core (60-135 DTE)', 'mid': 'Mid (135-195 DTE)', 'far': 'Far (195+ DTE)'}
    buckets = []
    for b in ['near', 'core', 'mid', 'far']:
        pct = (by_bucket.get(b, 0) / total_n * 100) if total_n else 0
        lo, hi = targets[b]
        status = "ok" if lo <= pct <= hi else ("light" if pct < lo else "heavy")
        buckets.append({"label": labels[b], "pct": round(pct, 1), "target_lo": lo, "target_hi": hi, "status": status})

    by_date = opt.groupby(opt['expiry_dt'].dt.date)['notional'].sum().sort_values(ascending=False)
    top_dates = []
    for d, n in by_date.head(5).items():
        pct = n / total_n * 100 if total_n else 0
        top_dates.append({
            "date": str(d), "notional": round(float(n), 2), "pct": round(pct, 1),
            "status": "over" if pct > 25 else ("edge" if pct > 20 else "ok"),
        })

    opt_req = gen.option_requirements.get(acct_a_name, 0)
    stress_low = total_n * 0.15 * 0.18
    stress_high = total_n * 0.20 * 0.18
    emergency_reserve = 200000
    operating_cash_target = 100000

    return _to_native({
        "as_of": today.isoformat(),
        "total_notional": total_n,
        "opt_req": opt_req,
        "stress_low": stress_low,
        "stress_high": stress_high,
        "operating_cash_target": operating_cash_target,
        "emergency_reserve": emergency_reserve,
        "reserve_covers_stress": emergency_reserve >= stress_high,
        "capacity": ACCOUNTS_CONFIG[acct_a_name].get('capacity'),
        "capacity_as_of": ACCOUNTS_CONFIG[acct_a_name].get('capacity_as_of'),
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
    """The full India weekly report -- same treatment as the US
    get_report_text(): a real, existing generator function's output,
    cached (India's own report also does live yfinance/statement-parsing
    work) rather than re-run on every dashboard hit. Called with empty
    credentials, same as india_weekly_report.py's own __main__ demo --
    real behavior for this trader (statements-only, no live Breeze
    session token kept lying around), not a stub.
    """
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
