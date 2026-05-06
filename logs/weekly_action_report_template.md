# THETA-LAB Weekly Action Report — DYNAMIC SCREENING TEMPLATE
**Generated from live screens (no hardcoding)**

---

## STEP 1: Market Regime Check
```
CALL: check_market_regime()
OUTPUT:
- Current regime: [BEAR_SIDEWAYS | TRANSITIONING | CAUTIOUS_BULL | BULL]
- New entries allowed: [YES | NO]
- Profit-take threshold: [40-60% | 50-60% | 70%]
- VIX level: [current]
- S&P 500 vs 50/200-day MA: [above/below]
```

---

## STEP 2: Account A — Live Position Scans

### 2A: Position Heat (Red/Yellow/Green)
```
CALL: scan_position_heat(account="A")
OUTPUT:
🔴 RED POSITIONS (≤21 DTE or deeply ITM, cost-to-close > 2x premium):
  [Symbol][Expiry][Strike][Days to Exp][Distance to Strike][Recommended Action]

🟡 YELLOW POSITIONS (Approaching 21 DTE or moderately ITM):
  [Symbol][Expiry][Strike][Days to Exp][Distance to Strike][Recommended Action]

🟢 GREEN POSITIONS (Healthy, time working):
  [Symbol][Expiry][Strike][Days to Exp][Distance to Strike][Status]
```

### 2B: Roll Candidates (≤21 DTE, ITM, or mark > 2x premium)
```
CALL: scan_roll_candidates(account="A")
OUTPUT:
PRIORITIZED BY URGENCY:
  1. [Symbol][Current Strike][Proposed Strike][Proposed DTE][Est. Net Credit]
  2. [Symbol][Current Strike][Proposed Strike][Proposed DTE][Est. Net Credit]
  ...

DECISION MATRIX:
  - If DTE > 45 and thesis intact → HOLD (time still working)
  - If DTE ≤ 21 → ROLL (lower strike + extend DTE for net credit)
  - If thesis broken → CLOSE (cut loss)
```

### 2C: Profit-Take Candidates (At 40-60% bear / 70% bull threshold)
```
CALL: scan_profit_take_candidates(account="A")
OUTPUT:
CLOSE CANDIDATES (Hit profit target):
  1. [Symbol][Expiry][Current Premium Captured %][Est. Close Price]
  2. [Symbol][Expiry][Current Premium Captured %][Est. Close Price]
  ...

ACTION: Close when ≥ threshold; redeploy capital to new entries or rolls
```

### 2D: New Entry Opportunities (If regime allows)
```
IF regime = CAUTIOUS_BULL or BULL:
  CALL: screen_new_entries(account="A", tier=1)
  OUTPUT:
  Top candidates by IV Rank (must be ≥ 40):
    1. [Symbol][Sector][Current Price][IV Rank][Recommended Trade]
    2. [Symbol][Sector][Current Price][IV Rank][Recommended Trade]
    ...
  
  CALL: get_iv_rank(symbols=[candidates])
  OUTPUT:
    [Symbol]: IVR [value] | IV Percentile [value] | Status [Entry OK / IVR too low]

ELSE IF regime = BEAR_SIDEWAYS:
  NO NEW ENTRIES — Focus on managing existing positions
```

---

## STEP 3: Account B (IRA Wheel) — Live Scans

### 3A: Wheel Status
```
CALL: get_live_positions(account="B")
OUTPUT:
OPEN CSP POSITIONS:
  [Symbol][Strike][Expiry][DTE][Distance to Strike][Status]
  
ASSIGNED EQUITY (if any):
  [Symbol][Shares][Cost Basis][Current Price][Unrealized P&L][CC Strike Sold / Plan]

ACTION:
  - CSP at 21 DTE or ITM → Roll down/out or close
  - Assigned shares → Sell CC immediately to reduce cost basis
```

### 3B: Position Heat (Account B only)
```
CALL: scan_position_heat(account="B")
OUTPUT:
[Same RED/YELLOW/GREEN as Account A, but for IRA wheel]
```

---

## STEP 4: Account C — Clean Status Check

```
CALL: get_live_positions(account="C")
OUTPUT:
Status: [No positions | Minimal positions | On track]
Action: [Monitor | No action needed]
```

---

## STEP 5: India (ICICI Direct) — Weekly Action

```
CALL: generate_india_weekly_report()
OUTPUT:
Market Regime: [BEAR_SIDEWAYS | BULL]
Nifty 50 vs MAs: [Above/Below]

PHASE 1 EXITS (Immediate):
  [Symbol][Current Price][Exit Target][Reasoning]

PHASE 2 EXITS (On Bounce):
  [Symbol][Current Price][Exit Target][Reasoning]

CORE HOLDS:
  [Symbol][Thesis][No action]
```

---

## STEP 6: Consolidated Weekly Action Plan

### Format: Dynamic Output from Scans
```
🔴 RED POSITIONS (Action Required This Week):
  From scan_position_heat() + scan_roll_candidates()
  
🟡 YELLOW POSITIONS (Monitor / Prepare to Roll):
  From scan_position_heat()
  
🟢 GREEN POSITIONS (Let Decay Work):
  From scan_position_heat()
  
💰 PROFIT-TAKE CANDIDATES (Close These):
  From scan_profit_take_candidates()
  
🆕 NEW ENTRIES (If Regime Allows):
  From screen_new_entries() + get_iv_rank()
  
🇮🇳 INDIA ACTIONS:
  From generate_india_weekly_report()
```

---

## EXECUTION CHECKLIST (Auto-Generated)
```
For each RED position:
  ☐ Run dry_run_order() before live execution
  ☐ Confirm margin impact
  ☐ Execute trade

For each YELLOW position:
  ☐ Monitor until ≤21 DTE
  ☐ Prepare roll parameters
  ☐ Execute when ready

For each profit-take candidate:
  ☐ Check bid/ask spread
  ☐ Close at market or limit
  ☐ Redeploy proceeds

For each new entry candidate:
  ☐ Verify IVR ≥ 40
  ☐ Verify regime gate (CAUTIOUS_BULL+ for new entries)
  ☐ Calculate strike (delta 0.20 for puts)
  ☐ Run dry_run_order()
  ☐ Execute if approved
```

---

## DATA SOURCES (Not Hardcoded)
- **scan_position_heat()** — Live position risk
- **scan_roll_candidates()** — Live roll triggers
- **scan_profit_take_candidates()** — Live profit threshold
- **check_market_regime()** — Live regime + entry gate
- **screen_new_entries()** — Live screened candidates
- **get_iv_rank()** — Live IV validation
- **generate_india_weekly_report()** — Live India action
- **dry_run_order()** — Pre-execution validation

---

**Weekly Report Generated: [DATETIME]**  
**Powered by: Theta-Lab live screening (zero hardcoding)**
