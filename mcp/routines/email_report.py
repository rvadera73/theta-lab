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


def _build_screener_section(candidates: list[dict], title: str) -> str:
    visible = [c for c in candidates if c.get("signal") in {"ENTER_NOW", "WATCH"}]
    visible.sort(
        key=lambda c: (
            {"ENTER_NOW": 0, "WATCH": 1}.get(c.get("signal", "WATCH"), 1),
            -float(c.get("opportunity_score", 0) or 0),
        )
    )
    source = visible[0] if visible else (candidates[0] if candidates else {})
    regime = source.get("regime", "TRANSITIONING")
    heavy_sectors = source.get("heavy_sectors") or []
    concentration = ", ".join(heavy_sectors) if heavy_sectors else "None"
    currency = "₹" if "India" in title else "$"

    if not visible:
        return f"""
<div style="background:white;margin-top:8px;padding:20px 24px;">
  <div style="font-size:18px;font-weight:bold;margin-bottom:6px;">{title}</div>
  <div style="font-size:13px;color:#666;line-height:1.8;">
    Regime: <b>{regime}</b> &nbsp;|&nbsp; Portfolio concentration: <b>{concentration}</b><br>
    No ENTER_NOW or WATCH candidates cleared the live filters this run.
  </div>
</div>"""

    cards = ""
    for candidate in visible:
        signal = candidate.get("signal", "WATCH")
        badge_color = "#1a7a1a" if signal == "ENTER_NOW" else "#b87800"
        tier = candidate.get("tier", "—")
        price = candidate.get("price")
        price_text = f"{currency}{float(price):,.2f}" if price is not None else "—"
        rsi = candidate.get("rsi")
        rsi_text = f"{float(rsi):.1f}" if rsi is not None else "—"
        ivr = candidate.get("ivr")
        ivr_text = f"{float(ivr):.1f}" if ivr is not None else "—"
        est_monthly_pct = candidate.get("est_monthly_pct")
        est_text = f"{float(est_monthly_pct):.1f}%/mo" if est_monthly_pct is not None else "—"
        pct_off_high = candidate.get("pct_off_high")
        pct_off_high_text = f"{float(pct_off_high):.1f}% off 52w high" if pct_off_high is not None else "52w high n/a"
        earnings_days = candidate.get("earnings_days")
        earnings_line = (
            f'<div style="font-size:12px;color:#b87800;margin-top:6px;">⚠️ earnings in {earnings_days} days</div>'
            if candidate.get("earnings_soon") and earnings_days is not None
            else ""
        )
        cards += f"""
  <div style="border:1px solid #ececec;border-radius:8px;padding:14px 16px;margin-top:10px;background:#fcfcfc;">
    <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap;">
      <div style="font-size:15px;font-weight:bold;"><span style="background:{badge_color};color:white;padding:3px 8px;border-radius:4px;font-size:11px;">{signal}</span> {candidate.get('symbol', '')} <span style="font-size:12px;color:#666;font-weight:normal;">{candidate.get('sector', '')}</span></div>
      <div><span style="background:#e9eef5;color:#334;padding:3px 8px;border-radius:4px;font-size:11px;font-weight:bold;">Tier {tier}</span></div>
    </div>
    <div style="font-size:13px;color:#444;line-height:1.8;margin-top:6px;">
      Price: <b>{price_text}</b> &nbsp;|&nbsp; RSI: <b>{rsi_text}</b> &nbsp;|&nbsp; IVR: <b>{ivr_text}</b> &nbsp;|&nbsp; ~<b>{est_text}</b> premium est.<br>
      Strategy: <b>{candidate.get('strategy', '—')}</b> &nbsp;|&nbsp; {pct_off_high_text}
    </div>
    <div style="font-size:12px;color:#666;margin-top:6px;line-height:1.7;">{candidate.get('reason', '')}</div>
    {earnings_line}
  </div>"""

    return f"""
<div style="background:white;margin-top:8px;padding:20px 24px;">
  <div style="font-size:18px;font-weight:bold;margin-bottom:6px;">{title}</div>
  <div style="font-size:13px;color:#666;line-height:1.8;">Regime: <b>{regime}</b> &nbsp;|&nbsp; Portfolio concentration: <b>{concentration}</b></div>
  {cards}
</div>"""


