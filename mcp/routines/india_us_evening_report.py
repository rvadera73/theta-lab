"""
India + US Evening Trading Report — runs Sun-Thu at 8 PM IST via GitHub Actions.

Data sources (drop in data/statements/ and commit):
  7510078170_*.csv    — ICICI Direct F&O Portfolio Details export
  7500069840_*.csv    — ICICI Direct Equity transaction history export
  empower-holding*.xlsx — Empower unified holdings export (all US accounts)

Config (edit and commit — no Python changes needed):
  data/india_config.yaml  — core portfolio list + exit triggers

Run locally: RESEND_API_KEY=xxx python3 mcp/routines/india_us_evening_report.py
"""

import csv
import glob
import math
import os
import re
from datetime import datetime, date

try:
    import openpyxl
    _OPENPYXL = True
except ImportError:
    _OPENPYXL = False

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
except ImportError:
    pass

try:
    import yaml
    _YAML = True
except ImportError:
    _YAML = False

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
INDIA_RF   = 0.065  # India 10-year government bond ~6.5%

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

# ---------------------------------------------------------------------------
# ICICI Direct symbol → (display name, yfinance ticker)
# Add new symbols here when you buy a new stock.
# ---------------------------------------------------------------------------

SYMBOL_MAP: dict[str, tuple[str, str]] = {
    "ADAPOR": ("Adani Ports",    "ADANIPORTS.NS"),
    "ADAPOW": ("Adani Power",    "ADANIPOWER.NS"),
    "ANARAJ": ("Anant Raj",      "ANANTRAJ.NS"),
    "APOHOS": ("Apollo Hosp",    "APOLLOHOSP.NS"),
    "BAJFI":  ("Bajaj Finance",  "BAJFINANCE.NS"),
    "BHAELE": ("BEL",            "BEL.NS"),
    "DIXTEC": ("Dixon Tech",     "DIXON.NS"),
    "DLFLIM": ("DLF",            "DLF.NS"),
    "DRREDD": ("Dr Reddy's",     "DRREDDY.NS"),
    "GENOVE": ("Genus Power",    "GENUSPOWER.NS"),
    "HCLTEC": ("HCL Tech",       "HCLTECH.NS"),
    "HDFBAN": ("HDFC Bank",      "HDFCBANK.NS"),
    "HERHON": ("Hero MotoCorp",  "HEROMOTOCO.NS"),
    "HINAER": ("HAL",            "HAL.NS"),
    "LIC":    ("LIC",            "LICI.NS"),
    "MAZDOC": ("Mazagon Dock",   "MAZDOCK.NS"),
    "NTPC":   ("NTPC",           "NTPC.NS"),
    "RELIND": ("Reliance",       "RELIANCE.NS"),
    "STABAN": ("SBI",            "SBIN.NS"),
    "SUZENE": ("Suzlon",         "SUZLON.NS"),
    "TCS":    ("TCS",            "TCS.NS"),
    "YATHOS": ("Yatharth",       "YATHARTH.NS"),
    "ZOMLIM": ("Eternal/Zomato", "ETERNAL.NS"),
}

# F&O index codes as they appear in ICICI Direct contract names
LOT_SIZES: dict[str, int] = {
    "NIFTY":     65,
    "CNXBAN":    30,   # BANKNIFTY
    "NIFMID150": 120,  # MIDCAPNIFTY
}

INDEX_DISPLAY: dict[str, str] = {
    "NIFTY":     "NIFTY",
    "CNXBAN":    "BANKNIFTY",
    "NIFMID150": "MIDCAPNIFTY",
}

INDEX_YF: dict[str, str] = {
    "NIFTY":  "^NSEI",
    "CNXBAN": "^NSEBANK",
}

# US urgent items — update when Schwab positions change
US_URGENT = [
    {"symbol": "PYPL",  "note": "1,300 shares @ ~$82 avg | PERMANENT EXIT — sell CCs immediately if none active"},
    {"symbol": "ADBE",  "note": "300 shares @ ~$495 avg | Sell CCs immediately if none active"},
    {"symbol": "AXON",  "note": "$470P Jun18 — deep ITM | Roll down+out, net credit only"},
    {"symbol": "NKE",   "note": "$65P Jun18 + 100 shares @ $86 | Broken thesis — exit entire NKE name"},
    {"symbol": "MSFT",  "note": "$420P May15 (18 DTE) — close if >= 40% profit captured"},
    {"symbol": "MRNA",  "note": "Natural CC exit in progress — no new puts"},
]

# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_india_config() -> tuple[list[str], list[dict]]:
    """
    Returns (core_portfolio_symbols, exit_triggers).
    Falls back to hardcoded defaults if YAML not available.
    """
    cfg_path = os.path.join(DATA_DIR, "india_config.yaml")
    if _YAML and os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        core = cfg.get("core_portfolio", [])
        triggers = cfg.get("exit_triggers", [])
        print(f"  Config: {len(core)} core symbols, {len(triggers)} exit triggers")
        return core, triggers

    # Fallback defaults
    print("  Warning: data/india_config.yaml not found — using hardcoded defaults")
    core = ["RELIND", "ADAPOR", "HDFBAN", "BAJFI", "HINAER", "APOHOS", "TCS"]
    triggers = [
        {"icici_symbol": "GENOVE", "trigger": 0,    "shares": "all", "phase": 1, "action": "Sell all — immediate"},
        {"icici_symbol": "SUZENE", "trigger": 0,    "shares": "all", "phase": 1, "action": "Sell all — immediate"},
        {"icici_symbol": "HCLTEC", "trigger": 1265, "shares": "all", "phase": 1, "action": "Sell >= 1,265"},
        {"icici_symbol": "NTPC",   "trigger": 414,  "shares": 75,    "phase": 1, "action": "Sell 75 of 150 >= 414"},
        {"icici_symbol": "MAZDOC", "trigger": 2800, "shares": "all", "phase": 2, "action": "Exit >= 2,800"},
        {"icici_symbol": "ANARAJ", "trigger": 520,  "shares": "all", "phase": 2, "action": "Exit >= 520"},
        {"icici_symbol": "YATHOS", "trigger": 750,  "shares": "all", "phase": 2, "action": "Exit >= 750"},
        {"icici_symbol": "ADAPOW", "trigger": 230,  "shares": "all", "phase": 2, "action": "Exit >= 230"},
        {"icici_symbol": "HERHON", "trigger": 5500, "shares": "all", "phase": 2, "action": "Exit >= 5,500"},
    ]
    return core, triggers

# ---------------------------------------------------------------------------
# F&O CSV parser  (7510078170_FNOPortfolioDetails.csv)
# ---------------------------------------------------------------------------

def _parse_contract(name: str) -> dict | None:
    """
    Parse  OPT-CNXBAN-26-May-2026-52500-P-E
    into   {idx, expiry (date), strike (int), type (str)}
    """
    parts = name.strip().split("-")
    # Expected: OPT | INDEX | DD | MMM | YYYY | STRIKE | P/C | E
    if len(parts) < 8 or parts[0] != "OPT":
        return None
    try:
        idx    = parts[1]
        expiry = datetime.strptime(f"{parts[2]}-{parts[3]}-{parts[4]}", "%d-%b-%Y").date()
        strike = int(parts[5])
        opt_type = parts[6]
        return {"idx": idx, "expiry": expiry, "strike": strike, "type": opt_type}
    except Exception:
        return None


def parse_fno_csv(filepath: str) -> list[dict]:
    """
    Parse ICICI Direct F&O Portfolio Details CSV.
    Returns open short positions only (Trade Flow = Sell, Qty != 0).
    """
    positions = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Find header row (contains "Contract")
    header_idx = next((i for i, l in enumerate(lines) if l.strip().startswith("Contract,")), None)
    if header_idx is None:
        return positions

    reader = csv.DictReader(lines[header_idx:])
    for row in reader:
        contract = row.get("Contract", "").strip()
        flow     = row.get("Trade Flow", "").strip()
        qty_str  = row.get("Open Position Qty", "0").strip()

        try:
            qty = int(float(qty_str))
        except ValueError:
            continue

        if flow != "Sell" or qty == 0:
            continue

        parsed = _parse_contract(contract)
        if parsed is None:
            continue

        try:
            avg = float(row.get("Open Position Avg. Price", "0").strip())
        except ValueError:
            avg = 0.0

        lot = LOT_SIZES.get(parsed["idx"], 0)
        if lot == 0:
            print(f"  Warning: unknown index {parsed['idx']} in {contract}")
            continue

        positions.append({
            "idx":     parsed["idx"],
            "display": INDEX_DISPLAY.get(parsed["idx"], parsed["idx"]),
            "expiry":  parsed["expiry"].strftime("%Y-%m-%d"),
            "strike":  parsed["strike"],
            "type":    parsed["type"],
            "avg":     avg,
            "lot":     abs(qty),   # ICICI stores short qty as negative
        })

    return positions


# ---------------------------------------------------------------------------
# Equity CSV parser  (7500069840_PortFolioEqtAll.csv)
# ---------------------------------------------------------------------------

def parse_equity_csv(filepath: str) -> list[dict]:
    """
    Aggregate buy/sell transactions to compute current holdings.
    Handles bonus shares (price = 0) by adjusting avg cost without adding cost.
    Returns list of {icici_symbol, name, ticker, shares, avg, keep} for non-zero positions.
    """
    totals: dict[str, dict] = {}  # icici_symbol → {shares, total_cost}

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sym    = row.get("Stock Symbol", "").strip()
            action = row.get("Action", "").strip()
            try:
                qty   = float(row.get("Quantity", "0").strip())
                price = float(row.get("Transaction Price", "0").strip())
            except ValueError:
                continue
            if not sym or qty <= 0:
                continue

            if sym not in totals:
                totals[sym] = {"shares": 0.0, "total_cost": 0.0}

            if action == "Buy":
                if price > 0:
                    totals[sym]["total_cost"] += qty * price
                # bonus shares (price = 0) add qty without adding cost → avg halves naturally
                totals[sym]["shares"] += qty
            elif action == "Sell":
                if totals[sym]["shares"] > 0:
                    sell_frac = min(qty / totals[sym]["shares"], 1.0)
                    totals[sym]["total_cost"] *= (1 - sell_frac)
                    totals[sym]["shares"] = max(0, totals[sym]["shares"] - qty)

    holdings = []
    for sym, state in totals.items():
        shares = round(state["shares"])
        if shares <= 0:
            continue
        avg = state["total_cost"] / state["shares"] if state["shares"] > 0 else 0
        name, ticker = SYMBOL_MAP.get(sym, (sym, f"{sym}.NS"))
        holdings.append({
            "icici_symbol": sym,
            "name":   name,
            "ticker": ticker,
            "shares": shares,
            "avg":    round(avg, 2),
        })

    # Sort: known symbols first (in SYMBOL_MAP order), unknowns last
    order = list(SYMBOL_MAP.keys())
    holdings.sort(key=lambda h: order.index(h["icici_symbol"]) if h["icici_symbol"] in order else 999)
    return holdings

