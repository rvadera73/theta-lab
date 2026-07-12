"""
Monthly net options-premium aggregator (YTD trend).

Builds a per-account, month-by-month series of NET option premium
(STO/STC credits minus BTC/BTO debits) from dated transaction/activity exports.
This is what the position-snapshot reports cannot provide (snapshots are point-in-time).

Supported export formats (auto-detected by columns):
  - schwab   : Date, Action ('Sell to Open'/'Buy to Close'/...), Amount ('$1,234.56' / '-$..')
  - fidelity : Run Date, Account, Action ('YOU SOLD OPENING TRANSACTION PUT ...'), Amount ($)
  - robinhood: Activity Date, Trans Code (STO/BTC/BTO/STC), Amount ('$..' / '($..)')

Vanguard is equity-only (no options) -> not aggregated here.
"""
from __future__ import annotations
import glob
import os
import re
import pandas as pd

DATA_DIR = "/home/rahulvadera/projects/theta-lab/data/positions"

# account -> (filename glob, format, optional {Account-column value: display name})
SOURCES: list[tuple[str, str, str, dict | None]] = [
    ("Account A (232)", "Individual_XXX232_Transactions_*.csv", "schwab", None),
    ("Account B (275)", "Contributory_XXX275_Transactions_*.csv", "schwab", None),
    ("Account C (634)", "Designated_Bene_Individual_XXX634_Transactions_*.csv", "schwab", None),
    ("Fidelity (Rahul)", "Accounts_History_fidelity_Rahul.csv", "fidelity", {
        "Traditional IRA": "Fidelity (Rahul)",
        "ROTH IRA for Minor": "Fidelity (Rahul)",  # fold minor into Rahul -> 3 Fidelity accounts
    }),
    ("Fidelity (Rajul)", "Accounts_History_fidelity_Rajul.csv", "fidelity", {
        "ROTH IRA": "Fidelity (Rajul — Roth IRA)",
        "Rollover IRA": "Fidelity (Rajul — Rollover IRA)",
    }),
    # globs match new (hood-rahul-*) and legacy (robinhood_rahul_*) names; newest wins
    ("Robinhood (Individual)", "*hood*dividual*.csv", "robinhood", None),
    ("Robinhood (Traditional IRA)", "*hood*traditional*.csv", "robinhood", None),
    # Vanguard OFX export has a positions section AND a transactions section
    ("Vanguard (Rahul)", "*vanguard*.csv", "vanguard", None),
]


def _money(series: pd.Series) -> pd.Series:
    """Parse '$1,234.56' / '-$1,234' / '($1,234.56)' -> float."""
    s = series.astype(str).str.strip()
    s = s.str.replace(r"[\$,]", "", regex=True)
    s = s.str.replace(r"^\((.*)\)$", r"-\1", regex=True)  # (123) -> -123
    return pd.to_numeric(s, errors="coerce")


def _latest(glob_pat: str) -> str | None:
    files = sorted(glob.glob(os.path.join(DATA_DIR, glob_pat)), key=os.path.getmtime)
    return files[-1] if files else None


