from __future__ import annotations

"""Dynamic screening universes for the monthly report."""


US_FLAGS_BY_SYMBOL = {
    "BE": ['SPECULATIVE_STORY', 'GOING_CONCERN'],
    "PCG": ['REGULATORY_RISK'],
    "BA": ['TURNAROUND_UNPROVEN', 'BINARY_EVENT_RISK'],
    "RKLB": ['SPECULATIVE_STORY', 'BINARY_EVENT_RISK'],
    "ALAB": ['AI_CONCENTRATION', 'SPECULATIVE_STORY'],
    "DELL": ['THIN_MARGINS', 'LOW_MOAT'],
    "HPE": ['THIN_MARGINS', 'LOW_MOAT'],
    "SMCI": ['ACCOUNTING_RISK', 'DELISTING_RISK'],
    "WDC": ['HIGH_DEBT', 'COMMODITY_PRICE_RISK'],
    "CRWD": ['AI_CONCENTRATION'],
    "PANW": ['AI_CONCENTRATION'],
    "RBRK": ['SPECULATIVE_STORY', 'LOW_OPTIONS_LIQUIDITY'],
    "S": ['SPECULATIVE_STORY', 'LOW_OPTIONS_LIQUIDITY'],
    "ZS": ['AI_CONCENTRATION', 'HIGH_DEBT'],
    "SLB": ['COMMODITY_PRICE_RISK'],
    "HAL": ['COMMODITY_PRICE_RISK'],
    "OXY": ['COMMODITY_PRICE_RISK'],
    "PBR": ['COMMODITY_PRICE_RISK', 'REGULATORY_RISK'],    # Brazil nationalization risk
    "CCJ": ['COMMODITY_PRICE_RISK'],                        # uranium price cycle
    "LASR": ['SPECULATIVE_STORY', 'LOW_MOAT'],              # emerging defense-laser tech
    "MUFG": ['REGULATORY_RISK'],                            # Japan financial regulation
    "MRNA": ['PERMANENT_EXIT'],
    "NVDA": ['AI_CONCENTRATION', 'CHINA_EXPOSURE'],
    "META": ['AI_CONCENTRATION', 'REGULATORY_RISK'],
    "GOOGL": ['AI_CONCENTRATION', 'REGULATORY_RISK'],
    "COIN": ['REGULATORY_RISK', 'HIGH_DEBT'],
    "MSTR": ['HIGH_DEBT', 'SPECULATIVE_STORY'],
    # Platform & Subscription Growth — contrarian rotation thesis
    "TSLA": ['THIN_MARGINS', 'LOW_MOAT', 'CHINA_EXPOSURE'],
    "NU": ['LOW_MOAT'],
}

INDIA_FLAGS_BY_SYMBOL = {
    "NTPC": ['COMMODITY_PRICE_RISK'],
    "POWERGRID": ['COMMODITY_PRICE_RISK'],
    "ADANIGREEN": ['REGULATORY_RISK'],
    "BAJFINANCE": ['HIGH_DEBT'],
    "TATAMOTORS": ['CHINA_EXPOSURE'],
}

EXTRA_SYMBOL_FLAGS = {
    "PYPL": ['PERMANENT_EXIT'],
    "AAPL": ['CHINA_EXPOSURE'],
    "QCOM": ['CHINA_EXPOSURE'],
    "MRVL": ['AI_CONCENTRATION'],
    "MCHI": ['CHINA_EXPOSURE'],
    "EWZ": ['REGULATORY_RISK'],
    "ADANIPORTS": ['REGULATORY_RISK'],
}

QUALITY_FLAGS_BY_SYMBOL = {**US_FLAGS_BY_SYMBOL, **INDIA_FLAGS_BY_SYMBOL, **EXTRA_SYMBOL_FLAGS}


