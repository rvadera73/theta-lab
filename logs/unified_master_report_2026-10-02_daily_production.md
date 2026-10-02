# UNIFIED MASTER REPORT — DAILY (327 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** October 02, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,415,485
- **Total notional exposure:** $7,981,998
- **Total option requirement:** $2,773,706
- **Positions with short puts:** 87
- **Positions with short calls:** 52
- **YTD Net Premium:** $362,543 (live from transactions)
- **Month-to-Date Premium:** $21,053
- **Snapshot currency:** 2026-08-22

### Two Lenses on Monthly Performance

_(both derived from your transaction history)_

#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]

| Account | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | YTD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Account A (232) | 10,255 | 12,483 | 23,800 | 20,880 | -1,244 | -2,884 | 20,362 | 50,309 | 67,164 | 15,954 | 217,079 |
| Account B (275) | 31 | 3,322 | 1,546 | 4,894 | 9,709 | 3,948 | 575 | 3,476 | 7,497 | 1,967 | 36,965 |
| Account C (634) | 31 | 934 | 449 | 1,959 | 4,435 | 1,321 | 2,286 | 6,028 | 6,308 | 0 | 23,751 |
| Fidelity (Rahul) | 17 | 1,824 | 1,231 | 5,580 | 4,947 | 10,629 | 5,151 | 3,339 | 11,763 | 0 | 44,481 |
| Fidelity (Rajul — Rollover IRA) | 0 | 0 | 0 | 944 | 932 | 0 | 667 | 3,508 | 280 | 3,132 | 9,463 |
| Fidelity (Rajul — Roth IRA) | 0 | 0 | 0 | 95 | 189 | 1,028 | 1,326 | 1,196 | 0 | 0 | 3,834 |
| Robinhood (Individual) | 0 | 107 | 0 | 0 | 205 | -9 | 0 | 609 | 350 | 0 | 1,262 |
| Robinhood (Traditional IRA) | 0 | 518 | 816 | 6,275 | 2,879 | 2,087 | 517 | 5,573 | 7,043 | 0 | 25,708 |
| **TOTAL** | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 100,405 | 21,053 | 362,543 |
| Gross SOLD (STO, opened this month) | 181,739 | 68,408 | 199,758 | 324,125 | 349,672 | 243,331 | 135,826 | 242,546 | 233,320 | 38,706 | 2,017,431 |
| Net REALIZED (FIFO, closed this month) | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 100,405 | 21,053 | 362,543 |

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
| Account A (232) | $403,000 | 16.7% | $5,515,222 | $992,740 | Margin | 🔴 OVER CAP | $33,085 | ✅ $-2,712 |
| Account B (275) | $261,000 | 10.8% | $373,155 | $316,050 | Cash-Sec | 🟠 COVERAGE GAP | $9,595 | ✅ $-786 |
| Account C (634) | $256,067 | 10.6% | $342,965 | $213,150 | Cash-Sec | ⚠️ WATCH | $9,413 | ✅ $-771 |
| Fidelity (Rahul) | $563,432 | 23.3% | $693,264 | $615,718 | Cash-Sec | 🟠 COVERAGE GAP | $20,712 | ✅ $-1,698 |
| Fidelity (Rajul — Roth IRA) | $44,942 | 1.9% | $53,419 | $52,208 | Cash-Sec | 🟠 COVERAGE GAP | $1,652 | ✅ $-135 |
| Fidelity (Rajul — Rollover IRA) | $141,349 | 5.9% | $176,686 | $163,700 | Cash-Sec | 🟠 COVERAGE GAP | $5,196 | ✅ $-426 |
| Vanguard (Rahul) | $320,492 | 13.3% | $462,677 | $420,140 | Cash-Sec | 🟠 COVERAGE GAP | $11,782 | ✅ $-966 |
| Robinhood (Individual) | $13,000 | 0.5% | $26,874 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $478 | ✅ $-39 |
| Robinhood (Traditional IRA) | $220,000 | 9.1% | $337,735 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,087 | ✅ $-663 |
| Fidelity 401K (Rahul) | $192,200 | 8.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,415,485 | 100.0% | $7,981,998 | $2,773,706 |  |  |  |  |

