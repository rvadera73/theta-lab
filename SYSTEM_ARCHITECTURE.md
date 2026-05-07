# Theta-Lab System Architecture — Closed Loop

## Overview

The hedge fund operating system is a **closed-loop feedback mechanism** where:
1. **Persona** defines conviction framework and risk philosophy
2. **Reports** generate live thesis snapshots and action agendas
3. **Skills** execute based on latest thesis state
4. **Data** feeds back into next report cycle
5. **Framework** evolves when reports reveal contradictions

**Key principle:** Every report run updates thesis state. No document is static. Everything synchronizes.

---

## Architecture Layers

### Layer 1: Conviction Framework (Static, Reference)

**File:** `trading_persona.md` (in `~/.claude/skills/options-trader/`)

**Contains:**
- Tier classification (why AXON is Tier 1, RKLB is Tier 2, IONQ is Tier 3)
- Moat assessment philosophy (what makes moat STRONG vs MODERATE)
- Conviction scale definition (what does 7/10 mean?)
- Account strategies (Account A aggressive, B wheel, C conservative)
- Risk guardrails (max position sizes, margin limits, assignment caps)
- Permanent exit list (names never re-entered: MRNA, PYPL, SMCI, INMD)

**Updated when:**
- A position graduates between tiers (Tier 3 → Tier 2 when conviction ≥ 7)
- A moat assessment changes (competitive threat discovered)
- Conviction scale needs refinement (conviction 5 no longer means "neutral")

---

### Layer 2: Dynamic Universe (Runtime, Generated)

**File:** `screener_loader.py`

**Generates:**
- `TIER_1_NAMES`, `TIER_2_NAMES`, `TIER_3_NAMES` (extracted from trading_persona)
- `MOAT_STRENGTH` dict (moat assessments per ticker)
- `PERMANENT_EXITS` set (names never to re-enter)
- `get_current_holdings_universe()` → regime-filtered eligible candidates

**Logic:**
- BEAR regime: Tier 1+2 only, no Tier 3
- BULL regime: all tiers allowed
- All candidates filtered by: moat, thesis validity, permanent exit list

**Updated when:**
- Persona tiers change (recompile candidates)
- Moat assessment updates (recalculate alternatives)
- New permanent exits discovered (update PERMANENT_EXITS set)

---

### Layer 3: Thesis State (Live, Persistent)

**File:** `thesis_state_tracker.py`

**Maintains:**
- `logs/thesis_state_{YYYY-MM-DD}.json` — daily persistent state
- Each position tracks: `{current: latest_state, history: [timestamped_entries]}`
- Each state entry contains:
  - `status`: RED / YELLOW / GREEN
  - `conviction`: 1-10 score
  - `moat_strength`: STRONG / MODERATE / WEAK
  - `reason`: why this status (e.g., "weak moat + 2 guidance cuts")
  - `action`: recommended trade (CLOSE, ROLL, HOLD)
  - `alternatives`: top 3 redeploy candidates from screener
  - `guidance_cuts`: count of guidance misses
  - `earnings_beat`: last earnings result

**Updated when:**
- Any report runs (daily_trade_execution, enhanced_weekly, enhanced_monthly, position_detail)
- Each position's thesis is validated against screener rules
- Alternatives are re-scored based on current regime + moat + tier

**Key insight:** This file is the **action agenda**. Skills read from here. Reports write to here. All three reports (daily, weekly, monthly) append to the same file, so conviction trends accumulate over time.

---

### Layer 4: Reports (Output, Actionable)

#### 4a. Daily Trade Execution Report
**File:** `scripts/daily_trade_execution_report.py`

**Runs:** 6 AM ET each morning

**Generates:**
- Current Greeks status (delta, gamma, theta, vega)
- Greeks breaches (which guardrails are violated)
- Greeks targets (should be ±20 delta, ≤0.5 gamma, ≥$300 theta)
- Account-by-account breakdown (A, B, C, Traditional IRA, Roth IRA, Vanguard)
- **NEW:** Equity-level thesis validation
  - Shows sample positions (PYPL, ADBE, AXON, CRM) with thesis status
  - Conviction scores and moat assessment
  - Suggested alternatives for RED positions
