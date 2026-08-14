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

Known limitation: Vanguard's OPTION-side Symbol field (and its free-text
Investment Name fallback) is blank on most option rows — not just "later
legs" of a contract, confirmed by direct inspection to include many first
legs too — so there is often no recoverable ticker/strike/expiry at all for
a given row. Vanguard is excluded from OPTION-level FIFO matching entirely;
no amount of matching cleverness fixes a value that isn't in the file.
Vanguard's EQUITY-side Symbol field is a different, reliably-populated
column and IS included.

Unrealized P&L is MARK-TO-MARKET throughout (current price vs. cost/credit
basis) — a deliberate choice, not "assume every open position eventually
realizes 100% of its premium." That optimistic alternative was considered
and rejected: this account's own realized history already includes hundreds
of early Buy-to-Close events, so "everything runs to expiration/assignment"
is not how this trader actually operates, and would overstate the true
picture. Mark-to-market is also what a brokerage's own unrealized-P&L
display shows, so it's the like-for-like comparison. The intended use of
the resulting deviation (large mark-to-market unrealized loss/gain on a
specific position) is diagnostic — a signal to check whether a strategy or
roll decision on that name is working, not a prediction of the final outcome.

Unrealized P&L (still-open option lots, marked to current market price via
mcp/reports/report_utils.py::option_market_price — already-proven code,
reused rather than rebuilt) is included for Schwab/Fidelity/Robinhood, the
same three brokers included in realized option-level P&L. Equity-level
unrealized (still-open share lots, marked to current price via
scripts/yahoo_price_fetcher.py — the same module the main unified report
already depends on) uses the identical mark-to-market approach, batched
once across every account's distinct tickers rather than fetched per
account.

Robinhood: no assignment mechanism was found in this data at all — expect
near-zero equity-level activity there; this is an accurate reflection of the
data, not a gap.
"""

import os
import sys
import csv
import re
import time
from collections import defaultdict, deque
from datetime import date

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, os.path.join(_ROOT, "mcp"))
sys.path.insert(0, os.path.join(_ROOT, "mcp", "reports"))

from update_snapshot import (
    find_schwab_transactions, find_fidelity_transactions,
    find_vanguard_transactions, find_robinhood_transactions,
    _clean, _parse_amount, _parse_date, _FIDELITY_ACCOUNT_LABELS,
    _parse_option_symbol, _FIDELITY_POS_SYMBOL,
)
from report_utils import option_market_price
from yahoo_price_fetcher import fetch_prices
from unified_master_report_production import ACCOUNTS_CONFIG, MONTHLY_TARGET_NET_BASE

# ACCOUNTS_CONFIG's Robinhood labels differ from this module's (which include
# the account-number suffix used elsewhere in this session's work) — map
# rather than duplicate the target data under a second set of keys.
_TARGET_LABEL_ALIASES = {
    "Robinhood Individual (9079)": "Robinhood (Individual)",
    "Robinhood IRA (3600)": "Robinhood (Traditional IRA)",
}


def _annual_target(label):
    key = _TARGET_LABEL_ALIASES.get(label, label)
    cfg = ACCOUNTS_CONFIG.get(key)
    return cfg["monthly_target"] * 12 if cfg else None


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
    unmatched_qty: float, open_lots: list[(key, remaining_qty, credit_per_unit)]).
    open_lots is the detail behind what used to be a bare "still_open_qty" count —
    needed to compute unrealized P&L (current price vs. the credit already banked
    on each specific still-open contract), not just know how many are open."""
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

    open_lots = [(key, lot[0], lot[1]) for key, q in queues.items() for lot in q]
    return monthly, monthly_n, unmatched_qty, open_lots


# ---------------------------------------------------------------------------
# Unrealized P&L for still-open option lots — marks each to its current
# market price via report_utils.option_market_price (proven, already used
# elsewhere in this codebase; not rebuilt here). Per-broker functions turn a
# FIFO key back into (underlying, expiry_iso, strike, option_type).
# ---------------------------------------------------------------------------

def _parse_schwab_key(key):
    parsed = _parse_option_symbol(key)
    if not parsed:
        return None
    return parsed["underlying"], parsed["expiry"], parsed["strike"], parsed["option_type"]


def _parse_fidelity_key(key):
    m = _FIDELITY_POS_SYMBOL.match(key)
    if not m:
        return None
    expiry = date(2000 + int(m.group(2)), int(m.group(3)), int(m.group(4))).isoformat()
    return m.group(1), expiry, float(m.group(6)), ("CALL" if m.group(5) == "C" else "PUT")