def build_weekly_combined_html(data: dict, report_date: str = None) -> str:
    """Build a readable weekly combined report email."""
    import re

    if not report_date:
        report_date = datetime.now().strftime("%B %d, %Y")

    def _money(value: float) -> str:
        return f"${float(value or 0):,.0f}"

    def _date_label(raw: str) -> str:
        try:
            return datetime.fromisoformat(str(raw)).strftime("%b %d")
        except Exception:
            return str(raw or "—")

    def _parse_leg(details: str) -> dict | None:
        match = re.search(r"(PUT|CALL)\s+([\d.]+)\s+exp\s+(\d{4}-\d{2}-\d{2})\s+\(([-\d]+) DTE\)", str(details or ""))
        if not match:
            return None
        return {
            "option_type": match.group(1),
            "strike": float(match.group(2)),
            "expiry": match.group(3),
            "dte": int(match.group(4)),
        }

    def _action_sentence(item: dict, leg: dict | None) -> tuple[str, str, str]:
        action = item.get("action", "Monitor")
        account = f"Acct {item.get('account', 'A')}" if item.get("account") else "Acct A"
        pnl = _money(item.get("combined_pnl", 0))
        if leg:
            option_label = f"${leg['strike']:g} {str(leg['option_type']).title()}"
            due = _date_label(str(leg["expiry"]))
            dte = max(int(leg["dte"]), 0)
        else:
            option_label = "current position"
            due = "soon"
            dte = 0

        if action == "Roll or close":
            headline = f"Roll by {due}" if leg else "Review this week"
            body = f"{option_label} expires in <b>{dte} days</b> — roll to the next cycle."
        elif action == "Take profit":
            headline = "Take profit"
            body = f"Close {option_label} and lock in the current gain."
        elif action == "Review / defend loss":
            headline = f"Review by {due}" if leg else "Review now"
            body = f"{option_label} needs attention now — manage risk before expiration."
        elif action == "Accelerate permanent exit":
            headline = "Reduce exposure"
            body = "Keep selling calls to shrink the position faster."
        else:
            headline = "Stay patient"
            body = f"{option_label} is on track — no trade needed today."
        foot = f"{account} · {dte if leg else '—'} DTE · Current P&L: {pnl}"
        return headline, body, foot

    def _watch_line(item: dict) -> str:
        leg = _parse_leg(item.get("details", ""))
        if leg:
            option_code = 'P' if leg['option_type'] == 'PUT' else 'C'
            option_label = f"${leg['strike']:g}{option_code} {_date_label(str(leg['expiry']))}"
            return f"• <b>{item.get('symbol', '?')}</b> — {option_label}, {max(int(leg['dte']), 0)} DTE, {item.get('action', 'monitor').lower()}"
        return f"• <b>{item.get('symbol', '?')}</b> — {item.get('action', 'Monitor')}, no action needed today"

    header = data.get("header", {})
    warning = _warning_banner(data["warning"]) if data.get("warning") else ""
    pace = data.get("income_pace", {})
    weekly_pace = float(pace.get("weekly_premium", 0) or 0)
    weekly_target = float(pace.get("weekly_target", 20000) or 20000)
    daily_pace = float(pace.get("daily_pace", 0) or 0)
    daily_target = float(pace.get("daily_target", 5000) or 5000)
    days_remaining = int(pace.get("days_remaining_week", 0) or 0)
    need_per_day = max(0.0, float(pace.get("need_per_remaining_day", 0) or 0))
    pct = max(0, min(100, int(round((weekly_pace / weekly_target) * 100)))) if weekly_target else 0
    income_color = "#1a7a1a" if pct >= 80 else ("#b87800" if pct >= 50 else "#cc2200")

    actions = data.get("account_a_actions", [])
    urgent_items = [item for item in actions if item.get("priority") == "URGENT"]
    watch_items = [item for item in actions if item.get("priority") != "URGENT"]

    urgent_cards = ""
    for item in urgent_items:
        leg = _parse_leg(item.get("details", ""))
        headline, body, foot = _action_sentence(item, leg)
        urgent_cards += f"""
<div style="border:1px solid #fde0de;border-left:4px solid #cc2200;background:#fff8f7;padding:12px 16px;border-radius:0 6px 6px 0;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
    <span style="font-size:16px;font-weight:bold;">{item.get('symbol', '?')}</span>
    <span style="font-size:11px;background:#cc2200;color:white;padding:2px 8px;border-radius:10px;">{headline}</span>
  </div>
  <div style="font-size:13px;color:#444;margin-top:6px;">{body}</div>
  <div style="font-size:12px;color:#888;margin-top:4px;">{foot}</div>
</div>"""
    if not urgent_cards:
        urgent_cards = '<div style="font-size:13px;color:#666;line-height:1.7;">No urgent US rolls or defenses right now.</div>'

    if watch_items:
        watch_list = '<div style="font-size:13px;line-height:2;color:#555;">' + '<br>'.join(_watch_line(item) for item in watch_items) + '</div>'
    else:
        watch_list = '<div style="font-size:13px;color:#666;line-height:1.7;">Everything else is in the green bucket.</div>'

    bc_rows = []
    notes = []
    for acct_key, acct_name in (("account_b", "Account B"), ("account_c", "Account C")):
        account_payload = data.get(acct_key, {})
        for row in account_payload.get("rows", []):
            symbol, strategy, _shares, next_dte, alert = (list(row) + ["—", "—", "—", "—", "—"])[:5]
            status = "Roll soon" if "≤21" in str(alert) else ("Monitor manually" if "Monitor" in str(alert) else "On track")
            bc_rows.append([acct_name, symbol, strategy, str(next_dte), status])
        if account_payload.get("note"):
            notes.append(account_payload["note"])
    if not bc_rows:
        bc_rows = [["Account B", "No positions", "—", "—", "All clear"]]
    bc_table = _table(["Account", "Symbol", "Strategy", "Next DTE", "Status"], bc_rows)
    if notes:
        bc_table += '<div style="font-size:12px;color:#777;margin-top:8px;line-height:1.7;">' + '<br>'.join(notes) + '</div>'

    india_rows = data.get("india_actions", [])
    if india_rows and india_rows[0][0] != "No F&O positions":
        india_blocks = []
        for row in india_rows:
            priority = "URGENT" if str(row[3]).lower() in ("close / roll", "defend") else "WATCH"
            india_blocks.append(
                f"<div style='border:1px solid #eee;border-radius:6px;padding:10px 12px;margin-bottom:8px;background:#fafafa;font-size:13px;'><b>{row[0]}</b> — {row[1]} DTE · {row[2]} · <span style='color:{_color(priority)};font-weight:bold;'>{row[3]}</span></div>"
            )
        india_html = ''.join(india_blocks)
    else:
        india_html = '<div style="font-size:13px;color:#666;line-height:1.7;">No India F&O action items right now.</div>'

    earnings_rows = data.get("earnings_blackout", [])
    if earnings_rows and earnings_rows[0][0] != "None found":
        earnings_html = '<div style="font-size:13px;line-height:2;color:#555;">' + '<br>'.join(
            f"• <b>{row[0]}</b> reports around {row[1]} ({row[2]}) — avoid new entries" for row in earnings_rows
        ) + '</div>'
    else:
        earnings_html = '<div style="font-size:13px;color:#666;line-height:1.7;">No known earnings blackout conflicts in the next 14 days.</div>'

    us_badge = _badge(str(header.get("us_regime", data.get("us_regime", {}).get("regime", "WATCH"))))
    india_badge = _badge(str(header.get("india_regime", data.get("india_regime", {}).get("regime", "WATCH"))))
    generated = datetime.now().strftime('%Y-%m-%d %H:%M')
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;max-width:680px;margin:0 auto;background:#f5f5f5;color:#222;padding:0;">
  <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:24px;border-radius:8px 8px 0 0;margin-bottom:0;">
    <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#7fb3f5;margin-bottom:4px;">THETA-LAB WEEKLY REPORT</div>
    <div style="font-size:20px;font-weight:bold;">{report_date}</div>
    <div style="margin-top:12px;display:flex;gap:12px;flex-wrap:wrap;">
      <span style="background:rgba(255,255,255,0.15);padding:4px 10px;border-radius:12px;font-size:12px;">🇺🇸 US: {us_badge} | New entries: <b>{'YES' if header.get('us_entries') else 'NO'}</b></span>
      <span style="background:rgba(255,255,255,0.15);padding:4px 10px;border-radius:12px;font-size:12px;">🇮🇳 India: {india_badge} | New entries: <b>{'YES' if header.get('india_entries') else 'NO'}</b></span>
    </div>
  </div>
  {warning}
  <div style="background:white;padding:20px 24px;border-bottom:1px solid #eee;">
    <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#999;margin-bottom:8px;">THIS WEEK'S INCOME GOAL: {_money(weekly_target)}</div>
    <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;">
      <div style="font-size:36px;font-weight:bold;color:{income_color};">{_money(weekly_pace)}</div>
      <div style="font-size:15px;color:#666;">projected this week</div>
    </div>
    <div style="background:#e8e8e8;height:8px;border-radius:4px;margin:12px 0 6px;">
      <div style="background:{income_color};width:{pct}%;height:8px;border-radius:4px;"></div>
    </div>
    <div style="font-size:12px;color:#888;display:flex;justify-content:space-between;gap:8px;">
      <span>$0</span>
      <span style="font-weight:bold;color:{income_color};">{pct}% of target</span>
      <span>{_money(weekly_target)}</span>
    </div>
    <div style="margin-top:12px;padding:10px;background:#f9f9f9;border-radius:6px;font-size:13px;color:#555;line-height:1.7;">
      📅 Daily avg: <b>{_money(daily_pace)}</b> (target {_money(daily_target)}/day) &nbsp;|&nbsp;
      ⏳ {days_remaining} trading days left this week &nbsp;|&nbsp;
      💡 Need <b>{_money(need_per_day)}/day</b> to hit target
    </div>
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:15px;font-weight:bold;color:#cc2200;margin-bottom:12px;">🔴 Act This Week ({len(urgent_items)} positions)</div>
    {urgent_cards}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:15px;font-weight:bold;color:#b87800;margin-bottom:12px;">🟡 Keep Watching ({len(watch_items)} positions)</div>
    {watch_list}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">📋 Account B & C Status</div>
    {bc_table}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">🇮🇳 India F&O Actions</div>
    {india_html}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">📅 Earnings Blackout — Next 14 Days</div>
    {earnings_html}
  </div>
  <div style="padding:16px 24px;font-size:11px;color:#999;text-align:center;margin-top:8px;">Generated by Theta-Lab · {generated} · Verify before trading</div>
