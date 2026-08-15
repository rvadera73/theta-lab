#!/usr/bin/env python3
"""
Analyze current holdings by sector using Yahoo Finance classifications
Shows conviction, heat, and valuation positioning by sector
Used to inform sector rotation framework design
"""

import sys
import json
from pathlib import Path
from datetime import date

# Add paths
base_path = Path(__file__).parent.parent
sys.path.insert(0, str(base_path / 'mcp' / 'reports'))
sys.path.insert(0, str(base_path / 'scripts'))
sys.path.insert(0, str(base_path / 'mcp' / 'analysis'))

from open_positions_loader_v2 import OpenPositionsLoaderV2
from enhanced_metrics import batch_get_metrics
from sector_analysis import batch_get_sector_analysis


def main():
    """Generate sector analysis from current holdings"""
    print("\n" + "=" * 120)
    print(f"SECTOR DATA ANALYSIS — {date.today().strftime('%A, %B %d, %Y')}")
    print("=" * 120 + "\n")

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

    # Analyze by sector
    print("Analyzing sectors...")
    sector_summary, analysis_section, rotation_section, _ticker_sector_map = batch_get_sector_analysis(
        open_positions, metrics, prices
    )
    print(f"  ✓ Analyzed {len(sector_summary)} sectors")

    # Print analysis
    print("\n".join(analysis_section))
    print("\n".join(rotation_section))

    # Save to file
    output_file = base_path / 'logs' / f'sector_analysis_{date.today().isoformat()}.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        # Serialize sector_summary (convert top_positions tuples to lists)
        serializable_summary = {}
        for sector, data in sector_summary.items():
            serializable_summary[sector] = {
                **data,
                'top_positions': [list(pos) for pos in data['top_positions']]
            }

        json.dump({
            'date': date.today().isoformat(),
            'sector_summary': serializable_summary,
            'sectors_analyzed': len(sector_summary),
            'total_positions': len(open_positions),
            'total_tickers': len(position_summary),
        }, f, indent=2)

    print(f"\n✓ Analysis saved to: {output_file}")

    # Summary stats
    print("\n" + "=" * 120)
    print("SECTOR ANALYSIS SUMMARY")
    print("=" * 120)

    attraction_count = sum(1 for d in sector_summary.values() if d['signal_type'] == 'ATTRACTION')
    extension_count = sum(1 for d in sector_summary.values() if d['signal_type'] == 'EXTENSION')
    mixed_count = sum(1 for d in sector_summary.values() if d['signal_type'] == 'MIXED')
    neutral_count = sum(1 for d in sector_summary.values() if d['signal_type'] in ['CAUTION', 'NEUTRAL'])

    print(f"Total sectors represented: {len(sector_summary)}")
    print(f"  🟢 Attraction signals: {attraction_count}")
    print(f"  🟠 Mixed signals: {mixed_count}")
    print(f"  🔴 Extension signals: {extension_count}")
    print(f"  🟡 Neutral/Monitor signals: {neutral_count}")

    print("\n")


if __name__ == '__main__':
    main()
