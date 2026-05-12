"""
Data Loader for May 11 Account Consolidation
Loads all 6 accounts and extracts open option positions with live prices
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import date
import sys

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
from yahoo_price_fetcher import YahooFinanceFetcher


class DataLoaderMay11:
    """Load consolidated account data from May 11 downloads"""

    def __init__(self, data_dir: str = '/home/rahulvadera/projects/theta-lab/data/positions'):
        self.data_dir = Path(data_dir)
        self.consolidated_df = None
        self.option_rows = None
        self.prices = {}

    def load_all_data(self) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Load all account data and fetch live prices"""
        self._load_accounts()
        self._extract_options()
        self._fetch_prices()
        return self.option_rows, self.prices

    def _load_accounts(self):
        """Load all 6 account files"""
        account_files = [
            ('Individual_XXX232_Transactions_20260511-113621.csv', 'Account A (232)'),
            ('Contributory_XXX275_Transactions_20260511-113648.csv', 'Account B (275)'),
            ('Designated_Bene_Individual_XXX634_Transactions_20260511-113723.csv', 'Account C (634)'),
            ('Accounts_History-fidelity-Rahul.csv', 'Fidelity (Rahul)'),
            ('Accounts_History-fidelity-Rajul.csv', 'Fidelity (Rajul)'),
        ]

        dfs = []
        for filename, account_name in account_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                df['account_name'] = account_name
                dfs.append(df)
                print(f"✓ Loaded {account_name}: {len(df)} rows")

        self.consolidated_df = pd.concat(dfs, ignore_index=True)
        self.consolidated_df.columns = self.consolidated_df.columns.str.strip().str.lower()
        # Use account_name consistently
        if 'account_name' not in self.consolidated_df.columns and 'account' in self.consolidated_df.columns:
            self.consolidated_df.rename(columns={'account': 'account_name'}, inplace=True)
        print(f"✓ Total: {len(self.consolidated_df)} rows")

    def _extract_options(self):
        """Extract option positions and calculate position counts"""
        def extract_ticker(symbol_str):
            if pd.isna(symbol_str):
                return None
            symbol_str = str(symbol_str).strip()
            match = re.match(r'^([A-Z]{1,5})\s', symbol_str)
            return match.group(1) if match else None

        self.consolidated_df['ticker'] = self.consolidated_df['symbol'].apply(extract_ticker)

        # Filter option transactions
        self.option_rows = self.consolidated_df[
            (self.consolidated_df['ticker'].notna()) &
            (self.consolidated_df['action'].isin(['Sell to Open', 'Buy to Close', 'Sell to Close', 'Buy to Open']))
        ].copy()

        # Extract contract details
        def extract_contract(symbol_str):
            if pd.isna(symbol_str):
                return {'ticker': None, 'expiry': None, 'strike': None, 'type': None}
            s = str(symbol_str).strip()
            # Pattern: TICKER DATE STRIKE TYPE
            # Example: BE 11/20/2026 190.00 P
            match = re.match(r'^([A-Z]{1,5})\s+(\d{1,2}/\d{1,2}/\d{4})\s+([\d.]+)\s+([CP])', s)
            if match:
                return {
                    'ticker': match.group(1),
                    'expiry': match.group(2),
                    'strike': float(match.group(3)),
                    'type': 'CALL' if match.group(4) == 'C' else 'PUT'
                }
            return {'ticker': None, 'expiry': None, 'strike': None, 'type': None}

        contract_info = self.option_rows['symbol'].apply(extract_contract)
        self.option_rows['expiry'] = contract_info.apply(lambda x: x['expiry'])
        self.option_rows['strike'] = contract_info.apply(lambda x: x['strike'])
        self.option_rows['type'] = contract_info.apply(lambda x: x['type'])

        print(f"✓ Found {len(self.option_rows)} option transactions")
        print(f"✓ Unique tickers: {self.option_rows['ticker'].nunique()}")

    def _fetch_prices(self):
        """Fetch live prices for all tickers"""
        tickers = sorted(self.option_rows['ticker'].unique().tolist())
        print(f"\nFetching {len(tickers)} live prices from Yahoo Finance...")

        fetcher = YahooFinanceFetcher(batch_size=10, delay_seconds=2.0, max_retries=3)
        self.prices = fetcher.fetch_prices(tickers)

        print(f"✓ Fetched {len(self.prices)} prices")

    def get_position_summary(self) -> pd.DataFrame:
        """Get summary of positions by symbol"""
        if self.option_rows is None:
            return pd.DataFrame()

        def join_accounts(x):
            accounts = [str(a) for a in x.unique() if pd.notna(a)]
            return ', '.join(accounts) if accounts else 'Unknown'

        summary = self.option_rows.groupby('ticker').agg({
            'symbol': 'count',
            'quantity': 'sum',
            'account_name': join_accounts,
            'type': lambda x: f"{(x=='CALL').sum()} Calls, {(x=='PUT').sum()} Puts"
        }).rename(columns={
            'symbol': 'transactions',
            'quantity': 'total_qty',
            'account_name': 'accounts',
            'type': 'position_mix'
        })

        summary['price'] = summary.index.map(lambda x: self.prices.get(x, 0))
        return summary.sort_values('transactions', ascending=False)

    def get_account_summary(self) -> pd.DataFrame:
        """Get position count by account"""
        if self.option_rows is None:
            return pd.DataFrame()

        return self.option_rows.groupby('account_name').size().to_frame('position_count').sort_values('position_count', ascending=False)


if __name__ == '__main__':
    loader = DataLoaderMay11()
    option_rows, prices = loader.load_all_data()

    print("\n" + "="*70)
    print("POSITION SUMMARY BY SYMBOL")
    print("="*70)
    summary = loader.get_position_summary()
    print(summary.head(20))

    print("\n" + "="*70)
    print("POSITION COUNT BY ACCOUNT")
    print("="*70)
    accounts = loader.get_account_summary()
    print(accounts)
