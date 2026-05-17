"""
Enhanced Portfolio Analysis Report
Covers all 8 accounts with comprehensive breakdown
"""

import pandas as pd
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')

from open_positions_loader_v2 import OpenPositionsLoaderV2
from enhanced_metrics import batch_get_metrics


class PortfolioAnalysisAllAccounts:
    """Enhanced portfolio analysis covering all 8 accounts"""

    def __init__(self):
        self.loader = OpenPositionsLoaderV2()
        self.open_positions, self.prices = self.loader.load_all_data()
        self.position_summary = self.loader.get_position_summary()
        self.account_summary = self.loader.get_account_summary()
        self.metrics = batch_get_metrics(
            self.position_summary.index.tolist(), self.prices
        )

    def generate_report(self, today: date = None) -> str:
        """Generate comprehensive portfolio analysis for all 8 accounts"""
        if today is None:
            today = date.today()

        output = []

        # Header
        output.append("=" * 100)
        output.append(f"COMPREHENSIVE PORTFOLIO ANALYSIS REPORT — ALL 8 ACCOUNTS")
        output.append(f"Generated: {today.strftime('%B %d, %Y')}")
        output.append("=" * 100)
        output.append("")

        # Executive Summary
        output.append("EXECUTIVE SUMMARY")
        output.append("-" * 100)
        output.append(f"Total Accounts:              8 (Schwab: 3, Fidelity: 2, Robinhood: 2, Vanguard: 1)")
        output.append(f"Total Open Positions:        {len(self.open_positions)}")
        output.append(f"Unique Tickers:              {self.open_positions['ticker'].nunique()}")
        output.append(f"Data Currency:               {today.isoformat()}")
        output.append("")

        # Portfolio Distribution by Account
        output.append("PORTFOLIO DISTRIBUTION BY ACCOUNT")
        output.append("-" * 100)
        total_positions = len(self.open_positions)
        total_notional = sum(self.prices.get(t, 0) * int(self.position_summary.loc[t, 'total_open_contracts']) * 100
                           for t in self.position_summary.index)

        for acct_name, row in self.account_summary.iterrows():
            acct_positions = self.open_positions[self.open_positions['account_name'] == acct_name]
            acct_notional = sum(self.prices.get(row['ticker'], 0) * row['net_quantity'] * 100
                              for _, row in acct_positions.iterrows())
            pct = 100 * len(acct_positions) / total_positions if total_positions > 0 else 0
            notional_pct = 100 * acct_notional / total_notional if total_notional > 0 else 0
            bar = "█" * int(pct / 2)

            output.append(f"{acct_name:35}: {len(acct_positions):3} pos ({pct:5.1f}%) | ${acct_notional:>12,.0f} ({notional_pct:5.1f}%) {bar}")

        output.append(f"{'TOTAL':35}: {total_positions:3} pos (100.0%) | ${total_notional:>12,.0f} (100.0%)")
        output.append("")

        # Top 25 Positions
        output.append("TOP 25 POSITIONS BY CONTRACTS")
        output.append("-" * 100)
        for i, (ticker, row) in enumerate(self.position_summary.head(25).iterrows(), 1):
            price = self.prices.get(ticker, 0)
            contracts = int(row['total_open_contracts'])
            accounts = int(row['accounts_with_position'])
            conviction = self.metrics.get(ticker, {}).get('conviction', 5.0)

            output.append(f"{i:2}. {ticker:8} ${price:>8.2f} | {contracts:3} contracts | {accounts} account(s) | Conv: {conviction:5.1f}/10")

        output.append("")

        # Conviction Distribution
        output.append("CONVICTION DISTRIBUTION")
        output.append("-" * 100)
        high_conv = []
        mod_conv = []
        low_conv = []

        for ticker, metrics in self.metrics.items():
            conv = metrics.get('conviction', 5.0)
            if conv >= 8:
                high_conv.append(ticker)
            elif conv >= 6:
                mod_conv.append(ticker)
            else:
                low_conv.append(ticker)

        output.append(f"HIGH CONVICTION (8-10):    {len(high_conv):3} positions — {', '.join(sorted(high_conv)[:10])}")
        if len(high_conv) > 10:
            output.append(f"                           {'':3}   and {len(high_conv) - 10} more")
        output.append("")
        output.append(f"MODERATE CONVICTION (6-8): {len(mod_conv):3} positions")
        output.append("")
        output.append(f"LOW CONVICTION (<6):       {len(low_conv):3} positions")
        output.append("")

        # Account-Specific Summaries
        output.append("DETAILED ACCOUNT SUMMARIES")
        output.append("=" * 100)
        output.append("")

        for acct_name in self.account_summary.index:
            acct_positions = self.open_positions[self.open_positions['account_name'] == acct_name]
            acct_notional = sum(self.prices.get(row['ticker'], 0) * row['net_quantity'] * 100
                              for _, row in acct_positions.iterrows())

            output.append(f"{acct_name.upper()}")
            output.append("-" * 100)
            output.append(f"├─ Positions: {len(acct_positions)}")
            output.append(f"├─ Total notional: ${acct_notional:,.0f}")
            output.append(f"├─ Top tickers in account:")

            # Top 5 tickers for this account
            top_by_contracts = acct_positions.groupby('ticker')['net_quantity'].sum().sort_values(ascending=False).head(5)
            for ticker, qty in top_by_contracts.items():
                price = self.prices.get(ticker, 0)
                notional = price * qty * 100
                conv = self.metrics.get(ticker, {}).get('conviction', 5.0)
                output.append(f"│   {ticker:8} | {qty:3} contracts | ${notional:>12,.0f} | Conv: {conv:.1f}/10")

            output.append("")

        output.append("=" * 100)
        output.append("")

        return "\n".join(output)


def main():
    analyzer = PortfolioAnalysisAllAccounts()
    report = analyzer.generate_report()

    # Save report
    logs_dir = Path('/home/rahulvadera/projects/theta-lab/logs')
    logs_dir.mkdir(exist_ok=True)

    today = date.today()
    filename = f'portfolio_analysis_all_accounts_{today.strftime("%Y-%m-%d")}.txt'
    filepath = logs_dir / filename

    with open(filepath, 'w') as f:
        f.write(report)

    print(report)
    print(f"\n✓ Saved to {filepath}")


if __name__ == '__main__':
    main()
