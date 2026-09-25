"""A persistent watchlist for symbols NOT currently in the portfolio --
the real gap the trader flagged: sector/vertical/heat tracking only ever
covered held positions (everything upstream reads from
self.open_positions), so a candidate symbol under research had nowhere to
live and would need to be re-discovered from scratch every session.

Same SQLite file as ledger.py (one DB for the whole dashboard's persisted
state). A watchlist symbol is either `tracked` (actively analyzed
alongside held positions) or not (kept in the list, history preserved,
just excluded from the active analysis pass) -- toggled by the trader, not
auto-removed, so "stop tracking" never means "lose the record of why this
was once considered."
"""
import sqlite3
from datetime import datetime, timezone

from .ledger import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS watchlist (
    symbol TEXT PRIMARY KEY,
    tracked INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    added_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def _now():
    return datetime.now(timezone.utc).isoformat()


def add_symbol(symbol: str, notes: str = "") -> None:
    symbol = symbol.upper().strip()
    conn = _conn()
    try:
        now = _now()
        conn.execute(
            "INSERT INTO watchlist (symbol, tracked, notes, added_at, updated_at) VALUES (?, 1, ?, ?, ?) "
            "ON CONFLICT(symbol) DO UPDATE SET tracked=1, notes=excluded.notes, updated_at=excluded.updated_at",
            (symbol, notes, now, now),
        )
        conn.commit()
    finally:
        conn.close()


def set_tracked(symbol: str, tracked: bool) -> None:
    symbol = symbol.upper().strip()
    conn = _conn()
    try:
        conn.execute(
            "UPDATE watchlist SET tracked=?, updated_at=? WHERE symbol=?",
            (1 if tracked else 0, _now(), symbol),
        )
        conn.commit()
    finally:
        conn.close()


def list_watchlist(tracked_only: bool = False) -> list[dict]:
    conn = _conn()
    try:
        if tracked_only:
            rows = conn.execute("SELECT * FROM watchlist WHERE tracked = 1 ORDER BY symbol").fetchall()
        else:
            rows = conn.execute("SELECT * FROM watchlist ORDER BY tracked DESC, symbol").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
