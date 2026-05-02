from __future__ import annotations

import io
import math
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from typing import Any

from analysis.iv_rank import batch_iv_rank
from config import INDIA_REGIME_THRESHOLDS, RISK
from reports.report_utils import technical_snapshot, upcoming_earnings, yf_symbol
from reports.screener_universe import INDIA_UNIVERSE, US_UNIVERSE


def _quiet_call(func, *args, **kwargs):
    sink = io.StringIO()
    with redirect_stdout(sink), redirect_stderr(sink):
        return func(*args, **kwargs)


def _rsi_score(rsi: float | None) -> int:
    if rsi is None:
        return 40
    if rsi < 30:
        return 100
    if rsi < 40:
        return 80
    if rsi < 55:
        return 50
    if rsi < 65:
        return 30
    return 10


def _tier_score(tier: int) -> int:
    return {1: 100, 2: 70, 3: 40}.get(tier, 40)


def _sector_weight(sector: str, regime: str) -> int:
    bull = {
        "AI Infrastructure & Data Center": 100,
        "Cybersecurity": 92,
        "Tech": 90,
        "Consumer & Retail": 78,
        "Financials": 78,
        "Industrials & Infrastructure": 76,
        "Nuclear & Clean Energy": 82,
        "Defense & Aerospace": 72,
        "Energy": 72,
        "Healthcare & Biotech": 68,
        "IT": 92,
        "Banking & NBFC": 84,
        "Infrastructure & Capital Goods": 82,
        "Auto": 84,
        "Consumer": 72,
        "Energy & Power": 78,
        "Pharma": 66,
    }
    risky = {
        "Defense & Aerospace": 100,
        "Energy": 95,
        "Nuclear & Clean Energy": 90,
        "Financials": 85,
        "Industrials & Infrastructure": 82,
        "Healthcare & Biotech": 72,
        "Consumer & Retail": 58,
        "Cybersecurity": 55,
        "AI Infrastructure & Data Center": 30,
        "Tech": 25,
        "Energy & Power": 92,
        "Banking & NBFC": 88,
        "Infrastructure & Capital Goods": 85,
        "Pharma": 72,
        "Consumer": 60,
        "Auto": 58,
        "IT": 35,
    }
    transitioning = {
        "Defense & Aerospace": 85,
        "Energy": 80,
        "Nuclear & Clean Energy": 78,
        "Financials": 76,
        "Industrials & Infrastructure": 74,
        "Healthcare & Biotech": 70,
        "Consumer & Retail": 60,
        "Cybersecurity": 56,
        "AI Infrastructure & Data Center": 45,
        "Tech": 40,
        "Energy & Power": 82,
        "Banking & NBFC": 78,
        "Infrastructure & Capital Goods": 78,
        "Pharma": 72,
        "Consumer": 62,
        "Auto": 64,
        "IT": 48,
    }
    if regime == "BULL":
        return bull.get(sector, 60)
    if regime in {"BEAR_SIDEWAYS", "RISKY_BULL"}:
        return risky.get(sector, 50)
    return transitioning.get(sector, 55)


def _india_regime(india_vix: float) -> str:
    bull = float(INDIA_REGIME_THRESHOLDS.get("indiavix_bull_threshold", 15.0))
    pause = float(INDIA_REGIME_THRESHOLDS.get("indiavix_pause_threshold", 25.0))
    if india_vix <= bull:
        return "BULL"
    if india_vix <= bull + 3:
        return "TRANSITIONING"
    if india_vix <= pause:
        return "RISKY_BULL"
    return "BEAR_SIDEWAYS"


def _heavy_sector_counts(current_symbols: list[str], universe: list[dict[str, Any]]) -> tuple[Counter, list[str]]:
    sector_map = {item["symbol"]: item["sector"] for item in universe}
    counts = Counter(sector_map[symbol] for symbol in current_symbols if symbol in sector_map)
    heavy = sorted(sector for sector, count in counts.items() if count >= 3)
    return counts, heavy


def _resolve_strategy(meta: dict[str, Any], in_portfolio: bool, ivr: float | None, regime: str) -> str:
    preferred = meta["preferred_strategy"]
    if in_portfolio and preferred == "CC":
        return "CC"
    if preferred == "CSP_or_strangle":
        if regime == "BULL" and (ivr or 0) >= 60:
            return "strangle"
        return "CSP"
    return preferred


def _earnings_days(symbol: str, india: bool) -> tuple[bool, int | None]:
    earnings = _quiet_call(upcoming_earnings, yf_symbol(symbol, india=india), days=21)
    if not earnings:
        return False, None
    days = []
    for item in earnings:
        try:
            days.append((date.fromisoformat(item) - date.today()).days)
        except Exception:
            continue
    if not days:
        return False, None
    return True, min(days)


def _reason(signal: str, meta: dict[str, Any], ivr: float | None, rsi: float | None, regime: str, regime_fit: int, earnings_days: int | None, portfolio_note: str | None) -> str:
    parts = [
        f"IVR {ivr:.1f}" if ivr is not None else "IVR unavailable",
        f"RSI {rsi:.1f}" if rsi is not None else "RSI unavailable",
        f"{meta['sector']} fit {regime_fit}/100 in {regime}",
    ]
    if earnings_days is not None:
        parts.append(f"earnings in {earnings_days}d")
    if portfolio_note:
        parts.append(portfolio_note)
    if signal == "ENTER_NOW":
        return " | ".join(parts)
    if signal == "WATCH":
        return "Watchlist: " + " | ".join(parts)
    return "Skip for now: " + " | ".join(parts)


