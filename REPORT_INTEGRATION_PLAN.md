# Report Integration Plan: Position-Level Decisions + Risk Model + Regime Analysis

## Executive Summary

**Goal:** Add position-level decision framework, risk model tracking, and regime shift detection to existing reports WITHOUT removing current sections.

**Approach:** Enhance and merge new sections with existing structure across all 4 reports.

**New data inputs:** Yahoo Finance (VIX, S&P 50/200-MA), position-level P&L, DTE allocation, regime shifts.

---

## DAILY Report Integration

### Current Structure (7 sections + crash warning)
```
SECTION 0: Account health
SECTION 1: System status
SECTION 2: Conviction updates
SECTION 3: Position heat distribution
SECTION 4: Market regime & signals
SECTION 5: Position distribution by account
SECTION 6: Heat matrix & action
SECTION 6.5: Crash early warning
SECTION 7: Action framework
```

### New Sections to Add/Enhance

**ENHANCE SECTION 4: Market Regime & Signals**
- Add data-driven regime detection (from Yahoo Finance)
- Show: VIX level, S&P 50/200-MA position, IV Rank
- Show: Regime confidence % and shift probability
- **NEW:** If regime shifted from yesterday → Show "SHIFT DETECTED" with reason
  ```
  Example: "Regime shifted from BULL to TRANSITIONING on 2026-06-09
           Reason: VIX rose from 15.8 to 18.2 (>18 alert) + S&P 50-MA slope declining"
  ```

**ENHANCE SECTION 7: Action Framework — ADD P&L Impact**
- Keep: Close/Roll/Hold/Enter structure
- **ADD:** Expected P&L impact per decision
  ```
  Before:
  1️⃣  CLOSE NOW 🔴 (3 positions)
  
  After:
  1️⃣  CLOSE NOW 🔴 (3 positions) | Expected profit: $2,350
       └─ Margin freed: $92K | Redeploy capital available
  ```

**NO REMOVAL:** All existing sections stay as-is.

---

## WEEKLY Report Integration (PRIORITY - Most Changes)

### Current Structure (10 sections)
```
SECTION 0: Account health
SECTION 1: Market regime forecast
SECTION 2: Action priorities
SECTION 3: Top-5 action items
SECTION 4: Position heat by account
SECTION 5: IV Rank & entry gate
SECTION 6: Cash & margin forecast
SECTION 7: Theta & P&L tracking
SECTION 8: Risk guardrails
SECTION 9: Decision tree
SECTION 10: Framework status
```

### New Sections to Add/Enhance

**NEW SECTION 1A (After SECTION 1): Risk Model & Regime-Adjusted Targets**
```
Position: Between market regime forecast and action priorities
Content:
├─ Current market regime: TRANSITIONING (65% confidence)
├─ Shift probability: 35% to BEAR, 15% to BULL, 50% hold
├─ Risk tolerance (regime-adjusted):
│  ├─ Max margin utilization: 60% (BULL=75%, BEAR=40%)
│  ├─ Max position concentration: 4% (BULL=5%, BEAR=3%)
│  ├─ Position DTE preference: 30-60 days (balanced)
│  └─ Assignment tolerance: MEDIUM (close at 40%+)
├─ Monthly target (adjusted):
│  ├─ Base: $100,000
│  ├─ Regime adjustment: TRANSITIONING = -10%
│  ├─ Adjusted target: $90,000/month
│  └─ Weekly pace: $22,500
├─ Current pace: $4,633/day ($155K/month annualized)
└─ Status: 139% of target (UNSUSTAINABLE if regime shifts) ⚠️

**IF regime shifts to BEAR:**
├─ New target: $70,000/month (-22%)
├─ Risk adjustment: Max margin 40% (reduce by $1.2M in exposure)
├─ DTE shift: 50% long / 30% medium / 20% short
└─ Trigger: Automatic if 200-MA breaks or VIX > 25
```

