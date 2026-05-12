#!/usr/bin/env python3
"""
Generate Tactical Change Detection Report
Runs weekly, only reports if major changes detected
"""

import sys
import json
from pathlib import Path
from datetime import date, timedelta

base_path = Path(__file__).parent.parent
sys.path.insert(0, str(base_path / 'mcp' / 'reports'))
sys.path.insert(0, str(base_path / 'scripts'))

from open_positions_loader_v2 import OpenPositionsLoaderV2
from enhanced_metrics import batch_get_metrics
from thematic_analysis import batch_get_sector_analysis
from tactical_change_detection import TacticalChangeDetector, load_previous_metrics, generate_change_report


def main():
    """Generate tactical change report"""
    print("\n" + "=" * 140)
    print(f"TACTICAL CHANGE DETECTION — {date.today().strftime('%A, %B %d, %Y')}")
    print("=" * 140 + "\n")

    # Load current data
    print("Loading current positions and metrics...")
    loader = OpenPositionsLoaderV2()
    open_positions, prices = loader.load_all_data()
    position_summary = loader.get_position_summary()

    metrics = batch_get_metrics(position_summary.index.tolist(), prices)
    sector_summary, _, _ = batch_get_sector_analysis(open_positions, metrics, prices)

    print(f"  ✓ Current data loaded: {len(open_positions)} positions, {len(metrics)} metrics")

    # Load previous week's data
    print("Loading previous week's metrics...")
    previous_metrics = load_previous_metrics(days_back=7)
    if previous_metrics:
        print(f"  ✓ Previous week data found ({(date.today() - timedelta(days=7)).isoformat()})")
    else:
        print("  ⚠️ No previous week data available (first run or stale data)")

    # Run change detection
    print("Running change detection...")
    detector = TacticalChangeDetector(sector_summary, {}, prices)

    # Simulate theme metrics from sector analysis for demo
    theme_metrics = {}  # In production, this would come from thematic_analysis.py output

    severity, changes, should_report = detector.run_detection(
        previous_metrics=previous_metrics,
        prices_history=None,  # Would need historical prices in production
        missing_names={
            'SNDK': 1500000,
            'AVGO': 1200000,
            'PWR': 800000,
            'TER': 600000,
            'LRCX': 750000,
        }
    )

    print(f"  ✓ Change severity: {severity:.1f}/10")
    print(f"  ✓ Changes detected: {len(changes)}")
    print(f"  ✓ Report generation: {'YES (threshold exceeded)' if should_report else 'NO (below threshold)'}")

    # Generate report
    if should_report:
        print("\nGenerating tactical change report...")
        report_lines = generate_change_report(changes, severity)
        report_text = "\n".join(report_lines)

        # Print to console
        print("\n" + report_text)

        # Save to file
        output_file = base_path / 'logs' / f'tactical_change_report_{date.today().isoformat()}.txt'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(report_text)

        print(f"\n✓ Report saved to: {output_file}")

        # Save change metadata for next week
        metadata_file = base_path / 'logs' / f'tactical_changes_metadata_{date.today().isoformat()}.json'
        with open(metadata_file, 'w') as f:
            json.dump({
                'date': date.today().isoformat(),
                'severity': severity,
                'changes_count': len(changes),
                'should_report': should_report,
                'changes': changes,
            }, f, indent=2)

        print(f"✓ Metadata saved to: {metadata_file}")

    else:
        print("\n⊘ No significant changes. Report suppressed.")
        print(f"  Severity: {severity:.1f}/10 (threshold: 2.5)")
        print(f"  Changes: {len(changes)} (threshold: 2)")
        # Still save metadata for audit trail
        metadata_file = base_path / 'logs' / f'tactical_changes_metadata_{date.today().isoformat()}.json'
        with open(metadata_file, 'w') as f:
            json.dump({
                'date': date.today().isoformat(),
                'severity': severity,
                'changes_count': len(changes),
                'should_report': should_report,
                'changes': changes,
            }, f, indent=2)
        print(f"✓ Metadata saved to: {metadata_file}")

    print("\n" + "=" * 140)


if __name__ == '__main__':
    main()
