# UNIFIED MASTER REPORT — DAILY (320 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** September 30, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,415,485
- **Total notional exposure:** $8,047,654
- **Total option requirement:** $2,767,899
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
| Account A (232) | $403,000 | 16.7% | $5,627,176 | $1,012,892 | Margin | 🔴 OVER CAP | $33,085 | ✅ $-2,812 |
| Account B (275) | $261,000 | 10.8% | $369,276 | $294,050 | Cash-Sec | 🔴 COVERAGE GAP | $9,595 | ✅ $-815 |
| Account C (634) | $256,067 | 10.6% | $351,402 | $211,950 | Cash-Sec | ⚠️ WATCH | $9,413 | ✅ $-800 |
| Fidelity (Rahul) | $563,432 | 23.3% | $693,234 | $620,942 | Cash-Sec | 🔴 COVERAGE GAP | $20,712 | ✅ $-1,760 |
| Fidelity (Rajul — Roth IRA) | $44,942 | 1.9% | $53,635 | $52,683 | Cash-Sec | 🔴 COVERAGE GAP | $1,652 | ✅ $-140 |
| Fidelity (Rajul — Rollover IRA) | $141,349 | 5.9% | $178,015 | $163,200 | Cash-Sec | 🔴 COVERAGE GAP | $5,196 | ✅ $-441 |
| Vanguard (Rahul) | $320,492 | 13.3% | $436,530 | $412,182 | Cash-Sec | 🔴 COVERAGE GAP | $11,782 | ✅ $-1,001 |
| Robinhood (Individual) | $13,000 | 0.5% | $26,718 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $478 | ✅ $-40 |
| Robinhood (Traditional IRA) | $220,000 | 9.1% | $311,667 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,087 | ✅ $-687 |
| Fidelity 401K (Rahul) | $192,200 | 8.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,415,485 | 100.0% | $8,047,654 | $2,767,899 |  |  |  |  |

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
| 🟢 | APP | $299.67 | 9.1 | $3,800 | 3.8% |
| 🟢 | BROS | $39.41 | 9.0 | $3,800 | 3.8% |
| 🟡 | JD | $26.58 | 8.6 | $3,800 | 3.8% |
| 🟡 | LASR | $38.95 | 8.5 | $3,800 | 3.8% |
| 🟢 | GEV | $954.39 | 8.4 | $3,800 | 3.8% |
| 🟢 | GOOGL | $351.42 | 8.4 | $3,800 | 3.8% |
| 🟡 | MU | $1072.24 | 8.4 | $3,800 | 3.8% |
| 🟢 | VRT | $243.34 | 8.3 | $3,800 | 3.8% |
| 🟡 | TSM | $461.03 | 8.2 | $3,800 | 3.8% |
| 🟡 | PL | $16.57 | 8.2 | $3,800 | 3.8% |
| 🟢 | AMKR | $52.56 | 8.1 | $3,800 | 3.8% |
| 🟡 | CAVA | $54.63 | 8.1 | $3,800 | 3.8% |
| 🟡 | IONQ | $44.73 | 8.0 | $3,800 | 3.8% |
| 🟡 | NVDA | $230.64 | 8.0 | $3,800 | 3.8% |
| 🟢 | NU | $12.31 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 60 positions | Total contribution: $60,000/month (60.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | SHOP | $151.11 | 7.8 | $1,000 | 1.0% |
| 🟡 | LLY | $1192.33 | 7.8 | $1,000 | 1.0% |
| 🟡 | ASTS | $61.90 | 7.8 | $1,000 | 1.0% |
| 🔴 | PLTR | $190.53 | 7.8 | $1,000 | 1.0% |
| 🟢 | NKE | $35.69 | 7.7 | $1,000 | 1.0% |
| 🟡 | MSFT | $518.50 | 7.6 | $1,000 | 1.0% |
| 🟡 | ANET | $204.78 | 7.5 | $1,000 | 1.0% |
| 🟢 | OKLO | $37.85 | 7.5 | $1,000 | 1.0% |
| 🟡 | CRWV | $86.75 | 7.5 | $1,000 | 1.0% |
| 🟡 | NBIS | $237.76 | 7.5 | $1,000 | 1.0% |
| 🟡 | QUBT | $8.56 | 7.5 | $1,000 | 1.0% |
| 🟡 | WMT | $105.48 | 7.5 | $1,000 | 1.0% |
| 🟢 | UNH | $370.76 | 7.4 | $1,000 | 1.0% |
| 🟡 | LITE | $945.47 | 7.4 | $1,000 | 1.0% |
| 🟡 | MP | $47.92 | 7.4 | $1,000 | 1.0% |
| 🟢 | ALAB | $346.17 | 7.3 | $1,000 | 1.0% |
| 🟡 | ISRG | $409.05 | 7.3 | $1,000 | 1.0% |
| 🟡 | SKHY | $185.82 | 7.3 | $1,000 | 1.0% |
| 🟡 | ALB | $106.59 | 7.2 | $1,000 | 1.0% |
| 🟡 | UBER | $68.98 | 7.2 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 40 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 17 positions | Total contribution: $-8,500/month (-8.5% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🔴 | OKTA | $210.95 | 5.9 | $-500 | 0.0% |
| 🟢 | VST | $137.38 | 5.9 | $-500 | 0.0% |
| 🔴 | TWLO | $293.33 | 5.8 | $-500 | 0.0% |
| 🟡 | IBM | $221.12 | 5.7 | $-500 | 0.0% |
| 🟢 | PYPL | $53.09 | 5.6 | $-500 | 0.0% |
| 🔴 | SONO | $17.96 | 5.6 | $-500 | 0.0% |
| 🟢 | INFY | $10.70 | 5.6 | $-500 | 0.0% |
| 🟡 | COIN | $186.83 | 5.5 | $-500 | 0.0% |
| 🟢 | DIS | $105.78 | 5.3 | $-500 | 0.0% |
| 🟢 | REGN | $754.38 | 5.2 | $-500 | 0.0% |
| 🟡 | TSLA | $348.39 | 5.2 | $-500 | 0.0% |
| 🟡 | ADBE | $239.47 | 5.1 | $-500 | 0.0% |
| 🟢 | SMR | $8.03 | 5.0 | $-500 | 0.0% |
| 🟡 | NVO | $38.56 | 4.7 | $-500 | 0.0% |
| 🟡 | CCJ | $87.81 | 4.5 | $-500 | 0.0% |
| 🟢 | TTD | $12.11 | 4.3 | $-500 | 0.0% |
| 🟢 | XYZ | $73.80 | 4.2 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 38 positions (41.3%)
- 🟡 YELLOW (Neutral): 46 positions (50.0%)
- 🔴 RED (Extended/Overbought): 8 positions (8.7%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.9 — VIX 15.9 sustained < 20
- **S&P 500:** 7714 (50d MA: 7649, 200d MA: 7217)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg Yield% | Signal |
|---|---|---|---|---|---|---|
| Technology | 108 | 6.85 | 57.6 | 59.0 | 26% | 🟡 NEUTRAL |
| Healthcare | 22 | 6.5 | 52.4 | 46.4 | 12% | 🟡 NEUTRAL |
| Consumer Cyclical | 33 | 6.71 | 43.5 | 33.5 | 23% | 🟡 NEUTRAL |
| Industrials | 35 | 6.91 | 46.6 | 36.2 | 35% | 🟡 NEUTRAL |
| Energy | 2 | 5.75 | 32.2 | 44.3 | 17% | 🟢 BUY (rich premium) |
| Consumer Defensive | 1 | 7.5 | 49.2 | 18.2 | 8% | 🟡 BUY stock/THIN premium |
| Utilities | 10 | 6.58 | 35.9 | 5.7 | 29% | 🟢 BUY (rich premium) |
| Communication Services | 37 | 7.45 | 46.5 | 25.3 | 25% | 🟡 NEUTRAL |
| Defense | 9 | 6.5 | 31.6 | 15.1 | 11% | 🟡 BUY stock/THIN premium |
| Brand-Quality (Non-AI) | 13 | 7.04 | 44.3 | 21.1 | 17% | 🟢 BUY (rich premium) |
| Crypto Mining | 7 | 6.27 | 49.2 | 41.8 | 49% | 🟡 NEUTRAL |
| Basic Materials | 12 | 7.27 | 34.7 | 17.2 | 26% | 🟢 BUY (rich premium) |
| Financial Services | 31 | 6.05 | 47.4 | 36.0 | 25% | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Basic Materials:** Conv 7.3/10, RSI 34.7, 52W %ile 17.2 — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling)
- ✓ **Defense:** Conv 6.5/10, RSI 31.6, 52W %ile 15.1 — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 11% < 15%) — not attractive for CSPs/CCs
- ✓ **Brand-Quality (Non-AI):** Conv 7.0/10, RSI 44.3, 52W %ile 21.1 — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling)
- ✓ **Utilities:** Conv 6.6/10, RSI 35.9, 52W %ile 5.7 — 🟢 BUY — Oversold + rich premium (avg real yield 29%, good for selling)
- ✓ **Consumer Defensive:** Conv 7.5/10, RSI 49.2, 52W %ile 18.2 — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 8% < 15%) — not attractive for CSPs/CCs
- ✓ **Energy:** Conv 5.8/10, RSI 32.2, 52W %ile 44.3 — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.8/10, RSI 57.6, 52W %ile 59.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Consumer Cyclical:** Conv 6.7/10, RSI 43.5, 52W %ile 33.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Communication Services:** Conv 7.5/10, RSI 46.5, 52W %ile 25.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 6.9/10, RSI 46.6, 52W %ile 36.2 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.0/10, RSI 47.4, 52W %ile 36.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 6.5/10, RSI 52.4, 52W %ile 46.4 — 🟡 MONITOR — Neutral positioning
- ◇ **Crypto Mining:** Conv 6.3/10, RSI 49.2, 52W %ile 41.8 — 🟡 MONITOR — Neutral positioning


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
| APP | ENTER | Communication Services | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| BROS | ENTER | Consumer Cyclical | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| OKTA | TRIM | Technology | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +1%. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SONO | TRIM | Technology | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TWLO | TRIM | Technology | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -10%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Top 10 GREEN — best-positioned

