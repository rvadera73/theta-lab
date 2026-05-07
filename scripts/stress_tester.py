"""
Stress Tester — Model portfolio loss under various market scenarios.

Scenarios tested:
  - Market ±5%, ±10%, ±15%, ±20%
  - IV changes: ±20 vol points
  - Combined: Market move + IV move
"""

import math
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class StressScenario:
    """A single stress test scenario."""
    name: str
    market_move_pct: float  # -0.10 = market down 10%
    iv_move_pct: float  # +0.20 = IV up 20 points
    delta_loss: float
    gamma_loss: float
    vega_loss: float
    total_loss: float
    portfolio_drawdown_pct: float
    breaking_budget: bool  # True if exceeds risk budget
    margin_call_risk: bool  # True if margin utilization > 80%


class StressTester:
    """Run portfolio stress tests."""

    def __init__(self, portfolio_equity: float, risk_budget: float):
        self.portfolio_equity = portfolio_equity
        self.risk_budget = risk_budget

    def run_scenario(
        self,
        delta: float,
        gamma: float,
        vega: float,
        market_move: float,
        iv_move: float = 0
    ) -> StressScenario:
        """
        Model portfolio loss for a given market/IV move.

        Loss = (delta × market_move) + (gamma × market_move^2 / 2) + (vega × iv_move)

        Assumptions:
          - $10K notional per delta point
          - Vega = dollars per IV point
        """

        notional_per_delta = 10000

        # Loss components
        delta_loss = delta * market_move * notional_per_delta
        gamma_loss = gamma * (market_move ** 2) / 2 * notional_per_delta
        vega_loss = vega * iv_move * 100  # vega per IV point

        total_loss = delta_loss + gamma_loss + vega_loss
        drawdown_pct = total_loss / self.portfolio_equity

        breaking_budget = abs(total_loss) > self.risk_budget
        margin_call_risk = abs(drawdown_pct) > 0.15  # 15% drawdown triggers margin concerns

        return StressScenario(
            name=f"Market {market_move:+.0%}, IV {iv_move:+.0f}pts",
            market_move_pct=market_move,
            iv_move_pct=iv_move,
            delta_loss=delta_loss,
            gamma_loss=gamma_loss,
            vega_loss=vega_loss,
            total_loss=total_loss,
            portfolio_drawdown_pct=drawdown_pct,
            breaking_budget=breaking_budget,
            margin_call_risk=margin_call_risk
        )

    def run_standard_scenarios(self, delta: float, gamma: float, vega: float) -> List[StressScenario]:
        """Run standard scenarios: market ±5%, ±10%, ±15%, ±20%."""

        scenarios = []

        for move in [-0.05, -0.10, -0.15, -0.20, 0.05, 0.10, 0.15, 0.20]:
            # Assume IV rises in down markets, falls in up markets
            iv_move = 20 if move < 0 else -15

            scenario = self.run_scenario(delta, gamma, vega, move, iv_move)
            scenarios.append(scenario)

        return scenarios

    def find_breaking_point(self, delta: float, gamma: float, vega: float) -> float:
        """At what market move % does portfolio loss exceed risk budget?"""

        # Search for breaking point via binary search
        for move_pct in [0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30]:
            scenario = self.run_scenario(delta, gamma, vega, move_pct, 0)
            if scenario.breaking_budget:
                return move_pct

        return None

    def generate_report(self, scenarios: List[StressScenario], breaking_point: float) -> str:
        """Generate formatted stress test report."""

        output = []
        output.append("=" * 70)
        output.append("STRESS TEST REPORT — Weekly Scenarios")
        output.append("=" * 70)
        output.append("")

        for scenario in scenarios:
            status = "❌ EXCEEDS BUDGET" if scenario.breaking_budget else ("⚠️ MARGIN CALL RISK" if scenario.margin_call_risk else "✅ ACCEPTABLE")

            output.append(f"{scenario.name:30} → Loss ${scenario.total_loss:>10,.0f} ({scenario.portfolio_drawdown_pct:>6.2%}) {status}")

        output.append("")
        output.append(f"BREAKING POINT: ±{breaking_point:.1%}" if breaking_point else "No breaking point found")

        output.append("=" * 70)

        return "\n".join(output)
