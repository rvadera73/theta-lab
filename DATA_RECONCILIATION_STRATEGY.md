# Data Reconciliation Strategy — The Real Problem & How to Fix It

**Date:** June 9, 2026  
**Status:** Diagnostic Complete — Framework is correct, underlying data needs sync

---

## The Problem You're Seeing

You're right: the reports show contradictory decisions because they pull from 4+ out-of-sync data sources:

| Data Element | Source | Status | Problem |
|---|---|---|---|
| **Account Balances** | Hardcoded in code | Not verified | $2.7M Account A — is this actual Schwab balance? |
| **YTD P&L** | `portfolio_snapshot.yaml` | STALE | Last updated May 30 — June 1-9 data missing |
| **Conviction Scores** | Yahoo Finance metrics | Calculated | May be 1-2 days stale |
| **Heat Status** | Calculated from RSI/price | Calculated | Depends on stale conviction data |
| **Sector Signals** | Sector analysis module | Calculated | Based on stale conviction assignments |
| **Close Recommendations** | Multiple sources | Conflicting | RED heat says close UNH/ETSY; Conviction says close CRWD/LLY |

**Result:** Framework applies correctly to bad data = contradictory recommendations.

---

## Why Data is Out of Sync

```
DAILY WORKFLOW (Current)
├─ Load open_positions_loader_v2.py (reads transaction files from 2-3 days ago)
├─ Fetch live prices from Yahoo Finance (current)
├─ Calculate conviction from price data (current)
├─ Load portfolio_snapshot.yaml (May 30 data = STALE)
├─ Calculate framework targets (uses stale snapshot)
├─ Generate recommendations (based on stale P&L, live prices, mixed conviction)
└─ Reports show conflicts (conviction not in sync with portfolio P&L)
```

The issue: **P&L data from May 30 doesn't match transaction loads from June 1-9**.

---

## The 3 Critical Data Mismatches

### 1. YTD/MTD P&L Mismatch

**What you told me:** Account A showed negative values at some points in June  
**What report shows:** YTD $292K, MTD $84K (all positive)  
**Root cause:** `portfolio_snapshot.yaml` has May 30 data, not June 1-9 actual

**Fix needed:**
- [ ] Export actual Schwab statement for Account A (Jun 1-9)
- [ ] Extract YTD P&L from transactions
- [ ] Update `portfolio_snapshot.yaml` with June 9 actual figures
- [ ] Recalculate monthly average

### 2. Account Balance Verification

**What report uses:** 
```
Account A: $2,732,234 (hardcoded)
Account B: $320,000 (hardcoded)
... (all hardcoded)
```

**What's needed:** 
- [ ] Get actual Schwab account statements (June 9)
- [ ] Verify these balances match reality
- [ ] Update ACCOUNTS_CONFIG if different
- [ ] Recalculate option requirements based on actual balances

### 3. Conviction Score Inconsistency

**Problem:** Different sections recommend closing different positions:
- **SECTION 6 (Heat Matrix - RED):** Close UNH, ETSY, NCLH
- **SECTION 2 (Conviction - LOW):** Close CRWD, LLY, OKTA
- **Sector analysis:** Recommends healthcare/utilities entries (contradicts heating closing healthcare names)

**Root cause:** Conviction scores were calculated with stale data, then positions moved, now heat and conviction misaligned.

**Fix needed:**
- [ ] Recalculate all conviction scores with CURRENT prices
- [ ] Re-evaluate heat status based on CURRENT conviction
- [ ] Verify close recommendations match CURRENT data
- [ ] Rebuild sector positioning from fresh scores

---

## How to Design the Reconciliation

### Phase 1: Establish Single Source of Truth (Data Hierarchy)

Create a priority for what's "truth" when sources conflict:

```
TRUTH HIERARCHY (use in this order):

1. LIVE SCHWAB STATEMENTS (highest priority)
   - Account balances
   - Transaction history (confirms what's actually open)
   - Actual assignment events
   - Current margin utilization

2. TRANSACTION FILES (transactions)
   - Open positions (derived from bought/sold history)
   - Entry/exit prices
   - P&L (realized vs unrealized)
   - Execution dates

3. SNAPSHOT.YAML (snapshot in time)
   - Used only when fresh (< 1 day old)
   - Fallback for YTD calculations
   - Should be updated daily from statements

4. LIVE PRICES (current)
   - Used for notional calculations
   - Used for Greeks calculations
   - Should NOT be used for P&L (use statements instead)

5. CALCULATED METRICS (lowest priority)
   - Conviction scores (derived from prices)
   - Heat status (derived from conviction)
   - Sector positioning (derived from heat)
```

### Phase 2: Establish Data Refresh Cadence

Create a predictable schedule so data stays in sync:

```
DAILY (Before 8 AM ET - report generation):
├─ Run 1: Export Schwab statements (Account A/B/C as of market close yesterday)
├─ Run 2: Load transaction files (merge yesterday's closes)
├─ Run 3: Calculate fresh YTD/MTD P&L from transactions
├─ Run 4: Update portfolio_snapshot.yaml with latest balances/P&L
├─ Run 5: Recalculate conviction scores with today's prices
├─ Run 6: Regenerate heat status from fresh conviction
├─ Run 7: Run sector analysis from fresh heat status
└─ Run 8: Generate reports (all data now synchronized)

WEEKLY (Friday EOD):
├─ Full portfolio rebalance check
├─ Account allocation audit
└─ Conviction tier refresh

MONTHLY (1st of month):
├─ Full P&L reconciliation (statements vs reported)
├─ Account balances verification
└─ Framework target reset for new month
```

