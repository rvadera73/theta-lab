# Performance Engine Reports — How to Generate

## Quick Reference: What to Ask

### Daily Report (Market Close, ~4:15 PM ET)
```
Generate live dashboard with June 8 validated position data
```
**Output:** `logs/THETA_LAB_LIVE_DASHBOARD_2026-06-[DATE].txt`  
**Contains:** Margin status, Greeks, concentration, naked calls, next steps  
**Time:** ~2 minutes

---

### Weekly Report (Friday ~4:15 PM ET)
```
Generate weekly execution report comparing plan vs actual
```
**Output:** `logs/THETA_LAB_WEEKLY_EXECUTION_2026-06-[DATE].txt`  
**Contains:** Planned actions, actual execution, P&L variance, account performance  
**Time:** ~3 minutes (need plan from Monday)

---

### Bi-Weekly Report (7th & 22nd of month)
```
Generate bi-weekly trend and risk analysis report
```
**Output:** `logs/THETA_LAB_BIWEEKLY_TREND_2026-06-[DATE].txt`  
**Contains:** Edge validity (puts vs calls), market breakdown scenarios, regime forecast  
**Time:** ~3 minutes

---

### Monthly Report (Month-end)
```
Generate monthly strategy review with annual progress update
```
**Output:** `logs/THETA_LAB_MONTHLY_STRATEGY_2026-06-[DATE].txt`  
**Contains:** YTD vs target, account performance, H2 plan adjustments  
**Time:** ~3 minutes

---

## Full Command (All 4 Reports at Once)

```
Generate all four reports: live dashboard, weekly execution, bi-weekly trend, monthly strategy
with June 8 validated position data, save to logs folder
```

This generates all 4 reports in one run. Use this at month-end or after major position changes.

---

## Required Data Before Each Report

### Live Dashboard
✓ Current position files (loads automatically from data/positions/)  
✓ Current market data (IV Rank, VIX, SPX level)  
✓ No manual input needed

### Weekly Execution
✓ Plan from previous Monday (what you planned to do)  
✓ Actual executions (what you actually did)  
✓ Current positions (loads automatically)  
- **Ask:** "Generate weekly execution report (closed trades: [closed tickets], new entries: [entries])"

### Bi-Weekly Trend
✓ Transaction history (loads automatically)  
✓ Current positions (loads automatically)  
✓ Current market regime (IV Rank, VIX, sector performance)  
- **Ask:** "Generate bi-weekly trend analysis (IV Rank 45, VIX 18, sideways regime)"

### Monthly Strategy
✓ All the above  
✓ Closed trades for the month  
✓ Adjustments made or planned  
- **Ask:** "Generate monthly strategy review with [account changes], [new positions closed/opened]"

---

## Default Behavior (Automated)

The engine is configured to:
1. **Load position files automatically** from `/data/positions/`
2. **Save all reports to** `/logs/` folder
3. **Include validated June 8 baseline** for comparison
4. **Generate date-stamped filenames** (THETA_LAB_TYPE_2026-06-08.txt)
5. **No data entry needed** except for weekly execution details

---

## What NOT to Ask

❌ "Update the reports" (ambiguous — which report?)  
❌ "Generate reports" (ambiguous — all 4 or one?)  
❌ "Run the analysis" (ambiguous — what analysis?)  

---

## What TO Ask

✅ "Generate live dashboard"  
✅ "Generate weekly execution report for [plan]"  
✅ "Generate all four reports"  
✅ "Generate bi-weekly trend analysis"  
✅ "Generate monthly strategy review"  

---

## Example Conversation Flow

**You (Monday 9 AM):** "Here's the plan for this week: [entries: ABC, DEF; closures: XYZ]"  
**Me:** *saves plan*

**You (Friday 4 PM):** "Generate weekly execution report (closed: ABC at 50%, DEF at 40%, entered: XYZ)"  
**Me:** *loads actual positions, compares to plan, generates weekly report*  
**Output:** `logs/THETA_LAB_WEEKLY_EXECUTION_2026-06-14.txt`

**You (22nd of month):** "Generate bi-weekly trend analysis"  
**Me:** *analyzes transaction history, current regime, market conditions*  
**Output:** `logs/THETA_LAB_BIWEEKLY_TREND_2026-06-22.txt`

**You (June 30):** "Generate monthly strategy review"  
**Me:** *calculates YTD vs target, account performance, H2 adjustments*  
**Output:** `logs/THETA_LAB_MONTHLY_STRATEGY_2026-06-30.txt`

---

## File Organization

```
/home/rahulvadera/projects/theta-lab/
├── theta_lab_performance_engine.py          (main engine, auto-saves to logs/)
├── data/
│   ├── positions/                           (source: Schwab position exports)
│   ├── portfolio_snapshot.yaml              (YTD baseline)
│   └── statements/
├── logs/                                    (all reports saved here)
│   ├── THETA_LAB_LIVE_DASHBOARD_*.txt       (daily)
│   ├── THETA_LAB_WEEKLY_EXECUTION_*.txt     (Friday)
│   ├── THETA_LAB_BIWEEKLY_TREND_*.txt       (7th & 22nd)
│   ├── THETA_LAB_MONTHLY_STRATEGY_*.txt     (month-end)
│   ├── CORRECTED_ASSUMPTIONS.md
│   └── ENGINE_READY_SUMMARY.md
└── scripts/
    ├── data_loader_final.py
    └── generate_real_reports.py
```

---

## Frequency & Cadence

| Report Type | Frequency | Best Time | Ask | Output |
|-------------|-----------|-----------|-----|--------|
| Live Dashboard | Daily | 4:15 PM ET | "Generate live dashboard" | `LIVE_DASHBOARD_*.txt` |
| Weekly Execution | Fridays | 4:15 PM ET | "Generate weekly execution report ([plan])" | `WEEKLY_EXECUTION_*.txt` |
| Bi-Weekly Trend | 7th & 22nd | 9 AM | "Generate bi-weekly trend analysis" | `BIWEEKLY_TREND_*.txt` |
| Monthly Strategy | Month-end | 9 AM | "Generate monthly strategy review" | `MONTHLY_STRATEGY_*.txt` |

---

## Example: Full Month Sequence

```
June 1:   → Live Dashboard (market open)
June 3:   → Weekly Execution (Friday, closed trades this week)
June 7:   → Bi-Weekly Trend (mid-month check)
June 10:  → Live Dashboard (daily check)
June 14:  → Weekly Execution (Friday, weekly recap)
June 21:  → Bi-Weekly Trend (late month check)
June 28:  → Weekly Execution (Friday, last week of month)
June 30:  → Monthly Strategy Review (month-end, H2 planning)
```

---

## Notes

- **All reports load data automatically** from position files — no manual entry needed
- **All reports save to logs folder** — clean organization, no clutter in main directory
- **All reports include June 8 validation baseline** — ensures data consistency
- **Reports are timestamped** — easy to track versions and run history
- **Reports are self-contained** — can be archived/compared over time

