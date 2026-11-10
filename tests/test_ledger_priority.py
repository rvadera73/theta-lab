"""
Regression tests for dashboard/backend/app/ledger.py's new `priority` column
(ADR 0001 step 10 wiring) -- the explicit sort key every source now writes
at sync time (lower = more urgent), replacing the old status-then-recency
ordering that gave a RED hard-stop and a routine watch item identical
visual priority.

Uses an ISOLATED temp SQLite file for the whole run (patches ledger.DB_PATH
directly -- ledger._conn()/'s. other functions all read the module-level
DB_PATH global at call time, so reassigning it is sufficient; unlike
account_state.py, nothing here imports DB_PATH BY NAME into a second
module's namespace) -- never the real production DB_PATH, restored in a
finally block regardless of outcome.

Deliberately does NOT call the real sync_all() -- it hits live network/
position data (8-account reload + Yahoo fetches) and has no place in a fast
regression suite. _upsert_new_only()/list_action_items() are tested
directly instead, and sync_all()'s wiring (decision_engine import +
rank_in_sequence as the sequenced-row priority source) is confirmed via a
static read of its own source -- an honest substitute for a full live
integration test, not a claim that it's equivalent to one.

No pytest dependency -- run directly: python3 tests/test_ledger_priority.py
"""
import inspect
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "dashboard" / "backend"
sys.path.insert(0, str(_BACKEND))

from app import ledger  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


_original_db_path = ledger.DB_PATH
_tmp_dir = tempfile.mkdtemp(prefix="theta_lab_test_ledger_priority_")
_tmp_db_path = os.path.join(_tmp_dir, "test_dashboard_actions.db")
ledger.DB_PATH = _tmp_db_path

try:
    print("priority column exists on a fresh DB")

    conn = ledger._conn()
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(action_items)")}
    check("a freshly-migrated DB's action_items table has a priority column",
          "priority" in cols, f"got columns={cols}")
    conn.close()

    print("\n_upsert_new_only(): priority is refreshed on re-sync, status is not")

    conn = ledger._conn()
    ledger._upsert_new_only(
        conn, "item_1", "US", "sequenced", "TIER1_MANAGE", "Title 1", "Desc 1", "OPEN", priority=5,
    )
    conn.commit()

    row1 = conn.execute("SELECT * FROM action_items WHERE id = ?", ("item_1",)).fetchone()
    check("first insert carries the given priority (5)",
          row1 is not None and row1["priority"] == 5, f"got {dict(row1) if row1 else None}")

    # Simulate the dashboard resolving this item -- set_status equivalent,
    # done directly here since set_status() isn't the thing under test.
    conn.execute("UPDATE action_items SET status = 'RESOLVED' WHERE id = ?", ("item_1",))
    conn.commit()

    # Re-sync with a different priority, same item_id -- same shape sync_all()
    # produces when the same sequenced item reappears with a new rank_in_sequence.
    ledger._upsert_new_only(
        conn, "item_1", "US", "sequenced", "TIER1_MANAGE", "Title 1", "Desc 1 updated", "OPEN", priority=2,
    )
    conn.commit()

    row2 = conn.execute("SELECT * FROM action_items WHERE id = ?", ("item_1",)).fetchone()
    check("re-syncing the same item_id with a NEW priority (2) actually updates it, not frozen at first-seen (5)",
          row2 is not None and row2["priority"] == 2, f"got {dict(row2) if row2 else None}")
    check("re-syncing does NOT clobber a status the dashboard already set (still RESOLVED, not reset to OPEN)",
          row2 is not None and row2["status"] == "RESOLVED", f"got {dict(row2) if row2 else None}")
    conn.close()

    print("\nlist_action_items(): RESOLVED sinks last; priority orders within each bucket")

    conn = ledger._conn()
    # item_1 is already RESOLVED with priority=2 from above.
    ledger._upsert_new_only(conn, "item_2", "US", "sequenced", "TIER0_GATE", "Title 2", "Desc 2", "OPEN", priority=0)
    ledger._upsert_new_only(conn, "item_3", "US", "sequenced", "TIER2_ENTER", "Title 3", "Desc 3", "OPEN", priority=100)
    ledger._upsert_new_only(conn, "item_4", "US", "manual", "General", "Title 4", "Desc 4", "OPEN", priority=1000)
    conn.commit()
    conn.close()

    items = ledger.list_action_items(market="US")
    ids_in_order = [i["id"] for i in items]

    check("item_1 (RESOLVED) sorts LAST despite its low priority (2), beating item_4's priority (1000)",
          ids_in_order[-1] == "item_1", f"got order={ids_in_order}")

    non_resolved_ids = [i["id"] for i in items if i["status"] != "RESOLVED"]
    non_resolved_priorities = [i["priority"] for i in items if i["status"] != "RESOLVED"]
    check("non-resolved rows are present and sorted by priority ascending (item_2=0, item_3=100, item_4=1000)",
          non_resolved_ids == ["item_2", "item_3", "item_4"],
          f"got order={non_resolved_ids}")
    check("priorities within the non-resolved bucket are strictly non-decreasing",
          non_resolved_priorities == sorted(non_resolved_priorities),
          f"got priorities={non_resolved_priorities}")

