"""
Realized P&L, split at OPTION level and EQUITY level, by month, per account,
across all four brokerages.

Why two levels: the trader's $1.2M/year objective is tracked at the OPTION
level specifically (premium income from selling puts/calls). Equity P&L
(gains/losses on shares — mostly acquired via put assignment, disposed via
call assignment, i.e. a classic options-wheel strategy) is supplementary,
not what the objective is measured against.

Method: FIFO-match every closing transaction (Buy-to-Close/Expired/Assigned
for options; Sell for equity) against its originating opening transaction
(Sell-to-Open for options; Buy for equity), and attribute the realized gain
to the CLOSE date's month — not a simple same-month cash-flow sum, which
misattributes P&L for positions that open and close in different months.

Important, hard-won correction baked into this module: option ASSIGNMENT
is a closing event (the seller keeps the full premium, no further debit) —
earlier option-level P&L work this session omitted this, leaving assigned
options as permanently "still open" and understating realized P&L. Fixed
here for Schwab/Fidelity/Vanguard.

Reuses the file-finders and low-level helpers from update_snapshot.py rather
than duplicating them — this is a read-only reporting layer on top of that
data, not a replacement for it.

Known limitation: Vanguard's OPTION-side Symbol field is blank on most rows
after the first leg of a contract (confirmed by direct file inspection this
session), so Vanguard is excluded from OPTION-level FIFO matching — including
it would risk silently wrong contract pairings. Vanguard's EQUITY-side Symbol
field is a different, reliably-populated field and IS included.

Robinhood: no assignment mechanism was found in this data at all — expect
near-zero equity-level activity there; this is an accurate reflection of the
data, not a gap.
"""

import os
import sys
import csv
import re
from collections import defaultdict, deque
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_snapshot import (
    find_schwab_transactions, find_fidelity_transactions,
    find_vanguard_transactions, find_robinhood_transactions,
    _clean, _parse_amount, _parse_date, _FIDELITY_ACCOUNT_LABELS,
)


# ---------------------------------------------------------------------------
# Unified FIFO engine — works for both options (qty=contracts) and equity
# (qty=shares) because every source amount is already naturally signed
# (a credit/proceeds is positive, a debit/cost is negative in the raw data).
# realized = open_amount_per_unit + close_amount_per_unit, matched FIFO,
# with partial-lot consumption (needed for equity: a sell can span multiple
# differently-sized buy lots; options only ever trade whole units but the
# same logic handles that fine too).
# ---------------------------------------------------------------------------

def fifo_realize(events):
    """events: list of (date, key, side, qty, amount) — side 'open'/'close'.
    Returns (monthly_realized: dict[str, float], monthly_closed_count: dict[str, int],
    unmatched_qty: float, still_open_qty: float)."""
    events = sorted(events, key=lambda e: e[0])
    queues = defaultdict(deque)  # key -> deque of [remaining_qty, per_unit_amount]
    monthly = defaultdict(float)
    monthly_n = defaultdict(int)
    unmatched_qty = 0.0

    for d, key, side, qty, amount in events:
        if qty <= 0:
            continue
        per_unit = amount / qty
        if side == "open":
            queues[key].append([qty, per_unit])
        else:
            remaining = qty
            month = d.strftime("%Y-%m")
            matched_any = False
            while remaining > 1e-9 and queues[key]:
                lot = queues[key][0]
                take = min(remaining, lot[0])
                monthly[month] += (lot[1] + per_unit) * take
                lot[0] -= take
                remaining -= take
                matched_any = True
                if lot[0] <= 1e-9:
                    queues[key].popleft()
            if matched_any:
                monthly_n[month] += 1
            if remaining > 1e-9:
                unmatched_qty += remaining

    still_open_qty = sum(lot[0] for q in queues.values() for lot in q)
    return monthly, monthly_n, unmatched_qty, still_open_qty


def _qty(row, col, default=1.0):
    try:
        v = float(_clean(row.get(col) or str(default)) or str(default))
        return abs(v)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Schwab — both levels from one file
# ---------------------------------------------------------------------------

_SCHWAB_OPT_OPEN = {"Sell to Open"}
_SCHWAB_OPT_CLOSE = {"Buy to Close", "Expired", "Assigned"}


