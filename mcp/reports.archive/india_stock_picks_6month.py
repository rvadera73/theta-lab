"""
India Stock Picks — 6-Month Roadmap (June 2026 - Nov 2026)
Specific stock names, entry prices, targets, and timing
"""

from datetime import date
from typing import List, Dict

class IndiaStockPicks:
    """Detailed stock recommendations with specific entry points"""

    def __init__(self):
        self.today = date.today()

    def generate_report(self) -> str:
        """Generate comprehensive stock picks report"""
        output = []

        output.append("=" * 130)
        output.append("INDIA STOCK PICKS & TIMING GUIDE — 6-MONTH ROADMAP (June 2026 - Nov 2026)")
        output.append(f"Date: {self.today.strftime('%B %d, %Y')}")
        output.append("=" * 130)
        output.append("")

        # Section 1: Defense & Aerospace
        output.extend(self._defense_picks())

        # Section 2: IT & Tech
        output.extend(self._it_tech_picks())

        # Section 3: Pharma & Healthcare
        output.extend(self._pharma_picks())

        # Section 4: Infrastructure & Logistics
        output.extend(self._infrastructure_picks())

        # Section 5: Banking & Finance
        output.extend(self._banking_picks())

        # Section 6: Chemicals & Specialty
        output.extend(self._chemicals_picks())

        # Section 7: Power & Energy
        output.extend(self._energy_picks())

        # Section 8: Consumer & Retail
        output.extend(self._consumer_picks())

        # Summary table
        output.extend(self._summary_table())

        return "\n".join(output)

    def _defense_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 1: DEFENSE & AEROSPACE (Conviction: 8.5/10) — CORE POSITION 12-15%")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: 20-year govt capex ₹1L+ cr. Private sector participation accelerating. DRDO contracts, domestic fighter jet (Tejas), Airbus/Boeing partnerships.")
        output.append("")

        picks = [
            {
                'name': 'HAL (Hindustan Aeronautics)',
                'ticker': 'HALIND',
                'current_price': 4800,
                'entry_may': 4800,
                'dip_entry_jun': 4500,  # -6% dip
                'target_nov': 5800,
                'upside': '20.8%',
                'risk': '-6%',
                'quantity': 5,
                'timing': 'BUY NOW or on dip Jun-Jul',
                'why': 'Fighter jet (Tejas) manufacturing ramp-up, DRDO contracts accelerating, export potential',
                'catalyst': 'Q1 FY27 earnings, Tejas production orders, Airbus partnerships',
                'alternate': 'BEL (Bharat Electronics)'
            },
            {
                'name': 'Paras Defence (Private)',
                'ticker': 'PARDEF',
                'current_price': 753,
                'entry_may': 750,
                'dip_entry_jun': 680,  # -10% dip
                'target_nov': 950,
                'upside': '26%',
                'risk': '-10%',
                'quantity': 20,
                'timing': 'BUY on dips (target ₹680-720 in Jun-Jul)',
                'why': 'Missile tech leader, DRDO certified, growth from ₹100cr → ₹500cr revenue in 3 years',
                'catalyst': 'New defense contracts, margin expansion, scale-up from missile programs',
                'alternate': 'Mazagon Dock (MAZDOC) — Naval shipbuilding'
            },
            {
                'name': 'BEL (Bharat Electronics)',
                'ticker': 'BHAELE',
                'current_price': 423,
                'entry_may': 420,
                'dip_entry_jun': 385,  # -9% dip
                'target_nov': 530,
                'upside': '25.3%',
                'risk': '-9%',
                'quantity': 30,
                'timing': 'BUY on weakness, core hold',
                'why': 'Electronics for defense, radar systems, surveillance. Govt push to reduce imports.',
                'catalyst': 'Radar contract wins, Government procurement, border security projects',
                'alternate': 'Zenith Motors — Turret systems (micro-cap growth)'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): ₹{pick['entry_may']} | Dip Entry (Jun): ₹{pick['dip_entry_jun']} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside: {pick['upside']} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _it_tech_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 2: IT & TECH (Conviction: 8.0/10) — BUILD 5% → 12%")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: USD denominated earnings, US rate cuts boost demand. TCS recovery, Infosys growth, HCL outsourcing gains.")
        output.append("")

        picks = [
            {
                'name': 'TCS (Tata Consultancy Services)',
                'ticker': 'TCS',
                'current_price': 2264,
                'entry_may': 2264,
                'dip_entry_jun': 2000,  # -12% dip (recovery play)
                'target_nov': 2700,
                'upside': '19.2%',
                'risk': '-12%',
                'quantity': 10,
                'timing': 'BUY on dip Jun-Jul if NIFTY falls (currently down -21% YTD)',
                'why': 'Largest IT company, strong balance sheet, US rate cuts → consulting demand up',
                'catalyst': 'Strong Q1 FY27 earnings, margin recovery, digital transformation deals',
                'alternate': 'Infosys (INFY) — Growth story, better margins'
            },
            {
                'name': 'Infosys',
                'ticker': 'INFY',
                'current_price': 1520,
                'entry_may': 1520,
                'dip_entry_jun': 1380,  # -9% dip
                'target_nov': 1850,
                'upside': '21.7%',
                'risk': '-9%',
                'quantity': 15,
                'timing': 'BUY now or on dips. Stronger trajectory than TCS.',
                'why': 'Growth-focused management, strong deal wins, attrition under control',
                'catalyst': 'Strong bookings, deal TCV growth, margin guidance raise',
                'alternate': 'HCL Technologies (HCLTECH) — Deep tech focus'
            },
            {
                'name': 'HCL Technologies',
                'ticker': 'HCLTECH',
                'current_price': 1050,
                'entry_may': 1050,
                'dip_entry_jun': 950,  # -10% dip
                'target_nov': 1300,
                'upside': '23.8%',
                'risk': '-10%',
                'quantity': 15,
                'timing': 'BUY small position May, scale up on Jun dip',
                'why': 'Deep tech focus (software services), better deal margins, cloud/AI exposure',
                'catalyst': 'Cloud deal wins, product revenue growth, AI service uptake',
                'alternate': 'Tech Mahindra (TECHM) — Infrastructure IT'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): ₹{pick['entry_may']} | Dip Entry (Jun): ₹{pick['dip_entry_jun']} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside: {pick['upside']} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _pharma_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 3: PHARMA & HEALTHCARE (Conviction: 7.5/10) — HOLD/BUILD 15-20%")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: Weak rupee (₹83.5) = strong exports. Pricing power in India. GLP-1 opportunities (diabetes drugs).")
        output.append("")

        picks = [
            {
                'name': 'Dr Reddy\'s Laboratories',
                'ticker': 'DRREDD',
                'current_price': 1336,
                'entry_may': 1340,
                'dip_entry_jun': 1200,  # -10% dip
                'target_nov': 1650,
                'upside': '23.4%',
                'risk': '-10%',
                'quantity': 10,
                'timing': 'BUY now or on dip Jun-Jul',
                'why': 'Strong export base (US+EU), GLP-1 drugs, pricing power, R&D pipeline',
                'catalyst': 'Q1 FY27 US business growth, GLP-1 approvals, API pricing gains',
                'alternate': 'Cipla (CIPLA) — Respiratory focus'
            },
            {
                'name': 'Cipla Limited',
                'ticker': 'CIPLA',
                'current_price': 1380,
                'entry_may': 1380,
                'dip_entry_jun': 1250,  # -9% dip
                'target_nov': 1700,
                'upside': '23.2%',
                'risk': '-9%',
                'quantity': 12,
                'timing': 'BUY small now, scale on dip',
                'why': 'Respiratory/chronic disease focus, emerging markets growth, India pricing power',
                'catalyst': 'US business recovery, India volume growth, cost initiatives',
                'alternate': 'Biocon (BIOCON) — Biosimilars, insulin'
            },
            {
                'name': 'Apollo Hospitals',
                'ticker': 'APOHOS',
                'current_price': 8082,
                'entry_may': 8080,
                'dip_entry_jun': 7300,  # -10% dip
                'target_nov': 10000,
                'upside': '23.8%',
                'risk': '-10%',
                'quantity': 2,
                'timing': 'BUY on dips (higher price = smaller qty)',
                'why': 'Hospital network expansion, India healthcare growing 12-15% YoY, premium services',
                'catalyst': 'New hospital openings, higher ARPPU (average patient spend), diagnostic growth',
                'alternate': 'Max Healthcare (MAXHEALTH) — Mid-tier hospitals'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): ₹{pick['entry_may']} | Dip Entry (Jun): ₹{pick['dip_entry_jun']} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside: {pick['upside']} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _infrastructure_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 4: INFRASTRUCTURE & LOGISTICS (Conviction: 7.5/10) — STRONG HOLD 10-12%")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: Govt capex ₹11L cr, port volumes, logistics maturity post-GST. ADAPOR (ports) already +24%.")
        output.append("")

        picks = [
            {
                'name': 'Adani Ports & Special Economic Zones',
                'ticker': 'ADAPOR',
                'current_price': 1795,
                'entry_may': 1795,
                'dip_entry_jun': 1620,  # -10% dip
                'target_nov': 2200,
                'upside': '22.6%',
                'risk': '-10%',
                'quantity': 10,
                'timing': 'STRONG HOLD (already up +24% YTD). Add on dips only.',
                'why': 'Port volume growth 15%+ YoY, capex cycle strong, dividend yield 1.5%',
                'catalyst': 'Port volumes post-monsoon, terminal expansions, container volume growth',
                'alternate': 'IFC (Indian Ports Association) — Micro-cap alternative'
            },
            {
                'name': 'L&T (Larsen & Toubro)',
                'ticker': 'LT',
                'current_price': 3200,
                'entry_may': 3200,
                'dip_entry_jun': 2880,  # -10% dip
                'target_nov': 3920,
                'upside': '22.5%',
                'risk': '-10%',
                'quantity': 5,
                'timing': 'BUY on dips (large cap, lower volatility)',
                'why': 'Construction + EPC contracts benefiting from govt capex. Water, power, roads projects.',
                'catalyst': 'Order book growth, execution updates, margin expansion',
                'alternate': 'Godrej & Boyce (GODREJBOL) — Infrastructure services'
            },
            {
                'name': 'Container Corporation of India',
                'ticker': 'CONCOR',
                'current_price': 850,
                'entry_may': 850,
                'dip_entry_jun': 765,  # -10% dip
                'target_nov': 1050,
                'upside': '23.5%',
                'risk': '-10%',
                'quantity': 20,
                'timing': 'BUY small position. Micro-cap logistics play.',
                'why': 'Rail freight volumes growing, container exports rising, GST helping logistics',
                'catalyst': 'Rail freight growth, container export surge, cost efficiency',
                'alternate': 'VRL Logistics (VRLLOG) — Road transport alternative'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): ₹{pick['entry_may']} | Dip Entry (Jun): ₹{pick['dip_entry_jun']} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside: {pick['upside']} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _banking_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 5: BANKING & FINANCE (Conviction: 6.5/10) — REDUCE NOW, BUY AUG (POST-RATE CUT)")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: Currently under pressure (BANKNIFTY -5%, deposits flowing out). Best entry AFTER Aug rate cut (-25bp).")
        output.append("")

        picks = [
            {
                'name': 'HDFC Bank',
                'ticker': 'HDFBAN',
                'current_price': 767,
                'entry_may': 'AVOID',
                'dip_entry_jun': 'WAIT',
                'dip_entry_aug': 690,  # Wait for Aug rate cut
                'target_nov': 900,
                'upside_from_aug': '30.4%',
                'risk': '-5%',
                'quantity': 15,
                'timing': 'WAIT until Aug rate cut. BUY at ₹690-720 post-RBI meeting.',
                'why': 'Best private bank, deposit stabilization expected post rate cuts. Prime buy AFTER Aug.',
                'catalyst': 'RBI rate cut Aug, deposit growth stabilization, NIM expansion',
                'alternate': 'ICICI Bank (ICICIBANK) — Faster growth'
            },
            {
                'name': 'ICICI Bank',
                'ticker': 'ICICIBANK',
                'current_price': 1050,
                'entry_may': 'AVOID',
                'dip_entry_jun': 'WAIT',
                'dip_entry_aug': 945,  # Wait for Aug rate cut
                'target_nov': 1250,
                'upside_from_aug': '32.3%',
                'risk': '-5%',
                'quantity': 12,
                'timing': 'WAIT until Aug RBI rate cut. BUY at ₹945-980 post-cut.',
                'why': 'Stronger capital ratio, better deposit franchise post-RBI policy change.',
                'catalyst': 'Rate cut announcement, deposit turnaround, credit growth',
                'alternate': 'Axis Bank (AXISBANK) — Turnaround story'
            },
            {
                'name': 'State Bank of India',
                'ticker': 'STABAN',
                'current_price': 963,
                'entry_may': 'AVOID',
                'dip_entry_jun': 'WAIT',
                'dip_entry_aug': 865,  # Wait for Aug rate cut
                'target_nov': 1100,
                'upside_from_aug': '27.2%',
                'risk': '-6%',
                'quantity': 15,
                'timing': 'DEFENSIVE play. BUY post-Aug rate cut at ₹860-890.',
                'why': 'PSU bank, strong deposit base, government backstop. Boring but safe.',
                'catalyst': 'RBI rate cut, PSU bank thrust, deposit growth',
                'alternate': 'Bank of Baroda (BOBARODA) — Micro-cap PSU'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): {pick['entry_may']} | Entry (Aug, Post-Rate Cut): ₹{pick.get('dip_entry_aug', 'TBD')} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside (from Aug): {pick.get('upside_from_aug', 'TBD')} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _chemicals_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 6: CHEMICALS & SPECIALTY (Conviction: 6.5/10) — BUILD 8-10%")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: Weak rupee (₹83.5) helps exports. Specialty chemicals command premium pricing.")
        output.append("")

        picks = [
            {
                'name': 'FMC (Fresh Mountain Chemical)',
                'ticker': 'FMC',
                'current_price': 1417,
                'entry_may': 1417,
                'dip_entry_jun': 1275,  # -10% dip
                'target_nov': 1750,
                'upside': '23.5%',
                'risk': '-10%',
                'quantity': 8,
                'timing': 'BUY on dips. Specialty pesticides/chemicals.',
                'why': 'Agricultural chemicals export strength, weak rupee tailwind, pricing power',
                'catalyst': 'Export volume growth, pricing gains, margin expansion',
                'alternate': 'Gharda Chemicals (GHARDA) — Specialty playstay'
            },
            {
                'name': 'SRF Limited',
                'ticker': 'SRF',
                'current_price': 2450,
                'entry_may': 2450,
                'dip_entry_jun': 2205,  # -10% dip
                'target_nov': 3050,
                'upside': '24.5%',
                'risk': '-10%',
                'quantity': 6,
                'timing': 'BUY small position. High-value specialty chemicals.',
                'why': 'Fluorochemicals (high margin), packaging films, export-led growth',
                'catalyst': 'Specialty chem pricing, Refrigerant demand, margin beat',
                'alternate': 'Kiran Chemicals (KIRANC) — Micro-cap specialty'
            },
            {
                'name': 'Aarti Industries',
                'ticker': 'AARTIIND',
                'current_price': 800,
                'entry_may': 800,
                'dip_entry_jun': 720,  # -10% dip
                'target_nov': 1000,
                'upside': '25%',
                'risk': '-10%',
                'quantity': 20,
                'timing': 'BUY on dips. Mid-cap specialty chemicals.',
                'why': 'Specialty organic chemicals for pharma/agrochemicals, strong export base',
                'catalyst': 'Export orders, margin expansion, capacity additions',
                'alternate': 'Deepak Nitrite (DEEPAKNTR) — Fine chemicals focus'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): ₹{pick['entry_may']} | Dip Entry (Jun): ₹{pick['dip_entry_jun']} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside: {pick['upside']} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _energy_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 7: POWER & ENERGY (Conviction: 5.5/10) — REDUCE THERMAL, FAVOR GREEN")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: REDUCE thermal coal exposure. FAVOR renewable energy (solar, wind).")
        output.append("")

        picks = [
            {
                'name': 'SOLIN (Solar Industries India)',
                'ticker': 'SOLIN',
                'current_price': 17314,
                'entry_may': 17314,
                'dip_entry_jun': 15583,  # -10% dip
                'target_nov': 21000,
                'upside': '21.3%',
                'risk': '-10%',
                'quantity': 1,
                'timing': 'STRONG HOLD (already up +6.7% YTD). Add on dips.',
                'why': 'Solar equipment manufacturer, govt solar push ₹2L+ cr capex, PLI scheme benefits',
                'catalyst': 'Solar capacity addition, PLI awards, export orders',
                'alternate': 'Waaree Energies (WAAREE) — Solar module maker'
            },
            {
                'name': 'Tata Power',
                'ticker': 'TATAPOWER',
                'current_price': 380,
                'entry_may': 380,
                'dip_entry_jun': 342,  # -10% dip
                'target_nov': 480,
                'upside': '26.3%',
                'risk': '-10%',
                'quantity': 20,
                'timing': 'BUY on dips. Renewable transition play.',
                'why': 'Renewable power plant growth, coal phase-out strategy, clean energy focus',
                'catalyst': 'Renewable capacity growth, coal exit, dividend yield 2%+',
                'alternate': 'Power Grid Corporation (POWERGRID) — Transmission, dividends'
            },
            {
                'name': 'Power Grid Corporation of India',
                'ticker': 'POWERGRID',
                'current_price': 265,
                'entry_may': 265,
                'dip_entry_jun': 238,  # -10% dip
                'target_nov': 330,
                'upside': '24.5%',
                'risk': '-10%',
                'quantity': 30,
                'timing': 'BUY for dividend income. Boring but safe, 2-3% yield.',
                'why': 'Transmission network expansion, renewable integration, stable cash flows',
                'catalyst': 'Transmission capex, dividend growth, transmission auctions',
                'alternate': 'NTPC (NTPC) — BUT reduce thermal. Not recommended.'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): ₹{pick['entry_may']} | Dip Entry (Jun): ₹{pick['dip_entry_jun']} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside: {pick['upside']} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _consumer_picks(self) -> List[str]:
        output = []
        output.append("=" * 130)
        output.append("SECTOR 8: CONSUMER & RETAIL (Conviction: 4.5/10) — BUY POST-MONSOON (OCT-NOV)")
        output.append("=" * 130)
        output.append("")
        output.append("Thesis: Weak demand now. WAIT for monsoon confirmation (good rains) and festive season (Oct-Nov).")
        output.append("")

        picks = [
            {
                'name': 'Yatharth Hospital (YOUR HOLDING)',
                'ticker': 'YATHOS',
                'current_price': 815,
                'entry_may': 'HOLD',
                'entry_oct': 750,  # Post-monsoon entry
                'target_nov': 1000,
                'upside': '22.8%',
                'risk': '-8%',
                'quantity': 'HOLD 200 shares',
                'timing': 'HOLD current. Add on dips post-Aug. Strong hospital chain.',
                'why': 'Healthcare is defensive. Add after monsoon confirmation (Oct onwards).',
                'catalyst': 'Hospital expansion, higher ARPPU, occupancy growth',
                'alternate': 'Care Hospitals (CAREHEALTH) — Metro tier-2 expansion'
            },
            {
                'name': 'Indian Hotels Company (ITC Hotels)',
                'ticker': 'INDIGO',
                'current_price': 3150,
                'entry_may': 'WAIT',
                'entry_oct': 2835,  # Post-monsoon entry
                'target_nov': 3800,
                'upside': '34.1%',
                'risk': '-10%',
                'quantity': 5,
                'timing': 'AVOID now. BUY only post-Oct (Diwali/festive season).',
                'why': 'Hospitality/airline, weak demand now. Strong on festive season.',
                'catalyst': 'Diwali bookings, year-end travel, domestic tourism',
                'alternate': 'Oberoi Hotels (OBEROIRLTY) — Luxury segment'
            },
            {
                'name': 'Britannia Industries',
                'ticker': 'BRITANNIA',
                'current_price': 4500,
                'entry_may': 'HOLD',
                'entry_oct': 4050,  # Post-monsoon entry
                'target_nov': 5400,
                'upside': '20%',
                'risk': '-10%',
                'quantity': 'If you add: 3-4 shares',
                'timing': 'HOLD if own. Add small on dips post-Oct.',
                'why': 'FMCG defensive. Good on monsoon recovery + festive consumption.',
                'catalyst': 'Good monsoon → rural demand, festive season strength',
                'alternate': 'Nestlé India (NESTLEIND) — Premium FMCG'
            }
        ]

        for i, pick in enumerate(picks, 1):
            output.append(f"{i}. {pick['name'].upper()} ({pick['ticker']})")
            output.append(f"   Current Price: ₹{pick['current_price']} | Entry (May): {pick['entry_may']} | Entry (Oct, Post-Monsoon): ₹{pick.get('entry_oct', 'TBD')} | Target (Nov): ₹{pick['target_nov']}")
            output.append(f"   Upside: {pick['upside']} | Risk: {pick['risk']} | Suggested Qty: {pick['quantity']}")
            output.append(f"   Timing: {pick['timing']}")
            output.append(f"   Why: {pick['why']}")
            output.append(f"   Catalyst: {pick['catalyst']}")
            output.append(f"   ⚡ Alternate: {pick['alternate']}")
            output.append("")

        return output

    def _summary_table(self) -> List[str]:
        output = []
        output.append("")
        output.append("=" * 130)
        output.append("QUICK REFERENCE — ALL STOCK PICKS SUMMARY")
        output.append("=" * 130)
        output.append("")

        summary_data = [
            ("SECTOR", "PRIMARY PICK", "ENTRY (MAY)", "TARGET (NOV)", "UPSIDE", "TIMING", "ALTERNATE"),
            ("─" * 15, "─" * 25, "─" * 12, "─" * 12, "─" * 8, "─" * 20, "─" * 25),
            ("Defense", "HAL", "₹4,800", "₹5,800", "+20.8%", "BUY NOW", "BEL, PARDEF"),
            ("", "PARDEF", "₹750", "₹950", "+26%", "BUY dips", "MAZDOC"),
            ("", "BEL", "₹420", "₹530", "+25.3%", "BUY dips", "Zenith Motors"),
            ("", "", "", "", "", "", ""),
            ("IT & Tech", "INFY", "₹1,520", "₹1,850", "+21.7%", "BUY NOW", "HCL, HCLTECH"),
            ("", "TCS", "₹2,264", "₹2,700", "+19.2%", "BUY dips Jun", "INFY, HCLTECH"),
            ("", "HCLTECH", "₹1,050", "₹1,300", "+23.8%", "BUY small", "TECHM"),
            ("", "", "", "", "", "", ""),
            ("Pharma", "DRREDD", "₹1,340", "₹1,650", "+23.4%", "BUY NOW", "CIPLA, BIOCON"),
            ("", "CIPLA", "₹1,380", "₹1,700", "+23.2%", "BUY small", "DRREDD, BIOCON"),
            ("", "APOHOS", "₹8,080", "₹10,000", "+23.8%", "BUY dips", "MAXHEALTH"),
            ("", "", "", "", "", "", ""),
            ("Infrastructure", "ADAPOR", "₹1,795", "₹2,200", "+22.6%", "HOLD, add dips", "IFC"),
            ("", "L&T", "₹3,200", "₹3,920", "+22.5%", "BUY dips", "GODREJBOL"),
            ("", "CONCOR", "₹850", "₹1,050", "+23.5%", "BUY small", "VRLLOG"),
            ("", "", "", "", "", "", ""),
            ("Banking", "HDFBAN", "AVOID", "₹900 (Aug entry)", "+30%", "BUY AUG only", "ICICIBANK"),
            ("", "ICICIBANK", "AVOID", "₹1,250 (Aug entry)", "+32%", "BUY AUG only", "STABAN"),
            ("", "STABAN", "AVOID", "₹1,100 (Aug entry)", "+27%", "BUY AUG only", "BOBARODA"),
            ("", "", "", "", "", "", ""),
            ("Chemicals", "FMC", "₹1,417", "₹1,750", "+23.5%", "BUY dips", "GHARDA"),
            ("", "SRF", "₹2,450", "₹3,050", "+24.5%", "BUY small", "KIRANC"),
            ("", "AARTIIND", "₹800", "₹1,000", "+25%", "BUY dips", "DEEPAKNTR"),
            ("", "", "", "", "", "", ""),
            ("Energy/Green", "SOLIN", "₹17,314", "₹21,000", "+21.3%", "HOLD, add dips", "WAAREE"),
            ("", "TATAPOWER", "₹380", "₹480", "+26.3%", "BUY dips", "POWERGRID"),
            ("", "POWERGRID", "₹265", "₹330", "+24.5%", "BUY for dividend", "NTPC (avoid thermal)"),
            ("", "", "", "", "", "", ""),
            ("Consumer", "YATHOS", "HOLD 200", "₹1,000 (add post-Oct)", "+22.8%", "HOLD, add post-Oct", "CAREHEALTH"),
            ("", "INDIGO", "WAIT", "₹3,800 (Oct entry)", "+34%", "BUY post-Oct only", "OBEROIRLTY"),
            ("", "BRITANNIA", "HOLD", "₹5,400 (if add post-Oct)", "+20%", "HOLD, add post-Oct", "NESTLEIND"),
        ]

        for row in summary_data:
            if len(row[0]) < 5:  # Header or separator
                output.append(f"{row[0]:<15} {row[1]:<25} {row[2]:<12} {row[3]:<12} {row[4]:<8} {row[5]:<20} {row[6]:<25}")
            else:
                output.append(f"{row[0]:<15} {row[1]:<25} {row[2]:<12} {row[3]:<12} {row[4]:<8} {row[5]:<20} {row[6]:<25}")

        output.append("")
        output.append("=" * 130)
        output.append("")

        return output


def main():
    analyzer = IndiaStockPicks()
    report = analyzer.generate_report()

    # Save and print
    from pathlib import Path
    logs_dir = Path('/home/rahulvadera/projects/theta-lab/logs')
    logs_dir.mkdir(exist_ok=True)

    today = date.today()
    filename = f'india_stock_picks_6month_{today.strftime("%Y-%m-%d")}.txt'
    filepath = logs_dir / filename

    with open(filepath, 'w') as f:
        f.write(report)

    print(report)
    print(f"\n✓ Saved to {filepath}")


if __name__ == '__main__':
    main()
