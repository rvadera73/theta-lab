"""
ICICI Direct Breeze API client.
Wraps breeze_connect and normalises responses for use by india_weekly_report.

Session token is daily — set BREEZE_SESSION_TOKEN each morning after logging in
at https://api.icicidirect.com/apiuser/login
"""

from datetime import date, datetime
from typing import Any


def _breeze_connect(api_key: str, api_secret: str, session_token: str):
    """Initialise and return an authenticated BreezeConnect instance."""
    from breeze_connect import BreezeConnect  # type: ignore

    breeze = BreezeConnect(api_key=api_key)
    breeze.generate_session(api_secret=api_secret, session_token=session_token)
    return breeze


def get_portfolio_positions(api_key: str, api_secret: str, session_token: str) -> list[dict]:
    """
    Returns all open positions from ICICI Direct.

    Each item in the returned list has at minimum:
        symbol        str   e.g. "RELIANCE", "NIFTY2561824500PE"
        exchange      str   "NSE" or "NFO"
        product_type  str   "cash", "futures", "options"
        quantity      int   net quantity (negative = short)
        avg_price     float average trade price
        market_value  float current market value of the position
        option_type   str   "CE" | "PE" | ""
        strike_price  str   strike as string (Breeze returns strings)
        expiry_date   str   "YYYY-MM-DD" (normalised from Breeze format)
    """
    breeze = _breeze_connect(api_key, api_secret, session_token)
    resp = breeze.get_portfolio_positions()

    if not isinstance(resp, dict) or resp.get("Status") != 200:
        return []

    raw_positions = resp.get("Success") or []
    positions = []

    for p in raw_positions:
        if not isinstance(p, dict):
            continue

        # Normalise expiry date — Breeze returns "29-May-2025" or "2025-05-29"
        expiry_raw = p.get("expiry_date", "") or ""
        expiry_date = _normalise_expiry(expiry_raw)

        positions.append({
            "symbol":       p.get("stock_code", ""),
            "exchange":     p.get("exchange_code", "NSE"),
            "product_type": p.get("product_type", "cash"),
            "quantity":     int(p.get("quantity", 0) or 0),
            "avg_price":    float(p.get("average_cost", 0) or 0),
            "market_value": float(p.get("market_value", 0) or 0),
            "option_type":  p.get("right", "") or "",       # "CE" | "PE" | ""
            "strike_price": str(p.get("strike_price", "") or ""),
            "expiry_date":  expiry_date,
            # Carry raw fields in case caller needs them
            "_raw": p,
        })

    return positions


def get_quotes(
    api_key: str,
    api_secret: str,
    session_token: str,
    symbols: list[str],
    exchange_code: str = "NSE",
) -> dict[str, float]:
    """
    Returns {symbol: last_price} for a list of NSE equity symbols.
    Use exchange_code='NFO' for options.
    """
    breeze = _breeze_connect(api_key, api_secret, session_token)
    prices: dict[str, float] = {}

    for symbol in symbols:
        try:
            resp = breeze.get_quotes(
                stock_code=symbol,
                exchange_code=exchange_code,
                product_type="cash",
                expiry_date="",
                right="",
                strike_price="",
            )
            if isinstance(resp, dict) and resp.get("Status") == 200:
                success = resp.get("Success") or []
                if success and isinstance(success, list):
                    last = success[0].get("ltp", 0) or success[0].get("last_trade_price", 0)
                    prices[symbol] = float(last or 0)
        except Exception:
            pass

    return prices


def get_option_quote(
    api_key: str,
    api_secret: str,
    session_token: str,
    symbol: str,
    expiry_date: str,
    right: str,
    strike_price: str,
) -> float:
    """
    Returns the last traded price for an NSE option leg.
    right: "CE" or "PE"
    expiry_date: "YYYY-MM-DD"
    """
    breeze = _breeze_connect(api_key, api_secret, session_token)
    try:
        resp = breeze.get_quotes(
            stock_code=symbol,
            exchange_code="NFO",
            product_type="options",
            expiry_date=expiry_date,
            right=right,
            strike_price=strike_price,
        )
        if isinstance(resp, dict) and resp.get("Status") == 200:
            success = resp.get("Success") or []
            if success and isinstance(success, list):
                last = success[0].get("ltp", 0) or success[0].get("last_trade_price", 0)
                return float(last or 0)
    except Exception:
        pass
    return 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise_expiry(raw: str) -> str:
    """Convert Breeze expiry formats to YYYY-MM-DD."""
    if not raw:
        return ""
    raw = raw.strip()
    # Already in ISO format
    if len(raw) == 10 and raw[4] == "-":
        return raw
    # "29-May-2025" or "29-MAY-2025"
    for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw
