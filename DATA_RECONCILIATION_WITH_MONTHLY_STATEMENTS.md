# Data Reconciliation Using Monthly Statements (May 31)

**Constraint:** Monthly statements only (May 31), not intra-month  
**What we have:** Transaction files with May 2-31 data in positions folder  
**What we need:** Reconcile reports to May 31 actuals (which are the most recent clean data)

---

## The Real Problem (Revised)

The issue isn't that we need daily statements. The issue is:

```
CURRENT STATE:
├─ portfolio_snapshot.yaml → May 30 data (outdated)
├─ Transaction files → May 2-31 data (actual closed trades)
├─ Open positions loader → May 31+ data (current positions)
└─ Framework targets → Calculated from May 30 snapshot (should use May 31)

RESULT: Using May 30 to calculate framework while positions are May 31+
        Creates 1-day lag that cascades into bigger mismatches
```

**Solution:** Use May 31 as the authoritative baseline (most recent month-end we have)

---

## Step 1: Calculate Actual May 31 Balances & P&L

**From transaction files you have (May 2-31):**

```
Extract from Schwab transaction files:
  Account A (232) May 2-31:
    ├─ All option closes (realized P&L)
    ├─ All option entries (capital deployed)
    ├─ Sum of realized P&L = $ ???
    └─ Opening balance May 1 + Realized P&L = Estimated May 31 balance

Account B (275) May 2-31:
    ├─ All option closes (realized P&L)
    ├─ All entries
    └─ Same calculation

... (all other accounts)
```

**Then verify against May 31 statements:**
```
What you'll provide from statements (May 31):
  Account A closing balance: $ ??? (from statement)
  Account B closing balance: $ ??? (from statement)
  Fidelity balances: $ ???
  Vanguard balances: $ ???
  Robinhood balances: $ ???
```

**Reconciliation:**
```
IF Calculated May 31 balance = Statement May 31 balance
  → All transaction data is accurate
  → Use these as baseline for framework

ELSE IF Calculated ≠ Statement
  → Small variance (< 2%): Likely rounding
  → Large variance (> 2%): Investigate differences
  → Use statement value (it's the source of truth)
```

---

## Step 2: Calculate YTD P&L (Jan 1 - May 31)

**From transaction files + statements:**

```
YTD P&L Calculation:
  Account A:
    ├─ Add up all realized option P&L from transaction file (Jan 1 - May 31)
    ├─ Add unrealized P&L from May 31 open positions
    └─ Total = Account A YTD P&L

  Account B, C, Fidelity, Vanguard, Robinhood:
    └─ Same calculation

TOTAL YTD P&L (all accounts) = Sum of above
```

**What this gives you:**
- Actual YTD P&L through May 31 (verified against statements)
- Clean baseline for framework calculations
- Accurate monthly average (YTD ÷ 5 months)

---

## Step 3: Set May 31 as Framework Baseline

Update `portfolio_snapshot.yaml`:

```yaml
last_updated: "2026-05-31"
ytd_net_options_income: [CALCULATED from transaction files + verified against statements]
month_to_date_premium: [May 31 month-to-date]
ytd_months: 5
monthly_average_ytd: [YTD ÷ 5]

account_balances:
  Account A (232): [May 31 statement balance]
  Account B (275): [May 31 statement balance]
  Account C (634): [May 31 statement balance]
  Fidelity (Rahul): [May 31 statement balance]
  Fidelity (Rajul — Roth IRA): [May 31 statement balance]
  Fidelity (Rajul — Rollover IRA): [May 31 statement balance]
  Vanguard (Rahul): [May 31 statement balance]
  Robinhood (Individual): [May 31 statement balance]
  Robinhood (Traditional IRA): [May 31 statement balance]

total_portfolio_balance: [Sum of above]
```

---

## Step 4: Reconcile Framework Targets to May 31 Baseline

**Current framework (wrong baseline):**
```
YTD: $292,421 (from May 30 snapshot)
Target: $100K/month × 5 months = $500K
Gap: -$207,579
```

**New framework (May 31 baseline):**
```
YTD: $ [ACTUAL from transaction files + statements]
Target: $100K/month × 5 months = $500K
Gap: $ [ACTUAL target - actual YTD]

Example (if YTD turns out to be $320K):
  YTD: $320,000
  Target: $500,000
  Gap: -$180,000 (36% below)
```

The gap calculation changes based on actual May 31 P&L.

---

## Step 5: Account Balance Verification

**From May 31 statements, verify hardcoded balances:**

```
Hardcoded in code:
  Account A: $2,732,234
  Account B: $320,000
  Account C: $267,289
  Fidelity (Rahul): $512,000
  ... (all 9 accounts)

May 31 Statement shows:
  Account A: $ ???
  Account B: $ ???
  ... (all 9 accounts)

Comparison:
  IF match: ✅ Use as-is
  ELSE IF < 5% variance: ⚠️ Update to statement values
  ELSE IF > 5% variance: 🔴 Investigate why (missing deposits, income)

Update ACCOUNTS_CONFIG with verified May 31 balances.
```

---

## Step 6: Calculate May 31 Open Position Values

**From positions loader + May 31 prices:**

```
For each open position:
  ├─ Get May 31 closing price (from statement or Yahoo Finance)
  ├─ Get current contracts open (from statement)
  ├─ Calculate notional = price × contracts × 100
  └─ Calculate unrealized P&L

Sum notional across all positions = Portfolio notional May 31
```

This tells you:
- How much notional is deployed
- How much margin is required
- How much cash is available for new entries

---

## Step 7: Framework Targets Based on May 31 Actual

**Once May 31 is reconciled, framework should show:**

```
FRAMEWORK OVERVIEW (May 31 baseline):
  Base: $100,000/month net
  CAUTIOUS_BULL adjustment: 90%
  Regime-adjusted target: $90,000/month net

ACTUAL YTD PERFORMANCE (May 31):
  YTD Actual: $ [Calculated from transactions]
  YTD Target: $500,000 (5 months × $100K)
  YTD Gap: $ [Actual - Target]
  Monthly average (YTD): $ [YTD ÷ 5]

JUNE PERFORMANCE (Jun 1-9):
  June target so far: $90K × (9/30) = $27K
  June actual so far: $ [Open positions + June closed trades]
  June pace: [If this pace continues → June monthly total]

TOTAL FRAMEWORK GAP:
  YTD gap: $ [Amount behind through May 31]
  June gap (projected): $ [If current pace continues]
  Must close by: [End of June / End of year]
```

---

## What You Need to Provide (Specific)

**For each of the 9 accounts, May 31 statement showing:**

```
Account Name: ___________________
As of Date: May 31, 2026

1. Opening Balance (May 1): $ _________
2. Deposits/Withdrawals (May): $ _________
3. Option Realized P&L (May): $ _________
4. Closing Balance (May 31): $ _________

5. Open Positions (as of May 31):
   - Position 1: [Ticker] [Contracts] @ [Strike] [Exp]
   - Position 2: [Ticker] [Contracts] @ [Strike] [Exp]
   ... (list all)

6. Margin Used (May 31): $ _________
7. Cash Available (May 31): $ _________
8. Option Requirement (May 31): $ _________
```

**Do this for all 9 accounts:**
- Account A (232)
- Account B (275)
- Account C (634)
- Fidelity (Rahul)
- Fidelity (Rajul — Roth IRA)
- Fidelity (Rajul — Rollover IRA)
- Vanguard (Rahul)
- Robinhood (Individual)
- Robinhood (Traditional IRA)

---

## Process Flow (Once You Provide May 31 Data)

```
1. USER provides May 31 statements for all 9 accounts
   ↓
2. EXTRACT:
   ├─ YTD P&L (Jan 1 - May 31)
   ├─ May 31 balances
   ├─ May 31 open positions
   ├─ Margin used
   └─ Cash available
   ↓
3. UPDATE:
   ├─ portfolio_snapshot.yaml with May 31 actual data
   ├─ ACCOUNTS_CONFIG with May 31 verified balances
   └─ last_updated: 2026-05-31
   ↓
4. RECALCULATE:
   ├─ Conviction scores (with May 31 prices)
   ├─ Framework targets (based on actual YTD P&L)
   ├─ Gap-closure math (with real numbers)
   └─ Close recommendations (from fresh conviction)
   ↓
5. REGENERATE REPORTS:
   ├─ Daily (based on May 31 + current positions)
   ├─ Weekly
   ├─ Biweekly
   └─ Monthly
   ↓
6. RESULT:
   ├─ Consistent close recommendations (all methods agree)
   ├─ Accurate gap-closure impact (based on real P&L)
   ├─ Verified account balances
   └─ Framework targets reconciled to actual performance
```

---

## Why May 31 is Sufficient

```
BEFORE FRAMEWORK INTEGRATION:
  Need: Daily statements to show intra-month performance
  
WITH FRAMEWORK INTEGRATION:
  May 31 is the baseline for target calculation
  → June 1-9 open positions show June-to-date progress
  → June 10-30 will show additional progress
  → But June's target is tied to May 31 baseline, not daily fluctuations
  
EXAMPLE:
  May 31 YTD: $320,000 (verified from statements)
  May 31 Baseline: Account A balance $2.7M (verified)
  
  June 1-9: Open positions show $ [Current unrealized P&L]
  June 10-30: Closed trades will add realized P&L
  
  Framework: "YTD through May: $320K. Need $180K more by Dec 31."
             "June pace: If we hit $90K this month, we're on track."
```

The monthly statement approach is perfect for framework calculations because:
1. Framework targets are monthly ($90K/month)
2. Monthly statements give you verified baselines
3. Open positions show current progress within the month
4. You don't need daily reconciliation for monthly targets

---

## Summary

**You can provide:** May 31 statements for all 9 accounts  
**System calculates:** YTD P&L, verified balances, framework baselines  
**Result:** Reports reconciled to May 31 actual data  

The May 30 vs May 31 one-day difference will disappear once we update to official May 31 statements.

**Once you provide the 9 May 31 statements, I can:**
1. Reconcile all account balances
2. Calculate true YTD P&L
3. Update framework with real numbers
4. Fix all the contradictory recommendations
5. Show gap-closure based on actual data
