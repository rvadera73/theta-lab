"""Real, live annualized yield-on-capital for a ~10% OTM put/call at
roughly this book's own 90/120-day strategy window -- the metric that came
out of comparing WMT vs BABA/TSM live 2026-09-25 (WMT: ~7% annualized;
BABA: ~15-20%; TSM: ~12-14%, same OTM%/DTE target). Answers "for the same
$X of capital, which name actually pays more" -- opportunity cost, not
richness relative to the stock's own history (that's iv_rank.py's job).
Deliberately a separate, single-purpose module rather than folded into
iv_rank.py or enhanced_metrics.py -- this is genuinely a different
question (capital efficiency vs. volatility-richness) with a different
data need (a live option chain, not just price history).
"""
import json
import os
from datetime import date, datetime
from typing import Optional

import yfinance as yf

DEFAULT_OTM_PCT = 0.10
DEFAULT_DTE_LOW = 75
DEFAULT_DTE_HIGH = 135
TARGET_DTE_MIDPOINT = 100  # centers on this book's own 90/120-day window

# "Rich" cutoff for the Sector Heat "thin/rich premium" labeling -- replaced
# an IV-Rank->=40-vs-own-history check 2026-09-30 after live verification
# (PFE, SBUX) showed IV Rank can read anywhere while real annualized yield
# stays genuinely thin, since IV Rank never compares to market/sector vol or
# to what a dollar of capital actually earns. 15% annualized is the
# trader's own chosen bar (upper end of this book's stated "quality bucket"
# target range, 10-15% annualized, from the AI capex playbook) -- not an
# invented threshold.
RICH_YIELD_THRESHOLD_PCT = 15.0

_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
_CACHE_FILE = os.path.join(_CACHE_DIR, "premium_yield_cache.json")


def _pick_expiry(ticker_obj, today, dte_low, dte_high):
    best, best_dte = None, None
    for e in ticker_obj.options:
        exp_date = datetime.strptime(e, "%Y-%m-%d").date()
        dte = (exp_date - today).days
        if dte_low <= dte <= dte_high:
            if best is None or abs(dte - TARGET_DTE_MIDPOINT) < abs(best_dte - TARGET_DTE_MIDPOINT):
                best, best_dte = e, dte
    return best, best_dte


def get_yield_on_capital(
    symbol: str,
    otm_pct: float = DEFAULT_OTM_PCT,
    dte_low: int = DEFAULT_DTE_LOW,
    dte_high: int = DEFAULT_DTE_HIGH,
) -> dict:
    """Live put AND call yield-on-capital at the nearest ~otm_pct strike,
    nearest expiry inside [dte_low, dte_high] DTE. Returns an error key
    (never raises) so a batch caller can skip a bad symbol without the
    whole run failing -- same convention as iv_rank.get_iv_rank.
    """
    try:
        t = yf.Ticker(symbol)
        today = date.today()
        hist = t.history(period="1d")
        if len(hist) == 0:
            return {"symbol": symbol, "error": "no_price_data"}
        price = float(hist["Close"].iloc[-1])

        expiry, dte = _pick_expiry(t, today, dte_low, dte_high)
        if not expiry:
            return {"symbol": symbol, "error": f"no_expiry_in_{dte_low}-{dte_high}_dte_window"}

        chain = t.option_chain(expiry)
        puts, calls = chain.puts, chain.calls
        if len(puts) == 0 or len(calls) == 0:
            return {"symbol": symbol, "error": "empty_option_chain"}

        put_target = price * (1 - otm_pct)
        call_target = price * (1 + otm_pct)
        put_row = puts.iloc[(puts["strike"] - put_target).abs().argsort()[:1]]
        call_row = calls.iloc[(calls["strike"] - call_target).abs().argsort()[:1]]

        def _yield_for(row, capital):
            if len(row) == 0 or capital is None or capital <= 0:
                return None
            bid, ask = float(row["bid"].values[0]), float(row["ask"].values[0])
            if bid == 0.0 and ask == 0.0:
                # A real option essentially never has a simultaneous zero
                # bid AND zero ask unless it's worthless -- found live
                # 2026-10-02: every single ticker's chain came back with
                # bid=ask=0.0 for strikes that are clearly not worthless
                # (e.g. COIN $210C, AXON $460C), meaning this is Yahoo not
                # having live quotes available (after-hours/no-data), not a
                # real zero premium. Returning None here instead of a false,
                # confident "0% annualized (thin)" that would otherwise get
                # cached for the rest of the day and silently mislabel the
                # whole book as thin on a day with no real data, not a day
                # with genuinely worthless options.
                return None
            mid = (bid + ask) / 2
            premium = mid * 100
            annualized = (premium / capital) * (365 / dte) * 100
            return {
                "strike": float(row["strike"].values[0]),
                "bid": bid, "ask": ask, "mid": round(mid, 2),
                "premium_dollars": round(premium, 2),
                "capital_required": round(capital, 2),
                "annualized_yield_pct": round(annualized, 2),
            }

        put_capital = float(put_row["strike"].values[0]) * 100 if len(put_row) else None
        call_capital = price * 100  # notional basis -- a covered call's real "capital" is the shares already owned

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "expiry": expiry,
            "dte": dte,
            "put": _yield_for(put_row, put_capital),
            "call": _yield_for(call_row, call_capital),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def batch_get_yield_on_capital(symbols: list[str], **kwargs) -> dict[str, dict]:
    return {s: get_yield_on_capital(s, **kwargs) for s in symbols}


def average_annualized_yield(entry: Optional[dict]) -> Optional[float]:
    """One summarizing richness number per ticker -- mean of put/call
    annualized_yield_pct, whichever side(s) resolved. Returns None if
    neither side has real data (e.g. empty_option_chain)."""
    if not entry:
        return None
    vals = [entry[side]["annualized_yield_pct"] for side in ("put", "call")
            if entry.get(side) and entry[side].get("annualized_yield_pct") is not None]
    return sum(vals) / len(vals) if vals else None


def get_cached_batch_yield(symbols: list[str], **kwargs) -> dict[str, dict]:
    """Batch yield-on-capital, cached once per calendar day and reused
    across every report type generated that day (daily/weekly/biweekly/
    monthly) -- trader-confirmed 2026-09-30. Unlike IV Rank (price-history
    only, cheap), this needs one live option-chain fetch PER TICKER;
    re-fetching all 92 on every report run is real, avoidable latency and
    yfinance rate-limit risk for strikes 90-135 DTE out that don't move
    enough intraday to justify a same-day re-fetch. A stale cache from a
    prior day is never reused -- the date check below forces a fresh pull
    the first time any report runs on a new day.
    """
    today = date.today().isoformat()
    cache: dict = {}
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE) as f:
                stored = json.load(f)
            if stored.get("date") == today:
                cache = stored.get("data", {})
        except Exception:
            pass

    missing = [s for s in symbols if s not in cache]
    if missing:
        cache.update(batch_get_yield_on_capital(missing, **kwargs))
        try:
            os.makedirs(_CACHE_DIR, exist_ok=True)
            with open(_CACHE_FILE, "w") as f:
                json.dump({"date": today, "data": cache}, f)
        except Exception:
            pass

    return {s: cache[s] for s in symbols if s in cache}
