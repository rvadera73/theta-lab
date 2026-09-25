"""The Action Tracker ledger -- ONE consolidated, cross-market action list
(docs/DASHBOARD_PLAN.md Phase B), replacing per-dashboard action panels
that just duplicated (and could disagree with) each other.

Source-of-truth stays with the existing files (active_decisions.yaml, the
quarterly portfolio-direction docs, india_6month_plan.yaml) -- sync_all()
reads them and upserts into SQLite, but a NEW item's status is only ever
set by sync on first sight; once a row exists here, only an explicit
dashboard action (set_status) changes its status, so marking something
resolved in the dashboard survives the next sync instead of being
silently overwritten. Every status change is appended to an event log
(action_item_events), fixing the actual original gap: active_decisions.yaml
only ever showed CURRENT status, never how it got there.
"""
import os
import re
import sqlite3
import hashlib
from datetime import datetime, timezone

from .services import DATA_ROOT  # same constant services.py already defines -- one source of truth

DB_PATH = os.path.join(DATA_ROOT, "data", "dashboard_actions.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS action_items (
    id TEXT PRIMARY KEY,
    market TEXT NOT NULL,
    source TEXT NOT NULL,
    category TEXT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS action_item_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_item_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    detail TEXT
);
"""


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def _now():
    return datetime.now(timezone.utc).isoformat()


def _short_id(*parts) -> str:
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _upsert_new_only(conn, item_id, market, source, category, title, description, status):
    """Inserts a new item if it doesn't exist yet. Deliberately does NOT
    update an existing row's status/title on re-sync -- see module
    docstring: this ledger, not the source file, owns status once an item
    has been seen once, so a dashboard resolution isn't clobbered by the
    next sync. (title/description/category ARE refreshed, since those are
    just descriptive text, not a decision the dashboard makes.)
    """
    existing = conn.execute("SELECT id FROM action_items WHERE id = ?", (item_id,)).fetchone()
    now = _now()
    if existing:
        conn.execute(
            "UPDATE action_items SET category=?, title=?, description=?, updated_at=? WHERE id=?",
            (category, title, description, now, item_id),
        )
    else:
        conn.execute(
            "INSERT INTO action_items (id, market, source, category, title, description, status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (item_id, market, source, category, title, description, status, now, now),
        )
        conn.execute(
            "INSERT INTO action_item_events (action_item_id, event_type, timestamp, detail) VALUES (?,?,?,?)",
            (item_id, "created", now, f"synced from {source}"),
        )


def _parse_open_items_bullets(markdown_text: str) -> list[str]:
    """Pulls top-level '- ' bullets out of an 'Open Items' style markdown
    section (both quarterly docs use this exact shape -- see
    quarterly_portfolio_direction_{us,india}_2026-Q3.md's final section).
    """
    bullets = []
    current = None
    for line in markdown_text.split("\n"):
        if line.startswith("- "):
            if current:
                bullets.append(current.strip())
            current = line[2:]
        elif current is not None and line.startswith("  "):
            current += " " + line.strip()
        elif line.strip() == "" and current is not None:
            continue
        elif current is not None and not line.startswith("  "):
            bullets.append(current.strip())
            current = None
    if current:
        bullets.append(current.strip())
    return bullets


def _title_from_description(description: str, fallback: str, max_len: int = 150) -> str:
    """A real, human title instead of a raw snake_case id -- active_decisions
    .yaml's own description already opens with a clear imperative sentence
    (e.g. "Reduce BE put exposure to zero over the next ~10 days...") that
    is a far better title than the id it's filed under (e.g.
    "be_puts_reduction"). Takes everything up to the first sentence-ending
    period; falls back to the id only if there's truly no description.
    """
    description = (description or "").strip()
    if not description:
        return fallback
    first_sentence = description.split(". ")[0].split(".\n")[0]
    if len(first_sentence) > max_len:
        first_sentence = first_sentence[:max_len].rsplit(" ", 1)[0] + "..."
    return first_sentence.rstrip(".") + "." if not first_sentence.endswith(("...", ".")) else first_sentence


def sync_all():
    """Pulls every market's real open-item sources into the ledger. Call
    this before list_action_items() so a first-ever run isn't empty, and
    optionally on a manual refresh -- cheap (no live price/report calls),
    unlike the report-engine refresh endpoints.

    Deliberately does NOT sync the quarterly-direction docs' "Open Items /
    Not Yet Built" sections (removed 2026-09-25, was here in the first
    version of this ledger) -- checked their real content and every one of
    them ("No India crash-probability model exists", "No single-name
    concentration cap exists", ...) is a gap in the ANALYSIS SYSTEM itself,
    not a trading decision. Mixing "build a new risk model" in with "close
    this position" in the same tracker is what made the trader say this
    "doesn't look like actions at all" -- those belong in
    docs/DASHBOARD_PLAN.md's own phase backlog, not here.
    """
    from . import services  # local import: avoids a circular import at module load

    conn = _conn()
    try:
        # -- US: active_decisions.yaml (only OPEN/BLOCKED items -- resolved
        # ones are historical, not something to re-track as an open action).
        for d in services.get_active_decisions():
            status = (d.get("status") or "").upper()
            if status not in ("OPEN", "BLOCKED"):
                continue
            item_id = f"us_ad_{d.get('id')}"
            desc = (d.get("description") or "").strip()
            title = _title_from_description(desc, d.get("id"))
            _upsert_new_only(
                conn, item_id, "US", "active_decisions",
                d.get("account") or "General",
                title, desc[:2000], status,
            )

        # -- India: 6-month plan's F&O legs flagged for closing + equity exits
        plan = services.get_india_plan() or {}
        for leg in plan.get("fno_legs_to_close_month_1", []):
            contract = leg.get("contract", "unknown")
            item_id = f"india_fno_{_short_id(contract)}"
            title = f"Close {contract}"
            desc = f"Planned close, P&L if closed as planned: {leg.get('pnl')}"
            _upsert_new_only(conn, item_id, "India", "india_6month_plan", "F&O", title, desc, "OPEN")
        for symbol, exit_info in (plan.get("equity_exits") or {}).items():
            item_id = f"india_exit_{_short_id(symbol)}"
            title = f"Exit {exit_info.get('name', symbol)} ({symbol})"
            _upsert_new_only(conn, item_id, "India", "india_6month_plan", "Equity", title, exit_info.get("note", ""), "OPEN")

        conn.commit()
    finally:
        conn.close()


def create_manual_item(market: str, category: str, title: str, description: str = "") -> str:
    """Backs the dashboard's "Track as action" buttons -- turns a flagged
    table row (a DTE bucket over target, an expiry-date over the cliff
    ceiling, a sector at HIGH MACRO EXPOSURE, ...) into a real tracked
    item instead of leaving it as an observation the trader has to
    remember. This is the direct fix for the recurring "I see mostly
    observations, not actions" feedback from earlier in this project.
    Idempotent on (market, source='manual', title): re-clicking the same
    row's button doesn't create a duplicate, it just returns the existing
    item's id.
    """
    item_id = f"manual_{_short_id(market, title)}"
    conn = _conn()
    try:
        _upsert_new_only(conn, item_id, market, "manual", category, title, description, "OPEN")
        conn.commit()
        return item_id
    finally:
        conn.close()


def list_action_items(market: str = None):
    conn = _conn()
    try:
        if market and market.lower() != "all":
            rows = conn.execute(
                "SELECT * FROM action_items WHERE market = ? ORDER BY status, updated_at DESC", (market,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM action_items ORDER BY market, status, updated_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_item_history(item_id: str):
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT * FROM action_item_events WHERE action_item_id = ? ORDER BY timestamp", (item_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_status(item_id: str, new_status: str, note: str = ""):
    valid = {"OPEN", "BLOCKED", "RESOLVED"}
    new_status = new_status.upper()
    if new_status not in valid:
        raise ValueError(f"status must be one of {valid}")
    conn = _conn()
    try:
        existing = conn.execute("SELECT status FROM action_items WHERE id = ?", (item_id,)).fetchone()
        if not existing:
            raise ValueError(f"unknown action item id: {item_id}")
        now = _now()
        conn.execute("UPDATE action_items SET status=?, updated_at=? WHERE id=?", (new_status, now, item_id))
        conn.execute(
            "INSERT INTO action_item_events (action_item_id, event_type, timestamp, detail) VALUES (?,?,?,?)",
            (item_id, "status_change", now, f"{existing['status']} -> {new_status}" + (f": {note}" if note else "")),
        )
        conn.commit()
    finally:
        conn.close()
