"""
Premium/KPI aggregation and per-position action/priority signal helpers
split out of report_utils.py (Bolt b19). report_utils.py re-exports
everything here so every existing `from report_utils import X` call site
keeps working unchanged.
"""
from collections import defaultdict
from datetime import date
from typing import Any

from analysis.metrics import breakeven_velocity, premium_capture_rate, profit_factor, sortino_ratio
from analysis.pnl import Position
from config import PERMANENT_EXITS, RISK
from report_utils_core import parse_amount, parse_txn_date
from report_utils_pricing import parse_option_symbol


def monthly_premium(rows: list[dict[str, str]], month_start: date) -> float:
    total = 0.0
    for row in rows:
        txn_date = parse_txn_date(row.get("Date", ""))
        if not txn_date or txn_date.year != month_start.year or txn_date.month != month_start.month:
            continue
        parsed = parse_option_symbol(row.get("Symbol", ""))
        if not parsed:
            continue
        action = str(row.get("Action", "")).strip()
        amount = parse_amount(row.get("Amount", 0))
        if "Sell to Open" in action and amount > 0:
            total += amount
        elif action == "Buy to Close" and amount < 0:
            total -= abs(amount)
    return round(total, 2)


def monthly_option_pnl_series(rows: list[dict[str, str]]) -> list[float]:
    monthly: defaultdict[tuple[int, int], float] = defaultdict(float)
    for row in rows:
        txn_date = parse_txn_date(row.get("Date", ""))
        if not txn_date:
            continue
        parsed = parse_option_symbol(row.get("Symbol", ""))
        if not parsed:
            continue
        action = str(row.get("Action", "")).strip()
        amount = parse_amount(row.get("Amount", 0))
        key = (txn_date.year, txn_date.month)
        if "Sell to Open" in action and amount > 0:
            monthly[key] += amount
        elif action == "Buy to Close" and amount < 0:
            monthly[key] -= abs(amount)
    return [monthly[key] for key in sorted(monthly)]


def combined_kpis(txns: dict[str, list[dict[str, str]]], snapshot: dict[str, Any]) -> dict[str, Any]:
    all_rows = [row for rows in txns.values() for row in rows]
    capture = premium_capture_rate(all_rows) if all_rows else {"capture_rate": snapshot.get("ytd_premium_capture_rate"), "signal": "WATCH"}
    pf = profit_factor(all_rows) if all_rows else {"profit_factor": snapshot.get("ytd_profit_factor"), "win_rate": None, "signal": "WATCH"}
    monthly_series = monthly_option_pnl_series(all_rows)
    sortino = sortino_ratio(monthly_series) if len(monthly_series) >= 3 else {"sortino_annualized": None, "signal": "WATCH"}
    return {"capture": capture, "profit_factor": pf, "sortino": sortino}


def priority_from_position(position: Position, regime: str) -> tuple[int, str, str]:
    roll = position.roll_signal()
    loss = position.loss_flag()
    profit = position.profit_take_signal(regime)
    if loss.get("flag"):
        return 1, "URGENT", f"Mark {loss.get('multiplier')}x premium received"
    if any(leg.dte <= RISK["roll_dte_threshold"] for leg in position.option_legs):
        return 2, "URGENT", "At or inside 21 DTE"
    if profit.get("signal"):
        return 2, "STRONG", f"{profit.get('pct_captured')}% premium captured"
    if position.symbol in PERMANENT_EXITS:
        return 2, "WATCH", "Permanent exit: accelerate covered call exit"
    return 5, "WATCH", "No immediate action"


def action_for_option_leg(underlying: float, strike: float, option_type: str, dte: int) -> str:
    if dte <= 21:
        return "ROLL / CLOSE"
    if option_type == "PUT" and underlying and underlying < strike:
        return "DEFEND / ROLL"
    if option_type == "CALL" and underlying and underlying > strike:
        return "MANAGE ITM CALL"
    return "HOLD"


def estimate_delta(underlying: float, strike: float, option_type: str) -> float | None:
    if not underlying or not strike:
        return None
    moneyness = strike / underlying
    if option_type == "PUT":
        if moneyness >= 1.05:
            return -0.65
        if moneyness >= 1.0:
            return -0.55
        if moneyness >= 0.95:
            return -0.35
        return -0.2
    if moneyness <= 0.95:
        return 0.65
    if moneyness <= 1.0:
        return 0.55
    if moneyness <= 1.05:
        return 0.35
    return 0.2
