"""
Unified Master Report — All 8 Accounts (May 11, 2026)
Schwab (A/B/C) + Fidelity (2) + Vanguard + Robinhood (2)
"""

import pandas as pd
import sys
from datetime import date
from pathlib import Path
from typing import Optional, Dict, List

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
from open_positions_loader_v2 import OpenPositionsLoaderV2


async def generate_unified_master_report_8accounts(
    report_type: Optional[str] = None,
    save_to_file: bool = True
) -> dict:
    """Generate unified master report from all 8 accounts"""

    today = date.today()

    # Auto-detect report type
    if not report_type:
        if today.day == 1:
            report_type = 'MONTHLY'
        elif today.day == 15:
            report_type = 'BIWEEKLY'
        elif today.weekday() == 0:
            report_type = 'WEEKLY'
        else:
            report_type = 'DAILY'

    # Load all data
    print("\n" + "="*70)
    print("LOADING ALL 8 ACCOUNT DATA")
    print("="*70)

    loader = OpenPositionsLoaderV2()
    open_positions, prices = loader.load_all_data()

    position_summary = loader.get_position_summary()
    account_summary = loader.get_account_summary()
    type_summary = loader.get_account_type_summary()

    # Generate report
    output = []

    if report_type == 'DAILY':
        output = generate_daily_report(today, open_positions, prices, position_summary, account_summary, type_summary)
    elif report_type == 'WEEKLY':
        output = generate_weekly_report(today, open_positions, prices, position_summary, account_summary, type_summary)
    elif report_type == 'BIWEEKLY':
        output = generate_biweekly_report(today, open_positions, prices, position_summary, account_summary, type_summary)
    elif report_type == 'MONTHLY':
        output = generate_monthly_report(today, open_positions, prices, position_summary, account_summary, type_summary)

    report_text = "\n".join(output)

    # Save
    output_file = None
    if save_to_file:
        output_file = f"logs/unified_master_report_{today.isoformat()}_{report_type.lower()}_8accounts.txt"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"\n✓ Report saved to: {output_file}")

    print("="*70 + "\n")

    return {
        "text": report_text,
        "type": report_type,
        "saved_to": output_file
    }


def generate_daily_report(
    today: date,
    open_positions: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame,
    type_summary: pd.DataFrame
) -> List[str]:
    """Generate DAILY report"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — DAILY (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %d, %Y')} — 6:00 AM ET")
    output.append("=" * 80)
    output.append("")

    output.append("ACCOUNT POSITION SUMMARY")
    output.append("-" * 80)
    output.append("")

    output.append(f"Total open positions:        {len(open_positions)}")
    output.append(f"Unique tickers:              {open_positions['ticker'].nunique()}")
    output.append(f"Active accounts:             {account_summary.shape[0]}")
    output.append("")

    output.append("OPEN POSITIONS BY ACCOUNT TYPE:")
    output.append("-" * 80)
    for acct_type, row in type_summary.iterrows():
        output.append(f"• {acct_type}: {row['open_positions']} positions")
    output.append("")

    output.append("TOP 15 SYMBOLS BY OPEN CONTRACTS:")
    output.append("-" * 80)
    for i, (ticker, row) in enumerate(position_summary.head(15).iterrows(), 1):
        price = prices.get(ticker, 0)
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  {int(row['total_open_contracts']):2} contracts")
    output.append("")

    output.append("ACTIVE ACCOUNTS:")
    output.append("-" * 80)
    for account, row in account_summary.iterrows():
        output.append(f"• {account}: {row['open_positions']} positions")
    output.append("")

    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()}")
    output.append("=" * 80)

    return output


def generate_weekly_report(
    today: date,
    open_positions: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame,
    type_summary: pd.DataFrame
) -> List[str]:
    """Generate WEEKLY report"""
    output = []

    week_num = (today.day - 1) // 7 + 1

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — WEEKLY (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %d, %Y')} — 8:00 AM ET")
    output.append(f"Week {week_num} of {today.strftime('%B')}")
    output.append("=" * 80)
    output.append("")

    output.append("SECTION 1: PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    output.append(f"Total open positions:        {len(open_positions):,}")
    output.append(f"Unique tickers:              {open_positions['ticker'].nunique()}")
    output.append(f"Total accounts:              8")
    output.append(f"  Schwab:     3 accounts")
    output.append(f"  Fidelity:   2 accounts")
    output.append(f"  Robinhood:  2 accounts")
    output.append(f"  Vanguard:   1 account")
    output.append("")

    output.append("SECTION 2: MOST ACTIVE SYMBOLS (BY OPEN CONTRACTS)")
    output.append("=" * 80)
    output.append("")

    for i, (ticker, row) in enumerate(position_summary.head(20).iterrows(), 1):
        price = prices.get(ticker, 0)
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  {int(row['total_open_contracts']):2} contracts | {int(row['accounts_with_position'])} accounts")

    output.append("")

    output.append("SECTION 3: POSITION COUNT BY ACCOUNT TYPE")
    output.append("=" * 80)
    output.append("")

    total_positions = type_summary['open_positions'].sum()
    for acct_type, row in type_summary.iterrows():
        pct = 100 * row['open_positions'] / total_positions if total_positions > 0 else 0
        output.append(f"{acct_type:12}: {row['open_positions']:4} positions ({pct:5.1f}%)")

    output.append("")

    output.append("SECTION 4: INDIVIDUAL ACCOUNTS")
    output.append("=" * 80)
    output.append("")

    for account, row in account_summary.iterrows():
        output.append(f"• {account}: {row['open_positions']} positions")

    output.append("")
    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()}")
    output.append("=" * 80)

    return output


def generate_biweekly_report(
    today: date,
    open_positions: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame,
    type_summary: pd.DataFrame
) -> List[str]:
    """Generate BIWEEKLY report"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — BI-WEEKLY CHECKPOINT (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %d, %Y')}")
    output.append("=" * 80)
    output.append("")

    output.append("MID-MONTH PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    output.append(f"Total open positions:       {len(open_positions):,}")
    output.append(f"Unique tickers:             {open_positions['ticker'].nunique()}")
    output.append(f"Total accounts:             {account_summary.shape[0]} (across 4 brokers)")
    output.append("")

    output.append("TOP 10 POSITIONS BY CONTRACT COUNT")
    output.append("-" * 80)

    for i, (ticker, row) in enumerate(position_summary.head(10).iterrows(), 1):
        price = prices.get(ticker, 0)
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  {int(row['total_open_contracts'])} contracts")

    output.append("")
    output.append("=" * 80)

    return output


def generate_monthly_report(
    today: date,
    open_positions: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame,
    type_summary: pd.DataFrame
) -> List[str]:
    """Generate MONTHLY report"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — MONTHLY REVIEW (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %Y')}")
    output.append("=" * 80)
    output.append("")

    output.append("MONTHLY POSITION SUMMARY")
    output.append("=" * 80)
    output.append("")

    output.append(f"Month: {today.strftime('%B %Y')}")
    output.append("")
    output.append(f"Total open positions:       {len(open_positions):,}")
    output.append(f"Unique tickers:             {open_positions['ticker'].nunique()}")
    output.append(f"Total accounts:             {account_summary.shape[0]} across 4 brokers")
    output.append("")

    output.append("TOP 15 ACTIVE POSITIONS")
    output.append("-" * 80)

    for i, (ticker, row) in enumerate(position_summary.head(15).iterrows(), 1):
        price = prices.get(ticker, 0)
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  {int(row['total_open_contracts'])} open contracts")

    output.append("")
    output.append("=" * 80)

    return output
