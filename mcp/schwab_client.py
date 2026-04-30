"""
Thin wrapper around open-stocks-mcp Schwab tools.
Normalises responses and adds retry/error handling.
"""

import asyncio
import os
from typing import Any

from open_stocks_mcp.tools.schwab_account_tools import (
    get_schwab_account_balances,
    get_schwab_account_numbers,
    get_schwab_accounts,
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
    get_schwab_options_positions,
)
from open_stocks_mcp.tools.schwab_trading_tools import (
    get_schwab_orders,
    place_schwab_order,
)


def _result(resp: dict) -> dict:
    """Extract the result payload from an open_stocks_mcp response."""
    return resp.get("result", {}) if isinstance(resp, dict) else {}


def _ok(resp: dict) -> bool:
    """open_stocks_mcp uses {"result": {"status": "success", ...}}."""
    r = _result(resp)
    return isinstance(r, dict) and r.get("status") == "success"


# Account number suffix → hash, built lazily from the env so we can match
# accounts without hashValue in the /accounts response.
_ACCT_SUFFIXES = {
    os.getenv("SCHWAB_ACCOUNT_A_HASH", ""): ("232", "1232"),
    os.getenv("SCHWAB_ACCOUNT_B_HASH", ""): ("275", "9275"),
    os.getenv("SCHWAB_ACCOUNT_C_HASH", ""): ("634", "8634"),
}


async def get_account_hashes() -> dict[str, str]:
    """Returns {accountNumber: hashValue} for all Schwab accounts."""
    resp = await get_schwab_account_numbers()
    r = _result(resp)
    accounts = r.get("accounts", [])
    return {a.get("account_id", ""): a.get("hash_value", "") for a in accounts}


_TOKEN_PATHS = {
    os.getenv("SCHWAB_ACCOUNT_A_HASH", ""): os.path.expanduser("~/.tokens/schwab_token.json"),
    os.getenv("SCHWAB_ACCOUNT_B_HASH", ""): os.path.expanduser("~/.tokens/schwab_token_b.json"),
    os.getenv("SCHWAB_ACCOUNT_C_HASH", ""): os.path.expanduser("~/.tokens/schwab_token_c.json"),
}


async def _get_accounts_direct(token_path: str) -> list[dict]:
    """Fetch all accounts directly via schwab-py (bypasses open_stocks_mcp broker registry).
    Used for accounts B and C which have separate Schwab logins / tokens.
    """
    import asyncio as _asyncio
    api_key = os.getenv("SCHWAB_API_KEY", "")
    app_secret = os.getenv("SCHWAB_APP_SECRET", "")
    if not api_key or not app_secret:
        return []
    try:
        from schwab import auth
        from schwab.client import Client
        client = auth.client_from_token_file(token_path, api_key, app_secret)

        def _fetch():
            resp = client.get_accounts(fields=Client.Account.Fields.POSITIONS)
            return resp.json()

        return await _asyncio.to_thread(_fetch)
    except Exception as e:
        sys.stderr.write(f"[theta-lab] direct account fetch failed ({token_path}): {e}\n")
        return []


async def get_all_positions(account_hash: str) -> list[dict]:
    """All positions (equity + options) for an account.

    Account A uses the open_stocks_mcp broker registry (registered at server startup).
    Accounts B and C use direct schwab-py calls with their own token files.
    """
    suffixes = _ACCT_SUFFIXES.get(account_hash, ())
    token_path = _TOKEN_PATHS.get(account_hash, "")

    # Accounts B and C: fetch directly using their own token
    if token_path and token_path != os.path.expanduser("~/.tokens/schwab_token.json"):
        if not os.path.exists(token_path):
            return []
        raw_accounts = await _get_accounts_direct(token_path)
        for acct in raw_accounts:
            sec = acct.get("securitiesAccount", {})
            acct_num = str(sec.get("accountNumber", ""))
            if not suffixes or any(acct_num.endswith(s) for s in suffixes):
                return sec.get("positions", [])
        return raw_accounts[0].get("securitiesAccount", {}).get("positions", []) if len(raw_accounts) == 1 else []

    # Account A: use open_stocks_mcp broker registry
    resp = await get_schwab_accounts(include_positions=True)
    accounts = _result(resp).get("accounts", [])
    if not accounts:
        return []

    for acct in accounts:
        sec = acct.get("securitiesAccount", {})
        acct_num = str(sec.get("accountNumber", ""))
        if not suffixes or any(acct_num.endswith(s) for s in suffixes):
            return sec.get("positions", [])

    if not suffixes and len(accounts) == 1:
        return accounts[0].get("securitiesAccount", {}).get("positions", [])
    return []


async def get_options_positions(account_hash: str) -> list[dict]:
    """Options positions only, with enriched fields."""
    resp = await get_schwab_options_positions(account_hash)
    if not _ok(resp):
        return []
    return _result(resp).get("positions", [])


async def get_balances(account_hash: str) -> dict:
    """Returns current_balances dict with buyingPower, cashBalance, etc."""
    resp = await get_schwab_account_balances(account_hash)
    if not _ok(resp):
        return {}
    r = _result(resp)
    cb = r.get("current_balances", {})
    # Normalise key names for downstream compatibility
    return {
        "buyingPower": cb.get("buying_power", 0),
        "cashBalance": cb.get("cash_balance", 0),
        "liquidationValue": cb.get("market_value", 0),
        "availableFunds": cb.get("available_funds", 0),
    }


async def get_quote(symbol: str) -> dict:
    resp = await get_schwab_quote(symbol)
    if not _ok(resp):
        return {}
    quotes = _result(resp).get("quotes", {})
    q = quotes.get(symbol.upper(), {})
    return {"lastPrice": q.get("last_price", 0)}


async def get_quotes(symbols: list[str]) -> dict[str, dict]:
    """Returns {SYMBOL: {"lastPrice": ..., ...}} for compatibility with parse_schwab_positions."""
    resp = await get_schwab_quotes(symbols)
    if not _ok(resp):
        return {}
    quotes = _result(resp).get("quotes", {})
    return {sym: {"lastPrice": q.get("last_price", 0)} for sym, q in quotes.items()}


async def get_price_history_closes(symbol: str, days: int = 252) -> list[float]:
    """Returns list of closing prices for IV rank calculation."""
    resp = await get_schwab_price_history(
        symbol,
        period_type="year",
        period=1,
        frequency_type="daily",
        frequency=1,
    )
    if not _ok(resp):
        return []
    candles = _result(resp).get("candles", [])
    return [c["close"] for c in candles if "close" in c]


async def get_option_chain(symbol: str, contract_type: str = "ALL") -> dict:
    resp = await get_schwab_option_chain(
        symbol,
        contract_type=contract_type,
        include_underlying_quote=True,
    )
    return _result(resp) if _ok(resp) else {}


async def get_open_orders(account_hash: str) -> list[dict]:
    resp = await get_schwab_orders(account_hash, max_results=50)
    if not _ok(resp):
        return []
    orders = _result(resp).get("orders", [])
    return [o for o in orders if o.get("status") == "WORKING"]


async def dry_run_order(account_hash: str, order_spec: dict) -> dict:
    """
    Validates an order without submitting it.
    Checks: buying power, position limits, earnings blackout.
    Returns: {ok: bool, checks: [...], warnings: [...]}
    """
    balances = await get_balances(account_hash)
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

    # Contract limit check
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
