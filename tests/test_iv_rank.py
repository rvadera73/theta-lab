"""
Direct unit/integration tests for mcp/analysis/iv_rank.py (previously only
exercised indirectly via mocks in test_composite_score_iv_wiring.py and
test_symbol_context.py -- never unit-tested on its own HV-proxy fallback
math until now).

Covers:
  - _historical_volatility()'s log-return / sample-variance / sqrt(*252)
    annualization math, against hand-built price series with an
    independently hand-computed expected volatility (not just "returns a
    positive float" -- that would be tautological).
  - get_iv_rank()'s HV-proxy path (current_iv=None): confirms the returned
    current_iv genuinely IS the HV proxy by re-fetching the same 1y history
    and re-running the real _historical_volatility() (the function under
    test, not a reimplementation of its math) over the same trailing
    31-close window get_iv_rank() itself uses -- an integration check of
    the wiring, not the math (already covered above).
  - get_iv_rank()'s current_iv override path: confirms current_iv passes
    through exactly (round(iv*100,1), not re-derived from HV) and that
    iv_rank is computed as this value's percentile position between the
    SAME hv_52w_low/high the HV-proxy path reported for the same symbol.
  - The actual failure shape that fires for an invalid/delisted symbol,
    confirmed live rather than assumed (see note at that section below).
  - batch_iv_rank() returning both shapes correctly, per-symbol.

The HV-proxy / override / batch sections hit LIVE yfinance data (same
pattern as tests/test_symbol_context.py) -- no mocking of the function
under test.

No pytest dependency -- run directly: python3 tests/test_iv_rank.py
"""
import math
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(_ROOT / "mcp"))

import yfinance as yf  # noqa: E402 -- only used here, to independently re-fetch for the cross-check below
from iv_rank import _historical_volatility, get_iv_rank, batch_iv_rank  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# _historical_volatility -- hand-computed expected values, not tautological
# ---------------------------------------------------------------------------
print("_historical_volatility(): hand-computed expected values")

# 31 closes -> 30 log returns, alternating +r/-r (r=0.02) starting +r.
# 15 of each sign -> mean == 0 exactly, so sample variance = sum(r^2)/(n-1)
#   = 30*r^2/29. Expected annualized HV = r * sqrt(252 * 30 / 29).
r = 0.02
alt_closes = [100.0]
for i in range(30):
    step = r if i % 2 == 0 else -r
    alt_closes.append(alt_closes[-1] * math.exp(step))

expected_hv = r * math.sqrt(252 * 30 / 29)
actual_hv = _historical_volatility(alt_closes, window=30)
check("alternating +/-2% log-return series matches hand-computed annualized HV",
      abs(actual_hv - expected_hv) < 1e-9,
      f"expected {expected_hv!r} got {actual_hv!r}")

# Constant daily log-return series (zero variance in returns) -> HV ~ 0.
const_closes = [100.0 * (1.01 ** i) for i in range(31)]
const_hv = _historical_volatility(const_closes, window=30)
check("constant daily log-return series yields ~0 annualized HV (zero variance)",
      const_hv < 1e-6, f"got {const_hv!r}")

# Fewer than window+1 closes -> documented 0.0 short-circuit, not a crash.
short_hv = _historical_volatility(alt_closes[:20], window=30)
check("fewer than window+1 closes returns 0.0 (documented short-circuit)",
      short_hv == 0.0, f"got {short_hv!r}")

# ---------------------------------------------------------------------------
# get_iv_rank("AAPL") -- HV-proxy path (current_iv=None), live yfinance data
# ---------------------------------------------------------------------------
print("\nget_iv_rank('AAPL') HV-proxy fallback (current_iv=None), live data")

baseline = get_iv_rank("AAPL")
check("HV-proxy call has no error key (healthy symbol, enough history)",
      "error" not in baseline, f"got {baseline}")
check("iv_rank is a float in [0, 100]",
      isinstance(baseline.get("iv_rank"), float) and 0.0 <= baseline["iv_rank"] <= 100.0,
      f"got {baseline.get('iv_rank')!r}")
check("iv_pct is a float in [0, 100]",
      isinstance(baseline.get("iv_pct"), float) and 0.0 <= baseline["iv_pct"] <= 100.0,
      f"got {baseline.get('iv_pct')!r}")
check("hv_52w_low <= hv_52w_high",
      baseline["hv_52w_low"] <= baseline["hv_52w_high"],
      f"low={baseline['hv_52w_low']!r} high={baseline['hv_52w_high']!r}")
check("current_iv is present and numeric (not None)",
      isinstance(baseline.get("current_iv"), (int, float)),
      f"got {baseline.get('current_iv')!r}")