</body>
</html>"""


def build_bimonthly_technical_html(data: dict, report_date: str = None) -> str:
    """Build a readable bi-monthly technical report email."""
    if not report_date:
        report_date = datetime.now().strftime("%B %d, %Y")

    def _date_label(raw: str) -> str:
        try:
            return datetime.fromisoformat(str(raw)).strftime("%b %d")
        except Exception:
            return str(raw or "—")

    def _int_or_none(raw: str) -> int | None:
        try:
            return int(float(str(raw).replace('%', '').strip()))
        except Exception:
            return None

    warning = _warning_banner(data["warning"]) if data.get("warning") else ""
    assigned_map = {
        row[0]: row for row in data.get("assigned_stocks", [])
        if row and row[0] not in ("Data unavailable", "No positions")
    }
    grouped: dict[str, list[list[str]]] = {}
    for row in data.get("option_legs", []):
        if not row or row[0] in ("Data unavailable", "No positions"):
            continue
        grouped.setdefault(row[0], []).append(row)

    symbol_cards = ""
    for symbol in sorted(set(assigned_map) | set(grouped)):
        assigned = assigned_map.get(symbol)
        legs = sorted(grouped.get(symbol, []), key=lambda row: (_int_or_none(row[4]) if len(row) > 4 else 999) or 999)
        subtitle_bits = []
        if assigned:
            subtitle_bits.append(f"{assigned[1]} sh assigned")
        accounts = sorted({str(leg[8]) for leg in legs if len(leg) > 8 and str(leg[8]).strip()})
        if accounts:
            subtitle_bits.append(f"Account {'/'.join(accounts)}")
        price_text = assigned[3] if assigned else "Price unavailable"
        rsi_text = assigned[5] if assigned and len(assigned) > 5 else (legs[0][6] if legs and len(legs[0]) > 6 else "—")
        ma50_text = legs[0][7] if legs and len(legs[0]) > 7 else "—"
        ma200_text = assigned[7] if assigned and len(assigned) > 7 else "—"
        thesis = assigned[11] if assigned and len(assigned) > 11 else ("WATCH" if any((_int_or_none(leg[4]) or 999) <= 21 for leg in legs) else "INTACT")
        thesis_action = assigned[12] if assigned and len(assigned) > 12 else ("Hold" if thesis == "INTACT" else "Review")
        thesis_color = "#f0f7ff" if thesis == "INTACT" else ("#fff6dd" if thesis == "WATCH" else "#fff0f0")
        thesis_text = "INTACT — trend still supportive." if thesis == "INTACT" else ("WATCH — momentum has softened." if thesis == "WATCH" else "BROKEN — thesis needs to be re-underwritten.")

        leg_rows = ""
        for leg in legs:
            dte = _int_or_none(leg[4]) or 0
            action = str(leg[10]) if len(leg) > 10 else "Monitor"
            if dte <= 21 or "roll" in action.lower():
                action_label = "ROLL NOW"
                action_color = "#cc2200"
            elif "profit" in action.lower() or "close" in action.lower():
                action_label = "TAKE PROFIT"
                action_color = "#1a7a1a"
            else:
                action_label = "HOLD"
                action_color = "#b87800"
            leg_rows += f"""
      <tr>
        <td style="padding:8px;border-bottom:1px solid #eee;">{leg[1]}</td>
        <td style="padding:8px;border-bottom:1px solid #eee;">${leg[2]}</td>
        <td style="padding:8px;border-bottom:1px solid #eee;">{_date_label(leg[3])}</td>
        <td style="padding:8px;border-bottom:1px solid #eee;color:{'#cc2200' if dte <= 21 else '#444'};font-weight:{'bold' if dte <= 21 else 'normal'};">{leg[4]}</td>
        <td style="padding:8px;border-bottom:1px solid #eee;">{leg[5]} OTM/ITM</td>
        <td style="padding:8px;border-bottom:1px solid #eee;color:{action_color};font-weight:bold;">{action_label}</td>
      </tr>"""
        if not leg_rows:
            leg_rows = '<tr><td colspan="6" style="padding:8px;color:#666;">No open option legs.</td></tr>'

        subtitle = ' · '.join(subtitle_bits) if subtitle_bits else 'US options position'
        symbol_cards += f"""
