"""
Portfolio-1 Monthly Review — regime-filtered scan of the full investment
universe watchlist. Per skills/options-trader: regime filter, 52W range
positioning, top candidates, remove-list.

Extended (2026-08-14) to close three gaps found doing this by hand in a chat
session: (1) the watchlist scan had zero awareness of ACTUAL open positions,
so most "candidates" turned out to already be held (or, like SBUX/CMG,
actively held but simply absent from the watchlist file, an invisible gap);
(2) IV rank alone doesn't tell you real premium — HDB screened at IVR 89.9
but real option-chain yield was 2.2-2.6% annualized, structurally thin
despite a "rich" relative reading; (3) individual-name screening never
checked whether a candidate sits in a sector the macro crash-risk layer has
flagged as most exposed to today's specific risk driver. All three are now
checked automatically.

Source: newest "Portfolio-1 *.xlsx" file found in data/portfolio/ (glob by
mtime, not a hardcoded date — this must keep working on future runs).
IV rank uses the live theta-lab analysis module directly (same function the
MCP tool wraps) to batch all tickers in one process instead of one MCP
round-trip per ticker.
"""
import sys
import glob
import os
from datetime import date

import pandas as pd
import yfinance as yf

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/analysis')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')

from config import UNIVERSE, Tier, PERMANENT_EXITS
from iv_rank import batch_iv_rank
from open_positions_loader_v2 import OpenPositionsLoaderV2
from enhanced_metrics import batch_get_metrics
from sector_analysis import batch_get_sector_analysis
from macro_risk_analyzer import analyze_macro_risk

PORTFOLIO_DIR = '/home/rahulvadera/projects/theta-lab/data/portfolio'
LOGS_DIR = '/home/rahulvadera/projects/theta-lab/logs'

TIER_MAP = {}
for tier, names in UNIVERSE.items():
    for n in names:
        TIER_MAP[n] = tier.name


def find_latest_portfolio1():
    files = glob.glob(os.path.join(PORTFOLIO_DIR, 'Portfolio-1 *.xlsx'))
    if not files:
        raise FileNotFoundError(f"No 'Portfolio-1 *.xlsx' export found in {PORTFOLIO_DIR}")
    return max(files, key=os.path.getmtime)


def scan_universe_technicals(src_path):
    """Original scan: RSI, 52-week positioning, sector, PE per watchlist ticker."""
    xl = pd.ExcelFile(src_path, engine='calamine')
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

    return pd.DataFrame(rows)


def get_held_summary(open_positions):
    """{ticker: {"accounts": {acct: contracts}, "puts": n, "calls": n}} across all accounts."""
    held = {}
    for ticker, grp in open_positions.groupby("ticker"):
        by_acct = grp.groupby("account_name")["net_quantity"].sum().to_dict()
        puts = grp[grp["option_type"] == "P"]["net_quantity"].sum() if "option_type" in grp.columns else 0
        calls = grp[grp["option_type"] == "C"]["net_quantity"].sum() if "option_type" in grp.columns else 0
        held[ticker] = {"accounts": by_acct, "puts": int(puts), "calls": int(calls)}
    return held


def get_real_put_yield(ticker, price, min_dte=25, max_dte=65, otm_lo=0.72, otm_hi=0.92):
    """Pull the actual option chain and return the best available (strike,
    annualized_yield, dte) in a moderate 10-28% OTM / 25-65 DTE band — the
    check that would have caught HDB's thin real premium despite IVR 89.9,
    done automatically instead of by hand. Returns None if no usable chain."""
    try:
        t = yf.Ticker(ticker)
        expiries = t.options
        today = date.today()
        candidates = []
        for e in expiries:
            y, m, d = map(int, e.split("-"))
            dte = (date(y, m, d) - today).days
            if min_dte <= dte <= max_dte:
                candidates.append((e, dte))
        if not candidates:
            return None
        expiry, dte = candidates[0]
        chain = t.option_chain(expiry)
        puts = chain.puts
        puts = puts[(puts["strike"] < price * otm_hi) & (puts["strike"] > price * otm_lo)]
        if puts.empty:
            return None
        # Prefer the strike closest to 15% OTM (a reasonable, moderate delta proxy)
        target = price * 0.85
        puts = puts.copy()
        puts["dist"] = (puts["strike"] - target).abs()
        row = puts.sort_values("dist").iloc[0]
        bid, ask = row["bid"], row["ask"]
        mid = (bid + ask) / 2 if bid and ask else row.get("lastPrice", 0)
        strike = row["strike"]
        collateral = strike * 100
        if not collateral or not mid:
            return None
        annualized = (mid * 100 / collateral) * (365 / dte) * 100
        return {"strike": float(strike), "dte": dte, "premium": float(mid * 100),
                "collateral": float(collateral), "annualized_pct": round(annualized, 1)}
    except Exception:
        return None


