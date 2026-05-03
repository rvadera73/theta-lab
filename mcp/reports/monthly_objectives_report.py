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
    monthly_option_pnl_series,
    monthly_premium,
    previous_month,
    project_value,
    save_html,
)
from analysis.india_regime import detect_india_regime
from analysis.regime import detect_regime
from config import ACCOUNT_A, ACCOUNT_B, ACCOUNT_C, PERMANENT_EXITS
from reports.dynamic_screener import screen_india_opportunities, screen_us_opportunities
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
    regime_data = detect_regime()
    india_regime_data = detect_india_regime()

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

    # --- YTD calculations ---
    annual_target = 1_200_000  # $1.2M/year = $100K/month × 12
    months_elapsed = today.month - 1 + (today.day / 30)  # fractional months through today
    ytd_expected = round(annual_target / 12 * months_elapsed)  # what you should have at this point
    # Sum all completed months this year for each account
    all_txns = [row for rows in txns.values() for row in rows]
    ytd_series = monthly_option_pnl_series(all_txns)  # list of monthly net premiums, all-time
    # Filter to current year only (series items are sorted by month key)
    ytd_income = float(snapshot.get("ytd_net_options_income", 0) or 0)
    # If transactions available, prefer computed sum over snapshot
    if all_txns:
        from reports.report_utils import parse_txn_date, parse_option_symbol, parse_amount
        ytd_income = 0.0
        for row in all_txns:
            txn_date = parse_txn_date(row.get("Date", ""))
            if not txn_date or txn_date.year != today.year:
                continue
            parsed = parse_option_symbol(row.get("Symbol", ""))
            if not parsed:
                continue
            action = str(row.get("Action", "")).strip()
            amount = parse_amount(row.get("Amount", 0))
            if "Sell to Open" in action and amount > 0:
                ytd_income += amount
            elif action == "Buy to Close" and amount < 0:
                ytd_income -= abs(amount)
    ytd_income = round(ytd_income, 0)
    ytd_vs_expected_gap = ytd_income - ytd_expected
    # Monthly breakdown for the bar chart (Jan→current month)
    import calendar
    monthly_breakdown = []
    for m in range(1, today.month + 1):
        month_start = today.replace(month=m, day=1)
        m_income = monthly_premium(all_txns, month_start) if all_txns else 0.0
        monthly_breakdown.append({
            "label": calendar.month_abbr[m],
            "income": round(m_income, 0),
            "target": 100_000,
        })

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

    # Build assigned book from live Schwab positions (us["positions"]) — never stale snapshot.
    # For each equity position: cost_basis from Schwab, monthly_cc from active short calls.
    assigned_rows = []
    idle_positions = []
    book_value = 0.0
    _DEFAULT_CC_YIELD = 0.015   # fallback for when no calls are open
    for pos in us.get("positions", []):
        if pos.shares <= 0:
            continue
        cost_basis_total = (pos.stock_cost_basis or 0) * pos.shares
        market_value = (pos.current_price or 0) * pos.shares
        book_value += market_value
        # Monthly CC = sum of premium already received on open short calls / hold_days * 30
        open_calls = [lg for lg in pos.option_legs if lg.quantity < 0 and lg.option_type == "CALL"]
        if open_calls:
            # Annualise: premium_received / original_dte * 30 per leg
            cc = sum(
                abs(lg.premium_received) / max(lg.dte + 30, 30) * 30
                for lg in open_calls
            )
        else:
            cc = 0.0
        remaining = max(0.0, cost_basis_total - market_value)
        months = round(remaining / cc, 1) if cc > 0 else None
        assigned_rows.append([
            pos.symbol,
            str(int(pos.shares)),
            f"${remaining:,.0f}",
            f"${cc:,.0f}/mo" if cc > 0 else "$0 IDLE",
            f"{months} mo" if months is not None else "∞",
        ])
        if cc == 0:
            idle_positions.append(pos.symbol)

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

    # --- Gap Closure Analysis ---
    months_remaining = max(0.5, 12 - months_elapsed)
    remaining_to_target = max(0, annual_target - ytd_income)
    required_monthly = round(remaining_to_target / months_remaining)

    # Idle CC potential: estimated from live IV if available, else formula-based.
    # iv * sqrt(30/365) * otm_factor — same formula used across the screener.
    # No per-name hardcoded yields; LEGACY_EXIT_RULES.min_cc_strike_pct_above_price
    # enforces the OTM floor at order time.
    _DEFAULT_CC_YIELD = 0.015      # fallback: ~1.5% monthly on price × shares (5% OTM CC)
    _EXIT_CC_YIELD    = 0.025      # PERMANENT_EXIT names: sell closer-to-money to exit faster
    idle_cc_opportunities = []
    total_idle_cc_potential = 0.0
    for item in snapshot.get("assigned_positions", []):
        sym = item["symbol"]
        cc = float(item.get("monthly_cc", 0) or 0)
        if cc > 0:
            continue  # already active
        shares = int(item.get("shares", 0) or 0)
        price = current_price(sym) or float(item.get("cost_basis", 0) or 0)
        if not shares or not price:
            continue
        is_exit = sym in PERMANENT_EXITS
        yield_pct = _EXIT_CC_YIELD if is_exit else _DEFAULT_CC_YIELD
        potential = round(shares * price * yield_pct)
        idle_cc_opportunities.append({
            "symbol":  sym,
            "shares":  shares,
            "price":   round(price, 2),
            "potential": potential,
            "note": "permanent exit — sell OTM CCs above current price to accelerate exit" if is_exit
                    else "write OTM CC per LEGACY_EXIT_RULES thresholds",
        })
        total_idle_cc_potential += potential

    # Efficiency lever: improving capture rate 58% → 65%
    current_capture = float((capture.get("capture_rate") or 0))
    # Gross credits implied: ytd_income / capture_rate
    gross_credits_est = ytd_income / max(current_capture / 100, 0.01) if current_capture else 0
    improved_income_est = round(gross_credits_est * 0.65 - ytd_income) if gross_credits_est else 0
    efficiency_monthly_gain = round(improved_income_est / max(months_elapsed, 1))

    # Scenario projections (what year-end looks like under each path)
    scenarios = [
        {
            "name": "Current pace (no change)",
            "monthly": round(ytd_income / max(months_elapsed, 1)),
            "color": "#cc2200",
            "note": "Assumes Feb-level months recur. Needs discipline to avoid.",
        },
        {
            "name": "Activate all idle CCs",
            "monthly": round(ytd_income / max(months_elapsed, 1) + total_idle_cc_potential),
            "color": "#b87800",
            "note": f"Write CCs on {', '.join(i['symbol'] for i in idle_cc_opportunities[:4])} + others = +${total_idle_cc_potential:,.0f}/mo",
        },
        {
            "name": "Idle CCs + improve capture to 65%",
            "monthly": round(ytd_income / max(months_elapsed, 1) + total_idle_cc_potential + efficiency_monthly_gain),
            "color": "#b87800",
            "note": f"Tighten BTC discipline (+${efficiency_monthly_gain:,.0f}/mo from efficiency gains)",
        },
        {
            "name": "Stretch: sustain April pace",
            "monthly": 110_000,
            "color": "#1a7a1a",
            "note": "April was $110K — achievable if no more Feb-type months",
        },
    ]
    for s in scenarios:
        projected = round(ytd_income + s["monthly"] * months_remaining)
        s["projected_year_end"] = projected
        s["pct_of_target"] = round(projected / annual_target * 100)
        s["gap_to_target"] = annual_target - projected

    # Capital lever: how much extra AUM needed to close gap at current yield rate
    active_aum_estimate = float(snapshot.get("active_options_aum") or 700_000)
    if active_aum_estimate <= 0:
        active_aum_estimate = 700_000
    current_monthly_yield_pct = (ytd_income / max(months_elapsed, 1)) / active_aum_estimate
    monthly_gap_to_close = max(0, required_monthly - (ytd_income / max(months_elapsed, 1) + total_idle_cc_potential + efficiency_monthly_gain))
    capital_needed_to_close = round(monthly_gap_to_close / max(current_monthly_yield_pct, 0.001)) if monthly_gap_to_close > 0 else 0

    gap_closure = {
        "required_monthly": required_monthly,
        "months_remaining": round(months_remaining, 1),
        "remaining_to_target": remaining_to_target,
        "idle_cc_opportunities": idle_cc_opportunities,
        "total_idle_cc_potential": round(total_idle_cc_potential),
        "efficiency_monthly_gain": efficiency_monthly_gain,
        "scenarios": scenarios,
        "capital_needed": capital_needed_to_close,
        "monthly_yield_pct": round(current_monthly_yield_pct * 100, 2),
        "active_aum": active_aum_estimate,
    }

    india_vix = (
        india_regime_data.get("signals", {}).get("india_vix", {}).get("value")
        if isinstance(india_regime_data.get("signals", {}).get("india_vix", {}), dict)
        else None
    )
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
        "regime": regime_data,
        "india_regime": india_regime_data,
        "india_vix": india_vix if india_vix is not None else 15.0,
        "ytd": {
            "income": ytd_income,
            "annual_target": annual_target,
            "ytd_expected": ytd_expected,
            "gap": ytd_vs_expected_gap,
            "months_elapsed": round(months_elapsed, 1),
            "monthly_breakdown": monthly_breakdown,
            "run_rate_annual": round(ytd_income / max(months_elapsed, 0.5) * 12),
        },
        "gap_closure": gap_closure,
    }

    # Dynamic screener — regime-aware new entry candidates
    regime_str = data.get("regime", {}).get("regime", "TRANSITIONING")
    current_us_symbols = [p.symbol for p in us.get("positions", [])]
    current_india_symbols = [p.symbol for p in india.get("positions", [])] if india.get("positions") else []

    us_candidates = screen_us_opportunities(regime_str, current_us_symbols, top_n=8)
    india_candidates = screen_india_opportunities(
        data.get("india_vix", 15.0), current_india_symbols, top_n=6
    )
    data["us_screener"] = us_candidates
    data["india_screener"] = india_candidates

    # Portfolio heat scan — uses live positions already loaded above
    try:
        from analysis.heat_scanner import heat_from_positions, format_heat_html
        all_positions = us.get("positions", []) + list(india.get("positions", []))
        if all_positions:
            heat_result = heat_from_positions(all_positions, regime_str)
            data["portfolio_heat"] = heat_result
            data["portfolio_heat_html"] = format_heat_html(heat_result)
    except Exception as e:
        data["portfolio_heat"] = {}
        data["portfolio_heat_html"] = f"<p style='color:#999'>Heat scanner unavailable: {e}</p>"

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
