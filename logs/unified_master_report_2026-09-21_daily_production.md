# UNIFIED MASTER REPORT — DAILY (335 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** September 21, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $8,442,743
- **Total option requirement:** $2,839,586
- **Positions with short puts:** 93
- **Positions with short calls:** 51
- **YTD Net Premium:** $284,620 (live from transactions)
- **Month-to-Date Premium:** $43,535
- **Snapshot currency:** 2026-08-22

### Two Lenses on Monthly Performance

_(both derived from your transaction history)_

#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]

| Account | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | YTD |
|---|---|---|---|---|---|---|---|---|---|---|
| Account A (232) | 10,255 | 12,483 | 23,800 | 20,880 | -1,244 | -2,884 | 20,362 | 50,309 | 38,547 | 172,508 |
| Account B (275) | 31 | 3,322 | 1,546 | 4,894 | 9,709 | 3,948 | 575 | 3,476 | 2,614 | 30,115 |
| Account C (634) | 31 | 934 | 449 | 1,959 | 4,435 | 1,321 | 2,286 | 6,028 | 1,624 | 19,067 |
| Fidelity (Rahul) | 17 | 1,824 | 1,231 | 5,580 | 4,947 | 10,629 | 5,151 | 3,339 | 750 | 33,468 |
| Fidelity (Rajul — Rollover IRA) | 0 | 0 | 0 | 944 | 932 | 0 | 667 | 3,508 | 0 | 6,051 |
| Fidelity (Rajul — Roth IRA) | 0 | 0 | 0 | 95 | 189 | 1,028 | 1,326 | 1,196 | 0 | 3,834 |
| Robinhood (Individual) | 0 | 107 | 0 | 0 | 205 | -9 | 0 | 609 | 0 | 912 |
| Robinhood (Traditional IRA) | 0 | 518 | 816 | 6,275 | 2,879 | 2,087 | 517 | 5,573 | 0 | 18,665 |
| **TOTAL** | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 43,535 | 284,620 |
| Gross SOLD (STO, opened this month) | 181,739 | 68,408 | 199,758 | 324,125 | 349,672 | 243,331 | 135,826 | 242,546 | 131,804 | 1,877,209 |
| Net REALIZED (FIFO, closed this month) | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 43,535 | 284,620 |

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
| Account A (232) | $403,000 | 17.2% | $5,882,062 | $1,058,771 | Margin | 🔴 OVER CAP | $34,010 | ✅ $-1,564 |
| Account B (275) | $261,000 | 11.1% | $375,390 | $294,050 | Cash-Sec | 🔴 COVERAGE GAP | $9,863 | ✅ $-453 |
| Account C (634) | $266,000 | 11.4% | $341,094 | $211,950 | Cash-Sec | ⚠️ WATCH | $10,052 | ✅ $-462 |
| Fidelity (Rahul) | $498,560 | 21.3% | $754,300 | $636,442 | Cash-Sec | 🔴 COVERAGE GAP | $18,840 | ✅ $-866 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $54,228 | $54,277 | Cash-Sec | 🔴 COVERAGE GAP | $1,480 | ✅ $-68 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $174,375 | $161,850 | Cash-Sec | 🔴 COVERAGE GAP | $4,840 | ✅ $-222 |
| Vanguard (Rahul) | $320,492 | 13.7% | $515,785 | $422,246 | Cash-Sec | 🔴 COVERAGE GAP | $12,111 | ✅ $-557 |
| Robinhood (Individual) | $13,000 | 0.6% | $28,275 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $491 | ✅ $-22 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $317,235 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,314 | ✅ $-382 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $8,442,743 | $2,839,586 |  |  |  |  |

