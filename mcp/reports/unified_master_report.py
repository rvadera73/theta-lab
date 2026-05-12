"""
Unified Master Report — Summary of Real Position Data
"""

import pandas as pd
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import re

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from data_loader import DynamicDataLoader


async def generate_unified_master_report(
    report_type: Optional[str] = None,
    save_to_file: bool = True
) -> dict:
    """Generate unified master report from real account data"""

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

    positions_df, _ = DynamicDataLoader().load_all_data()

    print(f"\n✓ Loaded {len(positions_df)} total transactions/positions")

    # Extract real option positions from descriptions
    option_rows = positions_df[
        (positions_df['description'].notna()) &
        (positions_df['description'].astype(str).str.contains('PUT|CALL', regex=True, case=False)) &
        (positions_df['qty'] != 0)
    ]

    print(f"✓ Open option positions: {len(option_rows)}")
    print(f"✓ Unique symbols with options: {option_rows['symbol'].nunique()}")

    # Generate report
    output = []

    if report_type == 'DAILY':
        output = generate_daily_report(today, option_rows, positions_df)
    elif report_type == 'WEEKLY':
        output = generate_weekly_report(today, option_rows, positions_df)
    elif report_type == 'BIWEEKLY':
        output = generate_biweekly_report(today, option_rows, positions_df)
    elif report_type == 'MONTHLY':
        output = generate_monthly_report(today, option_rows, positions_df)

    report_text = "\n".join(output)

    # Save
    output_file = None
    if save_to_file:
        output_file = f"logs/unified_master_report_{today.isoformat()}_{report_type.lower()}.txt"
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


def generate_daily_report(today: date, option_rows: pd.DataFrame, positions_df: pd.DataFrame) -> List[str]:
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

    output.append(f"Total positions loaded:  {len(positions_df)}")
    output.append(f"Open option positions:   {len(option_rows)}")
    output.append(f"Symbols with options:    {option_rows['symbol'].nunique()}")
    output.append("")

    output.append("TOP SYMBOLS BY POSITION COUNT:")
    output.append("-" * 80)
    symbol_counts = option_rows['symbol'].value_counts().head(15)
    for i, (symbol, count) in enumerate(symbol_counts.items(), 1):
        output.append(f"{i:2}. {symbol:8} — {count:2} open positions")
    output.append("")

    output.append("ACCOUNTS ACTIVE:")
    output.append("-" * 80)
    account_counts = positions_df['account'].value_counts()
    for account, count in account_counts.items():
        output.append(f"• {account}: {count} positions")
    output.append("")

    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()}")
    output.append("=" * 80)

    return output


def generate_weekly_report(today: date, option_rows: pd.DataFrame, positions_df: pd.DataFrame) -> List[str]:
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

    total_positions = len(positions_df)
    option_positions = len(option_rows)
    unique_symbols = positions_df['symbol'].nunique()

    output.append(f"Total transactions/positions:  {total_positions:,}")
    output.append(f"Open option contracts:         {option_positions}")
    output.append(f"Unique symbols:                {unique_symbols}")
    output.append(f"Accounts tracked:              {positions_df['account'].nunique()}")
    output.append("")

    output.append("SECTION 2: MOST ACTIVE SYMBOLS")
    output.append("=" * 80)
    output.append("")

    top_symbols = option_rows['symbol'].value_counts().head(20)
    for i, (symbol, count) in enumerate(top_symbols.items(), 1):
        # Count by type (PUT/CALL)
        sym_options = option_rows[option_rows['symbol'] == symbol]
        put_count = len(sym_options[sym_options['description'].str.contains('PUT', case=False)])
        call_count = len(sym_options[sym_options['description'].str.contains('CALL', case=False)])

        output.append(f"{i:2}. {symbol:8} — Total: {count:2} | PUTs: {put_count} | CALLs: {call_count}")

    output.append("")

    output.append("SECTION 3: OPTION TYPE DISTRIBUTION")
    output.append("=" * 80)
    output.append("")

    put_count = len(option_rows[option_rows['description'].str.contains('PUT', case=False)])
    call_count = len(option_rows[option_rows['description'].str.contains('CALL', case=False)])

    output.append(f"Total PUTs:    {put_count:3} ({100*put_count/(put_count+call_count):.0f}%)")
    output.append(f"Total CALLs:   {call_count:3} ({100*call_count/(put_count+call_count):.0f}%)")
    output.append("")

    output.append("SECTION 4: ACCOUNT DISTRIBUTION")
    output.append("=" * 80)
    output.append("")

    for account, count in positions_df['account'].value_counts().head(10).items():
        output.append(f"• {account}: {count} positions")

    output.append("")
    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()}")
    output.append("=" * 80)

    return output


def generate_biweekly_report(today: date, option_rows: pd.DataFrame, positions_df: pd.DataFrame) -> List[str]:
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

    output.append(f"Total positions:        {len(positions_df):,}")
    output.append(f"Option positions:       {len(option_rows)}")
    output.append(f"Unique symbols:         {positions_df['symbol'].nunique()}")
    output.append("")

    output.append("TOP 10 POSITIONS BY SYMBOL")
    output.append("-" * 80)

    for i, (symbol, count) in enumerate(option_rows['symbol'].value_counts().head(10).items(), 1):
        output.append(f"{i:2}. {symbol:8} — {count} open positions")

    output.append("")
    output.append("=" * 80)

    return output


def generate_monthly_report(today: date, option_rows: pd.DataFrame, positions_df: pd.DataFrame) -> List[str]:
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
    output.append(f"Total positions loaded:  {len(positions_df):,}")
    output.append(f"Open option positions:   {len(option_rows)}")
    output.append(f"Unique symbols tracked:  {positions_df['symbol'].nunique()}")
    output.append("")

    output.append("TOP 15 ACTIVE POSITIONS")
    output.append("-" * 80)

    for i, (symbol, count) in enumerate(option_rows['symbol'].value_counts().head(15).items(), 1):
        output.append(f"{i:2}. {symbol:8} — {count} open option contracts")

    output.append("")
    output.append("=" * 80)

    return output
