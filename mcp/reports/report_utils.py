import asyncio
import calendar
import csv
import math
import os
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import yaml

import yfinance as yf

from analysis.metrics import breakeven_velocity, premium_capture_rate, profit_factor, sortino_ratio
from analysis.pnl import OptionLeg, Position, parse_schwab_positions
from analysis.india_statement_parser import build_positions_from_statements, load_india_config
from config import PORTFOLIO, RISK
from routines.email_report import send_email

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
STATEMENTS_DIR = DATA_DIR / "statements"
LOGS_DIR = PROJECT_ROOT / "logs"
SNAPSHOT_FILE = DATA_DIR / "portfolio_snapshot.yaml"
TO_EMAIL = "ravjdpr@gmail.com"
FROM_EMAIL = "onboarding@resend.dev"

_ACCOUNT_FILES = {
    "A": "Individual_XXX232_Transactions_*.csv",
    "B": "Contributory_XXX275_Transactions_*.csv",
    "C": "Designated_XXX8634_Transactions_*.csv",
}

_INDIA_SYMBOL_MAP = {
    "ADAPOR": "ADANIPORTS.NS",
    "ADAPOW": "ADANIPOWER.NS",
    "ANARAJ": "ANANTRAJ.NS",
    "APOHOS": "APOLLOHOSP.NS",
    "BAJFI": "BAJFINANCE.NS",
    "BHAELE": "BEL.NS",
    "DIXTEC": "DIXON.NS",
    "DLFLIM": "DLF.NS",
    "DRREDD": "DRREDDY.NS",
    "GENOVE": "GENUSPOWER.NS",
    "HCLTEC": "HCLTECH.NS",
    "HDFBAN": "HDFCBANK.NS",
    "HERHON": "HEROMOTOCO.NS",
    "HINAER": "HAL.NS",
    "LIC": "LICI.NS",
    "MAZDOC": "MAZDOCK.NS",
    "NTPC": "NTPC.NS",
    "RELIND": "RELIANCE.NS",
    "STABAN": "SBIN.NS",
    "SUZENE": "SUZLON.NS",
    "TCS": "TCS.NS",
    "YATHOS": "YATHARTH.NS",
    "ZOMLIM": "ETERNAL.NS",
}

_US_PRICE_CACHE: dict[str, dict[str, Any]] = {}
_INDIA_PRICE_CACHE: dict[str, dict[str, Any]] = {}
_OPTION_CHAIN_CACHE: dict[tuple[str, str], Any] = {}
_EARNINGS_CACHE: dict[str, list[str]] = {}


def ensure_logs_dir() -> Path:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR


def load_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_FILE.exists():
        return {}
    with SNAPSHOT_FILE.open() as f:
        return yaml.safe_load(f) or {}


def latest_file(pattern: str) -> Path | None:
    matches = sorted(STATEMENTS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def load_account_transactions() -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for account, pattern in _ACCOUNT_FILES.items():
        path = latest_file(pattern)
        if not path:
            result[account] = []
            continue
        with path.open(newline="", encoding="utf-8-sig") as f:
            result[account] = list(csv.DictReader(f))
    return result


def parse_amount(raw: Any) -> float:
    text = str(raw or "").replace("$", "").replace(",", "").strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def parse_qty(raw: Any) -> int:
    text = str(raw or "0").replace(",", "").replace('"', '').strip()
    try:
        return int(float(text))
    except ValueError:
        return 0


def parse_txn_date(raw: str) -> date | None:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(raw).strip(), fmt).date()
        except Exception:
            continue
    return None


def month_window(target: date) -> tuple[date, date]:
    first = target.replace(day=1)
    last = target.replace(day=calendar.monthrange(target.year, target.month)[1])
    return first, last


def previous_month(target: date) -> date:
    prev = target.replace(day=1) - timedelta(days=1)
    return prev.replace(day=1)


def month_name(target: date) -> str:
    return target.strftime("%B %Y")


def month_days(target: date) -> int:
    return calendar.monthrange(target.year, target.month)[1]


def project_value(current_value: float, as_of: date) -> float:
    elapsed = max(1, as_of.day)
    return current_value / elapsed * month_days(as_of)


def fmt_money(value: Any) -> str:
    try:
        num = float(value)
    except Exception:
        return "—"
    return f"${num:,.0f}"


def fmt_inr(value: Any) -> str:
    try:
        num = float(value)
    except Exception:
        return "—"
    return f"₹{num:,.0f}"


