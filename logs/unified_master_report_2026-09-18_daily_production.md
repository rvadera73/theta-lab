# UNIFIED MASTER REPORT — DAILY (325 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** September 18, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $7,642,860
- **Total option requirement:** $2,707,034
- **Positions with short puts:** 93
- **Positions with short calls:** 45
- **YTD Net Premium:** $274,245 (live from transactions)
- **Month-to-Date Premium:** $33,160
- **Snapshot currency:** 2026-08-22

### Two Lenses on Monthly Performance

_(both derived from your transaction history)_

#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]

| Account | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | YTD |
|---|---|---|---|---|---|---|---|---|---|---|
| Account A (232) | 10,255 | 12,483 | 23,800 | 20,880 | -1,244 | -2,884 | 20,362 | 50,309 | 28,172 | 162,133 |
| Account B (275) | 31 | 3,322 | 1,546 | 4,894 | 9,709 | 3,948 | 575 | 3,476 | 2,614 | 30,115 |
| Account C (634) | 31 | 934 | 449 | 1,959 | 4,435 | 1,321 | 2,286 | 6,028 | 1,624 | 19,067 |
| Fidelity (Rahul) | 17 | 1,824 | 1,231 | 5,580 | 4,947 | 10,629 | 5,151 | 3,339 | 750 | 33,468 |
| Fidelity (Rajul — Rollover IRA) | 0 | 0 | 0 | 944 | 932 | 0 | 667 | 3,508 | 0 | 6,051 |
| Fidelity (Rajul — Roth IRA) | 0 | 0 | 0 | 95 | 189 | 1,028 | 1,326 | 1,196 | 0 | 3,834 |
| Robinhood (Individual) | 0 | 107 | 0 | 0 | 205 | -9 | 0 | 609 | 0 | 912 |
| Robinhood (Traditional IRA) | 0 | 518 | 816 | 6,275 | 2,879 | 2,087 | 517 | 5,573 | 0 | 18,665 |
| **TOTAL** | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 33,160 | 274,245 |
| Gross SOLD (STO, opened this month) | 181,739 | 68,408 | 199,758 | 324,125 | 349,672 | 243,331 | 135,826 | 242,546 | 88,613 | 1,834,018 |
| Net REALIZED (FIFO, closed this month) | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 33,160 | 274,245 |

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
| Account A (232) | $403,000 | 17.2% | $5,190,018 | $934,203 | Margin | 🔴 OVER CAP | $28,615 | ✅ $-1,259 |
| Account B (275) | $261,000 | 11.1% | $364,503 | $294,050 | Cash-Sec | 🔴 COVERAGE GAP | $10,669 | ✅ $-469 |
| Account C (634) | $266,000 | 11.4% | $325,407 | $211,950 | Cash-Sec | ⚠️ WATCH | $10,874 | ✅ $-478 |
| Fidelity (Rahul) | $498,560 | 21.3% | $711,592 | $631,334 | Cash-Sec | 🔴 COVERAGE GAP | $20,380 | ✅ $-896 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $51,589 | $53,016 | Cash-Sec | 🔴 COVERAGE GAP | $1,601 | ✅ $-70 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $170,964 | $161,850 | Cash-Sec | 🔴 COVERAGE GAP | $5,236 | ✅ $-230 |
| Vanguard (Rahul) | $320,492 | 13.7% | $496,253 | $420,630 | Cash-Sec | 🔴 COVERAGE GAP | $13,100 | ✅ $-577 |
| Robinhood (Individual) | $13,000 | 0.6% | $27,436 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $531 | ✅ $-23 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $305,098 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,993 | ✅ $-395 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $7,642,860 | $2,707,034 |  |  |  |  |