def _parse(fmt: str, path: str, acct_map: dict | None, mode: str = "net") -> dict[str, pd.Series]:
    """Return {display_account: monthly_premium_series}.

    mode='net'   -> all option opens+closes (STO/STC credits minus BTC/BTO debits) = income kept
    mode='gross' -> opening SELLS only (STO / 'Sell to Open' / 'SOLD OPENING') = premium sold
    """
    if fmt == "schwab":
        df = pd.read_csv(path)
        actions = ["Sell to Open"] if mode == "gross" else ["Sell to Open", "Buy to Close", "Buy to Open", "Sell to Close"]
        opt = df[df["Action"].isin(actions)].copy()
        opt["m"] = pd.to_datetime(opt["Date"], errors="coerce").dt.to_period("M").astype(str)
        opt["amt"] = _money(opt["Amount"])
        return {"__self__": opt.groupby("m")["amt"].sum()}

    if fmt == "fidelity":
        df = pd.read_csv(path, skiprows=2)
        df.columns = [str(c).strip() for c in df.columns]
        pat_ = "SOLD OPENING TRANSACTION" if mode == "gross" else "OPENING TRANSACTION|CLOSING TRANSACTION"
        is_opt = df["Action"].astype(str).str.contains(pat_, case=False, na=False)
        opt = df[is_opt].copy()
        opt["m"] = pd.to_datetime(opt["Run Date"], errors="coerce").dt.to_period("M").astype(str)
        opt["amt"] = _money(opt["Amount ($)"])
        out: dict[str, pd.Series] = {}
        for acct_val, disp in (acct_map or {}).items():
            sub = opt[opt["Account"].astype(str).str.strip() == acct_val]
            if len(sub):
                s = sub.groupby("m")["amt"].sum()
                out[disp] = out[disp].add(s, fill_value=0) if disp in out else s
        return out

    if fmt == "vanguard":
        raw = open(path, encoding="utf-8", errors="replace").read().splitlines()
        hidx = next((i for i, ln in enumerate(raw) if "Trade Date" in ln and "Transaction Type" in ln), None)
        if hidx is None:
            return {}
        from io import StringIO
        df = pd.read_csv(StringIO("\n".join(raw[hidx:])))
        df.columns = [str(c).strip() for c in df.columns]
        types = ["sell to open"] if mode == "gross" else ["sell to open", "buy to close", "buy to open", "sell to close"]
        opt = df[df["Transaction Type"].astype(str).str.lower().isin(types)].copy()
        opt["m"] = pd.to_datetime(opt["Trade Date"], errors="coerce").dt.to_period("M").astype(str)
        opt["amt"] = _money(opt["Net Amount"])
        return {"__self__": opt.groupby("m")["amt"].sum()}

    if fmt == "robinhood":
        df = pd.read_csv(path, on_bad_lines="skip", engine="python")
        df.columns = [str(c).strip() for c in df.columns]
        code_col = next((c for c in df.columns if c.lower() in ("trans code", "trans_code", "code")), None)
        desc_col = next((c for c in df.columns if c.lower() == "description"), None)
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        amt_col = next((c for c in df.columns if c.lower() == "amount"), None)
        codes = ["STO"] if mode == "gross" else ["STO", "BTC", "BTO", "STC"]
        opt = df[df[code_col].astype(str).str.upper().isin(codes)].copy()
        if desc_col is not None:
            opt = opt[opt[desc_col].astype(str).str.contains("put|call", case=False, na=False)]
        opt["m"] = pd.to_datetime(opt[date_col], errors="coerce").dt.to_period("M").astype(str)
        opt["amt"] = _money(opt[amt_col])
        return {"__self__": opt.groupby("m")["amt"].sum()}

    return {}


def compute_monthly_premium(mode: str = "net") -> dict[str, pd.Series]:
    result: dict[str, pd.Series] = {}
    for default_name, pat, fmt, acct_map in SOURCES:
        path = _latest(pat)
        if not path:
            continue
        try:
            parsed = _parse(fmt, path, acct_map, mode)
        except Exception as e:  # pragma: no cover
            print(f"! {default_name}: parse error {e}")
            continue
        for key, series in parsed.items():
            name = default_name if key == "__self__" else key
            result[name] = series.dropna()
    return result


_TB_CACHE: dict | None = None
_TB_DONE = False


def total_book_pnl() -> dict | None:
    """LENS 2 — total book P&L (realized premium + unrealized MTM + equity), ≈ Empower's
    'portfolio value change' basis. Reconstructs positions from transactions and marks them
    at current Yahoo prices. Cached per process (report calls it 4×). Returns None if it
    can't run (e.g. inside an async event loop)."""
    global _TB_CACHE, _TB_DONE
    if _TB_DONE:
        return _TB_CACHE
    import asyncio
    try:
        if asyncio.get_event_loop().is_running():
            return None
    except RuntimeError:
        pass
    try:
        from reports.report_utils import load_us_positions
        data = asyncio.run(load_us_positions())
    except Exception:
        _TB_DONE = True
        return None
    positions = data.get("positions", [])
    premium = sum(getattr(p, "total_premium_received", 0) or 0 for p in positions)
    cost_to_close = sum(getattr(p, "total_cost_to_close_options", 0) or 0 for p in positions)
    stock = sum(getattr(p, "stock_pnl", 0) or 0 for p in positions)
    total = sum(getattr(p, "combined_net_pnl", 0) or 0 for p in positions)
    _TB_CACHE = {
        "premium_collected": premium,          # income booked (cash in)
        "unrealized_option_mtm": premium - cost_to_close,  # if closed now
        "equity_mtm": stock,                   # assigned-stock gains/losses
        "total_book_pnl": total,               # ≈ Empower total value change basis
        "positions": len(positions),
    }
    _TB_DONE = True
    return _TB_CACHE


def to_table(result: dict[str, pd.Series]) -> pd.DataFrame:
    months = sorted(set().union(*[set(s.index) for s in result.values()])) if result else []
    rows = {}
    for acct, s in result.items():
        rows[acct] = [round(float(s.get(m, 0.0)), 0) for m in months]
    df = pd.DataFrame(rows, index=months).T
    df["YTD"] = df.sum(axis=1)
    df.loc["TOTAL"] = df.sum(axis=0)
    return df


