# UNIFIED MASTER REPORT — DAILY (314 POSITIONS)

**Type:** DAILY  |  **Regime:** BULL  |  **Generated:** September 08, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $7,028,035
- **Total option requirement:** $2,593,269
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
| Account A (232) | $403,000 | 17.2% | $4,565,444 | $821,780 | Margin | 🔴 OVER CAP | $28,615 | ⚠️ $802 |
| Account B (275) | $261,000 | 11.1% | $364,421 | $291,950 | Cash-Sec | 🔴 COVERAGE GAP | $10,669 | ⚠️ $299 |
| Account C (634) | $266,000 | 11.4% | $335,646 | $214,450 | Cash-Sec | ⚠️ WATCH | $10,874 | ⚠️ $305 |
| Fidelity (Rahul) | $498,560 | 21.3% | $697,284 | $626,290 | Cash-Sec | 🔴 COVERAGE GAP | $20,380 | ⚠️ $571 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $53,091 | $52,133 | Cash-Sec | 🔴 COVERAGE GAP | $1,601 | ⚠️ $45 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $164,923 | $161,150 | Cash-Sec | 🔴 COVERAGE GAP | $5,236 | ⚠️ $147 |
| Vanguard (Rahul) | $320,492 | 13.7% | $512,290 | $425,517 | Cash-Sec | 🔴 COVERAGE GAP | $13,100 | ⚠️ $366 |
| Robinhood (Individual) | $13,000 | 0.6% | $27,746 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $531 | ⚠️ $15 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $307,190 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,993 | ⚠️ $252 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $7,028,035 | $2,593,269 |  |  |  |  |

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
- Monthly gap: $2,800

**Position tier distribution → gap closure:**

- Tier 1 (14 positions): $53,200/month (53% of $100,000 target)
- Tier 2 (54 positions): $54,000/month (54% of target)
- Tier 3 (20 positions): $-10,000/month (-10% drag)
- Current total: 88 positions = $97,200/month (97% of target)

**Gap closure path:**

- To hit $100,000 target: Need 1 more Tier 1 positions
- Alternative: Scale existing OR exit 8 worst Tier 3 positions
- Capital required for 1 new positions: $10,000 (1 × $10K)

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

- Tier 1 (14 positions): $53,200/month — each contributes $3,800/month (4.2% of $100,000)
- Tier 2 (54 positions): $54,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (20 positions): $-10,000/month — each drags -$500/month (-0.6% of target)
- Portfolio: 97,200/month (97% of target) — Need $2,800 more