<div style="background:white;border:1px solid #eee;border-radius:8px;padding:16px;margin:0 0 12px 0;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
    <div>
      <div style="font-size:18px;font-weight:bold;">{symbol}</div>
      <div style="font-size:12px;color:#666;margin-top:4px;">{subtitle}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:18px;font-weight:bold;">{price_text}</div>
      <div style="font-size:12px;color:#666;">RSI {rsi_text} · 50d: {ma50_text} · 200d: {ma200_text}</div>
    </div>
  </div>
  <div style="background:{thesis_color};padding:8px 12px;border-radius:4px;font-size:12px;margin-bottom:10px;">📋 <b>Thesis:</b> {thesis_text} <b>{thesis_action}</b></div>
  <table style="width:100%;font-size:12px;border-collapse:collapse;">
    <tr style="background:#f5f5f5;">
      <th style="padding:8px;text-align:left;">Type</th><th style="padding:8px;text-align:left;">Strike</th><th style="padding:8px;text-align:left;">Expiry</th><th style="padding:8px;text-align:left;">DTE</th><th style="padding:8px;text-align:left;">Status</th><th style="padding:8px;text-align:left;">Action</th>
    </tr>
    {leg_rows}
  </table>
</div>"""

    if not symbol_cards:
        symbol_cards = '<div style="background:white;border:1px solid #eee;border-radius:8px;padding:16px;color:#666;">No US option positions available.</div>'

    exit_cards = ''.join(
        f"<div style='border-left:4px solid #b87800;background:#fffaf0;padding:10px 12px;margin-bottom:8px;border-radius:0 6px 6px 0;'><b>{item.get('symbol', '?')}</b> — {item.get('status', 'Monitor')}<br><span style='font-size:12px;color:#666;'>{item.get('progress', '')}</span></div>"
        for item in data.get("permanent_exits", [])
    ) or '<div style="font-size:13px;color:#666;">No permanent exit notes.</div>'

    india_equities = _table(["Symbol", "Shares", "Avg Cost", "CMP", "P&L", "RSI", "% off 52W high", "P/E", "Thesis", "Action"], data.get("india_equities", []))
    india_fno = _table(["Symbol", "Type", "Strike", "Expiry", "DTE", "Delta", "Premium", "P&L", "Action"], data.get("india_fno", []))
    sectors = _table(["Sector", "Outlook", "Note"], data.get("india_sector_scorecard", []))

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;max-width:680px;margin:0 auto;background:#f5f5f5;color:#222;padding:0;">
  <div style="background:linear-gradient(135deg,#102542,#1b4965);color:white;padding:24px;border-radius:8px 8px 0 0;">
    <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9fd3ff;margin-bottom:4px;">THETA-LAB TECHNICAL REVIEW</div>
    <div style="font-size:20px;font-weight:bold;">{report_date}</div>
    <div style="font-size:12px;color:#d7e6f2;margin-top:6px;">Grouped by symbol so each name has one clear read.</div>
  </div>
  {warning}
  <div style="background:white;padding:20px 24px;margin-top:8px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">🔎 US Positions — By Symbol</div>
    {symbol_cards}
  </div>
  <div style="background:white;padding:20px 24px;margin-top:8px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">🚪 Permanent Exit Names</div>
    {exit_cards}
  </div>
  <div style="background:white;padding:20px 24px;margin-top:8px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">🇮🇳 India Equity Check</div>
    {india_equities}
  </div>
  <div style="background:white;padding:20px 24px;margin-top:8px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">🇮🇳 India F&O Positions</div>
    {india_fno}
  </div>
  <div style="background:white;padding:20px 24px;margin-top:8px;">
    <div style="font-size:15px;font-weight:bold;margin-bottom:12px;">🏭 India Sector Scorecard</div>
    {sectors}
  </div>
</body>
</html>"""


