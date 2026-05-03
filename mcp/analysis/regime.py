"""
Market regime detection: BEAR_SIDEWAYS / TRANSITIONING / CAUTIOUS_BULL / BULL.

Four-tier system calibrated for a theta-selling persona:
  BULL          — VIX < 16, SPX above both MAs, not stretched. Full throttle.
  CAUTIOUS_BULL — Technical bull but VIX 16-20 or SPX >12% above 200d MA.
                  New entries allowed with tighter strikes (Tier 1-2 only).
  TRANSITIONING — Mixed signals: VIX 20-25 or SPX above 200d but below 50d.
                  Tier 1 only, reduced size.
  BEAR_SIDEWAYS — Bear confirmed: VIX > 25 or SPX below 200d MA. No new entries.
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
    Signals checked: VIX level + trend, S&P 500 vs 50/200-day MA, SPX extension.
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

    # Determine base technical regime
    if bull_signals >= 3 and bear_signals == 0:
        tech_regime = Regime.BULL
    elif bear_signals >= 3:
        tech_regime = Regime.BEAR_SIDEWAYS
    elif bull_signals > bear_signals:
        tech_regime = Regime.TRANSITIONING
    else:
        tech_regime = Regime.BEAR_SIDEWAYS

    # CAUTIOUS_BULL downgrade: technical signals are all green but environment is not clean.
    # Triggers (any one sufficient):
    #   1. VIX 16-20: elevated but sub-threshold — not truly complacent
    #   2. SPX > 12% above 200d MA: stretched/overextended — asymmetric downside risk
    # This replaces the manual trader override with data-driven caution.
    caution_reasons = []
    if tech_regime == Regime.BULL and current_vix is not None:
        if current_vix >= 16.0:
            caution_reasons.append(f"VIX {current_vix:.1f} ≥ 16 (elevated, not complacent)")
        if spx_current and spx_ma200:
            extension_pct = (spx_current / spx_ma200 - 1) * 100
            signals["spx_extension"] = {"pct_above_200d": round(extension_pct, 1)}
            if extension_pct > 12.0:
                caution_reasons.append(f"SPX {extension_pct:.1f}% above 200d MA (stretched)")

    if caution_reasons:
        final_regime = Regime.CAUTIOUS_BULL
        note = "CAUTIOUS_BULL: technical signals green but — " + "; ".join(caution_reasons) + ". New entries allowed, Tier 1-2 only, tighter strikes."
    else:
        final_regime = tech_regime
        note = f"Regime auto-detected from data. No caution flags active."

    return {
        "regime": final_regime.value,
        "technical_regime": tech_regime.value,
        "trader_override": None,
        "new_entries_allowed": True,  # strangles work in all regimes; bear = peak income months
        "signals": signals,
        "bull_signal_count": bull_signals,
        "bear_signal_count": bear_signals,
        "note": note,
    }
