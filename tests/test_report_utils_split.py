"""
Characterization tests for mcp/reports/report_utils.py (Bolt b19), written
BEFORE splitting the file into submodules. report_utils.py had grown to
1502 lines (over this repo's 1000-line Code Quality Gate file cap); this
Bolt's job is to split it into focused sibling submodules under
mcp/reports/, with report_utils.py itself becoming a thin re-export shim so
every real `from report_utils import X` / `import report_utils` call site
across the repo keeps working unchanged.

This suite pins down REAL current behavior of the functions this Bolt is
about to relocate, run against the CURRENT, unmodified file and confirmed
green first, then re-run after each extraction. It deliberately does NOT
duplicate tests/test_report_utils_cache_freshness.py (narrow: the two
unbounded in-process caches) or the Schwab/Robinhood/extended-hours
coverage already in tests/test_schwab_source_selection.py,
tests/test_robinhood_netting.py, tests/test_extended_hours_pricing.py --
this file covers the REMAINING load-bearing surface: symbol mapping, date/
money/math utilities, option-symbol parsing, reconstructed-leg building,
position-CSV loading, India position mapping, upcoming-earnings/option-chain
pricing, KPI aggregation, and the action/priority/delta signal helpers.

Where a function calls out to yfinance, the mock boundary is yf.Ticker
itself (a true process-wide singleton module object) rather than any
higher-level report_utils helper name -- this keeps these tests valid
regardless of which sibling submodule ends up owning the higher-level
function, since patching yf.Ticker's attribute affects every caller that
holds a reference to the same yfinance module object, no matter which file
defines the caller.

No pytest dependency -- run directly: python3 tests/test_report_utils_split.py
"""
import csv
import sys
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT / "mcp", ROOT / "mcp" / "reports", ROOT / "mcp" / "analysis", ROOT / "scripts"):
    sys.path.insert(0, str(_p))

import report_utils  # noqa: E402
from analysis.pnl import Position, OptionLeg  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# yf_symbol() -- India ticker mapping
# ---------------------------------------------------------------------------
print("yf_symbol()")

check("US symbol passes through unchanged when india=False",
      report_utils.yf_symbol("AAPL", india=False) == "AAPL")
check("a mapped India broker code resolves via _INDIA_SYMBOL_MAP",
      report_utils.yf_symbol("TCS", india=True) == "TCS.NS",
      report_utils.yf_symbol("TCS", india=True))
check("an unmapped India symbol gets a bare .NS suffix",
      report_utils.yf_symbol("SOMEUNMAPPEDCODE", india=True) == "SOMEUNMAPPEDCODE.NS")
check("an already-suffixed India symbol is left alone",
      report_utils.yf_symbol("RELIANCE.NS", india=True) == "RELIANCE.NS")
check("an index symbol (^ prefix) is left alone",
      report_utils.yf_symbol("^NSEI", india=True) == "^NSEI")

# ---------------------------------------------------------------------------
# parse_option_symbol() -- Schwab-style option symbol string parsing
# ---------------------------------------------------------------------------
print("\nparse_option_symbol()")

parsed = report_utils.parse_option_symbol("AAPL 11/20/2026 140 C")
check("parses a valid CALL symbol", parsed == {
    "symbol": "AAPL", "expiry": "2026-11-20", "strike": 140.0, "option_type": "CALL",
}, f"got {parsed}")

parsed_put = report_utils.parse_option_symbol("MSFT 01/15/2027 350.5 P")
check("parses a valid PUT symbol with a decimal strike",
      parsed_put == {"symbol": "MSFT", "expiry": "2027-01-15", "strike": 350.5, "option_type": "PUT"},
      f"got {parsed_put}")

check("an equity symbol (no option suffix) returns None",
      report_utils.parse_option_symbol("AAPL") is None)
check("garbage input returns None, not a crash",
      report_utils.parse_option_symbol("") is None)

# ---------------------------------------------------------------------------
# Date / money / math utilities
# ---------------------------------------------------------------------------
print("\ndate/money/math utilities")

first, last = report_utils.month_window(date(2026, 2, 15))
check("month_window() returns the first and last calendar day of the month",
      (first, last) == (date(2026, 2, 1), date(2026, 2, 28)), f"got {(first, last)}")

check("previous_month() steps back to the 1st of the prior month",
      report_utils.previous_month(date(2026, 3, 15)) == date(2026, 2, 1))