# Known cost basis for assigned US equity (update when average cost changes).
# Empower export does not include cost basis.
US_COST_BASIS: dict[str, float] = {
    "PYPL":  82.0,
    "ADBE": 495.0,
    "AXON": 628.0,
    "CRM":  302.0,
    "OKTA":  91.0,
    "NKE":   86.0,
    "LYFT":  30.0,
    "MRNA":  96.0,
    "UNH":  390.0,
    "TWLO": 180.0,   # approximate — update when confirmed
    "ZBH":  130.0,
}

CASH_SYMBOLS = {"VMFXX", "SPAXX", "VUSXX", "FDRXX", "FCASH", "FMPXX", "SPRXX"}
OPT_RE = re.compile(r"^([A-Z0-9]+)(\d{6})([PC])(\d+)")
TICKER_RE = re.compile(r"^[A-Z]{1,6}$")   # valid equity ticker

# ---------------------------------------------------------------------------
# Empower Holdings Parser  (empower-holding*.xlsx)
# ---------------------------------------------------------------------------

def parse_empower_xlsx(filepath: str) -> dict:
    """
    Parse Empower unified holdings Excel export.
    Column A contains all data: 6 header rows then 7 rows per holding
    (symbol, name, shares, price, change%, 1day$, value).

    Returns {equity, options, cash, total, opt_by_underlying}.
    """
    if not _OPENPYXL:
        return {"equity": [], "options": [], "cash": 0.0, "total": 0.0, "opt_by_underlying": {}}

    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    vals = [row[0] for row in ws.iter_rows(values_only=True)]
    raw = vals[6:]   # skip header labels

    holdings = []
    i = 0
    while i + 6 < len(raw):
        block = raw[i:i + 7]
        if all(v is None for v in block):
            i += 1
            continue
        sym = block[0]
        if sym is None:
            i += 1
            continue
        try:
            shares = float(block[2]) if block[2] is not None else 0.0
            price  = float(block[3]) if block[3] is not None else 0.0
            chg    = float(block[4]) if block[4] is not None else 0.0
            val    = float(block[6]) if block[6] is not None else 0.0
        except (TypeError, ValueError):
            i += 1
            continue
        holdings.append({
            "symbol": str(sym).strip(),
            "name":   str(block[1]).strip() if block[1] else "",
            "shares": shares, "price": price, "change_pct": chg, "value": val,
        })
        i += 7

    equity, options, cash_val = [], [], 0.0
    opt_by_und: dict[str, float] = {}

    for h in holdings:
        sym = h["symbol"]

        # Filter out totals rows (numeric symbols or zero-share large-value rows)
        if not any(c.isalpha() for c in sym):
            continue
        # Skip money-market / cash
        if sym in CASH_SYMBOLS or (abs(h["price"] - 1.0) < 0.02 and h["shares"] > 100):
            cash_val += h["value"]
            continue

        m = OPT_RE.match(sym.split(".")[0])
        if m:
            und, exp, opt_type, stk = m.groups()
            try:
                expiry = datetime.strptime(exp, "%y%m%d").strftime("%Y-%m-%d")
            except ValueError:
                expiry = exp
            strike = int(stk) / 1000
            options.append({**h, "underlying": und, "expiry": expiry,
                             "opt_type": opt_type, "strike": strike})
            opt_by_und[und] = opt_by_und.get(und, 0.0) + h["value"]
        elif TICKER_RE.match(sym) and h["shares"] > 0:
            equity.append(h)

    total = sum(h["value"] for h in holdings if any(c.isalpha() for c in h["symbol"]))
    return {
        "equity": sorted(equity, key=lambda x: -x["value"]),
        "options": options,
        "cash": cash_val,
        "total": cash_val + sum(h["value"] for h in equity) + sum(h["value"] for h in options),
        "opt_by_underlying": dict(sorted(opt_by_und.items(), key=lambda x: x[1])),
    }


def analyze_us(empower: dict) -> dict:
    """Compute assigned equity P&L, options summary, and flag urgent names."""
    assigned = []
    for h in empower["equity"]:
        sym = h["symbol"]
        cost_per_share = US_COST_BASIS.get(sym)
        if cost_per_share:
            cost   = cost_per_share * h["shares"]
            pl     = h["value"] - cost
            pl_pct = pl / cost * 100 if cost > 0 else None
        else:
            cost = pl = pl_pct = None
        assigned.append({**h, "cost_per_share": cost_per_share,
                          "total_cost": cost, "pl": pl, "pl_pct": pl_pct})

    # Top 15 options exposures
    top_opts = list(empower["opt_by_underlying"].items())[:15]

    equity_book = sum(h["value"] for h in empower["equity"])
    opts_mark   = sum(h["value"] for h in empower["options"])

    return {
        "assigned":     assigned,
        "top_opts":     top_opts,
        "equity_book":  equity_book,
        "opts_mark":    opts_mark,
        "cash":         empower["cash"],
        "total":        empower["total"],
    }

# ---------------------------------------------------------------------------
# Market Data
# ---------------------------------------------------------------------------

