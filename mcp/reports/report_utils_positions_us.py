"""
US broker position-loading helpers split out of report_utils.py (Bolt b19).
report_utils.py re-exports everything here so every existing
`from report_utils import X` call site keeps working unchanged.

load_us_positions() itself, plus current_price()/_snapshot_holdings()/
_fill_current_marks()/load_robinhood_positions(), stay physically in
report_utils.py (see that file's own module docstring note) -- several
existing regression tests mock.patch.object(report_utils, "<name>", ...)
for exactly those names while exercising load_us_positions(), which only
works if the patched name and load_us_positions() share one module's bare
-name global lookup. Everything in THIS file (confirmed by reading every
existing test) is never itself the target of that kind of patch, so it can
live in its own file and still call back into report_utils.py's
current_price()/_fill_current_marks() via ordinary (deferred, to sidestep
import ordering) cross-module imports -- those calls run with the REAL
function, unmocked, exactly as they do today.
"""
import csv
import re
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from analysis.pnl import OptionLeg, Position
from report_utils_core import (
    DATA_DIR, STATEMENTS_DIR, latest_file, load_account_transactions, load_snapshot,
    parse_amount, parse_qty, parse_txn_date, safe_div,
)
from report_utils_pricing import option_market_price, parse_option_symbol

_SCHWAB_SNAPSHOT_FILE = {
    "A": "schwab_rahul_individual.csv",
    "B": "schwab_pinky_ira.csv",
    "C": "schwab_designated-bene.csv",
}

