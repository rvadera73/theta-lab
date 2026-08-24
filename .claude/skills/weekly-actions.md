# Weekly Actions Skill

Runs Mondays at 8 AM ET to generate weekly action plan.

## Invocation

```
/weekly-actions
```

## Output

Generates weekly report with:
- Portfolio Greeks health (delta/gamma/theta targets)
- Position heat summary (RED/YELLOW/GREEN counts)
- **Thesis validation summary** (status distribution, avg conviction, tier distribution)
- **Top-5 actions** (thesis-aware, prioritized by conviction)
- Heat protocol (which positions threatened)
- Risk utilization check
- Stress test scenarios
- **AI Capex Risk Tracker** (Section 6.6) — Technology concentration and the
  named high-risk/quality-AI/avoid-list buckets' live $ exposure vs. the
  90-day Circular Financing Playbook's 30/70 target, flagged if drift
  exceeds 10pp. Scriptable tracking only; the Tier 1/2 credit/IPO check runs
  separately via `/ai-capex-risk-review`.
- Next week focus

Saves to: `logs/enhanced_weekly_report_{YYYY-MM-DD}.txt`

## Execution Flow

1. Load positions from all 6 accounts
2. Calculate Greeks
3. Update thesis state for each position
4. Get thesis summary (RED/YELLOW/GREEN counts, avg conviction, tier distribution)
5. Build Top-5 actions prioritized by:
   - RED thesis first (conviction ≤2, close immediately)
   - YELLOW thesis next (conviction 3-5, monitor)
   - Greeks breaches (delta/gamma/theta targets)
6. Show alternatives from screener for RED positions
7. Generate report and save to logs/

## Top-5 Actions Priority

1. **Close RED thesis positions** (conviction ≤2)
   - Example: PYPL weak moat + 2 guidance cuts
   - Alternatives: ALAB (Tier 2, STRONG), RKLB, VST

2. **Manage RED heat** (price threatens strike)
   - Roll down+out for puts, up+out for calls
   - Target: 40-50% profit close

3. **Fix Greeks breaches** (delta/gamma/theta)
   - Delta breach: close calls or puts
   - Gamma breach: close strangles
   - Theta shortfall: enter new positions

4. **Monitor YELLOW thesis** (conviction 3-5)
   - Prepare roll or exit
   - Watch for earnings/guidance updates
   - Be ready to close if conviction drops to RED

5. **Daily monitoring** (conviction + Greeks)
   - Check each morning
   - Alert if conviction drops or breaches occur
   - Monitor breaking point (max market move)

## What This Report Tells You

**Conviction Avg:** Is your portfolio getting stronger (higher conviction) or weaker?

**RED count:** How many positions have thesis broken?

**YELLOW count:** How many at risk, need watching?

**GREEN count:** How many have intact thesis?

**Tier distribution:** Are you weighted toward Tier 1 quality or drifting to Tier 3 speculation?

## Automatic Scheduling

GitHub Actions runs this Mondays at 8 AM ET:
```yaml
name: Weekly Actions Report
on:
  schedule:
    - cron: '0 13 * * 1'  # 8 AM ET Mondays = 13 UTC
```

Result emailed to user via Resend API.
