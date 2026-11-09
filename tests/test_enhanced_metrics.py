"""
Characterization tests for mcp/reports/enhanced_metrics.py (Bolt B10).

enhanced_metrics.py had ZERO test coverage before this Bolt. This suite is
the safety net a future refactor needs: get_ticker_metrics() (lines 172-557,
~386 lines in a single function) is the single worst Code Quality & Modularity
Gate function-length violation found across this wave of audits (file/function
limit is 50 lines -- nearly 8x over). It is NOT refactored here, by design --
see the PR this Bolt opens for the follow-up issue.

Covers:
  - BlackScholesGreeks: delta/gamma/theta/vega checked against an INDEPENDENT
    from-scratch Black-Scholes re-implementation below (math.erf-based normal
    CDF -- deliberately not scipy, so it isn't just re-running the module's
    own math), anchored to the classic Hull "Options, Futures and Other
    Derivatives" textbook example (S=42, K=40, r=0.1, sigma=0.2, T=0.5).
  - TechnicalIndicators.rsi/macd/bollinger_bands: hand-constructed series with
    exactly-computable expected values (monotonic/alternating series for RSI,
    constant/spike series for MACD and Bollinger).
  - get_ticker_metrics: a live yfinance call (AAPL) spot-checked against
    independently (re-)computed RSI/200-day-MA/range-position figures from the
    same history, plus a deterministic mocked-history test proving the
    call-vs-put RSI calibration (GitHub issue #1 backtest) actually produces
    different conviction scores, plus a no-data-ticker robustness check.
  - batch_get_metrics: consistency against individual get_ticker_metrics calls,
    and that repeat calls are served from cache.
  - _load_metrics_cache / _save_metrics_cache: round trip + corrupt/missing
    file resilience, via a temp cache path (the real cache is never touched).

No pytest dependency -- run directly: python3 tests/test_enhanced_metrics.py
"""
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pandas as pd
import yfinance as yf

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "reports"))

import enhanced_metrics as em  # noqa: E402
from enhanced_metrics import BlackScholesGreeks, TechnicalIndicators  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# =============================================================================
# BlackScholesGreeks -- independent from-scratch reference implementation
# (math.erf-based normal CDF, NOT scipy) so the test isn't just re-running
# the module's own formulas back at itself.
# =============================================================================
print("BlackScholesGreeks vs independent Black-Scholes reference")


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _norm_pdf(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def _ref_d1(S, K, T, r, sigma):
    return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))


def _ref_d2(S, K, T, r, sigma):
    return _ref_d1(S, K, T, r, sigma) - sigma * math.sqrt(T)


def _ref_call_delta(S, K, T, r, sigma):
    return _norm_cdf(_ref_d1(S, K, T, r, sigma))


def _ref_gamma(S, K, T, r, sigma):
    d1 = _ref_d1(S, K, T, r, sigma)
    return _norm_pdf(d1) / (S * sigma * math.sqrt(T))


def _ref_call_theta(S, K, T, r, sigma):
    d1 = _ref_d1(S, K, T, r, sigma)
    d2 = _ref_d2(S, K, T, r, sigma)
    theta = (-(S * _norm_pdf(d1) * sigma) / (2 * math.sqrt(T))
             - r * K * math.exp(-r * T) * _norm_cdf(d2))
    return theta / 365.0


def _ref_put_theta(S, K, T, r, sigma):
    d1 = _ref_d1(S, K, T, r, sigma)
    d2 = _ref_d2(S, K, T, r, sigma)
    theta = (-(S * _norm_pdf(d1) * sigma) / (2 * math.sqrt(T))
             + r * K * math.exp(-r * T) * _norm_cdf(-d2))
    return theta / 365.0


def _ref_vega(S, K, T, r, sigma):
    d1 = _ref_d1(S, K, T, r, sigma)
    return S * _norm_pdf(d1) * math.sqrt(T) / 100.0


# Hull's textbook example: S=42, K=40, T=0.5 years, r=0.1, sigma=0.2
# (the same parameters used to derive the textbook's ~$4.76 call price).
S, K, T, r, sigma = 42.0, 40.0, 0.5, 0.1, 0.2
ref_delta = _ref_call_delta(S, K, T, r, sigma)
ref_gamma_v = _ref_gamma(S, K, T, r, sigma)
ref_theta = _ref_call_theta(S, K, T, r, sigma)
ref_vega_v = _ref_vega(S, K, T, r, sigma)
mod_delta = BlackScholesGreeks.call_delta(S, K, T, r, sigma)
mod_gamma = BlackScholesGreeks.gamma(S, K, T, r, sigma)
mod_theta = BlackScholesGreeks.call_theta(S, K, T, r, sigma)
mod_vega = BlackScholesGreeks.vega(S, K, T, r, sigma)

