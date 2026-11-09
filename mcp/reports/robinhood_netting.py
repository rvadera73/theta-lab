"""
Shared option-transaction netting primitive + Robinhood transaction-log
parser. See docs/design/adr/0003-robinhood-position-ingestion.md.

Two callers:
  - scripts/open_positions_loader_v2.py's `_calculate_open_positions()` --
    the existing all-broker, ticker/count-level netter. It now calls
    `classify_action()` below instead of inlining the same decision chain,
    so there is exactly one implementation of "does this transaction row
    open or close a contract, and by how much."
  - mcp/reports/report_utils.py's `load_robinhood_positions()` -- the new
    Robinhood-specific entry point that reads one real transaction-log CSV
    directly and returns full per-leg detail (not just a ticker), for
    accounts D/E in `load_us_positions()`.

`classify_action()` is a byte-for-byte port of open_positions_loader_v2.py's
original inline chain (same token lists, same sign convention) -- it already
handles both Schwab/Fidelity/Vanguard's English action strings ("Sell to
Open", "Buy to Close", ...) and Robinhood's Trans Code abbreviations
(STO/BTC/BTO/STC) in one chain, because the original code already did. It is
genuinely broker-agnostic, not Robinhood-specific -- the Robinhood-only
parsing (CSV format, option-description regex, Trans Code normalization)
lives separately, below.
"""

from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Shared, broker-agnostic netting decision -- ported verbatim from
# scripts/open_positions_loader_v2.py's _calculate_open_positions (original
# inline chain, ~lines 867-883).
# ---------------------------------------------------------------------------

def classify_action(action: str, qty: float, source: str = "") -> tuple[float, bool]:
    """Classify one transaction row's effect on a contract's net open quantity.

    Returns (signed_qty_delta, is_opening):
      - signed_qty_delta follows the original sign convention: positive for
        SELL/STC/STO/SOLD-direction rows, negative for BUY/BTC/BTO/BOUGHT-
        direction rows (a running sum across a contract's rows gives the
        original algorithm's net_qty).
      - is_opening flags whether THIS row itself is an opening transaction
        (used to detect orphaned-close-only groups with no opening leg in
        the file -- a partial/YTD export symptom).
    """
    action_u = (action or "").upper()

    is_opening = False
    if source == "position_file":
        is_opening = True
    elif any(tok in action_u for tok in
             ("SELL", "OPEN", "STO", "BTO", "SOLD", "BOUGHT OPENING", "SOLD OPENING")):
        is_opening = True

    if any(tok in action_u for tok in ("SELL", "STC", "STO", "SOLD")):
        delta = qty
    elif any(tok in action_u for tok in ("BUY", "BTC", "BTO", "BOUGHT")):
        delta = -qty
    elif qty < 0:
        delta = -qty
    else:
        delta = qty
    return delta, is_opening


# ---------------------------------------------------------------------------
# Robinhood transaction-log parsing -- the real export format (confirmed
# against data/positions/robinhood_rahul_individual.csv and
# robinhood_rahul_traditional.csv):
#   "Activity Date","Process Date","Settle Date","Instrument","Description",
#   "Trans Code","Quantity","Price","Amount"
# Option rows' Description looks like "AAPL 1/17/2025 Call $200.00". Some
# non-option rows (e.g. an option-assignment's resulting stock Buy) carry a
# multi-line Description (embedded newlines inside the quoted CSV field) --
# real `csv` module parsing (not naive line-splitting) is required.
# ---------------------------------------------------------------------------

_OPTION_DESC_RE = re.compile(
    r"^([A-Z]+)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(Call|Put)\s+\$([\d.]+)\s*$", re.IGNORECASE
)

# Trans Codes that extinguish a contract outright (assignment/exercise) --
# not covered by classify_action()'s original token list (which only knows
# STO/BTC/BTO/STC and the Schwab/Fidelity English-string vocabulary). Found
# live in the real individual-account export: a DKNG $35 put sold-to-open
# 1/14/2026, then OASGN (assigned) 10/14/2026 with no accompanying
# price/amount. Normalized to "BTC" (closing) before classify_action() ever
# sees it, so the shared decision chain itself stays byte-for-byte unchanged.
_CLOSING_OVERRIDE_CODES = ("OASGN", "ASSIGN", "EXPIR", "EXERC")


def _normalize_trans_code(raw_code: str) -> str:
    code_u = (raw_code or "").strip().upper()
    if any(tok in code_u for tok in _CLOSING_OVERRIDE_CODES):
        return "BTC"
    return code_u


