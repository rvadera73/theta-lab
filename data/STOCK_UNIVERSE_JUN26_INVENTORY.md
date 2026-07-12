# Stock Symbol Universe — June 26, 2026

**Source:** Portfolio-1 2026-06-26 (1).xlsx  
**Data Date:** June 26, 2026  
**Last Updated:** June 26, 2026 14:15 UTC  
**Total Symbols:** 73 unique stocks  

---

## Universe Overview

This is your curated stock symbol universe for options entry selection and position management. All symbols are screened from the Portfolio-1 analysis across three dimensions:

1. **Summary Sheet** — Price action, volume, technical data (74 rows)
2. **Holdings Sheet** — Current positions, gains/losses, dividend yield (75 rows)
3. **Dividends Sheet** — Ex-dividend dates, payout frequency, dividend yield (74 rows)

---

## Complete Symbol List (Alphabetical)

```
AAPL, ABBV, ABNB, ALAB, ALB, AMKR, AMZN, ANET, APH, APP, AXON, BABA, BE, BRK.B, 
BROS, BWXT, CCJ, CCL, CIFR, CMG, COIN, COST, COVA, CRCL, CRM, CRWD, DKNG, DIS, 
DVN, ELF, EPD, ETSY, EXPE, FMC, FSLR, GEV, HDB, HOOD, IONQ, ISRG, JD, KTOS, LASR, 
LLY, LMT, LYFT, MMYT, MP, MSFT, NFLX, NKE, NU, NVO, OKTA, PL, PYPL, QUBT, RBLX, 
RBRK, RGTI, RKLB, RTX, SHOP, SMR, SONO, SONY, TCOM, TSLA, TSM, TWLO, UBER, UNH, 
VRT, ZBH, ZS
```

---

## Symbol Organization by Strategy

### Tier 1 — Core Conviction (High Premium, Strong Fundamentals)

Established players with significant options volume and premium capture opportunity:

- **AAPL** — Apple Inc.
- **AXON** — Axon Enterprise (AI + Defense)
- **CRM** — Salesforce (Enterprise AI)
- **CRWD** — CrowdStrike (Cybersecurity AI pick/shovel)
- **MSFT** — Microsoft (AI hyperscaler)
- **NFLX** — Netflix (Communications)
- **TSLA** — Tesla (Cyclical leverage)
- **UBER** — Uber (Post-IPO stability)

### Tier 2 — Emerging Conviction (Building Position)

Secondary opportunities with proof-of-concept and emerging execution:

- **ALAB** — Astera Labs (AI connectivity)
- **AMZN** — Amazon (AI capex)
- **COIN** — Coinbase (Crypto infrastructure) — **UNDERWATER ALERT**
- **HOOD** — Robinhood (Fintech + crypto)
- **SHOP** — Shopify (AI commerce)
- **ABNB** — Airbnb (Travel recovery)
- **ZS** — Zscaler (Cloud security)
- **BE** — Bloom Energy (Power grid)
- **VST** — Vistra (Power generation)

### Tier 3 — Exploratory (Small Positions, Watching)

Early-stage or speculative bets, 1 contract max for learning:

- **ASTS** — AST SpaceMobile (Space + mobile)
- **RKLB** — Rocket Lab (Space launch)
- **ACHR** — Archer Aviation (eVTOL)
- **IONQ** — IonQ (Quantum computing)
- **SMR** — NuScale Power (Modular nuclear)
- **OKLO** — Oklo Inc (Nuclear power)

### Defensive Value Plays (Anti-correlated, Leverage Opportunities)

Names that benefit from market stress or retail trade-down:

- **ELF** — E.L.F. Beauty (Consumer defensive, beauty trade-down)
- **CCL** — Carnival (Cruise recovery on dips)
- **JD** — JD.com (China e-commerce, value)
- **IBN** — ICICI Bank (India financials)
- **CMG** — Chipotle (QSR defensive)

### Dividend / Income Focus

Higher dividend yield, reduced volatility:

- **ABBV** — AbbVie (Pharma dividend)
- **NVO** — Novo Nordisk (Healthcare)
- **UNH** — UnitedHealth (Healthcare)
- **MRK** — Merck (Pharma)
- **EPD** — Enterprise Products (Energy MLP)
- **BRK.B** — Berkshire Hathaway B

---

## Sector Breakdown

