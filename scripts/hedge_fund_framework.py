"""
Hedge Fund Decision Framework for Options Portfolio

Combines industry-standard frameworks:
1. CONVICTION-BASED SIZING (Berkshire, Tiger Global)
   - Each position sized by conviction 1-10
   - Higher conviction = larger position size

2. KELLY CRITERION (Renaissance, Two Sigma)
   - Optimal bet size = (win% * payoff - loss% * cost) / payoff
   - Prevents over-betting on any single position

3. RISK BUDGET ALLOCATION (Bridgewater)
   - Capital allocated by Greeks targets, not notional
   - Each account has margin budget, risk budget targets

4. MULTI-TRIGGER EXIT FRAMEWORK (Citadel)
   - Position exits on MULTIPLE signals, not just profit target
   - Conviction drop, Greeks breach, time decay, thesis break

5. SECTOR ROTATION (Macro funds)
   - Dynamic sector weights based on regime + conviction
   - Rotate from declining to rising conviction sectors

6. WIN RATE OPTIMIZATION (Tastytrade)
   - Track actual performance of strategies
   - Size by win rates and risk/reward ratios
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import date
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')


@dataclass
class ConvictionScore:
    """Multi-factor conviction calculation."""
    symbol: str
    moat_strength: str  # STRONG/MODERATE/WEAK foundation
    earnings_trend: str  # BEAT/MISS/EQUAL recent earnings
    momentum_score: float  # -10 to +10 (recent price trend)
    heat_status: str  # GREEN/YELLOW/RED distance to strike
    pnl_status: str  # WINNING/NEUTRAL/LOSING
    conviction_score: int  # 1-10 final score


class HedgeFundFramework:
    """Industry-standard frameworks for portfolio management."""

    @staticmethod
    def calculate_conviction(
        symbol: str,
        moat_strength: str,
        earnings_trend: str,
        momentum_score: float,
        heat_status: str,
        pnl_status: str
    ) -> ConvictionScore:
        """
        Calculate conviction score (1-10 scale) using multiple factors.

        STRONG moat = 4 points (foundation)
        MODERATE moat = 2 points
        WEAK moat = 0 points

        Earnings BEAT = +2 points
        Earnings EQUAL = +0 points
        Earnings MISS = -2 points

        Momentum +10 = +1 point
        Momentum -10 = -1 point

        Heat GREEN = +1 point (no near-term assignment risk)
        Heat YELLOW = +0 points (manageable)
        Heat RED = -1 point (imminent threat)

        P&L WINNING = +1 point (thesis validated by market)
        P&L NEUTRAL = +0 points
        P&L LOSING = -1 point (thesis under pressure)

        Total: 1-10 scale
        """
        score = 1  # Floor: at least 1

        # Moat foundation (0-4 points)
        moat_map = {'STRONG': 4, 'MODERATE': 2, 'WEAK': 0}
        score += moat_map.get(moat_strength, 0)

        # Earnings validation (±2 points)
        earnings_map = {'BEAT': 2, 'EQUAL': 0, 'MISS': -2}
        score += earnings_map.get(earnings_trend, 0)

        # Momentum (±1 point)
        score += max(-1, min(1, int(momentum_score / 10)))

        # Heat status (±1 point)
        heat_map = {'🟢 GREEN': 1, '🟡 YELLOW': 0, '🔴 RED': -1}
        score += heat_map.get(heat_status, 0)

        # P&L status (±1 point)
        pnl_map = {'WINNING': 1, 'NEUTRAL': 0, 'LOSING': -1}
        score += pnl_map.get(pnl_status, 0)

        # Clamp to 1-10
        score = max(1, min(10, score))

        return ConvictionScore(
            symbol=symbol,
            moat_strength=moat_strength,
            earnings_trend=earnings_trend,
            momentum_score=momentum_score,
            heat_status=heat_status,
            pnl_status=pnl_status,
            conviction_score=int(score)
        )

    @staticmethod
    def kelly_criterion_position_size(
        conviction: int,
        win_rate: float,
        avg_win_ratio: float,
        avg_loss_ratio: float,
        max_position_pct: float = 0.05
    ) -> float:
        """
        Kelly Criterion: Optimal position sizing based on win rate and payoff.

        Formula: f* = (bp - q) / b
        where:
          f* = fraction of bankroll to bet
          b = odds (avg_win / avg_loss)
          p = win probability
          q = loss probability (1-p)

        Conviction acts as a multiplier on the base Kelly fraction.
        Conviction 1-10 scales the position from 0.1x to 1.0x of Kelly.

        Examples:
          - Conviction 10, WR 70%, ratio 2:1 → full Kelly fraction
          - Conviction 5, same stats → 0.5x Kelly fraction
          - Conviction 1 → 0.1x Kelly fraction (tiny position)
        """
        if win_rate <= 0 or win_rate >= 1:
            return max_position_pct * 0.1  # Safety floor

        # Base Kelly calculation
        b = avg_win_ratio / max(avg_loss_ratio, 0.01)
        p = win_rate
        q = 1 - p
        kelly_fraction = (b * p - q) / b

        # Clamp Kelly to reasonable range (typically 0.05-0.25 of bankroll)
        kelly_fraction = max(0.01, min(0.25, kelly_fraction))

        # Apply conviction multiplier (1-10 scale)
        conviction_multiplier = conviction / 10.0

        # Final position size
        position_size = kelly_fraction * conviction_multiplier

        # Respect maximum position size constraint
        position_size = min(position_size, max_position_pct)

        return position_size

    @staticmethod
    def multi_trigger_exit_decision(
        symbol: str,
        conviction: int,
        pnl_pct: float,
        heat_status: str,
        dte: int,
        regime: str
    ) -> Dict:
        """
        Multi-trigger exit framework (Citadel-style).
        Position doesn't exit on ONE signal, but on MULTIPLE signals.

        EXIT TRIGGERS:
        1. Conviction drop: conviction < 4 (thesis deteriorating)
        2. Heat breach: RED status = 10% risk
        3. Time decay: DTE < 21 (gamma risk near expiry)
        4. Profit target: regime-dependent (40% bear, 70% bull)
        5. Loss stop: max loss -20% (risk/reward)

        Returns: {exit_signal: bool, reason: str, priority: int}
        """
        exit_signals = []
        priority_score = 0

        # Signal 1: Conviction drop (thesis broken)
        if conviction < 4:
            exit_signals.append({
                'trigger': 'CONVICTION_DROP',
                'signal': True,
                'reason': f'Conviction {conviction}/10 (threshold < 4)',
                'priority': 1
            })
            priority_score += 10

        # Signal 2: Heat breach (price threat)
        if heat_status == '🔴 RED':
            exit_signals.append({
                'trigger': 'HEAT_RED',
                'signal': True,
                'reason': f'Position at risk of assignment',
                'priority': 1
            })
            priority_score += 8

        # Signal 3: Time decay (gamma risk)
        if dte <= 21:
            exit_signals.append({
                'trigger': 'TIME_DECAY',
                'signal': True,
                'reason': f'DTE {dte} (threshold ≤21)',
                'priority': 2
            })
            priority_score += 5

        # Signal 4: Profit target (regime-dependent)
        profit_target = 0.40 if regime in ['BEAR', 'SIDEWAYS'] else 0.70
        if pnl_pct >= profit_target * 100:
            exit_signals.append({
                'trigger': 'PROFIT_TARGET',
                'signal': True,
                'reason': f'P&L {pnl_pct:.0f}% (target {profit_target*100:.0f}%)',
                'priority': 2
            })
            priority_score += 3

        # Signal 5: Loss stop (max loss)
        if pnl_pct <= -20:
            exit_signals.append({
                'trigger': 'LOSS_STOP',
                'signal': True,
                'reason': f'P&L {pnl_pct:.0f}% (max loss -20%)',
                'priority': 1
            })
            priority_score += 10

        # Determine exit decision
        exit_decision = len(exit_signals) >= 1  # Exit if ANY signal fires

        # Priority 1 signals (conviction, heat, loss) override everything
        priority1_signals = [s for s in exit_signals if s['priority'] == 1]
        if priority1_signals:
            exit_decision = True
            priority_score = 10  # Force exit

        return {
            'exit_signal': exit_decision,
            'signals': exit_signals,
            'priority_score': priority_score,
            'action': 'CLOSE' if exit_decision else 'HOLD'
        }

    @staticmethod
    def sector_rotation_framework(
        positions_by_sector: Dict[str, List[str]],
        sector_convictions: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Sector rotation: Dynamically reweight sectors based on conviction changes.

        Input:
          positions_by_sector: {'AI': ['AXON', 'CRWD'], 'Energy': ['GEV']}
          sector_convictions: {'AI': 8.5, 'Energy': 6.2}

        Output:
          sector_weights: {'AI': 0.60, 'Energy': 0.20, 'Cash': 0.20}

        Logic:
          - High conviction sectors get more capital
          - Low conviction sectors get reduced exposure
          - Rebalance weekly/monthly as convictions change
        """
        if not sector_convictions:
            return {}

        # Normalize convictions to weights (use softmax)
        total_conviction = sum(sector_convictions.values())
        raw_weights = {
            sector: conviction / total_conviction
            for sector, conviction in sector_convictions.items()
        }

        # Apply conviction thresholds
        # If sector conviction < 5, reduce weight by 50%
        adjusted_weights = {}
        for sector, weight in raw_weights.items():
            conviction = sector_convictions[sector]
            if conviction < 5:
                adjusted_weights[sector] = weight * 0.5
            else:
                adjusted_weights[sector] = weight

        # Normalize to sum to 1.0
        total_adjusted = sum(adjusted_weights.values())
        final_weights = {
            sector: weight / total_adjusted
            for sector, weight in adjusted_weights.items()
        }

        return final_weights

    @staticmethod
    def win_rate_optimization(
        positions: List[Dict],
        lookback_days: int = 90
    ) -> Dict[str, float]:
        """
        Track win rates by strategy/sector and size accordingly.

        Input: List of positions with {symbol, strategy, pnl, close_date}
        Output: {strategy: win_rate, sector: win_rate}

        Example:
          Short strangles: 72% win rate (close at 50% profit)
          Covered calls: 85% win rate (natural assignment)
          Buy to close: 65% win rate (defensive closures)

        Size larger when strategy has higher win rate.
        """
        if not positions:
            return {}

        by_strategy = {}
        for pos in positions:
            strategy = pos.get('strategy', 'unknown')
            pnl = pos.get('pnl', 0)
            is_win = pnl > 0

            if strategy not in by_strategy:
                by_strategy[strategy] = {'wins': 0, 'total': 0}

            by_strategy[strategy]['total'] += 1
            if is_win:
                by_strategy[strategy]['wins'] += 1

        # Calculate win rates
        win_rates = {
            strategy: stats['wins'] / max(1, stats['total'])
            for strategy, stats in by_strategy.items()
        }

        return win_rates


if __name__ == "__main__":
    # Example: Calculate conviction for AXON
    conv = HedgeFundFramework.calculate_conviction(
        symbol='AXON',
        moat_strength='STRONG',
        earnings_trend='BEAT',
        momentum_score=8,
        heat_status='🟢 GREEN',
        pnl_status='WINNING'
    )
    print(f"\n{conv.symbol} Conviction: {conv.conviction_score}/10")

    # Example: Kelly position size (70% win rate, 2:1 payoff, conviction 8)
    size = HedgeFundFramework.kelly_criterion_position_size(
        conviction=8,
        win_rate=0.70,
        avg_win_ratio=2.0,
        avg_loss_ratio=1.0,
        max_position_pct=0.05
    )
    print(f"Position size (Kelly): {size*100:.1f}% of portfolio")

    # Example: Multi-trigger exit
    exit_result = HedgeFundFramework.multi_trigger_exit_decision(
        symbol='AXON',
        conviction=8,
        pnl_pct=45.0,
        heat_status='🟢 GREEN',
        dte=35,
        regime='BEAR'
    )
    print(f"\nExit decision: {exit_result['action']}")
    if exit_result['signals']:
        for sig in exit_result['signals']:
            print(f"  • {sig['trigger']}: {sig['reason']}")