def safe_div(n: float, d: float) -> float:
    return n / d if d else 0.0


def compute_rsi(prices, period: int = 14) -> float | None:
    try:
        delta = prices.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, math.nan)
        value = (100 - (100 / (1 + rs))).iloc[-1]
        return round(float(value), 1) if value == value else None
    except Exception:
        return None


def yf_symbol(symbol: str, india: bool = False) -> str:
    if not india:
        return symbol
    if symbol in _INDIA_SYMBOL_MAP:
        return _INDIA_SYMBOL_MAP[symbol]
    if symbol.startswith("^") or symbol.endswith(".NS"):
        return symbol
    return f"{symbol}.NS"


def _history_cache(symbol: str, india: bool = False):
    cache = _INDIA_PRICE_CACHE if india else _US_PRICE_CACHE
    key = yf_symbol(symbol, india)
    if key in cache:
        return cache[key]
    try:
        ticker = yf.Ticker(key)
        hist = ticker.history(period="1y", auto_adjust=False)
        cache[key] = {"ticker": ticker, "hist": hist}
    except Exception:
        cache[key] = {"ticker": None, "hist": None}
    return cache[key]


def current_price(symbol: str, india: bool = False) -> float:
    payload = _history_cache(symbol, india)
    hist = payload.get("hist")
    try:
        if hist is not None and not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return 0.0


def technical_snapshot(symbol: str, india: bool = False) -> dict[str, Any]:
    payload = _history_cache(symbol, india)
    hist = payload.get("hist")
    ticker = payload.get("ticker")
    if hist is None or getattr(hist, "empty", True):
        return {
            "symbol": symbol,
            "current": 0.0,
            "rsi": None,
            "ma50": None,
            "ma200": None,
            "above_50": None,
            "above_200": None,
            "week_52_high": None,
            "week_52_low": None,
            "pct_off_high": None,
            "pe": None,
        }
    close = hist["Close"]
    current = float(close.iloc[-1])
    ma50 = float(close.tail(50).mean()) if len(close) >= 50 else None
    ma200 = float(close.tail(200).mean()) if len(close) >= 200 else None
    week_52_high = float(close.max()) if len(close) else None
    week_52_low = float(close.min()) if len(close) else None
    pe = None
    if india:
        try:
            info = ticker.info if ticker else {}
            pe = info.get("trailingPE") or info.get("forwardPE")
        except Exception:
            pe = None
    return {
        "symbol": symbol,
        "current": current,
        "rsi": compute_rsi(close, 14),
        "ma50": round(ma50, 2) if ma50 else None,
        "ma200": round(ma200, 2) if ma200 else None,
        "above_50": current > ma50 if ma50 else None,
        "above_200": current > ma200 if ma200 else None,
        "week_52_high": round(week_52_high, 2) if week_52_high else None,
        "week_52_low": round(week_52_low, 2) if week_52_low else None,
        "pct_off_high": round((current - week_52_high) / week_52_high * 100, 1) if week_52_high else None,
        "pe": round(float(pe), 2) if pe else None,
    }


def upcoming_earnings(symbol: str, days: int = 14) -> list[str]:
    if symbol in _EARNINGS_CACHE:
        return _EARNINGS_CACHE[symbol]
    found: list[str] = []
    try:
        cal = yf.Ticker(symbol).calendar
        if hasattr(cal, "index"):
            if "Earnings Date" in getattr(cal, "index", []):
                values = cal.loc["Earnings Date"]
                for value in values if hasattr(values, "tolist") else [values]:
                    dt = getattr(value, "to_pydatetime", lambda: value)()
                    if isinstance(dt, datetime):
                        found.append(dt.date().isoformat())
            elif hasattr(cal, "columns") and "Earnings Date" in cal.columns:
                for value in cal["Earnings Date"].tolist():
                    if value is not None:
                        dt = getattr(value, "to_pydatetime", lambda: value)()
                        if isinstance(dt, datetime):
                            found.append(dt.date().isoformat())
        elif isinstance(cal, dict):
            values = cal.get("Earnings Date") or []
            for value in values if isinstance(values, list) else [values]:
                if hasattr(value, "date"):
                    found.append(value.date().isoformat())
    except Exception:
        pass
    cutoff = date.today() + timedelta(days=days)
    filtered = []
    for raw in found:
        try:
            dt = date.fromisoformat(raw)
            if date.today() <= dt <= cutoff:
                filtered.append(raw)
        except Exception:
            continue
    _EARNINGS_CACHE[symbol] = filtered
    return filtered


