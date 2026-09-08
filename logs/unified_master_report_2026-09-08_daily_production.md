# UNIFIED MASTER REPORT — DAILY (314 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** September 08, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $7,023,513
- **Total option requirement:** $2,593,364
- **Positions with short puts:** 85
- **Positions with short calls:** 39
- **YTD Net Premium:** $231,189 (live from transactions)
- **Month-to-Date Premium:** $-11
- **Snapshot currency:** 2026-08-22

### Two Lenses on Monthly Performance

_(both derived from your transaction history)_

#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]

| Account | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | YTD |
|---|---|---|---|---|---|---|---|---|---|---|
| Account A (232) | 10,255 | 12,483 | 23,800 | 20,880 | -1,244 | -2,884 | 20,362 | 50,309 | 0 | 133,961 |
| Account B (275) | 31 | 3,322 | 1,546 | 4,894 | 9,709 | 3,948 | 575 | 3,476 | 0 | 27,501 |
| Account C (634) | 31 | 934 | 449 | 1,959 | 4,435 | 1,321 | 2,286 | 6,028 | 0 | 17,443 |
| Fidelity (Rahul) | 17 | 1,824 | 1,231 | 5,580 | 4,947 | 10,629 | 5,151 | 3,339 | -11 | 32,707 |
| Robinhood (Individual) | 0 | 107 | 0 | 0 | 205 | -9 | 0 | 609 | 0 | 912 |
| Robinhood (Traditional IRA) | 0 | 518 | 816 | 6,275 | 2,879 | 2,087 | 517 | 5,573 | 0 | 18,665 |
| **TOTAL** | 10,334 | 19,188 | 27,842 | 39,588 | 20,931 | 15,092 | 28,891 | 69,334 | -11 | 231,189 |
| Gross SOLD (STO, opened this month) | 181,334 | 64,446 | 199,571 | 307,592 | 345,076 | 237,655 | 123,038 | 234,490 | 4,303 | 1,697,505 |
| Net REALIZED (FIFO, closed this month) | 10,334 | 19,188 | 27,842 | 39,588 | 20,931 | 15,092 | 28,891 | 69,334 | -11 | 231,189 |

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
| Account A (232) | $403,000 | 17.2% | $4,566,584 | $821,985 | Margin | 🔴 OVER CAP | $28,615 | ⚠️ $1,975 |
| Account B (275) | $261,000 | 11.1% | $364,170 | $291,950 | Cash-Sec | 🔴 COVERAGE GAP | $10,669 | ⚠️ $737 |
| Account C (634) | $266,000 | 11.4% | $335,281 | $214,450 | Cash-Sec | ⚠️ WATCH | $10,874 | ⚠️ $751 |
| Fidelity (Rahul) | $498,560 | 21.3% | $695,639 | $625,913 | Cash-Sec | 🔴 COVERAGE GAP | $20,380 | ⚠️ $1,407 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $53,263 | $52,012 | Cash-Sec | 🔴 COVERAGE GAP | $1,601 | ⚠️ $111 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $165,792 | $161,150 | Cash-Sec | 🔴 COVERAGE GAP | $5,236 | ⚠️ $362 |
| Vanguard (Rahul) | $320,492 | 13.7% | $507,659 | $425,904 | Cash-Sec | 🔴 COVERAGE GAP | $13,100 | ⚠️ $903 |
| Robinhood (Individual) | $13,000 | 0.6% | $27,618 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $531 | ⚠️ $37 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $307,508 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,993 | ⚠️ $621 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $7,023,513 | $2,593,364 |  |  |  |  |

