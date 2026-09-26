"""
Generates the THETA-LAB India Weekly Action Report.
Pulls live NSE/NFO positions via ICICI Breeze, runs India regime detection,
calculates combined P&L, and returns prioritised actions.

Currency: ₹ (INR)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Optional

from analysis.pnl import Position, OptionLeg
from analysis.india_regime import detect_india_regime
from analysis.india_statement_parser import (
    build_positions_from_statements,
    load_india_config,
)
from report_utils import current_price as _live_price, yf_symbol
from config import (
    INDIA_ACCOUNT,
    INDIA_PERMANENT_EXITS,
    PROFIT_TARGETS,
    Regime,
    RISK,
)

try:
    from enhanced_metrics import get_ticker_metrics
except ImportError:
    get_ticker_metrics = None
from routines.india_us_evening_report import _verdict_from_conviction, _verdict_reason

# yfinance tickers for NSE indices used as FNO underlyings
_INDEX_TICKERS = {
    "NIFTY":  "^NSEI",
    "CNXBAN": "^NSEBANK",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCPNIFTY": "NIFTY_MIDCAP_100.NS",
    # NIFSEL = Nifty Midcap SELECT, a different index from Midcap 100 above --
    # was missing entirely (confirmed live 2026-09-21: this is why NIFSEL kept
    # showing price ₹0.00 in the weekly report). Verified ticker via direct
    # yfinance test: NIFTY_MID_SELECT.NS returned 14,504.25, matching the
    # NIFSEL contract strikes (14,000-14,700) -- MIDCPNIFTY/NIFTY_MIDCAP_100.NS
    # trades in a completely different range and would have been silently wrong.
    "NIFSEL": "NIFTY_MID_SELECT.NS",
}

# Strangle-alternative suggestion, added 2026-08-25 per direct request to
# surface this whenever an index position is coming up on rollover, not just
# as a one-off manual analysis. Deliberately index-only (see _INDEX_TICKERS
# above) -- individual stock option chains in India are thinner, event-driven,
# and physically settled, so far-OTM legs needed for a strangle often lack
# real liquidity there; the index is the only part of the book where this
# structure is reliably executable. Computed once per report run and cached,
# since multiple index positions can be near rollover in the same run.
_VIX_PERCENTILE_CACHE: dict = {}

def _india_vix_percentile_note() -> str:
    """Live India VIX vs. its own 5yr distribution, with an explicit caution
    at low percentiles -- confirmed this session that selling a NEW 2-leg
    strangle when VIX is already unusually cheap carries real mean-reversion
    risk: a plain move back to the MEDIAN (not a spike) can erase two weeks
    of theta on a strangle with zero price move against you, since a 2-leg
    position is more vega-sensitive than the single-leg puts this book
    normally runs. Returns a cached, one-line note; never raises -- a live
    data failure just omits the suggestion rather than breaking the report.
    """
    if "note" in _VIX_PERCENTILE_CACHE:
        return _VIX_PERCENTILE_CACHE["note"]
    try:
        import yfinance as _yf
        import numpy as _np
        hist = _yf.Ticker("^INDIAVIX").history(period="5y")["Close"]
        current = float(hist.iloc[-1])
        pct = float((hist < current).mean() * 100)
        if pct < 25:
            note = (f"India VIX {current:.1f} sits at the {pct:.0f}th percentile of its own 5yr range -- "
                    "unusually cheap. A NEW 30-delta strangle here carries real mean-reversion risk "
                    "(a plain move back to median vol, not a spike, can erase early theta with zero "
                    "price move against you) -- consider a normal single-leg roll instead, or wait for "
                    "a modest vol uptick before adding a fresh strangle.")
        elif pct < 50:
            note = (f"India VIX {current:.1f} sits at the {pct:.0f}th percentile of its own 5yr range -- "
                    "still on the cheap side. A strangle roll is more defensible than at the extreme "
                    "lows, but size conservatively.")
        else:
            note = (f"India VIX {current:.1f} sits at the {pct:.0f}th percentile of its own 5yr range -- "
                    "a reasonable entry for a fresh 30-delta strangle roll instead of a same-structure "
                    "single-leg roll, if you want the richer combined premium. Verify live strikes/"
                    "liquidity before executing.")
    except Exception:
        note = ""
    _VIX_PERCENTILE_CACHE["note"] = note
    return note


def _backfill_equity_prices(positions: list) -> None:
    """Statement-fallback positions carry avg cost as current_price; overwrite
    with a live yfinance quote where available (mirrors report_utils.load_india_positions)."""
    for pos in positions:
        if pos.symbol in _INDEX_TICKERS or pos.shares <= 0:
            continue
        live = _live_price(pos.symbol, india=True)
        # `if live:` alone lets a NaN close price through: NaN is truthy in a
        # bool() check (only 0.0/None/False are falsy), so an illiquid/gappy
        # NSE ticker whose most recent Yahoo row is NaN would overwrite a
        # perfectly good avg-cost fallback with NaN -- confirmed live
        # 2026-08-24 on POWGRI/ADAPOR, which then propagated into stock_pnl
        # (current_price - cost_basis) * shares, showing as "Price: nan" and
        # "Net P&L: -nan" in the rendered report. `live > 0` is False for
        # both NaN and 0.0, so this guards both failure modes in one check.
        if live and live > 0:
            pos.current_price = live


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
    verdict = getattr(position, "_verdict", None)
    if verdict == "WEAK":
        # Fundamentally weak, not just technically hot — surface ahead of healthy
        # names regardless of P&L size, same tier as a roll-approaching signal.
        return 4, verdict, _verdict_reason(position._conviction_metrics)
    if verdict == "EXTENDED":
        # Good business, just technically overbought — a trim-consideration, not
        # a thesis break. Keep at WATCH tier so it doesn't crowd out WEAK names,
        # but still carries its own verdict label/reason instead of the generic one.
        return 5, verdict, _verdict_reason(position._conviction_metrics)
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
    exit_triggers  = {e["icici_symbol"]: e for e in india_cfg.get("exit_triggers", [])}
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


def _build_new_entry_actions(india_cfg: dict, regime_data: dict) -> list[dict]:
    """New-entry candidates as actionable items, same shape as the existing-
    position actions in `all_actions` so they compete in the same Top-5 sort
    instead of only ever being about what's already held. Added 2026-08-15 —
    the report previously never suggested anything new, which directly
    conflicted with the trader's stated goal of staying fully invested.

    Two sources, deliberately not deduped against each other (different
    purposes): (1) the curated data/india_config.yaml watchlist — thesis-
    driven names with a planned entry zone, checked via the SAME
    check_watchlist() the evening-report script already uses; (2) the
    broader indian-stock-list.xlsx market-watch scan (52-week-range + RSI)
    via scripts/india_stock_list_review.py — catches genuinely oversold
    names outside the small curated list (e.g. ITC, found 2026-08-15: 2% of
    52-week range, RSI 38, not on the YAML watchlist at all).
    """
    actions = []
    new_entries_allowed = regime_data.get("new_entries_allowed", True)

    def _base_action(symbol, price, reason, entry_detail):
        return {
            "priority": 2, "label": "NEW ENTRY", "symbol": symbol,
            "reason": reason, "shares": 0, "current_price": price or 0.0,
            "combined_pnl": 0, "premium_received": 0, "cost_to_close": 0,
            "profit_signal": {"signal": False}, "loss_flag": {"flag": False},
            "roll_signal": {"signal": False}, "legs": [],
            "permanent_exit": False, "exit_trigger": None, "is_core": False,
            "conviction_metrics": None, "is_new_entry": True,
            "entry_detail": entry_detail,
        }

    # Source 1: curated YAML watchlist, entry-zone check
    try:
        from routines.india_us_evening_report import check_watchlist
        for w in check_watchlist(india_cfg.get("watchlist", []), new_entries_allowed):
            if not w.get("actionable"):
                continue
            actions.append(_base_action(
                w["symbol"], w.get("current"),
                f"{w['status']} — {w.get('thesis', '')}",
                f"Entry zone ₹{w['entry_zone_low']:,}-₹{w['entry_zone_high']:,} | "
                f"Strategy: {w.get('strategy', '')} | Source: curated watchlist (india_config.yaml)",
            ))
    except Exception as e:
        print(f"  Warning: curated watchlist check failed: {e}")

    # Source 2: broader market-watch scan (indian-stock-list.xlsx)
    try:
        import pandas as pd
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts")
        sys.path.insert(0, scripts_dir)
        from india_stock_list_review import find_latest_stock_list, load_watchlist, scan_technicals
        from india_statement_parser import parse_equity_positions
        from report_utils import _INDIA_SYMBOL_MAP

        # Exclude names already held — this source is specifically "genuinely
        # new names," not "add more to an existing position" (that's a
        # different decision with different sizing implications; conflating
        # the two under one "NEW ENTRY" label would mislabel an add-more
        # signal like POWERGRID, an existing holding, as a fresh entry).
        yahoo_to_icici = {v.replace(".NS", ""): k for k, v in _INDIA_SYMBOL_MAP.items()}
        held_codes = set(parse_equity_positions().keys())

        def _is_held(scrip):
            if scrip in held_codes:
                return True
            icici_code = yahoo_to_icici.get(scrip)
            return icici_code in held_codes if icici_code else False

        src = find_latest_stock_list()
        wl = load_watchlist(src)
        tech = scan_technicals(wl["Scrip Name"].tolist())
        merged = wl.merge(tech, left_on="Scrip Name", right_on="scrip", how="left")
        already_flagged = {a["symbol"] for a in actions}
        for _, row in merged.iterrows():
            pos_range, rsi = row.get("pos_in_range"), row.get("rsi")
            if pos_range is None or pd.isna(pos_range) or rsi is None or pd.isna(rsi):
                continue
            if row["Scrip Name"] in already_flagged or _is_held(row["Scrip Name"]):
                continue
            if pos_range < 20 and rsi < 40 and new_entries_allowed:
                actions.append(_base_action(
                    row["Scrip Name"], row.get("price"),
                    f"Near 52w low ({pos_range:.0f}% range) AND oversold (RSI {rsi:.0f})",
                    f"Sector: {row.get('sector')} | Source: stock-list scan ({os.path.basename(src)})",
                ))
    except Exception as e:
        print(f"  Warning: stock-list scan check failed: {e}")

    return actions


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
            _backfill_equity_prices(positions)
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
                _backfill_equity_prices(equity_positions)
                positions.extend(equity_positions)
                lines.append("_Equity: loaded from local statement (demat API unavailable outside market hours)._\n")

        except Exception as e:
            lines.append(f"⚠️ Breeze API error ({e}) — falling back to local statements.\n")
            positions = build_positions_from_statements(india_cfg)
            _backfill_equity_prices(positions)

    # Enrich index positions (NIFTY, CNXBAN) with live underlying price from yfinance
    index_syms = [p.symbol for p in positions if p.symbol in _INDEX_TICKERS and p.current_price == 0.0]
    if index_syms:
        idx_prices = _fetch_index_prices(index_syms)
        for pos in positions:
            if pos.symbol in idx_prices:
                pos.current_price = idx_prices[pos.symbol]

    for pos in positions:
        if get_ticker_metrics is not None and pos.shares > 0 and pos.symbol not in _INDEX_TICKERS:
            m = get_ticker_metrics(yf_symbol(pos.symbol, india=True), pos.current_price)
            m["position_52w"] = m["position_in_52w_range"]  # _verdict_reason expects this key name
            pos._conviction_metrics = m
            pos._verdict, pos._verdict_color = _verdict_from_conviction(m["conviction"], m["heat_status"])

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
            "conviction_metrics": getattr(pos, "_conviction_metrics", None),
        })

    # New-entry candidates compete in the same Top-5 as existing-position
    # management — see _build_new_entry_actions' docstring for why.
    all_actions.extend(_build_new_entry_actions(india_cfg, regime_data))

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

            if act.get("is_new_entry"):
                lines += [
                    f"### #{i} {act['label']} — {sym}",
                    f"**Price:** ₹{price:,.2f} | **Status:** not yet held | **Reason:** {act['reason']}",
                    f"🌱 **NEW ENTRY CANDIDATE** — {act.get('entry_detail', '')}",
                ]
                lines.append("")
                continue

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
            if act["label"] in ("WEAK", "EXTENDED") and act["conviction_metrics"]:
                m = act["conviction_metrics"]
                lines.append(
                    f"⚠️ **{act['label']}** — conviction {m['conviction']:.1f}/10, "
                    f"RSI {m['rsi']:.0f}, {m['position_in_52w_range']:.0f}% of 52w range"
                )
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
                # Strangle-alternative suggestion -- index-only (see
                # _INDEX_TICKERS), surfaced whenever a rollover decision is
                # already being made, not as a separate action item.
                if sym in _INDEX_TICKERS:
                    vix_note = _india_vix_percentile_note()
                    if vix_note:
                        lines.append(f"   💡 **Strangle-alternative check:** {vix_note}")
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

    # --- Priority actions (bottom-up, CLOSE/ROLL/ENTER only) ---
    # Mirrors the US book's Priority Actions block -- same reasoning: a
    # stable book shouldn't flood this with every WATCH/HOLD line, only the
    # items that actually need a decision this week.
    priority = get_india_priority_actions(positions, india_cfg)
    if priority:
        lines.append("## PRIORITY ACTIONS (India, bottom-up)")
        lines.append("")
        verb_icon = {"CLOSE": "🚨", "ROLL": "🔄", "ENTER": "🟢"}
        for act in sorted(priority, key=lambda a: {"CLOSE": 0, "ROLL": 1, "ENTER": 2}.get(a["verb"], 3)):
            pnl_note = f" | Net: {_fmt_inr(act['pnl'])}" if act.get("pnl") is not None else ""
            lines.append(f"{verb_icon.get(act['verb'], '•')} **{act['verb']} — {act['symbol']}**: {act['reason']}{pnl_note}")
        lines.append("")

    # --- F&O concentration / OTM-buffer guard ---
    lines += _check_fno_concentration_risk(positions)

    # --- 6-month plan tracking ---
    lines += _check_6month_plan(positions, sigs)

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


def _fetch_us_10y_yield() -> float | None:
    """Real US 10-Year Treasury yield from FRED's public fredgraph.csv feed
    (series DGS10) -- no API key needed, same free endpoint pattern
    macro_risk_analyzer.py already uses for HYOAS/T10Y2Y. Confirmed live
    2026-09-25 this series is fetchable this exact way (real recent value:
    5.18% on 2026-09-24) before wiring it in here, not assumed. Returns
    None (never raises) on any failure -- callers already render "no data"
    for that case, matching the india_vix/nifty50_ma checks above it.
    """
    try:
        import requests
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        lines = [ln for ln in response.text.strip().splitlines() if ln]
        for line in reversed(lines[1:]):  # skip header, walk back from latest
            _, value = line.split(",")
            if value and value != ".":
                return float(value)
    except Exception:
        pass
    return None


def _realized_vol_annualized(yf_ticker: str, window: int = 20) -> Optional[float]:
    """Annualized realized volatility from the last `window` daily log
    returns -- used as a stand-in for implied vol. A real IV back-solve off
    NSE's own EOD settlement price isn't reliable here: many open legs in
    this book show zero traded volume (confirmed live 2026-09-25), meaning
    SttlmPric is a theoretical mark, not a real fill -- solving for "IV"
    against a synthetic price would just manufacture a precise-looking
    number with no real information in it. Historical vol is honestly an
    approximation of the market's expectation, not the market's own
    expectation, but it's a real, computable number instead of a fabricated
    one. Returns None on any failure (short history, network error).
    """
    try:
        import numpy as np
        import yfinance as yf
        hist = yf.Ticker(yf_ticker).history(period="3mo")
        closes = hist["Close"].dropna()
        if len(closes) < window + 1:
            return None
        log_ret = np.log(closes / closes.shift(1)).dropna()
        return float(log_ret.iloc[-window:].std() * (252 ** 0.5))
    except Exception:
        return None


def _bs_delta(spot: float, strike: float, dte: int, vol: float, option_type: str, r: float = 0.065) -> Optional[float]:
    """Standard Black-Scholes delta, using realized (not implied) vol as the
    input -- see _realized_vol_annualized's own caveat on why. r=6.5% is
    India's approximate risk-free short rate; delta is not very sensitive to
    r at these DTEs so this doesn't need to be exact."""
    import math
    if not vol or vol <= 0 or dte <= 0 or spot <= 0 or strike <= 0:
        return None
    try:
        T = dte / 365
        d1 = (math.log(spot / strike) + (r + 0.5 * vol * vol) * T) / (vol * math.sqrt(T))
    except (ValueError, ZeroDivisionError):
        return None
    n_d1 = 0.5 * (1 + math.erf(d1 / math.sqrt(2)))
    return n_d1 if option_type.upper().startswith("C") else n_d1 - 1