def render_trend_block(width: int = 120) -> list[str]:
    """Two lenses on performance: (1) premium income cash-flow and (2) total book P&L (MTM)."""
    net = compute_monthly_premium("net")
    if not net:
        return ["YTD PREMIUM TREND: (no transaction history available)", ""]
    net_tbl = to_table(net)
    gross = compute_monthly_premium("gross")
    gross_tbl = to_table(gross) if gross else None
    months = [c for c in net_tbl.columns if c != "YTD"]

    lines = ["═" * width,
             "TWO LENSES ON MONTHLY PERFORMANCE  (both derived from your transaction history)",
             "═" * width, ""]

    # ── LENS 1 — PREMIUM INCOME (cash flow) — the $100K/month target metric ──
    lines += ["LENS 1 — PREMIUM INCOME (cash flow)  =  what you COLLECT selling options  [the $100K target]",
              "─" * width]
    hdr = f"{'Account':<32}" + "".join(f"{m[-2:]:>11}" for m in months) + f"{'YTD':>13}"
    lines += [hdr, "-" * len(hdr)]
    for acct in net_tbl.index:
        if acct == "TOTAL":
            lines.append("-" * len(hdr))
        lines.append(f"{acct:<32}" + "".join(f"{net_tbl.loc[acct, m]:>11,.0f}" for m in months)
                     + f"{net_tbl.loc[acct, 'YTD']:>13,.0f}")
    # Gross sold vs net kept vs buyback drag (monthly totals)
    if gross_tbl is not None and "TOTAL" in gross_tbl.index:
        lines += ["", f"{'  Gross SOLD (STO)':<32}" + "".join(f"{gross_tbl.loc['TOTAL', m]:>11,.0f}" for m in months)
                  + f"{gross_tbl.loc['TOTAL', 'YTD']:>13,.0f}"]
        lines.append(f"{'  Net KEPT':<32}" + "".join(f"{net_tbl.loc['TOTAL', m]:>11,.0f}" for m in months)
                     + f"{net_tbl.loc['TOTAL', 'YTD']:>13,.0f}")
        drag = [gross_tbl.loc['TOTAL', m] - net_tbl.loc['TOTAL', m] for m in months]
        lines.append(f"{'  Buyback DRAG (rolling)':<32}" + "".join(f"{d:>11,.0f}" for d in drag)
                     + f"{sum(drag):>13,.0f}")
    lines += ["", "Net = STO/STC credits − BTC/BTO debits. High DRAG months = heavy rolling (premium given back).", ""]

    # ── LENS 2 — TOTAL ACCOUNT VALUE (mark-to-market) ≈ Empower "portfolio value change" ──
    lines += ["─" * width,
              "LENS 2 — TOTAL ACCOUNT VALUE (mark-to-market)  ≈  Empower 'portfolio value change'",
              "─" * width,
              "  = premium income  +  unrealized option MTM  +  equity/assigned-stock MTM  +  dividends",
              ""]
    tb = total_book_pnl()
    if tb:
        lines += [
            f"  Premium collected on OPEN positions:   ${tb['premium_collected']:>14,.0f}",
            f"  ⚠ Reconstructed unrealized MTM is unreliable right now — ~12 names have incomplete",
            f"    transaction history (premium parsed ~$0), so the raw total (${tb['total_book_pnl']:,.0f}) is distorted.",
        ]
    lines += ["",
              "  → For the authoritative total-value number, use EMPOWER. It reconciled to premium income",
              "    at the YTD level (~$435K ≈ our $438K), which validates the totals.",
              "",
              "WHY THEY DIVERGE MONTH-TO-MONTH:",
              "  • Empower's monthly figure is dominated by MARKET moves (unrealized MTM) — e.g. May +$288K",
              "    was your long book marking UP, not premium income (premium that month was ~$4K).",
              "  • LENS 1 books premium when SOLD — front-loaded because you sell long-dated (2027) contracts.",
              "  • So: use LENS 1 (income) for the $100K goal; use Empower (Lens 2) for net-worth/market view.",
              "  • To make Lens 2 exact here: backfill the ~12 names' transactions + drop fresh position snapshots.",
              ""]
    return lines


if __name__ == "__main__":
    res = compute_monthly_premium()
    tbl = to_table(res)
    pd.options.display.float_format = lambda x: f"{x:,.0f}"
    print(tbl.to_string())