def option_market_price(symbol: str, expiry: str, strike: float, option_type: str) -> float | None:
    key = (symbol, expiry)
    chain = _OPTION_CHAIN_CACHE.get(key)
    if chain is None:
        try:
            chain = yf.Ticker(symbol).option_chain(expiry)
        except Exception:
            chain = None
        _OPTION_CHAIN_CACHE[key] = chain
    if chain is None:
        return None
    try:
        table = chain.calls if option_type == "CALL" else chain.puts
        if table is None or table.empty:
            return None
        row = table.loc[(table["strike"] - float(strike)).abs().idxmin()]
        if abs(float(row["strike"]) - float(strike)) > 0.01:
            return None
        bid = float(row.get("bid", 0) or 0)
        ask = float(row.get("ask", 0) or 0)
        last = float(row.get("lastPrice", 0) or 0)
        if bid and ask:
            return round((bid + ask) / 2, 2)
        return round(last, 2) if last else None
    except Exception:
        return None


def parse_option_symbol(symbol: str) -> dict[str, Any] | None:
    import re

    match = re.match(r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$", str(symbol).strip())
    if not match:
        return None
    return {
        "symbol": match.group(1),
        "expiry": datetime.strptime(match.group(2), "%m/%d/%Y").date().isoformat(),
        "strike": float(match.group(3)),
        "option_type": "CALL" if match.group(4) == "C" else "PUT",
    }


def reconstruct_open_option_legs(rows: list[dict[str, str]], account: str) -> list[dict[str, Any]]:
    book: dict[tuple[str, str, float, str], dict[str, Any]] = {}
    for row in rows:
        parsed = parse_option_symbol(row.get("Symbol", ""))
        if not parsed:
            continue
        qty = max(1, parse_qty(row.get("Quantity", 1)))
        action = str(row.get("Action", "")).strip()
        amount = parse_amount(row.get("Amount", 0))
        txn_date = parse_txn_date(row.get("Date", "")) or date.today()
        key = (parsed["symbol"], parsed["expiry"], parsed["strike"], parsed["option_type"])
        item = book.setdefault(key, {
            **parsed,
            "contracts": 0,
            "net_credit": 0.0,
            "opened": None,
            "account": account,
        })
        if "Sell to Open" in action:
            item["contracts"] += qty
            item["net_credit"] += max(0.0, amount)
            item["opened"] = min(item["opened"], txn_date) if item["opened"] else txn_date
        elif action == "Buy to Close":
            item["contracts"] = max(0, item["contracts"] - qty)
            item["net_credit"] -= abs(amount)
        elif action in ("Assigned", "Expired", "Exercise"):
            item["contracts"] = 0
    open_legs = []
    for item in book.values():
        if item["contracts"] <= 0:
            continue
        dte = (date.fromisoformat(item["expiry"]) - date.today()).days
        underlying = current_price(item["symbol"])
        mark = option_market_price(item["symbol"], item["expiry"], item["strike"], item["option_type"])
        item.update({
            "dte": dte,
            "underlying_price": underlying,
            "mark": (mark or 0.0) * 100 * item["contracts"],
            "premium_received": item["net_credit"],
            "moneyness_pct": round(((underlying - item["strike"]) / underlying * 100), 1) if underlying else None,
        })
        open_legs.append(item)
    return sorted(open_legs, key=lambda x: (x["dte"], x["symbol"]))


def load_position_csv() -> list[dict[str, Any]]:
    path = latest_file("Individual-Positions*.csv")
    if not path:
        return []
    positions: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()
    header_idx = next((i for i, line in enumerate(lines) if "\"Symbol\"" in line and "Asset Type" in line), None)
    if header_idx is None:
        return []
    for row in csv.DictReader(lines[header_idx:]):
        symbol = str(row.get("Symbol", "")).strip().strip('"')
        if not symbol:
            continue
        positions.append({
            "symbol": symbol,
            "qty": parse_qty(row.get("Qty (Quantity)", 0)),
            "price": parse_amount(row.get("Price", 0)),
            "market_value": parse_amount(row.get("Mkt Val (Market Value)", 0)),
            "cost_basis_total": parse_amount(row.get("Cost Basis", 0)),
            "asset_type": str(row.get("Asset Type", "")).strip().strip('"'),
        })
    return positions


def fallback_us_positions() -> dict[str, Any]:
    snapshot = load_snapshot()
    txns = load_account_transactions()
    pos_rows = load_position_csv()
    price_map = {row["symbol"]: row["price"] for row in pos_rows if row.get("asset_type", "").lower() == "equity"}
    cost_map = {
        row["symbol"]: safe_div(row["cost_basis_total"], row["qty"])
        for row in pos_rows if row.get("asset_type", "").lower() == "equity" and row.get("qty")
    }
    positions: dict[tuple[str, str], Position] = {}
    for item in snapshot.get("assigned_positions", []):
        symbol = item.get("symbol")
        if not symbol:
            continue
        raw_account = str(item.get("account", "A"))
        if "8634" in raw_account or "634" in raw_account or raw_account.strip().upper() == "C":
            account = "C"
        elif "275" in raw_account or raw_account.strip().upper() == "B":
            account = "B"
        else:
            account = "A"
        positions[(account, symbol)] = Position(
            symbol=symbol,
            account=account,
            shares=int(item.get("shares", 0) or 0),
            stock_cost_basis=float(cost_map.get(symbol) or item.get("cost_basis", 0) or 0),
            current_price=float(price_map.get(symbol) or current_price(symbol) or item.get("cost_basis", 0) or 0),
        )
        positions[(account, symbol)]._snapshot_meta = item
    for account, rows in txns.items():
        for leg in reconstruct_open_option_legs(rows, account):
            pos = positions.get((account, leg["symbol"]))
            if not pos:
                pos = Position(
                    symbol=leg["symbol"],
                    account=account,
                    shares=0,
                    stock_cost_basis=0.0,
                    current_price=float(leg.get("underlying_price") or current_price(leg["symbol"]) or 0),
                )
                positions[(account, leg["symbol"])] = pos
            pos.option_legs.append(OptionLeg(
                description=f"{leg['option_type']} {leg['strike']} {leg['expiry']}",
                strike=float(leg["strike"]),
                expiry=leg["expiry"],
                option_type=leg["option_type"],
                quantity=-int(leg["contracts"]),
                premium_received=float(leg["premium_received"]),
                current_mark=float(leg["mark"]),
                dte=int(leg["dte"]),
            ))
            pos.current_price = float(leg.get("underlying_price") or pos.current_price)
    return {
        "positions": list(positions.values()),
        "balances": {"A": {}, "B": {}, "C": {}},
        "data_source": "SNAPSHOT (LIVE API UNAVAILABLE)",
        "warning": f"Using snapshot dated {snapshot.get('last_updated', 'unknown')} plus statement fallbacks.",
        "snapshot": snapshot,
        "transactions": txns,
    }


async def load_us_positions() -> dict[str, Any]:
    account_a_hash = os.getenv("SCHWAB_ACCOUNT_A_HASH", "")
    account_b_hash = os.getenv("SCHWAB_ACCOUNT_B_HASH", "")
    account_c_hash = os.getenv("SCHWAB_ACCOUNT_C_HASH", "")
    try:
        if not account_a_hash and not account_b_hash and not account_c_hash:
            raise RuntimeError("Schwab account hashes not configured")
        from schwab_client import get_all_positions, get_quotes, get_balances

        all_positions: list[Position] = []
        balances: dict[str, dict[str, Any]] = {}
        for acct_hash, label in ((account_a_hash, "A"), (account_b_hash, "B"), (account_c_hash, "C")):
            if not acct_hash:
                continue
            raw = await get_all_positions(acct_hash)
            if not raw:
                continue
            symbols = sorted({
                (p.get("instrument", {}).get("underlyingSymbol") or p.get("instrument", {}).get("symbol", "").split()[0])
                for p in raw
                if p.get("instrument", {}).get("assetType") in ("EQUITY", "OPTION")
            })
            quotes = await get_quotes(symbols)
            balances[label] = await get_balances(acct_hash)
            all_positions.extend(parse_schwab_positions(raw, label, quotes))
        if not all_positions:
            raise RuntimeError("No live positions returned")
        return {
            "positions": all_positions,
            "balances": balances,
            "data_source": "LIVE",
            "warning": None,
            "snapshot": load_snapshot(),
            "transactions": load_account_transactions(),
        }
    except Exception:
        return fallback_us_positions()


def _dte_from_expiry(expiry: str) -> int:
    try:
        return (date.fromisoformat(expiry) - date.today()).days
    except Exception:
        return 0


def _map_breeze_to_positions(raw_positions: list[dict]) -> list[Position]:
    equity_map: dict[str, Position] = {}
    option_legs: dict[str, list[OptionLeg]] = {}
    for pos in raw_positions:
        symbol = str(pos.get("symbol", "")).strip()
        if not symbol:
            continue
        exchange = str(pos.get("exchange", "NSE")).upper()
        product = str(pos.get("product_type", "")).lower()
        qty = int(pos.get("quantity", 0) or 0)
        avg_price = float(pos.get("avg_price", 0) or 0)
        market_value = float(pos.get("market_value", 0) or 0)
        last_price = float(pos.get("ltp", 0) or 0)
        current_px = last_price or (market_value / qty if qty else avg_price)
        if exchange == "NSE" and product in ("cash", ""):
            equity_map[symbol] = Position(symbol=symbol, account="INDIA", shares=qty, stock_cost_basis=avg_price, current_price=current_px)
        elif product == "options":
            option_type = "CALL" if str(pos.get("option_type", "")).upper() == "CE" else "PUT"
            strike = float(pos.get("strike_price", 0) or 0)
            expiry = str(pos.get("expiry_date", "") or "")
            dte = _dte_from_expiry(expiry)
            is_short = qty < 0
            abs_qty = abs(qty)
            premium = avg_price * abs_qty if is_short else 0.0
            mark = current_px * abs_qty if is_short else 0.0
            underlying = pos.get("_raw", {}).get("stock_code") or symbol
            option_legs.setdefault(underlying, []).append(
                OptionLeg(
                    description=f"{option_type} {strike} {expiry}",
                    strike=strike,
                    expiry=expiry,
                    option_type=option_type,
                    quantity=qty,
                    premium_received=premium,
                    current_mark=mark,
                    dte=dte,
                )
            )
    for underlying, legs in option_legs.items():
        if underlying not in equity_map:
            equity_map[underlying] = Position(symbol=underlying, account="INDIA", shares=0, stock_cost_basis=0.0, current_price=0.0)
        equity_map[underlying].option_legs.extend(legs)
    return list(equity_map.values())


def _map_breeze_equity_holdings(raw_holdings: list[dict]) -> list[Position]:
    positions: list[Position] = []
    india_cfg = load_india_config()
    core = set(india_cfg.get("core_portfolio", []))
    exits = {item["icici_symbol"]: item for item in india_cfg.get("exit_triggers", []) if "icici_symbol" in item}
    for holding in raw_holdings:
        symbol = holding.get("symbol", "")
        if not symbol:
            continue
        pos = Position(
            symbol=symbol,
            account="INDIA",
            shares=int(holding.get("quantity", 0) or 0),
            stock_cost_basis=float(holding.get("avg_price", 0) or 0),
            current_price=float(holding.get("ltp", 0) or holding.get("avg_price", 0) or 0),
        )
        pos._is_core = symbol in core
        pos._exit_trigger = exits.get(symbol)
        positions.append(pos)
    return positions


def load_india_positions() -> dict[str, Any]:
    api_key = os.getenv("BREEZE_API_KEY", "")
    api_secret = os.getenv("BREEZE_API_SECRET", "")
    session_token = os.getenv("BREEZE_SESSION_TOKEN", "")
    try:
        if not (api_key and api_secret and session_token):
            raise RuntimeError("Breeze credentials missing")
        from breeze_client import get_demat_holdings, get_portfolio_positions
        holdings = get_demat_holdings(api_key, api_secret, session_token)
        fno = get_portfolio_positions(api_key, api_secret, session_token)
        if not holdings and not fno:
            raise RuntimeError("No live India data")
        equity_positions = {p.symbol: p for p in _map_breeze_equity_holdings(holdings)}
        for pos in _map_breeze_to_positions(fno):
            if pos.symbol in equity_positions:
                equity_positions[pos.symbol].option_legs.extend(pos.option_legs)
            else:
                equity_positions[pos.symbol] = pos
        return {
            "positions": list(equity_positions.values()),
            "data_source": "LIVE",
            "warning": None,
            "config": load_india_config(),
        }
    except Exception:
        positions = build_positions_from_statements(load_india_config())
        for pos in positions:
            if pos.shares > 0:
                live = current_price(pos.symbol, india=True)
                if live:
                    pos.current_price = live
        return {
            "positions": positions,
            "data_source": "SNAPSHOT (LIVE API UNAVAILABLE)",
            "warning": "Using India statement/config fallback data.",
            "config": load_india_config(),
        }


def monthly_premium(rows: list[dict[str, str]], month_start: date) -> float:
    total = 0.0
    for row in rows:
        txn_date = parse_txn_date(row.get("Date", ""))
        if not txn_date or txn_date.year != month_start.year or txn_date.month != month_start.month:
            continue
        parsed = parse_option_symbol(row.get("Symbol", ""))
        if not parsed:
            continue
        action = str(row.get("Action", "")).strip()
        amount = parse_amount(row.get("Amount", 0))
        if "Sell to Open" in action and amount > 0:
            total += amount
        elif action == "Buy to Close" and amount < 0:
            total -= abs(amount)
    return round(total, 2)


def monthly_option_pnl_series(rows: list[dict[str, str]]) -> list[float]:
    monthly: defaultdict[tuple[int, int], float] = defaultdict(float)
    for row in rows:
        txn_date = parse_txn_date(row.get("Date", ""))
        if not txn_date:
            continue
        parsed = parse_option_symbol(row.get("Symbol", ""))
        if not parsed:
            continue
        action = str(row.get("Action", "")).strip()
        amount = parse_amount(row.get("Amount", 0))
        key = (txn_date.year, txn_date.month)
        if "Sell to Open" in action and amount > 0:
            monthly[key] += amount
        elif action == "Buy to Close" and amount < 0:
            monthly[key] -= abs(amount)
    return [monthly[key] for key in sorted(monthly)]


def combined_kpis(txns: dict[str, list[dict[str, str]]], snapshot: dict[str, Any]) -> dict[str, Any]:
    all_rows = [row for rows in txns.values() for row in rows]
    capture = premium_capture_rate(all_rows) if all_rows else {"capture_rate": snapshot.get("ytd_premium_capture_rate"), "signal": "WATCH"}
    pf = profit_factor(all_rows) if all_rows else {"profit_factor": snapshot.get("ytd_profit_factor"), "win_rate": None, "signal": "WATCH"}
    monthly_series = monthly_option_pnl_series(all_rows)
    sortino = sortino_ratio(monthly_series) if len(monthly_series) >= 3 else {"sortino_annualized": None, "signal": "WATCH"}
    return {"capture": capture, "profit_factor": pf, "sortino": sortino}


def save_html(prefix: str, html: str, report_day: date | None = None) -> Path:
    ensure_logs_dir()
    report_day = report_day or date.today()
    path = LOGS_DIR / f"{prefix}_{report_day.isoformat()}.html"
    path.write_text(html, encoding="utf-8")
    return path


def maybe_send(subject: str, html: str) -> dict[str, Any]:
    api_key = os.getenv("RESEND_API_KEY", "")
    if not api_key:
        return {"success": False, "error": "RESEND_API_KEY not set"}
    return send_email(
        to_email=TO_EMAIL,
        subject=subject,
        html_body=html,
        from_email=FROM_EMAIL,
        api_key=api_key,
    )


def priority_from_position(position: Position, regime: str) -> tuple[int, str, str]:
    roll = position.roll_signal()
    loss = position.loss_flag()
    profit = position.profit_take_signal(regime)
    if loss.get("flag"):
        return 1, "URGENT", f"Mark {loss.get('multiplier')}x premium received"
    if any(leg.dte <= RISK["roll_dte_threshold"] for leg in position.option_legs):
        return 2, "URGENT", "At or inside 21 DTE"
    if profit.get("signal"):
        return 2, "STRONG", f"{profit.get('pct_captured')}% premium captured"
    if position.symbol in ("PYPL", "MRNA"):
        return 2, "WATCH", "Permanent exit: accelerate covered call exit"
    return 5, "WATCH", "No immediate action"


def action_for_option_leg(underlying: float, strike: float, option_type: str, dte: int) -> str:
    if dte <= 21:
        return "ROLL / CLOSE"
    if option_type == "PUT" and underlying and underlying < strike:
        return "DEFEND / ROLL"
    if option_type == "CALL" and underlying and underlying > strike:
        return "MANAGE ITM CALL"
    return "HOLD"


def estimate_delta(underlying: float, strike: float, option_type: str) -> float | None:
    if not underlying or not strike:
        return None
    moneyness = strike / underlying
    if option_type == "PUT":
        if moneyness >= 1.05:
            return -0.65
        if moneyness >= 1.0:
            return -0.55
        if moneyness >= 0.95:
            return -0.35
        return -0.2
    if moneyness <= 0.95:
        return 0.65
    if moneyness <= 1.0:
        return 0.55
    if moneyness <= 1.05:
        return 0.35
    return 0.2
