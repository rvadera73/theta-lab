"""
Theta-Lab MCP Server
Exposes trading analysis tools to Claude via Model Context Protocol.
Wraps open-stocks-mcp Schwab tools + adds persona-aware analysis layer.

Start: python mcp/server.py
"""

import argparse
import asyncio
import json
import os
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any

import yfinance as yf

# Load .env from project root before anything else
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        # Fallback: parse .env manually
        with open(_env_file) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _, _v = _line.partition("=")
                    os.environ.setdefault(_k.strip(), _v.strip())

# Bootstrap credentials from ~/.claude.json (fills gaps if .env is incomplete)
from bootstrap import load_credentials as _load_credentials

_load_credentials()

# Add mcp dir to path so relative imports work
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

from config import ACCOUNT_A, ACCOUNT_B, ACCOUNTS, UNIVERSE, Tier, PERMANENT_EXITS, RISK
from analysis.iv_rank import get_iv_rank, batch_iv_rank
from analysis.regime import detect_regime
from analysis.india_regime import detect_india_regime
from analysis.flags_engine import (
    check_flags_live,
    get_flag_status,
    review_all_stale as review_all_stale_flags,
    update_flag as update_live_flag,
)
from analysis.strategy_engine import WARN_FLAGS, check_flags, recommend_trade
from models.vix_regime import entry_timing_score
from reports.dynamic_screener import screen_india_opportunities, screen_us_opportunities
from reports.report_utils import technical_snapshot, upcoming_earnings, yf_symbol
from reports.screener_universe import INDIA_UNIVERSE, QUALITY_FLAGS_BY_SYMBOL, US_UNIVERSE
from reports.weekly_report import generate_weekly_report
from reports.india_weekly_report import generate_india_weekly_report
from reports.weekly_combined_report import generate_weekly_combined_report
from reports.bimonthly_technical_report import generate_bimonthly_technical_report
from reports.monthly_objectives_report import generate_monthly_objectives_report
from reports.unified_master_report import generate_unified_master_report

# Derived from ACCOUNTS registry — do not hardcode per-account vars here
ACCOUNT_A_HASH = os.getenv("SCHWAB_ACCOUNT_A_HASH", "")  # kept for backward compat
ACCOUNT_B_HASH = os.getenv("SCHWAB_ACCOUNT_B_HASH", "")
ACCOUNT_C_HASH = os.getenv("SCHWAB_ACCOUNT_C_HASH", "")
RH_USERNAME = os.getenv("ROBINHOOD_USERNAME", "")
RH_PASSWORD = os.getenv("ROBINHOOD_PASSWORD", "")

# ── Startup credential audit ──────────────────────────────────────────────────
def _audit_credentials() -> None:
    """Log which credentials are present at startup. Never prints values."""
    import logging
    _log = logging.getLogger("theta-lab")
    required = {
        "SCHWAB_API_KEY": os.getenv("SCHWAB_API_KEY", ""),
        "SCHWAB_APP_SECRET": os.getenv("SCHWAB_APP_SECRET", ""),
        "SCHWAB_ACCOUNT_A_HASH": ACCOUNT_A_HASH,
        "SCHWAB_ACCOUNT_B_HASH": ACCOUNT_B_HASH,
    }
    optional = {
        "SCHWAB_ACCOUNT_C_HASH": ACCOUNT_C_HASH,
        "ROBINHOOD_USERNAME": RH_USERNAME,
        "BREEZE_API_KEY": os.getenv("BREEZE_API_KEY", ""),
        "BREEZE_SESSION_TOKEN": os.getenv("BREEZE_SESSION_TOKEN", ""),
    }
    missing = [k for k, v in required.items() if not v]
    present = [k for k, v in required.items() if v]
    _log.info("[theta-lab] ── Credential audit ──────────────────────")
    for k in present:
        _log.info(f"[theta-lab]   ✅ {k} = ***loaded***")
    for k in missing:
        _log.warning(f"[theta-lab]   ❌ {k} = MISSING — live Schwab tools will fail")
    for k, v in optional.items():
        status = "✅ loaded" if v else "⚠️  not set"
        _log.info(f"[theta-lab]   {status}: {k}")
    if missing:
        _log.warning(
            "[theta-lab] Fix: add missing vars to ~/.claude.json "
            "(mcpServers.theta-lab.env) or project .env, then restart."
        )
    else:
        _log.info("[theta-lab] ✅ All required credentials present — live tools enabled")
    _log.info("[theta-lab] ────────────────────────────────────────────")

_audit_credentials()
# ─────────────────────────────────────────────────────────────────────────────


def _get_configured_accounts() -> dict[str, dict]:
    """
    Returns all accounts from the ACCOUNTS registry.

    Data/auth policy: analysis is FILE-based (exported CSVs + Yahoo), so every
    account is always 'configured' — no Schwab/Robinhood credentials required to
    run analysis tools. (The live broker API has been removed.)
    """
    return {label: {**cfg} for label, cfg in ACCOUNTS.items()}


def _account_hash_map() -> dict[str, str]:
    """Legacy shim — returns Schwab hashes only. Use _get_configured_accounts() for new code."""
    configured = _get_configured_accounts()
    return {k: v["hash"] for k, v in configured.items() if v.get("broker") == "schwab" and "hash" in v}


def _target_accounts(account: str) -> list[tuple[str, str]]:
    """Legacy shim for Schwab-only callers (get_live_positions, get_account_summary)."""
    hashes = _account_hash_map()
    if account == "all":
        return list(hashes.items())
    return [(account, hashes.get(account, ""))]


async def _load_positions_all(account_filter: str = "all") -> list:
    """
    Delegates to load_us_positions() — the single canonical position loader.
    account_filter: "all" | "both" (A+B only) | specific label e.g. "A", "F1"
    To add a new broker: update config.ACCOUNTS + load_us_positions() only.
    """
    from reports.report_utils import load_us_positions
    us_data = await load_us_positions()
    positions = us_data.get("positions", [])

    if account_filter == "all":
        return positions
    elif account_filter == "both":
        return [p for p in positions if p.account in ("A", "B")]
    else:
        return [p for p in positions if p.account == account_filter]


def _position_action(position, regime: str) -> str:
    if position.symbol in PERMANENT_EXITS:
        return "Accelerate permanent exit"
    if position.loss_flag().get("flag"):
        return "Review / defend loss"
    roll_signal = position.roll_signal()
    if roll_signal.get("signal"):
        return roll_signal.get("recommendation", "Roll")
    profit_signal = position.profit_take_signal(regime)
    if profit_signal.get("signal"):
        return profit_signal.get("recommendation", "Take profit")
    if position.shares > 0 and not position.option_legs:
        return "Covered-call candidate / hold shares"
    return "Hold / monitor"


US_SECTOR_CHOICES = [
    "Energy",
    "Defense & Aerospace",
    "Nuclear & Clean Energy",
    "AI Infrastructure & Data Center",
    "Cybersecurity",
    "Financials",
    "Industrials & Infrastructure",
    "Healthcare & Biotech",
    "Consumer & Retail",
    "Tech",
]

_SYMBOL_META = {item["symbol"]: item for item in [*US_UNIVERSE, *INDIA_UNIVERSE]}


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


async def _run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(func, *args))


def _tier_label(tier: Any) -> str:
    try:
        return f"Tier {int(tier)}"
    except (TypeError, ValueError):
        return "Tier ?"


def _signal_display(signal: str) -> tuple[str, str]:
    normalized = (signal or "SKIP").upper().replace("_", " ")
    emoji = {
        "ENTER NOW": "🟢",
        "WATCH": "🟡",
        "SKIP": "🔴",
    }.get(normalized, "⚪")
    return emoji, normalized


def _normalized_iv_decimal(current_iv: Any, iv_rank: float | None = None) -> float:
    iv_value = _safe_float(current_iv)
    if iv_value is not None:
        return iv_value / 100.0 if iv_value > 1.5 else iv_value
    if iv_rank is not None:
        return max(0.12, min(1.20, (iv_rank / 100.0) * 0.5))
    return 0.25


def _strategy_regime_label(regime: str) -> str:
    labels = {
        "BEAR_SIDEWAYS": "Bear regime",
        "RISKY_BULL": "Risky bull regime",
        "TRANSITIONING": "Transitioning regime",
        "BULL": "Bull regime",
    }
    return labels.get(regime, regime.replace("_", " ").title())


def _format_price(value: Any, decimals: int = 0, prefix: str = "$", suffix: str = "") -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "n/a"
    return f"{prefix}{numeric:.{decimals}f}{suffix}"


