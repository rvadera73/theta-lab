"""
India + US Evening Trading Report — runs Sun-Thu at 8 PM IST via GitHub Actions.
Fetches live data from yfinance, estimates India F&O LTPs via Black-Scholes,
checks equity exit triggers, sends HTML email via Resend.

Run locally: RESEND_API_KEY=xxx python3 mcp/routines/india_us_evening_report.py
"""

import os
import math
from datetime import datetime, date

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
except ImportError:
    pass

try:
    import yfinance as yf
    _YF = True
except ImportError:
    _YF = False

try:
    from scipy.stats import norm as _norm
    _SCIPY = True
except ImportError:
    _SCIPY = False

try:
    import resend as resend_client
    _RESEND = True
except ImportError:
    _RESEND = False

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TO_EMAIL   = "ravjdpr@gmail.com"
FROM_EMAIL = "onboarding@resend.dev"
RESEND_KEY = os.getenv("RESEND_API_KEY", "")
INDIA_RF   = 0.065   # India 10-year government bond ~6.5%

# ---------------------------------------------------------------------------
# India F&O Positions
# Update when trades change in ICICI Direct FNO account (7510078170).
# All short puts, European cash-settled — no assignment ever.
# ---------------------------------------------------------------------------

INDIA_FNO = [
    # idx | expiry | strike | avg premium received | lot size
    {"idx": "NIFTY",     "expiry": "2026-05-05", "strike": 23450, "avg": 160.85, "lot": 65},
    {"idx": "NIFTY",     "expiry": "2026-05-12", "strike": 23300, "avg": 104.65, "lot": 65},
    {"idx": "NIFTY",     "expiry": "2026-05-12", "strike": 22950, "avg": 102.20, "lot": 65},
    {"idx": "NIFTY",     "expiry": "2026-05-19", "strike": 23000, "avg":  96.00, "lot": 65},
    {"idx": "NIFTY",     "expiry": "2026-05-26", "strike": 22550, "avg": 118.65, "lot": 65},
    {"idx": "BANKNIFTY", "expiry": "2026-05-26", "strike": 53500, "avg": 561.80, "lot": 30},
    {"idx": "BANKNIFTY", "expiry": "2026-05-26", "strike": 52500, "avg": 327.00, "lot": 30},
    {"idx": "BANKNIFTY", "expiry": "2026-06-30", "strike": 54500, "avg": 791.50, "lot": 30},
]

# ---------------------------------------------------------------------------
# India Equity — all current holdings
# ICICI Direct PIS delivery account (7500069840). NRI: no covered calls.
# keep=True → target portfolio  |  keep=None → monitoring/thesis check
# ---------------------------------------------------------------------------

INDIA_EQUITY = [
    {"name": "Reliance",       "ticker": "RELIANCE.NS",   "shares": 225, "avg": 1374, "keep": True},
    {"name": "Adani Ports",    "ticker": "ADANIPORTS.NS", "shares": 175, "avg": 1432, "keep": True},
    {"name": "HDFC Bank",      "ticker": "HDFCBANK.NS",   "shares": 150, "avg":  814, "keep": True},
    {"name": "Bajaj Finance",  "ticker": "BAJFINANCE.NS", "shares": 200, "avg":  947, "keep": True},
    {"name": "HAL",            "ticker": "HAL.NS",        "shares":  20, "avg": 4579, "keep": True},
    {"name": "Apollo Hosp",    "ticker": "APOLLOHOSP.NS", "shares":  15, "avg": 7785, "keep": True},
    {"name": "TCS",            "ticker": "TCS.NS",        "shares":  30, "avg": 3140, "keep": True},
    {"name": "LIC",            "ticker": "LICI.NS",       "shares": 200, "avg":  831, "keep": None},
    {"name": "SBI",            "ticker": "SBIN.NS",       "shares": 125, "avg":  933, "keep": None},
    {"name": "DLF",            "ticker": "DLF.NS",        "shares": 150, "avg":  677, "keep": None},
    {"name": "BEL",            "ticker": "BEL.NS",        "shares": 200, "avg":  400, "keep": None},
    {"name": "Eternal/Zomato", "ticker": "ZOMATO.NS",     "shares": 500, "avg":  254, "keep": None},
    {"name": "Dixon Tech",     "ticker": "DIXON.NS",      "shares":  10, "avg":14640, "keep": None},
    {"name": "Dr Reddy's",     "ticker": "DRREDDY.NS",    "shares":  45, "avg": 1226, "keep": None},
]

