# UNIFIED MASTER REPORT — DAILY (320 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** September 30, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,415,485
- **Total notional exposure:** $8,049,373
- **Total option requirement:** $2,767,637
- **Positions with short puts:** 90
- **Positions with short calls:** 51
- **YTD Net Premium:** $321,035 (live from transactions)
- **Month-to-Date Premium:** $79,950
- **Snapshot currency:** 2026-08-22

### Two Lenses on Monthly Performance

_(both derived from your transaction history)_

#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]

| Account | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | YTD |
|---|---|---|---|---|---|---|---|---|---|---|
| Account A (232) | 10,255 | 12,483 | 23,800 | 20,880 | -1,244 | -2,884 | 20,362 | 50,309 | 58,985 | 192,946 |
| Account B (275) | 31 | 3,322 | 1,546 | 4,894 | 9,709 | 3,948 | 575 | 3,476 | 2,614 | 30,115 |
| Account C (634) | 31 | 934 | 449 | 1,959 | 4,435 | 1,321 | 2,286 | 6,028 | 6,308 | 23,751 |
| Fidelity (Rahul) | 17 | 1,824 | 1,231 | 5,580 | 4,947 | 10,629 | 5,151 | 3,339 | 11,763 | 44,481 |
| Fidelity (Rajul — Rollover IRA) | 0 | 0 | 0 | 944 | 932 | 0 | 667 | 3,508 | 280 | 6,331 |
| Fidelity (Rajul — Roth IRA) | 0 | 0 | 0 | 95 | 189 | 1,028 | 1,326 | 1,196 | 0 | 3,834 |
| Robinhood (Individual) | 0 | 107 | 0 | 0 | 205 | -9 | 0 | 609 | 0 | 912 |
| Robinhood (Traditional IRA) | 0 | 518 | 816 | 6,275 | 2,879 | 2,087 | 517 | 5,573 | 0 | 18,665 |
| **TOTAL** | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 79,950 | 321,035 |
| Gross SOLD (STO, opened this month) | 181,739 | 68,408 | 199,758 | 324,125 | 349,672 | 243,331 | 135,826 | 242,546 | 179,816 | 1,925,221 |
| Net REALIZED (FIFO, closed this month) | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 79,950 | 321,035 |

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
| Account A (232) | $403,000 | 16.7% | $5,626,619 | $1,012,791 | Margin | 🔴 OVER CAP | $33,085 | ✅ $-2,812 |
| Account B (275) | $261,000 | 10.8% | $369,876 | $294,050 | Cash-Sec | 🔴 COVERAGE GAP | $9,595 | ✅ $-815 |
| Account C (634) | $256,067 | 10.6% | $352,034 | $211,950 | Cash-Sec | ⚠️ WATCH | $9,413 | ✅ $-800 |
| Fidelity (Rahul) | $563,432 | 23.3% | $693,875 | $620,871 | Cash-Sec | 🔴 COVERAGE GAP | $20,712 | ✅ $-1,760 |
| Fidelity (Rajul — Roth IRA) | $44,942 | 1.9% | $53,599 | $52,672 | Cash-Sec | 🔴 COVERAGE GAP | $1,652 | ✅ $-140 |
| Fidelity (Rajul — Rollover IRA) | $141,349 | 5.9% | $178,317 | $163,200 | Cash-Sec | 🔴 COVERAGE GAP | $5,196 | ✅ $-441 |
| Vanguard (Rahul) | $320,492 | 13.3% | $436,377 | $412,103 | Cash-Sec | 🔴 COVERAGE GAP | $11,782 | ✅ $-1,001 |
| Robinhood (Individual) | $13,000 | 0.5% | $26,779 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $478 | ✅ $-40 |
| Robinhood (Traditional IRA) | $220,000 | 9.1% | $311,897 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,087 | ✅ $-687 |
| Fidelity 401K (Rahul) | $192,200 | 8.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,415,485 | 100.0% | $8,049,373 | $2,767,637 |  |  |  |  |

