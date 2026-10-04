"""Composite risk-adjusted score model for the quarterly rotation review
(docs: logs/portfolio_rotation_review_2026-Q4.md Section 6) -- promoted from
a one-off scratch script into real, reusable code so the dashboard can show
it live instead of it only existing in a dated report file.

v3 (2026-10-04) -- trader pushback on v2's design, twice:

1. "That's not a fair way to score, and I don't trust it's working" after
   ONDS (a cash-burning, dilution-risk micro-cap -- real research confirmed
   $35M operating loss on $7M revenue) topped the ENTIRE list purely on its
   58.4% yield, with zero quality penalty, since it simply wasn't in the
   static flag registry. v2's response (a sqrt dampening on yield, hand-
   picked constants like +3/-5/0.2-per-flag) was itself still built from
   unvalidated, arbitrarily-scaled numbers -- a trend bonus of +3 could
   swamp a quality penalty of 2 for reasons that had nothing to do with
   which mattered more, just which constant I happened to pick.

2. Direct request to still have SOME fair, usable ranking (not just a raw
   unranked scorecard that punts the comparison back to the trader) --
   "there has to be a fair way to score... otherwise how do I read them."

v3 answers both: keep a single composite score (genuinely useful at 90+
names), but build it the way real multi-factor quant models actually do
(see the Citadel/factor-investing research from 2026-10-04) -- normalize
each continuous factor to a z-score (standard deviations from the SCORED
POPULATION's own mean), not hand-picked additive constants on arbitrary,
mismatched scales. Every modifier below is calibrated to that same
z-score-like magnitude (roughly -2..+2) specifically so one factor can't
silently dominate just because of which raw constant it happened to get.

Formula, per ticker:
  - Tail-risk gate (binary, the ONLY thing that disqualifies): GOING_CONCERN,
    ACCOUNTING_RISK, DELISTING_RISK, PERMANENT_EXIT (config.RISK's own
    "binary_exit_flags" set, plus config.PERMANENT_EXITS, plus
    QUALITY_FLAGS_BY_SYMBOL) -- about capital destruction, not business
    quality. Tail-risk names are excluded from the scored/ranked population
    entirely, including from the mean/stdev each z-score is computed against.
  - risk_reward_z = 0.6 * zscore(yield_pct) + 0.4 * zscore(conviction).
    Yield is the market-priced richness of the premium; conviction is this
    book's own composite RSI/range/200-day-trend/analyst-rating score.
    These are two INDEPENDENTLY COMPUTED signals (one priced by the options
    market, one computed from technicals+fundamentals) that happen to
    correlate sometimes -- blending correlated-but-distinct factors this
    way is standard multi-factor practice, not double-counting.
  - valuation_penalty = 0.5 if the ticker's real analyst target_upside_pct
    (enhanced_metrics.py, Yahoo-sourced, free -- the closest obtainable
    proxy to a "fair value" signal without a paid Morningstar subscription)
    is below -15%, the EXACT SAME threshold enhanced_metrics.py already
    uses internally for "fundamentally_confirms_weakness". This is
    deliberately NOT a full z-scored factor on its own, because
    target_upside_pct is already a sub-component baked into conviction's
    own formula -- re-adding its raw number as an equal-weight factor would
    be true double-counting (the same number entering the blend twice).
    Using it only as a threshold flag at an already-meaningful level
    targets the real failure mode this was built for (rich yield masking a
    name analysts themselves think is overvalued/weakening) without
    re-weighting a number already inside conviction.
  - trend_bonus = +0.5 if trend_verticals.py tags this ticker to a real
    hot-trend vertical, else 0.
  - crash_penalty = -0.5 if this ticker's sector is a CONFIRMED (strong-
    confidence) high-crash-sensitivity sector AND the macro stage is
    YELLOW/RED -- gated on strong confidence so a weak/unconfirmed read
    never moves anything, matching the project's standing rule for that
    signal elsewhere.
  - quality_penalty = 0.2 * count of non-tail-risk QUALITY_FLAGS_BY_SYMBOL
    flags (LOW_MOAT/THIN_MARGINS/COMMODITY_PRICE_RISK/etc.) -- modifies
    score and a suggested sizing multiplier (floor 0.5x), never excludes,
    matching how the live screener already treats these flags.
  - outlier_penalty = max(0, yield_z - 2.0) * 1.0, but ONLY when the ticker
    also carries at least one quality flag -- added 2026-10-04 after ONDS
    STILL topped the list under the z-score redesign (yield_z=2.66, a
    genuine outlier, paired with conviction_z=1.64 driven by a real recent
    revenue beat/raised guidance -- not a bug, a real extreme case). A flat
    0.2-per-flag penalty is far too small to counter a >2-standard-deviation
    outlier. This targets the actual ONDS mechanism directly: an extreme
    yield outlier is sometimes real opportunity, sometimes the market
    pricing in real danger (cash burn, dilution risk, a going-concern-
    adjacent story) -- when a real quality flag is ALSO present, treat the
    extremity itself as corroborating evidence of risk, not just reward,
    and scale the penalty to how extreme it is rather than a flat constant.
    An outlier with NO flags at all is left alone -- this isn't a general
    "punish rich yield" rule, only "don't let an extreme outlier override
    a real, already-known risk flag."

Honest limitation, stated plainly rather than hidden: the +0.5/-0.5/0.2/1.0
modifier weights are still a judgment call, not backtested -- what changed
is that they're now scaled to be comparable in magnitude to the z-scored
primary signal, instead of arbitrary constants that could swamp each other
for no principled reason. The quality-flag registry is also still a
manually-curated list with real, proven coverage gaps (ONDS, and
separately BAC's dynamically-computed-but-not-statically-registered
LOW_MOAT) -- a blank "flags" column means "not yet checked," not
"confirmed clean."

Per-factor ranks (yield_rank, conviction_rank, overall rank) are computed
across the SAME scored population (held + watchlist together, excluding
tail-risk names) so a new candidate's standing against what's already held
is directly visible, not just its own standalone number.
"""
import statistics