finally:
    ledger.DB_PATH = _original_db_path
    try:
        os.remove(_tmp_db_path)
    except OSError:
        pass
    try:
        os.rmdir(_tmp_dir)
    except OSError:
        pass

# ---------------------------------------------------------------------------
# sync_all() static source-inspection -- confirms the decision_engine wiring
# and rank_in_sequence-as-priority claim without running the real, live,
# network-dependent function. Honest limitation: this proves the source
# CONTAINS the expected call shape, not that it behaves correctly at
# runtime -- that behavioral claim is covered by decision_engine.py's own
# unit tests (tests/test_decision_engine.py) plus this file's direct
# _upsert_new_only()/list_action_items() checks above, AND (since the Bolt
# b15 Code Quality Gate refactor) by tests/test_ledger_sync_all.py's live,
# monkeypatched sync_all() runs, which assert the ACTUAL resulting row
# fields (priority == rank_in_sequence; a fake build_decision()'s output
# threaded into the description) end to end.
#
# Bolt b15 (2026-11) split sync_all() into named per-block helpers so the
# function itself stays within the Code Quality Gate's size/complexity
# limits; the rank_in_sequence-priority wiring now lives in
# _sync_sequenced_items(), and the per-leg build_decision(lg) call now lives
# in _leg_decision_note() (called via _build_leg_note()) -- sync_all() no
# longer contains either literal substring itself, so these two checks now
# inspect that combined source instead of sync_all()'s alone. This IS an
# edit to this file's assertions (not just sync_all()'s source), made
# because the refactor the Bolt was scoped to do genuinely requires it --
# a static substring check against the wrong function would either need to
# be weakened to meaninglessness or simply not find what it's looking for.
# ---------------------------------------------------------------------------
print("\nsync_all() source inspection (no live call -- see comment above)")

sync_all_source = inspect.getsource(ledger.sync_all)
sequenced_wiring_source = sync_all_source + inspect.getsource(ledger._sync_sequenced_items)
leg_decision_source = sync_all_source + inspect.getsource(ledger._leg_decision_note)
check("sync_all() imports build_decision from decision_engine",
      "from decision_engine import build_decision" in sync_all_source,
      "import line not found in sync_all() source")
check("sync_all()'s sequenced-sync wiring uses rank_in_sequence as the sequenced-row priority",
      'priority=row["rank_in_sequence"]' in sequenced_wiring_source,
      "rank_in_sequence priority wiring not found in sync_all()/_sync_sequenced_items() source")
check("sync_all()'s per-leg wiring calls build_decision(lg) to build a decision_note",
      "build_decision(lg)" in leg_decision_source,
      "build_decision(lg) call not found in sync_all()/_leg_decision_note() source")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
