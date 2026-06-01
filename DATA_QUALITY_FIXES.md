# Data Quality Fixes — May 31, 2026

## Issues Found and Fixed

### 1. **Fidelity Accounts Showing 0 Positions** ✅ FIXED
**Problem:** Fidelity glob pattern was `*Rahul*Fidelity*.csv` and `*Rajul*Fidelity*.csv`, but actual files were:
- `Accounts_History -Fidelity-Rahul.csv` (has Fidelity BEFORE Rahul)
- `Accounts_History-Rajul.csv` (no "Fidelity" in name)

Patterns didn't match → Fidelity files not loaded → 0 positions showed

**Solution:** Fixed patterns to:
- `*Fidelity*Rahul*.csv` (now matches Accounts_History -Fidelity-Rahul.csv)
- `*Rajul*.csv` (now matches Accounts_History-Rajul.csv)

**Result:** 
- Fidelity (Rahul): Now shows 67 open positions ($1.81M notional)
- Fidelity (Rajul — Roth IRA): Now shows 9 open positions ($51K notional)
- Fidelity (Rajul — Rollover IRA): Now shows 15 open positions ($258K notional)

### 2. **Vanguard Account Name Mismatch** ✅ FIXED
**Problem:** Data loader set account_name to just "Vanguard", but ACCOUNTS_CONFIG has "Vanguard (Rahul)"
Result: Vanguard positions didn't match any account in the report

**Solution:** Changed pattern from:
```python
('*Vanguard*.csv', 'Vanguard')
```
To:
```python
('*Vanguard*.csv', 'Vanguard (Rahul)')
```

**Note:** Vanguard shows 0 open positions (all equity, no options currently)

### 3. **ASML Appearing as Open Position When Fully Closed** ✅ FIXED
**Problem:** ASML had transactions like:
- 01/05: Sell to Open (STO) @ 1100P strike
- 01/05: Buy to Close (BTC) @ 950P strike ← orphaned close (no matching STO)
- 01/20: Buy to Close (BTC) @ 950P strike
- 01/21: Buy to Close (BTC) @ 1100P strike

The 950P strike had a BTC without matching STO in May 30 export, so it appeared as an open position.

**Root Cause:** Monthly transaction exports don't include full position history. When STO happened in Dec and BTC in Jan, a May export only sees the BTC and treats it as an open position.

**Solution:** Added check to filter out "orphaned closing transactions" — positions that only have BTC/STC without any matching STO/BTO in the dataset:
```python
# Only include if: net_qty != 0 AND has at least one opening transaction
if net_qty != 0 and has_opening:
    # include position
```

**Result:**
- ASML completely removed from all reports
- Total positions reduced: 296 → 259 (37 orphaned transactions filtered)
- ASML 950P strike (orphaned BTC) now excluded
- ASML 07/17 and 03/20 puts excluded (expired)

### 4. **Missing Option Requirement Per Account** ✅ ADDED
**Problem:** Section 0 showed notional but not option requirement per account
Notional and option requirement are different:
- **Notional** = price × contracts × 100 (underlying value)
- **Option Requirement** = notional × 12.5% (margin/collateral needed on Schwab)

**Solution:** Added "Opt Req" column to Section 0 breakdown showing per-account option requirement

**Before:**
```
Account A (232)  |  Notional: $4,683,464
```

**After:**
```
Account A (232)  |  Notional: $3,319,229  |  Opt Req: $414,904  |  Margin: 60.0%
```

Plus definitions:
- Notional = price × contracts × 100
- Option Requirement = Notional × 12.5% (margin collateral needed)

## Revised Account Positions Summary

| Account | Positions | Notional | Opt Req | Status |
|---------|-----------|----------|---------|--------|
| Account A (232) | 119 | $3.32M | $414K | ✅ Margin 60% |
| Account B (275) | 28 | $376K | $47K | ✅ Compliant |
| Account C (634) | 21 | $228K | $28K | ✅ Compliant |
| Fidelity (Rahul) | 67 | $1.81M | $226K | ✅ Compliant |
| Fidelity (Rajul — Roth IRA) | 9 | $51K | $6.5K | ✅ Compliant |
| Fidelity (Rajul — Rollover IRA) | 15 | $258K | $32K | ✅ Compliant |
| Vanguard (Rahul) | 0 | $0 | $0 | Equity only |
| Robinhood (Individual) | 0 | $0 | $0 | Equity only |
| Robinhood (Traditional IRA) | 0 | $0 | $0 | Equity only |
| **TOTAL** | **259** | **$6.05M** | **$756K** | **✅ SAFE** |

## Impact on Reports

### Updated Section 0: Account Health
- Now shows all 8 accounts (was showing 2)
- Shows position count per account
- Shows notional exposure per account
- Shows option requirement per account (NEW)
- Shows monthly target per account
- Clear status indicators (MARGIN, COMPLIANT, etc.)

### Clean Data
- Removed 37 orphaned closing transactions
- Removed ASML and other closed positions incorrectly showing as open
- Total positions: 296 → 259
- All remaining positions have matching opening transactions

## Data Integrity Standards Going Forward

### What We Now Require
1. **Complete transaction history** — not monthly exports
   - If possible, get YTD or account-inception history
   - This way, all BTC transactions have matching STO transactions in the same export

2. **Account mapping clarity**
   - For Fidelity, ensure Account column properly identifies different IRA types
   - Current mapping:
     - "ROTH IRA" or "ROTH IRA for Minor" → Fidelity (Rajul — Roth IRA)
     - "Traditional IRA" → Fidelity (Rajul — Rollover IRA)

3. **File naming consistency**
   - Stick to current patterns (files will auto-match):
     - Schwab: `*XXX<account#>_Transactions_*.csv`
     - Fidelity: `*Fidelity*Rahul*.csv`, `*Rajul*.csv`
     - Vanguard: `*Vanguard*.csv`
     - Robinhood: `Robinhood_Account<#>_*.csv`

## Next Steps

1. Export **complete YTD transaction history** from Schwab/Fidelity/Vanguard/Robinhood
   - This ensures all positions are fully reconciled
   - Prevents "orphaned" closing transactions

2. For May reporting: re-run with complete YTD file if available

3. Monitor: each month, if you see positions that "should be closed", check:
   - Is there an opening transaction in the export?
   - If BTC without STO = likely historical transaction that opened before the export period

## Files Modified

- `/home/rahulvadera/projects/theta-lab/scripts/open_positions_loader_v2.py`
  - Fixed Fidelity/Vanguard/Robinhood glob patterns
  - Added orphaned closing transaction filter
  - Added account mapping for Rajul IRA accounts

- `/home/rahulvadera/projects/theta-lab/mcp/reports/unified_master_report_production.py`
  - Added option requirement calculation per account
  - Added definitions for notional vs option requirement
  - Enhanced Section 0 to show all 8 accounts with option requirements
