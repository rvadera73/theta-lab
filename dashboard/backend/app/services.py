"""Thin wrappers around the existing report engine (mcp/reports,
scripts/realized_pnl.py) and the raw YAML trackers. No report-generation
logic lives here -- every function below calls something that already
exists and just reshapes it into JSON for the dashboard. See
docs/DASHBOARD_PLAN.md (Phase 1: read-only dashboard).
"""
import sys
import os
import yaml


def _to_native(obj):
    """Recursively convert numpy/pandas scalar types to plain Python so
    FastAPI's JSON encoder doesn't choke on them -- _compute_account_status
    sums pandas columns internally and can hand back numpy.float64/int64.
    """
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    if hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    return obj

CODE_ROOT = "/app"
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp", "reports"))
sys.path.insert(0, os.path.join(CODE_ROOT, "mcp"))
sys.path.insert(0, os.path.join(CODE_ROOT, "scripts"))

# The report engine (mcp/reports/*.py, scripts/open_positions_loader_v2.py)
# hardcodes this exact absolute host path for data/logs, not a CWD-relative
# one -- confirmed live 2026-09-25 ("No objects to concatenate" when data/
# was mounted at /app/data instead). docker-compose.yml mounts the real
# data/logs volumes here to match, so those modules work completely
# unmodified inside the container.
DATA_ROOT = "/home/rahulvadera/projects/theta-lab"

_report_generator = None


def _get_generator():
    # Cached at module scope, not per-request -- __init__ loads every
    # position file and fetches live prices for ~90 tickers (real network
    # calls), which is too slow to redo on every dashboard hit. A
    # dedicated "refresh" endpoint (Phase 1 stretch / Phase 4 scheduler)
    # invalidates this when fresher data is wanted.
    global _report_generator
    if _report_generator is None:
        from unified_master_report_production import UnifiedReportProduction
        _report_generator = UnifiedReportProduction()
    return _report_generator


def refresh_generator():
    global _report_generator
    _report_generator = None
    return _get_generator()


def get_account_status():
    gen = _get_generator()
    status = gen._compute_account_status()
    return _to_native([
        {"account": name, **dict(data.items())}
        for name, data in status.items()
    ])


def get_ytd_summary():
    from realized_pnl import get_realized_summary
    return get_realized_summary()


def get_monthly_by_account():
    from realized_pnl import get_realized_monthly_by_account
    return get_realized_monthly_by_account()


def _load_yaml(rel_path):
    path = os.path.join(DATA_ROOT, rel_path)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def get_active_decisions():
    data = _load_yaml("data/active_decisions.yaml") or {}
    return data.get("decisions", [])


def get_india_plan():
    return _load_yaml("data/india_6month_plan.yaml")
