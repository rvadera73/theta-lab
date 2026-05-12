# Strategic Objectives & Principles Framework

## Annual Objectives (North Star)

### Primary Objective
**Generate $1.2M in annual premium income (theta decay)**
- YTD Target: $1.2M
- Current (May 2026): $341K
- Pace: $1.03M annualized (86% of target)
- Gap: Need $859K more (7 months remaining)
- Monthly rate needed: $122.7K/month to hit $1.2M

### Secondary Objectives
1. **Maintain risk-adjusted returns** (Sharpe ratio > 1.5)
2. **Preserve capital** (Max drawdown -20%, never exceed)
3. **Compound monthly** (Each month beats previous month)
4. **Build durable positioning** (Core Tier 1 holdings growing)

## Core Principles (Immutable)

### 1. Thesis-Driven Decisions
- **Principle**: Only hold positions where thesis is INTACT
- **Applied in Closed-Loop**: 
  - Daily: Conviction < 4 = thesis broken = prepare exit
  - Weekly: Conviction trending down = thesis weakening = flag
  - Monthly: Recalibrate if thesis deteriorated
- **Constraint**: If 30%+ of portfolio has broken thesis, STOP new entries

### 2. Risk-Aware Execution
- **Principle**: Greeks targets are hard floors, not suggestions
- **Delta target**: ±20 (never allow >±30)
- **Gamma target**: ≤0.5 (never allow >1.0)
- **Theta target**: ≥$300/day (never drop below $200)
- **Applied in Closed-Loop**:
  - Daily: Monitor Greeks vs targets
  - Weekly: If breached, rebalance immediately
  - Monthly: Review Greeks trend

### 3. Regime-Adaptive Strategy
- **Principle**: Portfolio composition changes with market regime
- **BEAR/SIDEWAYS** (current):
  - Only Tier 1/2 names (no Tier 3 speculation)
  - New entries: FROZEN until BULL regime
  - Profit target: 40% (take early wins)
  - Position sizing: Conservative (25% at risk)
- **BULL regime** (future):
  - All tiers allowed
  - New entries: ENABLED if conviction ≥6
  - Profit target: 70% (let winners run)
  - Position sizing: Aggressive (50% at risk)
- **Applied in Closed-Loop**:
  - Daily: Market regime check at top of report
  - Weekly: Regime signals (VIX, moving averages)
  - Monthly: Regime shift triggers portfolio restructure

### 4. Conviction-Based Sizing
- **Principle**: Position size = f(conviction, win_rate, available_capital)
- **Conviction 9-10**: Full Kelly size (~5% of portfolio)
- **Conviction 7-8**: 0.75x Kelly
- **Conviction 5-6**: 0.5x Kelly
- **Conviction <5**: Close position, redeploy
- **Applied in Closed-Loop**:
  - Daily: Calculate Kelly sizes for each position
  - Weekly: Reweight if conviction changes >1 point
  - Monthly: Rebuild portfolio based on conviction distribution

### 5. Disciplined Multi-Signal Exits
- **Principle**: Exit only when MULTIPLE signals align
- **Signal Types**:
  - Conviction drop <4 (thesis broken)
  - Heat RED (assignment imminent)
  - DTE <21 (gamma risk)
  - Profit target hit (regime-dependent)
  - Loss stop -20% (max loss)
- **Decision Logic**: Need 1+ Priority 1 signal OR 2+ Priority 2 signals
- **Applied in Closed-Loop**:
  - Daily: Scan for multi-signal exits
  - Weekly: Prepare exit list for following week
  - Monthly: Execute strategic exits

### 6. Quality-Biased Holdings
- **Principle**: Prefer STRONG moat over speculation
- **Moat Priority**: STRONG > MODERATE > WEAK
- **Tier Priority**: Tier 1 (core) > Tier 2 (building) > Tier 3 (spec)
- **Distribution Target**:
  - Tier 1: 60-70% of portfolio value
  - Tier 2: 20-30% of portfolio value
  - Tier 3: 0-10% of portfolio value (max 1 contract each)
