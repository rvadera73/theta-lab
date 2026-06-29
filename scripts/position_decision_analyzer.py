"""
Position-Level Decision Analysis

Analyzes each position and recommends:
- CLOSE NOW (take profit or risk reduction)
- ROLL NOW (extend thesis, collect credit)
- HOLD (conviction intact, no action)
- ENTER NEW (new opportunities)

Includes P&L impact and 5-day theta potential.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import date, timedelta


class PositionDecisionAnalyzer:
    """Analyze positions and generate actionable decisions"""

    def __init__(self, positions_df: pd.DataFrame, metrics: Dict, prices: Dict = None):
        self.positions = positions_df
        self.metrics = metrics
        self.prices = prices or {}
        self.decisions = {
            'close': [],
            'roll': [],
            'hold': [],
            'enter': []
        }

    def analyze_all_positions(self) -> Dict:
        """Analyze all positions and categorize by decision"""

        close_decisions = []
        roll_decisions = []
        hold_decisions = []
        entry_decisions = []

        for idx, position in self.positions.iterrows():
            ticker = position.get('ticker', 'UNKNOWN')
            if not ticker:
                continue

            metric = self.metrics.get(ticker, {})

            # Get decision for this position
            decision = self._decide_position_action(position, metric)

            # Add to appropriate category
            if decision['action'] == 'CLOSE':
                close_decisions.append(decision)
            elif decision['action'] == 'ROLL':
                roll_decisions.append(decision)
            elif decision['action'] == 'HOLD':
                hold_decisions.append(decision)

        # Identify SCALE opportunities (existing high-conviction positions worth adding to)
        for idx, position in self.positions.iterrows():
            ticker = position.get('ticker', 'UNKNOWN')
            if not ticker:
                continue

            metric = self.metrics.get(ticker, {})
            conviction = metric.get('conviction', 0)

            # Only consider positions with VERY high conviction (8+) for scaling
            if conviction >= 8.0:
                # Check if it's GREEN (attractive) or hasn't hit profit targets yet
                heat = metric.get('heat_status', 'GREEN')
                pnl_pct = metric.get('pnl_pct', 0)

                # Scale if GREEN heat or underwater (negative P&L, adding at lower cost avg)
                if heat == 'GREEN' or pnl_pct < 0.05:  # Less than 5% profit
                    scale_entry = self._create_scale_opportunity(ticker, metric, position)
                    if scale_entry:
                        entry_decisions.append(scale_entry)

        # Also identify new entry opportunities (tickers not held yet)
        existing_tickers = set(self.positions['ticker'].dropna().unique())
        for ticker, metric in self.metrics.items():
            if ticker in existing_tickers:
                continue

            if metric.get('conviction', 0) >= 8.0:
                entry = self._create_entry_opportunity(ticker, metric)
                if entry:
                    entry_decisions.append(entry)

        # Sort by priority within each category
        close_decisions.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        roll_decisions.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        hold_decisions.sort(key=lambda x: x.get('conviction', 0), reverse=True)
        entry_decisions.sort(key=lambda x: x.get('premium_potential', 0), reverse=True)

        self.decisions['close'] = close_decisions
        self.decisions['roll'] = roll_decisions
        self.decisions['hold'] = hold_decisions
        self.decisions['enter'] = entry_decisions

        return self.decisions

    def _decide_position_action(self, position: pd.Series, metric: Dict) -> Dict:
        """Decide action for a single position"""

        ticker = position.get('ticker')
        dte = position.get('dte', 45)
        conviction = metric.get('conviction', 5.0)
        heat = metric.get('heat_status', 'GREEN')
        rsi = metric.get('rsi', 50)

        # Get actual P&L from consolidated position data
        pnl = metric.get('pnl', metric.get('option_pnl', 0))
        pnl_pct = metric.get('pnl_pct', metric.get('option_pnl_pct', 0))

        max_premium = metric.get('max_premium', metric.get('collected_premium', 1000))
        daily_theta = metric.get('daily_theta', metric.get('theta', 10))

        # Calculate 5-day theta potential
        theta_5day = daily_theta * 5
        theta_5day_with_decay = daily_theta * 5 * 0.8  # Theta accelerates

        # Decision scoring
        close_score = 0
        roll_score = 0

        # Close signals
        if conviction < 5:
            close_score += 10
        if heat == 'RED':
            close_score += 8
        if rsi > 75:  # Overbought
            close_score += 6
        if dte < 21:
            close_score += 4
        if pnl_pct > 0.40:  # 40%+ profit, declining theta
            close_score += 5
        if dte < 14 and pnl > 0:  # Short DTE with profit
            close_score += 4

        # Roll signals
        if conviction >= 7 and dte < 30:
            roll_score += 10
        if heat == 'YELLOW' and conviction >= 6:
            roll_score += 6
        if dte < 14 and conviction >= 7:
            roll_score += 8  # Rolling better than closing

        # Determine action
        if close_score > roll_score and close_score >= 10:
            action = 'CLOSE'
            priority = close_score
            reason_list = self._close_reasons(position, metric, conviction, heat, rsi, dte, pnl_pct)
        elif roll_score >= 10:
            action = 'ROLL'
            priority = roll_score
            reason_list = self._roll_reasons(position, metric, conviction, dte)
        else:
            action = 'HOLD'
            priority = conviction
            reason_list = ['Conviction adequate', 'Heat manageable', 'DTE allows thesis to play out']

        # Calculate P&L impact if action taken
        current_pnl = pnl
        if action == 'CLOSE':
            future_pnl_5day = pnl  # Closing now, no future
            future_pnl_10day = pnl
        else:
            future_pnl_5day = pnl + theta_5day_with_decay
            future_pnl_10day = pnl + (daily_theta * 10 * 0.7)

        return {
            'ticker': ticker,
            'action': action,
            'priority_score': priority,
            'current_pnl': round(current_pnl, 0),
            'pnl_pct': round(pnl_pct * 100, 1),
            'pct_of_max_premium': round(pnl_pct * 100, 1),
            'theta_5day': round(theta_5day_with_decay, 0),
            'expected_pnl_5day': round(future_pnl_5day, 0),
            'expected_pnl_10day': round(future_pnl_10day, 0),
            'dte': int(dte),
            'conviction': round(conviction, 1),
            'heat': heat,
            'rsi': round(rsi, 1),
            'reasons': reason_list,
            'decision_score': {
                'close': close_score,
                'roll': roll_score,
                'hold': 20 - (close_score + roll_score)  # Residual
            }
        }

    def _close_reasons(self, position, metric, conviction, heat, rsi, dte, pnl_pct) -> List[str]:
        """Generate reasons for CLOSE recommendation"""
        reasons = []

        if conviction < 5:
            reasons.append(f"Conviction {conviction:.1f}/10 below threshold")
        if heat == 'RED':
            reasons.append("Position at RED heat status")
        if rsi > 75:
            reasons.append(f"RSI {rsi:.1f} (overbought, reversal risk)")
        if dte < 21:
            reasons.append(f"Short DTE ({dte} days, gamma risk increasing)")
        if pnl_pct > 0.40:
            reasons.append(f"Profit {pnl_pct*100:.0f}% captured, theta accelerating decay")

        return reasons if reasons else ["Strategic profit-taking"]

    def _roll_reasons(self, position, metric, conviction, dte) -> List[str]:
        """Generate reasons for ROLL recommendation"""
        reasons = []

        if conviction >= 7:
            reasons.append(f"Conviction {conviction:.1f}/10 supports extension")
        if dte < 30:
            reasons.append(f"Approaching assignment risk ({dte} days)")
        if dte < 14:
            reasons.append("Rolling better than closing (preserve thesis)")

        return reasons if reasons else ["Extend thesis, collect more premium"]

    def _create_scale_opportunity(self, ticker: str, metric: Dict, position: pd.Series) -> Dict:
        """Create SCALE recommendation for existing high-conviction positions"""

        conviction = metric.get('conviction', 5.0)
        heat = metric.get('heat_status', 'GREEN')
        rsi = metric.get('rsi', 50)
        current_price = metric.get('price', 100)
        contracts = position.get('net_quantity', 1)
        pnl = metric.get('pnl', 0)
        pnl_pct = metric.get('pnl_pct', 0)

        # Scale signals
        reasons = []

        if heat == 'GREEN':
            reasons.append(f"Technically attractive (GREEN) at {rsi:.0f} RSI")

        if pnl_pct < 0.05:  # Less than 5% profit
            reasons.append(f"Still building position ({contracts} contracts, {pnl_pct*100:+.1f}% P&L)")

        if conviction >= 8.5:
            reasons.append(f"Very high conviction {conviction:.1f}/10 — core thesis")

        if not reasons:
            return None

        # Estimate additional scale parameters
        estimated_strike = round(current_price * 0.90, 2)  # 10% below current
        estimated_dte = 40
        estimated_premium_pct = 0.02  # Conservative 2% for scaling
        estimated_credit = round(estimated_strike * estimated_premium_pct, 2)

        return {
            'ticker': ticker,
            'action': 'SCALE',
            'conviction': round(conviction, 1),
            'heat': heat,
            'rsi': round(rsi, 1),
            'current_contracts': int(contracts),
            'entry_type': 'SCALE (Add to position)',
            'suggested_strike': estimated_strike,
            'suggested_dte': estimated_dte,
            'estimated_credit': estimated_credit,
            'estimated_premium_pct': round(estimated_premium_pct * 100, 2),
            'premium_potential': estimated_credit,
            'priority_score': int(conviction * 10),
            'reasons': reasons,
            'entry_score': int(conviction * 10)
        }

    def _create_entry_opportunity(self, ticker: str, metric: Dict) -> Dict:
        """Create entry recommendation for new position"""

        conviction = metric.get('conviction', 5.0)
        heat = metric.get('heat_status', 'GREEN')
        rsi = metric.get('rsi', 50)
        iv_rank = metric.get('iv_rank', 50)
        current_price = metric.get('price', 100)

        # Entry signals
        entry_score = 0
        reasons = []

        # High conviction
        if conviction >= 8:
            entry_score += 10
            reasons.append(f"High conviction {conviction:.1f}/10")

        # Green heat (attractive)
        if heat == 'GREEN':
            entry_score += 5
            reasons.append("Technically attractive (GREEN)")

        # Oversold RSI
        if rsi < 35:
            entry_score += 5
            reasons.append(f"Oversold (RSI {rsi:.1f})")

        # Elevated IV for premium
        if iv_rank > 50:
            entry_score += 5
            reasons.append(f"Elevated IV ({iv_rank:.0f}) → fat premium")

        if entry_score < 8:
            return None

        # Estimate entry parameters
        # CSP (Cash Secured Put): 30-45 DTE, delta ~0.20 (80% PoP)
        # Target: 1-3% monthly premium
        estimated_strike = round(current_price * 0.90, 2)  # 10% below current
        estimated_dte = 40  # 40 DTE optimal
        estimated_premium_pct = (iv_rank / 100.0) * 0.03  # 3% at high IV, scaled
        estimated_credit = round(estimated_strike * estimated_premium_pct, 2)

        return {
            'ticker': ticker,
            'action': 'ENTER',
            'conviction': round(conviction, 1),
            'heat': heat,
            'rsi': round(rsi, 1),
            'entry_type': 'CSP (Cash-Secured Put)',
            'suggested_strike': estimated_strike,
            'suggested_dte': estimated_dte,
            'estimated_credit': estimated_credit,
            'estimated_premium_pct': round(estimated_premium_pct * 100, 2),
            'premium_potential': estimated_credit,
            'priority_score': entry_score,
            'reasons': reasons,
            'entry_score': entry_score
        }

    def summarize_decisions(self) -> Dict:
        """Create summary of all decisions"""
        return {
            'close_count': len(self.decisions['close']),
            'close_total_pnl': sum(d.get('current_pnl', 0) for d in self.decisions['close']),
            'close_freed_margin': len(self.decisions['close']) * 30000,  # Approximate
            'roll_count': len(self.decisions['roll']),
            'roll_total_credit': sum(d.get('theta_5day', 0) / 5 * 2 for d in self.decisions['roll']),  # Rough credit estimate
            'hold_count': len(self.decisions['hold']),
            'hold_avg_conviction': np.mean([d.get('conviction', 0) for d in self.decisions['hold']]) if self.decisions['hold'] else 0
        }

    def get_top_decisions(self, n: int = 5, action: str = 'close') -> List[Dict]:
        """Get top N decisions by priority"""
        decisions = self.decisions.get(action, [])
        return decisions[:n]


def analyze_position_decisions(positions_df: pd.DataFrame, metrics: Dict, prices: Dict = None) -> Dict:
    """
    Main entry point for position decision analysis.

    Returns decisions categorized by action (CLOSE, ROLL, HOLD, ENTER).
    """
    analyzer = PositionDecisionAnalyzer(positions_df, metrics, prices)
    decisions = analyzer.analyze_all_positions()
    summary = analyzer.summarize_decisions()

    return {
        'decisions': decisions,
        'summary': summary,
        'top_closes': analyzer.get_top_decisions(n=5, action='close'),
        'top_rolls': analyzer.get_top_decisions(n=5, action='roll'),
        'top_entries': analyzer.get_top_decisions(n=5, action='enter'),
        'analyzer': analyzer  # For further analysis if needed
    }