- **Account A (232):** 171 option positions | Monthly target: $33,085 | Equity: ADBE 300sh, APP 100sh, AXON 200sh, COIN 200sh, CRCL 100sh +15 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 21 option positions | Monthly target: $9,595 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 21 option positions | Monthly target: $9,413 | Equity: ABNB 100sh, NKE 100sh, PL 100sh, TWLO 324sh
- **Fidelity (Rahul):** 42 option positions | Monthly target: $20,712 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,652 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
- **Fidelity (Rajul — Rollover IRA):** 10 option positions | Monthly target: $5,196
- **Vanguard (Rahul):** 25 option positions | Monthly target: $11,782
  - ⚠️ Balance as of 2026-07-31 (61 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $478 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,087
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (61 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (122 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

**Definitions:**

- Notional = Stock price × contracts × 100 (underlying value of options position)
- Opt Req = Strike × contracts × 100 for short puts + current_price × contracts × 100 for naked calls (covered calls = $0)
- Margin accounts (Account A only): real Reg-T buffer — OVER CAP/EMERGENCY means real margin-call risk
- Cash-secured accounts (everyone else): no leverage, no margin call possible — COVERAGE GAP means the requirement exceeds the account's own cash, a liquidity question answered in dollars, not a broker-enforced risk
- Target/Gap columns: same figures previously shown in a separate 'ACCOUNT-LEVEL GAP BREAKDOWN' block below this one

### 60% Close Cost Ratio Framework — Consolidated View

**Framework overview:**

- Base: $100,000/month net = $1.2M/year (at 60% close costs)
- Current Regime: BULL (applies 100% of base)
- Adjusted Target: $100,000 net per month

**Performance vs. target (YTD cumulative):**

- Target (9 months): $900,000
- Actual YTD: $321,035.0
- Gap to close: $578,965.0 (64.3%)
- Monthly average (YTD): $35,671
- Monthly average needed: $100,000
- Monthly gap: $-8,500

**Position tier distribution → gap closure:**

- Tier 1 (15 positions): $57,000/month (57% of $100,000 target)
- Tier 2 (60 positions): $60,000/month (60% of target)
- Tier 3 (17 positions): $-8,500/month (-8% drag)
- Current total: 92 positions = $108,500/month (108% of target)

**Gap closure path:**

- To hit $100,000 target: Need 0 more Tier 1 positions
- Alternative: Scale existing OR exit 6 worst Tier 3 positions
- Capital required for 0 new positions: $0 (0 × $10K)

**Risk guardrails:**

- Margin account (Account A only): >75% alert, >80% emergency — real broker margin-call risk
- Cash-secured accounts (everyone else): >75% watch, >=100% coverage gap — a liquidity question (does cash cover full assignment), not a leverage/margin-call risk
- Cash floor (all accounts): $75,000 minimum to trade
- Cash emergency: <$50,000 → deploy emergency fund
- Current status: ⚠️ MONITOR


### Supplementary: Production Framework — 60% Close Cost Ratio Targets

- Framework: $100,000/month net = $1.2M/year target (at 60% close costs)
- Regime: BULL (applies 100% of base)
- Adjusted Target: $250,000 gross / $100,000 net

**Account Targets (Regime-Adjusted)** — complements Section 0's Per-Account
Breakdown 'Target' column: that one is the raw monthly_target; these are the
same targets scaled by the current regime's adjustment factor, gross+net.

| Account | Gross | Net |
|---|---|---|
| Account A (232) | $82,712 | $33,085 |
| Account B (275) | $23,987 | $9,595 |
| Account C (634) | $23,532 | $9,413 |
| Fidelity (Rahul) | $51,780 | $20,712 |
| Fidelity (Rajul — Roth IRA) | $4,130 | $1,652 |
| Fidelity (Rajul — Rollover IRA) | $12,990 | $5,196 |
| Vanguard (Rahul) | $29,455 | $11,782 |
| Robinhood (Individual) | $1,195 | $478 |
| Robinhood (Traditional IRA) | $20,217 | $8,087 |
| **TOTAL** | $249,998 | $100,000 |


## Section 1: SYSTEM STATUS & PORTFOLIO SNAPSHOT

- **Total open positions:** 320
- **Unique tickers:** 92
- **Active accounts:** 10
- **Data currency:** 2026-09-30
- **Live prices:** 92 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (15 positions): $57,000/month — each contributes $3,800/month (4.2% of $100,000)
- Tier 2 (60 positions): $60,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (17 positions): $-8,500/month — each drags -$500/month (-0.6% of target)
- Portfolio: 108,500/month (108% of target) — Need $-8,500 more

**HIGH (Tier 1: 8-10) conviction** — 15 positions | Total contribution: $57,000/month (57.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $299.13 | 9.1 | $3,800 | 3.8% |
| 🟢 | BROS | $39.29 | 9.0 | $3,800 | 3.8% |
| 🟡 | JD | $26.53 | 8.6 | $3,800 | 3.8% |
| 🟡 | LASR | $39.08 | 8.5 | $3,800 | 3.8% |
| 🟢 | GEV | $954.10 | 8.4 | $3,800 | 3.8% |
| 🟢 | GOOGL | $352.40 | 8.4 | $3,800 | 3.8% |
| 🟡 | MU | $1073.65 | 8.4 | $3,800 | 3.8% |
| 🟢 | VRT | $243.65 | 8.3 | $3,800 | 3.8% |
| 🟡 | TSM | $461.80 | 8.2 | $3,800 | 3.8% |
| 🟡 | PL | $16.58 | 8.2 | $3,800 | 3.8% |
| 🟢 | AMKR | $52.63 | 8.1 | $3,800 | 3.8% |
| 🟡 | CAVA | $54.51 | 8.1 | $3,800 | 3.8% |
| 🟡 | IONQ | $44.73 | 8.0 | $3,800 | 3.8% |
| 🟡 | NVDA | $230.91 | 8.0 | $3,800 | 3.8% |
| 🟢 | NU | $12.34 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 60 positions | Total contribution: $60,000/month (60.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | SHOP | $150.78 | 7.8 | $1,000 | 1.0% |
| 🟡 | LLY | $1187.00 | 7.8 | $1,000 | 1.0% |
| 🟡 | ASTS | $61.83 | 7.8 | $1,000 | 1.0% |
| 🔴 | PLTR | $190.48 | 7.8 | $1,000 | 1.0% |
| 🟢 | NKE | $35.64 | 7.7 | $1,000 | 1.0% |
| 🟡 | MSFT | $519.32 | 7.6 | $1,000 | 1.0% |
| 🟡 | ANET | $204.74 | 7.5 | $1,000 | 1.0% |
| 🟢 | OKLO | $37.74 | 7.5 | $1,000 | 1.0% |
| 🟡 | CRWV | $86.99 | 7.5 | $1,000 | 1.0% |
| 🟡 | NBIS | $239.59 | 7.5 | $1,000 | 1.0% |
| 🟡 | QUBT | $8.55 | 7.5 | $1,000 | 1.0% |
| 🟡 | WMT | $105.56 | 7.5 | $1,000 | 1.0% |
| 🟢 | UNH | $370.96 | 7.4 | $1,000 | 1.0% |
| 🟡 | LITE | $947.18 | 7.4 | $1,000 | 1.0% |
| 🟡 | MP | $47.86 | 7.4 | $1,000 | 1.0% |
| 🟢 | ALAB | $347.15 | 7.3 | $1,000 | 1.0% |
| 🟡 | ZS | $202.40 | 7.3 | $1,000 | 1.0% |
| 🟡 | ISRG | $408.82 | 7.3 | $1,000 | 1.0% |
| 🟡 | SKHY | $186.47 | 7.3 | $1,000 | 1.0% |
| 🟡 | ALB | $106.69 | 7.2 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 40 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 17 positions | Total contribution: $-8,500/month (-8.5% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🔴 | OKTA | $211.33 | 5.9 | $-500 | 0.0% |
| 🟢 | VST | $137.24 | 5.9 | $-500 | 0.0% |
| 🔴 | TWLO | $294.50 | 5.8 | $-500 | 0.0% |
| 🟡 | IBM | $220.60 | 5.7 | $-500 | 0.0% |
| 🟢 | PYPL | $53.13 | 5.6 | $-500 | 0.0% |
| 🔴 | SONO | $17.97 | 5.6 | $-500 | 0.0% |
| 🟢 | INFY | $10.71 | 5.6 | $-500 | 0.0% |
| 🟡 | COIN | $186.72 | 5.5 | $-500 | 0.0% |
| 🟡 | ADBE | $239.13 | 5.5 | $-500 | 0.0% |
| 🟢 | SMR | $8.01 | 5.3 | $-500 | 0.0% |
| 🟢 | DIS | $105.75 | 5.3 | $-500 | 0.0% |
| 🟢 | REGN | $752.61 | 5.2 | $-500 | 0.0% |
| 🟡 | TSLA | $349.95 | 5.2 | $-500 | 0.0% |
| 🟢 | NVO | $38.49 | 4.7 | $-500 | 0.0% |
| 🟡 | CCJ | $87.71 | 4.5 | $-500 | 0.0% |
| 🟢 | TTD | $12.11 | 4.3 | $-500 | 0.0% |
| 🟢 | XYZ | $73.77 | 4.2 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 38 positions (41.3%)
- 🟡 YELLOW (Neutral): 46 positions (50.0%)
- 🔴 RED (Extended/Overbought): 8 positions (8.7%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.9 — VIX 15.9 sustained < 20
- **S&P 500:** 7720 (50d MA: 7649, 200d MA: 7217)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg Yield% | Signal |
|---|---|---|---|---|---|---|
| Technology | 108 | 6.92 | 57.6 | 59.1 | 26% | 🟡 NEUTRAL |
| Healthcare | 22 | 6.5 | 52.1 | 46.1 | 12% | 🟡 NEUTRAL |
| Consumer Cyclical | 33 | 6.71 | 43.3 | 33.5 | 23% | 🟡 NEUTRAL |
| Industrials | 35 | 6.93 | 46.6 | 36.3 | 35% | 🟡 NEUTRAL |
| Energy | 2 | 5.75 | 32.2 | 44.5 | 17% | 🟢 BUY (rich premium) |
| Consumer Defensive | 1 | 7.5 | 49.6 | 18.4 | 8% | 🟡 BUY stock/THIN premium |
| Utilities | 10 | 6.58 | 35.7 | 5.5 | 29% | 🟢 BUY (rich premium) |
| Communication Services | 37 | 7.45 | 46.7 | 25.5 | 25% | 🟡 NEUTRAL |
| Defense | 9 | 6.5 | 31.4 | 15.0 | 11% | 🟡 BUY stock/THIN premium |
| Brand-Quality (Non-AI) | 13 | 7.04 | 44.5 | 21.3 | 17% | 🟢 BUY (rich premium) |
| Crypto Mining | 7 | 6.27 | 48.9 | 41.6 | 49% | 🟡 NEUTRAL |
| Basic Materials | 12 | 7.27 | 34.8 | 17.2 | 26% | 🟢 BUY (rich premium) |
| Financial Services | 31 | 6.05 | 47.3 | 35.9 | 25% | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Basic Materials:** Conv 7.3/10, RSI 34.8, 52W %ile 17.2 — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling)
- ✓ **Defense:** Conv 6.5/10, RSI 31.4, 52W %ile 15.0 — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 11% < 15%) — not attractive for CSPs/CCs
- ✓ **Brand-Quality (Non-AI):** Conv 7.0/10, RSI 44.5, 52W %ile 21.3 — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling)
- ✓ **Utilities:** Conv 6.6/10, RSI 35.7, 52W %ile 5.5 — 🟢 BUY — Oversold + rich premium (avg real yield 29%, good for selling)
- ✓ **Consumer Defensive:** Conv 7.5/10, RSI 49.6, 52W %ile 18.4 — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 8% < 15%) — not attractive for CSPs/CCs
- ✓ **Energy:** Conv 5.8/10, RSI 32.2, 52W %ile 44.5 — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.9/10, RSI 57.6, 52W %ile 59.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Consumer Cyclical:** Conv 6.7/10, RSI 43.3, 52W %ile 33.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Communication Services:** Conv 7.5/10, RSI 46.7, 52W %ile 25.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 6.9/10, RSI 46.6, 52W %ile 36.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.0/10, RSI 47.3, 52W %ile 35.9 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 6.5/10, RSI 52.1, 52W %ile 46.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Crypto Mining:** Conv 6.3/10, RSI 48.9, 52W %ile 41.6 — 🟡 MONITOR — Neutral positioning


## Section 5: POSITION DISTRIBUTION BY ACCOUNT

- **Account A (232):** 171 positions (53.4%) `██████████████████████████`
- **Fidelity (Rahul):** 42 positions (13.1%) `██████`
- **Vanguard (Rahul):** 25 positions (7.8%) `███`
- **Account B (275):** 21 positions (6.6%) `███`
- **Account C (634):** 21 positions (6.6%) `███`
- **Robinhood (Traditional IRA):** 18 positions (5.6%) `██`
- **Fidelity (Rajul — Rollover IRA):** 10 positions (3.1%) `█`
- **Fidelity (Rajul — Roth IRA):** 8 positions (2.5%) `█`
- **Robinhood (Individual):** 4 positions (1.2%) ``
- **Fidelity 401K (Rahul):** 0 positions (0.0%) ``


## Section 6: POSITION HEAT MATRIX BY SECTOR — Sector -> Symbol, Put/Call/Total Value, Heat, Suggestion


### Priority Actions (bottom-up, CLOSE/TRIM/ENTER only)

| Symbol | Verb | Sector | Action | Detail |
|---|---|---|---|---|
| APP | ENTER | Communication Services | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BROS | ENTER | Consumer Cyclical | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| CRWD | TRIM | Technology | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GEV | ENTER | Industrials | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GOOGL | ENTER | Communication Services | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| OKTA | TRIM | Technology | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +0%. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PANW | TRIM | Technology | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~27% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| PFE | TRIM | Healthcare | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +0%. Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| RBRK | TRIM | Technology | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| SONO | TRIM | Technology | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| TWLO | TRIM | Technology | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -11%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| VRT | ENTER | Industrials | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Top 10 GREEN — best-positioned

| Symbol | Sector | Conv | Notional | Action | Detail |
|---|---|---|---|---|---|
| APP | Communication Services | 9.1 | $299,130 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BROS | Consumer Cyclical | 9.0 | $3,929 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| GEV | Industrials | 8.4 | $381,640 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GOOGL | Communication Services | 8.4 | $140,960 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| VRT | Industrials | 8.3 | $73,094 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| AMKR | Technology | 8.1 | $21,052 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NU | Financial Services | 8.0 | $1,234 | 🟢 HOLD — let run | RSI/heat: Dropped -12% in 7 days AND -16% below its 200-day average — genuinely beaten down. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NKE | Brand-Quality (Non-AI) | 7.7 | $24,948 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 7 covered (700 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| OKLO | Utilities | 7.5 | $15,098 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| UNH | Healthcare | 7.4 | $148,384 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Top 10 RED — most concerning

| Symbol | Sector | Conv | Notional | Action | Detail |
|---|---|---|---|---|---|
| OKTA | Technology | 5.9 | $169,064 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +0%. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| TWLO | Technology | 5.8 | $117,800 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -11%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| CRWD | Technology | 6.0 | $107,036 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| PANW | Technology | 6.0 | $80,722 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~27% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| PLTR | Technology | 7.8 | $19,048 | 🟡 WATCH: RED heat, but conviction 7.8 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| PFE | Healthcare | 6.2 | $14,385 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +0%. Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| RBRK | Technology | 6.3 | $11,596 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| SONO | Technology | 5.6 | $7,188 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |

### Technology (31 positions, $2,883,066) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 9%-47%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LITE | $284,154 | $94,718 | $378,872 | 🟡 | 7.4 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 85% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| MU | $214,729 | $107,365 | $322,094 | 🟡 | 8.4 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: 83% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-09-18): Confirms and strengthens the 2026-09-01 flag: HBM4 capacity now sold out through 2027, likely through 2028; $100B+ in logged orders; CEO says demand exceeds capacity by ~50%. Stock now $935-986 range, +~200% YTD, $1.1T market cap. Q4 earnings 2026-09-30 (11 days out) is a real near-term catalyst/ris |
| CRM | $92,950 | $139,425 | $232,375 | 🟡 | 6.7 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: 70% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 5 covered call(s) (500 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-09-18): 2026-09-01 finding (Salesforce/Anthropic "Claudeforce" partnership) not re-checked this pass -- carried forward, no new SA headline this cycle contradicting it. |
| ALAB | $173,575 | $34,715 | $208,290 | 🟢 | 7.3 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~47% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ADBE | $71,740 | $119,567 | $191,308 | 🟡 | 5.5 | 🟡 WATCH: strangle (2C/3P) — call side uncapped if it rallies | RSI/heat: 28% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 3 covered call(s) (300 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| TSM | $138,541 | $46,180 | $184,722 | 🟡 | 8.2 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Technically extended (+20% vs 200-day average), but analyst upside still +20% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| OKTA | $42,266 | $126,798 | $169,064 | 🔴 | 5.9 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +0%. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| ANET | $102,370 | $61,422 | $163,792 | 🟡 | 7.5 | 🟡 WATCH: strangle (3C/5P) — call side uncapped if it rallies | RSI/heat: 90% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~23% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 3 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| MSFT | $103,864 | $51,932 | $155,796 | 🟡 | 7.6 | 🟡 WATCH: 83% of 52-week range approaching the high extreme (90%+) | RSI/heat: 83% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| TWLO | $29,450 | $88,350 | $117,800 | 🔴 | 5.8 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -11%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| CRWD | $80,277 | $26,759 | $107,036 | 🔴 | 6.0 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| IBM | $66,179 | $22,060 | $88,238 | 🟡 | 5.7 | 🟡 WATCH: 16% of 52-week range approaching the low extreme (10%-) | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| ZS | $60,720 | $20,240 | $80,960 | 🟡 | 7.3 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: RSI 72 approaching overbought (70+). Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| PANW | $80,722 | $0 | $80,722 | 🔴 | 6.0 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~27% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NVDA | $69,274 | $0 | $69,274 | 🟡 | 8.0 | 🟡 WATCH: Technically extended (+16% vs 200-day average), but analyst upside still +42% — may be fundamentally supported, watch rather than force a close | RSI/heat: Technically extended (+16% vs 200-day average), but analyst upside still +42% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| SHOP | $60,312 | $0 | $60,312 | 🟡 | 7.8 | 🟡 WATCH: RSI 73 approaching overbought (70+) | RSI/heat: RSI 73 approaching overbought (70+). Real yield-on-capital ~28% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| XYZ | $29,508 | $14,754 | $44,262 | 🟢 | 4.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~20% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| UBER | $41,388 | $0 | $41,388 | 🟡 | 7.2 | 🟡 WATCH: RSI/range reads oversold, but -8% vs its 200-day average — verify before treating as attractive | RSI/heat: RSI/range reads oversold, but -8% vs its 200-day average — verify before treating as attractive. Real yield-on-capital ~15% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| FSLR | $35,226 | $0 | $35,226 | 🟢 | 6.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~26% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| IONQ | $17,893 | $8,946 | $26,839 | 🟡 | 8.0 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: RSI/range reads overbought, but +3% vs its 200-day average — watch, don't force a close. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| AMKR | $21,052 | $0 | $21,052 | 🟢 | 8.1 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| PLTR | $19,048 | $0 | $19,048 | 🔴 | 7.8 | 🟡 WATCH: RED heat, but conviction 7.8 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| SKHY | $18,647 | $0 | $18,647 | 🟡 | 7.3 | 🟡 WATCH: 82% of 52-week range approaching the high extreme (90%+) | RSI/heat: 82% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| ASTS | $18,550 | $0 | $18,550 | 🟡 | 7.8 | 🟡 WATCH: 15% of 52-week range approaching the low extreme (10%-) | RSI/heat: 15% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| RBRK | $11,596 | $0 | $11,596 | 🔴 | 6.3 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| LYFT | $1,517 | $7,585 | $9,102 | 🟡 | 6.6 | 🟡 WATCH: 21% of 52-week range approaching the low extreme (10%-) | RSI/heat: 21% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 5 covered (500 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| CRWV | $8,699 | $0 | $8,699 | 🟡 | 7.5 | 🟡 WATCH: 29% of 52-week range approaching the low extreme (10%-) | RSI/heat: 29% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~41% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| LASR | $7,817 | $0 | $7,817 | 🟡 | 8.5 | 🟡 WATCH: 19% of 52-week range approaching the low extreme (10%-) | RSI/heat: 19% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~37% annualized (rich premium for CSPs/CCs, ~10% OTM/79DTE). No qualitative flag on file. |
| SONO | $0 | $7,188 | $7,188 | 🔴 | 5.6 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| INFY | $1,071 | $1,071 | $2,141 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| QUBT | $855 | $0 | $855 | 🟡 | 7.5 | 🟡 WATCH: 12% of 52-week range approaching the low extreme (10%-) | RSI/heat: 12% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Industrials (9 positions, $1,161,322) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| AXON | $85,362 | $341,448 | $426,810 | 🟡 | 6.2 | 🟡 WATCH: strangle (6C/2P) — call side uncapped if it rallies | RSI/heat: 21% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 6 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GEV | $286,230 | $95,410 | $381,640 | 🟢 | 8.4 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BE | $140,720 | $56,288 | $197,008 | 🟡 | 7.0 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: 75% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~43% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| VRT | $48,729 | $24,365 | $73,094 | 🟢 | 8.3 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| RKLB | $43,059 | $0 | $43,059 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~41% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| BWXT | $27,713 | $0 | $27,713 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~20% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| KTOS | $8,738 | $0 | $8,738 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| PL | $1,658 | $0 | $1,658 | 🟡 | 8.2 | 🟡 WATCH: 15% of 52-week range approaching the low extreme (10%-) | RSI/heat: 15% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~50% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| SMR | $1,603 | $0 | $1,603 | 🟢 | 5.3 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Communication Services (8 positions, $1,043,864) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 9%-47%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| META | $294,632 | $73,658 | $368,290 | 🟡 | 7.2 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: 83% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~16% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| APP | $209,391 | $89,739 | $299,130 | 🟢 | 9.1 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NFLX | $112,376 | $42,141 | $154,517 | 🟢 | 6.7 | 🟡 WATCH: technicals attractive, but a qualitative flag is unresolved | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~15% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 6 naked call(s) (uncapped upside if it rallies), AND 16 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-09-18): Wells Fargo downgraded NFLX to Underweight from Equal Weight, cut PT to $57 from $80 (2026-09-18), citing engagement decline (viewing hours -8% adjusted for password-sharing crackdown/geo mix) and a weak content slate (base case -21% YoY hours from top-100 originals). Stock on a 4th straight session |
| GOOGL | $105,720 | $35,240 | $140,960 | 🟢 | 8.4 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| RBLX | $20,897 | $12,538 | $33,436 | 🟢 | 7.0 | 🟢 HOLD — let run | RSI/heat: Dropped -18% in 7 days AND -25% below its 200-day average — genuinely beaten down. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NBIS | $23,959 | $0 | $23,959 | 🟡 | 7.5 | 🟡 WATCH: 73% of 52-week range approaching the high extreme (90%+) | RSI/heat: 73% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~47% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| DIS | $21,150 | $0 | $21,150 | 🟢 | 5.3 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| TTD | $2,422 | $0 | $2,422 | 🟢 | 4.3 | 🟢 HOLD — let run | RSI/heat: Dropped -13% in 7 days AND -47% below its 200-day average — genuinely beaten down. Real yield-on-capital ~37% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Healthcare (7 positions, $992,508) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LLY | $356,100 | $118,700 | $474,800 | 🟡 | 7.8 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Technically extended (+11% vs 200-day average), but analyst upside still +12% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ISRG | $122,646 | $40,882 | $163,528 | 🟡 | 7.3 | 🟡 WATCH: RSI/range reads overbought, but -9% vs its 200-day average — watch, don't force a close | RSI/heat: RSI/range reads overbought, but -9% vs its 200-day average — watch, don't force a close. Real yield-on-capital ~15% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| REGN | $75,261 | $75,261 | $150,522 | 🟢 | 5.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| UNH | $74,192 | $74,192 | $148,384 | 🟢 | 7.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NVO | $15,398 | $7,699 | $23,097 | 🟢 | 4.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| ZBH | $8,896 | $8,896 | $17,792 | 🟢 | 6.5 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PFE | $14,385 | $0 | $14,385 | 🔴 | 6.2 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +0%. Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Financial Services (7 positions, $673,501) — 🟡 MONITOR — Neutral positioning ⚠️ MIXED — individual real yield ranges 6%-40%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| MA | $223,040 | $0 | $223,040 | 🟢 | 6.9 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| COIN | $37,344 | $168,048 | $205,392 | 🟡 | 5.5 | 🟡 WATCH: strangle (7C/1P) — call side uncapped if it rallies | RSI/heat: 18% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 7 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| JPM | $66,568 | $33,284 | $99,852 | 🟡 | 6.7 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: RSI 28 approaching oversold (30-). Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| PYPL | $15,939 | $63,756 | $79,695 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~15% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 11 covered call(s) (1100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CRCL | $24,846 | $16,564 | $41,410 | 🟡 | 6.1 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Dropped -12% in 7 days but only -4% vs its 200-day average — pullback within trend, verify thesis before treating as an entry. Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| HOOD | $22,879 | $0 | $22,879 | 🟢 | 6.5 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~32% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NU | $1,234 | $0 | $1,234 | 🟢 | 8.0 | 🟢 HOLD — let run | RSI/heat: Dropped -12% in 7 days AND -16% below its 200-day average — genuinely beaten down. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Consumer Cyclical (12 positions, $450,554) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 9%-46%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| EXPE | $106,112 | $26,528 | $132,640 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| AMZN | $50,290 | $25,145 | $75,435 | 🟢 | 7.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| TSLA | $69,990 | $0 | $69,990 | 🟡 | 5.2 | 🟡 WATCH: 26% of 52-week range approaching the low extreme (10%-) | RSI/heat: 26% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~17% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| BABA | $54,180 | $0 | $54,180 | 🟡 | 6.0 | 🟡 WATCH: 16% of 52-week range approaching the low extreme (10%-) | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| ABNB | $16,137 | $32,274 | $48,411 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~16% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| MMYT | $18,952 | $4,738 | $23,690 | 🟡 | 6.4 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 23% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~46% annualized (rich premium for CSPs/CCs, ~10% OTM/79DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| JD | $7,960 | $7,960 | $15,921 | 🟡 | 8.6 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ETSY | $7,259 | $7,259 | $14,518 | 🟢 | 6.0 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| CAVA | $5,451 | $0 | $5,451 | 🟡 | 8.1 | 🟡 WATCH: 20% of 52-week range approaching the low extreme (10%-) | RSI/heat: 20% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| BROS | $3,929 | $0 | $3,929 | 🟢 | 9.0 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| DKNG | $3,883 | $0 | $3,883 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~37% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| CCL | $2,506 | $0 | $2,506 | 🟡 | 7.2 | 🟡 WATCH: Spiked 12% in 7 days but only -8% vs its 200-day average — short-term move, not structurally extended | RSI/heat: Spiked 12% in 7 days but only -8% vs its 200-day average — short-term move, not structurally extended. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Defense (3 positions, $355,560) — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 11% < 15%) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LMT | $153,498 | $0 | $153,498 | 🟡 | 6.5 | 🟡 WATCH: 29% of 52-week range approaching the low extreme (10%-) | RSI/heat: 29% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~8% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NOC | $97,272 | $48,636 | $145,908 | 🟢 | 6.6 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BA | $37,436 | $18,718 | $56,154 | 🟡 | 6.4 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: 13% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Brand-Quality (Non-AI) (4 positions, $217,847) — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling) ⚠️ MIXED — individual real yield ranges 9%-30%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ULTA | $109,176 | $54,588 | $163,764 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NKE | $0 | $24,948 | $24,948 | 🟢 | 7.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 7 covered (700 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| SBUX | $18,944 | $0 | $18,944 | 🟡 | 6.1 | 🟡 WATCH: RSI 29 approaching oversold (30-) | RSI/heat: RSI 29 approaching oversold (30-). Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| ELF | $10,191 | $0 | $10,191 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~30% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Utilities (3 positions, $120,398) — 🟢 BUY — Oversold + rich premium (avg real yield 29%, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| VST | $41,173 | $13,724 | $54,898 | 🟢 | 5.9 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CEG | $50,402 | $0 | $50,402 | 🟡 | 6.1 | 🟡 WATCH: RSI 26 approaching oversold (30-); 13% of 52-week range approaching the low extreme (10%-) | RSI/heat: RSI 26 approaching oversold (30-); 13% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| OKLO | $15,098 | $0 | $15,098 | 🟢 | 7.5 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Basic Materials (2 positions, $104,496) — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling) 🟡 possible macro exposure (weak historical signal, see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ALB | $64,014 | $21,338 | $85,352 | 🟡 | 7.2 | 🟡 WATCH: strangle (2C/6P) — call side uncapped if it rallies | RSI/heat: 18% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~26% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 6 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-09-18): JPMorgan cut its lithium price forecast and PT to $140 (Dec 2027, down from $160/Dec 2026), Neutral maintained -- short-term commodity pricing pressure (China lithium carbonate ~$21,625/mt Q3 vs ~$24,810 Q2), not a structural downgrade. Q2 revenue +31.1% YoY, EPS beat. Stock fell -3.51% on 2026-09-1 |
| MP | $14,358 | $4,786 | $19,144 | 🟡 | 7.4 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~26% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Crypto Mining (3 positions, $22,259) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| RIOT | $8,254 | $2,064 | $10,318 | 🟡 | 6.2 | 🟡 WATCH: Dropped -15% in 7 days but only +7% vs its 200-day average — pullback within trend, verify thesis before treating as an entry | RSI/heat: Dropped -15% in 7 days but only +7% vs its 200-day average — pullback within trend, verify thesis before treating as an entry. Real yield-on-capital ~46% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| HUT | $8,743 | $0 | $8,743 | 🟡 | 6.7 | 🟡 WATCH: Dropped -16% in 7 days but only +10% vs its 200-day average — pullback within trend, verify thesis before treating as an entry | RSI/heat: Dropped -16% in 7 days but only +10% vs its 200-day average — pullback within trend, verify thesis before treating as an entry. Real yield-on-capital ~54% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| CIFR | $3,199 | $0 | $3,199 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Dropped -15% in 7 days AND -13% below its 200-day average — genuinely beaten down. Real yield-on-capital ~52% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Energy (2 positions, $13,440) — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling) ⚠️ MIXED — individual real yield ranges 13%-21%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| CCJ | $8,771 | $0 | $8,771 | 🟡 | 4.5 | 🟡 WATCH: RSI 27 approaching oversold (30-); 17% of 52-week range approaching the low extreme (10%-) | RSI/heat: RSI 27 approaching oversold (30-); 17% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| DVN | $4,669 | $0 | $4,669 | 🟡 | 7.0 | 🟡 WATCH: 72% of 52-week range approaching the high extreme (90%+) | RSI/heat: 72% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Consumer Defensive (1 positions, $10,556) — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 8% < 15%) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| WMT | $10,556 | $0 | $10,556 | 🟡 | 7.5 | 🟡 WATCH: 18% of 52-week range approaching the low extreme (10%-) | RSI/heat: 18% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~8% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 6.7% ($535,610)
- 🟡 MONITOR: 57.8% ($4,651,865)
- 🟢 HEALTHY: 35.6% ($2,861,897)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟢 GREEN

**Summary:** ✅ BULL regime stable. All indicators healthy. Proceed with normal sizing.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| ⚠️ | BREADTH | 53.84615384615385 | YELLOW | 60% (caution), 50% (alert) |
| ✅ | AD_RATIO | 1.173913043478261 | GREEN | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 308 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.37% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟢 30-day crash probability: 15.2% — Action: 🟢 NORMAL: Proceed with standard sizing
- 🟡 60-day crash probability: 26.4%
- 🟡 90-day crash probability: 37.5%
- 📌 Primary risk factor: BREADTH elevated

- 90-day trend: not enough history yet (need 2+ report runs on different days) — this fills in automatically as reports run going forward.

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

- ✅ No action needed
- Proceed with normal entry sizing
- Monitor for any signal changes

### AI Capex Risk Tracker (Circular Financing Playbook — the scriptable half of the same macro picture above)

- **Technology concentration:** 35.8% of notional (108 positions, $2,883,066)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $928,304 live — 83% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $184,722 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $109,876 across NBIS, CRWV, RKLB, OKLO, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-28 (2 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action on any tracked name since the Jul 9 S&P Oracle downgrade (BBB to BBB-, still current, stable outlook) -- checked live via WebSearch: no new Moody's/S&P action on the "Moody's six" (MSFT/AMZN/GOOGL/META/ORCL/CRWV) since their Jul 24 thematic AI-capex warning (already known, correctly not a firing event -- Moody's itself said an imminent downgrade of MSFT/AMZN/GOOGL/META is unlikely). Two items found that looked like new CoreWeave credit action on first read turned out to be stale/mischaracterized: the "$4bn Blue Owl financing failed" story is from Feb 2026 (already reflected in CoreWeave's known ~50% CDS-implied default probability, not new), and "CoreWeave rating downgrade" headlines are equity ANALYST rating changes (buy/hold/sell), not a credit-rating action -- explicitly the distinction this gate is supposed to hold the line on. CoreWeave's own newest debt facility ($8.5B DDTL, Mar 2026) is A3/Moody's -- investment grade -- a real, positive credit-access data point that complicates the "CoreWeave credit is purely deteriorating" read.
Tier-2 gate: NOT fired. Private-credit redemption pressure is actually DE-ESCALATING this quarter (Ares 14.4%->13.1%, Apollo 16.8%->14.7%, BlackRock HPS 13.3%->11.5% Q2->Q3 2026) -- no new fund gating found.
REAL new development this cycle: ORCL's own equity has now cracked. Last check (2026-09-08) explicitly flagged "equity hasn't cracked yet even though credit is flashing" for the neocloud/hyperscaler cluster -- that's no longer true for ORCL specifically. Live yfinance pull today: ORCL -7.1% (7d) / -7.9% (30d), a full reversal from +8.4%/+9.0% at the last check, and press coverage confirms real price weakness ("Oracle Shares Fall... One-Year Low"). NBIS/CRWV/HUT/RIOT are still net positive 30d (NBIS +10.9%, CRWV -0.5%, HUT +13.9%, RIOT +11.6%) but CRWV's 30d figure flipped from +9.2% to -0.5% -- deceleration, not yet a crack. META is still strongly UP (+13.0%/+30.6%), the opposite direction from the "mega-cap spenders underperforming" pattern the last check described -- that divergence read is weakening, not strengthening.
Anthropic IPO: delayed from an October target to November 2026 (WSJ, reported Sept 18), still targeting a ~$2T valuation vs. $965B private valuation in May -- a real but modest, single-month slip, not a pulled or repriced deal.
Breadth: 53.8% (live, today's report) -- between the 50% alert and 60% caution lines, roughly flat vs. the 51.3-53.9% range seen across the last several checks. HY OAS: 280bps, GREEN, well inside normal (400bps caution / 450bps alert) -- broad credit markets show no stress; the Oracle/CoreWeave stress remains a single-name/CDS story, not a HY-index- wide one.
Dial state: BASE CASE (30/70) -- unchanged. No Tier-1 or Tier-2 condition has actually fired; ORCL's equity crack is a real, single-name confirmation of the credit stress already known and priced into its Jul downgrade, not a new systemic signal. Worth a closer look next cycle specifically on whether ORCL's weakness spreads to CRWV/NBIS (the CRWV 30d deceleration is the one number to watch).

**⚠️ Underperformance proxy** — check these for credit news specifically:

- HUT: -15.6% (7d) vs SPX -0.6% — >10pp gap
- RIOT: -14.6% (7d) vs SPX -0.6% — >10pp gap


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | NVO | P | 50.0 | 79 | 97% | $5,000 |  |
| Account C (634) | TWLO | C | 145.0 | 107 | 94% | $14,500 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account C (634) | TWLO | C | 150.0 | 107 | 93% | $30,000 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account A (232) | OKTA | C | 140.0 | 51 | 92% | $14,000 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account A (232) | AXON | P | 560.0 | 79 | 87% | $56,000 |  |
| Account B (275) | AMKR | P | 70.0 | 107 | 87% | $7,000 |  |
| Account C (634) | CCJ | P | 110.0 | 107 | 86% | $11,000 |  |
| Account A (232) | CRM | C | 185.0 | 51 | 85% | $18,500 |  |
| Account A (232) | AXON | P | 540.0 | 79 | 84% | $54,000 |  |
| Account A (232) | MP | P | 60.0 | 79 | 84% | $6,000 |  |
| Account A (232) | ADBE | P | 260.0 | 16 | 83% | $26,000 |  |
| Account A (232) | NFLX | P | 80.0 | 51 | 83% | $24,000 |  |
| Account B (275) | CRM | C | 175.0 | 79 | 82% | $17,500 |  |
| Account B (275) | BWXT | P | 160.0 | 107 | 78% | $16,000 |  |
| Account A (232) | PYPL | C | 42.5 | 51 | 77% | $21,250 |  |
| Account A (232) | NFLX | P | 77.5 | 51 | 77% | $15,500 |  |
| Account C (634) | ABNB | C | 145.0 | 16 | 77% | $14,500 |  |
| Account A (232) | COIN | C | 170.0 | 16 | 75% | $17,000 |  |
| Account A (232) | PYPL | C | 45.0 | 51 | 74% | $9,000 |  |
| Account A (232) | ETSY | C | 60.0 | 79 | 73% | $6,000 |  |
| Account A (232) | PYPL | C | 45.0 | 79 | 71% | $13,500 |  |
| Account C (634) | UBER | P | 75.0 | 107 | 71% | $7,500 |  |
| Account A (232) | META | C | 650.0 | 79 | 69% | $65,000 |  |
| Account A (232) | WMT | P | 110.0 | 51 | 68% | $11,000 |  |
| Account A (232) | CRCL | P | 90.0 | 51 | 67% | $9,000 |  |
_...and 83 more within 120 DTE (not shown)_

- **Worst case (all shown):** $3,469,000 across 108 positions
- **Realistic (>=30% prob):** $1,726,000 across 76 positions
- **Likely (>=50% prob):** $869,250 across 47 positions

No positions currently combine >=50% probability with RED heat on a truly naked (non-strangle) call, or an at-risk put.


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ⚠️ Last scan: 2026-09-18 (12 days ago)
- **NFLX:** CONCRETE WEEKLY ACTION: Account A holds 2 ITM cash-secured NFLX puts right now -- $77.50P x2 (Nov 20) and $80P x3 (Nov 20), both already ITM at $72 spot, both already flagged separately as low-premium (<$500/contract) in this week's Account A cleanup pass. This new catalyst adds real downside conviction on top of an already-poor risk/reward. Recommend reviewing both for an early close/roll before assignment risk grows further, rather than waiting for expiry. The 2 naked NFLX calls ($80C x3 Nov 20, $85C x3 Jan 15) are UNAFFECTED negatively -- a decline moves them further OTM, reducing their risk.

- **MU:** Flag for next quarterly bucket review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET) -- conviction on the reclass is now stronger than 2026-09-01, not an immediate action. Note the 09-30 earnings date if sizing any near-dated MU options this cycle.

- **AVGO:** No Tier CR trigger -- no rating-agency action, structure is clearer but not worse than already tracked in the Circular Financing Playbook. Confirmation with real mechanical detail, not escalation -- worth folding the SPV structure detail into that document's Tier CR section at its next full review.

- **ALB:** No action -- existing ITM $120P (Feb 19) already reflects the known downside; JPMorgan's own long-term target ($140) still implies recovery above current spot. Fundamentals (revenue/EPS) intact.

- **CRM:** Carried forward from 2026-09-01 -- no update this cycle.
- Open items:
  - NFLX: review the 2 ITM Nov-20 cash-secured puts ($77.50P x2, $80P x3, Account A) for an early close/roll given the Wells Fargo downgrade -- new this cycle.
  - MU: reclass conviction strengthened for next quarterly bucket review -- not urgent.
- ⚠️ Over 10 days since the last Seeking Alpha scan — run the weekly theme-scan skill.


## Section 6.9: ACTIVE DECISION TRACKER


**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 112.53238414001466
  - Live: macro_risk_level = GREEN

**⏳ be_puts_reduction** — OPEN

Reduce BE put exposure to zero over the next ~10 days (target: 2026-09-20) by closing/rolling out of all 6 open BE put legs across every account. BE is RED heat, RSI 77-81 (overbought/extended), and is the most widely-held name in the book -- also carries a naked short-call pair against it in Account A/Fidelity Rahul (no BE shares owned anywhere). Baseline as of 2026-09-10: Account A $170P (Jan 15 2027) x2 [Jan+Feb], Account B $180P (Feb 19 2027), Fidelity (Rahul) $190P (Jan 15 2027), Fidelity (Rajul - Rollover IRA) $200P (Jun 17 2027), Robinhood (Traditional) $180P (Jun 17 2027). Trader confirmed 2026-09-10 this should cover ALL open BE puts (not just the near-dated ones) -- an initial "Dec 2026 and before" framing didn't match any real BE put, since the earliest is Jan 15 2027.
KNOWN GAP: the automated check only sees 5 of these 6 legs -- the Robinhood (Traditional) $180P (Jun 17 2027) has an option-type parsing gap in that account's transaction reconstruction and won't count toward the live total below. This entry will show RESOLVED once the other 5 close even if that 6th one is still open -- manually confirm the Robinhood leg separately before treating BE exposure as fully closed.
  - Live check: 4 leg(s) open now (baseline was 6), target: 0

**Resolved (collapsed — see `data/active_decisions.yaml` for full history):**
  - ✅ account_a_800k_4week_plan — CLEARED (2026-09-21)
  - ✅ axon_sept18_roll_450c — RESOLVED (2026-09-18)
  - ✅ pypl_naked_calls_cleanup — RESOLVED (2026-09-21)
  - ✅ crcl_naked_call_dec — RESOLVED (2026-09-25)



## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-8,500 to $-8,500 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (7 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $7,000/month contribution from MODERATE conviction positions
- Names: OKTA, PFE, TWLO, SONO, CRWD +2 more (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (38 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 38 healthy positions contribute $38,000/month baseline (expected)
- ✅ 38 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (7 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 7 Tier 1 entries = $26,600/month; closes gap from $-8,500 to $-35,100 (26.6% closure)
  - APP: Conv 9.1/10 | RSI 42.3 | Value $299,130 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - BROS: Conv 9.0/10 | RSI 26.0 | Value $3,929 ⚠️ Consumer Cyclical is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 57.0 | Value $381,640
  - GOOGL: Conv 8.4/10 | RSI 63.5 | Value $140,960 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - VRT: Conv 8.3/10 | RSI 47.4 | Value $73,094

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 92
- 🔴 Critical actions: 0 closes + 7 monitors
- 🟡 Yellow cautions: 45
- 🟢 Green healthy: 38
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $-8,500 (-8.5% below target)
- After closes: $-8,500 (saves ~0.0%)
- After new Tier 1 entries: $-35,100 (26.6% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-30 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_