**ENHANCE SECTION 2: Weekly Action Priorities — ADD Position-Level Decisions**
```
Replace current list with CATEGORIZED position decisions:

CLOSE NOW (3 positions) | Expected profit: $2,350 | Margin freed: $92K
├─ 1. LLY 06/18 1150C | P&L: +$1,200 | Driver: RSI 78.6 (overbought), 10 DTE
│     └─ Impact: Lock profit, free $59.5K margin for new entries
├─ 2. TWLO 06/18 200P | P&L: +$850 | Driver: Below alpha target (2.1%/day), ITM
│     └─ Impact: Redeploy $23K, reduce assignment risk
└─ 3. EWJ 06/18 92P | P&L: +$450 | Driver: ITM, conviction 4/10, short DTE

ROLL NOW (5 positions) | Expected credit: $1,850 | Extend thesis
├─ 1. AMZN 06/18 260C | P&L: +$680 | To: 07/16 $265C (+$200 credit)
│     └─ Reason: Thesis intact (conv 8/10), extend theta, avoid assignment
├─ [4 more rolls with P&L impact]
└─ Impact: Collect $1,850 net credit, extend DTE to medium band

HOLD (124 positions) | 52% of portfolio | No action needed
├─ Conviction: 6+/10 (adequate thesis support)
├─ Heat: YELLOW/GREEN (manageable risk)
├─ DTE: 31-60 days (sweet spot)
└─ Next check: At 21 DTE for rolls; weekly for conviction breaches

ENTER NEW (3-4 positions) | Expected premium: $2,690 | Capital: $85K
├─ 1. OKTA 45 DTE $115P | Premium: $890 | IVR: 100, Conv: 8/10
├─ 2. CRM 45 DTE $180P | Premium: $1,120 | IVR: 83.7, Conv: 9/10
└─ 3. RBLX 45 DTE $40P | Premium: $680 | IVR: 88.8, Conv: 7.2/10
     └─ Impact: Deploy $85K capital, maintain allocation targets
```

**ENHANCE SECTION 3: Top-5 Weekly Action Items — ADD P&L Detail**
```
Current: Just lists top 5 by conviction
New format:
#1 — LLY POSITION REVIEW | Action: CLOSE
     ├─ Conv 4.0, Heat RED, RSI 78.6
     ├─ Current P&L: +$1,200
     ├─ Days to exp: 10 (gamma risk increasing)
     └─ Expected outcome: Realize profit, avoid forced assignment

#2 — AMZN POSITION REVIEW | Action: ROLL
     ├─ Conv 8/10, Heat YELLOW, ITM
     ├─ Current P&L: +$680
     ├─ Roll to: 07/16 $265 (collect $200 credit)
     └─ Expected outcome: Extend thesis, avoid assignment
     
[3 more items with same detail]
```

**NEW SECTION 7A (After SECTION 7): DTE Allocation Analysis**
```
Position: After theta & P&L tracking, before risk guardrails
Content:
├─ Current portfolio DTE distribution:
│  ├─ Short DTE (0-30 days): 60 positions (25%) | Theta: $1,200/day
│  ├─ Medium DTE (30-60 days): 83 positions (35%) | Theta: $2,100/day
│  └─ Long DTE (60+ days): 95 positions (40%) | Theta: $1,333/day
│
├─ Regime-aligned target (TRANSITIONING):
│  ├─ Short DTE: 30% (currently 25%) → UNDERWEIGHT -5%
│  ├─ Medium DTE: 40% (currently 35%) → UNDERWEIGHT -5%
│  └─ Long DTE: 30% (currently 40%) → OVERWEIGHT +10%
│
├─ Rebalancing actions needed:
│  ├─ Close 10 long DTE positions (to reduce from 40% to 30%)
│  ├─ Enter 5 medium DTE positions (to increase from 35% to 40%)
│  └─ Timeline: Complete by end of week
│
└─ Impact if rebalanced:
   ├─ Theta generation: Still $3,500+/day (sufficient for $90K/month target)
   ├─ Assignment risk: Reduced (fewer long DTE)
   ├─ Flexibility: Improved (can respond to regime shifts faster)
   └─ Margin utilization: 55% (target 60%, healthier)
```

**ENHANCE SECTION 8: Risk & Guardrails — ADD Risk Model Status**
```
Current: Just Greek guardrails (Delta, Gamma, Theta, Vega)
New section:

GREEKS PORTFOLIO LEVEL (existing):
├─ Delta: +16 (target ±25) ✅
├─ Gamma: 0.39 (target ≤1.0) ✅
├─ Theta: $385/day (target ≥$300) ✅
└─ Vega: $240 (IV sensitivity) ✅

**RISK MODEL PERFORMANCE (NEW):**
├─ Margin utilization: 56% (target 60% for TRANSITIONING) ✅
├─ Max concentration: Largest 3.2% (target 4%) ✅ WITHIN LIMITS
├─ Conviction filter: 95% of held positions 6+/10 ✅
├─ DTE allocation: 25/35/40 vs target 30/40/30 ⚠️ REBALANCE
├─ Assignment rate: 2% (historical avg 5%) ✅ GOOD
└─ Overall status: HEALTHY — adjustments ongoing
```

