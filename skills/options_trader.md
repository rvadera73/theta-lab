# Options Trader Skill

**Status: SCAFFOLD** — Full logic will be populated after trading_persona.md is complete.

## Invocation
This skill is invoked when the user asks to scan for trades, evaluate a position, or manage existing positions.

## Pre-Flight Checklist (MANDATORY — every trade)
1. Load `config/risk_params.yaml`
2. Load `skills/trading_persona.md` (verify not PENDING)
3. Call `dry_run()` via open-stocks-mcp — confirm balance, buying power, Greeks
4. Verify position does not breach portfolio-level Greeks limits
5. Verify ticker is in approved universe from trading_persona.md
6. Check earnings blackout calendar
7. Check VIX regime gate

## Account A Logic (Margin — Phases 2, 3, 4)
- TO BE POPULATED after persona analysis

## Account B Logic (IRA — Phase 4 only)
- TO BE POPULATED after IRA options level confirmed
- Prerequisite: Schwab IRA Level 2 options approval

## Phase Gate
Current phase is read from `config/phase.yaml` (created at Day 1).
All actions are gated to current phase rules before execution.