from screener_universe import QUALITY_FLAGS_BY_SYMBOL
from config import PERMANENT_EXITS, RISK
from trend_verticals import get_verticals_for_ticker
from premium_yield import average_annualized_yield, get_cached_batch_yield
from enhanced_metrics import batch_get_metrics

TAIL_RISK_FLAGS = RISK.get("binary_exit_flags", {"ACCOUNTING_RISK", "DELISTING_RISK", "GOING_CONCERN", "PERMANENT_EXIT"})
OVERVALUATION_THRESHOLD = -15.0  # matches enhanced_metrics.py's own "fundamentally_confirms_weakness" bar
TREND_BONUS = 0.5
CRASH_PENALTY = 0.5
VALUATION_PENALTY = 0.5
QUALITY_PENALTY_PER_FLAG = 0.2
OUTLIER_Z_THRESHOLD = 2.0
OUTLIER_PENALTY_PER_SIGMA = 1.0


def _raw_row(ticker, yield_pct, conviction, target_upside_pct, verticals, sector,
             invested=None, heat=None, rsi=None, price=None, is_new=False):
    flags = set(QUALITY_FLAGS_BY_SYMBOL.get(ticker, []))
    tail_risk = bool(flags & TAIL_RISK_FLAGS) or ticker in PERMANENT_EXITS
    return {
        "ticker": ticker, "tail_risk": tail_risk,
        "flags": sorted(flags),
        "yield_pct": round(yield_pct, 1) if yield_pct is not None else None,
        "conviction": conviction,
        "target_upside_pct": target_upside_pct,
        "sector": sector, "verticals": verticals, "invested": invested,
        "heat": heat, "rsi": rsi, "price": price, "is_new": is_new,
    }


def _zscore(value, mean, stdev):
    if not stdev:
        return 0.0
    return (value - mean) / stdev


