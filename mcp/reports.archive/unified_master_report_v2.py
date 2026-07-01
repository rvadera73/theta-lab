"""
Unified Master Report v2 — Real Position Data from May 11 Accounts
Generates DAILY, WEEKLY, BIWEEKLY, MONTHLY reports with live prices
"""

import pandas as pd
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Dict, List
import re

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
from data_loader_may11 import DataLoaderMay11


async def generate_unified_master_report_v2(
    report_type: Optional[str] = None,
    save_to_file: bool = True
) -> dict:
    """Generate unified master report from real May 11 account data"""

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

    # Load real positions
    print("\n" + "="*70)
    print("LOADING ACCOUNT DATA")
    print("="*70)

    loader = DataLoaderMay11()
    option_rows, prices = loader.load_all_data()

    print(f"\n✓ Loaded {len(option_rows)} option transactions")
    print(f"✓ Unique symbols: {option_rows['ticker'].nunique()}")
    print(f"✓ Live prices: {len(prices)}")

    # Get summaries
    position_summary = loader.get_position_summary()
    account_summary = loader.get_account_summary()

    # Generate report
    output = []

    if report_type == 'DAILY':
        output = generate_daily_report(today, option_rows, prices, position_summary, account_summary)
    elif report_type == 'WEEKLY':
        output = generate_weekly_report(today, option_rows, prices, position_summary, account_summary)
    elif report_type == 'BIWEEKLY':
        output = generate_biweekly_report(today, option_rows, prices, position_summary, account_summary)
    elif report_type == 'MONTHLY':
        output = generate_monthly_report(today, option_rows, prices, position_summary, account_summary)

    report_text = "\n".join(output)

    # Save
    output_file = None
    if save_to_file:
        output_file = f"logs/unified_master_report_{today.isoformat()}_{report_type.lower()}_v2.txt"
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
    option_rows: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame
) -> List[str]:
    """Generate DAILY report"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — DAILY")
    output.append(f"{today.strftime('%B %d, %Y')} — 6:00 AM ET")
    output.append("=" * 80)
    output.append("")

    output.append("ACCOUNT POSITION SUMMARY")
    output.append("-" * 80)
    output.append("")

    output.append(f"Total option transactions:   {len(option_rows)}")
    output.append(f"Unique symbols with options: {option_rows['ticker'].nunique()}")
    output.append(f"Active accounts:             {account_summary.shape[0]}")
    output.append("")

    output.append("TOP 15 SYMBOLS BY TRANSACTION COUNT:")
    output.append("-" * 80)
    for i, (ticker, row) in enumerate(position_summary.head(15).iterrows(), 1):
        price = prices.get(ticker, 0)
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  {int(row['transactions']):2} transactions  |  {row['position_mix']}")
    output.append("")

    output.append("ACCOUNTS ACTIVE:")
    output.append("-" * 80)
    for account, row in account_summary.iterrows():
        output.append(f"• {account}: {row['position_count']} positions")
    output.append("")

    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()}")
    output.append("=" * 80)

    return output


def generate_weekly_report(
    today: date,
    option_rows: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame
) -> List[str]:
    """Generate WEEKLY report"""
    output = []

    week_num = (today.day - 1) // 7 + 1

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — WEEKLY")
    output.append(f"{today.strftime('%B %d, %Y')} — 8:00 AM ET")
    output.append(f"Week {week_num} of {today.strftime('%B')}")
    output.append("=" * 80)
    output.append("")

    output.append("SECTION 1: PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    total_transactions = len(option_rows)
    unique_symbols = option_rows['ticker'].nunique()
    accounts_tracked = account_summary.shape[0]

    output.append(f"Total option transactions:   {total_transactions:,}")
    output.append(f"Unique symbols tracked:      {unique_symbols}")
    output.append(f"Accounts tracked:            {accounts_tracked}")
    output.append("")

    # Calculate position mix
    call_count = len(option_rows[option_rows['type'] == 'CALL'])
    put_count = len(option_rows[option_rows['type'] == 'PUT'])
    total_positions = call_count + put_count

    output.append("SECTION 2: MOST ACTIVE SYMBOLS")
    output.append("=" * 80)
    output.append("")

    for i, (ticker, row) in enumerate(position_summary.head(20).iterrows(), 1):
        price = prices.get(ticker, 0)
        calls = len(option_rows[(option_rows['ticker'] == ticker) & (option_rows['type'] == 'CALL')])
        puts = len(option_rows[(option_rows['ticker'] == ticker) & (option_rows['type'] == 'PUT')])
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  Total: {int(row['transactions']):2} | Calls: {calls} | Puts: {puts}")

    output.append("")

    output.append("SECTION 3: OPTION TYPE DISTRIBUTION")
    output.append("=" * 80)
    output.append("")

    if total_positions > 0:
        call_pct = 100 * call_count / total_positions
        put_pct = 100 * put_count / total_positions
        output.append(f"Total Calls:   {call_count:3} ({call_pct:.0f}%)")
        output.append(f"Total Puts:    {put_count:3} ({put_pct:.0f}%)")
    output.append("")

    output.append("SECTION 4: ACCOUNT DISTRIBUTION")
    output.append("=" * 80)
    output.append("")

    for account, row in account_summary.iterrows():
        output.append(f"• {account}: {row['position_count']} positions")

    output.append("")
    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()}")
    output.append("=" * 80)

    return output


def generate_biweekly_report(
    today: date,
    option_rows: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame
) -> List[str]:
    """Generate BIWEEKLY report"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — BI-WEEKLY CHECKPOINT")
    output.append(f"{today.strftime('%B %d, %Y')}")
    output.append("=" * 80)
    output.append("")

    output.append("MID-MONTH PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    output.append(f"Total option transactions:  {len(option_rows):,}")
    output.append(f"Unique symbols:             {option_rows['ticker'].nunique()}")
    output.append(f"Active accounts:            {account_summary.shape[0]}")
    output.append("")

    output.append("TOP 10 POSITIONS BY SYMBOL")
    output.append("-" * 80)

    for i, (ticker, row) in enumerate(position_summary.head(10).iterrows(), 1):
        price = prices.get(ticker, 0)
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  {int(row['transactions'])} positions")

    output.append("")
    output.append("=" * 80)

    return output


def generate_monthly_report(
    today: date,
    option_rows: pd.DataFrame,
    prices: Dict[str, float],
    position_summary: pd.DataFrame,
    account_summary: pd.DataFrame
) -> List[str]:
    """Generate MONTHLY report"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — MONTHLY REVIEW")
    output.append(f"{today.strftime('%B %Y')}")
    output.append("=" * 80)
    output.append("")

    output.append("MONTHLY POSITION SUMMARY")
    output.append("=" * 80)
    output.append("")

    output.append(f"Month: {today.strftime('%B %Y')}")
    output.append("")
    output.append(f"Total option transactions:  {len(option_rows):,}")
    output.append(f"Unique symbols tracked:     {option_rows['ticker'].nunique()}")
    output.append(f"Active accounts:            {account_summary.shape[0]}")
    output.append("")

    output.append("TOP 15 ACTIVE POSITIONS")
    output.append("-" * 80)

    for i, (ticker, row) in enumerate(position_summary.head(15).iterrows(), 1):
        price = prices.get(ticker, 0)
        output.append(f"{i:2}. {ticker:8} ${price:>8.2f}  —  {int(row['transactions'])} option contracts")

    output.append("")
    output.append("=" * 80)

    return output
