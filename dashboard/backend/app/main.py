import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from . import services

app = FastAPI(title="theta-lab dashboard")

# Resolved from this file's own location, not the process's CWD -- the
# report engine this app wraps (services.py) expects to run with the repo
# ROOT as CWD (relative "data/..." paths throughout), which is a different
# directory than this package lives in.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/account-status")
def account_status():
    return services.get_account_status()


@app.get("/api/ytd")
def ytd_summary():
    return services.get_ytd_summary()


@app.get("/api/monthly-by-account")
def monthly_by_account():
    return services.get_monthly_by_account()


@app.get("/api/active-decisions")
def active_decisions():
    return services.get_active_decisions()


@app.get("/api/india-plan")
def india_plan():
    plan = services.get_india_plan()
    return plan if plan is not None else {}


@app.post("/api/refresh")
def refresh():
    services.refresh_generator()
    return {"status": "refreshed"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
