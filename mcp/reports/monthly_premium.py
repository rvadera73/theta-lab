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
import sys
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

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
    if mode == "net":
        # FIFO-realized, attributed to the CLOSE month — from
        # scripts/realized_pnl.py, the corrected engine that replaced this
        # module's own same-month cash-flow sum (which booked premium the
        # month it was SOLD rather than the month a position actually
        # closed, and didn't recognize assignment as a closing event at
        # all — see realized_pnl.py's docstring for the full rationale).
        from realized_pnl import get_realized_monthly_by_account
        monthly = get_realized_monthly_by_account()
        return {label: pd.Series(m).sort_index() for label, m in monthly.items() if m}

    # "gross" mode (opening SELLS only) is a plain same-month cash-flow
    # filter, not a P&L computation — no FIFO matching needed, so the
    # original per-broker parsing is still correct here.
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
    all_pos = data.get("positions", [])
    # Only positions with COMPLETE entry data — exclude ones opened before the transaction
    # window (premium ~0), which would otherwise distort MTM. (Per user: none closed recently,
    # so these are simply pre-2026 opens we lack the entry premium for.)
    positions = [p for p in all_pos if (getattr(p, "total_premium_received", 0) or 0) >= 50]
    excluded = len(all_pos) - len(positions)
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
        "excluded": excluded,                  # pre-window opens (no entry premium)
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


def _md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    def _cell(c):
        return str(c).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(_cell(c) for c in row) + " |")
    return lines


def render_trend_block(width: int = 120) -> list[str]:
    """Two lenses on performance: (1) premium income cash-flow and (2) total book P&L (MTM)."""
    net = compute_monthly_premium("net")
    if not net:
        return ["**YTD Premium Trend:** (no transaction history available)", ""]
    net_tbl = to_table(net)
    gross = compute_monthly_premium("gross")
    gross_tbl = to_table(gross) if gross else None
    months = [c for c in net_tbl.columns if c != "YTD"]

    lines = ["### Two Lenses on Monthly Performance",
             "",
             "_(both derived from your transaction history)_", ""]

    # ── LENS 1 — PREMIUM INCOME (cash flow) — the $100K/month target metric ──
    lines += ["#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]",
              ""]
    headers = ["Account"] + [m[-2:] for m in months] + ["YTD"]
    rows = []
    for acct in net_tbl.index:
        rows.append([acct if acct != "TOTAL" else "**TOTAL**"]
                    + [f"{net_tbl.loc[acct, m]:,.0f}" for m in months]
                    + [f"{net_tbl.loc[acct, 'YTD']:,.0f}"])
    # Gross SOLD (this month's opens) vs Net REALIZED (this month's closes,
    # FIFO-matched) — these are on DIFFERENT bases (open-month vs close-month),
    # so their difference is NOT a "buyback drag" figure and isn't shown as
    # one; a prior version of this line subtracted the two directly, which
    # only made sense when both sides were same-month cash-flow sums.
    if gross_tbl is not None and "TOTAL" in gross_tbl.index:
        rows.append(["Gross SOLD (STO, opened this month)"]
                    + [f"{gross_tbl.loc['TOTAL', m]:,.0f}" for m in months]
                    + [f"{gross_tbl.loc['TOTAL', 'YTD']:,.0f}"])
        rows.append(["Net REALIZED (FIFO, closed this month)"]
                    + [f"{net_tbl.loc['TOTAL', m]:,.0f}" for m in months]
                    + [f"{net_tbl.loc['TOTAL', 'YTD']:,.0f}"])
    lines += _md_table(headers, rows)
    lines += ["", "Net REALIZED = FIFO-matched close gain/loss, attributed to the month a position CLOSED",
              "(assignment counts as a close). Gross SOLD = premium collected on positions OPENED that",
              "month — a different basis, so Gross minus Net is not a meaningful 'drag' figure; a position",
              "opened this month may not close for months. See scripts/realized_pnl.py for the full method.", ""]

    # ── LENS 2 — TOTAL ACCOUNT VALUE (mark-to-market) ≈ Empower "portfolio value change" ──
    lines += ["#### Lens 2 — Total Account Value (mark-to-market) ≈ Empower 'portfolio value change'",
              "",
              "= premium income + unrealized option MTM + equity/assigned-stock MTM + dividends",
              ""]
    lines += [
        "- Total value = premium income (LENS 1, accurate) + unrealized option MTM + equity MTM + dividends.",
        "- The MTM parts need CURRENT option marks, which live in your POSITION-SNAPSHOT exports (or live quotes) — NOT in transaction files. So this total is NOT computed here (reconstructed marks are stale). Transactions give income; marks give value — you need both, from different exports.",
        "- Use EMPOWER for the authoritative total value. (A prior version of this note claimed a specific $435K/$438K reconciliation — that was against LENS 1's OLD same-month cash-flow total, not the FIFO-realized figure above; re-verify against Empower with today's numbers rather than trusting that stale comparison.)",
        "- To compute a live total HERE: drop fresh position-snapshot exports (they carry current marks).",
        "",
        "**Why they diverge month-to-month:**",
        "",
        "- Empower's monthly figure is dominated by MARKET moves (unrealized MTM) — e.g. May +$288K was your long book marking UP, not premium income (premium that month was ~$4K).",
        "- LENS 1 books premium when SOLD — front-loaded because you sell long-dated (2027) contracts.",
        "- So: use LENS 1 (income) for the $100K goal; use Empower (Lens 2) for net-worth/market view.",
        "- To make Lens 2 exact here: backfill the ~12 names' transactions + drop fresh position snapshots.",
        ""]
    return lines


if __name__ == "__main__":
    res = compute_monthly_premium()
    tbl = to_table(res)
    pd.options.display.float_format = lambda x: f"{x:,.0f}"
    print(tbl.to_string())