- **Account A (232):** 179 option positions | Monthly target: $34,010 | Equity: ADBE 300sh, APP 100sh, AXON 200sh, COIN 200sh, CRCL 100sh +14 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 21 option positions | Monthly target: $9,863 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 21 option positions | Monthly target: $10,052 | Equity: ABNB 100sh, NKE 100sh, PL 100sh, TWLO 324sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ⚠️ WATCH reading above
- **Fidelity (Rahul):** 42 option positions | Monthly target: $18,840 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
  - ⚠️ Balance as of 2026-07-31 (52 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,480 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
  - ⚠️ Balance as of 2026-07-31 (52 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Rollover IRA):** 14 option positions | Monthly target: $4,840
  - ⚠️ Balance as of 2026-07-31 (52 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Vanguard (Rahul):** 28 option positions | Monthly target: $12,111
  - ⚠️ Balance as of 2026-07-31 (52 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $491 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,314
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (52 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (113 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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
- Actual YTD: $284,620.0
- Gap to close: $615,380.0 (68.4%)
- Monthly average (YTD): $31,624
- Monthly average needed: $100,000
- Monthly gap: $-4,600

**Position tier distribution → gap closure:**

- Tier 1 (12 positions): $45,600/month (46% of $100,000 target)
- Tier 2 (67 positions): $67,000/month (67% of target)
- Tier 3 (16 positions): $-8,000/month (-8% drag)
- Current total: 95 positions = $104,600/month (105% of target)

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
| Account A (232) | $85,025 | $34,010 |
| Account B (275) | $24,657 | $9,863 |
| Account C (634) | $25,130 | $10,052 |
| Fidelity (Rahul) | $47,100 | $18,840 |
| Fidelity (Rajul — Roth IRA) | $3,700 | $1,480 |
| Fidelity (Rajul — Rollover IRA) | $12,100 | $4,840 |
| Vanguard (Rahul) | $30,277 | $12,111 |
| Robinhood (Individual) | $1,227 | $491 |
| Robinhood (Traditional IRA) | $20,785 | $8,314 |
| **TOTAL** | $250,001 | $100,001 |


## Section 1: SYSTEM STATUS & PORTFOLIO SNAPSHOT

- **Total open positions:** 335
- **Unique tickers:** 95
- **Active accounts:** 10
- **Data currency:** 2026-09-21
- **Live prices:** 94 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (12 positions): $45,600/month — each contributes $3,800/month (4.2% of $100,000)
- Tier 2 (67 positions): $67,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (16 positions): $-8,000/month — each drags -$500/month (-0.6% of target)
- Portfolio: 104,600/month (105% of target) — Need $-4,600 more

**HIGH (Tier 1: 8-10) conviction** — 12 positions | Total contribution: $45,600/month (45.6% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $328.59 | 9.1 | $3,800 | 3.8% |
| 🟡 | LASR | $39.84 | 8.5 | $3,800 | 3.8% |
| 🟡 | ONDS | $7.40 | 8.5 | $3,800 | 3.8% |
| 🟡 | JD | $27.23 | 8.4 | $3,800 | 3.8% |
| 🟢 | GOOGL | $356.24 | 8.4 | $3,800 | 3.8% |
| 🟢 | GEV | $953.69 | 8.4 | $3,800 | 3.8% |
| 🟡 | MU | $1040.69 | 8.4 | $3,800 | 3.8% |
| 🟡 | TSM | $442.79 | 8.2 | $3,800 | 3.8% |
| 🟢 | KTOS | $49.02 | 8.2 | $3,800 | 3.8% |
| 🟡 | SKHY | $187.39 | 8.2 | $3,800 | 3.8% |
| 🟢 | AMKR | $51.70 | 8.1 | $3,800 | 3.8% |
| 🟡 | ALAB | $335.36 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 67 positions | Total contribution: $67,000/month (67.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | LLY | $1165.58 | 7.9 | $1,000 | 1.0% |
| 🟡 | ANET | $203.20 | 7.8 | $1,000 | 1.0% |
| 🟡 | IONQ | $40.63 | 7.8 | $1,000 | 1.0% |
| 🟢 | BROS | $38.58 | 7.8 | $1,000 | 1.0% |
| 🟡 | PL | $17.00 | 7.8 | $1,000 | 1.0% |
| 🟡 | QUBT | $9.04 | 7.8 | $1,000 | 1.0% |
| 🟡 | QBTS | $17.73 | 7.8 | $1,000 | 1.0% |
| 🔴 | META | $741.48 | 7.6 | $1,000 | 1.0% |
| 🟡 | ASTS | $62.26 | 7.6 | $1,000 | 1.0% |
| 🟢 | LMT | $533.62 | 7.6 | $1,000 | 1.0% |
| 🟢 | CAVA | $51.79 | 7.6 | $1,000 | 1.0% |
| 🟡 | ALB | $112.58 | 7.5 | $1,000 | 1.0% |
| 🟢 | OKLO | $40.28 | 7.5 | $1,000 | 1.0% |
| 🟡 | HUT | $106.11 | 7.5 | $1,000 | 1.0% |
| 🟡 | RBLX | $51.05 | 7.4 | $1,000 | 1.0% |
| 🟡 | NOC | $525.25 | 7.4 | $1,000 | 1.0% |
| 🟡 | DVN | $47.56 | 7.4 | $1,000 | 1.0% |
| 🟢 | HOOD | $124.29 | 7.3 | $1,000 | 1.0% |
| 🟡 | AXON | $449.82 | 7.2 | $1,000 | 1.0% |
| 🟡 | RKLB | $69.88 | 7.2 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 47 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 16 positions | Total contribution: $-8,000/month (-8.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🔴 | CRWD | $248.17 | 5.9 | $-500 | 0.0% |
| 🟢 | ZBH | $94.43 | 5.9 | $-500 | 0.0% |
| 🔴 | OKTA | $190.07 | 5.8 | $-500 | 0.0% |
| 🟡 | ADBE | $248.50 | 5.8 | $-500 | 0.0% |
| 🟢 | CRCL | $93.26 | 5.8 | $-500 | 0.0% |
| 🟢 | MMYT | $48.47 | 5.6 | $-500 | 0.0% |
| 🟡 | REGN | $798.07 | 5.5 | $-500 | 0.0% |
| 🟢 | DIS | $104.18 | 5.3 | $-500 | 0.0% |
| 🟢 | BRKB | $0.00 | 5.3 | $-500 | 0.0% |
| 🟢 | SMR | $8.80 | 5.3 | $-500 | 0.0% |
| 🟢 | TTD | $13.98 | 5.1 | $-500 | 0.0% |
| 🟡 | PFE | $27.74 | 5.0 | $-500 | 0.0% |
| 🟢 | PYPL | $52.70 | 4.5 | $-500 | 0.0% |
| 🟡 | NVO | $39.63 | 4.3 | $-500 | 0.0% |
| 🟡 | XYZ | $77.82 | 4.2 | $-500 | 0.0% |
| 🟡 | CCJ | $93.25 | 3.5 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 32 positions (33.7%)
- 🟡 YELLOW (Neutral): 57 positions (60.0%)
- 🔴 RED (Extended/Overbought): 6 positions (6.3%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.0 — VIX 15.0 sustained < 20
- **S&P 500:** 7760 (50d MA: 7621, 200d MA: 7188)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 118 | 6.83 | 49.2 | 56.3 | 45 | 🟡 NEUTRAL |
| Healthcare | 22 | 6.0 | 44.1 | 46.0 | 18 | 🟡 NEUTRAL |
| Consumer Cyclical | 33 | 6.83 | 33.8 | 38.8 | 32 | 🟡 BUY stock/THIN premium |
| Industrials | 35 | 7.17 | 50.4 | 40.4 | 28 | 🟡 NEUTRAL |
| Energy | 3 | 6.1 | 44.2 | 59.5 | 36 | 🟡 NEUTRAL |
| Consumer Defensive | 1 | 7.2 | 60.2 | 23.6 | 94 | 🟢 BUY (rich premium) |
| Utilities | 8 | 6.68 | 51.8 | 8.9 | 18 | 🟡 BUY stock/THIN premium |
| Communication Services | 38 | 7.61 | 60.5 | 31.3 | 36 | 🟡 BUY stock/THIN premium |
| Defense | 8 | 6.93 | 39.2 | 26.9 | 28 | 🟡 BUY stock/THIN premium |
| Brand-Quality (Non-AI) | 22 | 6.88 | 43.5 | 49.5 | 26 | 🟡 NEUTRAL |
| Basic Materials | 11 | 7.32 | 30.9 | 22.3 | 21 | 🟡 BUY stock/THIN premium |
| Financial Services | 35 | 6.11 | 52.9 | 46.4 | 50 | 🟡 NEUTRAL |
| Unknown | 1 | 5.3 | 50.0 | 50.0 | 0 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Basic Materials:** Conv 7.3/10, RSI 30.9, 52W %ile 22.3 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 21 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Cyclical:** Conv 6.8/10, RSI 33.8, 52W %ile 38.8 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 32 < 40) — not attractive for CSPs/CCs
- ✓ **Communication Services:** Conv 7.6/10, RSI 60.5, 52W %ile 31.3 — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 36 < 40)
- ✓ **Defense:** Conv 6.9/10, RSI 39.2, 52W %ile 26.9 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 28 < 40) — not attractive for CSPs/CCs
- ✓ **Utilities:** Conv 6.7/10, RSI 51.8, 52W %ile 8.9 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 18 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Defensive:** Conv 7.2/10, RSI 60.2, 52W %ile 23.6 — 🟢 BUY — Oversold + rich premium (avg IVR 94, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.8/10, RSI 49.2, 52W %ile 56.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Brand-Quality (Non-AI):** Conv 6.9/10, RSI 43.5, 52W %ile 49.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.2/10, RSI 50.4, 52W %ile 40.4 — 🟡 MONITOR — Neutral positioning
- ◇ **Unknown:** Conv 5.3/10, RSI 50.0, 52W %ile 50.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.1/10, RSI 52.9, 52W %ile 46.4 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 6.0/10, RSI 44.1, 52W %ile 46.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 6.1/10, RSI 44.2, 52W %ile 59.5 — 🟡 MONITOR — Neutral positioning


## Section 5: POSITION DISTRIBUTION BY ACCOUNT

- **Account A (232):** 179 positions (53.4%) `██████████████████████████`
- **Fidelity (Rahul):** 42 positions (12.5%) `██████`
- **Vanguard (Rahul):** 28 positions (8.4%) `████`
- **Account B (275):** 21 positions (6.3%) `███`
- **Account C (634):** 21 positions (6.3%) `███`
- **Robinhood (Traditional IRA):** 18 positions (5.4%) `██`
- **Fidelity (Rajul — Rollover IRA):** 14 positions (4.2%) `██`
- **Fidelity (Rajul — Roth IRA):** 8 positions (2.4%) `█`
- **Robinhood (Individual):** 4 positions (1.2%) ``
- **Fidelity 401K (Rahul):** 0 positions (0.0%) ``


## Section 6: POSITION HEAT MATRIX BY SECTOR — Sector -> Symbol, Put/Call/Total Value, Heat, Suggestion


### Technology (34 positions, $3,092,048) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $477,853 | $95,571 | $573,423 | 🟡 | 6.2 | 🟡 MONITOR |
| MU | $208,138 | $104,069 | $312,207 | 🟡 | 8.4 | 🟡 MONITOR |
| ALAB | $234,749 | $33,536 | $268,284 | 🟡 | 8.0 | 🟡 MONITOR |
| CRM | $95,120 | $142,680 | $237,800 | 🟡 | 6.5 | 🟡 MONITOR |
| ADBE | $74,550 | $124,250 | $198,800 | 🟡 | 5.8 | 🟡 MONITOR |
| TSM | $132,837 | $44,279 | $177,116 | 🟡 | 8.2 | 🟡 MONITOR |
| OKTA | $38,014 | $133,049 | $171,063 | 🔴 | 5.8 | 🔴 TRIM CALL (delta/assignment risk); 🟢 HOLD PUT (near max profit, unaffected — a short call gains protection in a decline, don't close it purely on crash fears) |
| MSFT | $99,715 | $49,858 | $149,573 | 🟡 | 6.8 | 🟡 MONITOR |
| PANW | $147,764 | $0 | $147,764 | 🟡 | 6.5 | 🟡 MONITOR |
| CRWD | $99,268 | $24,817 | $124,085 | 🔴 | 5.9 | 🔴 TRIM CALL (delta/assignment risk); 🟢 HOLD PUT (near max profit, unaffected — a short call gains protection in a decline, don't close it purely on crash fears) |
| IBM | $91,490 | $22,873 | $114,363 | 🟡 | 6.0 | 🟡 MONITOR |
| TWLO | $25,977 | $77,932 | $103,910 | 🔴 | 7.1 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| ZS | $61,450 | $20,483 | $81,933 | 🔴 | 7.2 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| NVDA | $68,237 | $0 | $68,237 | 🟡 | 7.2 | 🟡 MONITOR |
| SHOP | $53,552 | $0 | $53,552 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| XYZ | $31,130 | $15,565 | $46,695 | 🟡 | 4.2 | 🟡 MONITOR |
| UBER | $42,648 | $0 | $42,648 | 🟡 | 7.2 | 🟡 MONITOR |
| FSLR | $40,010 | $0 | $40,010 | 🟡 | 7.0 | 🟡 MONITOR |
| IONQ | $24,378 | $8,126 | $32,504 | 🟡 | 7.8 | 🟡 MONITOR |
| AMKR | $25,850 | $0 | $25,850 | 🟢 | 8.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| SKHY | $18,739 | $0 | $18,739 | 🟡 | 8.2 | 🟡 MONITOR |
| PLTR | $18,188 | $0 | $18,188 | 🟡 | 6.5 | 🟡 MONITOR |
| APH | $16,150 | $0 | $16,150 | 🟡 | 7.2 | 🟡 MONITOR |
| ASTS | $12,452 | $0 | $12,452 | 🟡 | 7.6 | 🟡 MONITOR |
| RBRK | $11,278 | $0 | $11,278 | 🔴 | 6.3 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| LYFT | $1,527 | $7,633 | $9,159 | 🟡 | 6.4 | 🟡 MONITOR |
| CRWV | $8,694 | $0 | $8,694 | 🟡 | 6.4 | 🟡 MONITOR |
| LASR | $7,968 | $0 | $7,968 | 🟡 | 8.5 | 🟡 MONITOR |
| CIFR | $7,522 | $0 | $7,522 | 🟡 | 6.4 | 🟡 MONITOR |
| SONO | $0 | $6,488 | $6,488 | 🟢 | 6.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| INFY | $1,089 | $1,089 | $2,177 | 🟢 | 6.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QBTS | $1,773 | $0 | $1,773 | 🟡 | 7.8 | 🟡 MONITOR |
| QUBT | $904 | $0 | $904 | 🟡 | 7.8 | 🟡 MONITOR |
| ONDS | $740 | $0 | $740 | 🟡 | 8.5 | 🟡 MONITOR |

### Industrials (9 positions, $1,213,334) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $89,963 | $359,852 | $449,815 | 🟡 | 7.2 | 🟡 MONITOR |
| GEV | $286,107 | $95,369 | $381,476 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| BE | $165,291 | $55,097 | $220,388 | 🟡 | 6.6 | 🟡 MONITOR |
| VRT | $50,500 | $25,250 | $75,750 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |
| RKLB | $48,914 | $0 | $48,914 | 🟡 | 7.2 | 🟡 MONITOR |
| BWXT | $29,508 | $0 | $29,508 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| KTOS | $4,902 | $0 | $4,902 | 🟢 | 8.2 | 🟢 ATTRACTIVE — let run |
| PL | $1,700 | $0 | $1,700 | 🟡 | 7.8 | 🟡 MONITOR |
| SMR | $880 | $0 | $880 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

### Communication Services (8 positions, $1,165,494) — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 36 < 40) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $370,742 | $74,148 | $444,891 | 🔴 | 7.6 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| APP | $230,013 | $98,577 | $328,590 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $117,408 | $44,028 | $161,436 | 🟡 | 6.7 | 🟡 MONITOR |
| GOOGL | $106,871 | $35,624 | $142,494 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBLX | $25,525 | $15,315 | $40,840 | 🟡 | 7.4 | 🟡 MONITOR |
| NBIS | $23,610 | $0 | $23,610 | 🟡 | 7.2 | 🟡 MONITOR |
| DIS | $20,836 | $0 | $20,836 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TTD | $2,797 | $0 | $2,797 | 🟢 | 5.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Healthcare (7 positions, $880,348) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LLY | $233,116 | $116,558 | $349,674 | 🟡 | 7.9 | 🟡 MONITOR |
| ISRG | $119,802 | $39,934 | $159,736 | 🟡 | 7.2 | 🟡 MONITOR |
| REGN | $79,807 | $79,807 | $159,614 | 🟡 | 5.5 | 🟡 MONITOR |
| UNH | $75,415 | $75,415 | $150,830 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run |
| NVO | $19,815 | $7,926 | $27,741 | 🟡 | 4.3 | 🟡 MONITOR |
| ZBH | $9,443 | $9,443 | $18,885 | 🟢 | 5.9 | 🟢 ATTRACTIVE — let run |
| PFE | $13,868 | $0 | $13,868 | 🟡 | 5.0 | 🟡 MONITOR |

### Financial Services (8 positions, $687,406) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| COIN | $40,554 | $182,493 | $223,047 | 🟡 | 6.0 | 🟡 MONITOR |
| MA | $169,612 | $0 | $169,612 | 🟡 | 6.9 | 🟡 MONITOR |
| JPM | $70,382 | $35,191 | $105,573 | 🟡 | 7.0 | 🟡 MONITOR |
| PYPL | $31,620 | $63,240 | $94,860 | 🟢 | 4.5 | 🟢 ATTRACTIVE — let run |
| CRCL | $27,978 | $18,652 | $46,630 | 🟢 | 5.8 | 🟢 ATTRACTIVE — let run |
| HOOD | $24,859 | $0 | $24,859 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run |
| RIOT | $9,770 | $2,442 | $12,212 | 🟡 | 7.0 | 🟡 MONITOR |
| HUT | $10,611 | $0 | $10,611 | 🟡 | 7.5 | 🟡 MONITOR |

### Consumer Cyclical (12 positions, $450,968) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 32 < 40) — not attractive for CSPs/CCs 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $112,494 | $28,123 | $140,617 | 🟡 | 6.8 | 🟡 MONITOR |
| AMZN | $51,596 | $25,798 | $77,394 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ABNB | $16,717 | $50,151 | $66,868 | 🟡 | 6.8 | 🟡 MONITOR |
| BABA | $57,938 | $0 | $57,938 | 🟡 | 7.2 | 🟡 MONITOR |
| TSLA | $37,407 | $0 | $37,407 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MMYT | $19,389 | $4,847 | $24,236 | 🟢 | 5.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| JD | $8,168 | $8,168 | $16,335 | 🟡 | 8.4 | 🟡 MONITOR |
| ETSY | $7,243 | $7,243 | $14,486 | 🟡 | 6.7 | 🟡 MONITOR |
| CAVA | $5,179 | $0 | $5,179 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| DKNG | $4,418 | $0 | $4,418 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| BROS | $3,858 | $0 | $3,858 | 🟢 | 7.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CCL | $2,232 | $0 | $2,232 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (5 positions, $404,961) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ANET | $121,920 | $60,960 | $182,880 | 🟡 | 7.8 | 🟡 MONITOR |
| ULTA | $112,067 | $56,034 | $168,101 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run |
| NKE | $0 | $25,210 | $25,210 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run |
| SBUX | $18,916 | $0 | $18,916 | 🟡 | 6.1 | 🟡 MONITOR |
| ELF | $9,854 | $0 | $9,854 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |

### Defense (3 positions, $324,503) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 28 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| NOC | $105,050 | $52,525 | $157,575 | 🟡 | 7.4 | 🟡 MONITOR |
| LMT | $106,724 | $0 | $106,724 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run |
| BA | $40,136 | $20,068 | $60,204 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run |

### Basic Materials (2 positions, $98,966) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 21 < 40) — not attractive for CSPs/CCs 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $67,548 | $11,258 | $78,806 | 🟡 | 7.5 | 🟡 MONITOR |
| MP | $15,120 | $5,040 | $20,160 | 🟡 | 7.0 | 🟡 MONITOR |

### Utilities (3 positions, $95,135) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 18 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $42,463 | $14,154 | $56,618 | 🟡 | 6.2 | 🟡 MONITOR |
| CEG | $26,433 | $0 | $26,433 | 🟡 | 6.1 | 🟡 MONITOR |
| OKLO | $12,084 | $0 | $12,084 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run |

### Energy (2 positions, $18,836) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| DVN | $9,511 | $0 | $9,511 | 🟡 | 7.4 | 🟡 MONITOR |
| CCJ | $9,325 | $0 | $9,325 | 🟡 | 3.5 | 🟡 MONITOR |

### Consumer Defensive (1 positions, $10,746) — 🟢 BUY — Oversold + rich premium (avg IVR 94, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,746 | $0 | $10,746 | 🟡 | 7.2 | 🟡 MONITOR |

### Unknown (1 positions, $0) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| BRKB | $0 | $0 | $0 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 12.1% ($1,020,921)
- 🟡 MONITOR: 64.8% ($5,473,557)
- 🟢 HEALTHY: 23.1% ($1,948,265)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟢 GREEN

**Summary:** ✅ BULL regime stable. All indicators healthy. Proceed with normal sizing.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| ⚠️ | BREADTH | 51.28205128205128 | YELLOW | 60% (caution), 50% (alert) |
| ✅ | AD_RATIO | 4.555555555555555 | GREEN | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 268 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.25% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟢 30-day crash probability: 19.1% — Action: 🟢 NORMAL: Proceed with standard sizing
- 🟡 60-day crash probability: 32.8%
- 🟡 90-day crash probability: 46.5%
- 📌 Primary risk factor: BREADTH elevated

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▄▃▄▂`
  - 2026-09-01: 48% → 2026-09-21: 19% (falling, -29pp)

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

- **Technology concentration:** 36.6% of notional (118 positions, $3,092,048)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $1,172,102 live — 86% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $193,266 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $116,126 across NBIS, CRWV, RKLB, OKLO, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-08 (13 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.

Underperformance proxy: no tracked name diverging >10pp from SPX over 7 days.


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | NVO | P | 50.0 | 88 | 94% | $5,000 |  |
| Account A (232) | IBM | P | 270.0 | 25 | 93% | $27,000 |  |
| Account A (232) | RBLX | C | 40.0 | 25 | 93% | $8,000 |  |
| Account C (634) | TWLO | C | 145.0 | 116 | 91% | $14,500 | 🔴 EXIT CANDIDATE |
| Account C (634) | ABNB | C | 145.0 | 25 | 89% | $14,500 |  |
| Account C (634) | TWLO | C | 150.0 | 116 | 88% | $30,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | OKTA | C | 140.0 | 60 | 88% | $14,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | CRM | C | 185.0 | 60 | 84% | $18,500 |  |
| Account B (275) | AMKR | P | 70.0 | 116 | 84% | $7,000 |  |
| Account B (275) | CRM | C | 175.0 | 88 | 83% | $17,500 |  |
| Account A (232) | AXON | P | 560.0 | 88 | 81% | $56,000 |  |
| Account A (232) | PYPL | C | 42.5 | 60 | 80% | $21,250 |  |
| Account A (232) | COIN | C | 170.0 | 25 | 80% | $17,000 |  |
| Account C (634) | CCJ | P | 110.0 | 116 | 78% | $11,000 |  |
| Account A (232) | MP | P | 60.0 | 88 | 77% | $6,000 |  |
| Account A (232) | AXON | P | 540.0 | 88 | 77% | $54,000 |  |
| Account A (232) | PYPL | C | 45.0 | 60 | 75% | $9,000 |  |
| Account A (232) | NFLX | P | 80.0 | 60 | 74% | $24,000 |  |
| Account A (232) | PYPL | C | 45.0 | 88 | 71% | $13,500 |  |
| Account A (232) | ETSY | C | 60.0 | 88 | 70% | $6,000 |  |
| Account A (232) | XYZ | C | 65.0 | 88 | 70% | $13,000 |  |
| Account A (232) | ADBE | P | 260.0 | 25 | 69% | $26,000 |  |
| Account A (232) | DIS | P | 110.0 | 88 | 68% | $22,000 |  |
| Account B (275) | BWXT | P | 160.0 | 116 | 68% | $16,000 |  |
| Account A (232) | NFLX | P | 77.5 | 60 | 67% | $15,500 |  |
_...and 92 more within 120 DTE (not shown)_

- **Worst case (all shown):** $3,759,750 across 117 positions
- **Realistic (>=30% prob):** $1,895,500 across 81 positions
- **Likely (>=50% prob):** $773,750 across 44 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 4

- TWLO C 145.0 (Account C (634)) — 91% probability, RED heat
- TWLO C 150.0 (Account C (634)) — 88% probability, RED heat
- OKTA C 140.0 (Account A (232)) — 88% probability, RED heat
- META C 650.0 (Account A (232)) — 67% probability, RED heat


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ✅ Last scan: 2026-09-18 (3 days ago)
- **NFLX:** CONCRETE WEEKLY ACTION: Account A holds 2 ITM cash-secured NFLX puts right now -- $77.50P x2 (Nov 20) and $80P x3 (Nov 20), both already ITM at $72 spot, both already flagged separately as low-premium (<$500/contract) in this week's Account A cleanup pass. This new catalyst adds real downside conviction on top of an already-poor risk/reward. Recommend reviewing both for an early close/roll before assignment risk grows further, rather than waiting for expiry. The 2 naked NFLX calls ($80C x3 Nov 20, $85C x3 Jan 15) are UNAFFECTED negatively -- a decline moves them further OTM, reducing their risk.

- **MU:** Flag for next quarterly bucket review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET) -- conviction on the reclass is now stronger than 2026-09-01, not an immediate action. Note the 09-30 earnings date if sizing any near-dated MU options this cycle.

- **AVGO:** No Tier CR trigger -- no rating-agency action, structure is clearer but not worse than already tracked in the Circular Financing Playbook. Confirmation with real mechanical detail, not escalation -- worth folding the SPV structure detail into that document's Tier CR section at its next full review.

- **ALB:** No action -- existing ITM $120P (Feb 19) already reflects the known downside; JPMorgan's own long-term target ($140) still implies recovery above current spot. Fundamentals (revenue/EPS) intact.

- **CRM:** Carried forward from 2026-09-01 -- no update this cycle.
- Open items:
  - NFLX: review the 2 ITM Nov-20 cash-secured puts ($77.50P x2, $80P x3, Account A) for an early close/roll given the Wells Fargo downgrade -- new this cycle.
  - MU: reclass conviction strengthened for next quarterly bucket review -- not urgent.


## Section 6.9: ACTIVE DECISION TRACKER


**✅ account_a_800k_4week_plan** — CLEARED (as of 2026-09-21)

RESOLVED 2026-09-21 after a full walk-through of Account A's real Schwab Margin Details / Available Funds: Margin Equity $1,000,000, SMA (Reg-T initial-margin room) $1,600,000, Cash+Borrowing $102,000, debit balance $0 (zero margin interest -- no loan outstanding), no margin/maintenance requirement violation, no active call. Equity Percent read 29% at one point in the conversation (down from an earlier, WRONG 89% transcription) which triggered a real scare, but 29% is NOT the binding constraint here: that ratio governs a traditional debit-balance maintenance call, and this account carries zero debit balance, so that mechanism doesn't apply. The real constraint for an options-heavy, no-stock-loan margin account is the options margin requirement itself (Opt Req $831,000 real) against SMA/equity headroom. Conclusion: the trader's $800K/4-week plan is CONSERVATIVE, not aggressive, against real current capacity. `accounts_config.py`'s Account A capacity updated from $700K to $900K (a YELLOW-macro-regime working ceiling; see that file's comment for the full RED/YELLOW/GREEN regime dial: $700-750K / $900K-$1M / $1.1-1.2M). The $800K plan sits comfortably under the new $900K ceiling with room to spare.
  - Live: account_a_margin_utilization_pct = 135.7969639124189
  - Live: macro_risk_level = GREEN

**✅ axon_sept18_roll_450c** — RESOLVED (as of 2026-09-18)

Roll the AXON $450C (Sept 18 2026 expiry) out to a January 2027 call (~$560-580 strike, AXON's own missing rung in its Sept/Dec/March ladder) before Sept 18. Keep the $470C to settle against the 100 owned AXON shares as a clean covered assignment. Only 100 AXON shares exist to cover 2 ITM Sept-18 calls; rolling one removes the naked/short-stock risk that would otherwise be forced at expiry.

**✅ pypl_naked_calls_cleanup** — RESOLVED (as of 2026-09-21)

CORRECTED 2026-09-21 -- this was wrong. The account actually owns 1,100 PYPL shares (confirmed directly against the raw schwab_rahul_individual.csv: cost basis $132,985.05, avg $120.90/share, current value $57,926 at ~$52.66, -56.44% unrealized -- a real, large embedded loss the trader is running covered calls against, not a fresh naked-call build). 1,100 shares covers 11 of the 12 open PYPL calls ($42.50C x5 Nov 20, $45C x2 Nov 20, $45C x3 Dec 18, $47.50C x2 Jan 15) -- only ~1 contract is genuinely naked, not all 12. Root cause: `open_positions_loader_v2.py`'s `get_equity_summary()` returns 0 shares for PYPL/Account A despite the raw position file showing 1,100 directly -- same failure pattern already confirmed on FMC and NKE this session (2026-09-18). Do not trust this loader's equity summary for naked-call coverage checks without a raw-file cross-check; a real code fix is still open, not yet done. Trader's stated plan: sell additional puts near $52 to generate premium and, if assigned, use the resulting shares to further cover/resolve the calls as they roll forward -- a deliberate wheel strategy against the underwater long position, not an oversight.
  - Live check: 1 naked ITM contract(s) remaining (target: 0)

**⏳ crcl_naked_call_dec** — OPEN

1 naked short call on CRCL (0 shares owned), ITM as of 2026-09-10: $90C (Dec 18 2026). Smaller version of the same AXON/PYPL issue.
  - Live check: 1 naked ITM contract(s) remaining (target: 0)

**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 117.64123587417603
  - Live: macro_risk_level = GREEN

**⏳ be_puts_reduction** — OPEN

Reduce BE put exposure to zero over the next ~10 days (target: 2026-09-20) by closing/rolling out of all 6 open BE put legs across every account. BE is RED heat, RSI 77-81 (overbought/extended), and is the most widely-held name in the book -- also carries a naked short-call pair against it in Account A/Fidelity Rahul (no BE shares owned anywhere). Baseline as of 2026-09-10: Account A $170P (Jan 15 2027) x2 [Jan+Feb], Account B $180P (Feb 19 2027), Fidelity (Rahul) $190P (Jan 15 2027), Fidelity (Rajul - Rollover IRA) $200P (Jun 17 2027), Robinhood (Traditional) $180P (Jun 17 2027). Trader confirmed 2026-09-10 this should cover ALL open BE puts (not just the near-dated ones) -- an initial "Dec 2026 and before" framing didn't match any real BE put, since the earliest is Jan 15 2027.
KNOWN GAP: the automated check only sees 5 of these 6 legs -- the Robinhood (Traditional) $180P (Jun 17 2027) has an option-type parsing gap in that account's transaction reconstruction and won't count toward the live total below. This entry will show RESOLVED once the other 5 close even if that 6th one is still open -- manually confirm the Robinhood leg separately before treating BE exposure as fully closed.
  - Live check: 5 leg(s) open now (baseline was 6), target: 0



## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-4,600 to $-4,600 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (2 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $2,000/month contribution from MODERATE conviction positions
- Names: OKTA, CRWD (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (32 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 32 healthy positions contribute $32,000/month baseline (expected)
- ✅ 32 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (5 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 5 Tier 1 entries = $19,000/month; closes gap from $-4,600 to $-23,600 (19.0% closure)
  - APP: Conv 9.1/10 | RSI 57.4 | Value $328,590 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 58.8 | Value $381,476
  - GOOGL: Conv 8.4/10 | RSI 63.8 | Value $142,494 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - KTOS: Conv 8.2/10 | RSI 38.8 | Value $4,902
  - AMKR: Conv 8.1/10 | RSI 59.9 | Value $25,850 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 95
- 🔴 Critical actions: 0 closes + 2 monitors
- 🟡 Yellow cautions: 54
- 🟢 Green healthy: 32
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $-4,600 (-4.6% below target)
- After closes: $-4,600 (saves ~0.0%)
- After new Tier 1 entries: $-23,600 (19.0% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-21 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_