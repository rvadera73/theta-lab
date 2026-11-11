"""
report_utils.py -- Bolt b19 split.

This file used to be 1502 lines (over this repo's 1000-line Code Quality &
Modularity Gate file cap). The code has been split into focused sibling
submodules under mcp/reports/ by responsibility:

  report_utils_core.py            -- filesystem/snapshot/CSV-field parsing,
                                      calendar math, display formatting,
                                      HTML/email report output.
  report_utils_pricing.py         -- India symbol mapping, technical
                                      snapshot, upcoming earnings, option-
                                      chain pricing/probability-ITM.
  report_utils_positions_us.py    -- Schwab snapshot/transaction parsing,
                                      Schwab-snapshot-vs-transactions source
                                      selection, open-leg reconstruction,
                                      position-CSV loading.
  report_utils_positions_india.py -- Breeze/ICICI position mapping.
  report_utils_kpis.py            -- premium/KPI aggregation, per-position
                                      action/priority/delta signal helpers.

This file is now a thin shim: it re-exports every name from those
submodules explicitly (not a bare `import *`, since several real names --
_INDIA_SYMBOL_MAP, _clean_money, _dte_from_expiry, etc. -- are intentionally
underscore-prefixed, and a bare `import *` silently drops those), so every
existing `from report_utils import X` / `import report_utils` call site
across the repo keeps working completely unchanged.

A handful of functions/globals stay PHYSICALLY DEFINED here rather than
moving out: _now, _today, _history_cache, current_price,
get_extended_hours_quote, _extended_hours_is_usable,
get_cached_extended_hours_quote, overnight_move_pct, extended_hours_context,
_snapshot_holdings (+ _SNAPSHOT_HOLDINGS_CACHE), _fill_current_marks,
load_robinhood_positions, _record_account_failure, load_us_positions.
Several existing regression tests (tests/test_report_utils_cache_freshness.py,
tests/test_extended_hours_pricing.py, tests/test_robinhood_netting.py) do
`mock.patch.object(report_utils, "<name>", ...)` for exactly these names
while exercising ANOTHER one of these same functions -- that kind of patch
only takes effect if the patched name and its caller resolve the same bare
module-global at call time, i.e. are defined in the exact same module
object. Moving either half of such a pair into a different file would
silently stop the existing test's patch from working, without any import
error to flag it. Every name in the sibling submodules was confirmed (by
reading every existing test in the repo) to never be the target of that
kind of cross-function patching, so those are free to live in their own
files.
"""
import asyncio
import calendar
import csv
import json
import logging
import math
import os
import re
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import yaml

import sys as _sys
_p = os.path.dirname(os.path.abspath(__file__))
for _ in range(5):
    _cand = os.path.join(_p, "mcp", "analysis")
    if os.path.isdir(_cand):
        _sys.path.insert(0, _cand)
        break
    _p = os.path.dirname(_p)
import yahoo_throttle  # noqa: F401 -- installs the global cross-process Yahoo rate limiter, must run before any yfinance call
import yfinance as yf

# This module's own directory (mcp/reports/) -- so `robinhood_netting`
# (a sibling module, see docs/design/adr/0003-robinhood-position-ingestion.md)
# and the new report_utils_* sibling submodules are bare-importable
# regardless of whether this file was reached via server.py's
# "reports.report_utils" package import (which only puts mcp/ itself on
# sys.path) or a test's own flat sys.path setup.
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in _sys.path:
    _sys.path.insert(0, _this_dir)

from bootstrap import load_credentials as _load_credentials


_load_credentials()

from analysis.metrics import breakeven_velocity, premium_capture_rate, profit_factor, sortino_ratio
from analysis.same_day_cache import ensure_same_day, same_day_json_cache
from analysis.pnl import OptionLeg, Position, parse_schwab_positions
from analysis.india_statement_parser import build_positions_from_statements, load_india_config
from config import PORTFOLIO, RISK, PERMANENT_EXITS, OVERNIGHT_MOVE_GATE_PCT
from routines.email_report import send_email
from robinhood_netting import parse_robinhood_transaction_csv, net_robinhood_option_legs

