"""
Multi-factor CSP/entry screener (v2).

Replaces the v1 logic (70% of the rank was just IVR + oversold-RSI) with a gated,
multi-factor composite closer to how systematic equity desks select names:

    GATES (hard filters) -> reject value traps / falling knives / broken businesses
    SCORE = Quality 20% + Value 20% + Growth 20% + Momentum 15% + IVRank 15% + Timing 10%

Key principle: oversold (RSI) is ENTRY TIMING only (10%), not selection. Momentum is the
12-1 / 6-month trend (the OPPOSITE of mean-reversion) and is used to confirm the downtrend
has stopped before we sell a put — i.e. "not early in the recovery cycle".

Fundamentals + momentum come from yfinance. IV-rank is optional (reused from the existing
iv_rank helper when available); if missing, its weight is redistributed.
"""
from __future__ import annotations
import math
from typing import Any, Optional

import yfinance as yf

try:  # reuse existing IV-rank helper if importable
    from iv_rank import get_iv_rank  # analysis/iv_rank.py on sys.path
except Exception:  # pragma: no cover
    get_iv_rank = None


# ----------------------------- helpers --------------------------------------
def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def _scale(x: Optional[float], lo: float, hi: float) -> Optional[float]:
    """Linear-map x in [lo,hi] -> [0,100]; None passes through."""
    if x is None:
        return None
    return _clamp((x - lo) / (hi - lo) * 100.0)


def _rsi(closes, period: int = 14) -> Optional[float]:
    if closes is None or len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas][-period:]
    losses = [-d if d < 0 else 0 for d in deltas][-period:]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _timing_score(rsi: Optional[float]) -> Optional[float]:
    """Oversold = better entry timing (NOT a selection signal)."""
    if rsi is None:
        return None
    if rsi < 30:
        return 100.0
    if rsi < 40:
        return 80.0
    if rsi < 55:
        return 55.0
    if rsi < 70:
        return 30.0
    return 10.0  # overbought = poor entry timing


# ----------------------------- factor fetch ---------------------------------
def get_factors(symbol: str) -> dict[str, Any]:
    t = yf.Ticker(symbol)
    info = t.info or {}
    try:
        hist = t.history(period="1y")
        closes = list(hist["Close"].dropna()) if len(hist) else []
    except Exception:
        closes = []

    price = info.get("currentPrice") or (closes[-1] if closes else None)
    target = info.get("targetMeanPrice")
    value_gap = (target / price - 1.0) if (target and price) else None  # upside to target

    mom_6m = (closes[-1] / closes[-126] - 1.0) if len(closes) >= 126 else None
    mom_12_1 = (closes[-21] / closes[-252] - 1.0) if len(closes) >= 252 else None

    ivr = None
    if get_iv_rank is not None:
        try:
            iv = get_iv_rank(symbol)
            ivr = iv.get("iv_rank") if isinstance(iv, dict) else iv
        except Exception:
            ivr = None

    return {
        "symbol": symbol,
        "price": price,
        "rev_growth": info.get("revenueGrowth"),     # yoy
        "eps_growth": info.get("earningsGrowth"),
        "roe": info.get("returnOnEquity"),
        "margin": info.get("profitMargins"),
        "d2e": info.get("debtToEquity"),
        "fcf": info.get("freeCashflow"),
        "peg": info.get("pegRatio"),
        "fwd_pe": info.get("forwardPE"),
        "value_gap": value_gap,
        "mom_6m": mom_6m,
        "mom_12_1": mom_12_1,
        "rsi": _rsi(closes),
        "ivr": ivr,
    }


# ----------------------------- scoring --------------------------------------
def score(f: dict[str, Any]) -> dict[str, Any]:
    gates: list[str] = []
    # Hard filters — reject names you would NOT want to be assigned
    if f.get("fcf") is not None and f["fcf"] < 0:
        gates.append("negative_FCF")
    if f.get("rev_growth") is not None and f["rev_growth"] < -0.05:
        gates.append("revenue_shrinking")
    if f.get("mom_6m") is not None and f["mom_6m"] < -0.25:
        gates.append("falling_knife")  # still in a steep downtrend
    if f.get("d2e") is not None and f["d2e"] > 300:
        gates.append("over_levered")

    # Factor subscores (0-100)
    quality = _scale(f.get("roe"), 0.0, 0.30)          # ROE 0-30%
    value = _scale(f.get("value_gap"), 0.0, 0.30)      # 0-30% upside to target
    growth = _scale(f.get("rev_growth"), 0.0, 0.25)    # 0-25% rev growth
    momentum = _scale(f.get("mom_6m"), -0.10, 0.30)    # reward stabilized/up trend
    ivr_s = _scale(f.get("ivr"), 30.0, 90.0)           # IVR 30-90 -> premium richness
    timing = _timing_score(f.get("rsi"))

    weights = {"quality": 0.20, "value": 0.20, "growth": 0.20,
               "momentum": 0.15, "ivr": 0.15, "timing": 0.10}
    subs = {"quality": quality, "value": value, "growth": growth,
            "momentum": momentum, "ivr": ivr_s, "timing": timing}

    # Redistribute weight of any missing factor across the present ones
    present = {k: v for k, v in subs.items() if v is not None}
    wsum = sum(weights[k] for k in present)
    composite = sum(subs[k] * weights[k] for k in present) / wsum if wsum else 0.0

    return {
        "composite": round(composite, 1),
        "gates": gates,
        "subscores": {k: (round(v, 0) if v is not None else None) for k, v in subs.items()},
    }


def screen(symbols: list[str]) -> list[dict[str, Any]]:
    out = []
    for sym in symbols:
        try:
            f = get_factors(sym)
        except Exception as e:
            out.append({"symbol": sym, "error": str(e)})
            continue
        s = score(f)
        row = {**f, **s, "passes_gates": len(s["gates"]) == 0}
        out.append(row)
    # rank: gate-passers first, then by composite
    out.sort(key=lambda r: (r.get("passes_gates", False), r.get("composite", 0)), reverse=True)
    return out