def get_prices(tickers: list[str]) -> dict[str, float | None]:
    if not _YF:
        return {t: None for t in tickers}
    result: dict[str, float | None] = {}
    try:
        data = yf.download(tickers, period="3d", progress=False, auto_adjust=True)
        close = data["Close"] if "Close" in data else data
        for t in tickers:
            try:
                col = close if len(tickers) == 1 else close[t]
                val = col.dropna().iloc[-1]
                result[t] = float(val)
            except Exception:
                result[t] = None
    except Exception:
        for t in tickers:
            try:
                hist = yf.Ticker(t).history(period="3d")
                result[t] = float(hist["Close"].dropna().iloc[-1]) if not hist.empty else None
            except Exception:
                result[t] = None
    return result

# ---------------------------------------------------------------------------
# Black-Scholes Put Pricer
# ---------------------------------------------------------------------------

def bs_put(S: float, K: float, T_days: int, sigma: float, r: float = INDIA_RF) -> float:
    intrinsic = max(0.0, K - S)
    if T_days <= 0 or not _SCIPY or sigma <= 0 or S <= 0:
        return intrinsic
    T = T_days / 365.0
    try:
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        price = K * math.exp(-r * T) * _norm.cdf(-d2) - S * _norm.cdf(-d1)
        return max(intrinsic, float(price))
    except Exception:
        return intrinsic

# ---------------------------------------------------------------------------
# F&O Analysis
# ---------------------------------------------------------------------------

def analyze_fno(positions: list[dict], index_prices: dict, india_vix: float | None) -> list[dict]:
    """Estimate LTP via Black-Scholes and compute % captured for each short put."""
    today    = date.today()
    iv_base  = (india_vix / 100.0) if india_vix else 0.15
    iv_map   = {"NIFTY": iv_base, "CNXBAN": iv_base * 1.20, "NIFMID150": iv_base * 1.30}

    rows = []
    for pos in positions:
        expiry = datetime.strptime(pos["expiry"], "%Y-%m-%d").date()
        dte    = max(0, (expiry - today).days)
        yf_key = INDEX_YF.get(pos["idx"])
        spot   = index_prices.get(yf_key) if yf_key else None
        iv     = iv_map.get(pos["idx"], iv_base)

        ltp_est = bs_put(spot, pos["strike"], dte, iv) if spot else None

        avg = pos["avg"]
        pct = ((avg - ltp_est) / avg * 100) if ltp_est is not None and avg > 0 else None
        net_pl = ((avg - ltp_est) * pos["lot"]) if ltp_est is not None else None

        if ltp_est is None:
            status, sc = "NO DATA", "#888"
        elif dte == 0:
            status, sc = "EXPIRING", "#e74c3c"
        elif ltp_est > avg * 1.05:
            status, sc = "UNDERWATER", "#e74c3c"
        elif pct is not None and pct >= 85:
            status, sc = "ROLL CANDIDATE", "#e67e22"
        elif pct is not None and pct >= 50:
            status, sc = "ON TRACK", "#27ae60"
        else:
            status, sc = "HOLD", "#2c3e50"

        rows.append({**pos, "dte": dte, "spot": spot, "ltp_est": ltp_est,
                     "pct_captured": pct, "net_pl": net_pl,
                     "status": status, "status_color": sc})
    return rows

# ---------------------------------------------------------------------------
# Equity Analysis
# ---------------------------------------------------------------------------

def analyze_equity(
    holdings: list[dict],
    triggers: list[dict],
    core_symbols: list[str],
    prices: dict,
) -> tuple[list[dict], list[dict]]:
    """
    Attach keep flag and live price/P&L to each holding.
    Evaluate exit triggers against current prices.
    """
    # Tag keep status
    eq_rows = []
    for h in holdings:
        price  = prices.get(h["ticker"])
        cost   = h["avg"] * h["shares"]
        mkt    = price * h["shares"] if price else None
        pl     = (mkt - cost) if mkt is not None else None
        pl_pct = (pl / cost * 100) if pl is not None and cost > 0 else None
        keep   = h["icici_symbol"] in core_symbols
        eq_rows.append({**h, "price": price, "cost": cost, "mkt": mkt,
                        "pl": pl, "pl_pct": pl_pct, "keep": keep})

    # Map holdings by ICICI symbol for trigger lookup
    holding_map = {h["icici_symbol"]: h for h in holdings}

    exit_rows = []
    for t in triggers:
        sym  = t["icici_symbol"]
        h    = holding_map.get(sym, {})
        name, ticker = SYMBOL_MAP.get(sym, (sym, f"{sym}.NS"))
        price = prices.get(ticker)
        avg   = h.get("avg", 0)
        total_shares = h.get("shares", 0)
        sell_shares  = total_shares if t["shares"] == "all" else int(t.get("shares", total_shares))

        if t["trigger"] == 0:
            hit = True
        elif price is not None:
            hit = price >= t["trigger"]
        else:
            hit = False

        pl_est = (price - avg) * sell_shares if price and avg else None

        exit_rows.append({
            **t,
            "name": name,
            "ticker": ticker,
            "avg": avg,
            "total_shares": total_shares,
            "sell_shares": sell_shares,
            "price": price,
            "pl_est": pl_est,
            "hit": hit,
        })

    return eq_rows, exit_rows

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _inr(v: float | None, dec: int = 0) -> str:
    return f"&#8377;{v:,.{dec}f}" if v is not None else "&#8212;"

def _pct(v: float | None) -> str:
    if v is None: return "&#8212;"
    return f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%"

