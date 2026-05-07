"""
Position Detail Report — Transaction & Account Level Visibility

Shows:
1. Every open position with current Greeks, heat, P&L
2. Which positions are breaching guardrails
3. Recommended action per position (CLOSE, ROLL, HOLD, ENTER)
4. Account-level summary with utilization
5. Specific trades to execute (strike, qty, DTE, expected credit/debit)
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from data_loader import DynamicDataLoader
from greeks_calculator import GreeksCalculator
from thesis_state_tracker import ThesisStateTracker
from screener_loader import ScreenerLoader


class PositionDetailAnalyzer:
    """Analyze positions at transaction and account level."""

    @staticmethod
    def enrich_positions_with_signals(positions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add signal columns to each position:
        - HEAT (RED/YELLOW/GREEN)
        - P&L status (WINNING/LOSING)
        - RECOMMENDED ACTION (CLOSE/ROLL/HOLD/ENTER)
        - PRIORITY (1=urgent, 2=this week, 3=monitor)
        """
        positions = positions_df.copy()

        # Heat signal (distance to strike as % of current price)
        if 'distance_to_strike_pct' in positions.columns:
            positions['heat'] = positions['distance_to_strike_pct'].apply(
                lambda x: '🔴 RED' if pd.notna(x) and x < 0.10 else ('🟡 YELLOW' if pd.notna(x) and x < 0.20 else '🟢 GREEN')
            )
        else:
            positions['heat'] = '🟢 GREEN'

        # P&L signal (estimate from available columns)
        if 'current_value' in positions.columns:
            positions['pnl_status'] = positions['current_value'].apply(
                lambda x: 'WINNING' if pd.notna(x) and x > 0 else ('LOSING' if pd.notna(x) and x < 0 else 'NEUTRAL')
            )
        else:
            positions['pnl_status'] = 'NEUTRAL'

        # Greeks signal - identify breaches at position level
        positions['delta_signal'] = positions['delta'].apply(
            lambda x: '⚠️ LONG' if x > 0.8 else ('⚠️ SHORT' if x < -0.8 else '✅ NEUTRAL')
        )
        positions['gamma_signal'] = positions['gamma'].apply(
            lambda x: '⚠️ HIGH' if x > 0.15 else '✅ LOW'
        )
        positions['theta_signal'] = positions['theta'].apply(
            lambda x: '✅ DECAY' if x > 0 else '❌ LOSING'
        )

        # Recommended action per position
        def get_action(row):
            # RED = close immediately
            if row.get('heat') == '🔴 RED' and row.get('pnl_status') == 'WINNING':
                return 'CLOSE (ITM, collect profit)'
            elif row.get('heat') == '🔴 RED' and row.get('pnl_status') == 'LOSING':
                return 'ROLL (down+out, reduce loss)'

            # YELLOW = monitor/prepare roll
            elif row.get('heat') == '🟡 YELLOW':
                if row.get('dte', 999) < 21:
                    return 'ROLL (approaching expiry)'
                else:
                    return 'MONITOR (prepare roll if moves breach)'

            # GREEN = let it run
            else:
                if row.get('theta_signal') == '✅ DECAY':
                    return 'HOLD (let theta decay)'
                else:
                    return 'MONITOR'

        positions['recommended_action'] = positions.apply(get_action, axis=1)

        # Priority
        def get_priority(action):
            if 'CLOSE' in action or 'ROLL' in action:
                return 1
            elif 'MONITOR' in action and 'prepare' in action:
                return 2
            else:
                return 3

        positions['priority'] = positions['recommended_action'].apply(get_priority)

        return positions

    @staticmethod
    def generate_position_detail_report(
        positions_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        output_file: str = None
    ) -> str:
        """Generate detailed position report."""

        # Initialize thesis tracker
        thesis_tracker = ThesisStateTracker()

        positions = PositionDetailAnalyzer.enrich_positions_with_signals(positions_df)

        # Enrich with thesis data for each position
        if not positions.empty and 'symbol' in positions.columns:
            thesis_data = {}
            for symbol in positions['symbol'].dropna().unique():
                symbol = str(symbol).upper()
                pos = positions[positions['symbol'] == symbol].iloc[0]

                # Validate thesis
                thesis_result = ScreenerLoader.validate_position_thesis(
                    symbol=symbol,
                    current_price=pos.get('current_price'),
                    last_earnings_beat=pos.get('earnings_beat', True),
                    guidance_cuts=int(pos.get('guidance_cuts', 0))
                )

                tier = ScreenerLoader.get_tier(symbol)
                moat = ScreenerLoader.get_moat_strength(symbol)
                conviction = int(pos.get('conviction', 5))

                # Update thesis state
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

                thesis_data[symbol] = {
                    'status': thesis_result['status'],
                    'conviction': conviction,
                    'moat': moat,
                    'tier': tier,
                    'alternatives': [alt[0] for alt in ScreenerLoader.get_alternatives_for_position(symbol)[:3]]
                }

            # Add thesis columns
            positions['thesis_status'] = positions['symbol'].apply(
                lambda x: thesis_data.get(str(x).upper(), {}).get('status', 'UNKNOWN') if pd.notna(x) else 'UNKNOWN'
            )
            positions['conviction'] = positions['symbol'].apply(
                lambda x: thesis_data.get(str(x).upper(), {}).get('conviction', 0) if pd.notna(x) else 0
            )
            positions['moat'] = positions['symbol'].apply(
                lambda x: thesis_data.get(str(x).upper(), {}).get('moat', 'UNKNOWN') if pd.notna(x) else 'UNKNOWN'
            )
            positions['tier'] = positions['symbol'].apply(
                lambda x: thesis_data.get(str(x).upper(), {}).get('tier', 0) if pd.notna(x) else 0
            )
            positions['alternatives'] = positions['symbol'].apply(
                lambda x: thesis_data.get(str(x).upper(), {}).get('alternatives', []) if pd.notna(x) else []
            )

        output = []
        output.append("╔" + "═" * 68 + "╗")
        output.append(f"║ POSITION DETAIL REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M')} ║")
        output.append("╚" + "═" * 68 + "╝")
        output.append("")

        # 1. ACCOUNT-LEVEL SUMMARY
        output.append("1. ACCOUNT-LEVEL SUMMARY")
        output.append("-" * 70)
        output.append("")

        for account in sorted(positions['account'].unique()):
            if pd.isna(account):
                continue

            account_df = positions[positions['account'] == account]

            if account_df.empty:
                continue

            # Safe aggregations
            total_qty = account_df['qty'].sum() if 'qty' in account_df.columns else 0
            total_pnl = account_df['current_value'].sum() if 'current_value' in account_df.columns else 0
            red_count = len(account_df[account_df['heat'] == '🔴 RED'])
            yellow_count = len(account_df[account_df['heat'] == '🟡 YELLOW'])
            green_count = len(account_df[account_df['heat'] == '🟢 GREEN'])

            delta_sum = account_df['delta'].sum() if 'delta' in account_df.columns else 0
            gamma_sum = account_df['gamma'].sum() if 'gamma' in account_df.columns else 0
            theta_sum = account_df['theta'].sum() if 'theta' in account_df.columns else 0

            output.append(f"{account}:")
            output.append(f"  Positions: {len(account_df)} | Qty: {total_qty:+.0f} | P&L: ${total_pnl:+,.0f}")
            output.append(f"  Heat: 🔴{red_count} 🟡{yellow_count} 🟢{green_count}")
            output.append(f"  Greeks: δ={delta_sum:+.2f} γ={gamma_sum:+.3f} θ={theta_sum:+.0f}/day")
            output.append("")

        # 2. PRIORITY ACTIONS (Priority 1 = Urgent)
        output.append("2. PRIORITY ACTIONS (URGENT)")
        output.append("-" * 70)
        output.append("")

        priority_1 = positions[positions['priority'] == 1].sort_values('priority')
        if not priority_1.empty:
            for idx, pos in priority_1.iterrows():
                output.append(f"🔴 {pos['symbol']:20} {pos['recommended_action']}")
                output.append(f"    Thesis: {pos.get('thesis_status', 'UNKNOWN')} | Conviction {pos.get('conviction', 0)}/10 | {pos.get('moat', 'UNKNOWN')} moat")
                output.append(f"    Current: {pos['delta']:+.3f}δ {pos['gamma']:+.4f}γ")
                output.append(f"    Heat: {pos['heat']:15} | P&L: ${pos['current_value']:+,.0f}")

                # Show alternatives for RED thesis positions
                if pos.get('thesis_status') == 'RED' and pos.get('alternatives'):
                    alts = pos.get('alternatives', [])
                    output.append(f"    Redeploy to: {', '.join(alts[:3])}")
                output.append("")
        else:
            output.append("  ✅ No urgent actions")
            output.append("")

        # 3. THIS WEEK (Priority 2)
        output.append("3. THIS WEEK (MONITOR & PREPARE)")
        output.append("-" * 70)
        output.append("")

        priority_2 = positions[positions['priority'] == 2].sort_values('dte')
        if not priority_2.empty:
            for idx, pos in priority_2.head(10).iterrows():
                output.append(f"🟡 {pos['symbol']:20} DTE:{pos.get('dte', 'N/A')}")
                output.append(f"    Thesis: {pos.get('thesis_status', 'UNKNOWN')} | Conviction {pos.get('conviction', 0)}/10")
                output.append(f"    Action: {pos['recommended_action']}")
                output.append(f"    Greeks: δ={pos['delta']:+.3f} γ={pos['gamma']:+.4f} θ={pos['theta']:+.0f}")
                output.append("")
        else:
            output.append("  ✅ No positions need preparation this week")
            output.append("")

        # 4. HEALTHY POSITIONS (Priority 3 = Let Run)
        output.append("4. HEALTHY POSITIONS (LET DECAY)")
        output.append("-" * 70)
        output.append("")

        priority_3 = positions[positions['priority'] == 3]
        theta_total = priority_3['theta'].sum()
        output.append(f"Count: {len(priority_3)} positions generating ${theta_total:+.0f}/day theta decay")
        output.append(f"Action: Monitor daily, let time value decay")
        output.append("")

        # 5. CLOSING CANDIDATES (Positions at 50%+ profit)
        output.append("5. PROFIT-TAKE CANDIDATES (≥50% of max profit)")
        output.append("-" * 70)
        output.append("")

        # Estimate profit % for each position
        # For short options: profit % = (premium_received - current_mark) / premium_received * 100
        closing_candidates = []
        for idx, pos in positions.iterrows():
            if pd.notna(pos.get('premium_received')) and pos.get('premium_received', 0) > 0:
                if pd.notna(pos.get('mark_price')):
                    profit_pct = ((pos['premium_received'] - pos['mark_price']) / pos['premium_received'] * 100) if pos['premium_received'] > 0 else 0
                    if profit_pct >= 50:  # 50%+ profit
                        closing_candidates.append({
                            'symbol': pos['symbol'],
                            'profit_pct': profit_pct,
                            'pnl': pos['current_value'],
                            'account': pos['account']
                        })

        if closing_candidates:
            candidates_df = pd.DataFrame(closing_candidates).sort_values('profit_pct', ascending=False)
            for idx, cand in candidates_df.head(10).iterrows():
                output.append(f"✅ {cand['symbol']:20} {cand['profit_pct']:5.0f}% profit → Close for ${cand['pnl']:+,.0f}")
            output.append(f"\nTotal closeable P&L: ${candidates_df['pnl'].sum():+,.0f}")
        else:
            output.append("  None yet - wait for more decay")

        output.append("")

        # 6. NEW ENTRY OPPORTUNITIES (by account, showing available capacity)
        output.append("6. CAPACITY FOR NEW ENTRIES (by account)")
        output.append("-" * 70)
        output.append("")

        # Get Holdings universe for entry suggestions
        holdings_universe = ScreenerLoader.get_current_holdings_universe(
            market_regime='BEAR_SIDEWAYS',
            allow_new_entries=False,
            exclude_tier3=False
        )

        for account in sorted(positions['account'].unique()):
            account_df = positions[positions['account'] == account]
            account_theta = account_df['theta'].sum()
            current_symbols = set(account_df['symbol'].dropna().str.upper().unique())

            if account_theta < 300:
                needed_theta = 300 - account_theta
                # Find available Tier 1/2 candidates not yet in this account
                available_tier1 = [s for s, m in holdings_universe.items() if m['tier'] == 1 and s not in current_symbols]
                available_tier2 = [s for s, m in holdings_universe.items() if m['tier'] == 2 and s not in current_symbols]

                output.append(f"{account}:")
                output.append(f"  Current theta: ${account_theta:+.0f}/day")
                output.append(f"  Need: ${needed_theta:.0f} more theta → Enter 2-3 new CSPs/strangles")
                if available_tier1:
                    output.append(f"  Tier 1 candidates: {', '.join(available_tier1[:3])}")
                if available_tier2:
                    output.append(f"  Tier 2 candidates: {', '.join(available_tier2[:3])}")
                output.append("")
            else:
                output.append(f"{account}: ✅ Theta target met ({account_theta:.0f}/day)")
                output.append("")

        output.append("=" * 70)

        report = "\n".join(output)

        if output_file:
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
    output_file = f"logs/position_detail_report_{datetime.now().strftime('%Y-%m-%d')}.txt"
    report = PositionDetailAnalyzer.generate_position_detail_report(positions_df, transactions_df, output_file)

    print(report)
