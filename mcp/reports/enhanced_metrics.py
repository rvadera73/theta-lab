"""
Enhanced metrics from Yahoo Finance — Greeks, conviction, technical indicators, position heat
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
import numpy as np
import pandas as pd
from scipy.stats import norm
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import json
import logging
import os
import time

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BlackScholesGreeks:
    """Calculate Greeks using Black-Scholes model"""

    @staticmethod
    def d1(S, K, T, r, sigma):
        """d1 component"""
        if T <= 0 or sigma <= 0:
            return 0
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    @staticmethod
    def d2(S, K, T, r, sigma):
        """d2 component"""
        if T <= 0 or sigma <= 0:
            return 0
        d1 = BlackScholesGreeks.d1(S, K, T, r, sigma)
        return d1 - sigma * np.sqrt(T)

    @staticmethod
    def call_delta(S, K, T, r, sigma):
        """Call delta"""
        if T <= 0 or sigma <= 0:
            return 1.0 if S > K else 0.0
        return norm.cdf(BlackScholesGreeks.d1(S, K, T, r, sigma))

    @staticmethod
    def put_delta(S, K, T, r, sigma):
        """Put delta"""
        call_delta = BlackScholesGreeks.call_delta(S, K, T, r, sigma)
        return call_delta - 1

    @staticmethod
    def gamma(S, K, T, r, sigma):
        """Gamma for both calls and puts"""
        if T <= 0 or sigma <= 0:
            return 0.0
        d1 = BlackScholesGreeks.d1(S, K, T, r, sigma)
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    @staticmethod
    def call_theta(S, K, T, r, sigma):
        """Call theta (per day)"""
        if T <= 0 or sigma <= 0:
            return 0.0
        d1 = BlackScholesGreeks.d1(S, K, T, r, sigma)
        d2 = BlackScholesGreeks.d2(S, K, T, r, sigma)
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * norm.cdf(d2))
        return theta / 365.0

    @staticmethod
    def put_theta(S, K, T, r, sigma):
        """Put theta (per day)"""
        if T <= 0 or sigma <= 0:
            return 0.0
        d1 = BlackScholesGreeks.d1(S, K, T, r, sigma)
        d2 = BlackScholesGreeks.d2(S, K, T, r, sigma)
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                 + r * K * np.exp(-r * T) * norm.cdf(-d2))
        return theta / 365.0

    @staticmethod
    def vega(S, K, T, r, sigma):
        """Vega (per 1% change in IV)"""
        if T <= 0 or sigma <= 0:
            return 0.0
        d1 = BlackScholesGreeks.d1(S, K, T, r, sigma)
        return S * norm.pdf(d1) * np.sqrt(T) / 100.0


class TechnicalIndicators:
    """Calculate technical indicators from price history"""

    @staticmethod
    def rsi(closes: pd.Series, period: int = 14) -> float:
        """Relative Strength Index (0-100)"""
        # Convert to pandas Series if needed
        if not isinstance(closes, pd.Series):
            closes = pd.Series(closes)

        if len(closes) < period + 1:
            return 50.0

        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        with np.errstate(divide='ignore', invalid='ignore'):
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

        return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0

    @staticmethod
    def macd(closes: pd.Series) -> Dict[str, float]:
        """MACD indicator"""
        # Convert to pandas Series if needed
        if not isinstance(closes, pd.Series):
            closes = pd.Series(closes)

        if len(closes) < 26:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

        ema12 = closes.ewm(span=12).mean()
        ema26 = closes.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line

        return {
            "macd": float(macd_line.iloc[-1]) if not np.isnan(macd_line.iloc[-1]) else 0.0,
            "signal": float(signal_line.iloc[-1]) if not np.isnan(signal_line.iloc[-1]) else 0.0,
            "histogram": float(histogram.iloc[-1]) if not np.isnan(histogram.iloc[-1]) else 0.0
        }

    @staticmethod
    def bollinger_bands(closes: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
        """Bollinger Bands"""
        # Convert to pandas Series if needed
        if not isinstance(closes, pd.Series):
            closes = pd.Series(closes)

        if len(closes) < period:
            return {"upper": 0, "middle": 0, "lower": 0, "pct_b": 0.5}

        sma = closes.rolling(period).mean()
        std = closes.rolling(period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        current = closes.iloc[-1]
        pct_b = 0.5
        if upper.iloc[-1] != lower.iloc[-1]:
            pct_b = (current - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])

        return {
            "upper": float(upper.iloc[-1]) if not np.isnan(upper.iloc[-1]) else 0.0,
            "middle": float(sma.iloc[-1]) if not np.isnan(sma.iloc[-1]) else 0.0,
            "lower": float(lower.iloc[-1]) if not np.isnan(lower.iloc[-1]) else 0.0,
            "pct_b": float(np.clip(pct_b, 0, 1))
        }


# =============================================================================
# get_ticker_metrics -- decomposed into per-phase helpers (Bolt B14 refactor).
# Each phase dataclass carries forward the shared intermediate values computed
# once here (closes, ma50/ma200, etc.) so no helper re-fetches/re-derives data
# another helper already has -- this module hits yfinance network calls, so a
# redundant recompute would be a real perf/behavior-adjacent regression, not
# just a style issue.
# =============================================================================


@dataclass
class _Fundamentals:
    pe_ratio: Optional[float]
    week_52_high: Optional[float]
    week_52_low: Optional[float]
    revenue_growth: Optional[float]
    earnings_growth: Optional[float]
    analyst_rating: Optional[str]
    target_upside_pct: Optional[float]


@dataclass
class _TechnicalSignals:
    rsi: float
    macd_data: Dict[str, float]
    bb_data: Dict[str, float]
    roc_7d: Optional[float]


@dataclass
class _TrendPositioning:
    ma50: Optional[float]
    ma200: Optional[float]
    pct_above_50ma: Optional[float]
    pct_above_200ma: Optional[float]
    structurally_extended: bool
    structurally_weak: bool


@dataclass
class _FundamentalConfirmation:
    supports_extension: bool
    confirms_weakness: bool
    target_upside_pct: Optional[float]


@dataclass
class _HeatContext:
    rsi: float
    position_in_range: float
    roc_7d: Optional[float]
    bb_pct_b: float
    pct_above_200ma: Optional[float]
    structurally_extended: bool
    structurally_weak: bool
    supports_extension: bool
    confirms_weakness: bool
    vs200_s: str
    upside_s: str


@dataclass
class _MetricsResult:
    ticker: str
    current_price: float
    conviction: float
    technical: _TechnicalSignals
    trend: _TrendPositioning
    position_in_range: float
    fundamentals: _Fundamentals
    heat_status: str
    heat_reason: str


def _fetch_fundamentals(stock, current_price: float) -> _Fundamentals:
    """Pull fundamentals off stock.info, incl. analyst target upside."""
    info = stock.info
    pe_ratio = info.get('trailingPE', None)
    week_52_high = info.get('fiftyTwoWeekHigh', None)
    week_52_low = info.get('fiftyTwoWeekLow', None)
    revenue_growth = info.get('revenueGrowth', None)
    earnings_growth = info.get('earningsGrowth', None)
    if earnings_growth is None:
        earnings_growth = info.get('earningsQuarterlyGrowth', None)
    analyst_rating = info.get('recommendationKey', None)
    target_mean = info.get('targetMeanPrice', None)
    target_upside_pct = (
        (target_mean / current_price - 1) * 100
        if target_mean and current_price else None
    )
    if target_upside_pct is not None and pd.isna(target_upside_pct):
        target_upside_pct = None
    return _Fundamentals(pe_ratio, week_52_high, week_52_low, revenue_growth,
                          earnings_growth, analyst_rating, target_upside_pct)


def _position_in_52w_range(current_price: float, week_52_high: Optional[float],
                            week_52_low: Optional[float]) -> float:
    """Position in 52-week range (0-100)."""
    position_in_range = 50.0
    if week_52_high and week_52_low and week_52_high > week_52_low:
        position_in_range = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
        position_in_range = max(0, min(100, position_in_range))
    return position_in_range


def _fetch_price_history(stock, current_price: float) -> pd.Series:
    """Historical closes for technical indicators, with a 6mo fallback."""
    hist = stock.history(period="1y")
    if len(hist) == 0:
        hist = stock.history(period="6mo")
    return hist['Close'] if len(hist) > 0 else pd.Series([current_price])


def _compute_technical_signals(closes: pd.Series) -> _TechnicalSignals:
    """RSI/MACD/Bollinger plus 7-day rate-of-change -- a recency/speed measure
    RSI(14) and 52-week-range position both miss (a two-month grind and a
    one-week spike can both read RSI 80; this tells them apart)."""
    rsi = TechnicalIndicators.rsi(closes)
    macd_data = TechnicalIndicators.macd(closes)
    bb_data = TechnicalIndicators.bollinger_bands(closes)

    roc_7d = None
    if len(closes) >= 8:
        try:
            prior = float(closes.iloc[-8])
            if prior:
                roc_7d = float((closes.iloc[-1] / prior - 1) * 100)
        except (ZeroDivisionError, IndexError):
            roc_7d = None

    return _TechnicalSignals(rsi, macd_data, bb_data, roc_7d)


def _compute_moving_averages(closes: pd.Series) -> Tuple[Optional[float], Optional[float]]:
    """50/200-day simple moving averages, NaN-sanitized (gappy/holiday-
    misaligned history can average out to NaN even with enough window
    length; float(nan) doesn't raise, so this must be sanitized explicitly
    rather than relying on an `is not None` check alone)."""
    ma50 = float(closes.tail(50).mean()) if len(closes) >= 50 else None
    ma200 = float(closes.tail(200).mean()) if len(closes) >= 200 else None
    if ma50 is not None and pd.isna(ma50):
        ma50 = None
    if ma200 is not None and pd.isna(ma200):
        ma200 = None
    return ma50, ma200


def _compute_pct_above_ma(current_price: float, ma50: Optional[float],
                           ma200: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    """Price vs 50/200-day average, NaN-sanitized (see _compute_moving_averages)."""
    pct_above_50ma = (current_price / ma50 - 1) * 100 if ma50 else None
    pct_above_200ma = (current_price / ma200 - 1) * 100 if ma200 else None
    if pct_above_50ma is not None and pd.isna(pct_above_50ma):
        pct_above_50ma = None
    if pct_above_200ma is not None and pd.isna(pct_above_200ma):
        pct_above_200ma = None
    return pct_above_50ma, pct_above_200ma


def _compute_trend_positioning(closes: pd.Series, current_price: float) -> _TrendPositioning:
    """50/200-day trend positioning -- gates whether an RSI/ROC/Bollinger
    trigger earns a hard RED/GREEN or gets downgraded to a "watch, not
    confirmed" YELLOW (added 2026-08-24; >10% above/below the 200-day average
    is the structural-confirmation threshold, calibrated to cleanly separate
    confirmed-extended names from short-term-only bounces inside a longer
    consolidation/downtrend). Neither this nor the RSI/ROC/Bollinger triggers
    replaces the other."""
    ma50, ma200 = _compute_moving_averages(closes)
    pct_above_50ma, pct_above_200ma = _compute_pct_above_ma(current_price, ma50, ma200)
    structurally_extended = pct_above_200ma is not None and pct_above_200ma > 10
    structurally_weak = pct_above_200ma is not None and pct_above_200ma < -10
    return _TrendPositioning(ma50, ma200, pct_above_50ma, pct_above_200ma,
                             structurally_extended, structurally_weak)


def _compute_fundamental_confirmation(fundamentals: _Fundamentals) -> _FundamentalConfirmation:
    """Fundamentals confirmation gate (added 2026-08-24) -- can only pull a
    technical RED/GREEN back toward YELLOW, never overrides the 50/200MA
    confirmation. Uses analyst target_upside_pct/rating rather than a
    computed PEG ratio, which was tried informally this session and kept
    producing nonsense-cheap readings driven by a single quarter's extreme
    earnings-growth% off a low prior-period base."""
    target_upside_pct = fundamentals.target_upside_pct
    analyst_rating = fundamentals.analyst_rating
    supports_extension = target_upside_pct is not None and target_upside_pct > 10
    confirms_weakness = (
        (target_upside_pct is not None and target_upside_pct < -10)
        or analyst_rating in ("sell", "strong_sell", "underperform")
    )
    return _FundamentalConfirmation(supports_extension, confirms_weakness, target_upside_pct)


# --- Conviction scoring -- see get_ticker_metrics docstring for the overall
# approach (raw score accumulated across components, then rescaled onto the
# 1-10 display range by its own achievable range rather than clamped). ---

def _score_rsi_component(rsi: float, option_type: Optional[str]) -> float:
    """RSI contribution, direction-dependent per option side (GitHub issue #1
    backtest, n=343 Account A closed trades). Calls: oversold=bullish is the
    best setup, overbought=bearish the worst (matches the heat-scanner's
    "AI melt-up" warning). Puts: overbought was instead the BEST-performing
    put bucket (98.3% win rate, n=59) -- opposite sign from calls -- so puts
    are scored separately with modest, uniformly positive contributions
    rather than mirroring the call-side swing."""
    is_put = str(option_type or '').upper() in ('P', 'PUT')
    if is_put:
        if rsi > 70:
            return 1.0
        if 40 < rsi < 60:
            return 0.75
        if rsi < 30:
            return 0.75
        return 0.0
    if rsi < 30:
        return 2.0
    if rsi > 70:
        return -1.0
    if 40 < rsi < 60:
        return 0.5
    return 0.0


def _score_macd_component(macd_data: Dict[str, float]) -> float:
    """Max +1.5 / min -1.0."""
    if macd_data['histogram'] > 0 and macd_data['macd'] > macd_data['signal']:
        return 1.5
    if macd_data['histogram'] < 0 and macd_data['macd'] < macd_data['signal']:
        return -1.0
    return 0.0


def _score_range_position_component(position_in_range: float) -> float:
    """Max +1.5 / min -1.0."""
    if position_in_range < 25:
        return 1.5
    if position_in_range > 85:
        return -1.0
    return 0.0


def _score_pe_ratio_component(pe_ratio: Optional[float]) -> float:
    """Max +0.5 / min -0.5."""
    if pe_ratio and 15 < pe_ratio < 30:
        return 0.5
    if pe_ratio and pe_ratio > 40:
        return -0.5
    return 0.0


def _score_technical_component(technical: _TechnicalSignals, option_type: Optional[str],
                                position_in_range: float, pe_ratio: Optional[float]) -> float:
    """Supplemental technical score: RSI(2.0) + MACD(1.5) + range(1.5) + PE(0.5)."""
    score = _score_rsi_component(technical.rsi, option_type)
    score += _score_macd_component(technical.macd_data)
    score += _score_range_position_component(position_in_range)
    score += _score_pe_ratio_component(pe_ratio)
    return score


def _score_revenue_growth_component(revenue_growth: Optional[float]) -> float:
    """Max +1.5 / min -1.0."""
    if revenue_growth is None:
        return 0.0
    if revenue_growth > 0.20:
        return 1.5
    if revenue_growth > 0.05:
        return 0.5
    if revenue_growth < -0.05:
        return -1.0
    return 0.0


def _score_earnings_growth_component(earnings_growth: Optional[float]) -> float:
    """Max +1.5 / min -2.5 (deteriorating earnings is the dominant signal)."""
    if earnings_growth is None:
        return 0.0
    if earnings_growth > 0.20:
        return 1.5
    if earnings_growth >= 0:
        return 0.5
    if earnings_growth > -0.20:
        return -0.5
    return -2.5


def _score_analyst_rating_component(analyst_rating: Optional[str]) -> float:
    """Max +1.5 / min -2.0."""
    if analyst_rating in ("strong_buy",):
        return 1.5
    if analyst_rating in ("buy",):
        return 0.75
    if analyst_rating in ("hold",):
        return -0.5
    if analyst_rating in ("sell", "strong_sell", "underperform"):
        return -2.0
    return 0.0


def _score_target_upside_component(target_upside_pct: Optional[float]) -> float:
    """Max +1.0 / min -2.0 (analyst target below current price)."""
    if target_upside_pct is None:
        return 0.0
    if target_upside_pct > 15:
        return 1.0
    if target_upside_pct > 0:
        return 0.3
    if target_upside_pct > -15:
        return -1.0
    return -2.0


def _score_fundamental_component(fundamentals: _Fundamentals) -> float:
    """Primary signal -- weighted with a wider swing than the technical
    component, matching the trading persona's stated philosophy
    ("fundamentals + macro instinct is the research engine... technicals are
    supplemental, not primary"). A technical-only version of this formula
    shipped 2026-07-19 and scored Dr Reddy's (DRREDDY.NS) at 8.0/10 -- the
    HIGHEST conviction in a 23-name India audit -- purely because it was
    oversold with a "fair" PE, while earnings had collapsed -86% YoY with an
    analyst downgrade to hold. That's the exact failure mode this weighting
    prevents."""
    return (
        _score_revenue_growth_component(fundamentals.revenue_growth)
        + _score_earnings_growth_component(fundamentals.earnings_growth)
        + _score_analyst_rating_component(fundamentals.analyst_rating)
        + _score_target_upside_component(fundamentals.target_upside_pct)
    )


def _compute_conviction(fundamentals: _Fundamentals, technical: _TechnicalSignals,
                         option_type: Optional[str], position_in_range: float) -> float:
    """Achievable raw range is symmetric +/-11.0 (RSI 2.0 + MACD 1.5 + range
    1.5 + PE 0.5 + revenue 1.5 + earnings 1.5 + rating 1.5 + upside 1.0 = 11.0
    max; mirrored min). Rescaled onto the 5-wide half-range around baseline
    5.0 (not a baseline + clamp) so a 10.0 requires maxing EVERY component at
    once, not just clearing a handful of independent thresholds -- the old
    clamp approach let 20+ unrelated names all land on an identical 10.0/10."""
    raw_score = _score_technical_component(technical, option_type, position_in_range,
                                            fundamentals.pe_ratio)
    raw_score += _score_fundamental_component(fundamentals)
    MAX_RAW_SCORE = 11.0
    conviction = 5.0 + 5.0 * (raw_score / MAX_RAW_SCORE)
    return max(1, min(10, conviction))  # safety net only -- should rarely bind


# --- Heat status (RED/YELLOW/GREEN) determination. Checked in the same order
# as the original elif chain: each _heat_status_* below returns None (meaning
# "doesn't apply, check the next one") or a terminal (status, reason) tuple,
# exactly mirroring "if cond: ... elif cond2: ..." fall-through semantics. ---

def _build_heat_context(technical: _TechnicalSignals, trend: _TrendPositioning,
                         confirmation: _FundamentalConfirmation,
                         position_in_range: float) -> _HeatContext:
    pct_above_200ma = trend.pct_above_200ma
    vs200_s = f"{pct_above_200ma:+.0f}%" if pct_above_200ma is not None else "n/a (< 200d history)"
    upside_s = f"{confirmation.target_upside_pct:+.0f}%" if confirmation.target_upside_pct is not None else "n/a"
    return _HeatContext(
        rsi=technical.rsi,
        position_in_range=position_in_range,
        roc_7d=technical.roc_7d,
        bb_pct_b=technical.bb_data['pct_b'],
        pct_above_200ma=pct_above_200ma,
        structurally_extended=trend.structurally_extended,
        structurally_weak=trend.structurally_weak,
        supports_extension=confirmation.supports_extension,
        confirms_weakness=confirmation.confirms_weakness,
        vs200_s=vs200_s,
        upside_s=upside_s,
    )


def _heat_status_spike_up(ctx: _HeatContext) -> Optional[Tuple[str, str]]:
    if ctx.roc_7d is None or ctx.roc_7d <= 12:
        return None
    roc_7d = ctx.roc_7d
    if ctx.structurally_extended and not ctx.supports_extension:
        return "RED", f"Spiked {roc_7d:.0f}% in 7 days AND {ctx.pct_above_200ma:.0f}% above its 200-day average — genuinely extended, not just a pop"
    if ctx.structurally_extended:
        return "YELLOW", f"Spiked {roc_7d:.0f}% in 7 days, {ctx.pct_above_200ma:.0f}% above its 200-day average, but analyst upside still {ctx.upside_s} — may be fundamentally supported, watch rather than force a close"
    return "YELLOW", f"Spiked {roc_7d:.0f}% in 7 days but only {ctx.vs200_s} vs its 200-day average — short-term move, not structurally extended"


def _heat_status_bollinger_up(ctx: _HeatContext) -> Optional[Tuple[str, str]]:
    if ctx.bb_pct_b <= 1.0:
        return None
    if ctx.structurally_extended and not ctx.supports_extension:
        return "RED", f"Above upper Bollinger Band AND {ctx.pct_above_200ma:.0f}% above its 200-day average — confirmed extension"
    if ctx.structurally_extended:
        return "YELLOW", f"Above upper Bollinger Band and {ctx.pct_above_200ma:.0f}% above its 200-day average, but analyst upside still {ctx.upside_s} — may be fundamentally supported"
    return "YELLOW", f"Above upper Bollinger Band, but {ctx.vs200_s} vs its 200-day average — short-term only, not confirmed"


def _heat_status_overbought(ctx: _HeatContext) -> Optional[Tuple[str, str]]:
    if not (ctx.rsi > 75 or ctx.position_in_range > 90):
        return None
    if ctx.structurally_extended and not ctx.supports_extension:
        return "RED", f"Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only {ctx.upside_s}"
    if ctx.structurally_extended:
        return "YELLOW", f"Technically extended ({ctx.vs200_s} vs 200-day average), but analyst upside still {ctx.upside_s} — may be fundamentally supported, watch rather than force a close"
    return "YELLOW", f"RSI/range reads overbought, but {ctx.vs200_s} vs its 200-day average — watch, don't force a close"


def _heat_status_spike_down(ctx: _HeatContext) -> Optional[Tuple[str, str]]:
    if ctx.roc_7d is None or ctx.roc_7d >= -12:
        return None
    roc_7d = ctx.roc_7d
    if ctx.structurally_weak and ctx.confirms_weakness:
        return "RED", f"Dropped {roc_7d:.0f}% in 7 days, {ctx.pct_above_200ma:.0f}% below its 200-day average, AND analyst upside only {ctx.upside_s} — thesis may be broken, not a dip"
    if ctx.structurally_weak:
        return "GREEN", f"Dropped {roc_7d:.0f}% in 7 days AND {ctx.pct_above_200ma:.0f}% below its 200-day average — genuinely beaten down"
    return "YELLOW", f"Dropped {roc_7d:.0f}% in 7 days but only {ctx.vs200_s} vs its 200-day average — pullback within trend, verify thesis before treating as an entry"


def _heat_status_bollinger_down(ctx: _HeatContext) -> Optional[Tuple[str, str]]:
    if ctx.bb_pct_b >= 0.0:
        return None
    if ctx.structurally_weak and ctx.confirms_weakness:
        return "RED", f"Below lower Bollinger Band, {ctx.pct_above_200ma:.0f}% below its 200-day average, AND analyst upside only {ctx.upside_s} — verify thesis before averaging down"
    if ctx.structurally_weak:
        return "GREEN", f"Below lower Bollinger Band AND {ctx.pct_above_200ma:.0f}% below its 200-day average — genuinely oversold"
    return "YELLOW", f"Below lower Bollinger Band, but {ctx.vs200_s} vs its 200-day average — short-term only, not confirmed"


def _heat_status_oversold(ctx: _HeatContext) -> Optional[Tuple[str, str]]:
    if not (ctx.rsi < 25 or ctx.position_in_range < 10):
        return None
    if ctx.structurally_weak and ctx.confirms_weakness:
        return "RED", f"Oversold on RSI/range, but {ctx.vs200_s} vs 200-day average AND analyst upside only {ctx.upside_s} — this may be the DRREDDY pattern (cheap-looking, thesis actually broken), not a bargain"
    if ctx.structurally_weak:
        return "GREEN", "Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning"
    return "YELLOW", f"RSI/range reads oversold, but {ctx.vs200_s} vs its 200-day average — verify before treating as attractive"


def _heat_status_neutral(ctx: _HeatContext) -> Optional[Tuple[str, str]]:
    if 30 < ctx.rsi < 70 and 30 < ctx.position_in_range < 70:
        return "GREEN", "Neutral positioning"
    return None


def _heat_status_catchall(ctx: _HeatContext) -> Tuple[str, str]:
    """Transition zone just inside the outer 25/75 RSI and 10/90 range bounds
    already excluded above -- names the actual RSI/range value(s) that
    tripped it and which threshold they're approaching, rather than a
    generic "approaching extremes" with no numbers."""
    heat_status = "YELLOW"
    triggers = []
    if ctx.rsi >= 70:
        triggers.append(f"RSI {ctx.rsi:.0f} approaching overbought (70+)")
    elif ctx.rsi <= 30:
        triggers.append(f"RSI {ctx.rsi:.0f} approaching oversold (30-)")
    if ctx.position_in_range >= 70:
        triggers.append(f"{ctx.position_in_range:.0f}% of 52-week range approaching the high extreme (90%+)")
    elif ctx.position_in_range <= 30:
        triggers.append(f"{ctx.position_in_range:.0f}% of 52-week range approaching the low extreme (10%-)")
    heat_reason = "; ".join(triggers) if triggers else f"RSI {ctx.rsi:.0f}, {ctx.position_in_range:.0f}% of 52-week range — mixed signal, not cleanly neutral"
    return heat_status, heat_reason


def _determine_heat_status(ctx: _HeatContext) -> Tuple[str, str]:
    """Heat status (RED/YELLOW/GREEN). The two recency checks (spike/Bollinger)
    run FIRST -- a stock that just spiked/dropped hard in the last week or
    last 20 sessions deserves flagging even when RSI(14)/52-week positioning
    haven't caught up to it yet."""
    checks = (
        _heat_status_spike_up, _heat_status_bollinger_up, _heat_status_overbought,
        _heat_status_spike_down, _heat_status_bollinger_down, _heat_status_oversold,
        _heat_status_neutral,
    )
    for check in checks:
        result = check(ctx)
        if result is not None:
            return result
    return _heat_status_catchall(ctx)


def _build_metrics_result(r: _MetricsResult) -> Dict:
    """Assemble the documented public return dict -- field names/types/
    rounding must match byte-for-byte what report-generation callers expect."""
    f = r.fundamentals
    t = r.technical
    tr = r.trend
    return {
        "ticker": r.ticker,
        "price": round(r.current_price, 2),
        "conviction": round(r.conviction, 1),
        "rsi": round(t.rsi, 1),
        "macd": round(t.macd_data['macd'], 4),
        "macd_histogram": round(t.macd_data['histogram'], 4),
        "bb_position": round(t.bb_data['pct_b'], 2),
        "roc_7d": round(t.roc_7d, 1) if t.roc_7d is not None else None,
        "pct_above_50ma": round(tr.pct_above_50ma, 1) if tr.pct_above_50ma is not None else None,
        "pct_above_200ma": round(tr.pct_above_200ma, 1) if tr.pct_above_200ma is not None else None,
        "position_in_52w_range": round(r.position_in_range, 1),
        "week_52_high": round(f.week_52_high, 2) if f.week_52_high else None,
        "week_52_low": round(f.week_52_low, 2) if f.week_52_low else None,
        "pe_ratio": round(f.pe_ratio, 2) if f.pe_ratio else None,
        "heat_status": r.heat_status,
        "heat_reason": r.heat_reason,
        "revenue_growth": round(f.revenue_growth * 100, 1) if f.revenue_growth is not None else None,
        "earnings_growth": round(f.earnings_growth * 100, 1) if f.earnings_growth is not None else None,
        "analyst_rating": f.analyst_rating,
        "target_upside_pct": round(f.target_upside_pct, 1) if f.target_upside_pct is not None else None,
    }


def _fallback_metrics_result(ticker: str, current_price: float) -> Dict:
    """Unchanged from the pre-refactor except-block fallback, including its
    pre-existing (out of scope for this refactor) omission of
    pct_above_50ma/pct_above_200ma keys -- this path is a true fallback only
    on an actual exception (e.g. network outage), not exercised by the
    existing "no data" characterization test (that ticker runs the normal
    success path with mostly-None fields instead)."""
    return {
        "ticker": ticker,
        "price": round(current_price, 2),
        "conviction": 5.0,
        "rsi": 50.0,
        "macd": 0.0,
        "macd_histogram": 0.0,
        "bb_position": 0.5,
        "roc_7d": None,
        "position_in_52w_range": 50.0,
        "week_52_high": None,
        "week_52_low": None,
        "pe_ratio": None,
        "heat_status": "YELLOW",
        "heat_reason": "Data unavailable",
        "revenue_growth": None,
        "earnings_growth": None,
        "analyst_rating": None,
        "target_upside_pct": None,
    }


def get_ticker_metrics(ticker: str, current_price: float, option_type: str = None) -> Dict:
    """Get comprehensive metrics for a ticker from Yahoo Finance.

    option_type: None (default) or 'C'/'CALL' use the original RSI treatment
    (calibrated for call-side risk: overbought = bad). Pass 'P'/'PUT' to use
    the put-side RSI treatment instead — see _score_rsi_component for why
    these differ. Default is unchanged so all existing callers (portfolio-wide
    ticker tiering in batch_get_metrics, sector rotation) keep prior behavior;
    pass 'P' explicitly wherever the caller knows it's evaluating a put entry.
    """
    try:
        stock = yf.Ticker(ticker)
        fundamentals = _fetch_fundamentals(stock, current_price)
        position_in_range = _position_in_52w_range(
            current_price, fundamentals.week_52_high, fundamentals.week_52_low)

        closes = _fetch_price_history(stock, current_price)
        technical = _compute_technical_signals(closes)
        trend = _compute_trend_positioning(closes, current_price)
        confirmation = _compute_fundamental_confirmation(fundamentals)

        conviction = _compute_conviction(fundamentals, technical, option_type, position_in_range)

        heat_ctx = _build_heat_context(technical, trend, confirmation, position_in_range)
        heat_status, heat_reason = _determine_heat_status(heat_ctx)

        result = _MetricsResult(
            ticker=ticker, current_price=current_price, conviction=conviction,
            technical=technical, trend=trend, position_in_range=position_in_range,
            fundamentals=fundamentals, heat_status=heat_status, heat_reason=heat_reason,
        )
        return _build_metrics_result(result)
    except Exception as e:
        logger.warning(f"Error fetching metrics for {ticker}: {e}")
        return _fallback_metrics_result(ticker, current_price)


_METRICS_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "ticker_metrics_cache.json",
)
_METRICS_CACHE_TTL_SECONDS = 600  # 10 min
_INTER_TICKER_DELAY_SECONDS = 0.35