def _load_risk_rules() -> dict:
    import yaml as _yaml
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "india_6month_plan.yaml",
    )
    try:
        with open(path) as f:
            plan = _yaml.safe_load(f) or {}
    except Exception:
        return {}
    return plan.get("risk_rules") or {}


def _evaluate_fno_legs(positions: list) -> list[dict]:
    """Single source of truth for every open index F&O short leg's risk
    evaluation -- both the human-readable guard report and the priority-
    actions verb classifier read from this, so the two never drift apart.
    Returns one dict per short leg with underlying/leg/spot/vol/delta/
    buffer_pct/expected_move_pct/spacing_violation/cluster_violation.
    """
    rules = _load_risk_rules()
    if not rules:
        return []
    max_per_expiry = rules.get("max_short_legs_per_expiry_week", 3)
    min_spacing_pct = rules.get("min_strike_spacing_pct", 3.0)
    expected_move_multiple = rules.get("expected_move_buffer_multiple", 1.25)
    delta_roll_threshold = rules.get("delta_roll_threshold", 0.35)

    short_legs = []  # (underlying, spot, leg)
    for pos in positions:
        if pos.symbol not in _INDEX_TICKERS or not getattr(pos, "option_legs", None):
            continue
        spot = pos.current_price
        for leg in pos.option_legs:
            if leg.quantity < 0 and spot:
                short_legs.append((pos.symbol, spot, leg))
    if not short_legs:
        return []

    # Rule 1: same-expiry concentration.
    by_expiry: dict[str, list] = defaultdict(list)
    for underlying, spot, leg in short_legs:
        by_expiry[leg.expiry].append((underlying, leg))
    cluster_violation_expiries = {e for e, legs in by_expiry.items() if len(legs) > max_per_expiry}

    # Rule 2: strike spacing -- mark which specific legs participate in a
    # too-tight pair (a leg can be involved in more than one tight gap).
    spacing_violation_legs: set[int] = set()
    by_group: dict[tuple, list] = defaultdict(list)
    for underlying, spot, leg in short_legs:
        by_group[(underlying, leg.expiry, leg.option_type)].append((spot, leg))
    for (underlying, expiry, opt_type), entries in by_group.items():
        if len(entries) < 2:
            continue
        spot = entries[0][0]
        ordered = sorted(entries, key=lambda e: e[1].strike)
        for (_, leg_a), (_, leg_b) in zip(ordered, ordered[1:]):
            gap_pct = abs(leg_b.strike - leg_a.strike) / spot * 100 if spot else 0
            if gap_pct < min_spacing_pct:
                spacing_violation_legs.add(id(leg_a))
                spacing_violation_legs.add(id(leg_b))

    # Rules 3 & 4: realized-vol expected-move buffer + BS delta, with the
    # NIFSEL -> Nifty proxy fallback (see _realized_vol_annualized's own
    # docstring for why a real IV back-solve isn't reliable here).
    vol_cache: dict[str, Optional[float]] = {}
    vol_is_proxy: dict[str, bool] = {}
    for underlying, spot, leg in short_legs:
        if underlying in vol_cache:
            continue
        vol = _realized_vol_annualized(_INDEX_TICKERS[underlying])
        if vol is None and underlying != "NIFTY":
            vol = _realized_vol_annualized(_INDEX_TICKERS["NIFTY"])
            vol_is_proxy[underlying] = vol is not None
        vol_cache[underlying] = vol

    results = []
    for underlying, spot, leg in short_legs:
        vol = vol_cache.get(underlying)
        expected_move_pct = vol * (leg.dte / 365) ** 0.5 * 100 * expected_move_multiple if vol else None
        buffer_pct = abs(leg.strike - spot) / spot * 100 if spot else None
        delta = _bs_delta(spot, leg.strike, leg.dte, vol, leg.option_type) if vol else None
        results.append({
            "underlying": underlying,
            "leg": leg,
            "spot": spot,
            "vol": vol,
            "vol_is_proxy": vol_is_proxy.get(underlying, False),
            "buffer_pct": buffer_pct,
            "expected_move_pct": expected_move_pct,
            "buffer_violation": buffer_pct is not None and expected_move_pct is not None and buffer_pct < expected_move_pct,
            "delta": delta,
            "delta_violation": delta is not None and abs(delta) > delta_roll_threshold,
            "spacing_violation": id(leg) in spacing_violation_legs,
            "cluster_violation": leg.expiry in cluster_violation_expiries,
            "expected_move_multiple": expected_move_multiple,
            "delta_roll_threshold": delta_roll_threshold,
            "max_per_expiry": max_per_expiry,
            "min_spacing_pct": min_spacing_pct,
        })
    return results


