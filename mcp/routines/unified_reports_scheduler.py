"""
UNIFIED REPORTS SCHEDULER
Automated report generation based on day of week and date
Integrates with options-trader skill
"""

import asyncio
import sys
from datetime import date, datetime
from pathlib import Path

# Determine base path dynamically (works in both local and GitHub Actions environments)
base_path = Path(__file__).parent.parent.parent  # Goes up from mcp/routines to project root

sys.path.insert(0, str(base_path / 'scripts'))
sys.path.insert(0, str(base_path / 'mcp' / 'reports'))
sys.path.insert(0, str(base_path / 'mcp' / 'analysis'))
sys.path.insert(0, str(base_path / 'mcp'))

from mcp_unified_reports import (
    generate_daily_report_tool,
    generate_weekly_report_tool,
    generate_biweekly_report_tool,
    generate_monthly_report_tool,
    generate_all_reports_tool
)


class UnifiedReportsScheduler:
    """Automatic report generation scheduler"""

    @staticmethod
    def determine_report_type(report_date: date = None) -> list:
        """
        Determine which reports to generate based on date

        Daily: Always generated
        Weekly: Generated on Mondays (weekday == 0)
        Bi-weekly: Generated on the 1st and 15th of month
        Monthly: Generated on the 1st of month
        """
        if report_date is None:
            report_date = date.today()

        reports_to_generate = ['daily']  # Always generate daily

        # Monday = weekly
        if report_date.weekday() == 0:
            reports_to_generate.append('weekly')

        # 15th = biweekly
        if report_date.day == 15:
            reports_to_generate.append('biweekly')

        # 1st = monthly AND biweekly
        if report_date.day == 1:
            reports_to_generate.append('biweekly')
            reports_to_generate.append('monthly')

        return reports_to_generate

    @staticmethod
    async def run_scheduled_reports(report_date: date = None):
        """Run all applicable reports for the given date"""
        if report_date is None:
            report_date = date.today()

        print(f"\n{'='*80}")
        print(f"UNIFIED REPORTS SCHEDULER — {report_date.strftime('%A, %B %d, %Y')}")
        print(f"{'='*80}\n")

        reports_to_run = UnifiedReportsScheduler.determine_report_type(report_date)
        print(f"Reports scheduled for today: {', '.join(reports_to_run).upper()}\n")

        results = {}
        report_date_str = report_date.isoformat()

        # Run each report type
        if 'daily' in reports_to_run:
            print("Generating DAILY report...")
            result = await generate_daily_report_tool(report_date_str)
            results['daily'] = result
            if result.get('success'):
                print(f"  ✓ Daily report: {result['file_path']}\n")
            else:
                print(f"  ✗ Daily report failed: {result.get('error')}\n")

        if 'weekly' in reports_to_run:
            print("Generating WEEKLY report...")
            result = await generate_weekly_report_tool(report_date_str)
            results['weekly'] = result
            if result.get('success'):
                print(f"  ✓ Weekly report: {result['file_path']}\n")
            else:
                print(f"  ✗ Weekly report failed: {result.get('error')}\n")

        if 'biweekly' in reports_to_run:
            print("Generating BI-WEEKLY report...")
            result = await generate_biweekly_report_tool(report_date_str)
            results['biweekly'] = result
            if result.get('success'):
                print(f"  ✓ Bi-weekly report: {result['file_path']}\n")
            else:
                print(f"  ✗ Bi-weekly report failed: {result.get('error')}\n")

        if 'monthly' in reports_to_run:
            print("Generating MONTHLY report...")
            result = await generate_monthly_report_tool(report_date_str)
            results['monthly'] = result
            if result.get('success'):
                print(f"  ✓ Monthly report: {result['file_path']}\n")
            else:
                print(f"  ✗ Monthly report failed: {result.get('error')}\n")

        # Summary
        successful = sum(1 for r in results.values() if r.get('success'))
        total = len(results)

        print(f"{'='*80}")
        print(f"SCHEDULE EXECUTION COMPLETE: {successful}/{total} reports generated")
        print(f"{'='*80}\n")

        return {
            'date': report_date.isoformat(),
            'scheduled_reports': reports_to_run,
            'results': results,
            'successful': successful,
            'total': total,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Main entry point - can be called from GitHub Actions or cron"""
    import json

    # Generate reports for today
    result = await UnifiedReportsScheduler.run_scheduled_reports()

    # Write result to log file
    log_file = f"logs/scheduler_run_{date.today().isoformat()}.json"
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Scheduler log: {log_file}")

    return result


if __name__ == '__main__':
    asyncio.run(main())
