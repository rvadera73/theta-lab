"""
Data schema validator and transformer.

Validates incoming Schwab/Empower exports against required schema.
Transforms raw exports into standardized format for screener.
"""

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Literal, Optional, List
import csv
import json
from pathlib import Path

# ============================================================================
# DATA SCHEMAS (Single source of truth)
# ============================================================================

@dataclass
class Transaction:
    """A single options or equity trade."""

    date: date  # Trade date
    account_code: str  # "232", "275", "634", etc.
    account_name: str  # "Account A Margin", "Account B IRA", etc.
    action: Literal["Sell to Open", "Buy to Close", "Sell to Close", "Buy to Open"]
    symbol: str  # Ticker only (AXON, CRWD, etc. — no spaces)

    # For options: expiry, strike, type; for equities: None
    expiry: Optional[date] = None  # MM/DD/YYYY for options
    strike: Optional[float] = None  # Strike price for options
    option_type: Optional[Literal["CALL", "PUT"]] = None

    quantity: int = 1  # Always 1 or -1 per contract
    price: float = 0.0  # Premium per contract (for options) or price per share (for equity)
    commission: float = 0.0  # Fees
    net_amount: float = 0.0  # Credit/debit to account

    # Optional metadata
    description: str = ""  # Raw description from broker

    def is_valid(self) -> tuple[bool, str]:
        """Validate transaction against schema."""

        # Action must be valid
        valid_actions = {"Sell to Open", "Buy to Close", "Sell to Close", "Buy to Open"}
        if self.action not in valid_actions:
            return False, f"Invalid action: {self.action}"

        # Symbol must have no spaces
        if " " in self.symbol:
            return False, f"Symbol has spaces: {self.symbol}"

        # For options, all fields required
        if "Call" in self.description or "Put" in self.description or self.option_type:
            if not all([self.expiry, self.strike, self.option_type]):
                return False, "Option trade missing expiry/strike/type"

            # Quantity must be ±1
            if self.quantity not in [1, -1]:
                return False, f"Option quantity must be ±1, got {self.quantity}"

            # Net amount = Qty × Price × 100 ± Commission
            expected = abs(self.quantity * self.price * 100 - self.commission)
            if abs(abs(self.net_amount) - expected) > 1:  # Allow $1 rounding
                return False, f"Amount mismatch: {self.net_amount} vs {expected}"

        # Date must be valid
        if self.date > date.today():
            return False, f"Future trade date: {self.date}"

        return True, "Valid"


@dataclass
class Position:
    """A current open position (option or equity)."""

    account_code: str
    account_name: str
    symbol: str

    # For options: expiry, strike, type; for equities: None
    expiry: Optional[date] = None
    strike: Optional[float] = None
    option_type: Optional[Literal["CALL", "PUT"]] = None

    quantity: int = 1  # 1 or -1 for options; shares for equity
    mark_price: float = 0.0  # Mid-market premium (options) or price (equity)
    delta: Optional[float] = None  # For options only
    gamma: Optional[float] = None
    vega: Optional[float] = None
    theta: Optional[float] = None
    market_value: float = 0.0  # Qty × Mark × 100 (options) or Qty × Mark (equity)

    def is_valid(self) -> tuple[bool, str]:
        """Validate position against schema."""

        # Position must not be expired
        if self.expiry and self.expiry <= date.today():
            return False, f"Expired position: {self.symbol} exp {self.expiry}"

        # Delta must be valid if present
        if self.delta and not (-1 <= self.delta <= 1):
            return False, f"Invalid delta: {self.delta}"

        # Mark price must be positive
        if self.mark_price <= 0:
            return False, f"Invalid mark price: {self.mark_price}"

        return True, "Valid"


@dataclass
class AccountBalance:
    """Current account balances and constraints."""

    account_code: str
    account_name: str
    account_type: Literal["Margin", "IRA", "Taxable", "Trust", "Other"]

    total_equity: float  # Net liquidation value
    cash_available: float  # Free cash
    margin_utilization_pct: float  # 0-100
    buying_power: float  # For margin accounts
    option_requirement: float  # Margin tied up in options

    def is_valid(self) -> tuple[bool, str]:
        """Validate account balance against schema."""

        if self.total_equity <= 0:
            return False, f"Invalid equity: {self.total_equity}"

        if not (0 <= self.margin_utilization_pct <= 100):
            return False, f"Invalid margin %: {self.margin_utilization_pct}"

        if self.cash_available < 0:
            return False, f"Negative cash: {self.cash_available}"

        if self.account_type == "Margin" and self.buying_power < self.cash_available:
            return False, f"Buying power < cash for margin account"

        return True, "Valid"


