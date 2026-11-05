"""
MCP-tool-facing wrapper around dashboard/backend/app/services.get_leg_decisions()
-- ADR 0001 step 10, the half that was never built.

decision_engine.py (steps 3-8) and its persistence into the dashboard's
refresh cycle (step 9) were already complete and tested before this file
existed -- but only dashboard/backend/app/services.py could call any of it.
mcp/server.py's own tool handlers (get_position_detail, scan_position_heat)
never gained access, so every "what do I actually do about this leg" question
in a chat session had to be re-derived by hand instead of calling the
already-tested engine. This module is the missing wire, not new decision
logic: it imports the dashboard's `app` package the same way ad hoc scripts
in this repo already do (sys.path bootstrap relative to this file, not a
hardcoded container path -- CODE_ROOT="/app" inside services.py itself is
harmless noise once the correct path is already first on sys.path, since
Python resolves imports against whichever matching path it finds first) and
calls its one real function.

Never raises past this module's own boundary -- an MCP tool handler that
crashes on an import/runtime failure gives a worse experience than an
explicit "available": False result, matching the same discipline
decision_engine.py already uses for an unpriceable margin estimate
("REG_T_ESTIMATE" vs "UNAVAILABLE").
"""
import os
import sys


def _dashboard_backend_path() -> str:
    """Walk up from this file to the repo root, then down to
    dashboard/backend -- mirrors symbol_context.py's own bootstrap pattern
    (search upward for a known sibling directory) instead of assuming a
    fixed number of parent hops or a container-absolute path."""
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidate = os.path.join(here, "dashboard", "backend")
        if os.path.isdir(candidate):
            return candidate
        here = os.path.dirname(here)
    raise ImportError("could not locate dashboard/backend from mcp/analysis/leg_decisions_tool.py")


def _load_dashboard_services():
    """Isolated so tests can mock this one seam instead of the whole import
    system -- the only thing this function does is make `app.services`
    importable and return it."""
    backend_path = _dashboard_backend_path()
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app import services  # noqa: PLC0415 -- intentionally deferred, see module docstring
    return services


def get_leg_decisions_for_mcp() -> dict:
    """One LegDecisionRecord per open short leg plus the portfolio rollup,
    reusing the exact same computation the dashboard's Advisor surface
    (`GET /api/us/leg-decisions`) already serves -- not a second,
    independently-computed version that could drift from it.
    """
    try:
        dashboard_services = _load_dashboard_services()
        payload = dashboard_services.get_leg_decisions()
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: any failure here
        # must degrade to an explicit result, never propagate into the MCP
        # tool-call boundary as a raised exception.
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {"available": True, **payload}
