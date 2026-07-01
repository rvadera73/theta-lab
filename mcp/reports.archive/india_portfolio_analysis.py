"""
India Portfolio Analysis
Equity + FNO (ICICI Direct Accounts)
Account 1: 7500069840 (Equity)
Account 2: 7510078170 (FNO Options)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Tuple

class IndiaPortfolioAnalyzer:
    """Analyze India stock + F&O portfolio"""

    def __init__(self):
        self.data_dir = Path('/home/rahulvadera/projects/theta-lab/data/positions')
        self.equity_df = None
        self.fno_df = None
        self.load_data()

    def load_data(self):
        """Load equity and FNO data"""
        # Load equity portfolio
        equity_file = self.data_dir / '7500069840_PortFolioEqtSummary.csv'
        if equity_file.exists():
            self.equity_df = pd.read_csv(equity_file, skiprows=0)
            print(f"✓ Loaded equity portfolio: {len(self.equity_df)} positions")

        # Load FNO portfolio
        fno_file = None
        for f in self.data_dir.glob('*FNO*'):
            if f.suffix == '.csv' and 'Zone' not in f.name:
                fno_file = f
                break

        if fno_file:
            # FNO file structure is different - has multiple sections
            with open(fno_file, 'r') as f:
                lines = f.readlines()

            # Find the Options section and parse it
            options_section = []
            in_options = False
            for line in lines:
                if 'Options,' in line:
                    in_options = True
                    continue
                if in_options and line.strip():
                    options_section.append(line.strip())

            # Create FNO dataframe from options section
            if len(options_section) > 1:
                # Parse header and data
                from io import StringIO
                options_data = '\n'.join(options_section)
                try:
                    self.fno_df = pd.read_csv(StringIO(options_data))
                    self.fno_df = self.fno_df[self.fno_df['Open Position Qty'] != 0]  # Active positions only
                    print(f"✓ Loaded F&O portfolio: {len(self.fno_df)} active positions")
                except:
                    print("Note: F&O parsing encountered format issues, using raw data")

    def analyze_equity(self) -> Dict:
        """Analyze equity portfolio"""
        if self.equity_df is None:
            return {}

        df = self.equity_df.copy()

        # Clean numeric columns
        for col in ['Value At Market Price', 'Unrealized Profit/Loss', 'Unrealized Profit/Loss %']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        total_market_value = df['Value At Market Price'].sum()
        total_pl = df['Unrealized Profit/Loss'].sum()
        total_pl_pct = (total_pl / df['Value At Cost'].sum() * 100) if df['Value At Cost'].sum() > 0 else 0

        # Segment by sector (inferred from company name)
        sectors = self._categorize_sectors()

        return {
            'positions': len(df),
            'total_value': total_market_value,
            'total_unrealized_pl': total_pl,
            'total_unrealized_pl_pct': total_pl_pct,
            'holdings': df,
            'sectors': sectors
        }

    def _categorize_sectors(self) -> Dict:
        """Categorize holdings by sector"""
        sector_map = {
            'HDFBAN': 'Banking & Finance',
            'STABAN': 'Banking & Finance',
            'BAJFI': 'Banking & Finance',
            'SOLIN': 'Energy & Infrastructure',
            'ADAPOW': 'Energy & Infrastructure',
            'NTPC': 'Energy & Infrastructure',
            'RELIND': 'Energy & Infrastructure',
            'DLFLIM': 'Realty & Construction',
            'HINAER': 'Defense & Aerospace',
            'PARDEF': 'Defense & Aerospace',
            'MAZDOC': 'Defense & Aerospace',
            'BHAELE': 'Defense & Aerospace',
            'TCS': 'Technology & IT',
            'DRREDD': 'Pharmaceuticals & Healthcare',
            'APOHOS': 'Pharmaceuticals & Healthcare',
            'YATHOS': 'Pharmaceuticals & Healthcare',
            'ADAPOR': 'Logistics & Ports',
            'ZOMLIM': 'Other',
        }
        return sector_map

    def analyze_fno(self) -> Dict:
        """Analyze F&O positions"""
        if self.fno_df is None or len(self.fno_df) == 0:
            return {'active_positions': 0}

        df = self.fno_df.copy()

        # Filter active positions
        active = df[df['Open Position Qty'] != 0]

        # Parse contract details
        contracts = []
        for _, row in active.iterrows():
            contract = row['Contract']
            try:
                parts = contract.split('-')
                symbol = parts[1]  # e.g., CNXBAN, NIFSEL
                strike = int(parts[4])
                expiry = parts[2]
                option_type = parts[5]  # P or C
                contracts.append({
                    'symbol': symbol,
                    'strike': strike,
                    'expiry': expiry,
                    'type': option_type,
                    'qty': row['Open Position Qty'],
                    'value': row['Open Position Value'],
                    'pl': row['Profit/Loss Unrealized']
                })
            except:
                pass

        total_notional = df['Open Position Value'].sum()
        total_pl = df['Profit/Loss Unrealized'].sum()

        return {
            'active_positions': len(active),
            'total_notional': total_notional,
            'total_pl': total_pl,
            'contracts': contracts
        }

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        output = []
        today = date.today()

        output.append("=" * 110)
        output.append("INDIA PORTFOLIO ANALYSIS REPORT")
        output.append(f"ICICI Direct — 2 Accounts (Equity + F&O)")
        output.append(f"Generated: {today.strftime('%B %d, %Y')}")
        output.append("=" * 110)
        output.append("")

        # Equity Analysis
        equity = self.analyze_equity()
        output.extend(self._format_equity_section(equity))

        # F&O Analysis
        fno = self.analyze_fno()
        output.extend(self._format_fno_section(fno))

        # Combined Summary
        output.extend(self._format_summary(equity, fno))

        return "\n".join(output)

    def _format_equity_section(self, equity: Dict) -> List[str]:
        """Format equity portfolio section"""
        output = []
        output.append("")
        output.append("=" * 110)
        output.append("ACCOUNT 1: EQUITY PORTFOLIO (7500069840)")
        output.append("=" * 110)
        output.append("")

        if not equity:
            output.append("No equity data available")
            return output

        df = equity['holdings'].copy()

        output.append(f"PORTFOLIO SUMMARY:")
        output.append(f"├─ Total Positions: {equity['positions']}")
        output.append(f"├─ Total Market Value: ₹{equity['total_value']:,.0f}")
        output.append(f"├─ Unrealized P&L: ₹{equity['total_unrealized_pl']:,.0f} ({equity['total_unrealized_pl_pct']:+.2f}%)")
        output.append(f"└─ Status: {'🟢 PROFITABLE' if equity['total_unrealized_pl'] > 0 else '🔴 LOSS'}")
        output.append("")

        # Top holdings
        output.append("TOP 10 HOLDINGS BY MARKET VALUE:")
        output.append("-" * 110)
        output.append(f"{'Stock':12} {'Company':40} {'Qty':>6} {'Avg Cost':>10} {'CMP':>10} {'Change':>10} {'Value':>15} {'P&L':>12} {'P&L %':>10}")
        output.append("-" * 110)

        top_holdings = df.nlargest(10, 'Value At Market Price')
        for _, row in top_holdings.iterrows():
            stock = row['Stock Symbol']
            company = row['Company Name'][:38]
            qty = int(row['Qty'])
            avg_cost = float(row['Average Cost Price'])
            cmp = float(row['Current Market Price'])
            change = row['% Change over prev close']
            value = float(row['Value At Market Price'])
            pl = float(row['Unrealized Profit/Loss'])
            pl_pct = float(str(row['Unrealized Profit/Loss %']).replace('(', '-').replace(')', ''))

            output.append(f"{stock:12} {company:40} {qty:>6} ₹{avg_cost:>9.2f} ₹{cmp:>9.2f} {str(change):>10} ₹{value:>14,.0f} ₹{pl:>11,.0f} {pl_pct:>9.2f}%")

        output.append("")

        # Sector breakdown
        output.append("SECTOR BREAKDOWN:")
        output.append("-" * 110)

        sector_values = {}
        for _, row in df.iterrows():
            stock = row['Stock Symbol']
            value = float(row['Value At Market Price'])
            sector_map = equity['sectors']
            sector = sector_map.get(stock, 'Other')
            sector_values[sector] = sector_values.get(sector, 0) + value

        total_value = equity['total_value']
        for sector, value in sorted(sector_values.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * value / total_value
            bar = "█" * int(pct / 2)
            output.append(f"{sector:35} ₹{value:>12,.0f} ({pct:>5.1f}%) {bar}")

        output.append("")
        return output

    def _format_fno_section(self, fno: Dict) -> List[str]:
        """Format F&O portfolio section"""
        output = []
        output.append("=" * 110)
        output.append("ACCOUNT 2: F&O PORTFOLIO (7510078170)")
        output.append("=" * 110)
        output.append("")

        if fno['active_positions'] == 0:
            output.append("No active F&O positions")
            output.append("")
            return output

        output.append(f"F&O SUMMARY:")
        output.append(f"├─ Active Positions: {fno['active_positions']}")
        output.append(f"├─ Total Notional: ₹{fno['total_notional']:,.0f}")
        output.append(f"├─ Unrealized P&L: ₹{fno['total_pl']:,.0f}")
        output.append(f"└─ Status: {'🟢 PROFITABLE' if fno['total_pl'] > 0 else '🔴 LOSS'}")
        output.append("")

        # Organize by symbol and expiry
        if fno['contracts']:
            output.append("ACTIVE POSITIONS BY INDEX:")
            output.append("-" * 110)

            contracts_by_symbol = {}
            for c in fno['contracts']:
                symbol = c['symbol']
                if symbol not in contracts_by_symbol:
                    contracts_by_symbol[symbol] = []
                contracts_by_symbol[symbol].append(c)

            for symbol in sorted(contracts_by_symbol.keys()):
                positions = contracts_by_symbol[symbol]
                symbol_notional = sum(c['value'] for c in positions)
                symbol_pl = sum(c['pl'] for c in positions)

                output.append(f"\n{symbol} (Notional: ₹{symbol_notional:,.0f} | P&L: ₹{symbol_pl:+,.0f})")
                output.append(f"{'Expiry':12} {'Strike':>8} {'Type':>5} {'Qty':>5} {'Value':>12} {'P&L':>12}")

                for c in sorted(positions, key=lambda x: x['expiry']):
                    output.append(f"{c['expiry']:12} {c['strike']:>8} {c['type']:>5} {int(c['qty']):>5} ₹{c['value']:>11,.0f} ₹{c['pl']:>11,.0f}")

        output.append("")
        return output

    def _format_summary(self, equity: Dict, fno: Dict) -> List[str]:
        """Format combined summary"""
        output = []
        output.append("=" * 110)
        output.append("COMBINED PORTFOLIO SUMMARY")
        output.append("=" * 110)
        output.append("")

        total_equity_value = equity.get('total_value', 0)
        total_equity_pl = equity.get('total_unrealized_pl', 0)
        total_fno_notional = fno.get('total_notional', 0)
        total_fno_pl = fno.get('total_pl', 0)

        total_value = total_equity_value + total_fno_notional
        total_pl = total_equity_pl + total_fno_pl
        total_pl_pct = (total_pl / total_equity_value * 100) if total_equity_value > 0 else 0

        output.append(f"Equity Portfolio:   ₹{total_equity_value:>13,.0f} (P&L: ₹{total_equity_pl:>11,.0f}) {total_equity_pl/total_equity_value*100:>+6.2f}%")
        output.append(f"F&O Portfolio:      ₹{total_fno_notional:>13,.0f} (P&L: ₹{total_fno_pl:>11,.0f})")
        output.append(f"{'─' * 110}")
        output.append(f"TOTAL EXPOSURE:     ₹{total_value:>13,.0f} (P&L: ₹{total_pl:>11,.0f}) {total_pl_pct:>+6.2f}%")
        output.append("")

        return output


def main():
    analyzer = IndiaPortfolioAnalyzer()
    report = analyzer.generate_report()

    # Save report
    logs_dir = Path('/home/rahulvadera/projects/theta-lab/logs')
    logs_dir.mkdir(exist_ok=True)

    today = date.today()
    filename = f'india_portfolio_analysis_{today.strftime("%Y-%m-%d")}.txt'
    filepath = logs_dir / filename

    with open(filepath, 'w') as f:
        f.write(report)

    print(report)
    print(f"\n✓ Saved to {filepath}")


if __name__ == '__main__':
    main()
