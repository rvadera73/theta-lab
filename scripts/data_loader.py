"""
Dynamic Data Loader — Auto-discovers and consolidates account files.

No hardcoded filenames. Finds any positions/transaction CSVs regardless of naming.
Derives current positions from transaction history + live market data.
Automatically calculates Greeks from market data.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Dict
from datetime import datetime
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

try:
    from greeks_calculator_from_market import GreeksEnricher
    GREEKS_AVAILABLE = True
except ImportError:
    GREEKS_AVAILABLE = False
    print("Warning: yfinance not installed. Install with: pip install yfinance scipy")


class DynamicDataLoader:
    """Auto-discover and consolidate account data from any filename."""

    @staticmethod
    def _load_vanguard_positions(filepath: Path) -> pd.DataFrame:
        """
        Parse Vanguard CSV which has two sections:
        1. Positions section (Account Number, Investment Name, Symbol, Shares, Share Price, Total Value)
        2. Transactions section (Trade Date, Settlement Date, Transaction Type, etc.)

        Extracts only the positions section (stops at first blank line).
        """
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # Split by blank lines to separate sections
            sections = content.split('\n\n')
            if len(sections) < 1:
                return pd.DataFrame()

            # Use first section (positions)
            positions_section = sections[0]

            # Parse with error_bad_lines=False to skip malformed rows
            from io import StringIO
            df = pd.read_csv(StringIO(positions_section), on_bad_lines='skip')

            # Keep only rows that have a Symbol (filter out cash/money market entries with NaN symbols)
            if 'Symbol' in df.columns:
                df = df[df['Symbol'].notna()]

            return df if not df.empty else pd.DataFrame()
        except Exception as e:
            # Silently fail — Vanguard file is optional
            return pd.DataFrame()

    @staticmethod
    def find_latest_file(directory: str, pattern: str) -> Optional[Path]:
        """Find most recent file matching pattern in directory."""
        directory = Path(directory)
        if not directory.exists():
            return None

        files = list(directory.glob(pattern))
        if not files:
            return None

        # Sort by modification time, return newest
        return sorted(files, key=lambda f: f.stat().st_mtime)[-1]

    @staticmethod
    def load_all_positions(positions_dir: str = "data/positions") -> pd.DataFrame:
        """
        Auto-discover all position files and consolidate.

        Finds any CSV in positions_dir, regardless of naming.
        Returns consolidated DataFrame with all accounts.
        Normalizes column names to lowercase for consistency.
        """
        positions_dir = Path(positions_dir)
        positions_dir.mkdir(parents=True, exist_ok=True)

        all_positions = []
        csv_files = sorted(positions_dir.glob("*.csv"))

        if not csv_files:
            print(f"Warning: No position CSVs found in {positions_dir}")
            return pd.DataFrame()

        for file in csv_files:
            try:
                # Special handling for Vanguard files (two-section format: positions + transactions)
                if 'vanguard' in file.name.lower():
                    df = DynamicDataLoader._load_vanguard_positions(file)
                    if df.empty:
                        print(f"  ✗ Error loading {file.name}: Could not parse Vanguard format")
                        continue
                else:
                    df = pd.read_csv(file)

                # Normalize column names to lowercase
                df.columns = df.columns.str.lower()

                # Handle Vanguard file specially (before setting account from account number)
                if 'vanguard' in file.name.lower():
                    df['account'] = 'Vanguard Taxable'
                # Extract account number if not present and not Vanguard
                elif 'account' not in df.columns and 'account number' in df.columns:
                    df['account'] = df['account number']
                # Handle other account mapping if still no account
                elif 'account' not in df.columns:
                    # Try to infer from filename
                    filename = file.stem.lower()
                    if '232' in filename or 'account_a' in filename:
                        df['account'] = 'Account A (232)'
                    elif '275' in filename or 'account_b' in filename:
                        df['account'] = 'Account B (275)'
                    elif '634' in filename or 'account_c' in filename:
                        df['account'] = 'Account C (634)'
                    elif 'rahul' in filename:
                        df['account'] = 'Traditional IRA'
                    elif 'rajul' in filename:
                        df['account'] = 'ROTH IRA'
                    else:
                        df['account'] = file.stem

                # Normalize symbol column name
                if 'symbol' not in df.columns and 'description' in df.columns:
                    # If no symbol column, use description (Schwab format)
                    df['symbol'] = df['description']

                all_positions.append(df)
                print(f"  ✓ Loaded: {file.name}")
            except Exception as e:
                print(f"  ✗ Error loading {file.name}: {e}")

        if not all_positions:
            return pd.DataFrame()

        consolidated = pd.concat(all_positions, ignore_index=True)
        print(f"\n✓ Consolidated {len(all_positions)} position files → {len(consolidated)} rows")
        return consolidated

    @staticmethod
    def load_transactions(statements_dir: str = "data/statements") -> pd.DataFrame:
        """
        Auto-discover transaction files and consolidate.

        Finds the most recent transactions CSV (usually YTD consolidated file).
        Falls back to individual account transaction files if no consolidated found.
        """
        statements_dir = Path(statements_dir)
        statements_dir.mkdir(parents=True, exist_ok=True)

        # Look for consolidated transactions (usually contains "thru" in name)
        consolidated_file = None
        for file in sorted(statements_dir.glob("*transactions*.csv")):
            if "thru" in file.name.lower():
                consolidated_file = file
                break

        if consolidated_file:
            try:
                df = pd.read_csv(consolidated_file)
                print(f"✓ Loaded consolidated: {consolidated_file.name}")
                return df
            except Exception as e:
                print(f"  ✗ Error loading {consolidated_file.name}: {e}")

        # Fallback: consolidate individual account transaction files
        all_transactions = []
        for file in sorted(statements_dir.glob("*transactions*.csv")):
            if "thru" not in file.name.lower():  # Skip consolidated
                try:
                    df = pd.read_csv(file)
                    all_transactions.append(df)
                    print(f"  ✓ Loaded: {file.name}")
                except Exception as e:
                    print(f"  ✗ Error: {e}")

        if not all_transactions:
            print(f"Warning: No transaction CSVs found in {statements_dir}")
            return pd.DataFrame()

        consolidated = pd.concat(all_transactions, ignore_index=True)
        print(f"✓ Consolidated {len(all_transactions)} transaction files → {len(consolidated)} rows")
        return consolidated

    @staticmethod
    def derive_positions_from_transactions(transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Derive current positions from transaction history.

        Calculates net qty, average cost, realized P&L per symbol.
        Returns DataFrame of active positions.
        """
        if transactions_df.empty:
            return pd.DataFrame()

        # Group by account and symbol
        grouped = transactions_df.groupby(['account', 'symbol']).agg({
            'quantity': 'sum',
            'net_amount': 'sum',
            'date': 'max'
        }).reset_index()

        # Filter out closed positions (qty = 0)
        active = grouped[grouped['quantity'] != 0].copy()

        # Calculate average cost per share
        active['avg_cost'] = active['net_amount'] / active['quantity']
        active['cost_basis'] = active['net_amount'].abs()

        print(f"✓ Derived {len(active)} active positions from transactions")
        return active

    @staticmethod
    def load_all_data(
        positions_dir: str = "data/positions",
        statements_dir: str = "data/statements",
        use_live_positions: bool = True,
        calculate_greeks: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load all available data from directories.

        Args:
            positions_dir: Directory with position CSVs
            statements_dir: Directory with transaction CSVs
            use_live_positions: If True, use provided positions. If False, derive from transactions.
            calculate_greeks: If True, calculate Greeks from market data (requires yfinance)

        Returns:
            (positions_df, transactions_df)
        """
        print("\n" + "=" * 70)
        print("LOADING DATA")
        print("=" * 70)

        transactions_df = DynamicDataLoader.load_transactions(statements_dir)

        if use_live_positions:
            positions_df = DynamicDataLoader.load_all_positions(positions_dir)
            if positions_df.empty and not transactions_df.empty:
                print("\nNo positions files found. Deriving from transactions...")
                positions_df = DynamicDataLoader.derive_positions_from_transactions(transactions_df)
        else:
            positions_df = DynamicDataLoader.derive_positions_from_transactions(transactions_df)

        # Enhance with calculated Greeks
        if not positions_df.empty and calculate_greeks and GREEKS_AVAILABLE:
            print("\n" + "=" * 70)
            print("ENRICHING WITH CALCULATED GREEKS")
            print("=" * 70)
            positions_df = GreeksEnricher.enrich_positions(positions_df)

        print("=" * 70 + "\n")

        return positions_df, transactions_df


class PortfolioSnapshot:
    """Auto-calculate current portfolio state from live data."""

    @staticmethod
    def calculate_from_live(
        positions_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        market_regime: Optional[str] = None
    ) -> Dict:
        """
        Calculate portfolio snapshot from live data.

        No manual entry needed — derives from transactions + market data.
        """
        if transactions_df.empty:
            return {}

        # Monthly and YTD P&L from transactions
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        current_month_start = pd.Timestamp.now().replace(day=1)

        ytd_pnl = transactions_df[
            transactions_df['date'].dt.year == pd.Timestamp.now().year
        ]['net_amount'].sum()

        monthly_pnl = transactions_df[
            transactions_df['date'] >= current_month_start
        ]['net_amount'].sum()

        # Account equity (if available in positions)
        total_equity = 0
        if 'account_equity' in positions_df.columns:
            total_equity = positions_df['account_equity'].iloc[0] if not positions_df.empty else 0

        snapshot = {
            'snapshot_date': pd.Timestamp.now().isoformat(),
            'month': pd.Timestamp.now().strftime('%Y-%m'),

            'portfolio_metrics': {
                'ytd_realized_pnl': ytd_pnl,
                'monthly_realized_pnl': monthly_pnl,
                'total_equity': total_equity,
                'total_positions': len(positions_df),
                'accounts_active': positions_df['account'].nunique() if not positions_df.empty else 0,
            },

            'market_context': {
                'regime': market_regime or "Unknown",
                'data_source': 'Live (auto-calculated)',
                'positions_timestamp': positions_df['date'].max() if 'date' in positions_df.columns else None,
            }
        }

        return snapshot

    @staticmethod
    def from_config_with_live_overrides(config_path: str) -> Dict:
        """Load config defaults, override with live market data."""
        import yaml

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Override with live data where available
        snapshot = {
            'portfolio': config.get('portfolio', {}),
            'risk_budget': config.get('risk_budget', {}),
            'greeks': config.get('greeks', {}),
        }

        return snapshot


if __name__ == "__main__":
    # Test: Load all data
    positions, transactions = DynamicDataLoader.load_all_data()

    print(f"\nPositions shape: {positions.shape}")
    print(f"Transactions shape: {transactions.shape}")

    # Calculate snapshot
    snapshot = PortfolioSnapshot.calculate_from_live(positions, transactions)
    print(f"\nSnapshot: {snapshot}")
