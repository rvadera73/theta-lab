"""
Attribution Tracker — Break down P&L by source.

Attribution sources:
  1. Theta decay (time value capture)
  2. Vega capture (IV rank timing)
  3. Delta moves (directional exposure)
  4. Gamma realization (convexity)
  5. Roll credits (redeployment alpha)
  6. Slippage (bid-ask spread costs)
  7. Assignment impact (forced closure losses)
"""

import pandas as pd
from datetime import date, timedelta
from typing import Dict
from dataclasses import dataclass

@dataclass
class Attribution:
    """P&L attribution breakdown."""
    period: str  # "YTD", "2026-05", etc.
    total_pnl: float

    theta_decay: float
    vega_capture: float
    delta_moves: float
    gamma_realization: float
    roll_credits: float
    slippage: float
    assignment_impact: float


class AttributionTracker:
    """Track and report P&L attribution."""

    def calculate_attribution(self, transactions_df: pd.DataFrame) -> Attribution:
        """
        Break down P&L into attribution sources.

        Works with any transaction format. Sums amounts to get total P&L,
        then attributes based on heuristic assumptions.
        """

        if transactions_df.empty:
            return Attribution(
                period=f"{date.today().year}-{date.today().month:02d}",
                total_pnl=0,
                theta_decay=0, vega_capture=0, delta_moves=0,
                gamma_realization=0, roll_credits=0, slippage=0, assignment_impact=0
            )

        # Calculate total YTD P&L from transactions (sum of net amounts)
        if 'amount' in transactions_df.columns:
            total_pnl = transactions_df['amount'].sum()
        elif 'net_amount' in transactions_df.columns:
            total_pnl = transactions_df['net_amount'].sum()
        else:
            # Try any numeric column
            numeric_cols = transactions_df.select_dtypes(include=['number']).columns
            total_pnl = transactions_df[numeric_cols[0]].sum() if len(numeric_cols) > 0 else 0

        if total_pnl == 0:
            return Attribution(
                period=f"{date.today().year}-{date.today().month:02d}",
                total_pnl=0,
                theta_decay=0, vega_capture=0, delta_moves=0,
                gamma_realization=0, roll_credits=0, slippage=0, assignment_impact=0
            )

        # Simple heuristic attribution (can be improved with historical Greeks)
        # Assumption: 70% theta (time decay), 20% vega (IV timing), 10% other
        theta_decay = total_pnl * 0.70
        vega_capture = total_pnl * 0.20
        roll_credits = total_pnl * 0.10

        # Slippage estimate: assume 1-2% of PnL is cost
        slippage = -abs(total_pnl) * 0.02  # negative (cost)

        return Attribution(
            period=f"{date.today().year}-{date.today().month:02d}",
            total_pnl=total_pnl,
            theta_decay=theta_decay,
            vega_capture=vega_capture,
            delta_moves=0,  # Placeholder
            gamma_realization=0,
            roll_credits=roll_credits,
            slippage=slippage,
            assignment_impact=0
        )

    def generate_report(self, attribution: Attribution) -> str:
        """Generate formatted attribution report."""

        output = []
        output.append("=" * 70)
        output.append(f"ATTRIBUTION REPORT — {attribution.period}")
        output.append("=" * 70)
        output.append("")

        total = attribution.total_pnl
        if total == 0:
            output.append("No closed trades this period.")
            return "\n".join(output)

        output.append(f"GROSS P&L: ${total:,.0f}\n")

        # Attribution breakdown
        sources = [
            ("Theta decay (time value)", attribution.theta_decay),
            ("Vega capture (IV timing)", attribution.vega_capture),
            ("Delta moves (directional)", attribution.delta_moves),
            ("Gamma realization (convexity)", attribution.gamma_realization),
            ("Roll credits (redeployment)", attribution.roll_credits),
            ("Slippage (bid-ask)", attribution.slippage),
            ("Assignment impact", attribution.assignment_impact),
        ]

        for source, amount in sources:
            pct = (amount / total * 100) if total != 0 else 0
            output.append(f"{source:40} ${amount:>10,.0f}  {pct:>6.1f}%")

        output.append("\n" + "=" * 70)

        return "\n".join(output)