# ---------------------------------------------------------------------------
# Sibling submodules -- explicit re-export (see this file's own docstring for
# why not a bare `import *`). Safe to import right away: every cross-
# reference these submodules make back into THIS module's own
# forced-to-stay cluster (current_price/_today/_history_cache/
# _fill_current_marks/etc., see below) is a deferred, function-body-local
# import, resolved only when that function is actually CALLED -- by which
# point this module has finished executing and defined everything below.
# ---------------------------------------------------------------------------
from report_utils_core import (  # noqa: F401 -- re-exported for callers
    PROJECT_ROOT, DATA_DIR, STATEMENTS_DIR, LOGS_DIR, SNAPSHOT_FILE,
    TO_EMAIL, FROM_EMAIL, _ACCOUNT_FILES, _EXCLUDED_FILE_STEMS,
    ensure_logs_dir, load_snapshot, latest_file, load_account_transactions,
    parse_amount, parse_qty, parse_txn_date,
    month_window, previous_month, month_name, month_days, project_value,
    fmt_money, fmt_inr, safe_div, compute_rsi,
    save_html, maybe_send,
)
from report_utils_pricing import (  # noqa: F401 -- re-exported for callers
    _INDIA_SYMBOL_MAP, _OPTION_CHAIN_CACHE, _OPTION_CHAIN_CACHE_DATE,
    _EARNINGS_CACHE, _EARNINGS_CACHE_DATE,
    yf_symbol, technical_snapshot, upcoming_earnings, parse_option_symbol,
    option_market_price, option_probability_itm,
)
from report_utils_positions_us import (  # noqa: F401 -- re-exported for callers
    _SCHWAB_SNAPSHOT_FILE, _SCHWAB_OPT_SYMBOL, _clean_money,
    reconstruct_open_option_legs, load_position_csv, fallback_us_positions,
    schwab_source_choice, load_schwab_from_snapshot,
    reconstruct_positions_from_transactions,
)
from report_utils_positions_india import (  # noqa: F401 -- re-exported for callers
    _dte_from_expiry, _map_breeze_to_positions, _map_breeze_equity_holdings,
    load_india_positions,
)
from report_utils_kpis import (  # noqa: F401 -- re-exported for callers
    monthly_premium, monthly_option_pnl_series, combined_kpis,
    priority_from_position, action_for_option_leg, estimate_delta,
)

_US_PRICE_CACHE: dict[str, dict[str, Any]] = {}
_INDIA_PRICE_CACHE: dict[str, dict[str, Any]] = {}

# _OPTION_CHAIN_CACHE / _EARNINGS_CACHE now live in report_utils_pricing.py
# (re-exported above).

# How long a cached price is trusted before _history_cache() re-fetches it.
# Found live 2026-11-05: this cache previously had NO expiry at all, so a
# long-running MCP server process (container uptime since 2026-11-04 17:04
# UTC) served the SAME frozen price through an overnight earnings move and a
# +22% pre-market rally the next day -- confirmed via a direct yfinance pull
# showing the real contemporaneous price was $331+ while this cache kept
# returning a mid-session Nov-4 print of $236.94. 15 minutes bounds the
# worst case to "one refresh cycle," not "the life of the process," without
# re-fetching on every single call during normal use.
_PRICE_CACHE_TTL_SECONDS = 900

_logger = logging.getLogger(__name__)


def _now() -> float:
    """Isolated so tests can freeze/advance time without real sleeping."""
    return time.time()


def _today() -> str:
    """Isolated so tests can simulate a day change without real waiting."""
    return date.today().isoformat()


def _history_cache(symbol: str, india: bool = False):
    cache = _INDIA_PRICE_CACHE if india else _US_PRICE_CACHE
    key = yf_symbol(symbol, india)
    cached = cache.get(key)
    if cached is not None and (_now() - cached.get("fetched_at", 0)) < _PRICE_CACHE_TTL_SECONDS:
        return cached
    try:
        ticker = yf.Ticker(key)
        hist = ticker.history(period="1y", auto_adjust=False)
        cache[key] = {"ticker": ticker, "hist": hist, "fetched_at": _now()}
    except Exception:
        cache[key] = {"ticker": None, "hist": None, "fetched_at": _now()}
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


_EXTENDED_HOURS_CACHE_FILE = DATA_DIR / "extended_hours_cache.json"


