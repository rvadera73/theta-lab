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
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"))
try:
    from analysis.india_regime import detect_india_regime
except ImportError:
    detect_india_regime = None
try:
    from enhanced_metrics import get_ticker_metrics
except ImportError:
    get_ticker_metrics = None

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
    "AURPHA": ("Aurobindo Pharma", "AUROPHARMA.NS"),
    "BAJFI":  ("Bajaj Finance",  "BAJFINANCE.NS"),
    "BHAELE": ("BEL",            "BEL.NS"),
    "BSE":    ("BSE Ltd",        "BSE.NS"),
    "DIXTEC": ("Dixon Tech",     "DIXON.NS"),
    "DLFLIM": ("DLF",            "DLF.NS"),
    "DRREDD": ("Dr Reddy's",     "DRREDDY.NS"),
    "GENOVE": ("Genus Power",    "GENUSPOWER.NS"),
    "HCLTEC": ("HCL Tech",       "HCLTECH.NS"),
    "HDFBAN": ("HDFC Bank",      "HDFCBANK.NS"),
    "HERHON": ("Hero MotoCorp",  "HEROMOTOCO.NS"),
    "HINAER": ("HAL",            "HAL.NS"),
    "IDECEL": ("Vodafone Idea",  "IDEA.NS"),
    "LIC":    ("LIC",            "LICI.NS"),
    "LUPIN":  ("Lupin",          "LUPIN.NS"),
    "MAZDOC": ("Mazagon Dock",   "MAZDOCK.NS"),
    "NTPC":   ("NTPC",           "NTPC.NS"),
    "PARDEF": ("Paras Defence",  "PARAS.NS"),
    "POWGRI": ("Power Grid",     "POWERGRID.NS"),
    "RELIND": ("Reliance",       "RELIANCE.NS"),
    "SOLIN":  ("Solar Industries", "SOLARINDS.NS"),
    "STABAN": ("SBI",            "SBIN.NS"),
    "SUZENE": ("Suzlon",         "SUZLON.NS"),
    "TCS":    ("TCS",            "TCS.NS"),
    "TRENT":  ("Trent Ltd",      "TRENT.NS"),
    "VARBEV": ("Varun Beverages", "VBL.NS"),
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

# Sector + market-cap-segment universe for the recurring theme validation check
# (added 2026-07-19 — see SECTOR_THEME_CHECK below). Tickers verified against
# yfinance; several common candidates (Nifty Smallcap 100, Private Bank, Commodities,
# Manufacturing) had no working Yahoo ticker as of this date and are omitted rather
# than guessed at.
SECTOR_UNIVERSE: dict[str, str] = {
    "Nifty 50 (benchmark)": "^NSEI",
    "Nifty Next 50":        "^NSMIDCP",
    "Nifty Midcap 100":     "NIFTY_MIDCAP_100.NS",
    "Nifty 500 (broad)":    "^CRSLDX",
    "Pharma":                "^CNXPHARMA",
    "IT":                    "^CNXIT",
    "Auto":                  "^CNXAUTO",
    "Realty":                "^CNXREALTY",
    "Energy":                "^CNXENERGY",
    "Bank":                  "^NSEBANK",
    "PSU Bank":              "^CNXPSUBANK",
    "FMCG":                  "^CNXFMCG",
    "Metal":                 "^CNXMETAL",
    "Infra":                 "^CNXINFRA",
    "PSE (PSU/defense proxy)": "^CNXPSE",
    "Media":                 "^CNXMEDIA",
    "Consumption":           "^CNXCONSUM",
    "MNC":                   "^CNXMNC",
}