def _format_contract_premium(value: Any) -> str:
    numeric = _safe_float(value)
    return f"~${numeric:.0f}/contract" if numeric is not None else "premium n/a"


def _format_monthly_yield(value: Any) -> str:
    numeric = _safe_float(value)
    return f"{numeric:.2f}%/mo on capital" if numeric is not None else "yield n/a"


def _format_strategy_line(trade: dict[str, Any]) -> str:
    strategy = trade.get("strategy", "WAIT")
    dte = trade.get("dte", "n/a")
    account = trade.get("account", "A")
    put_strike = _safe_float(trade.get("strike_put"))
    call_strike = _safe_float(trade.get("strike_call"))

    if strategy == "CC" and call_strike is not None:
        structure = f"CC ${call_strike:.0f}C / {dte} DTE"
    elif strategy == "STRANGLE" and put_strike is not None and call_strike is not None:
        structure = f"STRANGLE ${put_strike:.0f}P / ${call_strike:.0f}C / {dte} DTE"
    elif strategy == "CSP" and put_strike is not None:
        structure = f"CSP ${put_strike:.0f}P / {dte} DTE"
    elif strategy == "SKIP":
        structure = "SKIP — blocked"
    else:
        structure = f"WAIT / {dte} DTE"

    return f"{structure}  |  {_format_contract_premium(trade.get('est_premium'))}  |  {_format_monthly_yield(trade.get('est_monthly_yield'))}  |  Acct {account}"


def _roll_summary(roll_triggers: dict[str, Any]) -> str:
    if not roll_triggers:
        return "Roll: n/a"
    profit = roll_triggers.get("profit_close", "")
    upgrade = roll_triggers.get("regime_upgrade", "")
    return f"Roll: {profit} | {upgrade}".strip()


def _format_flag_banner(symbol: str, flag_state: dict[str, Any], include_size_note: bool = True) -> list[str]:
    if flag_state.get("is_blocked"):
        lines = [f"🚫 {symbol.upper()} — BLOCKED"]
        for flag in flag_state.get("hard_blocks", []):
            lines.append(f"   {flag}: {flag_state['descriptions'].get(flag, '')}")
        lines.append("   Action: Remove from watchlist. Do not open new premium-selling exposure.")
        return lines

    warnings = flag_state.get("warnings", [])
    if not warnings:
        return []

    lines = [f"   ⚠️ FLAGS: {', '.join(warnings)}"]
    for flag in warnings:
        lines.append(f"   {flag}: {flag_state['descriptions'].get(flag, WARN_FLAGS.get(flag, ''))}")
    if include_size_note:
        lines.append("   Size: Reduce to half-size; speculative names stay at 1 contract max.")
    return lines


async def _load_live_portfolio() -> dict[str, Any]:
    configured = _get_configured_accounts()
    if not configured:
        raise RuntimeError(_no_credentials_message())

    all_positions = await _load_positions_all("all")

    current_symbols: set[str] = set()
    symbols: dict[str, Any] = {}
    for pos in all_positions:
        current_symbols.add(pos.symbol)
        item = symbols.setdefault(pos.symbol, {
            "symbol": pos.symbol,
            "shares": 0,
            "accounts": set(),
            "share_accounts": set(),
            "short_puts": 0,
            "short_calls": 0,
        })
        item["shares"] += int(pos.shares)
        item["accounts"].add(pos.account)
        if pos.shares > 0:
            item["share_accounts"].add(pos.account)
        for leg in pos.option_legs:
            if leg.quantity < 0 and leg.option_type == "PUT":
                item["short_puts"] += abs(int(leg.quantity))
            if leg.quantity < 0 and leg.option_type == "CALL":
                item["short_calls"] += abs(int(leg.quantity))

    sector_counts: Counter[str] = Counter()
    for symbol in current_symbols:
        sector = _SYMBOL_META.get(symbol, {}).get("sector")
        if sector:
            sector_counts[sector] += 1

    for item in symbols.values():
        item["accounts"] = sorted(item["accounts"])
        item["share_accounts"] = sorted(item["share_accounts"])

    return {
        "current_symbols": sorted(current_symbols),
        "symbols": symbols,
        "sector_counts": sector_counts,
        "_position_objects": all_positions,   # raw Position list for heat scanner
    }


async def _get_portfolio_check(symbol: str, portfolio: dict[str, Any], meta: dict[str, Any] | None = None) -> dict[str, Any]:
    symbol = symbol.upper()
    meta = meta or _SYMBOL_META.get(symbol, {})
    holding = portfolio.get("symbols", {}).get(symbol, {})
    sector = meta.get("sector")
    sector_count = int(portfolio.get("sector_counts", {}).get(sector, 0)) if sector else 0
    return {
        "symbol": symbol,
        "meta": meta,
        "shares": int(holding.get("shares", 0) or 0),
        "accounts": holding.get("accounts", []),
        "share_accounts": holding.get("share_accounts", []),
        "short_puts": int(holding.get("short_puts", 0) or 0),
        "short_calls": int(holding.get("short_calls", 0) or 0),
        "sector": sector,
        "sector_count": sector_count,
        "sector_warning": sector_count >= 3 if sector else False,
    }


def _symbol_heat_from_portfolio(symbol: str, portfolio: dict[str, Any], regime: str) -> dict | None:
    """Build a single-symbol heat scan from the already-loaded live portfolio dict."""
    try:
        from analysis.heat_scanner import heat_from_positions
        positions = portfolio.get("_position_objects", [])
        sym_positions = [p for p in positions if getattr(p, "symbol", "") == symbol.upper()]
        if not sym_positions:
            return None
        result = heat_from_positions(sym_positions, regime)
        # Return only this symbol's slice
        for item in result.get("positions", []):
            if item.get("symbol") == symbol.upper():
                return item
        return None
    except Exception:
        return None

async def _current_india_vix() -> float | None:
    loop = asyncio.get_event_loop()

    def _fetch() -> float | None:
        try:
            hist = yf.Ticker("^INDIAVIX").history(period="5d")
            if hist is None or hist.empty:
                return None
            return float(hist["Close"].iloc[-1])
        except Exception:
            return None

    return await loop.run_in_executor(None, _fetch)


def _research_signal(ivr_value: float | None, rsi: float | None, earnings_days: int | None,
                     regime_data: dict[str, Any], portfolio_check: dict[str, Any], symbol: str) -> str:
    if symbol in PERMANENT_EXITS and portfolio_check.get("shares", 0) <= 0:
        return "SKIP"
    if earnings_days is not None and earnings_days < RISK.get("earnings_blackout_days", 7):
        return "SKIP"
    if ivr_value is None or ivr_value < 25:
        return "SKIP"

    has_shares = portfolio_check.get("shares", 0) > 0
    new_entries_allowed = bool(regime_data.get("new_entries_allowed"))
    enter_ready = (
        ivr_value >= RISK.get("iv_rank_min_new_entry", 40)
        and (rsi is None or rsi < 65)
        and (earnings_days is None or earnings_days >= RISK.get("earnings_blackout_days", 7))
        and (new_entries_allowed or has_shares)
    )
    if enter_ready:
        if portfolio_check.get("short_puts", 0) > 0 and not has_shares:
            return "WATCH"
        if portfolio_check.get("sector_warning") and not has_shares:
            return "WATCH"
        return "ENTER NOW"
    return "WATCH"


def _recommended_trade(symbol: str, tech: dict[str, Any], iv_data: dict[str, Any],
                       portfolio_check: dict[str, Any], regime: str) -> dict[str, Any]:
    price = _safe_float(tech.get("current")) or 0.0
    meta = portfolio_check.get("meta", {})
    tier = int(meta.get("tier", 3) or 3)
    held_shares = int(portfolio_check.get("shares", 0) or 0)
    accounts = portfolio_check.get("share_accounts") or portfolio_check.get("accounts") or ["A"]
    display_account = "/".join(accounts)
    engine_account = str(accounts[0]) if accounts else "A"
    iv_rank = _safe_float(iv_data.get("iv_rank")) or 0.0
    iv = _normalized_iv_decimal(iv_data.get("current_iv"), iv_rank)
    rsi = _safe_float(tech.get("rsi")) or 50.0

    rec = recommend_trade(
        symbol=symbol,
        price=price,
        iv_rank=iv_rank,
        iv=iv,
        rsi=rsi,
        regime=regime,
        held_shares=held_shares,
        tier=tier,
        account=engine_account,
        flags=meta.get("flags", []),
    )
    trade = rec.__dict__.copy()
    trade["account"] = display_account or rec.account
    return trade