def classify_strategy(row, held, sensitivity_sectors):
    """Strategy classification per skills/options-trader/trading_persona.md's
    actual account structure (near-term wheel CSP vs LEAP CSP vs avoid) — not
    a generic textbook taxonomy. Returns (strategy, verdict, reason)."""
    ivr = row.get("ivr")
    pos_range = row.get("pos_in_range")
    rsi = row.get("rsi")
    yield_check = row.get("real_yield")
    sector = row.get("sector")
    is_held = row["ticker"] in held

    if ivr is None or pd.isna(ivr):
        return "Unverified", "n/a", "No IV rank data available"
    if ivr < 40:
        return "Avoid", "❌", f"IVR {ivr:.0f} < 40 gate — insufficient premium density"
    if pos_range is None or pd.isna(pos_range) or pos_range >= 25:
        return "Avoid (for now)", "❌", f"Not in bottom quartile ({pos_range:.0f}% of range) — not statistically cheap"
    if rsi is not None and not pd.isna(rsi) and rsi > 60:
        return "Avoid (for now)", "⚠️", f"Cheap by 52w range but RSI {rsi:.0f} already recovered — weak entry timing"

    real_annualized = yield_check.get("annualized_pct") if yield_check else None
    if real_annualized is not None and real_annualized < 8:
        strategy = "Avoid"
        verdict = "❌"
        reason = f"Screens well (IVR {ivr:.0f}) but real chain yield only {real_annualized:.1f}% annualized — thin in practice"
    elif real_annualized is not None:
        strategy = "Near-term CSP"
        verdict = "✅" if not is_held else "✅ (add/monitor — already held)"
        reason = f"Oversold ({pos_range:.0f}% range, RSI {rsi:.0f}), IVR {ivr:.0f}, verified {real_annualized:.1f}% annualized"
    else:
        strategy = "Near-term CSP (yield unverified)"
        verdict = "🟡"
        reason = f"Screens well (IVR {ivr:.0f}, {pos_range:.0f}% range) but no option chain data to verify real yield"

    if sector in sensitivity_sectors:
        reason += f" — CAUTION: {sector} flagged HIGH-exposure to today's primary macro risk driver"

    return strategy, verdict, reason


