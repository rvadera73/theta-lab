"""
Characterization tests for dashboard/backend/app/ledger.py's sync_all() --
written BEFORE the Code Quality Gate refactor (file/function-size,
complexity, params) that splits sync_all()'s three real distinct sync
blocks (the "sequenced" US block built from sequencer.build_priority_sequence,
the US active_decisions.yaml block, and the India 6-month-plan block) plus
its stale-sequenced-row prune into named helpers. This file is the safety
net: every check here must pass against the CURRENT, unrefactored sync_all()
first, and must keep passing, unchanged, after the refactor -- that's the
proof the refactor preserved exact behavior.

Unlike tests/test_ledger_priority.py (which deliberately avoids calling the
real sync_all() because it hits live network/position data), this file DOES
call the real sync_all() -- but with services.get_active_decisions(),
services.get_india_plan(), sequencer.build_priority_sequence(), and
decision_engine.build_decision() all monkeypatched to synthetic, deterministic
fixtures. sync_all() does local imports ("from . import services", "from .
import sequencer", "from decision_engine import build_decision") INSIDE the
function body, executed fresh on every call -- so patching the attribute on
the already-imported module object before calling sync_all() is sufficient;
there is nothing to reload.

No pytest dependency -- run directly: python3 tests/test_ledger_sync_all.py
"""
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "dashboard" / "backend"
sys.path.insert(0, str(_BACKEND))
# Real mcp/analysis path -- services.py's own sys.path.insert uses a
# hardcoded CODE_ROOT = "/app" (the container path), which doesn't exist in
# a dev checkout, so sync_all()'s "from decision_engine import build_decision"
# would fail here without this (see test_decision_engine.py, same pattern).
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))

from app import ledger, services, sequencer  # noqa: E402
import decision_engine  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def _fresh_db():
    tmp_dir = tempfile.mkdtemp(prefix="theta_lab_test_ledger_sync_all_")
    return tmp_dir, os.path.join(tmp_dir, "test_dashboard_actions.db")


def _cleanup_db(tmp_dir, tmp_db_path):
    try:
        os.remove(tmp_db_path)
    except OSError:
        pass
    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass


def _all_rows(ids_only=False):
    conn = ledger._conn()
    try:
        rows = [dict(r) for r in conn.execute("SELECT * FROM action_items").fetchall()]
        return [r["id"] for r in rows] if ids_only else rows
    finally:
        conn.close()


def _events_for(item_id):
    conn = ledger._conn()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM action_item_events WHERE action_item_id = ?", (item_id,)
        ).fetchall()]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Fixtures -- one position_heat row (single leg), one position_heat row
# (multi-leg "stagger", Tier 0 gate fired, unscored), one composite_score
# Tier 2 entry row, one composite_score row promoted to Tier 0 by a gate.
# ---------------------------------------------------------------------------
_LEG_ZS = {
    "color": "RED", "type": "PUT", "strike": 180, "expiry": "2026-12-19", "dte": 15,
    "action": "CLOSE_NOW", "reason": "deep ITM, hard stop",
    "covered": False, "covered_contracts": 0, "total_contracts": 1, "strangle": False,
    "data_source": "yahoo", "data_as_of": "2026-11-09", "days_stale": 1,
}
_LEG_ANET_1 = {
    "color": "RED", "type": "CALL", "strike": 200, "expiry": "2026-11-20", "dte": 10,
    "action": "ROLL_CALL", "reason": "earnings risk window",
    "covered": False, "covered_contracts": 0, "total_contracts": 1, "strangle": True,
    "data_source": "yahoo", "data_as_of": "2026-11-09", "days_stale": 1,
}
_LEG_ANET_2 = {
    "color": "YELLOW", "type": "PUT", "strike": 190, "expiry": "2026-12-19", "dte": 40,
    "action": "WATCH_CLOSE", "reason": "approaching strike",
    "covered": None, "covered_contracts": 0, "total_contracts": 1, "strangle": True,
    "data_source": "yahoo", "data_as_of": "2026-11-09", "days_stale": 1,
}
ROW_ZS = {
    "tier_source": "position_heat", "symbol": "ZS", "account": "AccountA",
    "legs": [_LEG_ZS],
    "score": 55, "rank": 3, "population_size": 50, "conviction": "HIGH", "iv_rank": 40,
    "gates_fired": [], "tier": 1, "rank_in_sequence": 1,
}
ROW_ANET = {
    "tier_source": "position_heat", "symbol": "ANET", "account": "AccountB",
    "legs": [_LEG_ANET_1, _LEG_ANET_2],
    "score": None, "rank": None, "population_size": None, "conviction": None, "iv_rank": None,
    "gates_fired": ["EARNINGS_RISK"], "tier": 0, "rank_in_sequence": 2,
}
ROW_NVDA = {
    "tier_source": "composite_score", "ticker": "NVDA", "score": 88, "rank": 1, "population_size": 50,
    "yield_pct": 2.1, "conviction": "HIGH", "iv_rank": 60, "sector": "Tech",
    "gates_fired": [], "tier": 2, "rank_in_sequence": 3,
}
ROW_TSLA = {
    "tier_source": "composite_score", "ticker": "TSLA", "score": 70, "rank": 2, "population_size": 50,
    "yield_pct": 1.5, "conviction": "MED", "iv_rank": 55, "sector": "Auto",
    "gates_fired": ["LIQUIDITY_GATE"], "tier": 0, "rank_in_sequence": 4,
}

