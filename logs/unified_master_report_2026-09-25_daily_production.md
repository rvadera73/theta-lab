# UNIFIED MASTER REPORT — DAILY (320 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** September 25, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,415,485
- **Total notional exposure:** $8,146,493
- **Total option requirement:** $2,786,047
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
| Account A (232) | $403,000 | 16.7% | $5,689,993 | $1,024,199 | Margin | 🔴 OVER CAP | $33,085 | ✅ $-2,878 |
| Account B (275) | $261,000 | 10.8% | $370,430 | $294,050 | Cash-Sec | 🔴 COVERAGE GAP | $9,595 | ✅ $-834 |
| Account C (634) | $256,067 | 10.6% | $354,179 | $211,950 | Cash-Sec | ⚠️ WATCH | $9,413 | ✅ $-818 |
| Fidelity (Rahul) | $563,432 | 23.3% | $715,642 | $625,262 | Cash-Sec | 🔴 COVERAGE GAP | $20,712 | ✅ $-1,801 |
| Fidelity (Rajul — Roth IRA) | $44,942 | 1.9% | $54,766 | $53,921 | Cash-Sec | 🔴 COVERAGE GAP | $1,652 | ✅ $-143 |
| Fidelity (Rajul — Rollover IRA) | $141,349 | 5.9% | $179,368 | $163,200 | Cash-Sec | 🔴 COVERAGE GAP | $5,196 | ✅ $-452 |
| Vanguard (Rahul) | $320,492 | 13.3% | $440,211 | $413,465 | Cash-Sec | 🔴 COVERAGE GAP | $11,782 | ✅ $-1,025 |
| Robinhood (Individual) | $13,000 | 0.5% | $27,808 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $478 | ✅ $-41 |
| Robinhood (Traditional IRA) | $220,000 | 9.1% | $314,096 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,087 | ✅ $-703 |
| Fidelity 401K (Rahul) | $192,200 | 8.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,415,485 | 100.0% | $8,146,493 | $2,786,047 |  |  |  |  |

