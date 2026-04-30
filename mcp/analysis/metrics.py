"""
Dashboard metrics for a theta / premium-selling strategy.
Computes: premium capture rate, profit factor, sortino ratio,
breakeven velocity, cost of carry, monthly target tracker.
All functions accept either a pandas DataFrame (from CSV) or plain dicts.
"""

import math
import re
from datetime import datetime, date
from typing import Optional


# ---------------------------------------------------------------------------
# Transaction CSV parsing helpers
# ---------------------------------------------------------------------------

def _parse_amount(val: str) -> float:
    if not val:
        return 0.0
    return float(str(val).replace("$", "").replace(",", "").strip())


def _parse_option_symbol(symbol: str) -> Optional[dict]:
    """
    Parse Schwab option symbol: 'APP 06/17/2027 580.00 C'
    Returns {underlying, expiry, strike, option_type} or None if equity.
    """
    m = re.match(
        r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$",
        str(symbol).strip(),
    )
    if not m:
        return None
    return {
        "underlying": m.group(1),
        "expiry": m.group(2),
        "strike": float(m.group(3)),
        "option_type": "CALL" if m.group(4) == "C" else "PUT",
    }


def load_transactions(filepath: str) -> list[dict]:
    """Load Schwab transaction CSV into list of dicts."""
    import csv
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


# ---------------------------------------------------------------------------
# Premium Capture Rate
# ---------------------------------------------------------------------------

def premium_capture_rate(transactions: list[dict]) -> dict:
    """
    % of sold premium actually kept.
    = (total STO credits - total BTC debits) / total STO credits
    Target: 65-70%. Below 60% = too many losses / early closes / assignments.
    """
    total_credits = 0.0
    total_debits = 0.0
    count_open = 0
    count_close = 0

    for row in transactions:
        action = row.get("Action", "").strip()
        amount = _parse_amount(row.get("Amount", "0"))
        opt = _parse_option_symbol(row.get("Symbol", ""))
        if opt is None:
            continue  # skip equity transactions

        if action in ("Sell to Open", "Buy to Close Sell to Open"):
            if amount > 0:
                total_credits += amount
                count_open += 1
        elif action == "Buy to Close":
            if amount < 0:
                total_debits += abs(amount)
                count_close += 1
        elif action == "Sell to Open":
            if amount > 0:
                total_credits += amount
                count_open += 1

    if total_credits == 0:
        return {"capture_rate": None, "error": "no_options_credits_found"}

    net = total_credits - total_debits
    rate = net / total_credits

    return {
        "total_credits": round(total_credits, 0),
        "total_debits": round(total_debits, 0),
        "net_premium": round(net, 0),
        "capture_rate": round(rate * 100, 1),
        "count_opened": count_open,
        "count_closed": count_close,
        "signal": "GOOD" if rate >= 0.65 else ("WATCH" if rate >= 0.55 else "POOR"),
        "target": "65-70%",
        "interpretation": (
            f"Keeping {rate*100:.1f}% of sold premium. "
            + ("On target." if rate >= 0.65 else
               "Slightly below target — review assignment rate and early close frequency." if rate >= 0.55 else
               "Below 55% — too many assignments or losers eroding premium edge.")
        ),
    }


# ---------------------------------------------------------------------------
# Profit Factor
# ---------------------------------------------------------------------------