- **Account A (232):** 169 option positions | Monthly target: $28,615 | Equity: ADBE 400sh, APP 100sh, AXON 200sh, COIN 200sh, CRCL 100sh +14 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 21 option positions | Monthly target: $10,669 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 21 option positions | Monthly target: $10,874 | Equity: ABNB 100sh, NKE 100sh, PL 100sh, TWLO 324sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ⚠️ WATCH reading above
- **Fidelity (Rahul):** 42 option positions | Monthly target: $20,380 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
  - ⚠️ Balance as of 2026-07-31 (49 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,601 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
  - ⚠️ Balance as of 2026-07-31 (49 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Rollover IRA):** 14 option positions | Monthly target: $5,236
  - ⚠️ Balance as of 2026-07-31 (49 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Vanguard (Rahul):** 28 option positions | Monthly target: $13,101
  - ⚠️ Balance as of 2026-07-31 (49 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $531 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,993
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (49 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (110 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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
- Actual YTD: $274,245.0
- Gap to close: $625,755.0 (69.5%)
- Monthly average (YTD): $30,472
- Monthly average needed: $100,000
- Monthly gap: $-4,400

**Position tier distribution → gap closure:**

- Tier 1 (13 positions): $49,400/month (49% of $100,000 target)
- Tier 2 (64 positions): $64,000/month (64% of target)
- Tier 3 (18 positions): $-9,000/month (-9% drag)
- Current total: 95 positions = $104,400/month (104% of target)

**Gap closure path:**

- To hit $100,000 target: Need 0 more Tier 1 positions
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
- Regime: BULL (applies 100% of base)
- Adjusted Target: $250,000 gross / $100,000 net

**Account Targets (Regime-Adjusted)** — complements Section 0's Per-Account
Breakdown 'Target' column: that one is the raw monthly_target; these are the
same targets scaled by the current regime's adjustment factor, gross+net.

| Account | Gross | Net |
|---|---|---|
| Account A (232) | $71,537 | $28,615 |
| Account B (275) | $26,672 | $10,669 |
| Account C (634) | $27,185 | $10,874 |
| Fidelity (Rahul) | $50,950 | $20,380 |
| Fidelity (Rajul — Roth IRA) | $4,002 | $1,601 |
| Fidelity (Rajul — Rollover IRA) | $13,090 | $5,236 |
| Vanguard (Rahul) | $32,752 | $13,101 |
| Robinhood (Individual) | $1,327 | $531 |
| Robinhood (Traditional IRA) | $22,482 | $8,993 |
| **TOTAL** | $249,997 | $100,000 |


## Section 1: SYSTEM STATUS & PORTFOLIO SNAPSHOT

- **Total open positions:** 325
- **Unique tickers:** 95
- **Active accounts:** 10
- **Data currency:** 2026-09-18
- **Live prices:** 94 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (13 positions): $49,400/month — each contributes $3,800/month (4.2% of $100,000)
- Tier 2 (64 positions): $64,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (18 positions): $-9,000/month — each drags -$500/month (-0.6% of target)
- Portfolio: 104,400/month (104% of target) — Need $-4,400 more

**HIGH (Tier 1: 8-10) conviction** — 13 positions | Total contribution: $49,400/month (49.4% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $316.11 | 9.1 | $3,800 | 3.8% |
| 🟢 | GOOGL | $350.96 | 8.8 | $3,800 | 3.8% |
| 🟡 | IONQ | $38.09 | 8.5 | $3,800 | 3.8% |
| 🟡 | TSM | $432.17 | 8.5 | $3,800 | 3.8% |
| 🟢 | GEV | $934.21 | 8.4 | $3,800 | 3.8% |
| 🟡 | ANET | $198.62 | 8.3 | $3,800 | 3.8% |
| 🟡 | RKLB | $64.22 | 8.2 | $3,800 | 3.8% |
| 🟡 | JD | $26.95 | 8.2 | $3,800 | 3.8% |
| 🟡 | QUBT | $8.31 | 8.2 | $3,800 | 3.8% |
| 🟡 | SKHY | $184.49 | 8.2 | $3,800 | 3.8% |
| 🟡 | AMKR | $48.50 | 8.1 | $3,800 | 3.8% |
| 🟡 | RBLX | $46.74 | 8.0 | $3,800 | 3.8% |
| 🟢 | ALAB | $297.51 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 64 positions | Total contribution: $64,000/month (64.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | LYFT | $15.26 | 7.8 | $1,000 | 1.0% |
| 🟡 | ISRG | $391.98 | 7.8 | $1,000 | 1.0% |
| 🟢 | BROS | $39.53 | 7.8 | $1,000 | 1.0% |
| 🟡 | QBTS | $16.61 | 7.8 | $1,000 | 1.0% |
| 🟡 | META | $673.93 | 7.6 | $1,000 | 1.0% |
| 🟡 | NVDA | $219.73 | 7.6 | $1,000 | 1.0% |
| 🟡 | ASTS | $59.02 | 7.6 | $1,000 | 1.0% |
| 🟡 | MU | $995.29 | 7.6 | $1,000 | 1.0% |
| 🟢 | CAVA | $51.55 | 7.6 | $1,000 | 1.0% |
| 🟢 | ALB | $111.46 | 7.5 | $1,000 | 1.0% |
| 🟡 | UBER | $70.17 | 7.5 | $1,000 | 1.0% |
| 🟡 | LASR | $39.03 | 7.5 | $1,000 | 1.0% |
| 🟢 | HUT | $91.97 | 7.5 | $1,000 | 1.0% |
| 🟢 | MP | $48.24 | 7.4 | $1,000 | 1.0% |
| 🟡 | DVN | $48.57 | 7.4 | $1,000 | 1.0% |
| 🟢 | APH | $78.90 | 7.4 | $1,000 | 1.0% |
| 🟡 | NOC | $524.38 | 7.4 | $1,000 | 1.0% |
| 🟢 | KTOS | $47.21 | 7.4 | $1,000 | 1.0% |
| 🟢 | NKE | $36.31 | 7.3 | $1,000 | 1.0% |
| 🟡 | TWLO | $240.37 | 7.3 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 44 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 18 positions | Total contribution: $-9,000/month (-9.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🔴 | CRWD | $236.90 | 5.9 | $-500 | 0.0% |
| 🟢 | ZBH | $95.16 | 5.9 | $-500 | 0.0% |
| 🟡 | ADBE | $249.02 | 5.8 | $-500 | 0.0% |
| 🟢 | CRCL | $92.29 | 5.8 | $-500 | 0.0% |
| 🟡 | BABA | $112.98 | 5.7 | $-500 | 0.0% |
| 🟢 | MMYT | $47.78 | 5.6 | $-500 | 0.0% |
| 🟡 | REGN | $785.09 | 5.6 | $-500 | 0.0% |
| 🟡 | COIN | $190.16 | 5.5 | $-500 | 0.0% |
| 🟢 | CEG | $257.86 | 5.5 | $-500 | 0.0% |
| 🟢 | PFE | $27.38 | 5.4 | $-500 | 0.0% |
| 🟢 | BRKB | $0.00 | 5.3 | $-500 | 0.0% |
| 🟢 | SMR | $8.62 | 5.3 | $-500 | 0.0% |
| 🟢 | TTD | $14.11 | 5.1 | $-500 | 0.0% |
| 🟢 | DIS | $103.09 | 5.0 | $-500 | 0.0% |
| 🟢 | PYPL | $52.74 | 4.5 | $-500 | 0.0% |
| 🟡 | XYZ | $76.31 | 4.2 | $-500 | 0.0% |
| 🟡 | CCJ | $91.21 | 4.2 | $-500 | 0.0% |
| 🟡 | NVO | $42.98 | 3.3 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 44 positions (46.3%)
- 🟡 YELLOW (Neutral): 48 positions (50.5%)
- 🔴 RED (Extended/Overbought): 3 positions (3.2%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.4 — VIX 15.4 sustained < 20
- **S&P 500:** 7626 (50d MA: 7617, 200d MA: 7183)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 115 | 6.96 | 44.9 | 51.7 | 49 | 🟡 NEUTRAL |
| Healthcare | 21 | 5.73 | 44.2 | 44.6 | 16 | 🟡 NEUTRAL |
| Consumer Cyclical | 33 | 6.59 | 26.2 | 37.1 | 40 | 🟢 BUY (rich premium) |
| Industrials | 33 | 7.3 | 45.9 | 38.7 | 29 | 🟡 NEUTRAL |
| Energy | 3 | 6.33 | 48.7 | 61.5 | 35 | 🟡 NEUTRAL |
| Consumer Defensive | 1 | 7.2 | 65.2 | 23.4 | 94 | 🔴 REDUCE |
| Utilities | 7 | 6.4 | 48.8 | 7.7 | 22 | 🟡 BUY stock/THIN premium |
| Communication Services | 39 | 7.69 | 53.3 | 25.2 | 33 | 🟡 BUY stock/THIN premium |
| Defense | 5 | 6.66 | 34.0 | 23.6 | 27 | 🟡 BUY stock/THIN premium |
| Brand-Quality (Non-AI) | 20 | 7.34 | 39.5 | 42.9 | 25 | 🟡 BUY stock/THIN premium |
| Basic Materials | 11 | 7.46 | 23.1 | 20.5 | 24 | 🟡 BUY stock/THIN premium |
| Financial Services | 36 | 5.77 | 50.9 | 42.3 | 50 | 🟡 NEUTRAL |
| Unknown | 1 | 5.3 | 50.0 | 50.0 | 0 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Basic Materials:** Conv 7.5/10, RSI 23.1, 52W %ile 20.5 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 24 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Cyclical:** Conv 6.6/10, RSI 26.2, 52W %ile 37.1 — 🟢 BUY — Oversold + rich premium (avg IVR 40, good for selling)
- ✓ **Brand-Quality (Non-AI):** Conv 7.3/10, RSI 39.5, 52W %ile 42.9 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 25 < 40) — not attractive for CSPs/CCs
- ✓ **Communication Services:** Conv 7.7/10, RSI 53.3, 52W %ile 25.2 — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 33 < 40)
- ✓ **Defense:** Conv 6.7/10, RSI 34.0, 52W %ile 23.6 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 27 < 40) — not attractive for CSPs/CCs
- ✓ **Utilities:** Conv 6.4/10, RSI 48.8, 52W %ile 7.7 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 22 < 40) — not attractive for CSPs/CCs

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- ✗ **Consumer Defensive:** Conv 7.2/10, RSI 65.2, 52W %ile 23.4 — 🔴 REDUCE — Overbought / extended

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 7.0/10, RSI 44.9, 52W %ile 51.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.3/10, RSI 45.9, 52W %ile 38.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Unknown:** Conv 5.3/10, RSI 50.0, 52W %ile 50.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 5.8/10, RSI 50.9, 52W %ile 42.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 5.7/10, RSI 44.2, 52W %ile 44.6 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 6.3/10, RSI 48.7, 52W %ile 61.5 — 🟡 MONITOR — Neutral positioning


## Section 5: POSITION DISTRIBUTION BY ACCOUNT

- **Account A (232):** 169 positions (52.0%) `██████████████████████████`
- **Fidelity (Rahul):** 42 positions (12.9%) `██████`
- **Vanguard (Rahul):** 28 positions (8.6%) `████`
- **Account B (275):** 21 positions (6.5%) `███`
- **Account C (634):** 21 positions (6.5%) `███`
- **Robinhood (Traditional IRA):** 18 positions (5.5%) `██`
- **Fidelity (Rajul — Rollover IRA):** 14 positions (4.3%) `██`
- **Fidelity (Rajul — Roth IRA):** 8 positions (2.5%) `█`
- **Robinhood (Individual):** 4 positions (1.2%) ``
- **Fidelity 401K (Rahul):** 0 positions (0.0%) ``


## Section 6: POSITION HEAT MATRIX BY SECTOR — Sector -> Symbol, Put/Call/Total Value, Heat, Suggestion


### Technology (34 positions, $2,771,857) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $361,998 | $90,499 | $452,497 | 🟡 | 6.7 | 🟡 MONITOR |
| CRM | $95,260 | $142,890 | $238,150 | 🟡 | 6.5 | 🟡 MONITOR |
| ADBE | $74,706 | $149,412 | $224,118 | 🟡 | 5.8 | 🟡 MONITOR |
| ALAB | $178,506 | $29,751 | $208,257 | 🟢 | 8.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MU | $199,058 | $0 | $199,058 | 🟡 | 7.6 | 🟡 MONITOR |
| TSM | $129,651 | $43,217 | $172,868 | 🟡 | 8.5 | 🟡 MONITOR |
| MSFT | $98,504 | $49,252 | $147,756 | 🟡 | 6.8 | 🟡 MONITOR |
| OKTA | $18,411 | $128,877 | $147,288 | 🔴 | 6.4 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| PANW | $143,928 | $0 | $143,928 | 🟡 | 7.0 | 🟡 MONITOR |
| CRWD | $94,758 | $23,690 | $118,448 | 🔴 | 5.9 | 🔴 TRIM CALL (delta/assignment risk); 🟢 HOLD PUT (near max profit, unaffected — a short call gains protection in a decline, don't close it purely on crash fears) |
| IBM | $92,114 | $23,029 | $115,143 | 🟡 | 6.0 | 🟡 MONITOR |
| TWLO | $24,037 | $72,110 | $96,146 | 🟡 | 7.3 | 🟡 MONITOR |
| NVDA | $87,892 | $0 | $87,892 | 🟡 | 7.6 | 🟡 MONITOR |
| ZS | $58,329 | $19,443 | $77,772 | 🔴 | 7.2 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| SHOP | $51,146 | $0 | $51,146 | 🟡 | 6.8 | 🟡 MONITOR |
| XYZ | $30,524 | $15,262 | $45,786 | 🟡 | 4.2 | 🟡 MONITOR |
| UBER | $42,100 | $0 | $42,100 | 🟡 | 7.5 | 🟡 MONITOR |
| FSLR | $38,966 | $0 | $38,966 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| AMKR | $24,250 | $0 | $24,250 | 🟡 | 8.1 | 🟡 MONITOR |
| IONQ | $22,854 | $0 | $22,854 | 🟡 | 8.5 | 🟡 MONITOR |
| SKHY | $18,449 | $0 | $18,449 | 🟡 | 8.2 | 🟡 MONITOR |
| PLTR | $17,405 | $0 | $17,405 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| APH | $15,779 | $0 | $15,779 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ASTS | $11,804 | $0 | $11,804 | 🟡 | 7.6 | 🟡 MONITOR |
| RBRK | $10,541 | $0 | $10,541 | 🟡 | 6.7 | 🟡 MONITOR |
| LYFT | $1,526 | $7,630 | $9,156 | 🟡 | 7.8 | 🟡 MONITOR |
| CRWV | $8,037 | $0 | $8,037 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LASR | $7,806 | $0 | $7,806 | 🟡 | 7.5 | 🟡 MONITOR |
| CIFR | $6,894 | $0 | $6,894 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| SONO | $0 | $6,168 | $6,168 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| INFY | $1,086 | $1,086 | $2,172 | 🟢 | 6.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QBTS | $1,661 | $0 | $1,661 | 🟡 | 7.8 | 🟡 MONITOR |
| QUBT | $831 | $0 | $831 | 🟡 | 8.2 | 🟡 MONITOR |
| ONDS | $730 | $0 | $730 | 🟡 | 7.0 | 🟡 MONITOR |

### Industrials (9 positions, $1,127,697) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $90,453 | $316,586 | $407,039 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |
| GEV | $280,262 | $93,421 | $373,682 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| BE | $162,282 | $54,094 | $216,376 | 🟡 | 6.6 | 🟡 MONITOR |
| VRT | $49,316 | $0 | $49,316 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |
| RKLB | $44,957 | $0 | $44,957 | 🟡 | 8.2 | 🟡 MONITOR |
| BWXT | $29,110 | $0 | $29,110 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| KTOS | $4,721 | $0 | $4,721 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| PL | $1,634 | $0 | $1,634 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |
| SMR | $862 | $0 | $862 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

### Communication Services (8 positions, $1,065,949) — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 33 < 40) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $269,572 | $67,393 | $336,965 | 🟡 | 7.6 | 🟡 MONITOR |
| APP | $221,274 | $94,832 | $316,105 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $115,232 | $43,212 | $158,444 | 🟡 | 7.0 | 🟡 MONITOR |
| GOOGL | $105,288 | $35,096 | $140,384 | 🟢 | 8.8 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NBIS | $42,910 | $0 | $42,910 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBLX | $23,370 | $14,022 | $37,392 | 🟡 | 8.0 | 🟡 MONITOR |
| DIS | $20,617 | $10,309 | $30,926 | 🟢 | 5.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TTD | $2,823 | $0 | $2,823 | 🟢 | 5.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Healthcare (7 positions, $794,657) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LLY | $229,814 | $114,907 | $344,721 | 🟡 | 6.7 | 🟡 MONITOR |
| ISRG | $156,792 | $39,198 | $195,990 | 🟡 | 7.8 | 🟡 MONITOR |
| UNH | $75,086 | $37,543 | $112,629 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |
| REGN | $78,509 | $0 | $78,509 | 🟡 | 5.6 | 🟡 MONITOR |
| NVO | $21,490 | $8,596 | $30,086 | 🟡 | 3.3 | 🟡 MONITOR |
| ZBH | $9,516 | $9,516 | $19,032 | 🟢 | 5.9 | 🟢 ATTRACTIVE — let run |
| PFE | $13,690 | $0 | $13,690 | 🟢 | 5.4 | 🟢 ATTRACTIVE — let run |

### Financial Services (8 positions, $677,648) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| COIN | $38,032 | $171,144 | $209,176 | 🟡 | 5.5 | 🟡 MONITOR |
| MA | $169,998 | $0 | $169,998 | 🟡 | 6.9 | 🟡 MONITOR |
| JPM | $69,464 | $34,732 | $104,196 | 🟡 | 6.4 | 🟡 MONITOR |
| PYPL | $31,641 | $63,282 | $94,923 | 🟢 | 4.5 | 🟢 ATTRACTIVE — let run |
| CRCL | $36,916 | $18,458 | $55,374 | 🟢 | 5.8 | 🟢 ATTRACTIVE — let run |
| HOOD | $23,509 | $0 | $23,509 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |
| RIOT | $9,020 | $2,255 | $11,275 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run |
| HUT | $9,197 | $0 | $9,197 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run |

### Consumer Cyclical (12 positions, $445,989) — 🟢 BUY — Oversold + rich premium (avg IVR 40, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $112,544 | $28,136 | $140,680 | 🟡 | 6.8 | 🟡 MONITOR |
| AMZN | $50,540 | $25,270 | $75,810 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ABNB | $16,525 | $49,575 | $66,100 | 🟡 | 6.8 | 🟡 MONITOR |
| BABA | $56,488 | $0 | $56,488 | 🟡 | 5.7 | 🟡 MONITOR |
| TSLA | $36,447 | $0 | $36,447 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MMYT | $19,110 | $4,778 | $23,888 | 🟢 | 5.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| JD | $8,085 | $8,085 | $16,170 | 🟡 | 8.2 | 🟡 MONITOR |
| ETSY | $7,328 | $7,328 | $14,656 | 🟡 | 6.7 | 🟡 MONITOR |
| CAVA | $5,155 | $0 | $5,155 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| DKNG | $4,444 | $0 | $4,444 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| BROS | $3,953 | $0 | $3,953 | 🟢 | 7.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CCL | $2,199 | $0 | $2,199 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (5 positions, $355,177) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 25 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ULTA | $108,104 | $54,052 | $162,156 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run |
| ANET | $79,448 | $59,586 | $139,034 | 🟡 | 8.3 | 🟡 MONITOR |
| NKE | $0 | $25,417 | $25,417 | 🟢 | 7.3 | 🟢 ATTRACTIVE — let run |
| SBUX | $19,160 | $0 | $19,160 | 🟡 | 6.1 | 🟡 MONITOR |
| ELF | $9,410 | $0 | $9,410 | 🟢 | 6.2 | 🟢 ATTRACTIVE — let run |

### Defense (3 positions, $197,306) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 27 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| NOC | $104,876 | $0 | $104,876 | 🟡 | 7.4 | 🟡 MONITOR |
| LMT | $53,216 | $0 | $53,216 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run |
| BA | $39,214 | $0 | $39,214 | 🟡 | 6.0 | 🟡 MONITOR |

### Basic Materials (2 positions, $97,315) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 24 < 40) — not attractive for CSPs/CCs 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $66,873 | $11,146 | $78,019 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MP | $14,472 | $4,824 | $19,296 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Utilities (3 positions, $79,693) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 22 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $42,516 | $0 | $42,516 | 🟡 | 6.7 | 🟡 MONITOR |
| CEG | $25,786 | $0 | $25,786 | 🟢 | 5.5 | 🟢 ATTRACTIVE — let run |
| OKLO | $11,391 | $0 | $11,391 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run |

### Energy (2 positions, $18,835) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| DVN | $9,714 | $0 | $9,714 | 🟡 | 7.4 | 🟡 MONITOR |
| CCJ | $9,121 | $0 | $9,121 | 🟡 | 4.2 | 🟡 MONITOR |

### Consumer Defensive (1 positions, $10,738) — 🔴 REDUCE — Overbought / extended

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,738 | $0 | $10,738 | 🟡 | 7.2 | 🟡 MONITOR |

### Unknown (1 positions, $0) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| BRKB | $0 | $0 | $0 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 5.6% ($428,501)
- 🟡 MONITOR: 60.6% ($4,634,956)
- 🟢 HEALTHY: 33.7% ($2,579,404)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🔴 RED

**Summary:** 🔴 ALERT — 2 indicators critical. Market fragility rising.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| 🔴 | BREADTH | 48.717948717948715 | RED | 60% (caution), 50% (alert) |
| 🔴 | AD_RATIO | 0.5625 | RED | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 270 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.27% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟠 30-day crash probability: 45.9% — Action: 🟡 CAUTION: Reduce overbought positions by 20-25%
- 🔴 60-day crash probability: 77.4%
- 🔴 90-day crash probability: 95.0%
- 📌 Primary risk factor: AD_RATIO critical

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▄▃▄`
  - 2026-09-01: 48% → 2026-09-18: 46% (flat, -2pp)

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
RED FLAG — Stage 2-3 Rotation (CRASH RISK: 46% prob in 30d)
  ⚠️ EMERGENCY PROTOCOL ACTIVATED

  Probability-Driven Threshold: 46% crash risk in next 30 days
  → Cut 20% of gross exposure immediately
  → Raise cash to 60% of portfolio
  → 60-day outlook: 77% probability (heightened vigilance)

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

- **Technology concentration:** 36.3% of notional (115 positions, $2,771,857)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $877,218 live — 82% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $188,647 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $127,767 across NBIS, CRWV, RKLB, OKLO, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-08 (10 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.

**⚠️ Underperformance proxy** — check these for credit news specifically:

- CRWV: -15.4% (7d) vs SPX -0.2% — >10pp gap
- NBIS: -10.8% (7d) vs SPX -0.2% — >10pp gap


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | ADBE | C | 230.0 | 0 | 100% | $23,000 |  |
| Account A (232) | IBM | P | 270.0 | 28 | 93% | $27,000 |  |
| Account B (275) | AMKR | P | 70.0 | 119 | 89% | $7,000 |  |
| Account C (634) | TWLO | C | 145.0 | 119 | 87% | $14,500 |  |
| Account C (634) | TWLO | C | 150.0 | 119 | 85% | $30,000 |  |
| Account A (232) | CRM | C | 185.0 | 63 | 84% | $18,500 |  |
| Account A (232) | MP | P | 60.0 | 91 | 84% | $6,000 |  |
| Account B (275) | CRM | C | 175.0 | 91 | 83% | $17,500 |  |
| Account A (232) | NVO | P | 50.0 | 91 | 83% | $5,000 |  |
| Account C (634) | CCJ | P | 110.0 | 119 | 82% | $11,000 |  |
| Account A (232) | RBLX | C | 40.0 | 28 | 81% | $8,000 |  |
| Account A (232) | PYPL | C | 42.5 | 63 | 80% | $21,250 |  |
| Account A (232) | AXON | P | 560.0 | 91 | 80% | $56,000 |  |
| Account C (634) | ABNB | C | 145.0 | 28 | 78% | $14,500 |  |
| Account A (232) | OKTA | C | 140.0 | 63 | 78% | $14,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | COIN | C | 170.0 | 28 | 77% | $17,000 |  |
| Account A (232) | AXON | P | 540.0 | 91 | 77% | $54,000 |  |
| Account A (232) | NFLX | P | 80.0 | 63 | 75% | $24,000 |  |
| Account A (232) | PYPL | C | 45.0 | 63 | 74% | $9,000 |  |
| Account A (232) | ETSY | C | 60.0 | 91 | 71% | $6,000 |  |
| Account A (232) | DIS | P | 110.0 | 91 | 71% | $22,000 |  |
| Account A (232) | NFLX | P | 77.5 | 63 | 70% | $15,500 |  |
| Account B (275) | AMKR | P | 55.0 | 119 | 70% | $5,500 |  |
| Account B (275) | BWXT | P | 160.0 | 119 | 70% | $16,000 |  |
| Account A (232) | ZBH | C | 85.0 | 91 | 70% | $8,500 |  |
_...and 87 more within 120 DTE (not shown)_

- **Worst case (all shown):** $3,237,250 across 112 positions
- **Realistic (>=30% prob):** $1,909,500 across 85 positions
- **Likely (>=50% prob):** $888,250 across 47 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 1

- OKTA C 140.0 (Account A (232)) — 78% probability, RED heat


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ⚠️ Last scan: 2026-09-01 (17 days ago)
- **CRM:** No new low-strike calls this week -- let existing ITM calls execute as planned.
- **MACRO:** No Tier CR trigger this week -- confirmation, not escalation.
- **MU:** Flag for next quarterly bucket review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET candidate) -- not an immediate reclass off one data point.
- ⚠️ Over 10 days since the last Seeking Alpha scan — run the weekly theme-scan skill.


## Section 6.9: ACTIVE DECISION TRACKER


**✅ axon_sept18_roll_450c** — RESOLVED (as of 2026-09-18)

Roll the AXON $450C (Sept 18 2026 expiry) out to a January 2027 call (~$560-580 strike, AXON's own missing rung in its Sept/Dec/March ladder) before Sept 18. Keep the $470C to settle against the 100 owned AXON shares as a clean covered assignment. Only 100 AXON shares exist to cover 2 ITM Sept-18 calls; rolling one removes the naked/short-stock risk that would otherwise be forced at expiry.

**⏳ pypl_naked_calls_cleanup** — OPEN

5 naked short call contracts on PYPL (0 shares owned), all ITM as of 2026-09-10: $45C x3 (Dec 18 2026), $47.5C x2 (Jan 15 2027). No shares exist to cover any of them. Lower urgency than the AXON Sept-18 pair (91-119 DTE at time of writing gives runway) but needs a roll-up/out or close before expiry approaches -- same structural risk as AXON, just further out.
  - Live check: 12 naked ITM contract(s) remaining (target: 0)

**⏳ crcl_naked_call_dec** — OPEN

1 naked short call on CRCL (0 shares owned), ITM as of 2026-09-10: $90C (Dec 18 2026). Smaller version of the same AXON/PYPL issue.
  - Live check: 1 naked ITM contract(s) remaining (target: 0)

**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 133.45761587251937
  - Live: macro_risk_level = RED

**⏳ be_puts_reduction** — OPEN

Reduce BE put exposure to zero over the next ~10 days (target: 2026-09-20) by closing/rolling out of all 6 open BE put legs across every account. BE is RED heat, RSI 77-81 (overbought/extended), and is the most widely-held name in the book -- also carries a naked short-call pair against it in Account A/Fidelity Rahul (no BE shares owned anywhere). Baseline as of 2026-09-10: Account A $170P (Jan 15 2027) x2 [Jan+Feb], Account B $180P (Feb 19 2027), Fidelity (Rahul) $190P (Jan 15 2027), Fidelity (Rajul - Rollover IRA) $200P (Jun 17 2027), Robinhood (Traditional) $180P (Jun 17 2027). Trader confirmed 2026-09-10 this should cover ALL open BE puts (not just the near-dated ones) -- an initial "Dec 2026 and before" framing didn't match any real BE put, since the earliest is Jan 15 2027.
KNOWN GAP: the automated check only sees 5 of these 6 legs -- the Robinhood (Traditional) $180P (Jun 17 2027) has an option-type parsing gap in that account's transaction reconstruction and won't count toward the live total below. This entry will show RESOLVED once the other 5 close even if that 6th one is still open -- manually confirm the Robinhood leg separately before treating BE exposure as fully closed.
  - Live check: 5 leg(s) open now (baseline was 6), target: 0



## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $-4,400 to $-4,400 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (1 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $1,000/month contribution from MODERATE conviction positions
- Names: CRWD (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (44 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 44 healthy positions contribute $44,000/month baseline (expected)
- ✅ 44 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (4 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 4 Tier 1 entries = $15,200/month; closes gap from $-4,400 to $-19,600 (15.2% closure)
  - APP: Conv 9.1/10 | RSI 49.1 | Value $316,105 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GOOGL: Conv 8.8/10 | RSI 53.6 | Value $140,384 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 53.6 | Value $373,682
  - ALAB: Conv 8.0/10 | RSI 51.8 | Value $208,257 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 95
- 🔴 Critical actions: 0 closes + 1 monitors
- 🟡 Yellow cautions: 45
- 🟢 Green healthy: 44
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $-4,400 (-4.4% below target)
- After closes: $-4,400 (saves ~0.0%)
- After new Tier 1 entries: $-19,600 (15.2% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-18 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_