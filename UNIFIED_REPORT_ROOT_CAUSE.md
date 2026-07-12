# Root Cause Analysis: Unified Master Report Failure

## The Real Problem

**Two completely different scripts exist:**

1. **Working version (generates good 06-01 reports):**
   - Location: `/home/rahulvadera/projects/theta-lab/mcp/reports/unified_master_report_production.py`
   - Status: ✅ Generates complete, well-structured reports with all sections
   - Output: 06-01 reports with 10 sections, detailed analysis, working conviction scores

2. **Broken version (current, generates incomplete 06-08 reports):**
   - Location: `/home/rahulvadera/projects/theta-lab/scripts/unified_master_report.py`
   - Status: ❌ Incomplete skeleton, missing critical logic
   - Output: 06-08 reports with just a raw list of all 573 positions, all showing "Conviction 2/10"

**User's requirement:** Consolidate to single script in `/scripts/` directory that works correctly for all 4 report types.

---

## What the MCP Version Does (CORRECT)

### Class: UnifiedReportProduction

**Initialization:**
- Loads open positions via `OpenPositionsLoaderV2()`
- Calculates Greeks for all positions via `batch_get_metrics()`
- Gets IV rank for top tickers via `batch_iv_rank()`
- Gets sector analysis via `batch_get_sector_analysis()`
- Detects market regime via `detect_regime()`
- Loads portfolio snapshot with YTD/MTD data

**Key Methods:**

1. **_parse_put_call_breakdown()** — Analyzes puts vs calls per ticker
   - Counts contracts per type
   - Calculates notional exposure per type
   - Result: Can separate puts from calls for different sections

2. **_calculate_option_requirement()** — Uses Greeks-based calculation
   - Delta × price × contracts × 100
   - Returns requirement per ticker
   - Enables margin safety checks

3. **_get_heat_summary()** — Groups positions by heat status
   - Returns counts: RED, YELLOW, GREEN
   - Used in all report types

4. **_get_conviction_summary()** — Groups positions by conviction
   - Buckets: HIGH (8-10), CORE (6-7), MONITOR (5), EXIT (<5)
   - Result: Can show meaningful conviction breakdown

**Report Generation:** Uses `generate_report_type(report_type)` method that generates completely different content for each type:
- DAILY: Focus on conviction updates + daily action items
- WEEKLY: Action priorities, IV rank gate, theta tracking, decision trees
- BIWEEKLY: YTD pace vs target, per-account variance
- MONTHLY: Framework recalibration, moat updates, annual goals

---

## What the Scripts Version Has (BROKEN)

### Class: UnifiedMasterReport

**Current structure:**
- Loads data via data_loader_final.py
- **MISSING:** Greeks calculation for all positions
- **MISSING:** Heat status per position
- **MISSING:** IV rank analysis
- **MISSING:** Sector analysis

**Current report generation:**
1. SECTION 0: Account Health (✅ correct)
2. SECTION 1: Conviction Updates (❌ broken)
   - Iterates through SYMBOLS, not POSITIONS
   - Takes only first position per symbol via `iloc[0]`
   - Calculates conviction per symbol (wrong)
   - All positions show "Conviction 2/10" (hardcoded output)

3. SECTION 2-3: Weekly/Monthly sections (❌ incomplete)
   - Has placeholder logic but missing actual data sources
   - No actual conviction per position
   - No Greeks analysis
   - No decision trees
   - No framework status automation tracking

**Report type detection:** Works but output is identical for all types

---

## Comparison Table: MCP vs Scripts Version

| Feature | MCP Version | Scripts Version |
|---------|------------|-----------------|
| Greeks Calculation | ✅ batch_get_metrics() | ❌ Missing |
| Heat Status | ✅ Per position | ❌ Placeholder '🟢 GREEN' |
| IV Rank Analysis | ✅ batch_iv_rank() | ❌ Missing |
| Sector Analysis | ✅ batch_get_sector_analysis() | ❌ Missing |
| Conviction Calculation | ✅ Per position with context | ❌ Per symbol, hardcoded to 2/10 |
| Report Type Differences | ✅ Different content per type | ❌ Same content for all types |
| Notional Exposure | ✅ Calculated | ❌ Missing |
| Option Requirement | ✅ Greeks-based | ❌ Missing |
| Position Heat Grouping | ✅ RED/YELLOW/GREEN counts | ❌ Missing |
| Decision Trees | ✅ IF/THEN action items | ❌ Missing |
| Framework Automation Status | ✅ Section 10 in report | ❌ Missing |

