# Weekly Actions Skill

Generates a weekly action plan. Run on-demand via the MCP tool
`generate_weekly_action_report` (or the equivalent `/weekly-actions`
invocation), triggered manually or via Claude Code — **not** on an
unattended schedule (see "Automatic Scheduling" below).

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

**Not currently automated.** There is no `.github/workflows/` directory in
this repo, so no GitHub Actions cron job runs this report. A scheduler
script (`mcp/routines/unified_reports_scheduler.py`) and a cron-install
script (`scripts/setup_cron.sh`) exist in the repo and can drive this
report on a schedule, but as of this writing there is no crontab installed
and the most recent scheduler run logs (`logs/scheduler_run_*.json`) are
from May 2026 — stale, not evidence of a live schedule. In practice this
report runs on-demand via the MCP tool, triggered manually or via Claude
Code.

Email delivery via Resend (`mcp/routines/email_report.py`, using the
`RESEND_API_KEY` env var) is real and can be wired into a manual or future
scheduled run, but it is not itself what triggers report generation.