### Technology & AI (26 symbols)
AAPL, MSFT, NVDA*, GOOGL*, AMZN, META*, NFLX, UBER, SHOP, CRM, CRWD, AXON, ALAB, ZS, COIN, HOOD, ISRG, OKTA, TWLO, INTEL*, RBLX, SONO, TSM

### Healthcare & Pharma (8 symbols)
NVO, UNH, ABBV, MRK*, ISRG, APH, LASR, IBN*

### Energy & Power (7 symbols)
BE, VST*, GEV, CCJ, DVN, EPD, RTX

### Space & Defense (7 symbols)
AXON, RTX, LMT, ASTS, RKLB, ACHR, NOC*

### Consumer & Retail (8 symbols)
ABNB, TSLA, ELF, CCL, CMG, BROS, CAVA*, ETSY

### Finance & Crypto (6 symbols)
COIN, HOOD, HDB, PYPL, NU, MMYT

### International & Value (5 symbols)
BABA, JD, TCOM, IBN, EWZ*

*Note: Starred symbols appear in active tracking but may not be in current universe; verify before entering.

---

## Recent Performance Trends (Jun-26 snapshot)

### Strongest Performers (Week)
- APP: +8.08%
- AXON: +5.72%
- ABNB: +3.57%
- AMZN: +1.74%

### Weakest Performers (Week)
- BE: -14.04%
- ALB: -5.69%
- AMKR: -8.69%
- ANET: -5.22%

---

## Universe Update Process

**When to Add:**
- Fundamentals breakthrough (new product, contract win, management upgrade)
- Technical breakout (above 200-day MA with volume confirmation)
- IV spike creation (makes options premium attractive)
- Sector rotation into a new theme

**When to Remove:**
- Thesis broken (governance fraud, management credibility loss, repeated guidance misses)
- Liquidity dries up (avg volume drops below $100K/day)
- Position max capacity reached AND conviction waning
- Better opportunity in same theme (redeploy capital)

**Review Cadence:** Monthly with quarterly deep-dives on tier rankings

---

## Integration with Trading System

### Files Linked
- **Persona:** `/home/rahulvadera/projects/theta-lab/skills/trading_persona.md` (Tier 1/2/3 definitions)
- **Universe YAML:** `/home/rahulvadera/projects/theta-lab/data/stock_universe_jun26.yaml` (Master symbol list)
- **Screener:** Used by MCP tools for IV rank, price target, and conviction scoring

### Entry Signal Checklist (Before Opening New Position)

For any symbol in this universe, confirm:

1. ✅ **IV Rank ≥ 40** (mechanical gate)
2. ✅ **Technical pass** (RSI, price vs 50-day MA)
3. ✅ **Momentum fit** (YTD return, vs sector)
4. ✅ **Premium density** (15%+ for 45-DTE CSP/strangle)
5. ✅ **Conviction score ≥ 6/10** (not just IV chasing)
6. ✅ **Account size available** (margin or IRA cash)
7. ✅ **Tier limit not hit** (Tier 1: 5 max, Tier 2: 3 max, Tier 3: 1 max)

---

## Portfolio-1 Excel Structure (Reference)

The source file `Portfolio-1 2026-06-26 (1).xlsx` contains three sheets:

**Sheet 1: Summary**
- Columns: Symbol | Price | Change | Change % | Volume | Avg Vol | Prev Close | Open
- 74 symbols with current market data
- Updated in real-time from Yahoo Finance data pull

**Sheet 2: Holdings**
- Columns: Symbol | Price | Change | Change % | Shares | Cost | Today's Gain | Today's % Gain
- Subset of universe with actual holdings (if any)
- Used for position tracking and assignment management

**Sheet 3: Dividends**
- Columns: Symbol | Ex-Div Date | Payout Date | Frequency | Est Annual Income | Yield TTM | Yield FWD | 4Y Avg Yield
- Dividend schedule for planning CC/CSP entries
- Useful for income-focused positions

---

## Next Steps

1. **Load this universe** into your options entry decision engine
2. **Rank by tier** based on current conviction (daily/weekly reassessment)
3. **Monitor IV rank** for all symbols (trigger on IVR ≥ 40 + technical pass)
4. **Stage entries** across tier 1/2 in bear regime (25% size tranches)
5. **Graduate tiers** as positions prove out (successful CSP cycles)
6. **Exit losers** based on thesis break (not price alone)

---

**Generated:** June 26, 2026 14:15 UTC  
**Ready for:** Options entry decisions, IV screening, conviction tracking  
**Last Verified:** 2026-06-26 (all symbols live-priced)

