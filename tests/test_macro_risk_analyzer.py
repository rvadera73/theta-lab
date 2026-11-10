"""
Characterization tests for mcp/analysis/macro_risk_analyzer.py --
the crash early-warning logic behind data/macro_risk_history.yaml and the
morning-briefing risk assessment. Zero test coverage existed before this file.

IMPORTANT real finding (read before touching this file): `analyze_risk()`'s
own `market_data` argument is **not actually used** to compute any signal.
`estimate_breadth(market_data)` ignores its argument and always calls
`get_breadth_from_yahoo()`; `estimate_ad_ratio()`, `get_vix_term_structure()`,
`get_hyoas()`, `get_put_call_ratio()`, `get_yield_curve()` take no market_data
at all. Every real signal is either a live Yahoo Finance / FRED fetch or a
hardcoded stub (get_put_call_ratio() always returns 0.75). The docstring's
"vix / spx_price / spx_50ma / spx_200ma" contract is aspirational, not real.
This means the only way to exercise analyze_risk()'s actual decision logic
(thresholds, severity, probability math, staging, primary-risk selection)
deterministically is to monkeypatch those six fetch methods at the instance
level -- which is what every fixture below does. This is flagged as a real
finding in the PR description, not silently worked around.

Also confirmed here: the `fetch_fred_data` key is the "FRED API key is dead"
dependency from prior known issues -- the comment in fetch_fred_data's
docstring documents that the registered-key endpoint returned HTTP 400 and
fetch_fred_data was rewritten to hit the public fredgraph.csv feed instead
(no key needed). We exercise the REAL fetch_fred_data/get_hyoas/get_yield_curve
parsing + fallback logic by monkeypatching only `requests.get` (the actual
network boundary), not the methods themselves.

No pytest dependency -- run directly: python3 tests/test_macro_risk_analyzer.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "analysis"))

import macro_risk_analyzer
from macro_risk_analyzer import MacroRiskAnalyzer, analyze_macro_risk

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def make_analyzer(breadth=70.0, ad_ratio=1.2, vix_term_type="CONTANGO",
                   hyoas=350.0, pcr=0.75, yield_curve=0.6):
    """A MacroRiskAnalyzer with its six external data-fetch methods pinned to
    controlled values (no network calls), so everything downstream of them --
    thresholding, severity, probability math, staging, primary-risk selection
    -- runs as REAL, unmocked analyzer code. Defaults are all-GREEN.

    Overriding via plain function assignment on the instance (not the class)
    means these are NOT bound as methods -- callers inside analyze_risk invoke
    them as `self.estimate_breadth(market_data)` etc., so the replacements
    must accept exactly the same args the real methods take, minus `self`.
    """
    a = MacroRiskAnalyzer()
    a.estimate_breadth = lambda market_data: breadth
    a.estimate_ad_ratio = lambda: ad_ratio
    a.get_vix_term_structure = lambda: {
        "type": vix_term_type, "front_vix": 15.8, "back_vix": 18.2,
    }
    a.get_hyoas = lambda: hyoas
    a.get_put_call_ratio = lambda: pcr
    a.get_yield_curve = lambda: yield_curve
    return a


# ---------------------------------------------------------------------------
# GREEN fixture -- every signal below its yellow threshold
# ---------------------------------------------------------------------------
print("GREEN fixture -- all 6 signals healthy")

green = make_analyzer()
r_green = green.analyze_risk({})
check("all-healthy inputs -> risk_level GREEN", r_green["risk_level"] == "GREEN",
      f"got {r_green['risk_level']}")
check("all-healthy inputs -> stage 0", r_green["stage"] == 0, f"got {r_green['stage']}")
check("no signal flagged -> severity_sum == 0.0",
      r_green["crash_probability"]["prob_30d"] == 6.0,  # base_prob_30d, no severity added
      f"got prob_30d={r_green['crash_probability']['prob_30d']}")
check("no elevated signal -> primary_risk is 'Market neutral'",
      r_green["crash_probability"]["primary_risk"] == "Market neutral",
      f"got {r_green['crash_probability']['primary_risk']}")
check("'Market neutral' -> sector_sensitivity is {} (no driver to map)",
      r_green["sector_sensitivity"] == {}, f"got {r_green['sector_sensitivity']}")
check("each individual signal reports GREEN status",
      all(s["status"] == "GREEN" for s in r_green["signals"].values()),
      f"got {[(k, v['status']) for k, v in r_green['signals'].items()]}")


# ---------------------------------------------------------------------------
# YELLOW fixture -- breadth and ad_ratio both dip into their yellow bands
# breadth=52 (yellow 60 / red 50): severity = (60-52)/10 = 0.8
# ad_ratio=0.85 (yellow 1.0 / red 0.8): severity = (1.0-0.85)/0.2 = 0.75
# severity_sum = 1.55 -> prob_30d = 6.0 + 1.55*15 = 29.25 (in the 20-60 YELLOW band)
# ---------------------------------------------------------------------------
print("\nYELLOW fixture -- breadth + ad_ratio both yellow (hand-calculated severity)")

yellow = make_analyzer(breadth=52.0, ad_ratio=0.85)
r_yellow = yellow.analyze_risk({})
cp_y = r_yellow["crash_probability"]
check("breadth=52 status is YELLOW", r_yellow["signals"]["breadth"]["status"] == "YELLOW",
      f"got {r_yellow['signals']['breadth']['status']}")
check("ad_ratio=0.85 status is YELLOW", r_yellow["signals"]["ad_ratio"]["status"] == "YELLOW",
      f"got {r_yellow['signals']['ad_ratio']['status']}")
check("hand-calculated severity_sum (0.8 + 0.75 = 1.55) matches prob_30d formula",
      abs(cp_y["prob_30d"] - 29.25) < 1e-9, f"got {cp_y['prob_30d']}")
check("prob_30d=29.25 (20-60 band) -> risk_level YELLOW", r_yellow["risk_level"] == "YELLOW",
      f"got {r_yellow['risk_level']}")
check("prob_30d=29.25 -> stage 1", r_yellow["stage"] == 1, f"got {r_yellow['stage']}")
check("breadth (severity 0.8) beats ad_ratio (0.75) as primary_risk",
      cp_y["primary_risk"] == "BREADTH elevated", f"got {cp_y['primary_risk']}")


# ---------------------------------------------------------------------------
# RED fixture -- breadth, ad_ratio and hyoas all breach their red thresholds,
# hyoas clearly the worst (unambiguous primary_risk winner)
# breadth=45 (red 50/yellow 60, gap 10): past-red -> 1.0 + (50-45)/20 = 1.25
# ad_ratio=0.9 (red 0.8/yellow 1.0, gap 0.2): pre-red -> (1.0-0.9)/0.2 = 0.5
# hyoas=800 (red 450/yellow 400, gap 50): past-red -> 1.0 + (800-450)/100 = 1.0 (capped)
#   -> hyoas severity = 2.0 (clamped cap)
# severity_sum = 1.25 + 0.5 + 2.0 = 3.75 -> prob_30d = 6 + 3.75*15 = 62.25 (>=60 RED)
# prob_60d = 11 + 3.75*25 = 104.75 -> capped at 95.0
# prob_90d = 16 + 3.75*35 = 147.25 -> capped at 95.0
# ---------------------------------------------------------------------------
print("\nRED fixture -- breadth/ad_ratio/hyoas all red, hyoas clearly worst (hand-calculated)")

red = make_analyzer(breadth=45.0, ad_ratio=0.9, hyoas=800.0)
r_red = red.analyze_risk({})
cp_r = r_red["crash_probability"]
check("breadth=45 status is RED", r_red["signals"]["breadth"]["status"] == "RED",
      f"got {r_red['signals']['breadth']['status']}")
check("ad_ratio=0.9 status is YELLOW (>= red threshold 0.8)",
      r_red["signals"]["ad_ratio"]["status"] == "YELLOW",
      f"got {r_red['signals']['ad_ratio']['status']}")
check("hyoas=800 status is RED", r_red["signals"]["hyoas"]["status"] == "RED",
      f"got {r_red['signals']['hyoas']['status']}")
check("hand-calculated severity_sum (1.25+0.5+2.0=3.75) matches prob_30d formula",
      abs(cp_r["prob_30d"] - 62.25) < 1e-9, f"got {cp_r['prob_30d']}")
check("prob_30d=62.25 (>=60) -> risk_level RED", r_red["risk_level"] == "RED",
      f"got {r_red['risk_level']}")
check("prob_30d>=60 -> stage 2", r_red["stage"] == 2, f"got {r_red['stage']}")
check("uncapped prob_60d (104.75) is capped at 95.0", cp_r["prob_60d"] == 95.0,
      f"got {cp_r['prob_60d']}")
check("uncapped prob_90d (147.25) is capped at 95.0", cp_r["prob_90d"] == 95.0,
      f"got {cp_r['prob_90d']}")
check("hyoas (severity 2.0, clearly worst) selected as primary_risk",
      cp_r["primary_risk"] == "HYOAS critical", f"got {cp_r['primary_risk']}")
check("RED stage action_trigger is the 70%+ EMERGENCY band only above prob 70 -- "
      "62.25 should land in the 50-70 HIGH RISK band",
      "HIGH RISK" in cp_r["action_trigger"], f"got {cp_r['action_trigger']}")


# ---------------------------------------------------------------------------
# primary_risk tie-break -- two indicators with IDENTICAL severity.
# ad_ratio=0.5 (red 0.8/yellow 1.0, gap 0.2): past-red -> 1.0 + (0.8-0.5)/0.4 = 1.75
# hyoas=525 (red 450/yellow 400, gap 50): past-red -> 1.0 + (525-450)/100 = 1.75
# Both RED, both severity 1.75 -- confirms current tie-break: strict ">"
# comparison means the FIRST indicator encountered in signals-dict insertion
# order (breadth, ad_ratio, vix_term, hyoas, pcr, yield_curve) wins a tie,
# not any semantic priority. This is current, real behavior -- documented
# here, not changed.
# ---------------------------------------------------------------------------
print("\nprimary_risk tie-break -- ad_ratio and hyoas tied at severity 1.75")

tie = make_analyzer(ad_ratio=0.5, hyoas=525.0)
r_tie = tie.analyze_risk({})
cp_t = r_tie["crash_probability"]
check("ad_ratio=0.5 status is RED", r_tie["signals"]["ad_ratio"]["status"] == "RED",
      f"got {r_tie['signals']['ad_ratio']['status']}")
check("hyoas=525 status is RED", r_tie["signals"]["hyoas"]["status"] == "RED",
      f"got {r_tie['signals']['hyoas']['status']}")
check("both tied indicators compute to the SAME severity (1.75) via _indicator_severity",
      abs(tie._indicator_severity("ad_ratio", 0.5) - tie._indicator_severity("hyoas", 525.0)) < 1e-9,
      f"ad_ratio={tie._indicator_severity('ad_ratio', 0.5)} hyoas={tie._indicator_severity('hyoas', 525.0)}")
check("on an exact severity tie, the first-in-iteration-order indicator "
      "(ad_ratio, inserted before hyoas) wins primary_risk -- current behavior",
      cp_t["primary_risk"] == "AD_RATIO critical", f"got {cp_t['primary_risk']}")
sector_t = r_tie["sector_sensitivity"]
check("primary_risk AD_RATIO maps to the AD_RATIO sector-sensitivity entry",
      sector_t.get("driver") == "AD_RATIO" and sector_t.get("confidence") == "strong",
      f"got {sector_t}")


# ---------------------------------------------------------------------------
# Stage transition -- RED/stage 2 reverting to YELLOW/stage 1, matching the
# documented real-world pattern (Nov 6 RED/Stage-2 spike reverting to
# YELLOW/Stage-1). Reuses the RED and YELLOW fixtures above as "before"/"after".
# ---------------------------------------------------------------------------
print("\nStage transition -- RED/stage2 de-escalating to YELLOW/stage1")

before = make_analyzer(breadth=45.0, ad_ratio=0.9, hyoas=800.0).analyze_risk({})
after = make_analyzer(breadth=52.0, ad_ratio=0.85).analyze_risk({})
check("before: stage 2 / RED", before["stage"] == 2 and before["risk_level"] == "RED",
      f"got stage={before['stage']} risk_level={before['risk_level']}")
check("after: stage 1 / YELLOW (de-escalation captured across two independent calls)",
      after["stage"] == 1 and after["risk_level"] == "YELLOW",
      f"got stage={after['stage']} risk_level={after['risk_level']}")
check("prob_30d actually decreased from before to after",
      after["crash_probability"]["prob_30d"] < before["crash_probability"]["prob_30d"],
      f"before={before['crash_probability']['prob_30d']} after={after['crash_probability']['prob_30d']}")


# ---------------------------------------------------------------------------
# Missing / malformed market_data -- confirms current (real) behavior: since
# analyze_risk() never actually reads any field off market_data (see module
# docstring above), None or a non-dict market_data does not raise. This is a
# real, slightly alarming finding (the documented input contract is not
# enforced -- or used -- at all), not a guess at "graceful" validation logic
# that doesn't exist in the source.
# ---------------------------------------------------------------------------
print("\nMissing/malformed market_data -- current behavior is 'ignored entirely', not validated")

benign = make_analyzer()
r_none = benign.analyze_risk(None)
check("market_data=None does not raise, still returns a full risk-assessment dict",
      set(["risk_level", "stage", "signals", "crash_probability"]).issubset(r_none.keys()),
      f"got keys={list(r_none.keys())}")
r_nonsense = benign.analyze_risk(123)
check("market_data as a non-dict (int) does not raise either -- confirms it is genuinely unused",
      r_nonsense["risk_level"] == r_none["risk_level"],
      f"got {r_nonsense['risk_level']} vs {r_none['risk_level']}")


# ---------------------------------------------------------------------------
# analyze_macro_risk() module-level entry point -- confirm it really
# delegates to a fresh MacroRiskAnalyzer().analyze_risk() rather than doing
# anything different. Monkeypatched at the CLASS level since
# analyze_macro_risk() constructs its own instance internally.
# ---------------------------------------------------------------------------
print("\nanalyze_macro_risk() entry point delegates correctly")

_orig = {
    name: getattr(MacroRiskAnalyzer, name)
    for name in ("estimate_breadth", "estimate_ad_ratio", "get_vix_term_structure",
                 "get_hyoas", "get_put_call_ratio", "get_yield_curve")
}
try:
    MacroRiskAnalyzer.estimate_breadth = lambda self, market_data: 52.0
    MacroRiskAnalyzer.estimate_ad_ratio = lambda self: 0.85
    MacroRiskAnalyzer.get_vix_term_structure = lambda self: {
        "type": "CONTANGO", "front_vix": 15.8, "back_vix": 18.2
    }
    MacroRiskAnalyzer.get_hyoas = lambda self: 350.0
    MacroRiskAnalyzer.get_put_call_ratio = lambda self: 0.75
    MacroRiskAnalyzer.get_yield_curve = lambda self: 0.6

    entry_result = analyze_macro_risk({"vix": 15.8, "spx_price": 7580,
                                        "spx_50ma": 7058, "spx_200ma": 6831})
    check("analyze_macro_risk() with the same patched inputs matches the YELLOW fixture result",
          entry_result["risk_level"] == "YELLOW" and entry_result["stage"] == 1
          and abs(entry_result["crash_probability"]["prob_30d"] - 29.25) < 1e-9,
          f"got {entry_result['risk_level']} / stage={entry_result['stage']} "
          f"/ prob_30d={entry_result['crash_probability']['prob_30d']}")
finally:
    for name, fn in _orig.items():
        setattr(MacroRiskAnalyzer, name, fn)


# ---------------------------------------------------------------------------
# FRED dependency -- real fetch_fred_data/get_hyoas/get_yield_curve code path,
# with ONLY requests.get monkeypatched (the actual network boundary). This is
# the "FRED API key is dead (HTTP 400)" known issue: fetch_fred_data was
# rewritten to hit the keyless public fredgraph.csv feed instead of the
# registered-key endpoint that returns HTTP 400. We exercise the real CSV
# parsing (skip header, walk back from latest, skip "." missing values) and
# the real fallback-on-failure defaults (380 for HYOAS, 0.6 for yield curve).
# ---------------------------------------------------------------------------
print("\nFRED dependency -- real parsing + fallback logic, only requests.get faked")


class _FakeResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


_real_requests_get = macro_risk_analyzer.requests.get

try:
    # Case 1: dead/broken endpoint (HTTP 400, matching the known FRED-key issue)
    # -> fetch_fred_data returns None -> get_hyoas/get_yield_curve fall back to
    # their documented defaults (380 bps, 0.6%) instead of crashing.
    macro_risk_analyzer.requests.get = lambda url, timeout=10: _FakeResponse(400, "")
    fred_analyzer = MacroRiskAnalyzer()
    check("HTTP 400 (dead key scenario) -> fetch_fred_data returns None",
          fred_analyzer.fetch_fred_data("BAMLH0A0HYM2") is None,
          f"got {fred_analyzer.fetch_fred_data('BAMLH0A0HYM2')}")
    check("HTTP 400 -> get_hyoas() falls back to documented default 380 (not a crash)",
          fred_analyzer.get_hyoas() == 380, f"got {fred_analyzer.get_hyoas()}")
    check("HTTP 400 -> get_yield_curve() falls back to documented default 0.6",
          fred_analyzer.get_yield_curve() == 0.6, f"got {fred_analyzer.get_yield_curve()}")

    # Case 2: a real-shaped fredgraph.csv response -- confirms the "walk back
    # from latest, skip '.' missing values" parsing logic, and the HYOAS
    # percent->bps (*100) conversion.
    csv_ok = "DATE,BAMLH0A0HYM2\n2026-01-01,2.70\n2026-01-02,.\n2026-01-03,3.25\n"
    macro_risk_analyzer.requests.get = lambda url, timeout=10: _FakeResponse(200, csv_ok)
    hyoas_raw = fred_analyzer.fetch_fred_data("BAMLH0A0HYM2")
    check("real CSV: latest non-missing value (3.25) is returned, not an earlier row",
          hyoas_raw == 3.25, f"got {hyoas_raw}")
    check("get_hyoas() converts percent to bps (3.25 * 100 = 325.0)",
          fred_analyzer.get_hyoas() == 325.0, f"got {fred_analyzer.get_hyoas()}")

    # Case 3: latest row IS missing ('.') -- must walk back further, not stop there.
    csv_latest_missing = "DATE,T10Y2Y\n2026-01-01,0.55\n2026-01-02,.\n"
    macro_risk_analyzer.requests.get = lambda url, timeout=10: _FakeResponse(200, csv_latest_missing)
    yc_raw = fred_analyzer.fetch_fred_data("T10Y2Y")
    check("real CSV with a missing latest value ('.') walks back to the prior real value (0.55)",
          yc_raw == 0.55, f"got {yc_raw}")
finally:
    macro_risk_analyzer.requests.get = _real_requests_get


print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
