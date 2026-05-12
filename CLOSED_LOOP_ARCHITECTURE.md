# Closed-Loop Self-Evolving Portfolio Framework

## Overview

This is a **self-correcting, continuous-evolution system** where:
- NO hardcoding of tier lists, moat scores, or holdings
- Everything derived from actual performance data
- Each report updates the framework
- Next report starts with improved framework
- System converges toward optimal portfolio allocation

**Big Picture Purpose:** Generate $1.2M annual premium income (theta decay) while maintaining risk discipline and thesis integrity

**See also:** `STRATEGIC_OBJECTIVES.md` for how this framework serves the annual goals and core principles

## Core Components

### 1. Hedge Fund Framework (`hedge_fund_framework.py`)

Industry-standard portfolio management frameworks:

**Conviction Scoring (1-10 scale)**
- Moat strength (0-4 points): STRONG=4, MODERATE=2, WEAK=0
- Earnings validation (±2 points): BEAT=+2, MISS=-2
- Momentum (±1 point): Price trend
- Heat status (±1 point): Distance to strike
- P&L status (±1 point): Winning/losing

**Multi-Factor Conviction = Foundation + Validation + Momentum + Heat + P&L**

**Kelly Criterion Position Sizing**
- Optimal bet size = f(win_rate, payoff_ratio, conviction)
- Prevents over-betting any single position
- Size scales with conviction (1-10)

**Multi-Trigger Exit Framework**
- Exit only when MULTIPLE signals align
- Signals: conviction drop (<4), heat RED, DTE <21, profit target, loss stop
- Prevents whipsaw exits on single bad day

**Sector Rotation**
- Dynamic sector weights by conviction
- High conviction sectors get more capital
- Low conviction sectors reduced exposure

### 2. Master Framework Engine (`master_framework_engine.py`)

Derives framework elements from actual performance:

**Holdings Universe (NO hardcoding)**
```
Conviction ≥7 + winning → TIER 1 (CORE)
Conviction 5-7 → TIER 2 (BUILDING)
Conviction <5 → TIER 3 (SPECULATIVE)
Conviction trending up → tier promotion candidate
Conviction trending down → tier demotion candidate
```

**Moat Strength (NO hardcoding)**
```
STRONG: Conviction ≥7 for 30 days + positive P&L + low variance
MODERATE: Conviction 5-7 with stable trend + neutral/positive P&L
WEAK: Declining conviction + negative P&L
```

**Tier Assignments (DERIVED, not static)**
- Load conviction history from thesis_state.json
- Calculate trend over last 30 days
- Assign tier based on conviction + trend
- Positions automatically promote/demote based on performance

### 3. Unified Master Report (`unified_master_report.py`)

Single report that orchestrates all three stages:

**AUTO-DETECTS STAGE:**
- Daily (weekdays): Conviction updates
- Weekly (Monday): Framework evolution
- Monthly (1st): Full recalibration

**RUNS ONCE, outputs all relevant sections**

## Continuous Loop Flow

```
DAY 1 (Any Weekday)
├─ Load current positions
├─ Calculate conviction using HF Framework
├─ Identify conviction changes
├─ Update thesis_state.json ✓
└─ Email: "Here's your daily conviction scores"
   
   ↓ (thesis_state.json has new conviction history)

WEEK 1 (Monday 8 AM)
├─ Load conviction history (7 days)
├─ Derive Holdings Universe from conviction trends
├─ Identify tier promotions/demotions
├─ Calculate sector rotation
├─ Update screener_loader.py with new tier assignments ✓
└─ Email: "Universe evolved, here's the changes"

   ↓ (screener_loader.py has updated tier assignments)

MONTH 1 (1st of month 8 AM)
├─ Load Master Framework Engine
├─ Recalibrate moat strengths from 30-day performance
├─ Identify new TIER 1 candidates (conviction ≥7)
├─ Flag TIER 3 candidates for exit (conviction <4)
├─ Update trading_persona.md ✓
└─ Email: "Monthly framework recalibration complete"

   ↓ (All framework files updated)

DAY 2 (Next day)
├─ System reads thesis_state.json (with yesterday's conviction history)
├─ System reads screener_loader.py (with updated tier assignments)
├─ System reads trading_persona.md (with updated moat scores)
├─ Framework is MORE ACCURATE than yesterday
├─ Cycle repeats with better data
└─ Conviction calculations are now informed by previous history
```

## What Gets Updated When

### Daily (6 AM ET) — Serving: Hit Monthly Theta Target + Preserve Capital
- `logs/thesis_state.json`
  - Conviction scores for each position (thesis health)
  - Conviction history (accumulates daily)
  - Status (GREEN/YELLOW/RED)
