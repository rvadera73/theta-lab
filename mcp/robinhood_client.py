"""
Robinhood client — thin wrapper around robin_stocks.
Sync (not async) — same pattern as breeze_client.py.

Authentication:
  Set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD in .env.
  On first login robin_stocks prompts for MFA via SMS/authenticator.
  After first login it stores a token in ~/.tokens/robinhood.pickle
  so subsequent calls are credential-free.

Usage:
  from robinhood_client import get_robinhood_positions
  equity, options = get_robinhood_positions()
"""

import os
from datetime import date
from typing import Any

_logged_in = False


def _ensure_login() -> bool:
    """Login once per process, reuse token on subsequent calls."""
    global _logged_in
    if _logged_in:
        return True
    username = os.getenv("ROBINHOOD_USERNAME", "")
    password = os.getenv("ROBINHOOD_PASSWORD", "")
    if not username or not password:
        return False
    try:
        import robin_stocks.robinhood as rh
        rh.login(
            username=username,
            password=password,
            store_session=True,
            pickle_name="robinhood",
            pickle_path=os.path.expanduser("~/.tokens/"),
        )
        _logged_in = True
        return True
    except Exception:
        return False


def _safe_float(val, default: float = 0.0) -> float:
    try:
        return float(val or default)
    except (TypeError, ValueError):
        return default


def _dte(expiry: str) -> int:
    try:
        return (date.fromisoformat(expiry) - date.today()).days
    except Exception:
        return 0


def get_equity_holdings() -> dict[str, dict[str, Any]]:
    """Returns {symbol: {price, quantity, average_buy_price}} from Robinhood."""
    if not _ensure_login():
        return {}
    try:
        import robin_stocks.robinhood as rh
        return rh.account.build_holdings() or {}
    except Exception:
        return {}


def get_option_positions() -> list[dict[str, Any]]:
    """
    Returns enriched option positions: each dict has strike, expiry, option_type,
    quantity (negative=short), premium_received, current_mark, underlying, dte.
    """
    if not _ensure_login():
        return []
    try:
        import robin_stocks.robinhood as rh
        raw = rh.options.get_open_option_positions() or []
        enriched = []
        for pos in raw:
            if not pos:
                continue
            qty = _safe_float(pos.get("quantity", 0))
            if qty == 0:
                continue

            # Fetch option instrument details (strike, expiry, type)
            option_url = pos.get("option", "")
            instrument = {}
            if option_url:
                try:
                    result = rh.helper.request_get(option_url)
                    if isinstance(result, dict):
                        instrument = result
                except Exception:
                    pass

            underlying = pos.get("chain_symbol", "")
            expiry = instrument.get("expiration_date", "")
            strike = _safe_float(instrument.get("strike_price", 0))
            option_type = instrument.get("type", "").upper()  # "CALL" or "PUT"
            if not option_type:
                option_type = pos.get("type", "").upper()

            # Average price is per-share premium (robin_stocks = per share, not per contract)
            avg_price_per_share = _safe_float(pos.get("average_price", 0))
            is_short = pos.get("type", "").lower() == "short"
            contracts = abs(int(qty))
            premium_received = avg_price_per_share * 100 * contracts if is_short else 0.0

            # Fetch current mark
            current_mark = 0.0
            if underlying and expiry and strike and option_type:
                try:
                    mkt = rh.options.get_option_market_data(
                        inputSymbols=underlying,
                        expirationDate=expiry,
                        strikePrice=str(int(strike)) if strike == int(strike) else str(strike),
                        optionType=option_type.lower(),
                    )
                    if mkt and isinstance(mkt, list) and mkt[0]:
                        mark = _safe_float(mkt[0][0].get("mark_price", 0) if isinstance(mkt[0], list) else mkt[0].get("mark_price", 0))
                        current_mark = mark * 100 * contracts
                except Exception:
                    pass

            enriched.append({
                "underlying": underlying,
                "option_type": option_type,
                "strike": strike,
                "expiry": expiry,
                "dte": _dte(expiry),
                "is_short": is_short,
                "contracts": contracts,
                "premium_received": premium_received,
                "current_mark": current_mark,
            })
        return enriched
    except Exception:
        return []


def get_robinhood_positions() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Returns (equity_holdings, enriched_option_positions).
    equity_holdings: {symbol: {price, quantity, average_buy_price, ...}}
    option_positions: list of enriched dicts (strike, expiry, option_type, etc.)
    """
    equity = get_equity_holdings()
    options = get_option_positions()
    return equity, options
