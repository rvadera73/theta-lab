"""
Enhanced metrics from Yahoo Finance — Greeks, conviction, technical indicators, position heat
"""

import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

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


def get_ticker_metrics(ticker: str, current_price: float, option_type: str = None) -> Dict:
    """Get comprehensive metrics for a ticker from Yahoo Finance.

    option_type: None (default) or 'C'/'CALL' use the original RSI treatment
    (calibrated for call-side risk: overbought = bad). Pass 'P'/'PUT' to use
    the put-side RSI treatment instead — see the RSI block below for why
    these differ. Default is unchanged so all existing callers (portfolio-wide
    ticker tiering in batch_get_metrics, sector rotation) keep prior behavior;
    pass 'P' explicitly wherever the caller knows it's evaluating a put entry.
    """

    try:
        stock = yf.Ticker(ticker)

        # Get fundamentals
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

        # Calculate position in 52-week range (0-100)
        position_in_range = 50.0
        if week_52_high and week_52_low and week_52_high > week_52_low:
            position_in_range = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
            position_in_range = max(0, min(100, position_in_range))

        # Get historical data for technical indicators
        hist = stock.history(period="1y")
        if len(hist) == 0:
            hist = stock.history(period="6mo")

        closes = hist['Close'] if len(hist) > 0 else pd.Series([current_price])

        # Calculate technical indicators
        rsi = TechnicalIndicators.rsi(closes)
        macd_data = TechnicalIndicators.macd(closes)
        bb_data = TechnicalIndicators.bollinger_bands(closes)

        # Determine conviction score (0-10). Fundamentals are weighted as the
        # PRIMARY signal (larger swing) with technicals SUPPLEMENTAL — matching
        # the trading persona's stated philosophy ("fundamentals + macro instinct
        # is the research engine... technicals are supplemental, not primary").
        # A technical-only version of this formula shipped 2026-07-19 and was found
        # to score Dr Reddy's (DRREDDY.NS) at 8.0/10 — the HIGHEST conviction in a
        # 23-name India audit — purely because it was oversold with a "fair" PE,
        # while its earnings had actually collapsed -86% YoY with an analyst
        # downgrade to hold. That's the exact failure mode this weighting prevents.
        # Accumulate a raw score first, then rescale by its own achievable range
        # (below) rather than adding to a baseline and clamping the overflow.
        # The old approach (baseline 5.0 + additive points, clamp to 1-10) let the
        # raw sum run from -11 to +11 around that baseline (range of 22) while the
        # display range is only 9 wide — any stock clearing roughly half its
        # criteria strongly blew past the ceiling. Result: 20+ completely
        # different names (SaaS platforms next to a cyclical memory-chip maker)
        # all landed on the identical "10.0/10", destroying differentiation at
        # exactly the point where it matters most (ranking "best of the best").
        raw_score = 0.0

        # --- Technical component (supplemental) ---
        # RSI contribution — direction-dependent (GitHub issue #1, backtest
        # 2026-07-31 against 343 real closed trades from Account A, split by
        # option type). A single "overbought = bad" rule is only true for
        # calls; puts showed the opposite pattern in this account's actual
        # history, so the two are now scored separately rather than sharing
        # one sign.
        is_put = str(option_type or '').upper() in ('P', 'PUT')
        if is_put:
            # PUT calibration — n=343 backtest: overbought entries were this
            # account's BEST-performing put setup (98.3% win rate, n=59, mean
            # +25.1%), not the worst. Neutral (91.0%, n=100) and oversold
            # (92.9%, n=14 — smallest sample) were close behind. All three
            # buckets are strong for puts, so contributions are modest and
            # uniformly positive rather than mirroring the call-side swing —
            # the data doesn't support a bigger spread than this at n=343.
            if rsi > 70:
                raw_score += 1.0   # best-performing put bucket in backtest
            elif 40 < rsi < 60:
                raw_score += 0.75  # neutral, nearly as strong
            elif rsi < 30:
                raw_score += 0.75  # smallest sample (n=14) — don't overweight
        else:
            # CALL calibration (also the default when option_type not given —
            # existing generic ticker-tiering use). Backtest confirmed this
            # direction is correct for calls: oversold entries were calls'
            # best setup (84.0% win rate, +20.1% mean), overbought their worst
            # (72.7% win rate) — matches the original "AI melt-up" heat-scanner
            # warning. Max +2.0 / min -1.0.
            if rsi < 30:
                raw_score += 2.0  # Oversold = bullish
            elif rsi > 70:
                raw_score -= 1.0  # Overbought = bearish
            elif 40 < rsi < 60:
                raw_score += 0.5  # Neutral tendency

        # MACD contribution: max +1.5 / min -1.0
        if macd_data['histogram'] > 0 and macd_data['macd'] > macd_data['signal']:
            raw_score += 1.5  # Bullish
        elif macd_data['histogram'] < 0 and macd_data['macd'] < macd_data['signal']:
            raw_score -= 1.0  # Bearish

        # Position in range contribution: max +1.5 / min -1.0
        if position_in_range < 25:
            raw_score += 1.5  # Near 52-week low = attractive
        elif position_in_range > 85:
            raw_score -= 1.0  # Near 52-week high = extended

        # P/E ratio contribution: max +0.5 / min -0.5
        if pe_ratio and 15 < pe_ratio < 30:
            raw_score += 0.5  # Fair valuation
        elif pe_ratio and pe_ratio > 40:
            raw_score -= 0.5  # Expensive

        # --- Fundamental component (primary — wider swing than technicals above) ---
        if revenue_growth is not None:
            if revenue_growth > 0.20:
                raw_score += 1.5  # max +1.5 / min -1.0
            elif revenue_growth > 0.05:
                raw_score += 0.5
            elif revenue_growth < -0.05:
                raw_score -= 1.0

        if earnings_growth is not None:
            if earnings_growth > 0.20:
                raw_score += 1.5  # max +1.5 / min -2.5
            elif earnings_growth >= 0:
                raw_score += 0.5
            elif earnings_growth > -0.20:
                raw_score -= 0.5
            else:
                raw_score -= 2.5  # Earnings deteriorating sharply — dominant signal

        if analyst_rating in ("strong_buy",):
            raw_score += 1.5  # max +1.5 / min -2.0
        elif analyst_rating in ("buy",):
            raw_score += 0.75
        elif analyst_rating in ("hold",):
            raw_score -= 0.5
        elif analyst_rating in ("sell", "strong_sell", "underperform"):
            raw_score -= 2.0

        if target_upside_pct is not None:
            if target_upside_pct > 15:
                raw_score += 1.0  # max +1.0 / min -2.0
            elif target_upside_pct > 0:
                raw_score += 0.3
            elif target_upside_pct > -15:
                raw_score -= 1.0
            else:
                raw_score -= 2.0  # Analyst target below current price

        # Achievable range derived directly from the max/min noted on each
        # component above: RSI(2.0) + MACD(1.5) + range(1.5) + PE(0.5)
        # + revenue(1.5) + earnings(1.5) + rating(1.5) + upside(1.0) = 11.0 max;
        # -1.0-1.0-1.0-0.5-1.0-2.5-2.0-2.0 = -11.0 min. Symmetric +/-11.
        # Rescale onto the 5-wide half-range around baseline 5.0 so hitting 10.0
        # requires maxing EVERY component at once (a true "perfect" stock), not
        # just clearing a handful of independent thresholds.
        MAX_RAW_SCORE = 11.0
        conviction = 5.0 + 5.0 * (raw_score / MAX_RAW_SCORE)
        conviction = max(1, min(10, conviction))  # safety net only — should rarely bind now

        # Determine heat status (RED/YELLOW/GREEN)
        if rsi > 75 or position_in_range > 90:
            heat_status = "RED"
            heat_reason = "Overbought / Extended"
        elif rsi < 25 or position_in_range < 10:
            heat_status = "GREEN"
            heat_reason = "Oversold / Attractive"
        elif 30 < rsi < 70 and 30 < position_in_range < 70:
            heat_status = "GREEN"
            heat_reason = "Neutral positioning"
        else:
            heat_status = "YELLOW"
            heat_reason = "Approaching extremes"

        return {
            "ticker": ticker,
            "price": round(current_price, 2),
            "conviction": round(conviction, 1),
            "rsi": round(rsi, 1),
            "macd": round(macd_data['macd'], 4),
            "macd_histogram": round(macd_data['histogram'], 4),
            "bb_position": round(bb_data['pct_b'], 2),
            "position_in_52w_range": round(position_in_range, 1),
            "week_52_high": round(week_52_high, 2) if week_52_high else None,
            "week_52_low": round(week_52_low, 2) if week_52_low else None,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
            "heat_status": heat_status,
            "heat_reason": heat_reason,
            "revenue_growth": round(revenue_growth * 100, 1) if revenue_growth is not None else None,
            "earnings_growth": round(earnings_growth * 100, 1) if earnings_growth is not None else None,
            "analyst_rating": analyst_rating,
            "target_upside_pct": round(target_upside_pct, 1) if target_upside_pct is not None else None,
        }
    except Exception as e:
        logger.warning(f"Error fetching metrics for {ticker}: {e}")
        return {
            "ticker": ticker,
            "price": round(current_price, 2),
            "conviction": 5.0,
            "rsi": 50.0,
            "macd": 0.0,
            "macd_histogram": 0.0,
            "bb_position": 0.5,
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


def batch_get_metrics(tickers: list, prices: dict, option_types: dict = None) -> dict:
    """Get metrics for multiple tickers.

    option_types: optional {ticker: 'P'|'C'} — the dominant option type held
    for that ticker, so the RSI component uses the right calibration (see
    get_ticker_metrics). Omit to keep the prior call-context/generic default.
    """
    option_types = option_types or {}
    results = {}
    for ticker in tickers:
        price = prices.get(ticker, 0)
        results[ticker] = get_ticker_metrics(ticker, price, option_type=option_types.get(ticker))
    return results


if __name__ == '__main__':
    # Test
    metrics = get_ticker_metrics("NFLX", 85.9)
    print("NFLX Metrics:")
    for key, val in metrics.items():
        print(f"  {key}: {val}")