def get_extended_hours_quote(symbol: str) -> dict[str, Any]:
    """Live extended-hours price signal for `symbol` (ADR 0004,
    docs/design/adr/0004-extended-hours-pricing-signal.md). Uses
    yfinance's Ticker.info, NOT fast_info -- verified LIVE 2026-11-09
    against AAPL and APP during regular trading hours: fast_info's schema
    has no preMarketPrice/postMarketPrice/marketState keys at all, so it
    structurally cannot distinguish a pre/post-market quote from a regular
    one, while .info carries marketState ("PRE"/"POST"/"REGULAR"/"CLOSED")
    plus real preMarketPrice/postMarketPrice fields that Yahoo only
    populates outside regular hours. Never raises (same fail-quiet
    convention as premium_yield.get_yield_on_capital) -- a failure or an
    unresolvable quote comes back with live_price=None and an "error" key,
    not an exception.
    """
    try:
        info = yf.Ticker(symbol).info
        market_state = info.get("marketState")
        regular_price = info.get("regularMarketPrice") or info.get("currentPrice")
        pre_price = info.get("preMarketPrice")
        post_price = info.get("postMarketPrice")

        if market_state in ("PRE", "PREPRE") and pre_price:
            return {"symbol": symbol, "live_price": round(float(pre_price), 2), "live_price_source": "pre_market"}
        if market_state in ("POST", "POSTPOST") and post_price:
            return {"symbol": symbol, "live_price": round(float(post_price), 2), "live_price_source": "after_hours"}
        if regular_price:
            return {"symbol": symbol, "live_price": round(float(regular_price), 2), "live_price_source": "regular"}
        return {"symbol": symbol, "live_price": None, "live_price_source": None, "error": "no_live_price"}
    except Exception as exc:
        return {"symbol": symbol, "live_price": None, "live_price_source": None, "error": str(exc)}


def _extended_hours_is_usable(entry: dict) -> bool:
    """Same convention as premium_yield._is_usable / symbol_context._is_usable:
    only a quote that actually resolved a live_price is worth caching."""
    return not entry.get("error") and entry.get("live_price") is not None


def get_cached_extended_hours_quote(symbol: str) -> dict[str, Any]:
    """Same-day cache, built on the shared same_day_json_cache helper
    (mirrors premium_yield.get_cached_batch_yield's JSON disk-cache shape
    exactly -- date-keyed file, stale/unusable entries dropped on read so a
    transient failure cached earlier today never blocks a retry) -- this
    codebase's established same-day caching pattern for per-symbol
    enrichment data (ADR 0004), not a new mechanism. One extra yfinance call
    per symbol per refresh cycle, not per request."""
    today = _today()
    cached = same_day_json_cache(
        _EXTENDED_HOURS_CACHE_FILE, today, [symbol],
        loader_fn=lambda missing: {missing[0]: get_extended_hours_quote(missing[0])},
        is_usable=_extended_hours_is_usable,
    )
    return cached[symbol]


def overnight_move_pct(regular_close_price: float | None, live_price: float | None) -> float | None:
    """The live extended-hours price vs. the regular-session close already
    used for margin/P&L math -- a read-only signal, never fed back into any
    dollar calculation (ADR 0004)."""
    if not regular_close_price or live_price is None:
        return None
    return round((live_price - regular_close_price) / regular_close_price * 100, 2)


def extended_hours_context(symbol: str, regular_close_price: float | None) -> dict[str, Any]:
    """One-stop per-symbol extended-hours annotation -- live_price/
    live_price_source/overnight_move_pct, plus gates_fired containing
    "OVERNIGHT_MOVE" when abs(overnight_move_pct) exceeds
    OVERNIGHT_MOVE_GATE_PCT (mcp/config.py). Shared by every per-leg/
    per-symbol pricing output path (dashboard Position Heat,
    get_position_detail, scan_position_heat, get_live_positions) so the
    field/gate shape can't drift between them (ADR 0004)."""
    quote = get_cached_extended_hours_quote(symbol)
    live_price = quote.get("live_price")
    source = quote.get("live_price_source")
    move_pct = overnight_move_pct(regular_close_price, live_price)
    gates = ["OVERNIGHT_MOVE"] if (move_pct is not None and abs(move_pct) > OVERNIGHT_MOVE_GATE_PCT) else []
    return {
        "live_price": live_price,
        "live_price_source": source,
        "overnight_move_pct": move_pct,
        "gates_fired": gates,
    }


