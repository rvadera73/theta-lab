"""
HTML email formatter and Resend sender.
Setup: sign up at resend.com → API Keys → Create API Key.
Store in .env as RESEND_API_KEY.
Free tier: 3,000 emails/month, no credit card required.
Default sender: onboarding@resend.dev (works without a custom domain).
"""

import os
from datetime import datetime

try:
    import resend as resend_client
    _RESEND_AVAILABLE = True
except ImportError:
    _RESEND_AVAILABLE = False


# ---------------------------------------------------------------------------
# HTML Builder
# ---------------------------------------------------------------------------

def _color(signal: str) -> str:
    colors = {
        "EXCELLENT": "#1a7a1a", "STRONG": "#1a7a1a", "STRONG GO": "#1a7a1a",
        "GOOD": "#2d8a2d", "GO": "#2d8a2d", "ON TRACK": "#2d8a2d",
        "FAST": "#2d8a2d", "POSITIVE": "#2d8a2d", "NORMAL": "#2d8a2d",
        "WATCH": "#b87800", "MODERATE": "#b87800", "CAUTION": "#b87800",
        "SLOW": "#b87800", "BEHIND": "#b87800",
        "POOR": "#cc2200", "THROTTLE": "#cc2200", "URGENT": "#cc2200",
        "NO GO — negative EV even with CC recovery": "#cc2200",
        "STALLED": "#cc2200", "NEGATIVE": "#cc2200",
        "CONSIDER EXIT": "#cc2200",
    }
    return colors.get(signal, "#444444")


def _badge(signal: str) -> str:
    color = _color(signal)
    return (
        f'<span style="background:{color};color:white;padding:2px 8px;'
        f'border-radius:3px;font-size:12px;font-weight:bold;">{signal}</span>'
    )


def _section(title: str, content: str) -> str:
    return f"""
<div style="margin:20px 0;padding:16px;border:1px solid #e0e0e0;border-radius:6px;">
  <h2 style="margin:0 0 12px 0;font-size:16px;color:#222;border-bottom:2px solid #333;padding-bottom:6px;">
    {title}
  </h2>
  {content}
</div>"""


