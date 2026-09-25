"""Thin wrappers around the existing report engine (mcp/reports,
scripts/realized_pnl.py) and the raw YAML trackers. No report-generation
logic lives here -- every function below calls something that already
exists and just reshapes it into JSON for the dashboard. See
docs/DASHBOARD_PLAN.md (Phase 1: read-only dashboard).
"""
import sys
import os
import yaml


def _to_native(obj):
    """Recursively convert numpy/pandas scalar types to plain Python so
    FastAPI's JSON encoder doesn't choke on them -- _compute_account_status
    sums pandas columns internally and can hand back numpy.float64/int64.
    """
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    if hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    return obj

CODE_ROOT = "/app"
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp", "reports"))
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp", "analysis"))
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp"))
sys.path.insert(0, os.path.join(CODE_ROOT, "scripts"))

# The report engine (mcp/reports/*.py, scripts/open_positions_loader_v2.py)
# hardcodes this exact absolute host path for data/logs, not a CWD-relative
# one -- confirmed live 2026-09-25 ("No objects to concatenate" when data/
# was mounted at /app/data instead). docker-compose.yml mounts the real
# data/logs volumes here to match, so those modules work completely
# unmodified inside the container.
DATA_ROOT = "/home/rahulvadera/projects/theta-lab"

_report_generator = None


def _get_generator():
    # Cached at module scope, not per-request -- __init__ loads every
    # position file and fetches live prices for ~90 tickers (real network
    # calls), which is too slow to redo on every dashboard hit. A
    # dedicated "refresh" endpoint (Phase 1 stretch / Phase 4 scheduler)
    # invalidates this when fresher data is wanted.
    global _report_generator
    if _report_generator is None:
        from unified_master_report_production import UnifiedReportProduction
        _report_generator = UnifiedReportProduction()
    return _report_generator


def refresh_generator():
    global _report_generator
    _report_generator = None
    return _get_generator()


def get_account_status():
    gen = _get_generator()
    status = gen._compute_account_status()
    return _to_native([
        {"account": name, **dict(data.items())}
        for name, data in status.items()
    ])


def get_ytd_summary():
    from realized_pnl import get_realized_summary
    return get_realized_summary()


def get_monthly_by_account():
    from realized_pnl import get_realized_monthly_by_account
    return get_realized_monthly_by_account()


def _load_yaml(rel_path):
    path = os.path.join(DATA_ROOT, rel_path)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def get_active_decisions():
    data = _load_yaml("data/active_decisions.yaml") or {}
    return data.get("decisions", [])


def get_india_plan():
    return _load_yaml("data/india_6month_plan.yaml")


def _get_symbol_sector(ticker: str) -> str:
    """Same CUSTOM_SECTOR_MAP-then-Yahoo-fallback logic sector_analysis.py
    uses for held positions, reused directly for a watchlist symbol that
    isn't in any open_positions DataFrame yet."""
    from sector_analysis import SectorAnalyzer
    if ticker in SectorAnalyzer.CUSTOM_SECTOR_MAP:
        return SectorAnalyzer.CUSTOM_SECTOR_MAP[ticker]
    import yfinance as yf
    try:
        return yf.Ticker(ticker).info.get('sector', 'Unknown')
    except Exception:
        return 'Unknown'


def analyze_watchlist_symbol(ticker: str) -> dict:
    """The combined view the trader asked for: heat/conviction (the SAME
    enhanced_metrics.get_ticker_metrics real positions get -- no separate,
    lesser treatment for a candidate not yet held), sector + trend-vertical
    tags, IV Rank (richness relative to the stock's OWN history), and
    annualized yield-on-capital (opportunity cost vs. other candidates for
    the same capital) -- combined, per the trader's explicit direction,
    not treated as two separate, disconnected checks.
    """
    from enhanced_metrics import get_ticker_metrics
    from iv_rank import get_iv_rank
    from premium_yield import get_yield_on_capital
    from trend_verticals import get_verticals_for_ticker

    ticker = ticker.upper().strip()

    # Price first (from a cheap history call inside get_yield_on_capital's
    # own fetch, but get_ticker_metrics needs it passed in) -- reuse
    # premium_yield's own live fetch rather than a third separate call.
    yield_data = get_yield_on_capital(ticker)
    price = yield_data.get("price")
    if price is None:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="1d")
        price = float(hist["Close"].iloc[-1]) if len(hist) else None

    metrics = get_ticker_metrics(ticker, price, option_type=None) if price else {"error": "no_price"}
    iv = get_iv_rank(ticker)
    sector = _get_symbol_sector(ticker)
    verticals = get_verticals_for_ticker(ticker)

    return _to_native({
        "symbol": ticker,
        "price": price,
        "sector": sector,
        "verticals": verticals,
        "heat_status": metrics.get("heat_status"),
        "heat_reason": metrics.get("heat_reason"),
        "conviction": metrics.get("conviction"),
        "rsi": metrics.get("rsi"),
        "iv_rank": iv.get("iv_rank"),
        "iv_entry_signal": iv.get("entry_signal"),
        "yield_on_capital": yield_data,
    })


