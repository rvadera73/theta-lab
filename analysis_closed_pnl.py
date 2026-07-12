#!/usr/bin/env python3
"""
Comprehensive closed P&L analysis across all accounts.
Matches Sell to Open with Buy to Close to find realized P&L.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

def parse_schwab_symbol(symbol_str):
    """
    Parse Schwab symbol format: "SYMBOL MM/DD/YYYY strike.00 P/C"
    Returns: (symbol, expiry_date, strike, option_type)
    """
    if pd.isna(symbol_str):
        return None, None, None, None

    parts = symbol_str.split()
    if len(parts) < 4:
        return None, None, None, None

    symbol = parts[0]

    # Date is in MM/DD/YYYY format
    try:
        expiry = pd.to_datetime(parts[1], format="%m/%d/%Y")
    except:
        return None, None, None, None

    strike = float(parts[2])
    option_type = parts[3].strip()  # P or C

    return symbol, expiry, strike, option_type

def load_and_parse_schwab(file_path):
    """Load Schwab CSV and parse option details."""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.strip('"')

    # Clean up data
    df['Date'] = pd.to_datetime(df['Date'].str.split(' as of ').str[0].str.strip())
    df['Amount'] = df['Amount'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Price'] = df['Price'].str.replace('$', '').replace('', '0').astype(float)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0).astype(int)
    df['Fees & Comm'] = df['Fees & Comm'].str.replace('$', '').astype(float)

    # Parse symbol column
    parsed = df['Symbol'].apply(parse_schwab_symbol)
    df['ParsedSymbol'] = parsed.apply(lambda x: x[0])
    df['Expiry'] = parsed.apply(lambda x: x[1])
    df['Strike'] = parsed.apply(lambda x: x[2])
    df['OptionType'] = parsed.apply(lambda x: x[3])

    return df

def find_closed_trades(df, account_name):
    """
    Find matched pairs of Sell to Open + Buy to Close trades.
    Returns list of closed trades with P&L.
    """
    closed_trades = []

    # Group by symbol + strike + expiry + option_type
    for key, group in df.groupby(['ParsedSymbol', 'Strike', 'Expiry', 'OptionType']):
        if key[0] is None:
            continue

        group = group.sort_values('Date').reset_index(drop=True)

        # Track sells and buys
        for i in range(len(group)):
            if 'Sell to Open' not in group.iloc[i]['Action']:
                continue

            sell_row = group.iloc[i]
            sell_date = sell_row['Date']
            sell_price = sell_row['Price']
            sell_qty = sell_row['Quantity']
            sell_premium = sell_row['Amount']
            sell_fees = sell_row['Fees & Comm']

            # Find matching buy to close
            for j in range(i + 1, len(group)):
                if 'Buy to Close' not in group.iloc[j]['Action']:
                    continue

                buy_row = group.iloc[j]
                buy_date = buy_row['Date']
                buy_price = buy_row['Price']
                buy_qty = buy_row['Quantity']
                buy_cost = abs(buy_row['Amount'])
                buy_fees = buy_row['Fees & Comm']

                # Calculate P&L
                # P&L = Premium received - Cost to close - Fees
                gross_pnl = sell_premium - buy_cost
                net_pnl = gross_pnl - (sell_fees + buy_fees)

                closed_trades.append({
                    'Account': account_name,
                    'Symbol': key[0],
                    'OptionType': key[3],
                    'Strike': key[2],
                    'Expiry': key[1],
                    'OpenDate': sell_date,
                    'CloseDate': buy_date,
                    'DaysHeld': (buy_date - sell_date).days,
                    'OpenPrice': sell_price,
                    'ClosePrice': buy_price,
                    'Premium': sell_premium,
                    'BuyToCost': buy_cost,
                    'Fees': sell_fees + buy_fees,
                    'GrossP&L': gross_pnl,
                    'NetP&L': net_pnl,
                    'OpenQty': sell_qty,
                    'CloseQty': buy_qty,
                })
                break

    return closed_trades

def parse_fidelity_symbol(description):
    """
    Parse Fidelity description for option details.
    Format: "YOU SOLD OPENING TRANSACTION PUT (SYMBOL) COMPANY JAN 15 27 $STRIKE"
    """
    if pd.isna(description):
        return None, None, None, None

    # Determine option type
    if 'PUT' in description:
        option_type = 'P'
    elif 'CALL' in description:
        option_type = 'C'
    else:
        return None, None, None, None

    # Extract symbol from parentheses
    symbol_match = re.search(r'\(([A-Z][A-Z0-9]*)\)', description)
    symbol = symbol_match.group(1) if symbol_match else None

    # Extract strike
    strike_match = re.search(r'\$([0-9.]+)\s*\(', description)
    strike = float(strike_match.group(1)) if strike_match else None

    # Extract expiry - look for month abbreviations
    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }

    expiry = None
    for month_str, month_num in month_map.items():
        if month_str in description:
            # Extract day and year
            day_year_match = re.search(rf'{month_str}\s+(\d+)\s+(\d{{2}})', description)
            if day_year_match:
                day = int(day_year_match.group(1))
                year = 2000 + int(day_year_match.group(2))
                try:
                    expiry = pd.to_datetime(f"{month_num:02d}/{day:02d}/{year}", format="%m/%d/%Y")
                    break
                except:
                    pass

    return symbol, expiry, strike, option_type

def load_and_parse_fidelity(file_path):
    """Load Fidelity CSV and parse option details."""
    df = pd.read_csv(file_path, skiprows=2)
    df.columns = df.columns.str.strip()

    # Filter to options transactions only
    df = df[df['Action'].str.contains('PUT|CALL', case=False, na=False)].copy()

    df['Run Date'] = pd.to_datetime(df['Run Date'])
    df['Amount ($)'] = pd.to_numeric(df['Amount ($)'], errors='coerce')
    df['Price ($)'] = pd.to_numeric(df['Price ($)'], errors='coerce')
    df['Commission ($)'] = pd.to_numeric(df['Commission ($)'], errors='coerce').fillna(0)
    df['Fees ($)'] = pd.to_numeric(df['Fees ($)'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').astype(int)

    # Parse description
    parsed = df['Description'].apply(parse_fidelity_symbol)
    df['ParsedSymbol'] = parsed.apply(lambda x: x[0])
    df['Expiry'] = parsed.apply(lambda x: x[1])
    df['Strike'] = parsed.apply(lambda x: x[2])
    df['OptionType'] = parsed.apply(lambda x: x[3])

    return df

def find_closed_trades_fidelity(df, account_name):
    """
    Find matched pairs for Fidelity account.
    """
    closed_trades = []

    for key, group in df.groupby(['ParsedSymbol', 'Strike', 'Expiry', 'OptionType']):
        if key[0] is None:
            continue

        group = group.sort_values('Run Date').reset_index(drop=True)

        for i in range(len(group)):
            if 'SOLD' not in group.iloc[i]['Action'].upper():
                continue

            sell_row = group.iloc[i]
            sell_date = sell_row['Run Date']
            sell_price = abs(sell_row['Price ($)'])
            sell_qty = abs(sell_row['Quantity'])
            sell_amount = sell_row['Amount ($)']
            sell_fees = sell_row['Commission ($)'] + sell_row['Fees ($)']

            # Find matching buy to close
            for j in range(i + 1, len(group)):
                if 'BOUGHT' not in group.iloc[j]['Action'].upper():
                    continue

                buy_row = group.iloc[j]
                buy_date = buy_row['Run Date']
                buy_price = abs(buy_row['Price ($)'])
                buy_qty = abs(buy_row['Quantity'])
                buy_amount = abs(buy_row['Amount ($)'])
                buy_fees = buy_row['Commission ($)'] + buy_row['Fees ($)']

                # Calculate P&L
                gross_pnl = sell_amount - buy_amount
                net_pnl = gross_pnl - (sell_fees + buy_fees)

                closed_trades.append({
                    'Account': account_name,
                    'Symbol': key[0],
                    'OptionType': key[3],
                    'Strike': key[2],
                    'Expiry': key[1],
                    'OpenDate': sell_date,
                    'CloseDate': buy_date,
                    'DaysHeld': (buy_date - sell_date).days,
                    'OpenPrice': sell_price,
                    'ClosePrice': buy_price,
                    'Premium': sell_amount,
                    'BuyToCost': buy_amount,
                    'Fees': sell_fees + buy_fees,
                    'GrossP&L': gross_pnl,
                    'NetP&L': net_pnl,
                    'OpenQty': sell_qty,
                    'CloseQty': buy_qty,
                })
                break

    return closed_trades

def assign_conviction_level(symbol, dates, pnl_values):
    """
    Assign conviction level based on trade history.
    High (8-10): Multiple trades same ticker, held through rolls
    Medium (6-8): 2-3 trades, repeating patterns
    Low (4-6): Single entry, one-off trades
    """
    # Count trades in same symbol
    symbol_count = len(dates)

    if symbol_count >= 4:
        return 'High'
    elif symbol_count >= 2:
        return 'Medium'
    else:
        return 'Low'

def estimate_market_regime(date):
    """
    Estimate market regime based on date.
    April-May 2026: CAUTIOUS_BULL
    """
    if pd.to_datetime('2026-04-01') <= date <= pd.to_datetime('2026-05-31'):
        return 'CAUTIOUS_BULL'
    elif pd.to_datetime('2026-01-01') <= date < pd.to_datetime('2026-04-01'):
        return 'EARLY_BULL'
    elif pd.to_datetime('2026-06-01') <= date <= pd.to_datetime('2026-06-09'):
        return 'LATE_BULL'
    else:
        return 'UNKNOWN'

def main():
    data_path = '/home/rahulvadera/projects/theta-lab/data/positions/'

    all_closed_trades = []

    # Schwab accounts
    schwab_files = [
        ('Individual_XXX232_Transactions_20260609-135608.csv', 'Account A'),
        ('Contributory_XXX275_Transactions_20260530-161127.csv', 'Account B'),
        ('Designated_Bene_Individual_XXX634_Transactions_20260530-161206.csv', 'Account C'),
    ]

    for file, account_name in schwab_files:
        try:
            df = load_and_parse_schwab(data_path + file)
            closed = find_closed_trades(df, account_name)
            all_closed_trades.extend(closed)
            print(f"✓ {account_name}: {len(closed)} closed trades")
        except Exception as e:
            print(f"✗ {account_name}: {e}")

    # Fidelity accounts
    fidelity_files = [
        ('Accounts_History -Fidelity-Rahul.csv', 'Fidelity Rahul'),
        ('Accounts_History-Rajul.csv', 'Fidelity Rajul'),
    ]

    for file, account_name in fidelity_files:
        try:
            df = load_and_parse_fidelity(data_path + file)
            closed = find_closed_trades_fidelity(df, account_name)
            all_closed_trades.extend(closed)
            print(f"✓ {account_name}: {len(closed)} closed trades")
        except Exception as e:
            print(f"✗ {account_name}: {e}")

    if not all_closed_trades:
        print("\nNo closed trades found!")
        return

    # Create results DataFrame
    results_df = pd.DataFrame(all_closed_trades)
    results_df['Month'] = results_df['OpenDate'].dt.to_period('M')
    results_df['Regime'] = results_df['OpenDate'].apply(estimate_market_regime)

    # Assign conviction
    conviction_map = {}
    for symbol in results_df['Symbol'].unique():
        symbol_df = results_df[results_df['Symbol'] == symbol]
        conviction = assign_conviction_level(
            symbol,
            symbol_df['OpenDate'].values,
            symbol_df['NetP&L'].values
        )
        conviction_map[symbol] = conviction

    results_df['Conviction'] = results_df['Symbol'].map(conviction_map)

    # Calculate position type (for now: puts are puts, calls are calls)
    results_df['PositionType'] = results_df['OptionType'].apply(
        lambda x: 'Put' if x == 'P' else 'Call'
    )

    # Determine win/loss
    results_df['Result'] = results_df['NetP&L'].apply(
        lambda x: 'Win' if x > 200 else 'Loss' if x < -100 else 'Breakeven'
    )

    # Save detailed results
    results_df.to_csv('/home/rahulvadera/projects/theta-lab/analysis/closed_pnl_detail.csv', index=False)

    print("\n" + "="*60)
    print("CLOSED P&L ANALYSIS: Jan 1 - June 9, 2026")
    print("="*60)

    print(f"\nTOTAL STATISTICS:")
    print(f"  Total closed trades: {len(results_df)}")
    print(f"  Total net P&L: ${results_df['NetP&L'].sum():,.2f}")
    print(f"  Average P&L per trade: ${results_df['NetP&L'].mean():,.2f}")
    print(f"  Median P&L per trade: ${results_df['NetP&L'].median():,.2f}")
    print(f"  Win rate: {(results_df['NetP&L'] > 0).sum() / len(results_df) * 100:.1f}%")
    print(f"  Total fees paid: ${results_df['Fees'].sum():,.2f}")

    print(f"\nWIN/LOSS BREAKDOWN:")
    print(f"  Winners (>$200): {(results_df['NetP&L'] > 200).sum()} trades ({(results_df['NetP&L'] > 200).sum() / len(results_df) * 100:.1f}%)")
    print(f"    Avg: ${results_df[results_df['NetP&L'] > 200]['NetP&L'].mean():.2f}")
    print(f"  Losers (<-$100): {(results_df['NetP&L'] < -100).sum()} trades ({(results_df['NetP&L'] < -100).sum() / len(results_df) * 100:.1f}%)")
    print(f"    Avg: ${results_df[results_df['NetP&L'] < -100]['NetP&L'].mean():.2f}")
    print(f"  Breakeven: {(results_df['Result'] == 'Breakeven').sum()} trades ({(results_df['Result'] == 'Breakeven').sum() / len(results_df) * 100:.1f}%)")

    print(f"\nBY POSITION TYPE:")
    for pos_type in results_df['PositionType'].unique():
        subset = results_df[results_df['PositionType'] == pos_type]
        win_rate = (subset['NetP&L'] > 0).sum() / len(subset) * 100
        print(f"\n  {pos_type}:")
        print(f"    Count: {len(subset)}")
        print(f"    Total P&L: ${subset['NetP&L'].sum():,.2f}")
        print(f"    Avg P&L: ${subset['NetP&L'].mean():,.2f}")
        print(f"    Win rate: {win_rate:.1f}%")

    print(f"\nBY CONVICTION LEVEL:")
    for conviction in ['High', 'Medium', 'Low']:
        subset = results_df[results_df['Conviction'] == conviction]
        if len(subset) == 0:
            continue
        win_rate = (subset['NetP&L'] > 0).sum() / len(subset) * 100
        print(f"\n  {conviction} Conviction:")
        print(f"    Count: {len(subset)}")
        print(f"    Total P&L: ${subset['NetP&L'].sum():,.2f}")
        print(f"    Monthly avg: ${subset['NetP&L'].sum() / 6:.2f}")
        print(f"    Avg P&L per trade: ${subset['NetP&L'].mean():,.2f}")
        print(f"    Win rate: {win_rate:.1f}%")

    print(f"\nBY ACCOUNT:")
    for account in sorted(results_df['Account'].unique()):
        subset = results_df[results_df['Account'] == account]
        win_rate = (subset['NetP&L'] > 0).sum() / len(subset) * 100 if len(subset) > 0 else 0
        print(f"\n  {account}:")
        print(f"    Trades: {len(subset)}")
        print(f"    Total P&L: ${subset['NetP&L'].sum():,.2f}")
        print(f"    Avg P&L: ${subset['NetP&L'].mean():,.2f}")
        print(f"    Win rate: {win_rate:.1f}%")

    print(f"\nBY MONTH:")
    for month in sorted(results_df['Month'].unique()):
        subset = results_df[results_df['Month'] == month]
        print(f"\n  {month}:")
        print(f"    Trades: {len(subset)}")
        print(f"    P&L: ${subset['NetP&L'].sum():,.2f}")
        print(f"    Win rate: {(subset['NetP&L'] > 0).sum() / len(subset) * 100:.1f}%")

    print(f"\nBY REGIME:")
    for regime in sorted(results_df['Regime'].unique()):
        subset = results_df[results_df['Regime'] == regime]
        print(f"\n  {regime}:")
        print(f"    Trades: {len(subset)}")
        print(f"    P&L: ${subset['NetP&L'].sum():,.2f}")
        print(f"    Win rate: {(subset['NetP&L'] > 0).sum() / len(subset) * 100:.1f}%")

    print(f"\nTOP 10 WINNERS:")
    top_winners = results_df.nlargest(10, 'NetP&L')[['OpenDate', 'Symbol', 'PositionType', 'Strike', 'Conviction', 'NetP&L', 'Account']]
    for idx, row in top_winners.iterrows():
        print(f"  {row['OpenDate'].strftime('%m/%d')}: {row['Symbol']} {row['PositionType']} ${row['Strike']} - {row['Conviction']} - ${row['NetP&L']:.2f}")

    print(f"\nTOP 10 LOSERS:")
    top_losers = results_df.nsmallest(10, 'NetP&L')[['OpenDate', 'Symbol', 'PositionType', 'Strike', 'Conviction', 'NetP&L', 'Account']]
    for idx, row in top_losers.iterrows():
        print(f"  {row['OpenDate'].strftime('%m/%d')}: {row['Symbol']} {row['PositionType']} ${row['Strike']} - {row['Conviction']} - ${row['NetP&L']:.2f}")

if __name__ == '__main__':
    main()