def _pcol(v: float | None) -> str:
    if v is None: return "#888"
    return "#27ae60" if v >= 0 else "#e74c3c"

def _section(title: str, body: str) -> str:
    return (
        f'<div style="margin:20px 0;padding:16px;border:1px solid #e0e0e0;border-radius:6px;">'
        f'<h2 style="margin:0 0 12px 0;font-size:16px;color:#1a1a2e;'
        f'border-bottom:2px solid #e94560;padding-bottom:6px;">{title}</h2>{body}</div>'
    )

def _thead(*cols: str) -> str:
    cells = "".join(f'<th style="background:#1a1a2e;color:white;padding:8px 12px;text-align:left;">{c}</th>' for c in cols)
    return f"<thead><tr>{cells}</tr></thead>"

def _row(i: int, *cells: str, bg_override: str = "") -> str:
    bg = bg_override or ("#f9f9f9" if i % 2 == 0 else "#ffffff")
    tds = "".join(f'<td style="padding:7px 12px;">{c}</td>' for c in cells)
    return f'<tr style="background:{bg}">{tds}</tr>'

def _tbl(thead: str, tbody: str) -> str:
    return f'<table style="width:100%;border-collapse:collapse;font-size:13px;">{thead}<tbody>{tbody}</tbody></table>'

# ---------------------------------------------------------------------------
# HTML Builder
# ---------------------------------------------------------------------------

def build_us_section(us: dict) -> str:
    """Build US portfolio HTML section from analyzed Empower data."""
    # Summary bar
    total   = us["total"]
    cash    = us["cash"]
    eq_book = us["equity_book"]
    opts_mk = us["opts_mark"]
    danger  = eq_book > 375_000
    book_col = "#e74c3c" if danger else "#e67e22" if eq_book > 300_000 else "#27ae60"

    summary = (
        f'<div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:12px;">'
        f'<div style="padding:10px 16px;background:#f4f4f4;border-radius:5px;">'
        f'<div style="font-size:11px;color:#888;">Total Portfolio</div>'
        f'<div style="font-size:20px;font-weight:bold;">${total:,.0f}</div></div>'
        f'<div style="padding:10px 16px;background:#f4f4f4;border-radius:5px;">'
        f'<div style="font-size:11px;color:#888;">Cash / MM</div>'
        f'<div style="font-size:20px;font-weight:bold;">${cash:,.0f}</div></div>'
        f'<div style="padding:10px 16px;background:#f4f4f4;border-radius:5px;">'
        f'<div style="font-size:11px;color:#888;">Equity Book</div>'
        f'<div style="font-size:20px;font-weight:bold;color:{book_col};">${eq_book:,.0f}</div>'
        f'<div style="font-size:11px;color:#888;">{"DANGER &gt;$375K" if danger else "Target &le;$375K"}</div></div>'
        f'<div style="padding:10px 16px;background:#f4f4f4;border-radius:5px;">'
        f'<div style="font-size:11px;color:#888;">Options Liability</div>'
        f'<div style="font-size:20px;font-weight:bold;color:#e74c3c;">${opts_mk:,.0f}</div></div>'
        f'</div>'
    )

    # Assigned equity with P&L
    eq_body = ""
    for i, h in enumerate(us["assigned"][:15]):
        bg   = "#fff3cd" if h["pl"] is not None and h["pl"] < -20000 else ""
        pl_s = (f'<span style="color:{_pcol(h["pl"])};">${h["pl"]:+,.0f} ({_pct(h["pl_pct"])})</span>'
                if h["pl"] is not None else '<span style="color:#888;">no basis</span>')
        cb_s = f'${h["cost_per_share"]:.0f}' if h["cost_per_share"] else "—"
        eq_body += _row(
            i,
            f'<b>{h["symbol"]}</b>',
            h["name"][:30],
            f'{h["shares"]:.0f}',
            f'${h["price"]:.2f}',
            cb_s,
            f'<b>${h["value"]:,.0f}</b>',
            pl_s,
            f'<b style="color:{"#27ae60" if h["change_pct"]>=0 else "#e74c3c"};">{h["change_pct"]:+.1f}%</b>',
            bg_override=bg,
        )
    eq_tbl = _tbl(_thead("Symbol","Name","Shares","Price","Cost/sh","Value","Unrealized P&L","Today"), eq_body)

    # Top options exposures
    opt_body = ""
    for i, (und, mk) in enumerate(us["top_opts"]):
        bar_w = min(100, int(abs(mk) / 1200))
        bar = (f'<div style="background:#e74c3c;height:8px;border-radius:4px;'
               f'width:{bar_w}%;display:inline-block;margin-right:6px;vertical-align:middle;"></div>')
        opt_body += _row(i, f'<b>{und}</b>', f'${mk:,.0f}', bar)
    opt_tbl = _tbl(_thead("Underlying","Net Mark","Exposure"), opt_body)

    # Urgent items
    urg_body = "".join(
        _row(i, f'<b style="color:#e74c3c;">{u["symbol"]}</b>', u["note"])
        for i, u in enumerate(US_URGENT)
    )
    urg_tbl = (
        _tbl(_thead("Symbol","Action"), urg_body)
        + '<p style="font-size:12px;color:#888;margin:6px 0 0 0;">'
        + 'YTD net options income: $324K | MTD Apr: $184K | Capture rate: 59.8% (target 65-70%)</p>'
    )

    return (
        summary
        + '<h3 style="margin:16px 0 8px;font-size:14px;color:#1a1a2e;">Assigned Equity — CC Wheel Recovery</h3>'
        + eq_tbl
        + '<h3 style="margin:16px 0 8px;font-size:14px;color:#1a1a2e;">Top Options Exposures (Net Mark)</h3>'
        + opt_tbl
        + '<h3 style="margin:16px 0 8px;font-size:14px;color:#1a1a2e;">Urgent Actions</h3>'
        + urg_tbl
    )


