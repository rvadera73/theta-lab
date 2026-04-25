# System Architecture

## Signal Flow

```
Daily Scan (pre-market)
  └── IV Rank screener → filter universe by IVR threshold
  └── Regime filter → VIX gate (pause/reduce/normal)
  └── Earnings calendar → apply blackout windows

Strategy Router
  ├── Account A (Margin)
  │   ├── High IVR + Neutral bias  → Iron Condor / Short Strangle
  │   ├── High IVR + Directional   → Vertical Spread (credit)
  │   └── Low IVR + Trend signal   → Debit Spread
  └── Account B (IRA, Phase 4 only)
      └── Wheel: CSP (high IVR entry) → assignment → CC

Risk Engine (pre-execution, every trade)
  ├── Position size calculation (2-5% of account)
  ├── Portfolio Greeks check (delta, vega caps)
  ├── Liquidity validation (OI, bid-ask spread)
  └── dry_run() via open-stocks-mcp → confirm fills before submit

Execution
  ├── Limit order at mid-price
  ├── 2-step price improvement (walk 1 tick toward market)
  └── Log to paper_trades.log (Phase 1) or live_trades.log (Phase 2+)

Monitoring
  ├── Daily P&L vs 20% annualized target
  ├── Exit trigger scan (profit target, stop, DTE gate)
  └── Weekly performance report
```

## Data Sources

| Data Type | Source | Notes |
|-----------|--------|-------|
| Quotes + Options chains | open-stocks-mcp | Confirm real-time vs delayed |
| IV Rank / IV Percentile | Computed from 52-week high/low IV | Or Tradier if MCP insufficient |
| Earnings calendar | open-stocks-mcp or manual | Earnings blackout enforcement |
| VIX | open-stocks-mcp | Regime gating |

## Key Design Decisions

1. **dry_run() is mandatory** before every live order — no exceptions, hardcoded in skill
2. **Account B automation gated to Day 91** — IRA options level must be confirmed first
3. **Greeks limits are portfolio-level**, not just per-position — prevents correlated blowup
4. **50% profit target** is the standard for short premium; do not hold to expiration
5. **21 DTE close rule** — short gamma risk accelerates near expiration