_SNAPSHOT_HOLDINGS_CACHE: dict[str, Any] | None = None  # {"date": iso-date, "holdings": set}


def _snapshot_holdings() -> set:
    """Ground-truth held tickers from the position SNAPSHOTS (accurate, no phantoms).
    Uses open_positions_loader_v2 but skips the Yahoo price fetch for speed.
    Same-day cache (found live 2026-11-05: this previously cached its result
    for the life of the process with no expiry at all -- get_position_detail
    filters through this set, and a long-running server missed a real
    Fidelity position that only entered the snapshot after the cache had
    already been populated; a fresh process, with no cache yet, found it
    immediately). Day-based, not a short TTL like _history_cache's price
    cache, since holdings only change when the trader exports a new
    snapshot -- matches symbol_context.py's existing same-day-cache
    convention for the same reason."""
    global _SNAPSHOT_HOLDINGS_CACHE
    today = _today()
    if _SNAPSHOT_HOLDINGS_CACHE is not None and _SNAPSHOT_HOLDINGS_CACHE.get("date") == today:
        return _SNAPSHOT_HOLDINGS_CACHE["holdings"]
    try:
        import sys
        sys.path.insert(0, "/home/rahulvadera/projects/theta-lab/scripts")
        from open_positions_loader_v2 import OpenPositionsLoaderV2
        loader = OpenPositionsLoaderV2()
        loader.load_all_data()
        holdings = set(loader.open_positions["ticker"].dropna().str.upper().unique())
    except Exception as exc:
        # Deliberately NOT cached (found in review, 2026-11-05): a transient
        # failure (e.g. a momentary lock while the snapshot file is being
        # written) must be retried on the NEXT call, not locked in as
        # "no holdings" for the rest of the calendar day -- the ground-truth
        # filter at this function's one call site fails OPEN on an empty set
        # (`if holdings: filter(...)`), so caching a failure silently
        # disables phantom-position filtering for the remainder of the day.
        _logger.warning("_snapshot_holdings: load failed, will retry next call -- %s: %s",
                         type(exc).__name__, exc)
        return set()
    _SNAPSHOT_HOLDINGS_CACHE = {"date": today, "holdings": holdings}
    return holdings


def _fill_current_marks(lookups: list[tuple[str, str, float, str, "OptionLeg"]]) -> None:
    """Live cost-to-close for each leg in `lookups`, via yfinance's option chain
    (mid of bid/ask) -- batched one chain fetch per (symbol, expiry) pair rather
    than per leg, since several strikes on the same underlying/expiry share one
    chain. Never raises: a failed symbol/expiry just leaves current_mark at 0
    for its legs (same non-fatal-per-item policy as the rest of this loader) --
    heat_scanner.py's own NO_PRICE/UNKNOWN handling is the right place to
    surface that, not an exception here."""
    by_chain: dict[tuple[str, str], list[tuple[float, str, "OptionLeg"]]] = defaultdict(list)
    for symbol, expiry, strike, opt_type, leg in lookups:
        by_chain[(symbol, expiry)].append((strike, opt_type, leg))

    for (symbol, expiry), legs in by_chain.items():
        try:
            chain = yf.Ticker(symbol).option_chain(expiry)
        except Exception:
            continue
        for strike, opt_type, leg in legs:
            table = chain.calls if opt_type == "CALL" else chain.puts
            row = table[table["strike"] == strike]
            if row.empty:
                continue
            bid = float(row["bid"].iloc[0] or 0)
            ask = float(row["ask"].iloc[0] or 0)
            mid = (bid + ask) / 2 if (bid > 0 and ask > 0) else max(bid, ask, float(row["lastPrice"].iloc[0] or 0))
            qty = abs(leg.quantity)
            leg.current_mark = round(mid * 100 * qty, 2)