**NO REMOVAL:** All existing sections (0-10) stay intact.

---

## BIWEEKLY Report Integration

### Current Structure (7 sections)
```
SECTION 0: Account health
SECTION 1: YTD pace & monthly target
SECTION 2: 3-month conviction trend
SECTION 3: 3-month tier distribution
SECTION 4: 3-month win rate
SECTION 5: 3-month Greeks drift
SECTION 6: 3-month sector rotation
SECTION 7: Monthly variance pattern
```

### New Sections to Add/Enhance

**ENHANCE SECTION 1: YTD Pace & Monthly Target — ADD Regime Adjustments**
```
Current: Just shows YTD vs annual target
New section:

YTD PERFORMANCE:
├─ YTD net premium: $292,421
├─ Annual pace: $1.76M (at current rate)
├─ Annual target: $1.2M
└─ Status: 147% of target ✅ OVERPERFORMING

**MONTHLY TARGET TRACKING (REGIME-ADJUSTED):**
├─ May 2026 target: $100,000 (BULL regime)
├─ May 2026 actual: $139,000 ✅ +39% (BULL pushed higher)
│
├─ June 2026 target: $90,000 (TRANSITIONING regime)
│  ├─ Adjustment: -10% (lower certainty, more risk)
│  ├─ Rationale: VIX rising, regime shift probability 35%
│  └─ YTD pace on new target: 123% (still ahead)
│
├─ Current month pace (through Jun 8): $47,300
├─ Weekly pace needed: $22,500 (to hit adjusted $90K)
└─ Status: ON TRACK ✅ (ahead of adjusted target)

**IF REGIME SHIFTS:**
├─ To BEAR: New target would be $70,000 (-22%)
├─ To BULL: New target would be $95,000 (-5%)
└─ Monitoring: Weekly regime updates to adjust targets
```

**NEW SECTION 3A (After SECTION 2): Actions Execution Summary**
```
Position: Between conviction trend and tier distribution
Content:
├─ Weekly actions taken (from WEEKLY reports, weeks 1-2):
│  ├─ Positions closed: 16 | Profit locked: $12,400 | Margin freed: $360K
│  ├─ Positions rolled: 12 | Credit collected: $3,700 | Extended DTE
│  ├─ New positions: 6 | Premium collected: $5,380 | Capital deployed: $170K
│  └─ Held: 248 positions maintained (no conviction drop)
│
├─ Decision quality:
│  ├─ Close recommendations executed: 16/16 (100%) ✅
│  ├─ Roll recommendations executed: 12/12 (100%) ✅
│  ├─ Hold recommendations maintained: 248/248 (100%) ✅
│  └─ Overall compliance: 100% (framework followed precisely)
│
└─ Framework alignment:
   ├─ All closed positions were below conviction 6/10 or short DTE risk ✅
   ├─ All rolled positions had conviction 7+/10 and manageable risk ✅
   ├─ All new entries met IVR ≥40 and conv 7+/10 gates ✅
   └─ Assessment: DECISION FRAMEWORK PERFORMING WELL
```

**ENHANCE SECTION 5: 3-Month Greeks Drift — MERGE with DTE Analysis**
```
Current: Just Greek metrics over 3 months
Enhanced section:

GREEKS 3-MONTH DRIFT:
├─ Delta drift: +2 (stable, no directional bias increase)
├─ Gamma drift: -0.08 (declining, good as we close short DTE)
├─ Theta drift: +$50/day (increasing, more positions at peak decay)
└─ Assessment: Greeks well-managed, no structural issues

**DTE 3-MONTH EVOLUTION:**
├─ May (BULL): 20% short / 35% medium / 45% long (aggressive)
├─ Jun week 1 (BULL): 25% short / 35% medium / 40% long (rebalancing)
├─ Jun week 2 (TRANSITIONING): 28% short / 42% medium / 30% long (balanced)
│
├─ Trend: Successfully rebalanced from aggressive (BULL) to balanced (TRANSITIONING)
├─ Timing: Shifted allocation BEFORE regime shifted (proactive) ✅
└─ Next: If regime shifts to BEAR, will shift to 20% short / 30% medium / 50% long

**INTEGRATED ASSESSMENT:**
├─ Greeks remain in healthy range despite DTE rebalancing ✅
├─ Portfolio becomes more defensive as regime shifts ✅
├─ Theta generation stays >$3,000/day regardless of allocation ✅
└─ Risk model supporting both regime and Greeks management ✅
```

