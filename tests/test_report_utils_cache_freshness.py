"""
Regression tests for the two unbounded in-process caches in report_utils.py
found live 2026-11-05: _US_PRICE_CACHE (via _history_cache()) and
_SNAPSHOT_HOLDINGS_CACHE (via _snapshot_holdings()) both cached their first
result for the life of the process, with no TTL/invalidation at all. The
real-world symptom: the MCP server container had been running continuously
since 2026-11-04 17:04 UTC; the first time it looked up AppLovin's (APP)
price that day, it got a mid-session Nov 4 print (~$236.94) and served that
SAME frozen number through APP's after-hours earnings beat, a +22%
pre-market rally the next morning, and everything in between -- confirmed
live via a direct yfinance pull showing the real contemporaneous price was
$331+ while this tool kept returning $236.94. The exact same unbounded-cache
shape on _SNAPSHOT_HOLDINGS_CACHE is the leading explanation for a separate
symptom the same session: get_position_detail (which filters through
_snapshot_holdings()) missed a real Fidelity position that a fresh process
(no cache yet) found immediately.

Both fixes give the cache a bounded lifetime instead of removing caching
entirely (re-fetching live data on every single call would be its own real
cost) -- a TTL for price (time-based: a price is stale after N minutes
regardless of what day it is) and a same-day cache for snapshot holdings
(day-based: matches symbol_context.py's existing get_cached_symbol_context
same-day-cache convention, since holdings only change when the trader
exports a new snapshot, not intra-day).

No pytest dependency -- run directly: python3 tests/test_report_utils_cache_freshness.py
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "reports"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "analysis"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp"))

import report_utils  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# _history_cache() / _US_PRICE_CACHE -- time-based TTL
# ---------------------------------------------------------------------------
print("_history_cache() price TTL")

report_utils._US_PRICE_CACHE.clear()

fake_clock = {"t": 1_000_000.0}


def _fake_now():
    return fake_clock["t"]


_fetch_count = {"n": 0}  # shared across Ticker() instances -- a real refetch
                         # always constructs a NEW Ticker, so per-instance
                         # call_count can't tell "cache hit" from "refetch."


class _FakeTicker:
    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, **kwargs):
        _fetch_count["n"] += 1
        import pandas as pd
        # Price reflects WHEN it was fetched (total fetch count), so the
        # test can tell a real refetch happened from a cache hit.
        return pd.DataFrame({"Close": [100.0 + _fetch_count["n"]]})


def _fake_ticker_factory(symbol):
    return _FakeTicker(symbol)


with mock.patch.object(report_utils, "_now", _fake_now), \
     mock.patch.object(report_utils.yf, "Ticker", side_effect=_fake_ticker_factory):
    first = report_utils._history_cache("TESTSYM")
    check("first call fetches live (price 101)", first["hist"]["Close"].iloc[-1] == 101.0,
          f"got {first['hist']['Close'].iloc[-1]}")

    # Well within the TTL -- must be served from cache, not refetched.
    fake_clock["t"] += 60  # 1 minute later
    second = report_utils._history_cache("TESTSYM")
    check("a call within the TTL window is served from cache (still price 101, no refetch)",
          second["hist"]["Close"].iloc[-1] == 101.0, f"got {second['hist']['Close'].iloc[-1]}")
    check("no real fetch happened for the cache-hit call",
          _fetch_count["n"] == 1, f"fetch_count={_fetch_count['n']}")

    # Past the TTL -- a real crossing-a-session-boundary case like the real
    # APP incident (same process, price fetched hours earlier, never refreshed).
    fake_clock["t"] += report_utils._PRICE_CACHE_TTL_SECONDS + 1
    third = report_utils._history_cache("TESTSYM")
    check("a call past the TTL window triggers a real refetch (price advances to 102)",
          third["hist"]["Close"].iloc[-1] == 102.0, f"got {third['hist']['Close'].iloc[-1]}")

report_utils._US_PRICE_CACHE.clear()

# ---------------------------------------------------------------------------
# _snapshot_holdings() / _SNAPSHOT_HOLDINGS_CACHE -- same-day cache
# ---------------------------------------------------------------------------
print("\n_snapshot_holdings() same-day cache")

report_utils._SNAPSHOT_HOLDINGS_CACHE = None

_load_calls = {"n": 0}


class _FakeLoader:
    def __init__(self):
        self.open_positions = None

    def load_all_data(self):
        _load_calls["n"] += 1
        import pandas as pd
        # Simulates a real new position (e.g. the real Fidelity APP case)
        # appearing in the snapshot after the FIRST load already ran.
        tickers = ["AAPL"] if _load_calls["n"] == 1 else ["AAPL", "APP"]
        self.open_positions = pd.DataFrame({"ticker": tickers})


# _snapshot_holdings() does `from open_positions_loader_v2 import
# OpenPositionsLoaderV2` as a top-level module (after adding .../scripts to
# sys.path) -- patch sys.modules under that exact name so the in-function
# import resolves to the fake loader instead of hitting the real one.
import types
_fake_module = types.ModuleType("open_positions_loader_v2")
_fake_module.OpenPositionsLoaderV2 = _FakeLoader
sys.modules["open_positions_loader_v2"] = _fake_module

with mock.patch.object(report_utils, "_today", return_value="2026-11-04"):
    first_holdings = report_utils._snapshot_holdings()
    check("first call loads real data (APP not yet in the snapshot)",
          first_holdings == {"AAPL"}, f"got {first_holdings}")

    # Same day, called again -- must be served from cache, not reloaded.
    second_holdings = report_utils._snapshot_holdings()
    check("a same-day call is served from cache (APP still absent, no reload)",
          second_holdings == {"AAPL"} and _load_calls["n"] == 1,
          f"got {second_holdings}, load_calls={_load_calls['n']}")

# Next day -- the real-world case: the trader's snapshot now includes APP
# (e.g. a newly-loaded Fidelity position), and the cache must pick it up
# instead of serving yesterday's frozen set forever.
with mock.patch.object(report_utils, "_today", return_value="2026-11-05"):
    third_holdings = report_utils._snapshot_holdings()
    check("a new-day call reloads and picks up a real new holding (APP)",
          third_holdings == {"AAPL", "APP"} and _load_calls["n"] == 2,
          f"got {third_holdings}, load_calls={_load_calls['n']}")

report_utils._SNAPSHOT_HOLDINGS_CACHE = None

print("\n_snapshot_holdings() does not cache a transient failure")


class _FlakyThenOkLoader:
    """Fails on its first call (simulating a momentary lock on the snapshot
    file), succeeds on the second -- the real-world case this fix targets."""
    _attempt = {"n": 0}

    def __init__(self):
        self.open_positions = None

    def load_all_data(self):
        _FlakyThenOkLoader._attempt["n"] += 1
        if _FlakyThenOkLoader._attempt["n"] == 1:
            raise OSError("snapshot file locked")
        import pandas as pd
        self.open_positions = pd.DataFrame({"ticker": ["MSFT"]})


_fake_module.OpenPositionsLoaderV2 = _FlakyThenOkLoader

with mock.patch.object(report_utils, "_today", return_value="2026-11-06"):
    failed_holdings = report_utils._snapshot_holdings()
    check("a transient failure returns an empty set, not a crash",
          failed_holdings == set(), f"got {failed_holdings}")
    check("a transient failure is NOT cached -- the global stays unset",
          report_utils._SNAPSHOT_HOLDINGS_CACHE is None,
          f"got {report_utils._SNAPSHOT_HOLDINGS_CACHE}")

    retried_holdings = report_utils._snapshot_holdings()
    check("the very next call (same day) retries instead of reusing the failed result",
          retried_holdings == {"MSFT"}, f"got {retried_holdings}")

report_utils._SNAPSHOT_HOLDINGS_CACHE = None

# ---------------------------------------------------------------------------
# Per-account load failures must be visible, not silently swallowed
# ---------------------------------------------------------------------------
print("\n_record_account_failure() -- per-account errors are recorded, not swallowed")

errors: list[str] = []
report_utils._record_account_failure(errors, "F1", ValueError("boom"))
check("a recorded failure names the account label", "F1" in errors[0], f"got {errors}")
check("a recorded failure names the real exception type/message",
      "ValueError" in errors[0] and "boom" in errors[0], f"got {errors}")

errors2: list[str] = []
report_utils._record_account_failure(errors2, "ROBINHOOD1", RuntimeError("csv parse failed"))
check("a second, unrelated failure is appended independently",
      len(errors2) == 1 and "ROBINHOOD1" in errors2[0] and "csv parse failed" in errors2[0],
      f"got {errors2}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