def load_robinhood_positions(csv_path: str, account_label: str) -> list[Position]:
    """
    Parse a REAL Robinhood transaction-log export (ADR 0003,
    docs/design/adr/0003-robinhood-position-ingestion.md) into Position/
    OptionLeg objects -- replaces the old parse_robinhood_csv(), which
    required a "Symbol" header no real Robinhood export has ever had and
    therefore always returned [] against this account's actual files.

    Mirrors reconstruct_positions_from_transactions()'s established pattern
    in this same module: net the transaction log via the shared
    mcp/reports/robinhood_netting.py helpers, build OptionLeg objects with a
    current_mark=0 placeholder, then backfill real cost-to-close via the
    same _fill_current_marks() live option-chain lookup every other
    transaction-reconstructed leg already uses.
    """
    rows = parse_robinhood_transaction_csv(csv_path)
    legs = net_robinhood_option_legs(rows)

    positions: dict[str, Position] = {}
    pending_mark_lookups: list[tuple[str, str, float, str, "OptionLeg"]] = []

    for leg_data in legs:
        leg, lookup = _robinhood_leg_to_option_leg(leg_data)
        ticker = leg_data["ticker"]
        if ticker not in positions:
            positions[ticker] = Position(
                symbol=ticker, account=account_label,
                shares=0, stock_cost_basis=0.0, current_price=0.0,
            )
        positions[ticker].option_legs.append(leg)
        pending_mark_lookups.append(lookup)

    _fill_current_marks(pending_mark_lookups)

    return list(positions.values())


def _robinhood_leg_to_option_leg(leg_data: dict) -> tuple["OptionLeg", tuple[str, str, float, str, "OptionLeg"]]:
    """One netted robinhood_netting.py leg dict -> (OptionLeg,
    pending-mark-lookup tuple). Split out of load_robinhood_positions() to
    keep that function under the Code Quality Gate's 50-line cap."""
    is_short = leg_data["quantity"] < 0
    contracts = int(abs(leg_data["quantity"]))
    leg = OptionLeg(
        description=f"{leg_data['option_type']} {leg_data['strike']} {leg_data['expiry']}",
        strike=leg_data["strike"],
        expiry=leg_data["expiry"],
        option_type=leg_data["option_type"],
        quantity=-contracts if is_short else contracts,
        # Net credit only means "premium received" for a short leg; a
        # net-long leg's net_credit is a net debit (cost basis paid),
        # which OptionLeg has no slot for -- matches every other
        # broker's own parser convention here (parse_fidelity_csv etc.
        # also hardcode premium_received=0.0 for a long leg).
        premium_received=max(0.0, leg_data["net_credit"]) if is_short else 0.0,
        current_mark=0.0,  # filled in below via a live option-chain lookup
        dte=leg_data["dte"],
    )
    lookup = (leg_data["ticker"], leg_data["expiry"], leg_data["strike"], leg_data["option_type"], leg)
    return leg, lookup


def _record_account_failure(errors: list[str], label: str, exc: Exception) -> None:
    """A per-account load failure stays non-fatal (one bad account must
    never block the other 7), but must be VISIBLE, not indistinguishable
    from "this account genuinely doesn't hold the symbol" -- found live
    2026-11-05: `except Exception: pass` here meant a transient per-account
    failure and a real absence looked identical to every caller. Logged
    immediately (so it shows up in server logs even if a caller ignores the
    returned warning) and recorded into `errors` so load_us_positions()'s
    own "warning" field -- previously hardcoded to None -- can actually
    report it."""
    message = f"{label}: {type(exc).__name__}: {exc}"
    _logger.warning("load_us_positions: account load failed -- %s", message)
    errors.append(message)


