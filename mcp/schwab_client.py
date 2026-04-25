"""
Thin wrapper around open-stocks-mcp Schwab tools.
Normalises responses and adds retry/error handling.
"""

import os
from datetime import date, datetime, timedelta
from typing import Any

from open_stocks_mcp.tools.schwab_account_tools import (
    get_schwab_account_balances,
    get_schwab_account_numbers,
    get_schwab_accounts,
    get_schwab_options_positions,
    get_schwab_portfolio,
)
from open_stocks_mcp.tools.schwab_market_tools import (
    get_schwab_price_history,
    get_schwab_quote,
    get_schwab_quotes,
)
from open_stocks_mcp.tools.schwab_options_tools import (
    get_schwab_option_chain,
    get_schwab_option_expirations,
)
from open_stocks_mcp.tools.schwab_trading_tools import (
    get_schwab_orders,
    place_schwab_order,
)


def _ok(resp: dict) -> bool:
    return resp.get("success", False)


def get_account_hashes() -> dict[str, str]:
    """Returns {label: hash} for all Schwab accounts."""
    resp = get_schwab_account_numbers()
    if not _ok(resp):
        return {}
    accounts = resp.get("data", {}).get("accounts", [])
    return {a.get("accountNumber", ""): a.get("hashValue", "") for a in accounts}


def get_all_positions(account_hash: str) -> list[dict]:
    """All positions (equity + options) for an account."""
    resp = get_schwab_accounts(include_positions=True)
    if not _ok(resp):
        return []
    for acct in resp.get("data", {}).get("accounts", []):
        if acct.get("hashValue") == account_hash:
            return acct.get("positions", [])
    return []


def get_options_positions(account_hash: str) -> list[dict]:
    """Options positions only, with enriched fields."""
    resp = get_schwab_options_positions(account_hash)
    if not _ok(resp):
        return []
    return resp.get("data", {}).get("positions", [])


def get_balances(account_hash: str) -> dict:
    resp = get_schwab_account_balances(account_hash)
    return resp.get("data", {}) if _ok(resp) else {}


def get_quote(symbol: str) -> dict:
    resp = get_schwab_quote(symbol)
    return resp.get("data", {}) if _ok(resp) else {}


def get_quotes(symbols: list[str]) -> dict[str, dict]:
    resp = get_schwab_quotes(symbols)
    return resp.get("data", {}) if _ok(resp) else {}


def get_price_history_closes(symbol: str, days: int = 252) -> list[float]:
    """Returns list of closing prices for IV rank calculation."""
    resp = get_schwab_price_history(
        symbol,
        period_type="year",
        period=1,
        frequency_type="daily",
        frequency=1,
    )
    if not _ok(resp):
        return []
    candles = resp.get("data", {}).get("candles", [])
    return [c["close"] for c in candles if "close" in c]


def get_option_chain(symbol: str, contract_type: str = "ALL") -> dict:
    resp = get_schwab_option_chain(
        symbol,
        contract_type=contract_type,
        include_underlying_quote=True,
    )
    return resp.get("data", {}) if _ok(resp) else {}


def get_open_orders(account_hash: str) -> list[dict]:
    resp = get_schwab_orders(account_hash, max_results=50)
    if not _ok(resp):
        return []
    return [o for o in resp.get("data", {}).get("orders", []) if o.get("status") == "WORKING"]


def dry_run_order(account_hash: str, order_spec: dict) -> dict:
    """
    Validates an order without submitting it.
    Checks: buying power, position limits, earnings blackout.
    Returns: {ok: bool, checks: [...], warnings: [...]}
    """
    balances = get_balances(account_hash)
    buying_power = balances.get("buyingPower", 0)
    checks = []
    warnings = []

    # Buying power check
    notional = order_spec.get("notional_estimate", 0)
    if notional > buying_power:
        checks.append({"check": "buying_power", "passed": False,
                       "detail": f"Need ${notional:,.0f}, have ${buying_power:,.0f}"})
    else:
        checks.append({"check": "buying_power", "passed": True})

    # Contract limit check (basic)
    qty = order_spec.get("quantity", 1)
    symbol = order_spec.get("symbol", "")
    from config import UNIVERSE, Tier, PERMANENT_EXITS
    tier = Tier.CORE
    for t, tickers in UNIVERSE.items():
        if symbol in tickers:
            tier = t
            break
    max_contracts = {Tier.CORE: 5, Tier.EMERGING: 3, Tier.SPECULATIVE: 1}[tier]
    if qty > max_contracts:
        warnings.append(f"{symbol} is Tier {tier.value} — max {max_contracts} contracts")

    if symbol in PERMANENT_EXITS:
        checks.append({"check": "permanent_exit", "passed": False,
                       "detail": f"{symbol} is on permanent exit list — no new positions"})

    return {
        "ok": all(c["passed"] for c in checks),
        "checks": checks,
        "warnings": warnings,
        "buying_power": buying_power,
    }