def build_monthly_objectives_html(data: dict, report_date: str = None) -> str:
    """Build a readable monthly objectives report email."""
    if not report_date:
        report_date = datetime.now().strftime("%B %d, %Y")

    def _number(raw: str) -> float:
        try:
            return float(str(raw).replace('$', '').replace('₹', '').replace(',', '').replace('%', '').strip())
        except Exception:
            return 0.0

    def _metric_value(rows: list[list[str]], label: str, index: int = 2) -> str:
        for row in rows:
            if row and label.lower() in str(row[0]).lower():
                return str(row[index])
        return '—'

    warning = _warning_banner(data["warning"]) if data.get("warning") else ""
    header = data.get("header", {})
    income_rows = data.get("income_rows", [])
    kpi_rows = data.get("kpi_rows", [])
    assigned = data.get("assigned_book", {})
    ytd = data.get("ytd", {})
    # Extract ytd_income early — used in both ytd_section and gap_closure_section
    ytd_income = float(ytd.get("income", 0) or 0)
    months_elapsed = float(ytd.get("months_elapsed", 1) or 1)
    combined_row = income_rows[0] if income_rows else ["Combined monthly income", "$100,000", "$0", "$0", "$0", "BEHIND"]
    combined_target = max(1.0, _number(combined_row[1]))
    last_month_combined = _number(combined_row[2])
    current_pace = _number(combined_row[3])
    last_pct = int(round((last_month_combined / combined_target) * 100)) if combined_target else 0
    last_color = "#1a7a1a" if last_pct >= 100 else ("#b87800" if last_pct >= 70 else "#cc2200")
    capture_val = _number(_metric_value(kpi_rows, 'capture'))
    pf_val = _number(_metric_value(kpi_rows, 'profit factor'))
    capture_color = "#1a7a1a" if capture_val >= 65 else ("#b87800" if capture_val >= 55 else "#cc2200")
    pf_color = "#1a7a1a" if pf_val >= 2.0 else ("#b87800" if pf_val >= 1.5 else "#cc2200")
    idle_positions = assigned.get("idle_positions", [])
    assigned_value = float(assigned.get("value", 0) or 0)
    assigned_cap = float(assigned.get("cap", 375000) or 375000)
    assigned_gap = assigned_value - assigned_cap

    traffic_lines = [
        f"{'✅' if current_pace >= combined_target else '⚠️'} Monthly income pace: <b>{combined_row[3]}</b> — {'on pace for the $100K goal' if current_pace >= combined_target else f'behind pace by ${combined_target - current_pace:,.0f}'}",
        f"{'✅' if capture_val >= 65 else '⚠️'} Premium capture: <b>{capture_val:.1f}%</b> — {'inside the 65-70% band' if capture_val >= 65 else f'{65 - capture_val:.1f} points below target'}",
        f"{'✅' if pf_val >= 2.0 else '⚠️'} Profit factor: <b>{pf_val:.1f}</b> — {'above 2.0 target' if pf_val >= 2.0 else 'needs stronger win/loss efficiency'}",
        f"{'🔴' if assigned_gap > 0 else '✅'} Assigned book: <b>${assigned_value:,.0f}</b> — {'$' + format(assigned_gap, ',.0f') + ' over cap' if assigned_gap > 0 else 'inside the bear cap'}",
        f"{'🔴' if idle_positions else '✅'} Idle capital: <b>{', '.join(idle_positions) if idle_positions else 'None'}</b> — {'write covered calls this month' if idle_positions else 'all tracked names are producing income'}",
    ]

    action_cards = ""
    for idx, action in enumerate(data.get("gap_actions", [])[:3], 1):
        color = "#cc2200" if action.get("priority") == "URGENT" else "#b87800"
        bg = "#fff8f7" if action.get("priority") == "URGENT" else "#fffaf0"
        action_cards += f"""
<div style="border-left:4px solid {color};padding:12px 16px;margin:8px 0;background:{bg};border-radius:0 6px 6px 0;">
  <b>{idx}. {action.get('action', 'Review this month')}</b><br>
  <span style="font-size:13px;color:#555;">{action.get('reason', '')} {action.get('details', '')}</span>
</div>"""
    if not action_cards:
        action_cards = '<div style="font-size:13px;color:#666;">No major gaps flagged this month.</div>'

    account_rows = [row for row in income_rows[1:] if row and 'India' not in str(row[0])]
    account_breakdown = _table(["Income Line", "Target", "Last Month", "This Month Pace", "Gap", "Status"], account_rows) if account_rows else '<div style="font-size:13px;color:#666;">No account breakdown available.</div>'

    india = data.get("india_objectives", {})
    india_section = _progress_bar(float(india.get("pace", 0) or 0), float(india.get("target", 1) or 1), "India F&O pace")
    india_section += _table(["Symbol", "Premium", "Current P&L", "Alignment"], india.get("rows", []))

    us_screener_section = _build_screener_section(data.get("us_screener", []), "🔍 New Entry Opportunities — US")
    india_screener_section = _build_screener_section(data.get("india_screener", []), "🔍 New Entry Opportunities — India NSE")

    bev_table = _table(["Symbol", "Shares", "Remaining Loss", "CC / Month", "Months to Breakeven"], data.get("breakeven_rows", []))

    # --- Gap Closure Section ---
    gc = data.get("gap_closure", {})
    req_monthly = float(gc.get("required_monthly", 0) or 0)
    months_rem = float(gc.get("months_remaining", 8) or 8)
    remaining = float(gc.get("remaining_to_target", 0) or 0)
    idle_opps = gc.get("idle_cc_opportunities", [])
    total_idle = float(gc.get("total_idle_cc_potential", 0) or 0)
    eff_gain = float(gc.get("efficiency_monthly_gain", 0) or 0)
    capital_needed = float(gc.get("capital_needed", 0) or 0)
    aum = float(gc.get("active_aum", 700000) or 700000)
    yield_pct = float(gc.get("monthly_yield_pct", 0) or 0)
    gc_scenarios = gc.get("scenarios", [])

    # Idle CC table
    idle_rows_html = ""
    for opp in idle_opps:
        idle_rows_html += f"""
<tr>
  <td style="padding:7px 10px;border-bottom:1px solid #eee;font-weight:bold;">{opp['symbol']}</td>
  <td style="padding:7px 10px;border-bottom:1px solid #eee;">{opp['shares']} sh @ ${opp['price']:,.0f}</td>
  <td style="padding:7px 10px;border-bottom:1px solid #eee;color:#1a7a1a;font-weight:bold;">+${opp['potential']:,.0f}/mo</td>
  <td style="padding:7px 10px;border-bottom:1px solid #eee;font-size:12px;color:#666;">{opp['note']}</td>
</tr>"""
    if idle_rows_html:
        idle_table = f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:10px;">
  <thead><tr style="background:#333;color:white;">
    <th style="padding:7px 10px;text-align:left;">Symbol</th>
    <th style="padding:7px 10px;text-align:left;">Position</th>
    <th style="padding:7px 10px;text-align:left;">Potential</th>
    <th style="padding:7px 10px;text-align:left;">Action</th>
  </tr></thead>
  <tbody>{idle_rows_html}</tbody>
  <tfoot><tr style="background:#f0faf0;">
    <td colspan="2" style="padding:7px 10px;font-weight:bold;">Total idle CC potential</td>
    <td style="padding:7px 10px;color:#1a7a1a;font-weight:bold;">+${total_idle:,.0f}/mo</td>
    <td style="padding:7px 10px;font-size:12px;color:#666;">= +${total_idle*12:,.0f}/year</td>
  </tr></tfoot>