- **Applied in Closed-Loop**:
  - Daily: Flag overconcentration in Tier 3
  - Weekly: Suggest Tier 1 additions if Tier 3 too high
  - Monthly: Enforce tier distribution targets

### 7. Account-Specific Rules
- **Account A (Margin, $2M+)**:
  - Margin max: 65%
  - Cash floor: $75K
  - Target: $150K/month theta income
  - Strategy: Short strangles (primary)

- **Account B (IRA, $400K+)**:
  - Margin max: 0% (IRA constraint)
  - Strategy: Wheel (CSP → CC)
  - Target: $75K/month theta income
  - Tier 3: Max 1 contract per name

- **Account C (Conservative IRA, $200K+)**:
  - Tier 1 only (no Tier 2/3)
  - Strategy: Covered calls on assigned shares
  - Target: $25K/month income

## Quarterly Review Checkpoints

### End of Q2 (June 30)
- [ ] YTD P&L: Target $600K (50% annual)
- [ ] Current: ~$450K (75% of Q2 target)
- [ ] Conviction avg: Should be ≥6.5/10
- [ ] Tier 1 concentration: Should be ≥60%
- [ ] Greeks: All in range
- **Decision Point**: On track? Adjust Q3 strategy accordingly

### End of Q3 (September 30)
- [ ] YTD P&L: Target $900K (75% annual)
- [ ] Conviction distribution stabilizing?
- [ ] Moat scores converging to reality?
- [ ] Risk budget: Still available for new entries?
- **Decision Point**: Pace check. Need to adjust monthly targets?

### End of Q4 (December 31)
- [ ] YTD P&L: Hit $1.2M target?
- [ ] Framework improved through closed-loop?
- [ ] Tier assignments accurate based on performance?
- [ ] What worked? What didn't? (Win rate analysis)
- **Decision Point**: Reset for next year with learned framework

## How Closed-Loop Serves Objectives

### Daily Report
**Objective Tie**: Hit monthly theta target
- Calculate conviction (ensures quality positions)
- Identify multi-signal exits (preserve capital)
- Flag Greeks breaches (risk management)
- Recommend closes/opens (hit targets)
- **Success Metric**: Daily theta income tracking toward monthly target

### Weekly Report
**Objective Tie**: Maintain thesis integrity + regime alignment
- Aggregate conviction trends (thesis health check)
- Suggest tier promotions/demotions (quality-biased)
- Calculate sector rotation (diversification)
- Identify new entry candidates (hit monthly targets)
- **Success Metric**: % of portfolio with conviction ≥6 (thesis intact)

### Monthly Report
**Objective Tie**: Progress toward annual $1.2M target
- Recalibrate moat scores (quality validation)
- Review monthly P&L vs target ($122.7K/month needed)
- Update tier distribution (stay quality-biased)
- Identify rebalancing needs (hit account targets)
- **Success Metric**: Monthly P&L ≥ $122.7K AND Tier 1 ≥ 60%

## Framework Constraints (Non-Negotiable)

### Hard Stops (System must refuse)
- ❌ Max loss per position >20% (forced close)
- ❌ Delta outside ±30 (forced rebalance)
- ❌ Gamma >1.0 (forced strangle close)
- ❌ Margin >70% in Account A (frozen new entries)
- ❌ Tier 3 >15% of portfolio (forced tier distribution)
- ❌ Open Tier 3 in BEAR regime (frozen until BULL)

### Yellow Alerts (System flags for review)
- ⚠️ Conviction <5 on any position
- ⚠️ Heat RED on any position
- ⚠️ Account B naked call risk
- ⚠️ YTD P&L below monthly pace
- ⚠️ Greeks trending toward breach
- ⚠️ Sector concentration >40%