_REPORT_METHODS = {
    "daily": "generate_daily_report",
    "weekly": "generate_weekly_report",
    "biweekly": "generate_biweekly_report",
    "monthly": "generate_monthly_report",
}


def get_report_text(report_type: str) -> str:
    """The full report text generate_all_reports() writes to logs/*.md --
    used internally by extract_markdown_section() below, not surfaced raw
    to the dashboard any more (see docs/DASHBOARD_PLAN.md's "Rejected
    approaches" -- a raw-text dump per report type just moved the reports'
    own duplication into a dropdown instead of removing it).
    """
    method_name = _REPORT_METHODS.get(report_type)
    if not method_name:
        raise ValueError(f"Unknown report_type '{report_type}' (expected one of {list(_REPORT_METHODS)})")
    gen = _get_generator()
    return getattr(gen, method_name)()


def extract_section_from_text(text: str, start_marker: str, end_marker: str = None) -> str:
    """Pulls one section's markdown out of a full report by its own real
    heading text, rather than re-deriving that section's content with new
    logic. This is how Sector Heat / Risk & Macro / India's 6-Month Plan
    reach the dashboard as ONE deduplicated section (shown once) while
    still tracing back to the exact same computation the report engine
    already does -- no second, drifting implementation of that logic.

    start_marker: exact heading text to search for (e.g. "## Section 6:")
    -- matched as a substring so a caller doesn't need the full heading
    including its dynamic counts. end_marker: exact next-heading text; if
    omitted, cuts at the next line starting with "## " (a level-2 heading)
    after start_marker, or end of text if there isn't one.
    """
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return f"_Section not found: {start_marker}_"
    search_from = start_idx + len(start_marker)
    if end_marker:
        end_idx = text.find(end_marker, search_from)
    else:
        end_idx = text.find("\n## ", search_from)
    section = text[start_idx:end_idx] if end_idx != -1 else text[start_idx:]
    return section.strip()


def extract_markdown_section(report_type: str, start_marker: str, end_marker: str = None) -> str:
    """extract_section_from_text() over a US report_type's full text."""
    return extract_section_from_text(get_report_text(report_type), start_marker, end_marker)


def get_cash_margin_forecast():
    """Crash-scenario cash requirement + expiry-curve concentration for
    Account A (the only margin account) -- the SAME formulas
    unified_master_report_production.py's Section 6 already computes
    (18%-of-notional model, 15-20% stress range, near/core/mid/far DTE
    bands, single-date cliff check), reshaped as structured JSON instead
    of only being reachable as report text. Verified against the report's
    own live output 2026-09-25 (this and Section 6 must always agree,
    since they're the identical computation over the same live position
    data -- see docs/DASHBOARD_PLAN.md's "no rewrite" boundary).
    """
    import pandas as pd
    from datetime import date
    from accounts_config import ACCOUNTS_CONFIG

    gen = _get_generator()
    today = date.today()
    acct_a_name = "Account A (232)"

    opt = gen.open_positions[
        (gen.open_positions['account_name'] == acct_a_name) &
        (gen.open_positions['option_type'].isin(['C', 'P']))
    ].copy()
    opt['px'] = opt['ticker'].map(gen.prices).fillna(0)
    opt['notional'] = opt['px'] * opt['net_quantity'].abs() * 100
    opt['expiry_dt'] = pd.to_datetime(opt['expiry_date'], errors='coerce')
    opt['dte'] = (opt['expiry_dt'] - pd.Timestamp(today)).dt.days
    total_n = opt['notional'].sum()

    def bucket(dte):
        if pd.isna(dte):
            return 'unknown'
        if dte < 60:
            return 'near'
        if dte < 135:
            return 'core'
        if dte < 195:
            return 'mid'
        return 'far'

    opt['bucket'] = opt['dte'].apply(bucket)
    by_bucket = opt.groupby('bucket')['notional'].sum()
    targets = {'near': (10, 15), 'core': (35, 40), 'mid': (20, 24), 'far': (10, 15)}
    labels = {'near': 'Near (<60 DTE)', 'core': 'Core (60-135 DTE)', 'mid': 'Mid (135-195 DTE)', 'far': 'Far (195+ DTE)'}
    buckets = []
    for b in ['near', 'core', 'mid', 'far']:
        pct = (by_bucket.get(b, 0) / total_n * 100) if total_n else 0
        lo, hi = targets[b]
        status = "ok" if lo <= pct <= hi else ("light" if pct < lo else "heavy")
        buckets.append({"label": labels[b], "pct": round(pct, 1), "target_lo": lo, "target_hi": hi, "status": status})

    by_date = opt.groupby(opt['expiry_dt'].dt.date)['notional'].sum().sort_values(ascending=False)
    top_dates = []
    for d, n in by_date.head(5).items():
        pct = n / total_n * 100 if total_n else 0
        top_dates.append({
            "date": str(d), "notional": round(float(n), 2), "pct": round(pct, 1),
            "status": "over" if pct > 25 else ("edge" if pct > 20 else "ok"),
        })

    opt_req = gen.option_requirements.get(acct_a_name, 0)
    stress_low = total_n * 0.15 * 0.18
    stress_high = total_n * 0.20 * 0.18
    emergency_reserve = 200000
    operating_cash_target = 100000

    return _to_native({
        "as_of": today.isoformat(),
        "total_notional": total_n,
        "opt_req": opt_req,
        "stress_low": stress_low,
        "stress_high": stress_high,
        "operating_cash_target": operating_cash_target,
        "emergency_reserve": emergency_reserve,
        "reserve_covers_stress": emergency_reserve >= stress_high,
        "capacity": ACCOUNTS_CONFIG[acct_a_name].get('capacity'),
        "capacity_as_of": ACCOUNTS_CONFIG[acct_a_name].get('capacity_as_of'),
        "dte_buckets": buckets,
        "top_expiry_dates": top_dates,
    })