</table>"""
    else:
        idle_table = '<div style="font-size:13px;color:#666;">All positions have active CC coverage.</div>'

    # Scenario bars
    scenario_html = ""
    for s in gc_scenarios:
        s_pct = min(100, int(s.get("pct_of_target", 0) or 0))
        s_color = s.get("color", "#888")
        yr_end = float(s.get("projected_year_end", 0) or 0)
        gap = float(s.get("gap_to_target", 0) or 0)
        gap_str = (f'<span style="color:#1a7a1a;">beat by ${abs(gap):,.0f}</span>' if gap <= 0
                   else f'<span style="color:#cc2200;">${gap:,.0f} short</span>')
        scenario_html += f"""
<div style="margin:10px 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
    <span style="font-size:13px;font-weight:bold;">{s.get('name','')}</span>
    <span style="font-size:13px;font-weight:bold;color:{s_color};">${yr_end:,.0f} ({s_pct}%) — {gap_str}</span>
  </div>
  <div style="background:#e8e8e8;height:12px;border-radius:6px;">
    <div style="background:{s_color};width:{s_pct}%;height:12px;border-radius:6px;"></div>
  </div>
  <div style="font-size:11px;color:#888;margin-top:2px;">{s.get('note','')}</div>
</div>"""

    # Capital lever
    monthly_gap_to_close = max(0, req_monthly - (round(ytd_income / max(months_elapsed, 1)) + total_idle + eff_gain))
    if capital_needed > 0:
        capital_html = f"""
<div style="background:#fff8f7;border:1px solid #fde0de;border-radius:6px;padding:14px 16px;margin-top:14px;">
  <div style="font-size:14px;font-weight:bold;color:#cc2200;margin-bottom:6px;">💰 Capital Alternative</div>
  <div style="font-size:13px;color:#444;line-height:1.8;">
    If you max out idle CCs and efficiency gains but still face a gap:<br>
    <b>Additional capital needed: ${capital_needed:,.0f}</b> at your current {yield_pct:.1f}%/month yield on ${aum:,.0f} AUM.<br>
    Deploying this into new strangle/CSP positions would generate the remaining ${monthly_gap_to_close:,.0f}/month needed.
  </div>
