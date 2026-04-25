# 120-Day Execution Plan

## Phase Gates

### Phase 1: MOCK MODE (Days 1–30)
**Objective:** Validate signal generation and risk logic without capital at risk.

- All trade signals logged to `logs/paper_trades.log`
- No real orders submitted via open-stocks-mcp
- Daily log entries: ticker, strategy, entry price, strikes, expiration, Greeks, IVR
- **Exit criteria to advance:** 20+ paper trades logged, win rate > 55%, no logic errors

### Phase 2: ALPHA MODE (Days 31–60)
**Objective:** Validate live execution mechanics with limited capital.

- Account A only
- Hard cap: $100,000 deployed (regardless of account size)
- Max 5 concurrent positions
- Weekly review: P&L vs paper trade projections
- **Exit criteria to advance:** Execution fills within 5% of paper prices, no risk breaches

### Phase 3: SCALE MODE (Days 61–90)
**Objective:** Full Account A deployment.

- Account A: Full capital, standard position limits from risk_params.yaml
- Continue monitoring paper signals for Account B strategies (no execution)
- **Exit criteria to advance:** Annualized return on track (>15% pace), drawdown < 10%

### Phase 4: RETIREMENT MODE (Days 91–120)
**Objective:** Enable Account B (IRA) with conservative Wheel strategy.

- **Prerequisite:** Confirm Schwab IRA options Level 2 approval
- Account B: Cash-Secured Puts only (no spreads, no margin)
- IVR filter stricter: IVR > 60 required (vs 50 for Account A)
- Max position size: 3% per trade (more conservative than Account A)
- Assignment management: automatic CC leg when assigned

## Abort Conditions (any phase)

| Condition | Action |
|-----------|--------|
| Drawdown > 15% | Pause all new entries, review |
| 3 consecutive stop-outs | Pause 5 trading days, reassess signals |
| VIX > 35 sustained 3 days | Reduce to 50% position sizes |
| MCP connectivity failure | Halt all automated execution immediately |
| Account margin call | Emergency close all Account A positions |
