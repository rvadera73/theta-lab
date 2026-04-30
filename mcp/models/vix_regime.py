"""
VIX term structure and realized vs. implied volatility spread.
These are the two market-timing signals for premium sellers:
  1. Term structure ratio (VIX / VIX3M) > 1.0 = fear = rich premium
  2. Implied vol > Realized vol = you're getting paid above fair value
"""

import math
import yfinance as yf
from datetime import date


def get_vix_term_structure() -> dict:
    """
    VIX / VIX3M ratio.
    > 1.15 = extreme fear / backwardation — best premium environment
    1.0-1.15 = mild fear — premium is elevated
    0.90-1.0 = neutral contango
    < 0.90 = deep contango — premium is cheap; be very selective
    """
    try:
        vix_data = yf.Ticker("^VIX").history(period="5d")
        vix3m_data = yf.Ticker("^VIX3M").history(period="5d")

        if vix_data.empty or vix3m_data.empty:
            return {"error": "could_not_fetch_vix_data"}

        vix = float(vix_data["Close"].iloc[-1])
        vix3m = float(vix3m_data["Close"].iloc[-1])
        ratio = vix / vix3m

        if ratio >= 1.15:
            signal = "EXTREME_FEAR"
            action = "Best premium environment — open puts aggressively (10-15% OTM). High IV means vega profit as VIX reverts."
        elif ratio >= 1.0:
            signal = "ELEVATED_FEAR"
            action = "Good premium environment — open new puts at IVR >= 40. Premium is above fair value."
        elif ratio >= 0.90:
            signal = "NEUTRAL"
            action = "Normal contango. Be selective — only highest-conviction entries at IVR >= 40."
        else:
            signal = "COMPLACENT"
            action = "Deep contango. Premium is cheap. Hold existing positions; do not add new short premium."

        # VIX mean reversion estimate (VIX mean-reverts to ~20)
        vix_mean = 20.0
        if vix > vix_mean:
            half_life_days = 20  # rough approximation: VIX mean-reverts in ~3-4 weeks
            excess = vix - vix_mean
            vega_gain_estimate = excess * 0.1  # rough: each VIX point = ~$100 gain on typical short put
        else:
            half_life_days = None
            vega_gain_estimate = 0

        return {
            "vix": round(vix, 2),
            "vix3m": round(vix3m, 2),
            "ratio": round(ratio, 3),
            "signal": signal,
            "action": action,
            "vix_vs_mean": round(vix - vix_mean, 1),
            "mean_reversion_days_estimate": half_life_days,
            "entry_quality": "HIGH" if ratio >= 1.0 else ("MEDIUM" if ratio >= 0.90 else "LOW"),
        }

    except Exception as e:
        return {"error": str(e)}


def realized_vol_30d(symbol: str) -> float:
    """30-day annualized realized volatility from daily closes."""
    try:
        hist = yf.Ticker(symbol).history(period="45d")
        closes = hist["Close"].tolist()
        if len(closes) < 31:
            return 0.0
        returns = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
        recent = returns[-30:]
        mean = sum(recent) / len(recent)
        variance = sum((r - mean) ** 2 for r in recent) / (len(recent) - 1)
        return math.sqrt(variance * 252)
    except Exception:
        return 0.0


def realized_vs_implied_spread(symbol: str, implied_vol: float = None) -> dict:
    """
    Compares current implied vol to 30-day realized vol.
    If spread > 5 pts: premium is genuinely rich — strong sell signal.
    If spread < 2 pts: premium is fair value — be selective.
    If spread < 0: realized > implied — do NOT sell premium on this name.
    implied_vol: pass as decimal (0.35 = 35%). If None, uses HV as proxy.
    """
    rv = realized_vol_30d(symbol)

    if implied_vol is None:
        # Estimate IV from options chain if available, else use HV + 5pt typical premium
        # Without live options data, add a typical 5-8pt IV premium over HV
        implied_vol = rv + 0.06  # conservative estimate

    spread_pts = (implied_vol - rv) * 100  # in percentage points

    if spread_pts >= 8:
        signal = "RICH"
        action = f"IV premium is large ({spread_pts:.1f} pts above realized). Strong sell-premium signal."
    elif spread_pts >= 4:
        signal = "ELEVATED"
        action = f"IV moderately above realized ({spread_pts:.1f} pts). Good entry if IVR >= 40."
    elif spread_pts >= 0:
        signal = "FAIR"
        action = f"IV near realized ({spread_pts:.1f} pts). Selective entries only; need other confirmation."
    else:
        signal = "CHEAP"
        action = f"Realized vol EXCEEDS implied by {abs(spread_pts):.1f} pts. Do NOT sell premium — market is moving more than priced."

    return {
        "symbol": symbol,
        "implied_vol_pct": round(implied_vol * 100, 1),
        "realized_vol_30d_pct": round(rv * 100, 1),
        "spread_pts": round(spread_pts, 1),
        "signal": signal,
        "action": action,
        "sell_premium": spread_pts >= 4,
    }


def entry_timing_score(symbol: str, iv_rank: float = None, implied_vol: float = None) -> dict:
    """
    Composite entry quality score combining:
    - VIX term structure (regime timing)
    - IV Rank (name-specific richness)
    - Realized vs. Implied spread (true edge confirmation)
    Score 0-100. >= 70 = strong entry. 50-69 = acceptable. < 50 = wait.
    """
    term = get_vix_term_structure()
    rv_iv = realized_vs_implied_spread(symbol, implied_vol)

    # Score components (each 0-33 pts)
    term_score = 0
    if term.get("ratio", 0) >= 1.15:
        term_score = 33
    elif term.get("ratio", 0) >= 1.0:
        term_score = 25
    elif term.get("ratio", 0) >= 0.90:
        term_score = 15
    else:
        term_score = 5

    ivr_score = 0
    if iv_rank is not None:
        if iv_rank >= 60:
            ivr_score = 34
        elif iv_rank >= 40:
            ivr_score = 25
        elif iv_rank >= 25:
            ivr_score = 12
        else:
            ivr_score = 0

    spread_score = 0
    spread = rv_iv.get("spread_pts", 0)
    if spread >= 8:
        spread_score = 33
    elif spread >= 4:
        spread_score = 22
    elif spread >= 0:
        spread_score = 10
    else:
        spread_score = 0

    total = term_score + ivr_score + spread_score

    return {
        "symbol": symbol,
        "composite_score": total,
        "term_structure_score": term_score,
        "ivr_score": ivr_score,
        "spread_score": spread_score,
        "signal": "STRONG ENTRY" if total >= 70 else ("ACCEPTABLE" if total >= 50 else "WAIT"),
        "vix_ratio": term.get("ratio"),
        "iv_rank": iv_rank,
        "rv_iv_spread_pts": rv_iv.get("spread_pts"),
        "recommendation": (
            f"Score {total}/100 — "
            + ("Open position now." if total >= 70 else
               "Acceptable entry; size at 50% of target." if total >= 50 else
               "Wait for better setup (higher IVR or VIX spike).")
        ),
    }