def build_html(
    index_prices: dict, india_vix: float | None, spx: float | None, us_vix: float | None,
    fno_rows: list[dict], eq_rows: list[dict], exit_rows: list[dict],
    report_date: str, data_source: str, us_data: dict | None = None,
) -> str:

    nifty     = index_prices.get("^NSEI")
    banknifty = index_prices.get("^NSEBANK")

    # ── Market Snapshot ──
    def vstatus(v, lo, hi):
        if v is None: return "&#8212;"
        return "LOW" if v < lo else ("ELEVATED" if v > hi else "NORMAL")

    mkt_body = (
        _row(0, "NIFTY 50",   f"<b>{_inr(nifty)}</b>",             "India")
        + _row(1, "BANKNIFTY", f"<b>{_inr(banknifty)}</b>",         "India")
        + _row(2, "India VIX", f"<b>{india_vix:.2f}</b>" if india_vix else "&#8212;", vstatus(india_vix, 14, 20))
        + _row(3, "S&amp;P 500", f"<b>${spx:,.0f}</b>" if spx else "&#8212;", "US")
        + _row(4, "CBOE VIX",  f"<b>{us_vix:.2f}</b>" if us_vix else "&#8212;", vstatus(us_vix, 16, 25))
    )
    mkt_html = (
        _tbl(_thead("Market", "Close", "Status"), mkt_body)
        + '<p style="font-size:12px;color:#888;margin:8px 0 0 0;">'
        + 'India regime: <b>SIDEWAYS/BEARISH</b> — FII net sellers 18+ months. '
        + 'Shift trigger: FII net buyer 10+ consecutive sessions.<br>'
        + 'US regime: <b>APPROACHING TRANSITION</b> — VIX compressing. '
        + 'Bull confirmed: VIX &lt; 20 sustained + S&amp;P above 50d &amp; 200d MA.</p>'
    )

    # ── F&O Positions ──
    total_fno_pl = sum(r["net_pl"] for r in fno_rows if r["net_pl"] is not None)
    fno_body = ""
    for i, r in enumerate(fno_rows):
        ltp_s = f"&#8377;{r['ltp_est']:.1f}" if r["ltp_est"] is not None else "&#8212;"
        pct_s = f"{r['pct_captured']:.0f}%" if r["pct_captured"] is not None else "&#8212;"
        pl_s  = f'<span style="color:{_pcol(r["net_pl"])};">&#8377;{r["net_pl"]:+,.0f}</span>' if r["net_pl"] is not None else "&#8212;"
        sc    = r["status_color"]
        fno_body += _row(
            i,
            f'{r["display"]} {r["strike"]}P',
            f'{r["expiry"]} ({r["dte"]} DTE)',
            _inr(r["spot"]),
            f'&#8377;{r["avg"]:.2f}',
            ltp_s,
            f"<b>{pct_s}</b>",
            pl_s,
            f'<b style="color:{sc};">{r["status"]}</b>',
        )
    fno_html = (
        _tbl(_thead("Contract", "Expiry (DTE)", "Spot", "Avg Recv", "Est LTP", "% Captured", "Net P&L (1 lot)", "Status"), fno_body)
        + f'<p style="font-size:13px;margin:8px 0 0 0;">Total F&amp;O P&amp;L est: '
        + f'<b style="color:{_pcol(total_fno_pl)};">&#8377;{total_fno_pl:+,.0f}</b>'
        + ' &nbsp;|&nbsp; Roll rule: 85-90% captured. LTP = Black-Scholes estimate using India VIX.</p>'
    )

    # ── Exit Triggers ──
    exit_body = ""
    for i, e in enumerate(exit_rows):
        bg    = "#fff3cd" if e["hit"] else ""
        badge = ('<span style="background:#e74c3c;color:white;padding:2px 5px;'
                 'border-radius:3px;font-size:11px;font-weight:bold;">ACTION NOW</span>'
                 if e["hit"] else "")
        pl_s  = f'<span style="color:{_pcol(e["pl_est"])};">&#8377;{e["pl_est"]:+,.0f}</span>' if e["pl_est"] is not None else "&#8212;"
        trig_s = "IMMEDIATE" if e["trigger"] == 0 else f'&#8377;{e["trigger"]:,}'
        shares_s = f'{e["sell_shares"]} / {e["total_shares"]}' if e["sell_shares"] != e["total_shares"] else str(e["total_shares"])
        exit_body += _row(
            i,
            f'Ph{e["phase"]}',
            e["name"],
            shares_s,
            _inr(e["avg"]),
            _inr(e.get("price")),
            pl_s,
            trig_s,
            f'{e["action"]} {badge}',
            bg_override=bg,
        )
    exit_html = (
        _tbl(_thead("Ph", "Stock", "Shares (sell/total)", "Avg Cost", "Current", "Unrealized P&L", "Trigger", "Action"), exit_body)
        + '<p style="font-size:12px;color:#888;margin:6px 0 0 0;">'
        + 'Regime gate: No new equity buys until FII net buyer 10+ consecutive sessions. '
        + 'Edit <code>data/india_config.yaml</code> to add/remove triggers.</p>'
    )

    # ── Equity P&L ──
    eq_body = ""
    total_cost = total_mkt = 0.0
    for i, h in enumerate(eq_rows):
        tag  = "KEEP" if h["keep"] else "WATCH"
        tcol = "#27ae60" if h["keep"] else "#e67e22"
        pl_s = _pct(h["pl_pct"])
        pcol = _pcol(h["pl_pct"])
        if h.get("cost"): total_cost += h["cost"]
        if h.get("mkt"):  total_mkt  += h["mkt"]
        eq_body += _row(
            i,
            h["name"],
            str(h["shares"]),
            _inr(h["avg"]),
            f'<b>{_inr(h.get("price"))}</b>',
            f'<b style="color:{pcol};">{pl_s}</b>',
            f'<span style="color:{tcol};font-weight:bold;font-size:11px;">{tag}</span>',
        )
    total_pl     = total_mkt - total_cost if total_mkt and total_cost else None
    total_pl_pct = (total_pl / total_cost * 100) if total_pl and total_cost > 0 else None
    eq_html = (
        _tbl(_thead("Name", "Shares", "Avg Cost", "Current", "P&L %", "Status"), eq_body)
        + f'<p style="font-size:13px;margin:8px 0 0 0;">'
        + f'Portfolio cost &#8377;{total_cost:,.0f} &rarr; mkt &#8377;{total_mkt:,.0f} '
        + f'(<b style="color:{_pcol(total_pl_pct)};">{_pct(total_pl_pct)}</b>)'
        + ' &nbsp;|&nbsp; Target: 18% CAGR over 3 years &nbsp;|&nbsp; Target: 8-10 names.</p>'
    )

    # ── US Urgent ──
    us_body = "".join(
        _row(i, f'<b style="color:#1a1a2e;">{u["symbol"]}</b>', u["note"])
        for i, u in enumerate(US_URGENT)
    )
    us_html = (
        _tbl(_thead("Symbol", "Urgent Action"), us_body)
        + '<p style="font-size:12px;color:#888;margin:6px 0 0 0;">'
        + 'Account A: ~$401K assigned (danger zone &gt;$375K). '
        + 'Each week without CCs on PYPL/ADBE = $3-5K foregone recovery income.</p>'
    )

    # ── Alert badges ──
    triggered_n = sum(1 for e in exit_rows if e["hit"])
    roll_n      = sum(1 for r in fno_rows if r["status"] == "ROLL CANDIDATE")
    under_n     = sum(1 for r in fno_rows if r["status"] == "UNDERWATER")
    alerts = []
    if triggered_n:
        alerts.append(f'<span style="background:#e74c3c;color:white;padding:3px 8px;border-radius:3px;font-size:12px;margin-right:6px;">{triggered_n} EXIT TRIGGER{"S" if triggered_n > 1 else ""}</span>')
    if roll_n:
        alerts.append(f'<span style="background:#e67e22;color:white;padding:3px 8px;border-radius:3px;font-size:12px;margin-right:6px;">{roll_n} ROLL CANDIDATE{"S" if roll_n > 1 else ""}</span>')
    if under_n:
        alerts.append(f'<span style="background:#c0392b;color:white;padding:3px 8px;border-radius:3px;font-size:12px;margin-right:6px;">{under_n} UNDERWATER</span>')
    alert_bar = "".join(alerts) or '<span style="color:#2ecc71;font-weight:bold;">All positions within normal parameters</span>'

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;color:#333;background:#fff;padding:10px;">
<div style="background:#1a1a2e;color:white;padding:20px 24px;border-radius:6px 6px 0 0;">
  <h1 style="margin:0;font-size:22px;">Trading Report &mdash; {report_date}</h1>
  <div style="font-size:13px;color:#aaa;margin-top:4px;">India + US &nbsp;|&nbsp; 8 PM IST &nbsp;|&nbsp; {data_source}</div>
  <div style="margin-top:10px;">{alert_bar}</div>
