"""
Parses ICICI Direct equity and FNO portfolio CSV exports into Position objects.

Equity file (account 9840): transaction history — computes net holdings + cost basis.
FNO file   (account 8170): open positions snapshot — reads qty, avg price, LTP directly.

Contract name format (FNO): OPT-{UNDERLYING}-{DD-Mon-YYYY}-{STRIKE}-{CE|PE}-E
"""

import csv
import glob
import os
import re
import yaml
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from analysis.pnl import Position, OptionLeg


# ---------------------------------------------------------------------------
# Paths (resolved relative to project root)
# ---------------------------------------------------------------------------

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data", "statements")
_INDIA_CONFIG = os.path.join(_PROJECT_ROOT, "data", "india_config.yaml")

def _find_statement_file(account_number: str) -> str | None:
    """Find the latest CSV in data/statements/ whose name contains the account number."""
    pattern = os.path.join(_DATA_DIR, f"*{account_number}*.csv")
    matches = sorted(glob.glob(pattern), reverse=True)  # latest first if multiple
    return matches[0] if matches else None


EQUITY_ACCOUNT = "7500069840"
FNO_ACCOUNT    = "7510078170"

# Resolved at import time; may be None if files don't exist yet
EQUITY_CSV = _find_statement_file(EQUITY_ACCOUNT) or os.path.join(_DATA_DIR, f"{EQUITY_ACCOUNT}_PortFolioEqtAll.csv")
FNO_CSV    = _find_statement_file(FNO_ACCOUNT)    or os.path.join(_DATA_DIR, f"{FNO_ACCOUNT}_FNOPortfolioDetails.csv")


# ---------------------------------------------------------------------------
# india_config.yaml loader
# ---------------------------------------------------------------------------

def load_india_config() -> dict:
    """Returns parsed india_config.yaml or empty dict on failure."""
    try:
        with open(_INDIA_CONFIG) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# FNO contract name parser
# ---------------------------------------------------------------------------
# OPT-CNXBAN-26-May-2026-52500-P-E
# OPT-NIFTY-05-May-2026-23450-P-E
_FNO_RE = re.compile(
    r"OPT-(?P<underlying>[A-Z0-9]+)-"
    r"(?P<dd>\d{2})-(?P<mon>[A-Za-z]+)-(?P<yyyy>\d{4})-"
    r"(?P<strike>[\d.]+)-(?P<right>[CP])-E$"
)


def _parse_fno_contract(contract: str) -> dict | None:
    """Parse a Breeze/ICICI FNO contract string into components."""
    m = _FNO_RE.match(contract.strip())
    if not m:
        return None
    try:
        expiry = datetime.strptime(
            f"{m['dd']}-{m['mon']}-{m['yyyy']}", "%d-%b-%Y"
        ).date()
    except ValueError:
        return None
    return {
        "underlying": m["underlying"],
        "expiry":     expiry,
        "strike":     float(m["strike"]),
        "right":      "CALL" if m["right"] == "C" else "PUT",
    }


def _dte(expiry: date) -> int:
    return (expiry - date.today()).days


# ---------------------------------------------------------------------------
# Equity CSV parser — transaction history → net holdings
# ---------------------------------------------------------------------------

def parse_equity_positions(csv_path: str | None = None) -> dict[str, dict]:
    """
    Reads ICICI equity transaction CSV and returns net holdings dict:
        {symbol: {"qty": int, "avg_cost": float, "name": str}}
    Only symbols with qty > 0 are returned.
    """
    if csv_path is None:
        csv_path = _find_statement_file(EQUITY_ACCOUNT) or EQUITY_CSV
    holdings: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"qty": 0, "cost_total": 0.0, "name": ""}
    )

    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sym    = row.get("Stock Symbol", "").strip()
                action = row.get("Action", "").strip()
                name   = row.get("Company Name", "").strip()
                try:
                    qty   = int(row.get("Quantity", 0))
                    price = float(row.get("Transaction Price", 0))
                except (ValueError, TypeError):
                    continue

                if not sym or action not in ("Buy", "Sell"):
                    continue

                holdings[sym]["name"] = name
                if action == "Buy":
                    holdings[sym]["qty"]        += qty
                    holdings[sym]["cost_total"]  += qty * price
                else:
                    holdings[sym]["qty"]        -= qty
                    holdings[sym]["cost_total"]  -= qty * price

    except FileNotFoundError:
        return {}

    result = {}
    for sym, h in holdings.items():
        if h["qty"] > 0:
            result[sym] = {
                "qty":      h["qty"],
                "avg_cost": h["cost_total"] / h["qty"],
                "name":     h["name"],
            }
    return result


# ---------------------------------------------------------------------------
# FNO CSV parser — open position snapshot
# ---------------------------------------------------------------------------

