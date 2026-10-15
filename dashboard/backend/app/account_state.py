"""Manually-updated real account state (cash, equity %, option requirement)
for Account A -- the one thing this system genuinely cannot compute itself.
Confirmed 2026-10-15: get_account_summary's own output says it outright --
"Live cash balance requires broker access -- file-based summary." Every
other number on this dashboard is computed from position files + Yahoo;
this one has no substitute, so it's captured here each time the trader
checks Schwab directly (same numbers that drove the 2026-10-15 GEV/MA/ULTA
margin-relief sequencing and the Dubai-withdrawal risk discussion), instead
of being silently absent from the one view (Today) that's supposed to give
a real answer to "what do I do right now."

Same SQLite file as ledger.py/watchlist.py -- one DB for the whole
dashboard's persisted state.
"""
import sqlite3
from datetime import datetime, timezone

from .ledger import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS account_state (
    account TEXT PRIMARY KEY,
    cash REAL,
    cash_plus_borrowing REAL,
    option_requirement REAL,
    balance_subject_to_interest REAL,
    equity_pct REAL,
    notes TEXT,
    updated_at TEXT NOT NULL
);
"""


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def set_state(account: str, **fields) -> None:
    """Upserts the trader-reported numbers for one account. Any field left
    out keeps its previous value -- a partial update (e.g. just cash) never
    blanks out the rest."""
    conn = _conn()
    try:
        existing = conn.execute("SELECT * FROM account_state WHERE account = ?", (account,)).fetchone()
        merged = dict(existing) if existing else {
            "account": account, "cash": None, "cash_plus_borrowing": None,
            "option_requirement": None, "balance_subject_to_interest": None,
            "equity_pct": None, "notes": None,
        }
        merged.update({k: v for k, v in fields.items() if v is not None})
        merged["updated_at"] = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO account_state (account, cash, cash_plus_borrowing, option_requirement, "
            "balance_subject_to_interest, equity_pct, notes, updated_at) VALUES (?,?,?,?,?,?,?,?) "
            "ON CONFLICT(account) DO UPDATE SET cash=excluded.cash, "
            "cash_plus_borrowing=excluded.cash_plus_borrowing, option_requirement=excluded.option_requirement, "
            "balance_subject_to_interest=excluded.balance_subject_to_interest, equity_pct=excluded.equity_pct, "
            "notes=excluded.notes, updated_at=excluded.updated_at",
            (account, merged["cash"], merged["cash_plus_borrowing"], merged["option_requirement"],
             merged["balance_subject_to_interest"], merged["equity_pct"], merged.get("notes"), merged["updated_at"]),
        )
        conn.commit()
    finally:
        conn.close()


def get_state(account: str) -> dict | None:
    conn = _conn()
    try:
        row = conn.execute("SELECT * FROM account_state WHERE account = ?", (account,)).fetchone()
        if not row:
            return None
        d = dict(row)
        updated = datetime.fromisoformat(d["updated_at"])
        d["days_stale"] = (datetime.now(timezone.utc) - updated).days
        return d
    finally:
        conn.close()
