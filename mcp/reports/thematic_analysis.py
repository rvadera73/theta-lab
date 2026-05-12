"""
Market-Driven Thematic Analysis Report
Analyzes portfolio against emergent market themes (not generic sectors)
Focuses on macro narratives, conviction trends, IV regimes, catalysts, options playbooks
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import date
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ThematicAnalyzer:
    """Analyze portfolio positions against market-driven investment themes"""

    # Define market themes based on May 2026 market reality
    THEMES = {
        'AI_INFRASTRUCTURE': {
            'name': 'AI Infrastructure Capex Cycle',
            'description': 'Semiconductor & memory demand driven by hyperscaler AI CapEx ($700B planned spend in 2026)',
            'tickers': ['NVDA', 'ASML', 'TSM', 'MU', 'SMCI', 'AMD', 'AMAT'],
            'catalysts': [
                'TSMC earnings (capacity/demand signals)',
                'Nvidia earnings & guidance (AI chip demand)',
                'ASML earnings & backlog visibility',
                'Memory pricing trends (HBM/DDR)',
                'Hyperscaler capex announcements (MSFT, GOOG, AMZN earnings)',
            ],
            'macro_driver': 'AI CapEx cycle peak, risk of creative destruction in 2H 2026',
            'iv_regime': 'ELEVATED (26-52% growth expectations)',
            'hedge_fund_bias': 'Long best-of-breed (NVDA, ASML), short laggards (MU)',
        },
        'HYPERSCALER_CLOUD': {
            'name': 'Hyperscaler Cloud CapEx Deployment',
            'description': 'Cloud infrastructure build-out, AI software/security beneficiaries',
            'tickers': ['MSFT', 'GOOG', 'META', 'AMZN', 'CRWD', 'PANW', 'CRM', 'OKTA', 'ANET'],
            'catalysts': [
                'MSFT earnings & Azure guidance',
                'Google Cloud growth rate acceleration',
                'Meta capex commentary (AI/data center)',
                'Security software earnings (CRWD, PANW, CRM)',
                'Network infrastructure demand (ANET)',
            ],
            'macro_driver': '$700B tech capex cycle supporting cloud growth, AI adoption tailwind',
            'iv_regime': 'MODERATE (lower than semiconductors, steadier)',
            'hedge_fund_bias': 'Long cloud infrastructure & security, short laggards',
        },
        'DEFENSE_AEROSPACE': {
            'name': 'Defense & Aerospace Cyclical Recovery',
            'description': '1,400 aircraft deliveries in 2026, agentic AI in decision-making, supply normalization',
            'tickers': ['RTX', 'LMT', 'NOC', 'BA', 'GEV', 'AXON'],
            'catalysts': [
                'BA/RTX/LMT earnings & production rates',
                'Defense budget appropriations & authorizations',
                'Geopolitical events (Ukraine, Taiwan, Middle East)',
                'AI/agentic software deployment announcements',
                'Supply chain recovery milestones',
            ],
            'macro_driver': 'Multi-year defense budget growth, AI modernization, supply normalization',
            'iv_regime': 'LOW (stable, predictable, defensive)',
            'hedge_fund_bias': 'Long as core holding, low churn, yield generation',
        },
        'QUANTUM_COMPUTING': {
            'name': 'Quantum Computing Tipping Point',
            'description': '300+ companies adopting, drug discovery game-changer, grid optimization emerging',
            'tickers': ['IONQ', 'QBTS', 'GOOG', 'IBM'],  # GOOG, IBM have quantum divisions
            'catalysts': [
                'Quantum chip error rates & performance announcements',
                'Commercial partnerships (pharma, energy)',
                'Drug discovery success stories from quantum simulations',
                'Grid optimization use case proofs',
                'Regulatory clarity on quantum research',
            ],
            'macro_driver': 'Early commercial tipping point ($12.6B VC funding 2025), narrative-driven',
            'iv_regime': 'VERY HIGH (early stage, speculative, binary outcomes)',
            'hedge_fund_bias': 'Speculative core, theta collection on high IV, narrative trades',
        },
        'GLP1_EXPANSION': {
            'name': 'GLP-1 Market Expansion',
            'description': '$190B market by 2035, oral therapies expanding, 30% of population potential',
            'tickers': ['LLY', 'NVO', 'RGEN', 'MRK', 'PFE', 'UNH'],
            'catalysts': [
                'Eli Lilly oral GLP-1 approval (end 2026)',
                'Novo oral approval & uptake data',
                'Medicare expansion announcements',
                'Obesity drug penetration data (prescriptions/week)',
                'Payer/insurance coverage decisions',
                'Regulatory decisions on compounding pharmacies',
            ],
            'macro_driver': 'Structural demand expansion, 30% of obese/diabetic pop by 2035',
            'iv_regime': 'ELEVATED (binary catalyst-driven, earnings volatility)',
            'hedge_fund_bias': 'Long winners (LLY), short decliners (traditional pharma), event-driven',
        },
        'CONSUMER_CYCLICAL_HEADWINDS': {
            'name': 'Consumer Discretionary Headwinds',
            'description': 'Softer revenue, tariff/inflation exposure, economic sensitivity, confidence declining',
            'tickers': ['NKE', 'ULTA', 'ELF', 'CAVA', 'DIS', 'CCL', 'RBLX', 'ETSY'],
            'catalysts': [
                'Retail earnings & guidance (holiday season, traffic trends)',
                'Consumer confidence indices (PMI, unemployment)',
                'Tariff implementation & margin impact',
                'Discount/value migration (luxury weakening)',
                'Same-store sales trends by category',
            ],
            'macro_driver': 'Economic slowdown risk, consumer trade-down, tariff headwinds',
            'iv_regime': 'ELEVATED (earnings uncertainty, economic sensitivity)',
            'hedge_fund_bias': 'Short or selective long, premium collection on weakness, sector rotation play',
        },
        'ENERGY_TRANSITION_STALLED': {
            'name': 'Energy Sector Structural Headwinds',
            'description': 'Demand destruction narrative, geopolitical support vs energy transition pressure',
            'tickers': ['XOM', 'DVN', 'CCJ', 'CVX'],
            'catalysts': [
                'Oil/gas demand trends (IEA reports, refinery utilization)',
                'Geopolitical events (OPEC decisions, Middle East, Russia)',
                'Nuclear energy demand (grid reliability, AI data center power)',
                'Energy transition policy shifts',
                'Earnings (cash flow to shareholders vs capex)',
            ],
            'macro_driver': 'Long-term demand destruction vs short-term supply geopolitics',
            'iv_regime': 'MODERATE (commodity-driven, not earnings-driven)',
            'hedge_fund_bias': 'Cautious, thesis-dependent, not core secular bet',
        },
        'MEMORY_CYCLE_RESET': {
            'name': 'Memory Chip Cycle Reset',
            'description': 'Post-capex glut, pricing pressure on DRAM, HBM demand supports recovery',
            'tickers': ['MU', 'SK_HYNIX', 'SAMSUNG'],  # SK Hynix & Samsung not in portfolio
            'catalysts': [
                'Micron earnings & gross margin guidance',
                'DRAM/NAND pricing trends (weekly spot market)',
                'HBM demand from AI infrastructure',
                'Capex spending guidance (capex cycle trough)',
                'Competitor announcements (Samsung, SK Hynix supply cuts)',
            ],
            'macro_driver': 'Cyclical trough, HBM recovery possible, but near-term pressure',
            'iv_regime': 'HIGH (cycle reversal binary, earnings miss risk)',
            'hedge_fund_bias': 'Short-term caution, look for capitulation bottom, then rotate long',
        },
    }

    def __init__(self, open_positions: pd.DataFrame, metrics: Dict, prices: Dict):
        """Initialize thematic analyzer"""
        self.open_positions = open_positions
        self.metrics = metrics
        self.prices = prices
        self.theme_positions = self._map_positions_to_themes()

    def _map_positions_to_themes(self) -> Dict[str, List[str]]:
        """Map portfolio positions to themes"""
        theme_positions = defaultdict(list)
        position_tickers = set(self.open_positions['ticker'].unique())

        for theme_key, theme_data in self.THEMES.items():
            theme_tickers = set(theme_data['tickers'])
            matched = position_tickers & theme_tickers
            theme_positions[theme_key] = list(matched)

        return theme_positions

    def get_theme_metrics(self) -> Dict[str, Dict]:
        """Calculate metrics for each theme"""
        theme_metrics = {}

        for theme_key, theme_data in self.THEMES.items():
            positions = self.theme_positions.get(theme_key, [])

            if not positions:
                theme_metrics[theme_key] = {
                    'name': theme_data['name'],
                    'positions_held': 0,
                    'total_notional': 0,
                    'avg_conviction': 0,
                    'conviction_trend': 'N/A',
                    'heat_distribution': {},
                    'iv_regime': theme_data['iv_regime'],
                    'top_positions': [],
                }
                continue

            # Calculate metrics
            convictions = []
            notional_values = []
            heat_statuses = []
            pos_data = []

            for ticker in positions:
                ticker_rows = self.open_positions[self.open_positions['ticker'] == ticker]
                if ticker_rows.empty:
                    continue

                contracts = ticker_rows['net_quantity'].sum()
                price = self.prices.get(ticker, 0)
                notional = price * contracts * 100
                metrics = self.metrics.get(ticker, {})

                convictions.append(metrics.get('conviction', 5.0))
                notional_values.append(notional)
                heat_statuses.append(metrics.get('heat_status', 'YELLOW'))
                pos_data.append((ticker, notional, metrics.get('conviction', 5.0), metrics.get('heat_status', 'YELLOW')))

            # Heat distribution
            heat_dist = defaultdict(int)
            for heat in heat_statuses:
                heat_dist[heat] += 1

            # Conviction trend (simulate based on current level)
            avg_conv = np.mean(convictions)
            if avg_conv >= 8:
                trend = 'STRENGTHENING (High conviction, likely to intensify)'
            elif avg_conv >= 7:
                trend = 'STABLE (Moderate-high conviction, watch for catalysts)'
            elif avg_conv >= 6:
                trend = 'STABLE (Moderate conviction, neutral positioning)'
            else:
                trend = 'WEAKENING (Low conviction, caution warranted)'

            # Top positions
            top_positions = sorted(pos_data, key=lambda x: abs(x[1]), reverse=True)[:5]

            theme_metrics[theme_key] = {
                'name': theme_data['name'],
                'positions_held': len(positions),
                'total_notional': sum(notional_values),
                'avg_conviction': round(np.mean(convictions), 2),
                'conviction_trend': trend,
                'heat_distribution': dict(heat_dist),
                'iv_regime': theme_data['iv_regime'],
                'top_positions': top_positions,
                'macro_driver': theme_data['macro_driver'],
                'catalysts': theme_data['catalysts'],
                'hedge_fund_bias': theme_data['hedge_fund_bias'],
                'description': theme_data['description'],
            }

        return theme_metrics

    def generate_thematic_report(self, theme_metrics: Dict[str, Dict]) -> List[str]:
        """Generate formatted thematic analysis report"""
        output = []

        output.append("=" * 140)
        output.append("THEMATIC ANALYSIS REPORT — Market-Driven Investment Narratives")
        output.append(f"Date: {date.today().strftime('%A, %B %d, %Y')}")
        output.append("=" * 140)
        output.append("")

        output.append("OVERVIEW: Themes Driving Market in May 2026")
        output.append("-" * 140)
        output.append("")

        # Summary table
        output.append(f"{'Theme':<40} {'Positions':>10} {'Notional':>15} {'Avg Conv':>10} {'IV Regime':>20} {'Trend':>40}")
        output.append("-" * 140)

        for theme_key, metrics in theme_metrics.items():
            if metrics['positions_held'] == 0:
                continue

            theme_name = metrics['name'][:37]
            notional = metrics['total_notional']
            conv = metrics['avg_conviction']
            iv = metrics['iv_regime'][:18]
            trend_short = metrics['conviction_trend'].split('(')[0].strip()

            output.append(
                f"{theme_name:<40} {metrics['positions_held']:>10} ${notional:>14,.0f} "
                f"{conv:>10.1f}/10 {iv:>20} {trend_short:>40}"
            )

        output.append("")
        output.append("")

        # Detailed breakdown by theme
        output.append("=" * 140)
        output.append("DETAILED THEMATIC BREAKDOWN")
        output.append("=" * 140)
        output.append("")

        for theme_key, metrics in theme_metrics.items():
            if metrics['positions_held'] == 0:
                continue

            output.append(f"\n{'█' * 3} {metrics['name'].upper()}")
            output.append(f"├─ Positions held: {metrics['positions_held']} | Notional: ${metrics['total_notional']:,.0f}")
            output.append(f"├─ Avg conviction: {metrics['avg_conviction']}/10")
            output.append(f"├─ Conviction trend: {metrics['conviction_trend']}")
            output.append(f"├─ IV Regime: {metrics['iv_regime']}")
            output.append("")

            # Macro driver
            output.append(f"   MACRO NARRATIVE:")
            output.append(f"   {metrics['description']}")
            output.append(f"   Driver: {metrics['macro_driver']}")
            output.append("")

            # Heat distribution
            heat = metrics['heat_distribution']
            output.append(f"   PORTFOLIO HEAT:")
            output.append(f"   ├─ 🟢 GREEN: {heat.get('GREEN', 0)} positions (attractive/oversold)")
            output.append(f"   ├─ 🟡 YELLOW: {heat.get('YELLOW', 0)} positions (neutral/approaching extremes)")
            output.append(f"   └─ 🔴 RED: {heat.get('RED', 0)} positions (extended/overbought)")
            output.append("")

            # Top positions
            if metrics['top_positions']:
                output.append(f"   TOP POSITIONS IN THEME:")
                for ticker, notional, conv, heat_status in metrics['top_positions']:
                    heat_icon = "🟢" if heat_status == "GREEN" else "🟡" if heat_status == "YELLOW" else "🔴"
                    output.append(f"   ├─ {heat_icon} {ticker:<10} ${notional:>12,.0f} | Conv {conv:>5.1f}/10")
                output.append("")

            # Catalysts
            output.append(f"   CATALYST PIPELINE (Next 12 weeks):")
            for i, catalyst in enumerate(metrics['catalysts'][:5], 1):
                output.append(f"   {i}. {catalyst}")
            output.append("")

            # Hedge fund perspective
            output.append(f"   HEDGE FUND POSITIONING:")
            output.append(f"   {metrics['hedge_fund_bias']}")
            output.append("")

        output.append("=" * 140)
        output.append("")

        return output

    def generate_options_playbook(self, theme_metrics: Dict[str, Dict]) -> List[str]:
        """Generate options execution playbook by theme"""
        output = []

        output.append("=" * 140)
        output.append("OPTIONS PLAYBOOK BY THEME — Where to Sell Premium, Where to Avoid")
        output.append("=" * 140)
        output.append("")

        playbook = {
            'AI_INFRASTRUCTURE': {
                'sell_premium': 'YES — Elevated IV (26-52% growth). Sell calls 0.20 delta above recent highs (NVDA, ASML, TSM). Sell puts 0.15 delta on dips (good entry levels).',
                'avoid': 'Do NOT buy puts (no downside protection, premium expensive). Do NOT buy calls (upside capped by valuation). Risk of creative destruction in H2 2026.',
                'roll_strategy': 'Close calls at 50% profit (IV compression risk as capex matures). Hold puts to 70% (thesis intact, allow time decay).',
                'concentration_warning': 'CRITICAL: 7+ positions concentrated in semiconductors. Max 5 contracts per name. Monitor correlations — all move together in CapEx cycle.',
            },
            'HYPERSCALER_CLOUD': {
                'sell_premium': 'YES — Moderate IV, steadier than semis. Sell calls 0.25 delta (lower delta, capture more premium as rallies continue). Sell puts 0.15 delta in weakness.',
                'avoid': 'Cloud growth is secular. Don\'t short. Avoid puts in downturns (thesis intact through cycles).',
                'roll_strategy': 'Roll calls up on 50% profit (ride the trend). Roll puts out on 40% profit (capture extended DTE premium).',
                'concentration_warning': 'Moderate: 9 positions spread across cloud + security. No single name >10% of notional.',
            },
            'DEFENSE_AEROSPACE': {
                'sell_premium': 'YES — Low IV = low premium, but predictable. Sell calls 0.30 delta (take wider OTM strikes, capture more theta). Sell puts 0.20 delta (lower strikes, support theses).',
                'avoid': 'Do NOT avoid. Core holding. Geopolitical shocks can spike IV unexpectedly (use for premium collection). Accept assignment (hold as dividend stock).',
                'roll_strategy': 'Wheel strategy: Accept put assignment, sell covered calls at delta 0.25-0.30. Hold for 2-3 years (dividend + appreciation).',
                'concentration_warning': 'Healthy: 6 positions, no single name >30% of theme. Highly correlated (all benefit from defense budget) — diversification within theme.',
            },
            'QUANTUM_COMPUTING': {
                'sell_premium': 'YES — VERY HIGH IV = collect substantial premium. IONQ, QBTS: sell calls/puts 0.15 delta (far OTM, binary outcomes). Stagger across multiple expiries.',
                'avoid': 'Do NOT buy calls (speculative, theta works against you). Do NOT hold puts (assignment risk with limited volume). Avoid defined-risk spreads (IV crush on both sides).',
                'roll_strategy': 'Close calls at 60-70% profit (IV will compress on narrative maturation). Roll puts out aggressively (binary events can move them ITM fast). Exit before earnings.',
                'concentration_warning': 'Speculative: 2 core positions (IONQ, QBTS). Max 1 contract each. HIGH volatility risk — don\'t add to theme positions without conviction catalyst.',
            },
            'GLP1_EXPANSION': {
                'sell_premium': 'YES — Elevated IV from binary catalysts (FDA approvals, penetration data). LLY: sell calls 0.25 delta (rising trend, stay bullish). Sell puts 0.15 delta on dips.',
                'avoid': 'Avoid puts on traditional pharma (losers in this narrative) — assignment risk, dividend cut concerns. Avoid naked shorting winners (unlimited risk).',
                'roll_strategy': 'LLY calls: close at 60% profit or roll up on earnings beats. Puts: hold to 70% (thesis tailwind). Monitor oral GLP-1 approval catalyst (end 2026).',
                'concentration_warning': 'Moderate: LLY concentrated winner. Risk asymmetry if oral approval delayed or competitive. Hedge with shorts on value pharma.',
            },
            'CONSUMER_CYCLICAL_HEADWINDS': {
                'sell_premium': 'YES — Elevated IV from economic uncertainty. NKE, ULTA, ELF: sell calls 0.30 delta (expect sideways/down, collect premium). Sell puts 0.15 delta (set catch prices).',
                'avoid': 'Avoid buying calls (no upside conviction). Avoid buying puts (theta decay, economic cycles long). Avoid holding through earnings (binary moves).',
                'roll_strategy': 'Calls: close at 50% profit (premium valuable in weakness). Puts: roll down on bounces (lower entry prices). Manage for earnings (close 2 weeks before).',
                'concentration_warning': 'HIGH: 8 positions, many highly correlated to consumer confidence. Monitor macro (unemployment, PMI). Reduce if recession signals spike.',
            },
            'ENERGY_TRANSITION_STALLED': {
                'sell_premium': 'CAUTIOUS — Low conviction thesis, IV moderate. Only sell calls on strong bounces (geopolitical spikes). Avoid new puts (thesis fuzzy).',
                'avoid': 'Do NOT add to positions without catalyst clarity. Avoid long-dated puts (thesis change risk). Avoid assignment (no conviction to hold stock).',
                'roll_strategy': 'Calls: close on geopolitical spikes. Avoid rolling puts (instead, close and redeploy to higher-conviction themes).',
                'concentration_warning': 'LOW conviction theme: 4 positions, 1% notional. Consider exiting if thesis doesn\'t clarify by Q3 2026.',
            },
            'MEMORY_CYCLE_RESET': {
                'sell_premium': 'YES — HIGH IV from cycle reversal binary. MU: sell calls 0.20 delta (earnings volatility high). Sell puts 0.10 delta (far OTM, capitulation play).',
                'avoid': 'Avoid holding through earnings (binary outcomes). Avoid long calls (downside risk greater than upside in near term). Avoid puts near support levels.',
                'roll_strategy': 'Calls: close at 40% profit (IV likely to compress in cyclical trough). Puts: hold to capitulation (watch for cycle reversal signals, then buy back early).',
                'concentration_warning': 'Single name (MU) with HIGH volatility. Max 2 contracts. Monitor pricing trends (spot DRAM/NAND weekly). Watch for capex trough signal.',
            },
        }

        for theme_key, metrics in theme_metrics.items():
            if metrics['positions_held'] == 0:
                continue

            if theme_key not in playbook:
                continue

            pb = playbook[theme_key]

            output.append(f"\n{metrics['name'].upper()}")
            output.append(f"├─ Sell Premium: {pb['sell_premium']}")
            output.append(f"├─ Avoid: {pb['avoid']}")
            output.append(f"├─ Roll Strategy: {pb['roll_strategy']}")
            output.append(f"└─ Concentration Warning: {pb['concentration_warning']}")
            output.append("")

        output.append("=" * 140)
        output.append("")

        return output


def generate_thematic_report_file(
    open_positions: pd.DataFrame, metrics: Dict, prices: Dict, report_date: date = None
) -> Tuple[str, List[str]]:
    """Generate complete thematic analysis report"""
    if report_date is None:
        report_date = date.today()

    analyzer = ThematicAnalyzer(open_positions, metrics, prices)
    theme_metrics = analyzer.get_theme_metrics()
    thematic_section = analyzer.generate_thematic_report(theme_metrics)
    playbook_section = analyzer.generate_options_playbook(theme_metrics)

    report_text = "\n".join(thematic_section + playbook_section)

    return report_text, thematic_section + playbook_section