def _load_metrics_cache() -> dict:
    try:
        with open(_METRICS_CACHE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_metrics_cache(cache: dict) -> None:
    try:
        os.makedirs(os.path.dirname(_METRICS_CACHE_FILE), exist_ok=True)
        tmp = _METRICS_CACHE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(cache, f)
        os.replace(tmp, _METRICS_CACHE_FILE)
        # Written by both the host user and the dashboard's own Docker
        # container (root, no USER directive) -- same cross-process lockout
        # already found and fixed on macro_risk_history.yaml 2026-10-02.
        os.chmod(_METRICS_CACHE_FILE, 0o664)
    except Exception:
        pass


def batch_get_metrics(tickers: list, prices: dict, option_types: dict = None) -> dict:
    """Get metrics for multiple tickers.

    option_types: optional {ticker: 'P'|'C'} — the dominant option type held
    for that ticker, so the RSI component uses the right calibration (see
    get_ticker_metrics). Omit to keep the prior call-context/generic default.

    Cached (10 min TTL) + paced (0.35s between cold-cache tickers) as of
    2026-10-02 -- this function previously fired ~90 tickers x 2+ yfinance
    calls each with zero delay and no cache, every single time ANY report
    type was generated or the dashboard refreshed. Confirmed live the same
    day: a normal work session (reconciliation check + 4 report types +
    two dashboard refreshes, all within ~20 minutes) racked up 156 "Too
    Many Requests" hits and degraded every one of 90 tickers to the
    "Data unavailable" fallback (conviction 5.0, RSI 50 for all of them)
    at once -- not a code bug, a real rate-limit lockout from request
    volume. A "Data unavailable" result is never written to the cache
    (so a bad read doesn't poison the next 10 minutes for every caller),
    and is always treated as a cache miss on read for the same reason.
    """
    option_types = option_types or {}
    cache = _load_metrics_cache()
    now = time.time()
    results = {}
    misses = []
    for ticker in tickers:
        cached = cache.get(ticker)
        if cached and cached.get("heat_reason") != "Data unavailable" and (now - cached.get("_cached_at", 0)) < _METRICS_CACHE_TTL_SECONDS:
            results[ticker] = {k: v for k, v in cached.items() if k != "_cached_at"}
        else:
            misses.append(ticker)

    for i, ticker in enumerate(misses):
        price = prices.get(ticker, 0)
        m = get_ticker_metrics(ticker, price, option_type=option_types.get(ticker))
        results[ticker] = m
        if m.get("heat_reason") != "Data unavailable":
            cache[ticker] = {**m, "_cached_at": now}
        if i < len(misses) - 1:
            time.sleep(_INTER_TICKER_DELAY_SECONDS)

    if misses:
        _save_metrics_cache(cache)
    return results


if __name__ == '__main__':
    # Test
    metrics = get_ticker_metrics("NFLX", 85.9)
    print("NFLX Metrics:")
    for key, val in metrics.items():
        print(f"  {key}: {val}")
