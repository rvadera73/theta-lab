"""
Greeks Calculator — Portfolio-level Greeks aggregation and monitoring.

Daily workflow:
  1. Load positions CSV (with delta, gamma, vega, theta per contract)
  2. Aggregate to portfolio level
  3. Check guardrails (delta, gamma, vega, theta)
  4. Generate daily dashboard
  5. Alert on any breaches
"""

import pandas as pd
import yaml
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class PortfolioGreeks:
    """Portfolio-level Greeks."""
    date: date
    delta: float
    gamma: float
    vega: float
    theta: float  # dollars per day

    account_greeks: Dict[str, Dict[str, float]] = None  # By account
    position_count: int = 0

    def __post_init__(self):
        if self.account_greeks is None:
            self.account_greeks = {}


@dataclass
class GuardrailBreach:
    """A guardrail violation."""
    metric: str  # 'delta', 'gamma', 'vega', 'theta'
    current_value: float
    threshold: float
    severity: str  # 'warning', 'critical'
    recommended_action: str


# ============================================================================
# GREEKS CALCULATOR
# ============================================================================

class GreeksCalculator:
    """Calculates and monitors portfolio Greeks."""

    def __init__(self, config_path: Path = None):
        """Initialize with guardrail configuration."""
        if config_path:
            with open(config_path) as f:
                self.guardrails = yaml.safe_load(f).get('guardrails', {})
        else:
            # Default guardrails
            self.guardrails = {
                'delta': {'min': -20, 'max': 20},
                'gamma': {'max': 0.5},
                'vega': {'min': -10, 'max': 5},
                'theta': {'min': 300},  # dollars per day
            }

    def aggregate_to_portfolio(self, positions_df: pd.DataFrame) -> PortfolioGreeks:
        """
        Aggregate position-level Greeks to portfolio level.

        Input: DataFrame with columns [account, symbol, qty, delta, gamma, vega, theta]
        Output: PortfolioGreeks object

        Assumptions:
          - qty: 1 or -1 for options; shares for equity
          - delta, gamma, vega, theta: per contract (already scaled)
          - theta: in dollars per day
        """

        if positions_df.empty:
            return PortfolioGreeks(
                date=date.today(),
                delta=0, gamma=0, vega=0, theta=0,
                position_count=0
            )

        # Portfolio aggregation
        portfolio_delta = (positions_df['qty'] * positions_df['delta']).sum()
        portfolio_gamma = (positions_df['qty'] * positions_df['gamma']).sum()
        portfolio_vega = (positions_df['qty'] * positions_df['vega']).sum()
        portfolio_theta = (positions_df['qty'] * positions_df['theta']).sum()

        # By-account aggregation
        account_greeks = {}
        for account in positions_df['account'].unique():
            account_df = positions_df[positions_df['account'] == account]
            account_greeks[account] = {
                'delta': (account_df['qty'] * account_df['delta']).sum(),
                'gamma': (account_df['qty'] * account_df['gamma']).sum(),
                'vega': (account_df['qty'] * account_df['vega']).sum(),
                'theta': (account_df['qty'] * account_df['theta']).sum(),
                'position_count': len(account_df)
            }

        return PortfolioGreeks(
            date=date.today(),
            delta=portfolio_delta,
            gamma=portfolio_gamma,
            vega=portfolio_vega,
            theta=portfolio_theta,
            account_greeks=account_greeks,
            position_count=len(positions_df)
        )

    def check_guardrails(self, portfolio_greeks: PortfolioGreeks) -> List[GuardrailBreach]:
        """Check if portfolio Greeks violate guardrails."""
        breaches = []

        # Delta guardrail
        if portfolio_greeks.delta > self.guardrails['delta']['max']:
            breaches.append(GuardrailBreach(
                metric='delta',
                current_value=portfolio_greeks.delta,
                threshold=self.guardrails['delta']['max'],
                severity='warning',
                recommended_action=f"Close calls (portfolio too long). Target delta <= 20."
            ))

        if portfolio_greeks.delta < self.guardrails['delta']['min']:
            breaches.append(GuardrailBreach(
                metric='delta',
                current_value=portfolio_greeks.delta,
                threshold=self.guardrails['delta']['min'],
                severity='warning',
                recommended_action=f"Close puts (portfolio too short). Target delta >= -20."
            ))

        # Gamma guardrail
        if portfolio_greeks.gamma > self.guardrails['gamma']['max']:
            breaches.append(GuardrailBreach(
                metric='gamma',
                current_value=portfolio_greeks.gamma,
                threshold=self.guardrails['gamma']['max'],
                severity='warning',
                recommended_action=f"Close strangles (reduce convexity risk). Target gamma <= 0.5."
            ))

        # Vega guardrail
        if portfolio_greeks.vega > self.guardrails['vega']['max']:
            breaches.append(GuardrailBreach(
                metric='vega',
                current_value=portfolio_greeks.vega,
                threshold=self.guardrails['vega']['max'],
                severity='info',
                recommended_action=f"Long vol position. Monitor if IV continues to expand."
            ))

        if portfolio_greeks.vega < self.guardrails['vega']['min']:
            breaches.append(GuardrailBreach(
                metric='vega',
                current_value=portfolio_greeks.vega,
                threshold=self.guardrails['vega']['min'],
                severity='info',
                recommended_action=f"Short vol position (expected). Gain if IV contracts."
            ))

        # Theta guardrail
        if portfolio_greeks.theta < self.guardrails['theta']['min']:
            breaches.append(GuardrailBreach(
                metric='theta',
                current_value=portfolio_greeks.theta,
                threshold=self.guardrails['theta']['min'],
                severity='warning',
                recommended_action=f"Add new positions to boost daily theta income. Target >= $300/day."
            ))

        return breaches

    def generate_dashboard(self, portfolio_greeks: PortfolioGreeks, breaches: List[GuardrailBreach]) -> str:
        """Generate formatted dashboard text."""

        output = []
        output.append("=" * 70)
        output.append(f"GREEKS DASHBOARD — {portfolio_greeks.date}")
        output.append("=" * 70)
        output.append("")

        # Portfolio summary
        output.append("PORTFOLIO-LEVEL GREEKS:")
        output.append(f"  Delta: {portfolio_greeks.delta:>7.2f}  (net {'long' if portfolio_greeks.delta > 0 else 'short'} {abs(portfolio_greeks.delta)*100:.0f} shares equivalent)")
        output.append(f"  Gamma: {portfolio_greeks.gamma:>7.3f}  (convexity)")
        output.append(f"  Vega:  {portfolio_greeks.vega:>7.2f}  ({'short' if portfolio_greeks.vega < 0 else 'long'} volatility)")
        output.append(f"  Theta: {portfolio_greeks.theta:>7.0f}/day (daily time decay capture)")
        output.append("")

        # By account
        if portfolio_greeks.account_greeks:
            output.append("BY ACCOUNT:")
            for account, greeks in portfolio_greeks.account_greeks.items():
                output.append(f"\n  {account}:")
                output.append(f"    Delta: {greeks['delta']:>7.2f}")
                output.append(f"    Gamma: {greeks['gamma']:>7.3f}")
                output.append(f"    Vega:  {greeks['vega']:>7.2f}")
                output.append(f"    Theta: {greeks['theta']:>7.0f}/day")
                output.append(f"    Positions: {greeks['position_count']}")
            output.append("")

        # Guardrail status
        output.append("GUARDRAIL STATUS:")
        output.append(f"  Delta: {portfolio_greeks.delta:>7.2f} (target: {self.guardrails['delta']['min']} to {self.guardrails['delta']['max']:>3}) {'✅' if -20 <= portfolio_greeks.delta <= 20 else '⚠️'}")
        output.append(f"  Gamma: {portfolio_greeks.gamma:>7.3f} (target: max {self.guardrails['gamma']['max']:<6.1f}) {'✅' if portfolio_greeks.gamma <= 0.5 else '⚠️'}")
        output.append(f"  Vega:  {portfolio_greeks.vega:>7.2f} (target: {self.guardrails['vega']['min']} to {self.guardrails['vega']['max']:>3}) {'✅' if -10 <= portfolio_greeks.vega <= 5 else '⚠️'}")
        output.append(f"  Theta: {portfolio_greeks.theta:>7.0f} (target: min {self.guardrails['theta']['min']:<6.0f}) {'✅' if portfolio_greeks.theta >= 300 else '⚠️'}")
        output.append("")

        # Breaches
        if breaches:
            output.append(f"⚠️  GUARDRAIL BREACHES ({len(breaches)}):")
            for breach in breaches:
                output.append(f"\n  {breach.metric.upper()}: {breach.current_value:.2f} (threshold: {breach.threshold})")
                output.append(f"    Severity: {breach.severity.upper()}")
                output.append(f"    Action: {breach.recommended_action}")
        else:
            output.append("✅ NO GUARDRAIL BREACHES")

        output.append("")
        output.append("=" * 70)

        return "\n".join(output)