- **Objective Tie**: Ensures positions are thesis-driven (Principle #1)
- **Output**: "Here's your daily conviction. On pace for $122.7K/month target?"

### Weekly (Monday 8 AM ET) — Serving: Maintain Risk + Quality Distribution
- `scripts/screener_loader.py`
  - Tier assignments (1/2/3) updated based on conviction trends
  - Holdings universe derived from performance
  - Tier promotions/demotions applied
- **Objective Tie**: Ensures Tier 1 ≥60% (Principle #6, Quality-Biased)
- **Output**: "Conviction trends show thesis improvements. Tier distribution aligned?"

### Monthly (1st 8 AM ET) — Serving: Hit Annual $1.2M Target + Strategic Rebalance
- `mcp/trading_persona.md`
  - Moat strength scores updated (derived from 30-day performance)
  - TIER_1/2/3 lists updated (framework learns)
  - New universe derived from 30-day performance
- **Objective Tie**: Progress check toward $1.2M annual target
- **Output**: "Monthly P&L update: $XXX this month, $XXX YTD. On pace for annual target?"

## How Framework Evolution Works

### Example: Position AXON

**Day 1**
```
AXON: TIER 1 (hardcoded) → Conviction 9/10 (calculated)
Updates thesis_state.json with conviction=9, history=[9]
```

**Day 5**
```
AXON: Earnings MISS, P&L turns negative
Conviction drops to 6/10
thesis_state.json history=[9,8,7,6,6]
```

**Monday (Weekly Report)**
```
Load history: [9,8,7,6,6]
Trend: declining (-3 points over 5 days)
Recommendation: Monitor for TIER 2 demotion
Update screener_loader.py: Still TIER 1 but flagged
```

**Day 15**
```
Recovery, conviction back to 8
thesis_state.json history=[9,8,7,6,6,7,7,8]
Trend: +2 over last 3 days
Status: HOLDING
```

**Monthly**
```
Load all conviction history (30 days)
AXON: Average conviction 7.2, trend stable
Moat: STRONG (conviction stayed high, even with dip)
Result: TIER 1 confirmed, moat strength updated to STRONG
```

## No Hardcoding Principle

### ❌ OLD (Hardcoded)
```python
TIER_1_NAMES = {'AXON', 'CRM', 'ADBE', ...}  # Static list
MOAT_STRENGTH = {'AXON': 'STRONG', ...}      # Static scores
```

### ✅ NEW (Data-Driven)
```python
# Load from conviction history
tier_1 = [s for s, d in universe.items() if d['conviction'] >= 7]

# Derive from performance
moat = 'STRONG' if conviction_avg >= 7 and variance < 1.5 else 'MODERATE'
```

## Framework Files & Their Purpose

| File | Updated | Purpose |
|------|---------|---------|
| `thesis_state.json` | Daily | Conviction history, accumulates daily |
| `screener_loader.py` | Weekly | Tier assignments, moat scores (derived) |
| `trading_persona.md` | Monthly | Universe definition, tier lists (derived) |
| `logs/unified_master_report_*.txt` | Daily | Report showing all stages |

## Entry/Exit Gates (Framework Rules)

**ENTRY GATES (for new positions)**
- IVR ≥ 40 (volatility level)
- Conviction ≥ 6 (moat strength validation)
- Regime allows entries (BULL only, not BEAR)
- Risk budget available (Greeks targets)

**EXIT TRIGGERS (multi-signal)**
1. Conviction drops to <4 (thesis deteriorating)
2. Heat status = RED (assignment risk)
3. DTE < 21 (gamma risk)
4. Profit target hit (40-70% depending on regime)
5. Loss stop (-20% max)

Position doesn't exit on ONE signal. Only exits when multiple signals align or conviction drops to <4.

## Win Rate Optimization

System tracks what works:
```
Strategy: Short strangles
  Win rate: 72%
  Avg payoff: 2:1
  Kelly size: 5% of portfolio
  Conviction multiplier: 0.7x Kelly

Strategy: Covered calls
  Win rate: 85%
  Avg payoff: 1.5:1
  Kelly size: 7% of portfolio
  Conviction multiplier: 0.9x Kelly
```

Size positions larger for strategies with higher historical win rates.

## Sector Rotation Example

**Current Convictions by Sector:**
- AI Infrastructure: 8.2 (AXON, CRWD, TSM) → 35% weight
- Cybersecurity: 7.1 (CRWD, ZS) → 20% weight
- Space: 5.4 (RKLB, ASTS) → 15% weight
- Crypto: 3.8 (COIN, HOOD) → 10% weight
- Cash: - → 20% reserve

Next week: If Space conviction improves to 7, reweight to 25%.

## Testing & Validation

**Before first run:**
1. Check thesis_state.json loads correctly
2. Verify screener_loader tier assignments work
3. Test unified_master_report on sample data
4. Validate email delivery

**After first run:**
- Monitor daily conviction changes
- Weekly: Verify tier assignments make sense
- Monthly: Review moat recalibration

## Next Steps

1. ✓ Deploy unified_master_report.py
2. ✓ Update GitHub Actions workflows
3. Test with real data (positions + conviction history)
4. Monitor conviction trends over 2-4 weeks
5. Validate tier promotions/demotions
6. Confirm moat score evolution

System should start improving on week 2 as it has conviction history to work with.

---

**System Status:** ✅ Self-Evolving Closed-Loop Ready
**Framework Updates:** Daily → Weekly → Monthly → Next Cycle (Improved)
**Hardcoding:** ❌ NONE. Everything data-driven.