- Suggested actions to fix breaches

**Integrates:** 
- Reads positions from all 6 accounts
- Calls `thesis_state_tracker.update_position_thesis()` for each position
- Displays thesis summary in "EQUITY-LEVEL THESIS VALIDATION" section
- All updates written to `logs/thesis_state_{YYYY-MM-DD}.json`

---

#### 4b. Enhanced Weekly Report
**File:** `scripts/enhanced_weekly_report.py`

**Runs:** Monday morning (via skill or manual trigger)

**Generates:**
- Portfolio Greeks health (delta/gamma/theta/risk targets)
- Position heat summary (RED/YELLOW/GREEN counts)
- **NEW:** Thesis validation summary
  - RED/YELLOW/GREEN status distribution
  - Average conviction across all positions
  - Tier distribution (Tier 1/2/3 counts)
  - List of RED positions (thesis broken) with conviction scores
- Top-5 weekly actions (prioritized by thesis status first, then Greeks)
- Heat protocol (which positions threatened, by account)
- Risk utilization and breaking point check
- Stress test scenarios

**Integrates:**
- Calls `thesis_state_tracker.update_position_thesis()` for each position
- Calls `thesis_tracker.get_thesis_summary()` for aggregates
- Top-5 actions reference thesis status (close RED thesis first, then fix Greeks)
- Suggests alternatives from screener for RED positions
- All updates written to `logs/thesis_state_{YYYY-MM-DD}.json`

---

#### 4c. Enhanced Monthly Report
**File:** `scripts/enhanced_monthly_report.py`

**Runs:** First day of month (via skill or manual trigger)

**Generates:**
- Monthly P&L summary (vs target)
- YTD progress (vs $1.2M annual target)
- Attribution analysis (where profit comes from: theta, vega, rolls, slippage)
- Account performance (Account A vs Account B vs target)
- Greeks trends (delta/gamma/theta/vega current state)
- **NEW:** Holdings universe alignment
  - Current portfolio vs screener-eligible universe (coverage %)
  - Tier distribution (actual Tier 1/2/3 vs available)
  - Positions outside universe (thesis broken, should be closed)
  - Tier 3 → Tier 2 graduation candidates (conviction ≥ 7)
- Next month strategy (what levers to pull)

**Integrates:**
- Calls `thesis_state_tracker.update_position_thesis()` for each position
- Loads `screener_loader.get_current_holdings_universe()` to compare
- Identifies misalignment: actual portfolio vs regime-filtered universe
- Flags tier graduation candidates
- All updates written to `logs/thesis_state_{YYYY-MM-DD}.json`

---

#### 4d. Position Detail Report
**File:** `scripts/position_detail_report.py`

**Runs:** On-demand (via `/research [symbol]` skill)

**Generates:**
- Account-level summary (positions, Greeks, heat)
- Priority actions (urgent = RED heat or RED thesis)
- This week (monitor these, prepare for rolls)
- Healthy positions (let decay, no action)
- Profit-take candidates (≥50% of max profit)
- **NEW:** Capacity for new entries
  - Shows which Tier 1/2 candidates are available (not in portfolio yet)
  - Suggests specific entry names based on regime + screener

**Integrates:**
- For each position, calls `thesis_state_tracker.update_position_thesis()`
- Adds thesis columns: status (RED/YELLOW/GREEN), conviction, moat, tier
- Shows alternatives for RED positions
- Entry suggestions pulled from screener universe
- All updates written to `logs/thesis_state_{YYYY-MM-DD}.json`

---

### Layer 5: Skills (Execution, Autonomous)

**Trigger:** User asks for report or takes trade action