---

## The Fix Strategy

### Phase 1: Identify What to Port
- **From MCP:** UnifiedReportProduction class structure
- **From MCP:** All `generate_*` methods for each report type
- **From Scripts:** Data loading integration with data_loader_final.py
- **From Scripts:** Account configuration

### Phase 2: Build New Unified Script
The new `scripts/unified_master_report.py` needs:

1. **Data loading layer:**
   - Use OpenPositionsLoaderV2 (from MCP)
   - OR integrate with data_loader_final.py (current)
   - Include Greeks calculation via batch_get_metrics()

2. **Analysis layer:**
   - batch_get_metrics() for Greeks + heat status
   - batch_iv_rank() for IV analysis
   - batch_get_sector_analysis() for sector rotation
   - detect_regime() for market regime
   - Moat/tier lookups via screener_loader.py

3. **Report generation layer:**
   - Separate methods for each report type
   - DAILY: Conviction + heat scan
   - WEEKLY: Actions + IV gate + theta + decision trees
   - BIWEEKLY: YTD pace + account variance
   - MONTHLY: Framework recalibration + moat updates

4. **Output layer:**
   - Proper formatting for each type
   - Save to correct filenames with report type suffix
   - Support "all" argument to generate all 4

### Phase 3: Command-Line Interface
- `python3 scripts/unified_master_report.py DAILY` → generates daily report
- `python3 scripts/unified_master_report.py WEEKLY` → generates weekly report
- `python3 scripts/unified_master_report.py BIWEEKLY` → generates biweekly report
- `python3 scripts/unified_master_report.py MONTHLY` → generates monthly report
- `python3 scripts/unified_master_report.py all` → generates all 4 reports

---

## Why All Positions Show "Conviction 2/10"

Current code (line 183-191 in scripts version):
```python
moat = ScreenerLoader.get_moat_strength(symbol)  # Returns 'UNKNOWN' for most symbols
pnl = sym_data.get('pnl', 0)  # Gets 0 (pnl field doesn't exist or is 0)
heat = sym_data.get('heat', '🟢 GREEN')  # Placeholder, not from data

conviction_obj = HedgeFundFramework.calculate_conviction(
    symbol=symbol,
    moat_strength=moat,  # 'UNKNOWN' → moat_map.get('UNKNOWN', 0) = 0
    earnings_trend='BEAT' if pnl > 0 else 'EQUAL',  # Returns 'EQUAL' → +0
    momentum_score=momentum,  # momentum = -5 if pnl==0 → int(-5/10) = 0
    heat_status=heat,  # Placeholder → doesn't match heat_map keys
    pnl_status='WINNING' if pnl > 0 else 'NEUTRAL'  # Returns 'NEUTRAL' → +0
)
```

Calculation:
- score = 1 (floor)
- moat: 'UNKNOWN' → 0
- earnings: 'EQUAL' → 0  
- momentum: -5 → int(-0.5) = 0
- heat: '🟢 GREEN' → 1
- pnl: 'NEUTRAL' → 0
- **Total: 1 + 0 + 0 + 0 + 1 + 0 = 2**

Why does the output still say 2/10? Line 234 should use the actual conviction value:
```python
output.append(f"  • {sym:10} Conviction {conv}/10")  # conv comes from loop variable
```

But... the output file shows ALL 573 positions with 2/10, not just LOW conviction ones.

**Likely explanation:** The output at line 234 is iterating through wrong data or there's a bug in how low_conviction_positions list is built. It's showing ALL position details but saying they're all low conviction.

---

## Summary

**The task is to:**
1. Take the working MCP version logic
2. Port it to scripts/unified_master_report.py
3. Make it handle "all" argument to generate all 4 reports
4. Ensure conviction is calculated correctly per position
5. Ensure each report type has different, meaningful sections

**Files to change:**
- `/home/rahulvadera/projects/theta-lab/scripts/unified_master_report.py` — Complete rewrite from MCP version
- Supporting files: data_loader_final.py, screener_loader.py (may need tweaks)

**Do NOT change:**
- MCP version (keep it as reference/backup)
- Other report generator scripts (they're obsolete)

---

END OF ANALYSIS
