"""
India symbol mapping + derived market-data helpers split out of
report_utils.py (Bolt b19). report_utils.py re-exports everything here so
every existing `from report_utils import X` call site keeps working
unchanged.

Deliberately NOT moved here (stay physically in report_utils.py itself):
_now/_history_cache/current_price/get_extended_hours_quote/
get_cached_extended_hours_quote/extended_hours_context/_today -- several
existing regression tests (tests/test_report_utils_cache_freshness.py,
tests/test_extended_hours_pricing.py) do
`mock.patch.object(report_utils, "<name>", ...)` and then exercise ANOTHER
report_utils function that calls `<name>` by a bare module-global name --
that only works if both the patched name and its caller are defined in the
exact same module object the test imported as `report_utils`. Moving either
half of such a pair out from under the other would silently stop the
existing test's patch from taking effect. Everything in THIS file was
confirmed (by reading every existing test) to never be the target of that
kind of cross-function module-attribute patching, so it's free to live in
its own file; it still reaches into report_utils.py for current_price()/
_today() via ordinary cross-module imports, which is unaffected by where
the code lives.
"""
from datetime import date, datetime, timedelta

import yfinance as yf

from analysis.same_day_cache import ensure_same_day
from report_utils_core import compute_rsi

_INDIA_SYMBOL_MAP = {
    "ADAGRE": "ADANIGREEN.NS",  # Adani Green Energy -- confirmed via india_6month_plan.yaml equity_adds + live yfinance 2026-09-25
    "ADAPOR": "ADANIPORTS.NS",
    "ADAPOW": "ADANIPOWER.NS",
    "ANARAJ": "ANANTRAJ.NS",
    "APOHOS": "APOLLOHOSP.NS",
    "AURPHA": "AUROPHARMA.NS",
    "BAJFI": "BAJFINANCE.NS",
    "BHAELE": "BEL.NS",
    "BILGAR": "GROWW.NS",  # Billionbrains Garage Ventures (Groww) -- confirmed via india_6month_plan.yaml equity_adds + live yfinance 2026-09-25
    "BSE": "BSE.NS",
    "DIXTEC": "DIXON.NS",
    "DLFLIM": "DLF.NS",
    "DRREDD": "DRREDDY.NS",
    "GENOVE": "GENUSPOWER.NS",
    "HCLTEC": "HCLTECH.NS",
    "HDFBAN": "HDFCBANK.NS",
    "HERHON": "HEROMOTOCO.NS",
    "HIMFUT": "HFCL.NS",  # Himachal Futuristic Communications (HFCL) -- confirmed via india_6month_plan.yaml equity_adds + live yfinance 2026-09-25
    "HINAER": "HAL.NS",
    "IDECEL": "IDEA.NS",
    "LEMTRE": "LEMONTREE.NS",
    "LIC": "LICI.NS",
    "LUPIN": "LUPIN.NS",
    "MAZDOC": "MAZDOCK.NS",
    "MTAR": "MTARTECH.NS",  # MTAR Technologies -- MTAR.NS 404s on Yahoo; MTARTECH.NS confirmed live 2026-10-04
    "STLTC": "STLTECH.NS",  # Sterlite Technologies
    "NTPC": "NTPC.NS",
    "ONE97": "PAYTM.NS",  # One97 Communications (Paytm) -- confirmed via india_config.yaml watchlist entry, real ticker already used there
    "PARDEF": "PARAS.NS",
    "POWGRI": "POWERGRID.NS",
    "RELIND": "RELIANCE.NS",
    "SOBDEV": "SOBHA.NS",  # Sobha Developers/Limited -- confirmed via india_config.yaml watchlist entry + live yfinance 2026-09-25
    "SOLIN": "SOLARINDS.NS",
    "STABAN": "SBIN.NS",
    "SUZENE": "SUZLON.NS",
    "TCS": "TCS.NS",
    "TRENT": "TRENT.NS",
    "VARBEV": "VBL.NS",
    "YATHOS": "YATHARTH.NS",
    "ZOMLIM": "ETERNAL.NS",
}