# Cross-check: current_iv on the HV-proxy path must genuinely be the HV
# proxy and not some other value -- re-fetch the same 1y history
# independently and re-run the REAL _historical_volatility() over the same
# trailing 31-close window get_iv_rank() itself uses (closes[-31:],
# window=30, matching its internal hvs[-1] computation).
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")
closes = hist["Close"].tolist()
recomputed_current_hv_pct = round(_historical_volatility(closes[-31:], window=30) * 100, 1)
check("HV-proxy current_iv matches an independent re-fetch + re-run of "
      "_historical_volatility() over the same trailing window "
      "(small tolerance for inter-call timing/rounding)",
      abs(recomputed_current_hv_pct - baseline["current_iv"]) <= 0.3,
      f"recomputed={recomputed_current_hv_pct!r} returned={baseline['current_iv']!r}")

# ---------------------------------------------------------------------------
# get_iv_rank("AAPL", current_iv=0.25) -- override path
# ---------------------------------------------------------------------------
print("\nget_iv_rank('AAPL', current_iv=0.25) override path, live data")

overridden = get_iv_rank("AAPL", current_iv=0.25)
check("override current_iv surfaces exactly as round(0.25*100, 1) == 25.0, "
      "not re-derived from HV",
      overridden.get("current_iv") == 25.0, f"got {overridden.get('current_iv')!r}")
check("override path uses the SAME hv_52w_low/high range as the HV-proxy "
      "path for the same symbol (same underlying 1y history)",
      overridden["hv_52w_low"] == baseline["hv_52w_low"]
      and overridden["hv_52w_high"] == baseline["hv_52w_high"],
      f"baseline low/high={baseline['hv_52w_low']}/{baseline['hv_52w_high']} "
      f"overridden low/high={overridden['hv_52w_low']}/{overridden['hv_52w_high']}")

# Verify the percentile ranking math directly: hand-compute the expected
# rank from the RETURNED hv_52w_low/high using iv_rank.py's own documented
# formula ((iv - low) / (high - low) * 100) -- not a copy of the
# implementation's internals, a check of its output against the formula it
# claims to implement. Small tolerance for the *100-rounding already baked
# into the low/high/current_iv fields themselves.
lo, hi = overridden["hv_52w_low"], overridden["hv_52w_high"]
expected_rank = (overridden["current_iv"] - lo) / (hi - lo) * 100
check("iv_rank for the override matches the hand-computed percentile "
      "position between the returned hv_52w_low/high",
      abs(overridden["iv_rank"] - expected_rank) < 1.0,
      f"expected~={expected_rank!r} got={overridden['iv_rank']!r}")

# ---------------------------------------------------------------------------
# Failure shape for an invalid/delisted symbol -- confirmed live, not
# assumed. Reading iv_rank.py: the len(closes) < 60 guard (line ~44) returns
# {"symbol", "iv_rank": None, "iv_pct": None, "error": "insufficient_data"}
# -- carries an "error" key. A second, error-key-less failure shape exists
# at line ~53 (empty `hvs` list) but is unreachable through get_iv_rank()'s
# own public contract: once len(closes) >= 60 passes the guard above,
# range(30, len(closes)) always yields >= 30 entries in hvs, so that branch
# can never actually fire. Flagged in the report as dead code, not a bug --
# asserting on it here would be asserting on unreachable code.
# ---------------------------------------------------------------------------
print("\nget_iv_rank(): invalid/delisted symbol failure shape")

bad = get_iv_rank("ZZZZINVALIDXX")
check("invalid symbol returns the insufficient_data shape with an 'error' "
      "key (confirmed live, not the error-key-less empty-hvs shape)",
      bad == {"symbol": "ZZZZINVALIDXX", "iv_rank": None, "iv_pct": None,
              "error": "insufficient_data"},
      f"got {bad!r}")

# ---------------------------------------------------------------------------
# batch_iv_rank -- both symbols individually match the shapes verified above
# ---------------------------------------------------------------------------
print("\nbatch_iv_rank(['AAPL', 'MSFT'])")

batch = batch_iv_rank(["AAPL", "MSFT"])
check("batch result has exactly the requested symbols as keys",
      set(batch.keys()) == {"AAPL", "MSFT"}, f"got {list(batch.keys())!r}")
for sym in ("AAPL", "MSFT"):
    res = batch[sym]
    check(f"batch[{sym}] has no error key (healthy symbol)",
          "error" not in res, f"got {res}")
    check(f"batch[{sym}] iv_rank is a float in [0, 100]",
          isinstance(res.get("iv_rank"), float) and 0.0 <= res["iv_rank"] <= 100.0,
          f"got {res.get('iv_rank')!r}")
    check(f"batch[{sym}] hv_52w_low <= hv_52w_high",
          res["hv_52w_low"] <= res["hv_52w_high"],
          f"low={res.get('hv_52w_low')!r} high={res.get('hv_52w_high')!r}")
    check(f"batch[{sym}] current_iv is numeric (HV-proxy path, no override passed)",
          isinstance(res.get("current_iv"), (int, float)), f"got {res.get('current_iv')!r}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