## What Success Looks Like

### Day-Level
- [ ] Each position has conviction score
- [ ] Multi-trigger exits identified
- [ ] Daily theta income calculated
- [ ] Greeks in range

### Week-Level
- [ ] Conviction trends visible
- [ ] Tier assignments derived from data
- [ ] New entries proposed if capacity available
- [ ] Sector rotation calculated

### Month-Level
- [ ] P&L ≥ $122.7K
- [ ] Tier 1 positions ≥ 60% of portfolio value
- [ ] Moat scores recalibrated from performance
- [ ] Framework more accurate than previous month

### Annual-Level
- [ ] Hit $1.2M theta income target
- [ ] Max drawdown never exceeded -20%
- [ ] Avg conviction score ≥7/10
- [ ] Tier 1 concentration improved from start of year
- [ ] New framework (derived from data) better than old framework

## System Validation Rules

**The closed-loop is working if:**
1. ✅ Monthly P&L tracking toward $122.7K target
2. ✅ Conviction distribution improving (more 7+ scores)
3. ✅ Tier 1 concentration increasing (toward 70% target)
4. ✅ Moat scores converging to reality (less noise)
5. ✅ Greeks staying in range (risk managed)
6. ✅ No positions held beyond conviction threshold
7. ✅ Account-specific targets being met (A: $150K, B: $75K, C: $25K)

**Red flags if:**
1. ❌ Monthly P&L falling below $100K consistently
2. ❌ Conviction scores not updating (system broken)
3. ❌ Tier assignments not changing (not learning)
4. ❌ Greeks breaching repeatedly (risk not managed)
5. ❌ Low-conviction positions staying open >2 weeks
6. ❌ Account margin/cash constraints violated

## How Each Report Ensures Big Picture

### Daily Report
```
Header shows:
- Days into current month
- YTD P&L vs $1.2M target
- Monthly run rate (on pace?)
- Regime (strategy aligned?)

Body shows:
- Conviction distribution (thesis health)
- Greeks status (risk healthy?)
- Expected daily theta toward monthly target
- Multi-signal exits to preserve capital
```

### Weekly Report
```
Header shows:
- Week number in month
- YTD P&L vs $1.2M target
- Weekly theta income (tracking?)
- Account-specific targets

Body shows:
- Tier distribution vs targets (quality?)
- Sector concentration (diversified?)
- Conviction trends (thesis improving?)
- New entries to hit monthly targets
```

### Monthly Report
```
Header shows:
- Month name and number
- Monthly P&L vs $122.7K target
- YTD P&L vs $1.2M target (% complete)
- P&L by account (A/B/C)

Body shows:
- Tier distribution vs targets (60%+ Tier 1?)
- Moat score recalibration (learning?)
- Framework evolution (improving?)
- Strategic actions for next month
```

## Summary: Big Picture Alignment

**Objectives** (Strategic Goals)
- Hit $1.2M annual target ← Monthly reports validate progress
- Maintain risk within -20% max ← Daily reports enforce limits
- Build quality holdings ← Weekly reports validate tier distribution
- Compound month-over-month ← All reports track vs targets

**Principles** (How We Operate)
- Thesis-driven ← Conviction scores enforce this
- Risk-aware ← Greeks targets are hard constraints
- Regime-adaptive ← System changes with VIX/market
- Conviction-based ← Kelly sizing uses conviction
- Disciplined exits ← Multi-signal triggers
- Quality-biased ← Tier distribution targets
- Account-specific ← Account A/B/C constraints

**Closed-Loop** (How We Improve)
- Daily conviction updates → thesis health
- Weekly tier changes → quality validation
- Monthly moat recalibration → framework accuracy
- Each cycle: System gets smarter

---

**System Purpose:** Generate $1.2M annual premium income with disciplined risk management
**System Check:** Does closed-loop still serve this? ✅ YES (every report ties back to objectives)