check("previous_month() handles a January rollback to prior December",
      report_utils.previous_month(date(2026, 1, 10)) == date(2025, 12, 1))

check("month_name() formats as 'Month YYYY'",
      report_utils.month_name(date(2026, 7, 4)) == "July 2026")
check("month_days() returns the real day count for a 31-day month",
      report_utils.month_days(date(2026, 1, 1)) == 31)
check("month_days() returns 28 for Feb in a non-leap year",
      report_utils.month_days(date(2026, 2, 1)) == 28)

check("project_value() annualizes a partial-month value to the full month",
      round(report_utils.project_value(500.0, date(2026, 1, 10)), 2) == round(500.0 / 10 * 31, 2))

check("fmt_money() formats with a dollar sign, comma, no decimals",
      report_utils.fmt_money(1234.5) == "$1,234")
check("fmt_money() returns an em-dash placeholder for an unparseable value",
      report_utils.fmt_money("not-a-number") == "—")
check("fmt_inr() formats with a rupee sign",
      report_utils.fmt_inr(50000) == "₹50,000")
check("safe_div() returns 0.0 instead of raising on a zero denominator",
      report_utils.safe_div(10.0, 0.0) == 0.0)
check("safe_div() divides normally otherwise",
      report_utils.safe_div(10.0, 4.0) == 2.5)

try:
    import pandas as pd
    # A strictly monotonic series has zero down days, so compute_rsi's own
    # loss.replace(0, nan) safety makes rs (and so the final RSI) NaN ->
    # None by design (confirmed against the real unmodified function) --
    # a realistic mixed up/down series is needed to get a numeric RSI out.
    _rsi_prices = pd.Series([100 + (i % 3) - 1 + i * 0.3 for i in range(20)])
    rsi = report_utils.compute_rsi(_rsi_prices, period=14)
    check("compute_rsi() returns a numeric RSI for a mixed up/down series",
          rsi is not None, f"got {rsi}")
    check("compute_rsi() returns None instead of crashing on a too-short series",
          report_utils.compute_rsi(pd.Series([100.0, 101.0]), period=14) is None)
except ImportError:
    check("compute_rsi() test skipped (pandas unavailable)", True)

# ---------------------------------------------------------------------------
# _clean_money() -- Schwab-snapshot money-field cleaning
# ---------------------------------------------------------------------------
print("\n_clean_money()")

check("strips $ and , and surrounding quotes", report_utils._clean_money('"$1,234.50"') == 1234.50)
check("blank/garbage input returns 0.0, not a crash", report_utils._clean_money("") == 0.0)

# ---------------------------------------------------------------------------
# reconstruct_open_option_legs() -- transaction-row netting into open legs
#
# Mocked at yf.Ticker (a true process-wide singleton) rather than at
# current_price()/option_market_price() by name -- those two helpers' own
# internal bare-name lookups are resolved against whichever module physically
# defines them, so patching them *by name on the report_utils shim* would
# silently stop working the moment either one is relocated to a sibling
# submodule. Patching yf.Ticker instead exercises the REAL current_price()/
# option_market_price() code paths end-to-end and stays valid no matter which
# file ends up owning them.
# ---------------------------------------------------------------------------
print("\nreconstruct_open_option_legs()")

_today_iso = date.today().isoformat()
_future_expiry = (date.today() + timedelta(days=30)).strftime("%m/%d/%Y")
_rows = [
    {"Date": _today_iso, "Symbol": f"AAPL {_future_expiry} 140 C", "Action": "Sell to Open",
     "Quantity": "2", "Amount": "$300.00"},
    # Note: report_utils.parse_amount() has no handling for accounting-style
    # parenthesized negatives ("($50.00)") -- it only strips "$"/"," then
    # float()s the rest, so a parenthesized value fails to parse and is
    # caught back to 0.0 (confirmed against the real unmodified function).
    # A real Schwab export's BTC debit uses a plain leading minus sign
    # instead, which this DOES parse correctly -- matching that real format
    # here, not the accounting-parens one.
    {"Date": _today_iso, "Symbol": f"AAPL {_future_expiry} 140 C", "Action": "Buy to Close",
     "Quantity": "1", "Amount": "-$50.00"},
    {"Date": _today_iso, "Symbol": f"MSFT {_future_expiry} 300 P", "Action": "Sell to Open",
     "Quantity": "1", "Amount": "$200.00"},
    {"Date": _today_iso, "Symbol": f"MSFT {_future_expiry} 300 P", "Action": "Expired",
     "Quantity": "1", "Amount": "$0.00"},
]