def _load_schwab_account_positions(label: str, cfg: dict) -> tuple[list[Position] | None, dict | None]:
    """One Schwab account: snapshot-vs-transactions source selection (see
    schwab_source_choice()'s own docstring for why) + positions. Returns
    (None, None) if nothing could be loaded either way. May raise -- the
    caller (load_us_positions()) records the failure via
    _record_account_failure instead of letting one bad account block the
    rest."""
    snapshot_path = DATA_DIR / "positions" / _SCHWAB_SNAPSHOT_FILE.get(label, "")
    txn_pattern = {
        "A": "Individual_XXX232_Transactions_*.csv",
        "B": "Contributory_XXX275_Transactions_*.csv",
        "C": "Designated_Bene_Individual_XXX634_Transactions_*.csv",
    }.get(label, "")
    txn_files = list((DATA_DIR / "positions").glob(txn_pattern)) + list(STATEMENTS_DIR.glob(txn_pattern))
    txn_mtime = max((f.stat().st_mtime for f in txn_files), default=0)
    snapshot_mtime = snapshot_path.stat().st_mtime if snapshot_path.exists() else -1

    positions = None
    used_source, used_mtime = "transactions", txn_mtime
    if schwab_source_choice(snapshot_mtime, txn_mtime) == "snapshot":
        positions = load_schwab_from_snapshot(label)
        if positions:
            used_source, used_mtime = "snapshot", snapshot_mtime
    if not positions:
        positions = reconstruct_positions_from_transactions(label)
        used_source, used_mtime = "transactions", txn_mtime
    if not positions:
        return None, None

    as_of = datetime.fromtimestamp(used_mtime).date().isoformat() if used_mtime > 0 else None
    days_stale = (date.today() - datetime.fromtimestamp(used_mtime).date()).days if used_mtime > 0 else None
    return positions, {"source": used_source, "as_of": as_of, "days_stale": days_stale}


def _csv_account_source_entry(broker: str, file_mtime: float) -> dict:
    """account_sources parity with the Schwab loop (ADR 0004) -- previously
    only Schwab populated this, so data_source/data_as_of/days_stale came
    back None for every Fidelity/Vanguard/Robinhood leg downstream. The
    returned "as_of"/"days_stale" are the backing CSV export's own file
    age, same meaning as the Schwab snapshot/transactions mtime."""
    as_of_date = datetime.fromtimestamp(file_mtime).date()
    return {"source": broker, "as_of": as_of_date.isoformat(), "days_stale": (date.today() - as_of_date).days}


def _load_fidelity_account_positions(label: str, cfg: dict) -> tuple[list[Position], dict | None]:
    from analysis.pnl import parse_fidelity_csv

    csv_path = os.getenv(cfg.get("csv_path_env", ""), "")
    if not csv_path or not os.path.exists(csv_path):
        return [], None
    per_acct = parse_fidelity_csv(csv_path, account_filter=cfg.get("fidelity_account_number"))
    positions: list[Position] = []
    for _, pos_list in per_acct.items():
        for pos in pos_list:
            pos.account = label
        positions.extend(pos_list)
    return positions, _csv_account_source_entry("fidelity_csv", os.path.getmtime(csv_path))


def _load_robinhood_account_positions(label: str, cfg: dict) -> tuple[list[Position], dict | None]:
    csv_path = os.getenv(cfg.get("csv_path_env", ""), "")
    if not csv_path or not os.path.exists(csv_path):
        return [], None
    positions = load_robinhood_positions(csv_path, account_label=label)
    return positions, _csv_account_source_entry("robinhood_csv", os.path.getmtime(csv_path))


def _load_vanguard_account_positions(label: str, cfg: dict) -> tuple[list[Position], dict | None]:
    from analysis.pnl import parse_vanguard_csv, parse_vanguard_pdf

    pdf_path = os.getenv(cfg.get("pdf_path_env", ""), "")
    csv_path = os.getenv(cfg.get("csv_path_env", ""), "")
    if pdf_path and os.path.exists(pdf_path):
        positions = parse_vanguard_pdf(pdf_path, account_label=label)
        used_path = pdf_path
    elif csv_path and os.path.exists(csv_path):
        positions = parse_vanguard_csv(csv_path, account_label=label)
        used_path = csv_path
    else:
        return [], None
    return positions, _csv_account_source_entry("vanguard_csv", os.path.getmtime(used_path))


_CSV_ACCOUNT_LOADERS = {
    "fidelity_csv": _load_fidelity_account_positions,
    "robinhood_csv": _load_robinhood_account_positions,
    "vanguard_csv": _load_vanguard_account_positions,
}


