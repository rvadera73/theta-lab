"""Bi-monthly technical analysis report."""

import argparse
import asyncio
import os
import sys
from collections import defaultdict
from datetime import date
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routines.email_report import build_bimonthly_technical_html
from reports.report_utils import (
    action_for_option_leg,
    current_price,
    estimate_delta,
    load_india_positions,
    load_snapshot,
    load_us_positions,
    maybe_send,
    save_html,
    technical_snapshot,
)

SECTOR_MAP = {
    "Power": ["ADAPOW", "NTPC"],
    "Defense": ["HINAER", "BHAELE", "MAZDOC"],
    "Banking": ["HDFBAN", "BAJFI"],
    "Healthcare": ["APOHOS", "YATHOS"],
    "Real Estate": ["DLFLIM", "ANARAJ"],
}


async def generate_bimonthly_technical_report(send_email: bool = True, save_to_file: bool = True) -> dict[str, Any]:
    today = date.today()
    us = await load_us_positions()
    india = load_india_positions()
    snapshot = load_snapshot()

    assigned_rows = []
    for item in snapshot.get("assigned_positions", []):
        tech = technical_snapshot(item["symbol"])
        current = tech.get("current") or current_price(item["symbol"])
        unrealized = (current - float(item.get("cost_basis", 0) or 0)) * int(item.get("shares", 0) or 0)
        months = None
        cc = float(item.get("monthly_cc", 0) or 0)
        if cc:
            basis = float(item.get("cost_basis", 0) or 0) * int(item.get("shares", 0) or 0)
            market_value = current * int(item.get("shares", 0) or 0)
            remaining = max(0.0, basis - market_value - float(item.get("recovered", 0) or 0))
            months = round(remaining / cc, 1) if cc else None
        thesis = "BROKEN" if tech.get("above_200") is False and (tech.get("rsi") or 50) < 40 else "WATCH" if tech.get("above_50") is False else "INTACT"
        action = "Sell CC now" if cc == 0 else ("Tighten CCs" if thesis != "INTACT" else "Keep wheeling")
        assigned_rows.append([
            item["symbol"],
            str(item.get("shares", 0)),
            f"${float(item.get('cost_basis', 0) or 0):,.2f}",
            f"${current:,.2f}",
            f"${unrealized:,.0f}",
            str(tech.get("rsi") or "—"),
            f"${tech.get('ma50', 0):,.2f}" if tech.get("ma50") else "—",
            "Above" if tech.get("above_200") else "Below" if tech.get("above_200") is False else "—",
            f"{tech.get('pct_off_high')}%" if tech.get("pct_off_high") is not None else "—",
            f"{months} mo" if months is not None else "—",
            f"${cc:,.0f}/mo" if cc else "$0 IDLE",
            thesis,
            action,
        ])

    option_rows = []
    for pos in sorted(us["positions"], key=lambda p: (p.symbol, min([leg.dte for leg in p.option_legs] or [999]))):
        tier = "A" if pos.account == "A" else "B"
        tech = technical_snapshot(pos.symbol)
        for leg in pos.option_legs:
            moneyness = ((pos.current_price - leg.strike) / pos.current_price * 100) if pos.current_price else 0
            option_rows.append([
                pos.symbol,
                leg.option_type,
                f"{leg.strike:g}",
                leg.expiry,
                str(leg.dte),
                f"{moneyness:.1f}%",
                str(tech.get("rsi") or "—"),
                "Above" if tech.get("above_50") else "Below" if tech.get("above_50") is False else "—",
                tier,
                f"${leg.current_mark:,.0f}",
                action_for_option_leg(pos.current_price, leg.strike, leg.option_type, leg.dte),
            ])
    if not option_rows:
        option_rows = [["Data unavailable", "—", "—", "—", "—", "—", "—", "—", "—", "—", "—"]]

    exit_items = []
    for sym in ("PYPL", "MRNA"):
        calls = []
        for pos in us["positions"]:
            if pos.symbol != sym:
                continue
            for leg in pos.option_legs:
                if leg.option_type == "CALL":
                    calls.append(f"{leg.strike:g} exp {leg.expiry} ({leg.dte} DTE)")
        exit_items.append({
            "symbol": sym,
            "status": "CALLS ACTIVE" if calls else "NO ACTIVE CALL",
            "progress": "; ".join(calls) if calls else "Open covered call needed to accelerate exit.",
        })

    india_equity_rows = []
    india_fno_rows = []
    for pos in india["positions"]:
        if pos.shares > 0:
            tech = technical_snapshot(pos.symbol, india=True)
            pnl = (pos.current_price - pos.stock_cost_basis) * pos.shares
            thesis = "INTACT" if getattr(pos, "_is_core", False) and tech.get("above_200") is not False else "WATCH"
            action = pos._exit_trigger.get("action") if getattr(pos, "_exit_trigger", None) else ("Hold core" if getattr(pos, "_is_core", False) else "Review")
            india_equity_rows.append([
                pos.symbol,
                str(pos.shares),
                f"₹{pos.stock_cost_basis:,.2f}",
                f"₹{pos.current_price:,.2f}",
                f"₹{pnl:,.0f}",
                str(tech.get("rsi") or "—"),
                f"{tech.get('pct_off_high')}%" if tech.get("pct_off_high") is not None else "—",
                str(tech.get("pe") or "—"),
                thesis,
                action,
            ])
        for leg in pos.option_legs:
            delta = estimate_delta(pos.current_price, leg.strike, leg.option_type)
            pnl = leg.premium_received - leg.current_mark
            india_fno_rows.append([
                pos.symbol,
                leg.option_type,
                f"{leg.strike:g}",
                leg.expiry,
                str(leg.dte),
                f"{delta:.2f}" if delta is not None else "—",
                f"₹{leg.premium_received:,.0f}",
                f"₹{pnl:,.0f}",
                action_for_option_leg(pos.current_price, leg.strike, leg.option_type, leg.dte),
            ])
    if not india_equity_rows:
        india_equity_rows = [["Data unavailable", "—", "—", "—", "—", "—", "—", "—", "—", "—"]]
    if not india_fno_rows:
        india_fno_rows = [["No India F&O positions", "—", "—", "—", "—", "—", "—", "—", "—"]]

    sector_rows = []
    for sector, symbols in SECTOR_MAP.items():
        scores = []
        for sym in symbols:
            tech = technical_snapshot(sym, india=True)
            score = 0
            score += 1 if tech.get("above_50") else -1 if tech.get("above_50") is False else 0
            score += 1 if tech.get("above_200") else -1 if tech.get("above_200") is False else 0
            score += 1 if (tech.get("rsi") or 50) >= 55 else -1 if (tech.get("rsi") or 50) <= 40 else 0
            scores.append(score)
        avg = sum(scores) / len(scores) if scores else 0
        outlook = "STRONG" if avg >= 1 else "WATCH" if avg >= 0 else "WEAK"
        sector_rows.append([sector, outlook, f"Avg score {avg:.1f}"])

    data = {
        "title": "Theta-Lab Bi-monthly Technical Report",
        "data_source": f"US: {us['data_source']} | India: {india['data_source']}",
        "warning": " | ".join([msg for msg in [us.get('warning'), india.get('warning')] if msg]),
        "assigned_stocks": assigned_rows,
        "option_legs": option_rows,
        "permanent_exits": exit_items,
        "india_equities": india_equity_rows,
        "india_fno": india_fno_rows,
        "india_sector_scorecard": sector_rows,
    }
    html = build_bimonthly_technical_html(data, today.strftime("%B %d, %Y"))
    path = save_html("bimonthly_technical", html, today) if save_to_file else None
    subject = f"Theta-Lab Bi-monthly Technical Report — {today:%B %d, %Y}"
    email_result = maybe_send(subject, html) if send_email else {"success": False, "error": "send skipped"}
    summary = "\n".join([
        "# Bi-monthly Technical Report",
        f"- Date: {today.isoformat()}",
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
    result = await generate_bimonthly_technical_report(send_email=args.send and not args.html_only, save_to_file=not args.html_only)
    print(result["html"] if args.html_only else result["summary"])


if __name__ == "__main__":
    asyncio.run(_main())
