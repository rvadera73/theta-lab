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
        "ROTH IRA for Minor": "Fidelity (Rahul — Roth Minor)",
    }),
    ("Fidelity (Rajul)", "Accounts_History_fidelity_Rajul.csv", "fidelity", {
        "ROTH IRA": "Fidelity (Rajul — Roth IRA)",
        "Rollover IRA": "Fidelity (Rajul — Rollover IRA)",
    }),
    ("Robinhood (Individual)", "robinhood_rahul_individual.csv", "robinhood", None),
    ("Robinhood (Traditional IRA)", "robinhood_rahul_traditional.csv", "robinhood", None),
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


def _parse(fmt: str, path: str, acct_map: dict | None) -> dict[str, pd.Series]:
    """Return {display_account: monthly_net_premium_series}."""
    if fmt == "schwab":
        df = pd.read_csv(path)
        opt = df[df["Action"].isin(["Sell to Open", "Buy to Close", "Buy to Open", "Sell to Close"])].copy()
        opt["m"] = pd.to_datetime(opt["Date"], errors="coerce").dt.to_period("M").astype(str)
        opt["amt"] = _money(opt["Amount"])
        return {"__self__": opt.groupby("m")["amt"].sum()}

    if fmt == "fidelity":
        df = pd.read_csv(path, skiprows=2)
        df.columns = [str(c).strip() for c in df.columns]
        is_opt = df["Action"].astype(str).str.contains("OPENING TRANSACTION|CLOSING TRANSACTION", case=False, na=False)
        opt = df[is_opt].copy()
        opt["m"] = pd.to_datetime(opt["Run Date"], errors="coerce").dt.to_period("M").astype(str)
        opt["amt"] = _money(opt["Amount ($)"])
        out = {}
        for acct_val, disp in (acct_map or {}).items():
            sub = opt[opt["Account"].astype(str).str.strip() == acct_val]
            if len(sub):
                out[disp] = sub.groupby("m")["amt"].sum()
        return out

    if fmt == "robinhood":
        df = pd.read_csv(path, on_bad_lines="skip", engine="python")
        df.columns = [str(c).strip() for c in df.columns]
        code_col = next((c for c in df.columns if c.lower() in ("trans code", "trans_code", "code")), None)
        desc_col = next((c for c in df.columns if c.lower() == "description"), None)
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        amt_col = next((c for c in df.columns if c.lower() == "amount"), None)
        opt = df[df[code_col].astype(str).str.upper().isin(["STO", "BTC", "BTO", "STC"])].copy()
        if desc_col is not None:
            opt = opt[opt[desc_col].astype(str).str.contains("put|call", case=False, na=False)]
        opt["m"] = pd.to_datetime(opt[date_col], errors="coerce").dt.to_period("M").astype(str)
        opt["amt"] = _money(opt[amt_col])
        return {"__self__": opt.groupby("m")["amt"].sum()}

    return {}


def compute_monthly_premium() -> dict[str, pd.Series]:
    result: dict[str, pd.Series] = {}
    for default_name, pat, fmt, acct_map in SOURCES:
        path = _latest(pat)
        if not path:
            continue
        try:
            parsed = _parse(fmt, path, acct_map)
        except Exception as e:  # pragma: no cover
            print(f"! {default_name}: parse error {e}")
            continue
        for key, series in parsed.items():
            name = default_name if key == "__self__" else key
            result[name] = series.dropna()
    return result


def to_table(result: dict[str, pd.Series]) -> pd.DataFrame:
    months = sorted(set().union(*[set(s.index) for s in result.values()])) if result else []
    rows = {}
    for acct, s in result.items():
        rows[acct] = [round(float(s.get(m, 0.0)), 0) for m in months]
    df = pd.DataFrame(rows, index=months).T
    df["YTD"] = df.sum(axis=1)
    df.loc["TOTAL"] = df.sum(axis=0)
    return df


if __name__ == "__main__":
    res = compute_monthly_premium()
    tbl = to_table(res)
    pd.options.display.float_format = lambda x: f"{x:,.0f}"
    print(tbl.to_string())
