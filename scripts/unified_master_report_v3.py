"""
Unified Master Report V3 — All 8 Accounts with Template Sections
Uses OpenPositionsLoaderV2 + Yahoo Finance live prices with comprehensive template structure
"""

import pandas as pd
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
from open_positions_loader_v2 import OpenPositionsLoaderV2


def detect_report_type():
    """Auto-detect: DAILY | BI-WEEKLY (15th) | WEEKLY (Monday) | MONTHLY (1st)"""
    today = date.today()
    if today.day == 1:
        return 'MONTHLY'
    elif today.day == 15:
        return 'BIWEEKLY'
    elif today.weekday() == 0:
        return 'WEEKLY'
    else:
        return 'DAILY'


def generate_daily_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary):
    """Generate DAILY report with template sections"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — DAILY (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %d, %Y')} — 6:00 AM ET")
    output.append("=" * 80)
    output.append("")

    output.append("SYSTEM STATUS: Multi-broker portfolio tracking with live Yahoo Finance prices")
    output.append("Report Type: DAILY")
    output.append(f"Data Sources: 8 Accounts (Schwab, Fidelity, Vanguard, Robinhood) + Yahoo Finance")
    output.append(f"Positions analyzed: {len(open_positions)}")
    output.append(f"Unique tickers: {open_positions['ticker'].nunique()}")
    output.append("")
    output.append("=" * 80)
    output.append("")

    # SECTION 1: PORTFOLIO SNAPSHOT
    output.append("=" * 80)
    output.append("SECTION 1: PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    output.append(f"ACCOUNT STRUCTURE — {today.isoformat()}")
    output.append("")
    output.append(f"Total open positions:        {len(open_positions)}")
    output.append(f"Unique tickers:              {open_positions['ticker'].nunique()}")
    output.append("")
    output.append("Broker Distribution:")
    for acct_type in ['Schwab', 'Fidelity', 'Vanguard', 'Robinhood']:
        count = len(open_positions[open_positions['account_type'] == acct_type])
        pct = 100 * count / len(open_positions) if len(open_positions) > 0 else 0
        output.append(f"  • {acct_type:12}: {count:3} positions ({pct:5.1f}%)")
    output.append("")

    # SECTION 2: TOP POSITIONS
    output.append("=" * 80)
    output.append("SECTION 2: TOP 20 POSITIONS BY OPEN CONTRACTS")
    output.append("=" * 80)
    output.append("")

    for i, (ticker, row) in enumerate(position_summary.head(20).iterrows(), 1):
        price = prices.get(ticker, 0)
        contracts = int(row['total_open_contracts'])
        accounts = int(row['accounts_with_position'])
        output.append(f"{i:2}. {ticker:8} | ${price:>9.2f} | {contracts:3} contracts | {accounts:2} accounts")

    output.append("")

    # SECTION 3: ACCOUNT DETAILS
    output.append("=" * 80)
    output.append("SECTION 3: POSITIONS BY ACCOUNT")
    output.append("=" * 80)
    output.append("")

    for account, row in account_summary.iterrows():
        output.append(f"• {account:30}: {row['open_positions']:3} positions")

    output.append("")

    # SECTION 4: ACCOUNT TYPE ANALYSIS
    output.append("=" * 80)
    output.append("SECTION 4: DISTRIBUTION BY ACCOUNT TYPE")
    output.append("=" * 80)
    output.append("")

    total_positions = len(open_positions)
    for acct_type, row in type_summary.iterrows():
        pct = 100 * row['open_positions'] / total_positions if total_positions > 0 else 0
        bar = "█" * int(pct / 5)
        output.append(f"{acct_type:12} {row['open_positions']:3} positions ({pct:5.1f}%) {bar}")

    output.append("")

    # SECTION 5: OODA SUMMARY
    output.append("=" * 80)
    output.append("SECTION 5: OODA SUMMARY — LIVE DATA ANALYSIS")
    output.append("=" * 80)
    output.append("")

    output.append("Observe (Live Data from Yahoo Finance):")
    output.append(f"  ✅ {len(open_positions)} positions tracked across 8 accounts")
    output.append(f"  ✅ {open_positions['ticker'].nunique()} unique tickers")
    output.append(f"  ✅ {len(prices)} live prices fetched from Yahoo Finance")
    output.append(f"  ✅ Data currency: {today.isoformat()}")
    output.append("")

    output.append("Orient (Broker Diversity Analysis):")
    for acct_type, row in type_summary.iterrows():
        pct = 100 * row['open_positions'] / total_positions if total_positions > 0 else 0
        status = "✅" if row['open_positions'] > 0 else "⚠️"
        output.append(f"  {status} {acct_type:12}: {row['open_positions']:3} positions ({pct:5.1f}%)")
    output.append("")

    output.append("Decide (Position Management):")
    output.append("  1. Monitor live prices for mark-to-market changes")
    output.append("  2. Track position concentration across accounts")
    output.append("  3. Rebalance if any account exceeds risk limits")
    output.append("")

    output.append("Act (Next Steps):")
    output.append("  • Review top 20 positions for potential rolls/closes")
    output.append("  • Assess account-specific risk exposure")
    output.append("  • Prepare for weekly rebalancing decisions")
    output.append("")

    # FOOTER
    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()} | Data source: OpenPositionsLoaderV2 + Yahoo Finance")
    output.append("=" * 80)

    return "\n".join(output)


def generate_weekly_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary):
    """Generate WEEKLY report with template sections"""
    output = []
    week_num = (today.day - 1) // 7 + 1

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — WEEKLY (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %d, %Y')} — 8:00 AM ET")
    output.append(f"Week {week_num} of {today.strftime('%B')}")
    output.append("=" * 80)
    output.append("")

    output.append("SYSTEM STATUS: Weekly tier evolution & broker diversification analysis")
    output.append("Report Type: WEEKLY")
    output.append(f"Data Sources: 8 Accounts + Yahoo Finance (Live)")
    output.append(f"Total positions: {len(open_positions)}")
    output.append("")
    output.append("=" * 80)
    output.append("")

    # SECTION 1: PORTFOLIO SNAPSHOT
    output.append("=" * 80)
    output.append("SECTION 1: WEEKLY PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    output.append(f"Total open positions:        {len(open_positions):,}")
    output.append(f"Unique symbols tracked:      {open_positions['ticker'].nunique()}")
    output.append(f"Total accounts:              8")
    output.append(f"  Schwab:     3 accounts")
    output.append(f"  Fidelity:   2 accounts")
    output.append(f"  Robinhood:  2 accounts")
    output.append(f"  Vanguard:   1 account")
    output.append("")

    # SECTION 2: MOST ACTIVE SYMBOLS
    output.append("=" * 80)
    output.append("SECTION 2: TOP 25 SYMBOLS BY OPEN CONTRACTS")
    output.append("=" * 80)
    output.append("")

    for i, (ticker, row) in enumerate(position_summary.head(25).iterrows(), 1):
        price = prices.get(ticker, 0)
        contracts = int(row['total_open_contracts'])
        accounts = int(row['accounts_with_position'])
        bar = "█" * min(int(contracts / 2), 20)
        output.append(f"{i:2}. {ticker:8} | ${price:>9.2f} | {contracts:3} contracts | {accounts:2} accounts | {bar}")

    output.append("")

    # SECTION 3: BROKER DISTRIBUTION
    output.append("=" * 80)
    output.append("SECTION 3: BROKER DISTRIBUTION & CONCENTRATION")
    output.append("=" * 80)
    output.append("")

    output.append("POSITIONS BY ACCOUNT TYPE:")
    total = len(open_positions)
    for acct_type, row in type_summary.iterrows():
        pct = 100 * row['open_positions'] / total if total > 0 else 0
        status = "✅" if pct > 10 else "⚠️"
        output.append(f"  {status} {acct_type:12}: {row['open_positions']:3} ({pct:5.1f}%)")

    output.append("")
    output.append("POSITIONS BY INDIVIDUAL ACCOUNT:")
    for account, row in account_summary.iterrows():
        output.append(f"  • {account:30}: {row['open_positions']:3} positions")

    output.append("")

    # SECTION 4: RISK CONCENTRATION
    output.append("=" * 80)
    output.append("SECTION 4: CONCENTRATION & RISK ANALYSIS")
    output.append("=" * 80)
    output.append("")

    top_5_concentration = position_summary.head(5)['total_open_contracts'].sum()
    top_5_pct = 100 * top_5_concentration / open_positions['net_quantity'].sum() if len(open_positions) > 0 else 0

    output.append(f"Top 5 symbols concentration:  {top_5_pct:.1f}%")
    output.append(f"Diversification:             {open_positions['ticker'].nunique()} tickers across {len(account_summary)} accounts")
    output.append(f"Average position size:       {len(open_positions) / open_positions['ticker'].nunique():.1f} contracts per ticker")
    output.append("")

    # SECTION 5: OODA WEEKLY
    output.append("=" * 80)
    output.append("SECTION 5: WEEKLY OODA — STRATEGIC ANALYSIS")
    output.append("=" * 80)
    output.append("")

    output.append("Observe (Live Market Analysis):")
    output.append(f"  ✅ {len(open_positions)} total open positions")
    output.append(f"  ✅ {open_positions['ticker'].nunique()} unique tickers")
    output.append(f"  ✅ {len(account_summary)} active accounts across 4 brokers")
    output.append("")

    output.append("Orient (Broker Perspective):")
    for acct_type, row in type_summary.iterrows():
        pct = 100 * row['open_positions'] / total if total > 0 else 0
        output.append(f"  • {acct_type}: {row['open_positions']} positions ({pct:.1f}% of portfolio)")

    output.append("")

    output.append("Decide (Weekly Actions):")
    output.append("  1. Evaluate top 5 positions for profit-taking at 40-60% max profit")
    output.append("  2. Check positions approaching 21 DTE for roll opportunities")
    output.append("  3. Monitor concentration — ensure no single ticker >15% of portfolio")
    output.append("  4. Review account-type distribution for imbalances")
    output.append("")

    output.append("Act (Implementation):")
    output.append("  • Close profitable positions per exit matrix")
    output.append("  • Roll near-expiry positions per roll framework")
    output.append("  • Rebalance broker concentration if needed")
    output.append("")

    # SECTION 6: 3-MONTH TREND
    output.append("=" * 80)
    output.append("SECTION 6: PORTFOLIO TREND ANALYSIS")
    output.append("=" * 80)
    output.append("")

    output.append("Position Count Tracking (Weekly snapshots):")
    output.append("  Week 1: N/A (Baseline)")
    output.append(f"  Week {week_num}: {len(open_positions)} total positions")
    output.append("  Trend: Tracking portfolio evolution")
    output.append("")

    output.append("Broker Diversification Progress:")
    output.append("  • Schwab: Primary account (established)")
    output.append("  • Fidelity: Secondary accounts (IRA tier)")
    output.append("  • Robinhood: IRA + Taxable (growth)")
    output.append("  • Vanguard: Tertiary account (hold)")
    output.append("")

    # FOOTER
    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()} | Week {week_num} of {today.strftime('%B')}")
    output.append("=" * 80)

    return "\n".join(output)


def generate_biweekly_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary):
    """Generate BIWEEKLY report with template sections"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — BI-WEEKLY CHECKPOINT (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %d, %Y')}")
    output.append("=" * 80)
    output.append("")

    output.append("SYSTEM STATUS: Mid-month portfolio checkpoint")
    output.append("Report Type: BIWEEKLY")
    output.append(f"Checkpoint date: {today.isoformat()}")
    output.append("")
    output.append("=" * 80)
    output.append("")

    # SECTION 1: CHECKPOINT SNAPSHOT
    output.append("=" * 80)
    output.append("SECTION 1: MID-MONTH PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    output.append(f"Total open positions:       {len(open_positions):,}")
    output.append(f"Unique symbols:             {open_positions['ticker'].nunique()}")
    output.append(f"Total accounts:             {len(account_summary)} (across 4 brokers)")
    output.append("")

    # SECTION 2: TOP POSITIONS
    output.append("=" * 80)
    output.append("SECTION 2: TOP 10 POSITIONS BY CONTRACT COUNT")
    output.append("=" * 80)
    output.append("")

    for i, (ticker, row) in enumerate(position_summary.head(10).iterrows(), 1):
        price = prices.get(ticker, 0)
        contracts = int(row['total_open_contracts'])
        output.append(f"{i:2}. {ticker:8} ${price:>9.2f}  —  {contracts:3} contracts")

    output.append("")

    # SECTION 3: BROKER STATUS
    output.append("=" * 80)
    output.append("SECTION 3: BROKER STATUS — MID-MONTH CHECK")
    output.append("=" * 80)
    output.append("")

    total = len(open_positions)
    for account, row in account_summary.iterrows():
        pct = 100 * row['open_positions'] / total if total > 0 else 0
        output.append(f"• {account:30}: {row['open_positions']:3} positions ({pct:5.1f}%)")

    output.append("")

    # SECTION 4: ANALYSIS
    output.append("=" * 80)
    output.append("SECTION 4: CONCENTRATION ANALYSIS")
    output.append("=" * 80)
    output.append("")

    top_10_qty = position_summary.head(10)['total_open_contracts'].sum()
    top_10_pct = 100 * top_10_qty / open_positions['net_quantity'].sum() if len(open_positions) > 0 else 0

    output.append(f"Top 10 concentration:       {top_10_pct:.1f}%")
    output.append(f"Avg contracts per ticker:   {len(open_positions) / open_positions['ticker'].nunique():.1f}")
    output.append(f"Account diversity score:    {len(account_summary)}/8 accounts active")
    output.append("")

    # FOOTER
    output.append("=" * 80)
    output.append(f"Checkpoint generated: {today.isoformat()}")
    output.append("=" * 80)

    return "\n".join(output)


def generate_monthly_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary):
    """Generate MONTHLY report with template sections"""
    output = []

    output.append("=" * 80)
    output.append("UNIFIED MASTER REPORT — MONTHLY REVIEW (8 ACCOUNTS)")
    output.append(f"{today.strftime('%B %Y')}")
    output.append("=" * 80)
    output.append("")

    output.append("SYSTEM STATUS: Monthly portfolio review with all 8 accounts")
    output.append("Report Type: MONTHLY")
    output.append(f"Reporting date: {today.isoformat()}")
    output.append(f"Positions analyzed: {len(open_positions)}")
    output.append("")
    output.append("=" * 80)
    output.append("")

    # SECTION 1: MONTHLY SNAPSHOT
    output.append("=" * 80)
    output.append("SECTION 1: MONTHLY PORTFOLIO SNAPSHOT")
    output.append("=" * 80)
    output.append("")

    output.append(f"Month: {today.strftime('%B %Y')}")
    output.append("")
    output.append(f"Total open positions:  {len(open_positions):,}")
    output.append(f"Unique symbols tracked: {open_positions['ticker'].nunique()}")
    output.append(f"Total accounts:        {len(account_summary)} across 4 brokers")
    output.append("")

    # SECTION 2: TOP POSITIONS
    output.append("=" * 80)
    output.append("SECTION 2: TOP 15 ACTIVE POSITIONS")
    output.append("=" * 80)
    output.append("")

    for i, (ticker, row) in enumerate(position_summary.head(15).iterrows(), 1):
        price = prices.get(ticker, 0)
        contracts = int(row['total_open_contracts'])
        output.append(f"{i:2}. {ticker:8} | ${price:>9.2f}  |  {contracts:3} open contracts")

    output.append("")

    # SECTION 3: MONTHLY PERFORMANCE
    output.append("=" * 80)
    output.append("SECTION 3: ACCOUNT TYPE PERFORMANCE")
    output.append("=" * 80)
    output.append("")

    total = len(open_positions)
    for acct_type, row in type_summary.iterrows():
        pct = 100 * row['open_positions'] / total if total > 0 else 0
        output.append(f"{acct_type:12}: {row['open_positions']:3} positions ({pct:5.1f}%)")

    output.append("")

    # SECTION 4: MONTHLY SUMMARY
    output.append("=" * 80)
    output.append("SECTION 4: MONTHLY ACTION SUMMARY")
    output.append("=" * 80)
    output.append("")

    output.append(f"Current month: {today.strftime('%B %d, %Y')}")
    output.append(f"Portfolio positions: {len(open_positions)}")
    output.append(f"Diversification: {open_positions['ticker'].nunique()} unique tickers")
    output.append("")
    output.append("Actions taken this month:")
    output.append("  • Monitored all 8 accounts for position management")
    output.append("  • Tracked live prices via Yahoo Finance")
    output.append("  • Maintained broker diversification")
    output.append("  • Excluded closed-out positions from reporting")
    output.append("")

    # FOOTER
    output.append("=" * 80)
    output.append(f"Report generated: {today.isoformat()} | {today.strftime('%B %Y')} review complete")
    output.append("=" * 80)

    return "\n".join(output)


