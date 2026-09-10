# UNIFIED MASTER REPORT — DAILY (327 POSITIONS)

**Type:** DAILY  |  **Regime:** CAUTIOUS_BULL  |  **Generated:** September 10, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $7,462,312
- **Total option requirement:** $2,667,145
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
| Account A (232) | $403,000 | 17.2% | $4,999,127 | $899,843 | Margin | 🔴 OVER CAP | $25,753 | ✅ $-2,747 |
| Account B (275) | $261,000 | 11.1% | $364,384 | $291,050 | Cash-Sec | 🔴 COVERAGE GAP | $9,602 | ✅ $-1,024 |
| Account C (634) | $266,000 | 11.4% | $330,825 | $214,950 | Cash-Sec | ⚠️ WATCH | $9,786 | ✅ $-1,044 |
| Fidelity (Rahul) | $498,560 | 21.3% | $700,350 | $625,591 | Cash-Sec | 🔴 COVERAGE GAP | $18,342 | ✅ $-1,956 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $51,239 | $51,472 | Cash-Sec | 🔴 COVERAGE GAP | $1,440 | ✅ $-154 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $170,387 | $161,850 | Cash-Sec | 🔴 COVERAGE GAP | $4,712 | ✅ $-503 |
| Vanguard (Rahul) | $320,492 | 13.7% | $515,629 | $422,389 | Cash-Sec | 🔴 COVERAGE GAP | $11,790 | ✅ $-1,258 |
| Robinhood (Individual) | $13,000 | 0.6% | $28,850 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $477 | ✅ $-51 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $301,522 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,093 | ✅ $-864 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $7,462,312 | $2,667,145 |  |  |  |  |

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
- Current Regime: CAUTIOUS_BULL (applies 90% of base)
- Adjusted Target: $90,000 net per month

**Performance vs. target (YTD cumulative):**

- Target (9 months): $810,000
- Actual YTD: $239,895.0
- Gap to close: $570,105.0 (70.4%)
- Monthly average (YTD): $26,655
- Monthly average needed: $90,000
- Monthly gap: $-9,600

**Position tier distribution → gap closure:**

- Tier 1 (12 positions): $45,600/month (51% of $90,000 target)
- Tier 2 (63 positions): $63,000/month (70% of target)
- Tier 3 (18 positions): $-9,000/month (-10% drag)
- Current total: 93 positions = $99,600/month (111% of target)

**Gap closure path:**

- To hit $90,000 target: Need 0 more Tier 1 positions
- Alternative: Scale existing OR exit 7 worst Tier 3 positions
- Capital required for 0 new positions: $0 (0 × $10K)

**Risk guardrails:**

- Margin account (Account A only): >75% alert, >80% emergency — real broker margin-call risk
- Cash-secured accounts (everyone else): >75% watch, >=100% coverage gap — a liquidity question (does cash cover full assignment), not a leverage/margin-call risk
- Cash floor (all accounts): $75,000 minimum to trade
- Cash emergency: <$50,000 → deploy emergency fund
- Current status: ⚠️ MONITOR


### Supplementary: Production Framework — 60% Close Cost Ratio Targets

- Framework: $100,000/month net = $1.2M/year target (at 60% close costs)
- Regime: CAUTIOUS_BULL (applies 90% of base)
- Adjusted Target: $225,000 gross / $90,000 net

**Account Targets (Regime-Adjusted)** — complements Section 0's Per-Account
Breakdown 'Target' column: that one is the raw monthly_target; these are the
same targets scaled by the current regime's adjustment factor, gross+net.

| Account | Gross | Net |
|---|---|---|
| Account A (232) | $64,382 | $25,753 |
| Account B (275) | $24,005 | $9,602 |
| Account C (634) | $24,465 | $9,786 |
| Fidelity (Rahul) | $45,855 | $18,342 |
| Fidelity (Rajul — Roth IRA) | $3,600 | $1,440 |
| Fidelity (Rajul — Rollover IRA) | $11,780 | $4,712 |
| Vanguard (Rahul) | $29,475 | $11,790 |
| Robinhood (Individual) | $1,192 | $477 |
| Robinhood (Traditional IRA) | $20,232 | $8,093 |
| **TOTAL** | $224,986 | $89,995 |