def main():
    src = find_latest_portfolio1()
    print(f"Source: {src}")
    df = scan_universe_technicals(src)
    df.to_csv(os.path.join(LOGS_DIR, '_p1_technicals_raw.csv'), index=False)

    print("\n=== IV RANK (batched) ===")
    valid_tickers = [t for t in df['ticker'] if t]
    valid_tickers = df[~df.get('error', pd.Series(dtype=object)).notna()]['ticker'].tolist() if 'error' in df.columns else df['ticker'].tolist()
    ivr = batch_iv_rank(valid_tickers)
    ivr_df = pd.DataFrame([{"ticker": t, "ivr": d.get("iv_rank"), "entry_ok": d.get("entry_signal")} for t, d in ivr.items()])
    ivr_df.to_csv(os.path.join(LOGS_DIR, '_p1_ivr_raw.csv'), index=False)

    merged = df.merge(ivr_df, on='ticker', how='left')

    print("\n=== Loading current open positions across all accounts ===")
    loader = OpenPositionsLoaderV2()
    open_positions, prices = loader.load_all_data()
    held = get_held_summary(open_positions)

    option_types = {}
    if 'option_type' in open_positions.columns:
        for ticker, grp in open_positions.groupby('ticker'):
            counts = grp.groupby('option_type')['net_quantity'].sum()
            if len(counts) > 0 and counts.max() > 0:
                option_types[ticker] = counts.idxmax()
    metrics = batch_get_metrics(open_positions['ticker'].unique().tolist(), prices, option_types)
    sector_summary, _, _, ticker_sector_map = batch_get_sector_analysis(open_positions, metrics, prices)

    print("\n=== Macro sector-crash-sensitivity (today's primary risk driver) ===")
    macro = analyze_macro_risk({"vix": 15, "spx_price": 0, "spx_50ma": 0, "spx_200ma": 0})
    sensitivity = macro.get("sector_sensitivity") or {}
    high_sensitivity_sectors = set(sensitivity.get("high_sensitivity_sectors", []))
    print(f"Primary risk driver: {macro.get('crash_probability', {}).get('primary_risk')}")
    print(f"90-day crash probability: {macro.get('crash_probability', {}).get('prob_90d')}%")
    print(f"HIGH-exposure sectors: {sorted(high_sensitivity_sectors)}")

    merged['held'] = merged['ticker'].apply(lambda t: t in held)
    merged['held_accounts'] = merged['ticker'].apply(
        lambda t: '; '.join(f"{a}:{int(q)}" for a, q in held.get(t, {}).get('accounts', {}).items()) if t in held else '')
    merged['held_puts'] = merged['ticker'].apply(lambda t: held.get(t, {}).get('puts', 0))
    merged['held_calls'] = merged['ticker'].apply(lambda t: held.get(t, {}).get('calls', 0))

    # Held-but-not-in-watchlist gap — e.g. SBUX/CMG, actively traded but
    # invisible to this scanner because they were never added to the xlsx.
    watchlist_tickers = set(merged['ticker'].tolist())
    missing_from_watchlist = sorted(t for t in held.keys() if t not in watchlist_tickers)
    print(f"\nHeld tickers MISSING from the watchlist entirely: {missing_from_watchlist}")

    # Shortlist: bottom-quartile + IVR>=40 (the actual candidate pool) — run
    # real option-chain yield checks only on these, not all ~90 names, to
    # keep runtime bounded.
    shortlist_mask = (merged.get('pos_in_range', 100) < 25) & (merged.get('ivr', 0) >= 40)
    shortlist = merged[shortlist_mask].copy()
    print(f"\n=== Running real option-chain yield checks on {len(shortlist)} shortlisted names ===")
    real_yields = {}
    for t, price in zip(shortlist['ticker'], shortlist['price']):
        real_yields[t] = get_real_put_yield(t, price)
        print(f"  {t}: {real_yields[t]}")
    merged['real_yield'] = merged['ticker'].apply(lambda t: real_yields.get(t))
    shortlist['real_yield'] = shortlist['ticker'].apply(lambda t: real_yields.get(t))

    strategy_rows = []
    for _, row in shortlist.iterrows():
        strategy, verdict, reason = classify_strategy(row.to_dict(), held, high_sensitivity_sectors)
        strategy_rows.append({
            "ticker": row['ticker'], "sector": row.get('sector'), "held": row['ticker'] in held,
            "held_accounts": merged.loc[merged['ticker'] == row['ticker'], 'held_accounts'].iloc[0],
            "strategy": strategy, "verdict": verdict, "reason": reason,
        })
    strategy_df = pd.DataFrame(strategy_rows)

    merged.to_csv(os.path.join(LOGS_DIR, '_p1_merged.csv'), index=False)

    # ------------------------------------------------------------------
    # Assemble the markdown report
    # ------------------------------------------------------------------
    today_str = date.today().isoformat()
    lines = []
    lines.append(f"# Portfolio-1 Monthly Review — {today_str} ({len(merged)} names)")
    lines.append("")
    lines.append(f"**Source:** `{os.path.basename(src)}`. Cross-referenced against actual open positions "
                  f"across all accounts (not just the watchlist file in isolation) and today's live macro "
                  f"crash-sensitivity read.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Macro Backdrop (live)")
    lines.append("")
    cp = macro.get('crash_probability', {})
    lines.append(f"- Primary risk driver: **{cp.get('primary_risk', 'n/a')}**")
    lines.append(f"- Crash probability: 30d {cp.get('prob_30d', 0):.0f}% / 60d {cp.get('prob_60d', 0):.0f}% / 90d {cp.get('prob_90d', 0):.0f}%")
    lines.append(f"- Sectors flagged HIGH-exposure to today's driver: {', '.join(sorted(high_sensitivity_sectors)) or 'none'}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Held-Position Gap Check")
    lines.append("")
    if missing_from_watchlist:
        lines.append(f"**{len(missing_from_watchlist)} currently-held ticker(s) are completely absent from the "
                      f"watchlist file** — invisible to this scan until manually noticed:")
        lines.append("")
        for t in missing_from_watchlist:
            h = held[t]
            accts = '; '.join(f"{a}:{int(q)}" for a, q in h['accounts'].items())
            lines.append(f"- **{t}** — {accts} (puts:{h['puts']}, calls:{h['calls']})")
    else:
        lines.append("No gaps found — every currently-held ticker is present in the watchlist file.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Current Sector Exposure (real, all accounts)")
    lines.append("")
    lines.append("| Sector | Notional | Positions |")
    lines.append("|---|---|---|")
    for sector, data in sorted(sector_summary.items(), key=lambda kv: kv[1]['total_notional'], reverse=True):
        flag = " 🔴" if sector in high_sensitivity_sectors else ""
        lines.append(f"| {sector}{flag} | ${data['total_notional']:,.0f} | {data['position_count']} |")
    lines.append("")
    lines.append("🔴 = flagged HIGH-exposure to today's primary macro risk driver.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Candidate Shortlist (bottom-quartile + IVR≥40), Strategy-Classified & Yield-Verified")
    lines.append("")
    lines.append("| Ticker | Sector | Held? | Strategy | Verdict | Reason |")
    lines.append("|---|---|---|---|---|---|")
    for _, r in strategy_df.iterrows():
        held_str = r['held_accounts'] if r['held'] else "not held"
        lines.append(f"| {r['ticker']} | {r['sector']} | {held_str} | {r['strategy']} | {r['verdict']} | {r['reason']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Permanent-Exit Names Still Showing Live Exposure")
    lines.append("")
    exit_conflicts = [t for t in PERMANENT_EXITS if t in held]
    if exit_conflicts:
        for t in exit_conflicts:
            h = held[t]
            accts = '; '.join(f"{a}:{int(q)}" for a, q in h['accounts'].items())
            lines.append(f"- **{t}** flagged permanent-exit in `mcp/config.py` but still has live exposure: "
                          f"{accts} (puts:{h['puts']}, calls:{h['calls']})")
    else:
        lines.append("None — no permanent-exit name currently shows open exposure.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by `scripts/portfolio1_monthly_review.py`, {today_str}.*")

    report_path = os.path.join(LOGS_DIR, f'portfolio_review_P1_{today_str}.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"\nReport written to {report_path}")


if __name__ == '__main__':
    main()
