"""
IV Rank and IV Percentile calculation.
Uses Schwab price history to compute historical volatility range,
then scores current IV against 52-week range.
"""

import math
from typing import Optional
import yfinance as yf


def _historical_volatility(closes: list[float], window: int = 30) -> float:
    """Annualised HV from daily closes using log returns."""
    if len(closes) < window + 1:
        return 0.0
    returns = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    recent = returns[-window:]
    mean = sum(recent) / len(recent)
    variance = sum((r - mean) ** 2 for r in recent) / (len(recent) - 1)
    return math.sqrt(variance * 252)


def get_iv_rank(symbol: str, current_iv: Optional[float] = None) -> dict:
    """
    Returns IV Rank (0-100) and IV Percentile for a symbol.
    Fetches 1yr of daily closes via yfinance (fallback if Schwab unavailable).
    If current_iv is not provided, estimates from recent HV.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        closes = hist["Close"].tolist()
        if len(closes) < 60:
            return {"symbol": symbol, "iv_rank": None, "iv_pct": None, "error": "insufficient_data"}

        # Compute rolling 30-day HV for each day in the past year
        hvs = []
        for i in range(30, len(closes)):
            hv = _historical_volatility(closes[max(0, i-30):i+1], window=30)
            hvs.append(hv)

        if not hvs:
            return {"symbol": symbol, "iv_rank": None, "iv_pct": None}

        hv_min = min(hvs)
        hv_max = max(hvs)
        current_hv = hvs[-1]

        # Use current_iv if provided (from option chain), else use current HV as proxy
        iv = current_iv if current_iv is not None else current_hv

        iv_rank = round((iv - hv_min) / (hv_max - hv_min) * 100, 1) if hv_max > hv_min else 50.0
        iv_pct = round(sum(1 for h in hvs if h < iv) / len(hvs) * 100, 1)

        return {
            "symbol": symbol,
            "iv_rank": max(0.0, min(100.0, iv_rank)),
            "iv_pct": iv_pct,
            "current_iv": round(iv * 100, 1),
            "hv_52w_low": round(hv_min * 100, 1),
            "hv_52w_high": round(hv_max * 100, 1),
            "entry_signal": iv_rank >= 40,  # IVR >= 40 required per persona
        }
    except Exception as e:
        return {"symbol": symbol, "iv_rank": None, "iv_pct": None, "error": str(e)}


def batch_iv_rank(symbols: list[str]) -> dict[str, dict]:
    """IV rank for multiple symbols."""
    return {s: get_iv_rank(s) for s in symbols}
