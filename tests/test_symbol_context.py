"""
Regression tests for mcp/analysis/symbol_context.py's real-data wiring
(ADR 0001 steps 5-7): `_dividend_info()` (merged dividend yield + raw rate +
next ex-dividend date from one Yahoo call) and `get_symbol_context()`'s new
`current_iv` passthrough into `iv_rank.get_iv_rank(symbol, current_iv=...)`.

These hit LIVE yfinance data against real, known dividend-paying tickers
(AAPL, JNJ, KO) -- there is no local fixture for "does yfinance's real
exDividendDate/dividendRate field come back usable," which is exactly what
this real-data-wiring Bolt needs verified, not mocked. Keep assertions
honest about yfinance's own documented quirks (see _dividend_info()'s own
docstring): next_ex_dividend_date can legitimately be a PAST date until the
company declares its next one, so this suite never asserts it's always
future-dated, only that it's well-formed when present.

No pytest dependency -- run directly: python3 tests/test_symbol_context.py
"""
import sys
import time
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "reports"))
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp"))

from symbol_context import get_symbol_context, get_cached_symbol_context  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# Real dividend payers -- dividend_rate / next_ex_dividend_date
# ---------------------------------------------------------------------------
print("Real dividend-payer fields (live yfinance)")

DIVIDEND_PAYERS = ["AAPL", "JNJ", "KO"]

for sym in DIVIDEND_PAYERS:
    ctx = get_symbol_context(sym)
    rate = ctx.get("dividend_rate")
    check(f"{sym} dividend_rate is a positive float (real dividend payer)",
          isinstance(rate, (int, float)) and rate > 0, f"got {rate!r}")

    next_ex = ctx.get("next_ex_dividend_date")
    if next_ex is None:
        check(f"{sym} next_ex_dividend_date is None (acceptable -- yfinance "
              "sometimes has no ex-div date at all)", True)
    else:
        # Must be a well-formed ISO date string -- NOT asserted to be in the
        # future: _dividend_info()'s own docstring documents that yfinance's
        # exDividendDate often holds the MOST RECENT PAST date until the
        # company formally declares its next one.
        try:
            date.fromisoformat(next_ex)
            parsed_ok = True
        except (TypeError, ValueError):
            parsed_ok = False
        check(f"{sym} next_ex_dividend_date is a valid ISO date string when present",
              parsed_ok, f"got {next_ex!r}")

    # dividend_yield_pct still present (pre-existing field, now sourced from
    # the same merged _dividend_info() call) -- same-shape regression check.
    check(f"{sym} dividend_yield_pct is still present and numeric",
          isinstance(ctx.get("dividend_yield_pct"), (int, float)),
          f"got {ctx.get('dividend_yield_pct')!r}")

# ---------------------------------------------------------------------------
# current_iv override -- replaces iv_rank's own HV-proxy fallback
# ---------------------------------------------------------------------------
print("\ncurrent_iv kwarg overrides the HV-proxy fallback")

baseline = get_symbol_context("AAPL")
baseline_current_iv = baseline.get("current_iv")
check("baseline (no current_iv) call returns a numeric current_iv (HV-proxy fallback)",
      isinstance(baseline_current_iv, (int, float)), f"got {baseline_current_iv!r}")

overridden = get_symbol_context("AAPL", current_iv=0.35)
overridden_current_iv = overridden.get("current_iv")
# get_iv_rank()'s own contract: it stores whatever `iv` it used (the passed
# current_iv, in the same fractional-vol units as its internal HV calc) and
# returns it as round(iv * 100, 1) for display -- so a 0.35 override surfaces
# as 35.0, not 0.35 unchanged. Verified live against this exact code path
# before writing this assertion (see iv_rank.get_iv_rank, lines ~59-69).
check("current_iv=0.35 override surfaces as 35.0 (iv_rank's own *100 display convention)",
      overridden_current_iv == 35.0, f"got {overridden_current_iv!r}")
check("overridden current_iv differs from the HV-proxy baseline (override actually took effect)",
      overridden_current_iv != baseline_current_iv,
      f"baseline={baseline_current_iv!r} overridden={overridden_current_iv!r}")

# ---------------------------------------------------------------------------
# get_cached_symbol_context() -- same-day caching still works with the new
# current_iv-aware signature
# ---------------------------------------------------------------------------
print("\nget_cached_symbol_context() same-day caching with current_iv kwarg")

t0 = time.time()
first = get_cached_symbol_context("KO", current_iv=0.20)
t1 = time.time()
second = get_cached_symbol_context("KO", current_iv=0.20)
t2 = time.time()

first_call_s = t1 - t0
second_call_s = t2 - t1

check("first get_cached_symbol_context() call returns a usable dict (iv_rank present)",
      first.get("iv_rank") is not None, f"got {first}")
check("two calls for the same symbol/day return identical symbol-level facts "
      "(dividend_rate, current_iv, sector all match -- cache hit, not a fresh HV re-fetch)",
      (first.get("dividend_rate") == second.get("dividend_rate")
       and first.get("current_iv") == second.get("current_iv")
       and first.get("sector") == second.get("sector")),
      f"first={first} second={second}")
check("second call is fast -- well under what a live 1y-history + info fetch takes "
      "(cache hit, not a re-fetch; not compared directly against the first call's "
      "time since a same-day-rerun of this suite may already have KO cached, making "
      "the 'first' call here a cache hit too -- an absolute bound is the honest check)",
      second_call_s < 2.0,
      f"first={first_call_s:.3f}s second={second_call_s:.3f}s")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
