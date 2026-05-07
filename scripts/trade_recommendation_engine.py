"""
Trade Recommendation Engine — Actionable Trade Execution Plan

Given current portfolio state (delta breach, gamma breach, theta gap, etc.),
recommends SPECIFIC TRADES:
- Which symbol, strike, DTE, quantity
- Expected P&L impact
- Why (how it fixes the problem)
- Execution mechanics (sell CSP, sell CC, close position, etc.)
"""

import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from data_loader import DynamicDataLoader
from greeks_calculator import GreeksCalculator


@dataclass
class TradeRecommendation:
    """A specific trade to execute."""
    priority: int  # 1=urgent, 2=this week, 3=next week
    symbol: str
    action: str  # SELL_CSP, SELL_CC, SELL_STRANGLE, BUY_TO_CLOSE, ROLL_DOWN, ROLL_UP, CLOSE
    strike: Optional[float]
    expiry: Optional[str]  # YYYY-MM-DD
    quantity: int
    expected_premium: float
    expected_delta_impact: float  # How much this reduces/increases delta
    expected_gamma_impact: float
    expected_theta_impact: float
    why: str  # Reason for this trade
    hedge_fund_context: str  # What does this do in a hedge fund portfolio?


class TradeRecommendationEngine:
    """Generate specific trades to fix portfolio breaches."""

    @staticmethod
    def calculate_dte(expiry_str: str) -> int:
        """Calculate days to expiration."""
        if isinstance(expiry_str, str):
            try:
                expiry = datetime.strptime(expiry_str, '%Y-%m-%d')
                return (expiry - datetime.now()).days
            except:
                return 0
        return 0

    @staticmethod
    def recommend_delta_fixes(
        positions_df: pd.DataFrame,
        portfolio_greeks: Dict,
        account: str
    ) -> List[TradeRecommendation]:
        """
        If portfolio delta is too high (> +20) or too low (< -20),
        recommend closing calls (reduce long) or puts (reduce short).
        """
        recommendations = []
        delta_breach = portfolio_greeks.get('delta', 0)

        if delta_breach > 20:
            # Too long - close calls
            account_calls = positions_df[
                (positions_df['symbol'].astype(str).str.contains('CALL', na=False)) &
                (positions_df['account'] == account)
            ].sort_values('delta', ascending=False)

            for idx, call in account_calls.head(3).iterrows():
                recommendations.append(TradeRecommendation(
                    priority=1,
                    symbol=call['symbol'],
                    action='CLOSE',
                    strike=call.get('strike'),
                    expiry=call.get('expiry'),
                    quantity=abs(call['qty']),
                    expected_premium=-call['mark_price'],  # debit (cost to close)
                    expected_delta_impact=-call['delta'] * call['qty'],  # Reduces long delta
                    expected_gamma_impact=-call['gamma'] * call['qty'],
                    expected_theta_impact=-call['theta'] * call['qty'],
                    why=f"Close {call['symbol']} to reduce delta from {delta_breach:.1f} to target ±20",
                    hedge_fund_context="Long call reduction = reduce net long exposure in directional rally"
                ))

        elif delta_breach < -20:
            # Too short - close puts
            account_puts = positions_df[
                (positions_df['symbol'].astype(str).str.contains('PUT', na=False)) &
                (positions_df['account'] == account)
            ].sort_values('delta', ascending=True)

            for idx, put in account_puts.head(3).iterrows():
                recommendations.append(TradeRecommendation(
                    priority=1,
                    symbol=put['symbol'],
                    action='CLOSE',
                    strike=put.get('strike'),
                    expiry=put.get('expiry'),
                    quantity=abs(put['qty']),
                    expected_premium=-put['mark_price'],
                    expected_delta_impact=-put['delta'] * put['qty'],  # Reduces short delta
                    expected_gamma_impact=-put['gamma'] * put['qty'],
                    expected_theta_impact=-put['theta'] * put['qty'],
                    why=f"Close {put['symbol']} to reduce short delta from {delta_breach:.1f} to target ±20",
                    hedge_fund_context="Short put reduction = reduce net short exposure in directional decline"
                ))

        return recommendations

    @staticmethod
    def recommend_gamma_fixes(
        positions_df: pd.DataFrame,
        portfolio_greeks: Dict,
        account: str
    ) -> List[TradeRecommendation]:
        """
        If gamma is too high (> 0.5), close strangles (both calls and puts together).
        """
        recommendations = []
        gamma_breach = portfolio_greeks.get('gamma', 0)

        if gamma_breach > 0.5:
            # Too much convexity - close strangles (close both legs)
            account_positions = positions_df[positions_df['account'] == account]

            # Find strangle pairs (same symbol, same expiry, one call + one put)
            # Close the ones with highest gamma first
            for symbol in account_positions['symbol'].unique():
                symbol_pos = account_positions[account_positions['symbol'] == symbol]
                total_gamma = symbol_pos['gamma'].sum()

                if total_gamma > 0.05:  # Significant gamma contribution
                    recommendations.append(TradeRecommendation(
                        priority=1,
                        symbol=str(symbol),
                        action='CLOSE_STRANGLE',
                        strike=None,
                        expiry=None,
                        quantity=1,
                        expected_premium=symbol_pos['mark_price'].sum(),
                        expected_delta_impact=-symbol_pos['delta'].sum(),
                        expected_gamma_impact=-total_gamma,
                        expected_theta_impact=-symbol_pos['theta'].sum(),
                        why=f"Close strangle to reduce gamma from {gamma_breach:.3f} to target ≤0.5",
                        hedge_fund_context="Strangle reduction = reduce convexity risk (protection from large moves) to focus on theta decay"
                    ))

        return recommendations

    @staticmethod
    def recommend_theta_additions(
        positions_df: pd.DataFrame,
        portfolio_greeks: Dict,
        account: str
    ) -> List[TradeRecommendation]:
        """
        If theta is too low (< $300/day), recommend new CSP or strangle entries.
        """
        recommendations = []
        theta_current = portfolio_greeks.get('theta', 0)

        if theta_current < 300:
            theta_gap = 300 - theta_current
            # Need ~$15-20 theta per new strangle
            num_strangles_needed = int(theta_gap / 15)

            # Recommend Tier 1 names with IVR ≥ 40
            tier_1_names = ['AXON', 'CRWD', 'ADBE', 'SHOP', 'META', 'MSFT', 'NVDA']

            for i, symbol in enumerate(tier_1_names[:num_strangles_needed]):
                # Recommend selling strangle at delta 0.15 PUT / 0.20 CALL
                # Assume current stock price from positions data if available
                current_price = 100  # Placeholder

                put_strike = int(current_price * 0.85)  # 15% OTM
                call_strike = int(current_price * 1.20)  # 20% OTM

                recommendations.append(TradeRecommendation(
                    priority=2,
                    symbol=symbol,
                    action='SELL_STRANGLE',
                    strike=None,  # Two strikes
                    expiry='45-60 DTE',
                    quantity=1,
                    expected_premium=300,  # Rough estimate
                    expected_delta_impact=-0.15,  # Net short delta
                    expected_gamma_impact=0.05,
                    expected_theta_impact=15,
                    why=f"Sell {symbol} strangle to add ${theta_gap - (i*15):.0f} theta, close gap from {theta_current:.0f} to 300+",
                    hedge_fund_context="Strangle entry = systematic theta collection with defined risk (delta-neutral premium capture)"
                ))

        return recommendations

    @staticmethod
    def recommend_profit_takes(
        positions_df: pd.DataFrame,
        profit_threshold_pct: float = 50
    ) -> List[TradeRecommendation]:
        """
        Recommend closing positions that have hit 50%+ of max profit.
        """
        recommendations = []

        for idx, pos in positions_df.iterrows():
            if pd.notna(pos.get('premium_received')) and pos.get('premium_received', 0) > 0:
                if pd.notna(pos.get('mark_price')):
                    profit_pct = ((pos['premium_received'] - pos['mark_price']) / pos['premium_received'] * 100) if pos['premium_received'] > 0 else 0
                    if profit_pct >= profit_threshold_pct:
                        recommendations.append(TradeRecommendation(
                            priority=2,
                            symbol=pos['symbol'],
                            action='CLOSE',
                            strike=pos.get('strike'),
                            expiry=pos.get('expiry'),
                            quantity=abs(pos['qty']),
                            expected_premium=pos['mark_price'],
                            expected_delta_impact=0,  # Neutral
                            expected_gamma_impact=0,
                            expected_theta_impact=0,
                            why=f"Close at {profit_pct:.0f}% profit - redeploy capital to new opportunities",
                            hedge_fund_context="Profit realization & redeployment = compound returns by recycling profitable trades"
                        ))

        return recommendations

    @staticmethod
    def generate_execution_plan(
        positions_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        account: str = "Account A (232)"
    ) -> str:
        """
        Generate complete execution plan with all recommended trades.
        """
        # Calculate current Greeks
        greeks_calc = GreeksCalculator()
        account_positions = positions_df[positions_df['account'] == account]
        portfolio_greeks = greeks_calc.aggregate_to_portfolio(account_positions)

        # Get all recommendations
        delta_fixes = TradeRecommendationEngine.recommend_delta_fixes(positions_df, portfolio_greeks.__dict__, account)
        gamma_fixes = TradeRecommendationEngine.recommend_gamma_fixes(positions_df, portfolio_greeks.__dict__, account)
        theta_additions = TradeRecommendationEngine.recommend_theta_additions(positions_df, portfolio_greeks.__dict__, account)
        profit_takes = TradeRecommendationEngine.recommend_profit_takes(positions_df)

        all_trades = delta_fixes + gamma_fixes + theta_additions + profit_takes
        all_trades.sort(key=lambda x: x.priority)

        # Generate report
        output = []
        output.append("╔" + "═" * 68 + "╗")
        output.append(f"║ TRADE EXECUTION PLAN — {account}          ║")
        output.append("╚" + "═" * 68 + "╝")
        output.append("")

        output.append("CURRENT STATE:")
        output.append(f"  Delta:  {portfolio_greeks.delta:+.2f} (target: ±20)")
        output.append(f"  Gamma:  {portfolio_greeks.gamma:+.3f} (target: ≤0.5)")
        output.append(f"  Theta:  {portfolio_greeks.theta:+.0f}/day (target: ≥$300)")
        output.append("")

        output.append(f"RECOMMENDED TRADES: {len(all_trades)} execution items")
        output.append("")

        # Priority 1
        priority_1_trades = [t for t in all_trades if t.priority == 1]
        if priority_1_trades:
            output.append("🔴 PRIORITY 1 — EXECUTE THIS WEEK")
            output.append("-" * 70)
            for i, trade in enumerate(priority_1_trades, 1):
                output.append(f"\n{i}. {trade.action.replace('_', ' ')}: {trade.symbol}")
                output.append(f"   Quantity: {trade.quantity} | Strike: {trade.strike} | Expiry: {trade.expiry}")
                output.append(f"   Why: {trade.why}")
                output.append(f"   Expected impact:")
                output.append(f"     Delta: {trade.expected_delta_impact:+.2f} → New: {portfolio_greeks.delta + trade.expected_delta_impact:+.2f}")
                output.append(f"     Gamma: {trade.expected_gamma_impact:+.3f} → New: {portfolio_greeks.gamma + trade.expected_gamma_impact:+.3f}")
                output.append(f"     Theta: {trade.expected_theta_impact:+.0f}/day → New: {portfolio_greeks.theta + trade.expected_theta_impact:+.0f}/day")
                output.append(f"   Context: {trade.hedge_fund_context}")
            output.append("")

        # Priority 2
        priority_2_trades = [t for t in all_trades if t.priority == 2]
        if priority_2_trades:
            output.append("🟡 PRIORITY 2 — THIS WEEK (IF CAPACITY)")
            output.append("-" * 70)
            for i, trade in enumerate(priority_2_trades, 1):
                output.append(f"\n{i}. {trade.action.replace('_', ' ')}: {trade.symbol}")
                output.append(f"   Why: {trade.why}")
                output.append(f"   Context: {trade.hedge_fund_context}")
            output.append("")

        # Summary
        total_theta_impact = sum(t.expected_theta_impact for t in all_trades)
        total_gamma_impact = sum(t.expected_gamma_impact for t in all_trades)
        total_delta_impact = sum(t.expected_delta_impact for t in all_trades)

        output.append("EXECUTION SUMMARY:")
        output.append("-" * 70)
        output.append(f"Projected Greeks after execution:")
        output.append(f"  Delta:  {portfolio_greeks.delta + total_delta_impact:+.2f} (from {portfolio_greeks.delta:+.2f})")
        output.append(f"  Gamma:  {portfolio_greeks.gamma + total_gamma_impact:+.3f} (from {portfolio_greeks.gamma:+.3f})")
        output.append(f"  Theta:  {portfolio_greeks.theta + total_theta_impact:+.0f}/day (from {portfolio_greeks.theta:+.0f}/day)")
        output.append("")

        output.append("HEDGE FUND OPERATING PRINCIPLES:")
        output.append("  1. Systematic: Follow guardrails (delta ±20, gamma ≤0.5, theta ≥$300)")
        output.append("  2. Regime-aware: Adjust Greeks targets based on market regime")
        output.append("  3. Capital efficient: Recycle profits into new opportunities")
        output.append("  4. Risk-managed: Close positions at loss if thesis breaks")
        output.append("  5. Opportunistic: Add positions when IV elevated + risk capacity available")
        output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    # Load data
    positions_df, transactions_df = DynamicDataLoader.load_all_data(
        positions_dir="data/positions",
        statements_dir="data/statements",
        use_live_positions=True,
        calculate_greeks=True
    )

    # Generate execution plan
    for account in ["Account A (232)", "Account B (275)"]:
        plan = TradeRecommendationEngine.generate_execution_plan(positions_df, transactions_df, account)
        print(plan)
        print("\n\n")