**NO REMOVAL:** All existing sections (0-7) stay intact.

---

## MONTHLY Report Integration (FRAMEWORK ANALYSIS)

### Current Structure (5 sections)
```
SECTION 0: Account health
SECTION 1: Monthly actual vs target
SECTION 2: Performance by account
SECTION 3: Variance root cause
SECTION 4: Moat recalibration
SECTION 5: Citadel comparison
```

### New Sections to Add/Enhance

**ENHANCE SECTION 1: Monthly Actual vs Target — ADD Risk Model Analysis**
```
Current: Shows actual vs target variance
Enhanced section:

MONTHLY ACTUAL VS TARGET:
├─ Target: $90,000 (TRANSITIONING regime-adjusted)
├─ Actual: $47,300 (through Jun 8, 3 days in)
├─ Pace: $94,600/month ✅ ON TARGET
└─ Confidence: High (not dependent on regime shift yet)

**RISK MODEL PERFORMANCE:**
├─ Margin utilization: 56% (target 60%) ✅
├─ Assignment rate: 2% (sustainable) ✅
├─ Conviction filter compliance: 95% of held positions 6+/10 ✅
├─ DTE allocation: Rebalancing on track (25/35/40 → 30/40/30 by month-end)
├─ Monthly targets adjusted: 0 times (regime held steady)
└─ Framework assessment: RISK MODEL SUPPORTING TARGET ✅

**VARIANCE ANALYSIS vs PREVIOUS MONTH (MAY):**
├─ May target: $100,000 (BULL regime) | Actual: $139,000 | +39%
├─ June target: $90,000 (TRANSITIONING) | Actual YTD pace: $94,600 | +5%
├─ Analysis:
│  ├─ May outperformance: BULL regime = easier market, more assignments
│  ├─ June pace: Still strong despite more cautious regime
│  └─ Conclusion: Risk model working; adjusted targets realistic
└─ Next month outlook: If BEAR, expect $70K target (more challenging)
```

**NEW SECTION 2A: Regime Shift Summary & Analysis**
```
Position: After section 1, before performance by account
Content:

REGIME SHIFTS THIS MONTH:
├─ Regime on Jun 1: BULL (63% confidence)
├─ Regime on Jun 8: TRANSITIONING (65% confidence)
├─ Shift date: Jun 5-6, 2026
└─ Status: SHIFT DETECTED AND REPORTED ✅

**WHY DID REGIME SHIFT? (Data-driven analysis)**
├─ Signal 1: VIX increased
│  ├─ May 31: 15.8
│  ├─ Jun 8: 18.2 (+2.4)
│  └─ Assessment: Rising VIX = declining confidence (BULL → TRANSITIONING)
│
├─ Signal 2: S&P 50-MA slope changed
│  ├─ May 31: +522 (rising steeply = BULL)
│  ├─ Jun 8: +260 (slope declining = weakening momentum)
│  └─ Assessment: Momentum deteriorating
│
├─ Signal 3: S&P 200-MA still positive
│  ├─ May 31: +749 (above long-term support)
│  ├─ Jun 8: +572 (still positive, but weakening)
│  └─ Assessment: Long-term support intact, but near-term uncertain
│
├─ Signal 4: Market breadth declining (estimated from position data)
│  ├─ Winners: 45% of holdings
│  ├─ Losers: 55% of holdings
│  └─ Assessment: Breadth deteriorating (BULL→TRANSITIONING)
│
└─ CONCLUSION: Regime shift JUSTIFIED by data. Not noise; real change.

**ACTIONS TAKEN IN RESPONSE:**
├─ Adjusted June target: $100K → $90K (-10%)
├─ Risk tolerance: 75% margin → 60% margin
├─ DTE preference: 20/35/45 → 30/40/30
├─ New entry gate: Kept IVR ≥40 (no change, still selective)
├─ Monitoring: Increased daily (now watching for BEAR shift)
└─ Contingency: If 200-MA breaks <6,831 → immediate shift to BEAR

**WHAT IF IT SHIFTS AGAIN?**
├─ Back to BULL: Increase target $90K → $95K, adjust margin to 65%, rebalance DTE
├─ Forward to BEAR: Decrease target $90K → $70K, reduce margin to 40%, shift to defensive
├─ Probability (based on signals):
│  ├─ Stay TRANSITIONING: 50% (most likely)
│  ├─ Shift to BEAR: 35% (watch for 200-MA break)
│  └─ Shift to BULL: 15% (need VIX <14 + breadth >55% winners)
└─ Monitoring: Daily VIX and S&P 50-MA updates
```