| Symbol | Sector | Conv | Notional | Action | Detail |
|---|---|---|---|---|---|
| APP | Communication Services | 9.1 | $299,665 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| BROS | Consumer Cyclical | 9.0 | $3,941 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| GEV | Industrials | 8.4 | $381,756 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GOOGL | Communication Services | 8.4 | $140,568 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| VRT | Industrials | 8.3 | $73,001 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| AMKR | Technology | 8.1 | $21,024 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| NU | Financial Services | 8.0 | $1,231 | 🟢 HOLD — let run | RSI/heat: Dropped -12% in 7 days AND -16% below its 200-day average — genuinely beaten down. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NKE | Brand-Quality (Non-AI) | 7.7 | $24,980 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 7 covered (700 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| OKLO | Utilities | 7.5 | $15,140 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| UNH | Healthcare | 7.4 | $148,304 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Top 10 RED — most concerning

| Symbol | Sector | Conv | Notional | Action | Detail |
|---|---|---|---|---|---|
| OKTA | Technology | 5.9 | $168,756 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +1%. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TWLO | Technology | 5.8 | $117,334 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -10%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CRWD | Technology | 6.0 | $107,096 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PANW | Technology | 6.0 | $80,570 | 🟡 WATCH: RED heat, but conviction 6.0 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~27% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PLTR | Technology | 7.8 | $19,053 | 🟡 WATCH: RED heat, but conviction 7.8 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PFE | Healthcare | 6.2 | $14,365 | 🟡 WATCH: RED heat, but conviction 6.2 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +1%. Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| RBRK | Technology | 6.3 | $11,582 | 🟡 WATCH: RED heat, but conviction 6.3 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SONO | Technology | 5.6 | $7,184 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Technology (31 positions, $2,880,269) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 9%-47%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LITE | $283,641 | $94,547 | $378,188 | 🟡 | 7.4 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 85% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| MU | $214,449 | $107,224 | $321,673 | 🟡 | 8.4 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: 83% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): Confirms and strengthens the 2026-09-01 flag: HBM4 capacity now sold out through 2027, likely through 2028; $100B+ in logged orders; CEO says demand exceeds capacity by ~50%. Stock now $935-986 range, +~200% YTD, $1.1T market cap. Q4 earnings 2026-09-30 (11 days out) is a real near-term catalyst/ris |
| CRM | $93,080 | $139,620 | $232,700 | 🟡 | 6.7 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: 70% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 5 covered call(s) (500 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): 2026-09-01 finding (Salesforce/Anthropic "Claudeforce" partnership) not re-checked this pass -- carried forward, no new SA headline this cycle contradicting it. |
| ALAB | $173,085 | $34,617 | $207,702 | 🟢 | 7.3 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~47% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ADBE | $71,841 | $119,735 | $191,576 | 🟡 | 5.1 | 🟡 WATCH: strangle (2C/3P) — call side uncapped if it rallies | RSI/heat: 28% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 3 covered call(s) (300 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TSM | $138,309 | $46,103 | $184,412 | 🟡 | 8.2 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Technically extended (+20% vs 200-day average), but analyst upside still +20% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| OKTA | $42,189 | $126,567 | $168,756 | 🔴 | 5.9 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +1%. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ANET | $102,390 | $61,434 | $163,824 | 🟡 | 7.5 | 🟡 WATCH: strangle (3C/5P) — call side uncapped if it rallies | RSI/heat: 90% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~23% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 3 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| MSFT | $103,701 | $51,850 | $155,551 | 🟡 | 7.6 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 83% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TWLO | $29,333 | $88,000 | $117,334 | 🔴 | 5.8 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -10%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CRWD | $80,322 | $26,774 | $107,096 | 🔴 | 6.0 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| IBM | $66,336 | $22,112 | $88,448 | 🟡 | 5.7 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PANW | $80,570 | $0 | $80,570 | 🔴 | 6.0 | 🟡 WATCH: RED heat, but conviction 6.0 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~27% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ZS | $60,414 | $20,138 | $80,552 | 🟡 | 6.2 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: RSI 72 approaching overbought (70+). Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| NVDA | $69,192 | $0 | $69,192 | 🟡 | 8.0 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Technically extended (+15% vs 200-day average), but analyst upside still +42% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SHOP | $60,444 | $0 | $60,444 | 🟡 | 7.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI 74 approaching overbought (70+). Real yield-on-capital ~28% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| XYZ | $29,520 | $14,760 | $44,280 | 🟢 | 4.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~20% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| UBER | $41,391 | $0 | $41,391 | 🟡 | 7.2 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI/range reads oversold, but -8% vs its 200-day average — verify before treating as attractive. Real yield-on-capital ~15% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| FSLR | $35,183 | $0 | $35,183 | 🟢 | 6.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~26% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| IONQ | $17,892 | $8,946 | $26,838 | 🟡 | 8.0 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: RSI/range reads overbought, but +3% vs its 200-day average — watch, don't force a close. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| AMKR | $21,024 | $0 | $21,024 | 🟢 | 8.1 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PLTR | $19,053 | $0 | $19,053 | 🔴 | 7.8 | 🟡 WATCH: RED heat, but conviction 7.8 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SKHY | $18,582 | $0 | $18,582 | 🟡 | 7.3 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 81% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ASTS | $18,571 | $0 | $18,571 | 🟡 | 7.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 15% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| RBRK | $11,582 | $0 | $11,582 | 🔴 | 6.3 | 🟡 WATCH: RED heat, but conviction 6.3 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| LYFT | $1,517 | $7,585 | $9,102 | 🟡 | 6.6 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 21% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 5 covered (500 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CRWV | $8,675 | $0 | $8,675 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 28% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~41% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| LASR | $7,790 | $0 | $7,790 | 🟡 | 8.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 19% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~37% annualized (rich premium for CSPs/CCs, ~10% OTM/79DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SONO | $0 | $7,184 | $7,184 | 🔴 | 5.6 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +4%. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| INFY | $1,070 | $1,070 | $2,141 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| QUBT | $856 | $0 | $856 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 12% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Industrials (9 positions, $1,162,277) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| AXON | $85,746 | $342,984 | $428,730 | 🟡 | 6.2 | 🟡 WATCH: strangle (6C/2P) — call side uncapped if it rallies | RSI/heat: 21% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 6 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GEV | $286,317 | $95,439 | $381,756 | 🟢 | 8.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BE | $140,015 | $56,006 | $196,021 | 🟡 | 7.0 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: 74% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~43% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| VRT | $48,667 | $24,334 | $73,001 | 🟢 | 8.3 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| RKLB | $43,143 | $0 | $43,143 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~41% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| BWXT | $27,669 | $0 | $27,669 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~20% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| KTOS | $8,694 | $0 | $8,694 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| PL | $1,657 | $0 | $1,657 | 🟡 | 8.2 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 15% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~50% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| SMR | $1,606 | $0 | $1,606 | 🟢 | 5.0 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Communication Services (8 positions, $1,041,986) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 9%-47%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| META | $293,342 | $73,335 | $366,677 | 🟡 | 7.2 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: 82% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~16% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| APP | $209,766 | $89,900 | $299,665 | 🟢 | 9.1 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| NFLX | $112,216 | $42,081 | $154,297 | 🟢 | 6.7 | 🟡 WATCH: technicals attractive, but a qualitative flag is unresolved | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~15% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 6 naked call(s) (uncapped upside if it rallies), AND 16 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): Wells Fargo downgraded NFLX to Underweight from Equal Weight, cut PT to $57 from $80 (2026-09-18), citing engagement decline (viewing hours -8% adjusted for password-sharing crackdown/geo mix) and a weak content slate (base case -21% YoY hours from top-100 originals). Stock on a 4th straight session |
| GOOGL | $105,426 | $35,142 | $140,568 | 🟢 | 8.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| RBLX | $20,890 | $12,534 | $33,424 | 🟢 | 7.0 | 🟢 HOLD — let run | RSI/heat: Dropped -18% in 7 days AND -25% below its 200-day average — genuinely beaten down. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| NBIS | $23,776 | $0 | $23,776 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 73% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~47% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| DIS | $21,156 | $0 | $21,156 | 🟢 | 5.3 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TTD | $2,423 | $0 | $2,423 | 🟢 | 4.3 | 🟢 HOLD — let run | RSI/heat: Dropped -13% in 7 days AND -47% below its 200-day average — genuinely beaten down. Real yield-on-capital ~37% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Healthcare (7 positions, $995,085) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LLY | $357,699 | $119,233 | $476,932 | 🟡 | 7.8 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Technically extended (+11% vs 200-day average), but analyst upside still +11% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ISRG | $122,716 | $40,905 | $163,622 | 🟡 | 7.3 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI/range reads overbought, but -9% vs its 200-day average — watch, don't force a close. Real yield-on-capital ~15% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| REGN | $75,438 | $75,438 | $150,876 | 🟢 | 5.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| UNH | $74,152 | $74,152 | $148,304 | 🟢 | 7.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NVO | $15,424 | $7,712 | $23,136 | 🟡 | 4.7 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI 25 approaching oversold (30-); 12% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| ZBH | $8,925 | $8,925 | $17,850 | 🟢 | 6.5 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PFE | $14,365 | $0 | $14,365 | 🔴 | 6.2 | 🟡 WATCH: RED heat, but conviction 6.2 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +1%. Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Financial Services (7 positions, $673,936) — 🟡 MONITOR — Neutral positioning ⚠️ MIXED — individual real yield ranges 6%-40%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| MA | $223,248 | $0 | $223,248 | 🟢 | 6.9 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| COIN | $37,366 | $168,147 | $205,513 | 🟡 | 5.5 | 🟡 WATCH: strangle (7C/1P) — call side uncapped if it rallies | RSI/heat: 18% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 7 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| JPM | $66,567 | $33,283 | $99,850 | 🟡 | 6.7 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: RSI 29 approaching oversold (30-). Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| PYPL | $15,927 | $63,708 | $79,635 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~15% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 11 covered call(s) (1100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CRCL | $24,942 | $16,628 | $41,570 | 🟢 | 6.1 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| HOOD | $22,888 | $0 | $22,888 | 🟢 | 6.5 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~32% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NU | $1,231 | $0 | $1,231 | 🟢 | 8.0 | 🟢 HOLD — let run | RSI/heat: Dropped -12% in 7 days AND -16% below its 200-day average — genuinely beaten down. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Consumer Cyclical (12 positions, $450,246) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 9%-46%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| EXPE | $106,012 | $26,503 | $132,515 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| AMZN | $50,296 | $25,148 | $75,444 | 🟢 | 7.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TSLA | $69,678 | $0 | $69,678 | 🟡 | 5.2 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 25% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~17% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| BABA | $54,240 | $0 | $54,240 | 🟡 | 6.0 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ABNB | $16,120 | $32,240 | $48,360 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~16% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| MMYT | $19,016 | $4,754 | $23,770 | 🟡 | 6.4 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 23% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~46% annualized (rich premium for CSPs/CCs, ~10% OTM/79DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| JD | $7,973 | $7,973 | $15,945 | 🟡 | 8.6 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 17% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ETSY | $7,251 | $7,251 | $14,503 | 🟢 | 6.0 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CAVA | $5,463 | $0 | $5,463 | 🟡 | 8.1 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 20% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| BROS | $3,941 | $0 | $3,941 | 🟢 | 9.0 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| DKNG | $3,875 | $0 | $3,875 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~37% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CCL | $2,512 | $0 | $2,512 | 🟡 | 7.2 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Spiked 13% in 7 days but only -8% vs its 200-day average — short-term move, not structurally extended. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Defense (3 positions, $355,551) — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 11% < 15%) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LMT | $153,564 | $0 | $153,564 | 🟡 | 6.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 29% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~8% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| NOC | $97,164 | $48,582 | $145,746 | 🟢 | 6.6 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BA | $37,494 | $18,747 | $56,241 | 🟡 | 6.4 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: 14% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Brand-Quality (Non-AI) (4 positions, $217,020) — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling) ⚠️ MIXED — individual real yield ranges 9%-30%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ULTA | $108,616 | $54,308 | $162,924 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NKE | $0 | $24,980 | $24,980 | 🟢 | 7.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Calls: 7 covered (700 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| SBUX | $18,956 | $0 | $18,956 | 🟡 | 6.1 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI 29 approaching oversold (30-). Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| ELF | $10,160 | $0 | $10,160 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~30% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Utilities (3 positions, $120,583) — 🟢 BUY — Oversold + rich premium (avg real yield 29%, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| VST | $41,214 | $13,738 | $54,952 | 🟢 | 5.9 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CEG | $50,491 | $0 | $50,491 | 🟡 | 6.1 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI 26 approaching oversold (30-); 13% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| OKLO | $15,140 | $0 | $15,140 | 🟢 | 7.5 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Basic Materials (2 positions, $104,442) — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling) 🟡 possible macro exposure (weak historical signal, see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ALB | $63,954 | $21,318 | $85,272 | 🟡 | 7.2 | 🟡 WATCH: strangle (2C/6P) — call side uncapped if it rallies | RSI/heat: 18% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~26% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 6 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): JPMorgan cut its lithium price forecast and PT to $140 (Dec 2027, down from $160/Dec 2026), Neutral maintained -- short-term commodity pricing pressure (China lithium carbonate ~$21,625/mt Q3 vs ~$24,810 Q2), not a structural downgrade. Q2 revenue +31.1% YoY, EPS beat. Stock fell -3.51% on 2026-09-1 |
| MP | $14,377 | $4,792 | $19,170 | 🟡 | 7.4 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~26% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Crypto Mining (3 positions, $22,273) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| RIOT | $8,264 | $2,066 | $10,330 | 🟡 | 6.2 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Dropped -14% in 7 days but only +7% vs its 200-day average — pullback within trend, verify thesis before treating as an entry. Real yield-on-capital ~46% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| HUT | $8,740 | $0 | $8,740 | 🟡 | 6.7 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Dropped -15% in 7 days but only +10% vs its 200-day average — pullback within trend, verify thesis before treating as an entry. Real yield-on-capital ~54% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| CIFR | $3,203 | $0 | $3,203 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Dropped -15% in 7 days AND -13% below its 200-day average — genuinely beaten down. Real yield-on-capital ~52% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Energy (2 positions, $13,438) — 🟢 BUY — Oversold + rich premium (avg real yield 17%, good for selling) ⚠️ MIXED — individual real yield ranges 13%-21%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| CCJ | $8,781 | $0 | $8,781 | 🟡 | 4.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI 27 approaching oversold (30-); 18% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |
| DVN | $4,658 | $0 | $4,658 | 🟡 | 7.0 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 71% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

### Consumer Defensive (1 positions, $10,548) — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 8% < 15%) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| WMT | $10,548 | $0 | $10,548 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: 18% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~8% annualized (thin premium for CSPs/CCs, ~10% OTM/107DTE). No qualitative flag on file. |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 6.9% ($557,857)
- 🟡 MONITOR: 57.3% ($4,610,721)
- 🟢 HEALTHY: 35.8% ($2,879,076)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟢 GREEN

**Summary:** ✅ BULL regime stable. All indicators healthy. Proceed with normal sizing.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| ⚠️ | BREADTH | 53.84615384615385 | YELLOW | 60% (caution), 50% (alert) |
| ✅ | AD_RATIO | 1.2727272727272727 | GREEN | 1.0 (caution), 0.8 (alert) |
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

- **Technology concentration:** 35.8% of notional (108 positions, $2,880,269)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $926,616 live — 83% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $184,412 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $109,803 across NBIS, CRWV, RKLB, OKLO, HUT, RIOT

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

- HUT: -15.3% (7d) vs SPX -0.6% — >10pp gap
- RIOT: -14.2% (7d) vs SPX -0.6% — >10pp gap


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | NVO | P | 50.0 | 79 | 95% | $5,000 |  |
| Account A (232) | OKTA | C | 140.0 | 51 | 90% | $14,000 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account C (634) | TWLO | C | 145.0 | 107 | 90% | $14,500 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account C (634) | CCJ | P | 110.0 | 107 | 87% | $11,000 |  |
| Account C (634) | TWLO | C | 150.0 | 107 | 87% | $30,000 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account A (232) | AXON | P | 560.0 | 79 | 87% | $56,000 |  |
| Account B (275) | AMKR | P | 70.0 | 107 | 87% | $7,000 |  |
| Account A (232) | CRM | C | 185.0 | 51 | 86% | $18,500 |  |
| Account A (232) | ADBE | P | 260.0 | 16 | 85% | $26,000 |  |
| Account A (232) | MP | P | 60.0 | 79 | 84% | $6,000 |  |
| Account A (232) | NFLX | P | 80.0 | 51 | 84% | $24,000 |  |
| Account A (232) | AXON | P | 540.0 | 79 | 83% | $54,000 |  |
| Account B (275) | CRM | C | 175.0 | 79 | 83% | $17,500 |  |
| Account B (275) | BWXT | P | 160.0 | 107 | 78% | $16,000 |  |
| Account A (232) | NFLX | P | 77.5 | 51 | 77% | $15,500 |  |
| Account C (634) | ABNB | C | 145.0 | 16 | 77% | $14,500 |  |
| Account A (232) | PYPL | C | 42.5 | 51 | 77% | $21,250 |  |
| Account A (232) | COIN | C | 170.0 | 16 | 76% | $17,000 |  |
| Account A (232) | PYPL | C | 45.0 | 51 | 73% | $9,000 |  |
| Account A (232) | ETSY | C | 60.0 | 79 | 73% | $6,000 |  |
| Account A (232) | PYPL | C | 45.0 | 79 | 71% | $13,500 |  |
| Account C (634) | UBER | P | 75.0 | 107 | 71% | $7,500 |  |
| Account A (232) | WMT | P | 110.0 | 51 | 68% | $11,000 |  |
| Account A (232) | META | C | 650.0 | 79 | 68% | $65,000 |  |
| Account A (232) | NFLX | P | 75.0 | 107 | 67% | $22,500 |  |
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
  - Live: account_a_margin_utilization_pct = 112.54352448272704
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

#### 2. Monitor for Rolls 🟡 (3 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $3,000/month contribution from MODERATE conviction positions
- Names: OKTA, TWLO, SONO (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (38 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 38 healthy positions contribute $38,000/month baseline (expected)
- ✅ 38 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (7 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 7 Tier 1 entries = $26,600/month; closes gap from $-8,500 to $-35,100 (26.6% closure)
  - APP: Conv 9.1/10 | RSI 42.5 | Value $299,665 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - BROS: Conv 9.0/10 | RSI 27.2 | Value $3,941 ⚠️ Consumer Cyclical is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 56.7 | Value $381,756
  - GOOGL: Conv 8.4/10 | RSI 63.0 | Value $140,568 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - VRT: Conv 8.3/10 | RSI 47.2 | Value $73,001

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 92
- 🔴 Critical actions: 0 closes + 3 monitors
- 🟡 Yellow cautions: 44
- 🟢 Green healthy: 38
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $-8,500 (-8.5% below target)
- After closes: $-8,500 (saves ~0.0%)
- After new Tier 1 entries: $-35,100 (26.6% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-30 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_