DECISIONS = [
    {"id": "be_puts_reduction", "status": "OPEN", "account": "AccountA",
     "description": "Reduce BE put exposure to zero over the next ~10 days. Risk too high currently."},
    {"id": "close_risk_gate", "status": "BLOCKED", "account": "AccountB",
     "description": "Portfolio-level gate blocking all new entries pending review."},
    {"id": "old_resolved", "status": "RESOLVED", "account": "AccountA", "description": "Already resolved, historical."},
    {"id": "legacy_closed", "status": "CLOSED", "account": "AccountA", "description": "Closed out."},
    {"id": "no_account_item", "status": "OPEN", "description": "Needs an account default."},
    {"id": "no_description_item", "status": "OPEN", "account": "AccountC", "description": ""},
    {"id": "long_desc_item", "status": "OPEN", "account": "AccountA", "description": "X" * 2500},
]

INDIA_PLAN = {
    "fno_legs_to_close_month_1": [{"contract": "NIFTY24000CE", "pnl": 1200}],
    "equity_exits": {"RELIANCE": {"name": "Reliance Industries", "note": "Exit due to re-rating"}},
}


def _fake_build_decision(leg):
    # Only the ZS $180 PUT leg gets a non-trivial decision, so we can confirm
    # sync_all() actually threads build_decision()'s output into the row
    # description (assignment cash impact / margin / gates), not just that
    # it's called (test_ledger_priority.py already confirms the call exists
    # via static source inspection).
    if leg.get("strike") == 180:
        return SimpleNamespace(
            assignment_cash_impact=-18000.0,
            assignment_resulting_position="+100 ZS shares (put assigned)",
            est_margin_requirement=3600.0,
            gates_fired=["TEST_GATE"],
        )
    return SimpleNamespace(
        assignment_cash_impact=None, assignment_resulting_position=None,
        est_margin_requirement=None, gates_fired=[],
    )


class _patched:
    """Context manager: monkeypatches the exact functions sync_all() calls,
    restores them unconditionally. Each attribute is set only if given, so a
    scenario can patch a subset (e.g. just sequencer, leaving decisions/plan
    as empty defaults) without repeating all four every time."""

    def __init__(self, sequenced_rows=(), decisions=(), india_plan=None):
        self.sequenced_rows = list(sequenced_rows)
        self.decisions = list(decisions)
        self.india_plan = india_plan

    def __enter__(self):
        self._orig_bps = sequencer.build_priority_sequence
        self._orig_gad = services.get_active_decisions
        self._orig_gip = services.get_india_plan
        self._orig_bd = decision_engine.build_decision
        sequencer.build_priority_sequence = lambda: list(self.sequenced_rows)
        services.get_active_decisions = lambda: list(self.decisions)
        services.get_india_plan = lambda: self.india_plan
        decision_engine.build_decision = _fake_build_decision
        return self

    def __exit__(self, *exc):
        sequencer.build_priority_sequence = self._orig_bps
        services.get_active_decisions = self._orig_gad
        services.get_india_plan = self._orig_gip
        decision_engine.build_decision = self._orig_bd


_original_db_path = ledger.DB_PATH

# ---------------------------------------------------------------------------
# Scenario 1: a full sync_all() run across all three real blocks.
# ---------------------------------------------------------------------------
print("sync_all() -- full run across sequenced / active_decisions / india blocks")

tmp_dir, tmp_db = _fresh_db()
ledger.DB_PATH = tmp_db
try:
    with _patched(sequenced_rows=[ROW_ZS, ROW_ANET, ROW_NVDA, ROW_TSLA],
                  decisions=DECISIONS, india_plan=INDIA_PLAN):
        ledger.sync_all()

    rows = _all_rows()
    by_id = {r["id"]: r for r in rows}

    id_zs = f"us_seq_{ledger._short_id('ZS', 'AccountA', 'position')}"
    id_anet = f"us_seq_{ledger._short_id('ANET', 'AccountB', 'position')}"
    id_nvda = f"us_seq_{ledger._short_id('NVDA', 'entry')}"
    id_tsla = f"us_seq_{ledger._short_id('TSLA', 'entry')}"

    check("sync_all() produces exactly 11 action_items rows "
          "(4 sequenced + 5 open/blocked active_decisions [2 of 7 skipped] + 2 india)",
          len(rows) == 11, f"got {len(rows)}: {sorted(by_id)}")

    # -- sequenced block (position_heat-sourced + composite_score-sourced) --
    check("ZS single-leg position item exists with source='sequenced'",
          by_id.get(id_zs, {}).get("source") == "sequenced", f"got {by_id.get(id_zs)}")
    check("ZS item category is TIER1_MANAGE (tier=1)",
          by_id.get(id_zs, {}).get("category") == "TIER1_MANAGE", f"got {by_id.get(id_zs)}")
    check("ZS item priority == rank_in_sequence (1)",
          by_id.get(id_zs, {}).get("priority") == 1, f"got {by_id.get(id_zs)}")
    check("ZS item status is OPEN",
          by_id.get(id_zs, {}).get("status") == "OPEN", f"got {by_id.get(id_zs)}")
    check("ZS item description threads build_decision()'s assignment cash impact through",
          "-$18,000" in (by_id.get(id_zs, {}).get("description") or ""),
          f"got {by_id.get(id_zs, {}).get('description')}")
    check("ZS item description threads build_decision()'s est margin through",
          "$3,600" in (by_id.get(id_zs, {}).get("description") or ""),
          f"got {by_id.get(id_zs, {}).get('description')}")
    check("ZS item description threads build_decision()'s gates_fired through",
          "TEST_GATE" in (by_id.get(id_zs, {}).get("description") or ""),
          f"got {by_id.get(id_zs, {}).get('description')}")

    check("ANET multi-leg stagger position item exists, keyed by (symbol, account) not per-leg",
          id_anet in by_id, f"got ids={sorted(by_id)}")
    check("ANET item category is TIER0_GATE (tier=0, gate fired)",
          by_id.get(id_anet, {}).get("category") == "TIER0_GATE", f"got {by_id.get(id_anet)}")
    check("ANET item title reflects the 2-leg structure, not a single leg",
          "2-leg structure" in (by_id.get(id_anet, {}).get("title") or ""),
          f"got {by_id.get(id_anet, {}).get('title')}")
    check("ANET item description carries the row-level GATE note (EARNINGS_RISK)",
          "GATE: EARNINGS_RISK" in (by_id.get(id_anet, {}).get("description") or ""),
          f"got {by_id.get(id_anet, {}).get('description')}")

    check("NVDA Tier2 entry item exists with source='sequenced', category TIER2_ENTER",
          by_id.get(id_nvda, {}).get("source") == "sequenced"
          and by_id.get(id_nvda, {}).get("category") == "TIER2_ENTER",
          f"got {by_id.get(id_nvda)}")
    check("NVDA item title starts with 'ENTER NVDA'",
          (by_id.get(id_nvda, {}).get("title") or "").startswith("ENTER NVDA"),
          f"got {by_id.get(id_nvda, {}).get('title')}")

    check("TSLA composite_score entry promoted to Tier 0 by its own gate carries category TIER0_GATE",
          by_id.get(id_tsla, {}).get("category") == "TIER0_GATE", f"got {by_id.get(id_tsla)}")
    check("TSLA item description carries the row-level GATE note (LIQUIDITY_GATE)",
          "GATE: LIQUIDITY_GATE" in (by_id.get(id_tsla, {}).get("description") or ""),
          f"got {by_id.get(id_tsla, {}).get('description')}")

    # -- active_decisions block --
    check("RESOLVED decision ('old_resolved') is never synced in at all",
          "us_ad_old_resolved" not in by_id, f"got ids={sorted(by_id)}")
    check("CLOSED decision ('legacy_closed') is never synced in at all (only OPEN/BLOCKED sync)",
          "us_ad_legacy_closed" not in by_id, f"got ids={sorted(by_id)}")
    check("BLOCKED decision gets priority=0 (as urgent as a Tier 0 gate)",
          by_id.get("us_ad_close_risk_gate", {}).get("priority") == 0,
          f"got {by_id.get('us_ad_close_risk_gate')}")
    check("OPEN decision gets priority=5",
          by_id.get("us_ad_be_puts_reduction", {}).get("priority") == 5,
          f"got {by_id.get('us_ad_be_puts_reduction')}")
    check("decision title is the first sentence of its description, not the raw id",
          by_id.get("us_ad_be_puts_reduction", {}).get("title")
          == "Reduce BE put exposure to zero over the next ~10 days.",
          f"got {by_id.get('us_ad_be_puts_reduction', {}).get('title')}")
    check("decision with no 'account' key falls back to category 'General'",
          by_id.get("us_ad_no_account_item", {}).get("category") == "General",
          f"got {by_id.get('us_ad_no_account_item')}")
    check("decision with empty description falls back to its own id as the title",
          by_id.get("us_ad_no_description_item", {}).get("title") == "no_description_item",
          f"got {by_id.get('us_ad_no_description_item')}")
    check("decision description longer than 2000 chars is truncated to exactly 2000",
          len(by_id.get("us_ad_long_desc_item", {}).get("description") or "") == 2000,
          f"got length={len(by_id.get('us_ad_long_desc_item', {}).get('description') or '')}")

    # -- india block --
    id_fno = f"india_fno_{ledger._short_id('NIFTY24000CE')}"
    id_exit = f"india_exit_{ledger._short_id('RELIANCE')}"
    check("india F&O close item exists with source='india_6month_plan', category F&O, priority 100",
          by_id.get(id_fno, {}).get("source") == "india_6month_plan"
          and by_id.get(id_fno, {}).get("category") == "F&O"
          and by_id.get(id_fno, {}).get("priority") == 100,
          f"got {by_id.get(id_fno)}")
    check("india equity exit item title names the company and ticker",
          by_id.get(id_exit, {}).get("title") == "Exit Reliance Industries (RELIANCE)",
          f"got {by_id.get(id_exit, {}).get('title')}")

    # -- dedup: a second sync_all() run over the SAME fixtures must not
    # duplicate any row, and must preserve a dashboard-set status.
    conn = ledger._conn()
    conn.execute("UPDATE action_items SET status='RESOLVED' WHERE id=?", ("us_ad_be_puts_reduction",))
    conn.commit()
    conn.close()

    with _patched(sequenced_rows=[ROW_ZS, ROW_ANET, ROW_NVDA, ROW_TSLA],
                  decisions=DECISIONS, india_plan=INDIA_PLAN):
        ledger.sync_all()

    rows2 = _all_rows()
    check("re-running sync_all() with the same inputs does not duplicate any row (still 11)",
          len(rows2) == 11, f"got {len(rows2)}: {sorted(r['id'] for r in rows2)}")
    by_id2 = {r["id"]: r for r in rows2}
    check("a dashboard-set RESOLVED status on a re-synced active_decisions item survives re-sync",
          by_id2.get("us_ad_be_puts_reduction", {}).get("status") == "RESOLVED",
          f"got {by_id2.get('us_ad_be_puts_reduction')}")
    check("that same item's priority (a descriptive field, not a decision) is still refreshed on re-sync",
          by_id2.get("us_ad_be_puts_reduction", {}).get("priority") == 5,
          f"got {by_id2.get('us_ad_be_puts_reduction')}")

    events_zs = _events_for(id_zs)
    check("re-syncing an already-seen sequenced item does NOT add a second 'created' event",
          len(events_zs) == 1, f"got {len(events_zs)} events: {events_zs}")
