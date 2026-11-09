"""
Shared per-symbol gate/parameter bundle -- the single place composite_score.py
(new-entry ranking) and services.get_position_heat() (existing-position
management) both pull IV Rank, dividend yield, earnings-date proximity,
sector, and liquidity from, instead of each independently (not) computing
its own subset. Built 2026-10-12 after the composite-score review found 8
real gaps (no IV Rank, no dividend, binary valuation cliff, static
qualitative flags, no liquidity check, no earnings-date awareness, no
debt/leverage check for most names, no concentration signal) and the
decision to split them: dividend/valuation get merged into the score itself
(separate work), IV Rank/sector/liquidity stay side-by-side facts, and
earnings-date/illiquidity become GATES that can promote an item to Tier 0
of the priority sequence regardless of its score -- see
dashboard/backend/app/sequencer.py and the plan this was built from.

Does NOT fetch options Greeks data, a second option-chain pull, or anything
premium_yield.py already has -- liquidity is computed from a pre-fetched
bid/ask pair the caller already has (e.g. from premium_yield.py's put/call
dicts), passed in explicitly, matching the same optional-pre-fetched-data
pattern iv_rank.get_iv_rank(symbol, current_iv=...) already uses.
"""
import json
import os
import sys
from datetime import date, datetime
from typing import Optional

_p = os.path.dirname(os.path.abspath(__file__))
for _ in range(5):
    _cand = os.path.join(_p, "mcp", "analysis")
    if os.path.isdir(_cand):
        sys.path.insert(0, _cand)
        break
    _p = os.path.dirname(_p)
import yahoo_throttle  # noqa: F401 -- installs the global cross-process Yahoo rate limiter, must run before any yfinance call
import yfinance as yf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"))
from iv_rank import get_iv_rank
from report_utils import upcoming_earnings
from sector_analysis import get_symbol_sector

_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
_CACHE_FILE = os.path.join(_CACHE_DIR, "symbol_context_cache.json")

# A real option essentially never trades with a 10%+ relative spread unless
# it's genuinely illiquid -- matches the trader's own stated tolerance, not
# an invented number; revisit if real trading experience says otherwise.
MAX_LIQUID_SPREAD_PCT = 10.0
EARNINGS_LOOKAHEAD_DAYS = 30

# Commonly-cited "high leverage" cutoff for debt/equity (yfinance's
# debtToEquity, already x100-scaled -- 200 means debt is 2x equity). A real,
# simple heuristic, NOT sector-adjusted -- a capital-intensive utility and an
# asset-light software name shouldn't really share one threshold, but this
# is the single concrete, defensible gate the 2026-10-15 quality-vs-
# risk-parameter discussion settled on: a named, asymmetric downside risk
# (the AVGO $60-100B debt-raise case), not a trade-off to merge into score.
HIGH_LEVERAGE_DEBT_TO_EQUITY = 200.0


def _dividend_info(symbol: str) -> dict:
    """Yield, raw per-share rate, and next ex-dividend date from ONE Yahoo
    call (yield alone used to be its own function, _dividend_yield_pct --
    merged here 2026-11-03, ADR 0001 step 5, so the new DIVIDEND_RISK
    early-exercise gate doesn't need a second live fetch for the same
    ticker's info payload).

    Yield is computed directly from dividendRate/currentPrice rather than
    trusted off yfinance's own `dividendYield` field, whose scaling
    convention isn't worth gambling on -- verified live 2026-10-12 against 7
    real tickers that THIS version's `dividendYield` already IS the
    percentage (GOOGL: dividendYield=0.25, dividendRate=$0.88/$352.72=0.25%
    -- matches exactly; PFE: dividendYield=6.08, $1.72/$28.40=6.06% --
    matches), but an earlier version of this function assumed the opposite
    (fraction needing *100) and silently reported GOOGL at 25% instead of
    0.25% -- a 100x error caught only because the real number was checked,
    not assumed. Falls back to the pre-computed field only if dividendRate
    or price is unavailable.

    next_ex_dividend_date: yfinance's `exDividendDate` is a Unix timestamp
    (seconds) on this version -- converted to an ISO date, or None if
    missing/unparseable (a non-dividend-payer has none; that's a normal
    result, not a failure). KNOWN LIMITATION, verified live 2026-11-03: this
    field often holds the MOST RECENT PAST ex-div date rather than a
    confirmed future one, until the company formally declares its next date
    (real case: MU/CRM/PYPL all returned past dates the same day LMT
    returned a real future one) -- decision_engine.py's DIVIDEND_RISK gate
    already guards against this (only fires when today <= ex_div_date <=
    expiry), so a stale past date just means the gate correctly doesn't
    fire, never a false positive. Not worth a quarterly-cadence projection
    heuristic on top of an already-labeled estimate."""
    try:
        info = yf.Ticker(symbol).info
        rate = info.get("dividendRate")
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        yield_pct = round(rate / price * 100, 2) if rate and price else round(info.get("dividendYield") or 0.0, 2)
        ex_div_ts = info.get("exDividendDate")
        ex_div_date = None
        if ex_div_ts:
            try:
                ex_div_date = datetime.fromtimestamp(float(ex_div_ts)).date().isoformat()
            except Exception:
                ex_div_date = None
        return {
            "dividend_yield_pct": yield_pct,
            "dividend_rate": rate or 0.0,
            "next_ex_dividend_date": ex_div_date,
        }
    except Exception:
        return {"dividend_yield_pct": 0.0, "dividend_rate": 0.0, "next_ex_dividend_date": None}