check("call_delta matches the independent BS reference AND the Hull textbook "
      "figure (~0.7791)",
      abs(mod_delta - ref_delta) < 1e-9 and abs(ref_delta - 0.7791) < 0.001,
      f"module={mod_delta} ref={ref_delta}")
check("gamma matches the independent BS reference AND the Hull figure (~0.0500)",
      abs(mod_gamma - ref_gamma_v) < 1e-9 and abs(ref_gamma_v - 0.0500) < 0.001,
      f"module={mod_gamma} ref={ref_gamma_v}")
check("call_theta (per day) matches the independent BS reference AND the Hull "
      "figure (~-0.01249/day)",
      abs(mod_theta - ref_theta) < 1e-9 and abs(ref_theta - (-0.01249)) < 0.0001,
      f"module={mod_theta} ref={ref_theta}")
check("vega (per 1% IV) matches the independent BS reference AND the Hull "
      "figure (~0.0881)",
      abs(mod_vega - ref_vega_v) < 1e-9 and abs(ref_vega_v - 0.0881) < 0.001,
      f"module={mod_vega} ref={ref_vega_v}")

mod_put_theta = BlackScholesGreeks.put_theta(S, K, T, r, sigma)
ref_put_theta_v = _ref_put_theta(S, K, T, r, sigma)
check("put_theta matches the independent BS reference",
      abs(mod_put_theta - ref_put_theta_v) < 1e-9,
      f"module={mod_put_theta} ref={ref_put_theta_v}")

print("\nDirectional sanity -- deep ITM / deep OTM / ATM delta")
d_itm = BlackScholesGreeks.call_delta(200.0, 100.0, 0.25, 0.03, 0.25)
check("deep ITM call delta is near 1.0", d_itm > 0.99, f"got {d_itm}")

d_otm = BlackScholesGreeks.call_delta(50.0, 100.0, 0.25, 0.03, 0.25)
check("deep OTM call delta is near 0.0", d_otm < 0.01, f"got {d_otm}")

d_atm = BlackScholesGreeks.call_delta(100.0, 100.0, 1.0, 0.0, 0.2)
ref_atm = _ref_call_delta(100.0, 100.0, 1.0, 0.0, 0.2)
check("ATM (r=0) call delta is near 0.5 and matches the independent reference "
      "exactly (small positive drift from the sigma^2/2 term)",
      abs(d_atm - 0.5) < 0.05 and abs(d_atm - ref_atm) < 1e-9,
      f"got {d_atm}, ref {ref_atm}")

print("\nput_delta = call_delta - 1 (put-call parity on delta)")
put_d = BlackScholesGreeks.put_delta(S, K, T, r, sigma)
check("put_delta equals call_delta - 1", abs(put_d - (ref_delta - 1)) < 1e-9, f"got {put_d}")

print("\nT=0 / sigma<=0 edge cases -- no division by zero, deterministic collapse")
check("T=0, S>K -> call_delta is exactly 1.0 (expired ITM)",
      BlackScholesGreeks.call_delta(110.0, 100.0, 0, 0.03, 0.25) == 1.0)
check("T=0, S<K -> call_delta is exactly 0.0 (expired OTM)",
      BlackScholesGreeks.call_delta(90.0, 100.0, 0, 0.03, 0.25) == 0.0)
check("T=0 -> gamma is exactly 0.0 (no division by zero)",
      BlackScholesGreeks.gamma(110.0, 100.0, 0, 0.03, 0.25) == 0.0)
check("sigma<=0 -> vega is exactly 0.0 (no division by zero)",
      BlackScholesGreeks.vega(100.0, 100.0, 0.5, 0.03, 0) == 0.0)


# =============================================================================
# TechnicalIndicators -- hand-constructed series, exactly-computable values
# =============================================================================
print("\nTechnicalIndicators.rsi -- hand-computed reference series")

closes_up = pd.Series(range(100, 115))  # 15 points -> 14 consecutive +1 diffs
check("RSI on a monotonically increasing 15-point series is exactly 100.0 "
      "(all 14 rolling diffs are gains, loss=0 -> RS=inf -> RSI=100)",
      TechnicalIndicators.rsi(closes_up) == 100.0,
      f"got {TechnicalIndicators.rsi(closes_up)}")