**NEW SECTION 4A: Framework Support & Decision Quality Analysis**
```
Position: After regime shift summary
Content:

DID WEEKLY DECISIONS SUPPORT MONTHLY TARGETS?

1. CLOSE DECISIONS: Were they profitable?
   ├─ Closed positions: 16
   ├─ Avg profit per close: +$775 (total $12,400)
   ├─ Avoided assignments: Yes (2 positions would have been assigned at loss)
   ├─ Capital redeployed: $360K → new medium DTE positions
   └─ Assessment: CLOSE DECISIONS WORKING ✅

2. ROLL DECISIONS: Did they extend thesis correctly?
   ├─ Rolled positions: 12
   ├─ Avg credit collected: +$308 per roll
   ├─ Positions still in thesis: 12/12 (100% conviction maintained)
   ├─ DTE extension: Average 19 days (appropriate for TRANSITIONING)
   └─ Assessment: ROLL DECISIONS WORKING ✅

3. HOLD DECISIONS: Were conviction filters effective?
   ├─ Held positions: 248
   ├─ Conviction below 5 breaches: 0 (filters working)
   ├─ Unwanted assignments: 2 (acceptable, <1%)
   ├─ Heat RED count: 13 (manageable, 5% of portfolio)
   └─ Assessment: HOLD DECISIONS EFFECTIVE ✅

4. ENTRY DECISIONS: Were new positions positioned correctly?
   ├─ New entries: 6
   ├─ All met IVR ≥40 gate: Yes (premium levels appropriate)
   ├─ All met conviction ≥7: Yes (thesis support strong)
   ├─ DTE (45-60 days): Aligned with TRANSITIONING preference
   └─ Assessment: ENTRY DECISIONS ALIGNED ✅

**OVERALL FRAMEWORK ASSESSMENT:**
├─ Decisions matched market regime: YES (rebalanced before TRANSITIONING)
├─ Decisions supported target: YES (on pace for adjusted $90K)
├─ Risk model kept us safe: YES (margin 56% vs 60% limit)
├─ Framework adjustments timely: YES (caught regime shift early)
└─ Confidence in framework: HIGH ✅
```

**NEW SECTION 5A: Next Month Contingencies & Adjustments**
```
Position: End of monthly report
Content:

SCENARIO PLANNING FOR JULY 2026:

**SCENARIO A: Regime stays TRANSITIONING (50% probability)**
├─ July target: $90,000/month (no change)
├─ DTE target: 30/40/30 (no change)
├─ Margin limit: 60% (no change)
├─ Actions: Continue current framework
├─ Exit condition: If 200-MA drops below 6,831 OR VIX spikes >25
└─ Expected outcome: $2,800-3,500/day theta generation

**SCENARIO B: Regime shifts to BEAR (35% probability)**
├─ Shift trigger: 200-MA < 6,831 OR VIX > 25 OR breadth <40%
├─ July target: $70,000/month (-22% from current)
├─ DTE adjustment: 50% long / 30% medium / 20% short (defensive)
├─ Margin limit: 40% (reduce positions by $2.5M notional)
├─ Actions: 
│  ├─ Close short DTE positions at profit (don't wait for assignment)
│  ├─ Roll medium DTE to long DTE (extend safety)
│  ├─ Reduce new entries (only IVR ≥60)
│  └─ Increase cash reserve to 25%
├─ Expected outcome: $2,200-2,500/day theta (sustainable in bear market)
└─ Recovery: When regime shifts back to BULL, scale back aggressively

**SCENARIO C: Regime shifts to BULL (15% probability)**
├─ Shift trigger: VIX <14 AND breadth >55% winners AND 50-MA accelerating
├─ July target: $95,000/month (+5% from current)
├─ DTE adjustment: 20% long / 35% medium / 45% short (aggressive)
├─ Margin limit: 70% (increase position sizes by $1.2M)
├─ Actions:
│  ├─ Increase new entry sizes (5-6 positions/week)
│  ├─ Reduce long DTE positions (let short DTE compound)
│  └─ Lower IVR gate to ≥35 (more entries available)
└─ Expected outcome: $3,500-4,500/day theta (higher pace)

**MONITORING CHECKLIST FOR JULY:**
├─ Daily: VIX level (alert if >25)
├─ Daily: S&P 50-MA slope (alert if flattening)
├─ Weekly: Breadth analysis (% winners vs losers)
├─ Weekly: 200-MA position vs price (alert if approaching break)
├─ Biweekly: Position-level conviction (close if <5)
├─ Monthly: Regime re-assessment (repeat this analysis)
└─ Escalation: If 2+ signals point to shift, adjust immediately (don't wait for full regime change)

**CONTINGENCY CAPITAL (ALWAYS RESERVED):**
├─ Emergency fund: $200K (never deployed, for crash only)
├─ Cash reserve: 15% of portfolio ($680K in TRANSITIONING, scale to 25% in BEAR)
├─ Redeploy capital: From closes ($12K/week expected)
└─ Margin buffer: Always maintain 20% below limit (current 56% vs 60% limit) ✅
```

