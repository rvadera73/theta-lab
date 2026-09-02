"""
Sector analysis using Yahoo Finance native sector classifications
Groups positions by sector and analyzes conviction, heat, and valuation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class SectorAnalyzer:
    """Analyze positions and metrics by sector"""

    SECTOR_DISPLAY_ORDER = [
        'Technology',
        'Healthcare',
        'Financials',
        'Consumer Cyclical',
        'Industrials',
        'Energy',
        'Materials',
        'Consumer Defensive',
        'Utilities',
        'Real Estate',
        'Communication Services',
        'Defense',
        'Brand-Quality (Non-AI)',
    ]

    # Custom sector mapping for specific tickers
    CUSTOM_SECTOR_MAP = {
        # Defense sector
        'NOC': 'Defense',
        'LMT': 'Defense',
        'RTX': 'Defense',
        'BA': 'Defense',
        'GD': 'Defense',
        'HII': 'Defense',
        'TXT': 'Defense',
        'CCI': 'Defense',

        # Brand-Quality (Non-AI) - luxury, consumer staples, healthcare
        'LVMH': 'Brand-Quality (Non-AI)',
        'EL': 'Brand-Quality (Non-AI)',
        'ULTA': 'Brand-Quality (Non-AI)',
        'ELF': 'Brand-Quality (Non-AI)',
        'MRK': 'Brand-Quality (Non-AI)',
        'JNJ': 'Brand-Quality (Non-AI)',
        'PG': 'Brand-Quality (Non-AI)',
        'KO': 'Brand-Quality (Non-AI)',
        'PEP': 'Brand-Quality (Non-AI)',
        'SBUX': 'Brand-Quality (Non-AI)',
        'MCD': 'Brand-Quality (Non-AI)',
        'CMG': 'Brand-Quality (Non-AI)',
        'NKE': 'Brand-Quality (Non-AI)',
        'ANET': 'Brand-Quality (Non-AI)',
    }

    def __init__(self, open_positions: pd.DataFrame, metrics: Dict, prices: Dict, iv_ranks: Dict = None):
        """
        Initialize with positions data and metrics

        Args:
            open_positions: DataFrame with ticker, net_quantity columns
            metrics: Dict[ticker] -> metrics dict with conviction, heat_status, rsi, position_in_52w_range
            prices: Dict[ticker] -> current price
            iv_ranks: Dict[ticker] -> {iv_rank, iv_pct, ...} from analysis.iv_rank.batch_iv_rank.
                Optional — omit (or pass {}) to keep the sector signal price-only,
                same as before this was added.
        """
        self.open_positions = open_positions
        self.metrics = metrics
        self.prices = prices
        self.iv_ranks = iv_ranks or {}
        self.sector_map = {}
        self.sector_data = {}
        self._fetch_sector_data()

    def _fetch_sector_data(self):
        """Fetch sector classifications from Yahoo Finance + custom overrides"""
        unique_tickers = self.open_positions['ticker'].unique()

        for ticker in unique_tickers:
            # Check custom sector map first
            if ticker in self.CUSTOM_SECTOR_MAP:
                self.sector_map[ticker] = self.CUSTOM_SECTOR_MAP[ticker]
            else:
                # Fall back to Yahoo Finance
                try:
                    info = yf.Ticker(ticker).info
                    sector = info.get('sector', 'Unknown')
                    self.sector_map[ticker] = sector
                except Exception as e:
                    logger.warning(f"Could not fetch sector for {ticker}: {e}")
                    self.sector_map[ticker] = 'Unknown'

    def get_sector_breakdown(self) -> Dict[str, Dict]:
        """
        Analyze positions and metrics by sector

        Returns:
            Dict mapping sector name to analysis dict with:
            - position_count: number of positions
            - total_notional: total notional exposure
            - avg_conviction: average conviction score
            - conviction_dist: distribution of positions by conviction level
            - heat_dist: distribution by heat status
            - avg_rsi: average RSI
            - position_in_range_avg: average position in 52W range
            - top_positions: list of largest positions in sector
            - key_signals: attraction/extension signals
        """
        sector_analysis = defaultdict(lambda: {
            'positions': [],
            'tickers': [],
            'notional_values': [],
            'convictions': [],
            'heat_statuses': [],
            'rsi_values': [],
            'position_ranges': [],
            'iv_ranks': [],
        })

        # Group positions by sector
        for idx, row in self.open_positions.iterrows():
            ticker = row['ticker']
            sector = self.sector_map.get(ticker, 'Unknown')
            contracts = row['net_quantity']
            price = self.prices.get(ticker, 0)
            notional = price * contracts * 100
            metrics = self.metrics.get(ticker, {})

            sector_analysis[sector]['tickers'].append(ticker)
            sector_analysis[sector]['positions'].append(contracts)
            sector_analysis[sector]['notional_values'].append(notional)
            sector_analysis[sector]['convictions'].append(metrics.get('conviction', 5.0))
            sector_analysis[sector]['heat_statuses'].append(metrics.get('heat_status', 'YELLOW'))
            sector_analysis[sector]['rsi_values'].append(metrics.get('rsi', 50.0))
            sector_analysis[sector]['position_ranges'].append(metrics.get('position_in_52w_range', 50.0))
            iv_rank = self.iv_ranks.get(ticker, {}).get('iv_rank')
            if iv_rank is not None:
                sector_analysis[sector]['iv_ranks'].append(iv_rank)

        # Calculate sector-level metrics
        sector_summary = {}
        for sector, data in sector_analysis.items():
            if not data['tickers']:
                continue

            convictions = data['convictions']
            heat_statuses = data['heat_statuses']
            rsi_values = data['rsi_values']
            position_ranges = data['position_ranges']
            notional_values = data['notional_values']

            # Conviction distribution
            high_conv = sum(1 for c in convictions if c >= 8)
            mod_conv = sum(1 for c in convictions if 6 <= c < 8)
            low_conv = sum(1 for c in convictions if c < 6)

            # Heat distribution
            heat_dist = defaultdict(int)
            for heat in heat_statuses:
                heat_dist[heat] += 1

            # Get top positions in sector
            top_positions = sorted(
                zip(data['tickers'], data['notional_values'], data['convictions']),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]

            # Determine sector signals
            avg_conv = np.mean(convictions)
            avg_rsi = np.mean(rsi_values)
            avg_position_range = np.mean(position_ranges)
            iv_ranks = data['iv_ranks']
            avg_iv_rank = float(np.mean(iv_ranks)) if iv_ranks else None
            # IVR >= 40 is this codebase's own established "worth selling
            # premium here" threshold (see analysis/iv_rank.py's entry_signal).
            # Below that, options are cheap regardless of how the stock itself
            # is priced — a sector can be statistically oversold on PRICE
            # (Utilities, Energy) while being a poor premium-selling sector
            # because its options are structurally low-IV. This was previously
            # invisible: "BUY" meant "cheap stock," not "cheap stock AND rich
            # premium," which is what actually matters for a premium-selling
            # strategy.
            premium_rich = avg_iv_rank is not None and avg_iv_rank >= 40

            # Discriminating bands. Sector AVERAGES rarely hit conjunctive extremes,
            # so overbought/oversold (OR conditions) drive the color; conviction guards it.
            if avg_conv < 5:
                signal = "🟡 MONITOR — Low conviction across sector"
                signal_type = "CAUTION"
            elif avg_rsi >= 65 or avg_position_range >= 80:
                signal = "🔴 REDUCE — Overbought / extended"
                signal_type = "EXTENSION"
            elif avg_rsi <= 40 or avg_position_range <= 25:
                if avg_iv_rank is None:
                    signal = "🟢 BUY — Oversold / attractively valued (IV rank unavailable — premium richness unknown)"
                elif premium_rich:
                    signal = f"🟢 BUY — Oversold + rich premium (avg IVR {avg_iv_rank:.0f}, good for selling)"
                else:
                    signal = f"🟡 BUY (stock only) — Oversold but THIN premium (avg IVR {avg_iv_rank:.0f} < 40) — not attractive for CSPs/CCs"
                signal_type = "ATTRACTION"
            elif avg_conv >= 7.5 and avg_position_range < 50:
                if avg_iv_rank is None:
                    signal = "🟢 BUY — High conviction (IV rank unavailable — premium richness unknown)"
                elif premium_rich:
                    signal = f"🟢 BUY — High conviction + rich premium (avg IVR {avg_iv_rank:.0f})"
                else:
                    signal = f"🟡 BUY (stock only) — High conviction but THIN premium (avg IVR {avg_iv_rank:.0f} < 40)"
                signal_type = "ATTRACTION"
            else:
                signal = "🟡 MONITOR — Neutral positioning"
                signal_type = "NEUTRAL"

            sector_summary[sector] = {
                'position_count': len(data['tickers']),
                'total_notional': sum(notional_values),
                'avg_conviction': round(avg_conv, 2),
                'conviction_dist': {
                    'HIGH (8-10)': high_conv,
                    'MODERATE (6-8)': mod_conv,
                    'LOW (<6)': low_conv,
                },
                'heat_dist': dict(heat_dist),
                'avg_rsi': round(avg_rsi, 1),
                'avg_position_in_52w_range': round(avg_position_range, 1),
                'avg_iv_rank': round(avg_iv_rank, 1) if avg_iv_rank is not None else None,
                'top_positions': top_positions,
                'signal': signal,
                'signal_type': signal_type,
            }

        return sector_summary

    def generate_sector_analysis_report(self, sector_summary: Dict[str, Dict]) -> List[str]:
        """Generate formatted sector analysis section for reports"""
        output = []

        output.append("=" * 120)
        output.append("SECTOR ANALYSIS & ROTATION FRAMEWORK")
        output.append("=" * 120)
        output.append("")

        # Sort sectors by order for display
        ordered_sectors = [s for s in self.SECTOR_DISPLAY_ORDER if s in sector_summary]
        # Add any sectors not in the standard list
        other_sectors = [s for s in sector_summary.keys() if s not in ordered_sectors]
        ordered_sectors.extend(sorted(other_sectors))

        # Summary table
        output.append("SECTOR SNAPSHOT — Conviction & Valuation Positioning:")
        output.append("")
        output.append(f"{'Sector':<25} {'Positions':>10} {'Avg Conv':>10} {'Avg RSI':>9} {'52W %ile':>10} {'Avg IVR':>9} {'Signal':>40}")
        output.append("-" * 120)

        for sector in ordered_sectors:
            data = sector_summary[sector]
            conv = data['avg_conviction']
            rsi = data['avg_rsi']
            range_pct = data['avg_position_in_52w_range']
            ivr = data.get('avg_iv_rank')
            ivr_str = f"{ivr:.0f}" if ivr is not None else "n/a"
            signal_type = data['signal_type']

            # Shorten signal for display — BUY splits on premium richness
            # (avg IV rank >= 40) so a cheap-but-thin-premium sector like
            # Utilities/Energy doesn't read identically to a cheap-and-rich
            # one; PRICE_ONLY (no IV data) is called out rather than guessed.
            if signal_type == "ATTRACTION":
                if ivr is None:
                    signal_short = "🟢 BUY (price only)"
                elif ivr >= 40:
                    signal_short = "🟢 BUY (rich premium)"
                else:
                    signal_short = "🟡 BUY stock/THIN premium"
            elif signal_type == "EXTENSION":
                signal_short = "🔴 REDUCE"
            elif signal_type == "MIXED":
                signal_short = "🟠 HOLD"
            elif signal_type == "CAUTION":
                signal_short = "🟡 MONITOR"
            else:
                signal_short = "🟡 NEUTRAL"

            output.append(f"{sector:<25} {data['position_count']:>10} {conv:>10} {rsi:>9.1f} {range_pct:>10.1f} {ivr_str:>9} {signal_short:>40}")

        output.append("")
        output.append("Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by")
        output.append("sector) is in Section 6 — not repeated here to avoid two versions of the")
        output.append("same per-ticker/per-sector data going out of sync with each other.")
        output.append("")
        output.append("=" * 120)
        output.append("")

        return output

    def get_sector_rotation_insights(self, sector_summary: Dict[str, Dict]) -> List[str]:
        """Generate sector rotation framework insights"""
        output = []

        output.append("=" * 120)
        output.append("SECTOR ROTATION FRAMEWORK")
        output.append("=" * 120)
        output.append("")

        # Categorize sectors by signal
        buy_sectors = [s for s, d in sector_summary.items() if d['signal_type'] == 'ATTRACTION']
        hold_sectors = [s for s, d in sector_summary.items() if d['signal_type'] == 'MIXED']
        reduce_sectors = [s for s, d in sector_summary.items() if d['signal_type'] == 'EXTENSION']
        monitor_sectors = [s for s, d in sector_summary.items() if d['signal_type'] in ['CAUTION', 'NEUTRAL']]

        output.append("PRIORITY 1: BUY SIGNALS (Attractive pricing + conviction)")
        if buy_sectors:
            for sector in buy_sectors:
                data = sector_summary[sector]
                output.append(f"  ✓ {sector}: Conv {data['avg_conviction']:.1f}/10, RSI {data['avg_rsi']:.1f}, 52W %ile {data['avg_position_in_52w_range']:.1f}")
                output.append(f"    {data['signal']}")
        else:
            output.append("  (None currently)")
        output.append("")

        output.append("PRIORITY 2: HOLD SIGNALS (Conviction intact but extended)")
        if hold_sectors:
            for sector in hold_sectors:
                data = sector_summary[sector]
                output.append(f"  ⊙ {sector}: Conv {data['avg_conviction']:.1f}/10, RSI {data['avg_rsi']:.1f}, 52W %ile {data['avg_position_in_52w_range']:.1f}")
                output.append(f"    {data['signal']}")
        else:
            output.append("  (None currently)")
        output.append("")

        output.append("PRIORITY 3: REDUCE SIGNALS (Extended positioning or low conviction)")
        if reduce_sectors:
            for sector in reduce_sectors:
                data = sector_summary[sector]
                output.append(f"  ✗ {sector}: Conv {data['avg_conviction']:.1f}/10, RSI {data['avg_rsi']:.1f}, 52W %ile {data['avg_position_in_52w_range']:.1f}")
                output.append(f"    {data['signal']}")
        else:
            output.append("  (None currently)")
        output.append("")

        output.append("PRIORITY 4: MONITOR SIGNALS (Neutral or low conviction)")
        if monitor_sectors:
            for sector in monitor_sectors:
                data = sector_summary[sector]
                output.append(f"  ◇ {sector}: Conv {data['avg_conviction']:.1f}/10, RSI {data['avg_rsi']:.1f}, 52W %ile {data['avg_position_in_52w_range']:.1f}")
                output.append(f"    {data['signal']}")
        else:
            output.append("  (None currently)")
        output.append("")

        output.append("=" * 120)
        output.append("")

        return output


def batch_get_sector_analysis(open_positions: pd.DataFrame, metrics: Dict, prices: Dict, iv_ranks: Dict = None) -> Tuple[Dict, List[str], List[str], Dict[str, str]]:
    """
    Generate sector analysis for unified reports

    Args:
        iv_ranks: optional Dict[ticker] -> {iv_rank, ...} from analysis.iv_rank.batch_iv_rank,
            used to split BUY signals into rich-premium vs thin-premium. Omit to
            keep the prior price-only signal behavior.

    Returns:
        (sector_summary, sector_analysis_section, sector_rotation_section, ticker_to_sector_map)
    """
    analyzer = SectorAnalyzer(open_positions, metrics, prices, iv_ranks)
    sector_summary = analyzer.get_sector_breakdown()
    analysis_section = analyzer.generate_sector_analysis_report(sector_summary)
    rotation_section = analyzer.get_sector_rotation_insights(sector_summary)

    return sector_summary, analysis_section, rotation_section, analyzer.sector_map