class _FakeCombinedTicker:
    """Supports both .history() (current_price/_history_cache) and
    .option_chain() (option_market_price) -- the two live yfinance calls
    reconstruct_open_option_legs() makes per open leg."""
    def __init__(self, symbol):
        self.symbol = symbol

    def history(self, **kwargs):
        import pandas as pd
        return pd.DataFrame({"Close": [150.0]})

    def option_chain(self, expiry):
        import pandas as pd

        class _Chain:
            calls = pd.DataFrame({
                "strike": [140.0], "bid": [5.0], "ask": [5.4],
                "lastPrice": [5.2], "impliedVolatility": [0.35],
            })
            puts = pd.DataFrame({
                "strike": [140.0], "bid": [3.0], "ask": [3.4],
                "lastPrice": [3.2], "impliedVolatility": [0.32],
            })
        return _Chain()


report_utils._US_PRICE_CACHE.clear()
report_utils._OPTION_CHAIN_CACHE.clear()
report_utils._OPTION_CHAIN_CACHE_DATE[0] = None

with mock.patch.object(report_utils.yf, "Ticker", side_effect=_FakeCombinedTicker):
    legs = report_utils.reconstruct_open_option_legs(_rows, account="A")

check("MSFT's STO+Expired sequence nets to fully closed (not returned)",
      all(leg["symbol"] != "MSFT" for leg in legs), f"got {[l['symbol'] for l in legs]}")
check("AAPL's STO 2 / BTC 1 nets to exactly 1 still-open contract",
      len(legs) == 1 and legs[0]["symbol"] == "AAPL" and legs[0]["contracts"] == 1,
      f"got {legs}")
if legs:
    check("the open leg's mark is contracts * 100 * (mid of bid/ask)",
          legs[0]["mark"] == round((5.0 + 5.4) / 2, 2) * 100 * 1, f"got {legs[0]['mark']}")
    check("the open leg's premium_received reflects net STO credit minus BTC debit",
          legs[0]["premium_received"] == 300.00 - 50.00, f"got {legs[0]['premium_received']}")
    check("the open leg's underlying_price is the live current_price() result",
          legs[0]["underlying_price"] == 150.0, f"got {legs[0]['underlying_price']}")

report_utils._US_PRICE_CACHE.clear()
report_utils._OPTION_CHAIN_CACHE.clear()
report_utils._OPTION_CHAIN_CACHE_DATE[0] = None

# ---------------------------------------------------------------------------
# load_position_csv() -- Schwab "Individual-Positions*.csv" export parsing
#
# Writes a real fixture into the real STATEMENTS_DIR (confirmed empty except
# for .gitkeep) rather than patching STATEMENTS_DIR/latest_file by name --
# same reasoning as above: load_position_csv() may move to a sibling
# submodule, and a real file + the real glob/mtime-sort logic stays valid
# regardless of which file ends up defining it. Cleaned up in finally.
# ---------------------------------------------------------------------------
print("\nload_position_csv()")

_pos_csv = report_utils.STATEMENTS_DIR / "Individual-Positions-charsplittest.csv"
try:
    with open(_pos_csv, "w", newline="") as fh:
        fh.write('"Positions for account Individual XXX232 as of 09:00 AM ET, 2026-11-09"\n')
        writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
        writer.writerow(["Symbol", "Description", "Qty (Quantity)", "Price", "Mkt Val (Market Value)",
                          "Cost Basis", "Asset Type"])
        writer.writerow(["AAPL", "APPLE INC", "100", "$150.00", "$15,000.00", "$10,000.00", "Equity"])

    rows = report_utils.load_position_csv()
    check("parses the real header row after the disclaimer line, skipping it",
          any(r["symbol"] == "AAPL" for r in rows), f"got {rows}")
    aapl_row = next((r for r in rows if r["symbol"] == "AAPL"), None)
    if aapl_row:
        check("numeric fields are parsed to real numbers",
              aapl_row["qty"] == 100 and aapl_row["price"] == 150.0 and aapl_row["cost_basis_total"] == 10000.0,
              f"got {aapl_row}")
