# UNIFIED MASTER REPORT — DAILY (327 POSITIONS)

**Type:** DAILY  |  **Regime:** BEAR_SIDEWAYS  |  **Generated:** September 10, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $7,389,297
- **Total option requirement:** $2,659,365
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
| Account A (232) | $403,000 | 17.2% | $4,960,523 | $892,894 | Margin | 🔴 OVER CAP | $20,030 | ✅ $-5,952 |
| Account B (275) | $261,000 | 11.1% | $359,056 | $291,050 | Cash-Sec | 🔴 COVERAGE GAP | $7,468 | ✅ $-2,219 |
| Account C (634) | $266,000 | 11.4% | $328,694 | $214,950 | Cash-Sec | ⚠️ WATCH | $7,611 | ✅ $-2,262 |
| Fidelity (Rahul) | $498,560 | 21.3% | $686,933 | $624,839 | Cash-Sec | 🔴 COVERAGE GAP | $14,266 | ✅ $-4,239 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $50,585 | $51,173 | Cash-Sec | 🔴 COVERAGE GAP | $1,120 | ✅ $-333 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $168,866 | $161,850 | Cash-Sec | 🔴 COVERAGE GAP | $3,665 | ✅ $-1,089 |
| Vanguard (Rahul) | $320,492 | 13.7% | $510,952 | $422,609 | Cash-Sec | 🔴 COVERAGE GAP | $9,170 | ✅ $-2,725 |
| Robinhood (Individual) | $13,000 | 0.6% | $27,506 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $371 | ✅ $-111 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $296,181 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $6,295 | ✅ $-1,870 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $7,389,297 | $2,659,365 |  |  |  |  |

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
- Monthly gap: $-20,800

**Position tier distribution → gap closure:**

- Tier 1 (11 positions): $41,800/month (60% of $70,000 target)
- Tier 2 (60 positions): $60,000/month (86% of target)
- Tier 3 (22 positions): $-11,000/month (-16% drag)
- Current total: 93 positions = $90,800/month (130% of target)

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

- Tier 1 (11 positions): $41,800/month — each contributes $3,800/month (4.2% of $70,000)
- Tier 2 (60 positions): $60,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (22 positions): $-11,000/month — each drags -$500/month (-0.6% of target)
- Portfolio: 90,800/month (130% of target) — Need $-20,800 more