**NO REMOVAL:** All existing sections (0-5) stay intact.

---

## Summary: What Changes Where

| Report | Keep All | Enhance | Add New |
|--------|----------|---------|---------|
| **DAILY** | ✅ Sections 0-7 | ✅ Section 4 (regime data), Section 7 (P&L) | None |
| **WEEKLY** | ✅ Sections 0-10 | ✅ Sections 1,2,3,8 | ✅ Section 1A (risk model), Section 7A (DTE analysis) |
| **BIWEEKLY** | ✅ Sections 0-7 | ✅ Section 1 (regime adjustments), Section 5 (Greeks+DTE) | ✅ Section 3A (actions summary) |
| **MONTHLY** | ✅ Sections 0-5 | ✅ Section 1 (risk model) | ✅ Section 2A (regime shift), Section 4A (framework support), Section 5A (contingencies) |

---

## Data Sources (Yahoo Finance)

**All from Yahoo Finance (yfinance library):**
- VIX level → `yfinance.Ticker("^VIX").history()`
- S&P 500 price → `yfinance.Ticker("^GSPC").history()`
- Calculate 50-MA and 200-MA from daily closes
- IV Rank → Already calculated from option chains

**Regime Detection Logic (Data-driven, NOT hardcoded):**
```
if VIX < 15 and SPX_50MA_above_200MA and breadth > 55%:
    regime = "BULL"
elif VIX > 25 or SPX_50MA_below_200MA or breadth < 40%:
    regime = "BEAR"
else:
    regime = "TRANSITIONING"

regime_confidence = calculate_signal_strength()  # 0-100%
shift_probability = calculate_directional_risk()  # % chance of next regime
```

**Regime Shift Detection:**
- Compare regime from yesterday to today
- If shifted: Capture WHY it shifted (which signals changed)
- Report: "Shifted from X to Y on [date] due to: [signals]"

---

## Next Steps for Implementation

1. **Update unified_master_report.py to:**
   - Pull VIX and S&P data from Yahoo Finance daily
   - Implement data-driven regime detection (not hardcoded)
   - Calculate regime confidence and shift probability
   - Track regime changes day-to-day

2. **Add position-level P&L tracking:**
   - Entry price per position
   - Current market value per position
   - Unrealized P&L and % of max premium
   - Expected P&L if action taken

3. **Implement DTE allocation calculator:**
   - Segment portfolio by DTE bands
   - Compare to regime-adjusted targets
   - Suggest rebalancing actions

4. **Create regime shift alerting:**
   - Detect shift from previous day
   - Capture signals that triggered shift
   - Report in DAILY and WEEKLY

5. **Implement contingency planning:**
   - 3 scenario models (BULL, BEAR, TRANSITIONING)
   - Adjusted targets for each scenario
   - Trigger conditions clearly defined

---

## Questions Before Implementation

1. **Do you want position-level decisions in WEEKLY only?** Or also in DAILY with fewer details?

2. **P&L impact calculation:** Should we show:
   - Just "Expected profit if closed today"?
   - Or also "Additional profit if held 5 more days"?

3. **Regime shift trigger levels:** Should we set:
   - VIX alert threshold: 25? (or lower, like 22?)
   - 200-MA break: Exact price? (currently 6,831)
   - Breadth threshold: 40%? (or 45%?)

4. **Do you want automatic regime shifts to adjust targets immediately?** Or report shift but keep current target until you confirm?

5. **Monthly contingency detail:** Too much? Or should we add scenario trees (if X then Y then Z)?