</div>
{_section("Market Snapshot", mkt_html)}
{_section("India F&amp;O &mdash; Position Status (All Short Puts, Cash-Settled)", fno_html)}
{_section("India Equity &mdash; Overhaul Exit Triggers", exit_html)}
{_section("India Equity &mdash; Full Portfolio P&amp;L", eq_html)}
{_section("US Accounts &mdash; Urgent Items", us_html)}
{_section("US Portfolio &mdash; Empower Holdings", build_us_section(us_data)) if us_data else ""}
<div style="padding:12px 16px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:20px;">
  Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} &nbsp;|&nbsp;
  F&amp;O LTPs = Black-Scholes estimates; verify in ICICI Direct before acting. &nbsp;|&nbsp;
  US items are semi-static; check Schwab for latest.
</div>
</body></html>"""

# ---------------------------------------------------------------------------
# Email Sender
# ---------------------------------------------------------------------------

def send_report(html: str, subject: str) -> bool:
    if not _RESEND:
        print("ERROR: resend not installed")
        return False
    if not RESEND_KEY:
        print("ERROR: RESEND_API_KEY not set")
        return False
    try:
        resend_client.api_key = RESEND_KEY
        resp = resend_client.Emails.send({"from": FROM_EMAIL, "to": [TO_EMAIL], "subject": subject, "html": html})
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

    statements_dir = os.path.join(DATA_DIR, "statements")

    # 1. Load config (core portfolio + exit triggers)
    core_symbols, trigger_cfg = load_india_config()

    # 2. Parse F&O positions from latest ICICI export
    fno_files = sorted(glob.glob(os.path.join(statements_dir, "7510078170_*.csv")), key=os.path.getmtime)
    if fno_files:
        fno_positions = parse_fno_csv(fno_files[-1])
        print(f"  F&O: {len(fno_positions)} open positions from {os.path.basename(fno_files[-1])}")
    else:
        fno_positions = []
        print("  Warning: no 7510078170_*.csv found in data/statements/")

    # 3. Parse equity holdings from latest ICICI transaction export
    eq_files = sorted(glob.glob(os.path.join(statements_dir, "7500069840_*.csv")), key=os.path.getmtime)
    if eq_files:
        holdings = parse_equity_csv(eq_files[-1])
        print(f"  Equity: {len(holdings)} holdings from {os.path.basename(eq_files[-1])}")
    else:
        holdings = []
        print("  Warning: no 7500069840_*.csv found in data/statements/")

    # 4. Collect all tickers to fetch
    index_tickers = ["^NSEI", "^NSEBANK", "^INDIAVIX", "^GSPC", "^VIX"]
    eq_tickers    = [h["ticker"] for h in holdings]
    trig_tickers  = [SYMBOL_MAP.get(t["icici_symbol"], (None, f'{t["icici_symbol"]}.NS'))[1] for t in trigger_cfg]
    all_tickers   = list(dict.fromkeys(index_tickers + eq_tickers + trig_tickers))

    print(f"  Fetching {len(all_tickers)} tickers from yfinance...")
    prices = get_prices(all_tickers)

    index_prices = {t: prices.get(t) for t in index_tickers}
    india_vix    = prices.get("^INDIAVIX")
    spx          = prices.get("^GSPC")
    us_vix       = prices.get("^VIX")

    nifty_val = index_prices.get("^NSEI")
    bnf_val   = index_prices.get("^NSEBANK")
    print(f"  NIFTY={nifty_val} | BANKNIFTY={bnf_val} | IndiaVIX={india_vix} | SPX={spx} | VIX={us_vix}")

    # 5. Parse Empower US holdings (empower-holding*.xlsx or empower-holidng*.xlsx)
    emp_files = sorted(
        glob.glob(os.path.join(statements_dir, "empower-holding*.xlsx"))
        + glob.glob(os.path.join(statements_dir, "empower-holidng*.xlsx")),
        key=os.path.getmtime,
    )
    if emp_files:
        if not _OPENPYXL:
            print("  Warning: openpyxl not installed — skipping Empower section")
            us_data = None
        else:
            empower = parse_empower_xlsx(emp_files[-1])
            us_data = analyze_us(empower)
            print(f"  Empower: {len(empower['equity'])} equity, {len(empower['options'])} options "
                  f"from {os.path.basename(emp_files[-1])}")
    else:
        us_data = None
        print("  Warning: no empower-holding*.xlsx found in data/statements/")

    # 6. Analyze
    fno_rows             = analyze_fno(fno_positions, index_prices, india_vix)
    eq_rows, exit_rows   = analyze_equity(holdings, trigger_cfg, core_symbols, prices)

    roll_n  = sum(1 for r in fno_rows if r["status"] == "ROLL CANDIDATE")
    under_n = sum(1 for r in fno_rows if r["status"] == "UNDERWATER")
    hit_n   = sum(1 for e in exit_rows if e["hit"])
    print(f"  F&O: {roll_n} roll candidates, {under_n} underwater")
    print(f"  Equity: {hit_n} exit triggers HIT")

    # 7. Build HTML
    fno_src  = os.path.basename(fno_files[-1]) if fno_files else "no file"
    eq_src   = os.path.basename(eq_files[-1]) if eq_files else "no file"
    emp_src  = os.path.basename(emp_files[-1]) if emp_files else "no file"
    data_source = f"F&O: {fno_src} | EQ: {eq_src} | US: {emp_src}"
    html = build_html(index_prices, india_vix, spx, us_vix,
                      fno_rows, eq_rows, exit_rows, report_date, data_source,
                      us_data=us_data)

    # 8. Send
    parts = []
    if hit_n:   parts.append(f"{hit_n} EXIT")
    if roll_n:  parts.append(f"{roll_n} ROLL")
    if under_n: parts.append(f"{under_n} UW")
    alert_tag = f" [{', '.join(parts)}]" if parts else ""
    nifty_s   = f"NIFTY {nifty_val:,.0f}" if nifty_val else "NIFTY —"
    subject   = f"Trading Report {datetime.utcnow().strftime('%a %b %d')}{alert_tag} | {nifty_s} | India+US"

    send_report(html, subject)
    print("  Done.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-email", action="store_true", help="Skip sending email; save HTML to logs/ instead")
    args = parser.parse_args()
    if args.no_email:
        # Monkey-patch send_report to save HTML file instead
        import sys
        _orig_send = send_report
        def _save_only(html, subject):
            logs_dir = os.path.join(DATA_DIR, "..", "logs")
            os.makedirs(logs_dir, exist_ok=True)
            out = os.path.join(logs_dir, f"india_us_report_{date.today()}.html")
            with open(out, "w") as f:
                f.write(html)
            print(f"  Saved → {out}")
            return True
        import builtins
        globals()["send_report"] = _save_only
    main()