**HIGH (Tier 1: 8-10) conviction** — 11 positions | Total contribution: $41,800/month (59.7% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $308.98 | 9.1 | $3,800 | 5.4% |
| 🟡 | MU | $987.76 | 8.8 | $3,800 | 5.4% |
| 🟢 | APH | $79.82 | 8.5 | $3,800 | 5.4% |
| 🟡 | TSM | $425.18 | 8.5 | $3,800 | 5.4% |
| 🟢 | AMKR | $49.08 | 8.4 | $3,800 | 5.4% |
| 🟢 | GEV | $930.71 | 8.4 | $3,800 | 5.4% |
| 🟢 | VRT | $245.68 | 8.3 | $3,800 | 5.4% |
| 🟡 | JD | $26.92 | 8.2 | $3,800 | 5.4% |
| 🟡 | SKHY | $188.44 | 8.2 | $3,800 | 5.4% |
| 🟡 | RBLX | $44.60 | 8.0 | $3,800 | 5.4% |
| 🟡 | META | $644.45 | 8.0 | $3,800 | 5.4% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 60 positions | Total contribution: $60,000/month (85.7% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | LYFT | $14.69 | 7.8 | $1,000 | 1.4% |
| 🟡 | HUT | $89.64 | 7.8 | $1,000 | 1.4% |
| 🟢 | UNH | $397.21 | 7.7 | $1,000 | 1.4% |
| 🟢 | BWXT | $155.61 | 7.7 | $1,000 | 1.4% |
| 🟢 | ALAB | $282.00 | 7.6 | $1,000 | 1.4% |
| 🟡 | NVDA | $217.84 | 7.6 | $1,000 | 1.4% |
| 🟢 | CAVA | $55.62 | 7.6 | $1,000 | 1.4% |
| 🟡 | SPCX | $153.30 | 7.6 | $1,000 | 1.4% |
| 🟡 | UBER | $69.88 | 7.5 | $1,000 | 1.4% |
| 🟡 | LASR | $39.97 | 7.5 | $1,000 | 1.4% |
| 🟢 | NBIS | $230.52 | 7.5 | $1,000 | 1.4% |
| 🟢 | BROS | $44.48 | 7.5 | $1,000 | 1.4% |
| 🟢 | CRWV | $89.26 | 7.5 | $1,000 | 1.4% |
| 🟡 | WMT | $106.45 | 7.5 | $1,000 | 1.4% |
| 🟡 | IONQ | $37.27 | 7.4 | $1,000 | 1.4% |
| 🟢 | RIOT | $20.95 | 7.4 | $1,000 | 1.4% |
| 🟡 | LITE | $970.99 | 7.4 | $1,000 | 1.4% |
| 🟡 | MP | $52.90 | 7.4 | $1,000 | 1.4% |
| 🟡 | DVN | $49.11 | 7.4 | $1,000 | 1.4% |
| 🟢 | KTOS | $46.55 | 7.4 | $1,000 | 1.4% |
_(put/call detail: Section 6)_
_...and 40 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 22 positions | Total contribution: $-11,000/month (-15.7% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🔴 | OKTA | $176.42 | 5.9 | $-500 | 0.0% |
| 🟢 | ABNB | $168.05 | 5.9 | $-500 | 0.0% |
| 🟢 | ZBH | $92.78 | 5.9 | $-500 | 0.0% |
| 🟡 | COIN | $171.73 | 5.8 | $-500 | 0.0% |
| 🟢 | CRCL | $91.34 | 5.8 | $-500 | 0.0% |
| 🟡 | CRWD | $211.33 | 5.8 | $-500 | 0.0% |
| 🟡 | PANW | $340.73 | 5.8 | $-500 | 0.0% |
| 🟡 | REGN | $803.65 | 5.6 | $-500 | 0.0% |
| 🟢 | SBUX | $100.12 | 5.5 | $-500 | 0.0% |
| 🟡 | PFE | $27.62 | 5.4 | $-500 | 0.0% |
| 🟢 | INFY | $10.88 | 5.4 | $-500 | 0.0% |
| 🟢 | DIS | $104.35 | 5.3 | $-500 | 0.0% |
| 🟢 | BA | $206.08 | 5.3 | $-500 | 0.0% |
| 🟢 | BRKB | $0.00 | 5.3 | $-500 | 0.0% |
| 🟡 | SONO | $14.52 | 5.2 | $-500 | 0.0% |
| 🟡 | ETSY | $70.04 | 5.2 | $-500 | 0.0% |
| 🟡 | PYPL | $52.25 | 5.1 | $-500 | 0.0% |
| 🟡 | ADBE | $252.83 | 4.9 | $-500 | 0.0% |
| 🟢 | MMYT | $48.71 | 4.9 | $-500 | 0.0% |
| 🟡 | XYZ | $78.71 | 4.5 | $-500 | 0.0% |
_(put/call detail: Section 6)_
_...and 2 more (see Section 6 for the full sector-grouped list)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 42 positions (45.2%)
- 🟡 YELLOW (Neutral): 49 positions (52.7%)
- 🔴 RED (Extended/Overbought): 2 positions (2.2%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BEAR_SIDEWAYS
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 17.7 — VIX 17.7 sustained < 20
- **S&P 500:** 7586 (50d MA: 7604, 200d MA: 7157)
  - Above 50d MA: False | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 121 | 6.9 | 49.5 | 52.2 | 59 | 🟡 NEUTRAL |
| Healthcare | 18 | 5.66 | 41.7 | 42.7 | 25 | 🟡 NEUTRAL |
| Consumer Cyclical | 33 | 6.35 | 26.5 | 36.4 | 58 | 🟢 BUY (rich premium) |
| Industrials | 35 | 7.18 | 41.5 | 40.7 | 41 | 🟡 NEUTRAL |
| Energy | 3 | 6.23 | 50.6 | 67.4 | 30 | 🟡 NEUTRAL |
| Consumer Defensive | 1 | 7.5 | 58.9 | 20.9 | 95 | 🟢 BUY (rich premium) |
| Utilities | 9 | 6.98 | 60.4 | 14.6 | 19 | 🟡 BUY stock/THIN premium |
| Communication Services | 35 | 7.61 | 56.8 | 24.7 | 58 | 🟢 BUY (rich premium) |
| Defense | 5 | 6.12 | 27.8 | 27.5 | 48 | 🟢 BUY (rich premium) |
| Brand-Quality (Non-AI) | 20 | 6.63 | 46.2 | 42.2 | 31 | 🟡 NEUTRAL |
| Basic Materials | 11 | 6.83 | 41.3 | 30.8 | 25 | 🟡 NEUTRAL |
| Financial Services | 35 | 6.13 | 46.8 | 36.5 | 49 | 🟡 NEUTRAL |
| Unknown | 1 | 5.3 | 50.0 | 50.0 | 0 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Consumer Cyclical:** Conv 6.3/10, RSI 26.5, 52W %ile 36.4 — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling)
- ✓ **Communication Services:** Conv 7.6/10, RSI 56.8, 52W %ile 24.7 — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling)
- ✓ **Defense:** Conv 6.1/10, RSI 27.8, 52W %ile 27.5 — 🟢 BUY — Oversold + rich premium (avg IVR 48, good for selling)
- ✓ **Utilities:** Conv 7.0/10, RSI 60.4, 52W %ile 14.6 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 19 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Defensive:** Conv 7.5/10, RSI 58.9, 52W %ile 20.9 — 🟢 BUY — Oversold + rich premium (avg IVR 95, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.9/10, RSI 49.5, 52W %ile 52.2 — 🟡 MONITOR — Neutral positioning
- ◇ **Basic Materials:** Conv 6.8/10, RSI 41.3, 52W %ile 30.8 — 🟡 MONITOR — Neutral positioning
- ◇ **Brand-Quality (Non-AI):** Conv 6.6/10, RSI 46.2, 52W %ile 42.2 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.2/10, RSI 41.5, 52W %ile 40.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Unknown:** Conv 5.3/10, RSI 50.0, 52W %ile 50.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.1/10, RSI 46.8, 52W %ile 36.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 5.7/10, RSI 41.7, 52W %ile 42.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 6.2/10, RSI 50.6, 52W %ile 67.4 — 🟡 MONITOR — Neutral positioning


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


### Technology (34 positions, $2,775,669) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $388,396 | $0 | $388,396 | 🟡 | 7.4 | 🟡 MONITOR |
| TSM | $212,590 | $42,518 | $255,108 | 🟡 | 8.5 | 🟡 MONITOR |
| CRM | $74,197 | $173,127 | $247,325 | 🟡 | 6.8 | 🟡 MONITOR |
| ADBE | $75,849 | $151,698 | $227,547 | 🟡 | 4.9 | 🟡 MONITOR |
| ALAB | $169,200 | $56,400 | $225,600 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MU | $197,552 | $0 | $197,552 | 🟡 | 8.8 | 🟡 MONITOR |
| OKTA | $35,283 | $123,491 | $158,774 | 🔴 | 5.9 | 🔴 TRIM CALL (delta/assignment risk); 🟢 HOLD PUT (near max profit, unaffected — a short call gains protection in a decline, don't close it purely on crash fears) |
| IBM | $96,166 | $24,041 | $120,207 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| PANW | $102,219 | $0 | $102,219 | 🟡 | 5.8 | 🟡 MONITOR |
| MSFT | $49,041 | $49,041 | $98,082 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TWLO | $23,127 | $69,382 | $92,510 | 🟡 | 6.6 | 🟡 MONITOR |
| NVDA | $87,134 | $0 | $87,134 | 🟡 | 7.6 | 🟡 MONITOR |
| CRWD | $63,399 | $21,133 | $84,532 | 🟡 | 5.8 | 🟡 MONITOR |
| ZS | $50,565 | $16,855 | $67,420 | 🟡 | 7.0 | 🟡 MONITOR |
| APH | $47,889 | $15,963 | $63,852 | 🟢 | 8.5 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| SHOP | $51,072 | $0 | $51,072 | 🟡 | 6.5 | 🟡 MONITOR |
| XYZ | $31,486 | $15,743 | $47,229 | 🟡 | 4.5 | 🟡 MONITOR |
| UBER | $41,928 | $0 | $41,928 | 🟡 | 7.5 | 🟡 MONITOR |
| FSLR | $40,010 | $0 | $40,010 | 🟡 | 6.7 | 🟡 MONITOR |
| SKHY | $37,688 | $0 | $37,688 | 🟡 | 8.2 | 🟡 MONITOR |
| IONQ | $18,635 | $7,454 | $26,089 | 🟡 | 7.4 | 🟡 MONITOR |
| AMKR | $24,540 | $0 | $24,540 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBRK | $18,318 | $0 | $18,318 | 🟡 | 6.7 | 🟡 MONITOR |
| PLTR | $16,753 | $0 | $16,753 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ASTS | $12,694 | $0 | $12,694 | 🟡 | 6.9 | 🟡 MONITOR |
| CRWV | $8,926 | $0 | $8,926 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LYFT | $1,469 | $7,343 | $8,811 | 🟡 | 7.8 | 🟡 MONITOR |
| LASR | $7,993 | $0 | $7,993 | 🟡 | 7.5 | 🟡 MONITOR |
| CIFR | $6,176 | $0 | $6,176 | 🟡 | 6.7 | 🟡 MONITOR |
| SONO | $0 | $5,806 | $5,806 | 🟡 | 5.2 | 🟡 MONITOR |
| INFY | $1,088 | $1,088 | $2,175 | 🟢 | 5.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QBTS | $1,676 | $0 | $1,676 | 🟡 | 6.7 | 🟡 MONITOR |
| QUBT | $792 | $0 | $792 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ONDS | $734 | $0 | $734 | 🟡 | 7.0 | 🟡 MONITOR |

### Industrials (9 positions, $1,260,777) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $147,153 | $392,407 | $539,560 | 🟡 | 6.5 | 🟡 MONITOR |
| GEV | $279,212 | $93,071 | $372,282 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| BE | $155,301 | $51,767 | $207,068 | 🔴 | 7.1 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| VRT | $49,136 | $0 | $49,136 | 🟢 | 8.3 | 🟢 ATTRACTIVE — let run |
| RKLB | $38,157 | $0 | $38,157 | 🟡 | 7.0 | 🟡 MONITOR |
| BWXT | $31,122 | $0 | $31,122 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| SPCX | $15,330 | $0 | $15,330 | 🟡 | 7.6 | 🟡 MONITOR |
| KTOS | $4,655 | $0 | $4,655 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| PL | $3,466 | $0 | $3,466 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |

### Communication Services (7 positions, $956,437) — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $257,780 | $64,445 | $322,225 | 🟡 | 8.0 | 🟡 MONITOR |
| APP | $185,388 | $61,796 | $247,184 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $120,928 | $45,348 | $166,276 | 🟡 | 6.4 | 🟡 MONITOR |
| GOOGL | $98,742 | $0 | $98,742 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| NBIS | $46,105 | $0 | $46,105 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBLX | $31,220 | $13,380 | $44,600 | 🟡 | 8.0 | 🟡 MONITOR |
| DIS | $20,870 | $10,435 | $31,305 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Financial Services (8 positions, $625,905) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| COIN | $68,692 | $137,384 | $206,076 | 🟡 | 5.8 | 🟡 MONITOR |
| MA | $169,797 | $0 | $169,797 | 🟡 | 6.9 | 🟡 MONITOR |
| PYPL | $31,350 | $62,700 | $94,050 | 🟡 | 5.1 | 🟡 MONITOR |
| JPM | $70,326 | $0 | $70,326 | 🟡 | 7.0 | 🟡 MONITOR |
| CRCL | $36,536 | $18,268 | $54,804 | 🟢 | 5.8 | 🟢 ATTRACTIVE — let run |
| HOOD | $11,415 | $0 | $11,415 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run |
| RIOT | $8,378 | $2,095 | $10,473 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| HUT | $8,964 | $0 | $8,964 | 🟡 | 7.8 | 🟡 MONITOR |

### Healthcare (7 positions, $519,080) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ISRG | $143,018 | $0 | $143,018 | 🟡 | 6.7 | 🟡 MONITOR |
| UNH | $79,442 | $39,721 | $119,163 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| LLY | $112,948 | $0 | $112,948 | 🟡 | 7.0 | 🟡 MONITOR |
| REGN | $80,365 | $0 | $80,365 | 🟡 | 5.6 | 🟡 MONITOR |
| NVO | $22,300 | $8,920 | $31,220 | 🟢 | 3.7 | 🟢 ATTRACTIVE — let run |
| ZBH | $9,278 | $9,278 | $18,556 | 🟢 | 5.9 | 🟢 ATTRACTIVE — let run |
| PFE | $13,810 | $0 | $13,810 | 🟡 | 5.4 | 🟡 MONITOR |

### Consumer Cyclical (12 positions, $442,070) — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $109,700 | $27,425 | $137,125 | 🟡 | 6.8 | 🟡 MONITOR |
| AMZN | $50,399 | $25,200 | $75,599 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ABNB | $16,805 | $50,416 | $67,222 | 🟢 | 5.9 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| BABA | $53,940 | $0 | $53,940 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TSLA | $36,646 | $0 | $36,646 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MMYT | $19,484 | $4,871 | $24,355 | 🟢 | 4.9 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| JD | $8,075 | $8,075 | $16,149 | 🟡 | 8.2 | 🟡 MONITOR |
| ETSY | $7,004 | $7,004 | $14,007 | 🟡 | 5.2 | 🟡 MONITOR |
| CAVA | $5,562 | $0 | $5,562 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| DKNG | $4,756 | $0 | $4,756 | 🟡 | 6.4 | 🟡 MONITOR |
| BROS | $4,448 | $0 | $4,448 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CCL | $2,260 | $0 | $2,260 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (4 positions, $358,914) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ULTA | $107,071 | $53,536 | $160,607 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run |
| ANET | $95,265 | $57,159 | $152,424 | 🟡 | 7.2 | 🟡 MONITOR |
| NKE | $0 | $25,858 | $25,858 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run |
| SBUX | $20,025 | $0 | $20,025 | 🟢 | 5.5 | 🟢 ATTRACTIVE — let run |

### Defense (3 positions, $197,569) — 🟢 BUY — Oversold + rich premium (avg IVR 48, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| NOC | $103,746 | $0 | $103,746 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| LMT | $52,608 | $0 | $52,608 | 🟡 | 6.8 | 🟡 MONITOR |
| BA | $41,216 | $0 | $41,216 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

### Utilities (3 positions, $115,321) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 19 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $59,366 | $14,842 | $74,208 | 🟡 | 7.0 | 🟡 MONITOR |
| CEG | $28,791 | $0 | $28,791 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |
| OKLO | $12,323 | $0 | $12,323 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |

### Basic Materials (2 positions, $107,255) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $73,797 | $12,300 | $86,097 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MP | $15,869 | $5,290 | $21,158 | 🟡 | 7.4 | 🟡 MONITOR |

### Energy (2 positions, $19,655) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| CCJ | $9,833 | $0 | $9,833 | 🟢 | 3.9 | 🟢 ATTRACTIVE — let run |
| DVN | $9,822 | $0 | $9,822 | 🟡 | 7.4 | 🟡 MONITOR |

### Consumer Defensive (1 positions, $10,645) — 🟢 BUY — Oversold + rich premium (avg IVR 95, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,645 | $0 | $10,645 | 🟡 | 7.5 | 🟡 MONITOR |

### Unknown (1 positions, $0) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| BRKB | $0 | $0 | $0 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 8.7% ($640,618)
- 🟡 MONITOR: 58.2% ($4,299,595)
- 🟢 HEALTHY: 33.1% ($2,449,085)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🔴 RED

**Summary:** 🔴 ALERT — 2 indicators critical. Market fragility rising.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| 🔴 | BREADTH | 46.15384615384615 | RED | 60% (caution), 50% (alert) |
| 🔴 | AD_RATIO | 0.5625 | RED | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 267 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.40% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟠 30-day crash probability: 47.8% — Action: 🟡 CAUTION: Reduce overbought positions by 20-25%
- 🔴 60-day crash probability: 80.7%
- 🔴 90-day crash probability: 95.0%
- 📌 Primary risk factor: AD_RATIO critical

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▄▄`
  - 2026-09-01: 48% → 2026-09-10: 48% (flat, -0pp)

**Historical magnitude reference** (real, verified past events — NOT a prediction of this specific reading's outcome):

| Event | Magnitude |
|---|---|
| 2000 dot-com | -17.2% initial leg / -49.1% full bear |
| 2007 GFC | -56.8% full bear, VIX peaked 80.9 |
| 2013 taper tantrum | -5.8% / 34 days |
| 2021-22 growth derate | -25.4% / 282 days |
| 2023 SVB | -4.8% / 7 days (resolved fast via FDIC backstop) |

See logs/circular_financing_playbook.html for the full framework this session's AI-capex risk analysis is built on.

**Sector Sensitivity to Primary Risk Driver** (AD_RATIO):

- 🔴 HIGH exposure: Technology, Consumer Cyclical, Communication Services, Basic Materials
- 🟢 LOW exposure: Utilities, Healthcare, Consumer Defensive, Energy, Defense

New entries in HIGH-exposure sectors compound the exact risk this driver is flagging, even if the individual name looks statistically oversold — see the opportunity list in Section 7 for a per-name check against this.

**Recommended Actions:**

- 🔴 Stage 2-3 Rotation (Crash risk rising)
- Close 50% of remaining overbought positions
- Reduce naked call exposure by 30% more
- Rotate proceeds to: Cash (40%), Defensive (30%)
- Stop entering new GROWTH positions
- Prepare for potential Stage 3 (emergency)

**Rotation Playbook:**

```
RED FLAG — Stage 2-3 Rotation (CRASH RISK: 48% prob in 30d)
  ⚠️ EMERGENCY PROTOCOL ACTIVATED

  Probability-Driven Threshold: 48% crash risk in next 30 days
  → Cut 20% of gross exposure immediately
  → Raise cash to 60% of portfolio
  → 60-day outlook: 81% probability (heightened vigilance)

  Account A Actions:
    1. Close ALL overbought positions (RSI >70) — don't wait for 70% profit
    2. Close remaining naked calls (or hedge heavily with long puts)
    3. Reduce notional from 100% → 80% of normal
    4. Increase cash to 40-50% (emergency fund)
    5. Consider long puts on SPY/QQQ for crash protection
    6. HALT all new strangle entries — CSPs/CCs only on defensive names

  Account B Actions:
    1. Close all CSP new entries for Tier 1/2 names
    2. Exit assigned positions (harvest remaining CCs quickly)
    3. Go to 60% cash, 40% defensive covered calls (Healthcare, Staples)
    4. Stand ready to deploy cash on 95% probability dips

  CIRCUIT BREAKER:
    • IF VIX spikes >30 AND prob stays >60% → FULL CASH (100% defensive)
    • IF regime breaks (S&P below 200-MA) → Redeploy cash on 5%+ dips ONLY
```

### AI Capex Risk Tracker (Circular Financing Playbook — the scriptable half of the same macro picture above)

- **Technology concentration:** 37.6% of notional (121 positions, $2,775,669)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $828,301 live — 72% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $318,960 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $140,278 across NBIS, CRWV, RKLB, OKLO, SPCX, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-08 (2 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.

Underperformance proxy: no tracked name diverging >10pp from SPX over 7 days.


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | AXON | C | 450.0 | 8 | 100% | $45,000 |  |
| Account A (232) | CRM | C | 175.0 | 8 | 100% | $17,500 |  |
| Account A (232) | COIN | P | 250.0 | 8 | 98% | $25,000 |  |
| Account C (634) | PL | P | 32.0 | 36 | 97% | $3,200 |  |
| Account A (232) | CRM | C | 185.0 | 71 | 89% | $18,500 |  |
| Account B (275) | CRM | C | 175.0 | 99 | 87% | $17,500 |  |
| Account A (232) | OKTA | C | 140.0 | 71 | 86% | $14,000 | 🔴 EXIT CANDIDATE |
| Account C (634) | ABNB | C | 145.0 | 36 | 84% | $14,500 |  |
| Account A (232) | AXON | P | 570.0 | 8 | 83% | $57,000 |  |
| Account A (232) | CRCL | P | 105.0 | 8 | 81% | $10,500 |  |
| Account A (232) | IBM | P | 270.0 | 36 | 80% | $27,000 |  |
| Account A (232) | ADBE | C | 230.0 | 8 | 79% | $23,000 |  |
| Account A (232) | NVO | P | 50.0 | 99 | 76% | $5,000 |  |
| Account A (232) | AXON | C | 470.0 | 8 | 74% | $47,000 |  |
| Account A (232) | MP | P | 60.0 | 99 | 71% | $6,000 |  |
| Account A (232) | AXON | P | 560.0 | 99 | 71% | $56,000 |  |
| Account A (232) | CRM | C | 210.0 | 99 | 71% | $21,000 |  |
| Account A (232) | PYPL | C | 45.0 | 71 | 71% | $9,000 |  |
| Account A (232) | PYPL | C | 42.5 | 71 | 70% | $21,250 |  |
| Account A (232) | XYZ | C | 65.0 | 99 | 69% | $13,000 |  |
| Account A (232) | PYPL | C | 45.0 | 99 | 68% | $13,500 |  |
| Account A (232) | RBLX | C | 40.0 | 36 | 68% | $8,000 |  |
| Account A (232) | AXON | P | 540.0 | 99 | 67% | $54,000 |  |
| Account A (232) | DIS | P | 110.0 | 99 | 66% | $22,000 |  |
| Account A (232) | NFLX | P | 80.0 | 71 | 66% | $24,000 |  |
_...and 61 more within 120 DTE (not shown)_

- **Worst case (all shown):** $2,164,450 across 86 positions
- **Realistic (>=30% prob):** $1,503,450 across 65 positions
- **Likely (>=50% prob):** $831,950 across 40 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 1

- OKTA C 140.0 (Account A (232)) — 86% probability, RED heat


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
  - Live: account_a_margin_utilization_pct = 127.55630594852994
  - Live: macro_risk_level = RED



## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-20,800 to $-20,800 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (1 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $1,000/month contribution from MODERATE conviction positions
- Names: OKTA (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (42 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 42 healthy positions contribute $42,000/month baseline (expected)
- ✅ 42 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (5 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 5 Tier 1 entries = $19,000/month; closes gap from $-20,800 to $-39,800 (27.1% closure)
  - APP: Conv 9.1/10 | RSI 50.1 | Value $247,184 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - APH: Conv 8.5/10 | RSI 59.3 | Value $63,852 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 42.5 | Value $372,282
  - AMKR: Conv 8.4/10 | RSI 46.3 | Value $24,540 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it
  - VRT: Conv 8.3/10 | RSI 42.2 | Value $49,136

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 93
- 🔴 Critical actions: 0 closes + 1 monitors
- 🟡 Yellow cautions: 47
- 🟢 Green healthy: 42
- 📊 Market regime: BEAR_SIDEWAYS

**Gap Closure Summary:**

- Current gap: $-20,800 (-29.7% below target)
- After closes: $-20,800 (saves ~0.0%)
- After new Tier 1 entries: $-39,800 (27.1% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-10 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_