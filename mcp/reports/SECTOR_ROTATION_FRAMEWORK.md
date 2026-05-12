# Sector Rotation Framework

## Overview

The sector rotation framework analyzes holdings by Yahoo Finance sector classifications and evaluates sector-level conviction, valuation positioning, and heat distribution. This complements the existing individual position conviction scoring and heat classification by providing macro-level sector rotation guidance.

## Current Portfolio State (May 12, 2026)

### Sector Distribution by Conviction & Heat

| Sector | Positions | Avg Conv | Heat Status | Signal | Action |
|--------|-----------|----------|-------------|--------|--------|
| **Consumer Defensive** | 4 | 7.5/10 | 🟢 GREEN (4/4) | BUY | **Add exposure** |
| **Industrials** | 59 | 6.81/10 | Mixed (22G, 29Y, 8R) | MONITOR | Hold, monitor for higher conviction |
| **Financial Services** | 46 | 6.86/10 | Mostly 🟡 YELLOW (41Y, 5R) | MONITOR | Hold, wait for cleaner entry |
| **Technology** | 132 | 6.24/10 | Balanced (65G, 51Y, 16R) | MONITOR | Largest sector, stay diversified |
| **Utilities** | 10 | 6.55/10 | 🟡 YELLOW (10Y) | MONITOR | Hold, neutral |
| **Communication Services** | 35 | 6.49/10 | 🟢 GREEN dominant (22G, 11Y, 2R) | MONITOR | Hold, selective entry on dips |
| **Consumer Cyclical** | 76 | 6.15/10 | 🟢 GREEN dominant (35G, 40Y, 1R) | MONITOR | Hold, watch for weakness |
| **Healthcare** | 30 | 6.15/10 | 🔴 RED elevated (6G, 11Y, 13R) | CAUTION | Reduce overbought positions |
| **Basic Materials** | 27 | 5.72/10 | 🟢 GREEN heavy (22G, 5Y) | MONITOR | Hold, low conviction but attractive |
| **Energy** | 6 | 4.17/10 | Extended (2G, 4Y) | REDUCE | Exit or hold for mean reversion |
| **Unknown** | 13 | 6.23/10 | Mixed (5G, 8Y) | MONITOR | Classify and monitor |

### Key Signals

**🟢 BUY (1 sector)**
- **Consumer Defensive**: ELF and similar names at 52W lows, 7.5/10 conviction, RSI oversold (28.6)
  - Thesis: Value segment benefits from consumer trade-down in bear/sideways regimes
  - Action: Use CSP/wheel strategy to accumulate; IVR gate applies to NEW entries only

**🟡 MONITOR (9 sectors)**
- Portfolio is broadly neutral with mixed conviction across most sectors
- No sector has both HIGH conviction AND attractive valuation simultaneously
- Technology (132 pos, $3.4M) is largest but only 6.24/10 conviction — indicates some positions are stretched or thesis-challenged
- Industrials (59 pos) shows 6.81/10 conviction with 22 HIGH positions — core strength, hold
- Financial Services shows elevated YELLOW heat but no RED — approaching extremes, not yet extended

**🔴 CAUTION (1 sector)**
- **Healthcare**: RSI 59.9 approaching overbought (>70), 13 RED heat positions, 42.9% 52W range (mid-to-high)
  - Top overbought: LLY, MRK, UNH approaching or at highs
  - Action: Close/reduce profitable calls and call spreads; avoid new CSP entries

**🔴 REDUCE (1 sector)**
- **Energy**: 4.17/10 conviction (lowest), extended at 72.8% 52W range
  - Low thesis conviction + extended valuation = structural headwind
  - Action: Close or roll positions; do not add new

## Sector Rotation Framework Design

### Principle 1: Conviction + Valuation Alignment

A sector is actionable only when conviction AND valuation are aligned:

| Conviction | Valuation (52W %ile) | Action |
|-----------|-------------------|--------|
| **HIGH (8-10)** | Attractive (0-35%) | 🟢 **BUY** — Open new CSP/strangles; target max size |
| **HIGH (8-10)** | Neutral (35-65%) | 🟡 **HOLD** — Run to profit targets; don't add |
| **HIGH (8-10)** | Extended (65-100%) | 🟠 **REDUCE** — Close calls for profit; hold puts for theta |
| **MODERATE (6-8)** | Attractive (0-35%) | 🟡 **MONITOR** — Selective entries; smaller size |
| **MODERATE (6-8)** | Neutral (35-65%) | 🟡 **HOLD** — No action |
| **MODERATE (6-8)** | Extended (65-100%) | 🟡 **HOLD** — Do not add; reduce on strength |
| **LOW (<6)** | Attractive (0-35%) | 🟡 **MONITOR** — Fundamental thesis check required |
| **LOW (<6)** | Extended (65-100%) | 🔴 **REDUCE** — Exit thesis-challenged positions |