- **Account A (232):** 173 option positions | Monthly target: $33,085 | Equity: ADBE 300sh, APP 100sh, AXON 200sh, COIN 200sh, CRCL 100sh +15 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 20 option positions | Monthly target: $9,595 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🟠 COVERAGE GAP reading above
- **Account C (634):** 21 option positions | Monthly target: $9,413 | Equity: ABNB 100sh, NKE 100sh, PL 100sh, TWLO 324sh
- **Fidelity (Rahul):** 41 option positions | Monthly target: $20,712 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,652 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
- **Fidelity (Rajul — Rollover IRA):** 10 option positions | Monthly target: $5,196
- **Vanguard (Rahul):** 28 option positions | Monthly target: $11,782
  - ⚠️ Balance as of 2026-07-31 (63 days ago) — re-confirm if the 🟠 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $478 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 22 option positions | Monthly target: $8,087
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (63 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (124 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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

- Target (10 months): $1,000,000
- Actual YTD: $362,543.0
- Gap to close: $637,457.0 (63.7%)
- Monthly average (YTD): $36,254
- Monthly average needed: $100,000
- Monthly gap: $-8,200

**Position tier distribution → gap closure:**

- Tier 1 (14 positions): $53,200/month (53% of $100,000 target)
- Tier 2 (62 positions): $62,000/month (62% of target)
- Tier 3 (14 positions): $-7,000/month (-7% drag)
- Current total: 90 positions = $108,200/month (108% of target)

**Gap closure path:**

- To hit $100,000 target: Need 0 more Tier 1 positions
- Alternative: Scale existing OR exit 5 worst Tier 3 positions
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

- **Total open positions:** 327
- **Unique tickers:** 90
- **Active accounts:** 10
- **Data currency:** 2026-10-02
- **Live prices:** 90 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (14 positions): $53,200/month — each contributes $3,800/month (4.2% of $100,000)
- Tier 2 (62 positions): $62,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (14 positions): $-7,000/month — each drags -$500/month (-0.6% of target)
- Portfolio: 108,200/month (108% of target) — Need $-8,200 more

**HIGH (Tier 1: 8-10) conviction** — 14 positions | Total contribution: $53,200/month (53.2% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | BROS | $38.77 | 9.0 | $3,800 | 3.8% |
| 🟡 | MU | $1081.89 | 8.6 | $3,800 | 3.8% |
| 🟡 | GEV | $986.63 | 8.5 | $3,800 | 3.8% |
| 🟡 | NVDA | $236.43 | 8.4 | $3,800 | 3.8% |
| 🟡 | ONDS | $7.22 | 8.4 | $3,800 | 3.8% |
| 🟡 | LLY | $1137.87 | 8.2 | $3,800 | 3.8% |
| 🟡 | AMKR | $56.08 | 8.2 | $3,800 | 3.8% |
| 🟡 | LASR | $40.60 | 8.2 | $3,800 | 3.8% |
| 🟡 | PL | $17.36 | 8.1 | $3,800 | 3.8% |
| 🟡 | CAVA | $54.89 | 8.1 | $3,800 | 3.8% |
| 🟢 | APP | $271.58 | 8.0 | $3,800 | 3.8% |
| 🟡 | ANET | $206.40 | 8.0 | $3,800 | 3.8% |
| 🟡 | IONQ | $44.99 | 8.0 | $3,800 | 3.8% |
| 🟢 | VRT | $252.68 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 62 positions | Total contribution: $62,000/month (62.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | MSFT | $515.04 | 7.9 | $1,000 | 1.0% |
| 🔴 | ALAB | $356.14 | 7.8 | $1,000 | 1.0% |
| 🔴 | PLTR | $190.38 | 7.8 | $1,000 | 1.0% |
| 🟡 | QBTS | $16.48 | 7.8 | $1,000 | 1.0% |
| 🟡 | NU | $13.09 | 7.6 | $1,000 | 1.0% |
| 🟡 | LYFT | $15.26 | 7.5 | $1,000 | 1.0% |
| 🟢 | GOOGL | $343.37 | 7.5 | $1,000 | 1.0% |
| 🟡 | TSM | $473.66 | 7.5 | $1,000 | 1.0% |
| 🟡 | CRM | $234.82 | 7.4 | $1,000 | 1.0% |
| 🟡 | MP | $46.99 | 7.4 | $1,000 | 1.0% |
| 🟢 | KTOS | $42.99 | 7.4 | $1,000 | 1.0% |
| 🟢 | NKE | $33.17 | 7.3 | $1,000 | 1.0% |
| 🟡 | JD | $25.75 | 7.3 | $1,000 | 1.0% |
| 🟡 | UBER | $67.69 | 7.3 | $1,000 | 1.0% |
| 🟢 | SHOP | $152.13 | 7.3 | $1,000 | 1.0% |
| 🟡 | ALB | $103.45 | 7.2 | $1,000 | 1.0% |
| 🟡 | AXON | $411.86 | 7.2 | $1,000 | 1.0% |
| 🔴 | LITE | $1087.99 | 7.2 | $1,000 | 1.0% |
| 🟡 | UNH | $367.79 | 7.2 | $1,000 | 1.0% |
| 🟢 | AMZN | $250.85 | 7.2 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 42 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 14 positions | Total contribution: $-7,000/month (-7.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🔴 | OKTA | $214.40 | 5.8 | $-500 | 0.0% |
| 🟡 | CRCL | $81.74 | 5.8 | $-500 | 0.0% |
| 🔴 | TWLO | $295.18 | 5.8 | $-500 | 0.0% |
| 🟢 | PYPL | $52.84 | 5.6 | $-500 | 0.0% |
| 🔴 | PANW | $403.00 | 5.6 | $-500 | 0.0% |
| 🟢 | TSLA | $372.63 | 5.6 | $-500 | 0.0% |
| 🟡 | COIN | $182.08 | 5.5 | $-500 | 0.0% |
| 🟡 | PFE | $27.48 | 5.4 | $-500 | 0.0% |
| 🔴 | SONO | $17.98 | 5.4 | $-500 | 0.0% |
| 🟢 | SMR | $7.86 | 5.3 | $-500 | 0.0% |
| 🟢 | NVO | $37.24 | 4.7 | $-500 | 0.0% |
| 🟡 | CCJ | $85.43 | 4.5 | $-500 | 0.0% |
| 🟢 | TTD | $11.85 | 4.3 | $-500 | 0.0% |
| 🟢 | XYZ | $74.49 | 4.2 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 34 positions (37.8%)
- 🟡 YELLOW (Neutral): 47 positions (52.2%)
- 🔴 RED (Extended/Overbought): 9 positions (10.0%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.7 — VIX 15.7 sustained < 20
- **S&P 500:** 7725 (50d MA: 7658, 200d MA: 7226)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg Yield% | Signal |
|---|---|---|---|---|---|---|
| Technology | 115 | 7.05 | 57.6 | 60.5 | 27% | 🟡 NEUTRAL |
| Healthcare | 23 | 6.39 | 37.4 | 39.0 | 13% | 🟡 BUY stock/THIN premium |
| Consumer Cyclical | 32 | 6.76 | 36.3 | 33.9 | 23% | 🟢 BUY (rich premium) |
| Industrials | 32 | 7.06 | 51.2 | 38.1 | 34% | 🟡 NEUTRAL |
| Energy | 1 | 4.5 | 27.8 | 13.5 | 18% | 🟡 MONITOR |
| Consumer Defensive | 2 | 6.0 | 34.0 | 14.5 | 8% | 🟡 BUY stock/THIN premium |
| Utilities | 11 | 6.25 | 45.8 | 6.8 | 28% | 🟢 BUY (rich premium) |
| Communication Services | 38 | 6.81 | 27.7 | 19.8 | 26% | 🟢 BUY (rich premium) |
| Defense | 9 | 6.6 | 25.3 | 16.4 | 10% | 🟡 BUY stock/THIN premium |
| Brand-Quality (Non-AI) | 10 | 6.95 | 32.0 | 22.4 | 15% | 🟢 BUY (rich premium) |
| Crypto Mining | 9 | 6.26 | 46.9 | 40.3 | 49% | 🟡 NEUTRAL |
| Basic Materials | 12 | 7.27 | 36.7 | 13.7 | 27% | 🟢 BUY (rich premium) |
| Financial Services | 33 | 6.05 | 39.3 | 33.6 | 26% | 🟢 BUY (rich premium) |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Basic Materials:** Conv 7.3/10, RSI 36.7, 52W %ile 13.7 — 🟢 BUY — Oversold + rich premium (avg real yield 27%, good for selling)
- ✓ **Consumer Cyclical:** Conv 6.8/10, RSI 36.3, 52W %ile 33.9 — 🟢 BUY — Oversold + rich premium (avg real yield 23%, good for selling)
- ✓ **Communication Services:** Conv 6.8/10, RSI 27.7, 52W %ile 19.8 — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling)
- ✓ **Defense:** Conv 6.6/10, RSI 25.3, 52W %ile 16.4 — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 10% < 15%) — not attractive for CSPs/CCs
- ✓ **Financial Services:** Conv 6.0/10, RSI 39.3, 52W %ile 33.6 — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling)
- ✓ **Healthcare:** Conv 6.4/10, RSI 37.4, 52W %ile 39.0 — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 13% < 15%) — not attractive for CSPs/CCs
- ✓ **Brand-Quality (Non-AI):** Conv 7.0/10, RSI 32.0, 52W %ile 22.4 — 🟢 BUY — Oversold + rich premium (avg real yield 15%, good for selling)
- ✓ **Utilities:** Conv 6.2/10, RSI 45.8, 52W %ile 6.8 — 🟢 BUY — Oversold + rich premium (avg real yield 28%, good for selling)
- ✓ **Consumer Defensive:** Conv 6.0/10, RSI 34.0, 52W %ile 14.5 — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 8% < 15%) — not attractive for CSPs/CCs

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 7.0/10, RSI 57.6, 52W %ile 60.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.1/10, RSI 51.2, 52W %ile 38.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 4.5/10, RSI 27.8, 52W %ile 13.5 — 🟡 MONITOR — Low conviction across sector
- ◇ **Crypto Mining:** Conv 6.3/10, RSI 46.9, 52W %ile 40.3 — 🟡 MONITOR — Neutral positioning

### Hot Trend Verticals — cross-sector thematic exposure

_Informational only — never a CLOSE/TRIM/ENTER gate. Shows how much of the book leans on each real market theme, independent of GICS sector._

| Vertical | Tickers | Notional | Avg Conv |
|---|---|---|---|
| AI/Pick-and-Shovel | ALAB, AMKR, LITE, MU, NVDA, TSM | $1,275,875 | 8.0 |
| AI/Hyperscaler | AMZN, GOOGL, META, MSFT | $731,529 | 7.2 |
| AI/Data-Center-Infra | ANET, CRWV, GEV, VRT | $665,210 | 7.9 |
| AI/SaaS | ADBE, CRM, PLTR, TWLO | $570,268 | 6.8 |
| AI/Security | CRWD, OKTA, PANW, ZS | $514,906 | 5.8 |
| Defense/Geopolitical | BA, LMT, NOC, RKLB | $381,697 | 6.7 |
| GLP-1 | LLY, NVO | $371,153 | 6.4 |
| Defense/AI | AXON, KTOS | $296,899 | 7.3 |
| Crypto | CIFR, COIN, CRCL, HUT, RIOT | $285,385 | 6.1 |
| Global Brand | BABA, INFY, JD, MMYT, NKE, NU, SBUX, TSM | $279,742 | 7.0 |
| AI/Nuclear-Power | BWXT, CCJ, CEG, OKLO, SMR, VST | $183,324 | 5.9 |
| US Brand | ULTA | $162,162 | 6.4 |
| Space | ASTS, PL, RKLB | $50,442 | 7.2 |
| AI/Quantum | IONQ, QUBT | $27,834 | 7.3 |

_53 of 90 held tickers carry at least one vertical tag; 37 carry none (expected, not a gap — see trend_verticals.py)._


## Section 5: POSITION DISTRIBUTION BY ACCOUNT

- **Account A (232):** 173 positions (52.9%) `██████████████████████████`
- **Fidelity (Rahul):** 41 positions (12.5%) `██████`
- **Vanguard (Rahul):** 28 positions (8.6%) `████`
- **Robinhood (Traditional IRA):** 22 positions (6.7%) `███`
- **Account C (634):** 21 positions (6.4%) `███`
- **Account B (275):** 20 positions (6.1%) `███`
- **Fidelity (Rajul — Rollover IRA):** 10 positions (3.1%) `█`
- **Fidelity (Rajul — Roth IRA):** 8 positions (2.4%) `█`
- **Robinhood (Individual):** 4 positions (1.2%) ``
- **Fidelity 401K (Rahul):** 0 positions (0.0%) ``


## Section 6: POSITION HEAT MATRIX BY SECTOR — Sector -> Symbol, Put/Call/Total Value, Heat, Suggestion


### Priority Actions (bottom-up, CLOSE/TRIM/ENTER only)

| Symbol | Verb | Sector | Action | Detail |
|---|---|---|---|---|
| BROS | ENTER | Consumer Cyclical | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| CRWD | TRIM | Technology | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| OKTA | TRIM | Technology | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -1%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PANW | TRIM | Technology | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~28% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| RBRK | TRIM | Technology | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +2%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| SONO | TRIM | Technology | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| TWLO | TRIM | Technology | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -11%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |

### Top 10 GREEN — best-positioned

| Symbol | Sector | Conv | Notional | Action | Detail |
|---|---|---|---|---|---|
| BROS | Consumer Cyclical | 9.0 | $3,877 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| APP | Communication Services | 8.0 | $271,580 | 🟢 HOLD — let run | RSI/heat: Dropped -14% in 7 days AND -40% below its 200-day average — genuinely beaten down. Real yield-on-capital ~36% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| VRT | Industrials | 8.0 | $75,805 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GOOGL | Communication Services | 7.5 | $137,348 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| KTOS | Industrials | 7.4 | $8,597 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~30% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| NKE | Brand-Quality (Non-AI) | 7.3 | $23,216 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 7 covered (700 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| SHOP | Technology | 7.3 | $76,065 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~28% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| AMZN | Consumer Cyclical | 7.2 | $75,256 | 🟡 WATCH: technicals attractive, but a qualitative flag is unresolved | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-10-02): New (FT, reported 2026-10-01/02): Amazon in talks to move ~$8B of Nvidia Grace Blackwell chips (deployed across 12+ US data centers, 5 states) into a special-purpose vehicle, then lease them back -- same "SPV buys chips, leases back to the hyperscaler" mechanical pattern as the AVGO/Anthropic struct |
| ETSY | Consumer Cyclical | 7.2 | $14,505 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| CRWV | Technology | 7.2 | $8,988 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Top 10 RED — most concerning

| Symbol | Sector | Conv | Notional | Action | Detail |
|---|---|---|---|---|---|
| LITE | Technology | 7.2 | $435,196 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Spiked 16% in 7 days AND 46% above its 200-day average — genuinely extended, not just a pop. Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| OKTA | Technology | 5.8 | $192,960 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -1%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| ALAB | Technology | 7.8 | $178,072 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +9%. Real yield-on-capital ~47% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CRWD | Technology | 6.0 | $161,844 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| TWLO | Technology | 5.8 | $88,555 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -11%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PANW | Technology | 5.6 | $80,600 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~28% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| PLTR | Technology | 7.8 | $57,114 | 🟡 WATCH: RED heat, but conviction 7.8 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| RBRK | Technology | 6.3 | $11,751 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +2%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| SONO | Technology | 5.4 | $7,190 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |

### Technology (33 positions, $3,118,903) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 9%-57%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LITE | $326,397 | $108,799 | $435,196 | 🔴 | 7.2 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Spiked 16% in 7 days AND 46% above its 200-day average — genuinely extended, not just a pop. Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| MU | $324,567 | $108,189 | $432,756 | 🟡 | 8.6 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Technically extended (+59% vs 200-day average), but analyst upside still +41% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~26% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-10-02): RESOLVED (earnings printed) -- Q4 FY26 reported 2026-09-30: revenue $54.2B (+31% QoQ, +379% YoY), EPS $33.42 vs $31.50 est (+6.1% beat), gross margin 87% (+210bps QoQ), operating margin 82%. Full FY26 revenue $133.2B (+256% YoY), first year DRAM revenue topped $100B. 26 strategic customer agreements |
| CRM | $93,926 | $140,889 | $234,815 | 🟡 | 7.4 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: RSI 29 approaching oversold (30-); 72% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 5 covered call(s) (500 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-10-02): 2026-09-01 finding (Salesforce/Anthropic "Claudeforce" partnership) not re-checked this pass -- carried forward, no new SA headline this cycle contradicting it. |
| OKTA | $64,320 | $128,640 | $192,960 | 🔴 | 5.8 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -1%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| ADBE | $71,169 | $118,615 | $189,784 | 🟡 | 6.1 | 🟡 WATCH: strangle (2C/3P) — call side uncapped if it rallies | RSI/heat: RSI 26 approaching oversold (30-); 27% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 3 covered call(s) (300 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ANET | $123,843 | $61,921 | $185,764 | 🟡 | 8.0 | 🟡 WATCH: strangle (3C/6P) — call side uncapped if it rallies | RSI/heat: Technically extended (+30% vs 200-day average), but analyst upside still +17% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~23% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 3 naked call(s) (uncapped upside if it rallies), AND 6 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ALAB | $142,458 | $35,614 | $178,072 | 🔴 | 7.8 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +9%. Real yield-on-capital ~47% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CRWD | $134,870 | $26,974 | $161,844 | 🔴 | 6.0 | 🔴 TRIM CALL / HOLD PUT (call has delta/assignment risk; put near max profit, unaffected) | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -12%. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| MSFT | $103,008 | $51,504 | $154,512 | 🟡 | 7.9 | 🟡 WATCH: 81% of 52-week range approaching the high extreme (90%+) | RSI/heat: 81% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| TSM | $94,732 | $47,366 | $142,098 | 🟡 | 7.5 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Technically extended (+23% vs 200-day average), but analyst upside still +17% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| IBM | $44,478 | $44,478 | $88,957 | 🟢 | 6.6 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| TWLO | $0 | $88,555 | $88,555 | 🔴 | 5.8 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -11%. Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PANW | $80,600 | $0 | $80,600 | 🔴 | 5.6 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%. Real yield-on-capital ~28% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| ZS | $59,627 | $19,876 | $79,502 | 🟢 | 6.0 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| SHOP | $76,065 | $0 | $76,065 | 🟢 | 7.3 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~28% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| NVDA | $70,929 | $0 | $70,929 | 🟡 | 8.4 | 🟡 WATCH: Technically extended (+18% vs 200-day average), but analyst upside still +39% — may be fundamentally supported, watch rather than force a close | RSI/heat: Technically extended (+18% vs 200-day average), but analyst upside still +39% — may be fundamentally supported, watch rather than force a close. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| PLTR | $57,114 | $0 | $57,114 | 🔴 | 7.8 | 🟡 WATCH: RED heat, but conviction 7.8 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| FSLR | $52,755 | $0 | $52,755 | 🟢 | 6.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~27% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| XYZ | $29,796 | $14,898 | $44,694 | 🟢 | 4.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~21% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| UBER | $40,614 | $0 | $40,614 | 🟡 | 7.3 | 🟡 WATCH: RSI/range reads oversold, but -9% vs its 200-day average — verify before treating as attractive | RSI/heat: RSI/range reads oversold, but -9% vs its 200-day average — verify before treating as attractive. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| IONQ | $17,996 | $8,998 | $26,994 | 🟡 | 8.0 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: RSI/range reads overbought, but +3% vs its 200-day average — watch, don't force a close. Real yield-on-capital ~39% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| SKHY | $19,442 | $0 | $19,442 | 🟡 | 6.6 | 🟡 WATCH: RSI/range reads overbought, but n/a (< 200d history) vs its 200-day average — watch, don't force a close | RSI/heat: RSI/range reads overbought, but n/a (< 200d history) vs its 200-day average — watch, don't force a close. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| ASTS | $17,439 | $0 | $17,439 | 🟡 | 6.7 | 🟡 WATCH: 10% of 52-week range approaching the low extreme (10%-) | RSI/heat: 10% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~41% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| AMKR | $16,824 | $0 | $16,824 | 🟡 | 8.2 | 🟡 WATCH: RSI 74 approaching overbought (70+) | RSI/heat: RSI 74 approaching overbought (70+). Real yield-on-capital ~38% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| RBRK | $11,751 | $0 | $11,751 | 🔴 | 6.3 | 🔴 TRIM PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +2%. Real yield-on-capital ~31% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| LYFT | $1,526 | $7,628 | $9,153 | 🟡 | 7.5 | 🟡 WATCH: 21% of 52-week range approaching the low extreme (10%-) | RSI/heat: 21% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 5 covered (500 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| CRWV | $8,988 | $0 | $8,988 | 🟢 | 7.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| LASR | $8,121 | $0 | $8,121 | 🟡 | 8.2 | 🟡 WATCH: 21% of 52-week range approaching the low extreme (10%-) | RSI/heat: 21% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~42% annualized (rich premium for CSPs/CCs, ~10% OTM/77DTE). No qualitative flag on file. |
| SONO | $0 | $7,190 | $7,190 | 🔴 | 5.4 | 🔴 TRIM CALL | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +3%. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| INFY | $1,102 | $1,102 | $2,205 | 🟢 | 6.5 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| QBTS | $1,648 | $0 | $1,648 | 🟡 | 7.8 | 🟡 WATCH: 11% of 52-week range approaching the low extreme (10%-) | RSI/heat: 11% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| QUBT | $840 | $0 | $840 | 🟡 | 6.7 | 🟡 WATCH: 11% of 52-week range approaching the low extreme (10%-) | RSI/heat: 11% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~44% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| ONDS | $722 | $0 | $722 | 🟡 | 8.4 | 🟡 WATCH: 22% of 52-week range approaching the low extreme (10%-) | RSI/heat: 22% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~57% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Industrials (9 positions, $1,033,818) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| GEV | $295,989 | $98,663 | $394,652 | 🟡 | 8.5 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: RSI/range reads overbought, but +8% vs its 200-day average — watch, don't force a close. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| AXON | $82,372 | $205,930 | $288,302 | 🟡 | 7.2 | 🟡 WATCH: strangle (3C/2P) — call side uncapped if it rallies | RSI/heat: RSI 25 approaching oversold (30-); 17% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~33% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 2 covered call(s) (200 sh owned), 3 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BE | $146,580 | $58,632 | $205,212 | 🟡 | 6.0 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: 79% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~44% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| VRT | $50,537 | $25,268 | $75,805 | 🟢 | 8.0 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| RKLB | $29,530 | $0 | $29,530 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~41% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| BWXT | $26,676 | $0 | $26,676 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~20% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| KTOS | $8,597 | $0 | $8,597 | 🟢 | 7.4 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~30% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| PL | $1,736 | $1,736 | $3,473 | 🟡 | 8.1 | 🟡 WATCH: 17% of 52-week range approaching the low extreme (10%-) | RSI/heat: 17% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~39% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| SMR | $1,571 | $0 | $1,571 | 🟢 | 5.3 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~44% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Communication Services (6 positions, $968,192) — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling) 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 12%-37%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| META | $291,530 | $72,883 | $364,413 | 🟡 | 6.0 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: 81% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~16% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| APP | $190,106 | $81,474 | $271,580 | 🟢 | 8.0 | 🟢 HOLD — let run | RSI/heat: Dropped -14% in 7 days AND -40% below its 200-day average — genuinely beaten down. Real yield-on-capital ~36% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NFLX | $107,136 | $40,176 | $147,312 | 🟢 | 7.0 | 🟡 WATCH: technicals attractive, but a qualitative flag is unresolved | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~15% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 6 naked call(s) (uncapped upside if it rallies), AND 16 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-10-02): STILL OPEN, now 2 weeks stale. 2026-09-18 Wells Fargo downgrade (Underweight, PT $57) thesis has played out on price -- spot fell from ~$72 (09-18) to ~$67 today, confirming the bearish read rather than reversing it. Position has grown since the original flag: now 16 short puts + 6 naked calls (was  |
| GOOGL | $103,011 | $34,337 | $137,348 | 🟢 | 7.5 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| RBLX | $29,960 | $12,840 | $42,800 | 🟢 | 6.7 | 🟢 HOLD — let run | RSI/heat: Dropped -13% in 7 days AND -23% below its 200-day average — genuinely beaten down. Real yield-on-capital ~35% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 7 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| TTD | $4,740 | $0 | $4,740 | 🟢 | 4.3 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~37% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Healthcare (7 positions, $867,573) — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 13% < 15%) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LLY | $227,574 | $113,787 | $341,361 | 🟡 | 8.2 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: 70% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ISRG | $118,830 | $39,610 | $158,440 | 🟡 | 6.8 | 🟡 WATCH: 25% of 52-week range approaching the low extreme (10%-) | RSI/heat: 25% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~15% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| UNH | $73,558 | $73,558 | $147,116 | 🟡 | 7.2 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: RSI 30 approaching oversold (30-). Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| REGN | $72,920 | $72,920 | $145,840 | 🟡 | 6.5 | 🟡 WATCH: strangle (1C/1P) — call side uncapped if it rallies | RSI/heat: RSI 29 approaching oversold (30-). Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NVO | $18,620 | $11,172 | $29,792 | 🟢 | 4.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PFE | $27,475 | $0 | $27,475 | 🟡 | 5.4 | 🟡 WATCH: 71% of 52-week range approaching the high extreme (90%+) | RSI/heat: 71% of 52-week range approaching the high extreme (90%+). Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| ZBH | $8,775 | $8,775 | $17,549 | 🟡 | 7.2 | 🟡 WATCH: RSI 27 approaching oversold (30-) | RSI/heat: RSI 27 approaching oversold (30-). Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |

### Financial Services (7 positions, $683,627) — 🟢 BUY — Oversold + rich premium (avg real yield 26%, good for selling) ⚠️ MIXED — individual real yield ranges 6%-41%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| MA | $220,504 | $0 | $220,504 | 🟡 | 6.9 | 🟡 WATCH: RSI 29 approaching oversold (30-) | RSI/heat: RSI 29 approaching oversold (30-). Real yield-on-capital ~6% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| COIN | $36,416 | $182,080 | $218,496 | 🟡 | 5.5 | 🟡 WATCH: strangle (8C/2P) — call side uncapped if it rallies | RSI/heat: 16% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~34% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 2 covered call(s) (200 sh owned), 8 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| JPM | $66,235 | $33,117 | $99,352 | 🟡 | 6.7 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: RSI 29 approaching oversold (30-). Real yield-on-capital ~7% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| PYPL | $15,852 | $63,408 | $79,260 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~16% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 11 covered call(s) (1100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CRCL | $24,522 | $16,348 | $40,870 | 🟡 | 5.8 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 29% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~41% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| HOOD | $22,528 | $0 | $22,528 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~32% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| NU | $2,617 | $0 | $2,617 | 🟡 | 7.6 | 🟡 WATCH: 24% of 52-week range approaching the low extreme (10%-) | RSI/heat: 24% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Consumer Cyclical (12 positions, $449,928) — 🟢 BUY — Oversold + rich premium (avg real yield 23%, good for selling) 🟡 possible macro exposure (weak historical signal, see Section 6.5) ⚠️ MIXED — individual real yield ranges 12%-40%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| EXPE | $105,758 | $26,439 | $132,197 | 🟡 | 6.8 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: RSI 29 approaching oversold (30-). Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| AMZN | $50,171 | $25,085 | $75,256 | 🟢 | 7.2 | 🟡 WATCH: technicals attractive, but a qualitative flag is unresolved | RSI/heat: Neutral positioning. Real yield-on-capital ~12% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-10-02): New (FT, reported 2026-10-01/02): Amazon in talks to move ~$8B of Nvidia Grace Blackwell chips (deployed across 12+ US data centers, 5 states) into a special-purpose vehicle, then lease them back -- same "SPV buys chips, leases back to the hyperscaler" mechanical pattern as the AVGO/Anthropic struct |
| TSLA | $74,526 | $0 | $74,526 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~16% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| BABA | $52,682 | $0 | $52,682 | 🟡 | 6.0 | 🟡 WATCH: 14% of 52-week range approaching the low extreme (10%-) | RSI/heat: 14% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~17% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| ABNB | $16,333 | $32,666 | $48,999 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~15% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| MMYT | $18,020 | $4,505 | $22,525 | 🟢 | 6.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~40% annualized (rich premium for CSPs/CCs, ~10% OTM/77DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| JD | $7,724 | $7,724 | $15,447 | 🟡 | 7.3 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 11% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~14% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ETSY | $7,253 | $7,253 | $14,505 | 🟢 | 7.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~24% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| CAVA | $5,489 | $0 | $5,489 | 🟡 | 8.1 | 🟡 WATCH: 21% of 52-week range approaching the low extreme (10%-) | RSI/heat: 21% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~32% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| BROS | $3,877 | $0 | $3,877 | 🟢 | 9.0 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~29% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| CCL | $2,560 | $0 | $2,560 | 🟡 | 7.2 | 🟡 WATCH: Spiked 17% in 7 days but only -6% vs its 200-day average — short-term move, not structurally extended | RSI/heat: Spiked 17% in 7 days but only -6% vs its 200-day average — short-term move, not structurally extended. Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| DKNG | $1,865 | $0 | $1,865 | 🟢 | 6.9 | 🟢 HOLD — let run | RSI/heat: Dropped -12% in 7 days AND -27% below its 200-day average — genuinely beaten down. Real yield-on-capital ~38% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Defense (3 positions, $352,167) — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 10% < 15%) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LMT | $150,970 | $0 | $150,970 | 🟡 | 6.8 | 🟡 WATCH: RSI 25 approaching oversold (30-); 26% of 52-week range approaching the low extreme (10%-) | RSI/heat: RSI 25 approaching oversold (30-); 26% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~8% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| NOC | $95,642 | $47,821 | $143,463 | 🟢 | 6.6 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BA | $38,489 | $19,245 | $57,734 | 🟡 | 6.4 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: 20% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Brand-Quality (Non-AI) (3 positions, $204,330) — 🟢 BUY — Oversold + rich premium (avg real yield 15%, good for selling) ⚠️ MIXED — individual real yield ranges 9%-19%, not uniformly thin (see per-symbol detail below)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ULTA | $108,108 | $54,054 | $162,162 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~13% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NKE | $0 | $23,216 | $23,216 | 🟢 | 7.3 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~19% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Calls: 7 covered (700 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| SBUX | $18,953 | $0 | $18,953 | 🟢 | 6.9 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Real yield-on-capital ~9% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Utilities (3 positions, $146,533) — 🟢 BUY — Oversold + rich premium (avg real yield 28%, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| CEG | $76,747 | $0 | $76,747 | 🟡 | 6.1 | 🟡 WATCH: 15% of 52-week range approaching the low extreme (10%-) | RSI/heat: 15% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~20% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| VST | $41,422 | $13,807 | $55,230 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~22% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| OKLO | $14,556 | $0 | $14,556 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Real yield-on-capital ~39% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Basic Materials (2 positions, $101,558) — 🟢 BUY — Oversold + rich premium (avg real yield 27%, good for selling) 🟡 possible macro exposure (weak historical signal, see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ALB | $62,070 | $20,690 | $82,760 | 🟡 | 7.2 | 🟡 WATCH: strangle (2C/6P) — call side uncapped if it rallies | RSI/heat: 13% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~25% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 6 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Qualitative flag (2026-10-02): JPMorgan cut its lithium price forecast and PT to $140 (Dec 2027, down from $160/Dec 2026), Neutral maintained -- short-term commodity pricing pressure (China lithium carbonate ~$21,625/mt Q3 vs ~$24,810 Q2), not a structural downgrade. Q2 revenue +31.1% YoY, EPS beat. Stock fell -3.51% on 2026-09-1 |
| MP | $14,098 | $4,699 | $18,798 | 🟡 | 7.4 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: 15% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~32% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Crypto Mining (3 positions, $26,019) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| RIOT | $11,943 | $1,991 | $13,934 | 🟡 | 6.2 | 🟡 WATCH: Dropped -19% in 7 days but only +3% vs its 200-day average — pullback within trend, verify thesis before treating as an entry | RSI/heat: Dropped -19% in 7 days but only +3% vs its 200-day average — pullback within trend, verify thesis before treating as an entry. Real yield-on-capital ~46% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| HUT | $8,978 | $0 | $8,978 | 🟡 | 6.7 | 🟡 WATCH: Dropped -12% in 7 days but only +12% vs its 200-day average — pullback within trend, verify thesis before treating as an entry | RSI/heat: Dropped -12% in 7 days but only +12% vs its 200-day average — pullback within trend, verify thesis before treating as an entry. Real yield-on-capital ~51% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |
| CIFR | $3,108 | $0 | $3,108 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Dropped -15% in 7 days AND -15% below its 200-day average — genuinely beaten down. Real yield-on-capital ~56% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Consumer Defensive (1 positions, $20,804) — 🟡 BUY (stock only) — Oversold but THIN premium (avg real yield 8% < 15%) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| WMT | $20,804 | $0 | $20,804 | 🟡 | 6.0 | 🟡 WATCH: 15% of 52-week range approaching the low extreme (10%-) | RSI/heat: 15% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~8% annualized (thin premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

### Energy (1 positions, $8,543) — 🟡 MONITOR — Low conviction across sector

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| CCJ | $8,543 | $0 | $8,543 | 🟡 | 4.5 | 🟡 WATCH: RSI 28 approaching oversold (30-); 13% of 52-week range approaching the low extreme (10%-) | RSI/heat: RSI 28 approaching oversold (30-); 13% of 52-week range approaching the low extreme (10%-). Real yield-on-capital ~18% annualized (rich premium for CSPs/CCs, ~10% OTM/105DTE). No qualitative flag on file. |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 15.3% ($1,221,827)
- 🟡 MONITOR: 61.0% ($4,867,226)
- 🟢 HEALTHY: 23.7% ($1,892,945)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟡 YELLOW

**Summary:** ⚠️ CAUTION — 1 indicators turning yellow. Watch for deterioration.

_Severity: today 1.58 raw, 1.28 smoothed over the trailing 4 logged day(s) (target window: 14d, will widen as more days log). Bands: GREEN <1.0, YELLOW 1.0-2.0, RED ≥2.0._

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| 🔴 | BREADTH | 46.15384615384615 | RED | 60% (caution), 50% (alert) |
| ⚠️ | AD_RATIO | 0.9230769230769231 | YELLOW | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 324 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.46% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟡 30-day crash probability: 29.7% — Action: 🟢 NORMAL: Proceed with standard sizing
- 🟠 60-day crash probability: 50.4%
- 🟠 90-day crash probability: 71.2%
- 📌 Primary risk factor: BREADTH critical

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▃▄▂▁▃`
  - 2026-09-02: 48% → 2026-10-02: 30% (falling, -18pp)

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
YELLOW FLAG — Stage 1 Rotation (Crash prob: 30% in 30d | 50% in 60d)
  PROBABILITY-DRIVEN ACTIONS:
    • Position reduction: Cut 0% of notional exposure
    • Focus: Close low-conviction positions first (Conv <6/10)
    • New entries: PAUSE or reduce to 25% of normal size

  Account A Actions:
    1. Close CRWD, LLY, OKTA (low conviction + overbought) at 40-50%
    2. Reduce AXON, NFLX from max to 75% of current size (0% total)
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

- **Technology concentration:** 39.1% of notional (115 positions, $3,118,903)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $1,103,138 live — 89% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $142,098 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $75,985 across CRWV, RKLB, OKLO, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-28 (4 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action on any tracked name since the Jul 9 S&P Oracle downgrade (BBB to BBB-, still current, stable outlook) -- checked live via WebSearch: no new Moody's/S&P action on the "Moody's six" (MSFT/AMZN/GOOGL/META/ORCL/CRWV) since their Jul 24 thematic AI-capex warning (already known, correctly not a firing event -- Moody's itself said an imminent downgrade of MSFT/AMZN/GOOGL/META is unlikely). Two items found that looked like new CoreWeave credit action on first read turned out to be stale/mischaracterized: the "$4bn Blue Owl financing failed" story is from Feb 2026 (already reflected in CoreWeave's known ~50% CDS-implied default probability, not new), and "CoreWeave rating downgrade" headlines are equity ANALYST rating changes (buy/hold/sell), not a credit-rating action -- explicitly the distinction this gate is supposed to hold the line on. CoreWeave's own newest debt facility ($8.5B DDTL, Mar 2026) is A3/Moody's -- investment grade -- a real, positive credit-access data point that complicates the "CoreWeave credit is purely deteriorating" read.
Tier-2 gate: NOT fired. Private-credit redemption pressure is actually DE-ESCALATING this quarter (Ares 14.4%->13.1%, Apollo 16.8%->14.7%, BlackRock HPS 13.3%->11.5% Q2->Q3 2026) -- no new fund gating found.
REAL new development this cycle: ORCL's own equity has now cracked. Last check (2026-09-08) explicitly flagged "equity hasn't cracked yet even though credit is flashing" for the neocloud/hyperscaler cluster -- that's no longer true for ORCL specifically. Live yfinance pull today: ORCL -7.1% (7d) / -7.9% (30d), a full reversal from +8.4%/+9.0% at the last check, and press coverage confirms real price weakness ("Oracle Shares Fall... One-Year Low"). NBIS/CRWV/HUT/RIOT are still net positive 30d (NBIS +10.9%, CRWV -0.5%, HUT +13.9%, RIOT +11.6%) but CRWV's 30d figure flipped from +9.2% to -0.5% -- deceleration, not yet a crack. META is still strongly UP (+13.0%/+30.6%), the opposite direction from the "mega-cap spenders underperforming" pattern the last check described -- that divergence read is weakening, not strengthening.
Anthropic IPO: delayed from an October target to November 2026 (WSJ, reported Sept 18), still targeting a ~$2T valuation vs. $965B private valuation in May -- a real but modest, single-month slip, not a pulled or repriced deal.
Breadth: 53.8% (live, today's report) -- between the 50% alert and 60% caution lines, roughly flat vs. the 51.3-53.9% range seen across the last several checks. HY OAS: 280bps, GREEN, well inside normal (400bps caution / 450bps alert) -- broad credit markets show no stress; the Oracle/CoreWeave stress remains a single-name/CDS story, not a HY-index- wide one.
Dial state: BASE CASE (30/70) -- unchanged. No Tier-1 or Tier-2 condition has actually fired; ORCL's equity crack is a real, single-name confirmation of the credit stress already known and priced into its Jul downgrade, not a new systemic signal. Worth a closer look next cycle specifically on whether ORCL's weakness spreads to CRWV/NBIS (the CRWV 30d deceleration is the one number to watch).

**⚠️ Underperformance proxy** — check these for credit news specifically:

- RIOT: -19.4% (7d) vs SPX +0.2% — >10pp gap
- HUT: -12.5% (7d) vs SPX +0.2% — >10pp gap


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | NVO | P | 50.0 | 77 | 100% | $5,000 |  |
| Account A (232) | OKTA | C | 140.0 | 49 | 96% | $14,000 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account C (634) | TWLO | C | 145.0 | 105 | 93% | $14,500 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account C (634) | TWLO | C | 150.0 | 105 | 92% | $30,000 | ✅ COVERED — assignment is the intended outcome, not an exit |
| Account A (232) | NFLX | P | 80.0 | 49 | 89% | $24,000 |  |
| Account C (634) | CCJ | P | 110.0 | 105 | 89% | $11,000 |  |
| Account A (232) | AXON | P | 560.0 | 77 | 89% | $56,000 |  |
| Account C (634) | ABNB | C | 145.0 | 14 | 88% | $14,500 |  |
| Account A (232) | CRM | C | 185.0 | 49 | 87% | $18,500 |  |
| Account A (232) | AXON | P | 540.0 | 77 | 86% | $54,000 |  |
| Account A (232) | ADBE | P | 260.0 | 14 | 85% | $26,000 |  |
| Account A (232) | NFLX | P | 77.5 | 49 | 85% | $15,500 |  |
| Account A (232) | MP | P | 60.0 | 77 | 84% | $6,000 |  |
| Account B (275) | CRM | C | 175.0 | 77 | 84% | $17,500 |  |
| Account B (275) | BWXT | P | 160.0 | 105 | 82% | $16,000 |  |
| Account B (275) | AMKR | P | 70.0 | 105 | 79% | $7,000 |  |
| Account A (232) | PYPL | C | 42.5 | 49 | 77% | $21,250 |  |
| Account A (232) | PYPL | C | 45.0 | 49 | 76% | $9,000 |  |
| Account A (232) | NFLX | P | 75.0 | 105 | 76% | $22,500 |  |
| Account C (634) | UBER | P | 75.0 | 105 | 74% | $7,500 |  |
| Account A (232) | WMT | P | 110.0 | 49 | 74% | $11,000 |  |
| Account A (232) | RBLX | C | 40.0 | 14 | 73% | $8,000 |  |
| Account A (232) | PYPL | C | 45.0 | 77 | 72% | $13,500 |  |
| Account A (232) | ETSY | C | 60.0 | 77 | 70% | $6,000 |  |
| Account A (232) | COIN | C | 170.0 | 14 | 69% | $17,000 |  |
_...and 75 more within 120 DTE (not shown)_

- **Worst case (all shown):** $3,097,800 across 100 positions
- **Realistic (>=30% prob):** $1,909,300 across 82 positions
- **Likely (>=50% prob):** $871,250 across 45 positions

No positions currently combine >=50% probability with RED heat on a truly naked (non-strangle) call, or an at-risk put.


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ✅ Last scan: 2026-10-02 (0 days ago)
- **NFLX:** STILL CONCRETE WEEKLY ACTION, now overdue: review the short NFLX puts for an early close/roll -- the original 09-18 catalyst has since been confirmed by price action, not contradicted. Worth asking directly whether this is being deliberately held (thesis the decline is overdone) or simply not yet gotten to.

- **MU:** Reclass conviction is now STRONGER than either prior flag -- real printed numbers, not forward guidance. Recommend executing the HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET reclass at the next quarterly bucket review rather than flagging it a third time; the evidence bar this flag was waiting for has been cleared.

- **AMZN:** No Tier CR trigger -- no rating action, no covenant/redemption event; this is AMZN proactively offloading balance-sheet risk via a presumptively investment-grade SPV, the same pattern the AVGO finding showed the market reading as reassuring rather than alarming. Fold this mechanical detail into the Circular Financing Playbook's Tier CR section at its next full review (now 3 real SPV-structure examples logged there: AVGO/Anthropic, this AMZN/Nvidia one, plus CoreWeave's own IG-rated DDTL facility from the 2026-09-28 AI Capex Review) -- the pattern itself (hyperscalers structuring AI-chip debt off their own balance sheets into separately-rated vehicles) is becoming the market-standard financing approach, not an isolated red flag.

- **AVGO:** No Tier CR trigger -- no rating-agency action, structure is clearer but not worse than already tracked in the Circular Financing Playbook. Confirmation with real mechanical detail, not escalation -- worth folding the SPV structure detail into that document's Tier CR section at its next full review.

- **ALB:** No action -- existing ITM $120P (Feb 19) already reflects the known downside; JPMorgan's own long-term target ($140) still implies recovery above current spot. Fundamentals (revenue/EPS) intact.

- **CRM:** Carried forward from 2026-09-01 -- no update this cycle.
- Open items:
  - NFLX: review short puts for an early close/roll given the Wells Fargo downgrade -- OVERDUE, open since 2026-09-18 (2 full cycles), thesis confirmed by price action since, not contradicted.
  - MU: execute the HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET reclass at the next quarterly bucket review -- real Q4 earnings print now backs it, not just forward guidance.
  - AVGO/AMZN SPV financing pattern: fold both into the Circular Financing Playbook's Tier CR section at its next full review -- no action needed before then.


## Section 6.9: ACTIVE DECISION TRACKER


**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 110.30444078445434
  - Live: macro_risk_level = YELLOW

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
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-8,200 to $-8,200 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (6 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $6,000/month contribution from MODERATE conviction positions
- Names: OKTA, CRWD, SONO, TWLO, PANW +1 more (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (34 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 34 healthy positions contribute $34,000/month baseline (expected)
- ✅ 34 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (3 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 3 Tier 1 entries = $11,400/month; closes gap from $-8,200 to $-19,600 (11.4% closure)
  - BROS: Conv 9.0/10 | RSI 16.0 | Value $3,877 ⚠️ Consumer Cyclical is HIGH-exposure to today's primary risk driver — adding here compounds it
  - APP: Conv 8.0/10 | RSI 20.8 | Value $271,580 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - VRT: Conv 8.0/10 | RSI 60.9 | Value $75,805

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 90
- 🔴 Critical actions: 0 closes + 6 monitors
- 🟡 Yellow cautions: 46
- 🟢 Green healthy: 34
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $-8,200 (-8.2% below target)
- After closes: $-8,200 (saves ~0.0%)
- After new Tier 1 entries: $-19,600 (11.4% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-10-02 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_