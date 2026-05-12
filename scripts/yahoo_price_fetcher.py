"""
Yahoo Finance Price Fetcher with Intelligent Rate Limiting
Batch downloads with exponential backoff and retry logic
"""

import yfinance as yf
import pandas as pd
import time
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YahooFinanceFetcher:
    """Fetch live prices from Yahoo Finance with batch requests and rate limiting"""

    def __init__(self, batch_size=10, delay_seconds=2.0, max_retries=3):
        """
        Initialize fetcher with batch downloading

        Args:
            batch_size: Symbols per batch (optimal: 5-15)
            delay_seconds: Delay between batches
            max_retries: Max retries per batch
        """
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.price_cache = {}

    def fetch_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetch prices using batch downloads with intelligent retry

        Args:
            symbols: List of tickers to fetch

        Returns:
            Dict of {symbol: price}
        """
        if not symbols:
            return {}

        # Normalize symbols
        symbols = [s.upper().strip() for s in symbols if s]
        symbols = list(set(symbols))

        logger.info(f"Fetching prices for {len(symbols)} symbols in batches of {self.batch_size}...")

        prices = {}
        failed = []

        # Process in batches
        for batch_num, i in enumerate(range(0, len(symbols), self.batch_size)):
            batch = symbols[i : i + self.batch_size]

            logger.info(f"  Batch {batch_num + 1}: {', '.join(batch)}")
            batch_prices = self._fetch_batch_with_retry(batch)

            # Track results
            prices.update(batch_prices)
            fetched = set(batch_prices.keys())
            batch_failed = [s for s in batch if s not in fetched]
            failed.extend(batch_failed)

            # Rate limiting between batches
            if i + self.batch_size < len(symbols):
                time.sleep(self.delay_seconds)

        # Report
        success = len(prices)
        total = len(symbols)
        logger.info(f"✓ Fetched {success}/{total} prices")
        if failed:
            logger.warning(f"✗ Failed: {', '.join(failed[:5])}")

        # Cache
        self.price_cache.update(prices)
        return prices

    def _fetch_batch_with_retry(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch batch with exponential backoff"""
        prices = {}

        for attempt in range(self.max_retries):
            try:
                # Batch download - yfinance handles multiple tickers efficiently
                data = yf.download(
                    symbols, period="1d", progress=False, threads=False
                )

                # Parse multi-index DataFrame
                if not data.empty:
                    # yfinance returns multi-index: (OHLCV, symbol)
                    for symbol in symbols:
                        try:
                            if ("Close", symbol) in data.columns:
                                close = data[("Close", symbol)].iloc[-1]
                            elif symbol in data.columns:
                                close = data[symbol]["Close"].iloc[-1]
                            else:
                                continue

                            if pd.notna(close):
                                prices[symbol] = float(close)
                                logger.info(f"    ✓ {symbol}: ${prices[symbol]:.2f}")
                        except:
                            pass

                return prices  # Success

            except Exception as e:
                wait = 2**attempt
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"    Attempt {attempt + 1} failed: {type(e).__name__}. "
                        f"Waiting {wait}s..."
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"    All retries exhausted")

        return prices

    def get_cached(self, symbol: str) -> Optional[float]:
        """Get cached price"""
        return self.price_cache.get(symbol.upper())

    def clear_cache(self):
        """Clear cache"""
        self.price_cache.clear()


# Global instance
_fetcher = None


def get_fetcher() -> YahooFinanceFetcher:
    """Get global fetcher"""
    global _fetcher
    if _fetcher is None:
        _fetcher = YahooFinanceFetcher(batch_size=10, delay_seconds=2.0, max_retries=3)
    return _fetcher


def fetch_prices(symbols: List[str]) -> Dict[str, float]:
    """Convenience function"""
    return get_fetcher().fetch_prices(symbols)


if __name__ == "__main__":
    # Test
    test_symbols = [
        "AXON",
        "CRWD",
        "META",
        "SHOP",
        "ASML",
        "BA",
        "NFLX",
        "ABNB",
        "DIS",
        "EXPE",
        "GEV",
        "VST",
        "LMT",
    ]

    fetcher = YahooFinanceFetcher(batch_size=5)
    prices = fetcher.fetch_prices(test_symbols)

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    for symbol in test_symbols:
        price = prices.get(symbol)
        if price:
            print(f"  {symbol:8} ${price:>8.2f}")
        else:
            print(f"  {symbol:8} FAILED")