### Principle 2: RSI as Entry Gate (NEW entries only)

Use sector-level and individual position RSI to gate new CSP/strangle entries:

- **Sector RSI < 35**: Oversold — **STRONG gate for NEW entries** (high premium environment)
- **Sector RSI 35-65**: Neutral — **Standard IVR ≥ 40 gate applies**
- **Sector RSI > 70**: Overbought — **No new puts; CC exits only**

Individual position RSI overrides sector RSI if tighter (e.g., entry gate for specific name).

### Principle 3: Heat Distribution as Rebalance Signal

Track sector heat distribution to identify when rebalancing is needed:

| Heat Composition | Portfolio Stress | Action |
|-----------------|------------------|--------|
| Mostly 🟢 GREEN (>60%) | Attractive | Hold; selective adds on dips |
| Balanced 🟢🟡 (30-60% each) | Neutral | Hold; standard gamma/theta management |
| Elevated 🟡 YELLOW (>60%) | Approaching extremes | Monitor closely; reduce on bounce |
| Elevated 🔴 RED (>30%) | Stressed | Reduce or close RED positions; pause new entries |

**Current portfolio**: Heavily skewed toward 🟢 GREEN (227/438 = 52%) — attractive overall, but concentrated in Consumer Cyclical (46% GREEN).

### Principle 4: Sector Conviction Floor

Maintain sector-level conviction floors to prevent thesis decay:

| Regime | Min Sector Conviction | Action if < Floor |
|--------|--------------------|--------------------|
| **BULL** | 6.0/10 | Acceptable, hold |
| **CAUTIOUS_BULL** | 6.5/10 | Monitor, reduce low-conviction names |
| **BEAR_SIDEWAYS** | 7.0/10 | Exit or reduce sub-7.0 sectors |

**Current regime**: CAUTIOUS_BULL (VIX 18.4, healthy MAs)
- **Energy (4.17)**: BELOW floor — reduce
- **Basic Materials (5.72)**: BELOW floor — monitor, reduce if thesis weakens
- **Healthcare (6.15)**: BELOW floor — reduce extended positions

## Integration with Existing Systems

### Greeks-Based Option Requirement (No change)

Sector analysis informs *what to trade*, not *how much* to trade. Greeks calculations remain position-level and unchanged.

### Conviction Scoring (Position-Level, Enhanced)

Current: Individual position conviction from RSI, MACD, P/E, 52W range

Enhanced:
- Sector-level conviction now visible alongside position conviction
- Position with conviction 7.0 in a 5.5 sector = **idiosyncratic strength** (good)
- Position with conviction 5.5 in a 7.0 sector = **lagging** (watch for exit)
- Sector floor triggers review of outlier positions

### Heat Classification (Position-Level, Confirmed)

Current: Individual position heat (GREEN/YELLOW/RED) from RSI and 52W range

Enhanced:
- Sector heat distribution confirms portfolio stress level
- RED positions in YELLOW/RED sectors = higher priority close
- GREEN positions in GREEN sectors = higher theta collection confidence

### Market Regime (Macro Layer)

Regime determines:
1. **Entry conviction floor** (6.0 BULL → 7.0 BEAR)
2. **Sector size caps** (smaller in BEAR, larger in BULL)
3. **Sector rotation pace** (faster in CAUTIOUS_BULL, slower in BEAR)

## Weekly Sector Action Framework

**Every Monday (at weekly report generation):**

```
1. Calculate sector-level conviction (average across positions)
2. Calculate sector-level heat distribution (% GREEN/YELLOW/RED)
3. Calculate sector-level 52W range positioning (average)
4. Compare to previous week:
   - Conviction rising/falling? → Signal momentum
   - Heat distribution changing? → Portfolio stress level
   - Range position shifting? → Valuation thesis evolution
5. Identify action sectors:
   - BUY: Conviction ≥8, RSI <35, range <35%
   - REDUCE: Conviction <6, range >70% (or conviction 6-8, range >85%)
   - HOLD: Everything else
6. Present to trader: "Which sectors need attention?"
```

## Current Week Action Items (Week of May 12)

Based on May 12 sector analysis:

### Action 1: Consumer Defensive — Add Exposure
- **Signal**: 7.5/10 conviction, RSI 28.6 (OVERSOLD), 0.6% 52W range (LOWEST)
- **Thesis**: Value sector + oversold = high-probability entry
- **Implementation**: Add 1-2 CSP contracts on ELF and similar names if IVR ≥ 40
- **Size**: Standard per tier (1 contract Consumer Defensive per account)
- **Profit target**: 70% (oversold, higher premium expected)

