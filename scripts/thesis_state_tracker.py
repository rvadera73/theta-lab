"""
Thesis State Tracker — Persistent validation cache across all reports

Stores thesis status, conviction, moat assessment for every position.
Updated by: daily_trade_execution_report, enhanced_weekly_report, enhanced_monthly_report
Used by: All reports to show thesis trends + alternatives

State file: logs/thesis_state_{YYYY-MM-DD}.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from screener_loader import ScreenerLoader


class ThesisStateTracker:
    """Manage persistent thesis validation state across reports."""

    STATE_DIR = Path("logs/thesis_state")

    def __init__(self):
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.state_file = self.STATE_DIR / f"thesis_state_{datetime.now().strftime('%Y-%m-%d')}.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load thesis state from file, or create empty."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'generated_at': datetime.now().isoformat(),
            'positions': {},
            'universe': {}
        }

    def _save_state(self):
        """Persist thesis state to file."""
        self.state['last_updated'] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def update_position_thesis(
        self,
        symbol: str,
        thesis_status: str,  # GREEN/YELLOW/RED
        reason: str,
        action: str,
        tier: int,
        moat_strength: str,
        conviction: int = 5,  # 1-10 scale
        guidance_cuts: int = 0,
        earnings_beat: Optional[bool] = None,
        alternatives: Optional[List[str]] = None
    ):
        """Update thesis status for a single position."""
        symbol = str(symbol).upper()

        if symbol not in self.state['positions']:
            self.state['positions'][symbol] = {
                'history': []
            }

        # Append new state
        self.state['positions'][symbol]['history'].append({
            'timestamp': datetime.now().isoformat(),
            'status': thesis_status,
            'reason': reason,
            'action': action,
            'tier': tier,
            'moat_strength': moat_strength,
            'conviction': conviction,
            'guidance_cuts': guidance_cuts,
            'earnings_beat': earnings_beat,
            'alternatives': alternatives or []
        })

        # Keep latest state as current
        self.state['positions'][symbol]['current'] = self.state['positions'][symbol]['history'][-1]
        self._save_state()

    def get_position_thesis(self, symbol: str) -> Optional[Dict]:
        """Get current thesis state for a position."""
        symbol = str(symbol).upper()
        if symbol in self.state['positions']:
            return self.state['positions'][symbol].get('current')
        return None

    def get_position_history(self, symbol: str) -> List[Dict]:
        """Get full thesis history for a position."""
        symbol = str(symbol).upper()
        if symbol in self.state['positions']:
            return self.state['positions'][symbol].get('history', [])
        return []

    def update_universe_snapshot(self, market_regime: str, universe: Dict):
        """Record Holdings universe at time of report generation."""
        self.state['universe'][market_regime] = {
            'timestamp': datetime.now().isoformat(),
            'count': len(universe),
            'tier_distribution': {
                'tier_1': sum(1 for m in universe.values() if m.get('tier') == 1),
                'tier_2': sum(1 for m in universe.values() if m.get('tier') == 2),
                'tier_3': sum(1 for m in universe.values() if m.get('tier') == 3),
            },
            'eligible_names': list(universe.keys())
        }
        self._save_state()

    def get_thesis_summary(self) -> Dict:
        """Get summary: RED/YELLOW/GREEN counts, conviction distribution."""
        summary = {
            'total_positions': len(self.state['positions']),
            'status_distribution': {'RED': 0, 'YELLOW': 0, 'GREEN': 0},
            'conviction_avg': 0,
            'tier_distribution': {'tier_1': 0, 'tier_2': 0, 'tier_3': 0},
            'permanent_exits': [],
            'thesis_broken': [],
            'thesis_intact': []
        }

        conviction_sum = 0
        count = 0

        for symbol, pos_data in self.state['positions'].items():
            current = pos_data.get('current')
            if not current:
                continue

            # Status distribution
            status = current.get('status')
            summary['status_distribution'][status] = summary['status_distribution'].get(status, 0) + 1

            # Conviction
            conv = current.get('conviction', 5)
            conviction_sum += conv
            count += 1

            # Tier distribution
            tier = current.get('tier')
            if tier == 1:
                summary['tier_distribution']['tier_1'] += 1
            elif tier == 2:
                summary['tier_distribution']['tier_2'] += 1
            elif tier == 3:
                summary['tier_distribution']['tier_3'] += 1

            # Categorize by thesis status
            reason = current.get('reason', '')
            if 'permanent exit' in reason.lower():
                summary['permanent_exits'].append(symbol)
            elif status == 'RED':
                summary['thesis_broken'].append(symbol)
            elif status == 'GREEN':
                summary['thesis_intact'].append(symbol)

        if count > 0:
            summary['conviction_avg'] = conviction_sum / count

        return summary

    def get_thesis_validation_report(self, positions_df: pd.DataFrame) -> str:
        """Generate thesis validation report for all positions in positions_df."""
        output = []
        output.append("=" * 80)
        output.append("THESIS VALIDATION SUMMARY (All Positions)")
        output.append("=" * 80)
        output.append("")

        # Get unique positions from positions_df
        symbols = set(positions_df['symbol'].dropna().str.upper().unique())

        # Group by thesis status
        red_positions = []
        yellow_positions = []
        green_positions = []

        for symbol in sorted(symbols):
            thesis = self.get_position_thesis(symbol)
            if not thesis:
                continue

            status = thesis.get('status')
            tier = thesis.get('tier')
            conviction = thesis.get('conviction', 5)
            moat = thesis.get('moat_strength', 'UNKNOWN')

            display_line = f"  {symbol:10} Tier {tier} | {moat:10} | Conviction {conviction}/10"

            if status == 'RED':
                red_positions.append((symbol, thesis, display_line))
            elif status == 'YELLOW':
                yellow_positions.append((symbol, thesis, display_line))
            else:
                green_positions.append((symbol, thesis, display_line))

        # Display RED
        if red_positions:
            output.append("❌ THESIS BROKEN (RED) — Action Required")
            output.append("-" * 80)
            for symbol, thesis, line in red_positions:
                output.append(line)
                output.append(f"     Reason: {thesis.get('reason')}")
                output.append(f"     Action: {thesis.get('action')}")
                alts = thesis.get('alternatives', [])
                if alts:
                    output.append(f"     Alternatives: {', '.join(alts[:3])}")
                output.append("")

        # Display YELLOW
        if yellow_positions:
            output.append("⚠️  THESIS AT RISK (YELLOW) — Monitor Closely")
            output.append("-" * 80)
            for symbol, thesis, line in yellow_positions:
                output.append(line)
                output.append(f"     Reason: {thesis.get('reason')}")
                output.append(f"     Action: {thesis.get('action')}")
                output.append("")

        # Display GREEN
        if green_positions:
            output.append("✅ THESIS INTACT (GREEN) — Hold")
            output.append("-" * 80)
            for symbol, thesis, line in green_positions:
                output.append(line)
                output.append(f"     Reason: {thesis.get('reason')}")
                output.append("")

        # Summary stats
        summary = self.get_thesis_summary()
        output.append("=" * 80)
        output.append("SUMMARY STATISTICS")
        output.append("=" * 80)
        output.append(f"Total Positions: {summary['total_positions']}")
        output.append(f"  RED (Action): {summary['status_distribution']['RED']}")
        output.append(f"  YELLOW (Monitor): {summary['status_distribution']['YELLOW']}")
        output.append(f"  GREEN (Hold): {summary['status_distribution']['GREEN']}")
        output.append(f"Average Conviction: {summary['conviction_avg']:.1f}/10")
        output.append(f"Tier Distribution:")
        output.append(f"  Tier 1 (Core): {summary['tier_distribution']['tier_1']}")
        output.append(f"  Tier 2 (Emerging): {summary['tier_distribution']['tier_2']}")
        output.append(f"  Tier 3 (Speculative): {summary['tier_distribution']['tier_3']}")
        output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    print("Thesis State Tracker Test\n")

    tracker = ThesisStateTracker()

    # Update some positions
    tracker.update_position_thesis(
        'PYPL',
        thesis_status='RED',
        reason='Fintech thesis broken. Weak moat vs Apple Pay/Stripe',
        action='CLOSE and redeploy',
        tier=2,
        moat_strength='WEAK',
        conviction=2,
        guidance_cuts=2,
        alternatives=['ALAB', 'RKLB', 'VST']
    )

    tracker.update_position_thesis(
        'AXON',
        thesis_status='GREEN',
        reason='Tier 1 AI pick/shovel. Strong moat in gov tech.',
        action='HOLD',
        tier=1,
        moat_strength='STRONG',
        conviction=9,
        earnings_beat=True
    )

    tracker.update_position_thesis(
        'ADBE',
        thesis_status='YELLOW',
        reason='Canva/Midjourney eroding consumer moat. Enterprise stickier.',
        action='MONITOR. Prepare exit if margin pressure continues.',
        tier=1,
        moat_strength='MODERATE',
        conviction=6,
        earnings_beat=False
    )

    # Get summary
    summary = tracker.get_thesis_summary()
    print(f"Positions tracked: {summary['total_positions']}")
    print(f"Status: {summary['status_distribution']}")
    print(f"Avg conviction: {summary['conviction_avg']:.1f}/10")
    print("")

    # Get position history
    print("PYPL History:")
    for entry in tracker.get_position_history('PYPL'):
        print(f"  {entry['timestamp']}: {entry['status']} - {entry['reason']}")