## Section 1: SYSTEM STATUS & PORTFOLIO SNAPSHOT

- **Total open positions:** 327
- **Unique tickers:** 93
- **Active accounts:** 10
- **Data currency:** 2026-09-10
- **Live prices:** 92 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (12 positions): $45,600/month — each contributes $3,800/month (4.2% of $90,000)
- Tier 2 (63 positions): $63,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (18 positions): $-9,000/month — each drags -$500/month (-0.6% of target)
- Portfolio: 99,600/month (111% of target) — Need $-9,600 more

**HIGH (Tier 1: 8-10) conviction** — 12 positions | Total contribution: $45,600/month (50.7% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $305.06 | 9.1 | $3,800 | 4.2% |
| 🟡 | NVDA | $223.67 | 8.8 | $3,800 | 4.2% |
| 🟢 | AMKR | $51.35 | 8.4 | $3,800 | 4.2% |
| 🟢 | GEV | $951.04 | 8.4 | $3,800 | 4.2% |
| 🟡 | MU | $1027.77 | 8.4 | $3,800 | 4.2% |
| 🟡 | APH | $81.34 | 8.3 | $3,800 | 4.2% |
| 🟢 | VRT | $262.89 | 8.3 | $3,800 | 4.2% |
| 🟡 | TSM | $435.36 | 8.2 | $3,800 | 4.2% |
| 🟡 | JD | $27.00 | 8.2 | $3,800 | 4.2% |
| 🟡 | SKHY | $198.63 | 8.2 | $3,800 | 4.2% |
| 🟡 | RBLX | $44.52 | 8.0 | $3,800 | 4.2% |
| 🟡 | META | $653.69 | 8.0 | $3,800 | 4.2% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 63 positions | Total contribution: $63,000/month (70.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | LYFT | $14.90 | 7.8 | $1,000 | 1.1% |
| 🟡 | FSLR | $203.10 | 7.8 | $1,000 | 1.1% |
| 🟢 | UNH | $393.06 | 7.7 | $1,000 | 1.1% |
| 🟢 | BWXT | $156.71 | 7.7 | $1,000 | 1.1% |
| 🟢 | ALAB | $300.54 | 7.6 | $1,000 | 1.1% |
| 🟢 | CAVA | $56.51 | 7.6 | $1,000 | 1.1% |
| 🟢 | ULTA | $541.86 | 7.5 | $1,000 | 1.1% |
| 🟡 | LASR | $40.99 | 7.5 | $1,000 | 1.1% |
| 🟡 | NBIS | $240.35 | 7.5 | $1,000 | 1.1% |
| 🟢 | BROS | $44.96 | 7.5 | $1,000 | 1.1% |
| 🟡 | CRWV | $94.94 | 7.5 | $1,000 | 1.1% |
| 🟡 | HUT | $95.92 | 7.5 | $1,000 | 1.1% |
| 🟢 | SPCX | $147.55 | 7.5 | $1,000 | 1.1% |
| 🟡 | DVN | $48.98 | 7.4 | $1,000 | 1.1% |
| 🟢 | KTOS | $46.74 | 7.4 | $1,000 | 1.1% |
| 🟢 | NKE | $37.35 | 7.3 | $1,000 | 1.1% |
| 🟢 | GOOGL | $330.65 | 7.3 | $1,000 | 1.1% |
| 🟢 | HOOD | $115.28 | 7.3 | $1,000 | 1.1% |
| 🟡 | ANET | $192.93 | 7.2 | $1,000 | 1.1% |
| 🟡 | UBER | $71.08 | 7.2 | $1,000 | 1.1% |
_(put/call detail: Section 6)_
_...and 43 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 18 positions | Total contribution: $-9,000/month (-10.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | ABNB | $169.63 | 5.9 | $-500 | 0.0% |
| 🟡 | CRWD | $207.80 | 5.8 | $-500 | 0.0% |
| 🟡 | BA | $206.42 | 5.7 | $-500 | 0.0% |
| 🟢 | ZBH | $94.61 | 5.6 | $-500 | 0.0% |
| 🟡 | REGN | $807.65 | 5.6 | $-500 | 0.0% |
| 🟡 | COIN | $174.72 | 5.5 | $-500 | 0.0% |
| 🟢 | SBUX | $100.04 | 5.5 | $-500 | 0.0% |
| 🟡 | PFE | $27.78 | 5.4 | $-500 | 0.0% |
| 🟢 | DIS | $104.18 | 5.3 | $-500 | 0.0% |
| 🟢 | BRKB | $0.00 | 5.3 | $-500 | 0.0% |
| 🟡 | SONO | $14.55 | 5.2 | $-500 | 0.0% |
| 🟡 | ETSY | $71.19 | 5.2 | $-500 | 0.0% |
| 🟡 | PYPL | $52.17 | 5.1 | $-500 | 0.0% |
| 🟡 | ADBE | $254.86 | 4.9 | $-500 | 0.0% |
| 🟢 | MMYT | $49.06 | 4.9 | $-500 | 0.0% |
| 🟡 | XYZ | $79.40 | 4.5 | $-500 | 0.0% |
| 🟢 | CCJ | $100.41 | 3.9 | $-500 | 0.0% |
| 🟢 | NVO | $44.56 | 3.7 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 40 positions (43.0%)
- 🟡 YELLOW (Neutral): 51 positions (54.8%)
- 🔴 RED (Extended/Overbought): 2 positions (2.2%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** CAUTIOUS_BULL
- **Note:** CAUTIOUS_BULL: technical signals green but — VIX 17.6 ≥ 16 (elevated, not complacent). New entries allowed, Tier 1-2 only, tighter strikes.
- **VIX:** 17.6 — VIX 17.6 sustained < 20
- **S&P 500:** 7636 (50d MA: 7602, 200d MA: 7152)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 121 | 6.93 | 50.4 | 53.9 | 61 | 🟡 NEUTRAL |
| Healthcare | 18 | 5.69 | 36.8 | 42.9 | 25 | 🟡 BUY stock/THIN premium |
| Consumer Cyclical | 33 | 6.29 | 26.6 | 37.0 | 59 | 🟢 BUY (rich premium) |
| Industrials | 35 | 7.18 | 40.3 | 42.1 | 46 | 🟡 NEUTRAL |
| Energy | 3 | 6.23 | 54.6 | 68.1 | 35 | 🟡 NEUTRAL |
| Consumer Defensive | 1 | 7.2 | 34.0 | 19.2 | 96 | 🟢 BUY (rich premium) |
| Utilities | 9 | 6.98 | 59.5 | 17.0 | 22 | 🟡 BUY stock/THIN premium |
| Communication Services | 35 | 7.61 | 56.9 | 25.4 | 58 | 🟢 BUY (rich premium) |
| Defense | 5 | 6.28 | 21.0 | 27.1 | 53 | 🟢 BUY (rich premium) |
| Brand-Quality (Non-AI) | 20 | 7.11 | 44.9 | 43.9 | 37 | 🟡 NEUTRAL |
| Basic Materials | 11 | 6.76 | 42.4 | 32.8 | 26 | 🟡 NEUTRAL |
| Financial Services | 35 | 6.08 | 51.6 | 38.3 | 52 | 🟡 NEUTRAL |
| Unknown | 1 | 5.3 | 50.0 | 50.0 | 0 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Consumer Cyclical:** Conv 6.3/10, RSI 26.6, 52W %ile 37.0 — 🟢 BUY — Oversold + rich premium (avg IVR 59, good for selling)
- ✓ **Communication Services:** Conv 7.6/10, RSI 56.9, 52W %ile 25.4 — 🟢 BUY — High conviction + rich premium (avg IVR 58)
- ✓ **Defense:** Conv 6.3/10, RSI 21.0, 52W %ile 27.1 — 🟢 BUY — Oversold + rich premium (avg IVR 53, good for selling)
- ✓ **Healthcare:** Conv 5.7/10, RSI 36.8, 52W %ile 42.9 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 25 < 40) — not attractive for CSPs/CCs
- ✓ **Utilities:** Conv 7.0/10, RSI 59.5, 52W %ile 17.0 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 22 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Defensive:** Conv 7.2/10, RSI 34.0, 52W %ile 19.2 — 🟢 BUY — Oversold + rich premium (avg IVR 96, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.9/10, RSI 50.4, 52W %ile 53.9 — 🟡 MONITOR — Neutral positioning
- ◇ **Basic Materials:** Conv 6.8/10, RSI 42.4, 52W %ile 32.8 — 🟡 MONITOR — Neutral positioning
- ◇ **Brand-Quality (Non-AI):** Conv 7.1/10, RSI 44.9, 52W %ile 43.9 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.2/10, RSI 40.3, 52W %ile 42.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Unknown:** Conv 5.3/10, RSI 50.0, 52W %ile 50.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.1/10, RSI 51.6, 52W %ile 38.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 6.2/10, RSI 54.6, 52W %ile 68.1 — 🟡 MONITOR — Neutral positioning


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


### Technology (34 positions, $2,811,167) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $395,592 | $0 | $395,592 | 🟡 | 7.0 | 🟡 MONITOR |
| TSM | $217,680 | $43,536 | $261,216 | 🟡 | 8.2 | 🟡 MONITOR |
| CRM | $73,248 | $170,912 | $244,160 | 🟡 | 6.8 | 🟡 MONITOR |
| ALAB | $180,324 | $60,108 | $240,432 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ADBE | $76,458 | $152,916 | $229,374 | 🟡 | 4.9 | 🟡 MONITOR |
| MU | $205,554 | $0 | $205,554 | 🟡 | 8.4 | 🟡 MONITOR |
| OKTA | $34,548 | $120,918 | $155,466 | 🔴 | 6.4 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| IBM | $95,976 | $23,994 | $119,970 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| PANW | $100,530 | $0 | $100,530 | 🟡 | 6.1 | 🟡 MONITOR |
| MSFT | $49,165 | $49,165 | $98,330 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TWLO | $22,719 | $68,157 | $90,876 | 🟡 | 6.6 | 🟡 MONITOR |
| NVDA | $89,468 | $0 | $89,468 | 🟡 | 8.8 | 🟡 MONITOR |
| CRWD | $62,340 | $20,780 | $83,120 | 🟡 | 5.8 | 🟡 MONITOR |
| ZS | $49,830 | $16,610 | $66,440 | 🟡 | 7.0 | 🟡 MONITOR |
| APH | $48,804 | $16,268 | $65,072 | 🟡 | 8.3 | 🟡 MONITOR |
| SHOP | $50,716 | $0 | $50,716 | 🟡 | 6.5 | 🟡 MONITOR |
| XYZ | $31,760 | $15,880 | $47,640 | 🟡 | 4.5 | 🟡 MONITOR |
| UBER | $42,648 | $0 | $42,648 | 🟡 | 7.2 | 🟡 MONITOR |
| FSLR | $40,620 | $0 | $40,620 | 🟡 | 7.8 | 🟡 MONITOR |
| SKHY | $39,726 | $0 | $39,726 | 🟡 | 8.2 | 🟡 MONITOR |
| IONQ | $19,070 | $7,628 | $26,698 | 🟡 | 7.0 | 🟡 MONITOR |
| AMKR | $25,675 | $0 | $25,675 | 🟢 | 8.4 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| RBRK | $17,764 | $0 | $17,764 | 🟡 | 6.7 | 🟡 MONITOR |
| PLTR | $16,953 | $0 | $16,953 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ASTS | $12,484 | $0 | $12,484 | 🟡 | 6.9 | 🟡 MONITOR |
| CRWV | $9,494 | $0 | $9,494 | 🟡 | 7.5 | 🟡 MONITOR |
| LYFT | $1,490 | $7,450 | $8,940 | 🟡 | 7.8 | 🟡 MONITOR |
| LASR | $8,198 | $0 | $8,198 | 🟡 | 7.5 | 🟡 MONITOR |
| CIFR | $6,760 | $0 | $6,760 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| SONO | $0 | $5,820 | $5,820 | 🟡 | 5.2 | 🟡 MONITOR |
| INFY | $1,093 | $1,093 | $2,186 | 🟢 | 6.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QBTS | $1,712 | $0 | $1,712 | 🟡 | 6.4 | 🟡 MONITOR |
| QUBT | $804 | $0 | $804 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ONDS | $729 | $0 | $729 | 🟡 | 7.0 | 🟡 MONITOR |

### Industrials (9 positions, $1,279,475) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $147,000 | $392,000 | $539,000 | 🟡 | 6.5 | 🟡 MONITOR |
| GEV | $285,312 | $95,104 | $380,416 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| BE | $161,568 | $53,856 | $215,424 | 🔴 | 7.1 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| VRT | $52,578 | $0 | $52,578 | 🟢 | 8.3 | 🟢 ATTRACTIVE — let run |
| RKLB | $37,842 | $0 | $37,842 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |
| BWXT | $31,342 | $0 | $31,342 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| SPCX | $14,755 | $0 | $14,755 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run |
| KTOS | $4,674 | $0 | $4,674 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| PL | $3,444 | $0 | $3,444 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |

### Communication Services (7 positions, $961,198) — 🟢 BUY — High conviction + rich premium (avg IVR 58) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $261,476 | $65,369 | $326,845 | 🟡 | 8.0 | 🟡 MONITOR |
| APP | $183,036 | $61,012 | $244,048 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $121,648 | $45,618 | $167,266 | 🟡 | 6.4 | 🟡 MONITOR |
| GOOGL | $99,195 | $0 | $99,195 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| NBIS | $48,070 | $0 | $48,070 | 🟡 | 7.5 | 🟡 MONITOR |
| RBLX | $31,164 | $13,356 | $44,520 | 🟡 | 8.0 | 🟡 MONITOR |
| DIS | $20,836 | $10,418 | $31,254 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Financial Services (8 positions, $632,711) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| COIN | $69,888 | $139,776 | $209,664 | 🟡 | 5.5 | 🟡 MONITOR |
| MA | $170,250 | $0 | $170,250 | 🟡 | 6.9 | 🟡 MONITOR |
| PYPL | $31,302 | $62,604 | $93,906 | 🟡 | 5.1 | 🟡 MONITOR |
| JPM | $70,942 | $0 | $70,942 | 🟡 | 6.5 | 🟡 MONITOR |
| CRCL | $37,196 | $18,598 | $55,794 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| HOOD | $11,528 | $0 | $11,528 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run |
| RIOT | $8,828 | $2,207 | $11,035 | 🟡 | 7.0 | 🟡 MONITOR |
| HUT | $9,592 | $0 | $9,592 | 🟡 | 7.5 | 🟡 MONITOR |

### Healthcare (7 positions, $516,404) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 25 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ISRG | $141,296 | $0 | $141,296 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |
| UNH | $78,612 | $39,306 | $117,918 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| LLY | $112,421 | $0 | $112,421 | 🟡 | 7.0 | 🟡 MONITOR |
| REGN | $80,765 | $0 | $80,765 | 🟡 | 5.6 | 🟡 MONITOR |
| NVO | $22,280 | $8,912 | $31,192 | 🟢 | 3.7 | 🟢 ATTRACTIVE — let run |
| ZBH | $9,461 | $9,461 | $18,922 | 🟢 | 5.6 | 🟢 ATTRACTIVE — let run |
| PFE | $13,890 | $0 | $13,890 | 🟡 | 5.4 | 🟡 MONITOR |

### Consumer Cyclical (12 positions, $443,470) — 🟢 BUY — Oversold + rich premium (avg IVR 59, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $109,040 | $27,260 | $136,300 | 🟡 | 6.8 | 🟡 MONITOR |
| AMZN | $50,480 | $25,240 | $75,720 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ABNB | $16,963 | $50,889 | $67,852 | 🟡 | 5.9 | 🟡 MONITOR |
| BABA | $54,700 | $0 | $54,700 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TSLA | $36,781 | $0 | $36,781 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MMYT | $19,624 | $4,906 | $24,530 | 🟢 | 4.9 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| JD | $8,100 | $8,100 | $16,200 | 🟡 | 8.2 | 🟡 MONITOR |
| ETSY | $7,119 | $7,119 | $14,238 | 🟡 | 5.2 | 🟡 MONITOR |
| CAVA | $5,651 | $0 | $5,651 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| DKNG | $4,732 | $0 | $4,732 | 🟡 | 6.0 | 🟡 MONITOR |
| BROS | $4,496 | $0 | $4,496 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CCL | $2,270 | $0 | $2,270 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (4 positions, $363,055) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ULTA | $108,372 | $54,186 | $162,558 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run |
| ANET | $96,465 | $57,879 | $154,344 | 🟡 | 7.2 | 🟡 MONITOR |
| NKE | $0 | $26,145 | $26,145 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run |
| SBUX | $20,008 | $0 | $20,008 | 🟢 | 5.5 | 🟢 ATTRACTIVE — let run |

### Defense (3 positions, $196,844) — 🟢 BUY — Oversold + rich premium (avg IVR 53, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| NOC | $103,114 | $0 | $103,114 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| LMT | $52,446 | $0 | $52,446 | 🟡 | 6.8 | 🟡 MONITOR |
| BA | $41,284 | $0 | $41,284 | 🟡 | 5.7 | 🟡 MONITOR |

### Utilities (3 positions, $117,712) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 22 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $60,440 | $15,110 | $75,550 | 🟡 | 7.0 | 🟡 MONITOR |
| CEG | $29,390 | $0 | $29,390 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |
| OKLO | $12,771 | $0 | $12,771 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |

### Basic Materials (2 positions, $109,857) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $75,546 | $12,591 | $88,137 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MP | $16,290 | $5,430 | $21,720 | 🟡 | 6.7 | 🟡 MONITOR |

### Energy (2 positions, $19,837) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| CCJ | $10,041 | $0 | $10,041 | 🟢 | 3.9 | 🟢 ATTRACTIVE — let run |
| DVN | $9,796 | $0 | $9,796 | 🟡 | 7.4 | 🟡 MONITOR |

### Consumer Defensive (1 positions, $10,583) — 🟢 BUY — Oversold + rich premium (avg IVR 96, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,583 | $0 | $10,583 | 🟡 | 7.2 | 🟡 MONITOR |

### Unknown (1 positions, $0) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| BRKB | $0 | $0 | $0 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 8.7% ($647,904)
- 🟡 MONITOR: 58.6% ($4,370,788)
- 🟢 HEALTHY: 32.7% ($2,443,620)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🔴 RED

**Summary:** 🔴 ALERT — 2 indicators critical. Market fragility rising.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| 🔴 | BREADTH | 46.15384615384615 | RED | 60% (caution), 50% (alert) |
| 🔴 | AD_RATIO | 0.35135135135135137 | RED | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 267 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.40% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟠 30-day crash probability: 53.9% — Action: 🟠 HIGH RISK: Reduce gross exposure by 30-40%
- 🔴 60-day crash probability: 90.8%
- 🔴 90-day crash probability: 95.0%
- 📌 Primary risk factor: AD_RATIO critical

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▄▄`
  - 2026-09-01: 48% → 2026-09-10: 54% (rising, +6pp)

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
RED FLAG — Stage 2-3 Rotation (CRASH RISK: 54% prob in 30d)
  ⚠️ EMERGENCY PROTOCOL ACTIVATED

  Probability-Driven Threshold: 54% crash risk in next 30 days
  → Cut 35% of gross exposure immediately
  → Raise cash to 75% of portfolio
  → 60-day outlook: 91% probability (heightened vigilance)

  Account A Actions:
    1. Close ALL overbought positions (RSI >70) — don't wait for 70% profit
    2. Close remaining naked calls (or hedge heavily with long puts)
    3. Reduce notional from 100% → 65% of normal
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

- **Technology concentration:** 37.7% of notional (121 positions, $2,811,167)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $858,531 live — 72% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $326,288 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $143,559 across NBIS, CRWV, RKLB, OKLO, SPCX, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-08 (2 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.

Underperformance proxy: no tracked name diverging >10pp from SPX over 7 days.


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | ADBE | C | 230.0 | 8 | 100% | $23,000 |  |
| Account A (232) | ADBE | C | 240.0 | 36 | 100% | $24,000 |  |
| Account A (232) | ADBE | P | 260.0 | 36 | 100% | $26,000 |  |
| Account A (232) | ADBE | C | 230.0 | 99 | 100% | $23,000 |  |
| Account A (232) | AXON | C | 450.0 | 8 | 100% | $45,000 |  |
| Account A (232) | AXON | C | 470.0 | 8 | 100% | $47,000 |  |
| Account A (232) | AXON | P | 570.0 | 8 | 100% | $57,000 |  |
| Account A (232) | AXON | P | 540.0 | 99 | 100% | $54,000 |  |
| Account A (232) | AXON | P | 560.0 | 99 | 100% | $56,000 |  |
| Account A (232) | COIN | P | 250.0 | 8 | 100% | $25,000 |  |
| Account A (232) | COIN | C | 170.0 | 36 | 100% | $17,000 |  |
| Account A (232) | CRCL | P | 105.0 | 8 | 100% | $10,500 |  |
| Account A (232) | CRCL | C | 85.0 | 36 | 100% | $8,500 |  |
| Account A (232) | CRCL | C | 90.0 | 99 | 100% | $9,000 |  |
| Account A (232) | CRM | C | 175.0 | 8 | 100% | $17,500 |  |
| Account A (232) | CRM | C | 185.0 | 71 | 100% | $18,500 |  |
| Account A (232) | CRM | C | 210.0 | 99 | 100% | $21,000 |  |
| Account A (232) | DIS | P | 110.0 | 99 | 100% | $22,000 |  |
| Account A (232) | ETSY | C | 60.0 | 99 | 100% | $6,000 |  |
| Account A (232) | ETSY | P | 75.0 | 99 | 100% | $7,500 |  |
| Account A (232) | IBM | P | 270.0 | 36 | 100% | $27,000 |  |
| Account A (232) | IONQ | P | 40.0 | 99 | 100% | $8,000 |  |
| Account A (232) | ISRG | P | 370.0 | 36 | 100% | $37,000 |  |
| Account A (232) | META | C | 650.0 | 99 | 100% | $65,000 |  |
| Account A (232) | MP | P | 60.0 | 99 | 100% | $6,000 |  |
_...and 61 more within 120 DTE (not shown)_

- **Worst case (all shown):** $2,164,450 across 86 positions
- **Realistic (>=30% prob):** $872,950 across 41 positions
- **Likely (>=50% prob):** $872,950 across 41 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 1

- OKTA C 140.0 (Account A (232)) — 100% probability, RED heat


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


## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-9,600 to $-9,600 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (0 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $0/month contribution from MODERATE conviction positions
- ✅ None — all CRITICAL positions are RED/close candidates

#### 3. Let Run — Nothing Needed 🟢 (40 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 40 healthy positions contribute $40,000/month baseline (expected)
- ✅ 40 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (4 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 4 Tier 1 entries = $15,200/month; closes gap from $-9,600 to $-24,800 (16.9% closure)
  - APP: Conv 9.1/10 | RSI 46.3 | Value $244,048 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 42.3 | Value $380,416
  - AMKR: Conv 8.4/10 | RSI 51.4 | Value $25,675 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it
  - VRT: Conv 8.3/10 | RSI 50.9 | Value $52,578

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 93
- 🔴 Critical actions: 0 closes + 0 monitors
- 🟡 Yellow cautions: 49
- 🟢 Green healthy: 40
- 📊 Market regime: CAUTIOUS_BULL

**Gap Closure Summary:**

- Current gap: $-9,600 (-10.7% below target)
- After closes: $-9,600 (saves ~0.0%)
- After new Tier 1 entries: $-24,800 (16.9% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-10 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_