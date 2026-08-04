"""
Backtest the VIX regime / RSI entry thresholds against actual closed trades
from Account A's transaction history (the same account + methodology the
existing PROFIT_TARGETS/DTE_TARGETS comments cite: "195 matched trades").

For GitHub issue #1 (theta-lab): recalibrate config.py thresholds that were
plausible textbook levels but never checked against this account's own data.
"""
import sys
import re
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')
from enhanced_metrics import TechnicalIndicators

TXN_FILE = '/home/rahulvadera/projects/theta-lab/data/positions/Individual_XXX232_Transactions_20260712-111304.csv'


def parse_schwab_symbol(symbol_str):
    if pd.isna(symbol_str):
        return None, None, None, None
    parts = str(symbol_str).split()
    if len(parts) < 4:
        return None, None, None, None
    symbol = parts[0]
    try:
        expiry = pd.to_datetime(parts[1], format="%m/%d/%Y")
    except Exception:
        return None, None, None, None
    try:
        strike = float(parts[2])
    except Exception:
        return None, None, None, None
    option_type = parts[3].strip()
    return symbol, expiry, strike, option_type


def load_txns(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.strip('"')
    df['Date'] = pd.to_datetime(df['Date'].astype(str).str.split(' as of ').str[0].str.strip(), errors='coerce')
    df['Amount'] = df['Amount'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    parsed = df['Symbol'].apply(parse_schwab_symbol)
    df['ParsedSymbol'] = parsed.apply(lambda x: x[0])
    df['Expiry'] = parsed.apply(lambda x: x[1])
    df['Strike'] = parsed.apply(lambda x: x[2])
    df['OptionType'] = parsed.apply(lambda x: x[3])
    return df


def find_closed_trades(df):
    closed = []
    for key, group in df.groupby(['ParsedSymbol', 'Strike', 'Expiry', 'OptionType']):
        if key[0] is None:
            continue
        group = group.sort_values('Date').reset_index(drop=True)
        for i in range(len(group)):
            action_i = str(group.iloc[i].get('Action', ''))
            if 'Sell to Open' not in action_i:
                continue
            sell_row = group.iloc[i]
            for j in range(i + 1, len(group)):
                action_j = str(group.iloc[j].get('Action', ''))
                if 'Buy to Close' not in action_j:
                    continue
                buy_row = group.iloc[j]
                premium = sell_row['Amount']
                cost = abs(buy_row['Amount'])
                if pd.isna(premium) or pd.isna(cost) or premium <= 0:
                    break
                net_pnl = premium - cost
                profit_pct = net_pnl / premium
                closed.append({
                    'Symbol': key[0], 'OptionType': key[3], 'Strike': key[2],
                    'OpenDate': sell_row['Date'], 'CloseDate': buy_row['Date'],
                    'DaysHeld': (buy_row['Date'] - sell_row['Date']).days,
                    'Premium': premium, 'Cost': cost, 'NetPnL': net_pnl,
                    'ProfitPct': profit_pct,
                })
                break
    return pd.DataFrame(closed)


def main():
    df = load_txns(TXN_FILE)
    trades = find_closed_trades(df)
    trades = trades.dropna(subset=['OpenDate', 'CloseDate'])
    print(f"Matched closed trades: {len(trades)}")
    if trades.empty:
        return

    win_rate = (trades['ProfitPct'] > 0).mean()
    print(f"Overall win rate: {win_rate:.1%} | Median profit%: {trades['ProfitPct'].median():.1%} | "
          f"Mean profit%: {trades['ProfitPct'].mean():.1%} | Median DaysHeld: {trades['DaysHeld'].median():.0f}")

    # --- VIX at entry ---
    min_d, max_d = trades['OpenDate'].min() - pd.Timedelta(days=5), trades['OpenDate'].max() + pd.Timedelta(days=5)
    vix_hist = yf.Ticker('^VIX').history(start=min_d.date(), end=max_d.date())
    vix_hist.index = vix_hist.index.tz_localize(None)

    def vix_on(d):
        idx = vix_hist.index[vix_hist.index <= d]
        if len(idx) == 0:
            return np.nan
        return float(vix_hist.loc[idx[-1], 'Close'])

    trades['VIX'] = trades['OpenDate'].apply(vix_on)

    def vix_bucket(v):
        if pd.isna(v):
            return 'unknown'
        if v < 20:
            return '<20 (bull)'
        if v < 35:
            return '20-35 (pause zone)'
        return '>35 (pause)'

    trades['VIXBucket'] = trades['VIX'].apply(vix_bucket)
    print("\n=== By VIX-at-entry bucket (current thresholds: 20.0 / 35.0) ===")
    print(trades.groupby('VIXBucket')['ProfitPct'].agg(['count', 'mean', 'median',
                                                          lambda s: (s > 0).mean()]).rename(
        columns={'<lambda_0>': 'win_rate'}))

    # --- RSI of underlying at entry ---
    symbols = trades['Symbol'].dropna().unique().tolist()
    hist_cache = {}
    for sym in symbols:
        try:
            h = yf.Ticker(sym).history(period='2y', auto_adjust=False)
            if h is not None and not h.empty:
                h.index = h.index.tz_localize(None)
                hist_cache[sym] = h['Close']
        except Exception:
            pass

    def rsi_on(sym, d):
        closes = hist_cache.get(sym)
        if closes is None:
            return np.nan
        sub = closes[closes.index <= d]
        if len(sub) < 15:
            return np.nan
        return TechnicalIndicators.rsi(sub)

    trades['RSI'] = trades.apply(lambda r: rsi_on(r['Symbol'], r['OpenDate']), axis=1)

    def rsi_bucket(v):
        if pd.isna(v):
            return 'unknown'
        if v < 30:
            return '<30 (oversold)'
        if v > 70:
            return '>70 (overbought)'
        return '30-70 (neutral)'

    trades['RSIBucket'] = trades['RSI'].apply(rsi_bucket)
    print("\n=== By underlying-RSI-at-entry bucket (current thresholds: 30 / 70) ===")
    print(trades.groupby('RSIBucket')['ProfitPct'].agg(['count', 'mean', 'median',
                                                          lambda s: (s > 0).mean()]).rename(
        columns={'<lambda_0>': 'win_rate'}))

    print("\n=== By RSI bucket, split by option type (avoids conflating put/call meaning) ===")
    print(trades.groupby(['OptionType', 'RSIBucket'])['ProfitPct'].agg(
        ['count', 'mean', 'median', lambda s: (s > 0).mean()]).rename(columns={'<lambda_0>': 'win_rate'}))

    trades.to_csv('/home/rahulvadera/projects/theta-lab/logs/backtest_closed_trades_2026-07-31.csv', index=False)
    print("\nSaved raw trade-level data to logs/backtest_closed_trades_2026-07-31.csv")


if __name__ == '__main__':
    main()