def _classify_fno_action(ev: dict, roll_cutoff_dte: int = 5) -> tuple[str, str]:
    """India F&O verb classification -- CLOSE/ROLL/WATCH/HOLD, the same
    5-verb family as the US book's CLOSE/TRIM/ENTER/HOLD/WATCH (TRIM has no
    real equivalent for a single option leg -- ROLL is the risk-reduction
    action that plays TRIM's role here). Added 2026-09-25 per direct
    request to turn the concentration/buffer/delta guard into concrete
    actions, not just flags to read.

    roll_cutoff_dte=5 -- once a short leg is this close to expiry, rolling
    a leg that's already at real directional delta mostly just defers the
    same risk to a new strike/date rather than fixing anything; closing and
    taking the loss is the cleaner action. Above that DTE there's enough
    time value left for a roll-out-and-down to be a real credit, not just a
    deferral.
    """
    leg = ev["leg"]
    if ev["delta_violation"]:
        if leg.dte <= roll_cutoff_dte:
            return "CLOSE", f"delta ≈{ev['delta']:+.2f}, only {leg.dte}d left — too late to roll productively, close and take the loss"
        return "ROLL", f"delta ≈{ev['delta']:+.2f} exceeds {ev['delta_roll_threshold']} threshold, {leg.dte}d left — roll out/down for a credit"
    if ev["buffer_violation"] or ev["spacing_violation"] or ev["cluster_violation"]:
        reasons = []
        if ev["buffer_violation"]:
            reasons.append(f"buffer {ev['buffer_pct']:.1f}% vs {ev['expected_move_pct']:.1f}% expected move")
        if ev["spacing_violation"]:
            reasons.append("strikes stacked too close to another same-side leg")
        if ev["cluster_violation"]:
            reasons.append(f"shares an over-crowded expiry ({ev['max_per_expiry']}+ legs)")
        return "WATCH", "; ".join(reasons)
    return "HOLD", "no rule violations"


