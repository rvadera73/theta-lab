"""A real precomputed-result cache, so dashboard requests read instantly
instead of triggering UnifiedReportProduction's ~90s live yfinance/position
load synchronously on every cold hit. SQLite, not Postgres -- this is a
single local user with a single writer process (the background refresh job
below); Postgres buys concurrent-write safety and a second service to run/
monitor/back up that nothing here needs. Revisit only if this dashboard
grows real concurrent writers.

Reuses ledger.py's same SQLite file (one DB for the whole dashboard's
persisted state) rather than a second file to manage.
"""
import json
import sqlite3
from datetime import datetime, timezone

from .ledger import DB_PATH, _now  # same file, same "now" helper

_SCHEMA = """
CREATE TABLE IF NOT EXISTS computed_cache (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    computed_at TEXT NOT NULL
);
"""


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def set_cached(key: str, value) -> None:
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO computed_cache (key, value_json, computed_at) VALUES (?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, computed_at=excluded.computed_at",
            (key, json.dumps(value), _now()),
        )
        conn.commit()
    finally:
        conn.close()


def get_cached(key: str):
    """Returns (value, computed_at) or (None, None) if never computed."""
    conn = _conn()
    try:
        row = conn.execute("SELECT value_json, computed_at FROM computed_cache WHERE key = ?", (key,)).fetchone()
        if not row:
            return None, None
        return json.loads(row["value_json"]), row["computed_at"]
    finally:
        conn.close()


def age_seconds(computed_at: str) -> float:
    if not computed_at:
        return float("inf")
    dt = datetime.fromisoformat(computed_at)
    return (datetime.now(timezone.utc) - dt).total_seconds()


# Every US/India computation the dashboard serves, keyed for the refresh
# job below to iterate over. String values (report text) are wrapped in a
# dict since set_cached always JSON-encodes.
def _build_us_entries(services):
    return {
        "us_account_status": services.get_account_status(),
        "us_pnl_trend": services.get_pnl_trend(),
        "us_cash_margin_forecast": services.get_cash_margin_forecast(),
        "us_sector_heat": {"text": services.extract_markdown_section("daily", "## Section 6: POSITION HEAT MATRIX", "\n## Section 6.5")},
        "us_risk_macro": {"text": (
            services.extract_markdown_section("daily", "## Section 6.5: CRASH EARLY WARNING", "\n## Section 6.6")
            + "\n\n" + services.extract_markdown_section("weekly", "## Section 8: RISK & GUARDRAILS", "\n## Section 9")
        )},
        "us_framework_status": {"text": services.extract_markdown_section("weekly", "## Section 10: FRAMEWORK STATUS")},
    }


def _build_india_entries(services):
    return {
        "india_report": {"text": services.get_india_report_text(force_refresh=True)},
        "india_6month_check": {"text": services.get_india_6month_check()},
        "india_market_signals": {"text": services.get_india_market_signals()},
    }


def refresh_all():
    """The one function the scheduler (main.py) and the manual /api/refresh
    endpoints both call. Recomputes everything live ONCE, then writes it
    all to cache -- callers never block on this; they read whatever's
    already cached while this runs.
    """
    from . import services

    services.refresh_generator()  # forces a fresh UnifiedReportProduction (live prices)
    for key, value in _build_us_entries(services).items():
        set_cached(key, value)
    for key, value in _build_india_entries(services).items():
        set_cached(key, value)
    # Quarterly direction docs and active-decisions/india-plan are cheap
    # file reads already (no live computation) -- not cached, read live
    # every time (see services.py) so an edit to those files shows up
    # immediately without waiting for the next scheduled refresh.