def _parse_amount(raw: str) -> float:
    s = (raw or "").strip().strip('"')
    if not s:
        return 0.0
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace("$", "").replace(",", "").strip()
    if not s:
        return 0.0
    try:
        val = float(s)
    except ValueError:
        return 0.0
    return -val if negative else val


def _parse_qty(raw: str) -> float:
    s = (raw or "").strip().strip('"').replace(",", "")
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_date(raw: str) -> Optional[date]:
    s = (raw or "").strip().strip('"')
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_robinhood_transaction_csv(csv_path: str) -> list[dict[str, Any]]:
    """Read a real Robinhood transaction-log export and return one
    normalized dict per OPTION transaction row (non-option rows -- ACH,
    INT, CDIV, plain equity Buy/Sell, etc. -- are not option contracts and
    are skipped; see ADR 0003's "out of scope" note on Robinhood equity
    netting).

    Each returned row: {date, ticker, strike, expiry (YYYY-MM-DD),
    option_type, trans_code (normalized), raw_trans_code, quantity, amount}.
    """
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        raw_rows = list(reader)

    rows: list[dict[str, Any]] = []
    for raw in raw_rows:
        description = (raw.get("Description") or "").strip()
        m = _OPTION_DESC_RE.match(description)
        if not m:
            continue  # not an option transaction row

        ticker, date_str, cp, strike_s = m.groups()
        txn_date = _parse_date(raw.get("Activity Date", ""))
        try:
            expiry_date = datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            continue
        if txn_date is None:
            continue

        raw_code = raw.get("Trans Code", "")
        rows.append({
            "date": txn_date,
            "ticker": ticker.upper(),
            "strike": float(strike_s),
            "expiry": expiry_date.isoformat(),
            "option_type": "CALL" if cp.lower() == "call" else "PUT",
            "trans_code": _normalize_trans_code(raw_code),
            "raw_trans_code": raw_code,
            "quantity": _parse_qty(raw.get("Quantity", "")),
            "amount": _parse_amount(raw.get("Amount", "")),
        })
    return rows


def net_robinhood_option_legs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Net a Robinhood transaction log's option rows (from
    `parse_robinhood_transaction_csv`) into open per-contract legs, using
    the shared `classify_action()` decision for each row.

    Returns one dict per still-open contract: {ticker, strike, expiry,
    option_type, quantity (signed: negative = net short/STO-direction,
    positive = net long/BTO-direction -- matches analysis.pnl.OptionLeg's
    own convention), net_credit (real cash collected to date -- Robinhood's
    own Amount column is already signed credit-positive/debit-negative, so
    summing it per contract is exact, no Schwab-style max(0, amount)
    heuristic needed), opened (earliest opening row's date, ISO string).
    Expired contracts (expiry in the past) and fully-closed or orphaned
    (net zero, or close-only with no opening row in this file) contracts
    are excluded.
    """
    groups: dict[tuple[str, float, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["ticker"], row["strike"], row["expiry"], row["option_type"])
        groups.setdefault(key, []).append(row)

    today = date.today()
    legs: list[dict[str, Any]] = []
    for (ticker, strike, expiry, option_type), group_rows in groups.items():
        expiry_date = date.fromisoformat(expiry)
        if expiry_date < today:
            continue  # already expired -- not an open position

        net_qty = 0.0
        has_opening = False
        net_credit = 0.0
        open_dates: list[date] = []

        for row in group_rows:
            delta, is_opening = classify_action(row["trans_code"], row["quantity"])
            net_qty += delta
            net_credit += row["amount"]
            if is_opening:
                has_opening = True
                open_dates.append(row["date"])

        if net_qty == 0 or not has_opening:
            continue  # closed out, or an orphaned close with no opening leg in this file

        legs.append({
            "ticker": ticker,
            "strike": strike,
            "expiry": expiry,
            "option_type": option_type,
            # net_qty > 0 means SELL/STO-direction dominates -> net short.
            # net_qty < 0 means BUY/BTO-direction dominates -> net long.
            "quantity": -abs(net_qty) if net_qty > 0 else abs(net_qty),
            "net_credit": round(net_credit, 2),
            "opened": min(open_dates).isoformat() if open_dates else None,
            "dte": (expiry_date - today).days,
        })

    return sorted(legs, key=lambda x: (x["dte"], x["ticker"]))