def _parse_robinhood_key(key):
    # Built by robinhood_events() as "TICKER MM/DD/YYYY TYPE STRIKE" — this
    # module controls the format, so a plain split is enough, no regex needed.
    parts = key.split()
    if len(parts) != 4:
        return None
    ticker, date_str, opt_type, strike_str = parts
    try:
        m, d, y = date_str.split("/")
        expiry = date(int(y), int(m), int(d)).isoformat()
        return ticker, expiry, float(strike_str), opt_type
    except (ValueError, IndexError):
        return None


def compute_unrealized(open_lots, parse_key_fn):
    """open_lots: list[(key, qty, credit_per_unit)] from fifo_realize's 4th
    return value. Returns (total_unrealized, priced_lot_count, failed_lot_count).
    Failed lots (no exact strike match, fetch error, unparseable key) are
    counted, not silently treated as zero — a data gap here should be visible,
    not quietly understate the objective figure."""
    total = 0.0
    priced = failed = 0
    seen_chains = set()
    for key, qty, credit_per_unit in open_lots:
        parsed = parse_key_fn(key)
        if not parsed:
            failed += 1
            continue
        underlying, expiry, strike, opt_type = parsed
        chain_key = (underlying, expiry)
        if chain_key not in seen_chains:
            seen_chains.add(chain_key)
            time.sleep(0.3)  # only throttle on a genuinely new (underlying, expiry) chain fetch
        current = option_market_price(underlying, expiry, strike, opt_type)
        if current is None:
            failed += 1
            continue
        # option_market_price returns a PER-SHARE price; credit_per_unit is
        # already a full per-CONTRACT dollar amount (the raw source Amount
        # divided by contract qty) — multiply by the standard 100 multiplier
        # before comparing, same convention already used by every other
        # caller of this function (see report_utils.py's reconstruct_open_option_legs,
        # which does `(mark or 0.0) * 100 * contracts`).
        total += (credit_per_unit - current * 100) * qty
        priced += 1
    return total, priced, failed


def compute_equity_unrealized(open_lots, price_dict):
    """open_lots: list[(ticker, qty, cost_per_share)] from fifo_realize's 4th
    return value on an equity event stream. price_dict: pre-fetched
    {ticker: current_price} — batched once across every account by the
    caller (main()), not fetched here, since the same ticker can appear in
    multiple accounts and yahoo_price_fetcher.fetch_prices() has no
    persistent cache of its own (unlike option_market_price, which does).
    Mark-to-market: unrealized = (current_price - cost_per_share) * shares —
    the opposite sign relationship from options, since equity cost is a
    debit (negative in the raw data) and this is a LONG position, not short."""
    total = 0.0
    priced = failed = 0
    for ticker, qty, cost_per_share in open_lots:
        current = price_dict.get(ticker)
        if not current:
            failed += 1
            continue
        # cost_per_share is negative (it's a debit/cost in the raw signed
        # data), so current + cost_per_share = current - abs(cost) = gain.
        total += (current + cost_per_share) * qty
        priced += 1
    return total, priced, failed


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

def _gather(broker, label, option_events, equity_events, note="", parse_key_fn=None):
    """Run FIFO once per account and stash everything needed to print +
    compute unrealized later, without recomputing or re-fetching."""
    opt_monthly, opt_n, opt_unmatched, opt_open = fifo_realize(option_events) if option_events is not None else ({}, {}, 0, [])
    eq_monthly, eq_n, eq_unmatched, eq_open = fifo_realize(equity_events) if equity_events is not None else ({}, {}, 0, [])
    return {
        "broker": broker, "label": label, "note": note, "parse_key_fn": parse_key_fn,
        "opt_monthly": opt_monthly, "opt_unmatched": opt_unmatched, "opt_open": opt_open,
        "eq_monthly": eq_monthly, "eq_unmatched": eq_unmatched, "eq_open": eq_open,
        "has_opt": option_events is not None, "has_eq": equity_events is not None,
    }