# ============================================================================
# HEAT MONITOR (Companion to Greeks)
# ============================================================================

class PositionHeatMonitor:
    """Monitor individual positions for RED/YELLOW/GREEN status."""

    @staticmethod
    def calculate_heat(
        current_mark: float,
        premium_received: float,
        dte: int,
        distance_to_strike_pct: float
    ) -> str:
        """
        Determine position heat status.

        GREEN: Distance > 20%, DTE > 30, Mark < 1.5x premium
        YELLOW: Distance 10-20%, DTE 21-30, Mark 1.5-2x premium
        RED: Distance < 10%, DTE < 21, Mark > 2x premium
        """

        mark_ratio = current_mark / premium_received if premium_received > 0 else 0

        # RED (highest priority)
        if mark_ratio > 2.0 or dte < 21 or distance_to_strike_pct < 10:
            return 'RED'

        # YELLOW (monitor)
        if mark_ratio > 1.5 or (dte >= 21 and dte <= 30) or (10 <= distance_to_strike_pct <= 20):
            return 'YELLOW'

        # GREEN (healthy)
        return 'GREEN'

    @staticmethod
    def summarize_heat(positions_df: pd.DataFrame) -> Dict[str, int]:
        """Count RED/YELLOW/GREEN positions."""

        positions_df['heat'] = positions_df.apply(
            lambda row: PositionHeatMonitor.calculate_heat(
                row['current_mark'],
                row['premium_received'],
                row['dte'],
                row['distance_to_strike_pct']
            ),
            axis=1
        )

        return {
            'green': len(positions_df[positions_df['heat'] == 'GREEN']),
            'yellow': len(positions_df[positions_df['heat'] == 'YELLOW']),
            'red': len(positions_df[positions_df['heat'] == 'RED']),
        }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Greeks Calculator v1.0")
    print("=" * 70)

    # Example usage (requires positions CSV with Greeks)
    #
    # positions = pd.read_csv('data/positions/all_accounts_consolidated_YYYY-MM-DD.csv')
    #
    # calc = GreeksCalculator()
    # portfolio_greeks = calc.aggregate_to_portfolio(positions)
    # breaches = calc.check_guardrails(portfolio_greeks)
    # dashboard = calc.generate_dashboard(portfolio_greeks, breaches)
    #
    # print(dashboard)
    #
    # # Save to logs
    # with open(f"logs/greeks_dashboard_{date.today().isoformat()}.txt", 'w') as f:
    #     f.write(dashboard)