def _backfill_missing_prices(all_positions: list[Position]) -> None:
    """Live Yahoo Finance call for any position current_price() didn't
    already set (mutates in place). The CSV parsers only set current_price
    from an OWNED-EQUITY row in the export; a pure options position (short
    put/call with no shares held — the normal case for cash-secured puts
    and naked calls, i.e. most of this book) has no such row, so the merge
    step hardcoded current_price=0.0 as a placeholder and NEVER actually
    called Yahoo for it. That silently cascaded into scan_position_heat/
    scan_profit_take_candidates/scan_roll_candidates treating the majority
    of open legs as NO_PRICE (found: 49 of 55 legs) — not a Yahoo outage, a
    code path that skipped the live lookup entirely for anything without
    owned shares."""
    for pos in all_positions:
        if not pos.current_price or pos.current_price <= 0:
            live = current_price(pos.symbol)
            if live:
                pos.current_price = live


def _apply_snapshot_ground_truth_filter(all_positions: list[Position]) -> list[Position]:
    """Applies to BOTH parser and fallback positions: drop any position not
    in the actual position snapshots — removes phantoms from incomplete/
    orphaned transaction history."""
    holdings = _snapshot_holdings()
    if holdings:
        return [p for p in all_positions if str(p.symbol).upper() in holdings]
    return all_positions


def _load_all_schwab_positions(accounts: dict, all_positions: list[Position],
                                account_sources: dict, load_errors: list[str]) -> None:
    """Schwab accounts — from the current position snapshot when it's at
    least as fresh as the transactions file, else reconstructed from
    transaction history (NO live API either way; file+Yahoo only). See
    _load_schwab_account_positions()'s own docstring for why the snapshot
    is preferred whenever it's current. Mutates all_positions/
    account_sources/load_errors in place (non-fatal per account)."""
    for label, cfg in accounts.items():
        if cfg.get("broker") != "schwab":
            continue
        try:
            positions, source_entry = _load_schwab_account_positions(label, cfg)
            if positions:
                all_positions.extend(positions)
                account_sources[label] = source_entry
        except Exception as exc:
            _record_account_failure(load_errors, label, exc)  # never block on one account


def _load_all_csv_positions(accounts: dict, all_positions: list[Position],
                             account_sources: dict, load_errors: list[str]) -> None:
    """CSV-based accounts (fidelity_csv/robinhood_csv/vanguard_csv), each
    non-fatal. Mutates all_positions/account_sources/load_errors in place."""
    for label, cfg in accounts.items():
        loader = _CSV_ACCOUNT_LOADERS.get(cfg.get("broker"))
        if loader is None:
            continue
        try:
            positions, source_entry = loader(label, cfg)
            if positions:
                all_positions.extend(positions)
            if source_entry:
                account_sources[label] = source_entry
        except Exception as exc:
            _record_account_failure(load_errors, label, exc)  # never block on one account


async def load_us_positions() -> dict[str, Any]:
    """
    Load all US positions from every configured account in the ACCOUNTS registry.
    Schwab accounts fetched live in parallel; CSV-based accounts loaded from file.
    Non-fatal per account — one failure never blocks others, but every
    failure is recorded (see _record_account_failure) into this function's
    own "warning" field instead of being silently indistinguishable from
    "this account has no position in this symbol."
    """
    from config import ACCOUNTS

    all_positions: list[Position] = []
    balances: dict[str, dict[str, Any]] = {}
    # Which real source + how current it was, per account -- lets any caller
    # (e.g. Position Heat) show "based on data from N days ago" per leg
    # instead of silently trusting whichever file happened to load.
    account_sources: dict[str, dict[str, Any]] = {}
    load_errors: list[str] = []

    _load_all_schwab_positions(ACCOUNTS, all_positions, account_sources, load_errors)
    _load_all_csv_positions(ACCOUNTS, all_positions, account_sources, load_errors)

    # If the live parsers produced nothing, use the fallback dataset as the source.
    data_source = "LIVE"
    if not all_positions:
        fb = fallback_us_positions()
        all_positions = fb.get("positions", [])
        data_source = fb.get("data_source", "SNAPSHOT")

    _backfill_missing_prices(all_positions)
    all_positions = _apply_snapshot_ground_truth_filter(all_positions)

    return {
        "positions": all_positions,
        "balances": balances,
        "data_source": data_source,
        "warning": "; ".join(load_errors) if load_errors else None,
        "snapshot": load_snapshot(),
        "transactions": load_account_transactions(),
        "account_sources": account_sources,
    }
