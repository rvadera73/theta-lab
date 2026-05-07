# Daily Execution Skill

Runs each morning at 6 AM ET to generate daily trading action plan.

## Invocation

```
/daily-execution
```

## Output

Generates daily report with:
- Current Greeks status (delta, gamma, theta)
- Greeks breaches (vs targets)
- Thesis validation (RED/YELLOW/GREEN positions)
- Account-by-account trades (CLOSE, ROLL, ENTER)
- Execution mechanics (how to place trades)

Saves to: `logs/daily_trade_execution_{YYYY-MM-DD}.txt`

## Execution Flow

1. Load positions from all 6 accounts (Schwab, Fidelity, Vanguard)
2. Calculate Greeks from market data
3. Update thesis state for each position
4. Identify Greeks breaches
5. Prioritize trades (thesis RED first, then Greeks)
6. Format recommendations with strike/qty/DTE
7. Generate report and save to logs/

## Pre-Execution

Before executing trades from this report:
- [ ] Review thesis validation section (any RED positions?)
- [ ] Check Greeks targets (which are breached?)
- [ ] Run `dry_run_order` on first 2-3 trades
- [ ] Verify account equity % matches expectations

## What to Do With This Report

**If delta breached (+22, target ±20):**
- Close 2 short calls (reduces long delta)
- Or close puts if delta negative

**If gamma breached (+0.64, target ≤0.5):**
- Close short strangles (both legs)
- Target: Reduce by 0.15 gamma

**If theta below target (+176, need ≥$300):**
- Enter new strangles/CSPs
- 2-3 new positions = +$30-50/day theta
- Check IVR ≥40 before entering

**If thesis RED (conviction ≤2):**
- Close immediately, don't wait
- Redeploy to alternatives suggested in report
- Examples: PYPL RED → ALAB/RKLB/VST

## Automatic Scheduling

GitHub Actions runs this at 6 AM ET daily:
```yaml
name: Daily Trade Execution Report
on:
  schedule:
    - cron: '0 11 * * *'  # 6 AM ET = 11 UTC
```

Result emailed to user via Resend API.
