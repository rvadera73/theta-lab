"""
Strategy Engine — regime-aware trade recommendation for any symbol.

Called by: research_symbol, scan_sector, run_screener, dry_run_order.
Never hardcodes strikes or DTE — all derived from live regime + IV + RSI.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt
from typing import Literal

RegimeType = Literal["BULL", "BEAR_SIDEWAYS", "TRANSITIONING", "RISKY_BULL"]
StrategyType = Literal["CSP", "CC", "STRANGLE", "WAIT"]


@dataclass
class TradeRecommendation:
    strategy: StrategyType
    strike_put: float | None
    strike_call: float | None
    dte: int
    otm_pct: float
    est_premium: float | None
    est_monthly_yield: float | None
    rationale: str
    roll_triggers: dict
    account: str


_DTE_RANGES: dict[RegimeType, tuple[int, int]] = {
    "BEAR_SIDEWAYS": (90, 130),
    "RISKY_BULL": (90, 130),
    "TRANSITIONING": (60, 90),
    "BULL": (30, 45),
}

_BASE_OTM: dict[RegimeType, float] = {
    "BEAR_SIDEWAYS": 0.20,
    "RISKY_BULL": 0.18,
    "TRANSITIONING": 0.14,
    "BULL": 0.10,
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _round_to_five(value: float) -> float:
    rounded = round(value / 5.0) * 5.0
    return float(max(5.0, rounded))


def _norm_cdf(x: float) -> float:
    """Abramowitz and Stegun approximation for the standard normal CDF."""
    sign = 1 if x >= 0 else -1
    z = abs(x)
    t = 1.0 / (1.0 + 0.2316419 * z)
    poly = t * (
        0.319381530
        + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429)))
    )
    pdf = 0.3989422804014327 * exp(-(z * z) / 2.0)
    cdf = 1.0 - pdf * poly
    return cdf if sign > 0 else 1.0 - cdf


def _bsm_put(S: float, K: float, T: float, iv: float, r: float = 0.02) -> float:
    if S <= 0 or K <= 0 or T <= 0 or iv <= 0:
        return max(K - S, 0.0)
    sigma_t = iv * sqrt(T)
    d1 = (log(S / K) + (r + 0.5 * iv * iv) * T) / sigma_t
    d2 = d1 - sigma_t
    price = K * exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)
    return max(price, 0.0)


def _bsm_call(S: float, K: float, T: float, iv: float, r: float = 0.02) -> float:
    if S <= 0 or K <= 0 or T <= 0 or iv <= 0:
        return max(S - K, 0.0)
    sigma_t = iv * sqrt(T)
    d1 = (log(S / K) + (r + 0.5 * iv * iv) * T) / sigma_t
    d2 = d1 - sigma_t
    price = S * _norm_cdf(d1) - K * exp(-r * T) * _norm_cdf(d2)
    return max(price, 0.0)


def _normalized_iv(iv: float) -> float:
    return _clamp(float(iv or 0.0), 0.05, 2.0)


def _regime_label(regime: RegimeType) -> str:
    return {
        "BEAR_SIDEWAYS": "Bear regime",
        "RISKY_BULL": "Risky bull regime",
        "TRANSITIONING": "Transitioning regime",
        "BULL": "Bull regime",
    }[regime]


def _rsi_label(rsi: float) -> str | None:
    if rsi < 20:
        return "deeply oversold"
    if rsi < 30:
        return "oversold"
    if rsi > 70:
        return "stretched overbought"
    if rsi > 65:
        return "overbought"
    return None


def _dte_for(regime: RegimeType, tier: int, iv_rank: float) -> int:
    low, high = _DTE_RANGES[regime]
    dte = (low + high) / 2
    if tier == 3:
        dte *= 0.80
    if iv_rank >= 70:
        dte *= 0.85
    elif iv_rank <= 30:
        dte *= 1.20
    return max(21, int(round(dte)))


def _otm_for(regime: RegimeType, iv_rank: float, rsi: float, tier: int) -> float:
    otm = _BASE_OTM[regime]
    if iv_rank >= 70:
        otm += 0.03
    elif iv_rank <= 30:
        otm -= 0.04
    if rsi < 30:
        otm -= 0.02
    elif rsi > 65:
        otm += 0.03
    if tier == 3:
        otm += 0.03
    elif tier == 1:
        otm -= 0.02
    return _clamp(otm, 0.08, 0.30)


def _estimate_premium(strategy: StrategyType, price: float, strike_put: float | None, strike_call: float | None, dte: int, iv: float) -> float | None:
    if strategy == "WAIT":
        return None
    term = max(dte, 1) / 365.0
    premium = 0.0
    if strategy in {"CSP", "STRANGLE"} and strike_put:
        premium += _bsm_put(price, strike_put, term, iv)
    if strategy in {"CC", "STRANGLE"} and strike_call:
        premium += _bsm_call(price, strike_call, term, iv)
    return round(max(premium, 0.0) * 100.0, 2)


def _monthly_yield(premium: float | None, reference_strike: float | None, dte: int) -> float | None:
    if premium is None or reference_strike is None or reference_strike <= 0:
        return None
    capital_at_risk = reference_strike * 100.0
    return round((premium / capital_at_risk) * (30.0 / max(dte, 1)) * 100.0, 2)


def _bull_upgrade_ratio(strategy: StrategyType, price: float, iv: float, current_premium: float | None) -> tuple[float, float, float]:
    bull_otm = 0.10
    bull_dte = 45
    bull_put = _round_to_five(price * (1.0 - bull_otm))
    bull_call = _round_to_five(price * (1.0 + bull_otm * 0.6))
    bull_premium = _estimate_premium(strategy, price, bull_put, bull_call, bull_dte, iv)
    if current_premium and bull_premium:
        ratio = bull_premium / current_premium
    else:
        ratio = 0.0
    return bull_put, bull_call, ratio


def _roll_triggers(symbol: str, strategy: StrategyType, strike_put: float | None, strike_call: float | None, dte: int, price: float, iv: float, current_premium: float | None) -> dict:
    bull_put, bull_call, ratio = _bull_upgrade_ratio(strategy if strategy != "WAIT" else "CSP", price, iv, current_premium)
    if strategy == "CC":
        defense = f"If {symbol} loses ${price * 0.93:.0f}: roll the call out for credit or reduce overwrite size."
        regime_upgrade = f"If regime shifts BULL: roll up to ~${bull_call:.0f}C, 45 DTE — premium jumps {ratio:.1f}x"
    elif strategy == "STRANGLE":
        defense = f"If {symbol} trades through ${((strike_put or price) * 0.97):.0f}: roll the tested put down and out for credit."
        regime_upgrade = f"If regime shifts BULL: center near ~${bull_put:.0f}P / ${bull_call:.0f}C, 45 DTE — premium jumps {ratio:.1f}x"
    else:
        put_ref = strike_put or bull_put
        defense = f"If {symbol} trades through ${put_ref * 0.97:.0f}: roll down and out for credit — do not take assignment in bear regime."
        regime_upgrade = f"If regime shifts BULL: roll up to ~${bull_put:.0f}P, 45 DTE — premium jumps {ratio:.1f}x"

    if strategy == "WAIT":
        return {
            "profit_close": "No position yet — wait for better premium.",
            "regime_upgrade": regime_upgrade,
            "time_based": "Recheck after the next IV or RSI shift.",
            "defense": "No defense needed until a position is opened.",
        }

    return {
        "profit_close": "Close at 50% of premium collected — redeploy capital",
        "regime_upgrade": regime_upgrade,
        "time_based": f"At {max(dte // 2, 1)} DTE remaining: assess roll if not at 50% profit",
        "defense": defense,
    }


def _rationale(symbol: str, strategy: StrategyType, regime: RegimeType, rsi: float, iv_rank: float, otm_pct: float, dte: int, premium: float | None, monthly_yield: float | None, bull_put: float, bull_call: float, held_shares: int) -> str:
    regime_text = _regime_label(regime)
    rsi_text = _rsi_label(rsi)
    lead = regime_text
    if rsi_text:
        lead += f" + RSI {rsi:.0f} ({rsi_text})"
    else:
        lead += f" + IVR {iv_rank:.0f}"

    premium_text = f"~${premium:.0f}/contract" if premium is not None else "thin premium"
    yield_text = f" (~{monthly_yield:.2f}%/mo)" if monthly_yield is not None else ""

    if strategy == "WAIT":
        return f"{lead}: IVR {iv_rank:.0f} is below the 25 floor, so premium is too thin to justify risk right now."
    if strategy == "CC":
        return f"{lead} with {held_shares} shares already owned: sell the covered call near ${bull_call:.0f}C at {dte} DTE for {premium_text}{yield_text} and recycle at 50% profit."
    if strategy == "STRANGLE":
        return f"{lead}: a {otm_pct * 100:.0f}% OTM put and {otm_pct * 60:.0f}% OTM call at {dte} DTE keeps both sides wide while collecting {premium_text}{yield_text}."
    return f"{lead}: {otm_pct * 100:.0f}% OTM at {dte} DTE balances cushion and income while collecting {premium_text}{yield_text}; roll toward ${bull_put:.0f}P/45 DTE when the regime upgrades to BULL."


def recommend_trade(
    symbol: str,
    price: float,
    iv_rank: float,
    iv: float,
    rsi: float,
    regime: RegimeType,
    held_shares: int = 0,
    tier: int = 2,
    account: str = "A",
) -> TradeRecommendation:
    iv_rank = _clamp(float(iv_rank or 0.0), 0.0, 100.0)
    iv = _normalized_iv(iv)
    rsi = float(rsi or 50.0)
    price = float(price or 0.0)
    tier = int(tier or 2)
    regime = regime if regime in _DTE_RANGES else "TRANSITIONING"

    dte = _dte_for(regime, tier, iv_rank)
    otm_pct = _otm_for(regime, iv_rank, rsi, tier)

    if held_shares > 0:
        strategy: StrategyType = "CC"
    elif iv_rank < 25:
        strategy = "WAIT"
    elif account == "A" and regime == "BULL" and tier <= 2:
        strategy = "STRANGLE"
    elif regime in ("BEAR_SIDEWAYS", "RISKY_BULL") and account != "A":
        strategy = "CSP"
    else:
        strategy = "CSP"

    strike_put = None
    strike_call = None
    if strategy in {"CSP", "STRANGLE"}:
        strike_put = _round_to_five(price * (1.0 - otm_pct))
    if strategy == "CC":
        strike_call = _round_to_five(price * (1.0 + otm_pct * 0.6))
    elif strategy == "STRANGLE":
        strike_call = _round_to_five(price * (1.0 + otm_pct * 0.6))

    est_premium = _estimate_premium(strategy, price, strike_put, strike_call, dte, iv)
    reference_strike = strike_put or strike_call or price
    est_monthly_yield = _monthly_yield(est_premium, reference_strike, dte)
    bull_put, bull_call, _ = _bull_upgrade_ratio(strategy if strategy != "WAIT" else "CSP", price, iv, est_premium)
    rationale = _rationale(symbol, strategy, regime, rsi, iv_rank, otm_pct, dte, est_premium, est_monthly_yield, bull_put, bull_call, held_shares)
    roll_triggers = _roll_triggers(symbol, strategy, strike_put, strike_call, dte, price, iv, est_premium)

    return TradeRecommendation(
        strategy=strategy,
        strike_put=strike_put,
        strike_call=strike_call,
        dte=dte,
        otm_pct=round(otm_pct, 4),
        est_premium=est_premium,
        est_monthly_yield=est_monthly_yield,
        rationale=rationale,
        roll_triggers=roll_triggers,
        account=account,
    )