def schwab_events(path):
    option_events, equity_events = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            action = _clean(row.get("Action", ""))
            symbol = _clean(row.get("Symbol", ""))
            d = _parse_date(_clean(row.get("Date", "")))
            if not symbol or not d:
                continue
            qty = _qty(row, "Quantity")
            amount = _parse_amount(row.get("Amount", "0"))

            if action in _SCHWAB_OPT_OPEN:
                option_events.append((d, symbol, "open", qty, amount))
            elif action in _SCHWAB_OPT_CLOSE:
                # Expired/Assigned carry no debit — full credit already realized.
                option_events.append((d, symbol, "close", qty, amount if action == "Buy to Close" else 0.0))
            elif action == "Buy":
                equity_events.append((d, symbol, "open", qty, amount))
            elif action == "Sell":
                equity_events.append((d, symbol, "close", qty, amount))
    return option_events, equity_events


# ---------------------------------------------------------------------------
# Fidelity — both levels from one file, split by sub-account via Account Number
# ---------------------------------------------------------------------------

def fidelity_events(path):
    """Returns dict[account_label] -> (option_events, equity_events)."""
    by_account = defaultdict(lambda: ([], []))
    with open(path, newline="", encoding="utf-8-sig") as f:
        lines = [l for l in f if l.strip()]  # leading blank line(s) before the real header
    for row in csv.DictReader(lines):
        acct = _FIDELITY_ACCOUNT_LABELS.get(_clean(row.get("Account Number") or ""))
        if not acct:
            continue
        desc = (row.get("Action") or "").strip().upper()
        symbol = (row.get("Symbol") or "").strip()
        d = _parse_date(_clean(row.get("Run Date") or ""))
        if not d or not symbol:
            continue
        qty = _qty(row, "Quantity")
        amount = _parse_amount(row.get("Amount ($)") or "0")
        opt_events, eq_events = by_account[acct]

        if desc.startswith("YOU SOLD OPENING TRANSACTION"):
            opt_events.append((d, symbol, "open", qty, amount))
        elif desc.startswith("YOU BOUGHT CLOSING TRANSACTION"):
            opt_events.append((d, symbol, "close", qty, amount))
        elif desc.startswith("ASSIGNED AS OF"):
            opt_events.append((d, symbol, "close", qty, 0.0))
        elif desc.startswith("YOU BOUGHT ASSIGNED PUTS"):
            eq_events.append((d, symbol, "open", qty, amount))
        elif desc.startswith("YOU SOLD ASSIGNED CALLS"):
            eq_events.append((d, symbol, "close", qty, amount))
    return by_account


# ---------------------------------------------------------------------------
# Vanguard — EQUITY level only (option side excluded, see module docstring).
# Section 2 of the export (see parse_vanguard_transactions in update_snapshot.py
# for why this file has 3 concatenated sections).
# ---------------------------------------------------------------------------

_VANGUARD_TXN_HEADER = "Account Number,Trade Date,Settlement Date,Transaction Type"


def vanguard_equity_events(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(_VANGUARD_TXN_HEADER)), None)
    if start is None:
        return []
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].strip()), len(lines))

    events = []
    for row in csv.DictReader(lines[start:end]):
        ttype = (row.get("Transaction Type") or "").strip().lower()
        symbol = (row.get("Symbol") or "").strip()
        d = _parse_date(_clean(row.get("Trade Date") or ""))
        if not d or not symbol:
            continue
        qty = _qty(row, "Shares")
        amount = _parse_amount(row.get("Net Amount") or "0")
        if ttype == "buy":
            events.append((d, symbol, "open", qty, amount))
        elif ttype == "sell":
            events.append((d, symbol, "close", qty, amount))
    return events


# ---------------------------------------------------------------------------
# Robinhood — both levels from one full-history file (see module docstring —
# no assignment mechanism confirmed, so no special-case needed there).
# ---------------------------------------------------------------------------

_RH_DESC = re.compile(r"^(\w+)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(Put|Call)\s+\$([\d.]+)", re.IGNORECASE)