def _quality_fields(symbol: str) -> dict:
    """Bucket-2 trade-off context (market cap, beta, leverage, profitability,
    analyst coverage) -- shown side-by-side, never merged into score, per
    the 2026-10-15 discussion: each of these is a genuine two-sided
    trade-off (small+growing vs. large+stable, thin coverage vs. crowded),
    not a one-way quality signal. beta is the one exception that DOES feed
    into score (composite_score.py risk-adjusts yield by beta directly,
    since a high yield that's purely a volatility artifact isn't really
    compensating for anything -- see that module's own comment)."""
    try:
        info = yf.Ticker(symbol).info
        return {
            "beta": info.get("beta"),
            "market_cap": info.get("marketCap"),
            "debt_to_equity": info.get("debtToEquity"),
            "profit_margin_pct": round(info.get("profitMargins") * 100, 2) if info.get("profitMargins") is not None else None,
            "analyst_count": info.get("numberOfAnalystOpinions"),
            "analyst_rating_mean": info.get("recommendationMean"),
        }
    except Exception:
        return {"beta": None, "market_cap": None, "debt_to_equity": None,
                "profit_margin_pct": None, "analyst_count": None, "analyst_rating_mean": None}


def _is_usable(entry: dict) -> bool:
    """Same convention as premium_yield.py's _is_usable: an entry is only
    worth caching if it didn't come back as a structural failure. Unlike
    yield-on-capital, a symbol genuinely having no upcoming earnings or 0%
    dividend is a normal, real result, not a failure -- only iv_rank's own
    error key (or every other field all being unresolved) marks this
    unusable."""
    return not (entry.get("iv_rank") is None and entry.get("sector") == "Unknown"
                and entry.get("dividend_yield_pct") == 0.0 and not entry.get("earnings_within_dte"))


def get_symbol_context(symbol: str, dte: Optional[int] = None,
                        bid: Optional[float] = None, ask: Optional[float] = None,
                        current_iv: Optional[float] = None) -> dict:
    """The shared bundle. `dte` is the specific option leg's days-to-expiry
    if the caller has one (Position Heat does; a fresh composite-score entry
    candidate may not yet) -- used to decide whether an upcoming earnings
    date actually falls inside THIS trade's window, not just "sometime in
    the next 30 days" in the abstract. `bid`/`ask`, if passed, come from a
    chain the caller already fetched (premium_yield.py); if omitted,
    liquidity simply isn't assessed for this call rather than triggering a
    second live chain fetch. `current_iv`, if passed (also from a chain the
    caller already fetched -- premium_yield.py's `iv` field, ADR 0001 step
    6), replaces iv_rank.get_iv_rank()'s HV-proxy fallback with the real
    current implied vol; every live caller omitted this before, so IV Rank
    was always ranking recent realized vol against its own history, never
    actual current IV richness.
    """
    iv = get_iv_rank(symbol, current_iv=current_iv)
    sector = get_symbol_sector(symbol)
    dividend = _dividend_info(symbol)
    earnings_dates = upcoming_earnings(symbol, days=EARNINGS_LOOKAHEAD_DAYS)
    quality = _quality_fields(symbol)

    gates_fired = []
    if quality.get("debt_to_equity") is not None and quality["debt_to_equity"] > HIGH_LEVERAGE_DEBT_TO_EQUITY:
        gates_fired.append("HIGH_LEVERAGE")

    earnings_within_window = earnings_dates
    if dte is not None and earnings_dates:
        cutoff = date.today().toordinal() + dte
        earnings_within_window = [
            d for d in earnings_dates if date.fromisoformat(d).toordinal() <= cutoff
        ]
    if earnings_within_window:
        gates_fired.append("EARNINGS_RISK")

    liquidity_ok, spread_pct = None, None
    if bid is not None and ask is not None and bid > 0 and ask > 0:
        mid = (bid + ask) / 2
        spread_pct = round((ask - bid) / mid * 100, 2) if mid else None
        liquidity_ok = spread_pct is not None and spread_pct <= MAX_LIQUID_SPREAD_PCT
        if liquidity_ok is False:
            gates_fired.append("ILLIQUID")

    return {
        "symbol": symbol,
        "iv_rank": iv.get("iv_rank"),
        "iv_entry_signal": iv.get("entry_signal", False),
        # The resolved vol iv_rank actually ranked against -- real current_iv
        # if a caller passed one (step 6), else its own HV-proxy fallback.
        # Computed here all along but never surfaced in this dict until now
        # (ADR 0001 step 7) -- decision_engine.py's Greeks rollup needs it.
        "current_iv": iv.get("current_iv"),
        "dividend_yield_pct": dividend["dividend_yield_pct"],
        "dividend_rate": dividend["dividend_rate"],
        "next_ex_dividend_date": dividend["next_ex_dividend_date"],
        "earnings_within_dte": earnings_within_window,
        "sector": sector,
        "liquidity_ok": liquidity_ok,
        "spread_pct": spread_pct,
        "gates_fired": gates_fired,
        **quality,
    }