- **Account A (232):** 171 option positions | Monthly target: $33,085 | Equity: ADBE 300sh, APP 100sh, AXON 200sh, COIN 200sh, CRCL 100sh +15 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 21 option positions | Monthly target: $9,595 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 21 option positions | Monthly target: $9,413 | Equity: ABNB 100sh, NKE 100sh, PL 100sh, TWLO 324sh
- **Fidelity (Rahul):** 42 option positions | Monthly target: $20,712 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,652 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
- **Fidelity (Rajul — Rollover IRA):** 10 option positions | Monthly target: $5,196
- **Vanguard (Rahul):** 25 option positions | Monthly target: $11,782
  - ⚠️ Balance as of 2026-07-31 (56 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $478 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,087
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (56 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (117 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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
- Monthly gap: $-8,700

**Position tier distribution → gap closure:**

- Tier 1 (14 positions): $53,200/month (53% of $100,000 target)
- Tier 2 (63 positions): $63,000/month (63% of target)
- Tier 3 (15 positions): $-7,500/month (-8% drag)
- Current total: 92 positions = $108,700/month (109% of target)

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
- **Data currency:** 2026-09-25
- **Live prices:** 92 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (14 positions): $53,200/month — each contributes $3,800/month (4.2% of $100,000)
- Tier 2 (63 positions): $63,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (15 positions): $-7,500/month — each drags -$500/month (-0.6% of target)
- Portfolio: 108,700/month (109% of target) — Need $-8,700 more

**HIGH (Tier 1: 8-10) conviction** — 14 positions | Total contribution: $53,200/month (53.2% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $312.47 | 9.1 | $3,800 | 3.8% |
| 🟢 | GOOGL | $342.36 | 8.8 | $3,800 | 3.8% |
| 🟡 | NVDA | $224.58 | 8.8 | $3,800 | 3.8% |
| 🟡 | CAVA | $53.51 | 8.8 | $3,800 | 3.8% |
| 🟢 | KTOS | $47.02 | 8.5 | $3,800 | 3.8% |
| 🟡 | LASR | $40.62 | 8.5 | $3,800 | 3.8% |
| 🟢 | NKE | $35.99 | 8.4 | $3,800 | 3.8% |
| 🟡 | JD | $26.75 | 8.4 | $3,800 | 3.8% |
| 🟢 | GEV | $955.04 | 8.4 | $3,800 | 3.8% |
| 🟡 | MU | $1080.53 | 8.4 | $3,800 | 3.8% |
| 🟢 | VRT | $245.30 | 8.3 | $3,800 | 3.8% |
| 🟡 | QUBT | $9.16 | 8.3 | $3,800 | 3.8% |
| 🟡 | PL | $17.62 | 8.2 | $3,800 | 3.8% |
| 🟢 | SHOP | $145.16 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 63 positions | Total contribution: $63,000/month (63.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | LLY | $1181.89 | 7.9 | $1,000 | 1.0% |
| 🟡 | LITE | $929.04 | 7.8 | $1,000 | 1.0% |
| 🟡 | ASTS | $61.06 | 7.8 | $1,000 | 1.0% |
| 🟢 | BROS | $38.51 | 7.8 | $1,000 | 1.0% |
| 🟡 | SKHY | $186.37 | 7.8 | $1,000 | 1.0% |
| 🟡 | TSM | $451.15 | 7.7 | $1,000 | 1.0% |
| 🟡 | AMKR | $52.69 | 7.7 | $1,000 | 1.0% |
| 🟢 | HOOD | $120.82 | 7.6 | $1,000 | 1.0% |
| 🟡 | ANET | $205.70 | 7.5 | $1,000 | 1.0% |
| 🟡 | ALB | $108.25 | 7.5 | $1,000 | 1.0% |
| 🟡 | RBLX | $48.83 | 7.5 | $1,000 | 1.0% |
| 🟡 | IONQ | $44.98 | 7.5 | $1,000 | 1.0% |
| 🟡 | UBER | $69.22 | 7.5 | $1,000 | 1.0% |
| 🟢 | OKLO | $38.29 | 7.5 | $1,000 | 1.0% |
| 🟢 | CRWV | $90.13 | 7.5 | $1,000 | 1.0% |
| 🟢 | CCL | $21.79 | 7.5 | $1,000 | 1.0% |
| 🟡 | HUT | $101.54 | 7.5 | $1,000 | 1.0% |
| 🟡 | WMT | $107.59 | 7.5 | $1,000 | 1.0% |
| 🟡 | LYFT | $14.75 | 7.3 | $1,000 | 1.0% |
| 🔴 | ALAB | $360.51 | 7.3 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 43 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 15 positions | Total contribution: $-7,500/month (-7.5% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | CRCL | $93.00 | 5.8 | $-500 | 0.0% |
| 🔴 | TWLO | $299.66 | 5.8 | $-500 | 0.0% |
| 🟡 | CEG | $261.62 | 5.8 | $-500 | 0.0% |
| 🟡 | BA | $196.80 | 5.7 | $-500 | 0.0% |
| 🟢 | MMYT | $46.87 | 5.6 | $-500 | 0.0% |
| 🔴 | OKTA | $206.64 | 5.3 | $-500 | 0.0% |
| 🟢 | SMR | $8.47 | 5.3 | $-500 | 0.0% |
| 🟢 | DIS | $105.56 | 5.3 | $-500 | 0.0% |
| 🟡 | REGN | $796.02 | 5.2 | $-500 | 0.0% |
| 🟡 | PYPL | $52.60 | 5.1 | $-500 | 0.0% |
| 🟡 | PFE | $28.41 | 4.9 | $-500 | 0.0% |
| 🟢 | NVO | $38.62 | 4.7 | $-500 | 0.0% |
| 🟡 | XYZ | $76.74 | 4.5 | $-500 | 0.0% |
| 🟢 | CCJ | $88.12 | 4.5 | $-500 | 0.0% |
| 🟢 | TTD | $12.63 | 4.3 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 30 positions (32.6%)
- 🟡 YELLOW (Neutral): 54 positions (58.7%)
- 🔴 RED (Extended/Overbought): 8 positions (8.7%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.2 — VIX 15.2 sustained < 20
- **S&P 500:** 7704 (50d MA: 7632, 200d MA: 7201)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 102 | 6.92 | 50.5 | 56.3 | 43 | 🟡 NEUTRAL |
| Healthcare | 22 | 6.38 | 39.9 | 47.3 | 16 | 🟡 BUY stock/THIN premium |
| Consumer Cyclical | 33 | 6.94 | 29.7 | 31.7 | 33 | 🟡 BUY stock/THIN premium |
| Industrials | 35 | 7.36 | 44.6 | 37.0 | 25 | 🟡 NEUTRAL |
| Energy | 2 | 5.9 | 38.3 | 50.1 | 28 | 🟡 BUY stock/THIN premium |
| Consumer Defensive | 1 | 7.5 | 47.3 | 24.0 | 98 | 🟢 BUY (rich premium) |
| Utilities | 10 | 6.64 | 41.7 | 7.1 | 15 | 🟡 BUY stock/THIN premium |
| Communication Services | 37 | 7.64 | 51.9 | 29.4 | 33 | 🟡 BUY stock/THIN premium |
| Defense | 9 | 6.23 | 38.1 | 23.3 | 30 | 🟡 BUY stock/THIN premium |
| Brand-Quality (Non-AI) | 21 | 7.39 | 42.4 | 47.7 | 19 | 🟡 NEUTRAL |
| Basic Materials | 12 | 7.33 | 30.8 | 19.7 | 26 | 🟡 BUY stock/THIN premium |
| Financial Services | 36 | 6.43 | 43.0 | 44.4 | 52 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Basic Materials:** Conv 7.3/10, RSI 30.8, 52W %ile 19.7 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 26 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Cyclical:** Conv 6.9/10, RSI 29.7, 52W %ile 31.7 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 33 < 40) — not attractive for CSPs/CCs
- ✓ **Communication Services:** Conv 7.6/10, RSI 51.9, 52W %ile 29.4 — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 33 < 40)
- ✓ **Defense:** Conv 6.2/10, RSI 38.1, 52W %ile 23.3 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 30 < 40) — not attractive for CSPs/CCs
- ✓ **Healthcare:** Conv 6.4/10, RSI 39.9, 52W %ile 47.3 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 16 < 40) — not attractive for CSPs/CCs
- ✓ **Utilities:** Conv 6.6/10, RSI 41.7, 52W %ile 7.1 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 15 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Defensive:** Conv 7.5/10, RSI 47.3, 52W %ile 24.0 — 🟢 BUY — Oversold + rich premium (avg IVR 98, good for selling)
- ✓ **Energy:** Conv 5.9/10, RSI 38.3, 52W %ile 50.1 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 28 < 40) — not attractive for CSPs/CCs

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.9/10, RSI 50.5, 52W %ile 56.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Brand-Quality (Non-AI):** Conv 7.4/10, RSI 42.4, 52W %ile 47.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.4/10, RSI 44.6, 52W %ile 37.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.4/10, RSI 43.0, 52W %ile 44.4 — 🟡 MONITOR — Neutral positioning


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


### Technology (31 positions, $2,717,855) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $278,712 | $92,904 | $371,616 | 🟡 | 7.8 | 🟡 MONITOR |
| MU | $216,106 | $108,053 | $324,159 | 🟡 | 8.4 | 🟡 MONITOR |
| CRM | $95,288 | $142,932 | $238,220 | 🟡 | 6.5 | 🟡 MONITOR |
| ALAB | $180,255 | $36,051 | $216,306 | 🔴 | 7.3 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| ADBE | $71,679 | $119,465 | $191,144 | 🟡 | 6.1 | 🟡 MONITOR |
| TSM | $135,345 | $45,115 | $180,460 | 🟡 | 7.7 | 🟡 MONITOR |
| OKTA | $41,328 | $123,984 | $165,312 | 🔴 | 5.3 | 🔴 TRIM CALL (delta/assignment risk); 🟢 HOLD PUT (near max profit, unaffected — a short call gains protection in a decline, don't close it purely on crash fears) |
| MSFT | $99,586 | $49,793 | $149,379 | 🟡 | 7.2 | 🟡 MONITOR |
| TWLO | $29,966 | $89,898 | $119,864 | 🔴 | 5.8 | 🔴 TRIM CALL (delta/assignment risk); 🟢 HOLD PUT (near max profit, unaffected — a short call gains protection in a decline, don't close it purely on crash fears) |
| CRWD | $77,901 | $25,967 | $103,868 | 🔴 | 6.0 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| IBM | $68,118 | $22,706 | $90,824 | 🟡 | 6.0 | 🟡 MONITOR |
| ZS | $64,392 | $21,464 | $85,856 | 🟡 | 6.7 | 🟡 MONITOR |
| PANW | $77,984 | $0 | $77,984 | 🔴 | 6.6 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| NVDA | $67,374 | $0 | $67,374 | 🟡 | 8.8 | 🟡 MONITOR |
| SHOP | $58,064 | $0 | $58,064 | 🟢 | 8.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| XYZ | $30,696 | $15,348 | $46,044 | 🟡 | 4.5 | 🟡 MONITOR |
| UBER | $41,532 | $0 | $41,532 | 🟡 | 7.5 | 🟡 MONITOR |
| FSLR | $34,432 | $0 | $34,432 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| IONQ | $17,992 | $8,996 | $26,988 | 🟡 | 7.5 | 🟡 MONITOR |
| AMKR | $21,076 | $0 | $21,076 | 🟡 | 7.7 | 🟡 MONITOR |
| PLTR | $19,259 | $0 | $19,259 | 🟡 | 6.8 | 🟡 MONITOR |
| SKHY | $18,637 | $0 | $18,637 | 🟡 | 7.8 | 🟡 MONITOR |
| ASTS | $18,318 | $0 | $18,318 | 🟡 | 7.8 | 🟡 MONITOR |
| RBRK | $11,380 | $0 | $11,380 | 🔴 | 6.3 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| CRWV | $9,013 | $0 | $9,013 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LYFT | $1,475 | $7,375 | $8,850 | 🟡 | 7.3 | 🟡 MONITOR |
| LASR | $8,124 | $0 | $8,124 | 🟡 | 8.5 | 🟡 MONITOR |
| SONO | $0 | $7,136 | $7,136 | 🔴 | 6.0 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| CIFR | $3,620 | $0 | $3,620 | 🟡 | 6.7 | 🟡 MONITOR |
| INFY | $1,050 | $1,050 | $2,100 | 🟢 | 6.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QUBT | $916 | $0 | $916 | 🟡 | 8.3 | 🟡 MONITOR |

### Industrials (9 positions, $1,172,023) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $89,000 | $356,000 | $445,000 | 🟡 | 7.2 | 🟡 MONITOR |
| GEV | $286,512 | $95,504 | $382,016 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| BE | $133,325 | $53,330 | $186,655 | 🟡 | 7.0 | 🟡 MONITOR |
| VRT | $49,060 | $24,530 | $73,590 | 🟢 | 8.3 | 🟢 ATTRACTIVE — let run |
| RKLB | $44,166 | $0 | $44,166 | 🟡 | 7.2 | 🟡 MONITOR |
| BWXT | $27,736 | $0 | $27,736 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| KTOS | $9,404 | $0 | $9,404 | 🟢 | 8.5 | 🟢 ATTRACTIVE — let run |
| PL | $1,762 | $0 | $1,762 | 🟡 | 8.2 | 🟡 MONITOR |
| SMR | $1,694 | $0 | $1,694 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

### Communication Services (8 positions, $1,083,043) — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 33 < 40) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $311,036 | $77,759 | $388,795 | 🔴 | 7.2 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| APP | $218,729 | $93,741 | $312,470 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $114,752 | $43,032 | $157,784 | 🟡 | 7.0 | 🟡 MONITOR |
| GOOGL | $102,708 | $34,236 | $136,944 | 🟢 | 8.8 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| RBLX | $24,415 | $14,649 | $39,064 | 🟡 | 7.5 | 🟡 MONITOR |
| NBIS | $24,348 | $0 | $24,348 | 🟡 | 7.2 | 🟡 MONITOR |
| DIS | $21,112 | $0 | $21,112 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TTD | $2,526 | $0 | $2,526 | 🟢 | 4.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Healthcare (7 positions, $997,087) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 16 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LLY | $354,567 | $118,189 | $472,756 | 🟡 | 7.9 | 🟡 MONITOR |
| ISRG | $119,856 | $39,952 | $159,808 | 🟡 | 7.2 | 🟡 MONITOR |
| REGN | $79,602 | $79,602 | $159,204 | 🟡 | 5.2 | 🟡 MONITOR |
| UNH | $75,002 | $75,002 | $150,004 | 🟡 | 7.2 | 🟡 MONITOR |
| NVO | $15,448 | $7,724 | $23,172 | 🟢 | 4.7 | 🟢 ATTRACTIVE — let run |
| ZBH | $8,969 | $8,969 | $17,938 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |
| PFE | $14,205 | $0 | $14,205 | 🟡 | 4.9 | 🟡 MONITOR |

### Financial Services (9 positions, $719,945) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| MA | $226,432 | $0 | $226,432 | 🟡 | 6.6 | 🟡 MONITOR |
| COIN | $39,842 | $179,289 | $219,131 | 🟡 | 6.6 | 🟡 MONITOR |
| JPM | $67,712 | $33,856 | $101,568 | 🟡 | 6.7 | 🟡 MONITOR |
| PYPL | $15,780 | $63,120 | $78,900 | 🟡 | 5.1 | 🟡 MONITOR |
| CRCL | $27,900 | $18,600 | $46,500 | 🟢 | 5.8 | 🟢 ATTRACTIVE — let run |
| HOOD | $24,164 | $0 | $24,164 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run |
| RIOT | $9,392 | $2,348 | $11,740 | 🟡 | 7.0 | 🟡 MONITOR |
| HUT | $10,154 | $0 | $10,154 | 🟡 | 7.5 | 🟡 MONITOR |
| NU | $1,356 | $0 | $1,356 | 🟡 | 7.3 | 🟡 MONITOR |

### Consumer Cyclical (12 positions, $450,925) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 33 < 40) — not attractive for CSPs/CCs 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $104,700 | $26,175 | $130,875 | 🟡 | 6.8 | 🟡 MONITOR |
| TSLA | $75,588 | $0 | $75,588 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| AMZN | $49,876 | $24,938 | $74,814 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| BABA | $55,315 | $0 | $55,315 | 🟡 | 7.2 | 🟡 MONITOR |
| ABNB | $15,139 | $30,278 | $45,417 | 🟡 | 7.2 | 🟡 MONITOR |
| MMYT | $18,748 | $4,687 | $23,435 | 🟢 | 5.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| JD | $8,025 | $8,025 | $16,050 | 🟡 | 8.4 | 🟡 MONITOR |
| ETSY | $6,898 | $6,898 | $13,796 | 🟡 | 6.7 | 🟡 MONITOR |
| CAVA | $5,351 | $0 | $5,351 | 🟡 | 8.8 | 🟡 MONITOR |
| DKNG | $4,254 | $0 | $4,254 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| BROS | $3,851 | $0 | $3,851 | 🟢 | 7.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CCL | $2,179 | $0 | $2,179 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (5 positions, $383,174) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ULTA | $109,756 | $54,878 | $164,634 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run |
| ANET | $102,850 | $61,710 | $164,560 | 🟡 | 7.5 | 🟡 MONITOR |
| NKE | $0 | $25,193 | $25,193 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| SBUX | $18,730 | $0 | $18,730 | 🟡 | 6.1 | 🟡 MONITOR |
| ELF | $10,057 | $0 | $10,057 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |

### Defense (3 positions, $368,844) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 30 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LMT | $157,110 | $0 | $157,110 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| NOC | $101,796 | $50,898 | $152,694 | 🟡 | 6.2 | 🟡 MONITOR |
| BA | $39,360 | $19,680 | $59,040 | 🟡 | 5.7 | 🟡 MONITOR |

### Utilities (3 positions, $122,816) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 15 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $41,382 | $13,794 | $55,176 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |
| CEG | $52,324 | $0 | $52,324 | 🟡 | 5.8 | 🟡 MONITOR |
| OKLO | $15,316 | $0 | $15,316 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run |

### Basic Materials (2 positions, $106,320) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 26 < 40) — not attractive for CSPs/CCs 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $64,950 | $21,650 | $86,600 | 🟡 | 7.5 | 🟡 MONITOR |
| MP | $14,790 | $4,930 | $19,720 | 🟡 | 7.0 | 🟡 MONITOR |

### Energy (2 positions, $13,702) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 28 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| CCJ | $8,812 | $0 | $8,812 | 🟢 | 4.5 | 🟢 ATTRACTIVE — let run |
| DVN | $4,890 | $0 | $4,890 | 🟡 | 7.3 | 🟡 MONITOR |

### Consumer Defensive (1 positions, $10,759) — 🟢 BUY — Oversold + rich premium (avg IVR 98, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,759 | $0 | $10,759 | 🟡 | 7.5 | 🟡 MONITOR |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 14.1% ($1,150,894)
- 🟡 MONITOR: 63.7% ($5,192,305)
- 🟢 HEALTHY: 22.1% ($1,803,294)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟢 GREEN

**Summary:** ✅ BULL regime stable. All indicators healthy. Proceed with normal sizing.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| ⚠️ | BREADTH | 51.28205128205128 | YELLOW | 60% (caution), 50% (alert) |
| ✅ | AD_RATIO | 1.173913043478261 | GREEN | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 273 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.31% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟢 30-day crash probability: 19.1% — Action: 🟢 NORMAL: Proceed with standard sizing
- 🟡 60-day crash probability: 32.8%
- 🟡 90-day crash probability: 46.5%
- 📌 Primary risk factor: BREADTH elevated

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▄▃▄▂▂`
  - 2026-09-01: 48% → 2026-09-25: 19% (falling, -29pp)

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

- **Technology concentration:** 33.4% of notional (102 positions, $2,717,855)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $931,340 live — 84% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $180,460 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $114,737 across NBIS, CRWV, RKLB, OKLO, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ⚠️ Last check: 2026-09-08 (17 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.
- ⚠️ Over 14 days since the last real rating-action check — run /ai-capex-risk-review.

Underperformance proxy: no tracked name diverging >10pp from SPX over 7 days.


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | ADBE | P | 260.0 | 21 | 100% | $26,000 |  |
| Account A (232) | ADBE | C | 230.0 | 84 | 100% | $23,000 |  |
| Account A (232) | ADBE | P | 250.0 | 84 | 100% | $25,000 |  |
| Account A (232) | ALB | P | 110.0 | 84 | 100% | $11,000 |  |
| Account A (232) | AMZN | P | 250.0 | 84 | 100% | $25,000 |  |
| Account A (232) | ANET | C | 200.0 | 112 | 100% | $20,000 |  |
| Account A (232) | AXON | P | 540.0 | 84 | 100% | $54,000 |  |
| Account A (232) | AXON | P | 560.0 | 84 | 100% | $56,000 |  |
| Account A (232) | COIN | C | 170.0 | 21 | 100% | $17,000 |  |
| Account A (232) | COIN | C | 180.0 | 84 | 100% | $18,000 |  |
| Account A (232) | CRCL | C | 85.0 | 21 | 100% | $8,500 |  |
| Account A (232) | CRCL | C | 90.0 | 84 | 100% | $9,000 |  |
| Account A (232) | CRM | C | 185.0 | 56 | 100% | $18,500 |  |
| Account A (232) | CRM | C | 210.0 | 84 | 100% | $21,000 |  |
| Account A (232) | DIS | P | 110.0 | 84 | 100% | $22,000 |  |
| Account A (232) | ETSY | C | 60.0 | 84 | 100% | $6,000 |  |
| Account A (232) | ETSY | P | 75.0 | 84 | 100% | $7,500 |  |
| Account A (232) | META | C | 650.0 | 84 | 100% | $65,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | MP | P | 60.0 | 84 | 100% | $6,000 |  |
| Account A (232) | NFLX | P | 75.0 | 112 | 100% | $22,500 |  |
| Account A (232) | NFLX | P | 77.5 | 56 | 100% | $15,500 |  |
| Account A (232) | NFLX | P | 80.0 | 56 | 100% | $24,000 |  |
| Account A (232) | NVO | P | 50.0 | 84 | 100% | $5,000 |  |
| Account A (232) | OKTA | C | 140.0 | 56 | 100% | $14,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | PYPL | C | 47.5 | 112 | 100% | $9,500 |  |
_...and 83 more within 120 DTE (not shown)_

- **Worst case (all shown):** $3,469,000 across 108 positions
- **Realistic (>=30% prob):** $769,500 across 44 positions
- **Likely (>=50% prob):** $769,500 across 44 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 4

- META C 650.0 (Account A (232)) — 100% probability, RED heat
- OKTA C 140.0 (Account A (232)) — 100% probability, RED heat
- TWLO C 145.0 (Account C (634)) — 100% probability, RED heat
- TWLO C 150.0 (Account C (634)) — 100% probability, RED heat


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ✅ Last scan: 2026-09-18 (7 days ago)
- **NFLX:** CONCRETE WEEKLY ACTION: Account A holds 2 ITM cash-secured NFLX puts right now -- $77.50P x2 (Nov 20) and $80P x3 (Nov 20), both already ITM at $72 spot, both already flagged separately as low-premium (<$500/contract) in this week's Account A cleanup pass. This new catalyst adds real downside conviction on top of an already-poor risk/reward. Recommend reviewing both for an early close/roll before assignment risk grows further, rather than waiting for expiry. The 2 naked NFLX calls ($80C x3 Nov 20, $85C x3 Jan 15) are UNAFFECTED negatively -- a decline moves them further OTM, reducing their risk.

- **MU:** Flag for next quarterly bucket review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET) -- conviction on the reclass is now stronger than 2026-09-01, not an immediate action. Note the 09-30 earnings date if sizing any near-dated MU options this cycle.

- **AVGO:** No Tier CR trigger -- no rating-agency action, structure is clearer but not worse than already tracked in the Circular Financing Playbook. Confirmation with real mechanical detail, not escalation -- worth folding the SPV structure detail into that document's Tier CR section at its next full review.

- **ALB:** No action -- existing ITM $120P (Feb 19) already reflects the known downside; JPMorgan's own long-term target ($140) still implies recovery above current spot. Fundamentals (revenue/EPS) intact.

- **CRM:** Carried forward from 2026-09-01 -- no update this cycle.
- Open items:
  - NFLX: review the 2 ITM Nov-20 cash-secured puts ($77.50P x2, $80P x3, Account A) for an early close/roll given the Wells Fargo downgrade -- new this cycle.
  - MU: reclass conviction strengthened for next quarterly bucket review -- not urgent.


## Section 6.9: ACTIVE DECISION TRACKER


**⏳ crcl_naked_call_dec** — OPEN

1 naked short call on CRCL (0 shares owned), ITM as of 2026-09-10: $90C (Dec 18 2026). Smaller version of the same AXON/PYPL issue.
  - Live check: 1 naked ITM contract(s) remaining (target: 0)

**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 113.7998606338501
  - Live: macro_risk_level = GREEN

**⏳ be_puts_reduction** — OPEN

Reduce BE put exposure to zero over the next ~10 days (target: 2026-09-20) by closing/rolling out of all 6 open BE put legs across every account. BE is RED heat, RSI 77-81 (overbought/extended), and is the most widely-held name in the book -- also carries a naked short-call pair against it in Account A/Fidelity Rahul (no BE shares owned anywhere). Baseline as of 2026-09-10: Account A $170P (Jan 15 2027) x2 [Jan+Feb], Account B $180P (Feb 19 2027), Fidelity (Rahul) $190P (Jan 15 2027), Fidelity (Rajul - Rollover IRA) $200P (Jun 17 2027), Robinhood (Traditional) $180P (Jun 17 2027). Trader confirmed 2026-09-10 this should cover ALL open BE puts (not just the near-dated ones) -- an initial "Dec 2026 and before" framing didn't match any real BE put, since the earliest is Jan 15 2027.
KNOWN GAP: the automated check only sees 5 of these 6 legs -- the Robinhood (Traditional) $180P (Jun 17 2027) has an option-type parsing gap in that account's transaction reconstruction and won't count toward the live total below. This entry will show RESOLVED once the other 5 close even if that 6th one is still open -- manually confirm the Robinhood leg separately before treating BE exposure as fully closed.
  - Live check: 4 leg(s) open now (baseline was 6), target: 0

**Resolved (collapsed — see `data/active_decisions.yaml` for full history):**
  - ✅ account_a_800k_4week_plan — CLEARED (2026-09-21)
  - ✅ axon_sept18_roll_450c — RESOLVED (2026-09-18)
  - ✅ pypl_naked_calls_cleanup — RESOLVED (2026-09-21)



## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-8,700 to $-8,700 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (2 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $2,000/month contribution from MODERATE conviction positions
- Names: OKTA, TWLO (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (30 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 30 healthy positions contribute $30,000/month baseline (expected)
- ✅ 30 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (7 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 7 Tier 1 entries = $26,600/month; closes gap from $-8,700 to $-35,300 (26.6% closure)
  - APP: Conv 9.1/10 | RSI 49.5 | Value $312,470 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GOOGL: Conv 8.8/10 | RSI 50.1 | Value $136,944 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - KTOS: Conv 8.5/10 | RSI 43.5 | Value $9,404
  - GEV: Conv 8.4/10 | RSI 52.4 | Value $382,016
  - NKE: Conv 8.4/10 | RSI 26.8 | Value $25,193

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 92
- 🔴 Critical actions: 0 closes + 2 monitors
- 🟡 Yellow cautions: 52
- 🟢 Green healthy: 30
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $-8,700 (-8.7% below target)
- After closes: $-8,700 (saves ~0.0%)
- After new Tier 1 entries: $-35,300 (26.6% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-25 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_