def _print_realized_progress(accounts):
    """The PRIMARY progress-toward-$1.2M view: realized option P&L only —
    clean, bankable, matches what the brokerage itself reports — shown
    monthly and cumulative, per account against that account's own share of
    the objective, then portfolio-wide against the full $1.2M. Mark-to-market
    unrealized is deliberately NOT part of this section (see main() — it's a
    separate risk diagnostic, not a progress number, per trader decision:
    blending a volatile mark-to-market swing into "am I on track" produced a
    confusing, misleadingly pessimistic headline)."""
    opt_accounts = [a for a in accounts if a["has_opt"]]
    all_months = sorted({m for a in opt_accounts for m in a["opt_monthly"] if m.startswith("2026")})
    months_elapsed = len(all_months)

    print("=" * 90)
    print("REALIZED PROGRESS TOWARD $1.2M OBJECTIVE (option-level, cumulative by month)")
    print("=" * 90)

    portfolio_cumulative_by_month = defaultdict(float)
    grand_realized = grand_target = grand_open_credit = 0.0

    for acct in opt_accounts:
        target = _annual_target(acct["label"])
        print(f"\n{acct['label']}" + (f"  (annual target: ${target:,})" if target else "  (no target on file)"))
        print(f"  {'Month':8}{'Realized':>14}{'Cumulative':>16}")
        cum = 0.0
        for m in all_months:
            v = acct["opt_monthly"].get(m, 0.0)
            cum += v
            portfolio_cumulative_by_month[m] += v
            print(f"  {m:8}{v:>14,.2f}{cum:>16,.2f}")
        grand_realized += cum

        # Gross premium already collected on still-open positions — this is
        # real cash sitting in the account right now (you were paid the full
        # credit the moment you sold), distinct from both realized (only
        # counts CLOSED trades) and mark-to-market unrealized (nets off the
        # current cost to buy back). Answers "how much have I actually
        # generated, whether or not it's closed yet" — the ceiling if every
        # open position eventually decays to zero/gets assigned with no
        # early buyback; the mark-to-market section shows how much of that
        # ceiling is currently at risk of giving some back.
        open_credit = sum(credit * qty for _, qty, credit in acct["opt_open"])
        grand_open_credit += open_credit
        gross = cum + open_credit
        print(f"  + gross premium still open (not yet closed, but already collected): ${open_credit:,.2f}")
        print(f"  = TOTAL PREMIUM GENERATED YTD (closed + still-open): ${gross:,.2f}")

        if target:
            grand_target += target
            pace = (cum / months_elapsed * 12) if months_elapsed else 0.0
            pct = cum / target * 100
            gross_pct = gross / target * 100
            print(f"  YTD REALIZED: ${cum:,.2f} = {pct:.0f}% of ${target:,} target | pace: ${pace:,.0f}/yr")
            print(f"  YTD GROSS (incl. still-open): ${gross:,.2f} = {gross_pct:.0f}% of ${target:,} target")
            print(f"  (Gross is the ceiling, not a guarantee — some open positions will get bought back")
            print(f"   early rather than run to expiration/assignment; see the risk diagnostic below for")
            print(f"   how much of this open credit is currently at risk of being partly given back.)")

    print("\n" + "-" * 90)
    print("PORTFOLIO — cumulative realized option P&L by month, all accounts")
    print("-" * 90)
    cum = 0.0
    for m in all_months:
        cum += portfolio_cumulative_by_month[m]
        print(f"  {m:8}{portfolio_cumulative_by_month[m]:>14,.2f}{cum:>16,.2f}")
    pace = (cum / months_elapsed * 12) if months_elapsed else 0.0
    vanguard_target = ACCOUNTS_CONFIG.get("Vanguard (Rahul)", {}).get("monthly_target", 0) * 12
    gross_portfolio = cum + grand_open_credit
    print(f"\n  YTD REALIZED: ${cum:,.2f} = {cum / 1_200_000 * 100:.1f}% of the $1.2M objective")
    print(f"  + gross premium still open across all accounts (not yet closed): ${grand_open_credit:,.2f}")
    print(f"  = TOTAL PREMIUM GENERATED YTD (closed + still-open): ${gross_portfolio:,.2f} "
          f"= {gross_portfolio / 1_200_000 * 100:.1f}% of the $1.2M objective")
    print(f"  Sum of per-account annual targets shown above: ${grand_target:,.0f}")
    print(f"  (Short of $1.2M by ~${vanguard_target:,} — Vanguard's own target, excluded")
    print("   from option-level tracking entirely per the data-quality issue above,")
    print("   not a missing account.)")
    print(f"  Pace if this rate continues through the year: ${pace:,.0f}")
    print("=" * 90)


def _print_account(acct, equity_prices):
    print(f"\n{acct['label']}{('  — ' + acct['note']) if acct['note'] else ''}")
    opt_monthly, eq_monthly = acct["opt_monthly"], acct["eq_monthly"]
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

    opt_unrealized = eq_unrealized = 0.0
    if acct["has_opt"]:
        opt_open = acct["opt_open"]
        opt_open_qty = sum(lot[1] for lot in opt_open)
        print(f"  option: unmatched qty {acct['opt_unmatched']:.0f}, still-open qty {opt_open_qty:.0f}")
        if acct["parse_key_fn"] and opt_open:
            opt_unrealized, priced, failed = compute_unrealized(opt_open, acct["parse_key_fn"])
            print(f"  option unrealized (mark-to-market, still-open — risk diagnostic, "
                  f"NOT counted toward the objective): ${opt_unrealized:,.2f} "
                  f"({priced} priced, {failed} could not be priced)")
    if acct["has_eq"]:
        eq_open = acct["eq_open"]
        eq_open_qty = sum(lot[1] for lot in eq_open)
        print(f"  equity: unmatched qty {acct['eq_unmatched']:.0f}, still-open qty {eq_open_qty:.0f}")
        if eq_open:
            eq_unrealized, priced, failed = compute_equity_unrealized(eq_open, equity_prices)
            print(f"  equity unrealized (mark-to-market, still-open — supplementary, "
                  f"not part of the objective): ${eq_unrealized:,.2f} "
                  f"({priced} priced, {failed} could not be priced)")
    return opt_ytd, eq_ytd, opt_unrealized, eq_unrealized