def profit_factor(transactions: list[dict]) -> dict:
    """
    Gross winning trades / Gross losing trades on CLOSED options positions only.
    Target: > 2.0 (excellent). 1.5-2.0 = good. < 1.5 = edge eroding.
    Only counts positions with a closing event (BTC or Expired) — excludes open positions.
    """
    trades: dict[str, dict] = {}  # symbol → {credits, debits, closed}

    for row in transactions:
        action = row.get("Action", "").strip()
        symbol = row.get("Symbol", "").strip()
        amount = _parse_amount(row.get("Amount", "0"))
        opt = _parse_option_symbol(symbol)
        if opt is None:
            continue

        if symbol not in trades:
            trades[symbol] = {"credits": 0.0, "debits": 0.0, "closed": False}

        if action == "Sell to Open" and amount > 0:
            trades[symbol]["credits"] += amount
        elif action == "Buy to Close" and amount < 0:
            trades[symbol]["debits"] += abs(amount)
            trades[symbol]["closed"] = True
        elif action in ("Expired",):
            trades[symbol]["closed"] = True  # expired worthless = full credit kept
        elif action == "Assigned":
            trades[symbol]["closed"] = True

    gross_wins = 0.0
    gross_losses = 0.0
    win_count = 0
    loss_count = 0

    for sym, t in trades.items():
        if t["credits"] == 0 or not t["closed"]:
            continue  # skip open positions — not yet realized
        net = t["credits"] - t["debits"]
        if net > 0:
            gross_wins += net
            win_count += 1
        elif net < 0:
            gross_losses += abs(net)
            loss_count += 1

    if gross_losses == 0:
        pf = float("inf") if gross_wins > 0 else 0.0
    else:
        pf = gross_wins / gross_losses

    return {
        "profit_factor": round(pf, 2),
        "gross_wins": round(gross_wins, 0),
        "gross_losses": round(gross_losses, 0),
        "win_count": win_count,
        "loss_count": loss_count,
        "win_rate": round(win_count / (win_count + loss_count) * 100, 1) if (win_count + loss_count) > 0 else None,
        "signal": "EXCELLENT" if pf >= 2.0 else ("GOOD" if pf >= 1.5 else "WATCH" if pf >= 1.0 else "POOR"),
        "target": ">2.0",
        "interpretation": (
            f"Profit Factor {pf:.2f} — "
            + ("Excellent edge. Winners are {:.1f}x bigger than losers.".format(pf) if pf >= 2.0 else
               "Good edge. Maintain discipline." if pf >= 1.5 else
               "Marginal. Review strike selection or early close frequency." if pf >= 1.0 else
               "Edge is negative. Losers exceed winners — review strategy.")
        ),
    }


# ---------------------------------------------------------------------------
# Sortino Ratio
# ---------------------------------------------------------------------------

def sortino_ratio(monthly_pnl: list[float], target_monthly: float = 0.0) -> dict:
    """
    Sortino ratio on a series of monthly P&L values.
    Only penalizes downside months (not upside variance).
    Target: > 2.0 for an aggressive options strategy.
    monthly_pnl: list of net P&L per month in dollars
    target_monthly: minimum acceptable monthly return in dollars (default 0)
    """
    if len(monthly_pnl) < 3:
        return {"sortino": None, "error": "need_at_least_3_months"}

    n = len(monthly_pnl)
    avg = sum(monthly_pnl) / n
    downside_returns = [min(0.0, r - target_monthly) for r in monthly_pnl]
    downside_variance = sum(d ** 2 for d in downside_returns) / n
    downside_std = math.sqrt(downside_variance)

    if downside_std == 0:
        sortino = float("inf")
    else:
        sortino = (avg - target_monthly) / downside_std

    annualized = sortino * math.sqrt(12)

    return {
        "sortino_monthly": round(sortino, 2),
        "sortino_annualized": round(annualized, 2),
        "avg_monthly_pnl": round(avg, 0),
        "downside_std": round(downside_std, 0),
        "months_analyzed": n,
        "signal": "EXCELLENT" if annualized >= 2.0 else ("GOOD" if annualized >= 1.0 else "WATCH"),
        "target": "annualized > 2.0",
        "interpretation": (
            f"Annualized Sortino {annualized:.2f}. "
            + ("Strong risk-adjusted return with low downside risk." if annualized >= 2.0 else
               "Acceptable but monitor for downside months increasing." if annualized >= 1.0 else
               "Downside months are dragging risk-adjusted performance.")
        ),
    }


# ---------------------------------------------------------------------------
# Breakeven Velocity
# ---------------------------------------------------------------------------

def breakeven_velocity(
    symbol: str,
    unrealized_loss: float,
    monthly_cc_premium: float,
    months_elapsed: int = 0,
    premium_already_recovered: float = 0.0,
) -> dict:
    """
    How fast is each assigned position recovering via CC premium?
    unrealized_loss: positive number (dollars below cost basis)
    monthly_cc_premium: average monthly CC credit collected on this position
    """
    remaining_loss = unrealized_loss - premium_already_recovered

    if monthly_cc_premium <= 0:
        return {
            "symbol": symbol,
            "months_to_breakeven": None,
            "velocity_pct_month": 0.0,
            "remaining_loss": round(remaining_loss, 0),
            "signal": "STALLED",
            "interpretation": "No CC premium — open a covered call immediately.",
        }

    months_remaining = remaining_loss / monthly_cc_premium
    velocity_pct = monthly_cc_premium / unrealized_loss * 100

    if months_remaining <= 12:
        signal = "FAST"
    elif months_remaining <= 24:
        signal = "ON TRACK"
    elif months_remaining <= 36:
        signal = "SLOW"
    else:
        signal = "CONSIDER EXIT"

    return {
        "symbol": symbol,
        "unrealized_loss": round(unrealized_loss, 0),
        "premium_recovered": round(premium_already_recovered, 0),
        "remaining_loss": round(remaining_loss, 0),
        "monthly_cc_premium": round(monthly_cc_premium, 0),
        "months_to_breakeven": round(months_remaining, 1),
        "velocity_pct_month": round(velocity_pct, 1),
        "signal": signal,
        "interpretation": (
            f"{symbol}: ${remaining_loss:,.0f} left to recover at ${monthly_cc_premium:,.0f}/mo "
            f"= {months_remaining:.1f} months ({signal}). "
            + ("Accelerate CC strikes if possible." if signal in ("SLOW", "CONSIDER EXIT") else "")
        ),
    }


