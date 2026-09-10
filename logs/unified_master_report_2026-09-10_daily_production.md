# UNIFIED MASTER REPORT — DAILY (327 POSITIONS)

**Type:** DAILY  |  **Regime:** BEAR_SIDEWAYS  |  **Generated:** September 10, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $7,388,769
- **Total option requirement:** $2,658,071
- **Positions with short puts:** 91
- **Positions with short calls:** 43
- **YTD Net Premium:** $239,895 (live from transactions)
- **Month-to-Date Premium:** $8,695
- **Snapshot currency:** 2026-08-22

### Two Lenses on Monthly Performance

_(both derived from your transaction history)_

#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]

| Account | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | YTD |
|---|---|---|---|---|---|---|---|---|---|---|
| Account A (232) | 10,255 | 12,483 | 23,800 | 20,880 | -1,244 | -2,884 | 20,362 | 50,309 | 7,072 | 141,033 |
| Account B (275) | 31 | 3,322 | 1,546 | 4,894 | 9,709 | 3,948 | 575 | 3,476 | 662 | 28,163 |
| Account C (634) | 31 | 934 | 449 | 1,959 | 4,435 | 1,321 | 2,286 | 6,028 | 499 | 17,942 |
| Fidelity (Rahul) | 17 | 1,824 | 1,231 | 5,580 | 4,947 | 10,629 | 5,151 | 3,339 | 462 | 33,180 |
| Robinhood (Individual) | 0 | 107 | 0 | 0 | 205 | -9 | 0 | 609 | 0 | 912 |
| Robinhood (Traditional IRA) | 0 | 518 | 816 | 6,275 | 2,879 | 2,087 | 517 | 5,573 | 0 | 18,665 |
| **TOTAL** | 10,334 | 19,188 | 27,842 | 39,588 | 20,931 | 15,092 | 28,891 | 69,334 | 8,695 | 239,895 |
| Gross SOLD (STO, opened this month) | 181,334 | 64,446 | 199,571 | 307,592 | 345,076 | 237,655 | 123,038 | 234,490 | 36,604 | 1,729,806 |
| Net REALIZED (FIFO, closed this month) | 10,334 | 19,188 | 27,842 | 39,588 | 20,931 | 15,092 | 28,891 | 69,334 | 8,695 | 239,895 |

Net REALIZED = FIFO-matched close gain/loss, attributed to the month a position CLOSED
(assignment counts as a close). Gross SOLD = premium collected on positions OPENED that
month — a different basis, so Gross minus Net is not a meaningful 'drag' figure; a position
opened this month may not close for months. See scripts/realized_pnl.py for the full method.

#### Lens 2 — Total Account Value (mark-to-market) ≈ Empower 'portfolio value change'

= premium income + unrealized option MTM + equity/assigned-stock MTM + dividends

- Total value = premium income (LENS 1, accurate) + unrealized option MTM + equity MTM + dividends.
- The MTM parts need CURRENT option marks, which live in your POSITION-SNAPSHOT exports (or live quotes) — NOT in transaction files. So this total is NOT computed here (reconstructed marks are stale). Transactions give income; marks give value — you need both, from different exports.
- Use EMPOWER for the authoritative total value. (A prior version of this note claimed a specific $435K/$438K reconciliation — that was against LENS 1's OLD same-month cash-flow total, not the FIFO-realized figure above; re-verify against Empower with today's numbers rather than trusting that stale comparison.)
- To compute a live total HERE: drop fresh position-snapshot exports (they carry current marks).

**Why they diverge month-to-month:**

- Empower's monthly figure is dominated by MARKET moves (unrealized MTM) — e.g. May +$288K was your long book marking UP, not premium income (premium that month was ~$4K).
- LENS 1 books premium when SOLD — front-loaded because you sell long-dated (2027) contracts.
- So: use LENS 1 (income) for the $100K goal; use Empower (Lens 2) for net-worth/market view.
- To make Lens 2 exact here: backfill the ~12 names' transactions + drop fresh position snapshots.

### Per-Account Breakdown

| Account | Balance | % | Notional | Opt Req | Type | Status | Target | Gap |
|---|---|---|---|---|---|---|---|---|
| Account A (232) | $403,000 | 17.2% | $4,955,217 | $891,939 | Margin | 🔴 OVER CAP | $20,030 | ✅ $-6,753 |
| Account B (275) | $261,000 | 11.1% | $362,337 | $291,050 | Cash-Sec | 🔴 COVERAGE GAP | $7,468 | ✅ $-2,518 |
| Account C (634) | $266,000 | 11.4% | $329,781 | $214,950 | Cash-Sec | ⚠️ WATCH | $7,611 | ✅ $-2,567 |
| Fidelity (Rahul) | $498,560 | 21.3% | $689,049 | $624,624 | Cash-Sec | 🔴 COVERAGE GAP | $14,266 | ✅ $-4,809 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $50,536 | $51,237 | Cash-Sec | 🔴 COVERAGE GAP | $1,120 | ✅ $-378 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $169,657 | $161,850 | Cash-Sec | 🔴 COVERAGE GAP | $3,665 | ✅ $-1,235 |
| Vanguard (Rahul) | $320,492 | 13.7% | $505,009 | $422,420 | Cash-Sec | 🔴 COVERAGE GAP | $9,170 | ✅ $-3,092 |
| Robinhood (Individual) | $13,000 | 0.6% | $27,772 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $371 | ✅ $-126 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $299,410 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $6,295 | ✅ $-2,122 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $7,388,769 | $2,658,071 |  |  |  |  |

