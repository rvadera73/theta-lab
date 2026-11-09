"""
Regression tests for ADR 0004
(docs/design/adr/0004-extended-hours-pricing-signal.md): the new
extended-hours overnight-move signal in mcp/reports/report_utils.py, and
staleness-field (data_source/data_as_of/days_stale) parity across all 4
broker types in load_us_positions()'s account_sources, previously populated
only for Schwab.

Real incident this guards against (2026-11-05): AppLovin (APP) gapped +22%
pre-market on an earnings beat-and-raise, but every pricing path
(scan_position_heat, get_live_positions, get_position_detail) still showed
the prior regular-session close, with nothing anywhere distinguishing
"fresh but stale-relative-to-an-overnight-move" from "actually current."

No pytest dependency -- run directly: python3 tests/test_extended_hours_pricing.py
"""
import asyncio
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp"))
sys.path.insert(0, str(ROOT / "mcp" / "reports"))
sys.path.insert(0, str(ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(ROOT / "scripts"))

import report_utils  # noqa: E402
import config  # noqa: E402
import analysis.pnl as pnl_module  # noqa: E402
from analysis.pnl import Position, OptionLeg  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


class _FakeInfoTicker:
    """Mimics yf.Ticker(symbol).info -- the real field this codebase's
    get_extended_hours_quote reads. fast_info is deliberately NOT faked
    here since the production code never touches it (see the ADR's live
    verification note: fast_info's schema has no pre/post-market fields at
    all)."""
    def __init__(self, symbol, info):
        self.symbol = symbol
        self.info = info


# ---------------------------------------------------------------------------
# get_extended_hours_quote() -- distinguishes pre-market / after-hours / regular
# ---------------------------------------------------------------------------
print("get_extended_hours_quote() market-state classification")

with mock.patch.object(report_utils.yf, "Ticker",
                        side_effect=lambda s: _FakeInfoTicker(s, {
                            "marketState": "PRE",
                            "regularMarketPrice": 100.0,
                            "preMarketPrice": 122.0,
                            "postMarketPrice": None,
                        })):
    q = report_utils.get_extended_hours_quote("TESTSYM")
    check("PRE market state picks preMarketPrice", q["live_price"] == 122.0, f"got {q}")
    check("PRE market state labeled pre_market", q["live_price_source"] == "pre_market", f"got {q}")

with mock.patch.object(report_utils.yf, "Ticker",
                        side_effect=lambda s: _FakeInfoTicker(s, {
                            "marketState": "POST",
                            "regularMarketPrice": 100.0,
                            "preMarketPrice": None,
                            "postMarketPrice": 88.0,
                        })):
    q = report_utils.get_extended_hours_quote("TESTSYM")
    check("POST market state picks postMarketPrice", q["live_price"] == 88.0, f"got {q}")
    check("POST market state labeled after_hours", q["live_price_source"] == "after_hours", f"got {q}")

with mock.patch.object(report_utils.yf, "Ticker",
                        side_effect=lambda s: _FakeInfoTicker(s, {
                            "marketState": "REGULAR",
                            "regularMarketPrice": 100.0,
                            "preMarketPrice": None,
                            "postMarketPrice": None,
                        })):
    q = report_utils.get_extended_hours_quote("TESTSYM")
    check("REGULAR market state picks regularMarketPrice", q["live_price"] == 100.0, f"got {q}")
    check("REGULAR market state labeled regular", q["live_price_source"] == "regular", f"got {q}")

with mock.patch.object(report_utils.yf, "Ticker",
                        side_effect=lambda s: _FakeInfoTicker(s, {
                            "marketState": "PRE",
                            "regularMarketPrice": 100.0,
                            "preMarketPrice": None,  # Yahoo sometimes reports PRE with no quote yet
                            "postMarketPrice": None,
                        })):
    q = report_utils.get_extended_hours_quote("TESTSYM")
    check("PRE market state with no preMarketPrice falls back to regular",
          q["live_price"] == 100.0 and q["live_price_source"] == "regular", f"got {q}")


def _raise_ticker(symbol):
    raise RuntimeError("yfinance down")


with mock.patch.object(report_utils.yf, "Ticker", side_effect=_raise_ticker):
    q = report_utils.get_extended_hours_quote("TESTSYM")
    check("a fetch failure returns an error, not a crash",
          q["live_price"] is None and q.get("error"), f"got {q}")

# ---------------------------------------------------------------------------
# overnight_move_pct() -- plain arithmetic + None handling
# ---------------------------------------------------------------------------
print("\novernight_move_pct()")

check("a +22% overnight move computes correctly",
      report_utils.overnight_move_pct(236.94, 331.0) == round((331.0 - 236.94) / 236.94 * 100, 2),
      f"got {report_utils.overnight_move_pct(236.94, 331.0)}")
check("no regular close price -> None", report_utils.overnight_move_pct(None, 100.0) is None)
check("no live price -> None", report_utils.overnight_move_pct(100.0, None) is None)
check("zero regular close price -> None (no div-by-zero)", report_utils.overnight_move_pct(0.0, 100.0) is None)

# ---------------------------------------------------------------------------
# get_cached_extended_hours_quote() -- same-day cache (mirrors
# premium_yield.get_cached_batch_yield's convention, per ADR 0004)
# ---------------------------------------------------------------------------
print("\nget_cached_extended_hours_quote() same-day cache")

import tempfile
_tmp_cache = Path(tempfile.mkdtemp()) / "extended_hours_cache_test.json"
if _tmp_cache.exists():
    _tmp_cache.unlink()

_fetch_calls = {"n": 0}


def _fake_fresh_quote(symbol):
    _fetch_calls["n"] += 1
    return {"symbol": symbol, "live_price": 100.0 + _fetch_calls["n"], "live_price_source": "regular"}


with mock.patch.object(report_utils, "_EXTENDED_HOURS_CACHE_FILE", _tmp_cache), \
     mock.patch.object(report_utils, "get_extended_hours_quote", side_effect=_fake_fresh_quote), \
     mock.patch.object(report_utils, "_today", return_value="2026-11-09"):
    first = report_utils.get_cached_extended_hours_quote("CACHESYM")
    check("first call fetches live", first["live_price"] == 101.0, f"got {first}")
    second = report_utils.get_cached_extended_hours_quote("CACHESYM")
    check("a same-day call is served from cache (no refetch)",
          second["live_price"] == 101.0 and _fetch_calls["n"] == 1,
          f"got {second}, fetch_calls={_fetch_calls['n']}")

with mock.patch.object(report_utils, "_EXTENDED_HOURS_CACHE_FILE", _tmp_cache), \
     mock.patch.object(report_utils, "get_extended_hours_quote", side_effect=_fake_fresh_quote), \
     mock.patch.object(report_utils, "_today", return_value="2026-11-10"):
    third = report_utils.get_cached_extended_hours_quote("CACHESYM")
    check("a new-day call refetches instead of reusing yesterday's cache",
          third["live_price"] == 102.0 and _fetch_calls["n"] == 2,
          f"got {third}, fetch_calls={_fetch_calls['n']}")

_tmp_cache.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# extended_hours_context() -- the OVERNIGHT_MOVE gate
# ---------------------------------------------------------------------------
print("\nextended_hours_context() OVERNIGHT_MOVE gate")

with mock.patch.object(report_utils, "get_cached_extended_hours_quote",
                        return_value={"symbol": "APP", "live_price": 331.0, "live_price_source": "pre_market"}):
    ctx = report_utils.extended_hours_context("APP", 236.94)
    check("a +22% move (real APP incident figures) fires OVERNIGHT_MOVE",
          "OVERNIGHT_MOVE" in ctx["gates_fired"], f"got {ctx}")
    check("overnight_move_pct is the real ~+39.7% figure",
          ctx["overnight_move_pct"] > 10.0, f"got {ctx['overnight_move_pct']}")

with mock.patch.object(report_utils, "get_cached_extended_hours_quote",
                        return_value={"symbol": "QUIET", "live_price": 101.5, "live_price_source": "pre_market"}):
    ctx = report_utils.extended_hours_context("QUIET", 100.0)
    check("a +1.5% move does NOT fire OVERNIGHT_MOVE",
          "OVERNIGHT_MOVE" not in ctx["gates_fired"], f"got {ctx}")

with mock.patch.object(report_utils, "get_cached_extended_hours_quote",
                        return_value={"symbol": "EDGE", "live_price": 110.0, "live_price_source": "regular"}):
    ctx = report_utils.extended_hours_context("EDGE", 100.0)
    check("exactly at the 10% threshold does NOT fire (strictly greater-than)",
          "OVERNIGHT_MOVE" not in ctx["gates_fired"], f"got {ctx}")

with mock.patch.object(report_utils, "get_cached_extended_hours_quote",
                        return_value={"symbol": "DOWN", "live_price": 88.0, "live_price_source": "after_hours"}):
    ctx = report_utils.extended_hours_context("DOWN", 100.0)
    check("a large NEGATIVE move also fires (abs(), not one-sided)",
          "OVERNIGHT_MOVE" in ctx["gates_fired"], f"got {ctx}")

# ---------------------------------------------------------------------------
# load_us_positions() -- account_sources parity for Fidelity/Vanguard/
# Robinhood (previously populated only inside the Schwab loop)
# ---------------------------------------------------------------------------
print("\nload_us_positions() account_sources parity across all 4 broker types")

FAKE_FIDELITY_CSV = "/fake/fidelity_test.csv"
FAKE_ROBINHOOD_CSV = "/fake/robinhood_test.csv"
FAKE_VANGUARD_CSV = "/fake/vanguard_test.csv"

_fake_accounts = {
    "TESTFID": {"broker": "fidelity_csv", "csv_path_env": "TEST_FIDELITY_CSV_PATH", "fidelity_account_number": "999"},
    "TESTRH": {"broker": "robinhood_csv", "csv_path_env": "TEST_ROBINHOOD_CSV_PATH"},
    "TESTVG": {"broker": "vanguard_csv", "csv_path_env": "TEST_VANGUARD_CSV_PATH"},
}

_real_exists = report_utils.os.path.exists
_real_getmtime = report_utils.os.path.getmtime


def _fake_exists(path):
    if path in (FAKE_FIDELITY_CSV, FAKE_ROBINHOOD_CSV, FAKE_VANGUARD_CSV):
        return True
    return _real_exists(path)


# 2 days stale, anchored at local noon to avoid a midnight-boundary flake.
_stale_mtime = datetime.combine(date.today() - timedelta(days=2), datetime.min.time().replace(hour=12)).timestamp()


def _fake_getmtime(path):
    if path in (FAKE_FIDELITY_CSV, FAKE_ROBINHOOD_CSV, FAKE_VANGUARD_CSV):
        return _stale_mtime
    return _real_getmtime(path)


def _fake_parse_fidelity_csv(csv_path, account_filter=None):
    pos = Position(symbol="TESTFID1", account="TESTFID", shares=0, stock_cost_basis=0.0, current_price=50.0)
    return {account_filter: [pos]}


def _fake_load_robinhood_positions(csv_path, account_label=None):
    return [Position(symbol="TESTRH1", account=account_label, shares=0, stock_cost_basis=0.0, current_price=25.0)]


def _fake_parse_vanguard_csv(csv_path, account_label=None):
    return [Position(symbol="TESTVG1", account=account_label, shares=0, stock_cost_basis=0.0, current_price=75.0)]


with mock.patch.object(config, "ACCOUNTS", _fake_accounts), \
     mock.patch.object(report_utils.os, "getenv", side_effect=lambda k, d="": {
         "TEST_FIDELITY_CSV_PATH": FAKE_FIDELITY_CSV,
         "TEST_ROBINHOOD_CSV_PATH": FAKE_ROBINHOOD_CSV,
         "TEST_VANGUARD_CSV_PATH": FAKE_VANGUARD_CSV,
     }.get(k, d)), \
     mock.patch.object(report_utils.os.path, "exists", side_effect=_fake_exists), \
     mock.patch.object(report_utils.os.path, "getmtime", side_effect=_fake_getmtime), \
     mock.patch.object(pnl_module, "parse_fidelity_csv", side_effect=_fake_parse_fidelity_csv), \
     mock.patch.object(report_utils, "load_robinhood_positions", side_effect=_fake_load_robinhood_positions), \
     mock.patch.object(pnl_module, "parse_vanguard_csv", side_effect=_fake_parse_vanguard_csv), \
     mock.patch.object(report_utils, "_snapshot_holdings", return_value=set()):
    us_data = asyncio.run(report_utils.load_us_positions())

sources = us_data.get("account_sources", {})
print("  account_sources:", sources)

for label, broker in (("TESTFID", "fidelity_csv"), ("TESTRH", "robinhood_csv"), ("TESTVG", "vanguard_csv")):
    entry = sources.get(label)
    check(f"{label} ({broker}) has an account_sources entry at all",
          entry is not None, f"account_sources={sources}")
    if entry is None:
        continue
    check(f"{label} data_source is populated (was None pre-fix for non-Schwab)",
          entry.get("source") == broker, f"got {entry}")
    check(f"{label} data_as_of is populated (non-None)",
          entry.get("as_of") is not None, f"got {entry}")
    check(f"{label} days_stale is populated and reflects the ~2-day-old file",
          entry.get("days_stale") is not None and entry["days_stale"] >= 1,
          f"got {entry}")

# ---------------------------------------------------------------------------
# get_position_detail (mcp/server.py) -- previously missing BOTH the
# staleness fields AND the extended-hours fields entirely from its JSON
# output (only the dashboard's get_position_heat had them).
# ---------------------------------------------------------------------------
print("\nget_position_detail JSON output -- staleness + extended-hours fields")

import server  # noqa: E402 -- mcp/server.py; imported late so the sys.path setup above is in place

# server.py imports report_utils as "reports.report_utils" (a package import,
# since mcp/ is on sys.path), a SEPARATE module object in sys.modules from
# this test's own flat "report_utils" (mcp/reports/ directly on sys.path,
# matching test_schwab_source_selection.py's convention) -- same file,
# different sys.modules entry, so the mock has to target the one server.py
# actually calls.
from reports import report_utils as server_report_utils  # noqa: E402

# A synthetic position, not a real currently-held symbol -- real account
# holdings drift over time (confirmed live: this environment's real data no
# longer holds the OKTA/TWLO fixtures test_schwab_source_selection.py's own
# golden values assume, a pre-existing environment-drift failure unrelated
# to this ADR, reproduced identically against this same test on an unmodified
# checkout). Mocking load_us_positions() keeps this test deterministic
# instead of depending on whatever happens to be in the real account files
# today.
_synthetic_leg = OptionLeg(
    description="OKTA 11/20/2026 140 C", strike=140.0, expiry="2026-11-20",
    option_type="CALL", quantity=-1, premium_received=500.0, current_mark=4700.0, dte=11,
)
_synthetic_pos = Position(symbol="OKTA", account="A", shares=0, stock_cost_basis=0.0,
                           current_price=236.94, option_legs=[_synthetic_leg])
_fake_us_data = {
    "positions": [_synthetic_pos],
    "account_sources": {"A": {"source": "snapshot", "as_of": "2026-11-07", "days_stale": 2}},
}

with mock.patch.object(server_report_utils, "load_us_positions", return_value=_fake_us_data), \
     mock.patch.object(server_report_utils, "get_cached_extended_hours_quote",
                        return_value={"symbol": "OKTA", "live_price": 331.0, "live_price_source": "pre_market"}):
    text_result = asyncio.run(server.call_tool("get_position_detail", {"symbol": "OKTA"}))
    detail = json.loads(text_result[0].text)

check("get_position_detail's top-level live_price is the mocked live quote",
      detail.get("live_price") == 331.0, f"got {detail.get('live_price')}")
check("get_position_detail's top-level live_price_source is the mocked source",
      detail.get("live_price_source") == "pre_market", f"got {detail.get('live_price_source')}")
check("get_position_detail's overnight_move_pct reflects live vs. regular close (331 vs 236.94)",
      detail.get("overnight_move_pct") is not None and detail["overnight_move_pct"] > 10.0,
      f"got {detail.get('overnight_move_pct')}")
check("get_position_detail's gates_fired includes OVERNIGHT_MOVE for this +39.7% move",
      "OVERNIGHT_MOVE" in detail.get("gates_fired", []), f"got {detail.get('gates_fired')}")

some_account = detail.get("accounts", {}).get("A")
check("get_position_detail's per-account output has the synthetic position at all",
      some_account is not None, f"got accounts={list(detail.get('accounts', {}).keys())}")
if some_account is not None:
    check("get_position_detail's per-account data_source is now populated (was missing entirely)",
          some_account.get("data_source") == "snapshot", f"got {some_account.get('data_source')}")
    check("get_position_detail's per-account data_as_of is now populated",
          some_account.get("data_as_of") == "2026-11-07", f"got {some_account.get('data_as_of')}")
    check("get_position_detail's per-account days_stale is now populated",
          some_account.get("days_stale") == 2, f"got {some_account.get('days_stale')}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
