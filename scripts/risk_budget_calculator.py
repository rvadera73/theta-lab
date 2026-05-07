"""
Risk Budget Calculator — Position sizing based on risk allocation, not capital.

Framework:
  1. Define max portfolio drawdown tolerance ($500K = 20% of $2.5M)
  2. Allocate risk to each account (A: $200K, B: $200K, C: $100K)
  3. Monitor daily utilization (how much risk is currently being used?)
  4. Calculate breaking point (at what market move does portfolio exceed budget?)
  5. Alert if risk usage exceeds 75% or breaking point < ±12%
"""

import pandas as pd
import yaml
from datetime import date
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import math

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RiskBudgetConfig:
    """Risk budget configuration."""
    max_portfolio_drawdown_pct: float  # 20% = 0.20
    max_portfolio_loss_dollars: float  # Calculated from above
    total_portfolio_equity: float

    account_allocations: Dict[str, float]  # e.g., {"232": 200000, "275": 200000}
    risk_utilization_alert_pct: float  # 75% = 0.75
    breaking_point_alert_pct: float  # ±12% = 0.12


@dataclass
class RiskUtilization:
    """Daily risk utilization report."""
    date: date
    portfolio_equity: float
    total_risk_budget: float

    # Per account
    account_risk: Dict[str, Dict]  # {account: {allocated, used, utilization_pct, max_loss_at_5pct, ...}}

    # Portfolio level
    total_risk_used: float
    total_risk_utilization_pct: float
    breaking_point_market_move_pct: Optional[float]

    alerts: list  # List of alert messages


# ============================================================================
# RISK BUDGET CALCULATOR
# ============================================================================