- **Account A (232):** 161 option positions | Monthly target: $28,615 | Equity: ADBE 400sh, APP 100sh, AXON 100sh, COIN 100sh, CRM 300sh +13 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 20 option positions | Monthly target: $10,669 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 22 option positions | Monthly target: $10,874 | Equity: ABNB 100sh, NKE 100sh, TWLO 324sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ⚠️ WATCH reading above
- **Fidelity (Rahul):** 41 option positions | Monthly target: $20,380 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
  - ⚠️ Balance as of 2026-07-31 (39 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,601 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
  - ⚠️ Balance as of 2026-07-31 (39 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Rollover IRA):** 13 option positions | Monthly target: $5,236
  - ⚠️ Balance as of 2026-07-31 (39 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Vanguard (Rahul):** 27 option positions | Monthly target: $13,101
  - ⚠️ Balance as of 2026-07-31 (39 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $531 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,993
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (39 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (100 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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
- Actual YTD: $231,189.0
- Gap to close: $668,811.0 (74.3%)
- Monthly average (YTD): $25,688
- Monthly average needed: $100,000
- Monthly gap: $6,900

**Position tier distribution → gap closure:**

- Tier 1 (12 positions): $45,600/month (46% of $100,000 target)
- Tier 2 (57 positions): $57,000/month (57% of target)
- Tier 3 (19 positions): $-9,500/month (-10% drag)
- Current total: 88 positions = $93,100/month (93% of target)

**Gap closure path:**

- To hit $100,000 target: Need 2 more Tier 1 positions
- Alternative: Scale existing OR exit 7 worst Tier 3 positions
- Capital required for 2 new positions: $20,000 (2 × $10K)

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

- **Total open positions:** 314
- **Unique tickers:** 88
- **Active accounts:** 10
- **Data currency:** 2026-09-08
- **Live prices:** 87 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (12 positions): $45,600/month — each contributes $3,800/month (4.2% of $100,000)
- Tier 2 (57 positions): $57,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (19 positions): $-9,500/month — each drags -$500/month (-0.6% of target)
- Portfolio: 93,100/month (93% of target) — Need $6,900 more

**HIGH (Tier 1: 8-10) conviction** — 12 positions | Total contribution: $45,600/month (45.6% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $312.22 | 9.1 | $3,800 | 3.8% |
| 🟢 | BROS | $46.54 | 9.0 | $3,800 | 3.8% |
| 🟢 | GEV | $967.77 | 8.4 | $3,800 | 3.8% |
| 🟡 | MU | $1018.02 | 8.4 | $3,800 | 3.8% |
| 🟡 | APH | $83.24 | 8.3 | $3,800 | 3.8% |
| 🟢 | VRT | $288.12 | 8.3 | $3,800 | 3.8% |
| 🟡 | NVDA | $229.50 | 8.3 | $3,800 | 3.8% |
| 🟡 | TSM | $434.38 | 8.2 | $3,800 | 3.8% |
| 🟡 | SKHY | $186.17 | 8.2 | $3,800 | 3.8% |
| 🟢 | AMKR | $49.40 | 8.1 | $3,800 | 3.8% |
| 🟡 | RBLX | $43.92 | 8.0 | $3,800 | 3.8% |
| 🟡 | META | $616.31 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 57 positions | Total contribution: $57,000/month (57.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | LASR | $40.36 | 7.8 | $1,000 | 1.0% |
| 🟢 | UNH | $394.53 | 7.7 | $1,000 | 1.0% |
| 🟡 | BWXT | $160.01 | 7.7 | $1,000 | 1.0% |
| 🟢 | ALAB | $299.32 | 7.6 | $1,000 | 1.0% |
| 🟢 | GOOGL | $333.94 | 7.6 | $1,000 | 1.0% |
| 🟡 | UBER | $73.76 | 7.5 | $1,000 | 1.0% |
| 🟡 | NBIS | $238.49 | 7.5 | $1,000 | 1.0% |
| 🟢 | CRWV | $95.71 | 7.5 | $1,000 | 1.0% |
| 🟢 | SPCX | $147.21 | 7.5 | $1,000 | 1.0% |
| 🟡 | DVN | $48.69 | 7.4 | $1,000 | 1.0% |
| 🟢 | KTOS | $49.76 | 7.4 | $1,000 | 1.0% |
| 🟡 | ANET | $195.47 | 7.2 | $1,000 | 1.0% |
| 🟡 | IBM | $231.16 | 7.2 | $1,000 | 1.0% |
| 🟢 | OKLO | $43.84 | 7.2 | $1,000 | 1.0% |
| 🟢 | AMZN | $256.30 | 7.2 | $1,000 | 1.0% |
| 🟡 | WMT | $106.18 | 7.2 | $1,000 | 1.0% |
| 🟡 | NFLX | $76.32 | 7.0 | $1,000 | 1.0% |
| 🟢 | RIOT | $22.20 | 7.0 | $1,000 | 1.0% |
| 🟢 | RKLB | $65.63 | 7.0 | $1,000 | 1.0% |
| 🟡 | ISRG | $358.55 | 7.0 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 37 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 19 positions | Total contribution: $-9,500/month (-9.5% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | PANW | $328.85 | 5.8 | $-500 | 0.0% |
| 🟡 | SBUX | $103.67 | 5.8 | $-500 | 0.0% |
| 🟡 | CRWD | $207.90 | 5.8 | $-500 | 0.0% |
| 🟢 | ZBH | $96.28 | 5.8 | $-500 | 0.0% |
| 🟡 | AXON | $512.20 | 5.6 | $-500 | 0.0% |
| 🟡 | PFE | $28.03 | 5.4 | $-500 | 0.0% |
| 🟢 | INFY | $11.14 | 5.4 | $-500 | 0.0% |
| 🟡 | ABNB | $180.16 | 5.3 | $-500 | 0.0% |
| 🟢 | BA | $213.45 | 5.3 | $-500 | 0.0% |
| 🟢 | DIS | $104.51 | 5.3 | $-500 | 0.0% |
| 🟢 | BRKB | $0.00 | 5.3 | $-500 | 0.0% |
| 🟡 | SONO | $14.37 | 5.2 | $-500 | 0.0% |
| 🟢 | ETSY | $73.82 | 5.2 | $-500 | 0.0% |
| 🟢 | ADBE | $255.97 | 5.1 | $-500 | 0.0% |
| 🟢 | NVO | $45.73 | 4.8 | $-500 | 0.0% |
| 🟡 | PYPL | $53.71 | 4.2 | $-500 | 0.0% |
| 🟡 | MMYT | $53.59 | 4.2 | $-500 | 0.0% |
| 🟡 | XYZ | $81.29 | 4.1 | $-500 | 0.0% |
| 🟢 | CCJ | $103.80 | 3.5 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 39 positions (44.3%)
- 🟡 YELLOW (Neutral): 46 positions (52.3%)
- 🔴 RED (Extended/Overbought): 3 positions (3.4%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.5 — VIX 15.5 sustained < 20
- **S&P 500:** 7689 (50d MA: 7598, 200d MA: 7147)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 114 | 6.85 | 51.8 | 55.4 | 63 | 🟡 NEUTRAL |
| Healthcare | 15 | 6.22 | 43.2 | 38.7 | 24 | 🟡 NEUTRAL |
| Consumer Cyclical | 29 | 6.0 | 36.7 | 41.1 | 58 | 🟢 BUY (rich premium) |
| Industrials | 37 | 6.82 | 46.0 | 47.1 | 50 | 🟡 NEUTRAL |
| Energy | 4 | 5.45 | 58.3 | 63.6 | 33 | 🟡 NEUTRAL |
| Consumer Defensive | 1 | 7.2 | 33.2 | 20.1 | 97 | 🟢 BUY (rich premium) |
| Utilities | 7 | 7.04 | 64.1 | 16.9 | 31 | 🟡 BUY stock/THIN premium |
| Communication Services | 32 | 7.87 | 61.1 | 23.7 | 57 | 🟢 BUY (rich premium) |
| Defense | 4 | 5.95 | 24.6 | 30.4 | 62 | 🟢 BUY (rich premium) |
| Brand-Quality (Non-AI) | 21 | 6.78 | 48.9 | 44.5 | 36 | 🟡 NEUTRAL |
| Basic Materials | 11 | 6.51 | 46.2 | 34.6 | 27 | 🟡 NEUTRAL |
| Financial Services | 38 | 6.16 | 56.1 | 41.2 | 54 | 🟡 NEUTRAL |
| Unknown | 1 | 5.3 | 50.0 | 50.0 | 0 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Consumer Cyclical:** Conv 6.0/10, RSI 36.7, 52W %ile 41.1 — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling)
- ✓ **Communication Services:** Conv 7.9/10, RSI 61.1, 52W %ile 23.7 — 🟢 BUY — Oversold + rich premium (avg IVR 57, good for selling)
- ✓ **Defense:** Conv 6.0/10, RSI 24.6, 52W %ile 30.4 — 🟢 BUY — Oversold + rich premium (avg IVR 62, good for selling)
- ✓ **Utilities:** Conv 7.0/10, RSI 64.1, 52W %ile 16.9 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 31 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Defensive:** Conv 7.2/10, RSI 33.2, 52W %ile 20.1 — 🟢 BUY — Oversold + rich premium (avg IVR 97, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.8/10, RSI 51.8, 52W %ile 55.4 — 🟡 MONITOR — Neutral positioning
- ◇ **Basic Materials:** Conv 6.5/10, RSI 46.2, 52W %ile 34.6 — 🟡 MONITOR — Neutral positioning
- ◇ **Brand-Quality (Non-AI):** Conv 6.8/10, RSI 48.9, 52W %ile 44.5 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 6.8/10, RSI 46.0, 52W %ile 47.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Unknown:** Conv 5.3/10, RSI 50.0, 52W %ile 50.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.2/10, RSI 56.1, 52W %ile 41.2 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 6.2/10, RSI 43.2, 52W %ile 38.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 5.5/10, RSI 58.3, 52W %ile 63.6 — 🟡 MONITOR — Neutral positioning


## Section 5: POSITION DISTRIBUTION BY ACCOUNT

- **Account A (232):** 161 positions (51.3%) `█████████████████████████`
- **Fidelity (Rahul):** 41 positions (13.1%) `██████`
- **Vanguard (Rahul):** 27 positions (8.6%) `████`
- **Account C (634):** 22 positions (7.0%) `███`
- **Account B (275):** 20 positions (6.4%) `███`
- **Robinhood (Traditional IRA):** 18 positions (5.7%) `██`
- **Fidelity (Rajul — Rollover IRA):** 13 positions (4.1%) `██`
- **Fidelity (Rajul — Roth IRA):** 8 positions (2.5%) `█`
- **Robinhood (Individual):** 4 positions (1.3%) ``
- **Fidelity 401K (Rahul):** 0 positions (0.0%) ``


## Section 6: POSITION HEAT MATRIX BY SECTOR — Sector -> Symbol, Put/Call/Total Value, Heat, Suggestion


### Technology (33 positions, $2,637,786) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $368,296 | $0 | $368,296 | 🟡 | 6.7 | 🟡 MONITOR |
| TSM | $217,189 | $43,438 | $260,627 | 🟡 | 8.2 | 🟡 MONITOR |
| CRM | $74,339 | $173,457 | $247,796 | 🔴 | 6.8 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| ALAB | $209,524 | $29,932 | $239,456 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ADBE | $76,791 | $153,582 | $230,373 | 🟢 | 5.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MU | $203,604 | $0 | $203,604 | 🟡 | 8.4 | 🟡 MONITOR |
| OKTA | $33,464 | $117,124 | $150,588 | 🔴 | 6.4 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| IBM | $92,464 | $23,116 | $115,580 | 🟡 | 7.2 | 🟡 MONITOR |
| MSFT | $49,298 | $49,298 | $98,596 | 🟡 | 7.0 | 🟡 MONITOR |
| TWLO | $22,256 | $66,768 | $89,024 | 🟡 | 6.9 | 🟡 MONITOR |
| NVDA | $68,850 | $0 | $68,850 | 🟡 | 8.3 | 🟡 MONITOR |
| PANW | $65,770 | $0 | $65,770 | 🟡 | 5.8 | 🟡 MONITOR |
| ZS | $32,154 | $32,154 | $64,308 | 🟡 | 6.7 | 🟡 MONITOR |
| SHOP | $54,762 | $0 | $54,762 | 🟢 | 6.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| XYZ | $32,516 | $16,258 | $48,774 | 🟡 | 4.1 | 🟡 MONITOR |
| FSLR | $41,669 | $0 | $41,669 | 🟡 | 6.7 | 🟡 MONITOR |
| CRWD | $41,579 | $0 | $41,579 | 🟡 | 5.8 | 🟡 MONITOR |
| SKHY | $37,234 | $0 | $37,234 | 🟡 | 8.2 | 🟡 MONITOR |
| UBER | $36,880 | $0 | $36,880 | 🟡 | 7.5 | 🟡 MONITOR |
| APH | $24,972 | $8,324 | $33,296 | 🟡 | 8.3 | 🟡 MONITOR |
| IONQ | $21,497 | $8,599 | $30,096 | 🟡 | 6.7 | 🟡 MONITOR |
| AMKR | $24,700 | $0 | $24,700 | 🟢 | 8.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBRK | $18,051 | $0 | $18,051 | 🟡 | 6.7 | 🟡 MONITOR |
| PLTR | $17,204 | $0 | $17,204 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LYFT | $1,628 | $8,138 | $9,766 | 🟡 | 6.5 | 🟡 MONITOR |
| CRWV | $9,571 | $0 | $9,571 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LASR | $8,072 | $0 | $8,072 | 🟢 | 7.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CIFR | $7,156 | $0 | $7,156 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ASTS | $6,517 | $0 | $6,517 | 🟡 | 6.9 | 🟡 MONITOR |
| SONO | $0 | $5,748 | $5,748 | 🟡 | 5.2 | 🟡 MONITOR |
| INFY | $1,114 | $1,114 | $2,227 | 🟢 | 5.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QUBT | $841 | $0 | $841 | 🟡 | 7.0 | 🟡 MONITOR |
| ONDS | $776 | $0 | $776 | 🟡 | 6.4 | 🟡 MONITOR |

### Industrials (9 positions, $1,311,368) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $153,660 | $409,760 | $563,420 | 🟡 | 5.6 | 🟡 MONITOR |
| GEV | $290,330 | $0 | $290,330 | 🟢 | 8.4 | 🟢 ENTER (short put) |
| BE | $192,707 | $55,059 | $247,766 | 🔴 | 6.5 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| VRT | $115,248 | $0 | $115,248 | 🟢 | 8.3 | 🟢 ATTRACTIVE — let run |
| RKLB | $39,378 | $0 | $39,378 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |
| BWXT | $32,002 | $0 | $32,002 | 🟡 | 7.7 | 🟡 MONITOR |
| SPCX | $14,721 | $0 | $14,721 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run |
| KTOS | $4,976 | $0 | $4,976 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| PL | $3,528 | $0 | $3,528 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |

### Communication Services (7 positions, $914,485) — 🟢 BUY — Oversold + rich premium (avg IVR 57, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $246,524 | $61,631 | $308,155 | 🟡 | 8.0 | 🟡 MONITOR |
| APP | $187,330 | $62,443 | $249,773 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $106,848 | $45,792 | $152,640 | 🟡 | 7.0 | 🟡 MONITOR |
| GOOGL | $100,182 | $0 | $100,182 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| NBIS | $47,697 | $0 | $47,697 | 🟡 | 7.5 | 🟡 MONITOR |
| RBLX | $21,960 | $13,176 | $35,136 | 🟡 | 8.0 | 🟡 MONITOR |
| DIS | $20,902 | $0 | $20,902 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Financial Services (7 positions, $664,981) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| COIN | $90,062 | $144,100 | $234,162 | 🟡 | 6.4 | 🟡 MONITOR |
| MA | $172,185 | $0 | $172,185 | 🟡 | 6.9 | 🟡 MONITOR |
| PYPL | $16,113 | $80,565 | $96,678 | 🟡 | 4.2 | 🟡 MONITOR |
| JPM | $71,377 | $0 | $71,377 | 🟡 | 6.2 | 🟡 MONITOR |
| CRCL | $29,355 | $19,570 | $48,925 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| HUT | $28,333 | $0 | $28,333 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| RIOT | $11,100 | $2,220 | $13,320 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |

### Consumer Cyclical (12 positions, $383,744) — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $85,494 | $0 | $85,494 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| AMZN | $51,260 | $25,630 | $76,890 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ABNB | $18,016 | $54,048 | $72,064 | 🟡 | 5.3 | 🟡 MONITOR |
| BABA | $44,980 | $0 | $44,980 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TSLA | $35,860 | $0 | $35,860 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MMYT | $21,436 | $5,359 | $26,795 | 🟡 | 4.2 | 🟡 MONITOR |
| JD | $8,316 | $8,316 | $16,632 | 🟡 | 6.6 | 🟡 MONITOR |
| ETSY | $0 | $7,382 | $7,382 | 🟢 | 5.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CAVA | $5,983 | $0 | $5,983 | 🟡 | 6.9 | 🟡 MONITOR |
| DKNG | $4,682 | $0 | $4,682 | 🟡 | 6.4 | 🟡 MONITOR |
| BROS | $4,654 | $0 | $4,654 | 🟢 | 9.0 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| CCL | $2,328 | $0 | $2,328 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (4 positions, $374,352) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ULTA | $111,090 | $55,545 | $166,635 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| ANET | $97,735 | $58,641 | $156,376 | 🟡 | 7.2 | 🟡 MONITOR |
| NKE | $3,826 | $26,782 | $30,608 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| SBUX | $20,733 | $0 | $20,733 | 🟡 | 5.8 | 🟡 MONITOR |

### Healthcare (5 positions, $348,714) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ISRG | $143,420 | $35,855 | $179,275 | 🟡 | 7.0 | 🟡 MONITOR |
| UNH | $78,906 | $39,453 | $118,359 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| NVO | $22,865 | $4,573 | $27,438 | 🟢 | 4.8 | 🟢 ATTRACTIVE — let run |
| PFE | $14,015 | $0 | $14,015 | 🟡 | 5.4 | 🟡 MONITOR |
| ZBH | $0 | $9,628 | $9,628 | 🟢 | 5.8 | 🟢 ATTRACTIVE — let run |

### Defense (2 positions, $146,480) — 🟢 BUY — Oversold + rich premium (avg IVR 62, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| NOC | $103,790 | $0 | $103,790 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| BA | $42,690 | $0 | $42,690 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

### Basic Materials (2 positions, $111,929) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $76,751 | $12,792 | $89,543 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MP | $16,790 | $5,597 | $22,386 | 🟡 | 6.0 | 🟡 MONITOR |

### Utilities (3 positions, $88,557) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 31 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $45,564 | $0 | $45,564 | 🟡 | 7.0 | 🟡 MONITOR |
| CEG | $29,841 | $0 | $29,841 | 🟡 | 6.7 | 🟡 MONITOR |
| OKLO | $13,152 | $0 | $13,152 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |

### Energy (2 positions, $30,499) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| CCJ | $20,760 | $0 | $20,760 | 🟢 | 3.5 | 🟢 ATTRACTIVE — let run |
| DVN | $9,739 | $0 | $9,739 | 🟡 | 7.4 | 🟡 MONITOR |

### Consumer Defensive (1 positions, $10,618) — 🟢 BUY — Oversold + rich premium (avg IVR 97, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,618 | $0 | $10,618 | 🟡 | 7.2 | 🟡 MONITOR |

### Unknown (1 positions, $0) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| BRKB | $0 | $0 | $0 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 11.7% ($818,397)
- 🟡 MONITOR: 54.1% ($3,801,789)
- 🟢 HEALTHY: 34.2% ($2,403,327)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟡 YELLOW

**Summary:** ⚠️ CAUTION — 1 indicators turning yellow. Watch for deterioration.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| ⚠️ | BREADTH | 53.84615384615385 | YELLOW | 60% (caution), 50% (alert) |
| 🔴 | AD_RATIO | 0.5151515151515151 | RED | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 265 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.41% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟠 30-day crash probability: 40.9% — Action: 🟡 CAUTION: Reduce overbought positions by 20-25%
- 🟠 60-day crash probability: 69.2%
- 🔴 90-day crash probability: 95.0%
- 📌 Primary risk factor: AD_RATIO critical

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▃`
  - 2026-09-01: 48% → 2026-09-08: 41% (falling, -7pp)

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

- ⚠️ Stage 1 Rotation (6-8 week advance warning)
- Close 30% of overbought positions (RSI > 75)
- Reduce naked call exposure by 20%
- Shift new entries to DEFENSIVE sectors
- Keep short puts (they profit on dips)

**Rotation Playbook:**

```
YELLOW FLAG — Stage 1 Rotation (Crash prob: 41% in 30d | 69% in 60d)
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

- **Technology concentration:** 37.6% of notional (114 positions, $2,637,786)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $828,560 live — 74% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $293,923 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $166,173 across NBIS, CRWV, RKLB, OKLO, SPCX, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ✅ Last check: 2026-09-08 (0 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.

Underperformance proxy: no tracked name diverging >10pp from SPX over 7 days.


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | APH | P | 145.0 | 101 | 100% | $14,500 |  |
| Account A (232) | CRM | C | 175.0 | 10 | 100% | $17,500 | 🔴 EXIT CANDIDATE |
| Account A (232) | AXON | C | 450.0 | 10 | 99% | $45,000 |  |
| Account A (232) | COIN | P | 250.0 | 10 | 98% | $25,000 |  |
| Account A (232) | NKE | P | 62.5 | 10 | 97% | $6,250 |  |
| Account C (634) | PL | P | 32.0 | 38 | 95% | $3,200 |  |
| Account A (232) | IBM | P | 270.0 | 38 | 94% | $27,000 |  |
| Account B (275) | CRM | C | 175.0 | 101 | 87% | $17,500 | 🔴 EXIT CANDIDATE |
| Account A (232) | CRM | C | 185.0 | 73 | 85% | $18,500 | 🔴 EXIT CANDIDATE |
| Account A (232) | PYPL | C | 42.5 | 10 | 84% | $8,500 |  |
| Account C (634) | ABNB | C | 145.0 | 38 | 83% | $14,500 |  |
| Account A (232) | AXON | P | 570.0 | 10 | 80% | $57,000 |  |
| Account A (232) | AXON | C | 470.0 | 10 | 80% | $47,000 |  |
| Account A (232) | ADBE | C | 230.0 | 10 | 75% | $23,000 |  |
| Account A (232) | PYPL | C | 42.5 | 73 | 73% | $21,250 |  |
| Account A (232) | XYZ | C | 65.0 | 101 | 73% | $13,000 |  |
| Account A (232) | CRCL | P | 105.0 | 10 | 72% | $10,500 |  |
| Account A (232) | PYPL | C | 45.0 | 73 | 72% | $9,000 |  |
| Account A (232) | NVO | P | 50.0 | 101 | 71% | $5,000 |  |
| Account A (232) | ZS | P | 180.0 | 101 | 71% | $18,000 |  |
| Account A (232) | ALAB | P | 330.0 | 38 | 70% | $33,000 |  |
| Account A (232) | OKTA | C | 140.0 | 73 | 70% | $14,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | PYPL | C | 45.0 | 101 | 69% | $13,500 |  |
| Account A (232) | COIN | P | 190.0 | 10 | 69% | $19,000 |  |
| Account A (232) | CRM | C | 210.0 | 101 | 69% | $21,000 | 🔴 EXIT CANDIDATE |
_...and 66 more within 120 DTE (not shown)_

- **Worst case (all shown):** $2,227,700 across 91 positions
- **Realistic (>=30% prob):** $1,455,200 across 65 positions
- **Likely (>=50% prob):** $882,200 across 43 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 5

- CRM C 175.0 (Account A (232)) — 100% probability, RED heat
- CRM C 175.0 (Account B (275)) — 87% probability, RED heat
- CRM C 185.0 (Account A (232)) — 85% probability, RED heat
- OKTA C 140.0 (Account A (232)) — 70% probability, RED heat
- CRM C 210.0 (Account A (232)) — 69% probability, RED heat


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ✅ Last scan: 2026-09-01 (7 days ago)
- **CRM:** No new low-strike calls this week -- let existing ITM calls execute as planned.
- **MACRO:** No Tier CR trigger this week -- confirmation, not escalation.
- **MU:** Flag for next quarterly bucket review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET candidate) -- not an immediate reclass off one data point.


## Section 7: ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT


**Execution Sequence (do in this order):**

#### 1. Close Now 🔴 (0 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $6,900 to $6,900 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (0 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $0/month contribution from MODERATE conviction positions
- ✅ None — all CRITICAL positions are RED/close candidates

#### 3. Let Run — Nothing Needed 🟢 (39 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 39 healthy positions contribute $39,000/month baseline (expected)
- ✅ 39 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (5 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 5 Tier 1 entries = $19,000/month; closes gap from $6,900 to $-12,100 (19.0% closure)
  - APP: Conv 9.1/10 | RSI 54.0 | Value $249,773 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - BROS: Conv 9.0/10 | RSI 43.9 | Value $4,654 ⚠️ Consumer Cyclical is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 42.3 | Value $290,330
  - VRT: Conv 8.3/10 | RSI 59.0 | Value $115,248
  - AMKR: Conv 8.1/10 | RSI 37.7 | Value $24,700 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 88
- 🔴 Critical actions: 0 closes + 0 monitors
- 🟡 Yellow cautions: 43
- 🟢 Green healthy: 39
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $6,900 (6.9% below target)
- After closes: $6,900 (saves ~0.0%)
- After new Tier 1 entries: $-12,100 (19.0% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-08 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_