"""
Portfolio-1 Monthly Review — regime-filtered scan of the full investment
universe watchlist. Per skills/options-trader: regime filter, 52W range
positioning, top-5 deployment candidates, remove-list.

Source: newest Portfolio-1 export found. IV rank uses the live theta-lab
analysis module directly (same function the MCP tool wraps) to batch all
tickers in one process instead of one MCP round-trip per ticker.
"""
import sys
import json
import pandas as pd
import yfinance as yf

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/analysis')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')

from config import UNIVERSE, Tier, PERMANENT_EXITS
from iv_rank import batch_iv_rank

SRC = '/home/rahulvadera/projects/theta-lab/data/positions/arch/Portfolio-1 2026-06-26 (1).xlsx'

TIER_MAP = {}
for tier, names in UNIVERSE.items():
    for n in names:
        TIER_MAP[n] = tier.name

xl = pd.ExcelFile(SRC, engine='calamine')
summary = xl.parse('Summary')
tickers = [str(t).strip() for t in summary['Symbol'].dropna().unique() if str(t).strip()]
print(f"Universe size: {len(tickers)}")

rows = []
for i, t in enumerate(tickers):
    try:
        yft = yf.Ticker(t)
        hist = yft.history(period="1y", auto_adjust=False)
        if hist is None or hist.empty:
            rows.append({"ticker": t, "error": "no_history"})
            continue
        closes = hist['Close']
        current = float(closes.iloc[-1])
        wk_high = float(closes.max())
        wk_low = float(closes.min())
        pos_in_range = ((current - wk_low) / (wk_high - wk_low) * 100) if wk_high > wk_low else 50.0

        delta = closes.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if loss.iloc[-1] not in (0, None) else 50.0

        info = {}
        try:
            info = yft.info or {}
        except Exception:
            pass
        sector = info.get('sector', 'Unknown')
        pe = info.get('trailingPE')

        rows.append({
            "ticker": t, "price": round(current, 2), "wk52_high": round(wk_high, 2),
            "wk52_low": round(wk_low, 2), "pos_in_range": round(pos_in_range, 1),
            "rsi": round(rsi, 1), "sector": sector, "pe": pe,
            "tier": TIER_MAP.get(t, "Unmapped"),
            "permanent_exit": t in PERMANENT_EXITS,
        })
    except Exception as e:
        rows.append({"ticker": t, "error": str(e)})
    if (i + 1) % 15 == 0:
        print(f"  ...{i+1}/{len(tickers)} done", file=sys.stderr)

df = pd.DataFrame(rows)
df.to_csv('/home/rahulvadera/projects/theta-lab/logs/_p1_technicals_raw.csv', index=False)

print("\n=== IV RANK (batched) ===")
valid_tickers = [r['ticker'] for r in rows if 'error' not in r]
ivr = batch_iv_rank(valid_tickers)
ivr_rows = []
for t, d in ivr.items():
    ivr_rows.append({"ticker": t, "ivr": d.get("iv_rank"), "entry_ok": d.get("entry_signal")})
ivr_df = pd.DataFrame(ivr_rows)
ivr_df.to_csv('/home/rahulvadera/projects/theta-lab/logs/_p1_ivr_raw.csv', index=False)

merged = df.merge(ivr_df, on='ticker', how='left')
merged.to_csv('/home/rahulvadera/projects/theta-lab/logs/_p1_merged.csv', index=False)
print("\nSaved merged data. Rows:", len(merged))
print(merged.sort_values('pos_in_range').head(20).to_string())