finally:
    _pos_csv.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# India position mapping helpers
# ---------------------------------------------------------------------------
print("\nIndia position mapping (_dte_from_expiry / _map_breeze_*)")

_future_iso = (date.today() + timedelta(days=10)).isoformat()
check("_dte_from_expiry() computes a positive DTE for a future date",
      report_utils._dte_from_expiry(_future_iso) == 10, f"got {report_utils._dte_from_expiry(_future_iso)}")
check("_dte_from_expiry() returns 0 instead of crashing on garbage input",
      report_utils._dte_from_expiry("not-a-date") == 0)

_raw_positions = [
    {"symbol": "TCS", "exchange": "NSE", "product_type": "cash", "quantity": 10,
     "avg_price": 3500.0, "market_value": 36000.0, "ltp": 3600.0},
    {"symbol": "TCS26NOVCE4000", "exchange": "NSE", "product_type": "options",
     "quantity": -2, "avg_price": 50.0, "market_value": 0.0, "ltp": 40.0,
     "option_type": "CE", "strike_price": 4000.0, "expiry_date": _future_iso,
     "_raw": {"stock_code": "TCS"}},
]
mapped = report_utils._map_breeze_to_positions(_raw_positions)
_tcs = next((p for p in mapped if p.symbol == "TCS"), None)
check("an NSE cash-product row maps to an equity Position",
      _tcs is not None and _tcs.shares == 10, f"got {mapped}")
if _tcs is not None:
    check("a short options row on the same underlying attaches as an OptionLeg",
          len(_tcs.option_legs) == 1 and _tcs.option_legs[0].option_type == "CALL",
          f"got {_tcs.option_legs}")
    check("a short option leg's premium is avg_price * abs(qty)",
          _tcs.option_legs[0].premium_received == 50.0 * 2, f"got {_tcs.option_legs[0].premium_received}")

_raw_holdings = [{"symbol": "INFY", "quantity": 5, "avg_price": 1400.0, "ltp": 1450.0}]
holdings_mapped = report_utils._map_breeze_equity_holdings(_raw_holdings)
check("_map_breeze_equity_holdings() builds one equity Position per holding row",
      len(holdings_mapped) == 1 and holdings_mapped[0].symbol == "INFY",
      f"got {holdings_mapped}")

# ---------------------------------------------------------------------------
# load_india_positions() -- no Breeze creds configured in this test env -> falls
# back to the statement/config loader; just confirm the fallback shape, not
# specific golden numbers (real statement data drifts over time).
# ---------------------------------------------------------------------------
print("\nload_india_positions() fallback shape")

with mock.patch.dict("os.environ", {"BREEZE_API_KEY": "", "BREEZE_API_SECRET": "", "BREEZE_SESSION_TOKEN": ""}):
    india_data = report_utils.load_india_positions()
check("falls back to SNAPSHOT when no live Breeze credentials are configured",
      india_data.get("data_source", "").startswith("SNAPSHOT"), f"got {india_data.get('data_source')}")
check("fallback result always carries a 'positions' list (possibly empty)",
      isinstance(india_data.get("positions"), list), f"got {india_data.get('positions')}")

# ---------------------------------------------------------------------------
# upcoming_earnings() -- yfinance calendar parsing (mocked at yf.Ticker)
# ---------------------------------------------------------------------------
print("\nupcoming_earnings()")

report_utils._EARNINGS_CACHE.clear()
report_utils._EARNINGS_CACHE_DATE[0] = None


class _FakeCalendarTicker:
    def __init__(self, symbol):
        # Must be a real datetime (not a bare date) -- upcoming_earnings()'s
        # dict branch only accepts entries with a .date() method, which
        # datetime.datetime has and datetime.date does not (confirmed
        # against the real unmodified function).
        from datetime import datetime as _dt
        self.calendar = {"Earnings Date": [_dt.combine(date.today() + timedelta(days=5), _dt.min.time())]}


with mock.patch.object(report_utils.yf, "Ticker", side_effect=_FakeCalendarTicker):
    earnings = report_utils.upcoming_earnings("TESTEARN", days=14)
check("a near-term earnings date within the window is returned",
      len(earnings) == 1 and earnings[0] == (date.today() + timedelta(days=5)).isoformat(),
      f"got {earnings}")
