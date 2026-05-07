"""
Daily Trade Execution Report — Account-by-Account Specific Trades

Generates every morning:
1. Current state per account (Greeks, heat, risk, cash)
2. Exact trades to execute TODAY (symbol, strike, qty, action, why)
3. Expected Greeks impact after execution
4. Execution priority (urgent vs this week)
5. Account-specific constraints and rules
"""

import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from data_loader import DynamicDataLoader
from greeks_calculator import GreeksCalculator, PortfolioGreeks
from screener_loader import ScreenerLoader


@dataclass
class AccountTrade:
    """Trade recommendation for specific account."""
    account: str
    priority: int
    action: str  # CLOSE, ROLL, ENTER, HOLD
    symbol: str
    strike_put: Optional[float] = None
    strike_call: Optional[float] = None
    qty: int = 1
    dte: Optional[int] = None
    expected_premium: float = 0.0
    delta_impact: float = 0.0
    gamma_impact: float = 0.0
    theta_impact: float = 0.0
    reason: str = ""
    expected_margin_impact: float = 0.0


class DailyTradeExecutor:
    """Generate daily execution trades per account."""

    # Account-specific targets
    ACCOUNT_TARGETS = {
        'Account A (232)': {
            'name': 'Schwab Account A (Margin)',
            'delta_target': 20,
            'gamma_target': 0.5,
            'theta_target': 200,
            'risk_per_account': 200000,
            'margin_max': 0.65,
            'cash_min': 75000,
            'max_contracts_tier1': 5,
            'max_contracts_tier2': 3,
            'max_contracts_tier3': 1,
        },
        'Account B (275)': {
            'name': 'Schwab Account B (IRA Wheel)',
            'delta_target': 10,
            'gamma_target': 0.2,
            'theta_target': 75,
            'risk_per_account': 200000,
            'margin_max': 0.0,
            'cash_min': 50000,
            'max_contracts_tier1': 1,
            'max_contracts_tier2': 1,
            'max_contracts_tier3': 1,
        },
        'Account C (634)': {
            'name': 'Schwab Account C (Conservative IRA)',
            'delta_target': 5,
            'gamma_target': 0.1,
            'theta_target': 25,
            'risk_per_account': 100000,
            'margin_max': 0.0,
            'cash_min': 30000,
            'max_contracts_tier1': 1,
            'max_contracts_tier2': 0,
            'max_contracts_tier3': 0,
        },
        'Traditional IRA': {
            'name': 'Fidelity Traditional IRA',
            'delta_target': 8,
            'gamma_target': 0.2,
            'theta_target': 50,
            'risk_per_account': 100000,
            'margin_max': 0.0,
            'cash_min': 25000,
            'max_contracts_tier1': 1,
            'max_contracts_tier2': 1,
            'max_contracts_tier3': 0,
        },
        'ROTH IRA': {
            'name': 'Fidelity ROTH IRA',
            'delta_target': 8,
            'gamma_target': 0.2,
            'theta_target': 50,
            'risk_per_account': 100000,
            'margin_max': 0.0,
            'cash_min': 25000,
            'max_contracts_tier1': 1,
            'max_contracts_tier2': 1,
            'max_contracts_tier3': 0,
        },
        'Vanguard Taxable': {
            'name': 'Vanguard Taxable',
            'delta_target': 15,
            'gamma_target': 0.3,
            'theta_target': 100,
            'risk_per_account': 150000,
            'margin_max': 0.0,
            'cash_min': 50000,
            'max_contracts_tier1': 2,
            'max_contracts_tier2': 1,
            'max_contracts_tier3': 0,
        },
    }

    # Tier classification for position sizing
    TIER_1 = ['AXON', 'CRWD', 'ADBE', 'SHOP', 'META', 'MSFT', 'NVDA', 'COIN']  # Quality, liquid
    TIER_2 = ['SMR', 'CCJ', 'RKLB', 'ASTS', 'OKTA', 'ZS', 'LMT', 'RTX', 'BE', 'TSM']  # Growth
    TIER_3 = ['RGTI', 'ACHR', 'JOBY', 'SMCI', 'IONQ', 'OKLO']  # Speculative

    @staticmethod
    def classify_tier(symbol: str) -> int:
        """Classify stock into tier."""
        symbol = str(symbol).split()[0] if isinstance(symbol, str) else ""
        if symbol in DailyTradeExecutor.TIER_1:
            return 1
        elif symbol in DailyTradeExecutor.TIER_2:
            return 2
        elif symbol in DailyTradeExecutor.TIER_3:
            return 3
        return 2  # Default to Tier 2

    @staticmethod
    def get_account_recommendations(
        account_name: str,
        account_positions: pd.DataFrame,
        portfolio_greeks_dict: Dict,
        all_positions: pd.DataFrame
    ) -> List[AccountTrade]:
        """
        Generate specific trade recommendations for ONE account.

        Logic:
        1. If delta breached → close calls (reduce long) or puts (reduce short)
        2. If gamma breached → close strangles
        3. If theta gap → enter new CSPs/strangles
        4. If profitable positions → close them (profit take + recycle)
        5. If RED positions → close or roll immediately
        """
        trades = []
        targets = DailyTradeExecutor.ACCOUNT_TARGETS.get(account_name, {})

        if account_positions.empty:
            return trades

        # Add heat column if not present
        positions = account_positions.copy()
        if 'heat' not in positions.columns:
            if 'distance_to_strike_pct' in positions.columns:
                positions['heat'] = positions['distance_to_strike_pct'].apply(
                    lambda x: '🔴 RED' if pd.notna(x) and x < 0.10 else ('🟡 YELLOW' if pd.notna(x) and x < 0.20 else '🟢 GREEN')
                )
            else:
                positions['heat'] = '🟢 GREEN'

        account_positions = positions

        # Current state
        delta = account_positions['delta'].sum() if 'delta' in account_positions.columns else 0
        gamma = account_positions['gamma'].sum() if 'gamma' in account_positions.columns else 0
        theta = account_positions['theta'].sum() if 'theta' in account_positions.columns else 0
        heat = account_positions['heat'].value_counts() if 'heat' in account_positions.columns else {}

        delta_breach = delta > targets.get('delta_target', 20)
        gamma_breach = gamma > targets.get('gamma_target', 0.5)
        theta_gap = theta < targets.get('theta_target', 200)

        # --- PRIORITY 1: Fix RED positions (close profitable ones, roll losing ones) ---
        red_positions = account_positions[account_positions['heat'] == '🔴 RED']
        for idx, pos in red_positions.iterrows():
            if pd.notna(pos.get('pnl_status')) and pos.get('pnl_status') == 'WINNING':
                # Close profitable RED
                trades.append(AccountTrade(
                    account=account_name,
                    priority=1,
                    action='CLOSE',
                    symbol=str(pos['symbol']),
                    strike_call=pos.get('strike'),
                    qty=abs(int(pos.get('qty', 1))),
                    delta_impact=-pos.get('delta', 0),
                    gamma_impact=-pos.get('gamma', 0),
                    theta_impact=-pos.get('theta', 0),
                    reason=f"RED + WINNING → Collect profit, reduce heat"
                ))
            elif pd.notna(pos.get('pnl_status')) and pos.get('pnl_status') == 'LOSING':
                # Roll losing RED
                trades.append(AccountTrade(
                    account=account_name,
                    priority=1,
                    action='ROLL',
                    symbol=str(pos['symbol']),
                    strike_call=pos.get('strike'),
                    dte=45,
                    delta_impact=-pos.get('delta', 0) * 0.3,  # Partial reduction
                    gamma_impact=-pos.get('gamma', 0) * 0.3,
                    theta_impact=10,  # Roll gives more theta
                    reason=f"RED + LOSING → Roll down+out, extend time"
                ))

        # --- PRIORITY 1: Fix DELTA breach ---
        if delta_breach:
            # Close calls (reduce long delta)
            calls = account_positions[
                (account_positions['symbol'].astype(str).str.contains('CALL', na=False)) &
                (account_positions['delta'] > 0.3)
            ].sort_values('delta', ascending=False)

            for idx, call in calls.head(3).iterrows():
                tier = DailyTradeExecutor.classify_tier(call['symbol'])
                if tier <= 2:  # Only close Tier 1-2
                    trades.append(AccountTrade(
                        account=account_name,
                        priority=1,
                        action='CLOSE',
                        symbol=str(call['symbol']),
                        strike_call=call.get('strike'),
                        qty=abs(int(call.get('qty', 1))),
                        delta_impact=-call.get('delta', 0),
                        gamma_impact=-call.get('gamma', 0),
                        theta_impact=-call.get('theta', 0),
                        reason=f"DELTA breach ({delta:+.1f} > {targets.get('delta_target', 20)}): Close calls"
                    ))

        # --- PRIORITY 1: Fix GAMMA breach ---
        if gamma_breach:
            # Close strangles (both legs)
            symbols_by_gamma = account_positions.groupby('symbol')['gamma'].sum().sort_values(ascending=False)
            closed_gamma = 0

            for symbol in symbols_by_gamma.index:
                if closed_gamma >= gamma - targets.get('gamma_target', 0.5):
                    break

                symbol_pos = account_positions[account_positions['symbol'] == symbol]
                symbol_gamma = symbol_pos['gamma'].sum()

                if symbol_gamma > 0.05:
                    trades.append(AccountTrade(
                        account=account_name,
                        priority=1,
                        action='CLOSE_STRANGLE',
                        symbol=str(symbol),
                        qty=1,
                        delta_impact=-symbol_pos['delta'].sum(),
                        gamma_impact=-symbol_gamma,
                        theta_impact=-symbol_pos['theta'].sum(),
                        reason=f"GAMMA breach ({gamma:+.3f} > {targets.get('gamma_target', 0.5)}): Close strangle"
                    ))
                    closed_gamma += symbol_gamma

        # --- PRIORITY 2: Close profitable positions (profit take + recycle) ---
        for idx, pos in account_positions.iterrows():
            if pd.notna(pos.get('premium_received')) and pos.get('premium_received', 0) > 0:
                if pd.notna(pos.get('mark_price')):
                    profit_pct = ((pos['premium_received'] - pos['mark_price']) / pos['premium_received'] * 100) if pos['premium_received'] > 0 else 0
                    if profit_pct >= 50:  # 50%+ profit
                        trades.append(AccountTrade(
                            account=account_name,
                            priority=2,
                            action='CLOSE',
                            symbol=str(pos['symbol']),
                            strike_call=pos.get('strike'),
                            qty=abs(int(pos.get('qty', 1))),
                            expected_premium=pos.get('mark_price', 0),
                            reason=f"Profit take ({profit_pct:.0f}%): Close, redeploy capital"
                        ))

        # --- PRIORITY 2: Fill THETA gap ---
        if theta_gap:
            theta_needed = targets.get('theta_target', 200) - theta
            num_strangles = max(1, int(theta_needed / 15))  # ~$15 theta per strangle

            # Recommend Tier 1 names with available capacity
            for i, symbol in enumerate(DailyTradeExecutor.TIER_1[:num_strangles]):
                if i >= 3:  # Max 3 new entries per account per day
                    break

                # Check if symbol already at max contracts for this account
                existing_count = len(account_positions[account_positions['symbol'].astype(str).str.contains(symbol, na=False)])
                max_allowed = targets.get('max_contracts_tier1', 1)

                if existing_count < max_allowed:
                    trades.append(AccountTrade(
                        account=account_name,
                        priority=2,
                        action='ENTER',
                        symbol=symbol,
                        strike_put=None,  # Will be market-dependent
                        strike_call=None,
                        dte=45,
                        qty=1,
                        expected_premium=300,  # Rough estimate
                        delta_impact=-0.15,
                        gamma_impact=0.05,
                        theta_impact=15,
                        reason=f"THETA gap ({theta:+.0f} < {targets.get('theta_target', 200)}): Add CSP/strangle"
                    ))

        return trades

    @staticmethod
    def generate_daily_execution_report(
        positions_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        output_file: str = None
    ) -> str:
        """Generate complete daily execution report for all accounts."""

        greeks_calc = GreeksCalculator()

        output = []
        output.append("╔" + "═" * 80 + "╗")
        output.append(f"║ DAILY TRADE EXECUTION REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M ET'):60} ║")
        output.append("╚" + "═" * 80 + "╝")
        output.append("")

        # Get market regime & screener universe
        output.append("PORTFOLIO STRATEGY CONTEXT")
        output.append("=" * 80)
        output.append("")

        # Note: Market regime would come from theta-lab MCP in production
        # For now, use hardcoded based on trading_persona
        market_regime = "BEAR_SIDEWAYS"
        allow_new_entries = False
        output.append(f"Market Regime: {market_regime}")
        output.append(f"New Entries Allowed: {allow_new_entries}")
        output.append("")

        # Get screener universe (Holdings that pass regime filters)
        universe = ScreenerLoader.get_current_holdings_universe(
            market_regime=market_regime,
            allow_new_entries=allow_new_entries,
            exclude_tier3=False
        )
        output.append(f"Holdings Universe (regime-filtered): {len(universe)} eligible names")
        output.append(f"  Tier 1 (Core): {sum(1 for m in universe.values() if m['tier']==1)}")
        output.append(f"  Tier 2 (Emerging): {sum(1 for m in universe.values() if m['tier']==2)}")
        output.append(f"  Tier 3 (Speculative): {sum(1 for m in universe.values() if m['tier']==3)}")
        output.append("")

        output.append("ACTION SUMMARY (Execute in this order)")
        output.append("=" * 80)
        output.append("")

        # Process each account (dynamic — find all accounts in positions_df)
        all_trades = []
        all_accounts = sorted([acc for acc in positions_df['account'].unique()
                               if pd.notna(acc) and acc in DailyTradeExecutor.ACCOUNT_TARGETS])

        for account in all_accounts:
            account_pos = positions_df[positions_df['account'] == account]

            if account_pos.empty:
                continue

            # Get Greeks for this account
            portfolio_greeks = greeks_calc.aggregate_to_portfolio(account_pos)

            # Get recommendations
            account_trades = DailyTradeExecutor.get_account_recommendations(
                account,
                account_pos,
                portfolio_greeks.__dict__,
                positions_df
            )

            for trade in account_trades:
                all_trades.append(trade)

        # Sort by priority
        all_trades.sort(key=lambda x: (x.priority, x.account))

        # Display by priority
        for priority in [1, 2]:
            priority_trades = [t for t in all_trades if t.priority == priority]

            if priority == 1:
                output.append("🔴 PRIORITY 1 — EXECUTE TODAY (Before market open or in first hour)")
                output.append("-" * 80)
            else:
                output.append("🟡 PRIORITY 2 — THIS WEEK (Execute if market allows)")
                output.append("-" * 80)

            trade_num = 1
            for trade in priority_trades:
                output.append("")
                output.append(f"{priority_trades.index(trade) + 1}. {trade.action}: {trade.symbol}")
                output.append(f"   Account: {trade.account}")

                if trade.action == 'ENTER':
                    output.append(f"   Action: SELL {trade.symbol} STRANGLE")
                    output.append(f"   DTE: {trade.dte} days (45-60 DTE range)")
                    output.append(f"   Strikes: PUT ~85% of current, CALL ~115% of current")
                    output.append(f"   Qty: {trade.qty} contract(s)")
                    output.append(f"   Expected premium: ${trade.expected_premium:,.0f}")

                elif trade.action == 'CLOSE':
                    output.append(f"   Action: BUY TO CLOSE")
                    output.append(f"   Strike: ${trade.strike_put or trade.strike_call:.2f}" if trade.strike_put or trade.strike_call else "")
                    output.append(f"   Qty: {trade.qty} contract(s)")

                elif trade.action == 'ROLL':
                    output.append(f"   Action: ROLL OUT+DOWN")
                    output.append(f"   New DTE: {trade.dte} days")
                    output.append(f"   Expected credit: ${trade.expected_premium:,.0f}")

                elif trade.action == 'CLOSE_STRANGLE':
                    output.append(f"   Action: CLOSE ENTIRE STRANGLE (both PUT and CALL)")
                    output.append(f"   Qty: {trade.qty} complete strangle(s)")

                output.append(f"   Why: {trade.reason}")
                output.append(f"   Expected Greeks impact:")
                output.append(f"     Δ {trade.delta_impact:+.2f}  Γ {trade.gamma_impact:+.3f}  Θ {trade.theta_impact:+.0f}/day")

        # Account-level summary
        output.append("")
        output.append("=" * 80)
        output.append("ACCOUNT-LEVEL STATUS & TARGETS")
        output.append("=" * 80)
        output.append("")

        for account in all_accounts:
            account_pos = positions_df[positions_df['account'] == account].copy()

            if account_pos.empty:
                output.append(f"{account}: NO POSITIONS")
                output.append("")
                continue

            # Initialize heat column if not present
            if 'heat' not in account_pos.columns:
                if 'distance_to_strike_pct' in account_pos.columns:
                    account_pos['heat'] = account_pos['distance_to_strike_pct'].apply(
                        lambda x: '🔴 RED' if pd.notna(x) and x < 0.10 else ('🟡 YELLOW' if pd.notna(x) and x < 0.20 else '🟢 GREEN')
                    )
                else:
                    account_pos['heat'] = '🟢 GREEN'

            portfolio_greeks = greeks_calc.aggregate_to_portfolio(account_pos)
            targets = DailyTradeExecutor.ACCOUNT_TARGETS.get(account, {})

            output.append(f"{account}:")
            output.append(f"  Positions: {len(account_pos)} open | Heat: 🔴{len(account_pos[account_pos['heat']=='🔴 RED'])} 🟡{len(account_pos[account_pos['heat']=='🟡 YELLOW'])} 🟢{len(account_pos[account_pos['heat']=='🟢 GREEN'])}")
            output.append("")

            # Greeks status
            delta_ok = abs(portfolio_greeks.delta) <= targets.get('delta_target', 20)
            gamma_ok = portfolio_greeks.gamma <= targets.get('gamma_target', 0.5)
            theta_ok = portfolio_greeks.theta >= targets.get('theta_target', 200)

            output.append(f"  Greeks (Current → Target):")
            output.append(f"    Delta:  {portfolio_greeks.delta:+7.2f}  → Target ±{targets.get('delta_target', 20):5.0f}  {'✅' if delta_ok else '❌'}")
            output.append(f"    Gamma:  {portfolio_greeks.gamma:+7.3f}  → Target ≤{targets.get('gamma_target', 0.5):5.1f}  {'✅' if gamma_ok else '❌'}")
            output.append(f"    Theta:  {portfolio_greeks.theta:+7.0f}/day → Target ≥${targets.get('theta_target', 200):5.0f}  {'✅' if theta_ok else '❌'}")
            output.append("")

            # Trades for this account
            account_trades = [t for t in all_trades if t.account == account]
            if account_trades:
                output.append(f"  Trades to execute: {len(account_trades)}")
                for i, trade in enumerate(account_trades[:5], 1):  # Show top 5
                    output.append(f"    {i}. {trade.action} {trade.symbol} (Priority {trade.priority})")
            else:
                output.append(f"  Trades needed: None (all Greeks in range)")

            output.append("")

        # Equity-level thesis validation section
        output.append("=" * 80)
        output.append("EQUITY-LEVEL THESIS VALIDATION")
        output.append("=" * 80)
        output.append("")
        output.append("Current positions vs Holdings universe:")
        output.append("")

        # Sample thesis validation for key positions
        sample_positions = ['PYPL', 'ADBE', 'AXON', 'CRM']
        for symbol in sample_positions:
            thesis = ScreenerLoader.validate_position_thesis(symbol)
            tier = ScreenerLoader.get_tier(symbol)
            moat = ScreenerLoader.get_moat_strength(symbol)

            status_emoji = {'GREEN': '✅', 'YELLOW': '⚠️', 'RED': '❌'}.get(thesis['status'], '?')
            output.append(f"{status_emoji} {symbol:10} Tier {tier} | Moat: {moat}")
            output.append(f"   {thesis['reason']}")
            output.append(f"   → {thesis['action']}")

            # If RED, show alternatives
            if thesis['status'] == 'RED':
                alts = ScreenerLoader.get_alternatives_for_position(
                    symbol,
                    market_regime=market_regime,
                    max_alternatives=3
                )
                output.append(f"   Suggested alternatives (screener-eligible):")
                for i, (alt_sym, alt_meta) in enumerate(alts, 1):
                    output.append(f"     {i}. {alt_sym:10} Tier {alt_meta['tier']} | {alt_meta['moat_strength']}")

            output.append("")

        # Execution mechanics
        output.append("=" * 80)
        output.append("EXECUTION MECHANICS")
        output.append("=" * 80)
        output.append("")
        output.append("1. CLOSE / BUY TO CLOSE:")
        output.append("   - Enter as BUY TO CLOSE order")
        output.append("   - Good-til-Canceled (GTC) limit order")
        output.append("   - Limit price: mid-market bid/ask")
        output.append("")
        output.append("2. ENTER / SELL STRANGLE:")
        output.append("   - Check IVR first (must be ≥40 for Account A)")
        output.append("   - Sell PUT at ~delta 0.15 (85% of current price)")
        output.append("   - Sell CALL at ~delta 0.20 (115% of current price)")
        output.append("   - DTE: 45-60 days")
        output.append("   - GTC limit order, target $200-400 net credit")
        output.append("")
        output.append("3. ROLL:")
        output.append("   - Close current position at market")
        output.append("   - Immediately sell new position at further DTE")
        output.append("   - Target: Same strikes or adjusted, net credit ≥$100")
        output.append("")

        # Post-execution checklist
        output.append("=" * 80)
        output.append("POST-EXECUTION CHECKLIST")
        output.append("=" * 80)
        output.append("")
        output.append("After executing trades:")
        output.append("  [ ] Record each trade in trading log (date, symbol, qty, price, reason)")
        output.append("  [ ] Verify new Greeks in broker platform")
        output.append("  [ ] Check Greeks vs targets — are we back in range?")
        output.append("  [ ] Update positions spreadsheet")
        output.append("  [ ] Notify Account stakeholders (Account A = you, B = Pinky, C = ?)")
        output.append("")

        output.append("=" * 80)
        output.append("END OF REPORT")
        output.append("=" * 80)

        report = "\n".join(output)

        if output_file:
            from pathlib import Path
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"✅ Saved: {output_file}")

        return report


if __name__ == "__main__":
    # Load data
    positions_df, transactions_df = DynamicDataLoader.load_all_data(
        positions_dir="data/positions",
        statements_dir="data/statements",
        use_live_positions=True,
        calculate_greeks=True
    )

    # Generate report
    output_file = f"logs/daily_trade_execution_{datetime.now().strftime('%Y-%m-%d')}.txt"
    report = DailyTradeExecutor.generate_daily_execution_report(positions_df, transactions_df, output_file)

    print(report)