# ---------------------------------------------------------------------------
# Overhaul Exit Triggers — 3-month phased plan
# Phase 1 = sell immediately / on first bounce to trigger price
# Phase 2 = sell when price reaches trigger
# trigger=0 means exit at any price (no minimum)
# ---------------------------------------------------------------------------

EXIT_TRIGGERS = [
    {"name": "Genus Power",    "ticker": "GENUSPOWER.NS", "shares":  25, "avg":  358, "phase": 1, "trigger":    0, "action": "Sell all — immediate, any price"},
    {"name": "Suzlon",         "ticker": "SUZLON.NS",     "shares": 200, "avg":   57, "phase": 1, "trigger":    0, "action": "Sell all — immediate, any price"},
    {"name": "HCL Tech",       "ticker": "HCLTECH.NS",    "shares":  10, "avg": 1632, "phase": 1, "trigger": 1265, "action": "Sell on bounce >= 1,265"},
    {"name": "NTPC (partial)", "ticker": "NTPC.NS",       "shares":  75, "avg":  362, "phase": 1, "trigger":  414, "action": "Sell 75 of 150 shares >= 414"},
    {"name": "Mazagon Dock",   "ticker": "MAZDOCK.NS",    "shares":  20, "avg": 2494, "phase": 2, "trigger": 2800, "action": "Exit all >= 2,800"},
    {"name": "Anant Raj",      "ticker": "ANANTRAJ.NS",   "shares": 100, "avg":  585, "phase": 2, "trigger":  520, "action": "Exit all >= 520"},
    {"name": "Yatharth",       "ticker": "YATHARTH.NS",   "shares": 201, "avg":  784, "phase": 2, "trigger":  750, "action": "Exit all >= 750"},
    {"name": "Adani Power",    "ticker": "ADANIPOWER.NS", "shares": 200, "avg":  166, "phase": 2, "trigger":  230, "action": "Exit all >= 230"},
    {"name": "Hero MotoCorp",  "ticker": "HEROMOTOCO.NS", "shares":  25, "avg": 5019, "phase": 2, "trigger": 5500, "action": "Exit all >= 5,500"},
]

# US urgent items — semi-static, update when Schwab positions change
US_URGENT = [
    {"symbol": "PYPL",  "note": "1,300 shares @ ~$82 avg | PERMANENT EXIT — sell CCs immediately if none active"},
    {"symbol": "ADBE",  "note": "300 shares @ ~$495 avg | Sell CCs immediately if none active"},
    {"symbol": "AXON",  "note": "$470P Jun18 — deep ITM | Roll down+out, net credit only — do not close for loss"},
    {"symbol": "NKE",   "note": "$65P Jun18 + 100 shares @ $86 avg | Broken thesis — exit entire NKE name"},
    {"symbol": "MSFT",  "note": "$420P May15 (18 DTE) — close if >= 40% profit captured"},
    {"symbol": "MRNA",  "note": "Natural CC exit in progress — let CCs run to completion, no new puts"},
]

TICKER_MAP = {
    "NIFTY":     "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "INDIAVIX":  "^INDIAVIX",
    "SPX":       "^GSPC",
    "USVIX":     "^VIX",
}

# ---------------------------------------------------------------------------
# Market Data
# ---------------------------------------------------------------------------

def _safe_last(series) -> float | None:
    try:
        v = series.dropna().iloc[-1]
        return float(v)
    except Exception:
        return None


def get_prices(tickers: list[str]) -> dict[str, float | None]:
    """Batch fetch via yfinance. Falls back to individual calls on failure."""
    if not _YF:
        return {t: None for t in tickers}
    result: dict[str, float | None] = {}
    try:
        data = yf.download(tickers, period="3d", progress=False, auto_adjust=True)
        close = data["Close"] if "Close" in data else data
        for t in tickers:
            try:
                col = close if len(tickers) == 1 else close[t]
                result[t] = _safe_last(col)
            except Exception:
                result[t] = None
    except Exception:
        for t in tickers:
            try:
                hist = yf.Ticker(t).history(period="3d")
                result[t] = _safe_last(hist["Close"]) if not hist.empty else None
            except Exception:
                result[t] = None
    return result

