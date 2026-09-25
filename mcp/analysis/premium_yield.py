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
from datetime import date, datetime
from typing import Optional

import yfinance as yf

DEFAULT_OTM_PCT = 0.10
DEFAULT_DTE_LOW = 75
DEFAULT_DTE_HIGH = 135
TARGET_DTE_MIDPOINT = 100  # centers on this book's own 90/120-day window


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
