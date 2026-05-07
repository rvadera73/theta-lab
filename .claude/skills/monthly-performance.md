# Monthly Performance Skill

Runs 1st of month at 8 AM ET to generate monthly performance analysis.

## Invocation

```
/monthly-performance
```

## Output

Generates monthly report with:
- Monthly P&L vs target
- YTD progress vs annual target ($1.2M)
- Annualized pace projection
- **Attribution analysis** (theta, vega, rolls, slippage sources)
- Account performance (A vs B vs C vs IRAs vs Vanguard)
- **Holdings universe alignment** (actual portfolio vs screener-eligible universe)
- **Tier distribution** (actual Tier 1/2/3 vs available)
- **Positions outside universe** (thesis broken, should be closed)
- **Tier 3 → Tier 2 graduation candidates** (conviction ≥7)
- Greeks trends (current state + targets)
- Next month strategy

Saves to: `logs/enhanced_monthly_report_{YYYY-MM-DD}.txt`

## Execution Flow

1. Load positions and transactions from all 6 accounts
2. Calculate attribution (where profit comes from)
3. Update thesis state for each position
4. Load Holdings universe (screener-generated, regime-filtered)
5. Compare actual portfolio vs universe
6. Identify:
   - Coverage % (how many actual positions in universe?)
   - Tier distribution mismatches
   - Positions outside universe (RED thesis)
   - Graduation candidates (Tier 3 with high conviction)
7. Generate report and save to logs/

## What This Report Tells You

**Attribution:** Is theta your primary profit source (60%+)? Or vega? Or slippage?

**Conviction trends:** Did average conviction improve during the month?

**Holdings universe alignment:** Are you 95%+ covered by screener universe? Or are you holding broken theses?

**Tier distribution:** Target is 60% Tier 1, 30% Tier 2, 10% Tier 3. Are you aligned?

**Coverage %:** 90%+ = healthy. <80% = red flag for thesis breakdown.

**Graduation candidates:** Any Tier 3 with conviction ≥7? Consider promoting to Tier 2.

**Positions outside universe:** Why? Thesis changed? Need to investigate and update screener.

## Monthly Actions

1. **Review attribution** — Is theta ≥60% of profit?
   - If yes: Continue current strategy
   - If no: Need more strangles/CSPs

2. **Check conviction trend** — Is avg conviction rising?
   - If yes: Portfolio discipline improving
   - If no: Need to close more RED positions

3. **Assess universe alignment** — Is coverage ≥90%?
   - If yes: Portfolio stays thesis-aligned
   - If no: Red flag for broken theses, investigate

4. **Evaluate tier distribution** — Are you Tier 1 heavy?
   - Tier 1 heavy (70%+): Conservative, good quality
   - Tier 3 heavy (20%+): Risky, good for bull markets

5. **Plan next month** — What changed?
   - Did any sector thesis break?
   - Did any name graduate tiers?
   - Should portfolio composition shift?

## Automatic Scheduling

GitHub Actions runs this 1st of each month at 8 AM ET:
```yaml
name: Monthly Performance Report
on:
  schedule:
    - cron: '0 13 1 * *'  # 8 AM ET on 1st = 13 UTC
```

Result emailed to user via Resend API.

## Success Metrics (Month-over-Month)

- ✅ Conviction average rising (5.2 → 5.7 → 6.1)
- ✅ RED position count dropping (5 → 2 → 0)
- ✅ Holdings universe coverage rising (85% → 92% → 98%)
- ✅ Attribution theta ≥60% of profit
- ✅ P&L hitting monthly targets ($100K+)
