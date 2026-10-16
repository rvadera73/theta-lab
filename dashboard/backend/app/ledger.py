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
    optionally on a manual refresh -- mostly cheap (no live price/report
    calls), EXCEPT the US priority-actions source below, which reuses
    whatever report-engine instance is already warm in services.py's cache
    (fast on the common case, only slow -- a real ~90s live compute -- on a
    genuinely cold start with nothing cached yet).

    Deliberately does NOT sync the quarterly-direction docs' "Open Items /
    Not Yet Built" sections (removed 2026-09-25, was here in the first
    version of this ledger) -- checked their real content and every one of
    them ("No India crash-probability model exists", "No single-name
    concentration cap exists", ...) is a gap in the ANALYSIS SYSTEM itself,
    not a trading decision. Mixing "build a new risk model" in with "close
    this position" in the same tracker is what made the trader say this
    "doesn't look like actions at all" -- those belong in
    docs/DASHBOARD_PLAN.md's own phase backlog, not here.

    Also deliberately does NOT sync every WATCH/HOLD position from the
    Sector Heat table -- only the bottom-up CLOSE/TRIM/ENTER priority list
    (services.get_us_priority_actions(), itself already gated to a real,
    usually-small set: RED-heat-plus-low-conviction for close/trim, top-3
    HIGH-conviction GREEN-heat for enter). Trader's own stated worry
    2026-09-25: "hoping there are not 100 of trackable actions if
    portfolio is stable" -- syncing the full ~92-ticker table would
    guarantee exactly that; this list was 3 items out of 92 tickers on a
    normal day, verified live.
    """
    from . import services  # local import: avoids a circular import at module load
    from . import sequencer

    conn = _conn()
    try:
        # -- US: the one sequenced priority list (sequencer.py), replacing
        # the old separate priority_actions (conviction-gated, could miss a
        # bad TRADE on a high-conviction name entirely -- see position_heat's
        # own history below) AND position_heat sync blocks. Tier 0 = a gate
        # fired (earnings-risk, illiquid -- addresses "before anything else,"
        # not a score penalty); Tier 1 = existing positions needing
        # management, by real severity; Tier 2 = gate-clear new-entry
        # candidates, by score+IV Rank. See dashboard/backend/app/sequencer.py
        # and the plan this was built from for the full design.
        _TIER_CATEGORY = {0: "TIER0_GATE", 1: "TIER1_MANAGE", 2: "TIER2_ENTER"}
        seen_sequenced_ids: set[str] = set()
        for row in sequencer.build_priority_sequence():
            if row["tier_source"] == "position_heat":
                # row is now one (symbol, account) position group, not a
                # single leg -- real fix 2026-10-13: a deliberate multi-leg
                # "stagger" campaign (ZS's 3 legs, ANET's 8 legs across 2
                # accounts) was surfacing as N disconnected-looking alerts.
                # Keyed by (symbol, account) so the item is stable as legs
                # are added/removed from the same real position, instead of
                # a new id per leg.
                legs = row["legs"]
                item_id = f"us_seq_{_short_id(row['symbol'], row['account'], 'position')}"
                worst = legs[0]  # already sorted worst-color-first by services.get_position_heat()
                title = (
                    f"{worst['action']} {row['symbol']} ({len(legs)}-leg structure, {row['account']})"
                    if len(legs) > 1
                    else f"{worst['action']} {row['symbol']} {worst['type']} ${worst['strike']}"
                )
                score_note = (
                    f"score={row['score']} (rank {row['rank']}/{row['population_size']}) | "
                    f"conviction={row['conviction']} | iv_rank={row['iv_rank']} | "
                    if row.get("score") is not None else ""
                )
                leg_notes = []
                for lg in legs:
                    # Real fix 2026-10-16 (trader correction): a "naked" CALL
                    # that's actually strangle-paired (a cash-secured PUT sold
                    # alongside it on the same name/expiry) is an intentional,
                    # documented structure per Account A's own strategy
                    # ("naked calls are hedged by the short puts... premium on
                    # both sides widens the break-even range") -- NOT the same
                    # thing as an isolated naked call. Confirmed real case:
                    # META/ANET/CRWD's "naked" calls were all strangle legs,
                    # flagged identically to genuinely isolated ones (ZS, CRM,
                    # ADBE, etc.), losing exactly the context that changes how
                    # urgently it should read.
                    cov_note = ("naked (strangle-paired -- hedged by the put leg, not isolated)" if lg.get("covered") is False and lg.get("strangle")
                                else "naked" if lg.get("covered") is False
                                else f"partial ({lg.get('covered_contracts')}/{lg.get('total_contracts')})" if lg.get("covered_contracts")
                                else "cash-secured" if lg.get("type") == "PUT" else "")
                    stale_note = (
                        f" [{lg['data_source']} data as of {lg['data_as_of']}, {lg['days_stale']}d old]"
                        if lg.get("days_stale") is not None and lg["days_stale"] > 3 else ""
                    )
                    leg_notes.append(
                        f"{lg['color']} {lg['type']} ${lg['strike']} exp {lg['expiry']} ({lg['dte']}d) "
                        f"{lg['action']}: {lg['reason']} | {cov_note}{stale_note}"
                    )
                desc = f"{score_note}" + "  ||  ".join(leg_notes)
            else:  # composite_score, Tier 2 new-entry candidate
                item_id = f"us_seq_{_short_id(row['ticker'], 'entry')}"
                title = f"ENTER {row['ticker']}: score={row.get('score')} (rank {row.get('rank')}/{row.get('population_size')})"
                desc = (
                    f"yield={row.get('yield_pct')}% | conviction={row.get('conviction')} | "
                    f"iv_rank={row.get('iv_rank')} | sector={row.get('sector')}"
                )
            gate_note = f" -- GATE: {', '.join(row['gates_fired'])}" if row.get("gates_fired") else ""
            seen_sequenced_ids.add(item_id)
            _upsert_new_only(
                conn, item_id, "US", "sequenced",
                _TIER_CATEGORY.get(row["tier"], "TIER1_MANAGE"),
                title, desc + gate_note, "OPEN",
            )

        # Prune stale sequenced rows -- a row that's no longer produced by
        # build_priority_sequence() (position closed, gate cleared, or a
        # data-lineage fix like 2026-10-13's covered-call correction) must
        # not just sit here with its old description forever: _upsert_new_only
        # only ever inserts/refreshes rows it's handed, it never deletes, so
        # without this the Action Tracker would keep showing conditions that
        # no longer exist (confirmed real case: TWLO stayed flagged "naked"
        # after the loader fix made it genuinely covered, until this prune
        # was added).
        existing_sequenced = {
            r["id"] for r in conn.execute(
                "SELECT id FROM action_items WHERE source = 'sequenced'"
            ).fetchall()
        }
        stale_ids = existing_sequenced - seen_sequenced_ids
        if stale_ids:
            conn.executemany(
                "DELETE FROM action_items WHERE id = ?",
                [(i,) for i in stale_ids],
            )
            conn.executemany(
                "DELETE FROM action_item_events WHERE action_item_id = ?",
                [(i,) for i in stale_ids],
            )

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