# ---------------------------------------------------------------------------
# Cost of Carry on Assigned Positions
# ---------------------------------------------------------------------------

def cost_of_carry(
    symbol: str,
    shares: int,
    cost_basis_per_share: float,
    current_price: float,
    monthly_cc_premium: float,
    benchmark_monthly_yield: float = 0.025,  # 3% monthly = 36% annual yield for idle margin
) -> dict:
    """
    Opportunity cost: what could this capital earn as new CSPs vs. current CC yield?
    benchmark_monthly_yield: alternative use of capital (selling new CSPs = ~2-3%/month)
    """
    market_value = shares * current_price
    cc_yield = monthly_cc_premium / market_value if market_value > 0 else 0
    opportunity_cost_monthly = market_value * benchmark_monthly_yield
    net_carry = monthly_cc_premium - opportunity_cost_monthly

    return {
        "symbol": symbol,
        "shares": shares,
        "market_value": round(market_value, 0),
        "monthly_cc_premium": round(monthly_cc_premium, 0),
        "cc_yield_monthly_pct": round(cc_yield * 100, 2),
        "opportunity_cost_monthly": round(opportunity_cost_monthly, 0),
        "net_carry": round(net_carry, 0),
        "signal": "POSITIVE" if net_carry > 0 else "NEGATIVE",
        "interpretation": (
            f"{symbol}: CC yields ${monthly_cc_premium:,.0f}/mo ({cc_yield*100:.1f}%) vs. "
            f"${opportunity_cost_monthly:,.0f}/mo opportunity cost. "
            + (f"Net carry positive — keep wheeling." if net_carry > 0 else
               f"Net carry negative — accelerate exit; capital works harder as new CSPs.")
        ),
    }


# ---------------------------------------------------------------------------
# Monthly $100K Target Tracker
# ---------------------------------------------------------------------------

def monthly_target_tracker(
    transactions: list[dict],
    unrealized_equity_change: float = 0.0,
    target_monthly: float = 100_000.0,
    year: int = 2026,
    month: int = None,
) -> dict:
    """
    Tracks progress toward $100K/month combined (premium + equity appreciation).
    unrealized_equity_change: net change in mark-to-market value of stock positions this month.
    """
    if month is None:
        month = date.today().month

    # Filter transactions to current month
    monthly_credits = 0.0
    monthly_debits = 0.0

    for row in transactions:
        raw_date = row.get("Date", "")
        try:
            txn_date = datetime.strptime(raw_date.strip(), "%m/%d/%Y")
        except Exception:
            continue
        if txn_date.year != year or txn_date.month != month:
            continue

        action = row.get("Action", "").strip()
        amount = _parse_amount(row.get("Amount", "0"))
        opt = _parse_option_symbol(row.get("Symbol", ""))
        if opt is None:
            continue

        if action == "Sell to Open" and amount > 0:
            monthly_credits += amount
        elif action == "Buy to Close" and amount < 0:
            monthly_debits += abs(amount)

    net_premium = monthly_credits - monthly_debits
    combined = net_premium + unrealized_equity_change
    pct_of_target = combined / target_monthly * 100

    return {
        "month": f"{year}-{month:02d}",
        "target_monthly": target_monthly,
        "net_options_premium": round(net_premium, 0),
        "unrealized_equity_change": round(unrealized_equity_change, 0),
        "combined_total": round(combined, 0),
        "pct_of_target": round(pct_of_target, 1),
        "remaining_to_target": round(max(0, target_monthly - combined), 0),
        "signal": "ON TRACK" if pct_of_target >= 80 else ("WATCH" if pct_of_target >= 50 else "BEHIND"),
        "days_in_month": 30,
        "interpretation": (
            f"Month-to-date: ${combined:,.0f} of ${target_monthly:,.0f} target "
            f"({pct_of_target:.1f}%). "
            f"Premium: ${net_premium:,.0f} | Equity change: ${unrealized_equity_change:,.0f}."
        ),
    }