**Execution flow:**
1. Skill loads latest report output OR request latest report to be generated
2. Skill reads `thesis_state_{YYYY-MM-DD}.json` (the action agenda)
3. Skill formats recommendations based on:
   - Thesis status (RED positions get priority)
   - Conviction scores (HIGH conviction = bigger position size)
   - Moat strength (WEAK moat = tighter stops)
   - Greeks (secondary to thesis)
4. Skill calls `dry_run_order()` to validate trade before execution
5. Skill displays recommendation to user with thesis rationale
6. User approves, skill executes via MCP broker tools

**Key:** Skills are data-driven, not emotional. They read the thesis snapshot (which is generated by reports) and execute accordingly.

---

## Closed-Loop Workflow

```
Monday 6 AM:
  1. Daily report runs → updates thesis_state for all positions
  2. Thursday night: Position X shows earnings miss → conviction drops to 3
  
Monday 8 AM:
  3. User reads daily report, sees "PYPL conviction 2/10, RED thesis"
  4. User asks "/research PYPL" 
  5. Position detail report runs → updates thesis_state again
  6. Report shows PYPL RED status + suggests alternatives (ALAB, RKLB, VST)
  
Monday 10 AM:
  7. User decides to close PYPL, asks "should I close PYPL?"
  8. Skill reads thesis_state.json → sees PYPL is RED with alternatives
  9. Skill formats: "Close PYPL (thesis broken, moat weak) → Redeploy to ALAB (Tier 2, conviction 7)"
  10. User approves → Skill executes close trade
  
Tuesday 6 AM:
  11. Daily report runs → PYPL no longer in positions, thesis_state reflects closure
  12. Portfolio thesis summary updates → RED count drops, avg conviction rises
  
Tuesday 5 PM:
  13. User reviews enhanced_weekly_report (generated Monday)
  14. Sees "PYPL closed, portfolio now 12 GREEN / 2 YELLOW / 0 RED"
  15. Conviction average improved from 5.2 to 5.7
  
Friday 5 PM:
  16. End of week: ALAB performs well, earnings beat
  17. ALAB conviction rises to 8 (from entry conviction of 6)
  18. Thesis marked GREEN, thesis tracking historical conviction score rises
  
Next Monday 6 AM:
  19. Monthly report will show: conviction trends (5.2 → 5.7 → 6.1 over 30 days)
  20. May show ALAB as "Tier 2 graduation candidate" (conviction 8, moat strong)
  21. Suggest promoting ALAB to Tier 1.5 in next persona update
```

---

## What Changes When Reports Reveal Contradictions

### Example 1: Tier Graduation
**Report finding:** "RKLB conviction has been 8+ for 3 months straight, moat is STRONG, should be Tier 1.5"

**Updates needed (same commit):**
- `trading_persona.md` → Move RKLB from TIER_2_NAMES to a new "TIER_1B_EMERGING" section
- `screener_loader.py` → Update TIER_1B_NAMES, TIER_2_NAMES sets
- Position size limits in guardrails → Allow 5 contracts for RKLB (vs 3 for Tier 2)
- Next report run → RKLB now treated as higher-tier name

### Example 2: Moat Deterioration
**Report finding:** "CRM conviction dropped to 3, moat assessed WEAK due to competitive pressure from Salesforce"

**Updates needed (same commit):**
- `screener_loader.py` → Update `MOAT_STRENGTH['CRM'] = 'WEAK'`
- `trading_persona.md` → Add note explaining why CRM moat weakened
- Add CRM to watch list for potential future permanent exit
- If conviction drops to 1 next month → move to PERMANENT_EXITS set

### Example 3: Greeks Target Revision
**Report finding:** "Portfolio delta consistently hits +22 even with disciplined risk management. ±20 target is too tight for current portfolio size."

**Updates needed (same commit):**
- `greeks_calculator.py` → Update guardrails from `delta_target = ±20` to `delta_target = ±25`
- `trading_persona.md` → Document why (portfolio size growth, market regime accommodation)
- All future reports use new ±25 target
- Weekly/monthly reports show "all targets met" instead of constant delta breach