finally:
    ledger.DB_PATH = _original_db_path
    _cleanup_db(tmp_dir, tmp_db)


# ---------------------------------------------------------------------------
# Scenario 2: stale sequenced rows are pruned (from BOTH tables) when a
# position/entry no longer appears in build_priority_sequence() -- the real
# fix for the "TWLO stayed flagged naked" bug cited in sync_all()'s own
# docstring. Active_decisions/india are untouched by this prune.
# ---------------------------------------------------------------------------
print("\nsync_all() -- stale sequenced-row pruning")

tmp_dir, tmp_db = _fresh_db()
ledger.DB_PATH = tmp_db
try:
    id_zs = f"us_seq_{ledger._short_id('ZS', 'AccountA', 'position')}"
    id_anet = f"us_seq_{ledger._short_id('ANET', 'AccountB', 'position')}"

    with _patched(sequenced_rows=[ROW_ZS, ROW_ANET]):
        ledger.sync_all()

    ids_after_first = set(_all_rows(ids_only=True))
    check("first sync produces both sequenced rows",
          {id_zs, id_anet} <= ids_after_first, f"got {ids_after_first}")

    with _patched(sequenced_rows=[ROW_ZS]):  # ANET's position closed / no longer sequenced
        ledger.sync_all()

    ids_after_second = set(_all_rows(ids_only=True))
    check("ZS (still produced) survives the second sync",
          id_zs in ids_after_second, f"got {ids_after_second}")
    check("ANET (no longer produced) is pruned from action_items, not left stale",
          id_anet not in ids_after_second, f"got {ids_after_second}")
    check("ANET's event-log rows are pruned too, not orphaned",
          _events_for(id_anet) == [], f"got {_events_for(id_anet)}")
    check("no active_decisions/india rows leaked in from this scenario's empty defaults",
          len(ids_after_second) == 1, f"got {ids_after_second}")
finally:
    ledger.DB_PATH = _original_db_path
    _cleanup_db(tmp_dir, tmp_db)


# ---------------------------------------------------------------------------
# Scenario 3: get_india_plan() returning None (e.g. missing/unparseable
# india_6month_plan.yaml) must not crash sync_all() -- `plan = services.
# get_india_plan() or {}` is the current code's guard; confirm it actually
# holds end-to-end, not just by reading the line.
# ---------------------------------------------------------------------------
print("\nsync_all() -- get_india_plan() returning None doesn't crash the run")

tmp_dir, tmp_db = _fresh_db()
ledger.DB_PATH = tmp_db
try:
    exc = None
    try:
        with _patched(india_plan=None):  # sequenced_rows/decisions default to empty
            ledger.sync_all()
    except Exception as e:  # noqa: BLE001 -- we want to see ANY crash here
        exc = e
    check("sync_all() does not raise when get_india_plan() returns None",
          exc is None, f"raised: {exc!r}")
    check("an all-empty sync (no sequenced/decisions/india) produces zero rows, not an error state",
          _all_rows() == [], f"got {_all_rows()}")
finally:
    ledger.DB_PATH = _original_db_path
    _cleanup_db(tmp_dir, tmp_db)


print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