class RiskBudgetCalculator:
    """Manages position sizing and risk monitoring."""

    def __init__(self, config: RiskBudgetConfig):
        self.config = config

    def calculate_risk_utilization(
        self,
        positions_df: pd.DataFrame,
        portfolio_greeks: Dict[str, float]
    ) -> RiskUtilization:
        """
        Calculate how much of risk budget is currently used.

        Risk is determined by:
          - Current unrealized loss on positions
          - Potential loss at various market moves (5%, 10%, 15%)
          - Margin call risk
        """

        alerts = []
        account_risk = {}

        # Current unrealized loss
        positions_df['unrealized_pnl'] = positions_df['qty'] * positions_df['mark_price'] * 100 - positions_df['qty'] * positions_df['premium_received'] * 100

        for account in positions_df['account'].unique():
            account_df = positions_df[positions_df['account'] == account]

            # Get account equity from data or fallback to config
            if 'account_equity' in account_df.columns:
                account_equity_vals = account_df['account_equity'].dropna()
                account_equity = account_equity_vals.iloc[0] if len(account_equity_vals) > 0 else self.config.total_portfolio_equity / 3
            else:
                account_equity = self.config.total_portfolio_equity / 3

            # Get allocated risk for this account
            account_code = str(account).split('(')[-1].rstrip(')')
            allocated = self.config.account_allocations.get(account_code, self.config.account_allocations.get(account, 0))

            # Current unrealized loss in this account
            current_loss = account_df['unrealized_pnl'].sum()

            # Potential loss at various market moves
            # Loss ≈ delta × market_move + gamma × market_move^2 / 2
            account_delta = account_df['qty'].dot(account_df['delta'])
            account_gamma = account_df['qty'].dot(account_df['gamma'])

            max_loss_at_5pct = self._estimate_loss(account_delta, account_gamma, 0.05)
            max_loss_at_10pct = self._estimate_loss(account_delta, account_gamma, 0.10)
            max_loss_at_15pct = self._estimate_loss(account_delta, account_gamma, 0.15)

            current_risk_used = max(current_loss, max_loss_at_10pct)  # Worst case
            utilization_pct = (current_risk_used / allocated * 100) if allocated > 0 else 0

            account_risk[account] = {
                'allocated': allocated,
                'used': current_risk_used,
                'utilization_pct': utilization_pct,
                'max_loss_5pct': max_loss_at_5pct,
                'max_loss_10pct': max_loss_at_10pct,
                'max_loss_15pct': max_loss_at_15pct,
            }

            if utilization_pct > 75:
                alerts.append(f"⚠️  {account}: Risk usage {utilization_pct:.1f}% (exceeds 75% threshold)")

        # Portfolio level
        total_risk_used = sum(acc['used'] for acc in account_risk.values())
        total_utilization_pct = (total_risk_used / self.config.max_portfolio_loss_dollars * 100) if self.config.max_portfolio_loss_dollars > 0 else 0

        # Calculate breaking point
        breaking_point = self._calculate_breaking_point(
            portfolio_greeks.get('delta', 0),
            portfolio_greeks.get('gamma', 0),
            self.config.max_portfolio_loss_dollars
        )

        if breaking_point and breaking_point < 0.12:  # ±12%
            alerts.append(f"⚠️  Breaking point {breaking_point:.1%}. Consider reducing gamma.")

        return RiskUtilization(
            date=date.today(),
            portfolio_equity=self.config.total_portfolio_equity,
            total_risk_budget=self.config.max_portfolio_loss_dollars,
            account_risk=account_risk,
            total_risk_used=total_risk_used,
            total_risk_utilization_pct=total_utilization_pct,
            breaking_point_market_move_pct=breaking_point,
            alerts=alerts
        )

    def _estimate_loss(self, delta: float, gamma: float, market_move: float) -> float:
        """
        Estimate portfolio loss for a given market move.

        Loss = delta × market_move × $10K + gamma × market_move^2 / 2 × $10K
        (Assumes $10K notional per delta point)
        """
        notional_per_delta = 10000

        delta_loss = delta * market_move * notional_per_delta
        gamma_loss = gamma * (market_move ** 2) / 2 * notional_per_delta

        return abs(delta_loss + gamma_loss)

    def _calculate_breaking_point(self, delta: float, gamma: float, risk_budget: float) -> Optional[float]:
        """
        Calculate the market move % where portfolio loss exceeds risk budget.

        Solve: delta × x + gamma × x^2 / 2 × 10000 = risk_budget
        Quadratic: (gamma × 10000 / 2) × x^2 + (delta × 10000) × x - risk_budget = 0
        """

        notional_per_delta = 10000

        a = gamma * notional_per_delta / 2
        b = delta * notional_per_delta
        c = -risk_budget

        if a == 0:  # Linear equation
            if b != 0:
                return -c / b
            else:
                return None

        discriminant = b ** 2 - 4 * a * c
        if discriminant < 0:
            return None

        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)

        valid_roots = [abs(x) for x in [x1, x2] if x > 0]

        return min(valid_roots) if valid_roots else None

    def generate_report(self, utilization: RiskUtilization) -> str:
        """Generate formatted risk budget report."""

        output = []
        output.append("=" * 70)
        output.append(f"RISK BUDGET STATUS — {utilization.date}")
        output.append("=" * 70)
        output.append("")

        output.append(f"TOTAL RISK BUDGET: ${utilization.total_risk_budget:,.0f}")
        output.append("")

        # By account
        for account, risk in utilization.account_risk.items():
            output.append(f"{account}:")
            output.append(f"  Allocated: ${risk['allocated']:,.0f}")
            output.append(f"  Currently used: ${risk['used']:,.0f} ({risk['utilization_pct']:.1f}%)")
            output.append(f"  Max loss @ -5% market: ${risk['max_loss_5pct']:,.0f}")
            output.append(f"  Max loss @ -10% market: ${risk['max_loss_10pct']:,.0f}")
            output.append(f"  Max loss @ -15% market: ${risk['max_loss_15pct']:,.0f}")

            # Heat indicator
            if risk['utilization_pct'] > 75:
                heat = "🔴"
            elif risk['utilization_pct'] > 50:
                heat = "🟡"
            else:
                heat = "🟢"

            output.append(f"  Status: {heat}")
            output.append("")

        # Portfolio level
        output.append("PORTFOLIO-LEVEL RISK:")
        output.append(f"  Total risk used: ${utilization.total_risk_used:,.0f}")
        output.append(f"  Utilization: {utilization.total_risk_utilization_pct:.1f}%")

        if utilization.breaking_point_market_move_pct:
            output.append(f"  Breaking point: ±{utilization.breaking_point_market_move_pct:.1%}")
        else:
            output.append(f"  Breaking point: None (portfolio won't exceed budget in normal scenarios)")

        output.append("")

        # Alerts
        if utilization.alerts:
            output.append("⚠️  ALERTS:")
            for alert in utilization.alerts:
                output.append(f"  {alert}")
        else:
            output.append("✅ NO ALERTS")

        output.append("")
        output.append("=" * 70)

        return "\n".join(output)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Risk Budget Calculator v1.0")
    print("=" * 70)

    # Example configuration
    config = RiskBudgetConfig(
        max_portfolio_drawdown_pct=0.20,  # 20%
        max_portfolio_loss_dollars=500000,
        total_portfolio_equity=2050000,
        account_allocations={
            "232": 200000,   # Account A
            "275": 200000,   # Account B
            "634": 100000,   # Account C
        },
        risk_utilization_alert_pct=0.75,
        breaking_point_alert_pct=0.12
    )

    calc = RiskBudgetCalculator(config)

    # Usage:
    # positions = pd.read_csv('data/positions/all_accounts_consolidated_YYYY-MM-DD.csv')
    # portfolio_greeks = {'delta': 12.4, 'gamma': 0.42}
    # utilization = calc.calculate_risk_utilization(positions, portfolio_greeks)
    # report = calc.generate_report(utilization)
    # print(report)