def _rank_by(rows, key):
    ranked = sorted((r for r in rows if r.get(key) is not None), key=lambda r: -r[key])
    return {r["ticker"]: i + 1 for i, r in enumerate(ranked)}


def score_population(raw_rows: list[dict], high_exposure_sectors, sensitivity_confidence, macro_stage) -> list[dict]:
    """Scores a combined population of raw rows (held + watchlist together,
    so a new candidate is ranked on the exact same scale as what's already
    held, not a separate standalone number) via z-score normalization.
    Mutates and returns raw_rows with score + rank fields added; tail-risk
    rows are left as-is (excluded from the population the z-scores and
    ranks are computed against)."""
    scoreable = [r for r in raw_rows if not r["tail_risk"] and r["yield_pct"] is not None and r["conviction"] is not None]

    yields = [r["yield_pct"] for r in scoreable]
    convictions = [r["conviction"] for r in scoreable]
    yield_mean, yield_std = (statistics.mean(yields), statistics.pstdev(yields)) if yields else (0.0, 0.0)
    conv_mean, conv_std = (statistics.mean(convictions), statistics.pstdev(convictions)) if convictions else (0.0, 0.0)

    for r in scoreable:
        yz = _zscore(r["yield_pct"], yield_mean, yield_std)
        cz = _zscore(r["conviction"], conv_mean, conv_std)
        risk_reward_z = 0.6 * yz + 0.4 * cz

        non_tail_flags = [f for f in r["flags"] if f not in TAIL_RISK_FLAGS]
        quality_penalty = QUALITY_PENALTY_PER_FLAG * len(non_tail_flags)
        trend_bonus = TREND_BONUS if r["verticals"] else 0.0
        crash_penalty = CRASH_PENALTY if (
            r["sector"] in high_exposure_sectors and sensitivity_confidence == "strong" and macro_stage in ("YELLOW", "RED")
        ) else 0.0
        valuation_penalty = VALUATION_PENALTY if (
            r["target_upside_pct"] is not None and r["target_upside_pct"] < OVERVALUATION_THRESHOLD
        ) else 0.0
        outlier_penalty = (
            max(0.0, yz - OUTLIER_Z_THRESHOLD) * OUTLIER_PENALTY_PER_SIGMA if non_tail_flags else 0.0
        )

        score = risk_reward_z + trend_bonus - quality_penalty - crash_penalty - valuation_penalty - outlier_penalty
        r.update({
            "yield_z": round(yz, 2), "conviction_z": round(cz, 2), "risk_reward_z": round(risk_reward_z, 2),
            "trend_bonus": trend_bonus, "quality_penalty": round(quality_penalty, 2),
            "crash_penalty": crash_penalty, "valuation_penalty": valuation_penalty,
            "outlier_penalty": round(outlier_penalty, 2),
            "flags": non_tail_flags, "score": round(score, 3),
        })

    yield_rank = _rank_by(scoreable, "yield_pct")
    conviction_rank = _rank_by(scoreable, "conviction")
    overall_rank = _rank_by(scoreable, "score")
    for r in scoreable:
        r["yield_rank"] = yield_rank.get(r["ticker"])
        r["conviction_rank"] = conviction_rank.get(r["ticker"])
        r["rank"] = overall_rank.get(r["ticker"])
        r["population_size"] = len(scoreable)

    return raw_rows


def gather_held_rows(gen) -> list[dict]:
    """Raw (unscored) rows for every currently-held ticker on gen (a warm
    UnifiedReportProduction instance -- caller must have already run
    get_priority_actions() or generate_daily_report())."""
    held_tickers = set(gen.position_summary.index)
    put_call_breakdown = gen._parse_put_call_breakdown()
    rows = []
    for ticker in held_tickers:
        m = gen.metrics.get(ticker, {})
        conviction = m.get("conviction")
        yield_data = gen.premium_yields.get(ticker)
        yield_pct = average_annualized_yield(yield_data) if yield_data else None
        if conviction is None or yield_pct is None:
            continue
        bd = put_call_breakdown.get(ticker, {})
        invested = round(bd.get("put_notional", 0) + bd.get("call_notional", 0), 2)
        rows.append(_raw_row(
            ticker, yield_pct, conviction, m.get("target_upside_pct"),
            get_verticals_for_ticker(ticker), gen.ticker_sector_map.get(ticker, "Other"),
            invested=invested, heat=m.get("heat_status"), rsi=m.get("rsi"), is_new=False,
        ))
    return rows


