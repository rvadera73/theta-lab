"""Weekly combined US + India portfolio report."""

import argparse
import asyncio
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.india_regime import detect_india_regime
from analysis.regime import detect_regime
from config import ACCOUNT_B, ACCOUNT_C
from routines.email_report import build_weekly_combined_html
from reports.report_utils import (
    combined_kpis,
    current_price,
    load_india_positions,
    load_us_positions,
    maybe_send,
    priority_from_position,
    save_html,
)


async def generate_weekly_combined_report(send_email: bool = True, save_to_file: bool = True) -> dict[str, Any]:
    today = date.today()
    us = await load_us_positions()
    india = load_india_positions()
    us_regime = detect_regime()
    india_regime = detect_india_regime()
    snapshot = us.get("snapshot", {})
    txns = us.get("transactions", {})
    kpis = combined_kpis(txns, snapshot)

    account_a_positions = [p for p in us["positions"] if p.account == "A"]
    account_b_positions = [p for p in us["positions"] if p.account == "B"]
    india_positions = india["positions"]

    account_a_actions = []
    for pos in account_a_positions:
        pri, label, reason = priority_from_position(pos, us_regime["regime"])
        if pri > 3:
            continue
        details = []
        for leg in pos.option_legs:
            details.append(f"{leg.option_type} {leg.strike:g} exp {leg.expiry} ({leg.dte} DTE)")
        if pos.loss_flag().get("flag"):
            action = "Review / defend loss"
        elif pos.roll_signal().get("signal"):
            action = "Roll or close"
        elif pos.profit_take_signal(us_regime["regime"]).get("signal"):
            action = "Take profit"
        elif pos.symbol in ("PYPL", "MRNA"):
            action = "Accelerate permanent exit"
        else:
            action = "Monitor"
        account_a_actions.append({
            "symbol": pos.symbol,
            "action": action,
            "reason": reason,
            "priority": label,
            "details": " | ".join(details) or "Equity only",
            "combined_pnl": pos.combined_net_pnl,
        })
    account_a_actions.sort(key=lambda x: (0 if x["priority"] == "URGENT" else 1, -abs(x["combined_pnl"])))
    account_a_actions = account_a_actions[:5]

    account_b_rows = []
    for pos in sorted(account_b_positions, key=lambda p: min([leg.dte for leg in p.option_legs] or [999])):
        wheel_state = "CC" if pos.shares > 0 and any(leg.option_type == "CALL" for leg in pos.option_legs) else "CSP" if any(leg.option_type == "PUT" for leg in pos.option_legs) else "Assigned stock"
        next_dte = min([leg.dte for leg in pos.option_legs] or [0])
        alert = "⚠️ ≤21 DTE" if next_dte and next_dte <= 21 else "OK"
        account_b_rows.append([pos.symbol, wheel_state, str(pos.shares), str(next_dte or "—"), alert])
    if not account_b_rows:
        account_b_rows = [["Data unavailable", "Fallback statements only", "—", "—", "Monitor manually"]]

    account_c_positions = [p for p in us["positions"] if p.account == "C"]
    account_c_rows = []
    for pos in sorted(account_c_positions, key=lambda p: min([leg.dte for leg in p.option_legs] or [999])):
        wheel_state = "CC" if pos.shares > 0 and any(leg.option_type == "CALL" for leg in pos.option_legs) else "CSP" if any(leg.option_type == "PUT" for leg in pos.option_legs) else "Assigned"
        next_dte = min([leg.dte for leg in pos.option_legs] or [0])
        alert = "⚠️ ≤21 DTE" if next_dte and next_dte <= 21 else "OK"
        account_c_rows.append([pos.symbol, wheel_state, str(pos.shares), str(next_dte or "—"), alert])
    if not account_c_rows:
        account_c_rows = [["No positions", "—", "—", "—", "—"]]

    india_rows = []
    for pos in sorted(india_positions, key=lambda p: min([leg.dte for leg in p.option_legs] or [999])):
        if not pos.option_legs:
            continue
        dte = min(leg.dte for leg in pos.option_legs)
        pnl = pos.combined_net_pnl
        action = "Close / roll" if dte <= 21 else ("Defend" if pos.loss_flag().get("flag") else "Hold")
        india_rows.append([pos.symbol, str(dte), f"₹{pnl:,.0f}", action])
    if not india_rows:
        india_rows = [["No F&O positions", "—", "—", "—"]]

    earnings_rows = []
    seen = set()
    from reports.report_utils import upcoming_earnings as fetch_upcoming_earnings
    for pos in us["positions"]:
        if pos.symbol in seen:
            continue
        seen.add(pos.symbol)
        dates = fetch_upcoming_earnings(pos.symbol, 14)
        if dates:
            earnings_rows.append([pos.symbol, ", ".join(dates), pos.account, "Blackout new entries"])
    if not earnings_rows:
        earnings_rows = [["None found", "—", "—", "Clear"]]

    current_mtd = float(snapshot.get("month_to_date_premium", 0) or 0)
    ytd_target = round((today.timetuple().tm_yday / 365) * 1_200_000, 0)
    weekly_target = 20_000
    daily_target = 5_000
    days_elapsed_this_week = today.weekday() + 1
    days_remaining = max(0, 5 - today.weekday())
    weekly_mtd = current_mtd / max(1, today.day) * 7
    daily_pace = current_mtd / max(1, today.day)
    income_pace = {
        "weekly_premium": weekly_mtd,
        "weekly_target": weekly_target,
        "daily_pace": daily_pace,
        "daily_target": daily_target,
        "days_elapsed_this_week": days_elapsed_this_week,
        "days_remaining_week": days_remaining,
        "need_per_remaining_day": (weekly_target - current_mtd) / max(1, days_remaining) if days_remaining else 0,
        "ytd_premium": float(snapshot.get("ytd_net_options_income", 0) or 0),
        "ytd_target": ytd_target,
        "mtd_premium": current_mtd,
    }

    balances = us.get("balances", {}).get("A", {})
    buying_power = float(balances.get("buyingPower", 0) or 0)
    liquidation_value = float(balances.get("liquidationValue", 0) or 0)
    option_requirement = sum(max(0.0, p.total_cost_to_close_options) for p in account_a_positions)
    margin_health = {
        "buying_power": buying_power,
        "option_requirement_ratio": round(option_requirement / liquidation_value * 100, 1) if liquidation_value else None,
        "note": "Live balance data unavailable." if not balances else "Monitor buying power before new entries.",
    }

    data = {
        "title": "Theta-Lab Weekly Combined Report",
        "data_source": f"US: {us['data_source']} | India: {india['data_source']}",
        "warning": " | ".join([msg for msg in [us.get('warning'), india.get('warning')] if msg]),
        "header": {
            "date": today.isoformat(),
            "us_regime": us_regime["regime"],
            "us_entries": us_regime["new_entries_allowed"],
            "india_regime": india_regime["regime"],
            "india_entries": india_regime["new_entries_allowed"],
        },
        "us_regime": us_regime,
        "india_regime": india_regime,
        "account_a_actions": account_a_actions,
        "account_b": {"rows": account_b_rows, "note": f"Target annual return: {ACCOUNT_B['target_annual_return']:.0%}"},
        "account_c": {"rows": account_c_rows, "note": "Designated Beneficiary — CSP/CC only, no naked calls. Target: 12% annual."},
        "india_actions": india_rows,
        "income_pace": income_pace,
        "earnings_blackout": earnings_rows,
        "margin_health": margin_health,
        "kpis": kpis,
    }

    html = build_weekly_combined_html(data, today.strftime("%B %d, %Y"))
    path = save_html("weekly_combined", html, today) if save_to_file else None
    subject = f"Theta-Lab Weekly Combined Report — {today:%B %d, %Y}"
    email_result = maybe_send(subject, html) if send_email else {"success": False, "error": "send skipped"}
    summary_lines = [
        "# Weekly Combined Report",
        f"- Date: {today.isoformat()}",
        f"- Data source: {data['data_source']}",
        f"- US regime: {us_regime['regime']} | India regime: {india_regime['regime']}",
        f"- Saved HTML: {path}" if path else "- Saved HTML: skipped",
        f"- Email: {'sent' if email_result.get('success') else 'not sent'}",
    ]
    if email_result.get("error") and send_email:
        summary_lines.append(f"- Email detail: {email_result['error']}")
    return {"html": html, "path": str(path) if path else None, "summary": "\n".join(summary_lines), "data": data, "email": email_result}


async def _main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--send", action="store_true")
    group.add_argument("--no-send", action="store_true")
    parser.add_argument("--html-only", action="store_true")
    args = parser.parse_args()
    result = await generate_weekly_combined_report(send_email=args.send and not args.html_only, save_to_file=not args.html_only)
    print(result["html"] if args.html_only else result["summary"])


if __name__ == "__main__":
    asyncio.run(_main())