_SCHWAB_OPT_SYMBOL = re.compile(r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$")


def _clean_money(val: str) -> float:
    try:
        return float(val.strip().strip('"').replace("$", "").replace(",", ""))
    except (ValueError, AttributeError):
        return 0.0


def reconstruct_open_option_legs(rows: list[dict[str, str]], account: str) -> list[dict[str, Any]]:
    from report_utils import current_price

    book: dict[tuple[str, str, float, str], dict[str, Any]] = {}
    for row in rows:
        parsed = parse_option_symbol(row.get("Symbol", ""))
        if not parsed:
            continue
        qty = max(1, parse_qty(row.get("Quantity", 1)))
        action = str(row.get("Action", "")).strip()
        amount = parse_amount(row.get("Amount", 0))
        txn_date = parse_txn_date(row.get("Date", "")) or date.today()
        key = (parsed["symbol"], parsed["expiry"], parsed["strike"], parsed["option_type"])
        item = book.setdefault(key, {
            **parsed,
            "contracts": 0,
            "net_credit": 0.0,
            "opened": None,
            "account": account,
        })
        if "Sell to Open" in action:
            item["contracts"] += qty
            item["net_credit"] += max(0.0, amount)
            item["opened"] = min(item["opened"], txn_date) if item["opened"] else txn_date
        elif action == "Buy to Close":
            item["contracts"] = max(0, item["contracts"] - qty)
            item["net_credit"] -= abs(amount)
        elif action in ("Assigned", "Expired", "Exercise"):
            item["contracts"] = 0
    open_legs = []
    for item in book.values():
        if item["contracts"] <= 0:
            continue
        dte = (date.fromisoformat(item["expiry"]) - date.today()).days
        underlying = current_price(item["symbol"])
        mark = option_market_price(item["symbol"], item["expiry"], item["strike"], item["option_type"])
        item.update({
            "dte": dte,
            "underlying_price": underlying,
            "mark": (mark or 0.0) * 100 * item["contracts"],
            "premium_received": item["net_credit"],
            "moneyness_pct": round(((underlying - item["strike"]) / underlying * 100), 1) if underlying else None,
        })
        open_legs.append(item)
    return sorted(open_legs, key=lambda x: (x["dte"], x["symbol"]))


def load_position_csv() -> list[dict[str, Any]]:
    path = latest_file("Individual-Positions*.csv")
    if not path:
        return []
    positions: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()
    header_idx = next((i for i, line in enumerate(lines) if "\"Symbol\"" in line and "Asset Type" in line), None)
    if header_idx is None:
        return []
    for row in csv.DictReader(lines[header_idx:]):
        symbol = str(row.get("Symbol", "")).strip().strip('"')
        if not symbol:
            continue
        positions.append({
            "symbol": symbol,
            "qty": parse_qty(row.get("Qty (Quantity)", 0)),
            "price": parse_amount(row.get("Price", 0)),
            "market_value": parse_amount(row.get("Mkt Val (Market Value)", 0)),
            "cost_basis_total": parse_amount(row.get("Cost Basis", 0)),
            "asset_type": str(row.get("Asset Type", "")).strip().strip('"'),
        })
    return positions


def _fallback_account_letter(raw_account: str) -> str:
    """Normalize a snapshot's free-text account field to A/B/C."""
    if "8634" in raw_account or "634" in raw_account or raw_account.strip().upper() == "C":
        return "C"
    if "275" in raw_account or raw_account.strip().upper() == "B":
        return "B"
    return "A"


def _fallback_assigned_positions(snapshot: dict, price_map: dict, cost_map: dict) -> dict[tuple[str, str], Position]:
    from report_utils import current_price

    positions: dict[tuple[str, str], Position] = {}
    for item in snapshot.get("assigned_positions", []):
        symbol = item.get("symbol")
        if not symbol:
            continue
        account = _fallback_account_letter(str(item.get("account", "A")))
        positions[(account, symbol)] = Position(
            symbol=symbol,
            account=account,
            shares=int(item.get("shares", 0) or 0),
            stock_cost_basis=float(cost_map.get(symbol) or item.get("cost_basis", 0) or 0),
            current_price=float(price_map.get(symbol) or current_price(symbol) or item.get("cost_basis", 0) or 0),
        )
        positions[(account, symbol)]._snapshot_meta = item
    return positions


def _fallback_merge_reconstructed_legs(positions: dict[tuple[str, str], Position], txns: dict) -> None:
    """Mutates `positions` in place, adding any reconstructed open option
    leg (from the raw transaction log) onto an existing snapshot Position,
    or creating a new options-only Position when the snapshot didn't
    already carry one."""
    from report_utils import current_price

    for account, rows in txns.items():
        for leg in reconstruct_open_option_legs(rows, account):
            pos = positions.get((account, leg["symbol"]))
            if not pos:
                pos = Position(
                    symbol=leg["symbol"],
                    account=account,
                    shares=0,
                    stock_cost_basis=0.0,
                    current_price=float(leg.get("underlying_price") or current_price(leg["symbol"]) or 0),
                )
                positions[(account, leg["symbol"])] = pos
            pos.option_legs.append(OptionLeg(
                description=f"{leg['option_type']} {leg['strike']} {leg['expiry']}",
                strike=float(leg["strike"]),
                expiry=leg["expiry"],
                option_type=leg["option_type"],
                quantity=-int(leg["contracts"]),
                premium_received=float(leg["premium_received"]),
                current_mark=float(leg["mark"]),
                dte=int(leg["dte"]),
            ))
            pos.current_price = float(leg.get("underlying_price") or pos.current_price)


def fallback_us_positions() -> dict[str, Any]:
    snapshot = load_snapshot()
    txns = load_account_transactions()
    pos_rows = load_position_csv()
    price_map = {row["symbol"]: row["price"] for row in pos_rows if row.get("asset_type", "").lower() == "equity"}
    cost_map = {
        row["symbol"]: safe_div(row["cost_basis_total"], row["qty"])
        for row in pos_rows if row.get("asset_type", "").lower() == "equity" and row.get("qty")
    }

    positions = _fallback_assigned_positions(snapshot, price_map, cost_map)
    _fallback_merge_reconstructed_legs(positions, txns)

    return {
        "positions": list(positions.values()),
        "balances": {"A": {}, "B": {}, "C": {}},
        "data_source": "SNAPSHOT (LIVE API UNAVAILABLE)",
        "warning": f"Using snapshot dated {snapshot.get('last_updated', 'unknown')} plus statement fallbacks.",
        "snapshot": snapshot,
        "transactions": txns,
    }


def schwab_source_choice(snapshot_mtime: float, txn_mtime: float) -> str:
    """Decide whether load_us_positions() should use the position snapshot
    or reconstructed transaction history for a Schwab account. Compares
    calendar DAY, not raw mtime seconds: snapshot and transactions files
    are normally written by the same reconcile.py batch run, seconds apart
    in either order, so a same-day snapshot is always preferred -- it
    carries Schwab's own real share counts, which reconstruction cannot
    produce at all. Only a snapshot that is missing, or from a strictly
    earlier calendar day than the transactions file (meaning real trades
    happened since the last snapshot was taken), falls back to
    reconstruction. Confirmed real bug, 2026-10-13: Account C's snapshot
    was written 31 seconds BEFORE its same-batch transactions file; a raw
    `snapshot_mtime >= txn_mtime` check flipped to "transactions" for that
    reason alone, and reconstruction (which has no equity-share tracking)
    reported TWLO's real 324 shares as 0, misclassifying a covered call
    as naked."""
    if snapshot_mtime < 0:
        return "transactions"
    if txn_mtime <= 0:
        return "snapshot"
    snapshot_date = datetime.fromtimestamp(snapshot_mtime).date()
    txn_date = datetime.fromtimestamp(txn_mtime).date()
    return "snapshot" if snapshot_date >= txn_date else "transactions"


def load_schwab_from_snapshot(account: str) -> list[Position] | None:
    """Build Positions directly from the current Schwab POSITION snapshot
    (data/positions/schwab_*.csv -- the same canonical file reconcile.py
    maintains), instead of reconstructing from transaction history. Real
    advantage over reconstruct_positions_from_transactions(): this file
    carries Schwab's own live Cost Basis (-> premium_received) and Mkt Val
    (-> current_mark) per leg directly -- no live option-chain fetch needed,
    and no risk of a stale transaction file showing a contract as still
    open (or a share count as 0) when the broker's own current snapshot
    says otherwise. Confirmed real case, 2026-10-12: Account A's
    transactions file was 10 days stale and showed OKTA with 0 shares
    against 6 short calls (looked like naked calls, 15x loss); the SAME
    day's position snapshot (4:23 PM) showed the true figure -- 600 shares,
    fully covering all 6 contracts -- a covered-call position, not a naked
    one. Returns None if no snapshot file exists for this account."""
    lines = _read_schwab_snapshot_lines(account)
    if lines is None:
        return None

    header_idx = next((i for i, l in enumerate(lines) if '"Symbol"' in l and "Asset Type" in l), None)
    if header_idx is None:
        return None

    equity_map: dict[str, Position] = {}
    ctx = (equity_map, account)  # (equity_map, account) -- constant per row, bundled to stay <=4 params
    reader = csv.DictReader(lines[header_idx:])
    for row in reader:
        raw_sym = (row.get("Symbol") or "").strip().strip('"')
        if not raw_sym or raw_sym.lower().startswith(("account", "cash")):
            continue
        asset_type = (row.get("Asset Type") or "").strip().strip('"').lower()
        try:
            qty = float((row.get("Qty (Quantity)") or "0").strip().strip('"').replace(",", ""))
        except ValueError:
            continue
        price = _clean_money(row.get("Price") or "0")

        if asset_type in ("equity", "stock"):
            _apply_schwab_equity_row(ctx, raw_sym, qty, price)
        elif asset_type == "option" and qty < 0:
            _apply_schwab_option_row(ctx, raw_sym, qty, row)

    result = [p for p in equity_map.values() if p.option_legs]
    return result if result else None


def _read_schwab_snapshot_lines(account: str) -> list[str] | None:
    filename = _SCHWAB_SNAPSHOT_FILE.get(account)
    if not filename:
        return None
    path = DATA_DIR / "positions" / filename
    if not path.exists():
        return None
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return f.readlines()
    except Exception:
        return None


def _apply_schwab_equity_row(ctx: tuple[dict[str, Position], str], raw_sym: str, qty: float, price: float) -> None:
    equity_map, account = ctx
    if raw_sym not in equity_map:
        equity_map[raw_sym] = Position(
            symbol=raw_sym, account=account, shares=0,
            stock_cost_basis=0, current_price=price, option_legs=[],
        )
    equity_map[raw_sym].shares = int(qty) if qty > 0 else 0
    equity_map[raw_sym].current_price = price


def _apply_schwab_option_row(ctx: tuple[dict[str, Position], str], raw_sym: str, qty: float, row: dict) -> None:
    equity_map, account = ctx
    m = _SCHWAB_OPT_SYMBOL.match(raw_sym)
    if not m:
        return
    underlying, expiry_str, strike_str, opt_char = m.groups()
    expiry = datetime.strptime(expiry_str, "%m/%d/%Y").date()
    dte = (expiry - date.today()).days
    if dte < 0:
        return  # expired -- not an open position

    if underlying not in equity_map:
        equity_map[underlying] = Position(
            symbol=underlying, account=account, shares=0,
            stock_cost_basis=0, current_price=0, option_legs=[],
        )

    leg = OptionLeg(
        description=raw_sym,
        option_type="CALL" if opt_char == "C" else "PUT",
        strike=float(strike_str),
        expiry=expiry.isoformat(),
        dte=dte,
        quantity=-abs(qty),
        premium_received=abs(_clean_money(row.get("Cost Basis") or "0")),
        current_mark=abs(_clean_money(row.get("Mkt Val (Market Value)") or "0")),
    )
    equity_map[underlying].option_legs.append(leg)


_TXN_FILE_PATTERN_MAP = {
    "A": "Individual_XXX232_Transactions_*.csv",
    "B": "Contributory_XXX275_Transactions_*.csv",
    "C": "Designated_Bene_Individual_XXX634_Transactions_*.csv",
}


def _find_latest_txn_file(account: str):
    """Latest Individual_XXX###_Transactions_*.csv for `account` -- prefers
    data/positions/ (current, per the file contract), falls back to
    data/statements/. Newest by mtime wins. None if no pattern/file at all."""
    pattern = _TXN_FILE_PATTERN_MAP.get(account)
    if not pattern:
        return None
    txn_files = list((DATA_DIR / "positions").glob(pattern)) + list(STATEMENTS_DIR.glob(pattern))
    if not txn_files:
        return None
    return max(txn_files, key=lambda x: x.stat().st_mtime)


def _txn_row_amount(row: dict) -> float:
    raw = row.get("Amount", "").strip().strip('"').replace("$", "").replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _net_contracts_from_txn_csv(txn_file) -> tuple[dict, dict]:
    """Read one transaction CSV and net STO/BTC/Assigned/Expired rows into
    per-underlying {contract_symbol: net_quantity} plus real per-contract
    premium received (STO credits add, BTC debits reduce -- a partial close
    reduces the basis remaining on the still-open quantity; no live fetch
    needed, this is exactly what the broker already recorded)."""
    positions_dict = defaultdict(lambda: {"contracts": defaultdict(int)})
    premium_by_contract: dict[str, float] = defaultdict(float)

    with open(txn_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            action = row.get("Action", "").strip('"')
            symbol = row.get("Symbol", "").strip('"')
            qty_str = row.get("Quantity", "").strip('"')

            if not qty_str or not symbol:
                continue
            try:
                qty = int(qty_str)
            except ValueError:
                continue

            # Parse option symbol (skip equity)
            opt_match = re.match(r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$", symbol)
            if not opt_match:
                continue
            underlying = opt_match.group(1)

            if "Sell to Open" in action or "STO" in action:
                positions_dict[underlying]["contracts"][symbol] += qty
                premium_by_contract[symbol] += abs(_txn_row_amount(row))
            elif "Buy to Close" in action or "BTC" in action:
                positions_dict[underlying]["contracts"][symbol] -= qty
                premium_by_contract[symbol] -= abs(_txn_row_amount(row))
            elif "Assigned" in action or "Expired" in action:
                # short option closed by assignment/expiration — net it out
                positions_dict[underlying]["contracts"][symbol] -= abs(qty)

    return positions_dict, premium_by_contract


def _build_leg_from_contract(contract_sym: str, qty: int, premium_by_contract: dict) -> tuple[OptionLeg, str, float, str] | None:
    """One still-open contract -> (OptionLeg, expiry_iso, strike, opt_type),
    or None if expired or unparseable. Field names must match
    analysis.pnl.Position/OptionLeg exactly -- this call drifted from the
    real schema (cost_basis -> stock_cost_basis, a premium_received kwarg
    Position never had, qty -> quantity, and OptionLeg's required
    description was missing entirely) and silently returned None for every
    Schwab account on every call ever since, via the bare except this
    function's caller wraps. Confirmed live 2026-10-04:
    reconstruct_positions_from_transactions("A") raised TypeError:
    Position.__init__() got an unexpected keyword argument 'cost_basis' on
    every single call -- this is what made run_screener/scan_sector/
    screen_new_entries tag real Schwab-held names (AXON, NU) as "not
    currently held," not a one-ticker fluke."""
    opt_match = re.match(r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$", contract_sym)
    if not opt_match:
        return None
    expiry_str = opt_match.group(2)
    strike = float(opt_match.group(3))
    opt_type = "CALL" if opt_match.group(4) == "C" else "PUT"
    expiry = datetime.strptime(expiry_str, "%m/%d/%Y").date()
    dte = (expiry - date.today()).days
    if dte < 0:
        return None  # expired — no longer an open position

    leg = OptionLeg(
        description=contract_sym,
        option_type=opt_type,
        strike=strike,
        expiry=expiry.isoformat(),
        dte=dte,
        quantity=-abs(qty),  # short (negative), matching OptionLeg's own convention
        premium_received=max(0.0, premium_by_contract.get(contract_sym, 0.0)),
        current_mark=0,  # filled in below via a live option-chain lookup
    )
    return leg, expiry.isoformat(), strike, opt_type


def _build_positions_from_net_contracts(positions_dict: dict, premium_by_contract: dict, account: str):
    """Net contract quantities -> (list[Position], pending_mark_lookups) for
    _fill_current_marks(). Only NET-POSITIVE contracts are genuine open
    shorts (STO not yet closed); net-negative is an orphaned Buy-to-Close
    whose Sell-to-Open predates this file window (phantom)."""
    result: list[Position] = []
    pending_mark_lookups: list[tuple[str, str, float, str, "OptionLeg"]] = []  # (symbol, expiry, strike, opt_type, leg)

    for underlying in sorted(positions_dict.keys()):
        contracts = positions_dict[underlying]["contracts"]
        live_contracts = {sym: qty for sym, qty in contracts.items() if qty > 0}
        if not live_contracts:
            continue

        pos = Position(
            symbol=underlying, shares=0, stock_cost_basis=0, current_price=0,
            account=account, option_legs=[],
        )
        for contract_sym, qty in live_contracts.items():
            built = _build_leg_from_contract(contract_sym, qty, premium_by_contract)
            if built is None:
                continue
            leg, expiry_iso, strike, opt_type = built
            pos.option_legs.append(leg)
            pending_mark_lookups.append((underlying, expiry_iso, strike, opt_type, leg))

        if pos.option_legs:
            result.append(pos)

    return result, pending_mark_lookups


def reconstruct_positions_from_transactions(account: str = "A") -> list[Position] | None:
    """
    Reconstruct current positions from transaction history (fallback when live API unavailable).
    Parses Individual_XXX###_Transactions_*.csv, calculates net position state.
    Returns list of Position objects or None if transactions unavailable.
    """
    from report_utils import _fill_current_marks

    txn_file = _find_latest_txn_file(account)
    if not txn_file:
        return None

    try:
        positions_dict, premium_by_contract = _net_contracts_from_txn_csv(txn_file)
        result, pending_mark_lookups = _build_positions_from_net_contracts(positions_dict, premium_by_contract, account)
        _fill_current_marks(pending_mark_lookups)
        return result if result else None
    except Exception:
        return None
