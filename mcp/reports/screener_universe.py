from __future__ import annotations

"""Dynamic screening universes for the monthly report."""


def _entry(symbol: str, sector: str, tier: int, preferred_strategy: str, min_capital: int, notes: str) -> dict:
    return {
        "symbol": symbol,
        "sector": sector,
        "tier": tier,
        "preferred_strategy": preferred_strategy,
        "min_capital": min_capital,
        "notes": notes,
    }


US_UNIVERSE = [
    # Nuclear & Clean Energy
    _entry("VST", "Nuclear & Clean Energy", 2, "CSP_or_strangle", 12000, "Power demand + merchant generation leverage."),
    _entry("CEG", "Nuclear & Clean Energy", 1, "CSP_or_strangle", 18000, "Best-in-class nuclear exposure."),
    _entry("NRG", "Nuclear & Clean Energy", 2, "CSP", 9000, "Retail power + generation cash flow."),
    _entry("BE", "Nuclear & Clean Energy", 3, "CSP", 7000, "Speculative clean-energy volatility."),
    _entry("NEE", "Nuclear & Clean Energy", 1, "CSP", 10000, "Large-cap clean utility core name."),
    _entry("AES", "Nuclear & Clean Energy", 2, "CSP", 6000, "Transition utility with yield support."),
    _entry("ETR", "Nuclear & Clean Energy", 1, "CSP", 9000, "Utility + nuclear fleet stability."),
    _entry("PPL", "Nuclear & Clean Energy", 1, "CSP", 5000, "Defensive regulated utility."),
    _entry("DTE", "Nuclear & Clean Energy", 1, "CSP", 11000, "Midwest utility with infrastructure angle."),
    _entry("EXC", "Nuclear & Clean Energy", 1, "CSP", 7000, "Utility cash flow + nuclear footprint."),
    _entry("PCG", "Nuclear & Clean Energy", 2, "CSP", 5000, "Higher-beta California utility."),
    _entry("SO", "Nuclear & Clean Energy", 1, "CSP", 7000, "Defensive regulated utility income name."),
    # Defense & Aerospace
    _entry("LMT", "Defense & Aerospace", 1, "CSP", 15000, "Prime defense contractor, resilient backlog."),
    _entry("RTX", "Defense & Aerospace", 1, "CSP_or_strangle", 12000, "Defense + commercial aero diversification."),
    _entry("GD", "Defense & Aerospace", 1, "CSP", 15000, "Submarine/business jet exposure."),
    _entry("NOC", "Defense & Aerospace", 1, "CSP", 17000, "Mission-critical defense programs."),
    _entry("BA", "Defense & Aerospace", 3, "CSP", 12000, "Turnaround volatility, size small."),
    _entry("RKLB", "Defense & Aerospace", 3, "strangle", 5000, "Space launch volatility, speculative."),
    _entry("HII", "Defense & Aerospace", 1, "CSP", 14000, "Naval shipbuilding scarcity premium."),
    _entry("L3H", "Defense & Aerospace", 1, "CSP", 13000, "Electronics/ISR exposure."),
    _entry("LDOS", "Defense & Aerospace", 2, "CSP", 9000, "Services + cyber adjacencies."),
    _entry("KTOS", "Defense & Aerospace", 3, "CSP", 4000, "Emerging defense tech."),
    _entry("AXON", "Defense & Aerospace", 1, "CC", 15000, "Existing portfolio name; prefer covered calls over new puts."),
    # AI Infrastructure & Data Center
    _entry("VRT", "AI Infrastructure & Data Center", 1, "CSP_or_strangle", 12000, "Power/cooling beneficiary of AI buildout."),
    _entry("APH", "AI Infrastructure & Data Center", 1, "CSP", 11000, "Connectivity/infrastructure quality compounder."),
    _entry("ALAB", "AI Infrastructure & Data Center", 2, "strangle", 8000, "High-beta AI networking exposure."),
    _entry("DELL", "AI Infrastructure & Data Center", 2, "CSP", 9000, "Server/AI demand plus enterprise base."),
    _entry("HPE", "AI Infrastructure & Data Center", 2, "CSP", 5000, "Value AI infra angle."),
    _entry("SMCI", "AI Infrastructure & Data Center", 3, "strangle", 9000, "Very high vol; only when conditions align."),
    _entry("NTAP", "AI Infrastructure & Data Center", 2, "CSP", 9000, "Storage/data management."),
    _entry("STX", "AI Infrastructure & Data Center", 2, "CSP", 8000, "Data storage cyclical."),
    _entry("WDC", "AI Infrastructure & Data Center", 2, "CSP", 8000, "Memory/storage beta."),
    _entry("KEYS", "AI Infrastructure & Data Center", 1, "CSP", 12000, "Test/measurement picks-and-shovels."),
    # Cybersecurity
    _entry("CRWD", "Cybersecurity", 1, "CC", 15000, "Existing portfolio name; monetize strength with CCs."),
    _entry("PANW", "Cybersecurity", 1, "CSP", 14000, "Large-cap platform leader."),
    _entry("RBRK", "Cybersecurity", 3, "CSP", 7000, "Newer public backup/cyber name."),
    _entry("S", "Cybersecurity", 3, "CSP", 4000, "Speculative endpoint/security beta."),
    _entry("FTNT", "Cybersecurity", 1, "CSP", 8000, "Cash-generative security franchise."),
    _entry("ZS", "Cybersecurity", 2, "CSP", 10000, "Cloud security beta."),
    _entry("OKTA", "Cybersecurity", 1, "CSP", 7000, "Identity security, improved execution."),
    _entry("CYBR", "Cybersecurity", 2, "CSP", 12000, "Privileged access security leader."),
    # Financials
    _entry("GS", "Financials", 1, "CSP", 18000, "Capital markets franchise."),
    _entry("JPM", "Financials", 1, "CSP", 15000, "Best-in-class money center bank."),
    _entry("MS", "Financials", 1, "CSP", 12000, "Wealth + IB balance."),
    _entry("BAC", "Financials", 1, "CSP", 6000, "Rate-sensitive bank bellwether."),
    _entry("BLK", "Financials", 1, "CSP", 20000, "Asset management core compounder."),
    _entry("SCHW", "Financials", 1, "CSP", 7000, "Brokerage + sweep deposits."),
    _entry("V", "Financials", 1, "CSP", 14000, "Toll-booth payments franchise."),
    _entry("MA", "Financials", 1, "CSP", 17000, "High-quality payments compounder."),
    _entry("AXP", "Financials", 1, "CSP", 14000, "Affluent spend + lending."),
    # Energy (traditional + transition)
    _entry("XOM", "Energy", 1, "CSP", 11000, "Integrated major, strong cash returns."),
    _entry("CVX", "Energy", 1, "CSP", 13000, "Integrated major, lower beta."),
    _entry("COP", "Energy", 1, "CSP", 11000, "E&P torque to oil/gas."),
    _entry("SLB", "Energy", 2, "CSP", 6000, "Oilfield services cycle."),
    _entry("HAL", "Energy", 2, "CSP", 5000, "Oil services beta."),
    _entry("OXY", "Energy", 2, "CSP", 6000, "Buffett-backed oil beta."),
    _entry("MPC", "Energy", 1, "CSP", 14000, "Refining + midstream cash flow."),
    _entry("PSX", "Energy", 1, "CSP", 13000, "Refining/chemicals quality name."),
    # Industrials & Infrastructure
    _entry("CAT", "Industrials & Infrastructure", 1, "CSP", 15000, "Construction/mining cyclicality."),
    _entry("DE", "Industrials & Infrastructure", 1, "CSP", 17000, "Ag + construction machinery."),
    _entry("URI", "Industrials & Infrastructure", 1, "CSP", 20000, "Rental equipment leader."),
    _entry("PWR", "Industrials & Infrastructure", 1, "CSP", 13000, "Grid/data-center infrastructure builder."),
    _entry("PCAR", "Industrials & Infrastructure", 1, "CSP", 9000, "Truck cycle with quality balance sheet."),
    _entry("EMR", "Industrials & Infrastructure", 1, "CSP", 8000, "Automation/industrial diversification."),
    _entry("ETN", "Industrials & Infrastructure", 1, "CSP", 16000, "Electrical infrastructure leader."),
    _entry("IR", "Industrials & Infrastructure", 2, "CSP", 9000, "HVAC/industrial exposure."),
    # Healthcare & Biotech
    _entry("UNH", "Healthcare & Biotech", 1, "CC", 15000, "Existing assigned/core name; prefer CCs."),
    _entry("ELV", "Healthcare & Biotech", 1, "CSP", 17000, "Managed care quality peer."),
    _entry("HUM", "Healthcare & Biotech", 2, "CSP", 14000, "Medicare Advantage volatility."),
    _entry("LLY", "Healthcare & Biotech", 1, "CSP", 22000, "GLP-1 leader, expensive but liquid."),
    _entry("ABBV", "Healthcare & Biotech", 1, "CSP", 11000, "Defensive pharma income."),
    _entry("AMGN", "Healthcare & Biotech", 1, "CSP", 14000, "Large-cap biotech stability."),
    _entry("REGN", "Healthcare & Biotech", 1, "CSP", 20000, "Biotech quality, higher notional."),
    _entry("VRTX", "Healthcare & Biotech", 1, "CSP", 17000, "Profitable biotech with pipeline optionality."),
    _entry("MRNA", "Healthcare & Biotech", 3, "CC", 7000, "Existing portfolio exit/CC monetization only."),
    _entry("BMY", "Healthcare & Biotech", 1, "CSP", 6000, "Defensive pharma valuation support."),
    # Consumer & Retail
    _entry("COST", "Consumer & Retail", 1, "CSP", 22000, "Best-in-class retail quality."),
    _entry("HD", "Consumer & Retail", 1, "CSP", 16000, "Housing repair spend."),
    _entry("LOW", "Consumer & Retail", 1, "CSP", 13000, "Home improvement peer."),
    _entry("TGT", "Consumer & Retail", 2, "CSP", 8000, "Retail turnaround candidate."),
    _entry("NKE", "Consumer & Retail", 2, "CSP", 7000, "Brand reset + volatility."),
    _entry("SBUX", "Consumer & Retail", 2, "CSP", 7000, "Consumer turnaround with liquid options."),
    # Tech (existing portfolio names)
    _entry("NVDA", "Tech", 1, "CC", 20000, "Existing portfolio AI winner; keep for covered calls only."),
    _entry("ADBE", "Tech", 1, "CC", 15000, "Existing portfolio name; CC monetization over new CSPs."),
    _entry("CRM", "Tech", 1, "CC", 13000, "Existing portfolio name; covered call candidate."),
    _entry("MSFT", "Tech", 1, "CC", 16000, "Mega-cap core; keep for CCs if already owned."),
    _entry("META", "Tech", 1, "CC", 18000, "Momentum tech; avoid doubling down via CSP."),
    _entry("GOOGL", "Tech", 1, "CC", 10000, "Core tech exposure for CCs."),
    _entry("AMZN", "Tech", 1, "CC", 10000, "Keep for CCs if assigned/owned."),
    _entry("APP", "Tech", 3, "CC", 9000, "High-beta existing name; CC only."),
    _entry("COIN", "Tech", 3, "CC", 10000, "Crypto beta; monetize with CCs only if owned."),
    _entry("MSTR", "Tech", 3, "CC", 22000, "Extreme vol; CC only if already held."),
]