def get_pnl_trend():
    """MTD/YTD (from get_realized_summary, already period-computed) plus a
    QTD figure derived from the same monthly-by-account data
    get_realized_monthly_by_account() already returns -- no new premium
    computation, just a different rollup window over numbers that already
    exist.
    """
    from datetime import date
    from realized_pnl import get_realized_summary, get_realized_monthly_by_account

    summary = get_realized_summary()
    monthly = get_realized_monthly_by_account()
    today = date.today()
    quarter_start_month = ((today.month - 1) // 3) * 3 + 1
    qtd_months = {f"{today.year}-{m:02d}" for m in range(quarter_start_month, today.month + 1)}

    portfolio_qtd = 0.0
    per_account_qtd = {}
    for label, months in monthly.items():
        acct_qtd = sum(v for m, v in months.items() if m in qtd_months)
        per_account_qtd[label] = acct_qtd
        portfolio_qtd += acct_qtd

    return {
        **summary,
        "portfolio_qtd_realized": portfolio_qtd,
        "per_account_qtd": per_account_qtd,
    }


_india_report_cache = None


def get_india_report_text(force_refresh: bool = False) -> str:
    """The full India weekly report -- same treatment as the US
    get_report_text(): a real, existing generator function's output,
    cached (India's own report also does live yfinance/statement-parsing
    work) rather than re-run on every dashboard hit. Called with empty
    credentials, same as india_weekly_report.py's own __main__ demo --
    real behavior for this trader (statements-only, no live Breeze
    session token kept lying around), not a stub.
    """
    global _india_report_cache
    if _india_report_cache is None or force_refresh:
        import asyncio
        from india_weekly_report import generate_india_weekly_report
        _india_report_cache = asyncio.run(generate_india_weekly_report("", "", ""))
    return _india_report_cache


def refresh_india_report():
    return get_india_report_text(force_refresh=True)


def get_india_6month_check() -> str:
    """The '## 6-MONTH PLAN TRACKING' section, extracted from the real
    India report text (see extract_section_from_text) -- not
    re-implemented, since _check_6month_plan needs the same
    positions/regime_signals the full report generation already gathers.
    """
    return extract_section_from_text(get_india_report_text(), "## 6-MONTH PLAN TRACKING")


def get_india_market_signals() -> str:
    """The '## Market Signals' section (regime, India VIX, Nifty vs
    moving averages) -- same extraction approach as the 6-month check."""
    return extract_section_from_text(get_india_report_text(), "## Market Signals")


def get_quarterly_direction(market: str) -> str:
    """The hand-authored quarterly strategic doc -- NOT auto-regenerated
    like the 4 cadence reports (a real, periodic review, not a live
    computation), so this just reads the latest one on disk rather than
    calling a generator function. Picks the highest dated
    quarterly_portfolio_direction_{market}_*.md if more than one exists.
    """
    import glob
    pattern = os.path.join(DATA_ROOT, "logs", f"quarterly_portfolio_direction_{market}_*.md")
    matches = sorted(glob.glob(pattern))
    if not matches:
        return f"_No quarterly portfolio direction doc found for market '{market}'._"
    with open(matches[-1]) as f:
        return f.read()
