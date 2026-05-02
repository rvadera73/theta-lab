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
from datetime import date, datetime
from pathlib import Path

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

# Add mcp dir to path so relative imports work
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

from config import ACCOUNT_A, ACCOUNT_B, UNIVERSE, Tier, PERMANENT_EXITS, RISK
from analysis.iv_rank import get_iv_rank, batch_iv_rank
from analysis.regime import detect_regime
from reports.weekly_report import generate_weekly_report
from reports.india_weekly_report import generate_india_weekly_report

# Account hashes from environment (set after Schwab API setup)
ACCOUNT_A_HASH = os.getenv("SCHWAB_ACCOUNT_A_HASH", "")
ACCOUNT_B_HASH = os.getenv("SCHWAB_ACCOUNT_B_HASH", "")
ACCOUNT_C_HASH = os.getenv("SCHWAB_ACCOUNT_C_HASH", "")

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
                "Detects current market regime (BEAR_SIDEWAYS, TRANSITIONING, BULL) "
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
                        "enum": ["A", "B", "both"],
                        "description": "Which account(s) to analyse",
                        "default": "both",
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
                        "enum": ["A", "B", "both"],
                        "default": "both",
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
                        "enum": ["A", "B", "both"],
                        "default": "both",
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
                    "account": {"type": "string", "enum": ["A", "B"]},
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
                    "account": {"type": "string", "enum": ["A", "B"]},
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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "generate_weekly_action_report":
            report = await generate_weekly_report(ACCOUNT_A_HASH, ACCOUNT_B_HASH, ACCOUNT_C_HASH)
            if arguments.get("save_to_file", True):
                log_path = Path(__file__).parent.parent / "logs" / f"action_report_{date.today()}.md"
                log_path.write_text(report)
            return [TextContent(type="text", text=report)]

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
            if not ACCOUNT_A_HASH and not ACCOUNT_B_HASH:
                return [TextContent(type="text", text=_no_credentials_message())]
            from schwab_client import get_all_positions, get_quotes
            from analysis.pnl import parse_schwab_positions
            from config import Regime, PROFIT_TARGETS
            regime_data = detect_regime()
            regime = regime_data["regime"]
            account_filter = arguments.get("account", "both")
            acct_map = []
            if account_filter in ("A", "both") and ACCOUNT_A_HASH:
                acct_map.append((ACCOUNT_A_HASH, "A"))
            if account_filter in ("B", "both") and ACCOUNT_B_HASH:
                acct_map.append((ACCOUNT_B_HASH, "B"))
            lines = [f"## Portfolio P&L — Account {account_filter.upper()}", f"**Regime:** {regime} | **Profit target:** {int(PROFIT_TARGETS[Regime(regime)][0]*100)}-{int(PROFIT_TARGETS[Regime(regime)][1]*100)}%", ""]
            for acct_hash, acct_label in acct_map:
                try:
                    raw = await get_all_positions(acct_hash)
                    symbols = list({
                        (p.get("instrument", {}).get("underlyingSymbol")
                         or p.get("instrument", {}).get("symbol", "").split()[0])
                        for p in raw if p.get("instrument", {}).get("assetType") in ("EQUITY", "OPTION")
                    })
                    quotes = await get_quotes(symbols)
                    positions = parse_schwab_positions(raw, acct_label, quotes)
                    positions.sort(key=lambda p: p.combined_net_pnl)
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
                except Exception as e:
                    lines.append(f"⚠️ Account {acct_label} error: {e}")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "scan_profit_take_candidates":
            if not ACCOUNT_A_HASH and not ACCOUNT_B_HASH:
                return [TextContent(type="text", text=_no_credentials_message())]
            from schwab_client import get_all_positions, get_quotes
            from analysis.pnl import parse_schwab_positions
            from config import Regime, PROFIT_TARGETS
            regime_data = detect_regime()
            regime = regime_data["regime"]
            low, high = PROFIT_TARGETS[Regime(regime)]
            account_filter = arguments.get("account", "both")
            acct_map = []
            if account_filter in ("A", "both") and ACCOUNT_A_HASH:
                acct_map.append((ACCOUNT_A_HASH, "A"))
            if account_filter in ("B", "both") and ACCOUNT_B_HASH:
                acct_map.append((ACCOUNT_B_HASH, "B"))
            candidates = []
            for acct_hash, acct_label in acct_map:
                try:
                    raw = await get_all_positions(acct_hash)
                    symbols = list({
                        (p.get("instrument", {}).get("underlyingSymbol")
                         or p.get("instrument", {}).get("symbol", "").split()[0])
                        for p in raw if p.get("instrument", {}).get("assetType") in ("EQUITY", "OPTION")
                    })
                    quotes = await get_quotes(symbols)
                    positions = parse_schwab_positions(raw, acct_label, quotes)
                    for pos in positions:
                        sig = pos.profit_take_signal(regime)
                        if sig["signal"]:
                            candidates.append((pos, acct_label, sig))
                except Exception as e:
                    pass
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
            if not ACCOUNT_A_HASH and not ACCOUNT_B_HASH:
                return [TextContent(type="text", text=_no_credentials_message())]
            from schwab_client import get_all_positions, get_quotes
            from analysis.pnl import parse_schwab_positions
            from config import RISK
            account_filter = arguments.get("account", "both")
            acct_map = []
            if account_filter in ("A", "both") and ACCOUNT_A_HASH:
                acct_map.append((ACCOUNT_A_HASH, "A"))
            if account_filter in ("B", "both") and ACCOUNT_B_HASH:
                acct_map.append((ACCOUNT_B_HASH, "B"))
            roll_items = []
            for acct_hash, acct_label in acct_map:
                try:
                    raw = await get_all_positions(acct_hash)
                    symbols = list({
                        (p.get("instrument", {}).get("underlyingSymbol")
                         or p.get("instrument", {}).get("symbol", "").split()[0])
                        for p in raw if p.get("instrument", {}).get("assetType") in ("EQUITY", "OPTION")
                    })
                    quotes = await get_quotes(symbols)
                    positions = parse_schwab_positions(raw, acct_label, quotes)
                    for pos in positions:
                        roll = pos.roll_signal()
                        loss = pos.loss_flag()
                        itm_legs = [lg for lg in pos.option_legs if
                                    (lg.option_type == "PUT" and pos.current_price < lg.strike) or
                                    (lg.option_type == "CALL" and pos.current_price > lg.strike)]
                        if roll["signal"] or loss["flag"] or itm_legs:
                            roll_items.append({
                                "pos": pos, "acct": acct_label,
                                "roll": roll, "loss": loss,
                                "itm_legs": itm_legs,
                                "priority": 1 if (loss["flag"] or any(lg.dte <= 13 for lg in pos.option_legs)) else 2,
                            })
                except Exception as e:
                    pass
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
                    f"Trader override: BEAR_SIDEWAYS through Oct/Nov 2026\n\n"
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
