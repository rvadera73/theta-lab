# Production Framework Addition Summary

**Status:** ✅ Added surgically to existing reports (no rewrites)

---

## What Was Added (Not Replaced)

### 1. Configuration Block
Added to `scripts/unified_master_report.py`:
- `CLOSE_COST_RATIO` = 0.60
- `MONTHLY_TARGET_NET_BASE` = $100,000
- `MONTHLY_TARGET_GROSS_BASE` = $250,000 (auto-calculated)
- `REGIME_ADJUSTMENTS` = {'BULL': 1.00, 'SIDEWAYS': 0.85, 'BEAR': 0.70}
- `ACCOUNT_TARGETS` = All 8 accounts with gross/net targets

### 2. Helper Methods (UnifiedMasterReport class)
- `get_regime_adjusted_targets(regime)` → Returns adjusted gross/net targets for regime
- `format_production_framework_section(regime, snapshot)` → Formats supplementary framework display

### 3. Supplementary Section (After SECTION 0 in all reports)
**Title:** "SUPPLEMENTARY: PRODUCTION FRAMEWORK — 60% CLOSE COST RATIO TARGETS"

**Content:**
- Framework overview: $1.2M/year target at 60% close costs
- Current regime and adjustment %
- Adjusted monthly targets (gross/net)
- YTD performance (if snapshot available)
- Account-level regime-adjusted targets

**Placement:** After existing SECTION 0 (Account Health & Margin Status)

---

## Existing Sections (Unchanged)

All original report sections remain intact:
- ✅ SECTION 0: Account Health & Margin Status
- ✅ DAILY SECTION: Conviction Updates
- ✅ WEEKLY SECTION: Framework evolution
- ✅ MONTHLY SECTION: Portfolio rebalancing
- ✅ All other existing sections

---

## What Shows in Each Report Type

### DAILY Report
```
SECTION 0: Account Health & Margin Status [ORIGINAL]
  ├─ Portfolio snapshot
  ├─ Per-account breakdown
  └─ [existing content]

SUPPLEMENTARY: PRODUCTION FRAMEWORK — 60% CLOSE COST RATIO [NEW]
  ├─ Framework overview
  ├─ Current regime adjustment
  ├─ Adjusted targets (gross/net)
  ├─ YTD pace
  └─ Account-level targets
```

### WEEKLY Report
Same structure as DAILY (supplementary section added after SECTION 0)

### MONTHLY Report
Same structure as DAILY (supplementary section added after SECTION 0)

---

## Key Numbers Displayed

| Metric | Value |
|--------|-------|
| **Framework Target** | $1.2M/year net ($100K/month) |
| **Close Cost Ratio** | 60% (40% kept) |
| **Base Gross/Month** | $250,000 |
| **Base Net/Month** | $100,000 |

### By Regime
| Regime | Adjustment | Monthly Gross | Monthly Net |
|--------|------------|---------------|-----------|
| BULL | 100% | $250,000 | $100,000 |
| SIDEWAYS | 85% | $212,500 | $85,000 |
| BEAR | 70% | $175,000 | $70,000 |

### Account Allocation
Each account shows proportional targets, e.g., Account A (61% of capital):
- BEAR regime: $106,750 gross / $42,700 net
- BULL regime: $152,500 gross / $61,000 net
- SIDEWAYS: $129,625 gross / $51,850 net

---

## How Data Flows

1. **regime** (from `market_regime` variable in existing code)
   → Used by `get_regime_adjusted_targets(regime)`

2. **snapshot** (existing `portfolio_snapshot.yaml`)
   → Used by framework section to show YTD pace

3. **Output formatting** via `format_production_framework_section()`
   → Inserted after existing SECTION 0
   → Doesn't modify existing sections

---

## No Breaking Changes

- ✅ Original report structure intact
- ✅ Existing sections unchanged
- ✅ New section is purely additive (supplementary)
- ✅ Works with existing data sources (no new data required)
- ✅ Backward compatible with all 4 report types (daily/weekly/biweekly/monthly)

---

## To Use the Framework

1. Run existing report generation (no changes to workflow)
2. View supplementary framework section after SECTION 0
3. Compare actual performance (from snapshot) to regime-adjusted targets
4. Adjust trading strategy if needed based on variance

---

**Last updated:** June 9, 2026  
**Framework version:** 1.0 (supplementary addition, non-breaking)
