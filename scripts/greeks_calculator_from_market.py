"""
Calculate Greeks from market data using Black-Scholes.

Fetches live prices and IV from Yahoo Finance, then calculates delta/gamma/vega/theta.
No manual data entry needed.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import norm
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')


class BlackScholesCalculator:
    """Calculate option Greeks using Black-Scholes model."""

    RISK_FREE_RATE = 0.045  # Current ~4.5%

    @staticmethod
    def calculate_iv(S: float, K: float, C: float, T: float, r: float = 0.045) -> float:
        """
        Estimate implied volatility from option price using Newton-Raphson.

        Args:
            S: Current stock price
            K: Strike price
            C: Option price (market price)
            T: Time to expiration (years)
            r: Risk-free rate

        Returns:
            Implied volatility (annualized)
        """
        sigma = 0.3  # Starting guess: 30% IV

        for _ in range(20):  # Iterate to convergence
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)

            call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            vega = S * norm.pdf(d1) * np.sqrt(T)

            if abs(call_price - C) < 0.01:
                return sigma

            sigma = sigma - (call_price - C) / vega

        return sigma

    @staticmethod
    def calculate_greeks(
        S: float,
        K: float,
        T: float,
        sigma: float,
        option_type: str = 'CALL',
        r: float = 0.045,
        dividend_yield: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate option Greeks using Black-Scholes.

        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            sigma: Volatility (annualized)
            option_type: 'CALL' or 'PUT'
            r: Risk-free rate
            dividend_yield: Annual dividend yield

        Returns:
            Dict with delta, gamma, vega, theta
        """
        if T <= 0:
            # Expired
            if option_type == 'CALL':
                return {'delta': 1.0 if S > K else 0.0, 'gamma': 0, 'vega': 0, 'theta': 0}
            else:
                return {'delta': -1.0 if S < K else 0.0, 'gamma': 0, 'vega': 0, 'theta': 0}

        d1 = (np.log(S / K) + (r - dividend_yield + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'CALL':
            delta = np.exp(-dividend_yield * T) * norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma * np.exp(-dividend_yield * T) / (2 * np.sqrt(T))
                    - r * K * np.exp(-r * T) * norm.cdf(d2)
                    + dividend_yield * S * np.exp(-dividend_yield * T) * norm.cdf(d1)) / 365
        else:  # PUT
            delta = np.exp(-dividend_yield * T) * (norm.cdf(d1) - 1)
            theta = (-S * norm.pdf(d1) * sigma * np.exp(-dividend_yield * T) / (2 * np.sqrt(T))
                    + r * K * np.exp(-r * T) * norm.cdf(-d2)
                    - dividend_yield * S * np.exp(-dividend_yield * T) * norm.cdf(-d1)) / 365

        gamma = norm.pdf(d1) * np.exp(-dividend_yield * T) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) * np.exp(-dividend_yield * T) / 100  # Per 1% IV change

        return {
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta
        }


class MarketDataFetcher:
    """Fetch live data from Yahoo Finance."""

    @staticmethod
    def get_stock_price(symbol: str) -> Optional[float]:
        """Fetch current stock price from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if data.empty:
                return None
            return data['Close'].iloc[-1]
        except Exception as e:
            print(f"  ✗ Error fetching {symbol}: {e}")
            return None

    @staticmethod
    def get_option_chain(symbol: str) -> Optional[pd.DataFrame]:
        """Fetch option chain from Yahoo Finance (calls + puts)."""
        try:
            ticker = yf.Ticker(symbol)
            expirations = ticker.options

            if not expirations:
                return None

            all_options = []
            for exp_date in expirations[:3]:  # Get first 3 expirations
                call_chain = ticker.option_chain(exp_date).calls
                put_chain = ticker.option_chain(exp_date).puts

                call_chain['type'] = 'CALL'
                put_chain['type'] = 'PUT'

                all_options.append(call_chain)
                all_options.append(put_chain)

            return pd.concat(all_options, ignore_index=True) if all_options else None
        except Exception as e:
            print(f"  ✗ Error fetching option chain for {symbol}: {e}")
            return None

    @staticmethod
    def get_dividend_yield(symbol: str) -> float:
        """Fetch dividend yield from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            div_yield = ticker.info.get('dividendYield', 0)
            return div_yield if div_yield else 0.0
        except:
            return 0.0