report_utils._EARNINGS_CACHE.clear()
report_utils._EARNINGS_CACHE_DATE[0] = None

# ---------------------------------------------------------------------------
# option_market_price() / option_probability_itm() -- option-chain pricing
# (mocked at yf.Ticker -- a shared singleton regardless of which sibling
# submodule ends up owning these functions)
# ---------------------------------------------------------------------------
print("\noption_market_price() / option_probability_itm()")

report_utils._OPTION_CHAIN_CACHE.clear()
report_utils._OPTION_CHAIN_CACHE_DATE[0] = None


class _FakeChain:
    def __init__(self):
        import pandas as pd
        self.calls = pd.DataFrame({
            "strike": [140.0, 145.0], "bid": [5.0, 2.0], "ask": [5.4, 2.4],
            "lastPrice": [5.2, 2.2], "impliedVolatility": [0.35, 0.30],
        })
        self.puts = pd.DataFrame({
            "strike": [140.0, 145.0], "bid": [3.0, 6.0], "ask": [3.4, 6.4],
            "lastPrice": [3.2, 6.2], "impliedVolatility": [0.32, 0.31],
        })


class _FakeChainTicker:
    def __init__(self, symbol):
        pass

    def option_chain(self, expiry):
        return _FakeChain()


_future_expiry_iso = (date.today() + timedelta(days=30)).isoformat()
with mock.patch.object(report_utils.yf, "Ticker", side_effect=_FakeChainTicker):
    mark = report_utils.option_market_price("TESTOPT", _future_expiry_iso, 140.0, "CALL")
    check("mid of bid/ask is used when both are present",
          mark == round((5.0 + 5.4) / 2, 2), f"got {mark}")

    no_match = report_utils.option_market_price("TESTOPT", _future_expiry_iso, 999.0, "CALL")
    check("a strike far from any row in the chain returns None",
          no_match is None, f"got {no_match}")

    prob = report_utils.option_probability_itm("TESTOPT", _future_expiry_iso, 140.0, "PUT", spot=150.0)
    check("option_probability_itm() returns a probability in [0, 1] for a usable chain row",
          prob is not None and 0.0 <= prob <= 1.0, f"got {prob}")

    prob_none = report_utils.option_probability_itm("TESTOPT", _future_expiry_iso, 140.0, "PUT", spot=0.0)
    check("option_probability_itm() returns None instead of crashing with no usable spot",
          prob_none is None, f"got {prob_none}")
report_utils._OPTION_CHAIN_CACHE.clear()
report_utils._OPTION_CHAIN_CACHE_DATE[0] = None

# ---------------------------------------------------------------------------
# technical_snapshot() -- derived indicators built on top of _history_cache()
# ---------------------------------------------------------------------------
print("\ntechnical_snapshot()")

report_utils._US_PRICE_CACHE.clear()


class _FakeHistTicker:
    def __init__(self, symbol):
        pass

    def history(self, **kwargs):
        import pandas as pd
        return pd.DataFrame({"Close": [100.0 + i * 0.1 for i in range(60)]})


with mock.patch.object(report_utils.yf, "Ticker", side_effect=_FakeHistTicker):
    snap = report_utils.technical_snapshot("TESTTECH")
check("technical_snapshot() returns a populated current price from the fake history",
      snap["current"] > 0, f"got {snap}")
check("technical_snapshot() computes a 50-day moving average once >=50 points exist",
      snap["ma50"] is not None, f"got {snap}")
report_utils._US_PRICE_CACHE.clear()

# ---------------------------------------------------------------------------
# monthly_premium() / monthly_option_pnl_series() / combined_kpis()
# ---------------------------------------------------------------------------
print("\nmonthly_premium() / monthly_option_pnl_series() / combined_kpis()")

# "-$100.00" (plain leading minus), not accounting-style "($100.00)" -- see
# the reconstruct_open_option_legs() note above on parse_amount()'s real
# (lack of) parenthesized-negative handling.
_kpi_rows = [
    {"Date": "01/05/2026", "Symbol": "AAPL 02/20/2026 140 C", "Action": "Sell to Open", "Amount": "$300.00"},
    {"Date": "01/20/2026", "Symbol": "AAPL 02/20/2026 140 C", "Action": "Buy to Close", "Amount": "-$100.00"},
    {"Date": "02/03/2026", "Symbol": "MSFT 03/20/2026 300 P", "Action": "Sell to Open", "Amount": "$200.00"},
    {"Date": "03/03/2026", "Symbol": "TSLA 04/20/2026 250 P", "Action": "Sell to Open", "Amount": "$150.00"},
]
jan_premium = report_utils.monthly_premium(_kpi_rows, date(2026, 1, 1))
check("monthly_premium() nets STO credit minus BTC debit for the target month only",
      jan_premium == 300.0 - 100.0, f"got {jan_premium}")

