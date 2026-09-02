"""
MCP TOOLS — Unified Master Reports
Exposes unified report generation as MCP tools for options-trader skill
"""

import sys
import asyncio
import json
from datetime import date
from pathlib import Path
from typing import Optional

sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/reports')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp/analysis')
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/mcp')

from unified_master_report_production import UnifiedReportProduction


async def generate_daily_report_tool(report_date: Optional[str] = None) -> dict:
    """
    Generate DAILY report with full conviction analysis

    Args:
        report_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict with report text, file path, and summary metrics
    """
    try:
        if report_date:
            from datetime import datetime
            today = datetime.fromisoformat(report_date).date()
        else:
            today = date.today()

        generator = UnifiedReportProduction()
        report = generator.generate_daily_report(today)

        # Daily is the first report converted to real Markdown (trader-requested
        # 2026-09-02) -- .md extension; weekly/biweekly/monthly stay .txt until
        # they get the same treatment.
        output_file = f"/home/rahulvadera/projects/theta-lab/logs/unified_master_report_{today.isoformat()}_daily_production.md"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report)

        # Extract summary metrics
        summary = {
            "type": "DAILY",
            "date": today.isoformat(),
            "positions": len(generator.open_positions),
            "tickers": generator.open_positions['ticker'].nunique(),
            "accounts": generator.account_summary.shape[0],
            "regime": generator.regime_data['regime'],
            "report_path": output_file,
            "report_length": len(report.split('\n')),
            "status": "✅ GENERATED"
        }

        return {
            "success": True,
            "summary": summary,
            "report_text": report[:5000] + "\n...\n[Report truncated for display. Full report saved to file.]",
            "file_path": output_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate daily report: {e}"
        }


async def generate_weekly_report_tool(report_date: Optional[str] = None) -> dict:
    """
    Generate WEEKLY report with action priorities and IV rank analysis

    Args:
        report_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict with report text, file path, and summary metrics
    """
    try:
        if report_date:
            from datetime import datetime
            today = datetime.fromisoformat(report_date).date()
        else:
            today = date.today()

        generator = UnifiedReportProduction()
        report = generator.generate_weekly_report(today)

        output_file = f"/home/rahulvadera/projects/theta-lab/logs/unified_master_report_{today.isoformat()}_weekly_production.txt"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report)

        summary = {
            "type": "WEEKLY",
            "date": today.isoformat(),
            "week_number": (today.day - 1) // 7 + 1,
            "positions": len(generator.open_positions),
            "regime": generator.regime_data['regime'],
            "report_path": output_file,
            "report_length": len(report.split('\n')),
            "status": "✅ GENERATED"
        }

        return {
            "success": True,
            "summary": summary,
            "report_text": report[:5000] + "\n...\n[Report truncated for display. Full report saved to file.]",
            "file_path": output_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate weekly report: {e}"
        }


async def generate_biweekly_report_tool(report_date: Optional[str] = None) -> dict:
    """
    Generate BI-WEEKLY trend analysis report

    Args:
        report_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict with report text, file path, and trend analysis
    """
    try:
        if report_date:
            from datetime import datetime
            today = datetime.fromisoformat(report_date).date()
        else:
            today = date.today()

        generator = UnifiedReportProduction()
        report = generator.generate_biweekly_report(today)

        output_file = f"/home/rahulvadera/projects/theta-lab/logs/unified_master_report_{today.isoformat()}_biweekly_production.txt"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report)

        summary = {
            "type": "BIWEEKLY",
            "date": today.isoformat(),
            "analysis_window": "3-month rolling",
            "positions": len(generator.open_positions),
            "report_path": output_file,
            "report_length": len(report.split('\n')),
            "status": "✅ GENERATED"
        }

        return {
            "success": True,
            "summary": summary,
            "report_text": report[:5000] + "\n...\n[Report truncated for display. Full report saved to file.]",
            "file_path": output_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate biweekly report: {e}"
        }


async def generate_monthly_report_tool(report_date: Optional[str] = None) -> dict:
    """
    Generate MONTHLY strategic review with Citadel comparison

    Args:
        report_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict with report text, file path, and monthly performance analysis
    """
    try:
        if report_date:
            from datetime import datetime
            today = datetime.fromisoformat(report_date).date()
        else:
            today = date.today()

        generator = UnifiedReportProduction()
        report = generator.generate_monthly_report(today)

        output_file = f"/home/rahulvadera/projects/theta-lab/logs/unified_master_report_{today.isoformat()}_monthly_production.txt"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report)

        summary = {
            "type": "MONTHLY",
            "date": today.isoformat(),
            "month": today.strftime('%B %Y'),
            "positions": len(generator.open_positions),
            "includes_citadel_comparison": True,
            "report_path": output_file,
            "report_length": len(report.split('\n')),
            "status": "✅ GENERATED"
        }

        return {
            "success": True,
            "summary": summary,
            "report_text": report[:5000] + "\n...\n[Report truncated for display. Full report saved to file.]",
            "file_path": output_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate monthly report: {e}"
        }


async def generate_all_reports_tool(report_date: Optional[str] = None) -> dict:
    """
    Generate ALL 4 reports at once (DAILY, WEEKLY, BIWEEKLY, MONTHLY)

    Args:
        report_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict with all 4 reports and file paths
    """
    try:
        if report_date:
            from datetime import datetime
            today = datetime.fromisoformat(report_date).date()
        else:
            today = date.today()

        print(f"\n{'='*80}")
        print("GENERATING ALL 4 UNIFIED MASTER REPORTS")
        print(f"{'='*80}\n")

        generator = UnifiedReportProduction()

        reports = {
            'daily': generator.generate_daily_report(today),
            'weekly': generator.generate_weekly_report(today),
            'biweekly': generator.generate_biweekly_report(today),
            'monthly': generator.generate_monthly_report(today)
        }

        output_files = {}
        for report_type, report_text in reports.items():
            # Daily is Markdown (.md) as of 2026-09-02; weekly/biweekly/monthly
            # stay .txt until they get the same conversion.
            ext = 'md' if report_type == 'daily' else 'txt'
            output_file = f"/home/rahulvadera/projects/theta-lab/logs/unified_master_report_{today.isoformat()}_{report_type}_production.{ext}"
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report_text)
            output_files[report_type] = output_file
            print(f"✓ {report_type.upper():10} → {output_file}")

        print(f"\n{'='*80}")
        print("ALL 4 REPORTS GENERATED SUCCESSFULLY")
        print(f"{'='*80}\n")

        summary = {
            "type": "ALL_4_REPORTS",
            "date": today.isoformat(),
            "daily": output_files['daily'],
            "weekly": output_files['weekly'],
            "biweekly": output_files['biweekly'],
            "monthly": output_files['monthly'],
            "total_reports": 4,
            "total_lines": sum(len(r.split('\n')) for r in reports.values()),
            "status": "✅ ALL GENERATED"
        }

        return {
            "success": True,
            "summary": summary,
            "output_files": output_files,
            "message": "All 4 reports generated successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate reports: {e}"
        }


# Entry point for async execution
async def main():
    """Test all tools"""
    print("Testing MCP Report Tools\n")

    # Generate all reports
    result = await generate_all_reports_tool()
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    asyncio.run(main())