INDIA_UNIVERSE = [
    # Energy & Power
    _entry("NTPC", "Energy & Power", 1, "CSP", 25000, "Defensive PSU power exposure."),
    _entry("POWERGRID", "Energy & Power", 1, "CSP", 25000, "Regulated transmission utility."),
    _entry("ADANIGREEN", "Energy & Power", 3, "CSP", 40000, "High-beta renewable play."),
    _entry("TATAPOWER", "Energy & Power", 2, "CSP", 30000, "Integrated power + transition exposure."),
    _entry("TORNTPOWER", "Energy & Power", 2, "CSP", 35000, "Private utility compounder."),
    _entry("CESC", "Energy & Power", 2, "CSP", 20000, "Utility yield + lower notional."),
    _entry("JSWENERGY", "Energy & Power", 2, "CSP", 30000, "Power growth + volatility."),
    # Defense & Aerospace
    _entry("HAL", "Defense & Aerospace", 1, "CSP", 45000, "Flagship defense aerospace leader."),
    _entry("BEL", "Defense & Aerospace", 1, "CSP", 30000, "Defense electronics leader."),
    _entry("BHEL", "Defense & Aerospace", 2, "CSP", 25000, "Defense/industrial PSU beta."),
    _entry("COCHINSHIP", "Defense & Aerospace", 2, "CSP", 30000, "Shipbuilding/order book support."),
    _entry("GRSE", "Defense & Aerospace", 2, "CSP", 30000, "Defense shipyard beta."),
    _entry("PARASDEF", "Defense & Aerospace", 3, "CSP", 25000, "Smaller-cap defense electronics."),
    _entry("MTAR", "Defense & Aerospace", 3, "CSP", 25000, "Precision engineering/defense exposure."),
    # Banking & NBFC
    _entry("HDFCBANK", "Banking & NBFC", 1, "CSP", 30000, "Private bank core holding."),
    _entry("ICICIBANK", "Banking & NBFC", 1, "CSP", 30000, "Private bank leader."),
    _entry("KOTAKBANK", "Banking & NBFC", 1, "CSP", 30000, "High-quality bank franchise."),
    _entry("AXISBANK", "Banking & NBFC", 1, "CSP", 25000, "Private bank beta."),
    _entry("SBIN", "Banking & NBFC", 1, "CSP", 25000, "PSU bank bellwether."),
    _entry("BAJFINANCE", "Banking & NBFC", 1, "CSP", 45000, "NBFC compounder with liquid derivatives."),
    _entry("CHOLAFIN", "Banking & NBFC", 2, "CSP", 30000, "Vehicle finance + rural credit beta."),
    # IT
    _entry("TCS", "IT", 1, "CSP", 40000, "Large-cap IT services anchor."),
    _entry("INFY", "IT", 1, "CSP", 30000, "Large-cap IT services liquid name."),
    _entry("WIPRO", "IT", 2, "CSP", 20000, "Lower-beta IT optionality."),
    _entry("HCLTECH", "IT", 1, "CSP", 30000, "IT services quality name."),
    _entry("TECHM", "IT", 2, "CSP", 25000, "Telecom/enterprise IT beta."),
    _entry("LTIM", "IT", 2, "CSP", 35000, "Mid-tier IT services growth."),
    # Pharma
    _entry("SUNPHARMA", "Pharma", 1, "CSP", 30000, "Large-cap pharma leader."),
    _entry("DRREDDY", "Pharma", 1, "CSP", 35000, "Export pharma quality name."),
    _entry("CIPLA", "Pharma", 1, "CSP", 25000, "Defensive pharma exposure."),
    _entry("DIVISLAB", "Pharma", 1, "CSP", 35000, "High-quality API/export franchise."),
    _entry("AUROBINDO", "Pharma", 2, "CSP", 25000, "Higher-beta pharma value name."),
    # Infrastructure & Capital Goods
    _entry("LT", "Infrastructure & Capital Goods", 1, "CSP", 40000, "Core infra/capex proxy."),
    _entry("SIEMENS", "Infrastructure & Capital Goods", 1, "CSP", 45000, "Capex/electrification leader."),
    _entry("ABB", "Infrastructure & Capital Goods", 1, "CSP", 45000, "Automation and electrification."),
    _entry("CUMMINSIND", "Infrastructure & Capital Goods", 1, "CSP", 35000, "Power systems and industrial demand."),
    _entry("BHARATFORG", "Infrastructure & Capital Goods", 2, "CSP", 30000, "Forgings + defense/auto leverage."),
    # Auto
    _entry("MARUTI", "Auto", 1, "CSP", 50000, "Passenger vehicle leader."),
    _entry("TATAMOTORS", "Auto", 2, "CSP", 30000, "JLR + domestic auto beta."),
    _entry("M&M", "Auto", 1, "CSP", 35000, "SUV/tractor cycle leader."),
    _entry("BAJAJ-AUTO", "Auto", 1, "CSP", 45000, "Two-wheeler/export franchise."),
    _entry("EICHERMOT", "Auto", 1, "CSP", 40000, "Premium motorcycle franchise."),
    # Consumer
    _entry("HINDUNILVR", "Consumer", 1, "CSP", 30000, "Staples defensive anchor."),
    _entry("ITC", "Consumer", 1, "CSP", 20000, "Yield + staples stability."),
    _entry("NESTLEIND", "Consumer", 1, "CSP", 50000, "Premium staples quality."),
    _entry("BRITANNIA", "Consumer", 1, "CSP", 35000, "Staples quality with brand strength."),
]


US_UNIVERSE_BY_SYMBOL = {item["symbol"]: item for item in US_UNIVERSE}
INDIA_UNIVERSE_BY_SYMBOL = {item["symbol"]: item for item in INDIA_UNIVERSE}