def main():
    accounts = []

    for label, path in find_schwab_transactions().items():
        opt_ev, eq_ev = schwab_events(path)
        accounts.append(_gather("SCHWAB", label, opt_ev, eq_ev, os.path.basename(path), parse_key_fn=_parse_schwab_key))

    for person, path in find_fidelity_transactions().items():
        for acct, (opt_ev, eq_ev) in fidelity_events(path).items():
            accounts.append(_gather("FIDELITY", acct, opt_ev, eq_ev, os.path.basename(path), parse_key_fn=_parse_fidelity_key))

    vanguard_file = find_vanguard_transactions()
    if vanguard_file:
        eq_ev = vanguard_equity_events(vanguard_file)
        accounts.append(_gather("VANGUARD", "Vanguard (Rahul)", None, eq_ev, os.path.basename(vanguard_file)))

    for label, path in find_robinhood_transactions().items():
        opt_ev, eq_ev = robinhood_events(path)
        accounts.append(_gather("ROBINHOOD", label, opt_ev, eq_ev, os.path.basename(path), parse_key_fn=_parse_robinhood_key))

    # Batch-fetch equity prices ONCE across every account's distinct tickers —
    # yahoo_price_fetcher has no persistent cache of its own (unlike
    # option_market_price), and the same ticker can easily appear in several
    # accounts (e.g. a name wheeled across both Schwab and Fidelity).
    all_equity_tickers = sorted({
        ticker for acct in accounts for ticker, qty, _ in acct["eq_open"] if qty > 0
    })
    equity_prices = fetch_prices(all_equity_tickers) if all_equity_tickers else {}

    # PRIMARY: realized-only progress toward the $1.2M objective, monthly and
    # cumulative, per account against its real allocated target and
    # portfolio-wide. This is the number to actually track "am I on pace."
    _print_realized_progress(accounts)

    print("\n\n" + "=" * 78)
    print("DETAIL + MARK-TO-MARKET RISK DIAGNOSTIC (per account)")
    print("Not a progress number — a still-open position's current market value")
    print("is a snapshot, not an outcome. Use large swings here to decide whether")
    print("a specific position/roll needs attention, not to judge overall pace.")
    print("=" * 78)

    grand_opt = grand_eq = grand_opt_unrealized = grand_eq_unrealized = 0.0
    current_broker = None
    for acct in accounts:
        broker = acct["broker"]
        if broker != current_broker:
            print("\n" + "=" * 78)
            print(broker + (" — option-level excluded (unreliable contract identity in this "
                             "export — see module docstring); equity-level included."
                             if broker == "VANGUARD" else ""))
            print("=" * 78)
            current_broker = broker
        o, e, ou, eu = _print_account(acct, equity_prices)
        grand_opt += o
        grand_eq += e
        grand_opt_unrealized += ou
        grand_eq_unrealized += eu

    print("\n" + "=" * 78)
    print("GRAND TOTAL — MARK-TO-MARKET RISK SUMMARY (diagnostic, not a progress figure)")
    print("=" * 78)
    print(f"  Realized option-level (already counted in the PROGRESS section above): ${grand_opt:,.2f}")
    print(f"  Unrealized option-level, mark-to-market on still-open positions:       ${grand_opt_unrealized:,.2f}")
    print(f"  Realized equity-level (supplementary, not part of the objective):      ${grand_eq:,.2f}")
    print(f"  Unrealized equity-level, mark-to-market on still-open shares:          ${grand_eq_unrealized:,.2f}")
    print("\n  Note: Vanguard option-level, any account's pre-file-history positions,")
    print("  and any position that couldn't be priced (see 'could not be priced' counts")
    print("  above) are excluded/undercounted — every total here is a floor, not a")
    print("  guaranteed-complete figure. Mark-to-market unrealized reflects current")
    print("  risk, not a prediction — a large unrealized swing on one name is a")
    print("  prompt to review that specific position/roll, not a locked-in outcome,")
    print("  and it is NOT added to the realized progress figure above.")


if __name__ == "__main__":
    main()
