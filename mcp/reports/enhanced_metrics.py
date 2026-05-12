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


def get_ticker_metrics(ticker: str, current_price: float) -> Dict:
    """Get comprehensive metrics for a ticker from Yahoo Finance"""

    try:
        stock = yf.Ticker(ticker)

        # Get fundamentals
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        week_52_high = info.get('fiftyTwoWeekHigh', None)
        week_52_low = info.get('fiftyTwoWeekLow', None)

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

        # Determine conviction score (0-10) based on multiple factors
        conviction = 5.0  # baseline

        # RSI contribution: 0-2 points
        if rsi < 30:
            conviction += 2.0  # Oversold = bullish
        elif rsi > 70:
            conviction -= 1.0  # Overbought = bearish
        elif 40 < rsi < 60:
            conviction += 0.5  # Neutral tendency

        # MACD contribution: 0-2 points
        if macd_data['histogram'] > 0 and macd_data['macd'] > macd_data['signal']:
            conviction += 1.5  # Bullish
        elif macd_data['histogram'] < 0 and macd_data['macd'] < macd_data['signal']:
            conviction -= 1.0  # Bearish

        # Position in range contribution: 0-1.5 points
        if position_in_range < 25:
            conviction += 1.5  # Near 52-week low = attractive
        elif position_in_range > 85:
            conviction -= 1.0  # Near 52-week high = extended

        # P/E ratio contribution: 0-1 point
        if pe_ratio and 15 < pe_ratio < 30:
            conviction += 0.5  # Fair valuation
        elif pe_ratio and pe_ratio > 40:
            conviction -= 0.5  # Expensive

        conviction = max(1, min(10, conviction))  # Clamp to 1-10

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
        }


def batch_get_metrics(tickers: list, prices: dict) -> dict:
    """Get metrics for multiple tickers"""
    results = {}
    for ticker in tickers:
        price = prices.get(ticker, 0)
        results[ticker] = get_ticker_metrics(ticker, price)
    return results


if __name__ == '__main__':
    # Test
    metrics = get_ticker_metrics("NFLX", 85.9)
    print("NFLX Metrics:")
    for key, val in metrics.items():
        print(f"  {key}: {val}")
