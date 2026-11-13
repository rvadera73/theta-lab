# Daily Execution Skill

Generates a daily trading action plan. Run on-demand via the MCP tool
`generate_unified_master_report` (or the equivalent `/daily-execution`
invocation), triggered manually or via Claude Code — **not** on an
unattended schedule (see "Automatic Scheduling" below).

## Invocation

```
/daily-execution
```

## Output

Generates daily report with:
- Position heat summary (per-leg GREEN/YELLOW/RED, from `heat_scanner.py`)
- Thesis validation (RED/YELLOW/GREEN positions)
- Account-by-account trades (CLOSE, ROLL, ENTER)
- Execution mechanics (how to place trades)

Saves to: `logs/daily_trade_execution_{YYYY-MM-DD}.txt`

## Execution Flow

1. Load positions from all 9 accounts across 4 brokers: Schwab (A, B, C),
   Robinhood (D — Individual, E — Traditional IRA), Fidelity (F1 — Traditional
   IRA, F2 — Roth IRA (Minor), G1 — Roth IRA, G2 — Rollover IRA), Vanguard (H
   — Brokerage) — see `mcp/config.py`'s `ACCOUNTS` dict for the authoritative
   list.
2. Score each short option leg's heat (`heat_scanner.py`): coverage
   (COVERED/NAKED/CASH_SECURED_PUT/PARTIAL) gates which ladder applies, then
   distance-to-strike, cost-to-close as a multiple of premium received, and
   DTE remaining drive a GREEN/YELLOW/RED color + action per leg.
3. Update thesis state for each position
4. Rank actions across the book by real urgency (`sequencer.py`): gates
   (e.g. forced near-expiry closes) fire first regardless of score; existing
   positions in trouble outrank new entries; new entries are then ranked by
   composite score with IV Rank as a tie-breaker.
5. Prioritize trades (thesis RED first, then heat severity)
6. Format recommendations with strike/qty/DTE
7. Generate report and save to logs/

## Pre-Execution

Before executing trades from this report:
- [ ] Review thesis validation section (any RED positions?)
- [ ] Check position heat (any RED/YELLOW legs needing action?)
- [ ] Run `dry_run_order` on first 2-3 trades
- [ ] Verify account equity % matches expectations

## What to Do With This Report

**If a leg is heat RED (coverage-gated: naked/CSP/partial legs breach on
strike-distance + loss-multiplier; covered-call legs breach on DTE only —
see `heat_scanner.py`):**
- Naked/CSP/partial: roll or cut per the ladder's prescribed action
  (`CUT_RESTAGGER`, `ROLL_OR_CUT_PUT`, `ROLL_CALL`, etc.)
- Covered calls: manage by DTE window (gamma/roll-decision zone), not by
  loss-multiple — assignment at the strike is the designed outcome, not a
  loss

**If a leg is heat YELLOW:**
- Prepare to roll or harvest; watch for the position to cross into RED

**If thesis RED (conviction ≤2):**
- Close immediately, don't wait
- Redeploy to alternatives suggested in report
- Examples: PYPL RED → ALAB/RKLB/VST

Note: this report does not compute or track portfolio-level Greeks (delta/
gamma/theta) against fixed targets — no code in this pipeline does that
today (`mcp/reports/unified_master_report_production.py` flags this
honestly rather than showing fabricated numbers). Risk management here is
driven by the per-leg heat/coverage model above, not a Greeks-breach
workflow.

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