def robinhood_events(path):
    option_events, equity_events = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            trans_code = (row.get("Trans Code") or "").strip()
            d = _parse_date((row.get("Activity Date") or "").strip())
            if not d:
                continue
            qty = _qty(row, "Quantity")
            raw_amount = (row.get("Amount") or "").strip().replace("(", "-").replace(")", "")
            amount = _parse_amount(raw_amount)

            if trans_code in ("STO", "BTC"):
                desc = (row.get("Description") or "").strip().replace("\n", " ")
                m = _RH_DESC.match(desc)
                if not m:
                    continue
                key = f"{m.group(1).upper()} {m.group(2)} {m.group(3).upper()} {m.group(4)}"
                option_events.append((d, key, "open" if trans_code == "STO" else "close", qty, amount))
            elif trans_code in ("Buy", "Sell"):
                instrument = (row.get("Instrument") or "").strip()
                if not instrument:
                    continue
                equity_events.append((d, instrument, "open" if trans_code == "Buy" else "close", qty, amount))
    return option_events, equity_events


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _print_account(label, option_events, equity_events, note=""):
    print(f"\n{label}{('  — ' + note) if note else ''}")
    opt_monthly, opt_n, opt_unmatched, opt_open = fifo_realize(option_events) if option_events is not None else ({}, {}, 0, 0)
    eq_monthly, eq_n, eq_unmatched, eq_open = fifo_realize(equity_events) if equity_events is not None else ({}, {}, 0, 0)

    months = sorted(set(opt_monthly) | set(eq_monthly))
    months = [m for m in months if m.startswith("2026")]
    opt_ytd = eq_ytd = 0.0
    print(f"  {'Month':8}{'Option P&L':>14}{'Equity P&L':>14}{'Total':>14}")
    for m in months:
        o, e = opt_monthly.get(m, 0.0), eq_monthly.get(m, 0.0)
        opt_ytd += o
        eq_ytd += e
        print(f"  {m:8}{o:>14,.2f}{e:>14,.2f}{o + e:>14,.2f}")
    print(f"  {'YTD':8}{opt_ytd:>14,.2f}{eq_ytd:>14,.2f}{opt_ytd + eq_ytd:>14,.2f}")
    if option_events is not None:
        print(f"  option: unmatched qty {opt_unmatched:.0f}, still-open qty {opt_open:.0f}")
    if equity_events is not None:
        print(f"  equity: unmatched qty {eq_unmatched:.0f}, still-open qty {eq_open:.0f}")
    return opt_ytd, eq_ytd


def main():
    grand_opt = grand_eq = 0.0

    print("=" * 78)
    print("SCHWAB")
    print("=" * 78)
    for label, path in find_schwab_transactions().items():
        opt_ev, eq_ev = schwab_events(path)
        o, e = _print_account(label, opt_ev, eq_ev, os.path.basename(path))
        grand_opt += o
        grand_eq += e

    print("\n" + "=" * 78)
    print("FIDELITY")
    print("=" * 78)
    for person, path in find_fidelity_transactions().items():
        for acct, (opt_ev, eq_ev) in fidelity_events(path).items():
            o, e = _print_account(acct, opt_ev, eq_ev, os.path.basename(path))
            grand_opt += o
            grand_eq += e

    print("\n" + "=" * 78)
    print("VANGUARD — option-level excluded (unreliable contract identity in this")
    print("export — see module docstring); equity-level included.")
    print("=" * 78)
    vanguard_file = find_vanguard_transactions()
    if vanguard_file:
        eq_ev = vanguard_equity_events(vanguard_file)
        o, e = _print_account("Vanguard (Rahul)", None, eq_ev, os.path.basename(vanguard_file))
        grand_opt += o  # o is 0.0 here since option_events is None
        grand_eq += e

    print("\n" + "=" * 78)
    print("ROBINHOOD")
    print("=" * 78)
    for label, path in find_robinhood_transactions().items():
        opt_ev, eq_ev = robinhood_events(path)
        o, e = _print_account(label, opt_ev, eq_ev, os.path.basename(path))
        grand_opt += o
        grand_eq += e

    print("\n" + "=" * 78)
    print("GRAND TOTAL — ALL ACCOUNTS")
    print("=" * 78)
    print(f"  Option-level total (tracks the $1.2M objective): ${grand_opt:,.2f}")
    print(f"  Equity-level total (supplementary):               ${grand_eq:,.2f}")
    print(f"  Combined:                                         ${grand_opt + grand_eq:,.2f}")
    print("\n  Note: Vanguard option-level and any account's pre-file-history")
    print("  positions are excluded/undercounted where flagged above — this total")
    print("  is a floor, not a guaranteed-complete figure.")


if __name__ == "__main__":
    main()
