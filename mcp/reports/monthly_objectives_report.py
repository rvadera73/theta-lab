"""Monthly objectives gap analysis report."""

import argparse
import asyncio
import os
import sys
from datetime import date
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reports.report_utils import (
    combined_kpis,
    current_price,
    load_india_positions,
    load_snapshot,
    load_us_positions,
    maybe_send,
    month_name,
    monthly_premium,
    previous_month,
    project_value,
    save_html,
)
from config import ACCOUNT_A, ACCOUNT_B, ACCOUNT_C
from routines.email_report import build_monthly_objectives_html


async def generate_monthly_objectives_report(send_email: bool = True, save_to_file: bool = True) -> dict[str, Any]:
    today = date.today()
    current_month = today.replace(day=1)
    prior_month = previous_month(today)
    us = await load_us_positions()
    india = load_india_positions()
    snapshot = load_snapshot()
    txns = us.get("transactions", {})
    kpis = combined_kpis(txns, snapshot)

    account_a_last = monthly_premium(txns.get("A", []), prior_month)
    account_b_last = monthly_premium(txns.get("B", []), prior_month)
    account_c_last = monthly_premium(txns.get("C", []), prior_month)
    account_a_pace = project_value(monthly_premium(txns.get("A", []), current_month), today)
    account_b_pace = project_value(monthly_premium(txns.get("B", []), current_month), today)
    account_c_pace = project_value(monthly_premium(txns.get("C", []), current_month), today)
    india_last = sum(max(0.0, leg.premium_received) for pos in india["positions"] for leg in pos.option_legs)
    india_pace = india_last

    account_a_target = round(ACCOUNT_A["target_weekly_pnl"] * 4.33)
    account_b_target = round(ACCOUNT_B["target_weekly_pnl"] * 4.33)
    account_c_target = ACCOUNT_C["target_weekly_pnl"]
    combined_last = account_a_last + account_b_last + account_c_last
    combined_pace = account_a_pace + account_b_pace + account_c_pace

    income_rows = [
        ["Combined monthly income", "$100,000", f"${combined_last:,.0f}", f"${combined_pace:,.0f}", f"${100000 - combined_pace:,.0f}", "ON TRACK" if combined_pace >= 100000 else "BEHIND"],
        ["Account A premium", f"${account_a_target:,.0f}", f"${account_a_last:,.0f}", f"${account_a_pace:,.0f}", f"${account_a_target - account_a_pace:,.0f}", "ON TRACK" if account_a_pace >= account_a_target else "BEHIND"],
        ["Account B premium", f"${account_b_target:,.0f}", f"${account_b_last:,.0f}", f"${account_b_pace:,.0f}", f"${account_b_target - account_b_pace:,.0f}", "ON TRACK" if account_b_pace >= account_b_target else "BEHIND"],
        ["Account C premium", f"${account_c_target:,.0f}", f"${account_c_last:,.0f}", f"${account_c_pace:,.0f}", f"${account_c_target - account_c_pace:,.0f}", "ON TRACK" if account_c_pace >= account_c_target else "BEHIND"],
        ["India FNO premium", "₹50,000", f"₹{india_last:,.0f}", f"₹{india_pace:,.0f}", f"₹{50000 - india_pace:,.0f}", "ON TRACK" if india_pace >= 50000 else "BEHIND"],
    ]

    pf = kpis["profit_factor"]
    capture = kpis["capture"]
    sortino = kpis["sortino"]
    kpi_rows = [
        ["Premium capture rate", "65-70%", f"{capture.get('capture_rate', '—')}%", "GOOD" if (capture.get('capture_rate') or 0) >= 65 else "WATCH"],
        ["Profit factor", ">2.0", str(pf.get("profit_factor", "—")), "GOOD" if (pf.get('profit_factor') or 0) >= 2 else "WATCH"],
        ["Sortino ratio", ">2.0", str(sortino.get("sortino_annualized", "—")), "GOOD" if (sortino.get('sortino_annualized') or 0) >= 2 else "WATCH"],
        ["Win rate", ">65%", f"{pf.get('win_rate', '—')}%", "GOOD" if (pf.get('win_rate') or 0) >= 65 else "WATCH"],
    ]

    assigned_rows = []
    idle_positions = []
    book_value = 0.0
    for item in snapshot.get("assigned_positions", []):
        current = current_price(item["symbol"]) or float(item.get("cost_basis", 0) or 0)
        market_value = current * int(item.get("shares", 0) or 0)
        book_value += market_value
        cc = float(item.get("monthly_cc", 0) or 0)
        recovered = float(item.get("recovered", 0) or 0)
        remaining = max(0.0, float(item.get("cost_basis", 0) or 0) * int(item.get("shares", 0) or 0) - market_value - recovered)
        months = round(remaining / cc, 1) if cc else None
        assigned_rows.append([item["symbol"], str(item.get("shares", 0)), f"${remaining:,.0f}", f"${cc:,.0f}/mo" if cc else "$0 IDLE", f"{months} mo" if months is not None else "∞"])
        if cc == 0:
            idle_positions.append(item["symbol"])

    gap_actions = []
    if (capture.get("capture_rate") or 0) < 65:
        gap_actions.append({
            "symbol": "Capture Rate",
            "action": "Close earlier into the 40-60% bear target band",
            "reason": f"Premium capture {capture.get('capture_rate', '—')}% vs 65% target.",
            "priority": "WATCH",
            "details": "Prioritise easy winners and avoid letting credits decay into assignment risk.",
        })
    if idle_positions:
        gap_actions.append({
            "symbol": "Idle Capital",
            "action": "Sell covered calls on idle assigned names",
            "reason": f"Idle positions: {', '.join(idle_positions)}.",
            "priority": "URGENT",
            "details": "Target at least one call cycle per idle name this month.",
        })
    for row in assigned_rows:
        if row[-1] != "∞":
            try:
                months = float(row[-1].split()[0])
            except Exception:
                months = 0
            if months and months > 12:
                gap_actions.append({
                    "symbol": row[0],
                    "action": "Tighten covered call strikes or reduce exposure",
                    "reason": f"Breakeven velocity slow at {row[-1]}.",
                    "priority": "WATCH",
                    "details": f"Current CC income {row[3]} against {row[2]} remaining loss.",
                })
    if account_a_pace < account_a_target:
        gap_actions.append({
            "symbol": "Account A",
            "action": "Increase premium harvest from best liquid strangles / CCs",
            "reason": f"Projected ${account_a_pace:,.0f} vs ${account_a_target:,.0f} target.",
            "priority": "WATCH",
            "details": "Only in compliant regime; otherwise recycle capital from profit-takes.",
        })

    india_rows = []
    india_wins = 0
    india_total = 0
    for pos in india["positions"]:
        for leg in pos.option_legs:
            pnl = leg.premium_received - leg.current_mark
            india_rows.append([pos.symbol, f"₹{leg.premium_received:,.0f}", f"₹{pnl:,.0f}", "Aligned" if getattr(pos, "_is_core", False) else "Review"])
            india_total += 1
            india_wins += 1 if pnl >= 0 else 0
    if not india_rows:
        india_rows = [["Data unavailable", "—", "—", "—"]]
    india_summary = {
        "target": 50000,
        "pace": india_pace,
        "win_rate": round(india_wins / india_total * 100, 1) if india_total else None,
        "rows": india_rows,
    }

    data = {
        "title": "Theta-Lab Monthly Objectives Report",
        "data_source": f"US: {us['data_source']} | India: {india['data_source']}",
        "warning": " | ".join([msg for msg in [us.get('warning'), india.get('warning')] if msg]),
        "header": {"previous_month": month_name(prior_month), "current_month": month_name(current_month)},
        "income_rows": income_rows,
        "kpi_rows": kpi_rows,
        "assigned_book": {"value": book_value, "cap": 375000, "idle_positions": idle_positions},
        "breakeven_rows": assigned_rows,
        "gap_actions": gap_actions,
        "india_objectives": india_summary,
    }

    html = build_monthly_objectives_html(data, today.strftime("%B %d, %Y"))
    path = save_html("monthly_objectives", html, today) if save_to_file else None
    subject = f"Theta-Lab Monthly Objectives Report — {today:%B %d, %Y}"
    email_result = maybe_send(subject, html) if send_email else {"success": False, "error": "send skipped"}
    summary = "\n".join([
        "# Monthly Objectives Report",
        f"- Previous month: {month_name(prior_month)}",
        f"- Data source: {data['data_source']}",
        f"- Saved HTML: {path}" if path else "- Saved HTML: skipped",
        f"- Email: {'sent' if email_result.get('success') else 'not sent'}",
    ])
    return {"html": html, "path": str(path) if path else None, "summary": summary, "data": data, "email": email_result}


async def _main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--send", action="store_true")
    group.add_argument("--no-send", action="store_true")
    parser.add_argument("--html-only", action="store_true")
    args = parser.parse_args()
    result = await generate_monthly_objectives_report(send_email=args.send and not args.html_only, save_to_file=not args.html_only)
    print(result["html"] if args.html_only else result["summary"])


if __name__ == "__main__":
    asyncio.run(_main())