def get_india_priority_actions(positions: list, india_cfg: dict) -> list[dict]:
    """Bottom-up India priority-action list -- F&O legs (CLOSE/ROLL/WATCH)
    from the risk-rules evaluation above, plus equity ENTER/CLOSE items due
    this month from data/india_6month_plan.yaml. Mirrors the US book's
    get_priority_actions() (CLOSE/TRIM/ENTER only, bottom-up, not the full
    heat table) -- HOLD legs are deliberately excluded from this list, same
    reasoning as the US side: a stable book shouldn't flood the tracker.
    """
    import yaml as _yaml
    actions = []

    for ev in _evaluate_fno_legs(positions):
        verb, reason = _classify_fno_action(ev)
        if verb == "HOLD":
            continue
        leg = ev["leg"]
        actions.append({
            "market": "india", "asset": "fno",
            "symbol": f"{ev['underlying']} {leg.option_type} {leg.strike:g} ({leg.expiry})",
            "verb": verb, "reason": reason,
            "pnl": leg.premium_received - leg.current_mark,
        })

    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "india_6month_plan.yaml",
    )
    try:
        with open(path) as f:
            plan = _yaml.safe_load(f) or {}
    except Exception:
        plan = {}

    start = datetime.strptime(plan["plan_start_date"], "%Y-%m-%d").date() if plan.get("plan_start_date") else None
    month_idx = max(1, min(6, (date.today() - start).days // 30 + 1)) if start else 1
    by_symbol = {p.symbol: p for p in positions} if positions else {}

    for sym, cfg in plan.get("equity_adds", {}).items():
        if month_idx in cfg.get("adds", {}):
            if cfg.get("condition"):
                continue  # conditional adds need a live check the trader already reads in the 6-month-plan section, not a blind ENTER
            actions.append({
                "market": "india", "asset": "equity", "symbol": sym,
                "verb": "ENTER",
                "reason": f"₹{cfg['adds'][month_idx]:,} scheduled add, month {month_idx} ({cfg.get('name', sym)})",
                "pnl": None,
            })

    for sym, cfg in plan.get("equity_exits", {}).items():
        if cfg.get("month") == month_idx:
            still_held = any(p.symbol == sym and p.shares for p in positions) if positions else False
            if still_held:
                actions.append({
                    "market": "india", "asset": "equity", "symbol": sym,
                    "verb": "CLOSE",
                    "reason": f"scheduled exit, month {month_idx}: {cfg.get('note', '')}",
                    "pnl": None,
                })

    return actions


def _check_fno_concentration_risk(positions: list) -> list[str]:
    """Checks currently open index F&O short legs against data/india_6month_
    plan.yaml's risk_rules -- added 2026-09-25 after tracing the real root
    cause of the Sep-29 cluster loss (-2,73,632): NOT macro deterioration
    (live-checked that day: Nifty -3.96% vs its own 50-day MA, -1.77% off
    its 2-week high, India VIX 12.69 -- a normal pullback), but a structural
    concentration problem -- 5+ short legs, one shared expiry, strikes
    stacked 0.4-1.4% apart, so one routine move took the whole cluster out
    together.

    Rule 3 was originally a flat min-OTM-buffer floor, revised the same day
    after the trader's own pushback: a flat floor is reactive AND caps the
    upside, since the FY-to-date realized F&O P&L (₹5,48,819 on this book's
    ~₹26L margin baseline, confirmed live against the FNOPortfolioDetails
    export) is generated specifically by selling close enough to the money
    to collect real premium -- a flat 6% floor would have blocked the very
    trades that made that number. Replaced with an expected-move buffer
    (scaled to the underlying's own realized vol and the leg's DTE) so it
    only tightens automatically when real volatility is actually elevated,
    and a separate delta-based defensive-roll flag (Rule 4) on already-open
    legs, so deteriorating trades get caught early without limiting how
    aggressively a trade can be entered in the first place. Rules 1 and 2
    are unchanged -- diversifying across expiry dates and strikes doesn't
    reduce the total premium collected, it just stops one date from carrying
    all the risk.
    """
    evaluations = _evaluate_fno_legs(positions)
    if not evaluations:
        return []

    out = ["## F&O CONCENTRATION & OTM-BUFFER GUARD", ""]
    flags = []
    seen_cluster_expiries = set()

    for ev in evaluations:
        leg = ev["leg"]
        underlying = ev["underlying"]

        if ev["cluster_violation"] and leg.expiry not in seen_cluster_expiries:
            seen_cluster_expiries.add(leg.expiry)
            siblings = [e for e in evaluations if e["leg"].expiry == leg.expiry]
            names = ", ".join(f"{e['underlying']} {e['leg'].strike:g}{e['leg'].option_type[0]}" for e in siblings)
            flags.append(
                f"🚨 **{len(siblings)} short legs share expiry {leg.expiry}** (cap: {ev['max_per_expiry']}) — "
                f"this is the exact Sep-29 pattern. Legs: {names}"
            )

        if ev["spacing_violation"]:
            flags.append(
                f"⚠️ **{underlying} {leg.option_type} {leg.strike:g} ({leg.expiry}) sits within "
                f"{ev['min_spacing_pct']}% of another same-side strike** — a single move can breach both together."
            )

        if ev["buffer_violation"]:
            spot = ev["spot"]
            direction = "ITM already" if (
                (leg.option_type.upper().startswith("P") and spot < leg.strike) or
                (leg.option_type.upper().startswith("C") and spot > leg.strike)
            ) else "thin cushion"
            vol_note = f"{ev['vol']*100:.1f}% realized vol" + (" (Nifty proxy — own history too short)" if ev["vol_is_proxy"] else "")
            flags.append(
                f"⚠️ **{underlying} {leg.option_type} {leg.strike:g} ({leg.expiry}): "
                f"{ev['buffer_pct']:.1f}% buffer vs {ev['expected_move_pct']:.1f}% expected move** "
                f"({direction}; {vol_note} × {ev['expected_move_multiple']}x over {leg.dte}d)"
            )

        if ev["delta_violation"]:
            vol_note = f"{ev['vol']*100:.1f}% realized vol" + (" (Nifty proxy — own history too short)" if ev["vol_is_proxy"] else "")
            flags.append(
                f"🔻 **{underlying} {leg.option_type} {leg.strike:g} ({leg.expiry}): "
                f"delta ≈{ev['delta']:+.2f} (est. from {vol_note}) exceeds "
                f"{ev['delta_roll_threshold']} roll threshold** — consider rolling/closing regardless of DTE."
            )

    if flags:
        out.extend(flags)
    else:
        r = evaluations[0]
        out.append(
            f"✅ No concentration/spacing/expected-move/delta violations against risk_rules "
            f"({r['max_per_expiry']} legs/expiry cap, {r['min_spacing_pct']}% min spacing, "
            f"{r['expected_move_multiple']}x expected-move buffer, {r['delta_roll_threshold']} delta roll threshold)."
        )
    out.append("")
    return out


def _check_6month_plan(positions: list, regime_signals: dict) -> list[str]:
    """Checks live data against data/india_6month_plan.yaml every run --
    trader-requested 2026-09-24, same self-checking pattern as the US book's
    active_decisions.yaml, so the plan built after the NIFSEL/NIFTY Sep-29
    drawdown review doesn't need to be manually re-verified each week.

    Real F&O margin (the ₹26L figure and its glide path) can't be checked
    live from these statement files -- that needs the trader's own
    Margin Details screen, same as the US side's SMA/Equity-percent figures.
    This renders the target and asks for a live confirmation rather than
    silently guessing a number that was already confirmed wrong twice this
    session before landing on ₹26L.
    """
    import yaml as _yaml

    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "india_6month_plan.yaml",
    )
    try:
        with open(path) as f:
            plan = _yaml.safe_load(f) or {}
    except Exception as e:
        return ["## 6-MONTH PLAN TRACKING", "", f"⚠️ Could not load {path}: {e}", ""]

    start = datetime.strptime(plan["plan_start_date"], "%Y-%m-%d").date()
    days_elapsed = (date.today() - start).days
    month_idx = max(1, min(6, days_elapsed // 30 + 1))

    out = ["## 6-MONTH PLAN TRACKING", "", f"**Month {month_idx} of 6** (plan started {start.isoformat()}, {days_elapsed} days ago)", ""]

    # F&O margin glide path -- needs a live confirmation, can't be derived
    # from the statement files.
    glide = plan.get("fno_margin_glide_path", {})
    target = glide.get(f"month_{month_idx}_target")
    out.append(f"**F&O margin target this month: ₹{target:,}** (today's confirmed baseline: ₹{glide.get('today', 0):,}) — confirm live against your Margin Details screen, not derivable from the statement export.")
    out.append("")

    # Return-gate conditions -- 3 of 4 now checkable live (was 2), trader-
    # requested 2026-09-25 after confirming FRED's DGS10 series (real US
    # 10-year Treasury yield) is fetchable the exact same free, no-key way
    # macro_risk_analyzer.py already pulls HYOAS/T10Y2Y. FII flow data has
    # no free, reliably-scrapeable source (checked live 2026-09-25: NSDL's
    # real FPI portal TLS-fails, moneycontrol 403s, NSE's own FII/FPI report
    # path 404s) -- stays a real, honest manual check, not a guess.
    out.append("**F&O return-gate status:**")
    vix = regime_signals.get("india_vix", {}).get("value")
    ma = regime_signals.get("nifty50_ma", {})
    above_50d = ma.get("above_50d")
    us_10y = _fetch_us_10y_yield()
    cond1 = "✅" if above_50d else ("❌" if above_50d is not None else "❓ no data")
    cond2 = "✅" if (vix is not None and vix <= 12.5) else ("❌" if vix is not None else "❓ no data")
    cond3 = "✅" if (us_10y is not None and us_10y < 5.0) else ("❌" if us_10y is not None else "❓ no data")
    out.append(f"- {cond1} Nifty above 50-day MA (live: {ma.get('current', '?')} vs MA {ma.get('ma50', '?')})")
    out.append(f"- {cond2} India VIX back toward ~11-12 (live: {vix})")
    out.append(f"- {cond3} US 10-year yield off the 5%+ level (live: {us_10y}%, via FRED DGS10)")
    out.append("- ❓ FII outflows slowing 2+ weeks — no free reliable data source exists (checked "
                "NSDL/moneycontrol/NSE live 2026-09-25); check manually")
    out.append("")

    # Equity adds due this month, checked against live position values.
    adds = plan.get("equity_adds", {})
    due_this_month = {sym: cfg for sym, cfg in adds.items() if month_idx in cfg.get("adds", {})}
    if due_this_month:
        out.append("**Equity adds planned for this month:**")
        by_symbol = {p.symbol: p for p in positions} if positions else {}
        for sym, cfg in due_this_month.items():
            amt = cfg["adds"][month_idx]
            cond_note = f" — {cfg['condition']}" if cfg.get("condition") else ""
            live = by_symbol.get(sym)
            live_note = f"live value ₹{live.shares * live.current_price:,.0f}" if live and live.shares else "not found in live positions"
            out.append(f"- **{sym}** ({cfg.get('name', sym)}): +₹{amt:,} planned — {live_note}{cond_note}")
        out.append("")

    # Equity exits due this month.
    exits = plan.get("equity_exits", {})
    for sym, cfg in exits.items():
        if cfg.get("month") == month_idx:
            still_held = any(p.symbol == sym and p.shares for p in positions) if positions else False
            status = "⚠️ still showing in live positions — exit not confirmed" if still_held else "✅ confirmed exited"
            out.append(f"**Exit check — {sym}** ({cfg.get('name', sym)}): {status}. {cfg.get('note', '')}")
            out.append("")

    # ETF tranche due this month.
    etf = plan.get("etf_tranches", {}).get(f"month_{month_idx}")
    if etf:
        out.append(f"**ETF tranche this month:** Nifty 50 ₹{etf.get('nifty50', 0):,} + Bank Nifty ₹{etf.get('banknifty', 0):,} — not tracked live (ETF holdings aren't in the F&O/equity statement symbol set); confirm execution manually.")
        out.append("")

    out.append(f"_Full plan: `data/india_6month_plan.yaml`. Dashboard: https://claude.ai/artifact/Xg7Akk1Agxvk4kQedjEYtX_")
    out.append("")
    return out


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
