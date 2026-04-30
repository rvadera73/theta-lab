"""
Indian market regime detection: BEAR_SIDEWAYS / TRANSITIONING / BULL.
Uses India VIX and Nifty 50 vs 50/200-day moving averages.

Mirrors the structure of analysis/regime.py for API consistency.
"""

import os

import yfinance as yf

from config import Regime, INDIA_REGIME_THRESHOLDS


def _get_closes(symbol: str, period: str = "1y") -> list[float]:
    try:
        hist = yf.Ticker(symbol).history(period=period)
        return hist["Close"].tolist()
    except Exception:
        return []


def _moving_average(closes: list[float], window: int) -> float:
    if len(closes) < window:
        return 0.0
    return sum(closes[-window:]) / window


def detect_india_regime() -> dict:
    """
    Returns current India regime assessment with supporting data.

    Signals checked:
      - India VIX (^INDIAVIX): < 15 = BULL, 15-25 = neutral, > 25 = BEAR
      - Nifty 50 (^NSEI) vs 50-day and 200-day MA

    Returns dict with keys: regime, new_entries_allowed, signals
    (same shape as detect_regime() in analysis/regime.py)
    """
    bull_threshold = INDIA_REGIME_THRESHOLDS["indiavix_bull_threshold"]   # 15.0
    pause_threshold = INDIA_REGIME_THRESHOLDS["indiavix_pause_threshold"]  # 25.0
    ma_days = INDIA_REGIME_THRESHOLDS["ma_days"]                           # [50, 200]

    vix_closes = _get_closes("^INDIAVIX", "3mo")
    nifty_closes = _get_closes("^NSEI", "1y")

    current_vix = vix_closes[-1] if vix_closes else None
    vix_5d_avg = sum(vix_closes[-5:]) / 5 if len(vix_closes) >= 5 else current_vix

    nifty_current = nifty_closes[-1] if nifty_closes else None
    nifty_ma50 = _moving_average(nifty_closes, ma_days[0])
    nifty_ma200 = _moving_average(nifty_closes, ma_days[1])

    signals: dict = {}
    bull_signals = 0
    bear_signals = 0

    # India VIX signal
    if current_vix is not None:
        if vix_5d_avg < bull_threshold:
            signals["india_vix"] = {
                "value": round(current_vix, 1),
                "signal": "BULL",
                "detail": f"India VIX {current_vix:.1f} sustained < {bull_threshold} — low fear",
            }
            bull_signals += 1
        elif current_vix > pause_threshold:
            signals["india_vix"] = {
                "value": round(current_vix, 1),
                "signal": "BEAR",
                "detail": f"India VIX {current_vix:.1f} > {pause_threshold} — elevated fear, pause entries",
            }
            bear_signals += 2
        else:
            signals["india_vix"] = {
                "value": round(current_vix, 1),
                "signal": "NEUTRAL",
                "detail": f"India VIX {current_vix:.1f} in neutral zone {bull_threshold}-{pause_threshold}",
            }

    # Nifty 50 vs moving averages
    if nifty_current and nifty_ma50 and nifty_ma200:
        above_50 = nifty_current > nifty_ma50
        above_200 = nifty_current > nifty_ma200
        ma_signal = (
            "BULL" if (above_50 and above_200)
            else "BEAR" if (not above_50 and not above_200)
            else "MIXED"
        )
        signals["nifty50_ma"] = {
            "current": round(nifty_current, 0),
            "ma50": round(nifty_ma50, 0),
            "ma200": round(nifty_ma200, 0),
            "above_50d": above_50,
            "above_200d": above_200,
            "signal": ma_signal,
        }
        if ma_signal == "BULL":
            bull_signals += 2
        elif ma_signal == "BEAR":
            bear_signals += 2
        else:
            bear_signals += 1

    # Determine technical regime
    if bull_signals >= 3 and bear_signals == 0:
        tech_regime = Regime.BULL
    elif bear_signals >= 3:
        tech_regime = Regime.BEAR_SIDEWAYS
    elif bull_signals > bear_signals:
        tech_regime = Regime.TRANSITIONING
    else:
        tech_regime = Regime.BEAR_SIDEWAYS

    # Trader override via env var (mirrors US pattern)
    override_env = os.getenv("INDIA_REGIME_OVERRIDE", "").strip().upper()
    if override_env in (r.value for r in Regime):
        final_regime = Regime(override_env)
        override_note = f"Trader override active: {final_regime.value} (set via INDIA_REGIME_OVERRIDE)"
    else:
        final_regime = tech_regime
        override_note = None

    return {
        "regime": final_regime.value,
        "technical_regime": tech_regime.value,
        "trader_override": override_env or None,
        "new_entries_allowed": final_regime != Regime.BEAR_SIDEWAYS,
        "signals": signals,
        "bull_signal_count": bull_signals,
        "bear_signal_count": bear_signals,
        "note": override_note or "No trader override. Using technical signals.",
    }
