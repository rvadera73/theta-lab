"""
Unified Master Report — MCP entry point.

Delegates to the DETAILED production engine (UnifiedReportProduction), which loads
all 9 accounts via open_positions_loader_v2 (3 Schwab, 3 Fidelity, 1 Vanguard,
2 Robinhood) and renders the full multi-section daily/weekly/bi-weekly/monthly reports.

This replaces the former thin-summary implementation (which used DynamicDataLoader and
emitted only position counts). Wired to mcp/server.py's `generate_unified_master_report`
tool; preserves the same signature and return shape {text, type, saved_to}.
"""

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/analysis')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp')

from unified_master_report_production import UnifiedReportProduction


async def generate_unified_master_report(
    report_type: Optional[str] = None,
    save_to_file: bool = True,
) -> dict:
    """Generate the detailed unified master report (all 9 accounts) via the
    production engine.

    report_type: DAILY | WEEKLY | BIWEEKLY | MONTHLY (auto-detected if None).
    """
    today = date.today()

    if not report_type:
        if today.day == 1:
            report_type = 'MONTHLY'
        elif today.day == 15:
            report_type = 'BIWEEKLY'
        elif today.weekday() == 0:
            report_type = 'WEEKLY'
        else:
            report_type = 'DAILY'

    report_type = report_type.upper()

    generator = UnifiedReportProduction()
    builders = {
        'DAILY': generator.generate_daily_report,
        'WEEKLY': generator.generate_weekly_report,
        'BIWEEKLY': generator.generate_biweekly_report,
        'MONTHLY': generator.generate_monthly_report,
    }
    if report_type not in builders:
        report_type = 'DAILY'

    report_text = builders[report_type](today)

    output_file = None
    if save_to_file:
        output_file = (
            f"logs/unified_master_report_{today.isoformat()}_{report_type.lower()}_production.txt"
        )
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_text)

    return {
        "text": report_text,
        "type": report_type,
        "saved_to": output_file,
    }