async def generate_unified_master_report_v3(report_type=None, save_to_file=True):
    """Main function to generate unified master report V3"""
    today = date.today()

    if not report_type:
        report_type = detect_report_type()

    print("\n" + "=" * 70)
    print("LOADING ALL 8 ACCOUNT DATA (V3 — Template-Based Reports)")
    print("=" * 70)

    loader = OpenPositionsLoaderV2()
    open_positions, prices = loader.load_all_data()

    position_summary = loader.get_position_summary()
    account_summary = loader.get_account_summary()
    type_summary = loader.get_account_type_summary()

    # Generate report
    output = ""
    if report_type == 'DAILY':
        output = generate_daily_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary)
    elif report_type == 'WEEKLY':
        output = generate_weekly_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary)
    elif report_type == 'BIWEEKLY':
        output = generate_biweekly_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary)
    elif report_type == 'MONTHLY':
        output = generate_monthly_report_v3(today, open_positions, prices, position_summary, account_summary, type_summary)

    # Save
    output_file = None
    if save_to_file:
        output_file = f"logs/unified_master_report_{today.isoformat()}_{report_type.lower()}_v3.txt"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"\n✓ Report saved to: {output_file}")

    print("=" * 70 + "\n")

    return {
        "text": output,
        "type": report_type,
        "saved_to": output_file
    }


async def generate_all_reports_v3():
    """Generate all 4 report types at once (DAILY, WEEKLY, BIWEEKLY, MONTHLY)"""
    print("\n" + "=" * 80)
    print("GENERATING ALL 4 REPORT TYPES WITH TEMPLATE SECTIONS")
    print("=" * 80 + "\n")

    results = {}
    for report_type in ['DAILY', 'WEEKLY', 'BIWEEKLY', 'MONTHLY']:
        print(f"Generating {report_type} report...")
        result = await generate_unified_master_report_v3(report_type=report_type, save_to_file=True)
        results[report_type] = result
        print(f"  ✓ {report_type} report: {result['saved_to']}\n")

    print("=" * 80)
    print("ALL REPORTS GENERATED SUCCESSFULLY")
    print("=" * 80)
    print("\nGenerated files:")
    for report_type, result in results.items():
        print(f"  • {report_type:10}: {result['saved_to']}")

    return results


if __name__ == '__main__':
    import asyncio

    # Generate all 4 report types
    asyncio.run(generate_all_reports_v3())
