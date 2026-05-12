#!/usr/bin/env python3
"""
Generate standalone thematic analysis report
Market-driven investment narratives with options playbooks
"""

import sys
import json
from pathlib import Path
from datetime import date

# Add paths
base_path = Path(__file__).parent.parent
sys.path.insert(0, str(base_path / 'mcp' / 'reports'))
sys.path.insert(0, str(base_path / 'scripts'))

from open_positions_loader_v2 import OpenPositionsLoaderV2
from enhanced_metrics import batch_get_metrics
from thematic_analysis import generate_thematic_report_file


def main():
    """Generate thematic analysis report"""
    print("\n" + "=" * 140)
    print(f"THEMATIC ANALYSIS REPORT GENERATOR — {date.today().strftime('%A, %B %d, %Y')}")
    print("=" * 140 + "\n")

    # Load positions and metrics
    print("Loading positions data...")
    loader = OpenPositionsLoaderV2()
    open_positions, prices = loader.load_all_data()
    position_summary = loader.get_position_summary()

    print(f"  ✓ Loaded {len(open_positions)} positions across {len(position_summary)} tickers")

    # Get metrics
    print("Calculating metrics...")
    metrics = batch_get_metrics(
        position_summary.index.tolist(), prices
    )
    print(f"  ✓ Metrics calculated for {len(metrics)} tickers")

    # Generate thematic report
    print("Generating thematic analysis...")
    report_text, report_sections = generate_thematic_report_file(
        open_positions, metrics, prices, date.today()
    )

    # Print report
    print("\n")
    print(report_text)

    # Save to file
    output_file = base_path / 'logs' / f'thematic_report_{date.today().isoformat()}.txt'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(report_text)

    print(f"\n✓ Report saved to: {output_file}")

    # Summary statistics
    print("\n" + "=" * 140)
    print("REPORT SUMMARY")
    print("=" * 140)
    print(f"Generated: {date.today().isoformat()}")
    print(f"Positions analyzed: {len(open_positions)}")
    print(f"Tickers: {len(position_summary)}")
    print(f"Themes analyzed: 8")
    print(f"Report size: {len(report_text):,} characters")
    print("")


if __name__ == '__main__':
    main()