def get_cached_symbol_context(symbol: str, **kwargs) -> dict:
    """Same-day cache, modeled directly on premium_yield.get_cached_batch_yield
    -- iv_rank.get_iv_rank() alone does an uncached 1-year history fetch per
    call, and this bundle also adds a dividend/earnings/sector fetch on top,
    so re-running it per symbol on every report/refresh cycle is real,
    avoidable latency and rate-limit risk for data that doesn't move
    intraday. Keyed by symbol only (dte/bid/ask are per-call context, not
    part of what's cached) -- the earnings-within-window filter is applied
    AFTER the cache read using the caller's own dte, so two different DTEs
    on the same symbol correctly see different earnings_within_dte without
    needing two cache entries.
    """
    today = date.today().isoformat()
    cache: dict = {}
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE) as f:
                stored = json.load(f)
            if stored.get("date") == today:
                cache = {s: v for s, v in stored.get("data", {}).items() if _is_usable(v)}
        except Exception:
            pass

    dte = kwargs.get("dte")
    bid, ask = kwargs.get("bid"), kwargs.get("ask")
    current_iv = kwargs.get("current_iv")

    if symbol not in cache:
        # current_iv only matters on a cache MISS -- iv_rank is baked into
        # the cached payload at first-fetch time, same as every other
        # symbol-level fact here (not re-applied per-call the way dte/bid/
        # ask-derived fields are below). Whichever caller happens to run
        # first for a symbol on a given day -- and passes a real current_iv
        # -- determines that day's cached IV Rank for every other caller.
        fresh = get_symbol_context(symbol, dte=None, current_iv=current_iv)
        if _is_usable(fresh):
            cache[symbol] = fresh
            try:
                os.makedirs(_CACHE_DIR, exist_ok=True)
                with open(_CACHE_FILE, "w") as f:
                    json.dump({"date": today, "data": cache}, f)
            except Exception:
                pass
        else:
            return fresh  # don't cache a genuinely unresolved result

    result = dict(cache[symbol])
    # Re-apply the caller's own dte/bid/ask against the cached, symbol-level
    # facts rather than re-fetching -- the earnings list and raw bid/ask
    # context differ per call even though the underlying symbol data is the
    # same for the whole day.
    gates = [g for g in result.get("gates_fired", []) if g != "EARNINGS_RISK" and g != "ILLIQUID"]
    earnings_dates = result.get("earnings_within_dte") or []
    if dte is not None and earnings_dates:
        cutoff = date.today().toordinal() + dte
        earnings_dates = [d for d in earnings_dates if date.fromisoformat(d).toordinal() <= cutoff]
    if earnings_dates:
        gates.append("EARNINGS_RISK")
    result["earnings_within_dte"] = earnings_dates

    if bid is not None and ask is not None and bid > 0 and ask > 0:
        mid = (bid + ask) / 2
        spread_pct = round((ask - bid) / mid * 100, 2) if mid else None
        result["spread_pct"] = spread_pct
        result["liquidity_ok"] = spread_pct is not None and spread_pct <= MAX_LIQUID_SPREAD_PCT
        if result["liquidity_ok"] is False:
            gates.append("ILLIQUID")
    result["gates_fired"] = gates
    return result