# _OPTION_CHAIN_CACHE / _EARNINGS_CACHE: plain in-process dicts, NOT
# file-backed. Found, while reading every cache in this file for the
# same-day-cache unification, to have had NO staleness check at all -- a
# dict that memoized for the entire life of the process, the same
# unbounded-cache bug class already fixed live 2026-11-05 for
# _US_PRICE_CACHE and _SNAPSHOT_HOLDINGS_CACHE (both in report_utils.py).
# Given a calendar-day bound here too via same_day_cache.ensure_same_day,
# for consistency with those two and because neither has a legitimate
# reason to serve a chain or an earnings date list fetched on a prior day.
# Each `*_DATE` holder is the "last reset day" cell ensure_same_day needs
# (see that helper's docstring for why a 1-element list, not a bare
# str/None).
_OPTION_CHAIN_CACHE: dict[tuple[str, str], object] = {}
_OPTION_CHAIN_CACHE_DATE: list = [None]
_EARNINGS_CACHE: dict[str, list[str]] = {}
_EARNINGS_CACHE_DATE: list = [None]


def yf_symbol(symbol: str, india: bool = False) -> str:
    if not india:
        return symbol
    if symbol in _INDIA_SYMBOL_MAP:
        return _INDIA_SYMBOL_MAP[symbol]
    if symbol.startswith("^") or symbol.endswith(".NS"):
        return symbol
    return f"{symbol}.NS"


def _empty_technical_snapshot(symbol: str) -> dict:
    return {
        "symbol": symbol,
        "current": 0.0,
        "rsi": None,
        "ma50": None,
        "ma200": None,
        "above_50": None,
        "above_200": None,
        "week_52_high": None,
        "week_52_low": None,
        "pct_off_high": None,
        "pe": None,
    }


def _india_trailing_pe(ticker) -> float | None:
    try:
        info = ticker.info if ticker else {}
        return info.get("trailingPE") or info.get("forwardPE")
    except Exception:
        return None


def technical_snapshot(symbol: str, india: bool = False) -> dict:
    # Deferred import -- _history_cache/_today are defined directly in
    # report_utils.py (see this module's docstring for why) and, per
    # report_utils.py's own import ordering, aren't available as module
    # attributes until report_utils.py has finished defining them (this
    # submodule is itself pulled in partway through report_utils.py's own
    # top-to-bottom execution).
    from report_utils import _history_cache

    payload = _history_cache(symbol, india)
    hist = payload.get("hist")
    ticker = payload.get("ticker")
    if hist is None or getattr(hist, "empty", True):
        return _empty_technical_snapshot(symbol)

    close = hist["Close"]
    current = float(close.iloc[-1])
    ma50 = float(close.tail(50).mean()) if len(close) >= 50 else None
    ma200 = float(close.tail(200).mean()) if len(close) >= 200 else None
    week_52_high = float(close.max()) if len(close) else None
    week_52_low = float(close.min()) if len(close) else None
    pe = _india_trailing_pe(ticker) if india else None
    return {
        "symbol": symbol,
        "current": current,
        "rsi": compute_rsi(close, 14),
        "ma50": round(ma50, 2) if ma50 else None,
        "ma200": round(ma200, 2) if ma200 else None,
        "above_50": current > ma50 if ma50 else None,
        "above_200": current > ma200 if ma200 else None,
        "week_52_high": round(week_52_high, 2) if week_52_high else None,
        "week_52_low": round(week_52_low, 2) if week_52_low else None,
        "pct_off_high": round((current - week_52_high) / week_52_high * 100, 1) if week_52_high else None,
        "pe": round(float(pe), 2) if pe else None,
    }


def upcoming_earnings(symbol: str, days: int = 14) -> list[str]:
    from report_utils import _today

    ensure_same_day(_EARNINGS_CACHE, _EARNINGS_CACHE_DATE, _today())
    if symbol in _EARNINGS_CACHE:
        return _EARNINGS_CACHE[symbol]
    found: list[str] = []
    try:
        cal = yf.Ticker(symbol).calendar
        if hasattr(cal, "index"):
            if "Earnings Date" in getattr(cal, "index", []):
                values = cal.loc["Earnings Date"]
                for value in values if hasattr(values, "tolist") else [values]:
                    dt = getattr(value, "to_pydatetime", lambda: value)()
                    if isinstance(dt, datetime):
                        found.append(dt.date().isoformat())
            elif hasattr(cal, "columns") and "Earnings Date" in cal.columns:
                for value in cal["Earnings Date"].tolist():
                    if value is not None:
                        dt = getattr(value, "to_pydatetime", lambda: value)()
                        if isinstance(dt, datetime):
                            found.append(dt.date().isoformat())
        elif isinstance(cal, dict):
            values = cal.get("Earnings Date") or []
            for value in values if isinstance(values, list) else [values]:
                if hasattr(value, "date"):
                    found.append(value.date().isoformat())
    except Exception:
        pass
    cutoff = date.today() + timedelta(days=days)
    filtered = []
    for raw in found:
        try:
            dt = date.fromisoformat(raw)
            if date.today() <= dt <= cutoff:
                filtered.append(raw)
        except Exception:
            continue
    _EARNINGS_CACHE[symbol] = filtered
    return filtered