</div>"""
    else:
        capital_html = '<div style="font-size:13px;color:#1a7a1a;padding:10px 0;">✅ Gap can be closed through operational improvements — no additional capital required.</div>'

    gap_closure_section = f"""
<div style="background:white;margin-top:8px;padding:20px 24px;">
  <div style="font-size:18px;font-weight:bold;margin-bottom:4px;">🎯 Gap Closure Plan — How to Hit $1.2M</div>
  <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:12px 16px;margin:12px 0;font-size:13px;line-height:1.8;">
    <b>The math:</b> You need <b>${remaining:,.0f}</b> more over <b>{months_rem:.0f} months</b> = <b>${req_monthly:,.0f}/month</b> required.<br>
    Current average: <b>${round(ytd_income/max(months_elapsed,1)):,.0f}/month</b> &nbsp;·&nbsp;
    Monthly gap to close: <b>${max(0, req_monthly - round(ytd_income/max(months_elapsed,1))):,.0f}</b>
  </div>

  <div style="font-size:15px;font-weight:bold;margin:16px 0 8px;">Lever 1 — Activate Idle CC Positions</div>
  <div style="font-size:13px;color:#444;margin-bottom:6px;">
    {len(idle_opps)} assigned positions have <b>$0 covered call income</b> this month. Writing monthly calls generates:
  </div>
  {idle_table}

  <div style="font-size:15px;font-weight:bold;margin:16px 0 8px;">Lever 2 — Tighten Capture Rate (58% → 65%)</div>
  <div style="background:#f9f9f9;border-radius:6px;padding:12px 14px;font-size:13px;color:#444;line-height:1.8;">
    Closing positions at 50-60% of premium received (bear target) instead of letting them run or expire:<br>
    Estimated additional income: <b>+${eff_gain:,.0f}/month</b> from recycling capital faster.
  </div>

  <div style="font-size:15px;font-weight:bold;margin:16px 0 8px;">Scenario Projections — Year-End Outcomes</div>
  {scenario_html}

  {capital_html}
</div>"""

    # --- YTD Section ---
    ytd_annual_target = float(ytd.get("annual_target", 1_200_000) or 1_200_000)
    ytd_expected = float(ytd.get("ytd_expected", 0) or 0)
    ytd_gap = float(ytd.get("gap", 0) or 0)
    ytd_months = months_elapsed  # already extracted above
    ytd_run_rate = float(ytd.get("run_rate_annual", 0) or 0)
    ytd_pct = min(100, int(ytd_income / ytd_annual_target * 100)) if ytd_annual_target else 0
    ytd_bar_color = "#1a7a1a" if ytd_gap >= 0 else ("#b87800" if ytd_gap >= -50000 else "#cc2200")
    ytd_gap_str = (f"<b style='color:#1a7a1a;'>+${ytd_gap:,.0f} ahead</b>" if ytd_gap >= 0
                   else f"<b style='color:#cc2200;'>${abs(ytd_gap):,.0f} behind</b>")
    # Monthly mini-bars
    breakdown = ytd.get("monthly_breakdown", [])
    month_bars = ""
    for m in breakdown:
        m_inc = float(m.get("income", 0) or 0)
        m_tgt = float(m.get("target", 100000) or 100000)
        bar_h = max(4, min(60, int(m_inc / m_tgt * 60)))
        bar_c = "#1a7a1a" if m_inc >= m_tgt else ("#b87800" if m_inc >= m_tgt * 0.7 else "#cc2200")
        month_bars += f"""
<div style="display:inline-block;text-align:center;margin:0 4px;vertical-align:bottom;width:44px;">
  <div style="font-size:10px;color:#555;margin-bottom:2px;">${m_inc/1000:.0f}K</div>
  <div style="background:{bar_c};height:{bar_h}px;border-radius:3px 3px 0 0;"></div>
  <div style="font-size:10px;color:#888;margin-top:2px;">{m.get('label','')}</div>
</div>"""
    ytd_section = f"""
<div style="background:white;margin-top:8px;padding:20px 24px;">
  <div style="font-size:18px;font-weight:bold;margin-bottom:4px;">📈 Year-to-Date Progress</div>
  <div style="font-size:12px;color:#888;margin-bottom:16px;">{ytd_months:.0f} months elapsed · annual goal: $1.2M</div>
  <div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;">
    <div style="font-size:32px;font-weight:bold;color:{ytd_bar_color};">${ytd_income:,.0f}</div>
    <div style="font-size:14px;color:#666;">collected so far this year</div>
  </div>
  <div style="background:#e8e8e8;height:10px;border-radius:5px;margin:10px 0 6px;">
    <div style="background:{ytd_bar_color};width:{ytd_pct}%;height:10px;border-radius:5px;"></div>
  </div>
  <div style="font-size:12px;color:#888;display:flex;justify-content:space-between;margin-bottom:14px;">
    <span>$0</span>
    <span>{ytd_pct}% of $1.2M annual target</span>
    <span>$1.2M</span>
  </div>
  <div style="background:#f9f9f9;border-radius:6px;padding:10px 14px;font-size:13px;color:#444;line-height:1.9;margin-bottom:16px;">
    📌 Expected at this point: <b>${ytd_expected:,.0f}</b> &nbsp;·&nbsp; Actual: <b>${ytd_income:,.0f}</b> &nbsp;·&nbsp; {ytd_gap_str}<br>
    🏃 Annual run rate: <b>${ytd_run_rate:,.0f}/year</b> ({'on track for $1.2M' if ytd_run_rate >= 1_200_000 else f'${1_200_000 - ytd_run_rate:,.0f} short of $1.2M annual pace'})
  </div>
  <div style="font-size:12px;color:#999;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;">Monthly breakdown</div>
  <div style="line-height:1;white-space:nowrap;overflow-x:auto;">{month_bars}</div>
  <div style="font-size:11px;color:#bbb;margin-top:6px;">Bar height = % of $100K monthly target</div>