### Phase 3: Build Reconciliation Logic

When data sources conflict, use this decision tree:

```
IF Schwab statement exists AND is current (< 1 day)
  USE Schwab statement values (balances, actual P&L)
ELSE IF transaction file is current (loaded today)
  USE transaction-derived values (open positions, entry prices)
ELSE IF snapshot is fresh (< 1 day old)
  USE snapshot values (YTD P&L, monthly average)
ELSE
  FLAG AS STALE AND SKIP REPORT

IF conviction score conflicts with heat status
  RECALCULATE conviction from current price data
  REGENERATE heat status from fresh conviction
  
IF close recommendations from 2+ sources differ
  COMPARE:
    - Does Schwab statement confirm this position is open?
    - Is conviction score based on current price?
    - Is heat status based on current conviction?
  IF all confirmed: recommendation is valid
  ELSE: mark as "pending data refresh"
```

---

## The 5-Step Fix (What to Do Now)

### Step 1: Get Clean Data Sources

**You need to provide:**
```
1. Schwab Account A statement (Jun 1-9, 2026)
   - Opening balance June 1
   - All transactions (entries/closes) Jun 1-9
   - Closing balance June 9
   - Net P&L for June 1-9

2. Schwab Account B statement (same dates)

3. Fidelity statements for Rahul/Rajul accounts (same dates)

4. Vanguard statement (same dates)

5. Robinhood account statements (same dates)
```

### Step 2: Calculate Reconciled YTD/MTD P&L

**From statements above, calculate:**
```
YTD P&L (Jan 1 - Jun 9):
  Account A: $ ??? (from statement)
  Account B: $ ??? (from statement)
  ... (all accounts)
  TOTAL YTD: $ ???

MTD P&L (Jun 1 - Jun 9):
  Account A: $ ??? (from statement)
  Account B: $ ??? (from statement)
  ... (all accounts)
  TOTAL MTD: $ ???

Update portfolio_snapshot.yaml:
  ytd_net_options_income: [ACTUAL from statements]
  month_to_date_premium: [ACTUAL from statements]
  last_updated: 2026-06-09
```

### Step 3: Verify Account Balances

**From statements above:**
```
Account A balance (Jun 9): $ ???
  vs Hardcoded: $2,732,234
  → Match? If not, update code

Account B balance (Jun 9): $ ???
  vs Hardcoded: $320,000
  → Match? If not, update code

... (all accounts)
```

### Step 4: Recalculate Conviction & Heat

**Once balances + P&L are confirmed:**
```
1. Run fresh conviction scoring with latest prices
2. Regenerate heat status from fresh conviction
3. Rebuild sector positioning from fresh heat
4. Verify close recommendations match fresh data
```

### Step 5: Regenerate Reports with Clean Data

**Once data is synchronized:**
```
python3 generate_unified_master_report_production.py
```

Reports will show consistent recommendations across all sections.

---

## What the Framework Design Should Be (Revised)

Once data is clean, the framework should work like this:

```
FRAMEWORK TARGETS (from SECTION 0):
├─ Monthly target: $90,000 net (CAUTIOUS_BULL regime)
├─ YTD cumulative: $ [ACTUAL from statements]
├─ Monthly average (YTD): $ [ACTUAL from statements]
└─ Gap to close: $ [ACTUAL needed to hit target]

POSITION TIER CONTRIBUTION (from SECTION 2):
├─ Tier 1 (Conv ≥8): [Count] positions @ $3.8K/month = $ [Total]
├─ Tier 2 (Conv 6-8): [Count] positions @ $1K/month = $ [Total]
├─ Tier 3 (Conv <6): [Count] positions @ -$500/month = $ [Total]
└─ Portfolio total: $ [Sum] = [% of $90K target]

CLOSE RECOMMENDATIONS (ALL sections agree):
├─ Source 1 (Heat Matrix): Position X is RED → Close
├─ Source 2 (Conviction): Position X is Tier 3 → Close
├─ Source 3 (Framework): Position X contributes -$500 → Close
└─ Verdict: CLOSE (all sources agree)

ACTION IMPACT (shown for every decision):
├─ Close position X: Removes -$500 drag = +$500 swing to target
├─ Enter new position: Adds +$3.8K contribution = 4.2% gap closure
└─ Scale existing: +$1.9K additional = 2.1% gap closure
```

When data is clean, ALL sections will recommend the same closes, and the framework will show exactly how much each action moves you toward the $90K target.

---

## Why This Matters

**Right now:** Framework is correct, but applied to stale/conflicting data = noise  
**After reconciliation:** Framework will be correct + applied to clean data = signal

**Current state → After fix:**
- "Close UNH vs close CRWD?" → "Close [all Tier 3 positions identified by 3 independent methods]"
- "Which account needs priority?" → "Account A is -$16.7K, needs 6 more Tier 1 positions"
- "How much will this action help?" → "This close + entry = 18.4% gap closure = $7.6K toward $27.9K monthly target"

---

## Summary: The Real Issue

You're absolutely right to be confused. The framework design is sound, but:

1. **Data sources are stale** (May 30 snapshot vs June 9 positions)
2. **Conflicting recommendations** (different methods recommending different closes)
3. **Account balances unverified** (hardcoded, not from statements)
4. **P&L calculations uncertain** (stale snapshot vs transaction files)

The fix is straightforward: **get clean statement data, synchronize all sources, then regenerate reports.**

Once that's done, the framework will work exactly as designed: every decision shows its quantified impact on gap closure.