class GreeksEnricher:
    """Enrich position data with calculated Greeks."""

    @staticmethod
    def parse_option_symbol(symbol) -> Optional[Dict]:
        """
        Parse option symbol to extract strike, expiry, type.

        Handles two formats:
        1. Schwab description: "EXPE MAR 19 2027 $200 PUT"
        2. Schwab code: "-EXPE270319P200" (EXPE Mar 19 2027 $200 PUT)
        """
        if not isinstance(symbol, str) or pd.isna(symbol):
            return None

        symbol = symbol.strip().upper()

        # Try Schwab description format first: "SYMBOL MMM DD YYYY $STRIKE TYPE"
        # Example: "EXPE MAR 19 2027 $200 PUT"
        parts = symbol.split()

        if len(parts) >= 5 and parts[-1] in ['PUT', 'CALL']:
            try:
                base_symbol = parts[0]
                month_str = parts[1]
                day = int(parts[2])
                year = int(parts[3])

                # Find strike (starts with $)
                strike = None
                for part in parts:
                    if '$' in part:
                        strike = float(part.replace('$', ''))
                        break

                if strike is None:
                    return None

                # Month mapping
                month_map = {
                    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
                }

                month = month_map.get(month_str)
                if month is None:
                    return None

                expiry_date = datetime(year, month, day)
                option_type = parts[-1]

                return {
                    'base_symbol': base_symbol,
                    'strike': strike,
                    'expiry': expiry_date,
                    'type': option_type
                }
            except (ValueError, IndexError):
                pass

        # Try Schwab code format: "-SYMBOL[YYMMDDxxxx]TYPE"
        if not symbol.startswith('-'):
            return None  # Not an option in code format

        symbol = symbol[1:]  # Remove leading dash

        # Extract base symbol and code
        for i in range(len(symbol)):
            if symbol[i].isdigit():
                base = symbol[:i]
                code = symbol[i:]
                break
        else:
            return None

        if len(code) < 7:
            return None

        # YYMMDD = first 6 digits
        try:
            yy, mm, dd = int(code[0:2]), int(code[2:4]), int(code[4:6])
            year = 2000 + yy if yy <= 50 else 1900 + yy
            expiry_date = datetime(year, mm, dd)
        except ValueError:
            return None

        # Remaining = strike + type
        remainder = code[6:].rstrip('0')  # Remove trailing zeros

        # Last char is type (P=PUT, C=CALL)
        option_type = remainder[-1]
        if option_type not in ['P', 'C']:
            return None

        strike_str = remainder[:-1]
        try:
            strike = float(strike_str[:-2] + '.' + strike_str[-2:]) if len(strike_str) > 2 else float(strike_str)
        except ValueError:
            return None

        return {
            'base_symbol': base,
            'strike': strike,
            'expiry': expiry_date,
            'type': 'PUT' if option_type == 'P' else 'CALL'
        }

    @staticmethod
    def enrich_positions(positions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Greeks columns to positions dataframe.

        Fetches live market data and calculates Greeks for all option positions.
        """
        if positions_df.empty:
            return positions_df

        # Ensure required columns
        positions_df = positions_df.copy()
        positions_df['symbol'] = positions_df['symbol'].astype(str).str.strip()

        # Add Greeks columns
        for col in ['delta', 'gamma', 'vega', 'theta', 'mark_price', 'iv']:
            if col not in positions_df.columns:
                positions_df[col] = 0.0

        print("\nCalculating Greeks from market data...\n")

        # Group by unique base symbols to minimize API calls
        unique_symbols = set()
        symbol_map = {}

        for symbol in positions_df['symbol'].unique():
            parsed = GreeksEnricher.parse_option_symbol(symbol)
            if parsed:
                base = parsed['base_symbol']
                unique_symbols.add(base)
                symbol_map[symbol] = parsed

        # Fetch stock prices once per symbol
        stock_prices = {}
        dividend_yields = {}
        for base_symbol in unique_symbols:
            price = MarketDataFetcher.get_stock_price(base_symbol)
            if price:
                stock_prices[base_symbol] = price
                dividend_yields[base_symbol] = MarketDataFetcher.get_dividend_yield(base_symbol)
                print(f"  ✓ {base_symbol}: ${price:.2f}")
            else:
                print(f"  ✗ {base_symbol}: Could not fetch price")

        # Calculate Greeks for each option position
        print("\nCalculating Greeks:\n")
        for idx, row in positions_df.iterrows():
            symbol = row['symbol']
            parsed = symbol_map.get(symbol)

            if not parsed:
                continue

            base = parsed['base_symbol']
            if base not in stock_prices:
                continue

            S = stock_prices[base]
            K = parsed['strike']
            T = (parsed['expiry'] - datetime.now()).days / 365.25
            option_type = parsed['type']
            div_yield = dividend_yields.get(base, 0.0)

            # Estimate IV from mark price if available, else use 30%
            if 'mark_price' in row and pd.notna(row['mark_price']) and row['mark_price'] > 0:
                mark = row['mark_price']
                iv = BlackScholesCalculator.calculate_iv(S, K, mark, T)
            else:
                iv = 0.30  # Default: 30% IV

            # Calculate Greeks
            greeks = BlackScholesCalculator.calculate_greeks(S, K, T, iv, option_type, dividend_yield=div_yield)

            positions_df.loc[idx, 'delta'] = greeks['delta']
            positions_df.loc[idx, 'gamma'] = greeks['gamma']
            positions_df.loc[idx, 'vega'] = greeks['vega']
            positions_df.loc[idx, 'theta'] = greeks['theta']
            positions_df.loc[idx, 'iv'] = iv

            print(f"  {symbol:20} δ={greeks['delta']:+.3f}  γ={greeks['gamma']:+.4f}  θ={greeks['theta']:+.2f}")

        return positions_df


if __name__ == "__main__":
    # Test
    print("Testing Greeks calculation from market data\n")

    # Example: EXPE Mar 19 2027 $200 PUT
    S = 100  # Stock price
    K = 200  # Strike
    T = 0.87  # Years to expiration
    sigma = 0.30  # IV

    greeks = BlackScholesCalculator.calculate_greeks(S, K, T, sigma, 'PUT')
    print(f"EXPE 270319 $200 PUT:")
    print(f"  Delta: {greeks['delta']:+.3f}")
    print(f"  Gamma: {greeks['gamma']:+.4f}")
    print(f"  Vega: {greeks['vega']:+.2f}")
    print(f"  Theta: {greeks['theta']:+.2f}")
