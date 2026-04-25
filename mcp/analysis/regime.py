"""
Market regime detection: BEAR_SIDEWAYS / TRANSITIONING / BULL.
Uses VIX, S&P 500 MA relationship, and put/call ratio.
"""

import yfinance as yf
from config import Regime, REGIME_SIGNALS


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


def detect_regime() -> dict:
    """
    Returns current regime assessment with supporting data.
    Signals checked: VIX level, S&P 500 vs 50/200-day MA.
    """
    vix_closes = _get_closes("^VIX", "3mo")
    spx_closes = _get_closes("^GSPC", "1y")

    current_vix = vix_closes[-1] if vix_closes else None
    vix_5d_avg = sum(vix_closes[-5:]) / 5 if len(vix_closes) >= 5 else current_vix

    spx_current = spx_closes[-1] if spx_closes else None
    spx_ma50 = _moving_average(spx_closes, 50)
    spx_ma200 = _moving_average(spx_closes, 200)

    signals = {}
    bull_signals = 0
    bear_signals = 0

    # VIX signal
    if current_vix is not None:
        if vix_5d_avg < REGIME_SIGNALS["vix_bull_threshold"]:
            signals["vix"] = {"value": round(current_vix, 1), "signal": "BULL", "detail": f"VIX {current_vix:.1f} sustained < 20"}
            bull_signals += 1
        elif current_vix > REGIME_SIGNALS["vix_pause_threshold"]:
            signals["vix"] = {"value": round(current_vix, 1), "signal": "BEAR", "detail": f"VIX {current_vix:.1f} > 35 — pause entries"}
            bear_signals += 2
        else:
            signals["vix"] = {"value": round(current_vix, 1), "signal": "NEUTRAL", "detail": f"VIX {current_vix:.1f} in neutral zone 20-35"}

    # S&P vs MAs
    if spx_current and spx_ma50 and spx_ma200:
        above_50 = spx_current > spx_ma50
        above_200 = spx_current > spx_ma200
        ma_signal = "BULL" if (above_50 and above_200) else "BEAR" if (not above_50 and not above_200) else "MIXED"
        signals["sp500_ma"] = {
            "current": round(spx_current, 0),
            "ma50": round(spx_ma50, 0),
            "ma200": round(spx_ma200, 0),
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

    # Determine overall regime
    if bull_signals >= 3 and bear_signals == 0:
        regime = Regime.BULL
    elif bear_signals >= 3:
        regime = Regime.BEAR_SIDEWAYS
    elif bull_signals > bear_signals:
        regime = Regime.TRANSITIONING
    else:
        regime = Regime.BEAR_SIDEWAYS

    # Trader override: current stated view is BEAR_SIDEWAYS through Oct/Nov 2026
    trader_override = Regime.BEAR_SIDEWAYS
    final_regime = trader_override  # trader view takes precedence until override removed

    return {
        "regime": final_regime.value,
        "technical_regime": regime.value,
        "trader_override": trader_override.value,
        "new_entries_allowed": final_regime != Regime.BEAR_SIDEWAYS,
        "signals": signals,
        "bull_signal_count": bull_signals,
        "bear_signal_count": bear_signals,
        "note": "Trader override active: BEAR_SIDEWAYS through Oct/Nov 2026. Remove override in config when thesis changes.",
    }
