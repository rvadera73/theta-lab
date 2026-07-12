#!/usr/bin/env python3
"""
Example usage of the Theta-Lab Performance Engine.
Demonstrates all 4 report types and component access patterns.
"""

from theta_lab_performance_engine import PerformanceEngine
from datetime import date, timedelta

def main():
    """Run all example usage patterns"""

    print("=" * 80)
    print("THETA-LAB PERFORMANCE ENGINE — USAGE EXAMPLES")
    print("=" * 80)
    print()

    # Initialize the engine
    print("Initializing Performance Engine...")
    engine = PerformanceEngine()
    print("✓ Engine initialized with all components")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 1: Generate All Reports at Once
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 1: Generate All Reports at Once")
    print("-" * 80)

    reports = engine.generate_all_reports()
    print(f"Generated {len(reports)} reports:")
    for report_type in reports.keys():
        print(f"  ✓ {report_type}")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 2: Generate Daily Live Dashboard
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 2: Daily Live Dashboard")
    print("-" * 80)

    dashboard = engine.generate_live_dashboard()
    print("First 50 lines of dashboard:")
    print("\n".join(dashboard.split("\n")[:50]))
    print("\n... (full report in generated output) ...")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 3: Weekly Execution Report with Custom Plan
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 3: Weekly Report with Custom Plan")
    print("-" * 80)

    # Define what you planned to do this week
    weekly_plan = {
        'put_entries': 5,
        'call_entries': 3,
        'close_targets': 8,
        'reductions': 2,
    }

    print("Plan submitted for this week:")
    for action, target in weekly_plan.items():
        print(f"  {action}: {target}")
    print()

    weekly_report = engine.generate_weekly_report(plan=weekly_plan)
    print("Weekly Execution Report generated (first 40 lines):")
    print("\n".join(weekly_report.split("\n")[:40]))
    print("\n... (includes variance analysis and next week recommendations) ...")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 4: Bi-weekly Trend & Risk Analysis
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 4: Bi-weekly Trend & Risk Report")
    print("-" * 80)

    trend_report = engine.generate_trend_report()
    print("Bi-weekly Report generated (first 50 lines):")
    print("\n".join(trend_report.split("\n")[:50]))
    print("\n... (includes edge validity, market breakdown, regime forecast) ...")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 5: Monthly Strategy Review
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 5: Monthly Strategy Review")
    print("-" * 80)

    monthly_review = engine.generate_monthly_review()
    print("Monthly Review generated (first 45 lines):")
    print("\n".join(monthly_review.split("\n")[:45]))
    print("\n... (includes goal achievement, annual progress, H2 plan) ...")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 6: Access Individual Components
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 6: Direct Component Access")
    print("-" * 80)

    # Portfolio Metrics
    print("6a. Portfolio Metrics:")
    margin = engine.metrics.get_margin_utilization()
    print(f"  Margin utilization: {margin['current_percent']:.1f}%")
    print(f"  Status: {margin['status']}")
    print()

    concentration = engine.metrics.get_concentration()
    print(f"  Top position: {concentration['top_positions'][0]['symbol']} "
          f"({concentration['top_positions'][0]['percent']:.1f}%)")
    print()

    balances = engine.metrics.get_account_balances()
    total = sum(balances.values())
    print(f"  Total portfolio: ${total:,.0f}")
    print()

    # Closed P&L Analysis
    print("6b. Closed P&L Analysis:")
    total_pl = engine.closed_pl.get_total_pl()
    print(f"  Total P&L (all time): ${total_pl['total']:,.0f}")
    print()

    win_rate = engine.closed_pl.get_win_rate()
    print(f"  Overall win rate: {win_rate['overall']:.1%}")
    print()

    # Risk Monitoring
    print("6c. Risk Monitoring:")
    alerts = engine.risk.check_all()
    print(f"  Active alerts: {len(alerts)}")
    for alert in alerts:
        print(f"    - [{alert['type']}] {alert['category']}: {alert['detail'][:60]}...")
    print()

    # Trend Analysis
    print("6d. Trend & Regime Analysis:")
    edge = engine.trends.get_edge_validity()
    print(f"  Put-selling edge: {edge['put_selling_edge']['status']} "
          f"(+${edge['put_selling_edge']['ytd_pl']:,.0f} YTD)")
    print(f"  Call-selling edge: {edge['call_selling_edge']['status']} "
          f"(${edge['call_selling_edge']['ytd_pl']:,.0f} YTD)")
    print()

    regime = engine.trends.get_regime_assessment()
    print(f"  Current regime: {regime['regime']}")
    print(f"  IV Rank: {regime['iv_rank']}, VIX: {regime['vix']}")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 7: Risk Alert Interpretation
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 7: Interpreting Risk Alerts")
    print("-" * 80)

    print("Current risk alerts and what they mean:\n")

    for alert in alerts:
        severity = "🔴 CRITICAL" if alert['type'] == 'CRITICAL' else "🟡 WARNING"
        print(f"{severity}: {alert['category']}")
        print(f"  Current: {alert.get('current', alert.get('detail', 'N/A'))}")
        print(f"  Action: {alert['action']}")
        print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 8: Filtering Closed Trades
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 8: Filtering Closed Trades by Date/Account")
    print("-" * 80)

    # Get trades from June
    june_start = date(2026, 6, 1)
    june_end = date(2026, 6, 30)

    june_trades = engine.closed_pl.get_closed_trades(
        start_date=june_start,
        end_date=june_end
    )

    print(f"Closed trades in June 2026: {len(june_trades)}")
    print()

    # Get trades for specific account
    account_a_trades = engine.closed_pl.get_closed_trades(
        account='Account A (232)'
    )

    print(f"Total closed trades for Account A: {len(account_a_trades)}")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 9: Custom Weekly Plan Tracking
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 9: Execution Tracking During the Week")
    print("-" * 80)

    print("Scenario: You plan to execute specific trades this week")
    print()

    # Create tracker with your plan
    plan = {
        'targets': {
            'put_entries': 5,
            'call_entries': 3,
            'closes': 8,
        }
    }

    tracker = engine.tracker
    tracker.plan = plan

    # As you execute during the week, record actual trades
    print("Monday/Tuesday: Record your executions")
    tracker.record_actual('put_entries', 'AAPL', 1)
    tracker.record_actual('put_entries', 'MSFT', 2)
    tracker.record_actual('call_entries', 'TSLA', 1)
    tracker.record_actual('closes', 'NFLX', 3)

    print(f"  Recorded: 3 put entries, 1 call entry, 3 closes")
    print()

    # Get variance analysis
    variance = tracker.get_variance_analysis()
    print("Variance Analysis (Wed):")
    for action, metrics in variance['variance'].items():
        print(f"  {action}:")
        print(f"    Planned: {metrics['planned']}, Actual: {metrics['actual']}, "
              f"Variance: {metrics['variance_pct']:+.0f}%")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # EXAMPLE 10: Scenario Analysis
    # ═══════════════════════════════════════════════════════════════════
    print("-" * 80)
    print("EXAMPLE 10: Market Breakdown Scenario Analysis")
    print("-" * 80)

    breakdown = engine.trends.get_market_breakdown_risk()
    print("What happens if SPX drops 10% intraday?")
    print()
    print(f"Margin Risk:")
    print(f"  Current: {breakdown['margin_risk']['current_margin_pct']}%")
    print(f"  Post-crash: {breakdown['margin_risk']['post_crash_estimate']}")
    print(f"  Action: {breakdown['margin_risk']['action_required']}")
    print()

    print("Liquidity Risk:")
    print(f"  Status: {breakdown['liquidity_risk']['status']}")
    print(f"  Note: {breakdown['liquidity_risk']['note']}")
    print()

    print("Greek Risk:")
    print(f"  Delta: {breakdown['greek_risk']['delta_exposure']}")
    print(f"  Gamma: {breakdown['greek_risk']['gamma_risk']}")
    print()

    # ═══════════════════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════════════════
    print("=" * 80)
    print("SUMMARY: Performance Engine Integration Points")
    print("=" * 80)
    print()
    print("Daily:")
    print("  engine.generate_live_dashboard()  — Portfolio health & alerts")
    print()
    print("Weekly:")
    print("  engine.generate_weekly_report(plan)  — Execution tracking")
    print("  engine.tracker.record_actual()       — Log actual trades")
    print()
    print("Bi-weekly:")
    print("  engine.generate_trend_report()   — Edge validity & regime")
    print()
    print("Monthly:")
    print("  engine.generate_monthly_review()  — Goals & H2 planning")
    print()
    print("Anytime:")
    print("  engine.metrics.get_*()  — Current portfolio state")
    print("  engine.trends.get_*()   — Analysis & forecasts")
    print("  engine.risk.check_all() — Risk alerts")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