closes_down = pd.Series(range(115, 100, -1))
check("RSI on a monotonically decreasing 15-point series is exactly 0.0",
      TechnicalIndicators.rsi(closes_down) == 0.0,
      f"got {TechnicalIndicators.rsi(closes_down)}")

alt = [100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100]
closes_alt = pd.Series(alt)
check("RSI on an alternating +1/-1 series (7 gains, 7 equal-magnitude losses "
      "over the 14-window -> RS=1) is exactly 50.0",
      TechnicalIndicators.rsi(closes_alt) == 50.0,
      f"got {TechnicalIndicators.rsi(closes_alt)}")

short_series = pd.Series(range(100, 105))  # len 5 < period(14)+1
check("RSI on a series shorter than period+1 falls back to the documented "
      "default 50.0",
      TechnicalIndicators.rsi(short_series) == 50.0,
      f"got {TechnicalIndicators.rsi(short_series)}")

print("\nTechnicalIndicators.macd -- constant-price series collapses to exact zero")
const_closes = pd.Series([50.0] * 30)
macd_const = TechnicalIndicators.macd(const_closes)
check("MACD/signal/histogram are all exactly 0.0 for a constant-price series "
      "(12/26-EMA of a constant is that constant, so the difference is 0)",
      macd_const == {"macd": 0.0, "signal": 0.0, "histogram": 0.0},
      f"got {macd_const}")

print("\nTechnicalIndicators.bollinger_bands -- hand-computed std-dev series")
bb_const = TechnicalIndicators.bollinger_bands(const_closes)
check("constant-price series collapses all bands to the price, pct_b default 0.5",
      bb_const == {"upper": 50.0, "middle": 50.0, "lower": 50.0, "pct_b": 0.5},
      f"got {bb_const}")

# 19 values of 10.0 + one jump to 20.0 -- sample std (pandas default ddof=1):
# mean = 10.5; variance = (19*(10-10.5)^2 + (20-10.5)^2) / (20-1)
#             = (19*0.25 + 90.25) / 19 = 95/19 = 5.0; std = sqrt(5) ~= 2.236068
spike_closes = pd.Series([10.0] * 19 + [20.0])
bb_spike = TechnicalIndicators.bollinger_bands(spike_closes)
hand_mean = 10.5
hand_std = math.sqrt(5.0)
hand_upper = hand_mean + 2.0 * hand_std
hand_lower = hand_mean - 2.0 * hand_std
check("Bollinger middle band matches the hand-computed mean (10.5)",
      abs(bb_spike["middle"] - hand_mean) < 1e-6, f"got {bb_spike['middle']}")
check("Bollinger upper band matches hand-computed mean + 2*std (~14.972)",
      abs(bb_spike["upper"] - hand_upper) < 1e-6, f"got {bb_spike['upper']}")
check("Bollinger lower band matches hand-computed mean - 2*std (~6.028)",
      abs(bb_spike["lower"] - hand_lower) < 1e-6, f"got {bb_spike['lower']}")
check("pct_b is clipped to 1.0 (raw value ~1.562 since price sits above the "
      "upper band -- clipping behavior, not a fabricated reading)",
      bb_spike["pct_b"] == 1.0, f"got {bb_spike['pct_b']}")


# =============================================================================
# get_ticker_metrics -- documented field set + spot checks
# =============================================================================
_EXPECTED_KEYS = {
    "ticker", "price", "conviction", "rsi", "macd", "macd_histogram",
    "bb_position", "roc_7d", "pct_above_50ma", "pct_above_200ma",
    "position_in_52w_range", "week_52_high", "week_52_low", "pe_ratio",
    "heat_status", "heat_reason", "revenue_growth", "earnings_growth",
    "analyst_rating", "target_upside_pct",
}

print("\nget_ticker_metrics -- option_type RSI calibration (deterministic, "
      "mocked history -- GitHub issue #1 backtest)")


class _FakeTicker:
    """Minimal yf.Ticker stand-in: no fundamentals, a controlled price history."""

    def __init__(self, ticker):
        self.ticker = ticker
        self.info = {}

    def history(self, period="1y"):
        # Monotonic increase -> RSI(14) = 100.0 (overbought), deterministically.
        return pd.DataFrame({"Close": list(range(100, 130))})


with mock.patch.object(em, "yf") as fake_yf:
    fake_yf.Ticker.side_effect = _FakeTicker
    call_m = em.get_ticker_metrics("FAKE", 129.0, option_type=None)
    put_m = em.get_ticker_metrics("FAKE", 129.0, option_type="P")