def parse_fno_positions(csv_path: str | None = None) -> list[dict]:
    """
    Reads ICICI FNO portfolio snapshot and returns open option legs:
        [{"underlying", "expiry", "strike", "right", "qty", "avg_price", "ltp",
          "unrealized_pnl", "realized_pnl"}]
    Skips rows with qty == 0 (closed positions in history).
    """
    if csv_path is None:
        csv_path = _find_statement_file(FNO_ACCOUNT) or FNO_CSV
    legs = []
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = None
            for row in reader:
                if not row or not row[0].strip():
                    continue
                # Header row
                if row[0].strip().lower() in ("futures", "options"):
                    continue
                if row[0].strip().startswith("Contract"):
                    header = [c.strip() for c in row]
                    continue
                if header is None:
                    continue

                row_dict = dict(zip(header, [c.strip() for c in row]))
                contract = row_dict.get("Contract", "")
                if not contract.startswith("OPT-"):
                    continue

                try:
                    qty = int(row_dict.get("Open Position Qty", 0) or 0)
                except (ValueError, TypeError):
                    qty = 0

                if qty == 0:
                    continue

                parsed = _parse_fno_contract(contract)
                if not parsed:
                    continue

                try:
                    avg_price = float(row_dict.get("Open Position Avg. Price", 0) or 0)
                    ltp       = float(row_dict.get("LTP", 0) or 0)
                    unrealized = float(row_dict.get("Profit/Loss Unrealized", 0) or 0)
                    realized   = float(row_dict.get("Profit/Loss Realized", 0) or 0)
                except (ValueError, TypeError):
                    avg_price = ltp = unrealized = realized = 0.0

                legs.append({
                    **parsed,
                    "qty":           qty,
                    "avg_price":     avg_price,
                    "ltp":           ltp,
                    "unrealized_pnl": unrealized,
                    "realized_pnl":  realized,
                })

    except FileNotFoundError:
        return []

    return legs


# ---------------------------------------------------------------------------
# Build Position objects from static files + india_config.yaml
# ---------------------------------------------------------------------------

def build_positions_from_statements(
    india_cfg: dict | None = None,
) -> list[Position]:
    """
    Constructs Position objects from local CSV exports.
    Uses india_config.yaml for exit_trigger metadata if provided.
    """
    if india_cfg is None:
        india_cfg = load_india_config()

    core_symbols = set(india_cfg.get("core_portfolio", []))
    exit_map: dict[str, dict] = {
        e["icici_symbol"]: e
        for e in india_cfg.get("exit_triggers", [])
        if "icici_symbol" in e
    }

    equity = parse_equity_positions()
    fno_legs = parse_fno_positions()

    # Group FNO legs by underlying
    legs_by_underlying: dict[str, list[OptionLeg]] = defaultdict(list)
    for leg in fno_legs:
        underlying = leg["underlying"]
        is_short = leg["qty"] < 0
        abs_qty  = abs(leg["qty"])
        premium  = leg["avg_price"] * abs_qty if is_short else 0.0
        mark     = leg["ltp"]       * abs_qty if is_short else 0.0
        dte      = _dte(leg["expiry"])
        expiry_str = leg["expiry"].strftime("%Y-%m-%d")

        option_leg = OptionLeg(
            description=f"{leg['right']} {leg['strike']} {expiry_str}",
            strike=leg["strike"],
            expiry=expiry_str,
            option_type=leg["right"],
            quantity=leg["qty"],
            premium_received=premium,
            current_mark=mark,
            dte=dte,
        )
        legs_by_underlying[underlying].append(option_leg)

    positions: list[Position] = []
    seen: set[str] = set()

    # Equity positions (with optional FNO legs)
    for sym, h in equity.items():
        pos = Position(
            symbol=sym,
            account="INDIA",
            shares=h["qty"],
            stock_cost_basis=h["avg_cost"],
            current_price=h["avg_cost"],  # live price fetched separately if available
        )
        pos.option_legs = legs_by_underlying.get(sym, [])
        # Attach exit trigger metadata as custom attr (used in report rendering)
        pos._exit_trigger   = exit_map.get(sym)
        pos._is_core        = sym in core_symbols
        positions.append(pos)
        seen.add(sym)

    # Index-based FNO positions (NIFTY, CNXBAN, NIFSEL) — no equity leg
    for underlying, legs in legs_by_underlying.items():
        if underlying not in seen:
            pos = Position(
                symbol=underlying,
                account="INDIA",
                shares=0,
                stock_cost_basis=0.0,
                current_price=0.0,
            )
            pos.option_legs = legs
            pos._exit_trigger = None
            pos._is_core      = False
            positions.append(pos)
            seen.add(underlying)

    return positions