- **Account A (232):** 173 option positions | Monthly target: $28,615 | Equity: ADBE 400sh, APP 100sh, AXON 100sh, COIN 100sh, CRM 300sh +13 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 19 option positions | Monthly target: $10,669 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 22 option positions | Monthly target: $10,874 | Equity: ABNB 100sh, NKE 100sh, TWLO 324sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ⚠️ WATCH reading above
- **Fidelity (Rahul):** 42 option positions | Monthly target: $20,380 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
  - ⚠️ Balance as of 2026-07-31 (41 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,601 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
  - ⚠️ Balance as of 2026-07-31 (41 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Rollover IRA):** 14 option positions | Monthly target: $5,236
  - ⚠️ Balance as of 2026-07-31 (41 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Vanguard (Rahul):** 27 option positions | Monthly target: $13,101
  - ⚠️ Balance as of 2026-07-31 (41 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $531 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,993
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (41 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (102 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

**Definitions:**

- Notional = Stock price × contracts × 100 (underlying value of options position)
- Opt Req = Strike × contracts × 100 for short puts + current_price × contracts × 100 for naked calls (covered calls = $0)
- Margin accounts (Account A only): real Reg-T buffer — OVER CAP/EMERGENCY means real margin-call risk
- Cash-secured accounts (everyone else): no leverage, no margin call possible — COVERAGE GAP means the requirement exceeds the account's own cash, a liquidity question answered in dollars, not a broker-enforced risk
- Target/Gap columns: same figures previously shown in a separate 'ACCOUNT-LEVEL GAP BREAKDOWN' block below this one

### 60% Close Cost Ratio Framework — Consolidated View

**Framework overview:**

- Base: $100,000/month net = $1.2M/year (at 60% close costs)
- Current Regime: BEAR_SIDEWAYS (applies 70% of base)
- Adjusted Target: $70,000 net per month

**Performance vs. target (YTD cumulative):**

- Target (9 months): $630,000
- Actual YTD: $239,895.0
- Gap to close: $390,105.0 (61.9%)
- Monthly average (YTD): $26,655
- Monthly average needed: $70,000
- Monthly gap: $-23,600

**Position tier distribution → gap closure:**

- Tier 1 (12 positions): $45,600/month (65% of $70,000 target)
- Tier 2 (59 positions): $59,000/month (84% of target)
- Tier 3 (22 positions): $-11,000/month (-16% drag)
- Current total: 93 positions = $93,600/month (134% of target)

**Gap closure path:**

- To hit $70,000 target: Need 0 more Tier 1 positions
- Alternative: Scale existing OR exit 8 worst Tier 3 positions
- Capital required for 0 new positions: $0 (0 × $10K)

**Risk guardrails:**

- Margin account (Account A only): >75% alert, >80% emergency — real broker margin-call risk
- Cash-secured accounts (everyone else): >75% watch, >=100% coverage gap — a liquidity question (does cash cover full assignment), not a leverage/margin-call risk
- Cash floor (all accounts): $75,000 minimum to trade
- Cash emergency: <$50,000 → deploy emergency fund
- Current status: ⚠️ MONITOR


### Supplementary: Production Framework — 60% Close Cost Ratio Targets

- Framework: $100,000/month net = $1.2M/year target (at 60% close costs)
- Regime: BEAR_SIDEWAYS (applies 70% of base)
- Adjusted Target: $175,000 gross / $70,000 net

**Account Targets (Regime-Adjusted)** — complements Section 0's Per-Account
Breakdown 'Target' column: that one is the raw monthly_target; these are the
same targets scaled by the current regime's adjustment factor, gross+net.

| Account | Gross | Net |
|---|---|---|
| Account A (232) | $50,075 | $20,030 |
| Account B (275) | $18,670 | $7,468 |
| Account C (634) | $19,027 | $7,611 |
| Fidelity (Rahul) | $35,665 | $14,266 |
| Fidelity (Rajul — Roth IRA) | $2,800 | $1,120 |
| Fidelity (Rajul — Rollover IRA) | $9,162 | $3,665 |
| Vanguard (Rahul) | $22,925 | $9,170 |
| Robinhood (Individual) | $927 | $371 |
| Robinhood (Traditional IRA) | $15,737 | $6,295 |
| **TOTAL** | $174,988 | $69,996 |


## Section 1: SYSTEM STATUS & PORTFOLIO SNAPSHOT

- **Total open positions:** 327
- **Unique tickers:** 93
- **Active accounts:** 10
- **Data currency:** 2026-09-10
- **Live prices:** 92 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (12 positions): $45,600/month — each contributes $3,800/month (4.2% of $70,000)
- Tier 2 (59 positions): $59,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (22 positions): $-11,000/month — each drags -$500/month (-0.6% of target)
- Portfolio: 93,600/month (134% of target) — Need $-23,600 more

**HIGH (Tier 1: 8-10) conviction** — 12 positions | Total contribution: $45,600/month (65.1% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $314.79 | 9.1 | $3,800 | 5.4% |
| 🟡 | MU | $976.23 | 8.8 | $3,800 | 5.4% |
| 🟢 | APH | $79.57 | 8.5 | $3,800 | 5.4% |
| 🟡 | TSM | $429.82 | 8.5 | $3,800 | 5.4% |
| 🟢 | AMKR | $49.56 | 8.4 | $3,800 | 5.4% |
| 🟢 | GEV | $919.75 | 8.4 | $3,800 | 5.4% |
| 🟢 | VRT | $247.78 | 8.3 | $3,800 | 5.4% |
| 🟡 | JD | $27.01 | 8.2 | $3,800 | 5.4% |
| 🟡 | FSLR | $207.86 | 8.2 | $3,800 | 5.4% |
| 🟡 | DVN | $49.56 | 8.1 | $3,800 | 5.4% |
| 🟡 | RBLX | $45.47 | 8.0 | $3,800 | 5.4% |
| 🟡 | META | $651.00 | 8.0 | $3,800 | 5.4% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 59 positions | Total contribution: $59,000/month (84.3% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | LYFT | $14.97 | 7.8 | $1,000 | 1.4% |
| 🟡 | LITE | $938.55 | 7.8 | $1,000 | 1.4% |
| 🟡 | HUT | $89.65 | 7.8 | $1,000 | 1.4% |
| 🟢 | UNH | $391.82 | 7.7 | $1,000 | 1.4% |
| 🟢 | BWXT | $154.54 | 7.7 | $1,000 | 1.4% |
| 🟡 | SKHY | $190.45 | 7.7 | $1,000 | 1.4% |
| 🟢 | ALAB | $287.47 | 7.6 | $1,000 | 1.4% |
| 🟡 | NVDA | $218.21 | 7.6 | $1,000 | 1.4% |
| 🟢 | GOOGL | $330.95 | 7.6 | $1,000 | 1.4% |
| 🟢 | CAVA | $54.71 | 7.6 | $1,000 | 1.4% |
| 🟡 | LASR | $40.10 | 7.5 | $1,000 | 1.4% |
| 🟢 | NBIS | $227.02 | 7.5 | $1,000 | 1.4% |
| 🟢 | BROS | $43.79 | 7.5 | $1,000 | 1.4% |
| 🟢 | CRWV | $89.73 | 7.5 | $1,000 | 1.4% |
| 🟡 | WMT | $106.00 | 7.5 | $1,000 | 1.4% |
| 🟡 | IONQ | $38.00 | 7.4 | $1,000 | 1.4% |
| 🟢 | RIOT | $21.18 | 7.4 | $1,000 | 1.4% |
| 🟡 | MP | $51.79 | 7.4 | $1,000 | 1.4% |
| 🟢 | KTOS | $47.62 | 7.4 | $1,000 | 1.4% |
| 🟢 | HOOD | $113.88 | 7.3 | $1,000 | 1.4% |
_(put/call detail: Section 6)_
_...and 39 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 22 positions | Total contribution: $-11,000/month (-15.7% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🔴 | OKTA | $173.54 | 5.9 | $-500 | 0.0% |
| 🟡 | ABNB | $169.60 | 5.9 | $-500 | 0.0% |
| 🟡 | COIN | $172.37 | 5.8 | $-500 | 0.0% |
| 🟢 | CRCL | $90.85 | 5.8 | $-500 | 0.0% |
| 🟡 | PANW | $342.63 | 5.8 | $-500 | 0.0% |
| 🟡 | CRM | $244.62 | 5.7 | $-500 | 0.0% |
| 🟡 | REGN | $794.45 | 5.6 | $-500 | 0.0% |
| 🟢 | SBUX | $100.05 | 5.5 | $-500 | 0.0% |
| 🟢 | PFE | $27.50 | 5.4 | $-500 | 0.0% |
| 🟡 | CRWD | $213.62 | 5.4 | $-500 | 0.0% |
| 🟢 | INFY | $10.86 | 5.4 | $-500 | 0.0% |
| 🟢 | DIS | $105.02 | 5.3 | $-500 | 0.0% |
| 🟢 | BA | $206.72 | 5.3 | $-500 | 0.0% |
| 🟢 | BRKB | $0.00 | 5.3 | $-500 | 0.0% |
| 🟢 | SONO | $14.69 | 5.2 | $-500 | 0.0% |
| 🟢 | ETSY | $72.18 | 5.2 | $-500 | 0.0% |
| 🟡 | PYPL | $53.22 | 5.1 | $-500 | 0.0% |
| 🟡 | ADBE | $250.01 | 4.9 | $-500 | 0.0% |
| 🟢 | MMYT | $48.85 | 4.9 | $-500 | 0.0% |
| 🟡 | XYZ | $79.79 | 4.5 | $-500 | 0.0% |
_(put/call detail: Section 6)_
_...and 2 more (see Section 6 for the full sector-grouped list)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 43 positions (46.2%)
- 🟡 YELLOW (Neutral): 48 positions (51.6%)
- 🔴 RED (Extended/Overbought): 2 positions (2.2%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BEAR_SIDEWAYS
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 17.7 — VIX 17.7 sustained < 20
- **S&P 500:** 7599 (50d MA: 7604, 200d MA: 7157)
  - Above 50d MA: False | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 121 | 6.81 | 49.8 | 52.3 | 59 | 🟡 NEUTRAL |
| Healthcare | 18 | 5.83 | 41.3 | 41.8 | 26 | 🟡 NEUTRAL |
| Consumer Cyclical | 33 | 6.31 | 27.7 | 37.8 | 58 | 🟢 BUY (rich premium) |
| Industrials | 35 | 7.17 | 41.1 | 40.4 | 42 | 🟡 NEUTRAL |
| Energy | 3 | 6.7 | 52.5 | 68.7 | 30 | 🟡 NEUTRAL |
| Consumer Defensive | 1 | 7.5 | 57.9 | 19.6 | 95 | 🟢 BUY (rich premium) |
| Utilities | 9 | 6.98 | 59.5 | 14.3 | 19 | 🟡 BUY stock/THIN premium |
| Communication Services | 35 | 7.64 | 58.8 | 25.9 | 58 | 🟢 BUY (rich premium) |
| Defense | 5 | 6.12 | 29.6 | 28.5 | 49 | 🟢 BUY (rich premium) |
| Brand-Quality (Non-AI) | 20 | 6.57 | 46.0 | 42.1 | 32 | 🟡 NEUTRAL |
| Basic Materials | 11 | 6.83 | 40.8 | 30.5 | 25 | 🟡 NEUTRAL |
| Financial Services | 35 | 6.13 | 47.5 | 37.1 | 49 | 🟡 NEUTRAL |
| Unknown | 1 | 5.3 | 50.0 | 50.0 | 0 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Consumer Cyclical:** Conv 6.3/10, RSI 27.7, 52W %ile 37.8 — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling)
- ✓ **Communication Services:** Conv 7.6/10, RSI 58.8, 52W %ile 25.9 — 🟢 BUY — High conviction + rich premium (avg IVR 58)
- ✓ **Defense:** Conv 6.1/10, RSI 29.6, 52W %ile 28.5 — 🟢 BUY — Oversold + rich premium (avg IVR 49, good for selling)
- ✓ **Utilities:** Conv 7.0/10, RSI 59.5, 52W %ile 14.3 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 19 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Defensive:** Conv 7.5/10, RSI 57.9, 52W %ile 19.6 — 🟢 BUY — Oversold + rich premium (avg IVR 95, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.8/10, RSI 49.8, 52W %ile 52.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Basic Materials:** Conv 6.8/10, RSI 40.8, 52W %ile 30.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Brand-Quality (Non-AI):** Conv 6.6/10, RSI 46.0, 52W %ile 42.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.2/10, RSI 41.1, 52W %ile 40.4 — 🟡 MONITOR — Neutral positioning
- ◇ **Unknown:** Conv 5.3/10, RSI 50.0, 52W %ile 50.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.1/10, RSI 47.5, 52W %ile 37.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 5.8/10, RSI 41.3, 52W %ile 41.8 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 6.7/10, RSI 52.5, 52W %ile 68.7 — 🟡 MONITOR — Neutral positioning


## Section 5: POSITION DISTRIBUTION BY ACCOUNT

- **Account A (232):** 173 positions (52.9%) `██████████████████████████`
- **Fidelity (Rahul):** 42 positions (12.8%) `██████`
- **Vanguard (Rahul):** 27 positions (8.3%) `████`
- **Account C (634):** 22 positions (6.7%) `███`
- **Account B (275):** 19 positions (5.8%) `██`
- **Robinhood (Traditional IRA):** 18 positions (5.5%) `██`
- **Fidelity (Rajul — Rollover IRA):** 14 positions (4.3%) `██`
- **Fidelity (Rajul — Roth IRA):** 8 positions (2.4%) `█`
- **Robinhood (Individual):** 4 positions (1.2%) ``
- **Fidelity 401K (Rahul):** 0 positions (0.0%) ``


## Section 6: POSITION HEAT MATRIX BY SECTOR — Sector -> Symbol, Put/Call/Total Value, Heat, Suggestion


### Technology (34 positions, $2,763,681) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $375,420 | $0 | $375,420 | 🟡 | 7.8 | 🟡 MONITOR |
| TSM | $214,908 | $42,982 | $257,889 | 🟡 | 8.5 | 🟡 MONITOR |
| CRM | $73,386 | $171,234 | $244,620 | 🟡 | 5.7 | 🟡 MONITOR |
| ALAB | $172,482 | $57,494 | $229,976 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ADBE | $75,003 | $150,006 | $225,009 | 🟡 | 4.9 | 🟡 MONITOR |
| MU | $195,247 | $0 | $195,247 | 🟡 | 8.8 | 🟡 MONITOR |
| OKTA | $34,708 | $121,478 | $156,186 | 🔴 | 5.9 | 🔴 TRIM CALL (delta/assignment risk); 🟢 HOLD PUT (near max profit, unaffected — a short call gains protection in a decline, don't close it purely on crash fears) |
| IBM | $94,796 | $23,699 | $118,495 | 🟡 | 6.5 | 🟡 MONITOR |
| PANW | $102,789 | $0 | $102,789 | 🟡 | 5.8 | 🟡 MONITOR |
| MSFT | $49,268 | $49,268 | $98,536 | 🟡 | 7.0 | 🟡 MONITOR |
| TWLO | $23,283 | $69,849 | $93,132 | 🟡 | 6.6 | 🟡 MONITOR |
| NVDA | $87,282 | $0 | $87,282 | 🟡 | 7.6 | 🟡 MONITOR |
| CRWD | $64,088 | $21,362 | $85,450 | 🟡 | 5.4 | 🟡 MONITOR |
| ZS | $50,019 | $16,673 | $66,692 | 🟡 | 7.0 | 🟡 MONITOR |
| APH | $47,742 | $15,914 | $63,656 | 🟢 | 8.5 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| SHOP | $50,602 | $0 | $50,602 | 🟡 | 6.5 | 🟡 MONITOR |
| XYZ | $31,916 | $15,958 | $47,874 | 🟡 | 4.5 | 🟡 MONITOR |
| UBER | $42,924 | $0 | $42,924 | 🟡 | 7.2 | 🟡 MONITOR |
| FSLR | $41,572 | $0 | $41,572 | 🟡 | 8.2 | 🟡 MONITOR |
| SKHY | $38,090 | $0 | $38,090 | 🟡 | 7.7 | 🟡 MONITOR |
| IONQ | $19,000 | $7,600 | $26,600 | 🟡 | 7.4 | 🟡 MONITOR |
| AMKR | $24,780 | $0 | $24,780 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBRK | $18,187 | $0 | $18,187 | 🟡 | 6.7 | 🟡 MONITOR |
| PLTR | $16,676 | $0 | $16,676 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ASTS | $12,393 | $0 | $12,393 | 🟡 | 6.9 | 🟡 MONITOR |
| LYFT | $1,497 | $7,485 | $8,982 | 🟡 | 7.8 | 🟡 MONITOR |
| CRWV | $8,973 | $0 | $8,973 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LASR | $8,020 | $0 | $8,020 | 🟡 | 7.5 | 🟡 MONITOR |
| CIFR | $6,374 | $0 | $6,374 | 🟡 | 6.7 | 🟡 MONITOR |
| SONO | $0 | $5,874 | $5,874 | 🟢 | 5.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| INFY | $1,086 | $1,086 | $2,173 | 🟢 | 5.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QBTS | $1,682 | $0 | $1,682 | 🟡 | 6.7 | 🟡 MONITOR |
| QUBT | $791 | $0 | $791 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ONDS | $735 | $0 | $735 | 🟡 | 7.0 | 🟡 MONITOR |

### Industrials (9 positions, $1,254,196) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $145,927 | $389,140 | $535,067 | 🟡 | 6.5 | 🟡 MONITOR |
| GEV | $275,925 | $91,975 | $367,900 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| BE | $157,260 | $52,420 | $209,680 | 🔴 | 7.1 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| VRT | $49,556 | $0 | $49,556 | 🟢 | 8.3 | 🟢 ATTRACTIVE — let run |
| RKLB | $37,827 | $0 | $37,827 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |
| BWXT | $30,908 | $0 | $30,908 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| SPCX | $15,074 | $0 | $15,074 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |
| KTOS | $4,762 | $0 | $4,762 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| PL | $3,422 | $0 | $3,422 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |

### Communication Services (7 positions, $966,522) — 🟢 BUY — High conviction + rich premium (avg IVR 58) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $260,400 | $65,100 | $325,500 | 🟡 | 8.0 | 🟡 MONITOR |
| APP | $188,874 | $62,958 | $251,832 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $121,840 | $45,690 | $167,530 | 🟡 | 6.4 | 🟡 MONITOR |
| GOOGL | $99,285 | $0 | $99,285 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBLX | $31,826 | $13,640 | $45,465 | 🟡 | 8.0 | 🟡 MONITOR |
| NBIS | $45,404 | $0 | $45,404 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| DIS | $21,004 | $10,502 | $31,506 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Financial Services (8 positions, $628,345) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| COIN | $68,948 | $137,896 | $206,844 | 🟡 | 5.8 | 🟡 MONITOR |
| MA | $169,704 | $0 | $169,704 | 🟡 | 6.9 | 🟡 MONITOR |
| PYPL | $31,931 | $63,862 | $95,794 | 🟡 | 5.1 | 🟡 MONITOR |
| JPM | $70,546 | $0 | $70,546 | 🟡 | 7.0 | 🟡 MONITOR |
| CRCL | $36,341 | $18,171 | $54,512 | 🟢 | 5.8 | 🟢 ATTRACTIVE — let run |
| HOOD | $11,388 | $0 | $11,388 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run |
| RIOT | $8,474 | $2,118 | $10,592 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| HUT | $8,965 | $0 | $8,965 | 🟡 | 7.8 | 🟡 MONITOR |

### Healthcare (7 positions, $517,485) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ISRG | $144,554 | $0 | $144,554 | 🟡 | 7.0 | 🟡 MONITOR |
| UNH | $78,363 | $39,182 | $117,545 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| LLY | $112,680 | $0 | $112,680 | 🟡 | 7.0 | 🟡 MONITOR |
| REGN | $79,445 | $0 | $79,445 | 🟡 | 5.6 | 🟡 MONITOR |
| NVO | $22,202 | $8,881 | $31,083 | 🟢 | 3.7 | 🟢 ATTRACTIVE — let run |
| ZBH | $9,215 | $9,215 | $18,430 | 🟡 | 6.8 | 🟡 MONITOR |
| PFE | $13,748 | $0 | $13,748 | 🟢 | 5.4 | 🟢 ATTRACTIVE — let run |

### Consumer Cyclical (12 positions, $447,699) — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $112,986 | $28,246 | $141,232 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| AMZN | $50,516 | $25,258 | $75,774 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ABNB | $16,960 | $50,879 | $67,838 | 🟡 | 5.9 | 🟡 MONITOR |
| BABA | $54,310 | $0 | $54,310 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TSLA | $36,639 | $0 | $36,639 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MMYT | $19,542 | $4,885 | $24,427 | 🟢 | 4.9 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| JD | $8,104 | $8,104 | $16,209 | 🟡 | 8.2 | 🟡 MONITOR |
| ETSY | $7,218 | $7,218 | $14,435 | 🟢 | 5.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CAVA | $5,471 | $0 | $5,471 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| DKNG | $4,743 | $0 | $4,743 | 🟡 | 6.4 | 🟡 MONITOR |
| BROS | $4,379 | $0 | $4,379 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CCL | $2,242 | $0 | $2,242 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (4 positions, $359,574) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ULTA | $108,228 | $54,114 | $162,342 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run |
| ANET | $94,600 | $56,760 | $151,360 | 🟡 | 7.2 | 🟡 MONITOR |
| NKE | $0 | $25,861 | $25,861 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run |
| SBUX | $20,010 | $0 | $20,010 | 🟢 | 5.5 | 🟢 ATTRACTIVE — let run |

### Defense (3 positions, $198,580) — 🟢 BUY — Oversold + rich premium (avg IVR 49, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| NOC | $104,212 | $0 | $104,212 | 🟡 | 6.6 | 🟡 MONITOR |
| LMT | $53,024 | $0 | $53,024 | 🟡 | 6.8 | 🟡 MONITOR |
| BA | $41,344 | $0 | $41,344 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

### Utilities (3 positions, $114,961) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 19 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $59,320 | $14,830 | $74,150 | 🟡 | 7.0 | 🟡 MONITOR |
| CEG | $28,661 | $0 | $28,661 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |
| OKLO | $12,150 | $0 | $12,150 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |

### Basic Materials (2 positions, $107,399) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $74,298 | $12,383 | $86,681 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MP | $15,538 | $5,179 | $20,718 | 🟡 | 7.4 | 🟡 MONITOR |

### Energy (2 positions, $19,727) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| DVN | $9,912 | $0 | $9,912 | 🟡 | 8.1 | 🟡 MONITOR |
| CCJ | $9,815 | $0 | $9,815 | 🟢 | 3.9 | 🟢 ATTRACTIVE — let run |

### Consumer Defensive (1 positions, $10,600) — 🟢 BUY — Oversold + rich premium (avg IVR 95, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,600 | $0 | $10,600 | 🟡 | 7.5 | 🟡 MONITOR |

### Unknown (1 positions, $0) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| BRKB | $0 | $0 | $0 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 8.6% ($638,749)
- 🟡 MONITOR: 60.6% ($4,475,003)
- 🟢 HEALTHY: 30.8% ($2,275,017)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟡 YELLOW

**Summary:** ⚠️ CAUTION — 1 indicators turning yellow. Watch for deterioration.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| 🔴 | BREADTH | 47.43589743589743 | RED | 60% (caution), 50% (alert) |
| ⚠️ | AD_RATIO | 0.8518518518518519 | YELLOW | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 271 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.40% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟡 30-day crash probability: 34.0% — Action: 🟡 CAUTION: Reduce overbought positions by 20-25%
- 🟠 60-day crash probability: 57.7%
- 🔴 90-day crash probability: 81.4%
- 📌 Primary risk factor: BREADTH critical

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▄▃`
  - 2026-09-01: 48% → 2026-09-10: 34% (falling, -14pp)

**Historical magnitude reference** (real, verified past events — NOT a prediction of this specific reading's outcome):

| Event | Magnitude |
|---|---|
| 2000 dot-com | -17.2% initial leg / -49.1% full bear |
| 2007 GFC | -56.8% full bear, VIX peaked 80.9 |
| 2013 taper tantrum | -5.8% / 34 days |
| 2021-22 growth derate | -25.4% / 282 days |
| 2023 SVB | -4.8% / 7 days (resolved fast via FDIC backstop) |

See logs/circular_financing_playbook.html for the full framework this session's AI-capex risk analysis is built on.

**Sector Sensitivity to Primary Risk Driver** (BREADTH):

- 🔴 HIGH exposure: Technology, Consumer Cyclical, Communication Services, Basic Materials
- 🟢 LOW exposure: Utilities, Healthcare, Consumer Defensive, Energy, Defense

New entries in HIGH-exposure sectors compound the exact risk this driver is flagging, even if the individual name looks statistically oversold — see the opportunity list in Section 7 for a per-name check against this.

**Recommended Actions:**

- ⚠️ Stage 1 Rotation (6-8 week advance warning)
- Close 30% of overbought positions (RSI > 75)
- Reduce naked call exposure by 20%
- Shift new entries to DEFENSIVE sectors
- Keep short puts (they profit on dips)

**Rotation Playbook:**

```
YELLOW FLAG — Stage 1 Rotation (Crash prob: 34% in 30d | 58% in 60d)
  PROBABILITY-DRIVEN ACTIONS:
    • Position reduction: Cut 20% of notional exposure
    • Focus: Close low-conviction positions first (Conv <6/10)
    • New entries: PAUSE or reduce to 25% of normal size

  Account A Actions:
    1. Close CRWD, LLY, OKTA (low conviction + overbought) at 40-50%
    2. Reduce AXON, NFLX from max to 75% of current size (20% total)
    3. Buy protective puts on remaining naked calls (20% of notional)
    4. Shift new entries: Only DEFENSIVE (Healthcare, Utilities, Staples)
    5. Increase cash from 10% → 20%

  Account B Actions:
    1. Trim COIN, HOOD CSPs by 20%
    2. Add healthcare/staples CSPs if opportunity
    3. Build cash reserve to 25-30%

  DECISION GATE:
    • IF prob increases to >50% in next 3 days → Move to Stage 2
    • IF prob decreases to <20% → Resume normal sizing
```

### AI Capex Risk Tracker (Circular Financing Playbook — the scriptable half of the same macro picture above)

- **Technology concentration:** 37.4% of notional (121 positions, $2,763,681)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $817,319 live — 72% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $321,545 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $138,986 across NBIS, CRWV, RKLB, OKLO, SPCX, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-08 (2 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.

Underperformance proxy: no tracked name diverging >10pp from SPX over 7 days.


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | CRM | C | 175.0 | 8 | 98% | $17,500 |  |
| Account C (634) | PL | P | 32.0 | 36 | 95% | $3,200 |  |
| Account A (232) | COIN | P | 250.0 | 8 | 95% | $25,000 |  |
| Account A (232) | AXON | P | 570.0 | 8 | 93% | $57,000 |  |
| Account A (232) | CRCL | P | 105.0 | 8 | 91% | $10,500 |  |
| Account A (232) | IBM | P | 270.0 | 36 | 88% | $27,000 |  |
| Account A (232) | CRM | C | 185.0 | 71 | 85% | $18,500 |  |
| Account B (275) | CRM | C | 175.0 | 99 | 83% | $17,500 |  |
| Account C (634) | ABNB | C | 145.0 | 36 | 82% | $14,500 |  |
| Account A (232) | AXON | C | 450.0 | 8 | 80% | $45,000 |  |
| Account A (232) | NVO | P | 50.0 | 99 | 78% | $5,000 |  |
| Account A (232) | OKTA | C | 140.0 | 71 | 76% | $14,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | PYPL | C | 42.5 | 71 | 75% | $21,250 |  |
| Account A (232) | ADBE | C | 230.0 | 8 | 74% | $23,000 |  |
| Account A (232) | MP | P | 60.0 | 99 | 73% | $6,000 |  |
| Account A (232) | RBLX | C | 40.0 | 36 | 73% | $8,000 |  |
| Account A (232) | AXON | P | 560.0 | 99 | 72% | $56,000 |  |
| Account A (232) | PYPL | C | 45.0 | 71 | 72% | $9,000 |  |
| Account A (232) | XYZ | C | 65.0 | 99 | 71% | $13,000 |  |
| Account A (232) | ETSY | C | 60.0 | 99 | 70% | $6,000 |  |
| Account A (232) | PYPL | C | 45.0 | 99 | 70% | $13,500 |  |
| Account A (232) | AXON | P | 540.0 | 99 | 68% | $54,000 |  |
| Account A (232) | CRM | C | 210.0 | 99 | 67% | $21,000 |  |
| Account A (232) | ZS | P | 180.0 | 99 | 66% | $18,000 |  |
| Account A (232) | DIS | P | 110.0 | 99 | 65% | $22,000 |  |
_...and 61 more within 120 DTE (not shown)_

- **Worst case (all shown):** $2,164,450 across 86 positions
- **Realistic (>=30% prob):** $1,503,450 across 65 positions
- **Likely (>=50% prob):** $831,950 across 40 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 1

- OKTA C 140.0 (Account A (232)) — 76% probability, RED heat


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ✅ Last scan: 2026-09-01 (9 days ago)
- **CRM:** No new low-strike calls this week -- let existing ITM calls execute as planned.
- **MACRO:** No Tier CR trigger this week -- confirmation, not escalation.
- **MU:** Flag for next quarterly bucket review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET candidate) -- not an immediate reclass off one data point.


## Section 6.9: ACTIVE DECISION TRACKER


**⏳ axon_sept18_roll_450c** — OPEN

Roll the AXON $450C (Sept 18 2026 expiry) out to a January 2027 call (~$560-580 strike, AXON's own missing rung in its Sept/Dec/March ladder) before Sept 18. Keep the $470C to settle against the 100 owned AXON shares as a clean covered assignment. Only 100 AXON shares exist to cover 2 ITM Sept-18 calls; rolling one removes the naked/short-stock risk that would otherwise be forced at expiry.

**⏳ pypl_naked_calls_cleanup** — OPEN

5 naked short call contracts on PYPL (0 shares owned), all ITM as of 2026-09-10: $45C x3 (Dec 18 2026), $47.5C x2 (Jan 15 2027). No shares exist to cover any of them. Lower urgency than the AXON Sept-18 pair (91-119 DTE at time of writing gives runway) but needs a roll-up/out or close before expiry approaches -- same structural risk as AXON, just further out.
  - Live check: 12 naked ITM contract(s) remaining (target: 0)

**⏳ crcl_naked_call_dec** — OPEN

1 naked short call on CRCL (0 shares owned), ITM as of 2026-09-10: $90C (Dec 18 2026). Smaller version of the same AXON/PYPL issue.
  - Live check: 2 naked ITM contract(s) remaining (target: 0)

**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 127.41987235532488
  - Live: macro_risk_level = YELLOW

**⏳ be_puts_reduction** — OPEN

Reduce BE put exposure to zero over the next ~10 days (target: 2026-09-20) by closing/rolling out of all 6 open BE put legs across every account. BE is RED heat, RSI 77-81 (overbought/extended), and is the most widely-held name in the book -- also carries a naked short-call pair against it in Account A/Fidelity Rahul (no BE shares owned anywhere). Baseline as of 2026-09-10: Account A $170P (Jan 15 2027) x2 [Jan+Feb], Account B $180P (Feb 19 2027), Fidelity (Rahul) $190P (Jan 15 2027), Fidelity (Rajul - Rollover IRA) $200P (Jun 17 2027), Robinhood (Traditional) $180P (Jun 17 2027). Trader confirmed 2026-09-10 this should cover ALL open BE puts (not just the near-dated ones) -- an initial "Dec 2026 and before" framing didn't match any real BE put, since the earliest is Jan 15 2027.
KNOWN GAP: the automated check only sees 5 of these 6 legs -- the Robinhood (Traditional) $180P (Jun 17 2027) has an option-type parsing gap in that account's transaction reconstruction and won't count toward the live total below. This entry will show RESOLVED once the other 5 close even if that 6th one is still open -- manually confirm the Robinhood leg separately before treating BE exposure as fully closed.
  - Live check: 5 leg(s) open now (baseline was 6), target: 0



## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-23,600 to $-23,600 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (1 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $1,000/month contribution from MODERATE conviction positions
- Names: OKTA (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (43 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 43 healthy positions contribute $43,000/month baseline (expected)
- ✅ 43 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (5 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 5 Tier 1 entries = $19,000/month; closes gap from $-23,600 to $-42,600 (27.1% closure)
  - APP: Conv 9.1/10 | RSI 53.6 | Value $251,832 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - APH: Conv 8.5/10 | RSI 58.5 | Value $63,656 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 40.6 | Value $367,900
  - AMKR: Conv 8.4/10 | RSI 47.2 | Value $24,780 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it
  - VRT: Conv 8.3/10 | RSI 42.7 | Value $49,556

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 93
- 🔴 Critical actions: 0 closes + 1 monitors
- 🟡 Yellow cautions: 46
- 🟢 Green healthy: 43
- 📊 Market regime: BEAR_SIDEWAYS

**Gap Closure Summary:**

- Current gap: $-23,600 (-33.7% below target)
- After closes: $-23,600 (saves ~0.0%)
- After new Tier 1 entries: $-42,600 (27.1% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-10 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_