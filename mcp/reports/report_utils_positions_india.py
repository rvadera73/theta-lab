"""
India (Breeze/ICICI) position-loading helpers split out of report_utils.py
(Bolt b19). report_utils.py re-exports everything here so every existing
`from report_utils import X` call site keeps working unchanged.
"""
import os
from datetime import date
from typing import Any

from analysis.india_statement_parser import build_positions_from_statements, load_india_config
from analysis.pnl import OptionLeg, Position


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
    from report_utils import current_price

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