# ---------------------------------------------------------------------------
# Black-Scholes Put Pricer
# ---------------------------------------------------------------------------

def bs_put(S: float, K: float, T_days: int, sigma: float, r: float = INDIA_RF) -> float:
    """Put price via Black-Scholes. sigma = annualized IV (decimal). Floor at intrinsic."""
    intrinsic = max(0.0, K - S)
    if T_days <= 0 or not _SCIPY or sigma <= 0 or S <= 0:
        return intrinsic
    T = T_days / 365.0
    try:
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        price = K * math.exp(-r * T) * _norm.cdf(-d2) - S * _norm.cdf(-d1)
        return max(intrinsic, float(price))
    except Exception:
        return intrinsic

# ---------------------------------------------------------------------------
# F&O Analysis
# ---------------------------------------------------------------------------

def analyze_fno(nifty: float | None, banknifty: float | None, india_vix: float | None) -> list[dict]:
    """
    Estimate current LTP and % captured for each short put.
    India VIX is in percentage points (e.g. 14.5 → 14.5% annualized IV for NIFTY).
    BANKNIFTY IV ≈ 1.2× India VIX (typically runs hotter than NIFTY).
    """
    today    = date.today()
    iv_nifty = (india_vix / 100.0) if india_vix else 0.15
    iv_bnf   = iv_nifty * 1.20

    rows = []
    for pos in INDIA_FNO:
        expiry = datetime.strptime(pos["expiry"], "%Y-%m-%d").date()
        dte    = max(0, (expiry - today).days)
        spot   = nifty if pos["idx"] == "NIFTY" else banknifty
        iv     = iv_nifty if pos["idx"] == "NIFTY" else iv_bnf

        ltp_est = bs_put(spot, pos["strike"], dte, iv) if spot else None

        avg = pos["avg"]
        pct_captured = ((avg - ltp_est) / avg * 100) if ltp_est is not None and avg > 0 else None
        net_pl = ((avg - ltp_est) * pos["lot"]) if ltp_est is not None else None

        if ltp_est is None:
            status, sc = "NO DATA", "#888888"
        elif dte == 0:
            status, sc = "EXPIRING", "#e74c3c"
        elif ltp_est > avg * 1.05:
            status, sc = "UNDERWATER", "#e74c3c"
        elif pct_captured is not None and pct_captured >= 85:
            status, sc = "ROLL CANDIDATE", "#e67e22"
        elif pct_captured is not None and pct_captured >= 50:
            status, sc = "ON TRACK", "#27ae60"
        else:
            status, sc = "HOLD", "#2c3e50"

        rows.append({**pos, "dte": dte, "spot": spot, "ltp_est": ltp_est,
                     "pct_captured": pct_captured, "net_pl": net_pl,
                     "status": status, "status_color": sc})
    return rows

# ---------------------------------------------------------------------------
# Equity Analysis
# ---------------------------------------------------------------------------

def analyze_equity(prices: dict) -> tuple[list[dict], list[dict]]:
    """Returns (holdings_with_pl, exit_triggers_with_status)."""
    holdings = []
    for pos in INDIA_EQUITY:
        price = prices.get(pos["ticker"])
        cost  = pos["avg"] * pos["shares"]
        mkt   = price * pos["shares"] if price else None
        pl    = (mkt - cost) if mkt is not None else None
        pl_pct = (pl / cost * 100) if pl is not None and cost > 0 else None
        holdings.append({**pos, "price": price, "cost": cost, "mkt": mkt, "pl": pl, "pl_pct": pl_pct})

    exits = []
    for t in EXIT_TRIGGERS:
        price = prices.get(t["ticker"])
        if t["trigger"] == 0:
            hit = True  # immediate exit regardless of price
        elif price is not None:
            hit = price >= t["trigger"]
        else:
            hit = False
        exits.append({**t, "price": price, "hit": hit})

    return holdings, exits

# ---------------------------------------------------------------------------
# HTML Helpers
# ---------------------------------------------------------------------------

