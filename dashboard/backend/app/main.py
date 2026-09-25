import os
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel

from . import services
from . import ledger
from . import cache
from . import watchlist
from . import file_watcher
from . import quarterly_review_check

# Resolved from this file's own location, not the process's CWD -- the
# report engine this app wraps (services.py) expects to run with the repo
# ROOT as CWD (relative "data/..." paths throughout), which is a different
# directory than this package lives in.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

_scheduler = BackgroundScheduler()


def _initial_and_periodic_refresh():
    # Background thread, not the request/event loop -- refresh_all() does
    # ~90s of live yfinance/position-file work (see cache.py). Requests
    # made before this first completes fall back to a live compute via
    # _get_or_compute() below; every request after this either uses this
    # or a later scheduled run.
    cache.refresh_all()


app = FastAPI(title="theta-lab dashboards")


@app.on_event("startup")
def _on_startup():
    threading.Thread(target=_initial_and_periodic_refresh, daemon=True).start()
    # Every 30 minutes -- proportionate to how often live prices/positions
    # actually change for a personal, non-HFT options book; not tied to
    # market hours yet (a further refinement, which also needs India's very
    # different trading hours).
    _scheduler.add_job(cache.refresh_all, "interval", minutes=30, id="refresh_all", max_instances=1)
    # Every 2 minutes -- Phase E, built 2026-09-25: checks data/positions/
    # and data/statements/ for new files and triggers an immediate refresh
    # (rather than waiting for the interval above) the moment one lands,
    # plus the Quarterly Direction staleness/drift flag. Cheap on the
    # common case (just an mtime scan) -- see file_watcher.py for why
    # polling, not inotify/watchdog, in this real WSL/Docker environment.
    _scheduler.add_job(file_watcher.check_for_new_files_and_refresh, "interval", minutes=2,
                        id="file_watch", max_instances=1)
    _scheduler.start()
    threading.Thread(target=quarterly_review_check.check_and_flag_if_due, daemon=True).start()


@app.on_event("shutdown")
def _on_shutdown():
    _scheduler.shutdown(wait=False)


def _get_or_compute(key: str, compute_fn):
    """Reads a cached (value, age_seconds); if nothing has ever been
    computed for this key yet (very first request before the startup
    refresh finishes), computes it live once rather than showing an empty
    dashboard. Returns (value, computed_at_iso_or_None).
    """
    value, computed_at = cache.get_cached(key)
    if value is None:
        value = compute_fn()
        cache.set_cached(key, value)
        _, computed_at = cache.get_cached(key)
    return value, computed_at


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "landing.html"))


@app.get("/us")
def us_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "us.html"))


@app.get("/india")
def india_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "india.html"))


@app.get("/actions")
def actions_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "actions.html"))


@app.get("/watchlist")
def watchlist_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "watchlist.html"))


# ------------------------------------------------------ Action Tracker API --
# ONE consolidated, cross-market ledger (docs/DASHBOARD_PLAN.md Phase B) --
# replaces the separate per-dashboard action panels.

class StatusUpdate(BaseModel):
    status: str
    note: str = ""


class ManualItem(BaseModel):
    market: str
    category: str
    title: str
    description: str = ""


@app.post("/api/actions/track")
def actions_track(body: ManualItem):
    """Backs every dashboard "Track as action" button -- turns a flagged
    indicator row into a real ledger item. See ledger.create_manual_item.
    """
    item_id = ledger.create_manual_item(body.market, body.category, body.title, body.description)
    return {"id": item_id}


@app.get("/api/actions")
def actions_list(market: str = "all", sync: bool = True):
    if sync:
        ledger.sync_all()
    return ledger.list_action_items(market)


@app.post("/api/actions/sync")
def actions_sync():
    ledger.sync_all()
    return {"status": "synced"}


@app.post("/api/actions/{item_id}/status")
def actions_set_status(item_id: str, body: StatusUpdate):
    try:
        ledger.set_status(item_id, body.status, body.note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}


@app.get("/api/actions/{item_id}/history")
def actions_history(item_id: str):
    return ledger.get_item_history(item_id)


# --------------------------------------------------------------- Watchlist --
# Symbols NOT currently held, tracked persistently and analyzed through the
# SAME heat/conviction/IV-Rank/yield-on-capital pipeline held positions get
# -- the real gap flagged 2026-09-25: nothing upstream of this covered a
# candidate that wasn't already in open_positions.

class WatchlistAdd(BaseModel):
    symbol: str
    notes: str = ""


class WatchlistTrack(BaseModel):
    tracked: bool


@app.get("/api/watchlist")
def watchlist_list():
    return watchlist.list_watchlist()