def _format_symbol_heat(heat: dict | None) -> list[str]:
    """Render existing leg heat for a single symbol inside a research card."""
    if not heat or not heat.get("top_actions"):
        return []
    lines = [""]
    stagger = heat.get("stagger_capacity", {})
    if stagger:
        for sym, status in stagger.items():
            icon = "🔴" if "STOP" in status else ("🟡" if "HARVEST" in status else ("✅" if "OPEN" in status else "⏸️"))
            lines.append(f"   {icon} Stagger: {status}")
    c = heat.get("counts", {})
    if c.get("RED", 0) + c.get("YELLOW", 0) > 0:
        lines.append(f"   🌡️ Open legs: {c.get('RED',0)} RED · {c.get('YELLOW',0)} YELLOW · {c.get('GREEN',0)} GREEN")
        for it in heat.get("top_actions", []):
            color_icon = "🔴" if it["color"] == "RED" else "🟡"
            lines.append(
                f"     {color_icon} {it['option_type']} ${it['strike']:.0f} "
                f"exp {it['expiry']} ({it['dte']}d) | "
                f"{it['pnl_pct']:.0f}% captured | "
                f"**{it['action']}** — {it['reason']}"
            )
    return lines



    meta = portfolio_check.get("meta", {})
    tier_text = _tier_label(meta.get("tier"))
    sector_text = meta.get("sector", "Unmapped")
    emoji, signal_text = _signal_display(portfolio_check.get("signal", "SKIP"))
    trade = portfolio_check.get("trade", {})
    flag_state = portfolio_check.get("flags") or check_flags(symbol, meta)
    price = _safe_float(tech.get("current")) or _safe_float(portfolio_check.get("price"))
    rsi = _safe_float(tech.get("rsi"))
    ivr_value = _safe_float(ivr.get("iv_rank")) or _safe_float(portfolio_check.get("ivr"))
    current_iv = _safe_float(ivr.get("current_iv")) or _safe_float(portfolio_check.get("current_iv"))

    earnings_days = portfolio_check.get("earnings_days")
    if earnings:
        deltas = []
        for item in earnings:
            try:
                deltas.append((date.fromisoformat(item) - date.today()).days)
            except Exception:
                continue
        if deltas:
            earnings_days = min(deltas)

    notes = [f"{tier_text} · {sector_text}"]
    shares = portfolio_check.get("shares", 0)
    short_puts = portfolio_check.get("short_puts", 0)
    short_calls = portfolio_check.get("short_calls", 0)
    if earnings_days is not None:
        notes.append(f"earnings ~{earnings_days}d")
    if shares > 0:
        notes.append(f"own {shares} shares")
    elif short_puts > 0:
        notes.append(f"existing short puts: {short_puts}")
    else:
        notes.append("not currently held")
    if short_calls > 0:
        notes.append(f"open short calls: {short_calls}")
    if portfolio_check.get("sector_warning"):
        notes.append(f"sector heavy ({portfolio_check.get('sector_count', 0)} positions)")
    if symbol in PERMANENT_EXITS:
        notes.append("permanent-exit list")

    timing = portfolio_check.get("timing") or {}
    if timing.get("composite_score") is not None:
        notes.append(f"timing {timing['composite_score']}/100 {timing.get('signal', 'WAIT')}")

    price_text = _format_price(price)
    rsi_text = f"{rsi:.0f}" if rsi is not None else "n/a"
    ivr_text = f"{ivr_value:.0f}" if ivr_value is not None else "n/a"
    if flag_state.get("is_blocked"):
        return "\n".join(_format_flag_banner(symbol, flag_state, include_size_note=False))

    top_line = f"{emoji} {signal_text:<10} {symbol.upper():<6} {price_text}  RSI {rsi_text}  IVR {ivr_text}"

    flag_lines = _format_flag_banner(symbol, flag_state)
    strategy_line = f"   {_strategy_regime_label(regime)} → {_format_strategy_line(trade)}"
    if current_iv is not None:
        strategy_line += f"  |  IV {current_iv:.1f}%"

    return "\n".join([
        top_line,
        *flag_lines,
        strategy_line,
        f"   Rationale: {trade.get('rationale', 'n/a')}",
        f"   {_roll_summary(trade.get('roll_triggers', {}))}",
        f"   Notes: {' | '.join(notes)}",
        *_format_symbol_heat(portfolio_check.get("position_heat")),
    ])


app = Server("theta-lab")