</div>"""

    generated = datetime.now().strftime('%Y-%m-%d %H:%M')

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;max-width:680px;margin:0 auto;background:#f5f5f5;color:#222;padding:0;">
  <div style="background:linear-gradient(135deg,#1a2744,#0d1b40);color:white;padding:24px;border-radius:8px 8px 0 0;">
    <div style="font-size:22px;font-weight:bold;">Monthly Objectives</div>
    <div style="font-size:13px;color:#d7e6f2;margin-top:6px;">{header.get('previous_month', 'Last Month')} review + {header.get('current_month', 'This Month')} outlook</div>
  </div>
  {warning}
  <div style="display:flex;gap:12px;flex-wrap:wrap;padding:20px 24px;background:white;margin-top:8px;">
    <div style="flex:1;min-width:130px;border:1px solid #eee;border-radius:8px;padding:16px;text-align:center;">
      <div style="font-size:11px;color:#999;text-transform:uppercase;">{header.get('previous_month', 'Last Month')} Income</div>
      <div style="font-size:28px;font-weight:bold;color:{last_color};">${last_month_combined:,.0f}</div>
      <div style="font-size:12px;color:#666;">of ${combined_target:,.0f} target</div>
      <div style="font-size:12px;font-weight:bold;color:{last_color};">{last_pct}% {'✓' if last_pct >= 100 else ''}</div>
    </div>
    <div style="flex:1;min-width:130px;border:1px solid #eee;border-radius:8px;padding:16px;text-align:center;">
      <div style="font-size:11px;color:#999;text-transform:uppercase;">{header.get('current_month', 'This Month')} Pace</div>
      <div style="font-size:28px;font-weight:bold;color:{'#1a7a1a' if current_pace >= combined_target else '#b87800'};">${current_pace:,.0f}</div>
      <div style="font-size:12px;color:#666;">projected this month</div>
    </div>
    <div style="flex:1;min-width:130px;border:1px solid #eee;border-radius:8px;padding:16px;text-align:center;">
      <div style="font-size:11px;color:#999;text-transform:uppercase;">Capture Rate</div>
      <div style="font-size:28px;font-weight:bold;color:{capture_color};">{capture_val:.1f}%</div>
      <div style="font-size:12px;color:#666;">target: 65-70%</div>
    </div>
    <div style="flex:1;min-width:130px;border:1px solid #eee;border-radius:8px;padding:16px;text-align:center;">
      <div style="font-size:11px;color:#999;text-transform:uppercase;">Profit Factor</div>
      <div style="font-size:28px;font-weight:bold;color:{pf_color};">{pf_val:.1f}</div>
      <div style="font-size:12px;color:#666;">target: &gt;2.0</div>
    </div>
    <div style="flex:1;min-width:130px;border:2px solid {ytd_bar_color};border-radius:8px;padding:16px;text-align:center;">
      <div style="font-size:11px;color:#999;text-transform:uppercase;">YTD vs $1.2M</div>
      <div style="font-size:28px;font-weight:bold;color:{ytd_bar_color};">{ytd_pct}%</div>
      <div style="font-size:12px;color:#666;">${ytd_income:,.0f} collected</div>
      <div style="font-size:11px;color:{ytd_bar_color};font-weight:bold;">{'ahead ✓' if ytd_gap >= 0 else f'${abs(ytd_gap):,.0f} behind'}</div>
    </div>
  </div>
  {ytd_section}
  {gap_closure_section}
  {us_screener_section}
  {india_screener_section}
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:18px;font-weight:bold;margin-bottom:12px;">🌡️ Position Heat — Active Leg Management</div>
    {data.get('portfolio_heat_html', '<p style="font-size:13px;color:#999">Heat data unavailable — Schwab live positions required.</p>')}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:18px;font-weight:bold;margin-bottom:12px;">How did {header.get('previous_month', 'last month')} go?</div>
    <div style="font-size:13px;line-height:1.9;color:#444;">{'<br>'.join(traffic_lines)}</div>
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:18px;font-weight:bold;margin-bottom:12px;">🎯 3 Actions to Improve This Month</div>
    {action_cards}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:18px;font-weight:bold;margin-bottom:12px;">👥 Account by Account Breakdown</div>
    {account_breakdown}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:18px;font-weight:bold;margin-bottom:12px;">🇮🇳 India Objectives</div>
    {india_section}
  </div>
  <div style="background:white;margin-top:8px;padding:20px 24px;">
    <div style="font-size:18px;font-weight:bold;margin-bottom:12px;">📊 Assigned Book — Breakeven Progress</div>
    {bev_table}
  </div>
  <div style="padding:16px 24px;font-size:11px;color:#999;text-align:center;margin-top:8px;">Generated by Theta-Lab · {generated} · Verify before trading</div>
</body>
</html>"""
