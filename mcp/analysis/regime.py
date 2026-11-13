"""
Market regime detection: BEAR_SIDEWAYS / TRANSITIONING / CAUTIOUS_BULL / BULL.

Real VIX breakpoints (config.REGIME_SIGNALS), not a four-tier VIX scheme --
there are only two:
  vix_bull_threshold  = 20.0  — VIX 5-day avg sustained below this is a BULL
                                signal (+1 bull_signal).
  vix_pause_threshold = 35.0  — VIX above this is a BEAR signal (+2
                                bear_signals), "pause entries."
  A VIX reading strictly between 20 and 35 is NEUTRAL: it contributes zero
  weight to either bull_signals or bear_signals. It is not a bear-leaning
  "TRANSITIONING: VIX 20-25 / BEAR_SIDEWAYS: VIX > 25" scheme.

The VIX signal is combined with the S&P 500 vs. 50/200-day MA signal into
a base technical regime via the shared classification tree in
regime_common.classify_tech_regime() (BULL / TRANSITIONING / BEAR_SIDEWAYS),
then this module applies one further, US-specific downgrade on top:
  CAUTIOUS_BULL — technical regime is BULL but VIX >= 16 (elevated, not
                  truly complacent) or SPX is >12% above its 200d MA
                  (stretched/overextended). New entries allowed with
                  tighter strikes (Tier 1-2 only).
"""

import os as _os, sys as _sys
_p = _os.path.dirname(_os.path.abspath(__file__))
for _ in range(5):
    _cand = _os.path.join(_p, "mcp", "analysis")
    if _os.path.isdir(_cand):
        _sys.path.insert(0, _cand)
        break
    _p = _os.path.dirname(_p)
import yahoo_throttle  # noqa: F401 -- installs the global cross-process Yahoo rate limiter, must run before any yfinance call
import yfinance as yf
from config import Regime, REGIME_SIGNALS
from regime_common import get_closes as _get_closes, moving_average as _moving_average, classify_tech_regime


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

    # Determine base technical regime (shared with india_regime.py)
    tech_regime = classify_tech_regime(bull_signals, bear_signals)

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
