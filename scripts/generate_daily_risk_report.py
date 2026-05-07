"""
Master Report Generator — Unified Daily Risk & Performance Report

Orchestrates all 4 frameworks:
  1. Greeks Dashboard
  2. Risk Budget Allocation
  3. Attribution Tracking
  4. Stress Testing

Output: Single comprehensive report (text + HTML)
"""

import pandas as pd
import yaml
from datetime import date
from pathlib import Path

from greeks_calculator import GreeksCalculator, PositionHeatMonitor
from risk_budget_calculator import RiskBudgetCalculator, RiskBudgetConfig
from attribution_tracker import AttributionTracker
from stress_tester import StressTester
from data_loader import DynamicDataLoader


class DailyRiskReportGenerator:
    """Generate unified daily risk & performance report."""

    def __init__(self, config_path: Path):
        """Initialize with configuration file."""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize calculators
        self.greeks_calc = GreeksCalculator()

        self.risk_config = RiskBudgetConfig(
            max_portfolio_drawdown_pct=self.config['risk_budget']['max_drawdown_pct'],
            max_portfolio_loss_dollars=self.config['risk_budget']['max_loss_dollars'],
            total_portfolio_equity=self.config['portfolio']['total_equity'],
            account_allocations=self.config['risk_budget']['account_allocations'],
            risk_utilization_alert_pct=0.75,
            breaking_point_alert_pct=0.12
        )
        self.risk_calc = RiskBudgetCalculator(self.risk_config)

        self.attr_tracker = AttributionTracker()

        self.stress_tester = StressTester(
            self.config['portfolio']['total_equity'],
            self.config['risk_budget']['max_loss_dollars']
        )

    def generate_report(
        self,
        positions_dir: str = "data/positions",
        transactions_dir: str = "data/statements",
        output_dir: Path = Path("logs")
    ) -> str:
        """
        Generate complete daily risk report.

        Process:
          1. Auto-discover and load positions and transactions
          2. Calculate Greeks automatically from market data
          3. Run Greeks aggregation
          4. Calculate risk utilization
          5. Break down attribution
          6. Run stress scenarios
          7. Generate unified report
        """

        # Load data (auto-discovers files, calculates Greeks)
        positions_df, transactions_df = DynamicDataLoader.load_all_data(
            positions_dir=positions_dir,
            statements_dir=transactions_dir,
            use_live_positions=True,
            calculate_greeks=True
        )

        # Framework 1: Greeks
        portfolio_greeks = self.greeks_calc.aggregate_to_portfolio(positions_df)
        greeks_breaches = self.greeks_calc.check_guardrails(portfolio_greeks)
        greeks_dashboard = self.greeks_calc.generate_dashboard(portfolio_greeks, greeks_breaches)

        # Heat summary
        heat_summary = PositionHeatMonitor.summarize_heat(positions_df)

        # Framework 2: Risk Budget
        portfolio_greeks_dict = {
            'delta': portfolio_greeks.delta,
            'gamma': portfolio_greeks.gamma,
            'vega': portfolio_greeks.vega,
            'theta': portfolio_greeks.theta
        }
        risk_utilization = self.risk_calc.calculate_risk_utilization(
            positions_df, portfolio_greeks_dict
        )
        risk_report = self.risk_calc.generate_report(risk_utilization)

        # Framework 3: Attribution
        attribution = self.attr_tracker.calculate_attribution(transactions_df)
        attr_report = self.attr_tracker.generate_report(attribution)

        # Framework 4: Stress Testing
        scenarios = self.stress_tester.run_standard_scenarios(
            portfolio_greeks.delta, portfolio_greeks.gamma, portfolio_greeks.vega
        )
        breaking_point = self.stress_tester.find_breaking_point(
            portfolio_greeks.delta, portfolio_greeks.gamma, portfolio_greeks.vega
        )
        stress_report = self.stress_tester.generate_report(scenarios, breaking_point)

        # Unified report
        unified = self._generate_unified_report(
            greeks_dashboard, heat_summary, greeks_breaches,
            risk_report, risk_utilization,
            attr_report, attribution,
            stress_report, scenarios
        )

        # Save to file
        output_file = output_dir / f"daily_risk_report_{date.today().isoformat()}.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(unified)

        return unified

    def _generate_unified_report(
        self,
        greeks_dashboard: str, heat_summary: dict, greeks_breaches: list,
        risk_report: str, risk_utilization,
        attr_report: str, attribution,
        stress_report: str, scenarios: list
    ) -> str:
        """Assemble all 4 frameworks into single report."""

        output = []

        # Header
        output.append("╔" + "═" * 68 + "╗")
        output.append("║" + " " * 68 + "║")
        output.append(f"║ DAILY RISK & PERFORMANCE REPORT — {date.today().isoformat():24} ║")
        output.append("║" + " " * 68 + "║")
        output.append("╚" + "═" * 68 + "╝")
        output.append("")

        # 1. GREEKS
        output.append("1. GREEKS DASHBOARD")
        output.append("-" * 70)
        output.append(greeks_dashboard)
        output.append("")

        # Heat summary
        output.append("POSITION HEAT SUMMARY:")
        output.append(f"  🟢 GREEN (healthy): {heat_summary['green']} positions")
        output.append(f"  🟡 YELLOW (monitor): {heat_summary['yellow']} positions")
        output.append(f"  🔴 RED (threatened): {heat_summary['red']} positions")
        output.append("")

        # 2. RISK BUDGET
        output.append("2. RISK BUDGET STATUS")
        output.append("-" * 70)
        output.append(risk_report)
        output.append("")

        # 3. ATTRIBUTION
        output.append("3. ATTRIBUTION TRACKING (YTD)")
        output.append("-" * 70)
        output.append(attr_report)
        output.append("")

        # 4. STRESS TESTING
        output.append("4. STRESS TEST (Weekly Scenarios)")
        output.append("-" * 70)
        output.append(stress_report)
        output.append("")

        # ACTIONS
        output.append("ACTION ITEMS")
        output.append("-" * 70)

        # Compile all alerts
        all_alerts = []

        if greeks_breaches:
            for breach in greeks_breaches:
                all_alerts.append((1, f"GREEKS: {breach.metric.upper()}", breach.recommended_action))

        for alert in risk_utilization.alerts:
            all_alerts.append((2, "RISK BUDGET", alert))

        # Stress test alerts
        for scenario in scenarios:
            if scenario.breaking_budget:
                all_alerts.append((4, "STRESS TEST", f"Breaking point: {scenario.name}"))

        if not all_alerts:
            output.append("✅ NO ALERTS — All frameworks in compliance")
        else:
            for priority, framework, alert in all_alerts:
                output.append(f"Priority {priority} ({framework}): {alert}")

        output.append("")
        output.append("╔" + "═" * 68 + "╗")
        output.append("║ END OF REPORT" + " " * 54 + "║")
        output.append("╚" + "═" * 68 + "╝")

        return "\n".join(output)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    """
    Daily workflow:

    1. Export positions from Schwab → data/positions/
    2. Export transactions from Empower → data/statements/
    3. Run this script
    4. System auto-discovers files, calculates Greeks, generates report
    """

    config_file = Path("config/risk_framework.yaml")

    if not config_file.exists():
        print(f"ERROR: Config file not found at {config_file}")
        print("Create config/risk_framework.yaml with your risk budget settings")
        exit(1)

    generator = DailyRiskReportGenerator(config_file)
    report = generator.generate_report(
        positions_dir="data/positions",
        transactions_dir="data/statements",
        output_dir=Path("logs")
    )

    print(report)
    print(f"\n✅ Report saved to logs/daily_risk_report_{date.today().isoformat()}.txt")