# Which sector labels above map to each india_config.yaml core_portfolio theme —
# used to auto-flag when a "core" theme's underlying sector has stopped confirming it.
THEME_SECTOR_MAP: dict[str, list[str]] = {
    "Defense":            ["PSE (PSU/defense proxy)"],
    "Electricity/Power":  ["Energy"],
    "Hospitals":          [],  # no clean NSE healthcare-services index on yfinance
    "Real Estate":        ["Realty"],
    "Value/Banking":      ["Bank", "PSU Bank"],
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

def load_india_config() -> tuple[list[str], list[dict], list[dict]]:
    """
    Returns (core_portfolio_symbols, exit_triggers, watchlist).
    Falls back to hardcoded defaults if YAML not available.
    """
    cfg_path = os.path.join(DATA_DIR, "india_config.yaml")
    if _YAML and os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        core = cfg.get("core_portfolio", [])
        triggers = cfg.get("exit_triggers", [])
        watchlist = cfg.get("watchlist", [])
        print(f"  Config: {len(core)} core symbols, {len(triggers)} exit triggers, {len(watchlist)} watchlist")
        return core, triggers, watchlist

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
    return core, triggers, []

# ---------------------------------------------------------------------------
# Watchlist — new entry candidates (live-checked every run)
# ---------------------------------------------------------------------------

WATCHLIST_YF: dict[str, str] = {
    "KAYNES":     "KAYNES.NS",
    "SOLARINDS":  "SOLARINDS.NS",
    "GVTD":       "GVT&D.NS",
    "POWERINDIA": "POWERINDIA.NS",
}


def check_watchlist(watchlist: list[dict], new_entries_allowed: bool) -> list[dict]:
    """
    Live-checks each data/india_config.yaml watchlist candidate against its planned
    entry zone + a fresh conviction score. Added 2026-07-19 — the report previously
    never suggested anything new, only verdicts on existing holdings; the watchlist
    itself was also last checked manually in conversation, not automatically. Now
    recomputed every run alongside everything else.
    """
    if get_ticker_metrics is None:
        return []
    rows = []
    for w in watchlist:
        sym = w["symbol"]
        ticker = WATCHLIST_YF.get(sym, f"{sym}.NS")
        try:
            hist = yf.Ticker(ticker).history(period="5d")["Close"]
            current = float(hist.iloc[-1]) if not hist.empty else w.get("current_price")
        except Exception:
            current = w.get("current_price")
        metrics = get_ticker_metrics(ticker, current) if current else None

        lo, hi = w["entry_zone_low"], w["entry_zone_high"]
        if current is None:
            status, status_color = "NO DATA", "#888"
        elif current < lo:
            status, status_color = "BELOW ZONE — cheaper than planned", "#27ae60"
        elif current <= hi:
            status, status_color = "IN ZONE", "#27ae60"
        else:
            pct_above = (current / hi - 1) * 100
            status, status_color = f"ABOVE ZONE (+{pct_above:.0f}%) — wait", "#e67e22"

        rows.append({
            **w, "ticker": ticker, "current": current,
            "status": status, "status_color": status_color,
            "conviction": metrics["conviction"] if metrics else None,
            "analyst_rating": metrics["analyst_rating"] if metrics else None,
            "target_upside_pct": metrics["target_upside_pct"] if metrics else None,
            "actionable": bool(new_entries_allowed and current is not None and current <= hi),
        })
    return rows

# ---------------------------------------------------------------------------
# Sector & market-cap momentum — recurring theme validation
# ---------------------------------------------------------------------------

def check_sector_themes() -> dict:
    """
    Pulls 3mo/6mo returns for the sector + market-cap-segment universe and checks
    them against india_config.yaml's core_portfolio themes. Runs every report
    (this script executes Sun-Thu via GitHub Actions), not on a manual schedule —
    added 2026-07-19 after Pharma was found outperforming 4 of the 5 "core" themes
    while being explicitly excluded, and cited as the reason to exit a name whose
    actual problem was company-specific, not sector-wide.

    Flags:
      - a "core" theme's sector underperforming Nifty 50 on BOTH windows -> cooling
      - a non-core sector outperforming Nifty 50 by 10+ pts on BOTH windows -> reconsider
    """
    if not _YF:
        return {"rows": [], "cooling": [], "reconsider": []}

    rows = []
    for name, ticker in SECTOR_UNIVERSE.items():
        try:
            hist = yf.Ticker(ticker).history(period="1y")["Close"]
            if hist.empty or len(hist) < 63:
                continue
            current = hist.iloc[-1]
            chg3 = (current / hist.iloc[-63] - 1) * 100
            chg6 = (current / hist.iloc[-126] - 1) * 100 if len(hist) > 126 else None
            rows.append({"name": name, "ticker": ticker, "chg3mo": chg3, "chg6mo": chg6})
        except Exception:
            continue

    bench = next((r for r in rows if r["name"].startswith("Nifty 50")), None)
    bench3 = bench["chg3mo"] if bench else 0.0
    bench6 = bench["chg6mo"] if bench else 0.0

    core_sector_names = {s for sectors in THEME_SECTOR_MAP.values() for s in sectors}
    cooling, reconsider = [], []
    for r in rows:
        if r["chg6mo"] is None or r["name"].startswith("Nifty 50"):
            continue
        rel3, rel6 = r["chg3mo"] - bench3, r["chg6mo"] - bench6
        if r["name"] in core_sector_names and rel3 < 0 and rel6 < 0:
            cooling.append({**r, "vs_bench_3mo": rel3, "vs_bench_6mo": rel6})
        elif r["name"] not in core_sector_names and rel3 > 10 and rel6 > 10:
            reconsider.append({**r, "vs_bench_3mo": rel3, "vs_bench_6mo": rel6})

    return {"rows": rows, "cooling": cooling, "reconsider": reconsider}

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

def _verdict_from_conviction(conviction: float, heat_status: str) -> tuple[str, str]:
    """
    Derive (verdict, color) from live conviction score + heat status.
    Mirrors the US unified-master-report Position Heat Matrix framework
    (trading_persona.md Section 6), extended so conviction (now fundamentals-
    weighted — see enhanced_metrics.py) can override a merely-technical "GREEN"
    reading: heat alone only measures technical extremity, not business quality,
    so a fundamentally weak name sitting at a neutral RSI/52w-position (GREEN heat)
    must not default to LET RUN just because nothing looks extreme technically.
    This replaces static core-list / price-trigger tagging, which goes stale in
    both directions (2026-07-19 audit: DRREDD's trigger understated risk,
    STABAN's overstated it) — conviction+heat are recomputed every run instead.
    """
    # CRITICAL used to conflate two different situations (2026-07-19: Solar Industries
    # and Apollo Hospitals both flagged CRITICAL despite conviction 7+ and confusing the
    # trader) — split into WEAK (fundamentals genuinely bad) vs EXTENDED (good business,
    # just technically overbought — a trim-consideration, not an exit-the-thesis signal).
    if conviction < 4:
        return "WEAK", "#e74c3c"
    if heat_status == "RED":
        return "EXTENDED", "#c0392b"
    if heat_status == "YELLOW" and conviction < 5:
        return "WEAK", "#e74c3c"
    if heat_status == "YELLOW":
        return "MONITOR", "#e67e22"
    if heat_status == "GREEN" and conviction < 5:
        return "MONITOR", "#e67e22"  # oversold/neutral but fundamentally weak — value-trap risk, not a blind hold
    return "LET RUN", "#27ae60"


def _verdict_reason(h: dict) -> str:
    """
    Plain-English one-liner explaining WHY a row got its verdict, built from the
    same numbers already in the row (conviction/heat drivers). Added 2026-07-19 —
    previously only rows with a legacy config note showed any explanation at all;
    everything else (Adani Ports, BEL, BSE, ...) was a bare badge with numbers the
    trader had to decode by hand. Every row explains itself now.
    """
    drivers = []
    rg, eg = h.get("revenue_growth"), h.get("earnings_growth")
    rating, tgt_up = h.get("analyst_rating"), h.get("target_upside_pct")

    if eg is not None:
        if eg <= -20:
            drivers.append(f"earnings {eg:+.0f}% YoY (deteriorating)")
        elif eg > 20:
            drivers.append(f"earnings {eg:+.0f}% YoY (strong)")
        elif eg < 0:
            drivers.append(f"earnings {eg:+.0f}% YoY (softening)")
    if rg is not None:
        if rg < -5:
            drivers.append(f"revenue {rg:+.0f}% YoY (declining)")
        elif rg > 20:
            drivers.append(f"revenue {rg:+.0f}% YoY (strong)")
    if rating:
        drivers.append(f"analyst: {rating.replace('_', ' ')}")
    if tgt_up is not None:
        drivers.append(f"target {tgt_up:+.0f}% {'above' if tgt_up >= 0 else 'below'} current price")

    fundamentals_s = "; ".join(drivers) if drivers else "no analyst/fundamentals data on file"
    technical_s = f"{h['heat_reason']} (RSI {h['rsi']:.0f}, {h['position_52w']:.0f}% of 52w range)"
    return f"{fundamentals_s} &nbsp;|&nbsp; {technical_s}"


def analyze_equity(
    holdings: list[dict],
    triggers: list[dict],
    core_symbols: list[str],
    prices: dict,
) -> tuple[list[dict], list[dict]]:
    """
    Attach live price/P&L + live conviction score (RSI/MACD/valuation/52w-position,
    via enhanced_metrics.get_ticker_metrics — the same engine the US reports use) to
    each holding, and derive a verdict from it. Any config-level trigger note is kept
    as informational context (not the action gate) so a stale price level can no
    longer contradict the live data the way it did before.
    """
    trigger_notes = {t["icici_symbol"]: t for t in triggers}

    eq_rows = []
    for h in holdings:
        price  = prices.get(h["ticker"])
        cost   = h["avg"] * h["shares"]
        mkt    = price * h["shares"] if price else None
        pl     = (mkt - cost) if mkt is not None else None
        pl_pct = (pl / cost * 100) if pl is not None and cost > 0 else None

        metrics = (
            get_ticker_metrics(h["ticker"], price or h["avg"])
            if get_ticker_metrics is not None
            else None
        )
        if metrics:
            conviction, rsi = metrics["conviction"], metrics["rsi"]
            heat_status, heat_reason = metrics["heat_status"], metrics["heat_reason"]
            pos_52w, pe = metrics["position_in_52w_range"], metrics["pe_ratio"]
            rev_g, earn_g = metrics["revenue_growth"], metrics["earnings_growth"]
            rating, tgt_up = metrics["analyst_rating"], metrics["target_upside_pct"]
        else:
            conviction, rsi, heat_status, heat_reason, pos_52w, pe = 5.0, 50.0, "YELLOW", "No data", 50.0, None
            rev_g, earn_g, rating, tgt_up = None, None, None, None
        verdict, verdict_color = _verdict_from_conviction(conviction, heat_status)

        note = trigger_notes.get(h["icici_symbol"], {}).get("action")
        is_core = h["icici_symbol"] in core_symbols

        eq_rows.append({
            **h, "price": price, "cost": cost, "mkt": mkt, "pl": pl, "pl_pct": pl_pct,
            "conviction": conviction, "rsi": rsi, "heat_status": heat_status,
            "heat_reason": heat_reason, "position_52w": pos_52w, "pe_ratio": pe,
            "revenue_growth": rev_g, "earnings_growth": earn_g,
            "analyst_rating": rating, "target_upside_pct": tgt_up,
            "verdict": verdict, "verdict_color": verdict_color,
            "is_core": is_core, "config_note": note,
        })

    # Legacy exit_triggers config is now purely informational — surfaced alongside
    # the live verdict above, not used to gate an ACTION NOW badge on its own.
    return eq_rows, []

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


def build_india_html(
    index_prices: dict, india_vix: float | None, spx: float | None, us_vix: float | None,
    fno_rows: list[dict], eq_rows: list[dict], exit_rows: list[dict],
    report_date: str, data_source: str,
    regime_data: dict | None = None, sector_check: dict | None = None,
    watchlist_rows: list[dict] | None = None, new_entries_allowed: bool = False,
) -> str:
    """Build India-only evening report: F&O positions, equity P&L, exit triggers."""

    nifty     = index_prices.get("^NSEI")
    banknifty = index_prices.get("^NSEBANK")

    def vstatus(v, lo, hi):
        if v is None: return "&#8212;"
        return "LOW" if v < lo else ("ELEVATED" if v > hi else "NORMAL")

    # ── India Market Snapshot (S&P/VIX included as macro context for FII flows) ──
    mkt_body = (
        _row(0, "NIFTY 50",    f"<b>{_inr(nifty)}</b>",                                   "India")
        + _row(1, "BANKNIFTY", f"<b>{_inr(banknifty)}</b>",                               "India")
        + _row(2, "India VIX", f"<b>{india_vix:.2f}</b>" if india_vix else "&#8212;",     vstatus(india_vix, 14, 20))
        + _row(3, "S&amp;P 500 (macro)", f"<b>${spx:,.0f}</b>" if spx else "&#8212;",    "US macro")
        + _row(4, "CBOE VIX (macro)",    f"<b>{us_vix:.2f}</b>" if us_vix else "&#8212;", vstatus(us_vix, 16, 25))
    )
    if regime_data:
        regime_label = regime_data.get("regime", "UNKNOWN")
        sigs = regime_data.get("signals", {})
        sig_bits = []
        if "india_vix" in sigs:
            sig_bits.append(sigs["india_vix"]["detail"])
        if "nifty50_ma" in sigs:
            m = sigs["nifty50_ma"]
            sig_bits.append(
                f"Nifty {m['current']:,.0f} vs 50MA {m['ma50']:,.0f} "
                f"({'above' if m['above_50d'] else 'below'}) / 200MA {m['ma200']:,.0f} "
                f"({'above' if m['above_200d'] else 'below'})"
            )
        regime_line = f"Regime: <b>{regime_label}</b> — " + "; ".join(sig_bits)
        regime_line += (
            " &nbsp;<i>(technical signals only — VIX + Nifty MAs; "
            "no live FII flow data source wired in)</i>"
        )
    else:
        regime_line = "Regime: <b>UNKNOWN</b> — regime detector unavailable this run."
    mkt_html = (
        _tbl(_thead("Market", "Close", "Status"), mkt_body)
        + '<p style="font-size:12px;color:#888;margin:8px 0 0 0;">'
        + regime_line + '</p>'
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

    # ── Equity — unified live verdict table (conviction+heat driven; replaces the
    #    old separate KEEP/WATCH table + static price-trigger table, whose independent
    #    logic could and did disagree on the same symbol — e.g. YATHOS showing as both
    #    KEEP and ACTION NOW on 2026-07-19). Legacy config notes shown as context only.
    eq_body = ""
    total_cost = total_mkt = 0.0
    for i, h in enumerate(eq_rows):
        pl_s = _pct(h["pl_pct"])
        pcol = _pcol(h["pl_pct"])
        if h.get("cost"): total_cost += h["cost"]
        if h.get("mkt"):  total_mkt  += h["mkt"]
        core_tag = ' <span style="color:#888;font-size:10px;">(core)</span>' if h.get("is_core") else ""
        note = h.get("config_note")
        # A legacy config note urging exit is contradicted if live analysis says LET RUN/MONITOR
        # (2026-07-19: SBI showed "Exit immediately -43% loss" directly under a green LET RUN
        # verdict — confusing and undermines trust in the live number). Strike it through instead
        # of leaving it to silently contradict the verdict above it.
        contradicted = bool(note) and "exit" in note.lower() and h["verdict"] in ("LET RUN", "MONITOR")
        if note and contradicted:
            note_s = (f'<div style="font-size:11px;color:#aaa;margin-top:2px;">'
                       f'<s>{note}</s> <i>(superseded — live analysis does not support this)</i></div>')
        elif note:
            note_s = f'<div style="font-size:11px;color:#888;margin-top:2px;">{note}</div>'
        else:
            note_s = ""
        reason_s = f'<div style="font-size:11px;color:#666;margin-top:2px;">{_verdict_reason(h)}</div>'
        pe_s = f'{h["pe_ratio"]:.1f}' if h.get("pe_ratio") else "&#8212;"
        eq_body += _row(
            i,
            h["name"] + core_tag,
            str(h["shares"]),
            _inr(h["avg"]),
            f'<b>{_inr(h.get("price"))}</b>',
            f'<b style="color:{pcol};">{pl_s}</b>',
            f'{h["conviction"]:.1f}',
            f'{h["rsi"]:.0f}',
            pe_s,
            f'{h["position_52w"]:.0f}%',
            f'<b style="color:{h["verdict_color"]};">{h["verdict"]}</b>{reason_s}{note_s}',
        )
    total_pl     = total_mkt - total_cost if total_mkt and total_cost else None
    total_pl_pct = (total_pl / total_cost * 100) if total_pl and total_cost > 0 else None
    eq_html = (
        _tbl(_thead("Name", "Shares", "Avg Cost", "Current", "P&L %", "Conv", "RSI", "PE", "52wPos", "Verdict"), eq_body)
        + f'<p style="font-size:13px;margin:8px 0 0 0;">'
        + f'Portfolio cost &#8377;{total_cost:,.0f} &rarr; mkt &#8377;{total_mkt:,.0f} '
        + f'(<b style="color:{_pcol(total_pl_pct)};">{_pct(total_pl_pct)}</b>)'
        + ' &nbsp;|&nbsp; Target: 18% CAGR over 3 years.</p>'
        + '<p style="font-size:11px;color:#888;margin:4px 0 0 0;">'
        + 'Verdict = live conviction score (fundamentals-weighted: revenue/earnings growth, analyst '
        + 'rating/target upside &mdash; PRIMARY; RSI/MACD/PE/52w-position &mdash; supplemental) + heat status, '
        + 'recomputed every run, not a stale price trigger. '
        + '<b style="color:#e74c3c;">WEAK</b> = conviction &lt;4, or YELLOW heat with conviction &lt;5 &mdash; fundamentals genuinely weak. '
        + '<b style="color:#c0392b;">EXTENDED</b> = RED heat (technically overbought/near 52w high) regardless of conviction &mdash; '
        + 'a good business can still be a trim candidate here; this is NOT the same as WEAK. '
        + 'MONITOR = YELLOW heat with conviction &ge;5, or GREEN heat with conviction &lt;5 (value-trap check). '
        + 'LET RUN = GREEN heat with conviction &ge;5. '
        + '(core) = long-term thematic tag from <code>data/india_config.yaml</code>, informational only.</p>'
    )

    # ── Sector & Market-Cap Momentum — recurring theme validation (every run) ──
    sc = sector_check or {"rows": [], "cooling": [], "reconsider": []}
    sector_body = ""
    for i, r in enumerate(sc["rows"]):
        c3 = f'{r["chg3mo"]:+.1f}%' if r["chg3mo"] is not None else "&#8212;"
        c6 = f'{r["chg6mo"]:+.1f}%' if r["chg6mo"] is not None else "&#8212;"
        c3col = _pcol(r["chg3mo"])
        c6col = _pcol(r["chg6mo"]) if r["chg6mo"] is not None else "#888"
        flag = ""
        if any(x["name"] == r["name"] for x in sc["cooling"]):
            flag = ' <span style="background:#e67e22;color:white;padding:1px 5px;border-radius:3px;font-size:10px;">COOLING (core theme)</span>'
        elif any(x["name"] == r["name"] for x in sc["reconsider"]):
            flag = ' <span style="background:#27ae60;color:white;padding:1px 5px;border-radius:3px;font-size:10px;">RECONSIDER (non-core, outperforming)</span>'
        sector_body += _row(
            i, r["name"] + flag,
            f'<span style="color:{c3col};">{c3}</span>',
            f'<span style="color:{c6col};">{c6}</span>',
        )
    sector_html = (
        _tbl(_thead("Sector / Segment", "3mo vs prior", "6mo vs prior"), sector_body)
        + '<p style="font-size:11px;color:#888;margin:6px 0 0 0;">'
        + 'Checked every run against <code>data/india_config.yaml</code> core themes (Defense, '
        + 'Electricity/Power, Real Estate, Value/Banking — Hospitals has no clean NSE index proxy). '
        + 'COOLING = a core theme\'s sector underperforming Nifty 50 on both 3mo and 6mo. '
        + 'RECONSIDER = a non-core sector outperforming Nifty 50 by 10+ points on both windows. '
        + '2026-07-19: Pharma flagged RECONSIDER — it was excluded from core themes yet '
        + 'outperformed 4 of the 5 core themes over this period.</p>'
    )

    # ── New Entry Candidates — watchlist, live-checked every run ──
    wl = watchlist_rows or []
    wl_body = ""
    for i, w in enumerate(wl):
        conv_s = f'{w["conviction"]:.1f}' if w.get("conviction") is not None else "&#8212;"
        rating_s = w["analyst_rating"].replace("_", " ") if w.get("analyst_rating") else "&#8212;"
        tgt_s = f'{w["target_upside_pct"]:+.0f}%' if w.get("target_upside_pct") is not None else "&#8212;"
        action_badge = (
            '<span style="background:#27ae60;color:white;padding:2px 5px;border-radius:3px;font-size:11px;font-weight:bold;">ACTIONABLE</span>'
            if w["actionable"] else ""
        )
        wl_body += _row(
            i, w["name"],
            f'{_inr(w.get("current"))}',
            f'{_inr(w["entry_zone_low"])}&ndash;{_inr(w["entry_zone_high"])}',
            f'<b style="color:{w["status_color"]};">{w["status"]}</b> {action_badge}',
            conv_s, rating_s, tgt_s,
        )
    entries_note = (
        "New entries allowed this regime (selective, per your framework)."
        if new_entries_allowed else
        "Regime does not currently allow new entries — shown for awareness/planning only, not action."
    )
    watchlist_html = (
        _tbl(_thead("Name", "Current", "Entry Zone", "Status", "Conv", "Analyst", "Target Up"), wl_body)
        + f'<p style="font-size:12px;color:#888;margin:6px 0 0 0;">{entries_note} '
        + 'Checked live every run (price + conviction) against <code>data/india_config.yaml</code> '
        + 'watchlist entry zones — added 2026-07-20 so this is a live suggestion, not something only '
        + 'checked when manually asked. Add new candidates to the watchlist to have them checked here too.</p>'
        if wl else
        '<p style="color:#888;">No watchlist entries in <code>data/india_config.yaml</code>.</p>'
    )

    # ── Alert badges ──
    triggered_n = sum(1 for h in eq_rows if h["verdict"] in ("WEAK", "EXTENDED"))
    roll_n      = sum(1 for r in fno_rows if r["status"] == "ROLL CANDIDATE")
    under_n     = sum(1 for r in fno_rows if r["status"] == "UNDERWATER")
    alerts = []
    if triggered_n:
        alerts.append(f'<span style="background:#e74c3c;color:white;padding:3px 8px;border-radius:3px;font-size:12px;margin-right:6px;">{triggered_n} WEAK/EXTENDED</span>')
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
  <h1 style="margin:0;font-size:22px;">India Trading Report &mdash; {report_date}</h1>
  <div style="font-size:13px;color:#aaa;margin-top:4px;">ICICI Direct NRI &nbsp;|&nbsp; 8 PM IST &nbsp;|&nbsp; {data_source}</div>
  <div style="margin-top:10px;">{alert_bar}</div>
</div>
{_section("Market Snapshot", mkt_html)}
{_section("Sector &amp; Market-Cap Momentum &mdash; Theme Validation", sector_html)}
{_section("India F&amp;O &mdash; Position Status (All Short Puts, Cash-Settled)", fno_html)}
{_section("India Equity &mdash; Live Conviction &amp; Verdict", eq_html)}
{_section("New Entry Candidates &mdash; Watchlist", watchlist_html)}
<div style="padding:12px 16px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:20px;">
  Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} &nbsp;|&nbsp;
  F&amp;O LTPs = Black-Scholes estimates using India VIX; verify in ICICI Direct before acting.
</div>
</body></html>"""


def build_us_html(
    spx: float | None, us_vix: float | None,
    us_data: dict | None,
    report_date: str, data_source: str,
) -> str:
    """Build US-only evening report: Empower portfolio + urgent actions."""

    def vstatus(v, lo, hi):
        if v is None: return "&#8212;"
        return "LOW" if v < lo else ("ELEVATED" if v > hi else "NORMAL")

    # ── US Market Snapshot ──
    mkt_body = (
        _row(0, "S&amp;P 500", f"<b>${spx:,.0f}</b>" if spx else "&#8212;", "US")
        + _row(1, "CBOE VIX",  f"<b>{us_vix:.2f}</b>" if us_vix else "&#8212;", vstatus(us_vix, 16, 25))
    )
    mkt_html = (
        _tbl(_thead("Market", "Close", "Status"), mkt_body)
        + '<p style="font-size:12px;color:#888;margin:8px 0 0 0;">'
        + 'Regime: <b>APPROACHING TRANSITION</b> — VIX compressing. '
        + 'Bull confirmed: VIX &lt; 20 sustained + S&amp;P above 50d &amp; 200d MA.</p>'
    )

    # ── US Urgent Actions ──
    urg_body = "".join(
        _row(i, f'<b style="color:#e74c3c;">{u["symbol"]}</b>', u["note"])
        for i, u in enumerate(US_URGENT)
    )
    urg_html = (
        _tbl(_thead("Symbol", "Action Required"), urg_body)
        + '<p style="font-size:12px;color:#888;margin:6px 0 0 0;">'
        + 'YTD net options income: $324K &nbsp;|&nbsp; MTD Apr: $184K &nbsp;|&nbsp; '
        + 'Capture rate: 59.8% (target 65-70%)</p>'
    )

    # ── Empower Portfolio ──
    emp_html = build_us_section(us_data) if us_data else (
        '<p style="color:#888;">No Empower file found in data/statements/. '
        'Drop empower-holding*.xlsx there to populate this section.</p>'
    )

    # Alert bar
    danger = us_data and us_data["equity_book"] > 375_000
    alert_bar = (
        '<span style="background:#e74c3c;color:white;padding:3px 8px;border-radius:3px;font-size:12px;">'
        'ASSIGNED EQUITY DANGER ZONE &gt;$375K</span>'
        if danger else
        '<span style="color:#2ecc71;font-weight:bold;">Equity book within target range</span>'
    )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;color:#333;background:#fff;padding:10px;">
<div style="background:#0d3b66;color:white;padding:20px 24px;border-radius:6px 6px 0 0;">
  <h1 style="margin:0;font-size:22px;">US Portfolio Report &mdash; {report_date}</h1>
  <div style="font-size:13px;color:#aaa;margin-top:4px;">Empower &amp; Schwab (Accounts A+B) &nbsp;|&nbsp; {data_source}</div>
  <div style="margin-top:10px;">{alert_bar}</div>
</div>
{_section("US Market Snapshot", mkt_html)}
{_section("Urgent Actions", urg_html)}
{_section("Portfolio Holdings &mdash; Empower", emp_html)}
<div style="padding:12px 16px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:20px;">
  Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} &nbsp;|&nbsp;
  Holdings from Empower export; verify live prices in Schwab before acting.
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

    # 1. Load config (core portfolio + exit triggers + watchlist)
    core_symbols, trigger_cfg, watchlist_cfg = load_india_config()

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

    # 5b. Regime — real technical signals (VIX + Nifty MAs), not the old hardcoded narrative
    regime_data = None
    if detect_india_regime is not None:
        try:
            regime_data = detect_india_regime()
            print(f"  Regime: {regime_data['regime']} "
                  f"(bull_signals={regime_data['bull_signal_count']}, bear_signals={regime_data['bear_signal_count']})")
        except Exception as e:
            print(f"  Warning: regime detection failed: {e}")
    else:
        print("  Warning: could not import detect_india_regime — regime section will show UNKNOWN")

    # 5c. Sector & market-cap momentum — recurring theme validation (every run)
    sector_check = check_sector_themes()
    if sector_check["cooling"]:
        print(f"  Sector check: {len(sector_check['cooling'])} core theme(s) cooling vs Nifty 50")
    if sector_check["reconsider"]:
        names = ", ".join(r["name"] for r in sector_check["reconsider"])
        print(f"  Sector check: non-core sector(s) outperforming 10+pts both windows: {names}")

    # 6. Analyze
    fno_rows             = analyze_fno(fno_positions, index_prices, india_vix)
    eq_rows, exit_rows   = analyze_equity(holdings, trigger_cfg, core_symbols, prices)

    roll_n  = sum(1 for r in fno_rows if r["status"] == "ROLL CANDIDATE")
    under_n = sum(1 for r in fno_rows if r["status"] == "UNDERWATER")
    hit_n   = sum(1 for h in eq_rows if h["verdict"] in ("WEAK", "EXTENDED"))
    print(f"  F&O: {roll_n} roll candidates, {under_n} underwater")
    print(f"  Equity: {hit_n} WEAK/EXTENDED (live conviction+heat)")

    new_entries_allowed = bool(regime_data and regime_data.get("new_entries_allowed"))
    watchlist_rows = check_watchlist(watchlist_cfg, new_entries_allowed)
    actionable_n = sum(1 for w in watchlist_rows if w["actionable"])
    print(f"  Watchlist: {actionable_n} of {len(watchlist_rows)} actionable "
          f"(new entries {'allowed' if new_entries_allowed else 'NOT allowed'} — regime {regime_data.get('regime') if regime_data else 'unknown'})")

    # 7. Build HTML — two separate reports
    fno_src  = os.path.basename(fno_files[-1]) if fno_files else "no file"
    eq_src   = os.path.basename(eq_files[-1]) if eq_files else "no file"
    emp_src  = os.path.basename(emp_files[-1]) if emp_files else "no file"

    india_html = build_india_html(
        index_prices, india_vix, spx, us_vix,
        fno_rows, eq_rows, exit_rows,
        report_date, f"F&O: {fno_src} | EQ: {eq_src}",
        regime_data=regime_data, sector_check=sector_check,
        watchlist_rows=watchlist_rows, new_entries_allowed=new_entries_allowed,
    )
    us_html = build_us_html(
        spx, us_vix, us_data,
        report_date, f"Empower: {emp_src}",
    )

    # 8. Send — India report
    parts = []
    if hit_n:   parts.append(f"{hit_n} WEAK/EXT")
    if roll_n:  parts.append(f"{roll_n} ROLL")
    if under_n: parts.append(f"{under_n} UW")
    alert_tag = f" [{', '.join(parts)}]" if parts else ""
    nifty_s   = f"NIFTY {nifty_val:,.0f}" if nifty_val else "NIFTY —"
    india_subject = f"India Report {datetime.utcnow().strftime('%a %b %d')}{alert_tag} | {nifty_s}"
    send_report(india_html, india_subject)

    # 9. Send — US report
    spx_s = f"SPX {spx:,.0f}" if spx else "SPX —"
    us_subject = f"US Portfolio {datetime.utcnow().strftime('%a %b %d')} | {spx_s}"
    send_report(us_html, us_subject)

    print("  Done.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-email", action="store_true", help="Skip sending email; save HTML to logs/ instead")
    args = parser.parse_args()
    if args.no_email:
        _counter = [0]
        _labels  = ["india", "us"]
        def _save_only(html, subject):
            logs_dir = os.path.join(DATA_DIR, "..", "logs")
            os.makedirs(logs_dir, exist_ok=True)
            label = _labels[_counter[0]] if _counter[0] < len(_labels) else str(_counter[0])
            out = os.path.join(logs_dir, f"{label}_report_{date.today()}.html")
            with open(out, "w") as f:
                f.write(html)
            print(f"  Saved → {out}")
            _counter[0] += 1
            return True
        globals()["send_report"] = _save_only
    main()
