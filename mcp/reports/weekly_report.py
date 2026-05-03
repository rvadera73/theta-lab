"""
Generates the Monday Top-5 Weekly Action Report.
Pulls live Schwab data, runs all analysis, returns structured report.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from typing import Any

from analysis.pnl import Position, parse_robinhood_positions, parse_schwab_positions
from analysis.regime import detect_regime
from analysis.iv_rank import batch_iv_rank
from analysis.heat_scanner import heat_from_positions, format_heat_html
from config import (
    ACCOUNT_A, ACCOUNT_B, ACCOUNT_C, ACCOUNT_D, ACCOUNTS, PERMANENT_EXITS,
    LEGACY_EXIT_RULES, RISK, Regime, PROFIT_TARGETS, UNIVERSE, Tier,
)


def _dte_label(dte: int) -> str:
    if dte <= 7:   return f"⚠️ {dte}d — URGENT"
    if dte <= 21:  return f"🔶 {dte}d — act soon"
    if dte <= 45:  return f"🟡 {dte}d — watch"
    return f"🟢 {dte}d"


def _priority(position: Position, regime_str: str) -> tuple[int, str, str]:
    """Returns (priority 1-5, label, reason) for a position."""
    roll = position.roll_signal()
    loss = position.loss_flag()
    profit = position.profit_take_signal(regime_str)

    if loss["flag"]:
        return 1, "URGENT", f"Mark {loss['multiplier']}x premium — flag and review"
    for leg in position.option_legs:
        if leg.dte <= 7:
            return 1, "URGENT", f"Expires in {leg.dte} days — decide now"
    if any(leg.dte <= 21 for leg in position.option_legs):
        return 2, "URGENT", "Within 21 DTE — roll or close"
    if profit["signal"]:
        return 2, "REVIEW", f"At profit target ({profit['pct_captured']}% captured)"
    if roll["signal"]:
        return 3, "MONITOR", "Approaching roll threshold"
    if position.symbol in PERMANENT_EXITS:
        return 2, "REVIEW", "On permanent exit list — accelerate exit"
    return 5, "WATCH", "No immediate action needed"


async def generate_weekly_report(
    account_a_hash: str,
    account_b_hash: str,
    account_c_hash: str = "",
    schwab_client=None,
    save_to_file: bool = True,
) -> dict:
    """
    Main report generator. Returns dict with keys: html, text, data, path.
    schwab_client: optional mock for testing without live credentials.
    """
    from routines.email_report import build_weekly_action_html
    from reports.report_utils import save_html, maybe_send
    today = date.today()
    week_label = f"{today.strftime('%B %d')} – {(today + __import__('datetime').timedelta(days=4)).strftime('%B %d, %Y')}"

    # --- Regime ---
    regime_data = detect_regime()
    regime = regime_data["regime"]
    new_entries = regime_data["new_entries_allowed"]
    profit_low, profit_high = PROFIT_TARGETS[Regime(regime)]

    # --- Pull positions ---
    all_actions = []
    all_positions: list = []
    text_warnings = []

    for acct_hash, acct_cfg, acct_label in [
        (account_a_hash, ACCOUNT_A, "A"),
        (account_b_hash, ACCOUNT_B, "B"),
        (account_c_hash, ACCOUNT_C, "C"),
    ]:
        if not acct_hash:
            continue
        try:
            if schwab_client:
                raw = await schwab_client.get_all_positions(acct_hash)
                quotes_raw = {}
            else:
                from schwab_client import get_all_positions, get_quotes, get_balances
                raw = await get_all_positions(acct_hash)
                symbols = list({
                    (p.get("instrument", {}).get("underlyingSymbol")
                     or p.get("instrument", {}).get("symbol", "").split()[0])
                    for p in raw
                    if p.get("instrument", {}).get("assetType") in ("EQUITY", "OPTION")
                })
                quotes_raw = await get_quotes(symbols)

            positions = parse_schwab_positions(raw, acct_label, quotes_raw)
            all_positions.extend(positions)

            for pos in positions:
                pri, label, reason = _priority(pos, regime)
                combined_pnl = pos.combined_net_pnl
                profit_sig = pos.profit_take_signal(regime)
                loss_sig = pos.loss_flag()
                roll_sig = pos.roll_signal()
                all_actions.append({
                    "priority": pri,
                    "label": label,
                    "reason": reason,
                    "symbol": pos.symbol,
                    "account": acct_label,
                    "shares": pos.shares,
                    "current_price": pos.current_price,
                    "combined_pnl": combined_pnl,
                    "premium_received": pos.total_premium_received,
                    "cost_to_close": pos.total_cost_to_close_options,
                    "profit_signal": profit_sig,
                    "loss_flag": loss_sig,
                    "roll_signal": roll_sig,
                    "legs": pos.option_legs,
                    "permanent_exit": pos.symbol in PERMANENT_EXITS,
                })
        except Exception as e:
            text_warnings.append(f"⚠️ Could not load Account {acct_label}: {e}")

    # Account D — Robinhood (if configured)
    rh_user = os.getenv("ROBINHOOD_USERNAME", "")
    rh_pass = os.getenv("ROBINHOOD_PASSWORD", "")
    if rh_user and rh_pass:
        try:
            from robinhood_client import get_robinhood_positions
            rh_equity, rh_opts = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, get_robinhood_positions),
                timeout=15,
            )
            rh_positions = parse_robinhood_positions(rh_equity, rh_opts, account_label="D")
            all_positions.extend(rh_positions)
            for pos in rh_positions:
                pri, label, reason = _priority(pos, regime)
                combined_pnl = pos.combined_net_pnl
                all_actions.append({
                    "priority": pri, "label": label, "reason": reason,
                    "symbol": pos.symbol, "account": "D",
                    "shares": pos.shares, "current_price": pos.current_price,
                    "combined_pnl": combined_pnl,
                    "premium_received": pos.total_premium_received,
                    "cost_to_close": pos.total_cost_to_close_options,
                    "profit_signal": pos.profit_take_signal(regime),
                    "loss_flag": pos.loss_flag(),
                    "roll_signal": pos.roll_signal(),
                    "legs": pos.option_legs,
                    "permanent_exit": pos.symbol in PERMANENT_EXITS,
                })
        except Exception:
            pass

    all_actions.sort(key=lambda x: (x["priority"], -abs(x["combined_pnl"])))
    top5 = all_actions[:5]
    watching = [a for a in all_actions[5:] if a["priority"] <= 3][:5]

    # --- Heat scanner ---
    portfolio_heat_html = ""
    if all_positions:
        try:
            heat_result = heat_from_positions(all_positions, regime)
            portfolio_heat_html = format_heat_html(heat_result)
        except Exception as e:
            portfolio_heat_html = f"<p><em>Heat scanner unavailable: {e}</em></p>"

    # --- P&L rows ---
    pnl_rows = [
        ["A (Rahul Schwab)", f"${ACCOUNT_A['target_weekly_pnl']:,}", "— (order history needed)"],
        ["B (Pinky IRA)", f"${ACCOUNT_B['target_weekly_pnl']:,}", "—"],
        ["C (Designated)", f"${ACCOUNT_C['target_weekly_pnl']:,}", "—"],
        ["D (Robinhood IRA)", f"${ACCOUNT_D['target_weekly_pnl']:,}", "—"],
        ["Combined", f"${sum(ACCOUNTS[k]['target_weekly_pnl'] for k in ACCOUNTS):,}", "—"],
    ]

    report_data = {
        "regime": regime,
        "week_label": week_label,
        "new_entries_allowed": new_entries,
        "profit_low": profit_low,
        "profit_high": profit_high,
        "signals": regime_data.get("signals", {}),
        "top5": top5,
        "watching": watching,
        "portfolio_heat_html": portfolio_heat_html,
        "pnl_rows": pnl_rows,
    }

    html = build_weekly_action_html(report_data, today.strftime("%B %d, %Y"))

    # --- Markdown text (kept for MCP text response) ---
    lines = [
        f"# THETA-LAB Weekly Action Report",
        f"**Week of:** {week_label}",
        f"**Regime:** {regime} | New entries: {'YES' if new_entries else 'NO'}",
        f"**Profit-take target:** {int(profit_low*100)}-{int(profit_high*100)}%",
        "",
    ]
    lines += text_warnings
    lines.append("## TOP 5 ACTIONS THIS WEEK\n")
    for i, act in enumerate(top5, 1):
        sym = act["symbol"]
        cpnl = act["combined_pnl"]
        pnl_str = f"+${cpnl:,.0f}" if cpnl >= 0 else f"-${abs(cpnl):,.0f}"
        legs_str = " | ".join(
            f"{lg.option_type} ${lg.strike} {lg.expiry} ({_dte_label(lg.dte)})"
            for lg in act["legs"]
        ) or "equity only"
        lines += [
            f"### #{i} {act['label']} — {sym} | Account {act['account']}",
            f"**Price:** ${act['current_price']:,.2f} | **Net P&L:** {pnl_str} | **Reason:** {act['reason']}",
            f"**Legs:** {legs_str}",
        ]
        if act["permanent_exit"]:
            lines.append(f"🔴 **PERMANENT EXIT** — accelerate exit via CC premium collection.")
        if act["profit_signal"]["signal"]:
            lines.append(f"✅ **Profit target hit:** {act['profit_signal']['recommendation']}")
        if act["loss_flag"]["flag"]:
            lf = act["loss_flag"]
            lines.append(f"⚠️ **Loss flag:** {lf['multiplier']}x premium. → {lf['action']}")
        if act["roll_signal"]["signal"]:
            rs = act["roll_signal"]
            lines.append(f"🔄 **Roll needed:** {rs['recommendation']}")
        lines.append("")

    text = "\n".join(lines)

    path = None
    if save_to_file:
        path = save_html("action_report", html, today)

    subject = f"Theta-Lab Weekly Action Report — {today:%B %d, %Y}"
    email_result = maybe_send(subject, html)

    return {"html": html, "text": text, "data": report_data, "path": str(path) if path else None, "email": email_result}


if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_weekly_report("DEMO_A", "DEMO_B"))
