"""
Generates the THETA-LAB India Weekly Action Report.
Pulls live NSE/NFO positions via ICICI Breeze, runs India regime detection,
calculates combined P&L, and returns prioritised actions.

Currency: ₹ (INR)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timedelta
from typing import Any

from analysis.pnl import Position, OptionLeg
from analysis.india_regime import detect_india_regime
from analysis.india_statement_parser import (
    build_positions_from_statements,
    load_india_config,
)
from config import (
    INDIA_ACCOUNT,
    INDIA_PERMANENT_EXITS,
    PROFIT_TARGETS,
    Regime,
    RISK,
)

# yfinance tickers for NSE indices used as FNO underlyings
_INDEX_TICKERS = {
    "NIFTY":  "^NSEI",
    "CNXBAN": "^NSEBANK",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCPNIFTY": "NIFTY_MIDCAP_100.NS",
}


def _fetch_index_prices(symbols: list[str]) -> dict[str, float]:
    """Fetch current index prices from yfinance for FNO underlying indices."""
    prices: dict[str, float] = {}
    tickers = {sym: _INDEX_TICKERS[sym] for sym in symbols if sym in _INDEX_TICKERS}
    if not tickers:
        return prices
    try:
        import yfinance as yf
        for sym, ticker in tickers.items():
            try:
                data = yf.Ticker(ticker).fast_info
                lp = getattr(data, "last_price", None) or getattr(data, "regularMarketPrice", None)
                if lp:
                    prices[sym] = float(lp)
            except Exception:
                pass
    except ImportError:
        pass
    return prices


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dte_label(dte: int) -> str:
    if dte <= 7:   return f"⚠️ {dte}d — URGENT"
    if dte <= 21:  return f"🔶 {dte}d — act soon"
    if dte <= 45:  return f"🟡 {dte}d — watch"
    return f"🟢 {dte}d"


def _fmt_inr(amount: float) -> str:
    """Format amount as ₹ with commas, e.g. ₹1,23,456."""
    sign = "+" if amount >= 0 else "-"
    return f"{sign}₹{abs(amount):,.0f}"


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
    if position.symbol in INDIA_PERMANENT_EXITS:
        return 2, "REVIEW", "On permanent exit list — accelerate exit"
    return 5, "WATCH", "No immediate action needed"


def _dte_from_expiry(expiry: str) -> int:
    """Calculate DTE from YYYY-MM-DD string."""
    try:
        return (date.fromisoformat(expiry) - date.today()).days
    except Exception:
        return 0


def _map_breeze_to_positions(raw_positions: list[dict]) -> list[Position]:
    """
    Convert Breeze portfolio positions into Position objects.

    Breeze returns a flat list where equity and option legs are separate rows.
    We group option legs under their underlying equity symbol.
    """
    equity_map: dict[str, Position] = {}
    option_legs: dict[str, list[OptionLeg]] = {}

    for pos in raw_positions:
        symbol = pos.get("symbol", "").strip()
        if not symbol:
            continue

        exchange = pos.get("exchange", "NSE").upper()
        product = pos.get("product_type", "").lower()
        qty = int(pos.get("quantity", 0) or 0)
        avg_price = float(pos.get("avg_price", 0) or 0)
        market_value = float(pos.get("market_value", 0) or 0)

        # Current price = market_value / qty (avoid div-by-zero)
        current_price = market_value / qty if qty != 0 else avg_price

        if exchange == "NSE" and product in ("cash", ""):
            # Equity position
            equity_map[symbol] = Position(
                symbol=symbol,
                account="INDIA",
                shares=qty,
                stock_cost_basis=avg_price,
                current_price=current_price,
            )

        elif exchange in ("NFO", "NSE") and product == "options":
            # Option leg — map CE/PE → CALL/PUT
            right = pos.get("option_type", "").upper()
            option_type = "CALL" if right == "CE" else "PUT"
            strike_str = pos.get("strike_price", "0")
            try:
                strike = float(strike_str)
            except (ValueError, TypeError):
                strike = 0.0

            expiry = pos.get("expiry_date", "")
            dte = _dte_from_expiry(expiry)

            is_short = qty < 0
            abs_qty = abs(qty)
            # Premium received = avg_price * 100 * contracts (NSE lot ≈ 1 per unit in Breeze qty)
            # Breeze qty is already in units; avg_price is per unit
            premium = avg_price * abs_qty if is_short else 0.0
            mark = current_price * abs_qty if is_short else 0.0

            # Derive the underlying from the symbol (Breeze may pass root symbol separately)
            underlying = pos.get("_raw", {}).get("stock_code", symbol)
            if not underlying:
                underlying = symbol

            leg = OptionLeg(
                description=f"{option_type} {strike} {expiry}",
                strike=strike,
                expiry=expiry,
                option_type=option_type,
                quantity=qty,
                premium_received=premium,
                current_mark=mark,
                dte=dte,
            )
            option_legs.setdefault(underlying, []).append(leg)

    # Merge option legs into equity positions
    for underlying, legs in option_legs.items():
        if underlying not in equity_map:
            equity_map[underlying] = Position(
                symbol=underlying,
                account="INDIA",
                shares=0,
                stock_cost_basis=0.0,
                current_price=0.0,
            )
        equity_map[underlying].option_legs.extend(legs)

    return list(equity_map.values())


def _map_breeze_equity_to_positions(raw_holdings: list[dict], india_cfg: dict) -> list[Position]:
    """Convert live demat holdings from get_demat_holdings() into Position objects."""
    core_portfolio = set(india_cfg.get("core_portfolio", []))
    exit_triggers  = {e["symbol"]: e for e in india_cfg.get("exit_triggers", [])}
    permanent_exits = set(india_cfg.get("permanent_exits", []))

    positions = []
    for h in raw_holdings:
        symbol = h.get("symbol", "").strip()
        if not symbol:
            continue
        qty   = int(h.get("quantity", 0) or 0)
        avg   = float(h.get("avg_price", 0) or 0)
        ltp   = float(h.get("ltp", 0) or 0)
        pos = Position(
            symbol=symbol,
            account="INDIA",
            shares=qty,
            stock_cost_basis=avg,
            current_price=ltp if ltp else avg,
        )
        pos._is_core      = symbol in core_portfolio
        pos._exit_trigger = exit_triggers.get(symbol)
        if symbol in permanent_exits:
            pos._permanent_exit = True
        positions.append(pos)
    return positions



async def generate_india_weekly_report(
    api_key: str,
    api_secret: str,
    session_token: str,
    schwab_client=None,   # unused; kept for interface symmetry with US report
) -> str:
    """
    Main India report generator. Returns markdown-formatted weekly action report.
    Currency: ₹ (INR).
    """
    today = date.today()
    week_end = today + timedelta(days=4)
    week_label = f"{today.strftime('%B %d')} – {week_end.strftime('%B %d, %Y')}"

    # --- Regime ---
    regime_data = detect_india_regime()
    regime = regime_data["regime"]
    new_entries = regime_data["new_entries_allowed"]
    profit_low, profit_high = PROFIT_TARGETS[Regime(regime)]

    lines = [
        "# THETA-LAB India Weekly Action Report",
        f"**Week of:** {week_label}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Regime:** {regime} | New entries: {'YES' if new_entries else 'NO'}",
        f"**Profit-take target:** {int(profit_low*100)}-{int(profit_high*100)}% of max premium",
        "",
    ]

    # --- Market signals ---
    sigs = regime_data.get("signals", {})
    lines += ["## Market Signals", ""]

    if "india_vix" in sigs:
        v = sigs["india_vix"]
        lines.append(f"- **India VIX:** {v['value']} — {v['detail']}")

    if "nifty50_ma" in sigs:
        m = sigs["nifty50_ma"]
        above50_str  = "✅ above" if m["above_50d"]  else "❌ below"
        above200_str = "✅ above" if m["above_200d"] else "❌ below"
        lines.append(
            f"- **Nifty 50:** {m['current']:,.0f} | "
            f"50-day MA: {m['ma50']:,.0f} ({above50_str}) | "
            f"200-day MA: {m['ma200']:,.0f} ({above200_str})"
        )

    if regime_data.get("note"):
        lines.append(f"\n> ℹ️ {regime_data['note']}")

    lines.append("")

    # --- Pull positions ---
    all_actions = []
    india_cfg = {}

    if not api_key or not api_secret or not session_token:
        lines.append("_No Breeze credentials — loading positions from local statement files._\n")
        try:
            india_cfg = load_india_config()
            positions = build_positions_from_statements(india_cfg)
        except Exception as e:
            lines.append(f"⚠️ Could not parse local statements: {e}")
            positions = []
    else:
        india_cfg = load_india_config()
        try:
            from breeze_client import get_portfolio_positions, get_demat_holdings

            # FNO positions — always live from account 7510078170
            raw_fno = get_portfolio_positions(api_key, api_secret, session_token)
            positions = _map_breeze_to_positions(raw_fno)

            # Equity holdings — live from account 7500069840 during market hours,
            # CSV fallback outside market hours ("No Data Found" → empty list)
            raw_equity = get_demat_holdings(api_key, api_secret, session_token)
            if raw_equity:
                equity_positions = _map_breeze_equity_to_positions(raw_equity, india_cfg)
                positions.extend(equity_positions)
                lines.append(f"_Live equity: {len(raw_equity)} holdings from ICICI demat._\n")
            else:
                equity_positions = build_positions_from_statements(india_cfg, fno_only=False, equity_only=True)
                positions.extend(equity_positions)
                lines.append("_Equity: loaded from local statement (demat API unavailable outside market hours)._\n")

        except Exception as e:
            lines.append(f"⚠️ Breeze API error ({e}) — falling back to local statements.\n")
            positions = build_positions_from_statements(india_cfg)

    # Enrich index positions (NIFTY, CNXBAN) with live underlying price from yfinance
    index_syms = [p.symbol for p in positions if p.symbol in _INDEX_TICKERS and p.current_price == 0.0]
    if index_syms:
        idx_prices = _fetch_index_prices(index_syms)
        for pos in positions:
            if pos.symbol in idx_prices:
                pos.current_price = idx_prices[pos.symbol]

    for pos in positions:
        pri, label, reason = _priority(pos, regime)
        combined_pnl = pos.combined_net_pnl
        profit_sig = pos.profit_take_signal(regime)
        loss_sig = pos.loss_flag()
        roll_sig = pos.roll_signal()

        all_actions.append({
            "priority":         pri,
            "label":            label,
            "reason":           reason,
            "symbol":           pos.symbol,
            "shares":           pos.shares,
            "current_price":    pos.current_price,
            "combined_pnl":     combined_pnl,
            "premium_received": pos.total_premium_received,
            "cost_to_close":    pos.total_cost_to_close_options,
            "profit_signal":    profit_sig,
            "loss_flag":        loss_sig,
            "roll_signal":      roll_sig,
            "legs":             pos.option_legs,
            "permanent_exit":   pos.symbol in INDIA_PERMANENT_EXITS,
            "exit_trigger":     getattr(pos, "_exit_trigger", None),
            "is_core":          getattr(pos, "_is_core", False),
        })

    # Sort by priority then largest absolute P&L
    all_actions.sort(key=lambda x: (x["priority"], -abs(x["combined_pnl"])))
    top5 = all_actions[:5]

    lines.append("## TOP 5 ACTIONS THIS WEEK")
    lines.append("")

    if not top5:
        lines.append("_No open positions found — verify Breeze credentials and session token._")
        lines.append("")
    else:
        for i, act in enumerate(top5, 1):
            sym = act["symbol"]
            price = act["current_price"]
            cpnl = act["combined_pnl"]
            pnl_str = _fmt_inr(cpnl)

            legs_str = " | ".join(
                f"{lg.option_type} ₹{lg.strike:,.0f} {lg.expiry} ({_dte_label(lg.dte)})"
                for lg in act["legs"]
            ) or "equity only"

            lines += [
                f"### #{i} {act['label']} — {sym}",
                f"**Price:** ₹{price:,.2f} | **Net P&L:** {pnl_str} | **Reason:** {act['reason']}",
                f"**Legs:** {legs_str}",
            ]

            if act["permanent_exit"]:
                lines.append(
                    f"🔴 **PERMANENT EXIT** — {sym} is on no-re-entry list. "
                    "Accelerate exit via CC premium collection."
                )
            if act["exit_trigger"]:
                et = act["exit_trigger"]
                trigger = et.get("trigger", 0)
                shares = et.get("shares", "all")
                action_note = et.get("action", "")
                phase = et.get("phase", "")
                if trigger == 0:
                    lines.append(f"🚨 **EXIT TRIGGER (Phase {phase}):** Sell {shares} shares — immediate, any price")
                else:
                    lines.append(
                        f"🎯 **EXIT TRIGGER (Phase {phase}):** {action_note} "
                        f"| Target: ₹{trigger:,}"
                    )
            if act["is_core"]:
                lines.append("💎 **CORE HOLD** — Keep unless exit trigger hit")
            if act["profit_signal"]["signal"]:
                lines.append(f"✅ **Profit target hit:** {act['profit_signal']['recommendation']}")
            if act["loss_flag"]["flag"]:
                lf = act["loss_flag"]
                lines.append(
                    f"⚠️ **Loss flag:** {lf['multiplier']}x premium received. "
                    f"Premium: ₹{lf['premium_received']:,.0f} | "
                    f"Cost to close: ₹{lf['current_cost_to_close']:,.0f}"
                )
                lines.append(f"   → {lf['action']}")
            if act["roll_signal"]["signal"]:
                rs = act["roll_signal"]
                lines.append(
                    f"🔄 **Roll needed:** {', '.join(rs['legs'])} — {rs['recommendation']}"
                )
            lines.append("")

    # --- Also watching ---
    watching = [a for a in all_actions[5:] if a["priority"] <= 3]
    if watching:
        lines.append("## ALSO WATCHING")
        for act in watching[:5]:
            cpnl = act["combined_pnl"]
            lines.append(
                f"- **{act['symbol']}**: {act['reason']} | Net P&L: {_fmt_inr(cpnl)}"
            )
        lines.append("")

    # --- Exit triggers summary (from india_config.yaml) ---
    exit_triggers = india_cfg.get("exit_triggers", [])
    if exit_triggers:
        lines += ["## 🚨 EXIT TRIGGERS (Phased Plan)", ""]
        phase1 = [e for e in exit_triggers if e.get("phase") == 1]
        phase2 = [e for e in exit_triggers if e.get("phase") == 2]
        for phase_label, group in [("Phase 1 — Immediate", phase1), ("Phase 2 — On Bounce", phase2)]:
            if group:
                lines.append(f"**{phase_label}:**")
                for e in group:
                    sym = e["icici_symbol"]
                    trigger = e.get("trigger", 0)
                    shares = e.get("shares", "all")
                    action_note = e.get("action", "")
                    tag = "🚨" if trigger == 0 else "🎯"
                    lines.append(f"- {tag} **{sym}**: {action_note}")
                lines.append("")

    # --- P&L tracker ---
    lines += [
        "## WEEKLY P&L TRACKER",
        "",
        f"| Account | Weekly Target | Realized This Week | YTD Pace |",
        f"|---------|--------------|-------------------|---------|",
        f"| {INDIA_ACCOUNT['label']} | ₹{INDIA_ACCOUNT['target_weekly_pnl']:,} "
        f"| — (pull from order history) | — |",
        "",
        "_Note: Breeze API does not expose order history in this integration. "
        "Pull realized P&L from ICICI Direct statement._",
    ]

    return "\n".join(lines)


def _no_breeze_credentials_message() -> str:
    return (
        "## ICICI Breeze API Credentials Required\n\n"
        "Set the following environment variables to enable live data:\n\n"
        "```\n"
        "BREEZE_API_KEY=your_api_key\n"
        "BREEZE_API_SECRET=your_api_secret\n"
        "BREEZE_SESSION_TOKEN=your_daily_session_token\n"
        "```\n\n"
        "**Getting a session token (daily):**\n"
        "1. Log in at https://api.icicidirect.com/apiuser/login\n"
        "2. Approve the API session — you will be redirected to your callback URL\n"
        "3. Copy the `apisession` parameter from the redirect URL\n"
        "4. Set it as `BREEZE_SESSION_TOKEN` in your `.env` file\n\n"
        "Until credentials are set the report will show regime signals only.\n"
    )


if __name__ == "__main__":
    import asyncio

    async def _demo():
        report = await generate_india_weekly_report("", "", "")
        print(report)

    asyncio.run(_demo())
