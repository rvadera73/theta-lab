"""
Open Positions Loader V2 — Calculate Net Open Positions from All 8 Accounts
Properly extracts tickers from all broker formats (Schwab, Fidelity, Vanguard, Robinhood)
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import date
import sys
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
from yahoo_price_fetcher import YahooFinanceFetcher


class OpenPositionsLoaderV2:
    """Load all 8 accounts and calculate OPEN positions only with proper multi-broker support"""

    def __init__(self, data_dir: str = '/home/rahulvadera/projects/theta-lab/data/positions'):
        self.data_dir = Path(data_dir)
        self.consolidated_df = None
        self.open_positions = None
        self.prices = {}
        self.equity_positions = {}
        self.option_requirements = {}

    def _calculate_option_requirements(self, equity_positions: Dict[str, Dict[str, int]]) -> Dict[str, float]:
        """Calculate total option requirement per account.

        Two different formulas based on account type:
        - Margin accounts: 18% of total notional exposure
        - Cash accounts: Actual cash collateral needed per position
          * Short puts: strike × contracts × 100
          * Short calls (naked): current_price × contracts × 100
          * Short calls (covered by shares): $0

        Returns Dict[account_name, total_requirement]
        """
        requirements = defaultdict(float)
        notional_by_account = defaultdict(float)

        if self.open_positions is None or len(self.open_positions) == 0:
            return dict(requirements)

        # Define margin vs cash accounts
        margin_accounts = {'Account A (232)'}  # Only Account A is margin
        # All other accounts are cash/secured accounts

        for _, row in self.open_positions.iterrows():
            account = row['account_name']
            ticker = row['ticker']
            opt_type = row.get('option_type')
            strike = row.get('strike')
            contracts = row['net_quantity']
            current_price = self.prices.get(ticker, 0)

            if account in margin_accounts:
                # For margin accounts: accumulate notional for 18% calculation
                notional = current_price * contracts * 100
                notional_by_account[account] += notional

            else:  # All other accounts are cash/secured accounts
                # For cash accounts: calculate actual collateral needed
                if opt_type == 'P':
                    # Short put: strike × contracts × 100
                    if strike is not None:
                        requirements[account] += strike * contracts * 100
                elif opt_type == 'C':
                    # Short call: check if covered by owned shares
                    shares_owned = equity_positions.get(account, {}).get(ticker, 0)
                    covered_contracts = min(contracts, shares_owned // 100)
                    naked_contracts = contracts - covered_contracts
                    # Naked calls: current_price × contracts × 100
                    requirements[account] += naked_contracts * current_price * 100

        # For margin accounts: apply 18% of notional
        for account, notional in notional_by_account.items():
            requirements[account] = notional * 0.18

        return dict(requirements)

    def load_all_data(self) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Load all account data and fetch live prices"""
        self._load_accounts()
        self._calculate_open_positions()
        # Try to load equity positions from YAML file; fall back to transaction history
        self.equity_positions = self._load_equity_positions_from_yaml()
        if not self.equity_positions:
            self.equity_positions = self._track_equity_positions()
        self._fetch_prices()
        self.option_requirements = self._calculate_option_requirements(self.equity_positions)
        return self.open_positions, self.prices

    def _load_equity_positions_from_yaml(self) -> Dict[str, Dict[str, int]]:
        """Load equity positions from portfolio_equity_positions.yaml file"""
        try:
            import yaml
            yaml_path = self.data_dir / 'portfolio_equity_positions.yaml'
            if yaml_path.exists():
                with open(yaml_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'accounts' in data:
                        # Convert to Dict[account_name, Dict[ticker, shares]]
                        result = {}
                        for account_name, tickers in data['accounts'].items():
                            result[account_name] = {}
                            for ticker, position_data in tickers.items():
                                result[account_name][ticker] = position_data.get('shares', 0)
                        print(f"✓ Loaded equity positions from portfolio_equity_positions.yaml")
                        return result
        except Exception as e:
            print(f"! Could not load YAML: {e}")
        return {}

    def _load_accounts(self):
        """Load all 8 account files"""
        dfs = []

        # Try to load Schwab position files first (more accurate), fall back to transaction files
        import glob
        # Canonical filenames per data/account_files.yaml contract
        schwab_account_patterns = [
            (['schwab_rahul_individual.csv'], 'Account A (232)'),
            (['schwab_pinky_ira.csv'], 'Account B (275)'),
            (['schwab_designated-bene.csv'], 'Account C (634)'),
        ]

        for patterns, account_name in schwab_account_patterns:
            # Try each pattern in order
            if isinstance(patterns, str):
                patterns = [patterns]

            file_path = None
            for pattern in patterns:
                matches = sorted(glob.glob(str(self.data_dir / pattern)))
                if matches:
                    file_path = matches[-1]
                    break

            if file_path:
                try:
                    # Canonical Schwab files are always position snapshots
                    is_position_file = True

                    if is_position_file:
                        # Load position file (skip first 2 rows of metadata)
                        df = pd.read_csv(file_path, skiprows=2)
                        # Rename Symbol to symbol for consistency
                        if 'Symbol' in df.columns:
                            df['symbol'] = df['Symbol']
                        # Rename Qty column for consistency
                        if 'Qty (Quantity)' in df.columns:
                            df['quantity'] = df['Qty (Quantity)']
                        df['account_name'] = account_name
                        df['account_type'] = 'Schwab'
                        df['source'] = 'position_file'
                    else:
                        # Load transaction file
                        df = pd.read_csv(file_path)
                        df['account_name'] = account_name
                        df['account_type'] = 'Schwab'
                        df['source'] = 'transaction_file'

                    dfs.append(df)
                    source_type = 'position file' if is_position_file else 'transaction file'
                    print(f"✓ Loaded {account_name}: {len(df)} rows from {source_type}")
                except Exception as e:
                    print(f"! Error loading {account_name}: {e}")

        # Fidelity accounts - try position files first, fall back to transaction files
        # Canonical filenames per contract. Both files hold MULTIPLE accounts; the account
        # TYPE lives in the account-number column (name/case has shifted across exports —
        # seen as both 'Account Number' and 'Account number' — so it's matched case-insensitively).
        fidelity_account_patterns = [
            (['fidelity_rahul.csv'], None, {  # Rahul file: Traditional IRA (options wheel) + 401K
                'Traditional IRA': 'Fidelity (Rahul)',
                'PRECISE SOFTWARE SOL': 'Fidelity 401K (Rahul)',
            }, ['ROTH IRA for Minor']),  # negligible custodial account — dropped, not tracked
            (['fidelity_rajul.csv'], None, {  # Map by account-number column value
                'ROTH IRA': 'Fidelity (Rajul — Roth IRA)',
                'Rollover IRA': 'Fidelity (Rajul — Rollover IRA)',
                'ROTH IRA for Minor': 'Fidelity (Rajul — Roth IRA)',
            }, []),
        ]

        for patterns, default_account_name, account_map, drop_values in fidelity_account_patterns:
            # Try each pattern in order
            if isinstance(patterns, str):
                patterns = [patterns]

            file_path = None
            for pattern in patterns:
                matches = sorted(glob.glob(str(self.data_dir / pattern)))
                if matches:
                    file_path = matches[-1]
                    break

            if file_path:
                try:
                    is_position_file = True  # canonical Fidelity files are position snapshots

                    # Fidelity position files: row 0=header, row 1=disclaimer, data starts row 2
                    # Skip 1 row (the disclaimer) to keep header as first row
                    # Use index_col=False to prevent Account Number from being treated as index
                    # Fidelity position files have header in row 0, data starts row 1
                    # No disclaimer rows or metadata - just read normally
                    df = pd.read_csv(file_path, encoding='utf-8-sig', on_bad_lines='skip')

                    # Map column names for consistency
                    # Fidelity position files have misaligned columns - data is shifted left
                    # Symbol column has descriptions like "HOOD MAR 19 2027 $65 PUT"
                    # Description column actually contains quantities like "-1.0"
                    if is_position_file:
                        # Symbol already has what we need (descriptions)
                        df['symbol'] = df['Symbol']
                        # Description column has quantities for position files
                        if 'Description' in df.columns:
                            df['quantity'] = df['Description']
                    else:
                        # Transaction files
                        if 'Symbol' in df.columns:
                            df['symbol'] = df['Symbol']
                        if 'Quantity' in df.columns:
                            df['quantity'] = df['Quantity']

                    if 'Type' in df.columns:
                        df['type'] = df['Type']

                    # If we have a mapping, use Account column to assign account names
                    if account_map:
                        # Fidelity column shift: the account TYPE is in the account-number
                        # column ('ROTH IRA' / 'Rollover IRA' / etc), not 'Account Name'.
                        # Column name casing has changed across exports ('Account Number'
                        # vs 'Account number') so match it case-insensitively.
                        acct_num_col = next(
                            (c for c in df.columns if str(c).strip().lower() == 'account number'),
                            None
                        )
                        if acct_num_col:
                            if drop_values:
                                df = df[~df[acct_num_col].isin(drop_values)].copy()
                            df['account_name'] = df[acct_num_col].map(account_map)
                            # Rows below the holdings block (totals/disclaimer) have no type
                            df['account_name'] = df['account_name'].ffill()
                            df['account_name'] = df['account_name'].fillna(list(account_map.values())[0])
                        else:
                            # Transaction file - use default account name
                            df['account_name'] = default_account_name
                    else:
                        # Use the provided default account name for all rows
                        df['account_name'] = default_account_name

                    df['account_type'] = 'Fidelity'
                    df['source'] = 'position_file' if is_position_file else 'transaction_file'
                    dfs.append(df)

                    # Count by account name for logging
                    source_type = 'position file' if is_position_file else 'transaction file'
                    if account_map:
                        for acct_name, count in df['account_name'].value_counts().items():
                            print(f"✓ Loaded {acct_name}: {count} rows from {source_type}")
                    else:
                        print(f"✓ Loaded {default_account_name}: {len(df)} rows from {source_type}")
                except Exception as e:
                    print(f"! Fidelity load failed: {e}")

        # Vanguard - use glob pattern to find files
        vanguard_patterns = [
            ('vanguard_rahul.csv', 'Vanguard (Rahul)'),
        ]

        for pattern, account_name in vanguard_patterns:
            matches = sorted(glob.glob(str(self.data_dir / pattern)))
            if matches:
                filepath = matches[-1]  # Use latest file
                try:
                    df = pd.read_csv(filepath, on_bad_lines='skip', engine='python')
                    df['account_name'] = account_name
                    df['account_type'] = 'Vanguard'
                    dfs.append(df)
                    print(f"✓ Loaded {account_name}: {len(df)} rows from {Path(filepath).name}")
                except Exception as e:
                    print(f"! {account_name} load failed: {e}")

        # Robinhood accounts - use glob pattern to pick latest file
        # Supports both old naming (Robinhood_Account*.csv) and new naming (hood-*.csv)
        robinhood_patterns = [
            (['robinhood_rahul_traditional.csv'], 'Robinhood (Traditional IRA)'),
            (['robinhood_rahul_individual.csv'], 'Robinhood (Individual)'),
        ]

        for patterns, account_name in robinhood_patterns:
            # Try each pattern until one matches
            if isinstance(patterns, str):
                patterns = [patterns]

            matches = []
            for pattern in patterns:
                matches.extend(sorted(glob.glob(str(self.data_dir / pattern))))

            if matches:
                filepath = matches[-1]  # Use latest file
                try:
                    df = pd.read_csv(filepath, on_bad_lines='skip', engine='python')
                    df.columns = df.columns.str.replace('"', '').str.lower().str.strip()

                    # Filter out Robinhood cancellation/adjustment rows (OCA with invalid quantities)
                    initial_count = len(df)
                    df = df[~df['trans code'].isin(['OCA'])]  # Remove cancellations
                    # Also remove rows where Quantity contains non-numeric values
                    df = df[df['quantity'].astype(str).str.strip().str.replace('.', '').str.isdigit()]
                    filtered_count = initial_count - len(df)

                    df['account_name'] = account_name
                    df['account_type'] = 'Robinhood'
                    dfs.append(df)
                    msg = f"✓ Loaded {account_name}: {len(df)} rows"
                    if filtered_count > 0:
                        msg += f" (filtered {filtered_count} invalid rows)"
                    msg += f" from {Path(filepath).name}"
                    print(msg)
                except Exception as e:
                    print(f"! {account_name} load: {e}")

        self.consolidated_df = pd.concat(dfs, ignore_index=True)
        self.consolidated_df.columns = self.consolidated_df.columns.str.strip().str.lower()

        # Handle duplicate column names
        cols = pd.Series(self.consolidated_df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index] = ([dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))])
        self.consolidated_df.columns = cols

        print(f"\n✓ Total: {len(self.consolidated_df)} rows across 8 accounts")

    def _extract_ticker(self, row) -> Optional[str]:
        """
        Extract ticker symbol from a row, handling all broker formats.
        """
        account_type = row.get('account_type', '')

        # Fidelity: Try to extract from symbol column first (format: "TICKER MONTH DAY YEAR $STRIKE PUT/CALL")
        if account_type == 'Fidelity':
            symbol = str(row.get('symbol', '')).strip()
            # Pattern: "HOOD MAR 19 2027 $65 PUT" -> extract HOOD
            match = re.match(r'^([A-Z]{1,5})\s+', symbol)
            if match:
                return match.group(1)
            return None

        # Vanguard: Symbol column has "ABNB 270319 C 140.00" format
        if account_type == 'Vanguard':
            symbol = str(row.get('symbol', '')).strip()
            # Extract first word (ticker)
            match = re.match(r'^([A-Z]{1,5})\s', symbol)
            if match:
                return match.group(1)
            return None

        # Robinhood: Use instrument column which has the ticker directly
        if account_type == 'Robinhood':
            # Try to find instrument column (may exist in consolidated df)
            instrument = str(row.get('instrument', '')).strip()
            if instrument and instrument != 'nan':
                # Robinhood instrument column is just the ticker (e.g., "CMG", "SHOP")
                match = re.match(r'^([A-Z]{1,5})$', instrument)
                if match:
                    return match.group(1)

            # Fallback: extract from description "TICKER DATE Put/Call $STRIKE"
            description = str(row.get('description_1', row.get('description', ''))).strip()
            match = re.match(r'^([A-Z]{1,5})\s+\d+/\d+/\d+\s+(Put|Call)', description, re.IGNORECASE)
            if match:
                return match.group(1)

            return None

        # Schwab: Symbol column with format "IONQ 270319P35" or similar
        symbol = str(row.get('symbol', '')).strip()

        # Handle Fidelity-style symbols that start with "-"
        if symbol.startswith('-'):
            symbol = symbol[1:].strip()

        # Extract first 1-5 uppercase letters followed by space or number
        match = re.match(r'^([A-Z]{1,5})[\s\d]', symbol)
        if match:
            return match.group(1)

        return None

    def _parse_expiry_date(self, symbol_str: str) -> Optional['date']:
        """Extract expiry date from symbol string (format: TICKER MM/DD/YYYY STRIKE P/C)"""
        try:
            parts = str(symbol_str).split()
            if len(parts) >= 2:
                date_str = parts[1]
                if '/' in date_str:
                    month, day, year = date_str.split('/')
                    from datetime import date
                    return date(int(year), int(month), int(day))
        except:
            pass
        return None

    def _parse_option_symbol(self, row) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """Extract (strike, option_type) from symbol, handling all broker formats.
        Returns (strike_price, option_type) where option_type is 'P' or 'C', or (None, None) for equity rows."""
        account_type = row.get('account_type', '')
        # For Fidelity position files, use fidelity_posfile_symbol if available
        if account_type == 'Fidelity' and row.get('fidelity_posfile_symbol'):
            symbol = str(row.get('fidelity_posfile_symbol', '')).strip()
        else:
            symbol = str(row.get('symbol', '')).strip()
        description = str(row.get('description', '')).strip()

        # Schwab: "NFLX 05/16/2027 175.00 P"
        if account_type == 'Schwab':
            match = re.match(r'^[A-Z]+\s+\d{2}/\d{2}/\d{4}\s+([\d.]+)\s+([PC])$', symbol)
            if match:
                return (float(match.group(1)), match.group(2))

        # Fidelity: Format "TICKER MONTH DAY YEAR $STRIKE PUT/CALL" from position files
        # Example: "HOOD MAR 19 2027 $65 PUT"
        if account_type == 'Fidelity':
            # Extract strike and option type from the format
            match = re.search(r'\$([0-9.]+)\s+(PUT|CALL)$', symbol)
            if match:
                strike = float(match.group(1))
                opt_type = 'P' if match.group(2) == 'PUT' else 'C'
                return (strike, opt_type)

        # Vanguard: "COIN 260918 P 230.00" or just "CRM" (equity)
        if account_type == 'Vanguard':
            match = re.match(r'^[A-Z]+\s+\d{6}\s+([CP])\s+([\d.]+)$', symbol)
            if match:
                return (float(match.group(2)), match.group(1))

        # Robinhood: description "CMG 6/17/2027 Put $30.00" (equity has just ticker in instrument)
        if account_type == 'Robinhood':
            match = re.search(r'\s+(Put|Call)\s+\$([\d.]+)', description)
            if match:
                opt_type = 'P' if match.group(1) == 'Put' else 'C'
                return (float(match.group(2)), opt_type)

        return (None, None)

    def _track_equity_positions(self) -> Dict[str, Dict[str, int]]:
        """Track net equity shares owned per account per ticker from all transactions.
        Returns Dict[account_name, Dict[ticker, net_shares]]"""
        equity_positions = defaultdict(lambda: defaultdict(int))

        if self.consolidated_df is None or len(self.consolidated_df) == 0:
            return dict(equity_positions)

        for _, row in self.consolidated_df.iterrows():
            account = row.get('account_name', '')
            account_type = row.get('account_type', '')
            ticker = row.get('ticker')

            if not ticker or not account:
                continue

            # Get quantity from the right column
            qty = None
            if account_type == 'Robinhood':
                for col in ['quantity_1', 'quantity', 'shares']:
                    if col in row.index and pd.notna(row.get(col)):
                        qty = float(row.get(col))
                        break
            elif account_type == 'Vanguard':
                # Vanguard is positions snapshot - read Shares column directly for equity
                for col in ['shares', 'quantity_1', 'quantity']:
                    if col in row.index and pd.notna(row.get(col)):
                        shares_val = row.get(col)
                        # Skip if it's an option (negative shares)
                        if float(shares_val) > 0:
                            qty = float(shares_val)
                            break
            else:  # Schwab, Fidelity
                for col in ['quantity', 'shares', 'quantity_1']:
                    if col in row.index and pd.notna(row.get(col)):
                        qty = float(row.get(col))
                        break

            if qty is None:
                continue

            # Determine action to classify as equity (not option)
            action = str(row.get('action', '')).upper()
            trans_code = str(row.get('trans code', '')).upper() if 'trans code' in row.index else ''

            is_equity = False

            # Schwab: Handle direct Buy/Sell AND Assigned transactions
            if account_type == 'Schwab':
                if 'BUY TO OPEN' in action or 'BUY TO CLOSE' in action:
                    # Buy to open/close typically for equity
                    is_equity = True
                elif 'SELL TO OPEN' in action or 'SELL TO CLOSE' in action:
                    # Sell to close for equity (negative qty)
                    is_equity = True
                    qty = -abs(qty)
                elif action == 'ASSIGNED':
                    # Assignment: parse symbol to determine Put vs Call
                    symbol = str(row.get('symbol', '')).upper()
                    # Extract strike and option type
                    strike, opt_type = None, None
                    import re
                    # Schwab format: "TICKER MM/DD/YYYY STRIKE.00 P/C"
                    match = re.search(r'([A-Z]+)\s+\d{2}/\d{2}/\d{4}\s+[\d.]+\s+([PC])', symbol)
                    if match:
                        opt_type = match.group(2)
                        if opt_type == 'P':
                            # Put assignment: we RECEIVE shares (positive)
                            is_equity = True
                            qty = abs(qty)
                        elif opt_type == 'C':
                            # Call assignment: we GIVE UP shares (negative)
                            is_equity = True
                            qty = -abs(qty)

            # Fidelity equity keywords (assigned puts/calls create equity positions)
            if account_type == 'Fidelity' and ('ASSIGNED' in action and ('PUT' in action or 'CALL' in action)):
                if 'BOUGHT ASSIGNED PUTS' in action:
                    is_equity = True
                    qty = abs(qty)  # Ensure positive for long shares
                elif 'SOLD ASSIGNED CALLS' in action:
                    is_equity = True
                    qty = -abs(qty)  # Negative for shares sold/disposed

            # Vanguard: positive Shares = equity (already filtered above)
            if account_type == 'Vanguard' and qty > 0:
                is_equity = True

            # Robinhood equity keywords
            if account_type == 'Robinhood' and trans_code in ['BUY', 'SELL']:
                is_equity = True
                if trans_code == 'SELL':
                    qty = -qty  # Negative for sells

            if is_equity:
                equity_positions[account][ticker] += int(qty)

        return dict(equity_positions)

    def _calculate_open_positions(self):
        """Calculate net open positions by excluding closed-out positions and expired contracts"""
        from datetime import date

        # For Schwab position files, keep only option rows (they show open positions directly)
        if 'asset type' in self.consolidated_df.columns:
            # Filter out equity rows from position files (tracked separately)
            # and keep position files' option rows as-is
            position_file_equity_mask = (
                (self.consolidated_df['source'] == 'position_file') if 'source' in self.consolidated_df.columns
                else False
            ) & (self.consolidated_df['asset type'] == 'Equity')

            self.consolidated_df = self.consolidated_df[~position_file_equity_mask].copy()

            # Mark position file options as already having opening transactions (no netting)
            pf_option_mask = (
                (self.consolidated_df['source'] == 'position_file') if 'source' in self.consolidated_df.columns
                else False
            ) & (self.consolidated_df['asset type'] == 'Option')
            self.consolidated_df.loc[pf_option_mask, 'has_opening'] = True

        # Extract ticker for all rows
        self.consolidated_df['ticker'] = self.consolidated_df.apply(self._extract_ticker, axis=1)

        # Extract expiry date for all rows (for filtering expired positions)
        self.consolidated_df['expiry_date'] = self.consolidated_df['symbol'].apply(self._parse_expiry_date)

        # Identify option transactions
        option_masks = []

        # Schwab position files: asset type == 'Option'
        if 'asset type' in self.consolidated_df.columns:
            schwab_posfile_mask = (self.consolidated_df['account_type'] == 'Schwab') & (
                self.consolidated_df['asset type'] == 'Option'
            )
            option_masks.append(schwab_posfile_mask)

        # Fidelity position files: Detect by "PUT" or "CALL" in symbol column
        # Format: "TICKER MONTH DAY YEAR $STRIKE PUT/CALL" (e.g., "HOOD MAR 19 2027 $65 PUT")
        fidelity_posfile_mask = (self.consolidated_df['account_type'] == 'Fidelity') & (
            self.consolidated_df['source'].fillna('').astype(str) == 'position_file'
        ) & (
            self.consolidated_df['symbol'].fillna('').astype(str).str.contains('PUT|CALL', case=False, na=False)
        )
        option_masks.append(fidelity_posfile_mask)

        # Schwab: action in ['Sell to Open', 'Buy to Close', ...]
        if 'action' in self.consolidated_df.columns:
            schwab_mask = (self.consolidated_df['account_type'] == 'Schwab') & (
                self.consolidated_df['action'].isin(['Sell to Open', 'Buy to Close', 'Sell to Close', 'Buy to Open'])
            )
            option_masks.append(schwab_mask)

        # Fidelity: action contains option keywords
        action_cols = [c for c in self.consolidated_df.columns if 'action' in c]
        for action_col in action_cols:
            fidelity_mask = (self.consolidated_df['account_type'] == 'Fidelity') & (
                self.consolidated_df[action_col].astype(str).str.contains('SOLD OPENING|BOUGHT CLOSING|SOLD CLOSING|BOUGHT OPENING', case=False, na=False)
            )
            option_masks.append(fidelity_mask)

        # Vanguard: Check for C or P in symbol column (format: "ABNB 270319 C 140.00")
        symbol_cols = [c for c in self.consolidated_df.columns if c == 'symbol' or c.startswith('symbol')]
        for sym_col in symbol_cols:
            # Vanguard options have format with space-separated C or P: "TICKER DATE C/P STRIKE"
            vanguard_mask = (self.consolidated_df['account_type'] == 'Vanguard') & (
                self.consolidated_df[sym_col].fillna('').astype(str).str.contains(r'\s[CP]\s', regex=True, na=False) |
                self.consolidated_df[sym_col].fillna('').astype(str).str.contains('PUT|CALL', case=False, na=False)
            )
            option_masks.append(vanguard_mask)

        # Robinhood: Check description for "DATE Put/Call STRIKE" pattern
        # Note: After consolidation, Robinhood description may be in description_1 or description_N
        desc_cols = [c for c in self.consolidated_df.columns if 'description' in c.lower()]
        for desc_col in desc_cols:
            if desc_col not in self.consolidated_df.columns:
                continue
            # Check for both 'object' (pandas <2.0) and 'str' (pandas 2.0+) dtypes
            dtype = self.consolidated_df[desc_col].dtype
            if str(dtype) not in ['object', 'string', 'str']:
                continue
            robinhood_mask = (self.consolidated_df['account_type'] == 'Robinhood') & (
                self.consolidated_df[desc_col].fillna('').astype(str).str.contains(r'\d+/\d+/\d+\s+(Put|Call)', regex=True, case=False, na=False)
            )
            option_masks.append(robinhood_mask)

        if option_masks:
            combined_mask = option_masks[0]
            for mask in option_masks[1:]:
                combined_mask = combined_mask | mask
        else:
            combined_mask = pd.Series([False] * len(self.consolidated_df))

        # Filter out expired positions
        from datetime import date
        today = date.today()
        not_expired_mask = self.consolidated_df['expiry_date'].apply(
            lambda x: x is None or x >= today
        )

        all_options = self.consolidated_df[
            (self.consolidated_df['ticker'].notna()) & combined_mask & not_expired_mask
        ].copy()

        print(f"\n✓ Found {len(all_options)} total option transactions")
        print(f"✓ Options by account type:")
        for acct_type, count in all_options['account_type'].value_counts().items():
            print(f"    {acct_type}: {count}")

        # Calculate net quantity per position
        # Group by: account, ticker, and contract identifier
        # Use 'symbol' for most brokers, but for Robinhood use 'instrument' or description
        def _contract_id(row):
            # Robinhood (transactions): the full description IS the contract
            # ("RKT 3/19/2027 Put $15.00") — use it so different strikes/expiries
            # don't collapse onto the bare ticker.
            if row.get('account_type') == 'Robinhood':
                for c in ('description_1', 'description'):
                    v = row.get(c)
                    if pd.notna(v) and str(v).strip():
                        return str(v).strip()
            if pd.notna(row.get('symbol')):
                return row['symbol']
            if pd.notna(row.get('instrument')):
                return row.get('instrument')
            return row.get('description_1', row.get('description', 'unknown'))

        all_options['contract_id'] = all_options.apply(_contract_id, axis=1)

        position_groups = all_options.groupby(['account_name', 'ticker', 'contract_id'])

        open_positions_list = []
        orphaned_closes = []  # net_qty != 0 but no opening leg in this file — likely a partial/YTD export
        for (account, ticker, symbol), group in position_groups:
            # Calculate net quantity
            net_qty = 0
            account_type = group['account_type'].iloc[0]
            has_opening = False  # Track if this group has any opening transactions

            for _, row in group.iterrows():
                # Get quantity from the right column based on account type
                qty = None

                # Try type-specific columns first
                if account_type == 'Robinhood':
                    qty_col_candidates = ['quantity_1', 'quantity', 'shares']
                elif account_type == 'Vanguard':
                    qty_col_candidates = ['shares', 'quantity', 'quantity_1']
                elif account_type == 'Fidelity':
                    qty_col_candidates = ['quantity', 'quantity_1', 'shares']
                else:  # Schwab
                    qty_col_candidates = ['quantity', 'shares', 'quantity_1']

                for qty_col in qty_col_candidates:
                    if qty_col in row.index:
                        qty = row.get(qty_col)
                        if pd.notna(qty):
                            break

                if qty is None:
                    qty = 0
                else:
                    qty = float(qty)

                # Get action information - look for any action-like column
                action = ''
                action_col = None
                for col in group.columns:
                    cl = str(col).lower().strip()
                    # Robinhood uses 'Trans Code' (STO/BTC/BTO/STC), not an 'action' column
                    if 'action' in cl or cl in ('trans code', 'trans_code', 'transcode', 'code'):
                        action_col = col
                        break

                if action_col and pd.notna(row.get(action_col)):
                    action = str(row.get(action_col, '')).upper()

                # Check if this is an opening transaction
                # Position files show open positions directly, so mark them as having opening
                source = row.get('source') if 'source' in row.index else ''
                if source == 'position_file':
                    has_opening = True
                elif 'SELL' in action or 'OPEN' in action or 'STO' in action or 'BTO' in action or 'SOLD' in action or 'BOUGHT OPENING' in action or 'SOLD OPENING' in action:
                    has_opening = True

                # Logic: Sells/Opens = positive, Buys/Closes = negative
                if 'SELL' in action or 'STC' in action or 'STO' in action or 'SOLD' in action:
                    net_qty += qty
                elif 'BUY' in action or 'BTC' in action or 'BTO' in action or 'BOUGHT' in action:
                    net_qty -= qty
                elif qty < 0:  # For accounts without action info, negative qty = short
                    net_qty -= qty
                else:
                    net_qty += qty

            # Only include if:
            # 1. Net quantity is non-zero (position is open)
            # 2. Has at least one opening transaction (not just orphaned closes)
            if net_qty != 0 and not has_opening:
                # A close-side-only balance with no opening leg in this file means the
                # export's date range doesn't cover this position's open — classic
                # symptom of a YTD/partial export (see prefer_full_over_ytd in
                # data/account_files.yaml). Previously this was dropped with zero
                # signal; now it's surfaced so a bad Robinhood/Fidelity export doesn't
                # silently produce an incomplete report.
                orphaned_closes.append({
                    'account_name': account, 'ticker': ticker, 'contract_id': symbol,
                    'account_type': account_type, 'net_quantity': abs(net_qty),
                    'transaction_count': len(group),
                })
                continue
            if net_qty != 0 and has_opening:
                # Parse strike and option type from any row in the group
                first_row = group.iloc[0]
                strike, opt_type = self._parse_option_symbol(first_row)

                position = {
                    'account_name': account,
                    'ticker': ticker,
                    'symbol': symbol,  # symbol here is actually contract_id from groupby
                    'net_quantity': abs(net_qty),
                    'account_type': group['account_type'].iloc[0],
                    'transaction_count': len(group),
                    'strike': strike,
                    'option_type': opt_type
                }
                open_positions_list.append(position)

        self.open_positions = pd.DataFrame(open_positions_list)
        print(f"\n✓ Calculated {len(self.open_positions)} OPEN positions (closed-out positions excluded)")
        if len(self.open_positions) > 0:
            print(f"✓ Unique tickers in open positions: {self.open_positions['ticker'].nunique()}")
            print(f"✓ Open positions by account type:")
            for acct_type, count in self.open_positions['account_type'].value_counts().items():
                print(f"    {acct_type}: {count}")

        if orphaned_closes:
            by_type = defaultdict(int)
            for oc in orphaned_closes:
                by_type[oc['account_type']] += 1
            print(f"\n⚠️  {len(orphaned_closes)} position(s) EXCLUDED — close-side activity with no "
                  f"opening leg in the file(s) provided (likely a partial/YTD export, not a full "
                  f"transaction history — see 'prefer_full_over_ytd' in data/account_files.yaml):")
            for acct_type, count in by_type.items():
                print(f"    {acct_type}: {count} — re-export a FULL history file for this account")
            for oc in orphaned_closes[:10]:
                print(f"      {oc['account_name']} / {oc['ticker']} / {oc['contract_id']} "
                      f"(net qty {oc['net_quantity']}, {oc['transaction_count']} txns in file)")
            if len(orphaned_closes) > 10:
                print(f"      ... and {len(orphaned_closes) - 10} more")

    def _fetch_prices(self):
        """Fetch live prices for all tickers in open positions"""
        if self.open_positions is None or len(self.open_positions) == 0:
            print("✓ No open positions to fetch prices for")
            return

        tickers = sorted(self.open_positions['ticker'].unique().tolist())
        print(f"\n{'='*70}")
        print(f"Fetching {len(tickers)} live prices from Yahoo Finance...")
        print(f"{'='*70}")

        fetcher = YahooFinanceFetcher(batch_size=10, delay_seconds=2.0, max_retries=3)
        self.prices = fetcher.fetch_prices(tickers)

        print(f"\n✓ Fetched {len(self.prices)} prices")

    def get_position_summary(self) -> pd.DataFrame:
        """Get summary of open positions by ticker"""
        if self.open_positions is None:
            return pd.DataFrame()

        summary = self.open_positions.groupby('ticker').agg({
            'net_quantity': 'sum',
            'account_name': 'count',
            'transaction_count': 'sum'
        }).rename(columns={
            'net_quantity': 'total_open_contracts',
            'account_name': 'accounts_with_position',
            'transaction_count': 'total_transactions'
        })

        summary['price'] = summary.index.map(lambda x: self.prices.get(x, 0))
        return summary.sort_values('total_open_contracts', ascending=False)

    def get_account_summary(self) -> pd.DataFrame:
        """Get open position count by account.

        Includes EVERY loaded account (all 9), even equity-only accounts like
        Vanguard that have 0 open options — so the report covers the full book.
        """
        if self.open_positions is None:
            return pd.DataFrame()

        counts = self.open_positions.groupby('account_name').size()
        # Reindex over all accounts seen in the raw data so option-less accounts appear
        if self.consolidated_df is not None and 'account_name' in self.consolidated_df.columns:
            all_accounts = self.consolidated_df['account_name'].dropna().unique()
            counts = counts.reindex(all_accounts, fill_value=0)
        return counts.to_frame('open_positions').sort_values('open_positions', ascending=False)

    def get_account_type_summary(self) -> pd.DataFrame:
        """Get open position count by account type"""
        if self.open_positions is None:
            return pd.DataFrame()

        return self.open_positions.groupby('account_type').size().to_frame('open_positions')

    def get_equity_summary(self) -> Dict[str, Dict[str, int]]:
        """Returns net shares owned per account per ticker"""
        return self.equity_positions

    def get_option_requirements(self) -> Dict[str, float]:
        """Returns total option requirement per account"""
        return self.option_requirements

    def get_position_pnl_summary(self) -> Dict[str, Dict[str, float]]:
        """Calculate P&L for each open position aggregated from transactions

        Returns: Dict[ticker, {'pnl': $, 'pnl_pct': %, 'cost_basis': $, 'current_value': $}]
        """
        pnl_by_ticker = {}

        if self.consolidated_df is None or len(self.consolidated_df) == 0:
            return pnl_by_ticker

        def parse_currency(val):
            """Parse currency string to float"""
            if val is None or pd.isna(val):
                return 0.0
            try:
                if isinstance(val, str):
                    # Remove $, commas, and whitespace
                    val = val.replace('$', '').replace(',', '').strip()
                    return float(val)
                else:
                    return float(val)
            except (ValueError, TypeError):
                return 0.0

        # Group by ticker and aggregate P&L
        for ticker, group in self.consolidated_df.groupby('ticker', dropna=True):
            # Get gain/loss columns (try different naming conventions)
            gain_col = None
            for col in ['gain $ (gain/loss $)', 'total gain/loss dollar', "today's gain/loss dollar"]:
                if col in group.columns and group[col].notna().any():
                    gain_col = col
                    break

            gain_pct_col = None
            for col in ['gain % (gain/loss %)', 'total gain/loss percent', "today's gain/loss percent"]:
                if col in group.columns and group[col].notna().any():
                    gain_pct_col = col
                    break

            # Aggregate P&L values
            total_pnl = 0.0
            total_cost_basis = 0.0
            total_current_value = 0.0

            for idx, row in group.iterrows():
                if gain_col and pd.notna(row.get(gain_col)):
                    total_pnl += parse_currency(row[gain_col])

                if 'cost basis' in row and pd.notna(row.get('cost basis')):
                    total_cost_basis += parse_currency(row['cost basis'])

                if 'mkt val (market value)' in row and pd.notna(row.get('mkt val (market value)')):
                    total_current_value += parse_currency(row['mkt val (market value)'])

            # Calculate percentage
            pnl_pct = (total_pnl / total_cost_basis) if total_cost_basis > 0 else 0.0

            pnl_by_ticker[ticker] = {
                'pnl': total_pnl,
                'pnl_pct': pnl_pct,  # Keep as decimal
                'cost_basis': total_cost_basis,
                'current_value': total_current_value
            }

        return pnl_by_ticker


if __name__ == '__main__':
    loader = OpenPositionsLoaderV2()
    open_pos, prices = loader.load_all_data()

    print("\n" + "="*70)
    print("OPEN POSITIONS SUMMARY BY TICKER (Top 20)")
    print("="*70)
    summary = loader.get_position_summary()
    print(summary.head(20))

    print("\n" + "="*70)
    print("OPEN POSITIONS BY ACCOUNT")
    print("="*70)
    accounts = loader.get_account_summary()
    print(accounts)

    print("\n" + "="*70)
    print("OPEN POSITIONS BY ACCOUNT TYPE")
    print("="*70)
    types = loader.get_account_type_summary()
    print(types)