# ── 3-Month Strategic Macro Focus ─────────────────────────────────────────────
# Rahul's thesis: Anti-AI rotation + Iran war macro.
# Direct 60-70% of NEW premium capital into focus names for next 3 months.
# Keep existing AI positions for covered-call income — add NO new AI CSPs/strangles.
# AI concentration in portfolio should stay ≤50-60% (existing positions only).
STRATEGIC_MACRO_FOCUS: dict = {
    "active": True,
    "horizon_months": 3,
    "new_trade_allocation_pct": (60, 70),   # target % of new premium into focus names
    "ai_max_pct": 60,                        # hard cap on AI-sector concentration
    "thesis": (
        "Anti-AI rotation + Iran war macro: direct 60-70% of new premium capital "
        "into focus names for the next 3 months. Keep existing AI positions for "
        "covered-call income but add no new AI-sector CSPs/strangles."
    ),
    "symbols": ["PBR", "CCJ", "SHOP", "LASR", "NU", "MUFG"],
    "rationale": {
        "PBR":  ("Brazilian oil major; Iran geopolitical premium + EM energy torque; "
                 "anti-AI macro hedge; low P/E with high FCF yield."),
        "CCJ":  ("Uranium leader; nuclear power demand secular + AI data-center power "
                 "irony; clean-energy inflection; tier-1 quality."),
        "SHOP": ("Quality e-commerce infrastructure; merchant lock-in moat; orphaned "
                 "by AI mania — rotation target when AI trade deflates."),
        "LASR": ("Laser/directed-energy defense tech; Iran war escalation beneficiary; "
                 "DoD directed-energy spend ramp; small-cap with liquid options."),
        "NU":   ("LatAm digital bank; 100M+ users; quality non-AI growth; "
                 "EM credit-cycle expansion; liquid ADR."),
        "MUFG": ("Japanese megabank ADR; yen-appreciation play; international "
                 "diversification; non-US financial exposure; liquid options."),
    },
}


def _entry(symbol: str, sector: str, tier: int, preferred_strategy: str, min_capital: int, notes: str, flags: list[str] | None = None) -> dict:
    return {
        "symbol": symbol,
        "sector": sector,
        "tier": tier,
        "preferred_strategy": preferred_strategy,
        "min_capital": min_capital,
        "notes": notes,
        "flags": flags or [],
    }