def _inr(v: float | None, dec: int = 0) -> str:
    return f"&#8377;{v:,.{dec}f}" if v is not None else "&#8212;"


def _pct(v: float | None) -> str:
    if v is None:
        return "&#8212;"
    return f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%"


def _pcol(v: float | None) -> str:
    if v is None:
        return "#888"
    return "#27ae60" if v >= 0 else "#e74c3c"


def _section(title: str, content: str) -> str:
    return (
        f'<div style="margin:20px 0;padding:16px;border:1px solid #e0e0e0;border-radius:6px;">'
        f'<h2 style="margin:0 0 12px 0;font-size:16px;color:#1a1a2e;'
        f'border-bottom:2px solid #e94560;padding-bottom:6px;">{title}</h2>'
        f'{content}</div>'
    )


def _th(label: str) -> str:
    return f'<th style="background:#1a1a2e;color:white;padding:8px 12px;text-align:left;">{label}</th>'


def _td(content: str, i: int, extra: str = "") -> str:
    bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
    return f'<td style="padding:7px 12px;{extra}">{content}</td>'

# ---------------------------------------------------------------------------
# HTML Report Builder
# ---------------------------------------------------------------------------

def build_html(
    nifty: float | None, banknifty: float | None,
    india_vix: float | None, spx: float | None, us_vix: float | None,
    fno_rows: list[dict], holdings: list[dict], exits: list[dict],
    report_date: str,
) -> str:

    # ── Market Snapshot ──────────────────────────────────────────────────────
    def vix_status(v, low=14, high=20):
        if v is None: return "&#8212;"
        return "LOW" if v < low else ("ELEVATED" if v > high else "NORMAL")

    mkt_rows = [
        ("NIFTY 50",   _inr(nifty),             "India"),
        ("BANKNIFTY",  _inr(banknifty),          "India"),
        ("India VIX",  f"{india_vix:.2f}" if india_vix else "&#8212;", vix_status(india_vix)),
        ("S&amp;P 500", f"${spx:,.0f}" if spx else "&#8212;", "US"),
        ("CBOE VIX",   f"{us_vix:.2f}" if us_vix else "&#8212;", vix_status(us_vix, 16, 25)),
    ]
    mkt_body = "".join(
        f'<tr style="background:{"#f9f9f9" if i%2==0 else "#fff"}">'
        f'<td style="padding:7px 12px;">{r[0]}</td>'
        f'<td style="padding:7px 12px;text-align:right;"><b>{r[1]}</b></td>'
        f'<td style="padding:7px 12px;text-align:center;">{r[2]}</td></tr>'
        for i, r in enumerate(mkt_rows)
    )
    mkt_html = (
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<thead><tr>{_th("Market")}{_th("Close")}{_th("Status")}</tr></thead>'
        f'<tbody>{mkt_body}</tbody></table>'
        f'<p style="font-size:12px;color:#888;margin:8px 0 0 0;">'
        f'India regime: <b>SIDEWAYS/BEARISH</b> — FII net sellers 18+ months. '
        f'Shift trigger: FII net buyer 10+ consecutive sessions.<br>'
        f'US regime: <b>APPROACHING TRANSITION</b> — VIX compressing from March peak. '
        f'Bull confirmed: VIX &lt; 20 sustained + S&amp;P above 50d &amp; 200d MA.</p>'
    )

    # ── F&O Positions ────────────────────────────────────────────────────────
    total_fno_pl = sum(r["net_pl"] for r in fno_rows if r["net_pl"] is not None)
    fno_body = ""
    for i, r in enumerate(fno_rows):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        ltp_s  = f"&#8377;{r['ltp_est']:.1f}" if r["ltp_est"] is not None else "&#8212;"
        pct_s  = f"{r['pct_captured']:.0f}%" if r["pct_captured"] is not None else "&#8212;"
        pl_s   = f"&#8377;{r['net_pl']:+,.0f}" if r["net_pl"] is not None else "&#8212;"
        pl_col = _pcol(r["net_pl"])
        spot_s = _inr(r["spot"])
        fno_body += (
            f'<tr style="background:{bg}">'
            f'<td style="padding:7px 12px;">{r["idx"]} {r["strike"]}P</td>'
            f'<td style="padding:7px 12px;">{r["expiry"]} ({r["dte"]} DTE)</td>'
            f'<td style="padding:7px 12px;">{spot_s}</td>'
            f'<td style="padding:7px 12px;">&#8377;{r["avg"]:.2f}</td>'
            f'<td style="padding:7px 12px;">{ltp_s}</td>'
            f'<td style="padding:7px 12px;font-weight:bold;">{pct_s}</td>'
            f'<td style="padding:7px 12px;font-weight:bold;color:{pl_col};">{pl_s}</td>'
            f'<td style="padding:7px 12px;font-weight:bold;color:{r["status_color"]};">{r["status"]}</td>'
            f'</tr>'
        )
    pl_col = _pcol(total_fno_pl)
    fno_html = (
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<thead><tr>{_th("Contract")}{_th("Expiry (DTE)")}{_th("Spot")}'
        f'{_th("Avg Recv")}{_th("Est LTP")}{_th("% Captured")}'
        f'{_th("Net P&L (1 lot)")}{_th("Status")}</tr></thead>'
        f'<tbody>{fno_body}</tbody></table>'
        f'<p style="font-size:13px;margin:8px 0 0 0;">'
        f'Total estimated F&amp;O P&amp;L: '
        f'<b style="color:{pl_col};">&#8377;{total_fno_pl:+,.0f}</b>'
        f' &nbsp;|&nbsp; Roll rule: 85-90% captured (India costs too high to roll earlier).'
        f' LTP = Black-Scholes estimate using India VIX.</p>'
    )

    # ── Exit Triggers ────────────────────────────────────────────────────────
    exit_body = ""
    for i, e in enumerate(exits):
        bg  = "#fff3cd" if e["hit"] else ("#f9f9f9" if i % 2 == 0 else "#ffffff")
        trig_s = "IMMEDIATE" if e["trigger"] == 0 else f"&#8377;{e['trigger']:,}"
        price_s = _inr(e.get("price"))
        badge = (
            '<span style="background:#e74c3c;color:white;padding:2px 6px;'
            'border-radius:3px;font-size:11px;font-weight:bold;">ACTION NOW</span>'
            if e["hit"] else ""
        )
        pl_est = None
        if e.get("price") and e["avg"]:
            pl_est = (e["price"] - e["avg"]) * e["shares"]
        pl_s = (
            f'<span style="color:{_pcol(pl_est)};">&#8377;{pl_est:+,.0f}</span>'
            if pl_est is not None else "&#8212;"
        )
        exit_body += (
            f'<tr style="background:{bg}">'
            f'<td style="padding:7px 12px;font-weight:bold;">Ph{e["phase"]}</td>'
            f'<td style="padding:7px 12px;">{e["name"]}</td>'
            f'<td style="padding:7px 12px;">{e["shares"]}</td>'
            f'<td style="padding:7px 12px;">&#8377;{e["avg"]:,}</td>'
            f'<td style="padding:7px 12px;">{price_s}</td>'
            f'<td style="padding:7px 12px;">{pl_s}</td>'
            f'<td style="padding:7px 12px;">{trig_s}</td>'
            f'<td style="padding:7px 12px;">{e["action"]} {badge}</td>'
            f'</tr>'
        )
    exit_html = (
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<thead><tr>{_th("Phase")}{_th("Stock")}{_th("Shares")}'
        f'{_th("Avg Cost")}{_th("Current")}{_th("Unrealized P&L")}'
        f'{_th("Trigger")}{_th("Action")}</tr></thead>'
        f'<tbody>{exit_body}</tbody></table>'
        f'<p style="font-size:12px;color:#888;margin:6px 0 0 0;">'
        f'Regime gate: No new equity buys until FII net buyer 10+ consecutive sessions.</p>'
    )

    # ── Core Equity P&L ──────────────────────────────────────────────────────
    eq_body = ""
    total_cost = total_mkt = 0.0
    for i, h in enumerate(holdings):
        bg   = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        tag  = "KEEP" if h["keep"] is True else "WATCH"
        tcol = "#27ae60" if h["keep"] is True else "#e67e22"
        pl_s = _pct(h["pl_pct"])
        pcol = _pcol(h["pl_pct"])
        if h["cost"]:
            total_cost += h["cost"]
        if h["mkt"]:
            total_mkt += h["mkt"]
        eq_body += (
            f'<tr style="background:{bg}">'
            f'<td style="padding:7px 12px;">{h["name"]}</td>'
            f'<td style="padding:7px 12px;">{h["shares"]}</td>'
            f'<td style="padding:7px 12px;">&#8377;{h["avg"]:,}</td>'
            f'<td style="padding:7px 12px;"><b>{_inr(h.get("price"))}</b></td>'
            f'<td style="padding:7px 12px;font-weight:bold;color:{pcol};">{pl_s}</td>'
            f'<td style="padding:7px 12px;"><span style="color:{tcol};font-weight:bold;font-size:11px;">{tag}</span></td>'
            f'</tr>'
        )
    total_pl     = total_mkt - total_cost if total_mkt and total_cost else None
    total_pl_pct = (total_pl / total_cost * 100) if total_pl and total_cost > 0 else None
    eq_html = (
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<thead><tr>{_th("Name")}{_th("Shares")}{_th("Avg Cost")}'
        f'{_th("Current")}{_th("P&L %")}{_th("Status")}</tr></thead>'
        f'<tbody>{eq_body}</tbody></table>'
        f'<p style="font-size:13px;margin:8px 0 0 0;">'
        f'Portfolio: cost &#8377;{total_cost:,.0f} &rarr; mkt &#8377;{total_mkt:,.0f} '
        f'(<span style="color:{_pcol(total_pl_pct)};font-weight:bold;">{_pct(total_pl_pct)}</span>)'
        f' &nbsp;|&nbsp; Target: 18% CAGR over 3 years. Target 8-10 names.</p>'
    )

    # ── US Urgent Items ──────────────────────────────────────────────────────
    us_body = "".join(
        f'<tr style="background:{"#f9f9f9" if i%2==0 else "#fff"}">'
        f'<td style="padding:7px 12px;font-weight:bold;color:#1a1a2e;">{u["symbol"]}</td>'
        f'<td style="padding:7px 12px;">{u["note"]}</td></tr>'
        for i, u in enumerate(US_URGENT)
    )
    us_html = (
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<thead><tr>{_th("Symbol")}{_th("Urgent Action")}</tr></thead>'
        f'<tbody>{us_body}</tbody></table>'
        f'<p style="font-size:12px;color:#888;margin:6px 0 0 0;">'
        f'Account A: ~$401K assigned (danger zone &gt;$375K) — accelerate CC exits on all assigned names.'
        f' Each week without CCs on PYPL/ADBE = $3-5K foregone recovery income.</p>'
    )

    # ── Alert badges for header ───────────────────────────────────────────────
    alerts = []
    triggered_n = sum(1 for e in exits if e["hit"])
    roll_n      = sum(1 for r in fno_rows if r["status"] == "ROLL CANDIDATE")
    under_n     = sum(1 for r in fno_rows if r["status"] == "UNDERWATER")
    if triggered_n:
        alerts.append(
            f'<span style="background:#e74c3c;color:white;padding:3px 8px;'
            f'border-radius:3px;font-size:12px;margin-right:6px;">'
            f'{triggered_n} EXIT TRIGGER{"S" if triggered_n > 1 else ""}</span>'
        )
    if roll_n:
        alerts.append(
            f'<span style="background:#e67e22;color:white;padding:3px 8px;'
            f'border-radius:3px;font-size:12px;margin-right:6px;">'
            f'{roll_n} ROLL CANDIDATE{"S" if roll_n > 1 else ""}</span>'
        )
    if under_n:
        alerts.append(
            f'<span style="background:#c0392b;color:white;padding:3px 8px;'
            f'border-radius:3px;font-size:12px;margin-right:6px;">'
            f'{under_n} UNDERWATER</span>'
        )
    alert_bar = "".join(alerts) if alerts else (
        '<span style="color:#2ecc71;font-weight:bold;">All positions within normal parameters</span>'
    )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;color:#333;background:#fff;padding:10px;">