def parse_option_symbol(symbol: str) -> dict | None:
    import re

    match = re.match(r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$", str(symbol).strip())
    if not match:
        return None
    return {
        "symbol": match.group(1),
        "expiry": datetime.strptime(match.group(2), "%m/%d/%Y").date().isoformat(),
        "strike": float(match.group(3)),
        "option_type": "CALL" if match.group(4) == "C" else "PUT",
    }


def _get_cached_option_chain(symbol: str, expiry: str):
    """ensure_same_day-gated per-(symbol, expiry) option chain cache, shared
    by option_market_price()/option_probability_itm() -- no extra fetch if
    the same pair was already looked up earlier this run."""
    from report_utils import _today

    ensure_same_day(_OPTION_CHAIN_CACHE, _OPTION_CHAIN_CACHE_DATE, _today())
    key = (symbol, expiry)
    chain = _OPTION_CHAIN_CACHE.get(key)
    if chain is None:
        try:
            chain = yf.Ticker(symbol).option_chain(expiry)
        except Exception:
            chain = None
        _OPTION_CHAIN_CACHE[key] = chain
    return chain


def _closest_strike_row(chain, option_type: str, strike: float):
    """The chain row whose strike is closest to `strike`, or None if the
    calls/puts table is missing/empty or the closest strike isn't within
    $0.01 of the requested one."""
    table = chain.calls if option_type == "CALL" else chain.puts
    if table is None or table.empty:
        return None
    row = table.loc[(table["strike"] - float(strike)).abs().idxmin()]
    if abs(float(row["strike"]) - float(strike)) > 0.01:
        return None
    return row


def option_market_price(symbol: str, expiry: str, strike: float, option_type: str) -> float | None:
    chain = _get_cached_option_chain(symbol, expiry)
    if chain is None:
        return None
    try:
        row = _closest_strike_row(chain, option_type, strike)
        if row is None:
            return None
        bid = float(row.get("bid", 0) or 0)
        ask = float(row.get("ask", 0) or 0)
        last = float(row.get("lastPrice", 0) or 0)
        if bid and ask:
            return round((bid + ask) / 2, 2)
        return round(last, 2) if last else None
    except Exception:
        return None


def option_probability_itm(symbol: str, expiry: str, strike: float, option_type: str, spot: float) -> float | None:
    """Risk-neutral probability the contract finishes ITM at expiry. Uses
    the contract's own live implied vol (same cached chain as
    option_market_price -- no extra fetch if that was already called for
    this symbol/expiry this run) and delegates the actual d2/probability
    math to enhanced_metrics.BlackScholesGreeks.d2 -- that class was
    already imported into the production report and never instantiated
    (see unified_master_report_production.py's Section 7 comment); this is
    its first real caller rather than a second hand-rolled Black-Scholes
    implementation. Risk-free rate fixed at 0 -- no existing call site in
    this codebase sets one, and it's immaterial at these DTEs.
    Returns None if spot/strike/IV aren't all usable (matches
    option_market_price's fail-quiet convention -- callers already handle
    a None price the same way).
    Trader-facing meaning: for a short PUT this is "probability of
    assignment"; for a short CALL, "probability of being exercised against."
    """
    from enhanced_metrics import BlackScholesGreeks
    from scipy.stats import norm

    chain = _get_cached_option_chain(symbol, expiry)
    if chain is None or not spot or spot <= 0 or not strike or strike <= 0:
        return None
    try:
        row = _closest_strike_row(chain, option_type, strike)
        if row is None:
            return None
        iv = float(row.get("impliedVolatility", 0) or 0)
        if iv <= 0:
            return None
        expiry_date = date.fromisoformat(expiry)
        T = max((expiry_date - date.today()).days, 0) / 365.0
        if T <= 0:
            return 1.0 if (option_type == "PUT") == (spot < strike) else 0.0
        d2 = BlackScholesGreeks.d2(spot, strike, T, 0, iv)
        # P(S_T < K) for a put's assignment risk, P(S_T > K) for a call's
        # exercise risk -- both expressed as "probability this leg finishes
        # against the seller."
        return round(float(norm.cdf(-d2)) if option_type == "PUT" else float(norm.cdf(d2)), 4)
    except Exception:
        return None
