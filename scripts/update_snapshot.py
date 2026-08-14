"""
Auto-generate portfolio_snapshot.yaml from:
  - Schwab positions CSV  (holdings, open options)  — data/statements/
  - Schwab per-account Transactions CSVs (232/275/634)  — data/positions/
  - Fidelity per-person Accounts_History CSVs (Rahul/Rajul)  — data/positions/
  - Vanguard export  (vanguard_rahul.csv)  — data/positions/
  - Robinhood activity CSVs (Individual + Traditional IRA)  — data/positions/

Vanguard's export (vanguard_rahul.csv) is actually THREE concatenated
sections in one file: a small current-holdings snapshot, a full transaction
history (what feeds premium here — see parse_vanguard_transactions), and an
always-empty trailing section. Don't assume it's holdings-only just because
its top section looks like a snapshot — read the whole file.

Robinhood uses whatever full-history export is currently canonical in
data/positions/ (robinhood_rahul_individual.csv / robinhood_rahul_traditional.csv
— same files the main unified report already loads), even if it isn't freshly
re-exported this cycle. Stale-but-full beats missing entirely; re-export when
a current one is available (a partial/YTD-only export will silently produce
wrong open positions elsewhere in the pipeline — see prefer_full_over_ytd in
data/account_files.yaml — so don't drop in a YTD file just to "have something newer").

Weekly workflow:
  1. Export positions from Schwab (Account A) → drop in data/statements/
  2. Export per-account transactions from Schwab (232/275/634) → data/positions/
  3. Export Accounts_History from Fidelity (Rahul + Rajul) → data/positions/
  4. Export Vanguard activity → data/positions/vanguard_rahul.csv
  5. Export Robinhood activity (full history, not YTD) → data/positions/  (optional
     — reuses the last good file if skipped)
  6. python3 scripts/update_snapshot.py
  7. Set month_to_date_equity_change manually
  8. git add data/portfolio_snapshot.yaml && git commit -m 'Weekly snapshot' && git push
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
POSITIONS_DIR = os.path.join(ROOT, "data", "positions")
SNAPSHOT_PATH = os.path.join(ROOT, "data", "portfolio_snapshot.yaml")


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def find_latest(pattern: str) -> str | None:
    files = glob.glob(os.path.join(DATA_DIR, pattern))
    return max(files, key=os.path.getmtime) if files else None


_SCHWAB_TXN_PATTERNS = {
    "Account A (232)": "Individual_XXX232_Transactions_*.csv",
    "Account B (275)": "Contributory_XXX275_Transactions_*.csv",
    "Account C (634)": "Designated_Bene_Individual_XXX634_Transactions_*.csv",
}


def find_schwab_transactions() -> dict[str, str]:
    """Newest per-account Schwab Transactions CSV, keyed by canonical account label."""
    found = {}
    for label, pattern in _SCHWAB_TXN_PATTERNS.items():
        files = glob.glob(os.path.join(POSITIONS_DIR, pattern))
        if files:
            found[label] = max(files, key=os.path.getmtime)
    return found


_FIDELITY_HISTORY_PATTERNS = {
    "rahul": "Accounts_History_fidelity_Rahul.csv",
    "rajul": "Accounts_History_fidelity_Rajul.csv",
}


def find_fidelity_transactions() -> dict[str, str]:
    """Newest Fidelity Accounts_History CSV per person (each splits into sub-accounts
    internally by Account Number — see _FIDELITY_ACCOUNT_LABELS)."""
    found = {}
    for person, pattern in _FIDELITY_HISTORY_PATTERNS.items():
        files = glob.glob(os.path.join(POSITIONS_DIR, pattern))
        if files:
            found[person] = max(files, key=os.path.getmtime)
    return found


def find_vanguard_transactions() -> str | None:
    """Vanguard's export lives in data/positions/ under the same canonical name
    the main unified report already loads."""
    path = os.path.join(POSITIONS_DIR, "vanguard_rahul.csv")
    return path if os.path.exists(path) else None


_ROBINHOOD_FILES = {
    "Robinhood Individual (9079)": "robinhood_rahul_individual.csv",
    "Robinhood IRA (3600)": "robinhood_rahul_traditional.csv",
}


def find_robinhood_transactions() -> dict[str, str]:
    """Canonical per-account Robinhood activity CSVs in data/positions/ (the same
    files the main unified report already loads via open_positions_loader_v2.py).
    Previously this script instead globbed UUID-named files in data/statements/
    and guessed Individual-vs-IRA by relative file size — those files were stuck
    at a 2026-05-03 export while the canonical ones here had already been
    refreshed to 2026-07-31, so premium/YTD figures were needlessly ~3 months
    staler than the data on hand. Filename-based labeling replaces the size
    heuristic entirely."""
    found = {}
    for label, filename in _ROBINHOOD_FILES.items():
        path = os.path.join(POSITIONS_DIR, filename)
        if os.path.exists(path):
            found[label] = path
    return found


def parse_robinhood_transactions(filepath: str, account_label: str) -> list[dict]:
    """
    Parse a Robinhood activity CSV into normalized option transaction rows.
    Robinhood CSV columns: Activity Date, Process Date, Settle Date, Instrument,
                           Description, Trans Code, Quantity, Price, Amount
    All option trades in the file are returned (no date filter — use full file as source).
    """
    rows = []
    try:
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trans_code = (row.get("Trans Code") or "").strip()
                desc = (row.get("Description") or "").strip().replace("\n", " ")
                instrument = (row.get("Instrument") or "").strip()
                txn_date = _parse_date((row.get("Activity Date") or "").strip())
                raw_amount = (row.get("Amount") or "").strip().replace("(", "-").replace(")", "")

                if not txn_date:
                    continue

                # Only option trades
                if trans_code not in ("STO", "BTC", "BTO", "STC"):
                    continue
                if not re.search(r"\bput\b|\bcall\b", desc, re.IGNORECASE):
                    continue

                amount = _parse_amount(raw_amount)

                if trans_code == "STO":
                    action = "Sell to Open"
                elif trans_code == "BTC":
                    action = "Buy to Close"
                elif trans_code == "STC":
                    action = "Sell to Close"
                elif trans_code == "BTO":
                    action = "Buy to Open"
                else:
                    continue

                # Parse option description: "AXON 3/19/2027 Put $320.00"
                m = re.match(
                    r"^(\w+)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(Put|Call)\s+\$([\d.]+)",
                    desc, re.IGNORECASE,
                )
                if m:
                    underlying = m.group(1).upper()
                    opt_type = "C" if m.group(3).upper() == "CALL" else "P"
                else:
                    underlying = instrument.upper() if instrument else None
                    opt_type = "C" if re.search(r"\bcall\b", desc, re.IGNORECASE) else "P"

                rows.append({
                    "Date": txn_date.isoformat(),
                    "Action": action,
                    "underlying": underlying,
                    "opt_type": opt_type,
                    "Amount": amount,
                    "account": account_label,
                    "_desc": desc[:60],
                })
    except Exception as e:
        print(f"  Warning: could not parse Robinhood CSV {os.path.basename(filepath)}: {e}")
    return rows


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
# Schwab per-account Transactions CSV parser
# Columns: Date, Action, Symbol, Description, Quantity, Price, Fees & Comm, Amount
# Symbol is already in the "AXON 08/21/2026 500.00 P" format _parse_option_symbol handles.
# ---------------------------------------------------------------------------

_SCHWAB_TXN_ACTIONS = {"Sell to Open", "Buy to Close", "Expired"}


def parse_schwab_transactions(filepath: str, account_label: str) -> list[dict]:
    """Parse one Schwab per-account Transactions CSV into the shared option-txn shape."""
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            action = _clean(row.get("Action", ""))
            if action not in _SCHWAB_TXN_ACTIONS:
                continue
            parsed_sym = _parse_option_symbol(_clean(row.get("Symbol", "")))
            if not parsed_sym:
                continue
            txn_date = _parse_date(_clean(row.get("Date", "")))
            if not txn_date:
                continue

            rows.append({
                "Date": txn_date.isoformat(),
                "Action": action,
                "underlying": parsed_sym["underlying"],
                "opt_type": "C" if parsed_sym["option_type"] == "CALL" else "P",
                "Amount": _parse_amount(row.get("Amount", "0")),
                "account": account_label,
                "_desc": row.get("Description", "").strip(),
            })
    return rows


# ---------------------------------------------------------------------------
# Fidelity Accounts_History CSV parser (one file per person, splits into
# sub-accounts by Account Number — see _FIDELITY_ACCOUNT_LABELS).
# Columns: Run Date, Account, Account Number, Action, Symbol, Description,
#          Type, Price ($), Quantity, Commission ($), Fees ($),
#          Accrued Interest ($), Amount ($), Settlement Date
# Symbol looks like " -OKLO270319P40" (ticker + YYMMDD + P/C + strike).
# ---------------------------------------------------------------------------

# Only accounts tracked in ACCOUNTS_CONFIG (unified_master_report_production.py) — a
# custodial "ROTH IRA for Minor" (225798148's sibling, 258240575) also appears in the
# Rahul file but isn't a tracked account, so it's deliberately excluded, not guessed at.
_FIDELITY_ACCOUNT_LABELS = {
    "225798148": "Fidelity (Rahul)",
    "263508923": "Fidelity (Rajul — Rollover IRA)",
    "233461172": "Fidelity (Rajul — Roth IRA)",
}

_FIDELITY_OPEN = re.compile(r"^YOU SOLD OPENING TRANSACTION\s+(PUT|CALL)\s*\((\w+)\)", re.IGNORECASE)
_FIDELITY_CLOSE = re.compile(r"^YOU BOUGHT CLOSING TRANSACTION\s+(PUT|CALL)\s*\((\w+)\)", re.IGNORECASE)


def parse_fidelity_transactions(filepath: str) -> list[dict]:
    """Parse one Fidelity Accounts_History CSV into the shared option-txn shape.
    Note: no confirmed 'option expired' row pattern was found in sampled Fidelity
    data (only an equity-delisting 'EXPIRED POSITION' row, unrelated to options) —
    expired Fidelity options are not captured here. Known, disclosed gap."""
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        # File has leading blank line(s) before the real header — DictReader needs
        # the reader positioned at the header row itself.
        lines = [l for l in f if l.strip()]
    reader = csv.DictReader(lines)
    for row in reader:
        acct_num = _clean(row.get("Account Number") or "")
        account_label = _FIDELITY_ACCOUNT_LABELS.get(acct_num)
        if not account_label:
            continue

        desc = (row.get("Action") or "").strip()  # full free-text description lives in Action
        m_open = _FIDELITY_OPEN.match(desc)
        m_close = _FIDELITY_CLOSE.match(desc)
        if m_open:
            action, opt_match = "Sell to Open", m_open
        elif m_close:
            action, opt_match = "Buy to Close", m_close
        else:
            continue

        txn_date = _parse_date(_clean(row.get("Run Date") or ""))
        if not txn_date:
            continue

        underlying = opt_match.group(2).upper()
        opt_type = "C" if opt_match.group(1).upper() == "CALL" else "P"
        # Symbol column would be a more reliable strike/expiry source than free text,
        # but compute_metrics only needs underlying/opt_type/Amount/Action, not
        # strike/expiry, so a Symbol-parse miss here isn't fatal — underlying/opt_type
        # from the Action prefix above are used regardless.

        rows.append({
            "Date": txn_date.isoformat(),
            "Action": action,
            "underlying": underlying,
            "opt_type": opt_type,
            "Amount": _parse_amount(row.get("Amount ($)") or "0"),
            "account": account_label,
            "_desc": desc,
        })
    return rows


# ---------------------------------------------------------------------------
# Vanguard transaction history parser.
# The Vanguard export (vanguard_rahul.csv) is actually THREE concatenated
# sections, each with its own header line: (1) a small current-holdings
# snapshot, (2) a full transaction history — the one this parser reads — and
# (3) an always-empty trailing section. Section 2's header:
#   Account Number, Trade Date, Settlement Date, Transaction Type,
#   Transaction Description, Investment Name, Symbol, Shares, Share Price,
#   Principal Amount, Commissions and Fees, Net Amount, Accrued Interest,
#   Account Type
# Trade Date is already YYYY-MM-DD. Symbol, when present, looks like
# "LITE 270716 P 560.00" (ticker, YYMMDD, P/C, strike) — often blank on rows
# that aren't the original opening trade, so it's used best-effort, not as a
# gate (unlike Schwab, where Symbol is reliably populated on every row).
# ---------------------------------------------------------------------------

_VANGUARD_TXN_HEADER = "Account Number,Trade Date,Settlement Date,Transaction Type"
_VANGUARD_ACTIONS = {"sell to open": "Sell to Open", "buy to close": "Buy to Close", "expired": "Expired"}
_VANGUARD_SYMBOL = re.compile(r"^([A-Z]+)\s+(\d{2})(\d{2})(\d{2})\s+([PC])\s+[\d.]+$")


def parse_vanguard_transactions(filepath: str, account_label: str) -> list[dict]:
    """Parse the transaction-history section of a Vanguard export into the shared
    option-txn shape. See module comment above for why this is section 2 of 3."""
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()

    start = next((i for i, l in enumerate(lines) if l.startswith(_VANGUARD_TXN_HEADER)), None)
    if start is None:
        return []
    # Section ends at the next blank line or the next header-looking line.
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].strip()), len(lines))

    rows = []
    reader = csv.DictReader(lines[start:end])
    for row in reader:
        action = _VANGUARD_ACTIONS.get((row.get("Transaction Type") or "").strip().lower())
        if not action:
            continue
        txn_date = _parse_date(_clean(row.get("Trade Date") or ""))
        if not txn_date:
            continue

        underlying, opt_type = None, "P"
        sym_match = _VANGUARD_SYMBOL.match((row.get("Symbol") or "").strip())
        if sym_match:
            underlying = sym_match.group(1)
            opt_type = sym_match.group(5)
        elif re.search(r"\bcall\b", row.get("Investment Name") or "", re.IGNORECASE):
            opt_type = "C"

        rows.append({
            "Date": txn_date.isoformat(),
            "Action": action,
            "underlying": underlying,
            "opt_type": opt_type,
            "Amount": _parse_amount(row.get("Net Amount") or "0"),
            "account": account_label,
            "_desc": (row.get("Investment Name") or row.get("Transaction Description") or "").strip(),
        })
    return rows


# ---------------------------------------------------------------------------
# Metrics from Schwab + Fidelity + Vanguard + Robinhood transactions
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
    # Use latest Schwab positions export (Individual-Positions*.csv format)
    # Note: "Portfolio_Positions*.csv" files are typically from Fidelity, not Schwab
    # NOTE: this is a SEPARATE, pre-existing staleness gap from the Empower removal
    # below — data/statements/ hasn't had a fresh Individual-Positions*.csv in months,
    # so assigned_equity_book_value/open_puts may still be stale even after this fix.
    pos_file = find_latest("Individual-Positions*.csv")
    schwab_txn_files = find_schwab_transactions()
    fidelity_txn_files = find_fidelity_transactions()

    if not pos_file:
        print("ERROR: No Schwab positions CSV found.")
        print("Export from Schwab Account A: Accounts → Positions → Export to CSV")
        print("Expected filename pattern: Individual-Positions*.csv")
        sys.exit(1)
    if not schwab_txn_files:
        print("ERROR: No Schwab per-account Transactions CSVs found in data/positions/.")
        print("Export from each Schwab account: Accounts → Transactions → Export to CSV")
        sys.exit(1)
    if not fidelity_txn_files:
        print("ERROR: No Fidelity Accounts_History CSVs found in data/positions/.")
        print("Export from Fidelity: Accounts → Activity & Orders → Export → Accounts_History")
        sys.exit(1)

    print(f"  Positions  : {os.path.basename(pos_file)}")

    equity_positions, short_options = parse_positions(pos_file)
    equity_symbols = [p["symbol"] for p in equity_positions]
    print(f"  Equity: {len(equity_positions)} positions | Options: {len(short_options)} short contracts")

    txns = []
    for label, path in schwab_txn_files.items():
        schwab_txns = parse_schwab_transactions(path, label)
        print(f"  Schwab txns ({label}) — {os.path.basename(path)}: {len(schwab_txns)} option trades")
        txns.extend(schwab_txns)
    for person, path in fidelity_txn_files.items():
        fid_txns = parse_fidelity_transactions(path)
        print(f"  Fidelity txns ({person}) — {os.path.basename(path)}: {len(fid_txns)} option trades")
        txns.extend(fid_txns)

    vanguard_file = find_vanguard_transactions()
    if vanguard_file:
        vg_txns = parse_vanguard_transactions(vanguard_file, "Vanguard (Rahul)")
        print(f"  Vanguard txns — {os.path.basename(vanguard_file)}: {len(vg_txns)} option trades")
        txns.extend(vg_txns)

    # Add ALL transactions from each Robinhood CSV as the canonical Robinhood source
    for acct_label, rh_file in find_robinhood_transactions().items():
        rh_txns = parse_robinhood_transactions(rh_file, account_label=acct_label)
        print(f"  Robinhood CSV ({acct_label}) — {os.path.basename(rh_file)}: {len(rh_txns)} option trades")
        txns.extend(rh_txns)

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
        f.write("# Sources: Schwab positions+transactions CSVs + Fidelity Accounts_History CSVs + Robinhood activity CSV\n")
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