**HIGH (Tier 1: 8-10) conviction** — 14 positions | Total contribution: $53,200/month (53.2% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | APP | $310.67 | 9.1 | $3,800 | 3.8% |
| 🟢 | BROS | $46.16 | 9.0 | $3,800 | 3.8% |
| 🟡 | DVN | $48.97 | 8.5 | $3,800 | 3.8% |
| 🟢 | GEV | $964.50 | 8.4 | $3,800 | 3.8% |
| 🟡 | MU | $1015.28 | 8.4 | $3,800 | 3.8% |
| 🟡 | APH | $82.75 | 8.3 | $3,800 | 3.8% |
| 🟢 | VRT | $286.98 | 8.3 | $3,800 | 3.8% |
| 🟡 | NVDA | $228.27 | 8.3 | $3,800 | 3.8% |
| 🟡 | TSM | $434.65 | 8.2 | $3,800 | 3.8% |
| 🟡 | SKHY | $186.98 | 8.2 | $3,800 | 3.8% |
| 🟡 | FSLR | $210.56 | 8.2 | $3,800 | 3.8% |
| 🟢 | AMKR | $50.18 | 8.1 | $3,800 | 3.8% |
| 🟡 | RBLX | $43.99 | 8.0 | $3,800 | 3.8% |
| 🟡 | META | $618.25 | 8.0 | $3,800 | 3.8% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 54 positions | Total contribution: $54,000/month (54.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | LASR | $40.50 | 7.8 | $1,000 | 1.0% |
| 🟢 | UNH | $392.30 | 7.7 | $1,000 | 1.0% |
| 🟡 | BWXT | $158.86 | 7.7 | $1,000 | 1.0% |
| 🟢 | ALAB | $301.19 | 7.6 | $1,000 | 1.0% |
| 🟢 | GOOGL | $334.56 | 7.6 | $1,000 | 1.0% |
| 🟡 | UBER | $73.39 | 7.5 | $1,000 | 1.0% |
| 🟡 | NBIS | $238.75 | 7.5 | $1,000 | 1.0% |
| 🟢 | CRWV | $95.99 | 7.5 | $1,000 | 1.0% |
| 🟢 | SPCX | $148.70 | 7.5 | $1,000 | 1.0% |
| 🟢 | KTOS | $48.76 | 7.4 | $1,000 | 1.0% |
| 🟡 | ANET | $197.09 | 7.2 | $1,000 | 1.0% |
| 🟡 | IBM | $231.11 | 7.2 | $1,000 | 1.0% |
| 🟢 | OKLO | $44.00 | 7.2 | $1,000 | 1.0% |
| 🟢 | AMZN | $255.20 | 7.2 | $1,000 | 1.0% |
| 🟡 | WMT | $105.78 | 7.2 | $1,000 | 1.0% |
| 🔴 | BE | $273.19 | 7.1 | $1,000 | 1.0% |
| 🟡 | CRCL | $99.19 | 7.1 | $1,000 | 1.0% |
| 🟡 | NFLX | $76.39 | 7.0 | $1,000 | 1.0% |
| 🟢 | RIOT | $22.34 | 7.0 | $1,000 | 1.0% |
| 🟢 | RKLB | $65.56 | 7.0 | $1,000 | 1.0% |
_(put/call detail: Section 6)_
_...and 34 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 20 positions | Total contribution: $-10,000/month (-10.0% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | ABNB | $178.49 | 5.9 | $-500 | 0.0% |
| 🟡 | PANW | $328.77 | 5.8 | $-500 | 0.0% |
| 🟡 | SBUX | $102.84 | 5.8 | $-500 | 0.0% |
| 🟡 | JPM | $354.82 | 5.8 | $-500 | 0.0% |
| 🟡 | CRWD | $207.59 | 5.8 | $-500 | 0.0% |
| 🟢 | ZBH | $96.74 | 5.8 | $-500 | 0.0% |
| 🟡 | AXON | $510.85 | 5.6 | $-500 | 0.0% |
| 🟡 | PFE | $27.99 | 5.4 | $-500 | 0.0% |
| 🟢 | INFY | $11.18 | 5.4 | $-500 | 0.0% |
| 🟢 | BA | $213.20 | 5.3 | $-500 | 0.0% |
| 🟢 | DIS | $104.36 | 5.3 | $-500 | 0.0% |
| 🟢 | BRKB | $0.00 | 5.3 | $-500 | 0.0% |
| 🟡 | SONO | $14.42 | 5.2 | $-500 | 0.0% |
| 🟡 | ETSY | $72.63 | 5.2 | $-500 | 0.0% |
| 🟢 | ADBE | $256.62 | 5.1 | $-500 | 0.0% |
| 🟢 | NVO | $45.43 | 4.8 | $-500 | 0.0% |
| 🟡 | PYPL | $53.78 | 4.2 | $-500 | 0.0% |
| 🟡 | MMYT | $53.80 | 4.2 | $-500 | 0.0% |
| 🟡 | XYZ | $81.16 | 4.1 | $-500 | 0.0% |
| 🟢 | CCJ | $103.89 | 3.5 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 38 positions (43.2%)
- 🟡 YELLOW (Neutral): 48 positions (54.5%)
- 🔴 RED (Extended/Overbought): 2 positions (2.3%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** BULL
- **Note:** Regime auto-detected from data. No caution flags active.
- **VIX:** 15.7 — VIX 15.7 sustained < 20
- **S&P 500:** 7680 (50d MA: 7598, 200d MA: 7147)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 114 | 6.87 | 51.9 | 55.4 | 63 | 🟡 NEUTRAL |
| Healthcare | 15 | 6.22 | 42.5 | 38.3 | 24 | 🟡 NEUTRAL |
| Consumer Cyclical | 29 | 6.09 | 36.2 | 40.6 | 58 | 🟢 BUY (rich premium) |
| Industrials | 37 | 6.96 | 45.5 | 46.7 | 50 | 🟡 NEUTRAL |
| Energy | 4 | 6.0 | 59.1 | 64.3 | 34 | 🟡 NEUTRAL |
| Consumer Defensive | 1 | 7.2 | 32.8 | 19.0 | 98 | 🟢 BUY (rich premium) |
| Utilities | 7 | 7.04 | 64.7 | 17.7 | 31 | 🟡 BUY stock/THIN premium |
| Communication Services | 32 | 7.87 | 60.8 | 23.8 | 57 | 🟢 BUY (rich premium) |
| Defense | 4 | 5.95 | 24.3 | 30.3 | 62 | 🟢 BUY (rich premium) |
| Brand-Quality (Non-AI) | 21 | 6.78 | 49.3 | 44.7 | 37 | 🟡 NEUTRAL |
| Basic Materials | 11 | 6.51 | 47.4 | 35.6 | 27 | 🟡 NEUTRAL |
| Financial Services | 38 | 6.21 | 56.3 | 41.3 | 54 | 🟡 NEUTRAL |
| Unknown | 1 | 5.3 | 50.0 | 50.0 | 0 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Consumer Cyclical:** Conv 6.1/10, RSI 36.2, 52W %ile 40.6 — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling)
- ✓ **Communication Services:** Conv 7.9/10, RSI 60.8, 52W %ile 23.8 — 🟢 BUY — Oversold + rich premium (avg IVR 57, good for selling)
- ✓ **Defense:** Conv 6.0/10, RSI 24.3, 52W %ile 30.3 — 🟢 BUY — Oversold + rich premium (avg IVR 61, good for selling)
- ✓ **Utilities:** Conv 7.0/10, RSI 64.7, 52W %ile 17.7 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 31 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Defensive:** Conv 7.2/10, RSI 32.8, 52W %ile 19.0 — 🟢 BUY — Oversold + rich premium (avg IVR 98, good for selling)

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 6.9/10, RSI 51.9, 52W %ile 55.4 — 🟡 MONITOR — Neutral positioning
- ◇ **Basic Materials:** Conv 6.5/10, RSI 47.4, 52W %ile 35.6 — 🟡 MONITOR — Neutral positioning
- ◇ **Brand-Quality (Non-AI):** Conv 6.8/10, RSI 49.3, 52W %ile 44.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.0/10, RSI 45.5, 52W %ile 46.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Unknown:** Conv 5.3/10, RSI 50.0, 52W %ile 50.0 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.2/10, RSI 56.3, 52W %ile 41.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 6.2/10, RSI 42.5, 52W %ile 38.3 — 🟡 MONITOR — Neutral positioning
- ◇ **Energy:** Conv 6.0/10, RSI 59.1, 52W %ile 64.3 — 🟡 MONITOR — Neutral positioning


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


### Technology (33 positions, $2,646,331) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| LITE | $377,720 | $0 | $377,720 | 🟡 | 6.7 | 🟡 MONITOR |
| TSM | $217,325 | $43,465 | $260,790 | 🟡 | 8.2 | 🟡 MONITOR |
| CRM | $74,198 | $173,129 | $247,327 | 🟡 | 6.8 | 🟡 MONITOR |
| ALAB | $210,833 | $30,119 | $240,952 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ADBE | $76,988 | $153,975 | $230,962 | 🟢 | 5.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MU | $203,056 | $0 | $203,056 | 🟡 | 8.4 | 🟡 MONITOR |
| OKTA | $33,279 | $116,477 | $149,756 | 🔴 | 6.4 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| IBM | $92,444 | $23,111 | $115,555 | 🟡 | 7.2 | 🟡 MONITOR |
| MSFT | $49,202 | $49,202 | $98,405 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| TWLO | $22,301 | $66,902 | $89,203 | 🟡 | 6.6 | 🟡 MONITOR |
| NVDA | $68,481 | $0 | $68,481 | 🟡 | 8.3 | 🟡 MONITOR |
| PANW | $65,753 | $0 | $65,753 | 🟡 | 5.8 | 🟡 MONITOR |
| ZS | $31,869 | $31,869 | $63,738 | 🟡 | 6.7 | 🟡 MONITOR |
| SHOP | $53,744 | $0 | $53,744 | 🟡 | 6.1 | 🟡 MONITOR |
| XYZ | $32,464 | $16,232 | $48,696 | 🟡 | 4.1 | 🟡 MONITOR |
| FSLR | $42,112 | $0 | $42,112 | 🟡 | 8.2 | 🟡 MONITOR |
| CRWD | $41,518 | $0 | $41,518 | 🟡 | 5.8 | 🟡 MONITOR |
| SKHY | $37,396 | $0 | $37,396 | 🟡 | 8.2 | 🟡 MONITOR |
| UBER | $36,695 | $0 | $36,695 | 🟡 | 7.5 | 🟡 MONITOR |
| APH | $24,825 | $8,275 | $33,100 | 🟡 | 8.3 | 🟡 MONITOR |
| IONQ | $21,284 | $8,514 | $29,798 | 🟡 | 6.7 | 🟡 MONITOR |
| AMKR | $25,090 | $0 | $25,090 | 🟢 | 8.1 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| RBRK | $18,157 | $0 | $18,157 | 🟡 | 6.7 | 🟡 MONITOR |
| PLTR | $17,259 | $0 | $17,259 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LYFT | $1,627 | $8,137 | $9,765 | 🟡 | 6.5 | 🟡 MONITOR |
| CRWV | $9,599 | $0 | $9,599 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| LASR | $8,100 | $0 | $8,100 | 🟢 | 7.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| CIFR | $7,398 | $0 | $7,398 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ASTS | $6,588 | $0 | $6,588 | 🟢 | 6.9 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| SONO | $0 | $5,768 | $5,768 | 🟡 | 5.2 | 🟡 MONITOR |
| INFY | $1,118 | $1,118 | $2,235 | 🟢 | 5.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| QUBT | $838 | $0 | $838 | 🟡 | 7.0 | 🟡 MONITOR |
| ONDS | $778 | $0 | $778 | 🟡 | 6.4 | 🟡 MONITOR |

### Industrials (9 positions, $1,306,351) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| AXON | $153,255 | $408,680 | $561,935 | 🟡 | 5.6 | 🟡 MONITOR |
| GEV | $289,350 | $0 | $289,350 | 🟢 | 8.4 | 🟢 ATTRACTIVE — let run |
| BE | $191,233 | $54,638 | $245,871 | 🔴 | 7.1 | 🟡 WATCH (RED, conv holds it back from CLOSE/TRIM) |
| VRT | $114,792 | $0 | $114,792 | 🟢 | 8.3 | 🟢 ATTRACTIVE — let run |
| RKLB | $39,337 | $0 | $39,337 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |
| BWXT | $31,772 | $0 | $31,772 | 🟡 | 7.7 | 🟡 MONITOR |
| SPCX | $14,870 | $0 | $14,870 | 🟢 | 7.5 | 🟢 ATTRACTIVE — let run |
| KTOS | $4,876 | $0 | $4,876 | 🟢 | 7.4 | 🟢 ATTRACTIVE — let run |
| PL | $3,548 | $0 | $3,548 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |

### Communication Services (7 positions, $914,623) — 🟢 BUY — Oversold + rich premium (avg IVR 57, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| META | $247,300 | $61,825 | $309,125 | 🟡 | 8.0 | 🟡 MONITOR |
| APP | $186,402 | $62,134 | $248,536 | 🟢 | 9.1 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| NFLX | $106,946 | $45,834 | $152,780 | 🟡 | 7.0 | 🟡 MONITOR |
| GOOGL | $100,368 | $0 | $100,368 | 🟢 | 7.6 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| NBIS | $47,750 | $0 | $47,750 | 🟡 | 7.5 | 🟡 MONITOR |
| RBLX | $21,995 | $13,197 | $35,192 | 🟡 | 8.0 | 🟡 MONITOR |
| DIS | $20,872 | $0 | $20,872 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Financial Services (7 positions, $666,221) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| COIN | $90,665 | $145,064 | $235,729 | 🟡 | 6.4 | 🟡 MONITOR |
| MA | $171,470 | $0 | $171,470 | 🟡 | 6.9 | 🟡 MONITOR |
| PYPL | $16,134 | $80,670 | $96,804 | 🟡 | 4.2 | 🟡 MONITOR |
| JPM | $70,963 | $0 | $70,963 | 🟡 | 5.8 | 🟡 MONITOR |
| CRCL | $29,757 | $19,838 | $49,595 | 🟡 | 7.1 | 🟡 MONITOR |
| HUT | $28,255 | $0 | $28,255 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| RIOT | $11,171 | $2,234 | $13,406 | 🟢 | 7.0 | 🟢 ATTRACTIVE — let run |

### Consumer Cyclical (12 positions, $382,358) — 🟢 BUY — Oversold + rich premium (avg IVR 58, good for selling) 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| EXPE | $84,670 | $0 | $84,670 | 🟢 | 6.5 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| AMZN | $51,040 | $25,520 | $76,560 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| ABNB | $17,849 | $53,546 | $71,394 | 🟡 | 5.9 | 🟡 MONITOR |
| BABA | $45,144 | $0 | $45,144 | 🟡 | 6.0 | 🟡 MONITOR |
| TSLA | $36,148 | $0 | $36,148 | 🟢 | 6.7 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MMYT | $21,520 | $5,380 | $26,900 | 🟡 | 4.2 | 🟡 MONITOR |
| JD | $8,328 | $8,328 | $16,656 | 🟡 | 6.6 | 🟡 MONITOR |
| ETSY | $0 | $7,263 | $7,263 | 🟡 | 5.2 | 🟡 MONITOR |
| CAVA | $5,979 | $0 | $5,979 | 🟡 | 6.9 | 🟡 MONITOR |
| DKNG | $4,690 | $0 | $4,690 | 🟡 | 6.4 | 🟡 MONITOR |
| BROS | $4,616 | $0 | $4,616 | 🟢 | 9.0 | 🟢 ENTER (short put) ⚠️ HIGH macro exposure |
| CCL | $2,336 | $0 | $2,336 | 🟢 | 6.4 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Brand-Quality (Non-AI) (4 positions, $373,998) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ULTA | $109,988 | $54,994 | $164,982 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run |
| ANET | $98,545 | $59,127 | $157,672 | 🟡 | 7.2 | 🟡 MONITOR |
| NKE | $3,847 | $26,929 | $30,776 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| SBUX | $20,568 | $0 | $20,568 | 🟡 | 5.8 | 🟡 MONITOR |

### Healthcare (5 positions, $348,342) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ISRG | $143,782 | $35,945 | $179,727 | 🟡 | 7.0 | 🟡 MONITOR |
| UNH | $78,460 | $39,230 | $117,690 | 🟢 | 7.7 | 🟢 ATTRACTIVE — let run |
| NVO | $22,715 | $4,543 | $27,258 | 🟢 | 4.8 | 🟢 ATTRACTIVE — let run |
| PFE | $13,993 | $0 | $13,993 | 🟡 | 5.4 | 🟡 MONITOR |
| ZBH | $0 | $9,674 | $9,674 | 🟢 | 5.8 | 🟢 ATTRACTIVE — let run |

### Defense (2 positions, $146,478) — 🟢 BUY — Oversold + rich premium (avg IVR 61, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| NOC | $103,838 | $0 | $103,838 | 🟢 | 6.6 | 🟢 ATTRACTIVE — let run |
| BA | $42,640 | $0 | $42,640 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

### Basic Materials (2 positions, $112,924) — 🟡 MONITOR — Neutral positioning 🔴 HIGH MACRO EXPOSURE (see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| ALB | $77,328 | $12,888 | $90,216 | 🟢 | 6.8 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |
| MP | $17,031 | $5,677 | $22,708 | 🟢 | 6.0 | 🟢 ATTRACTIVE — let run ⚠️ HIGH macro exposure |

### Utilities (3 positions, $89,259) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 31 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| VST | $45,948 | $0 | $45,948 | 🟡 | 7.0 | 🟡 MONITOR |
| CEG | $30,111 | $0 | $30,111 | 🟡 | 6.7 | 🟡 MONITOR |
| OKLO | $13,200 | $0 | $13,200 | 🟢 | 7.2 | 🟢 ATTRACTIVE — let run |

### Energy (2 positions, $30,572) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| CCJ | $20,779 | $0 | $20,779 | 🟢 | 3.5 | 🟢 ATTRACTIVE — let run |
| DVN | $9,793 | $0 | $9,793 | 🟡 | 8.5 | 🟡 MONITOR |

### Consumer Defensive (1 positions, $10,578) — 🟢 BUY — Oversold + rich premium (avg IVR 98, good for selling)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| WMT | $10,578 | $0 | $10,578 | 🟡 | 7.2 | 🟡 MONITOR |

### Unknown (1 positions, $0) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Suggestion |
|---|---|---|---|---|---|---|
| BRKB | $0 | $0 | $0 | 🟢 | 5.3 | 🟢 ATTRACTIVE — let run |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 8.1% ($568,027)
- 🟡 MONITOR: 58.2% ($4,087,119)
- 🟢 HEALTHY: 33.8% ($2,372,890)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟡 YELLOW

**Summary:** ⚠️ CAUTION — 1 indicators turning yellow. Watch for deterioration.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| ⚠️ | BREADTH | 53.84615384615385 | YELLOW | 60% (caution), 50% (alert) |
| 🔴 | AD_RATIO | 0.42857142857142855 | RED | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 265 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.41% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

**Crash Probability Forecast (Probabilistic):**

- 🟠 30-day crash probability: 44.2% — Action: 🟡 CAUTION: Reduce overbought positions by 20-25%
- 🔴 60-day crash probability: 74.6%
- 🔴 90-day crash probability: 95.0%
- 📌 Primary risk factor: AD_RATIO critical

- **90-day trend** (30-day crash probability, one reading per day with data): `▄▄▄`
  - 2026-09-01: 48% → 2026-09-08: 44% (flat, -4pp)

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
YELLOW FLAG — Stage 1 Rotation (Crash prob: 44% in 30d | 75% in 60d)
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

- **Technology concentration:** 37.7% of notional (114 positions, $2,646,331)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $838,987 live — 74% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $293,890 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $166,417 across NBIS, CRWV, RKLB, OKLO, SPCX, HUT, RIOT

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
| Account A (232) | NKE | P | 62.5 | 10 | 100% | $6,250 |  |
| Account A (232) | CRM | C | 175.0 | 10 | 96% | $17,500 |  |
| Account C (634) | PL | P | 32.0 | 38 | 95% | $3,200 |  |
| Account A (232) | COIN | P | 250.0 | 10 | 94% | $25,000 |  |
| Account A (232) | AXON | P | 570.0 | 10 | 90% | $57,000 |  |
| Account A (232) | IBM | P | 270.0 | 38 | 90% | $27,000 |  |
| Account A (232) | CRM | C | 185.0 | 73 | 87% | $18,500 |  |
| Account A (232) | PYPL | C | 42.5 | 10 | 86% | $8,500 |  |
| Account A (232) | AXON | C | 450.0 | 10 | 86% | $45,000 |  |
| Account B (275) | CRM | C | 175.0 | 101 | 85% | $17,500 |  |
| Account A (232) | ADBE | C | 230.0 | 10 | 82% | $23,000 |  |
| Account C (634) | ABNB | C | 145.0 | 38 | 81% | $14,500 |  |
| Account A (232) | AXON | C | 470.0 | 10 | 77% | $47,000 |  |
| Account A (232) | PYPL | C | 42.5 | 73 | 77% | $21,250 |  |
| Account A (232) | NVO | P | 50.0 | 101 | 74% | $5,000 |  |
| Account A (232) | PYPL | C | 45.0 | 73 | 74% | $9,000 |  |
| Account A (232) | ZS | P | 180.0 | 101 | 72% | $18,000 |  |
| Account A (232) | XYZ | C | 65.0 | 101 | 72% | $13,000 |  |
| Account A (232) | CRCL | C | 85.0 | 38 | 72% | $8,500 |  |
| Account A (232) | PYPL | C | 45.0 | 101 | 71% | $13,500 |  |
| Account A (232) | ALAB | P | 330.0 | 38 | 68% | $33,000 |  |
| Account A (232) | OKTA | C | 140.0 | 73 | 68% | $14,000 | 🔴 EXIT CANDIDATE |
| Account A (232) | COIN | P | 190.0 | 10 | 67% | $19,000 |  |
| Account A (232) | CRM | C | 210.0 | 101 | 67% | $21,000 |  |
_...and 66 more within 120 DTE (not shown)_

- **Worst case (all shown):** $2,227,700 across 91 positions
- **Realistic (>=30% prob):** $1,455,200 across 65 positions
- **Likely (>=50% prob):** $891,200 across 44 positions

**🔴 Exit Candidates** (>=50% probability AND RED heat — both signals agree): 1

- OKTA C 140.0 (Account A (232)) — 68% probability, RED heat


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
- Gap Impact: Closing 0 RED positions saves ~$0/month drag; moves gap from $2,800 to $2,800 (0.0% improvement)
- ✅ None needed — no RED + high conviction conflicts

#### 2. Monitor for Rolls 🟡 (0 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $0/month contribution from MODERATE conviction positions
- ✅ None — all CRITICAL positions are RED/close candidates

#### 3. Let Run — Nothing Needed 🟢 (38 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 38 healthy positions contribute $38,000/month baseline (expected)
- ✅ 38 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (5 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 5 Tier 1 entries = $19,000/month; closes gap from $2,800 to $-16,200 (19.0% closure)
  - APP: Conv 9.1/10 | RSI 52.3 | Value $248,536 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - BROS: Conv 9.0/10 | RSI 42.7 | Value $4,616 ⚠️ Consumer Cyclical is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 41.0 | Value $289,350
  - VRT: Conv 8.3/10 | RSI 58.5 | Value $114,792
  - AMKR: Conv 8.1/10 | RSI 39.7 | Value $25,090 ⚠️ Technology is HIGH-exposure to today's primary risk driver — adding here compounds it

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 88
- 🔴 Critical actions: 0 closes + 0 monitors
- 🟡 Yellow cautions: 45
- 🟢 Green healthy: 38
- 📊 Market regime: BULL

**Gap Closure Summary:**

- Current gap: $2,800 (2.8% below target)
- After closes: $2,800 (saves ~0.0%)
- After new Tier 1 entries: $-16,200 (19.0% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-08 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_