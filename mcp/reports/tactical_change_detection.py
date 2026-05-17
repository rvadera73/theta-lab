"""
Tactical Change Detection Engine
Identifies major shifts in themes, conviction, catalysts, momentum
Triggers tactical report generation only on significant changes
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, Tuple, List
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TacticalChangeDetector:
    """Detect major changes across themes that warrant tactical report"""

    # Change thresholds (what constitutes MAJOR)
    CONVICTION_CHANGE_THRESHOLD = 1.0  # ±1.0 = major shift
    HEAT_DIST_CHANGE_THRESHOLD = 0.20  # 20% shift in heat distribution
    MOMENTUM_CHANGE_THRESHOLD = 0.15  # 15-day momentum reversal
    IV_REGIME_CHANGE = True  # Any IV regime shift = major
    CATALYST_URGENCY_THRESHOLD = 14  # Catalyst within 2 weeks = major
    MISSING_NAME_THRESHOLD = 1000  # New name >$1M opportunity = major

    def __init__(self, sector_summary: Dict, theme_metrics: Dict, prices: Dict):
        """Initialize change detector"""
        self.sector_summary = sector_summary
        self.theme_metrics = theme_metrics
        self.prices = prices
        self.changes_detected = []
        self.change_severity = 0  # 0-10 scale

    def detect_conviction_shifts(self, previous_theme_metrics: Dict = None) -> List[str]:
        """Detect conviction changes in themes"""
        changes = []

        if not previous_theme_metrics:
            return changes

        for theme_key, current_metrics in self.theme_metrics.items():
            if theme_key not in previous_theme_metrics:
                continue

            prev_metrics = previous_theme_metrics[theme_key]
            current_conv = current_metrics.get('avg_conviction', 0)
            prev_conv = prev_metrics.get('avg_conviction', 0)
            change = abs(current_conv - prev_conv)

            if change >= self.CONVICTION_CHANGE_THRESHOLD:
                direction = "↑ STRENGTHENING" if current_conv > prev_conv else "↓ WEAKENING"
                changes.append(
                    f"🔴 CONVICTION SHIFT: {current_metrics['name']} {direction} "
                    f"({prev_conv:.1f} → {current_conv:.1f}) [+{change:.1f}]"
                )
                self.change_severity += 2

        return changes

    def detect_heat_distribution_shifts(self, previous_theme_metrics: Dict = None) -> List[str]:
        """Detect portfolio stress level changes"""
        changes = []

        if not previous_theme_metrics:
            return changes

        for theme_key, current_metrics in self.theme_metrics.items():
            if theme_key not in previous_theme_metrics:
                continue

            prev_metrics = previous_theme_metrics[theme_key]
            current_heat = current_metrics.get('heat_distribution', {})
            prev_heat = prev_metrics.get('heat_distribution', {})

            # Check RED (stressed) positions
            current_red = current_heat.get('RED', 0)
            prev_red = prev_heat.get('RED', 0)
            total_positions = current_metrics.get('positions_held', 1)
            red_change = abs(current_red - prev_red) / max(total_positions, 1)

            if red_change >= self.HEAT_DIST_CHANGE_THRESHOLD:
                changes.append(
                    f"🟠 HEAT DISTRIBUTION: {current_metrics['name']} stress increased "
                    f"({prev_red} → {current_red} RED positions)"
                )
                self.change_severity += 1

        return changes

    def detect_iv_regime_shifts(self, previous_theme_metrics: Dict = None) -> List[str]:
        """Detect IV regime changes"""
        changes = []

        if not previous_theme_metrics:
            return changes

        iv_regime_map = {
            'LOW': 1,
            'MODERATE': 2,
            'ELEVATED': 3,
            'HIGH': 4,
            'VERY HIGH': 5,
        }

        for theme_key, current_metrics in self.theme_metrics.items():
            if theme_key not in previous_theme_metrics:
                continue

            prev_metrics = previous_theme_metrics[theme_key]
            current_iv = current_metrics.get('iv_regime', '')
            prev_iv = prev_metrics.get('iv_regime', '')

            # Extract base regime (ignore qualifiers)
            current_base = current_iv.split('(')[0].strip()
            prev_base = prev_iv.split('(')[0].strip()

            if current_base != prev_base and self.IV_REGIME_CHANGE:
                current_level = iv_regime_map.get(current_base, 0)
                prev_level = iv_regime_map.get(prev_base, 0)
                changes.append(
                    f"📊 IV REGIME SHIFT: {current_metrics['name']} {prev_base} → {current_base} "
                    f"(premium environment {'improved' if current_level > prev_level else 'deteriorated'})"
                )
                self.change_severity += 1.5

        return changes

    def detect_momentum_reversals(self, prices_history: Dict[str, List[float]] = None) -> List[str]:
        """Detect 15-day momentum reversals"""
        changes = []

        if not prices_history:
            return changes

        for theme_key, theme_positions in self.theme_metrics.items():
            positions = theme_positions.get('top_positions', [])

            for ticker, notional, conviction in positions[:3]:  # Check top 3 positions
                if ticker not in prices_history:
                    continue

                prices = prices_history[ticker]
                if len(prices) < 15:
                    continue

                # Calculate 15-day momentum
                price_15d_ago = prices[-15] if len(prices) > 15 else prices[0]
                price_today = prices[-1]
                momentum_pct = ((price_today - price_15d_ago) / price_15d_ago) * 100

                # Flag if >15% reversal
                if abs(momentum_pct) >= self.MOMENTUM_CHANGE_THRESHOLD * 100:
                    direction = "📈 RALLY" if momentum_pct > 0 else "📉 DECLINE"
                    changes.append(
                        f"{direction}: {theme_key} / {ticker} {momentum_pct:+.1f}% over 15 days "
                        f"(momentum {'exhaustion' if abs(momentum_pct) > 20 else 'continued'})"
                    )
                    self.change_severity += 1

        return changes

    def detect_catalyst_urgency(self) -> List[str]:
        """Detect urgent catalysts (within 2-3 weeks)"""
        changes = []

        for theme_key, theme_metrics in self.theme_metrics.items():
            catalysts = theme_metrics.get('catalysts', [])

            for catalyst in catalysts[:3]:  # Top 3 catalysts
                # Check for date-specific catalysts
                if 'earnings' in catalyst.lower() or 'approval' in catalyst.lower() or 'announcement' in catalyst.lower():
                    # Assume first catalyst is most imminent
                    changes.append(
                        f"⏰ URGENT CATALYST: {theme_key} | {catalyst} "
                        f"(within 14 days, plan exit/entry strategy)"
                    )
                    self.change_severity += 1.5
                    break  # One per theme

        return changes

    def detect_missing_opportunities(self, missing_names: Dict[str, float] = None) -> List[str]:
        """Detect new high-opportunity names not in portfolio"""
        changes = []

        if not missing_names:
            return changes

        for name, opportunity_score in missing_names.items():
            if opportunity_score >= self.MISSING_NAME_THRESHOLD:
                changes.append(
                    f"💡 NEW OPPORTUNITY: {name} (${opportunity_score:,.0f} premium potential, not in portfolio)"
                )
                self.change_severity += 1

        return changes

    def run_detection(self, previous_metrics: Dict = None, prices_history: Dict = None, missing_names: Dict = None) -> Tuple[int, List[str], bool]:
        """Run full change detection suite

        Returns:
            (change_severity: 0-10, changes: list of change descriptions, should_report: bool)
        """
        all_changes = []

        # Run all detectors
        all_changes.extend(self.detect_conviction_shifts(previous_metrics))
        all_changes.extend(self.detect_heat_distribution_shifts(previous_metrics))
        all_changes.extend(self.detect_iv_regime_shifts(previous_metrics))
        all_changes.extend(self.detect_momentum_reversals(prices_history))
        all_changes.extend(self.detect_catalyst_urgency())
        all_changes.extend(self.detect_missing_opportunities(missing_names))

        self.changes_detected = all_changes

        # Threshold: severity > 2.5 or >2 changes = generate report
        should_report = self.change_severity >= 2.5 or len(all_changes) >= 2

        return self.change_severity, all_changes, should_report

    def get_summary(self) -> str:
        """Generate change summary for email subject/header"""
        if not self.changes_detected:
            return "No significant changes detected"

        severity_label = {
            (0, 2): "Minor",
            (2, 4): "Moderate",
            (4, 6): "Significant",
            (6, 8): "Major",
            (8, 10): "Critical",
        }

        label = "Critical"
        for (min_sev, max_sev), sev_label in severity_label.items():
            if min_sev <= self.change_severity < max_sev:
                label = sev_label
                break

        return f"{label} changes detected ({self.change_severity:.1f}/10 severity) — {len(self.changes_detected)} signals"


def load_previous_metrics(days_back: int = 7) -> Dict:
    """Load theme metrics from previous week"""
    previous_date = date.today() - timedelta(days=days_back)
    sector_analysis_file = Path(f'logs/sector_analysis_{previous_date.isoformat()}.json')

    if not sector_analysis_file.exists():
        return None

    try:
        with open(sector_analysis_file, 'r') as f:
            data = json.load(f)
            return data.get('sector_summary', {})
    except Exception as e:
        logger.warning(f"Could not load previous metrics: {e}")
        return None


def generate_change_report(changes_detected: List[str], change_severity: float) -> List[str]:
    """Generate formatted change detection report"""
    output = []

    output.append("=" * 140)
    output.append("WEEKLY TACTICAL CHANGE ALERT")
    output.append(f"Date: {date.today().strftime('%A, %B %d, %Y')}")
    output.append("=" * 140)
    output.append("")

    output.append(f"CHANGE SEVERITY: {change_severity:.1f}/10")
    output.append(f"CHANGES DETECTED: {len(changes_detected)}")
    output.append("")

    if not changes_detected:
        output.append("✓ No significant changes detected. Continue with existing strategy.")
        output.append("")
    else:
        output.append("MAJOR SIGNALS:")
        output.append("-" * 140)
        for i, change in enumerate(changes_detected, 1):
            output.append(f"{i}. {change}")
        output.append("")

    output.append("=" * 140)
    output.append("")
    output.append("RECOMMENDED ACTIONS:")
    output.append("1. Review THEMATIC_TACTICAL_GUIDE.md for detailed entry/exit signals")
    output.append("2. Check catalyst calendar for this week's earnings/announcements")
    output.append("3. Monitor positions flagged above for execution")
    output.append("")

    return output
