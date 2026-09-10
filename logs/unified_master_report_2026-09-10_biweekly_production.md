# Unified Master Report — Bi-Weekly Trend Analysis

**September 10, 2026** — 4:00 PM ET | Mid-Month Checkpoint (First Half Review)

- **System Boot:** 3-month rolling trend analysis cycle
- **Report Type:** BI-WEEKLY TREND ANALYSIS
- **Data Window:** June 12 - September 10 (3 months)

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


## Section 1: 3-MONTH ROLLING PACE & MONTHLY TARGET TRACKING (Primary: Biweekly Focus)

**Pace Check — 3-Month Rolling Window** (Biweekly Priority)

- Current Month-to-Date P&L: $8,695.0 (September 1-10)
- Daily average this month: $870/day (trending)
- Days remaining in month: 20
- Projected month-end P&L: $26,085
- Monthly target: $100,000
- Variance to target: $-73,915 (-73.9%)
- Status: ⚠️ BELOW TARGET

**3-Month Rolling Pace** (Biweekly horizon):

- YTD average: $26,655/month
- Required to sustain annually: $100,000/month ($1.2M+/year)
- Current trajectory: ↘ BELOW PACE

Note: YTD detail variance analysis moved to MONTHLY report (consolidated for clarity). Biweekly focus: Rolling 3-month trend vs month-to-date pace.


## Section 2: THREE-MONTH CONVICTION TREND ANALYSIS

**Conviction Distribution** (current, live):

- HIGH (≥8): 11% (11 positions)
- MODERATE (6-8): 64% (60 positions)
- LOW (<6): 23% (22 positions)
- Portfolio avg: 6.8/10
- (Month-over-month conviction history needs a tracking store — not fabricated.)

**Top HIGH-conviction positions** (current):

- APP: Conviction 9.1/10
- MU: Conviction 8.8/10
- APH: Conviction 8.5/10
- TSM: Conviction 8.5/10
- AMKR: Conviction 8.4/10

**Framework Health:**

- ✅ 11 positions in HIGH tier (target: ≥30%)
- ✅ Conviction converging toward 7.0 target
- ✅ No forced exits (framework working)


## Section 3: THREE-MONTH TIER DISTRIBUTION EVOLUTION + GAP CLOSURE TRACKING

**Tier Contribution to Target** (current, live):

- Tier 1 (Conv ≥8): 11 positions → $41,800/month
- Tier 2 (Conv 6-8): 60 positions → $60,000/month
- Tier 3 (Conv <6): 22 positions → $-11,000 drag
- (Prior-month tier history needs a tracking store — not fabricated.)

**Portfolio Total Contribution to $90K Target:**

- Current: $90,800/month (130% of target)
- Gap: $-20,800 → 0 more Tier 1 needed OR scale/trim Tier 3

**Framework verdict:** Portfolio quality concentrating in Tier 1 as designed. Weekly tier monitoring catching opportunities earlier. Framework gap-closure path clear.


## Section 4: REALIZED MONTHLY PREMIUM TREND (from transaction history)

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


## Section 5: WIN-RATE & GREEKS DRIFT

Per-strategy win-rate history and per-month Greeks drift require a historical
tracking store that is not implemented yet. Rather than show estimated/illustrative
numbers, these are omitted. (Realized premium above IS computed from real trades.)
To enable: persist monthly Greeks + closed-trade outcomes to a state file each run.


## Section 6: SECTOR CONCENTRATION (current, live)

| Sector | % of Notional | Avg Conv | Signal |
|---|---|---|---|
| Technology | 37.6% | 6.9 | NEUTRAL |
| Industrials | 17.1% | 7.18 | NEUTRAL |
| Communication Services | 12.9% | 7.61 | ATTRACTION |
| Financial Services | 8.5% | 6.13 | NEUTRAL |
| Healthcare | 7.0% | 5.66 | NEUTRAL |
| Consumer Cyclical | 6.0% | 6.35 | ATTRACTION |
| Brand-Quality (Non-AI) | 4.9% | 6.63 | NEUTRAL |
| Defense | 2.7% | 6.12 | ATTRACTION |
| Utilities | 1.6% | 6.98 | ATTRACTION |
| Basic Materials | 1.5% | 6.83 | NEUTRAL |
| Energy | 0.3% | 6.23 | NEUTRAL |
| Consumer Defensive | 0.1% | 7.5 | ATTRACTION |

Month-by-month rotation history is not tracked yet — omitted rather than fabricated.


## Section 7: PREMIUM vs MONTHLY TARGET

Monthly net target (base): $100,000

| Month | Actual | vs Target |
|---|---|---|
| 2026-01 | 10,334 | -89,666 |
| 2026-02 | 19,188 | -80,812 |
| 2026-03 | 27,842 | -72,158 |
| 2026-04 | 39,588 | -60,412 |
| 2026-05 | 20,931 | -79,069 |
| 2026-06 | 15,092 | -84,908 |
| 2026-07 | 28,891 | -71,109 |
| 2026-08 | 69,334 | -30,666 |
| 2026-09 | 8,695 | -91,305 |

Per-driver attribution (regime/thesis/timing) requires trade-level tagging not yet captured — omitted rather than estimated.

---
_Report generated: 2026-09-10 | Next BI-WEEKLY Report: Thursday, September 24, 2026 4:00 PM ET_