def _table(headers: list[str], rows: list[list[str]]) -> str:
    header_html = "".join(
        f'<th style="background:#333;color:white;padding:8px 12px;text-align:left;">{h}</th>'
        for h in headers
    )
    rows_html = ""
    for i, row in enumerate(rows):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        cells = "".join(
            f'<td style="padding:7px 12px;border-bottom:1px solid #eee;">{c}</td>'
            for c in row
        )
        rows_html += f'<tr style="background:{bg};">{cells}</tr>'
    return f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead><tr>{header_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>"""


def build_html_email(data: dict, report_date: str = None) -> str:
    """
    Build full HTML email from dashboard data dict.
    data keys expected:
      monthly_target, regime, vix_term, metrics, portfolio_health,
      monte_carlo, top_actions, breakeven_tracker, kelly_candidates
    """
    if not report_date:
        report_date = datetime.now().strftime("%B %d, %Y")

    # ---- Monthly Target Section ----
    mt = data.get("monthly_target", {})
    target_pct = mt.get("pct_of_target", 0)
    target_bar_width = min(100, int(target_pct))
    bar_color = "#1a7a1a" if target_pct >= 80 else ("#b87800" if target_pct >= 50 else "#cc2200")

    monthly_html = f"""
<div style="margin-bottom:12px;">
  <div style="font-size:28px;font-weight:bold;color:#222;">${mt.get('combined_total', 0):,.0f}</div>
  <div style="color:#666;font-size:13px;">of ${mt.get('target_monthly', 100000):,.0f} target ({target_pct:.1f}%)</div>
  <div style="background:#e0e0e0;height:12px;border-radius:6px;margin:8px 0;">
    <div style="background:{bar_color};width:{target_bar_width}%;height:12px;border-radius:6px;"></div>
  </div>
  <div style="font-size:12px;color:#666;">
    Options premium: <b>${mt.get('net_options_premium', 0):,.0f}</b> &nbsp;|&nbsp;
    Equity change: <b>${mt.get('unrealized_equity_change', 0):,.0f}</b> &nbsp;|&nbsp;
    Remaining: <b>${mt.get('remaining_to_target', 0):,.0f}</b>
  </div>
</div>
{_badge(mt.get('signal', 'WATCH'))} {mt.get('interpretation', '')}"""

    # ---- Regime & VIX Section ----
    vix = data.get("vix_term", {})
    regime = data.get("regime", {})
    regime_html = f"""
<table style="width:100%;font-size:13px;">
<tr>
  <td style="padding:4px 8px;"><b>Regime:</b></td>
  <td>{_badge(regime.get('regime', 'BEAR_SIDEWAYS'))} {regime.get('note', '')}</td>
</tr>
<tr>
  <td style="padding:4px 8px;"><b>VIX:</b></td>
  <td>{vix.get('vix', '—')} &nbsp;|&nbsp; VIX3M: {vix.get('vix3m', '—')} &nbsp;|&nbsp; Ratio: <b>{vix.get('ratio', '—')}</b> {_badge(vix.get('signal', ''))}</td>
</tr>
<tr>
  <td style="padding:4px 8px;"><b>Entry quality:</b></td>
  <td>{_badge(vix.get('entry_quality', ''))} &nbsp; {vix.get('action', '')}</td>
</tr>
</table>"""

    # ---- Portfolio Health Section ----
    ph = data.get("portfolio_health", {})
    metrics = data.get("metrics", {})
    capture = metrics.get("premium_capture", {})
    pf = metrics.get("profit_factor", {})

    health_rows = [
        ["Assigned Equity Book", f"${ph.get('assigned_book', 0):,.0f}",
         f"Target: ${ph.get('danger_zone', 375000):,.0f}", _badge(ph.get('book_signal', 'WATCH'))],
        ["Net Options Premium (YTD)", f"${ph.get('ytd_net_premium', 0):,.0f}", "Pace vs 15% target", ""],
        ["Premium Capture Rate", f"{capture.get('capture_rate', 0)}%", "Target: 65-70%", _badge(capture.get('signal', ''))],
        ["Profit Factor", f"{pf.get('profit_factor', 0)}", "Target: >2.0", _badge(pf.get('signal', ''))],
        ["Win Rate", f"{pf.get('win_rate', 0)}%", f"{pf.get('win_count', 0)}W / {pf.get('loss_count', 0)}L", ""],
    ]
    health_html = _table(["Metric", "Value", "Benchmark", "Status"], health_rows)

    # ---- Monte Carlo Section ----
    mc = data.get("monte_carlo", {})
    mc_html = f"""
<div style="font-size:13px;">
  {_badge(mc.get('signal', 'NORMAL'))}
  <b>P(exceed ${mc.get('danger_zone_threshold', 375000):,.0f} danger zone): {mc.get('p_exceed_danger_zone', 0)}%</b>
  &nbsp;| Expected assigned book: ${mc.get('expected_assigned_equity', 0):,.0f}
  <br><br>
  <b>Distribution:</b> P10=${mc.get('percentiles', {}).get('p10', 0):,.0f} |
  P25=${mc.get('percentiles', {}).get('p25', 0):,.0f} |
  P50=${mc.get('percentiles', {}).get('p50', 0):,.0f} |
  P75=${mc.get('percentiles', {}).get('p75', 0):,.0f} |
  P90=${mc.get('percentiles', {}).get('p90', 0):,.0f}
  <br><br>
  <i>{mc.get('action', '')}</i>
</div>"""

    # ---- Top Actions Section ----
    actions = data.get("top_actions", [])
    action_rows = []
    for i, a in enumerate(actions[:7], 1):
        action_rows.append([
            f"<b>#{i}</b>",
            f"<b>{a.get('symbol', '')}</b>",
            a.get("action", ""),
            a.get("condition", ""),
            _badge(a.get("priority", "WATCH")),
        ])
    actions_html = _table(["#", "Symbol", "Action", "Condition", "Priority"], action_rows)

    # ---- Breakeven Tracker Section ----
    bev_items = data.get("breakeven_tracker", [])
    bev_rows = [
        [
            b.get("symbol", ""),
            f"${b.get('unrealized_loss', 0):,.0f}",
            f"${b.get('monthly_cc_premium', 0):,.0f}/mo",
            f"{b.get('months_to_breakeven', '?')} mo",
            f"{b.get('velocity_pct_month', 0)}%/mo",
            _badge(b.get("signal", "")),
        ]
        for b in bev_items
    ]
    bev_html = _table(
        ["Symbol", "Remaining Loss", "CC/Month", "Months to BEV", "Velocity", "Status"],
        bev_rows
    ) if bev_rows else "<p style='color:#666;font-size:13px;'>No assigned positions tracked.</p>"

    # ---- Kelly Candidates Section ----
    kelly_items = data.get("kelly_candidates", [])
    kelly_rows = [
        [
            k.get("symbol", ""),
            f"{k.get('pop', 0)*100:.0f}%",
            f"{k.get('half_kelly_pct', 0):.1f}%",
            str(k.get("max_contracts", 0)),
            f"${k.get('dollar_risk', 0):,.0f}",
            _badge(k.get("signal", "")),
        ]
        for k in kelly_items[:5]
    ]
    kelly_html = _table(
        ["Symbol", "PoP", "Half-Kelly %", "Max Contracts", "$ At Risk", "Signal"],
        kelly_rows
    ) if kelly_rows else "<p style='color:#666;font-size:13px;'>No candidates computed.</p>"

    # ---- Assemble Full Email ----
    body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;color:#222;background:#fff;">

  <div style="background:#1a1a2e;color:white;padding:20px 24px;border-radius:6px 6px 0 0;">
    <h1 style="margin:0;font-size:22px;">Theta-Lab Weekly Dashboard</h1>
    <div style="font-size:13px;color:#aaa;margin-top:4px;">{report_date} &nbsp;|&nbsp; Bear/Sideways Regime</div>
  </div>

  {_section("Monthly Target — $100K Combined (Premium + Equity)", monthly_html)}
  {_section("Market Regime & VIX Term Structure", regime_html)}
  {_section("Portfolio Health Metrics", health_html)}
  {_section("Monte Carlo — Assignment Probability", mc_html)}
  {_section("Top Actions This Week", actions_html)}
  {_section("Assigned Positions — Breakeven Tracker", bev_html)}
  {_section("Entry Candidates — Kelly Sizing", kelly_html)}

  <div style="padding:12px 16px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:20px;">
    Generated by Theta-Lab on {datetime.now().strftime('%Y-%m-%d %H:%M')} ET.
    Data from latest Schwab CSV exports. Verify all figures before trading.
  </div>

</body>
</html>"""

    return body


# ---------------------------------------------------------------------------
# Resend Sender
# ---------------------------------------------------------------------------

def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    from_email: str,
    api_key: str,
) -> dict:
    """
    Send HTML email via Resend API.
    Free tier: 3,000 emails/month. No domain needed — use onboarding@resend.dev.
    """
    if not _RESEND_AVAILABLE:
        return {"success": False, "error": "resend package not installed — run: pip install resend"}
    try:
        resend_client.api_key = api_key
        params = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        response = resend_client.Emails.send(params)
        if response.get("id"):
            return {"success": True, "to": to_email, "subject": subject, "id": response["id"]}
        return {"success": False, "error": str(response)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _progress_bar(current: float, target: float, label: str = "") -> str:
    pct = min(100, int(current / target * 100)) if target else 0
    color = "#1a7a1a" if pct >= 80 else ("#b87800" if pct >= 50 else "#cc2200")
    return f"""
<div style="margin:8px 0;">
  <div style="font-size:12px;color:#666;">{label}</div>
  <div style="background:#e0e0e0;height:10px;border-radius:5px;margin:4px 0;">
    <div style="background:{color};width:{pct}%;height:10px;border-radius:5px;"></div>
  </div>
  <div style="font-size:11px;color:#666;">${current:,.0f} / ${target:,.0f} ({pct}%)</div>
</div>"""


def _warning_banner(message: str) -> str:
    return f"""
<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:4px;padding:10px 14px;margin:10px 0;font-size:13px;">
  ⚠️ <b>DATA WARNING:</b> {message}
</div>"""


def _action_card(symbol: str, action: str, reason: str, priority: str, details: str = "") -> str:
    color = _color(priority)
    return f"""
<div style="border-left:4px solid {color};padding:10px 14px;margin:8px 0;background:#fafafa;border-radius:0 4px 4px 0;">
  <div style="font-size:14px;font-weight:bold;">{symbol} — {_badge(priority)}</div>
  <div style="font-size:13px;color:#333;margin-top:4px;"><b>Action:</b> {action}</div>
  <div style="font-size:12px;color:#666;margin-top:2px;">{reason}</div>
  {f'<div style="font-size:12px;color:#444;margin-top:4px;">{details}</div>' if details else ''}
</div>"""


def build_weekly_combined_html(data: dict, report_date: str = None) -> str:
    """Build HTML for the Sunday weekly combined US+India report."""
    if not report_date:
        report_date = datetime.now().strftime("%B %d, %Y")
    header = data.get("header", {})
    us_regime = data.get("us_regime", {})
    india_regime = data.get("india_regime", {})
    warning = _warning_banner(data["warning"]) if data.get("warning") else ""
    header_html = f"""
<div style="font-size:13px;line-height:1.7;">
  <div><b>Date:</b> {header.get('date', report_date)}</div>
  <div><b>US Regime:</b> {_badge(header.get('us_regime', 'WATCH'))} &nbsp; New entries: <b>{'YES' if header.get('us_entries') else 'NO'}</b></div>
  <div><b>India Regime:</b> {_badge(header.get('india_regime', 'WATCH'))} &nbsp; New entries: <b>{'YES' if header.get('india_entries') else 'NO'}</b></div>
  <div><b>Source:</b> {data.get('data_source', '—')}</div>
</div>"""
    us_table = _table(["Signal", "Value", "Status"], [
        ["VIX", str(us_regime.get('signals', {}).get('vix', {}).get('value', '—')), us_regime.get('signals', {}).get('vix', {}).get('detail', 'Data unavailable')],
        ["SPX vs 50d/200d", f"{us_regime.get('signals', {}).get('sp500_ma', {}).get('current', '—')} / {us_regime.get('signals', {}).get('sp500_ma', {}).get('ma50', '—')} / {us_regime.get('signals', {}).get('sp500_ma', {}).get('ma200', '—')}", us_regime.get('note', '')],
    ])
    india_table = _table(["Signal", "Value", "Status"], [
        ["India VIX", str(india_regime.get('signals', {}).get('india_vix', {}).get('value', '—')), india_regime.get('signals', {}).get('india_vix', {}).get('detail', 'Data unavailable')],
        ["Nifty vs 50d/200d", f"{india_regime.get('signals', {}).get('nifty50_ma', {}).get('current', '—')} / {india_regime.get('signals', {}).get('nifty50_ma', {}).get('ma50', '—')} / {india_regime.get('signals', {}).get('nifty50_ma', {}).get('ma200', '—')}", india_regime.get('note', '')],
    ])
    account_a_cards = "".join(_action_card(a.get("symbol", "?"), a.get("action", "Review"), a.get("reason", ""), a.get("priority", "WATCH"), a.get("details", "")) for a in data.get("account_a_actions", [])) or "<p style='font-size:13px;color:#666;'>No Account A actions flagged.</p>"
    account_b_html = _table(["Symbol", "Wheel status", "Shares", "Next DTE", "Alert"], data.get("account_b", {}).get("rows", []))
    if data.get("account_b", {}).get("note"):
        account_b_html += f"<div style='font-size:12px;color:#666;margin-top:8px;'>{data['account_b']['note']}</div>"
    india_actions_html = _table(["Symbol", "DTE", "Current P&L", "Action"], data.get("india_actions", []))
    pace = data.get("income_pace", {})
    income_html = _progress_bar(pace.get("weekly_premium", 0), pace.get("weekly_target", 1), "Weekly premium pace") + _progress_bar(pace.get("ytd_premium", 0), pace.get("ytd_target", 1), "YTD premium pace")
    blackout_html = _table(["Symbol", "Earnings date", "Account", "Action"], data.get("earnings_blackout", []))
    margin = data.get("margin_health", {})
    margin_html = f"""
<div style="font-size:13px;line-height:1.8;">
  <div><b>Buying power:</b> ${margin.get('buying_power', 0):,.0f}</div>
  <div><b>Option requirement ratio:</b> {margin.get('option_requirement_ratio', '—')}%</div>
  <div style="color:#666;">{margin.get('note', '')}</div>
</div>"""
    kpis = data.get("kpis", {})
    kpi_html = _table(["KPI", "Value", "Status"], [
        ["Premium capture", f"{kpis.get('capture', {}).get('capture_rate', '—')}%", _badge(kpis.get('capture', {}).get('signal', 'WATCH'))],
        ["Profit factor", str(kpis.get('profit_factor', {}).get('profit_factor', '—')), _badge(kpis.get('profit_factor', {}).get('signal', 'WATCH'))],
        ["Sortino", str(kpis.get('sortino', {}).get('sortino_annualized', '—')), _badge(kpis.get('sortino', {}).get('signal', 'WATCH'))],
    ])
    return f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:880px;margin:0 auto;color:#222;background:#fff;">
  <div style="background:#1a1a2e;color:white;padding:20px 24px;border-radius:6px 6px 0 0;">
    <h1 style="margin:0;font-size:22px;">Theta-Lab Weekly Combined Report</h1>
    <div style="font-size:13px;color:#bbb;margin-top:4px;">{report_date}</div>
  </div>
  {warning}
  {_section("Header", header_html)}
  {_section("US Market Regime", us_table)}
  {_section("India Regime", india_table)}
  {_section("Account A Top 5 Actions", account_a_cards)}
  {_section("Account B Summary", account_b_html)}
  {_section("India FNO Actions", india_actions_html)}
  {_section("Income Pace", income_html)}
  {_section("Earnings Blackout (next 14 days)", blackout_html)}
  {_section("Margin / Cash Health", margin_html)}
  {_section("Portfolio KPIs", kpi_html)}
  <div style="padding:12px 16px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:20px;">Generated by Theta-Lab on {datetime.now().strftime('%Y-%m-%d %H:%M')}.</div>
</body></html>"""


def build_bimonthly_technical_html(data: dict, report_date: str = None) -> str:
    """Build HTML for the 15th bi-monthly technical analysis report."""
    if not report_date:
        report_date = datetime.now().strftime("%B %d, %Y")
    warning = _warning_banner(data["warning"]) if data.get("warning") else ""
    exits_html = "".join(_action_card(item.get("symbol", "?"), item.get("status", "Monitor"), item.get("progress", ""), "WATCH") for item in data.get("permanent_exits", []))
    return f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:980px;margin:0 auto;color:#222;background:#fff;">
  <div style="background:#102542;color:white;padding:20px 24px;border-radius:6px 6px 0 0;">
    <h1 style="margin:0;font-size:22px;">Theta-Lab Bi-monthly Technical Report</h1>
    <div style="font-size:13px;color:#cfd8dc;margin-top:4px;">{report_date} &nbsp;|&nbsp; {data.get('data_source', '—')}</div>
  </div>
  {warning}
  {_section("Assigned Stocks", _table(["Symbol", "Shares", "Cost Basis", "Current Price", "Unrealized P&L", "RSI(14)", "50d MA", "200d MA", "% off 52W high", "Breakeven Velocity", "CC Coverage", "Thesis", "Action"], data.get("assigned_stocks", [])))}
  {_section("Option Legs by Symbol", _table(["Symbol", "Type", "Strike", "Expiry", "DTE", "% OTM/ITM", "RSI", "MA vs 50d", "Tier", "Current premium", "Action"], data.get("option_legs", [])))}
  {_section("Permanent Exits — PYPL / MRNA", exits_html or "<p style='font-size:13px;color:#666;'>No permanent exit details available.</p>")}
  {_section("India Equity Holdings", _table(["Symbol", "Shares", "Avg Cost", "CMP", "Unrealized P&L", "RSI", "% off 52W high", "P/E", "Thesis", "Action"], data.get("india_equities", [])))}
  {_section("India FNO Positions", _table(["Symbol", "Type", "Strike", "Expiry", "DTE", "Delta", "Premium received", "Current P&L", "Action"], data.get("india_fno", [])))}
  {_section("India Sector Scorecard", _table(["Sector", "Outlook", "Note"], data.get("india_sector_scorecard", [])))}
</body></html>"""


def build_monthly_objectives_html(data: dict, report_date: str = None) -> str:
    """Build HTML for the monthly objectives gap analysis report."""
    if not report_date:
        report_date = datetime.now().strftime("%B %d, %Y")
    warning = _warning_banner(data["warning"]) if data.get("warning") else ""
    assigned = data.get("assigned_book", {})
    assigned_html = f"""
<div style="font-size:13px;line-height:1.8;">
  <div><b>Assigned book value:</b> ${assigned.get('value', 0):,.0f} vs bear cap ${assigned.get('cap', 375000):,.0f}</div>
  <div><b>Idle positions:</b> {', '.join(assigned.get('idle_positions', [])) or 'None'}</div>
</div>""" + _progress_bar(assigned.get("value", 0), assigned.get("cap", 1), "Assigned equity book vs cap")
    actions_html = "".join(_action_card(a.get("symbol", "?"), a.get("action", "Review"), a.get("reason", ""), a.get("priority", "WATCH"), a.get("details", "")) for a in data.get("gap_actions", [])) or "<p style='font-size:13px;color:#666;'>No gap actions generated.</p>"
    india = data.get("india_objectives", {})
    india_html = _progress_bar(india.get("pace", 0), india.get("target", 1), "India FNO pace") + _table(["Symbol", "Premium", "Current P&L", "Thesis alignment"], india.get("rows", []))
    return f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:920px;margin:0 auto;color:#222;background:#fff;">
  <div style="background:#1f3b4d;color:white;padding:20px 24px;border-radius:6px 6px 0 0;">
    <h1 style="margin:0;font-size:22px;">Theta-Lab Monthly Objectives Gap Analysis</h1>
    <div style="font-size:13px;color:#d7e3ea;margin-top:4px;">Previous month: {data.get('header', {}).get('previous_month', '—')} &nbsp;|&nbsp; Current pace: {data.get('header', {}).get('current_month', '—')}</div>
  </div>
  {warning}
  {_section("Income Objectives", _table(["Metric", "Target", "Last Month Actual", "Current Month Pace", "Gap", "Status"], data.get("income_rows", [])))}
  {_section("Portfolio KPIs (YTD)", _table(["Metric", "Target", "Actual", "Status"], data.get("kpi_rows", [])))}
  {_section("Assigned Book Health", assigned_html)}
  {_section("Breakeven Velocity", _table(["Symbol", "Shares", "Remaining Loss", "CC / month", "Months to breakeven"], data.get("breakeven_rows", [])))}
  {_section("Gap Analysis & Actions", actions_html)}
  {_section("India Objectives", india_html)}
</body></html>"""
