"""
India Stock-List Review — regime-filtered scan of the `indian-stock-list.xlsx`
market-watch export, cross-referenced against actual current India holdings
(equity + F&O). Mirrors the style of scripts/portfolio1_monthly_review.py for
the US side, adapted for how this trader actually operates in India: staged
EQUITY accumulation at target entry zones (per skills/options-trader's India
section and data/india_config.yaml's watchlist), not individual-stock options
selling — India F&O activity here is index-level only (NIFTY/BANKNIFTY/
NIFSEL), confirmed by the currently-open F&O legs, so there's no IV-rank/
options-yield check here the way there is for the US scanner; the entry
criterion is 52-week-range positioning + RSI, matching the India weekly
report's own conviction methodology.

Source: newest `indian-stock-list*.xlsx` found in data/statements/.
"""
import sys
import glob
import os
from datetime import date

import pandas as pd
import yfinance as yf

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/analysis')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')

from india_statement_parser import parse_equity_positions, parse_fno_positions
from report_utils import _INDIA_SYMBOL_MAP

# Reverse lookup (Yahoo ticker -> ICICI code) so a watchlist row using the
# standard NSE symbol (e.g. "HDFCBANK") can be matched against ICICI's own
# internal transaction-history code for the same stock (e.g. "HDFBAN") —
# these are frequently NOT the same string (confirmed: ADAPOR/ADANIPORTS,
# HDFBAN/HDFCBANK, LEMTRE/LEMONTREE, ZOMLIM/ETERNAL all differ), so a plain
# exact-string match against held equity would silently miss most real
# holdings.
_YAHOO_TO_ICICI = {v.replace(".NS", ""): k for k, v in _INDIA_SYMBOL_MAP.items()}

STATEMENTS_DIR = '/home/rahulvadera/projects/theta-lab/data/statements'
LOGS_DIR = '/home/rahulvadera/projects/theta-lab/logs'


def find_latest_stock_list():
    files = glob.glob(os.path.join(STATEMENTS_DIR, 'indian-stock-list*.xlsx'))
    if not files:
        raise FileNotFoundError(f"No 'indian-stock-list*.xlsx' found in {STATEMENTS_DIR}")
    return max(files, key=os.path.getmtime)


def load_watchlist(path):
    df = pd.read_excel(path, sheet_name=0)
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()
    # File alternates data row / "NSE"-only exchange-label row
    df = df[df["Scrip Name"] != "NSE"].copy()
    df = df[df["Scrip Name"].notna() & (df["Scrip Name"] != "nan")]
    return df[["Scrip Name", "LTP", "% Change", "High", "Low"]].reset_index(drop=True)


def scan_technicals(scrips):
    rows = []
    for scrip in scrips:
        yahoo_ticker = f"{scrip}.NS"
        try:
            yft = yf.Ticker(yahoo_ticker)
            hist = yft.history(period="1y", auto_adjust=False)
            if hist is None or hist.empty:
                rows.append({"scrip": scrip, "yahoo_ticker": yahoo_ticker, "error": "no_history"})
                continue
            closes = hist['Close']
            current = float(closes.iloc[-1])
            wk_high, wk_low = float(closes.max()), float(closes.min())
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

            rows.append({
                "scrip": scrip, "yahoo_ticker": yahoo_ticker, "price": round(current, 2),
                "pos_in_range": round(pos_in_range, 1), "rsi": round(rsi, 1),
                "sector": info.get("sector", "Unknown"), "pe": info.get("trailingPE"),
            })
        except Exception as e:
            rows.append({"scrip": scrip, "yahoo_ticker": yahoo_ticker, "error": str(e)})
    return pd.DataFrame(rows)


def classify(row):
    if row.get("error"):
        return "Unverified", "🟡", f"Data error: {row['error']}"
    pos_range, rsi = row.get("pos_in_range"), row.get("rsi")
    if pos_range is None or pd.isna(pos_range):
        return "Unverified", "🟡", "No range data"
    if pos_range < 20 and rsi is not None and rsi < 40:
        return "Strong entry candidate", "✅", f"Near 52w low ({pos_range:.0f}% range) AND oversold (RSI {rsi:.0f})"
    if pos_range < 25:
        return "Watch — cheap by range", "🟡", f"Bottom-quartile range ({pos_range:.0f}%) but RSI {rsi:.0f} not confirming oversold"
    if pos_range > 85:
        return "Avoid — extended", "❌", f"Near 52w high ({pos_range:.0f}% range)"
    return "Neutral — no signal", "⚪", f"{pos_range:.0f}% of range, RSI {rsi:.0f} — mid-range, no clear entry signal"


