"""
Generates the Monday Top-5 Weekly Action Report.
Pulls live Schwab data, runs all analysis, returns structured report.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from typing import Any

from analysis.pnl import Position, parse_schwab_positions
from analysis.regime import detect_regime
from analysis.iv_rank import batch_iv_rank
from config import (
    ACCOUNT_A, ACCOUNT_B, ACCOUNT_C, PERMANENT_EXITS,
    ITM_POSITION_PLANS, RISK, Regime, PROFIT_TARGETS, UNIVERSE, Tier,
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
) -> str:
    """
    Main report generator. Returns markdown-formatted weekly action report.
    schwab_client: optional mock for testing without live credentials.
    """
    today = date.today()
    week_label = f"{today.strftime('%B %d')} – {(today + __import__('datetime').timedelta(days=4)).strftime('%B %d, %Y')}"

    # --- Regime ---
    regime_data = detect_regime()
    regime = regime_data["regime"]
    new_entries = regime_data["new_entries_allowed"]
    profit_low, profit_high = PROFIT_TARGETS[Regime(regime)]

    lines = [
        f"# THETA-LAB Weekly Action Report",
        f"**Week of:** {week_label}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Regime:** {regime} | New entries: {'YES' if new_entries else 'NO'}",
        f"**Profit-take target:** {int(profit_low*100)}-{int(profit_high*100)}% of max premium",
        "",
    ]

    # --- Market signals ---
    sigs = regime_data.get("signals", {})
    lines += ["## Market Signals", ""]
    if "vix" in sigs:
        v = sigs["vix"]
        lines.append(f"- **VIX:** {v['value']} — {v['detail']}")
    if "sp500_ma" in sigs:
        m = sigs["sp500_ma"]
        lines.append(f"- **S&P 500:** {m['current']:,.0f} | 50-day MA: {m['ma50']:,.0f} ({'✅ above' if m['above_50d'] else '❌ below'}) | 200-day MA: {m['ma200']:,.0f} ({'✅ above' if m['above_200d'] else '❌ below'})")
    lines.append("")

    # --- Pull positions ---
    all_actions = []

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
                # Fetch quotes for ALL underlying symbols (equities + option underlyings)
                symbols = list({
                    (p.get("instrument", {}).get("underlyingSymbol")
                     or p.get("instrument", {}).get("symbol", "").split()[0])
                    for p in raw
                    if p.get("instrument", {}).get("assetType") in ("EQUITY", "OPTION")
                })
                quotes_raw = await get_quotes(symbols)
                balances = await get_balances(acct_hash)

            positions = parse_schwab_positions(raw, acct_label, quotes_raw)

            for pos in positions:
                pri, label, reason = _priority(pos, regime)
                combined_pnl = pos.combined_net_pnl
                profit_sig = pos.profit_take_signal(regime)
                loss_sig = pos.loss_flag()
                roll_sig = pos.roll_signal()

                action = {
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
                    "itm_plan": ITM_POSITION_PLANS.get(pos.symbol),
                    "permanent_exit": pos.symbol in PERMANENT_EXITS,
                }
                all_actions.append(action)
        except Exception as e:
            lines.append(f"⚠️ Could not load Account {acct_label}: {e}")

    # Sort by priority and take top 5
    all_actions.sort(key=lambda x: (x["priority"], -abs(x["combined_pnl"])))
    top5 = all_actions[:5]

    lines.append("## TOP 5 ACTIONS THIS WEEK")
    lines.append("")

    for i, act in enumerate(top5, 1):
        sym = act["symbol"]
        acct = act["account"]
        price = act["current_price"]
        cpnl = act["combined_pnl"]
        pnl_str = f"+${cpnl:,.0f}" if cpnl >= 0 else f"-${abs(cpnl):,.0f}"
        legs_str = " | ".join(
            f"{lg.option_type} ${lg.strike} {lg.expiry} ({_dte_label(lg.dte)})"
            for lg in act["legs"]
        ) or "equity only"

        lines += [
            f"### #{i} {act['label']} — {sym} | Account {acct}",
            f"**Price:** ${price:,.2f} | **Net P&L:** {pnl_str} | **Reason:** {act['reason']}",
            f"**Legs:** {legs_str}",
        ]

        if act["permanent_exit"]:
            lines.append(f"🔴 **PERMANENT EXIT** — {sym} is on no-re-entry list. Accelerate exit via CC premium collection.")
        if act["itm_plan"]:
            lines.append(f"📋 **ITM Plan:** {act['itm_plan'].replace('_', ' ')}")
        if act["profit_signal"]["signal"]:
            lines.append(f"✅ **Profit target hit:** {act['profit_signal']['recommendation']}")
        if act["loss_flag"]["flag"]:
            lf = act["loss_flag"]
            lines.append(f"⚠️ **Loss flag:** {lf['multiplier']}x premium received. Premium: ${lf['premium_received']:,.0f} | Cost to close: ${lf['current_cost_to_close']:,.0f}")
            lines.append(f"   → {lf['action']}")
        if act["roll_signal"]["signal"]:
            rs = act["roll_signal"]
            lines.append(f"🔄 **Roll needed:** {', '.join(rs['legs'])} — {rs['recommendation']}")
        lines.append("")

    # --- Also watching ---
    watching = [a for a in all_actions[5:] if a["priority"] <= 3]
    if watching:
        lines.append("## ALSO WATCHING")
        for act in watching[:5]:
            cpnl = act["combined_pnl"]
            pnl_str = f"+${cpnl:,.0f}" if cpnl >= 0 else f"-${abs(cpnl):,.0f}"
            lines.append(f"- **{act['symbol']}** (Acct {act['account']}): {act['reason']} | Net P&L: {pnl_str}")
        lines.append("")

    # --- P&L tracker ---
    total_realized_week = 0  # Would need order history to compute
    lines += [
        "## WEEKLY P&L TRACKER",
        "",
        f"| Account | Weekly Target | Realized This Week | YTD Pace |",
        f"|---------|--------------|-------------------|---------|",
        f"| A (Rahul) | ${ACCOUNT_A['target_weekly_pnl']:,} | — (pull from order history) | — |",
        f"| B (Pinky) | ${ACCOUNT_B['target_weekly_pnl']:,} | — (pull from order history) | — |",
        f"| **Combined** | **${ACCOUNT_A['target_weekly_pnl'] + ACCOUNT_B['target_weekly_pnl']:,}** | — | — |",
        "",
        "_Note: Schwab API credentials required for live P&L. See setup guide._",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo mode — no credentials needed
    print(generate_weekly_report("DEMO_A", "DEMO_B"))