---

## File Synchronization Rules

**Golden rule:** When a report finds something that contradicts a framework, update ALL affected files in one commit.

| Contradiction | Updates Needed | Files Affected |
|---------------|----------------|-----------------|
| Tier should change | Persona, screener_loader, guardrails, memory | 4 files |
| Moat assessment wrong | Screener, persona, alternatives logic | 3 files |
| Greeks target unrealistic | Persona, greeks_calculator, all reports | 4 files |
| Conviction scale off | Persona, all thesis validation calls | 2 files |
| Permanent exit triggered | Screener_loader, persona, memory | 3 files |

No half-done updates. Either commit touches zero files or all affected files.

---

## State Machine: Position Thesis Lifecycle

```
ENTRY (Conviction 5-6):
  → Initial thesis in screener universe
  → Position opened via put sale or stock purchase
  
THESIS INTACT (GREEN, Conviction 6-8):
  → Thesis validated by earnings beats
  → Moat confirmed
  → Hold, collect theta
  
THESIS AT RISK (YELLOW, Conviction 3-5):
  → Earnings miss OR guidance cut
  → Moat pressure from competitor
  → Monitor closely, prepare roll or exit
  
THESIS BROKEN (RED, Conviction 1-2):
  → 2+ consecutive guidance cuts
  → Moat fundamentally weakened
  → Close and redeploy to alternative
  
PERMANENT EXIT (Conviction 0):
  → Fundamental thesis destroyed
  → Company failure or acquisition
  → Added to PERMANENT_EXITS, never re-enter
```

---

## System Health Checklist

✅ **System is working if:**
- Reports run daily without errors
- Each report updates thesis_state file
- thesis_state file grows (new entries accumulate)
- Conviction trends visible over 30 days
- Alternatives always sourced from screener, never hardcoded
- When persona changes, all downstream files also update same commit
- Skills read thesis_state and reference it in recommendations
- User can trace "why am I closing this position?" back to conviction score + moat assessment

❌ **System is broken if:**
- Reports generate but thesis_state doesn't update
- Alternatives are hardcoded instead of screener-sourced
- Persona and screener_loader disagree on tier classification
- Reports reference old Greeks guardrails not in trading_persona
- Skill recommendations don't cite conviction or thesis status

---

## Integration Points

### For Skills (e.g., `/daily-execution`, `/weekly-actions`)
```python
# Load latest thesis state
tracker = ThesisStateTracker()
summary = tracker.get_thesis_summary()

# Get screener-based alternatives
universe = ScreenerLoader.get_current_holdings_universe(regime='BEAR_SIDEWAYS')
alternatives = ScreenerLoader.get_alternatives_for_position(symbol)

# Format recommendation with thesis rationale
if summary['status_distribution']['RED'] > 0:
    # Close RED thesis positions FIRST
else:
    # Then handle Greeks breaches
```

### For Framework Updates
When a report contradicts persona/screener:
```python
# 1. Update screener_loader.py (code)
MOAT_STRENGTH['CRM'] = 'WEAK'  # was 'STRONG'

# 2. Update trading_persona.md (documentation)
# Explain WHY: "CRM moat weakened due to..."

# 3. Update memory if needed (for future sessions)
# Save: "CRM graduation halted due to competitive pressure from Salesforce"

# 4. Commit all three together
git commit -m "Update CRM moat assessment (STRONG→WEAK) per latest report findings"
```

---

## Success Metrics

- **Conviction trends improve over month:** Starting avg 5.2 → ending avg 6.1+
- **RED count drops:** As thesis discipline improves, fewer broken theses
- **Greeks consistently in target range:** Because thesis-focused, not just Greeks-focused
- **Alternatives always available:** When closing position, screener always has 3+ qualified candidates
- **Commits are coherent:** Each update touches all affected files, nothing left stale

This is a **living system**, not a static tool. The loop feeds on itself: reports generate insights, frameworks evolve, next reports are better, conviction improves. That's the whole point.
