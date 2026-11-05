"""
Regression tests for mcp/analysis/leg_decisions_tool.py -- the MCP-tool-facing
wrapper around dashboard/backend/app/services.get_leg_decisions() (ADR 0001
step 10, the half that was never built: the dashboard's Advisor surface had
no MCP tool exposing it, so every chat-driven decision this session had to
re-derive assignment-cash-impact/margin/gates by hand instead of calling the
already-tested decision_engine.py).

This module is a thin wrapper, not new decision logic -- decision_engine.py's
own tests (tests/test_decision_engine.py) already cover the real rules. What
needs testing here is the WIRING: (1) a successful call returns exactly what
services.get_leg_decisions() returns, unmodified, and (2) an import/call
failure (e.g. run outside the expected repo layout) degrades to an explicit
"unavailable" result instead of crashing the MCP tool call or raising past
the caller -- same discipline decision_engine.py itself already uses for
margin ("REG_T_ESTIMATE" vs "UNAVAILABLE").

No pytest dependency -- run directly: python3 tests/test_leg_decisions_tool.py
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "analysis"))

import leg_decisions_tool  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


print("get_leg_decisions_for_mcp() -- success path")

_fake_payload = {
    "decisions": [{"symbol": "OKTA", "coverage": "NAKED", "recommended_action": "hard stop"}],
    "rollup": {"total_margin_estimate": 4232.6, "concentration_gates": []},
}

with mock.patch.object(leg_decisions_tool, "_load_dashboard_services") as mocked_loader:
    mocked_loader.return_value = mock.Mock(get_leg_decisions=mock.Mock(return_value=_fake_payload))
    result = leg_decisions_tool.get_leg_decisions_for_mcp()

check("successful call returns the dashboard payload unmodified",
      result == {"available": True, **_fake_payload}, f"got {result}")

print("\n_load_dashboard_services() -- real (unmocked) import path")

# The mocked tests above only prove get_leg_decisions_for_mcp()'s OWN logic
# (success/failure shaping) -- they never exercise the real cross-app import,
# which is exactly how a prior review round caught this wrapper pointing at
# a dashboard_services.get_leg_decisions() that didn't exist yet in an
# incompletely-assembled worktree. This check imports the REAL app.services
# module (no mocking) and only asserts the attribute exists and is callable
# -- it deliberately does NOT call it, since a real call triggers an ~90s
# live 8-account reload + Yahoo fetch per symbol, which has no place in a
# fast regression suite. A live end-to-end call is a separate, explicit
# smoke-test step, not this test.
try:
    real_services = leg_decisions_tool._load_dashboard_services()
    has_attr = hasattr(real_services, "get_leg_decisions") and callable(real_services.get_leg_decisions)
    check("the real app.services module actually defines a callable get_leg_decisions",
          has_attr, f"module={real_services}")
except Exception as exc:
    check("the real app.services module actually defines a callable get_leg_decisions",
          False, f"_load_dashboard_services() raised {type(exc).__name__}: {exc}")

print("\nget_leg_decisions_for_mcp() -- import/call failure path")

with mock.patch.object(leg_decisions_tool, "_load_dashboard_services") as mocked_loader:
    mocked_loader.side_effect = ImportError("dashboard/backend/app not importable from this process")
    result2 = leg_decisions_tool.get_leg_decisions_for_mcp()

check("import failure returns an explicit unavailable result, not a raised exception",
      result2.get("available") is False and "error" in result2, f"got {result2}")
check("unavailable result never fabricates decisions/rollup keys",
      "decisions" not in result2 and "rollup" not in result2, f"got {result2}")

with mock.patch.object(leg_decisions_tool, "_load_dashboard_services") as mocked_loader:
    mocked_loader.return_value = mock.Mock(get_leg_decisions=mock.Mock(side_effect=RuntimeError("live data fetch failed")))
    result3 = leg_decisions_tool.get_leg_decisions_for_mcp()

check("a runtime failure inside get_leg_decisions() also degrades cleanly, not a crash",
      result3.get("available") is False and "error" in result3, f"got {result3}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