series = report_utils.monthly_option_pnl_series(_kpi_rows)
check("monthly_option_pnl_series() returns one value per distinct (year, month) in order",
      series == [200.0, 200.0, 150.0], f"got {series}")

kpis = report_utils.combined_kpis({"A": _kpi_rows}, snapshot={})
check("combined_kpis() returns the 3 expected top-level keys",
      set(kpis.keys()) == {"capture", "profit_factor", "sortino"}, f"got {kpis.keys()}")

# ---------------------------------------------------------------------------
# priority_from_position() / action_for_option_leg() / estimate_delta()
# ---------------------------------------------------------------------------
print("\npriority_from_position() / action_for_option_leg() / estimate_delta()")

_leg_near_dte = OptionLeg(description="PUT 140 2026-12-01", strike=140.0, expiry="2026-12-01",
                           option_type="PUT", quantity=-1, premium_received=300.0,
                           current_mark=250.0, dte=5)
_pos_urgent = Position(symbol="AAPL", account="A", shares=0, stock_cost_basis=0.0,
                        current_price=150.0, option_legs=[_leg_near_dte])
priority, label, reason = report_utils.priority_from_position(_pos_urgent, regime="NEUTRAL")
check("a leg at/inside the 21 DTE roll threshold is flagged URGENT",
      label == "URGENT", f"got {(priority, label, reason)}")

check("action_for_option_leg() recommends ROLL / CLOSE at or inside 21 DTE",
      report_utils.action_for_option_leg(150.0, 140.0, "PUT", dte=15) == "ROLL / CLOSE")
check("action_for_option_leg() flags an in-the-money short PUT as DEFEND / ROLL",
      report_utils.action_for_option_leg(130.0, 140.0, "PUT", dte=40) == "DEFEND / ROLL")
check("action_for_option_leg() flags an in-the-money short CALL as MANAGE ITM CALL",
      report_utils.action_for_option_leg(150.0, 140.0, "CALL", dte=40) == "MANAGE ITM CALL")
check("action_for_option_leg() otherwise recommends HOLD (OTM call, not near DTE)",
      report_utils.action_for_option_leg(100.0, 140.0, "CALL", dte=40) == "HOLD")

check("estimate_delta() returns None without a usable underlying/strike",
      report_utils.estimate_delta(0.0, 140.0, "PUT") is None)
check("estimate_delta() returns a negative delta for a PUT",
      report_utils.estimate_delta(100.0, 140.0, "PUT") < 0)
check("estimate_delta() returns a positive delta for a CALL",
      report_utils.estimate_delta(100.0, 90.0, "CALL") > 0)

# ---------------------------------------------------------------------------
# save_html() / maybe_send()
#
# Writes to the real LOGS_DIR (same reasoning as load_position_csv() above --
# no patching of a relocatable constant by name); a distinctive prefix avoids
# colliding with any real report output, cleaned up in finally.
# ---------------------------------------------------------------------------
print("\nsave_html() / maybe_send()")

_html_prefix = "b19_charsplittest_prefix"
try:
    out_path = report_utils.save_html(_html_prefix, "<html>hi</html>", report_day=date(2026, 1, 1))
    check("save_html() writes the file at the expected prefixed/dated path",
          out_path.name == f"{_html_prefix}_2026-01-01.html" and out_path.exists(), f"got {out_path}")
    check("save_html() writes the real HTML content",
          out_path.read_text(encoding="utf-8") == "<html>hi</html>")
finally:
    out_path.unlink(missing_ok=True)

with mock.patch.dict("os.environ", {"RESEND_API_KEY": ""}):
    result = report_utils.maybe_send("subject", "<html></html>")
check("maybe_send() fails soft (no crash) when RESEND_API_KEY is unset",
      result == {"success": False, "error": "RESEND_API_KEY not set"}, f"got {result}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
