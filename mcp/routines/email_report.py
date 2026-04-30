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