@dataclass
class UniverseName:
    """Portfolio universe definition (tier classification)."""

    symbol: str
    tier: Literal[1, 2, 3]
    reason: str  # Why this tier?
    min_iv_rank: int  # Min IV rank to trade this name (50, 40, 30, etc.)
    min_volume_millions: float  # Minimum daily volume in millions
    account_a_max_contracts: int  # Max contracts in Account A
    account_b_max_contracts: int  # Max in Account B (typically 0 or 1)
    account_b_allowed: bool  # Can be traded in IRA?
    last_updated: date

    def is_valid(self) -> tuple[bool, str]:
        """Validate universe entry against schema."""

        if self.tier not in [1, 2, 3]:
            return False, f"Invalid tier: {self.tier}"

        if not (0 <= self.min_iv_rank <= 100):
            return False, f"Invalid IV rank: {self.min_iv_rank}"

        if self.min_volume_millions < 0:
            return False, f"Invalid volume: {self.min_volume_millions}"

        if self.account_a_max_contracts <= 0:
            return False, f"Account A max must be > 0"

        return True, "Valid"


# ============================================================================
# VALIDATORS
# ============================================================================

class TransactionValidator:
    """Validates transaction CSVs."""

    @staticmethod
    def parse_schwab_format(raw_csv_path: Path) -> List[Transaction]:
        """Parse raw Schwab transaction export."""
        transactions = []

        with open(raw_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Extract symbol and option details from description
                    desc = row.get('Description', '')
                    symbol = row.get('Symbol', '').split()[0] if row.get('Symbol') else None

                    # Parse expiry/strike/type from description
                    # Format: "PUT SYMBOL $strike Exp MM/DD/YYYY"
                    expiry, strike, opt_type = None, None, None
                    if 'Put' in desc or 'Call' in desc:
                        opt_type = "PUT" if "Put" in desc else "CALL"
                        # Extract strike and expiry (implementation depends on format)

                    transaction = Transaction(
                        date=datetime.strptime(row['Date'], '%m/%d/%Y').date(),
                        account_code="232",  # TODO: derive from account name
                        account_name="Account A",
                        action=row.get('Action', ''),
                        symbol=symbol or "UNK",
                        expiry=expiry,
                        strike=strike,
                        option_type=opt_type,
                        quantity=int(row.get('Quantity', 1)),
                        price=float(row.get('Price', 0)),
                        commission=float(row.get('Fees & Comm', 0)),
                        net_amount=float(row.get('Amount', 0)),
                        description=desc,
                    )

                    valid, msg = transaction.is_valid()
                    if valid:
                        transactions.append(transaction)
                    else:
                        print(f"INVALID: {msg} | {row}")

                except Exception as e:
                    print(f"ERROR parsing row: {row} | {e}")

        return transactions

    @staticmethod
    def validate_batch(transactions: List[Transaction]) -> dict:
        """Validate a batch of transactions."""
        results = {
            'total': len(transactions),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }

        for txn in transactions:
            valid, msg = txn.is_valid()
            if valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({'transaction': asdict(txn), 'error': msg})

        return results


class PositionValidator:
    """Validates position CSVs."""

    @staticmethod
    def validate_batch(positions: List[Position]) -> dict:
        """Validate a batch of positions."""
        results = {
            'total': len(positions),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }

        for pos in positions:
            valid, msg = pos.is_valid()
            if valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({'position': asdict(pos), 'error': msg})

        return results


class BalanceValidator:
    """Validates account balance CSVs."""

    @staticmethod
    def validate_batch(balances: List[AccountBalance]) -> dict:
        """Validate a batch of account balances."""
        results = {
            'total': len(balances),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }

        for bal in balances:
            valid, msg = bal.is_valid()
            if valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({'account': asdict(bal), 'error': msg})

        return results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Data Schema Validator v1.0")
    print("=" * 60)

    # Example: Parse and validate a Schwab export
    # txns = TransactionValidator.parse_schwab_format(
    #     Path("data/statements/Individual_XXX232_Transactions_20260506-113045.csv")
    # )
    # print(f"Parsed {len(txns)} transactions")
    # results = TransactionValidator.validate_batch(txns)
    # print(f"Valid: {results['valid']}, Invalid: {results['invalid']}")
    # if results['errors']:
    #     for err in results['errors'][:5]:  # Show first 5 errors
    #         print(f"  - {err}")