check("both calls see the same overbought RSI=100.0 from identical mocked history",
      call_m["rsi"] == 100.0 and put_m["rsi"] == 100.0,
      f"call_rsi={call_m['rsi']} put_rsi={put_m['rsi']}")
# Hand-derived: with info={} (no fundamentals/52wk data), the only score
# contributions are RSI and MACD (both identical except RSI's sign/magnitude).
# Call: RSI>70 -> -1.0, call-side MACD bullish (+1.5) -> raw=0.5 ->
#   conviction = 5.0 + 5.0*(0.5/11.0) = 5.227... -> round(1) = 5.2
# Put:  RSI>70 -> +1.0 (best-performing put bucket per backtest), same MACD
#   (+1.5) -> raw=2.5 -> conviction = 5.0 + 5.0*(2.5/11.0) = 6.136... -> 6.1
check("call-side overbought RSI penalizes conviction (hand-derived 5.2)",
      call_m["conviction"] == 5.2, f"got {call_m['conviction']}")
check("put-side overbought RSI is the backtest's best-performing bucket and "
      "rewards conviction instead (hand-derived 6.1)",
      put_m["conviction"] == 6.1, f"got {put_m['conviction']}")
check("put conviction exceeds call conviction for the identical overbought "
      "reading (the call/put RSI calibration actually takes effect)",
      put_m["conviction"] > call_m["conviction"],
      f"call={call_m['conviction']} put={put_m['conviction']}")

print("\nget_ticker_metrics -- live yfinance call (AAPL), internal-consistency "
      "spot checks")

aapl_stock = yf.Ticker("AAPL")
aapl_hist = aapl_stock.history(period="1y")
aapl_closes = aapl_hist["Close"]
aapl_price = float(aapl_closes.iloc[-1])

m = em.get_ticker_metrics("AAPL", aapl_price)

check("get_ticker_metrics returns exactly the documented field set",
      set(m.keys()) == _EXPECTED_KEYS, f"got {sorted(m.keys())}")
check("price field matches the input price (rounded to 2dp)",
      m["price"] == round(aapl_price, 2), f"got {m['price']} vs input {aapl_price}")
check("conviction is within the documented 1-10 scale",
      1.0 <= m["conviction"] <= 10.0, f"got {m['conviction']}")
check("heat_status is one of the three documented buckets",
      m["heat_status"] in ("RED", "YELLOW", "GREEN"), f"got {m['heat_status']}")

# Spot-check rsi against an INDEPENDENT TechnicalIndicators.rsi() call over the
# same history fetched here, separately from get_ticker_metrics' own fetch --
# an internal-consistency check, not a duplicate of the module's computation.
independent_rsi = TechnicalIndicators.rsi(aapl_closes)
check("get_ticker_metrics' rsi is internally consistent with an independent "
      "TechnicalIndicators.rsi() call over the same history",
      abs(m["rsi"] - independent_rsi) < 1.0,
      f"module={m['rsi']} independent={independent_rsi}")

if len(aapl_closes) >= 200:
    independent_ma200 = float(aapl_closes.tail(200).mean())
    independent_pct_above_200ma = (aapl_price / independent_ma200 - 1) * 100
    check("pct_above_200ma is internally consistent with an independently "
          "hand-computed 200-day average",
          m["pct_above_200ma"] is not None
          and abs(m["pct_above_200ma"] - independent_pct_above_200ma) < 0.5,
          f"module={m['pct_above_200ma']} independent={independent_pct_above_200ma}")

if m["week_52_high"] and m["week_52_low"] and m["week_52_high"] > m["week_52_low"]:
    independent_pos = (aapl_price - m["week_52_low"]) / (m["week_52_high"] - m["week_52_low"]) * 100
    independent_pos = max(0, min(100, independent_pos))
    check("position_in_52w_range is internally consistent with the returned "
          "52-week high/low",
          abs(m["position_in_52w_range"] - independent_pos) < 1.0,
          f"module={m['position_in_52w_range']} independent={independent_pos}")

print("\nget_ticker_metrics -- no-data ticker is resilient (no crash, sane defaults)")
no_data = em.get_ticker_metrics("ZZZZINVALIDTICKER9999", 42.0)
check("an invalid/no-data ticker still returns the full documented field set",
      set(no_data.keys()) == _EXPECTED_KEYS, f"got {sorted(no_data.keys())}")