US_UNIVERSE = [
    _entry('VST', 'Nuclear & Clean Energy', 2, 'CSP_or_strangle', 12000, 'Power demand + merchant generation leverage.', US_FLAGS_BY_SYMBOL.get('VST')),
    _entry('CEG', 'Nuclear & Clean Energy', 1, 'CSP_or_strangle', 18000, 'Best-in-class nuclear exposure.', US_FLAGS_BY_SYMBOL.get('CEG')),
    _entry('NRG', 'Nuclear & Clean Energy', 2, 'CSP', 9000, 'Retail power + generation cash flow.', US_FLAGS_BY_SYMBOL.get('NRG')),
    _entry('BE', 'Nuclear & Clean Energy', 3, 'CSP', 7000, 'Speculative clean-energy volatility.', US_FLAGS_BY_SYMBOL.get('BE')),
    _entry('NEE', 'Nuclear & Clean Energy', 1, 'CSP', 10000, 'Large-cap clean utility core name.', US_FLAGS_BY_SYMBOL.get('NEE')),
    _entry('AES', 'Nuclear & Clean Energy', 2, 'CSP', 6000, 'Transition utility with yield support.', US_FLAGS_BY_SYMBOL.get('AES')),
    _entry('ETR', 'Nuclear & Clean Energy', 1, 'CSP', 9000, 'Utility + nuclear fleet stability.', US_FLAGS_BY_SYMBOL.get('ETR')),
    _entry('PPL', 'Nuclear & Clean Energy', 1, 'CSP', 5000, 'Defensive regulated utility.', US_FLAGS_BY_SYMBOL.get('PPL')),
    _entry('DTE', 'Nuclear & Clean Energy', 1, 'CSP', 11000, 'Midwest utility with infrastructure angle.', US_FLAGS_BY_SYMBOL.get('DTE')),
    _entry('EXC', 'Nuclear & Clean Energy', 1, 'CSP', 7000, 'Utility cash flow + nuclear footprint.', US_FLAGS_BY_SYMBOL.get('EXC')),
    _entry('PCG', 'Nuclear & Clean Energy', 2, 'CSP', 5000, 'Higher-beta California utility.', US_FLAGS_BY_SYMBOL.get('PCG')),
    _entry('SO', 'Nuclear & Clean Energy', 1, 'CSP', 7000, 'Defensive regulated utility income name.', US_FLAGS_BY_SYMBOL.get('SO')),
    _entry('CCJ', 'Nuclear & Clean Energy', 1, 'CSP', 10000, 'Uranium leader; nuclear power demand secular + AI data-center power irony; clean-energy inflection.', US_FLAGS_BY_SYMBOL.get('CCJ')),
    _entry('LMT', 'Defense & Aerospace', 1, 'CSP', 15000, 'Prime defense contractor, resilient backlog.', US_FLAGS_BY_SYMBOL.get('LMT')),
    _entry('RTX', 'Defense & Aerospace', 1, 'CSP_or_strangle', 12000, 'Defense + commercial aero diversification.', US_FLAGS_BY_SYMBOL.get('RTX')),
    _entry('GD', 'Defense & Aerospace', 1, 'CSP', 15000, 'Submarine/business jet exposure.', US_FLAGS_BY_SYMBOL.get('GD')),
    _entry('NOC', 'Defense & Aerospace', 1, 'CSP', 17000, 'Mission-critical defense programs.', US_FLAGS_BY_SYMBOL.get('NOC')),
    _entry('BA', 'Defense & Aerospace', 3, 'CSP', 12000, 'Turnaround volatility, size small.', US_FLAGS_BY_SYMBOL.get('BA')),
    _entry('RKLB', 'Defense & Aerospace', 3, 'strangle', 5000, 'Space launch volatility, speculative.', US_FLAGS_BY_SYMBOL.get('RKLB')),
    _entry('HII', 'Defense & Aerospace', 1, 'CSP', 14000, 'Naval shipbuilding scarcity premium.', US_FLAGS_BY_SYMBOL.get('HII')),
    _entry('L3H', 'Defense & Aerospace', 1, 'CSP', 13000, 'Electronics/ISR exposure.', US_FLAGS_BY_SYMBOL.get('L3H')),
    _entry('LDOS', 'Defense & Aerospace', 2, 'CSP', 9000, 'Services + cyber adjacencies.', US_FLAGS_BY_SYMBOL.get('LDOS')),
    _entry('KTOS', 'Defense & Aerospace', 3, 'CSP', 4000, 'Emerging defense tech.', US_FLAGS_BY_SYMBOL.get('KTOS')),
    _entry('AXON', 'Defense & Aerospace', 1, 'CC', 15000, 'Existing portfolio name; prefer covered calls over new puts.', US_FLAGS_BY_SYMBOL.get('AXON')),
    _entry('LASR', 'Defense & Aerospace', 2, 'CSP', 5000, 'Laser/directed-energy defense tech; Iran war escalation beneficiary; DoD directed-energy spend ramp.', US_FLAGS_BY_SYMBOL.get('LASR')),
    _entry('VRT', 'AI Infrastructure & Data Center', 1, 'CSP_or_strangle', 12000, 'Power/cooling beneficiary of AI buildout.', US_FLAGS_BY_SYMBOL.get('VRT')),
    _entry('APH', 'AI Infrastructure & Data Center', 1, 'CSP', 11000, 'Connectivity/infrastructure quality compounder.', US_FLAGS_BY_SYMBOL.get('APH')),
    _entry('ALAB', 'AI Infrastructure & Data Center', 2, 'strangle', 8000, 'High-beta AI networking exposure.', US_FLAGS_BY_SYMBOL.get('ALAB')),
    _entry('DELL', 'AI Infrastructure & Data Center', 2, 'CSP', 9000, 'Server/AI demand plus enterprise base.', US_FLAGS_BY_SYMBOL.get('DELL')),
    _entry('HPE', 'AI Infrastructure & Data Center', 2, 'CSP', 5000, 'Value AI infra angle.', US_FLAGS_BY_SYMBOL.get('HPE')),
    _entry('SMCI', 'AI Infrastructure & Data Center', 3, 'strangle', 9000, 'Very high vol; only when conditions align.', US_FLAGS_BY_SYMBOL.get('SMCI')),
    _entry('NTAP', 'AI Infrastructure & Data Center', 2, 'CSP', 9000, 'Storage/data management.', US_FLAGS_BY_SYMBOL.get('NTAP')),
    _entry('STX', 'AI Infrastructure & Data Center', 2, 'CSP', 8000, 'Data storage cyclical.', US_FLAGS_BY_SYMBOL.get('STX')),
    _entry('WDC', 'AI Infrastructure & Data Center', 2, 'CSP', 8000, 'Memory/storage beta.', US_FLAGS_BY_SYMBOL.get('WDC')),
    _entry('KEYS', 'AI Infrastructure & Data Center', 1, 'CSP', 12000, 'Test/measurement picks-and-shovels.', US_FLAGS_BY_SYMBOL.get('KEYS')),
    _entry('CRWD', 'Cybersecurity', 1, 'CC', 15000, 'Existing portfolio name; monetize strength with CCs.', US_FLAGS_BY_SYMBOL.get('CRWD')),
    _entry('PANW', 'Cybersecurity', 1, 'CSP', 14000, 'Large-cap platform leader.', US_FLAGS_BY_SYMBOL.get('PANW')),
    _entry('RBRK', 'Cybersecurity', 3, 'CSP', 7000, 'Newer public backup/cyber name.', US_FLAGS_BY_SYMBOL.get('RBRK')),
    _entry('S', 'Cybersecurity', 3, 'CSP', 4000, 'Speculative endpoint/security beta.', US_FLAGS_BY_SYMBOL.get('S')),
    _entry('FTNT', 'Cybersecurity', 1, 'CSP', 8000, 'Cash-generative security franchise.', US_FLAGS_BY_SYMBOL.get('FTNT')),
    _entry('ZS', 'Cybersecurity', 2, 'CSP', 10000, 'Cloud security beta.', US_FLAGS_BY_SYMBOL.get('ZS')),
    _entry('OKTA', 'Cybersecurity', 1, 'CSP', 7000, 'Identity security, improved execution.', US_FLAGS_BY_SYMBOL.get('OKTA')),
    _entry('CYBR', 'Cybersecurity', 2, 'CSP', 12000, 'Privileged access security leader.', US_FLAGS_BY_SYMBOL.get('CYBR')),
    _entry('GS', 'Financials', 1, 'CSP', 18000, 'Capital markets franchise.', US_FLAGS_BY_SYMBOL.get('GS')),
    _entry('JPM', 'Financials', 1, 'CSP', 15000, 'Best-in-class money center bank.', US_FLAGS_BY_SYMBOL.get('JPM')),
    _entry('MS', 'Financials', 1, 'CSP', 12000, 'Wealth + IB balance.', US_FLAGS_BY_SYMBOL.get('MS')),
    _entry('BAC', 'Financials', 1, 'CSP', 6000, 'Rate-sensitive bank bellwether.', US_FLAGS_BY_SYMBOL.get('BAC')),
    _entry('BLK', 'Financials', 1, 'CSP', 20000, 'Asset management core compounder.', US_FLAGS_BY_SYMBOL.get('BLK')),
    _entry('SCHW', 'Financials', 1, 'CSP', 7000, 'Brokerage + sweep deposits.', US_FLAGS_BY_SYMBOL.get('SCHW')),
    _entry('V', 'Financials', 1, 'CSP', 14000, 'Toll-booth payments franchise.', US_FLAGS_BY_SYMBOL.get('V')),
    _entry('MA', 'Financials', 1, 'CSP', 17000, 'High-quality payments compounder.', US_FLAGS_BY_SYMBOL.get('MA')),
    _entry('AXP', 'Financials', 1, 'CSP', 14000, 'Affluent spend + lending.', US_FLAGS_BY_SYMBOL.get('AXP')),
    _entry('MUFG', 'Financials', 2, 'CSP', 9000, 'Japanese megabank ADR; yen-appreciation play; international financial diversification; non-US exposure.', US_FLAGS_BY_SYMBOL.get('MUFG')),
    _entry('XOM', 'Energy', 1, 'CSP', 11000, 'Integrated major, strong cash returns.', US_FLAGS_BY_SYMBOL.get('XOM')),
    _entry('CVX', 'Energy', 1, 'CSP', 13000, 'Integrated major, lower beta.', US_FLAGS_BY_SYMBOL.get('CVX')),
    _entry('COP', 'Energy', 1, 'CSP', 11000, 'E&P torque to oil/gas.', US_FLAGS_BY_SYMBOL.get('COP')),
    _entry('SLB', 'Energy', 2, 'CSP', 6000, 'Oilfield services cycle.', US_FLAGS_BY_SYMBOL.get('SLB')),
    _entry('HAL', 'Energy', 2, 'CSP', 5000, 'Oil services beta.', US_FLAGS_BY_SYMBOL.get('HAL')),
    _entry('OXY', 'Energy', 2, 'CSP', 6000, 'Buffett-backed oil beta.', US_FLAGS_BY_SYMBOL.get('OXY')),
    _entry('MPC', 'Energy', 1, 'CSP', 14000, 'Refining + midstream cash flow.', US_FLAGS_BY_SYMBOL.get('MPC')),
    _entry('PSX', 'Energy', 1, 'CSP', 13000, 'Refining/chemicals quality name.', US_FLAGS_BY_SYMBOL.get('PSX')),
    _entry('PBR', 'Energy', 2, 'CSP', 7000, 'Brazilian oil major; Iran geopolitical premium + EM energy torque; anti-AI macro hedge; high FCF yield.', US_FLAGS_BY_SYMBOL.get('PBR')),
    _entry('CAT', 'Industrials & Infrastructure', 1, 'CSP', 15000, 'Construction/mining cyclicality.', US_FLAGS_BY_SYMBOL.get('CAT')),
    _entry('DE', 'Industrials & Infrastructure', 1, 'CSP', 17000, 'Ag + construction machinery.', US_FLAGS_BY_SYMBOL.get('DE')),
    _entry('URI', 'Industrials & Infrastructure', 1, 'CSP', 20000, 'Rental equipment leader.', US_FLAGS_BY_SYMBOL.get('URI')),
    _entry('PWR', 'Industrials & Infrastructure', 1, 'CSP', 13000, 'Grid/data-center infrastructure builder.', US_FLAGS_BY_SYMBOL.get('PWR')),
    _entry('PCAR', 'Industrials & Infrastructure', 1, 'CSP', 9000, 'Truck cycle with quality balance sheet.', US_FLAGS_BY_SYMBOL.get('PCAR')),
    _entry('EMR', 'Industrials & Infrastructure', 1, 'CSP', 8000, 'Automation/industrial diversification.', US_FLAGS_BY_SYMBOL.get('EMR')),
    _entry('ETN', 'Industrials & Infrastructure', 1, 'CSP', 16000, 'Electrical infrastructure leader.', US_FLAGS_BY_SYMBOL.get('ETN')),
    _entry('IR', 'Industrials & Infrastructure', 2, 'CSP', 9000, 'HVAC/industrial exposure.', US_FLAGS_BY_SYMBOL.get('IR')),
    _entry('UNH', 'Healthcare & Biotech', 1, 'CC', 15000, 'Existing assigned/core name; prefer CCs.', US_FLAGS_BY_SYMBOL.get('UNH')),
    _entry('ELV', 'Healthcare & Biotech', 1, 'CSP', 17000, 'Managed care quality peer.', US_FLAGS_BY_SYMBOL.get('ELV')),
    _entry('HUM', 'Healthcare & Biotech', 2, 'CSP', 14000, 'Medicare Advantage volatility.', US_FLAGS_BY_SYMBOL.get('HUM')),
    _entry('LLY', 'Healthcare & Biotech', 1, 'CSP', 22000, 'GLP-1 leader, expensive but liquid.', US_FLAGS_BY_SYMBOL.get('LLY')),
    _entry('ABBV', 'Healthcare & Biotech', 1, 'CSP', 11000, 'Defensive pharma income.', US_FLAGS_BY_SYMBOL.get('ABBV')),
    _entry('AMGN', 'Healthcare & Biotech', 1, 'CSP', 14000, 'Large-cap biotech stability.', US_FLAGS_BY_SYMBOL.get('AMGN')),
    _entry('REGN', 'Healthcare & Biotech', 1, 'CSP', 20000, 'Biotech quality, higher notional.', US_FLAGS_BY_SYMBOL.get('REGN')),
    _entry('VRTX', 'Healthcare & Biotech', 1, 'CSP', 17000, 'Profitable biotech with pipeline optionality.', US_FLAGS_BY_SYMBOL.get('VRTX')),
    _entry('MRNA', 'Healthcare & Biotech', 3, 'CC', 7000, 'Existing portfolio exit/CC monetization only.', US_FLAGS_BY_SYMBOL.get('MRNA')),
    _entry('BMY', 'Healthcare & Biotech', 1, 'CSP', 6000, 'Defensive pharma valuation support.', US_FLAGS_BY_SYMBOL.get('BMY')),
    _entry('COST', 'Consumer & Retail', 1, 'CSP', 22000, 'Best-in-class retail quality.', US_FLAGS_BY_SYMBOL.get('COST')),
    _entry('HD', 'Consumer & Retail', 1, 'CSP', 16000, 'Housing repair spend.', US_FLAGS_BY_SYMBOL.get('HD')),
    _entry('LOW', 'Consumer & Retail', 1, 'CSP', 13000, 'Home improvement peer.', US_FLAGS_BY_SYMBOL.get('LOW')),
    _entry('TGT', 'Consumer & Retail', 2, 'CSP', 8000, 'Retail turnaround candidate.', US_FLAGS_BY_SYMBOL.get('TGT')),
    _entry('NKE', 'Consumer & Retail', 2, 'CSP', 7000, 'Brand reset + volatility.', US_FLAGS_BY_SYMBOL.get('NKE')),
    _entry('SBUX', 'Consumer & Retail', 2, 'CSP', 7000, 'Consumer turnaround with liquid options.', US_FLAGS_BY_SYMBOL.get('SBUX')),
    # Platform & Subscription Growth — quality growth orphaned by AI mania; contrarian rotation targets.
    # Thesis: durable subscription/marketplace revenue, network moats, underowned while capital crowded into AI.
    # Sector weight is calibrated to surface these when RSI oversold + IVR spikes even in bear regime.
    # ADRs (MELI, SE, NU) provide international diversification with liquid US-listed options.
    _entry('NFLX', 'Platform & Subscription Growth', 2, 'CSP_or_strangle', 8000, 'Subscription media moat; ad-tier + password crackdown driving FCF; AI-mania rotation target.'),
    _entry('SPOT', 'Platform & Subscription Growth', 2, 'CSP_or_strangle', 12000, 'Audio platform monopoly; margin expansion story; AI-mania orphan.'),
    _entry('SHOP', 'Platform & Subscription Growth', 2, 'CSP_or_strangle', 9000, 'E-commerce infrastructure network; merchant lock-in moat; secular commerce tailwind.'),
    _entry('UBER', 'Platform & Subscription Growth', 2, 'CSP', 6000, 'Marketplace network effect; profitable at scale; rideshare + delivery flywheel.'),
    _entry('ABNB', 'Platform & Subscription Growth', 2, 'CSP', 10000, 'Asset-light marketplace; global travel network; premium spend resilience.'),
    _entry('TSLA', 'Platform & Subscription Growth', 3, 'strangle', 8000, 'High-vol EV + energy + autonomy optionality; volatility income play, not conviction long.', US_FLAGS_BY_SYMBOL.get('TSLA')),
    _entry('MELI', 'Platform & Subscription Growth', 2, 'CSP', 15000, 'LatAm Amazon+PayPal; 40%+ revenue growth; secular middle-class expansion; liquid ADR.'),
    _entry('SE', 'Platform & Subscription Growth', 3, 'CSP', 6000, 'SEA gaming+ecomm+fintech trifecta; underowned by US investors; high-growth ADR.'),
    _entry('NU', 'Platform & Subscription Growth', 3, 'CSP', 5000, 'LatAm digital bank; 100M+ users; emerging-market fintech ADR.', US_FLAGS_BY_SYMBOL.get('NU')),
    _entry('NVDA', 'Tech', 1, 'CC', 20000, 'Existing portfolio AI winner; keep for covered calls only.', US_FLAGS_BY_SYMBOL.get('NVDA')),
    _entry('ADBE', 'Tech', 1, 'CC', 15000, 'Existing portfolio name; CC monetization over new CSPs.', US_FLAGS_BY_SYMBOL.get('ADBE')),
    _entry('CRM', 'Tech', 1, 'CC', 13000, 'Existing portfolio name; covered call candidate.', US_FLAGS_BY_SYMBOL.get('CRM')),
    _entry('MSFT', 'Tech', 1, 'CC', 16000, 'Mega-cap core; keep for CCs if already owned.', US_FLAGS_BY_SYMBOL.get('MSFT')),
    _entry('META', 'Tech', 1, 'CC', 18000, 'Momentum tech; avoid doubling down via CSP.', US_FLAGS_BY_SYMBOL.get('META')),
    _entry('GOOGL', 'Tech', 1, 'CC', 10000, 'Core tech exposure for CCs.', US_FLAGS_BY_SYMBOL.get('GOOGL')),
    _entry('AMZN', 'Tech', 1, 'CC', 10000, 'Keep for CCs if assigned/owned.', US_FLAGS_BY_SYMBOL.get('AMZN')),
    _entry('APP', 'Tech', 3, 'CC', 9000, 'High-beta existing name; CC only.', US_FLAGS_BY_SYMBOL.get('APP')),
    _entry('COIN', 'Tech', 3, 'CC', 10000, 'Crypto beta; monetize with CCs only if owned.', US_FLAGS_BY_SYMBOL.get('COIN')),
    _entry('MSTR', 'Tech', 3, 'CC', 22000, 'Extreme vol; CC only if already held.', US_FLAGS_BY_SYMBOL.get('MSTR')),
]