def main():
    src = find_latest_stock_list()
    print(f"Source: {src}")
    watchlist = load_watchlist(src)
    print(f"Watchlist size: {len(watchlist)} names")

    tech = scan_technicals(watchlist["Scrip Name"].tolist())
    merged = watchlist.merge(tech, left_on="Scrip Name", right_on="scrip", how="left")

    print("\n=== Loading current India holdings (equity + F&O) ===")
    equity_holdings = parse_equity_positions()
    fno_positions = parse_fno_positions()
    fno_underlyings = {p["underlying"] for p in fno_positions if p.get("underlying")}
    print(f"Equity holdings: {list(equity_holdings.keys())}")
    print(f"F&O underlyings (open): {sorted(fno_underlyings)}")

    def held_via_mapping(scrip, held_codes):
        # Direct match (some ICICI codes ARE the standard NSE symbol, e.g.
        # LUPIN, NTPC, TCS, TRENT) OR reverse-mapped match (most aren't).
        if scrip in held_codes:
            return True
        icici_code = _YAHOO_TO_ICICI.get(scrip)
        return icici_code in held_codes if icici_code else False

    merged["held_equity"] = merged["Scrip Name"].apply(lambda s: held_via_mapping(s, equity_holdings.keys()))
    merged["held_fno"] = merged["Scrip Name"].apply(lambda s: held_via_mapping(s, fno_underlyings))

    results = []
    for _, row in merged.iterrows():
        strategy, verdict, reason = classify(row.to_dict())
        results.append({
            "scrip": row["Scrip Name"], "price": row.get("price"), "sector": row.get("sector"),
            "pos_in_range": row.get("pos_in_range"), "rsi": row.get("rsi"),
            "held_equity": row["held_equity"], "held_fno": row["held_fno"],
            "strategy": strategy, "verdict": verdict, "reason": reason,
        })
    results_df = pd.DataFrame(results).sort_values("pos_in_range", na_position="last")
    results_df.to_csv(os.path.join(LOGS_DIR, '_india_stock_list_merged.csv'), index=False)

    today_str = date.today().isoformat()
    lines = []
    lines.append(f"# India Stock-List Review — {today_str} ({len(watchlist)} names)")
    lines.append("")
    lines.append(f"**Source:** `{os.path.basename(src)}`. Cross-referenced against actual current "
                  f"equity holdings + open F&O underlyings. Entry criterion is 52-week-range "
                  f"positioning + RSI (this trader's India strategy is staged equity accumulation "
                  f"at target entry zones, not individual-stock options selling — India F&O activity "
                  f"here is index-level only, so there is no IV-rank/options-yield check as there is "
                  f"on the US scanner.")
    lines.append("")
    lines.append("**Symbol-matching:** held-status uses `report_utils.py`'s `_INDIA_SYMBOL_MAP` "
                  "(ICICI transaction code -> standard NSE ticker) with a reverse lookup, since ICICI's "
                  "own codes frequently differ from the standard symbol (e.g. `HDFBAN`/HDFCBANK, "
                  "`LEMTRE`/LEMONTREE, `ZOMLIM`/ETERNAL) — plain exact-string matching would silently "
                  "miss most real holdings. A stock held under a code NOT yet in that map would still "
                  "be missed here; add it to `_INDIA_SYMBOL_MAP` if a held-status result looks wrong.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Full Scan Results")
    lines.append("")
    lines.append("| Scrip | Price | Sector | 52w Range % | RSI | Held (equity/F&O) | Verdict | Reason |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for _, r in results_df.iterrows():
        held = []
        if r['held_equity']:
            held.append("equity")
        if r['held_fno']:
            held.append("F&O")
        held_str = "/".join(held) if held else "not held"
        pos_r = f"{r['pos_in_range']:.0f}%" if pd.notna(r['pos_in_range']) else "n/a"
        rsi_r = f"{r['rsi']:.0f}" if pd.notna(r['rsi']) else "n/a"
        lines.append(f"| {r['scrip']} | {r['price']} | {r['sector']} | {pos_r} | {rsi_r} | {held_str} | {r['verdict']} | {r['reason']} |")
    lines.append("")

    report_path = os.path.join(LOGS_DIR, f'india_stock_list_review_{today_str}.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"\nReport written to {report_path}")


if __name__ == '__main__':
    main()