check("price is preserved even with no Yahoo data",
      no_data["price"] == 42.0, f"got {no_data['price']}")
check("conviction stays within the 1-10 scale even with no Yahoo data",
      1.0 <= no_data["conviction"] <= 10.0, f"got {no_data['conviction']}")
check("heat_status is still one of the three documented buckets",
      no_data["heat_status"] in ("RED", "YELLOW", "GREEN"), f"got {no_data['heat_status']}")


# =============================================================================
# batch_get_metrics -- consistency with individual calls + caching
# =============================================================================
print("\nbatch_get_metrics -- consistency with individual get_ticker_metrics "
      "calls + same-day caching")

_batch_tmp_dir = tempfile.mkdtemp(prefix="theta_lab_test_enhanced_metrics_batch_")
_batch_cache_file = str(Path(_batch_tmp_dir) / "ticker_metrics_cache_test.json")

_batch_tickers = ["MSFT", "KO"]
_batch_prices = {"MSFT": 500.0, "KO": 70.0}

with mock.patch.object(em, "_METRICS_CACHE_FILE", _batch_cache_file), \
     mock.patch.object(em, "_INTER_TICKER_DELAY_SECONDS", 0.0):
    batch_results = em.batch_get_metrics(_batch_tickers, _batch_prices)
    individual_results = {t: em.get_ticker_metrics(t, _batch_prices[t]) for t in _batch_tickers}

for _t in _batch_tickers:
    check(f"batch_get_metrics({_t}) matches an individual get_ticker_metrics({_t}) call",
          batch_results[_t] == individual_results[_t],
          f"batch={batch_results[_t]} individual={individual_results[_t]}")

check("batch_get_metrics wrote a same-day cache file",
      os.path.exists(_batch_cache_file), f"expected cache at {_batch_cache_file}")

with open(_batch_cache_file) as _f:
    _cache_contents = json.load(_f)
check("the cache contains an entry for each ticker",
      set(_cache_contents.keys()) == set(_batch_tickers), f"got {list(_cache_contents.keys())}")

# A second call against the same cache file must be served entirely from
# cache -- force get_ticker_metrics to raise if it's called again, proving
# the hit (not just "results happen to match").
with mock.patch.object(em, "_METRICS_CACHE_FILE", _batch_cache_file), \
     mock.patch.object(em, "get_ticker_metrics",
                        side_effect=AssertionError("cache miss -- should have been served from cache")):
    cached_batch = em.batch_get_metrics(_batch_tickers, _batch_prices)
check("a same-day re-run is served entirely from cache (get_ticker_metrics "
      "never invoked, no AssertionError raised)",
      cached_batch[_batch_tickers[0]]["ticker"] == _batch_tickers[0]
      and cached_batch[_batch_tickers[1]]["ticker"] == _batch_tickers[1],
      f"got {cached_batch}")


# =============================================================================
# _load_metrics_cache / _save_metrics_cache -- round trip + corruption
# =============================================================================
print("\n_load_metrics_cache / _save_metrics_cache -- round trip + corrupt-file "
      "resilience (temp path, real cache never touched)")

_cache_rt_dir = tempfile.mkdtemp(prefix="theta_lab_test_enhanced_metrics_cache_rt_")
_cache_rt_file = str(Path(_cache_rt_dir) / "subdir" / "cache_roundtrip.json")

with mock.patch.object(em, "_METRICS_CACHE_FILE", _cache_rt_file):
    check("loading a cache file that doesn't exist yet returns {} (not a crash)",
          em._load_metrics_cache() == {}, f"got {em._load_metrics_cache()}")

    sample = {"AAPL": {"ticker": "AAPL", "price": 100.0, "_cached_at": 123.0}}
    em._save_metrics_cache(sample)
    check("_save_metrics_cache creates the file (and its parent dir, which "
          "didn't exist yet)",
          os.path.exists(_cache_rt_file), f"expected file at {_cache_rt_file}")
    check("round trip: what's loaded back matches exactly what was saved",
          em._load_metrics_cache() == sample, f"got {em._load_metrics_cache()}")

    with open(_cache_rt_file, "w") as _f:
        _f.write("{not valid json at all")
    check("loading a corrupt cache file returns {} instead of raising",
          em._load_metrics_cache() == {}, f"got {em._load_metrics_cache()}")

    em._save_metrics_cache({"recovered": True})
    check("saving after a corruption overwrites cleanly (no lingering corrupt state)",
          em._load_metrics_cache() == {"recovered": True}, f"got {em._load_metrics_cache()}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
