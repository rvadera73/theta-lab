"""
Final Data Loader — All 8 Accounts (May 11, 2026)
Loads: Schwab A/B/C, Fidelity x2, Vanguard, Robinhood x2
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import date
import sys

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
from yahoo_price_fetcher import YahooFinanceFetcher


class DataLoaderFinal:
    """Load all 8 accounts"""

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
        """Load all 8 account files"""
        dfs = []

        # Schwab accounts
        schwab_files = [
            ('Individual_XXX232_Transactions_20260511-113621.csv', 'Account A (232)'),
            ('Contributory_XXX275_Transactions_20260511-113648.csv', 'Account B (275)'),
            ('Designated_Bene_Individual_XXX634_Transactions_20260511-113723.csv', 'Account C (634)'),
        ]

        for filename, account_name in schwab_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                df['account_name'] = account_name
                df['account_type'] = 'Schwab'
                dfs.append(df)
                print(f"✓ Loaded {account_name}: {len(df)} rows")

        # Fidelity accounts
        fidelity_files = [
            ('Accounts_History-fidelity-Rahul.csv', 'Fidelity (Rahul)'),
            ('Accounts_History-fidelity-Rajul.csv', 'Fidelity (Rajul)'),
        ]

        for filename, account_name in fidelity_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                df = pd.read_csv(filepath)
                df['account_name'] = account_name
                df['account_type'] = 'Fidelity'
                dfs.append(df)
                print(f"✓ Loaded {account_name}: {len(df)} rows")

        # Vanguard
        vanguard_path = self.data_dir / 'Vanguard-ytd.csv'
        if vanguard_path.exists():
            try:
                # Read Vanguard with error handling
                df_vg = pd.read_csv(vanguard_path, nrows=40, on_bad_lines='skip', engine='python')
                df_vg['account_name'] = 'Vanguard'
                df_vg['account_type'] = 'Vanguard'
                dfs.append(df_vg)
                print(f"✓ Loaded Vanguard: {len(df_vg)} rows")
            except Exception as e:
                print(f"! Vanguard load: {e}")

        # Robinhood accounts
        robinhood_files = [
            ('Robinhood_Account1_20260511.csv', 'Robinhood IRA'),
            ('Robinhood_Account2_20260511.csv', 'Robinhood Taxable'),
        ]

        for filename, account_name in robinhood_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                try:
                    # Read with error handling for malformed rows
                    df = pd.read_csv(filepath, on_bad_lines='skip', engine='python')
                    # Robinhood format: lowercase column names with quotes
                    df.columns = df.columns.str.replace('"', '').str.lower().str.strip()
                    df['account_name'] = account_name
                    df['account_type'] = 'Robinhood'
                    dfs.append(df)
                    print(f"✓ Loaded {account_name}: {len(df)} rows")
                except Exception as e:
                    print(f"! {account_name} load: {e}")

        self.consolidated_df = pd.concat(dfs, ignore_index=True)
        self.consolidated_df.columns = self.consolidated_df.columns.str.strip().str.lower()

        # Handle duplicate column names by renaming them
        cols = pd.Series(self.consolidated_df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index] = ([dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))])
        self.consolidated_df.columns = cols

        print(f"\n✓ Total: {len(self.consolidated_df)} rows across 8 accounts")

    def _extract_options(self):
        """Extract option positions from all account types"""
        def extract_ticker(symbol_str):
            if pd.isna(symbol_str):
                return None
            symbol_str = str(symbol_str).strip()
            match = re.match(r'^([A-Z]{1,5})\s', symbol_str)
            return match.group(1) if match else None

        # Use the first 'symbol' column if duplicates exist
        symbol_col = [c for c in self.consolidated_df.columns if c == 'symbol' or c.startswith('symbol')][0]
        self.consolidated_df['ticker'] = self.consolidated_df[symbol_col].apply(extract_ticker)

        # Identify option transactions by account type
        option_masks = []

        # Schwab: action in ['Sell to Open', 'Buy to Close', ...]
        if 'action' in self.consolidated_df.columns:
            schwab_mask = (self.consolidated_df['account_type'] == 'Schwab') & (
                self.consolidated_df['action'].isin(['Sell to Open', 'Buy to Close', 'Sell to Close', 'Buy to Open'])
            )
            option_masks.append(schwab_mask)

        # Fidelity: action contains "SOLD OPENING" or "BOUGHT CLOSING"
        action_cols = [c for c in self.consolidated_df.columns if 'action' in c]
        for action_col in action_cols:
            fidelity_mask = (self.consolidated_df['account_type'] == 'Fidelity') & (
                self.consolidated_df[action_col].astype(str).str.contains('SOLD OPENING|BOUGHT CLOSING|SOLD CLOSING|BOUGHT OPENING', case=False, na=False)
            )
            option_masks.append(fidelity_mask)

        # Vanguard: symbol contains PUT or CALL
        symbol_cols = [c for c in self.consolidated_df.columns if c == 'symbol' or c.startswith('symbol')]
        for sym_col in symbol_cols:
            vanguard_mask = (self.consolidated_df['account_type'] == 'Vanguard') & (
                self.consolidated_df[sym_col].fillna('').astype(str).str.contains('PUT|CALL', case=False, na=False)
            )
            option_masks.append(vanguard_mask)

        # Robinhood: description contains Put or Call
        desc_cols = [c for c in self.consolidated_df.columns if 'description' in c]
        for desc_col in desc_cols:
            if self.consolidated_df[desc_col].dtype != 'object':
                continue
            robinhood_mask = (self.consolidated_df['account_type'] == 'Robinhood') & (
                self.consolidated_df[desc_col].fillna('').astype(str).str.contains('Put|Call', case=False, na=False)
            )
            option_masks.append(robinhood_mask)

        if option_masks:
            combined_mask = option_masks[0]
            for mask in option_masks[1:]:
                combined_mask = combined_mask | mask
        else:
            combined_mask = pd.Series([False] * len(self.consolidated_df))

        self.option_rows = self.consolidated_df[
            (self.consolidated_df['ticker'].notna()) & combined_mask
        ].copy()

        print(f"\n✓ Found {len(self.option_rows)} option transactions")
        print(f"✓ Unique tickers: {self.option_rows['ticker'].nunique()}")
        print(f"\nOptions by account name:")
        print(self.option_rows['account_name'].value_counts())

    def _fetch_prices(self):
        """Fetch live prices for all tickers"""
        tickers = sorted(self.option_rows['ticker'].unique().tolist())
        print(f"\n{'='*70}")
        print(f"Fetching {len(tickers)} live prices from Yahoo Finance...")
        print(f"{'='*70}")

        fetcher = YahooFinanceFetcher(batch_size=10, delay_seconds=2.0, max_retries=3)
        self.prices = fetcher.fetch_prices(tickers)

        print(f"\n✓ Fetched {len(self.prices)} prices")

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
        }).rename(columns={
            'symbol': 'transactions',
            'quantity': 'total_qty',
            'account_name': 'accounts',
        })

        summary['price'] = summary.index.map(lambda x: self.prices.get(x, 0))
        return summary.sort_values('transactions', ascending=False)

    def get_account_summary(self) -> pd.DataFrame:
        """Get position count by account"""
        if self.option_rows is None:
            return pd.DataFrame()

        return self.option_rows.groupby('account_name').size().to_frame('position_count').sort_values('position_count', ascending=False)

    def get_account_type_summary(self) -> pd.DataFrame:
        """Get position count by account type"""
        if self.option_rows is None:
            return pd.DataFrame()

        return self.option_rows.groupby('account_type').size().to_frame('position_count')


if __name__ == '__main__':
    loader = DataLoaderFinal()
    option_rows, prices = loader.load_all_data()

    print("\n" + "="*70)
    print("POSITION SUMMARY BY SYMBOL (Top 20)")
    print("="*70)
    summary = loader.get_position_summary()
    print(summary.head(20))

    print("\n" + "="*70)
    print("POSITION COUNT BY ACCOUNT")
    print("="*70)
    accounts = loader.get_account_summary()
    print(accounts)

    print("\n" + "="*70)
    print("POSITION COUNT BY ACCOUNT TYPE")
    print("="*70)
    types = loader.get_account_type_summary()
    print(types)