INDIA_UNIVERSE = [
    _entry('NTPC', 'Energy & Power', 1, 'CSP', 25000, 'Defensive PSU power exposure.', INDIA_FLAGS_BY_SYMBOL.get('NTPC')),
    _entry('POWERGRID', 'Energy & Power', 1, 'CSP', 25000, 'Regulated transmission utility.', INDIA_FLAGS_BY_SYMBOL.get('POWERGRID')),
    _entry('ADANIGREEN', 'Energy & Power', 3, 'CSP', 40000, 'High-beta renewable play.', INDIA_FLAGS_BY_SYMBOL.get('ADANIGREEN')),
    _entry('TATAPOWER', 'Energy & Power', 2, 'CSP', 30000, 'Integrated power + transition exposure.', INDIA_FLAGS_BY_SYMBOL.get('TATAPOWER')),
    _entry('TORNTPOWER', 'Energy & Power', 2, 'CSP', 35000, 'Private utility compounder.', INDIA_FLAGS_BY_SYMBOL.get('TORNTPOWER')),
    _entry('CESC', 'Energy & Power', 2, 'CSP', 20000, 'Utility yield + lower notional.', INDIA_FLAGS_BY_SYMBOL.get('CESC')),
    _entry('JSWENERGY', 'Energy & Power', 2, 'CSP', 30000, 'Power growth + volatility.', INDIA_FLAGS_BY_SYMBOL.get('JSWENERGY')),
    _entry('SOLARINDS', 'Energy & Power', 2, 'CSP', 25000, 'Solar sector growth; India energy transition secular story; not rate-sensitive.', INDIA_FLAGS_BY_SYMBOL.get('SOLARINDS')),
    _entry('HAL', 'Defense & Aerospace', 1, 'CSP', 45000, 'Flagship defense aerospace leader.', INDIA_FLAGS_BY_SYMBOL.get('HAL')),
    _entry('BEL', 'Defense & Aerospace', 1, 'CSP', 30000, 'Defense electronics leader.', INDIA_FLAGS_BY_SYMBOL.get('BEL')),
    _entry('BHEL', 'Defense & Aerospace', 2, 'CSP', 25000, 'Defense/industrial PSU beta.', INDIA_FLAGS_BY_SYMBOL.get('BHEL')),
    _entry('COCHINSHIP', 'Defense & Aerospace', 2, 'CSP', 30000, 'Shipbuilding/order book support.', INDIA_FLAGS_BY_SYMBOL.get('COCHINSHIP')),
    _entry('GRSE', 'Defense & Aerospace', 2, 'CSP', 30000, 'Defense shipyard beta.', INDIA_FLAGS_BY_SYMBOL.get('GRSE')),
    _entry('PARASDEF', 'Defense & Aerospace', 3, 'CSP', 25000, 'Smaller-cap defense electronics.', INDIA_FLAGS_BY_SYMBOL.get('PARASDEF')),
    _entry('MTAR', 'Defense & Aerospace', 3, 'CSP', 25000, 'Precision engineering/defense exposure.', INDIA_FLAGS_BY_SYMBOL.get('MTAR')),
    _entry('HDFCBANK', 'Banking & NBFC', 1, 'CSP', 30000, 'Private bank core holding.', INDIA_FLAGS_BY_SYMBOL.get('HDFCBANK')),
    _entry('ICICIBANK', 'Banking & NBFC', 1, 'CSP', 30000, 'Private bank leader.', INDIA_FLAGS_BY_SYMBOL.get('ICICIBANK')),
    _entry('KOTAKBANK', 'Banking & NBFC', 1, 'CSP', 30000, 'High-quality bank franchise.', INDIA_FLAGS_BY_SYMBOL.get('KOTAKBANK')),
    _entry('AXISBANK', 'Banking & NBFC', 1, 'CSP', 25000, 'Private bank beta.', INDIA_FLAGS_BY_SYMBOL.get('AXISBANK')),
    _entry('SBIN', 'Banking & NBFC', 1, 'CSP', 25000, 'PSU bank bellwether.', INDIA_FLAGS_BY_SYMBOL.get('SBIN')),
    _entry('BAJFINANCE', 'Banking & NBFC', 1, 'CSP', 45000, 'NBFC compounder with liquid derivatives.', INDIA_FLAGS_BY_SYMBOL.get('BAJFINANCE')),
    _entry('CHOLAFIN', 'Banking & NBFC', 2, 'CSP', 30000, 'Vehicle finance + rural credit beta.', INDIA_FLAGS_BY_SYMBOL.get('CHOLAFIN')),
    _entry('TCS', 'IT', 1, 'CSP', 40000, 'Large-cap IT services anchor.', INDIA_FLAGS_BY_SYMBOL.get('TCS')),
    _entry('INFY', 'IT', 1, 'CSP', 30000, 'Large-cap IT services liquid name.', INDIA_FLAGS_BY_SYMBOL.get('INFY')),
    _entry('WIPRO', 'IT', 2, 'CSP', 20000, 'Lower-beta IT optionality.', INDIA_FLAGS_BY_SYMBOL.get('WIPRO')),
    _entry('HCLTECH', 'IT', 1, 'CSP', 30000, 'IT services quality name.', INDIA_FLAGS_BY_SYMBOL.get('HCLTECH')),
    _entry('TECHM', 'IT', 2, 'CSP', 25000, 'Telecom/enterprise IT beta.', INDIA_FLAGS_BY_SYMBOL.get('TECHM')),
    _entry('LTIM', 'IT', 2, 'CSP', 35000, 'Mid-tier IT services growth.', INDIA_FLAGS_BY_SYMBOL.get('LTIM')),
    _entry('SUNPHARMA', 'Pharma', 1, 'CSP', 30000, 'Large-cap pharma leader.', INDIA_FLAGS_BY_SYMBOL.get('SUNPHARMA')),
    _entry('DRREDDY', 'Pharma', 1, 'CSP', 35000, 'Export pharma quality name.', INDIA_FLAGS_BY_SYMBOL.get('DRREDDY')),
    _entry('CIPLA', 'Pharma', 1, 'CSP', 25000, 'Defensive pharma exposure.', INDIA_FLAGS_BY_SYMBOL.get('CIPLA')),
    _entry('DIVISLAB', 'Pharma', 1, 'CSP', 35000, 'High-quality API/export franchise.', INDIA_FLAGS_BY_SYMBOL.get('DIVISLAB')),
    _entry('AUROBINDO', 'Pharma', 2, 'CSP', 25000, 'Higher-beta pharma value name.', INDIA_FLAGS_BY_SYMBOL.get('AUROBINDO')),
    _entry('LT', 'Infrastructure & Capital Goods', 1, 'CSP', 40000, 'Core infra/capex proxy.', INDIA_FLAGS_BY_SYMBOL.get('LT')),
    _entry('SIEMENS', 'Infrastructure & Capital Goods', 1, 'CSP', 45000, 'Capex/electrification leader.', INDIA_FLAGS_BY_SYMBOL.get('SIEMENS')),
    _entry('ABB', 'Infrastructure & Capital Goods', 1, 'CSP', 45000, 'Automation and electrification.', INDIA_FLAGS_BY_SYMBOL.get('ABB')),
    _entry('CUMMINSIND', 'Infrastructure & Capital Goods', 1, 'CSP', 35000, 'Power systems and industrial demand.', INDIA_FLAGS_BY_SYMBOL.get('CUMMINSIND')),
    _entry('BHARATFORG', 'Infrastructure & Capital Goods', 2, 'CSP', 30000, 'Forgings + defense/auto leverage.', INDIA_FLAGS_BY_SYMBOL.get('BHARATFORG')),
    _entry('KAYNES', 'Infrastructure & Capital Goods', 2, 'CSP', 30000, 'Electronics MFG; PLI scheme beneficiary; India domestic manufacturing compounder.', INDIA_FLAGS_BY_SYMBOL.get('KAYNES')),
    _entry('POWERINDIA', 'Infrastructure & Capital Goods', 2, 'CSP', 20000, 'Power infrastructure capex; government-backed electrification secular tailwind.', INDIA_FLAGS_BY_SYMBOL.get('POWERINDIA')),
    _entry('MARUTI', 'Auto', 1, 'CSP', 50000, 'Passenger vehicle leader.', INDIA_FLAGS_BY_SYMBOL.get('MARUTI')),
    _entry('TATAMOTORS', 'Auto', 2, 'CSP', 30000, 'JLR + domestic auto beta.', INDIA_FLAGS_BY_SYMBOL.get('TATAMOTORS')),
    _entry('M&M', 'Auto', 1, 'CSP', 35000, 'SUV/tractor cycle leader.', INDIA_FLAGS_BY_SYMBOL.get('M&M')),
    _entry('BAJAJ-AUTO', 'Auto', 1, 'CSP', 45000, 'Two-wheeler/export franchise.', INDIA_FLAGS_BY_SYMBOL.get('BAJAJ-AUTO')),
    _entry('EICHERMOT', 'Auto', 1, 'CSP', 40000, 'Premium motorcycle franchise.', INDIA_FLAGS_BY_SYMBOL.get('EICHERMOT')),
    _entry('HINDUNILVR', 'Consumer', 1, 'CSP', 30000, 'Staples defensive anchor.', INDIA_FLAGS_BY_SYMBOL.get('HINDUNILVR')),
    _entry('ITC', 'Consumer', 1, 'CSP', 20000, 'Yield + staples stability.', INDIA_FLAGS_BY_SYMBOL.get('ITC')),
    _entry('NESTLEIND', 'Consumer', 1, 'CSP', 50000, 'Premium staples quality.', INDIA_FLAGS_BY_SYMBOL.get('NESTLEIND')),
    _entry('BRITANNIA', 'Consumer', 1, 'CSP', 35000, 'Staples quality with brand strength.', INDIA_FLAGS_BY_SYMBOL.get('BRITANNIA')),
]


US_UNIVERSE_BY_SYMBOL = {item["symbol"]: item for item in US_UNIVERSE}
INDIA_UNIVERSE_BY_SYMBOL = {item["symbol"]: item for item in INDIA_UNIVERSE}
