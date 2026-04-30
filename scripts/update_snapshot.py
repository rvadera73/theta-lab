"""
Auto-generate portfolio_snapshot.yaml from:
  - Schwab positions CSV  (holdings, open options)
  - Empower unified transactions CSV  (all accounts, all brokerages)

Weekly workflow:
  1. Export positions from Schwab → drop in data/statements/
  2. Export transactions from Empower → drop in data/statements/
  3. python3 scripts/update_snapshot.py
  4. Set month_to_date_equity_change manually
  5. git add data/portfolio_snapshot.yaml && git commit -m 'Weekly snapshot' && git push
"""

import os
import sys
import csv
import re
import yaml
import glob
from datetime import datetime, date, timedelta
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "statements")
SNAPSHOT_PATH = os.path.join(ROOT, "data", "portfolio_snapshot.yaml")


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def find_latest(pattern: str) -> str | None:
    files = glob.glob(os.path.join(DATA_DIR, pattern))
    return max(files, key=os.path.getmtime) if files else None


def find_empower_transactions() -> str | None:
    """Find the Empower unified transactions export (date-range named file)."""
    candidates = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    for f in sorted(candidates, key=os.path.getmtime, reverse=True):
        name = os.path.basename(f)
        # Empower files look like "2026-01-01 thru 2026-04-25 transactions.csv"
        if re.search(r"\d{4}-\d{2}-\d{2}.*thru.*\d{4}-\d{2}-\d{2}", name, re.IGNORECASE):
            return f
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(val: str) -> str:
    return val.strip().strip('"').replace("$", "").replace(",", "").strip()


def _parse_amount(val: str) -> float:
    try:
        return float(_clean(str(val)))
    except ValueError:
        return 0.0