def gather_watchlist_rows(tickers: list[str], sector_hints: dict | None = None) -> tuple[list[dict], list[dict]]:
    """Raw (unscored) rows for every NOT-currently-held ticker (e.g.
    Watchlist entries), batched through the SAME cached/paced wrappers held
    tickers use (premium_yield.get_cached_batch_yield,
    enhanced_metrics.batch_get_metrics) instead of calling the raw
    per-ticker functions in a loop -- confirmed live 2026-10-04 that calling
    the raw single-ticker functions directly, right after the dashboard's
    own ~90-ticker held-name refresh, hit Yahoo's rate limit on every single
    one. Returns (rows, errors) -- errors are tickers with no live
    price/yield data (e.g. an ADR Yahoo can't quote)."""
    sector_hints = sector_hints or {}
    tickers = [t.upper().strip() for t in tickers]

    yields = get_cached_batch_yield(tickers)
    priced = {t: yields[t]["price"] for t in tickers if yields.get(t) and yields[t].get("price")}
    metrics = batch_get_metrics(list(priced.keys()), priced) if priced else {}

    rows, errors = [], []
    for ticker in tickers:
        yield_data = yields.get(ticker)
        price = yield_data.get("price") if yield_data else None
        if not price:
            errors.append({"ticker": ticker, "error": (yield_data or {}).get("error", "no_price_data")})
            continue
        yield_pct = average_annualized_yield(yield_data)
        m = metrics.get(ticker, {})
        conviction = m.get("conviction")
        if yield_pct is None or conviction is None:
            errors.append({"ticker": ticker, "error": "no_yield_or_conviction"})
            continue
        rows.append(_raw_row(
            ticker, yield_pct, conviction, m.get("target_upside_pct"),
            get_verticals_for_ticker(ticker), sector_hints.get(ticker, "Other"),
            heat=m.get("heat_status"), rsi=m.get("rsi"), price=price, is_new=True,
        ))
    return rows, errors


def compute_composite_scores(gen, watchlist_tickers: list[str] | None = None, watchlist_sector_hints: dict | None = None) -> dict:
    """Full pipeline: gathers held + watchlist raw rows, scores the combined
    population together (so ranks and z-scores reflect genuine standing
    against everything else, held or not), and returns the global
    regime/macro-stage context alongside the scored results."""
    risk_analysis = gen._get_macro_risk_analysis()
    from analysis.regime import detect_regime
    regime_data = detect_regime()
    sensitivity = risk_analysis.get("sector_sensitivity") or {}
    high_exposure_sectors = set(sensitivity.get("high_sensitivity_sectors", []))
    sensitivity_confidence = sensitivity.get("confidence", "unconfirmed")
    macro_stage = risk_analysis.get("risk_level")

    held_rows = gather_held_rows(gen)
    watchlist_rows, watchlist_errors = gather_watchlist_rows(watchlist_tickers or [], watchlist_sector_hints)

    all_rows = score_population(held_rows + watchlist_rows, high_exposure_sectors, sensitivity_confidence, macro_stage)

    return {
        "held": [r for r in all_rows if not r["is_new"]],
        "watchlist": [r for r in all_rows if r["is_new"]] + [
            {"ticker": e["ticker"], "tail_risk": None, "error": e["error"]} for e in watchlist_errors
        ],
        "regime": regime_data.get("regime"),
        "macro_stage": macro_stage,
        "severity_smoothed": risk_analysis.get("severity_smoothed"),
        "high_exposure_sectors": sorted(high_exposure_sectors),
        "sensitivity_confidence": sensitivity_confidence,
    }