<div style="background:#1a1a2e;color:white;padding:20px 24px;border-radius:6px 6px 0 0;">
  <h1 style="margin:0;font-size:22px;">Trading Report &mdash; {report_date}</h1>
  <div style="font-size:13px;color:#aaa;margin-top:4px;">India + US &nbsp;|&nbsp; 8 PM IST &nbsp;|&nbsp; ravjdpr@gmail.com</div>
  <div style="margin-top:10px;">{alert_bar}</div>
</div>

{_section("Market Snapshot", mkt_html)}
{_section("India F&O &mdash; Position Status (All Short Puts, Cash-Settled)", fno_html)}
{_section("India Equity &mdash; Overhaul Exit Triggers", exit_html)}
{_section("India Equity &mdash; Full Portfolio P&amp;L", eq_html)}
{_section("US Accounts &mdash; Urgent Items", us_html)}

<div style="padding:12px 16px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:20px;">
  Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} &nbsp;|&nbsp;
  F&amp;O LTPs = Black-Scholes estimates (India VIX as IV); verify in ICICI Direct before trading. &nbsp;|&nbsp;
  US items are semi-static; check Schwab for latest positions.
</div>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Email Sender
# ---------------------------------------------------------------------------

def send_report(html: str, subject: str) -> bool:
    if not _RESEND:
        print("ERROR: resend package not installed — pip install resend")
        return False
    if not RESEND_KEY:
        print("ERROR: RESEND_API_KEY not set")
        return False
    try:
        resend_client.api_key = RESEND_KEY
        resp = resend_client.Emails.send({
            "from": FROM_EMAIL,
            "to": [TO_EMAIL],
            "subject": subject,
            "html": html,
        })
        if resp.get("id"):
            print(f"  Email sent → {TO_EMAIL} (id: {resp['id']})")
            return True
        print(f"  Email error: {resp}")
        return False
    except Exception as e:
        print(f"  Email exception: {e}")
        return False

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    report_date = datetime.utcnow().strftime("%A, %B %d, %Y")
    print(f"[India+US Evening Report] {report_date} UTC")

    # 1. Collect all tickers
    index_tickers = list(TICKER_MAP.values())
    equity_tickers = [h["ticker"] for h in INDIA_EQUITY]
    exit_tickers   = [e["ticker"] for e in EXIT_TRIGGERS]
    all_tickers = list(dict.fromkeys(index_tickers + equity_tickers + exit_tickers))

    print(f"  Fetching {len(all_tickers)} tickers from yfinance...")
    prices = get_prices(all_tickers)

    nifty     = prices.get("^NSEI")
    banknifty = prices.get("^NSEBANK")
    india_vix = prices.get("^INDIAVIX")
    spx       = prices.get("^GSPC")
    us_vix    = prices.get("^VIX")

    print(f"  NIFTY={nifty} | BANKNIFTY={banknifty} | IndiaVIX={india_vix} | SPX={spx} | VIX={us_vix}")

    # 2. F&O analysis
    fno_rows = analyze_fno(nifty, banknifty, india_vix)
    roll_n   = sum(1 for r in fno_rows if r["status"] == "ROLL CANDIDATE")
    under_n  = sum(1 for r in fno_rows if r["status"] == "UNDERWATER")
    print(f"  F&O: {len(fno_rows)} positions | {roll_n} roll candidates | {under_n} underwater")

    # 3. Equity analysis
    holdings, exits = analyze_equity(prices)
    hit_n = sum(1 for e in exits if e["hit"])
    print(f"  Equity: {len(holdings)} holdings | {hit_n} exit triggers HIT")

    # 4. Build HTML
    html = build_html(nifty, banknifty, india_vix, spx, us_vix,
                      fno_rows, holdings, exits, report_date)

    # 5. Subject line (include alerts)
    parts = []
    if hit_n:
        parts.append(f"{hit_n} EXIT")
    if roll_n:
        parts.append(f"{roll_n} ROLL")
    if under_n:
        parts.append(f"{under_n} UW")
    alert_tag = f" [{', '.join(parts)}]" if parts else ""
    nifty_str = f"NIFTY {nifty:,.0f}" if nifty else "NIFTY —"
    subject = (
        f"Trading Report {datetime.utcnow().strftime('%a %b %d')}"
        f"{alert_tag} | {nifty_str} | India+US"
    )

    send_report(html, subject)
    print("  Done.")


if __name__ == "__main__":
    main()
