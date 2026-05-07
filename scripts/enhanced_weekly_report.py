"""
Enhanced Weekly Report — Top 5 Actions + Greeks Dashboard + Position Heat

Combines:
  - Existing: Top 5 weekly actions (closes, rolls, opens)
  - NEW: Greeks guardrail status
  - NEW: Risk utilization check
  - NEW: Stress test quick check
  - NEW: Heat summary (RED/YELLOW/GREEN)
"""

import pandas as pd
from datetime import date
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from greeks_calculator import GreeksCalculator, PositionHeatMonitor
from risk_budget_calculator import RiskBudgetCalculator, RiskBudgetConfig
from stress_tester import StressTester
from data_loader import DynamicDataLoader
from thesis_state_tracker import ThesisStateTracker
from screener_loader import ScreenerLoader


def generate_enhanced_weekly_report(
    positions_file: str = None,
    transactions_file: str = None,
    output_file: str = None,
    positions_df: pd.DataFrame = None,
    transactions_df: pd.DataFrame = None
) -> str:
    """
    Generate enhanced weekly report with Greeks + Risk + Heat.

    Output structure:
      1. EXECUTIVE SUMMARY (Greeks status, heat summary)
      2. TOP 5 ACTIONS (closes, rolls, opens)
      3. HEAT PROTOCOL (RED/YELLOW/GREEN breakdown)
      4. RISK CHECK (utilization, breaking point)
      5. STRESS TEST (quick scenario check)
      6. NEXT WEEK FOCUS
    """

    # Load data (from files or dataframes)
    if positions_df is None or transactions_df is None:
        if positions_file and transactions_file:
            positions_df = pd.read_csv(positions_file)
            transactions_df = pd.read_csv(transactions_file)
        else:
            raise ValueError("Must provide either file paths or dataframes")

    # Thesis validation
    thesis_tracker = ThesisStateTracker()

    # Update thesis for each unique symbol
    if not positions_df.empty and 'symbol' in positions_df.columns:
        for symbol in positions_df['symbol'].dropna().unique():
            symbol = str(symbol).upper()

            # Get position data
            pos_data = positions_df[positions_df['symbol'] == symbol]
            if pos_data.empty:
                continue
            pos = pos_data.iloc[0]

            # Validate thesis using screener rules
            thesis_result = ScreenerLoader.validate_position_thesis(
                symbol=symbol,
                current_price=pos.get('current_price'),
                last_earnings_beat=pos.get('earnings_beat', True),
                guidance_cuts=int(pos.get('guidance_cuts', 0))
            )

            # Update thesis state
            tier = ScreenerLoader.get_tier(symbol)
            moat = ScreenerLoader.get_moat_strength(symbol)
            conviction = int(pos.get('conviction', 5))

            thesis_tracker.update_position_thesis(
                symbol=symbol,
                thesis_status=thesis_result['status'],
                reason=thesis_result['reason'],
                action=thesis_result['action'],
                tier=tier,
                moat_strength=moat,
                conviction=conviction,
                guidance_cuts=int(pos.get('guidance_cuts', 0)),
                earnings_beat=pos.get('earnings_beat'),
                alternatives=[alt[0] for alt in ScreenerLoader.get_alternatives_for_position(symbol)[:3]]
            )

    thesis_summary = thesis_tracker.get_thesis_summary()

    # Greeks
    greeks_calc = GreeksCalculator()
    portfolio_greeks = greeks_calc.aggregate_to_portfolio(positions_df)
    breaches = greeks_calc.check_guardrails(portfolio_greeks)

    # Heat
    heat_summary = PositionHeatMonitor.summarize_heat(positions_df)

    # Risk
    risk_config = RiskBudgetConfig(
        max_portfolio_drawdown_pct=0.20,
        max_portfolio_loss_dollars=500000,
        total_portfolio_equity=2050000,
        account_allocations={"Account A": 200000},
        risk_utilization_alert_pct=0.75,
        breaking_point_alert_pct=0.12
    )
    risk_calc = RiskBudgetCalculator(risk_config)
    risk_util = risk_calc.calculate_risk_utilization(positions_df,
        {'delta': portfolio_greeks.delta, 'gamma': portfolio_greeks.gamma})

    # Stress
    stress_tester = StressTester(2050000, 500000)
    scenarios = stress_tester.run_standard_scenarios(
        portfolio_greeks.delta, portfolio_greeks.gamma, portfolio_greeks.vega
    )

    # Build report
    output = []
    output.append("╔" + "═" * 68 + "╗")
    output.append(f"║ ENHANCED WEEKLY REPORT — {date.today().isoformat():24} ║")
    output.append("╚" + "═" * 68 + "╝")
    output.append("")

    # 1. EXECUTIVE SUMMARY
    output.append("1. EXECUTIVE SUMMARY")
    output.append("-" * 70)
    output.append("")

    delta_ok = -20 <= portfolio_greeks.delta <= 20
    gamma_ok = portfolio_greeks.gamma <= 0.5
    theta_ok = portfolio_greeks.theta >= 300
    risk_ok = risk_util.total_risk_utilization_pct < 75

    output.append("PORTFOLIO HEALTH:")
    output.append(f"  Delta:     {portfolio_greeks.delta:+7.2f}  {'✅' if delta_ok else '❌'}  (target: ±20)")
    output.append(f"  Gamma:     {portfolio_greeks.gamma:+7.3f}  {'✅' if gamma_ok else '❌'}  (max 0.5)")
    output.append(f"  Theta:     {portfolio_greeks.theta:+7.0f}/day {'✅' if theta_ok else '❌'}  (min $300)")
    output.append(f"  Risk used: {risk_util.total_risk_utilization_pct:>7.1f}%  {'✅' if risk_ok else '❌'}  (max 75%)")
    output.append("")

    output.append("POSITION HEAT:")
    output.append(f"  🟢 GREEN:  {heat_summary['green']:3d}  (healthy, let run)")
    output.append(f"  🟡 YELLOW: {heat_summary['yellow']:3d}  (monitor, prepare rolls)")
    output.append(f"  🔴 RED:    {heat_summary['red']:3d}  (threatened, action needed)")
    output.append("")

    overall_ok = all([delta_ok, gamma_ok, theta_ok, risk_ok, heat_summary['red'] < 10])
    status = "🟢 GREEN" if overall_ok else "🟡 YELLOW" if heat_summary['red'] < 30 else "🔴 RED"
    output.append(f"OVERALL STATUS: {status}")
    output.append("")

    # 1.5 THESIS VALIDATION
    output.append("1.5 THESIS VALIDATION SUMMARY")
    output.append("-" * 70)
    output.append("")

    output.append("POSITION STATUS:")
    output.append(f"  🟢 GREEN (Thesis Intact):  {thesis_summary['status_distribution']['GREEN']:2d}")
    output.append(f"  🟡 YELLOW (At Risk):       {thesis_summary['status_distribution']['YELLOW']:2d}")
    output.append(f"  🔴 RED (Thesis Broken):    {thesis_summary['status_distribution']['RED']:2d}")
    output.append(f"  Average Conviction:        {thesis_summary['conviction_avg']:4.1f}/10")
    output.append("")

    output.append("TIER DISTRIBUTION:")
    output.append(f"  Tier 1 (Core):             {thesis_summary['tier_distribution']['tier_1']:2d}")
    output.append(f"  Tier 2 (Emerging):         {thesis_summary['tier_distribution']['tier_2']:2d}")
    output.append(f"  Tier 3 (Speculative):      {thesis_summary['tier_distribution']['tier_3']:2d}")
    output.append("")

    if thesis_summary['thesis_broken']:
        output.append("THESIS BROKEN — Action Required:")
        for sym in thesis_summary['thesis_broken'][:5]:
            thesis = thesis_tracker.get_position_thesis(sym)
            if thesis:
                output.append(f"  • {sym:10} Conviction {thesis['conviction']}/10 | {thesis['moat_strength']:10} | Action: {thesis['action']}")
        output.append("")

    # 2. TOP 5 ACTIONS
    output.append("2. TOP 5 WEEKLY ACTIONS")
    output.append("-" * 70)
    output.append("")

    actions = []
    action_num = 1

    # Action 1: RED thesis positions (conviction broken)
    if thesis_summary['thesis_broken']:
        actions.append(f"{action_num}. CLOSE RED THESIS POSITIONS ({len(thesis_summary['thesis_broken'])} positions)")
        for sym in thesis_summary['thesis_broken'][:3]:
            thesis = thesis_tracker.get_position_thesis(sym)
            if thesis:
                actions.append(f"   • {sym:10} Conviction {thesis['conviction']}/10: {thesis['reason']}")
                alts = thesis.get('alternatives', [])
                if alts:
                    actions.append(f"      → Redeploy to: {', '.join(alts[:2])}")
        actions.append(f"   → Target: All RED positions closed by end of week")
        actions.append("")
        action_num += 1

    # Action 2: RED heat positions (price threat)
    if heat_summary['red'] > 0:
        actions.append(f"{action_num}. MANAGE RED HEAT ({heat_summary['red']} positions at risk)")
        actions.append(f"   → Roll or close {min(5, heat_summary['red'])} most threatened positions")
        actions.append(f"   → Target: Reduce RED count to < 10")
        actions.append("")
        action_num += 1

    # Action 3: Greeks breaches
    if breaches:
        for breach in breaches[:2]:
            actions.append(f"{action_num}. FIX {breach.metric.upper()} BREACH")
            actions.append(f"    → {breach.recommended_action}")
            actions.append("")
            action_num += 1

    # Action 4: Profit takes on YELLOW thesis (at-risk positions approaching targets)
    yellow_count = thesis_summary['status_distribution']['YELLOW']
    if yellow_count > 0:
        actions.append(f"{action_num}. MONITOR YELLOW THESIS ({yellow_count} at risk)")
        actions.append(f"   → Scan for positions at 40-50% profit (close early if thesis deteriorating)")
        actions.append(f"   → Prepare alternatives in case thesis breaks completely")
        actions.append("")
        action_num += 1

    # Action 5: New entries if risk and conviction support
    if risk_ok and thesis_summary['conviction_avg'] >= 5:
        actions.append(f"{action_num}. ENTER NEW POSITIONS (Risk utilization: {risk_util.total_risk_utilization_pct:.1f}%)")
        actions.append(f"   → Screen for HIGH CONVICTION (≥6/10) Tier 1 candidates")
        actions.append(f"   → Capacity available for strangles/CSPs")
        actions.append("")
        action_num += 1

    # Action N: Daily monitoring
    actions.append(f"{action_num}. DAILY THESIS MONITORING")
    actions.append(f"   → Check Greeks + Thesis daily (6 AM email)")
    actions.append(f"   → Alert if conviction drops or earnings data updates")
    actions.append(f"   → Monitor breaking point (±{risk_util.breaking_point_market_move_pct:.0%})")

    output.extend(actions)
    output.append("")

    # 3. HEAT PROTOCOL
    output.append("3. POSITION HEAT DETAILS")
    output.append("-" * 70)
    output.append("")

    output.append("RED POSITIONS (Immediate Action):")
    red_positions = positions_df[positions_df['distance_to_strike_pct'] < 0.10]
    if len(red_positions) > 0:
        output.append(f"  Count: {len(red_positions)}")
        output.append(f"  Action: Roll DOWN+OUT for puts; UP+OUT for calls")
        output.append(f"  Target profit close: 40-50% (bear market rules)")
    else:
        output.append("  None - All clear")
    output.append("")

    output.append("YELLOW POSITIONS (Monitor):")
    output.append(f"  Count: {heat_summary['yellow']}")
    output.append(f"  Action: Prepare rolls if DTE < 30")
    output.append(f"  Target: Monitor daily, act if breach occurs")
    output.append("")

    output.append("GREEN POSITIONS (Let Run):")
    output.append(f"  Count: {heat_summary['green']}")
    output.append(f"  Action: No action needed, let theta decay work")
    output.append("")

    # 4. RISK CHECK
    output.append("4. RISK & LEVERAGE CHECK")
    output.append("-" * 70)
    output.append("")

    output.append("RISK UTILIZATION:")
    output.append(f"  Allocated: ${risk_util.total_risk_budget:,.0f}")
    output.append(f"  Used:      ${risk_util.total_risk_used:,.0f}")
    output.append(f"  Remaining: {100 - risk_util.total_risk_utilization_pct:.1f}% available")

    if risk_util.breaking_point_market_move_pct:
        output.append(f"\nBREAKING POINT: ±{risk_util.breaking_point_market_move_pct:.1%}")
        if risk_util.breaking_point_market_move_pct > 0.12:
            output.append(f"  Status: ✅ SAFE (> ±12% threshold)")
        else:
            output.append(f"  Status: ⚠️  VULNERABLE (< ±12% threshold)")
            output.append(f"  Action: Reduce gamma to improve resilience")
    output.append("")

    # 5. STRESS TEST
    output.append("5. STRESS TEST (Quick Check)")
    output.append("-" * 70)
    output.append("")

    output.append("MARKET SCENARIOS:")
    for s in scenarios[::3]:  # Show every 3rd scenario
        status = "✅" if not s.breaking_budget else "❌"
        output.append(f"  {s.market_move_pct:+.0%} → Loss ${s.total_loss:>10,.0f}  ({s.portfolio_drawdown_pct:>5.1%})  {status}")

    output.append("")

    # 6. NEXT WEEK FOCUS
    output.append("6. NEXT WEEK FOCUS")
    output.append("-" * 70)
    output.append("")

    if heat_summary['red'] > 20:
        output.append("  Priority: Reduce RED positions (> 20 threatened)")
    elif not delta_ok:
        output.append("  Priority: Rebalance delta (too long or short)")
    elif not gamma_ok:
        output.append("  Priority: Reduce gamma risk (convexity too high)")
    elif not theta_ok:
        output.append("  Priority: Add new positions (boost daily income)")
    else:
        output.append("  Priority: Maintain current positioning (all healthy)")

    output.append("")
    output.append("=" * 70)

    report = "\n".join(output)

    # Save if output_file provided
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"✅ Saved: {output_file}")

    return report


def generate_enhanced_weekly_report_from_df(
    positions_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    output_file: str = None
) -> str:
    """Wrapper to generate report from dataframes."""
    return generate_enhanced_weekly_report(
        positions_df=positions_df,
        transactions_df=transactions_df,
        output_file=output_file
    )


if __name__ == "__main__":
    # Auto-discover files and calculate Greeks
    positions_df, transactions_df = DynamicDataLoader.load_all_data(
        positions_dir="data/positions",
        statements_dir="data/statements",
        use_live_positions=True,
        calculate_greeks=True
    )

    # Generate report
    output_file = f"logs/enhanced_weekly_report_{date.today().isoformat()}.txt"
    report = generate_enhanced_weekly_report_from_df(positions_df, transactions_df, output_file)
    print(report)