@app.post("/api/watchlist")
def watchlist_add(body: WatchlistAdd):
    watchlist.add_symbol(body.symbol, body.notes)
    return {"status": "added"}


@app.post("/api/watchlist/{symbol}/tracked")
def watchlist_set_tracked(symbol: str, body: WatchlistTrack):
    watchlist.set_tracked(symbol, body.tracked)
    return {"status": "ok"}


@app.get("/api/watchlist/{symbol}/analysis")
def watchlist_analysis(symbol: str):
    """Live compute (not cached -- a deliberate "check this candidate"
    action, not a page-load-critical path). A handful of real yfinance
    calls, a few seconds, not the ~90s full report-engine refresh."""
    return services.analyze_watchlist_symbol(symbol)


# ---------------------------------------------------------------- US API --
# Every one of these now reads from cache.py's precomputed cache (populated
# by the startup + every-30-min background refresh above) instead of
# triggering a live ~90s computation per request -- the actual fix for
# "the dataset is taking too long."

@app.get("/api/us/account-status")
def us_account_status():
    value, computed_at = _get_or_compute("us_account_status", services.get_account_status)
    return {"data": value, "as_of": computed_at}


@app.get("/api/us/pnl-trend")
def us_pnl_trend():
    value, computed_at = _get_or_compute("us_pnl_trend", services.get_pnl_trend)
    return {"data": value, "as_of": computed_at}


@app.get("/api/us/cash-margin-forecast")
def us_cash_margin_forecast():
    value, computed_at = _get_or_compute("us_cash_margin_forecast", services.get_cash_margin_forecast)
    return {"data": value, "as_of": computed_at}


@app.get("/api/us/active-decisions")
def us_active_decisions():
    return services.get_active_decisions()


@app.get("/api/us/sector-heat")
def us_sector_heat():
    value, computed_at = _get_or_compute(
        "us_sector_heat",
        lambda: {"text": services.extract_markdown_section("daily", "## Section 6: POSITION HEAT MATRIX", "\n## Section 6.5")},
    )
    return {"text": value["text"], "as_of": computed_at}


@app.get("/api/us/risk-macro")
def us_risk_macro():
    def _compute():
        crash = services.extract_markdown_section("daily", "## Section 6.5: CRASH EARLY WARNING", "\n## Section 6.6")
        guardrails = services.extract_markdown_section("weekly", "## Section 8: RISK & GUARDRAILS", "\n## Section 9")
        return {"text": crash + "\n\n" + guardrails}
    value, computed_at = _get_or_compute("us_risk_macro", _compute)
    return {"text": value["text"], "as_of": computed_at}


@app.get("/api/us/quarterly-direction", response_class=PlainTextResponse)
def us_quarterly_direction():
    # Not cached: a cheap file read, and its OWN embedded "Generated/
    # Refreshed" date is the real staleness signal, not when this
    # container last touched the file -- see us.html's staleness parsing.
    return services.get_quarterly_direction("us")


@app.get("/api/us/framework-status")
def us_framework_status():
    """Admin-tier: automation/framework mechanics, not decision content."""
    value, computed_at = _get_or_compute(
        "us_framework_status",
        lambda: {"text": services.extract_markdown_section("weekly", "## Section 10: FRAMEWORK STATUS")},
    )
    return {"text": value["text"], "as_of": computed_at}


@app.get("/api/us/report/{report_type}", response_class=PlainTextResponse)
def us_report_text(report_type: str):
    try:
        return services.get_report_text(report_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/us/refresh")
def us_refresh():
    threading.Thread(target=cache.refresh_all, daemon=True).start()
    return {"status": "refreshing"}


# ------------------------------------------------------------- India API --

@app.get("/api/india/report")
def india_report():
    value, computed_at = _get_or_compute("india_report", lambda: {"text": services.get_india_report_text()})
    return {"text": value["text"], "as_of": computed_at}


@app.get("/api/india/6month-check")
def india_6month_check():
    value, computed_at = _get_or_compute("india_6month_check", lambda: {"text": services.get_india_6month_check()})
    return {"text": value["text"], "as_of": computed_at}


@app.get("/api/india/market-signals")
def india_market_signals():
    value, computed_at = _get_or_compute("india_market_signals", lambda: {"text": services.get_india_market_signals()})
    return {"text": value["text"], "as_of": computed_at}


@app.get("/api/india/quarterly-direction", response_class=PlainTextResponse)
def india_quarterly_direction():
    return services.get_quarterly_direction("india")


@app.get("/api/india/plan")
def india_plan():
    plan = services.get_india_plan()
    return plan if plan is not None else {}


@app.post("/api/india/refresh")
def india_refresh():
    threading.Thread(target=cache.refresh_all, daemon=True).start()
    return {"status": "refreshing"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
