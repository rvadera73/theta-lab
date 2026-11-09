"""
Regression tests for dashboard/backend/app/account_state.py's new
`emergency_reserve` column (ADR 0001 steps 1-2 -- replaces the hardcoded
$200K literal services.get_cash_margin_forecast() used to fall back to).

Uses an ISOLATED temp SQLite file for the whole run -- never the real
production DB_PATH -- so this test cannot corrupt the trader's real account
state. account_state.py does `from .ledger import DB_PATH`, which binds the
name directly into account_state's OWN module namespace; patching
`ledger.DB_PATH` alone would NOT affect account_state (it already has its
own bound reference), so this test patches `account_state.DB_PATH` itself,
and restores the original value in a finally block regardless of outcome.

No pytest dependency -- run directly: python3 tests/test_account_state.py
"""
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_BACKEND = _ROOT / "dashboard" / "backend"
sys.path.insert(0, str(_BACKEND))

from app import account_state  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


_original_db_path = account_state.DB_PATH
_tmp_dir = tempfile.mkdtemp(prefix="theta_lab_test_account_state_")
_tmp_db_path = os.path.join(_tmp_dir, "test_dashboard_actions.db")
account_state.DB_PATH = _tmp_db_path

try:
    print("emergency_reserve column -- set/get round trip")

    account_state.set_state("TEST_ACCT", emergency_reserve=145000.0)
    state1 = account_state.get_state("TEST_ACCT")
    check("set_state(emergency_reserve=145000.0) then get_state returns it back exactly",
          state1 is not None and state1.get("emergency_reserve") == 145000.0,
          f"got {state1}")

    print("\npartial update does not blank out a previously-set emergency_reserve")

    account_state.set_state("TEST_ACCT", cash=5000.0)
    state2 = account_state.get_state("TEST_ACCT")
    check("a later partial set_state(cash=...) leaves emergency_reserve untouched",
          state2 is not None and state2.get("emergency_reserve") == 145000.0,
          f"got {state2}")
    check("the partial update DID apply the field it was given (cash=5000.0)",
          state2 is not None and state2.get("cash") == 5000.0,
          f"got {state2}")

    print("\n_conn() ALTER TABLE migration is idempotent")

    try:
        conn1 = account_state._conn()
        conn1.close()
        conn2 = account_state._conn()
        conn2.close()
        migration_ok = True
        migration_detail = ""
    except Exception as exc:  # noqa: BLE001 -- we want to see ANY crash, not just OperationalError
        migration_ok = False
        migration_detail = f"{type(exc).__name__}: {exc}"
    check("calling _conn() twice in a row against the same (already-migrated) DB does not raise",
          migration_ok, migration_detail)

    print("\naccount with no emergency_reserve ever set")

    account_state.set_state("TEST_ACCT_NO_RESERVE", cash=1000.0)
    state3 = account_state.get_state("TEST_ACCT_NO_RESERVE")
    check("an account that never received emergency_reserve reports it as None, not 0 or a crash",
          state3 is not None and state3.get("emergency_reserve") is None,
          f"got {state3}")

finally:
    account_state.DB_PATH = _original_db_path
    try:
        os.remove(_tmp_db_path)
    except OSError:
        pass
    try:
        os.rmdir(_tmp_dir)
    except OSError:
        pass

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
