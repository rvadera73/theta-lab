#!/usr/bin/env python3
"""
Real P&L Calculator — Reconciles all 8 accounts
Calculates realized (closed) and unrealized (open) P&L per account
"""

import pandas as pd
from pathlib import Path
from datetime import date
from data_loader_final import DataLoaderFinal

class PnLCalculator:
    """Calculate actual realized + unrealized P&L per account"""

    def __init__(self):
        self.loader = DataLoaderFinal()
        self.option_rows, self.prices = self.loader.load_all_data()
        self.account_pnl = {}

    def calculate_all_accounts(self):
        """Calculate P&L for each account"""
        if self.option_rows is None or self.option_rows.empty:
            return {}

        # Group by account
        for account_name in self.option_rows['account_name'].unique():
            account_data = self.option_rows[self.option_rows['account_name'] == account_name]
            self.account_pnl[account_name] = self._calculate_account_pnl(account_name, account_data)

        return self.account_pnl

    def _calculate_account_pnl(self, account_name: str, account_data: pd.DataFrame) -> dict:
        """Calculate PnL for a single account"""

        # Separate into STO (Sell to Open) and BTC (Buy to Close)
        sto_data = account_data[account_data['action'].str.contains('Sell.*Open', case=False, na=False)]
        btc_data = account_data[account_data['action'].str.contains('Buy.*Close', case=False, na=False)]

        realized_pnl = 0
        unrealized_pnl = 0

        # Calculate realized P&L from closed positions
        if not btc_data.empty:
            realized_pnl = btc_data['value'].sum() if 'value' in btc_data.columns else 0

        # Calculate unrealized P&L from open positions
        if not sto_data.empty:
            for _, row in sto_data.iterrows():
                try:
                    ticker = row.get('ticker')
                    quantity = row.get('quantity', 0)
                    premium_collected = row.get('value', 0)
                    current_price = self.prices.get(ticker, 0)

                    # Unrealized = premium collected - current mark
                    if current_price > 0 and quantity != 0:
                        mark_value = abs(quantity) * current_price * 100  # Options are per 100 shares
                        unrealized = premium_collected - mark_value
                        unrealized_pnl += unrealized
                except:
                    pass

        return {
            'realized': realized_pnl,
            'unrealized': unrealized_pnl,
            'total': realized_pnl + unrealized_pnl,
            'positions': len(account_data),
        }

    def format_report(self) -> str:
        """Format P&L by account"""
        output = []
        output.append("\n" + "=" * 100)
        output.append("ACCOUNT P&L SUMMARY (Real Data)")
        output.append("=" * 100)
        output.append("")
        output.append(f"{'Account':<45} {'Realized':>12} {'Unrealized':>12} {'Total':>12} {'Positions':>10}")
        output.append("-" * 100)

        total_realized = 0
        total_unrealized = 0

        for account_name in sorted(self.account_pnl.keys()):
            pnl = self.account_pnl[account_name]
            output.append(
                f"{account_name:<45} ${pnl['realized']:>11,.0f} ${pnl['unrealized']:>11,.0f} "
                f"${pnl['total']:>11,.0f} {pnl['positions']:>10}"
            )
            total_realized += pnl['realized']
            total_unrealized += pnl['unrealized']

        output.append("-" * 100)
        output.append(
            f"{'TOTAL':<45} ${total_realized:>11,.0f} ${total_unrealized:>11,.0f} "
            f"${total_realized + total_unrealized:>11,.0f}"
        )
        output.append("")

        return "\n".join(output)

if __name__ == '__main__':
    print("\n" + "=" * 100)
    print("Loading all 8 accounts and calculating P&L...")
    print("=" * 100)

    calc = PnLCalculator()
    pnl_by_account = calc.calculate_all_accounts()

    print(calc.format_report())

    # Save to file
    output_file = f'/home/rahulvadera/projects/theta-lab/logs/account_pnl_{date.today().isoformat()}.txt'
    Path(output_file).write_text(calc.format_report())
    print(f"✓ P&L summary saved to {Path(output_file).name}")
