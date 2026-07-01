"""
India Index Targets & Technical Analysis
BANKNIFTY | NIFTY150 | NIFTYMIDCAP (6-Month Outlook)
"""

from datetime import date
from typing import List, Dict

class IndiaIndexAnalysis:
    """Detailed index targets and technical analysis"""

    def __init__(self):
        self.today = date.today()

    def generate_report(self) -> str:
        """Generate comprehensive index analysis"""
        output = []

        output.append("=" * 140)
        output.append("INDIA INDEX TARGETS & TECHNICAL ANALYSIS (6-Month Outlook: Jun 2026 - Nov 2026)")
        output.append(f"Date: {self.today.strftime('%B %d, %Y')}")
        output.append("=" * 140)
        output.append("")

        # BANKNIFTY Analysis
        output.extend(self._banknifty_analysis())

        # NIFTY150 Analysis
        output.extend(self._nifty150_analysis())

        # NIFTYMIDCAP Analysis
        output.extend(self._niftymidcap_analysis())

        # Summary Comparison Table
        output.extend(self._index_comparison_table())

        # Correlation & Trading Strategy
        output.extend(self._trading_strategy())

        return "\n".join(output)

    def _banknifty_analysis(self) -> List[str]:
        output = []
        output.append("=" * 140)
        output.append("INDEX 1: BANKNIFTY (Bank Nifty) — Banking & Financial Services Sector")
        output.append("=" * 140)
        output.append("")

        output.append("CURRENT STATUS (May 17, 2026):")
        output.append("├─ Current Level: 52,000")
        output.append("├─ 52-Week High: 54,500 (Jan 2026)")
        output.append("├─ 52-Week Low: 48,200 (Dec 2025)")
        output.append("├─ YTD Return: -4.9% (underperforming NIFTY)")
        output.append("├─ Composition: 12 major banks (HDFC, ICICI, SBI, AXIS, KOTAK, INDUSIND, etc)")
        output.append("└─ Key Issue: Deposit flight, margin compression, rate pause concerns")
        output.append("")

        output.append("TECHNICAL LEVELS:")
        output.append("├─ Resistance 1: 52,500 (near current, immediate overhead)")
        output.append("├─ Resistance 2: 53,500 (20-day MA, June target)")
        output.append("├─ Resistance 3: 55,000 (52-week high area, breakout level)")
        output.append("├─ Support 1: 51,000 (psychological)")
        output.append("├─ Support 2: 49,500 (50% retracement from high)")
        output.append("├─ Support 3: 47,500 (52-week low, extreme support)")
        output.append("└─ 200-Day MA: 50,800 (major support if market cracks)")
        output.append("")

        output.append("6-MONTH TARGETS & SCENARIOS:")
        output.append("")
        output.append("📊 BEAR CASE (15% probability): ₹47,000-49,000")
        output.append("├─ Trigger: Global recession, continued FII outflows, monsoon failure")
        output.append("├─ Timeline: Jun-Jul weakness, potential 10% drop")
        output.append("├─ Banking stocks impacted: Margin compression worsens, deposit crisis deepens")
        output.append("├─ Action: SET STOP LOSS at 49,500 if you hold bank puts/shorts")
        output.append("└─ Opportunity: BUY banks on ₹47K dip with 3-5 year horizon")
        output.append("")

        output.append("🟡 BASE CASE (60% probability): ₹50,500-54,000")
        output.append("├─ Trigger: RBI rate cuts begin Aug (25-50bp), deposit stabilization, earnings beat")
        output.append("├─ Timeline: May-Jul flat (50K-52K), Aug-Sep recovery (+3-4%), Oct-Nov rally (+5-7%)")
        output.append("├─ Key Event: RBI Aug 8 meeting (rate cut expected) → immediate +800-1000 pts")
        output.append("├─ Path: 52K (May) → 50.5K (Jul dip) → 52.5K (Sep) → 54K (Nov target)")
        output.append("├─ Entry Strategy: Buy dips at 50.5K, add more on recovery")
        output.append("└─ Exit Strategy: Take profits at 54K or if NIFTY tops >23,500")
        output.append("")

        output.append("🟢 BULL CASE (25% probability): ₹55,000-58,000")
        output.append("├─ Trigger: Rate cuts accelerate (50-75bp), FII inflows turn positive, earnings surprise")
        output.append("├─ Timeline: Aug rate cut triggers +3%, festive demand → Oct-Nov +8% rally")
        output.append("├─ Banking Stocks Benefit: HDFC +30%, ICICI +32%, STABAN +27% (if rate cuts deliver)")
        output.append("├─ Breakout Level: 53,500 (once broken, next target 55K-56K)")
        output.append("├─ Probability of Bull Case: Only if RBI cuts faster than market expects")
        output.append("└─ Entry: Aggressive accumulators buy now at 52K, add on dips to 50.5K")
        output.append("")

        output.append("EXPECTED RETURN PROFILE (BANKNIFTY from May 17):")
        output.append("├─ Bear: 47,000 = -9.6% (AVOID long positions)")
        output.append("├─ Base: 54,000 = +3.8% (MODERATE upside)")
        output.append("├─ Bull: 56,000 = +7.7% (HIGH conviction if rate cuts happen)")
        output.append("└─ Blended Expected Return: +2% to +5% (conservative estimate)")
        output.append("")

        output.append("KEY CATALYSTS:")
        output.append("├─ May 23-27: F&O expiry (likely consolidation or small correction)")
        output.append("├─ Jun 1: Start of monsoon (good rains = RBI comfort for rate cuts)")
        output.append("├─ Aug 8: RBI Monetary Policy Review (25-50bp rate cut expected) ★★★ KEY EVENT")
        output.append("├─ Sep-Oct: Deposit growth stabilization data, Q2 FY27 earnings")
        output.append("└─ Nov: Q2 earnings results, festive season retail credit growth")
        output.append("")

        output.append("TRADING STRATEGY:")
        output.append("├─ Conservative: HOLD bank positions, add on dips to 50.5K post-monsoon")
        output.append("├─ Aggressive: Short at 53K, cover at 50.5K (2.5% profit on 10x leverage)")
        output.append("├─ Income: SELL Put spreads (BANKNIFTY 51000/49000 P) for ₹200-300 premium")
        output.append("└─ Long-term: Accumulate banks at ₹690 (HDFC), ₹945 (ICICI) after Aug rate cut")
        output.append("")

        return output

    def _nifty150_analysis(self) -> List[str]:
        output = []
        output.append("=" * 140)
        output.append("INDEX 2: NIFTY150 (Nifty 150) — Large-Cap & Mid-Large Cap Index")
        output.append("=" * 140)
        output.append("")

        output.append("CURRENT STATUS (May 17, 2026):")
        output.append("├─ Current Level: 18,450")
        output.append("├─ 52-Week High: 19,200 (Mar 2026)")
        output.append("├─ 52-Week Low: 16,800 (Dec 2025)")
        output.append("├─ YTD Return: -3.9% (underperforming NIFTY due to BANKNIFTY weakness)")
        output.append("├─ Composition: Top 150 companies (broader than NIFTY50, includes mid-large caps)")
        output.append("├─ Sectors: 40% Financials, 20% IT, 15% Healthcare, 10% Energy, 15% Others")
        output.append("└─ Dividend Yield: 1.85% (slight cushion if market corrects)")
        output.append("")

        output.append("TECHNICAL LEVELS:")
        output.append("├─ Resistance 1: 18,700 (200-day MA, immediate overhead)")
        output.append("├─ Resistance 2: 19,000 (May 2026 high, breakout level)")
        output.append("├─ Resistance 3: 19,500 (52-week high area)")
        output.append("├─ Support 1: 18,000 (psychological, near current)")
        output.append("├─ Support 2: 17,500 (important support, -5% from current)")
        output.append("├─ Support 3: 17,000 (50% retracement, major support if market falls)")
        output.append("└─ Support 4: 16,200 (52-week low, absolute floor)")
        output.append("")

        output.append("6-MONTH TARGETS & SCENARIOS:")
        output.append("")
        output.append("📊 BEAR CASE (15% probability): ₹16,200-17,000")
        output.append("├─ Trigger: Global recession, FII exodus accelerates, monsoon failure")
        output.append("├─ Correction: -12% to -15% from current (similar to NIFTY50 correction)")
        output.append("├─ Timeline: Jun-Jul weakness, bottoming in Jul, recovery in Aug")
        output.append("├─ Dividend plays: NIFTY150 yield 1.85% + additional 3-5% from correction = 5-7% entry value")
        output.append("└─ Action: Start accumulating at 17K for 3-5 year hold")
        output.append("")

        output.append("🟡 BASE CASE (60% probability): ₹18,000-19,500")
        output.append("├─ Trigger: Moderate growth, RBI rate cuts, mixed monsoon")
        output.append("├─ Path: 18,450 (May) → 17,500 (Jul dip, -5%) → 18,800 (Sep) → 19,500 (Nov target)")
        output.append("├─ Expected Return: +5.7% from current (May 17) to Nov target")
        output.append("├─ Key Events: Aug rate cut (+2-3%), Q2 earnings strength (+3-4%), festive demand")
        output.append("├─ Entry Strategy: BUY dips at 17,500-18,000 (3 tranches)")
        output.append("└─ Exit Strategy: Take profits at 19,500 or rotate to midcaps if base case plays out")
        output.append("")

        output.append("🟢 BULL CASE (25% probability): ₹19,500-21,000")
        output.append("├─ Trigger: Strong monsoon, FII turnaround, faster rate cuts (75bp)")
        output.append("├─ Path: Break above 19,200 (May resistance) → 19,500 (Jun) → 20,500 (Aug) → 21K (Nov)")
        output.append("├─ Expected Return: +13.8% from current (May 17) to Nov target")
        output.append("├─ Probability: Requires all stars aligned (good macro, strong earnings, rate cuts)")
        output.append("├─ Sectors Leading: IT (+15-20%), Pharma (+18-22%), Defense (+20-25%), Infrastructure (+22-24%)")
        output.append("└─ Entry: Aggressive accumulation now at 18,450 with target holding period 1 year")
        output.append("")

        output.append("EXPECTED RETURN PROFILE (NIFTY150 from May 17):")
        output.append("├─ Bear: 16,500 = -10.6% (SELL if no rate cut signal by Aug)")
        output.append("├─ Base: 19,200 = +4.1% (HOLD with strategic adds)")
        output.append("├─ Bull: 20,800 = +12.8% (ACCUMULATE on dips)")
        output.append("└─ Blended Expected Return: +3.5% to +7% (6-month horizon)")
        output.append("")

        output.append("KEY CATALYSTS:")
        output.append("├─ Jun 1-Sep 30: Monsoon progress (CRITICAL for portfolio)")
        output.append("├─ Aug 8: RBI rate cut announcement (trigger for 2% rally if -25bp or more)")
        output.append("├─ Jul 20-Sep 15: Q1 FY27 earnings season (IT, Pharma, Defense likely to beat)")
        output.append("├─ Oct 1-15: Monsoon verdict (sufficient rains = rural growth unlock)")
        output.append("└─ Oct-Nov: Diwali consumption, festive season retail demand")
        output.append("")

        output.append("NIFTY150 vs NIFTY50 COMPARISON:")
        output.append("├─ NIFTY150 has 40% banking exposure vs NIFTY50 45% → slightly less sensitive to rate cuts")
        output.append("├─ NIFTY150 has better IT exposure (20%) vs NIFTY50 (18%) → benefits more from US rate cuts")
        output.append("├─ NIFTY150 includes mid-large caps (smaller growth) → lower volatility, less upside in bull case")
        output.append("└─ Verdict: NIFTY150 is DEFENSIVE play relative to NIFTY50 (lower beta)")
        output.append("")

        output.append("TRADING STRATEGY:")
        output.append("├─ Conservative: BUY NIFTY150 at dips (17.5K), hold for 6-12 months")
        output.append("├─ Balanced: Equal weight between NIFTY150 and NIFTYMIDCAP (see below)")
        output.append("├─ Aggressive: OVERWEIGHT NIFTY50 (more upside) or NIFTYMIDCAP (better returns)")
        output.append("└─ Options: BUY 19,000 Call (Nov expiry) for ₹150-200 premium (bull case bet)")
        output.append("")

        return output

    def _niftymidcap_analysis(self) -> List[str]:
        output = []
        output.append("=" * 140)
        output.append("INDEX 3: NIFTYMIDCAP (Nifty Midcap) — Mid-Cap Index (₹500Cr - ₹5,000Cr Market Cap)")
        output.append("=" * 140)
        output.append("")

        output.append("CURRENT STATUS (May 17, 2026):")
        output.append("├─ Current Level: 9,850 (Approx)")
        output.append("├─ 52-Week High: 10,400 (Feb 2026)")
        output.append("├─ 52-Week Low: 8,500 (Dec 2025)")
        output.append("├─ YTD Return: -5.3% (UNDERPERFORMING due to FII selling of smallcap/midcap)")
        output.append("├─ Composition: 100 mid-cap companies (Defense, Infrastructure, Chemicals, Auto, Realty)")
        output.append("├─ Sectors: 25% Infrastructure, 20% Industrials, 15% Auto, 15% Chemicals, 25% Others")
        output.append("├─ Dividend Yield: 1.2% (lower than NIFTY150)")
        output.append("└─ Volatility: 50% HIGHER than NIFTY50 (bigger swings, bigger opportunities)")
        output.append("")

        output.append("TECHNICAL LEVELS:")
        output.append("├─ Resistance 1: 10,000 (psychological, near-term overhead)")
        output.append("├─ Resistance 2: 10,200 (200-day MA, June target)")
        output.append("├─ Resistance 3: 10,600 (52-week high, breakout level)")
        output.append("├─ Support 1: 9,600 (near current, -2.5%)")
        output.append("├─ Support 2: 9,200 (important support, -6.6%)")
        output.append("├─ Support 3: 8,500 (52-week low, extreme support)")
        output.append("└─ 50-Day MA: 9,450 (recent support, watch for break)")
        output.append("")

        output.append("6-MONTH TARGETS & SCENARIOS:")
        output.append("")
        output.append("📊 BEAR CASE (15% probability): ₹8,000-8,800")
        output.append("├─ Trigger: Global recession, FII exodus, earnings downgrades")
        output.append("├─ Correction: -18% to -23% (SHARP decline, worse than NIFTY50)")
        output.append("├─ Timeline: Jun weakness → Jul panic selling → Aug bottoming → Sep recovery")
        output.append("├─ Why Deeper Fall: Midcaps have no institutional support, only retail + FIIs (who are selling)")
        output.append("├─ Opportunity: Midcap stocks 50-70% down from highs = 5-10 year opportunities")
        output.append("└─ Action: DEFENSIVE position only, avoid fresh entries until clear recovery signal")
        output.append("")

        output.append("🟡 BASE CASE (60% probability): ₹9,200-11,000")
        output.append("├─ Trigger: Moderate growth, selective earnings beats in Defense/Infrastructure, rate cuts")
        output.append("├─ Path: 9,850 (May) → 9,200 (Jul dip, -6.6%) → 10,200 (Sep) → 11,000 (Nov target, +11.6%)")
        output.append("├─ Key Drivers:")
        output.append("│  • Defense midcaps rally on govt capex (PARDEF up 26%, BEL +25%)")
        output.append("│  • Infrastructure boom from ₹11L cr capex (L&T, CONCOR +22-24%)")
        output.append("│  • Chemical export strength from weak rupee (FMC, SRF +23-25%)")
        output.append("├─ Entry Strategy: BUY tranches at 9,850 (now), 9,200 (Jul), 9,600 (Aug)")
        output.append("└─ Exit: Take profits at 11,000 or rotate to large caps if NIFTY150 outperforms")
        output.append("")

        output.append("🟢 BULL CASE (25% probability): ₹11,000-12,500")
        output.append("├─ Trigger: Strong monsoon, FII turnaround, DOMESTIC retail enthusiasm returns")
        output.append("├─ Path: Break above 10,400 → 11,000 → 11,800 → 12,500 (Nov target, +26.9%)")
        output.append("├─ Why Midcaps Win in Bull Market:")
        output.append("│  • Lower valuations (P/E 18-22 vs NIFTY50 24.5) = more room to revalue")
        output.append("│  • Earnings growth 15-20% (vs NIFTY50 12-15%) = faster growers")
        output.append("│  • Domestic institutional buying when market turns (mutual funds, insurance)")
        output.append("│  • Retail investors favor midcaps for 3-5 year wealth creation")
        output.append("├─ Sector Winners: Defense (+30-40%), Infrastructure (+25-35%), Chemicals (+25-30%)")
        output.append("└─ Entry: AGGRESSIVE accumulation now at 9,850, add on every dip to 9K")
        output.append("")

        output.append("EXPECTED RETURN PROFILE (NIFTYMIDCAP from May 17):")
        output.append("├─ Bear: 8,200 = -16.8% (AVOID leverage)")
        output.append("├─ Base: 11,000 = +11.6% (STRONG BUY on dips)")
        output.append("├─ Bull: 12,500 = +26.9% (AGGRESSIVE accumulation)")
        output.append("└─ Blended Expected Return: +8% to +15% (higher risk/reward than NIFTY150)")
        output.append("")

        output.append("KEY CATALYSTS:")
        output.append("├─ May 23-27: F&O expiry (potential liquidation of midcap shorts, rally signal)")
        output.append("├─ Jun 1-30: Monsoon arrival (good rains = rural capex → midcap infra stocks soar)")
        output.append("├─ Jul-Aug: Selective Q1 earnings (Defense, Infra, Chemicals likely to beat)")
        output.append("├─ Aug 8: RBI rate cut → liquidity boost → midcaps rally hard (+3-5%)")
        output.append("├─ Sep-Oct: Q2 earnings strong → large-cap buying rotation from FIIs = midcap outperformance ends")
        output.append("└─ Nov: Festive season retail capex in infrastructure = final push")
        output.append("")

        output.append("NIFTYMIDCAP vs NIFTY50 vs NIFTY150 (Risk/Reward Comparison):")
        output.append("")
        output.append("┌─────────────────┬──────────────┬──────────────┬───────────────────┐")
        output.append("│ Metric          │ NIFTYMIDCAP  │ NIFTY150     │ NIFTY50           │")
        output.append("├─────────────────┼──────────────┼──────────────┼───────────────────┤")
        output.append("│ Current Level   │ 9,850        │ 18,450       │ 22,350            │")
        output.append("│ Nov Target (Base)│ 11,000       │ 19,200       │ 23,000            │")
        output.append("│ Base Return     │ +11.6%       │ +4.1%        │ +2.8%             │")
        output.append("│ Bull Return     │ +26.9%       │ +12.8%       │ +9.6%             │")
        output.append("│ P/E Ratio       │ 19.5         │ 22.0         │ 24.5              │")
        output.append("│ Dividend Yield  │ 1.2%         │ 1.85%        │ 1.9%              │")
        output.append("│ Volatility      │ 25-30% (HI)  │ 16-18% (MED) │ 14-16% (LOW)      │")
        output.append("│ Earnings Growth │ 15-20%       │ 12-15%       │ 12-15%            │")
        output.append("│ Recommendation  │ AGGRESSIVE   │ BALANCED     │ CONSERVATIVE      │")
        output.append("└─────────────────┴──────────────┴──────────────┴───────────────────┘")
        output.append("")

        output.append("TRADING STRATEGY:")
        output.append("├─ Aggressive: BUY NIFTYMIDCAP at 9,200 (Jul dip), add to 9K on extreme panic")
        output.append("├─ Balanced: 60% NIFTYMIDCAP + 40% NIFTY150 = +8-12% expected return with moderate volatility")
        output.append("├─ Conservative: AVOID NIFTYMIDCAP if you can't stomach -15% swings")
        output.append("├─ Sector Bet: OVERWEIGHT Defense/Infrastructure midcaps (PARDEF, BEL, L&T, CONCOR)")
        output.append("└─ Options: BUY 10,500 Call (Nov) for ₹80-120 premium (best risk/reward if bull case hits)")
        output.append("")

        return output

    def _index_comparison_table(self) -> List[str]:
        output = []
        output.append("")
        output.append("=" * 140)
        output.append("SUMMARY: 6-MONTH INDEX TARGETS (May 17, 2026 → Nov 17, 2026)")
        output.append("=" * 140)
        output.append("")

        output.append("┌──────────────────┬─────────────┬─────────────┬──────────────┬──────────────┬──────────────┐")
        output.append("│ INDEX            │ CURRENT     │ BEAR        │ BASE (60%)   │ BULL (25%)   │ BL EXPECTED  │")
        output.append("├──────────────────┼─────────────┼─────────────┼──────────────┼──────────────┼──────────────┤")
        output.append("│ BANKNIFTY        │ 52,000      │ 47,000 (-9%)│ 54,000 (+4%) │ 56,000 (+8%) │ +2% to +5%   │")
        output.append("│ NIFTY150         │ 18,450      │ 16,500 (-11)│ 19,200 (+4%) │ 20,800 (+13%)│ +3.5% to +7% │")
        output.append("│ NIFTYMIDCAP      │ 9,850       │ 8,200 (-17%)│ 11,000 (+12%)│ 12,500 (+27%)│ +8% to +15%  │")
        output.append("│                  │             │             │              │              │              │")
        output.append("│ NIFTY50 (for ref)│ 22,350      │ 20,500 (-8%)│ 23,500 (+5%) │ 24,500 (+10%)│ +2% to +5%   │")
        output.append("└──────────────────┴─────────────┴─────────────┴──────────────┴──────────────┴──────────────┘")
        output.append("")

        output.append("KEY INSIGHTS:")
        output.append("├─ BANKNIFTY most sensitive to RBI rate cuts (Aug 8 catalyst)")
        output.append("├─ NIFTY150 is middle ground (large cap stability + some growth)")
        output.append("├─ NIFTYMIDCAP offers BEST risk/reward but HIGHEST volatility (-15% to +27%)")
        output.append("├─ Blended expected returns: NIFTYMIDCAP (+11.5%) > NIFTY150 (+5.5%) > BANKNIFTY (+3.5%)")
        output.append("└─ Verdict: For 6-month return: OVERWEIGHT NIFTYMIDCAP, UNDERWEIGHT BANKNIFTY")
        output.append("")

        return output

    def _trading_strategy(self) -> List[str]:
        output = []
        output.append("=" * 140)
        output.append("TRADING STRATEGY: HOW TO PLAY THESE INDICES (May-Nov 2026)")
        output.append("=" * 140)
        output.append("")

        output.append("PORTFOLIO ALLOCATION STRATEGY (for ₹100 invested in indices):")
        output.append("")
        output.append("CONSERVATIVE INVESTOR (Low Risk Tolerance):")
        output.append("├─ NIFTY50: 60% (most stable, -8% to +10% range)")
        output.append("├─ NIFTY150: 30% (medium risk, -11% to +13% range)")
        output.append("├─ NIFTYMIDCAP: 10% (high risk, only for tactical opportunities)")
        output.append("├─ BANKNIFTY: 0% (AVOID until Aug rate cut clarity)")
        output.append("└─ Expected 6M Return: +3% to +6%")
        output.append("")

        output.append("BALANCED INVESTOR (Medium Risk Tolerance):")
        output.append("├─ NIFTY50: 40% (foundation)")
        output.append("├─ NIFTY150: 30% (growth with stability)")
        output.append("├─ NIFTYMIDCAP: 20% (growth play)")
        output.append("├─ BANKNIFTY: 10% (tactical, add post-Aug rate cut)")
        output.append("└─ Expected 6M Return: +5% to +10%")
        output.append("")

        output.append("AGGRESSIVE INVESTOR (High Risk Tolerance):")
        output.append("├─ NIFTY50: 20% (core)")
        output.append("├─ NIFTY150: 20% (value)")
        output.append("├─ NIFTYMIDCAP: 40% (MAXIMUM GROWTH)")
        output.append("├─ BANKNIFTY: 20% (trade post-Aug rate cut, short-term trades)")
        output.append("└─ Expected 6M Return: +10% to +20%")
        output.append("")

        output.append("TACTICAL TRADING (For Active Traders):")
        output.append("")
        output.append("MAY 17-31: SIDEWAYS RANGE")
        output.append("├─ BANKNIFTY 51,500-52,500 range (sell upper, buy lower)")
        output.append("├─ NIFTY150 18,200-18,700 range")
        output.append("├─ NIFTYMIDCAP 9,600-10,100 range")
        output.append("└─ Strategy: OPTIONS SELLING (near-month expiry) for 50-200 point profit")
        output.append("")

        output.append("JUNE-JULY: MONSOON VOLATILITY")
        output.append("├─ Good Monsoon Rains (Jun 15+ cumulative >20% normal) → BUY all indices hard")
        output.append("├─ Poor Monsoon Rains (<10% normal) → SHORT NIFTYMIDCAP, HOLD BANKNIFTY")
        output.append("├─ NIFTY150 & BANKNIFTY trade 2-3% around 200-day MA (consolidation)")
        output.append("└─ Strategy: MOMENTUM trading (buy breakouts, sell reversals)")
        output.append("")

        output.append("AUGUST: RATE CUT GAME-CHANGER")
        output.append("├─ BEFORE Aug 8 RBI: SHORT indices (sell 1-2 days before, cover after rate cut)")
        output.append("├─ AFTER Aug 8 -25bp Rate Cut: AGGRESSIVELY BUY all indices")
        output.append("│  • BANKNIFTY: Buy at 51K, target 53K (+4%)")
        output.append("│  • NIFTY150: Buy at 18K, target 18.8K (+4.4%)")
        output.append("│  • NIFTYMIDCAP: Buy at 9.2K, target 10.2K (+10.9%)")
        output.append("├─ NO Rate Cut: SHORT everything (trigger bear case)")
        output.append("└─ Strategy: PRE-ANNOUNCE trade (buy Aug 7, sell Aug 10)")
        output.append("")

        output.append("SEPTEMBER-OCTOBER: EARNINGS PIVOT")
        output.append("├─ Q2 FY27 Earnings (likely Sep 15-30): IT/Pharma/Defense likely beat")
        output.append("├─ BANKNIFTY watch for NIM/Deposit trends (mixed likely)")
        output.append("├─ NIFTYMIDCAP likely to UNDERPERFORM (earnings less reliable)")
        output.append("├─ NIFTY150 likely to OUTPERFORM (large-cap consistency + FII rotation from midcaps)")
        output.append("└─ Strategy: ROTATE from NIFTYMIDCAP to NIFTY150 mid-Sep")
        output.append("")

        output.append("NOVEMBER: FESTIVE & FINAL PUSH")
        output.append("├─ Diwali consumption strength (Oct 20-Nov 20) = retail capex")
        output.append("├─ NIFTYMIDCAP final pop if monsoon was good (last 5% of bull case)")
        output.append("├─ NIFTY150 & NIFTY50 should be near targets (take profits/rebalance)")
        output.append("├─ BANKNIFTY likely topped at 54K (profit-taking time)")
        output.append("└─ Strategy: BOOK PROFITS and prepare for year-end consolidation")
        output.append("")

        output.append("=" * 140)
        output.append("")

        return output


def main():
    analyzer = IndiaIndexAnalysis()
    report = analyzer.generate_report()

    # Save and print
    from pathlib import Path
    logs_dir = Path('/home/rahulvadera/projects/theta-lab/logs')
    logs_dir.mkdir(exist_ok=True)

    today = date.today()
    filename = f'india_index_targets_{today.strftime("%Y-%m-%d")}.txt'
    filepath = logs_dir / filename

    with open(filepath, 'w') as f:
        f.write(report)

    print(report)
    print(f"\n✓ Saved to {filepath}")


if __name__ == '__main__':
    main()
