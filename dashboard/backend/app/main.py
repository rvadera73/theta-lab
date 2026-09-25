import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel

from . import services
from . import ledger

app = FastAPI(title="theta-lab dashboards")

# Resolved from this file's own location, not the process's CWD -- the
# report engine this app wraps (services.py) expects to run with the repo
# ROOT as CWD (relative "data/..." paths throughout), which is a different
# directory than this package lives in.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


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


# ------------------------------------------------------ Action Tracker API --
# ONE consolidated, cross-market ledger (docs/DASHBOARD_PLAN.md Phase B) --
# replaces the separate per-dashboard action panels.

class StatusUpdate(BaseModel):
    status: str
    note: str = ""


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


# ---------------------------------------------------------------- US API --

@app.get("/api/us/account-status")
def us_account_status():
    return services.get_account_status()


@app.get("/api/us/pnl-trend")
def us_pnl_trend():
    return services.get_pnl_trend()


@app.get("/api/us/cash-margin-forecast")
def us_cash_margin_forecast():
    return services.get_cash_margin_forecast()


@app.get("/api/us/active-decisions")
def us_active_decisions():
    return services.get_active_decisions()


@app.get("/api/us/sector-heat", response_class=PlainTextResponse)
def us_sector_heat():
    return services.extract_markdown_section("daily", "## Section 6: POSITION HEAT MATRIX", "\n## Section 6.5")


@app.get("/api/us/risk-macro", response_class=PlainTextResponse)
def us_risk_macro():
    crash = services.extract_markdown_section("daily", "## Section 6.5: CRASH EARLY WARNING", "\n## Section 6.6")
    guardrails = services.extract_markdown_section("weekly", "## Section 8: RISK & GUARDRAILS", "\n## Section 9")
    return crash + "\n\n" + guardrails


@app.get("/api/us/quarterly-direction", response_class=PlainTextResponse)
def us_quarterly_direction():
    return services.get_quarterly_direction("us")


@app.get("/api/us/framework-status", response_class=PlainTextResponse)
def us_framework_status():
    """Admin-tier: automation/framework mechanics, not decision content."""
    return services.extract_markdown_section("weekly", "## Section 10: FRAMEWORK STATUS")


@app.get("/api/us/report/{report_type}", response_class=PlainTextResponse)
def us_report_text(report_type: str):
    try:
        return services.get_report_text(report_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/us/refresh")
def us_refresh():
    services.refresh_generator()
    return {"status": "refreshed"}


# ------------------------------------------------------------- India API --

@app.get("/api/india/report", response_class=PlainTextResponse)
def india_report():
    return services.get_india_report_text()


@app.get("/api/india/6month-check", response_class=PlainTextResponse)
def india_6month_check():
    return services.get_india_6month_check()


@app.get("/api/india/market-signals", response_class=PlainTextResponse)
def india_market_signals():
    return services.get_india_market_signals()


@app.get("/api/india/quarterly-direction", response_class=PlainTextResponse)
def india_quarterly_direction():
    return services.get_quarterly_direction("india")


@app.get("/api/india/plan")
def india_plan():
    plan = services.get_india_plan()
    return plan if plan is not None else {}


@app.post("/api/india/refresh")
def india_refresh():
    services.refresh_india_report()
    return {"status": "refreshed"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