### Action 2: Healthcare — Review Extended Positions
- **Signal**: RSI 59.9 (approaching 70), 13 RED positions, mostly YELLOW heat
- **Thesis**: Sector approaching overbought, not yet but risk/reward deteriorating
- **Implementation**: 
  - Close or reduce calls at 50%+ profit (LLY, UNH calls)
  - Avoid new PUT entries on Healthcare names until RSI <50
  - Monitor closely; if RSI crosses 70, escalate to more aggressive closes
- **Monitor names**: LLY 99.5K, UNH $394K, ISRG $43K positions

### Action 3: Energy — Exit or Hold for Recovery
- **Signal**: 4.17/10 conviction, extended at 72.8% 52W range, NO conviction
- **Thesis**: Low thesis confidence + extended valuation = exit setup
- **Implementation**:
  - XOM, CCJ positions: Close on any bounce or 40%+ profit
  - Do NOT open new CSPs on Energy until conviction improves to 6.0+ AND regime supports
- **Monitor**: Watch for energy-bullish catalyst (geopolitical, supply shock) that could change thesis

### Action 4: Technology Sector Diversification Check
- **Signal**: Largest sector (132 pos, $3.4M), but only 6.24/10 conviction
- **Issue**: 16 RED positions, some may be thesis-challenged (MU, ASML, NVDA positions)
- **Implementation**:
  - Check if RED heat is from valuation extension or fundamental deterioration
  - MU (4.5/10 conv, RED) is likely extended at $731 — review for potential close
  - Maintain diversification; don't let Tech become >40% notional
- **Watch**: ASML (5.5/10, YELLOW) is expensive; monitor for rotation opportunity

## Sector-Aware Trade Execution (CSP/Wheel/Strangles)

When considering a new entry:

1. **Check sector conviction**: Is it above regime floor?
2. **Check sector heat**: Are we adding to an extended sector?
3. **Check sector RSI**: Is the gate open (RSI <35 for oversold sectors)?
4. **Check individual position RSI**: Is this specific name oversold?
5. **Check conviction alignment**: Does individual conv match sector conv?

Example:
- **Considering**: COIN CSP (Financial Services sector)
- **Sector conv**: 6.86/10 ✓ (above 6.5 floor)
- **Sector heat**: 41/46 YELLOW, 5 RED (approaching extremes) ⚠️
- **Sector RSI**: 43.7 (neutral)
- **COIN individual**: 8.0/10 conv, YELLOW heat, RSI 51.5 ✓
- **Decision**: COIN is strong individual play, but sector is approaching extremes. Enter smaller size (1 contract) instead of 2. Use 0.20 delta instead of 0.15.

## Reporting Integration

### Daily Report
- Show sector conviction summary (top 3 buy, top 3 reduce)
- Highlight any sector floor violations

### Weekly Report
- Full sector breakdown with conviction, heat, range
- Action items for week (BUY/REDUCE/HOLD sectors)
- Sector rotation recommendation

### Monthly Report
- Sector trend analysis (conviction direction, heat evolution)
- Sector rotation performance (did we execute the framework?)
- Sector rebalancing recommendations for next month

## Success Metrics

Sector rotation framework is successful when:

1. **Conviction floors respected**: Sectors below regime floor are reduced
2. **Valuation awareness**: High-conviction adds happen in attractive valuation zones
3. **Early reduction**: Extended sectors with low conviction are exited before CRASH
4. **Premium capture**: Oversold sectors (RSI <35) entries capture 20-30% higher premiums
5. **Portfolio health**: Sector heat distribution stays mostly GREEN + YELLOW (no RED dominance)

## Framework Assumptions (To Revisit)

1. **Yahoo Finance sector classifications**: Assumed accurate and up-to-date. Quarterly audit recommended.
2. **Conviction floor calibration**: Currently 6.0 BULL, 6.5 CAUTIOUS_BULL, 7.0 BEAR. May need adjustment based on regime drift.
3. **Heat distribution weights**: Currently equal weight (RED = highest concern). May benefit from notional-weighting.
4. **Sector RSI gate**: Currently <35 for oversold entry. May need finetuning per sector (tech vs energy volatility differences).

---

## Files & Integration Points

- **Sector analysis generation**: `mcp/reports/sector_analysis.py`
- **Weekly sector data**: Generated in `logs/sector_analysis_YYYY-MM-DD.json`
- **Unified reports**: Sector analysis section integrated into daily/weekly reports
- **Trade execution**: Sector framework applied in `dry_run_order` before any new position