def _score_candidate(meta: dict[str, Any], regime: str, current_symbols: list[str], heavy_sectors: list[str], india: bool, iv_lookup: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    symbol = meta["symbol"]
    in_portfolio = symbol in set(current_symbols)
    preferred = meta["preferred_strategy"]
    if in_portfolio and (preferred == "CSP" or preferred == "CSP_or_strangle"):
        return None

    iv_key = yf_symbol(symbol, india=india) if india else symbol
    iv_data = iv_lookup.get(iv_key, {})
    ivr = iv_data.get("iv_rank")
    iv_pct = iv_data.get("iv_pct")
    current_iv = iv_data.get("current_iv")

    try:
        snap = _quiet_call(technical_snapshot, symbol, india=india)
        price = float(snap.get("current", 0) or 0)
        if price <= 0:
            return None
        rsi = snap.get("rsi")
        pct_off_high_raw = snap.get("pct_off_high")
        pct_off_high = round(abs(float(pct_off_high_raw)), 1) if pct_off_high_raw is not None else None
        earnings_soon, earnings_days = _earnings_days(symbol, india)
        if earnings_days is not None and earnings_days <= RISK.get("earnings_blackout_days", 7):
            return None

        regime_fit = _sector_weight(meta["sector"], regime)
        portfolio_note = None
        if meta["sector"] in heavy_sectors:
            regime_fit = min(regime_fit, 20)
            portfolio_note = f"Sector already heavy ({meta['sector']})"
        if regime == "TRANSITIONING" and meta["tier"] != 1:
            regime_fit = min(regime_fit, 15)
            portfolio_note = (portfolio_note + "; Tier 1 only in transitioning regime") if portfolio_note else "Tier 1 only in transitioning regime"

        rsi_component = _rsi_score(rsi)
        tier_component = _tier_score(meta["tier"])
        ivr_value = float(ivr) if ivr is not None else 0.0
        score = (ivr_value * 0.4) + (rsi_component * 0.3) + (regime_fit * 0.2) + (tier_component * 0.1)
        strategy = _resolve_strategy(meta, in_portfolio, ivr, regime)

        if ivr is not None and ivr >= RISK.get("iv_rank_min_new_entry", 40) and not earnings_soon and regime_fit >= 50:
            signal = "ENTER_NOW"
        elif ((ivr is not None and 25 <= ivr < RISK.get("iv_rank_min_new_entry", 40)) or earnings_soon or 25 <= regime_fit < 50):
            signal = "WATCH"
        else:
            signal = "SKIP"

        est_monthly_pct = round((float(current_iv or 0) * math.sqrt(45 / 365) * 0.35), 1)
        return {
            "symbol": symbol,
            "sector": meta["sector"],
            "tier": meta["tier"],
            "strategy": strategy,
            "price": round(price, 2),
            "rsi": rsi,
            "ivr": ivr,
            "iv_pct": iv_pct,
            "est_monthly_pct": est_monthly_pct,
            "signal": signal,
            "reason": _reason(signal, meta, ivr, rsi, regime, regime_fit, earnings_days if earnings_soon else None, portfolio_note),
            "pct_off_high": pct_off_high,
            "earnings_soon": earnings_soon,
            "earnings_days": earnings_days,
            "portfolio_note": portfolio_note,
            "regime": regime,
            "heavy_sectors": heavy_sectors,
            "opportunity_score": round(score, 1),
            "notes": meta.get("notes", ""),
        }
    except Exception:
        return None


def _screen(universe: list[dict[str, Any]], regime: str, current_symbols: list[str], top_n: int, india: bool = False) -> list[dict]:
    _, heavy_sectors = _heavy_sector_counts(current_symbols, universe)
    lookup_symbols = [yf_symbol(item["symbol"], india=True) if india else item["symbol"] for item in universe]
    try:
        iv_lookup = _quiet_call(batch_iv_rank, lookup_symbols)
    except Exception:
        iv_lookup = {}

    results: list[dict[str, Any]] = []
    for meta in universe:
        try:
            candidate = _score_candidate(meta, regime, current_symbols, heavy_sectors, india, iv_lookup)
        except Exception:
            candidate = None
        if candidate:
            results.append(candidate)

    ordered = sorted(
        results,
        key=lambda item: (
            {"ENTER_NOW": 0, "WATCH": 1, "SKIP": 2}.get(item.get("signal", "SKIP"), 2),
            -float(item.get("opportunity_score", 0)),
            str(item.get("symbol", "")),
        ),
    )
    return ordered[:top_n]


def screen_us_opportunities(regime: str, current_symbols: list[str], top_n: int = 8) -> list[dict]:
    """
    Screens US universe. Returns top_n candidates ranked by opportunity score.
    Each result dict has:
      symbol, sector, tier, strategy, price, rsi, ivr, iv_pct, est_monthly_pct,
      signal ("ENTER_NOW" | "WATCH" | "SKIP"), reason, pct_off_high, earnings_soon
    """
    return _screen(US_UNIVERSE, regime or "TRANSITIONING", current_symbols or [], top_n=top_n, india=False)


def screen_india_opportunities(india_vix: float, current_symbols: list[str], top_n: int = 6) -> list[dict]:
    """
    Same logic for NSE universe.
    """
    regime = _india_regime(india_vix)
    return _screen(INDIA_UNIVERSE, regime, current_symbols or [], top_n=top_n, india=True)