def _parse_date(val: str) -> date | None:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(val.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_option_symbol(sym: str) -> dict | None:
    """Parse Schwab-format symbol 'AXON 01/16/2027 420.00 P'."""
    m = re.match(r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$", sym.strip())
    if not m:
        return None
    expiry = datetime.strptime(m.group(2), "%m/%d/%Y").date()
    return {
        "underlying": m.group(1),
        "expiry": expiry.isoformat(),
        "strike": float(m.group(3)),
        "option_type": "CALL" if m.group(4) == "C" else "PUT",
    }


def _normalize_account(raw: str) -> str:
    """Normalize Empower account names to short labels."""
    r = raw.strip()
    m = re.search(r"ending in\s*(\d+)", r, re.IGNORECASE)
    suffix = f" ({m.group(1)})" if m else ""

    if re.search(r"robinhood.*ira", r, re.IGNORECASE):
        return f"Robinhood IRA{suffix}"
    if re.search(r"robinhood", r, re.IGNORECASE):
        return f"Robinhood{suffix}"
    if re.search(r"roth.*minor", r, re.IGNORECASE):
        return f"Roth IRA Minor{suffix}"
    if re.search(r"roth", r, re.IGNORECASE):
        return f"Roth IRA{suffix}"
    if re.search(r"rollover", r, re.IGNORECASE):
        return f"Rollover IRA{suffix}"
    if re.search(r"contributory", r, re.IGNORECASE):
        return f"Schwab IRA{suffix}"
    if re.search(r"traditional.*ira|ira.*brokerage", r, re.IGNORECASE):
        return f"Traditional IRA{suffix}"
    if re.search(r"precise software|8014", r, re.IGNORECASE):
        return f"Individual 401k{suffix}"
    if re.search(r"global stock|health sciences|new era|small cap", r, re.IGNORECASE):
        return f"Vanguard Fund{suffix}"
    if re.search(r"individual", r, re.IGNORECASE):
        return f"Schwab Individual{suffix}"
    return f"Other{suffix}"


# ---------------------------------------------------------------------------
# Schwab positions CSV parser
# ---------------------------------------------------------------------------

def _extract_account_from_header(line: str) -> str:
    m = re.search(r"account\s+(.+?)\s+as of", line, re.IGNORECASE)
    if not m:
        return "Schwab"
    desc = m.group(1).strip().strip('"')
    digits = re.findall(r"\d+", desc)
    suffix = f" ({digits[-1]})" if digits else ""
    if "contributory" in desc.lower() or ("ira" in desc.lower() and "roth" not in desc.lower()):
        return f"Schwab IRA{suffix}"
    if "roth" in desc.lower():
        return f"Schwab Roth{suffix}"
    return f"Schwab Individual{suffix}"


def parse_positions(filepath: str) -> tuple[list[dict], list[dict]]:
    equity, options = [], []
    current_account = "Schwab"

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        if "positions for account" in line.lower():
            current_account = _extract_account_from_header(line)
            i += 1
            continue

        if '"Symbol"' in line or ("Symbol" in line and "Asset Type" in line):
            reader = csv.DictReader(lines[i:])
            for row in reader:
                raw_sym = row.get("Symbol", "").strip().strip('"')
                if not raw_sym or raw_sym.startswith("Account") or raw_sym.startswith("Cash"):
                    continue
                if "positions for account" in raw_sym.lower():
                    break

                asset_type = _clean(row.get("Asset Type", "")).lower()
                try:
                    qty = float(_clean(row.get("Qty (Quantity)", "0")).replace(",", "") or "0")
                    price = float(_clean(row.get("Price", "0")) or "0")
                    cost_total = float(_clean(row.get("Cost Basis", "0")).replace(",", "") or "0")
                    mkt_val = float(_clean(row.get("Mkt Val (Market Value)", "0")).replace(",", "") or "0")
                except ValueError:
                    continue

                if asset_type in ("equity", "stock") and qty > 0:
                    shares = int(qty)
                    equity.append({
                        "account": current_account,
                        "symbol": raw_sym,
                        "shares": shares,
                        "cost_basis_per_share": round(cost_total / shares if shares else 0, 2),
                        "current_price": round(price, 2),
                        "market_value": round(mkt_val, 0),
                        "unrealized_loss": round(abs(min(0, mkt_val - cost_total)), 0),
                    })
                elif asset_type == "option" and qty < 0:
                    parsed = _parse_option_symbol(raw_sym)
                    if parsed:
                        options.append({**parsed, "account": current_account, "contracts": int(abs(qty))})
            i += len(lines)
            continue
        i += 1

    return equity, options


# ---------------------------------------------------------------------------
# Empower unified transactions parser
# Handles all brokerage description formats in one pass
# Columns: Date, Account, Description, Category, Tags, Amount
# ---------------------------------------------------------------------------

# Action detection patterns (order matters — most specific first)
_IS_OPTION = re.compile(r"\bput\b|\bcall\b", re.IGNORECASE)
_STO_SIGNALS = re.compile(
    r"to\s+open|sold.*opening|sell.*open|you\s+sold\s+opening", re.IGNORECASE
)
_BTC_SIGNALS = re.compile(
    r"to\s+close|bought.*closing|buy.*close|you\s+bought\s+closing", re.IGNORECASE
)
_EXPIRED = re.compile(r"expir", re.IGNORECASE)

# Symbol extraction — try to pull ticker from various description styles
_SYM_PATTERNS = [
    re.compile(r"^(?:put|call)\s+(\w+)\s", re.IGNORECASE),                         # "Put AXON ..."
    re.compile(r"^(?:buy|sell)[\s\d.]+(\w+)\s+(?:put|call)", re.IGNORECASE),        # "Buy 1.0 AXON Put..."
    re.compile(r"\((\w{1,5})\)\s+\w", re.IGNORECASE),                               # "Put (AXON) ..."
    re.compile(r"^(?:put|call)\s+(\w[\w\s]+?)\$", re.IGNORECASE),                   # "Put Taiwan Semi$280"
]

# Option type
_IS_CALL = re.compile(r"\bcall\b", re.IGNORECASE)


def _extract_underlying(desc: str) -> str | None:
    for pat in _SYM_PATTERNS:
        m = pat.search(desc)
        if m:
            sym = m.group(1).strip().upper()
            if len(sym) <= 5 and sym.isalpha():
                return sym
    return None


def parse_empower_transactions(filepath: str) -> list[dict]:
    """
    Parse Empower unified export into normalized option transaction rows.
    Returns list of dicts with: Date, Action, underlying, opt_type, Amount, account
    Only option trades (Puts/Calls) are returned — equity and fund rows are skipped.
    """
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = row.get("Description", "").strip()
            cat = row.get("Category", "").strip()
            amount = _parse_amount(row.get("Amount", "0"))
            txn_date = _parse_date(row.get("Date", ""))
            account = _normalize_account(row.get("Account", ""))

            if not txn_date:
                continue
            if cat not in ("Securities Trades", "Investment Income"):
                continue
            if not _IS_OPTION.search(desc):
                continue

            # Determine action
            if _EXPIRED.search(desc):
                action = "Expired"
            elif _STO_SIGNALS.search(desc) or (amount > 0 and not _BTC_SIGNALS.search(desc)):
                action = "Sell to Open"
            else:
                action = "Buy to Close"

            # Infer from amount sign as fallback
            if action == "Sell to Open" and amount < 0:
                action = "Buy to Close"
            if action == "Buy to Close" and amount > 0:
                action = "Sell to Open"

            underlying = _extract_underlying(desc)
            opt_type = "C" if _IS_CALL.search(desc) else "P"

            rows.append({
                "Date": txn_date.isoformat(),
                "Action": action,
                "underlying": underlying,
                "opt_type": opt_type,
                "Amount": amount,
                "account": account,
                "_desc": desc,
            })
    return rows


# ---------------------------------------------------------------------------
# Metrics from Empower transactions
# ---------------------------------------------------------------------------

def compute_metrics(txns: list[dict], equity_symbols: list[str]) -> dict:
    today = date.today()
    start_of_month = today.replace(day=1)
    ninety_days_ago = today - timedelta(days=90)

    ytd_credits = 0.0
    ytd_debits = 0.0
    mtd_premium = 0.0

    # Profit factor: key by (account + desc snippet) for closed trade matching
    trades: dict[str, dict] = defaultdict(lambda: {"credits": 0.0, "debits": 0.0, "closed": False})
    cc_all_time: dict[str, float] = defaultdict(float)
    cc_last_90d: dict[str, float] = defaultdict(float)

    for row in txns:
        action = row["Action"]
        amount = row["Amount"]
        txn_date = _parse_date(row["Date"])
        underlying = row.get("underlying")
        opt_type = row.get("opt_type", "P")
        trade_key = f"{row['account']}|{row['_desc'][:40]}"

        if not txn_date:
            continue

        if action == "Sell to Open" and amount > 0:
            ytd_credits += amount
            trades[trade_key]["credits"] += amount
            if txn_date >= start_of_month:
                mtd_premium += amount
            if opt_type == "C" and underlying in equity_symbols:
                cc_all_time[underlying] += amount
                if txn_date >= ninety_days_ago:
                    cc_last_90d[underlying] += amount

        elif action == "Buy to Close" and amount < 0:
            ytd_debits += abs(amount)
            trades[trade_key]["debits"] += abs(amount)
            trades[trade_key]["closed"] = True
            if opt_type == "C" and underlying in equity_symbols:
                cc_all_time[underlying] -= abs(amount)
                if txn_date >= ninety_days_ago:
                    cc_last_90d[underlying] -= abs(amount)

        elif action == "Expired":
            trades[trade_key]["closed"] = True

    capture_rate = round((ytd_credits - ytd_debits) / ytd_credits * 100, 1) if ytd_credits else 0.0

    gross_wins = sum(
        t["credits"] - t["debits"]
        for t in trades.values()
        if t["closed"] and t["credits"] > t["debits"]
    )
    gross_losses = sum(
        t["debits"] - t["credits"]
        for t in trades.values()
        if t["closed"] and t["debits"] > t["credits"]
    )
    profit_factor = round(gross_wins / gross_losses, 2) if gross_losses > 0 else 0.0

    return {
        "ytd_credits": round(ytd_credits, 0),
        "ytd_debits": round(ytd_debits, 0),
        "ytd_net_premium": round(ytd_credits - ytd_debits, 0),
        "ytd_capture_rate": capture_rate,
        "ytd_profit_factor": profit_factor,
        "mtd_premium": round(mtd_premium, 0),
        "cc_all_time": dict(cc_all_time),
        "cc_last_90d": dict(cc_last_90d),
    }


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_snapshot() -> dict:
    pos_file = find_latest("Individual-Positions*.csv")
    txn_file = find_empower_transactions()

    if not pos_file:
        print("ERROR: No Schwab positions CSV found.")
        print("Export: Schwab → Accounts → Positions → Export")
        sys.exit(1)
    if not txn_file:
        print("ERROR: No Empower transactions CSV found.")
        print("Export: Empower → Transactions → date range → Export")
        sys.exit(1)

    print(f"  Positions  : {os.path.basename(pos_file)}")
    print(f"  Transactions: {os.path.basename(txn_file)}")

    equity_positions, short_options = parse_positions(pos_file)
    equity_symbols = [p["symbol"] for p in equity_positions]
    print(f"  Equity: {len(equity_positions)} positions | Options: {len(short_options)} short contracts")

    txns = parse_empower_transactions(txn_file)
    print(f"  Empower option transactions: {len(txns)}")

    metrics = compute_metrics(txns, equity_symbols)

    assigned_book = sum(p["market_value"] for p in equity_positions)
    print(f"  Assigned equity book : ${assigned_book:,.0f}")
    print(f"  YTD net premium      : ${metrics['ytd_net_premium']:,.0f} "
          f"(credits ${metrics['ytd_credits']:,.0f} / debits ${metrics['ytd_debits']:,.0f})")
    print(f"  YTD capture rate     : {metrics['ytd_capture_rate']}%")
    print(f"  MTD premium          : ${metrics['mtd_premium']:,.0f}")

    cc_all_time = metrics.get("cc_all_time", {})
    cc_last_90d = metrics.get("cc_last_90d", {})

    assigned_list = []
    for pos in equity_positions:
        sym = pos["symbol"]
        monthly_cc = max(0, round(cc_last_90d.get(sym, 0) / 3, 0))
        recovered = max(0, round(cc_all_time.get(sym, 0), 0))
        assigned_list.append({
            "account": pos["account"],
            "symbol": sym,
            "shares": pos["shares"],
            "cost_basis": pos["cost_basis_per_share"],
            "monthly_cc": int(monthly_cc),
            "recovered": int(recovered),
        })

    short_puts = [o for o in short_options if o["option_type"] == "PUT"]
    open_puts_list = [
        {
            "account": p["account"],
            "symbol": p["underlying"],
            "strike": p["strike"],
            "expiry": p["expiry"],
            "contracts": p["contracts"],
        }
        for p in sorted(short_puts, key=lambda x: (x["underlying"], x["expiry"]))
    ]
    print(f"  Open short puts      : {len(open_puts_list)}")

    today = date.today()
    return {
        "last_updated": today.isoformat(),
        "generated_by": "scripts/update_snapshot.py — do not edit manually",
        "assigned_equity_book_value": int(assigned_book),
        "ytd_premium_capture_rate": metrics["ytd_capture_rate"],
        "ytd_profit_factor": metrics["ytd_profit_factor"],
        "ytd_net_options_income": int(metrics["ytd_net_premium"]),
        "month": today.strftime("%Y-%m"),
        "month_to_date_premium": int(metrics["mtd_premium"]),
        "month_to_date_equity_change": 0,
        "assigned_positions": assigned_list,
        "open_puts": open_puts_list,
    }


def main():
    print(f"\nBuilding portfolio snapshot...")
    snapshot = build_snapshot()

    with open(SNAPSHOT_PATH, "w") as f:
        f.write("# Auto-generated by scripts/update_snapshot.py — do not edit manually\n")
        f.write("# Sources: Schwab positions CSV + Empower unified transactions CSV\n")
        f.write("# Only 'month_to_date_equity_change' requires manual input\n\n")
        yaml.dump(snapshot, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\nSnapshot saved → data/portfolio_snapshot.yaml")
    print(f"  Equity positions : {len(snapshot['assigned_positions'])}")
    print(f"  Open short puts  : {len(snapshot['open_puts'])}")
    print(f"  Assigned book    : ${snapshot['assigned_equity_book_value']:,.0f}")
    print(f"  YTD capture rate : {snapshot['ytd_premium_capture_rate']}%")
    print(f"  MTD premium      : ${snapshot['month_to_date_premium']:,.0f}")
    print()
    print("Next steps:")
    print("  1. Set month_to_date_equity_change (net stock mark-to-market this month)")
    print("  2. git add data/portfolio_snapshot.yaml && git commit -m 'Weekly snapshot' && git push")


if __name__ == "__main__":
    main()