# ---------------------------------------------------------------------------
# Tool: generate_weekly_action_report
# ---------------------------------------------------------------------------
@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate_weekly_action_report",
            description=(
                "Generates the Monday Top-5 Weekly Action Report. "
                "Pulls live Schwab positions, calculates combined P&L, checks profit-take "
                "and roll triggers, detects market regime, and returns prioritised actions "
                "for Account A (Rahul margin) and Account B (Pinky IRA)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Save report to logs/ directory",
                        "default": True,
                    }
                },
            },
        ),
        Tool(
            name="check_market_regime",
            description=(
                "Detects current market regime (BEAR_SIDEWAYS, TRANSITIONING, CAUTIOUS_BULL, BULL) "
                "using VIX level and S&P 500 vs 50/200-day moving averages. "
                "Returns regime, signals, and whether new entries are allowed."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_iv_rank",
            description=(
                "Returns IV Rank (0-100) and IV Percentile for one or more tickers. "
                "IVR >= 40 is required for new entries per trading persona. "
                "Use before any new CSP or strangle entry."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ticker symbols e.g. ['AXON', 'CRWD']",
                    }
                },
                "required": ["symbols"],
            },
        ),
        Tool(
            name="get_portfolio_pnl",
            description=(
                "Returns combined net P&L per position: stock cost basis + all option premiums. "
                "This is the only number that matters — not options P&L in isolation. "
                "Includes profit-take signal and loss flag for each position."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "all"],
                        "description": "Which account(s) to analyse\n\n{default: \"all\"}",
                        "default": "all",
                    }
                },
            },
        ),
        Tool(
            name="scan_profit_take_candidates",
            description=(
                "Scans all open positions and returns those that have hit the "
                "regime-appropriate profit-take threshold (40-60% in bear, 70% in bull). "
                "Returns ordered list with recommendation to close."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "all"],
                        "default": "all",
                    }
                },
            },
        ),
        Tool(
            name="scan_roll_candidates",
            description=(
                "Scans all open option positions and returns those at or within "
                "21 DTE (roll threshold), ITM, or with mark > 2x premium received. "
                "Returns prioritised roll recommendations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "all"],
                        "default": "all",
                    }
                },
            },
        ),
        Tool(
            name="scan_position_heat",
            description=(
                "Scans all open short option legs and assigns a traffic light (RED/YELLOW/GREEN) "
                "based on: distance of stock price to strike (primary), cost-to-close as multiple "
                "of premium received, and DTE. Applies regime-aware protocol: in CAUTIOUS_BULL "
                "(AI bull rally), tightens call monitoring and flags when to pause new strangles. "
                "Management rules: calls ROLLED when stock falls (harvest+re-sell lower), puts CUT "
                "at loss when stock falls through strike then re-enter fresh. Profit target: 40-50%."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "all"],
                        "default": "all",
                    }
                },
            },
        ),
        Tool(
            name="dry_run_order",
            description=(
                "Pre-flight check for any proposed option order. "
                "Validates: buying power, position limits, earnings blackout, "
                "permanent exit list, and regime gate. "
                "MUST be called before any live order submission."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "symbol": {"type": "string"},
                    "action": {"type": "string", "enum": ["sell_put", "sell_call", "sell_strangle", "buy_to_close", "roll"]},
                    "strike": {"type": "number"},
                    "expiry": {"type": "string", "description": "YYYY-MM-DD"},
                    "quantity": {"type": "integer"},
                    "option_type": {"type": "string", "enum": ["PUT", "CALL"]},
                },
                "required": ["account", "symbol", "action", "quantity"],
            },
        ),
        Tool(
            name="screen_new_entries",
            description=(
                "When regime allows new entries, screens the universe for candidates. "
                "Filters by IVR >= 40, earnings blackout, and tier limits. "
                "Returns ranked entry opportunities with suggested strikes and DTE."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "tier": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                        "description": "Only screen this tier (default: all)",
                    },
                },
            },
        ),
        Tool(
            name="generate_india_weekly_report",
            description=(
                "Generates the weekly action report for Indian stock/options portfolio via ICICI Breeze API. "
                "Checks India VIX + Nifty 50 regime, pulls live NSE positions, calculates P&L, "
                "and returns prioritised actions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Save report to logs/ directory",
                        "default": True,
                    }
                },
            },
        ),
        Tool(
            name="generate_weekly_combined_report",
            description=(
                "Generates the Sunday combined US + India report. Tries live Schwab and Breeze APIs first, "
                "falls back to snapshot/statement data, saves HTML to logs/, and emails via Resend when configured."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Save report to logs/ directory",
                        "default": True,
                    }
                },
            },
        ),
        Tool(
            name="generate_bimonthly_technical_report",
            description=(
                "Generates the 15th bi-monthly technical analysis report for US assigned names, option legs, and India holdings. "
                "Uses live APIs when available, otherwise falls back to snapshot and statements."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Save report to logs/ directory",
                        "default": True,
                    }
                },
            },
        ),
        Tool(
            name="generate_monthly_objectives_report",
            description=(
                "Generates the monthly objectives gap analysis report with prior month actuals and current month pace projection. "
                "Uses live APIs first, falls back to snapshot/statements, saves HTML, and emails via Resend when configured."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Save report to logs/ directory",
                        "default": True,
                    }
                },
            },
        ),
        Tool(
            name="generate_unified_master_report",
            description=(
                "Generates unified master report for all 4 types: DAILY | WEEKLY | BIWEEKLY | MONTHLY. "
                "Pulls live market data from Yahoo Finance and all 8 account positions. "
                "Auto-detects report type if not specified. Returns conviction updates, tier rebalancing, "
                "sector rotation, and framework evolution."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["DAILY", "WEEKLY", "BIWEEKLY", "MONTHLY"],
                        "description": "Type of report. Auto-detects if not specified.",
                    },
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Save report to logs/ directory",
                        "default": True,
                    }
                },
            },
        ),
        Tool(
            name="get_live_positions",
            description=(
                "Returns live positions from Schwab for a specific account (A, B, C, or 'all'). "
                "Shows equities, open options, current prices, and unrealised P&L. "
                "Use for ad-hoc 'show me my positions' questions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "all"],
                        "description": "Which account to query",
                    }
                },
                "required": ["account"],
            },
        ),
        Tool(
            name="get_account_summary",
            description=(
                "Returns live account balances, buying power, and key metrics for Account A, B, C, or all. "
                "Use for ad-hoc balance/margin questions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "all"],
                    }
                },
                "required": ["account"],
            },
        ),
        Tool(
            name="get_position_detail",
            description=(
                "Returns full detail for a specific symbol across all accounts: shares held, all open option legs, "
                "cost basis, current price, unrealised P&L, and suggested next action based on persona."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Ticker symbol e.g. CRWD, ADBE",
                    }
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="research_symbol",
            description=(
                "Deep-dive research on a specific symbol. Returns: signal (ENTER/WATCH/SKIP), "
                "recommended trade with strike zone and DTE, and key supporting data. "
                "Always cross-checks against your current portfolio."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Ticker symbol e.g. RKLB",
                    }
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="scan_sector",
            description=(
                "Scans a specific sector for the best entry opportunities right now. "
                "Filters by current regime, IVR, RSI, and your portfolio concentration. "
                "Returns top 3-5 names with signal and recommended trade."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sector": {
                        "type": "string",
                        "enum": US_SECTOR_CHOICES,
                        "description": "Sector from screener_universe.py",
                    }
                },
                "required": ["sector"],
            },
        ),
        Tool(
            name="run_screener",
            description=(
                "Runs the full dynamic regime-aware screener on demand — same data as the monthly report's "
                "New Entry Opportunities section, but available any time. Returns top US and/or India candidates "
                "with signals and recommended trades."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "market": {
                        "type": "string",
                        "enum": ["US", "India", "both"],
                        "default": "both",
                    }
                },
            },
        ),
        Tool(
            name="review_flags",
            description=(
                "Reviews current dynamic flags for a symbol, refreshes stale entries via live evaluators, "
                "and returns confidence, source, expiry, and what changed."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Ticker symbol e.g. SMCI",
                    }
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="update_flag",
            description=(
                "Manually add, remove, or extend a cached flag with an audit reason, then return updated state."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "flag": {"type": "string"},
                    "action": {"type": "string", "enum": ["add", "remove", "extend"]},
                    "reason": {"type": "string"},
                },
                "required": ["symbol", "flag", "action", "reason"],
            },
        ),
        Tool(
            name="refresh_flags_cache",
            description=(
                "Refreshes stale cached flags across the full US and India screener universes. "
                "Returns what was refreshed, cleared, newly flagged, or errored."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "generate_weekly_action_report":
            result = await generate_weekly_report(ACCOUNT_A_HASH, ACCOUNT_B_HASH, ACCOUNT_C_HASH, save_to_file=arguments.get("save_to_file", True))
            return [TextContent(type="text", text=result.get("text") or result.get("html", ""))]

        elif name == "check_market_regime":
            regime_data = detect_regime()
            return [TextContent(type="text", text=json.dumps(regime_data, indent=2))]

        elif name == "get_iv_rank":
            symbols = arguments.get("symbols", [])
            results = batch_iv_rank(symbols)
            lines = ["## IV Rank Scan", ""]
            for sym, data in results.items():
                ivr = data.get("iv_rank")
                entry = "✅ Entry OK (IVR ≥ 40)" if data.get("entry_signal") else "❌ IVR too low for new entry"
                if ivr is not None:
                    lines.append(f"**{sym}:** IVR {ivr:.0f} | IV Pct {data.get('iv_pct')}% | Current IV {data.get('current_iv')}% | {entry}")
                else:
                    lines.append(f"**{sym}:** Data unavailable — {data.get('error', 'unknown error')}")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "get_portfolio_pnl":
            configured = _get_configured_accounts()
            if not configured:
                return [TextContent(type="text", text=_no_credentials_message())]
            from config import Regime, PROFIT_TARGETS
            regime_data = detect_regime()
            regime = regime_data["regime"]
            account_filter = arguments.get("account", "all")
            all_positions = await _load_positions_all(account_filter)
            # Group by account
            by_account: dict[str, list] = {}
            for pos in all_positions:
                by_account.setdefault(pos.account, []).append(pos)
            lines = [f"## Portfolio P&L — Account {account_filter.upper()}", f"**Regime:** {regime} | **Profit target:** {int(PROFIT_TARGETS[Regime(regime)][0]*100)}-{int(PROFIT_TARGETS[Regime(regime)][1]*100)}%", ""]
            for acct_label in sorted(by_account):
                positions = sorted(by_account[acct_label], key=lambda p: p.combined_net_pnl)
                lines.append(f"### Account {acct_label}")
                lines.append("| Symbol | Price | Net P&L | Premium Rcvd | Cost-to-Close | % Captured | Signal |")
                lines.append("|--------|-------|---------|-------------|---------------|-----------|--------|")
                for pos in positions:
                    pnl = pos.combined_net_pnl
                    pct = pos.profit_pct_of_max
                    sig = pos.profit_take_signal(regime)
                    loss = pos.loss_flag()
                    flag = "🔴 LOSS FLAG" if loss["flag"] else ("✅ TAKE PROFIT" if sig["signal"] else "🟢 HOLD")
                    lines.append(
                        f"| {pos.symbol} | ${pos.current_price:,.2f} | {'+'if pnl>=0 else ''}{pnl:,.0f} "
                        f"| ${pos.total_premium_received:,.0f} | ${pos.total_cost_to_close_options:,.0f} "
                        f"| {round(pct*100,1) if pct else 'N/A'}% | {flag} |"
                    )
                lines.append("")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "scan_profit_take_candidates":
            configured = _get_configured_accounts()
            if not configured:
                return [TextContent(type="text", text=_no_credentials_message())]
            from config import Regime, PROFIT_TARGETS
            regime_data = detect_regime()
            regime = regime_data["regime"]
            low, high = PROFIT_TARGETS[Regime(regime)]
            account_filter = arguments.get("account", "all")
            all_positions = await _load_positions_all(account_filter)
            candidates = []
            for pos in all_positions:
                sig = pos.profit_take_signal(regime)
                if sig["signal"]:
                    candidates.append((pos, pos.account, sig))
            candidates.sort(key=lambda x: x[2]["pct_captured"], reverse=True)
            lines = [
                f"## Profit-Take Candidates",
                f"**Regime:** {regime} | **Threshold:** {int(low*100)}-{int(high*100)}% of premium received",
                f"**{len(candidates)} position(s) at or past profit target**", ""
            ]
            if not candidates:
                lines.append("✅ No positions currently at profit target.")
            for pos, acct, sig in candidates:
                lines += [
                    f"### {pos.symbol} — Account {acct} — {sig['pct_captured']}% captured",
                    f"- Premium received: ${pos.total_premium_received:,.0f}",
                    f"- Cost to close: ${pos.total_cost_to_close_options:,.0f}",
                    f"- Net P&L (combined): ${pos.combined_net_pnl:,.0f}",
                    f"- **Action:** {sig['recommendation']}",
                    ""
                ]
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "scan_roll_candidates":
            configured = _get_configured_accounts()
            if not configured:
                return [TextContent(type="text", text=_no_credentials_message())]
            from config import RISK
            account_filter = arguments.get("account", "all")
            all_positions = await _load_positions_all(account_filter)
            roll_items = []
            for pos in all_positions:
                roll = pos.roll_signal()
                loss = pos.loss_flag()
                itm_legs = [lg for lg in pos.option_legs if
                            (lg.option_type == "PUT" and pos.current_price < lg.strike) or
                            (lg.option_type == "CALL" and pos.current_price > lg.strike)]
                if roll["signal"] or loss["flag"] or itm_legs:
                    roll_items.append({
                        "pos": pos, "acct": pos.account,
                        "roll": roll, "loss": loss,
                        "itm_legs": itm_legs,
                        "priority": 1 if (loss["flag"] or any(lg.dte <= 13 for lg in pos.option_legs)) else 2,
                    })
            roll_items.sort(key=lambda x: (x["priority"], min((lg.dte for lg in x["pos"].option_legs), default=999)))
            lines = [f"## Roll Candidates — {len(roll_items)} position(s) need attention", ""]
            if not roll_items:
                lines.append("✅ No roll candidates. All positions healthy.")
            for item in roll_items:
                pos, acct = item["pos"], item["acct"]
                lines.append(f"### {'🚨' if item['priority']==1 else '🔶'} {pos.symbol} — Account {acct} | ${pos.current_price:,.2f}")
                if item["loss"]["flag"]:
                    lf = item["loss"]
                    lines.append(f"- ⚠️ Loss flag: {lf['multiplier']}x premium | Premium: ${lf['premium_received']:,.0f} → Cost to close: ${lf['current_cost_to_close']:,.0f}")
                if item["roll"]["signal"]:
                    for leg_str in item["roll"]["legs"]:
                        lines.append(f"- 🔄 Roll needed: {leg_str}")
                for lg in item["itm_legs"]:
                    pct = abs(pos.current_price - lg.strike) / pos.current_price * 100
                    lines.append(f"- 🔴 ITM: {lg.option_type} ${lg.strike} exp {lg.expiry} ({lg.dte} DTE) — {pct:.1f}% in the money")
                lines.append("")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "scan_position_heat":
            configured = _get_configured_accounts()
            if not configured:
                return [TextContent(type="text", text=_no_credentials_message())]
            from analysis.heat_scanner import assess_portfolio_heat
            account_filter = arguments.get("account", "all")
            regime_data = detect_regime()
            regime_str = regime_data.get("regime", "CAUTIOUS_BULL")
            all_positions = await _load_positions_all(account_filter)
            all_legs = []
            for pos in all_positions:
                for lg in pos.option_legs:
                    premium = abs(lg.premium_received or 0)
                    ctc = abs(getattr(lg, "current_mark", 0) or 0)
                    if premium <= 0:
                        continue
                    all_legs.append({
                        "symbol": pos.symbol,
                        "option_type": lg.option_type,
                        "strike": lg.strike,
                        "dte": lg.dte,
                        "expiry": lg.expiry,
                        "premium_received": premium,
                        "cost_to_close": ctc,
                        "current_price": pos.current_price,
                    })
            if not all_legs:
                return [TextContent(type="text", text="⚠️ No open option legs found (or live data unavailable).")]
            result = assess_portfolio_heat(all_legs, regime_str)
            lines = [
                f"## 🌡️ Position Heat Scan — Regime: {regime_str}",
                f"**{result['counts']['RED']} RED** · **{result['counts']['YELLOW']} YELLOW** · {result['counts']['GREEN']} GREEN",
                "",
                result["protocol"],
                "",
            ]
            if result["scale_back_new_entries"]:
                lines.append("⛔ **Scale back new strangles until RED/YELLOW calls are resolved.**")
                lines.append("")
            for color, emoji in [("RED", "🔴"), ("YELLOW", "🟡"), ("GREEN", "🟢")]:
                items = result["by_color"][color]
                if not items:
                    continue
                lines.append(f"### {emoji} {color} ({len(items)})")
                for item in items:
                    lines.append(
                        f"- **{item['symbol']} {item['type']} ${item['strike']:.0f}** exp {item['expiry']} ({item['dte']}d) | "
                        f"price=${item['current_price']:,.2f} | {item['distance_pct']:.0f}% to strike | "
                        f"P&L: {item['pnl_pct']:.0f}% captured | "
                        f"**{item['action']}** — {item['reason']}"
                    )
                lines.append("")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "dry_run_order":
            symbol = arguments.get("symbol", "")
            account = arguments.get("account", "")
            action = arguments.get("action", "")
            quantity = arguments.get("quantity", 1)
            expiry = arguments.get("expiry", "")

            checks = []
            warnings = []

            # Permanent exit check
            if symbol in PERMANENT_EXITS:
                checks.append({"check": "permanent_exit", "passed": False,
                               "detail": f"{symbol} is on permanent exit list — NO new positions ever"})
            else:
                checks.append({"check": "permanent_exit", "passed": True})

            # Regime gate
            regime_data = detect_regime()
            regime = regime_data["regime"]
            new_entries_ok = regime_data["new_entries_allowed"]
            if action in ["sell_put", "sell_call", "sell_strangle"] and not new_entries_ok:
                checks.append({"check": "regime_gate", "passed": False,
                               "detail": f"Regime is {regime} — no new entries until regime shifts"})
            else:
                checks.append({"check": "regime_gate", "passed": True})

            # Tier + contract limit
            tier_num = 1
            for t, tickers in UNIVERSE.items():
                if symbol in tickers:
                    tier_num = t.value
                    break
            max_q = {1: 5, 2: 3, 3: 1}[tier_num]
            if quantity > max_q:
                warnings.append(f"{symbol} is Tier {tier_num} — max {max_q} contracts (requested {quantity})")

            # IRA naked call check
            if account == "B" and action in ["sell_call", "sell_strangle"]:
                checks.append({"check": "ira_no_naked_calls", "passed": False,
                               "detail": "Account B (IRA) cannot sell naked calls — only CSPs and CCs against owned shares"})

            all_passed = all(c["passed"] for c in checks)
            result = {
                "ok": all_passed,
                "order": arguments,
                "checks": checks,
                "warnings": warnings,
                "regime": regime,
                "instruction": "PROCEED" if all_passed else "DO NOT SUBMIT — fix failing checks first",
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "screen_new_entries":
            regime_data = detect_regime()
            if not regime_data["new_entries_allowed"]:
                return [TextContent(type="text", text=(
                    f"🚫 **No new entries allowed**\n\n"
                    f"Regime: {regime_data['regime']}\n"
                    f"Note: {regime_data.get('note', '')}\n\n"
                    f"Action: Monitor universe, prepare watchlist for when regime shifts.\n\n"
                    f"**Regime shift signals to watch:**\n"
                    f"- VIX sustained below 20 for 10+ days\n"
                    f"- S&P 500 above both 50-day and 200-day MA\n"
                    f"- Put/call ratio below 0.80"
                ))]
            # When regime allows — screen by IVR
            tier_filter = arguments.get("tier")
            candidates = []
            for tier, tickers in UNIVERSE.items():
                if tier_filter and tier.value != tier_filter:
                    continue
                for sym in tickers:
                    if sym not in PERMANENT_EXITS:
                        candidates.append(sym)
            ivr_data = batch_iv_rank(candidates[:20])  # limit API calls
            qualified = [(s, d) for s, d in ivr_data.items() if d.get("entry_signal")]
            qualified.sort(key=lambda x: x[1].get("iv_rank", 0), reverse=True)
            lines = ["## Entry Candidates (IVR ≥ 40)", ""]
            for sym, d in qualified[:10]:
                lines.append(f"- **{sym}**: IVR {d['iv_rank']:.0f} | IV {d['current_iv']}% | Entry: ✅")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "get_live_positions":
            configured = _get_configured_accounts()
            if not configured:
                return [TextContent(type="text", text=_no_credentials_message())]
            # File-based (Schwab/Robinhood live API removed): positions from exported CSVs.
            account = arguments.get("account", "all")
            all_positions = await _load_positions_all(account)
            results: dict[str, Any] = {}
            for pos in all_positions:
                r = results.setdefault(pos.account, {"equities": [], "options": [], "total_positions": 0})
                r["total_positions"] += 1
                if getattr(pos, "shares", 0):
                    r["equities"].append({
                        "symbol": pos.symbol,
                        "qty": int(pos.shares),
                        "current_price": round(pos.current_price, 2),
                    })
                for leg in pos.option_legs:
                    r["options"].append({
                        "symbol": getattr(leg, "description", pos.symbol),
                        "underlying": pos.symbol,
                        "qty": leg.quantity,
                        "strike": getattr(leg, "strike", None),
                        "type": leg.option_type,
                    })
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_account_summary":
            configured = _get_configured_accounts()
            if not configured:
                return [TextContent(type="text", text=_no_credentials_message())]
            # File-based: live cash balances require broker access (Schwab API removed).
            # Report per-account position count + short-put collateral from the files.
            account = arguments.get("account", "all")
            all_positions = await _load_positions_all(account)
            by_acct: dict[str, list] = {}
            for pos in all_positions:
                by_acct.setdefault(pos.account, []).append(pos)
            results = {}
            for acct_label, plist in sorted(by_acct.items()):
                collateral = sum(
                    abs(getattr(leg, "strike", 0) or 0) * 100 * abs(leg.quantity)
                    for pos in plist for leg in pos.option_legs
                    if leg.quantity < 0 and leg.option_type == "PUT"
                )
                results[acct_label] = {
                    "positions": len(plist),
                    "short_put_collateral": round(collateral, 2),
                    "note": "Live cash balance requires broker access — file-based summary.",
                }
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_position_detail":
            configured = _get_configured_accounts()
            if not configured:
                return [TextContent(type="text", text=_no_credentials_message())]
            symbol = str(arguments.get("symbol", "")).strip().upper()
            regime = detect_regime()["regime"]
            accounts = {}
            aggregate = {
                "accounts_holding": [],
                "total_shares": 0,
                "combined_net_pnl": 0.0,
                "premium_received": 0.0,
                "cost_to_close_options": 0.0,
            }
            all_positions = await _load_positions_all("all")
            for pos in all_positions:
                if pos.symbol.upper() != symbol:
                    continue
                acct_label = pos.account
                profit_signal = pos.profit_take_signal(regime)
                roll_signal = pos.roll_signal()
                loss_signal = pos.loss_flag()
                accounts[acct_label] = {
                    "shares": pos.shares,
                    "stock_cost_basis": round(pos.stock_cost_basis, 2),
                    "current_price": round(pos.current_price, 2),
                    "stock_pnl": round(pos.stock_pnl, 2),
                    "net_options_pnl": round(pos.net_options_pnl, 2),
                    "combined_net_pnl": round(pos.combined_net_pnl, 2),
                    "premium_received": round(pos.total_premium_received, 2),
                    "cost_to_close_options": round(pos.total_cost_to_close_options, 2),
                    "profit_capture_pct": round(pos.profit_pct_of_max * 100, 1) if pos.profit_pct_of_max is not None else None,
                    "open_option_legs": [
                        {
                            "description": leg.description,
                            "strike": leg.strike,
                            "expiry": leg.expiry,
                            "option_type": leg.option_type,
                            "quantity": leg.quantity,
                            "premium_received": round(leg.premium_received, 2),
                            "current_mark": round(leg.current_mark, 2),
                            "dte": leg.dte,
                        }
                        for leg in pos.option_legs
                    ],
                    "signals": {
                        "profit_take": profit_signal,
                        "roll": roll_signal,
                        "loss": loss_signal,
                    },
                    "suggested_next_action": _position_action(pos, regime),
                }
                aggregate["accounts_holding"].append(acct_label)
                aggregate["total_shares"] += pos.shares
                aggregate["combined_net_pnl"] += pos.combined_net_pnl
                aggregate["premium_received"] += pos.total_premium_received
                aggregate["cost_to_close_options"] += pos.total_cost_to_close_options

            result = {
                "symbol": symbol,
                "regime": regime,
                "accounts": accounts,
                "aggregate": {
                    "accounts_holding": aggregate["accounts_holding"],
                    "total_shares": aggregate["total_shares"],
                    "combined_net_pnl": round(aggregate["combined_net_pnl"], 2),
                    "premium_received": round(aggregate["premium_received"], 2),
                    "cost_to_close_options": round(aggregate["cost_to_close_options"], 2),
                },
                "technical": technical_snapshot(symbol),
            }
            if not accounts:
                result["note"] = "No open position found across configured accounts."
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "research_symbol":
            symbol = str(arguments.get("symbol", "")).strip().upper()
            if not symbol:
                return [TextContent(type="text", text="symbol is required")]

            meta = _SYMBOL_META.get(symbol, {
                "symbol": symbol,
                "sector": "Unmapped",
                "tier": 3,
                "preferred_strategy": "CSP",
            })
            india = symbol in {item["symbol"] for item in INDIA_UNIVERSE}
            iv_symbol = yf_symbol(symbol, india=True) if india else symbol
            tech_symbol = symbol
            loop = asyncio.get_event_loop()
            iv_task = loop.run_in_executor(None, partial(get_iv_rank, iv_symbol))
            tech_task = loop.run_in_executor(None, partial(technical_snapshot, tech_symbol, india))
            iv_data, tech = await asyncio.gather(iv_task, tech_task)
            earnings = await _run_sync(upcoming_earnings, iv_symbol, 21)
            portfolio = await _load_live_portfolio()
            portfolio_check = await _get_portfolio_check(symbol, portfolio, meta)
            regime_data = detect_india_regime() if india else detect_regime()
            earnings_days = None
            if earnings:
                parsed = []
                for item in earnings:
                    try:
                        parsed.append((date.fromisoformat(item) - date.today()).days)
                    except Exception:
                        continue
                if parsed:
                    earnings_days = min(parsed)
            ivr_value = _safe_float(iv_data.get("iv_rank"))
            rsi = _safe_float(tech.get("rsi"))
            signal = _research_signal(ivr_value, rsi, earnings_days, regime_data, portfolio_check, symbol)
            timing = None
            if not india and ivr_value is not None:
                try:
                    timing = await _run_sync(entry_timing_score, symbol, ivr_value)
                except Exception:
                    timing = None
            flag_state = check_flags(symbol, meta)
            if flag_state.get("is_blocked"):
                signal = "SKIP"
            portfolio_check.update({
                "signal": signal,
                "flags": flag_state,
                "trade": _recommended_trade(symbol, tech, iv_data, portfolio_check, regime_data.get("regime", "TRANSITIONING")),
                "timing": timing,
                "earnings_days": earnings_days,
                "earnings_window": 21,
                "position_heat": _symbol_heat_from_portfolio(symbol, portfolio, regime_data.get("regime", "TRANSITIONING")),
            })
            return [TextContent(type="text", text=_format_research_card(symbol, tech, iv_data, earnings, portfolio_check, regime_data.get("regime", "UNKNOWN")))]

        elif name == "scan_sector":
            sector = str(arguments.get("sector", "")).strip()
            if sector not in US_SECTOR_CHOICES:
                return [TextContent(type="text", text=f"Unknown sector: {sector}")]
            portfolio = await _load_live_portfolio()
            regime_data = detect_regime()
            ranked = await _run_sync(screen_us_opportunities, regime_data.get("regime", "TRANSITIONING"), portfolio.get("current_symbols", []), len(US_UNIVERSE))
            sector_candidates = [item for item in ranked if item.get("sector") == sector][:5]
            if not sector_candidates:
                return [TextContent(type="text", text=f"No candidates found for {sector}.")]

            cards = []
            for candidate in sector_candidates:
                symbol = candidate["symbol"]
                meta = _SYMBOL_META.get(symbol, candidate)
                portfolio_check = await _get_portfolio_check(symbol, portfolio, meta)
                flag_state = check_flags(symbol, meta)
                signal = (candidate.get("signal") or "SKIP").replace("_", " ")
                if flag_state.get("is_blocked"):
                    signal = "SKIP"
                if not regime_data.get("new_entries_allowed") and portfolio_check.get("shares", 0) <= 0 and signal == "ENTER NOW":
                    signal = "WATCH"
                if portfolio_check.get("short_puts", 0) > 0 and portfolio_check.get("shares", 0) <= 0 and signal == "ENTER NOW":
                    signal = "WATCH"
                if portfolio_check.get("sector_warning") and portfolio_check.get("shares", 0) <= 0 and signal == "ENTER NOW":
                    signal = "WATCH"
                portfolio_check.update({
                    "signal": signal,
                    "flags": flag_state,
                    "trade": _recommended_trade(symbol, {"current": candidate.get("price"), "rsi": candidate.get("rsi")}, {"iv_rank": candidate.get("ivr"), "current_iv": candidate.get("current_iv")}, portfolio_check, regime_data.get("regime", "TRANSITIONING")),
                    "price": candidate.get("price"),
                    "ivr": candidate.get("ivr"),
                    "current_iv": candidate.get("current_iv"),
                    "pct_off_high": candidate.get("pct_off_high"),
                    "earnings_days": candidate.get("earnings_days") if candidate.get("earnings_soon") else None,
                    "earnings_window": 21,
                })
                tech = {
                    "current": candidate.get("price"),
                    "rsi": candidate.get("rsi"),
                    "week_52_high": None,
                    "week_52_low": None,
                    "pct_off_high": candidate.get("pct_off_high"),
                }
                iv_data = {"iv_rank": candidate.get("ivr"), "current_iv": candidate.get("current_iv")}
                cards.append(_format_research_card(symbol, tech, iv_data, [], portfolio_check, regime_data.get("regime", "UNKNOWN")))

            header = (
                f"## {sector} scan\n"
                f"Regime: {regime_data.get('regime', 'UNKNOWN')} | "
                f"Portfolio concentration: {portfolio.get('sector_counts', {}).get(sector, 0)} active positions\n"
            )
            return [TextContent(type="text", text=header + "\n\n".join(cards))]

        elif name == "run_screener":
            market = str(arguments.get("market", "both") or "both")
            market_key = market.lower()
            if market_key not in {"us", "india", "both"}:
                return [TextContent(type="text", text=f"Unknown market: {market}")]

            portfolio = await _load_live_portfolio()
            sections = []

            if market_key in {"us", "both"}:
                regime_data = detect_regime()
                us_candidates = await _run_sync(screen_us_opportunities, regime_data.get("regime", "TRANSITIONING"), portfolio.get("current_symbols", []), 8)
                us_cards = []
                for candidate in us_candidates:
                    symbol = candidate["symbol"]
                    meta = _SYMBOL_META.get(symbol, candidate)
                    portfolio_check = await _get_portfolio_check(symbol, portfolio, meta)
                    flag_state = check_flags(symbol, meta)
                    signal = (candidate.get("signal") or "SKIP").replace("_", " ")
                    if flag_state.get("is_blocked"):
                        signal = "SKIP"
                    if not regime_data.get("new_entries_allowed") and portfolio_check.get("shares", 0) <= 0 and signal == "ENTER NOW":
                        signal = "WATCH"
                    if portfolio_check.get("short_puts", 0) > 0 and portfolio_check.get("shares", 0) <= 0 and signal == "ENTER NOW":
                        signal = "WATCH"
                    if portfolio_check.get("sector_warning") and portfolio_check.get("shares", 0) <= 0 and signal == "ENTER NOW":
                        signal = "WATCH"
                    portfolio_check.update({
                        "signal": signal,
                        "flags": flag_state,
                        "trade": _recommended_trade(symbol, {"current": candidate.get("price"), "rsi": candidate.get("rsi")}, {"iv_rank": candidate.get("ivr"), "current_iv": candidate.get("current_iv")}, portfolio_check, regime_data.get("regime", "TRANSITIONING")),
                        "price": candidate.get("price"),
                        "ivr": candidate.get("ivr"),
                        "current_iv": candidate.get("current_iv"),
                        "pct_off_high": candidate.get("pct_off_high"),
                        "earnings_days": candidate.get("earnings_days") if candidate.get("earnings_soon") else None,
                        "earnings_window": 21,
                    })
                    tech = {
                        "current": candidate.get("price"),
                        "rsi": candidate.get("rsi"),
                        "week_52_high": None,
                        "week_52_low": None,
                        "pct_off_high": candidate.get("pct_off_high"),
                    }
                    iv_data = {"iv_rank": candidate.get("ivr"), "current_iv": candidate.get("current_iv")}
                    us_cards.append(_format_research_card(symbol, tech, iv_data, [], portfolio_check, regime_data.get("regime", "UNKNOWN")))
                sections.append(
                    f"## US screener\nRegime: {regime_data.get('regime', 'UNKNOWN')}\n\n"
                    + "\n\n".join(us_cards)
                )

            if market_key in {"india", "both"}:
                india_vix = await _current_india_vix()
                if india_vix is None:
                    sections.append("## India screener\nIndia VIX unavailable right now.")
                else:
                    india_regime_data = detect_india_regime()
                    india_candidates = await _run_sync(screen_india_opportunities, india_vix, [], 6)
                    india_cards = []
                    for candidate in india_candidates:
                        symbol = candidate["symbol"]
                        meta = _SYMBOL_META.get(symbol, candidate)
                        flag_state = check_flags(symbol, meta)
                        portfolio_check = {
                            "meta": meta,
                            "shares": 0,
                            "accounts": [],
                            "share_accounts": [],
                            "short_puts": 0,
                            "short_calls": 0,
                            "sector": meta.get("sector"),
                            "sector_count": 0,
                            "sector_warning": False,
                            "signal": "SKIP" if flag_state.get("is_blocked") else (candidate.get("signal") or "SKIP").replace("_", " "),
                            "flags": flag_state,
                            "trade": _recommended_trade(symbol, {"current": candidate.get("price"), "rsi": candidate.get("rsi")}, {"iv_rank": candidate.get("ivr"), "current_iv": candidate.get("current_iv")}, {"meta": meta, "shares": 0, "accounts": [], "share_accounts": [], "short_puts": 0, "short_calls": 0, "sector": meta.get("sector"), "sector_count": 0, "sector_warning": False}, india_regime_data.get("regime", "TRANSITIONING")),
                            "price": candidate.get("price"),
                            "ivr": candidate.get("ivr"),
                            "current_iv": candidate.get("current_iv"),
                            "pct_off_high": candidate.get("pct_off_high"),
                            "earnings_days": candidate.get("earnings_days") if candidate.get("earnings_soon") else None,
                            "earnings_window": 21,
                        }
                        tech = {
                            "current": candidate.get("price"),
                            "rsi": candidate.get("rsi"),
                            "week_52_high": None,
                            "week_52_low": None,
                            "pct_off_high": candidate.get("pct_off_high"),
                        }
                        iv_data = {"iv_rank": candidate.get("ivr"), "current_iv": candidate.get("current_iv")}
                        india_cards.append(_format_research_card(symbol, tech, iv_data, [], portfolio_check, india_regime_data.get("regime", "TRANSITIONING")))
                    sections.append(
                        f"## India screener\nIndia VIX: {india_vix:.1f} | Regime: {india_regime_data.get('regime', 'UNKNOWN')}\n\n"
                        + "\n\n".join(india_cards)
                    )

            return [TextContent(type="text", text="\n\n".join(section for section in sections if section))]

        elif name == "review_flags":
            symbol = str(arguments.get("symbol", "") or "").upper()
            if not symbol:
                return [TextContent(type="text", text="symbol is required")]

            before = get_flag_status(symbol)
            seed_flags = [str(flag).upper() for flag in _SYMBOL_META.get(symbol, {}).get("flags", [])]
            if not seed_flags:
                seed_flags = [str(flag).upper() for flag in QUALITY_FLAGS_BY_SYMBOL.get(symbol, [])]
            result = check_flags_live(symbol, seed_flags=seed_flags)
            after = get_flag_status(symbol)

            before_flags = {item.get("flag") for item in before.get("flags", [])}
            active_flags = result.get("hard_blocks", []) + result.get("warnings", [])
            active_flag_keys = {item.get("flag") for item in active_flags}
            cleared_flags = sorted(flag for flag in before_flags - active_flag_keys if flag)
            refreshed_flags = sorted(set(result.get("stale_flags_refreshed", [])))
            new_flags = sorted(flag for flag in active_flag_keys - before_flags if flag)

            lines = [f"## Flag review — {symbol}", f"Evaluated at: {result.get('evaluated_at', after.get('last_updated', 'n/a'))}", ""]
            if active_flags:
                for item in result.get("hard_blocks", []):
                    lines.append(
                        f"🚫 {item['flag']} | conf {item.get('confidence', 0):.2f} | expires {item.get('expires_at', 'n/a')}"
                    )
                    lines.append(f"   Source: {item.get('source', 'n/a')}")
                    if item.get("notes"):
                        lines.append(f"   Notes: {item['notes']}")
                for item in result.get("warnings", []):
                    lines.append(
                        f"⚠️ {item['flag']} | conf {item.get('confidence', 0):.2f} | expires {item.get('expires_at', 'n/a')}"
                    )
                    lines.append(f"   Source: {item.get('source', 'n/a')}")
                    if item.get("notes"):
                        lines.append(f"   Notes: {item['notes']}")
            else:
                lines.append("✅ No active flags.")

            if refreshed_flags:
                lines.extend(["", f"🔄 Refreshed: {', '.join(refreshed_flags)}"])
            if new_flags:
                lines.extend(["", f"⚠️ New flags: {', '.join(new_flags)}"])
            if cleared_flags:
                lines.extend(["", f"✅ Cleared: {', '.join(cleared_flags)}"])
            if after.get("removed_flags"):
                last_removed = after["removed_flags"][-3:]
                lines.append("")
                lines.append("Recent removals:")
                for item in last_removed:
                    lines.append(f"✅ {item.get('flag')} removed at {item.get('removed_at')} — {item.get('reason', '')}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "update_flag":
            symbol = str(arguments.get("symbol", "") or "").upper()
            flag = str(arguments.get("flag", "") or "").upper()
            action = str(arguments.get("action", "") or "").lower()
            reason = str(arguments.get("reason", "") or "")
            if not symbol or not flag or action not in {"add", "remove", "extend"} or not reason:
                return [TextContent(type="text", text="symbol, flag, action(add|remove|extend), and reason are required")]

            outcome = update_live_flag(symbol, flag, action, reason)
            state = get_flag_status(symbol)
            lines = [f"## Flag update — {symbol}", f"✅ {action.upper()} {flag}", f"Reason: {reason}", "", "Current cache state:"]
            if state.get("flags"):
                for item in state["flags"]:
                    emoji = "🚫" if item.get("flag") in {"ACCOUNTING_RISK", "DELISTING_RISK", "GOING_CONCERN", "HALTED", "PERMANENT_EXIT"} and float(item.get("confidence", 0)) >= 0.60 else "⚠️"
                    stale_note = " (stale)" if item.get("is_stale") else ""
                    lines.append(
                        f"{emoji} {item.get('flag')} | conf {item.get('confidence', 0):.2f} | expires {item.get('expires_at', 'n/a')}{stale_note}"
                    )
                    lines.append(f"   Source: {item.get('source', 'n/a')}")
                    if item.get("notes"):
                        lines.append(f"   Notes: {item.get('notes')}")
            else:
                lines.append("✅ No active flags.")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "refresh_flags_cache":
            universe_symbols = sorted({item["symbol"] for item in [*US_UNIVERSE, *INDIA_UNIVERSE]})
            summary = review_all_stale_flags(universe_symbols)
            lines = ["## Refresh flags cache"]
            refreshed = summary.get("refreshed", [])
            cleared = summary.get("cleared", [])
            new_flags = summary.get("new_flags", [])
            errors = summary.get("errors", [])

            lines.append(f"🔄 Refreshed symbols: {len(refreshed)}")
            lines.append(f"✅ Cleared symbols: {len(cleared)}")
            lines.append(f"⚠️ Newly flagged symbols: {len(new_flags)}")
            if errors:
                lines.append(f"❌ Errors: {len(errors)}")

            if refreshed:
                lines.append("")
                lines.append("Refreshed:")
                for item in refreshed:
                    lines.append(f"🔄 {item['symbol']}: {', '.join(item.get('flags', []))}")
            if cleared:
                lines.append("")
                lines.append("Cleared:")
                for item in cleared:
                    lines.append(f"✅ {item['symbol']}: {', '.join(item.get('flags', []))}")
            if new_flags:
                lines.append("")
                lines.append("New flags:")
                for item in new_flags:
                    lines.append(f"⚠️ {item['symbol']}: {', '.join(item.get('flags', []))}")
            if errors:
                lines.append("")
                lines.append("Errors:")
                for item in errors:
                    lines.append(f"❌ {item['symbol']}: {item.get('error', 'unknown error')}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "generate_india_weekly_report":
            BREEZE_API_KEY = os.getenv("BREEZE_API_KEY", "")
            BREEZE_API_SECRET = os.getenv("BREEZE_API_SECRET", "")
            BREEZE_SESSION_TOKEN = os.getenv("BREEZE_SESSION_TOKEN", "")
            report = await generate_india_weekly_report(
                BREEZE_API_KEY, BREEZE_API_SECRET, BREEZE_SESSION_TOKEN
            )
            if arguments.get("save_to_file", True):
                log_path = Path(__file__).parent.parent / "logs" / f"india_action_report_{date.today()}.md"
                log_path.parent.mkdir(parents=True, exist_ok=True)
                log_path.write_text(report)
            return [TextContent(type="text", text=report)]

        elif name == "generate_weekly_combined_report":
            result = await generate_weekly_combined_report(
                send_email=bool(os.getenv("RESEND_API_KEY", "")),
                save_to_file=arguments.get("save_to_file", True),
            )
            return [TextContent(type="text", text=result["summary"])]

        elif name == "generate_bimonthly_technical_report":
            result = await generate_bimonthly_technical_report(
                send_email=bool(os.getenv("RESEND_API_KEY", "")),
                save_to_file=arguments.get("save_to_file", True),
            )
            return [TextContent(type="text", text=result["summary"])]

        elif name == "generate_monthly_objectives_report":
            result = await generate_monthly_objectives_report(
                send_email=bool(os.getenv("RESEND_API_KEY", "")),
                save_to_file=arguments.get("save_to_file", True),
            )
            return [TextContent(type="text", text=result["summary"])]

        elif name == "generate_unified_master_report":
            result = await generate_unified_master_report(
                report_type=arguments.get("report_type"),
                save_to_file=arguments.get("save_to_file", True)
            )
            return [TextContent(type="text", text=result["text"])]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error in {name}: {e}")]


def _no_credentials_message() -> str:
    return (
        "## Schwab API Credentials Required\n\n"
        "Set the following environment variables to enable live data:\n\n"
        "```\n"
        "SCHWAB_API_KEY=your_key\n"
        "SCHWAB_APP_SECRET=your_secret\n"
        "SCHWAB_ACCOUNT_A_HASH=hash_for_232\n"
        "SCHWAB_ACCOUNT_B_HASH=hash_for_275\n"
        "```\n\n"
        "See `docs/schwab_api_setup.md` for registration instructions.\n\n"
        "Until credentials are set, use weekly_report.py with manual data from brokerage statements."
    )


def _schwab_data_required(tool: str) -> str:
    return f"Tool `{tool}` requires live Schwab credentials. See `docs/schwab_api_setup.md`."


async def _init_schwab_broker() -> None:
    """Register and authenticate the Schwab broker in the open_stocks_mcp registry."""
    api_key = os.getenv("SCHWAB_API_KEY")
    app_secret = os.getenv("SCHWAB_APP_SECRET")
    if not api_key or not app_secret:
        return
    try:
        from open_stocks_mcp.brokers.registry import get_broker_registry
        from open_stocks_mcp.brokers.schwab import SchwabBroker
        registry = await get_broker_registry()
        if "schwab" not in registry.list_brokers():
            broker = SchwabBroker(api_key=api_key, app_secret=app_secret)
            registry.register(broker)
            await registry.authenticate_all()
    except Exception as e:
        # Non-fatal — server still starts; live data tools will return errors
        sys.stderr.write(f"[theta-lab] Schwab broker init failed: {e}\n")


async def _run_stdio():
    await _init_schwab_broker()
    async with stdio_server() as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())


async def _run_http(host: str, port: int, token: str | None):
    import uvicorn
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Mount, Route

    await _init_schwab_broker()

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        if token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {token}":
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    async def handle_messages(request: Request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )

    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    sys.stderr.write(f"[theta-lab] HTTP/SSE server listening on http://{host}:{port}/sse\n")
    if token:
        sys.stderr.write(f"[theta-lab] Auth: Bearer token required (THETA_LAB_TOKEN)\n")
    else:
        sys.stderr.write(f"[theta-lab] Auth: NONE — set THETA_LAB_TOKEN env var to enable\n")
    await server.serve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Theta-Lab MCP Server")
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio",
        help="Transport mode: stdio (default, for Claude Code) or http (for remote agents)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8765, help="HTTP port (default: 8765)")
    args = parser.parse_args()

    token = os.getenv("THETA_LAB_TOKEN")  # optional bearer token for HTTP mode

    if args.transport == "http":
        asyncio.run(_run_http(args.host, args.port, token))
    else:
        asyncio.run(_run_stdio())
