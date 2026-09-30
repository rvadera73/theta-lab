# UNIFIED MASTER REPORT — DAILY (320 POSITIONS)

**Type:** DAILY  |  **Regime:** CAUTIOUS_BULL  |  **Generated:** September 28, 2026 — 12:00 AM ET


## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,415,485
- **Total notional exposure:** $8,107,705
- **Total option requirement:** $2,778,947
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
| Account A (232) | $403,000 | 16.7% | $5,665,889 | $1,019,860 | Margin | 🔴 OVER CAP | $29,776 | ✅ $-5,261 |
| Account B (275) | $261,000 | 10.8% | $370,955 | $294,050 | Cash-Sec | 🔴 COVERAGE GAP | $8,635 | ✅ $-1,526 |
| Account C (634) | $256,067 | 10.6% | $345,485 | $211,950 | Cash-Sec | ⚠️ WATCH | $8,471 | ✅ $-1,497 |
| Fidelity (Rahul) | $563,432 | 23.3% | $709,794 | $623,577 | Cash-Sec | 🔴 COVERAGE GAP | $18,640 | ✅ $-3,294 |
| Fidelity (Rajul — Roth IRA) | $44,942 | 1.9% | $53,891 | $53,511 | Cash-Sec | 🔴 COVERAGE GAP | $1,486 | ✅ $-263 |
| Fidelity (Rajul — Rollover IRA) | $141,349 | 5.9% | $179,558 | $163,200 | Cash-Sec | 🔴 COVERAGE GAP | $4,676 | ✅ $-826 |
| Vanguard (Rahul) | $320,492 | 13.3% | $438,794 | $412,799 | Cash-Sec | 🔴 COVERAGE GAP | $10,603 | ✅ $-1,874 |
| Robinhood (Individual) | $13,000 | 0.5% | $28,258 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $430 | ✅ $-76 |
| Robinhood (Traditional IRA) | $220,000 | 9.1% | $315,081 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $7,278 | ✅ $-1,286 |
| Fidelity 401K (Rahul) | $192,200 | 8.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,415,485 | 100.0% | $8,107,705 | $2,778,947 |  |  |  |  |

- **Account A (232):** 171 option positions | Monthly target: $33,085 | Equity: ADBE 300sh, APP 100sh, AXON 200sh, COIN 200sh, CRCL 100sh +15 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 21 option positions | Monthly target: $9,595 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 21 option positions | Monthly target: $9,413 | Equity: ABNB 100sh, NKE 100sh, PL 100sh, TWLO 324sh
- **Fidelity (Rahul):** 42 option positions | Monthly target: $20,712 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,652 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
- **Fidelity (Rajul — Rollover IRA):** 10 option positions | Monthly target: $5,196
- **Vanguard (Rahul):** 25 option positions | Monthly target: $11,782
  - ⚠️ Balance as of 2026-07-31 (59 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $478 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,087
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (59 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (120 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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
- Actual YTD: $321,035.0
- Gap to close: $488,965.0 (60.4%)
- Monthly average (YTD): $35,671
- Monthly average needed: $90,000
- Monthly gap: $-15,900

**Position tier distribution → gap closure:**

- Tier 1 (13 positions): $49,400/month (55% of $90,000 target)
- Tier 2 (64 positions): $64,000/month (71% of target)
- Tier 3 (15 positions): $-7,500/month (-8% drag)
- Current total: 92 positions = $105,900/month (118% of target)

**Gap closure path:**

- To hit $90,000 target: Need 0 more Tier 1 positions
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
- Regime: CAUTIOUS_BULL (applies 90% of base)
- Adjusted Target: $225,000 gross / $90,000 net

**Account Targets (Regime-Adjusted)** — complements Section 0's Per-Account
Breakdown 'Target' column: that one is the raw monthly_target; these are the
same targets scaled by the current regime's adjustment factor, gross+net.

| Account | Gross | Net |
|---|---|---|
| Account A (232) | $74,440 | $29,776 |
| Account B (275) | $21,587 | $8,635 |
| Account C (634) | $21,177 | $8,471 |
| Fidelity (Rahul) | $46,600 | $18,640 |
| Fidelity (Rajul — Roth IRA) | $3,715 | $1,486 |
| Fidelity (Rajul — Rollover IRA) | $11,690 | $4,676 |
| Vanguard (Rahul) | $26,507 | $10,603 |
| Robinhood (Individual) | $1,075 | $430 |
| Robinhood (Traditional IRA) | $18,195 | $7,278 |
| **TOTAL** | $224,986 | $89,995 |


## Section 1: SYSTEM STATUS & PORTFOLIO SNAPSHOT

- **Total open positions:** 320
- **Unique tickers:** 92
- **Active accounts:** 10
- **Data currency:** 2026-09-28
- **Live prices:** 92 tickers fetched from Yahoo Finance


## Section 2: CONVICTION UPDATES (Yahoo Finance Derived) + FRAMEWORK CONTRIBUTION

**Tier contribution to target:**

- Tier 1 (13 positions): $49,400/month — each contributes $3,800/month (4.2% of $90,000)
- Tier 2 (64 positions): $64,000/month — each contributes $1,000/month (1.1% of target)
- Tier 3 (15 positions): $-7,500/month — each drags -$500/month (-0.6% of target)
- Portfolio: 105,900/month (118% of target) — Need $-15,900 more

**HIGH (Tier 1: 8-10) conviction** — 13 positions | Total contribution: $49,400/month (54.9% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | JD | $26.51 | 9.3 | $3,800 | 4.2% |
| 🟢 | APP | $310.75 | 9.1 | $3,800 | 4.2% |
| 🟢 | GOOGL | $343.92 | 8.8 | $3,800 | 4.2% |
| 🟡 | MU | $1082.28 | 8.8 | $3,800 | 4.2% |
| 🟡 | NVDA | $225.07 | 8.8 | $3,800 | 4.2% |
| 🟡 | CAVA | $51.58 | 8.8 | $3,800 | 4.2% |
| 🟡 | LASR | $40.33 | 8.5 | $3,800 | 4.2% |
| 🟢 | NKE | $35.75 | 8.4 | $3,800 | 4.2% |
| 🟢 | GEV | $957.63 | 8.4 | $3,800 | 4.2% |
| 🟢 | KTOS | $45.62 | 8.2 | $3,800 | 4.2% |
| 🟡 | PL | $17.43 | 8.2 | $3,800 | 4.2% |
| 🟢 | SHOP | $142.25 | 8.0 | $3,800 | 4.2% |
| 🟢 | VRT | $253.28 | 8.0 | $3,800 | 4.2% |
_(put/call detail: Section 6)_

**MODERATE (Tier 2: 6-8) conviction** — 64 positions | Total contribution: $64,000/month (71.1% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟡 | RBLX | $46.44 | 7.9 | $1,000 | 1.1% |
| 🟡 | LITE | $941.65 | 7.8 | $1,000 | 1.1% |
| 🟡 | ASTS | $61.81 | 7.8 | $1,000 | 1.1% |
| 🟢 | BROS | $37.89 | 7.8 | $1,000 | 1.1% |
| 🟢 | HUT | $96.82 | 7.8 | $1,000 | 1.1% |
| 🟡 | TSM | $450.61 | 7.7 | $1,000 | 1.1% |
| 🟡 | AMKR | $53.61 | 7.7 | $1,000 | 1.1% |
| 🔴 | HOOD | $119.40 | 7.6 | $1,000 | 1.1% |
| 🟡 | SKHY | $191.56 | 7.6 | $1,000 | 1.1% |
| 🟡 | ANET | $206.55 | 7.5 | $1,000 | 1.1% |
| 🟡 | IONQ | $45.48 | 7.5 | $1,000 | 1.1% |
| 🟡 | UBER | $69.62 | 7.5 | $1,000 | 1.1% |
| 🟢 | OKLO | $38.04 | 7.5 | $1,000 | 1.1% |
| 🟡 | LLY | $1183.46 | 7.5 | $1,000 | 1.1% |
| 🟡 | CRWV | $87.59 | 7.5 | $1,000 | 1.1% |
| 🟡 | NBIS | $237.33 | 7.5 | $1,000 | 1.1% |
| 🟡 | QUBT | $8.96 | 7.5 | $1,000 | 1.1% |
| 🟡 | RIOT | $23.00 | 7.4 | $1,000 | 1.1% |
| 🟡 | LYFT | $14.86 | 7.3 | $1,000 | 1.1% |
| 🔴 | ALAB | $364.62 | 7.3 | $1,000 | 1.1% |
_(put/call detail: Section 6)_
_...and 44 more (see Section 6 for the full sector-grouped list)_

**LOW (Tier 3: <6) conviction** — 15 positions | Total contribution: $-7,500/month (-8.3% of target)

| Heat | Symbol | Price | Conv | Contribution | % Target |
|---|---|---|---|---|---|
| 🟢 | VST | $138.46 | 5.9 | $-500 | 0.0% |
| 🟢 | CRCL | $89.00 | 5.8 | $-500 | 0.0% |
| 🟢 | ETSY | $68.44 | 5.8 | $-500 | 0.0% |
| 🟡 | BA | $198.07 | 5.7 | $-500 | 0.0% |
| 🟢 | PYPL | $55.04 | 5.6 | $-500 | 0.0% |
| 🟢 | MMYT | $46.75 | 5.6 | $-500 | 0.0% |
| 🔴 | SONO | $18.18 | 5.4 | $-500 | 0.0% |
| 🟢 | SMR | $8.42 | 5.3 | $-500 | 0.0% |
| 🟢 | DIS | $106.15 | 5.3 | $-500 | 0.0% |
| 🟡 | REGN | $788.04 | 5.2 | $-500 | 0.0% |
| 🔴 | PFE | $28.67 | 4.9 | $-500 | 0.0% |
| 🟢 | NVO | $38.80 | 4.7 | $-500 | 0.0% |
| 🟡 | XYZ | $76.42 | 4.5 | $-500 | 0.0% |
| 🟢 | CCJ | $88.07 | 4.5 | $-500 | 0.0% |
| 🟢 | TTD | $12.60 | 4.3 | $-500 | 0.0% |
_(put/call detail: Section 6)_


## Section 3: POSITION HEAT DISTRIBUTION

- 🟢 GREEN (Attractive/Oversold): 35 positions (38.0%)
- 🟡 YELLOW (Neutral): 48 positions (52.2%)
- 🔴 RED (Extended/Overbought): 9 positions (9.8%)


## Section 4: MARKET REGIME & SIGNALS

- **Current Regime:** CAUTIOUS_BULL
- **Note:** CAUTIOUS_BULL: technical signals green but — VIX 16.0 ≥ 16 (elevated, not complacent). New entries allowed, Tier 1-2 only, tighter strikes.
- **VIX:** 16.0 — VIX 16.0 sustained < 20
- **S&P 500:** 7743 (50d MA: 7636, 200d MA: 7205)
  - Above 50d MA: True | Above 200d MA: True

## Section 4.5: Sector Analysis & Rotation Framework

### Sector Snapshot — Conviction & Valuation Positioning

| Sector | Positions | Avg Conv | Avg RSI | 52W %ile | Avg IVR | Signal |
|---|---|---|---|---|---|---|
| Technology | 108 | 7.02 | 50.5 | 57.9 | 40 | 🟡 NEUTRAL |
| Healthcare | 22 | 6.15 | 44.1 | 48.4 | 16 | 🟡 NEUTRAL |
| Consumer Cyclical | 33 | 6.9 | 31.7 | 32.3 | 29 | 🟡 BUY stock/THIN premium |
| Industrials | 35 | 7.06 | 44.8 | 37.9 | 26 | 🟡 NEUTRAL |
| Energy | 2 | 5.9 | 36.0 | 45.7 | 32 | 🟡 BUY stock/THIN premium |
| Consumer Defensive | 1 | 6.8 | 52.9 | 25.1 | 99 | 🟡 NEUTRAL |
| Utilities | 10 | 6.58 | 33.6 | 7.4 | 15 | 🟡 BUY stock/THIN premium |
| Communication Services | 37 | 7.66 | 49.4 | 27.4 | 31 | 🟡 BUY stock/THIN premium |
| Defense | 9 | 6.37 | 41.7 | 23.5 | 30 | 🟡 BUY stock/THIN premium |
| Brand-Quality (Non-AI) | 13 | 7.42 | 29.6 | 21.3 | 17 | 🟡 BUY stock/THIN premium |
| Crypto Mining | 7 | 7.26 | 53.4 | 53.1 | 37 | 🟡 NEUTRAL |
| Basic Materials | 12 | 7.13 | 33.3 | 20.2 | 25 | 🟡 BUY stock/THIN premium |
| Financial Services | 31 | 6.42 | 45.9 | 41.7 | 54 | 🟡 NEUTRAL |

Per-symbol drill-down (put/call/total value, heat, suggestion, grouped by
sector) is in Section 6 — not repeated here to avoid two versions of the
same per-ticker/per-sector data going out of sync with each other.

### Sector Rotation Framework

**Priority 1: Buy Signals** (Attractive pricing + conviction)

- ✓ **Basic Materials:** Conv 7.1/10, RSI 33.3, 52W %ile 20.2 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 25 < 40) — not attractive for CSPs/CCs
- ✓ **Consumer Cyclical:** Conv 6.9/10, RSI 31.7, 52W %ile 32.3 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 29 < 40) — not attractive for CSPs/CCs
- ✓ **Communication Services:** Conv 7.7/10, RSI 49.4, 52W %ile 27.4 — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 31 < 40)
- ✓ **Defense:** Conv 6.4/10, RSI 41.7, 52W %ile 23.5 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 30 < 40) — not attractive for CSPs/CCs
- ✓ **Brand-Quality (Non-AI):** Conv 7.4/10, RSI 29.6, 52W %ile 21.3 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 17 < 40) — not attractive for CSPs/CCs
- ✓ **Utilities:** Conv 6.6/10, RSI 33.6, 52W %ile 7.4 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 15 < 40) — not attractive for CSPs/CCs
- ✓ **Energy:** Conv 5.9/10, RSI 36.0, 52W %ile 45.7 — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 32 < 40) — not attractive for CSPs/CCs

**Priority 2: Hold Signals** (Conviction intact but extended)

- (None currently)

**Priority 3: Reduce Signals** (Extended positioning or low conviction)

- (None currently)

**Priority 4: Monitor Signals** (Neutral or low conviction)

- ◇ **Technology:** Conv 7.0/10, RSI 50.5, 52W %ile 57.9 — 🟡 MONITOR — Neutral positioning
- ◇ **Industrials:** Conv 7.1/10, RSI 44.8, 52W %ile 37.9 — 🟡 MONITOR — Neutral positioning
- ◇ **Financial Services:** Conv 6.4/10, RSI 45.9, 52W %ile 41.7 — 🟡 MONITOR — Neutral positioning
- ◇ **Healthcare:** Conv 6.2/10, RSI 44.1, 52W %ile 48.4 — 🟡 MONITOR — Neutral positioning
- ◇ **Consumer Defensive:** Conv 6.8/10, RSI 52.9, 52W %ile 25.1 — 🟡 MONITOR — Neutral positioning
- ◇ **Crypto Mining:** Conv 7.3/10, RSI 53.4, 52W %ile 53.1 — 🟡 MONITOR — Neutral positioning


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
| APP | ENTER | Communication Services | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| GOOGL | ENTER | Communication Services | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PFE | CLOSE | Healthcare | 🔴 CLOSE PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +1%. No qualitative flag on file. |
| SONO | TRIM | Technology | 🔴 TRIM CALL | RSI/heat: Spiked 17% in 7 days AND 19% above its 200-day average — genuinely extended, not just a pop. Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Technology (31 positions, $2,852,495) — 🟡 MONITOR — Neutral positioning 🟡 possible macro exposure (weak historical signal, see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LITE | $282,495 | $94,165 | $376,660 | 🟡 | 7.8 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| MU | $216,456 | $108,228 | $324,684 | 🟡 | 8.8 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Spiked 17% in 7 days, 64% above its 200-day average, but analyst upside still +41% — may be fundamentally supported, watch rather than force a close. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): Confirms and strengthens the 2026-09-01 flag: HBM4 capacity now sold out through 2027, likely through 2028; $100B+ in logged orders; CEO says demand exceeds capacity by ~50%. Stock now $935-986 range, +~200% YTD, $1.1T market cap. Q4 earnings 2026-09-30 (11 days out) is a real near-term catalyst/ris |
| CRM | $93,608 | $140,412 | $234,020 | 🟡 | 6.5 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 5 covered call(s) (500 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): 2026-09-01 finding (Salesforce/Anthropic "Claudeforce" partnership) not re-checked this pass -- carried forward, no new SA headline this cycle contradicting it. |
| ALAB | $182,310 | $36,462 | $218,772 | 🔴 | 7.3 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: Spiked 35% in 7 days AND 54% above its 200-day average — genuinely extended, not just a pop. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ADBE | $70,641 | $117,735 | $188,376 | 🟡 | 6.1 | 🟡 WATCH: strangle (2C/3P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 3 covered call(s) (300 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TSM | $135,183 | $45,061 | $180,244 | 🟡 | 7.7 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ANET | $103,275 | $61,965 | $165,240 | 🟡 | 7.5 | 🟡 WATCH: strangle (3C/5P) — call side uncapped if it rallies | RSI/heat: Technically extended (+32% vs 200-day average), but analyst upside still +17% — may be fundamentally supported, watch rather than force a close. Two-sided position: 0 covered call(s) (0 sh owned), 3 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| OKTA | $39,038 | $117,114 | $156,152 | 🟡 | 6.4 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Calls: 6 covered (600 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| MSFT | $103,234 | $51,617 | $154,851 | 🟡 | 6.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TWLO | $27,580 | $82,740 | $110,320 | 🔴 | 6.5 | 🟡 WATCH: RED heat, but conviction 6.5 holds it back from CLOSE/TRIM | RSI/heat: Spiked 15% in 7 days AND 60% above its 200-day average — genuinely extended, not just a pop. Calls: 3 covered (300 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CRWD | $75,639 | $25,213 | $100,852 | 🔴 | 6.0 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -7%. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| IBM | $67,653 | $22,551 | $90,204 | 🟡 | 6.0 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ZS | $57,915 | $19,305 | $77,220 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PANW | $74,948 | $0 | $74,948 | 🔴 | 6.2 | 🟡 WATCH: RED heat, but conviction 6.2 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +6%. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| NVDA | $67,521 | $0 | $67,521 | 🟡 | 8.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SHOP | $56,900 | $0 | $56,900 | 🟢 | 8.0 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| XYZ | $30,568 | $15,284 | $45,852 | 🟡 | 4.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| UBER | $41,772 | $0 | $41,772 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| FSLR | $35,542 | $0 | $35,542 | 🟢 | 6.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| IONQ | $18,192 | $9,096 | $27,288 | 🟡 | 7.5 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: Spiked 23% in 7 days but only +4% vs its 200-day average — short-term move, not structurally extended. Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| AMKR | $21,444 | $0 | $21,444 | 🟡 | 7.7 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Spiked 16% in 7 days but only -6% vs its 200-day average — short-term move, not structurally extended. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SKHY | $19,156 | $0 | $19,156 | 🟡 | 7.6 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| PLTR | $18,967 | $0 | $18,967 | 🟡 | 7.3 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ASTS | $18,543 | $0 | $18,543 | 🟡 | 7.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| RBRK | $10,955 | $0 | $10,955 | 🔴 | 6.7 | 🟡 WATCH: RED heat, but conviction 6.7 holds it back from CLOSE/TRIM | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +10%. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| LYFT | $1,486 | $7,432 | $8,919 | 🟡 | 7.3 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Calls: 5 covered (500 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CRWV | $8,759 | $0 | $8,759 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| LASR | $8,066 | $0 | $8,066 | 🟡 | 8.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| SONO | $0 | $7,272 | $7,272 | 🔴 | 5.4 | 🔴 TRIM CALL | RSI/heat: Spiked 17% in 7 days AND 19% above its 200-day average — genuinely extended, not just a pop. Calls: 4 covered (400 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| INFY | $1,050 | $1,050 | $2,100 | 🟢 | 6.3 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| QUBT | $896 | $0 | $896 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Spiked 12% in 7 days but only -3% vs its 200-day average — short-term move, not structurally extended. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Industrials (9 positions, $1,175,851) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| AXON | $86,022 | $344,088 | $430,110 | 🟡 | 7.2 | 🟡 WATCH: strangle (6C/2P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 2 covered call(s) (200 sh owned), 6 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| GEV | $287,289 | $95,763 | $383,052 | 🟢 | 8.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BE | $144,350 | $57,740 | $202,090 | 🟡 | 6.0 | 🟡 WATCH: strangle (2C/4P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| VRT | $50,656 | $25,328 | $75,984 | 🟢 | 8.0 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| RKLB | $44,370 | $0 | $44,370 | 🟡 | 6.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Spiked 16% in 7 days but only -9% vs its 200-day average — short-term move, not structurally extended. No qualitative flag on file. |
| BWXT | $27,694 | $0 | $27,694 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. No qualitative flag on file. |
| KTOS | $9,124 | $0 | $9,124 | 🟢 | 8.2 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. No qualitative flag on file. |
| PL | $1,743 | $0 | $1,743 | 🟡 | 8.2 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. No qualitative flag on file. |
| SMR | $1,684 | $0 | $1,684 | 🟢 | 5.3 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. No qualitative flag on file. |

### Communication Services (8 positions, $1,065,313) — 🟡 BUY (stock only) — High conviction but THIN premium (avg IVR 31 < 40) 🟡 possible macro exposure (weak historical signal, see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| META | $300,664 | $75,166 | $375,830 | 🔴 | 7.2 | 🟡 WATCH: strangle (1C/4P) — call side uncapped if it rallies | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +5%. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| APP | $217,525 | $93,225 | $310,750 | 🟢 | 9.1 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Two-sided position: 1 covered call(s) (100 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| NFLX | $113,840 | $42,690 | $156,530 | 🟡 | 6.7 | 🟡 WATCH: strangle (6C/16P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 6 naked call(s) (uncapped upside if it rallies), AND 16 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): Wells Fargo downgraded NFLX to Underweight from Equal Weight, cut PT to $57 from $80 (2026-09-18), citing engagement decline (viewing hours -8% adjusted for password-sharing crackdown/geo mix) and a weak content slate (base case -21% YoY hours from top-100 originals). Stock on a 4th straight session |
| GOOGL | $103,176 | $34,392 | $137,568 | 🟢 | 8.8 | 🟢 ENTER: sell put, 45-60 DTE, delta 0.15-0.20 | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| RBLX | $23,220 | $13,932 | $37,152 | 🟡 | 7.9 | 🟡 WATCH: strangle (1C/5P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 5 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| NBIS | $23,733 | $0 | $23,733 | 🟡 | 7.5 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Spiked 13% in 7 days, 45% above its 200-day average, but analyst upside still +19% — may be fundamentally supported, watch rather than force a close. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| DIS | $21,230 | $0 | $21,230 | 🟢 | 5.3 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TTD | $2,520 | $0 | $2,520 | 🟢 | 4.3 | 🟢 HOLD — let run | RSI/heat: Dropped -13% in 7 days AND -46% below its 200-day average — genuinely beaten down. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Healthcare (7 positions, $999,523) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LLY | $355,038 | $118,346 | $473,384 | 🟡 | 7.5 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| ISRG | $121,554 | $40,518 | $162,072 | 🟡 | 7.3 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| REGN | $78,804 | $78,804 | $157,608 | 🟡 | 5.2 | 🟡 WATCH: strangle (1C/1P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| UNH | $75,318 | $75,318 | $150,636 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NVO | $15,520 | $7,760 | $23,280 | 🟢 | 4.7 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Calls: 2 covered (200 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| ZBH | $9,104 | $9,104 | $18,208 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| PFE | $14,335 | $0 | $14,335 | 🔴 | 4.9 | 🔴 CLOSE PUT | RSI/heat: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only +1%. No qualitative flag on file. |

### Financial Services (7 positions, $696,898) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| MA | $227,060 | $0 | $227,060 | 🟡 | 6.9 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. No qualitative flag on file. |
| COIN | $39,022 | $175,599 | $214,621 | 🟡 | 6.6 | 🟡 WATCH: strangle (7C/1P) — call side uncapped if it rallies | RSI/heat: Spiked 19% in 7 days but only +4% vs its 200-day average — short-term move, not structurally extended. Two-sided position: 2 covered call(s) (200 sh owned), 7 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| JPM | $68,612 | $34,306 | $102,918 | 🟡 | 6.4 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| PYPL | $16,512 | $66,048 | $82,560 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 11 covered call(s) (1100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CRCL | $26,700 | $17,800 | $44,500 | 🟢 | 5.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| HOOD | $23,880 | $0 | $23,880 | 🔴 | 7.6 | 🟡 WATCH: RED heat, but conviction 7.6 holds it back from CLOSE/TRIM | RSI/heat: Spiked 14% in 7 days AND 26% above its 200-day average — genuinely extended, not just a pop. No qualitative flag on file. |
| NU | $1,359 | $0 | $1,359 | 🟡 | 7.3 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI/range reads oversold, but -8% vs its 200-day average — verify before treating as attractive. No qualitative flag on file. |

### Consumer Cyclical (12 positions, $452,064) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 29 < 40) — not attractive for CSPs/CCs 🟡 possible macro exposure (weak historical signal, see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| EXPE | $105,668 | $26,417 | $132,085 | 🟢 | 6.5 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 4 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| AMZN | $49,934 | $24,967 | $74,901 | 🟢 | 7.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| TSLA | $74,422 | $0 | $74,422 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| BABA | $54,870 | $0 | $54,870 | 🟡 | 7.2 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ABNB | $15,747 | $31,494 | $47,241 | 🟡 | 7.2 | 🟡 WATCH: strangle (1C/1P) — call side uncapped if it rallies | RSI/heat: RSI/range reads oversold, but +10% vs its 200-day average — verify before treating as attractive. Two-sided position: 1 covered call(s) (100 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 1 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| MMYT | $18,700 | $4,675 | $23,375 | 🟢 | 5.6 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| JD | $7,953 | $7,953 | $15,906 | 🟡 | 9.3 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 2 covered call(s) (200 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| ETSY | $6,844 | $6,844 | $13,688 | 🟢 | 5.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Calls: 1 covered (100 sh owned), 0 naked. No offsetting put position on this name. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CAVA | $5,158 | $0 | $5,158 | 🟡 | 8.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| DKNG | $4,404 | $0 | $4,404 | 🟢 | 6.0 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| BROS | $3,789 | $0 | $3,789 | 🟢 | 7.8 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |
| CCL | $2,225 | $0 | $2,225 | 🟢 | 7.2 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Defense (3 positions, $368,445) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 30 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| LMT | $155,868 | $0 | $155,868 | 🟢 | 6.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. No qualitative flag on file. |
| NOC | $102,104 | $51,052 | $153,156 | 🟡 | 6.6 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| BA | $39,614 | $19,807 | $59,421 | 🟡 | 5.7 | 🟡 WATCH: strangle (1C/2P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |

### Brand-Quality (Non-AI) (4 positions, $217,508) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 17 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ULTA | $109,040 | $54,520 | $163,560 | 🟢 | 6.4 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 2 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| NKE | $0 | $25,025 | $25,025 | 🟢 | 8.4 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Calls: 7 covered (700 sh owned), 0 naked. No offsetting put position on this name. No qualitative flag on file. |
| SBUX | $18,972 | $0 | $18,972 | 🟡 | 6.1 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI/range reads oversold, but -3% vs its 200-day average — verify before treating as attractive. No qualitative flag on file. |
| ELF | $9,951 | $0 | $9,951 | 🟢 | 6.2 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. No qualitative flag on file. |

### Utilities (3 positions, $123,254) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 15 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| VST | $41,538 | $13,846 | $55,384 | 🟢 | 5.9 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. No qualitative flag on file. |
| CEG | $52,654 | $0 | $52,654 | 🟡 | 6.1 | 🟡 WATCH: no confirmed direction yet | RSI/heat: RSI/range reads oversold, but -9% vs its 200-day average — verify before treating as attractive. No qualitative flag on file. |
| OKLO | $15,216 | $0 | $15,216 | 🟢 | 7.5 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. No qualitative flag on file. |

### Basic Materials (2 positions, $107,316) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 25 < 40) — not attractive for CSPs/CCs 🟡 possible macro exposure (weak historical signal, see Section 6.5)

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| ALB | $65,838 | $21,946 | $87,784 | 🟡 | 7.2 | 🟡 WATCH: strangle (2C/6P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 2 naked call(s) (uncapped upside if it rallies), AND 6 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). Qualitative flag (2026-09-18): JPMorgan cut its lithium price forecast and PT to $140 (Dec 2027, down from $160/Dec 2026), Neutral maintained -- short-term commodity pricing pressure (China lithium carbonate ~$21,625/mt Q3 vs ~$24,810 Q2), not a structural downgrade. Q2 revenue +31.1% YoY, EPS beat. Stock fell -3.51% on 2026-09-1 |
| MP | $14,649 | $4,883 | $19,532 | 🟡 | 7.0 | 🟡 WATCH: strangle (1C/3P) — call side uncapped if it rallies | RSI/heat: Approaching extremes. Two-sided position: 0 covered call(s) (0 sh owned), 1 naked call(s) (uncapped upside if it rallies), AND 3 short put(s) (assignment risk if it drops) -- a strangle by design, not an isolated naked call. Possible macro exposure (breadth, weak historical signal). No qualitative flag on file. |

### Crypto Mining (3 positions, $24,728) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| RIOT | $9,200 | $2,300 | $11,500 | 🟡 | 7.4 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Spiked 13% in 7 days, 20% above its 200-day average, but analyst upside still +40% — may be fundamentally supported, watch rather than force a close. No qualitative flag on file. |
| HUT | $9,682 | $0 | $9,682 | 🟢 | 7.8 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. No qualitative flag on file. |
| CIFR | $3,546 | $0 | $3,546 | 🟢 | 6.7 | 🟢 HOLD — let run | RSI/heat: Neutral positioning. No qualitative flag on file. |

### Energy (2 positions, $13,512) — 🟡 BUY (stock only) — Oversold but THIN premium (avg IVR 32 < 40) — not attractive for CSPs/CCs

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| CCJ | $8,807 | $0 | $8,807 | 🟢 | 4.5 | 🟢 HOLD — let run | RSI/heat: Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning. No qualitative flag on file. |
| DVN | $4,705 | $0 | $4,705 | 🟡 | 7.3 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. No qualitative flag on file. |

### Consumer Defensive (1 positions, $10,798) — 🟡 MONITOR — Neutral positioning

| Symbol | Put Value | Call Value | Total Value | Heat | Conv | Action | Detail |
|---|---|---|---|---|---|---|---|
| WMT | $10,798 | $0 | $10,798 | 🟡 | 6.8 | 🟡 WATCH: no confirmed direction yet | RSI/heat: Approaching extremes. No qualitative flag on file. |

**Portfolio Heat Allocation:**

- 🔴 CRITICAL: 12.1% ($983,016)
- 🟡 MONITOR: 60.3% ($4,888,209)
- 🟢 HEALTHY: 27.6% ($2,236,480)


## Section 6.5: CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS


**Risk Level:** 🟢 GREEN

**Summary:** ✅ BULL regime stable. All indicators healthy. Proceed with normal sizing.

**Indicator Status:**

|  | Indicator | Value | Status | Threshold |
|---|---|---|---|---|
| ⚠️ | BREADTH | 53.84615384615385 | YELLOW | 60% (caution), 50% (alert) |
| ✅ | AD_RATIO | 1.7777777777777777 | GREEN | 1.0 (caution), 0.8 (alert) |
| ✅ | VIX_TERM | CONTANGO | GREEN | Contango (normal) → Flat (caution) → Backwardation (alert) |
| ✅ | HYOAS | 280 bps | GREEN | 400 (caution), 450 (alert) |
| ✅ | PCR | 0.75 | GREEN | 1.0 (caution), 1.2 (alert) |
| ✅ | YIELD_CURVE | 0.36% | GREEN | Inverted (alert), <0.1% (caution), >0.5% (normal) |

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

- **Technology concentration:** 35.2% of notional (108 positions, $2,852,495)
  - Reference: top-10 S&P 500 concentration is 41.2%, a record — this line tracks your own book against that same structural risk, not just the index's.

**90-day capital plan tracking** (target 30% high-risk / 70% quality, $700K base):

- High-risk (ALAB/LITE/MU/PLTR): $939,083 live — 84% of tracked pair vs. 30% target
- Quality-AI (TSM/ASML/APH): $180,244 live
- ⚠️ Drift >10pp from the 30/70 target — check whether a tier fired to justify it before rebalancing.
- ⚠️ Avoid-list exposure still open: $113,260 across NBIS, CRWV, RKLB, OKLO, HUT, RIOT

Qualitative Tier 1/2 check (credit news, IPO status, private-credit gating) is NOT computed here — run /ai-capex-risk-review for the live dial state. This section tracks only the scriptable half.

#### Tier CR — Portfolio-Wide Credit Exit Gate

- ⚠️ Last check: 2026-09-08 (20 days ago)
- Gate fired: No
- Last outcome: Still no NEW rating-agency action beyond the already-known Oracle Jul 9 S&P downgrade (BBB to BBB-) -- but the credit-market stress that downgrade started has kept widening: Oracle's 5yr CDS is now ~215bps, up from ~145bps at year-end and from the ~185bps range in the last check. Nvidia's own CDS also touched a new high this period (largest single-day jump since the contract started trading Nov 2025), and CoreWeave's CDS-implied 5yr default probability remains near 50% (~855bps, unchanged from last check -- not new deterioration, still elevated). Nebius (NBIS) and CoreWeave (CRWV) both saw sharp single-day equity drops this period attributed explicitly to credit-swap-cost news (not fundamentals) per financial press. IMPORTANT DIVERGENCE caught by the scriptable underperformance proxy re-run today: despite this credit stress, NBIS/CRWV/ORCL/HUT/RIOT are all still UP 7d and 30d (NBIS +9.3%/+29.7%, CRWV +11.0%/+9.2%, ORCL +8.4%/+9.0%) -- equity hasn't cracked yet even though credit is flashing. The names actually showing weakness are the mega-cap spenders (MSFT -2.7%/-2.7%, GOOGL -1.9%/-6.5%, AMZN +0.1%/-7.8%, AVGO -1.3%/-13.2%), which lines up with JPMorgan technical strategist Jason Hunter's Sept 2026 note flagging a dot-com-echo pattern in the SAME divergence direction: the four biggest AI spenders (MSFT/AMZN/META/GOOGL, ~$725B combined 2026 capex, +77% YoY) underperforming while risk-appetite chases the infrastructure/ neocloud names credit markets are actually most worried about. BofA's own August fund-manager survey shows AI-bubble-as-top-tail-risk concern actually COOLING month over month (45% July -> 32% August), and "long semis" as the most crowded trade fell 82% -> 53% -- survey sentiment is de-risking faster than the public commentary volume suggests. Gate still NOT fired (no confirmed rating action on a tracked name), but this is a real, live escalation worth flagging: THIS SESSION'S OWN quantitative macro model independently moved GREEN (13% 30d crash prob, checked 2026-09-02) -> YELLOW (44.5% 30d, checked today) over the same window, driven by AD_RATIO (0.43, RED/critical) and breadth (51.3%, YELLOW) -- i.e. narrow market leadership, the same structural concern behind the credit/commentary story, arrived at independently from price-breadth data rather than the news cycle.
- ⚠️ Over 14 days since the last real rating-action check — run /ai-capex-risk-review.

Underperformance proxy: no tracked name diverging >10pp from SPX over 7 days.


## Section 6.6: ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE)


| Account | Ticker | T | Strike | DTE | Prob | Cash-at-Risk | Flag |
|---|---|---|---|---|---|---|---|
| Account A (232) | ADBE | P | 260.0 | 18 | 100% | $26,000 |  |
| Account A (232) | ADBE | C | 230.0 | 81 | 100% | $23,000 |  |
| Account A (232) | ADBE | P | 250.0 | 81 | 100% | $25,000 |  |
| Account A (232) | ALB | P | 110.0 | 81 | 100% | $11,000 |  |
| Account A (232) | AMZN | P | 250.0 | 81 | 100% | $25,000 |  |
| Account A (232) | ANET | C | 200.0 | 109 | 100% | $20,000 |  |
| Account A (232) | AXON | P | 540.0 | 81 | 100% | $54,000 |  |
| Account A (232) | AXON | P | 560.0 | 81 | 100% | $56,000 |  |
| Account A (232) | COIN | C | 170.0 | 18 | 100% | $17,000 |  |
| Account A (232) | COIN | C | 180.0 | 81 | 100% | $18,000 |  |
| Account A (232) | CRCL | C | 85.0 | 18 | 100% | $8,500 |  |
| Account A (232) | CRCL | P | 90.0 | 53 | 100% | $9,000 |  |
| Account A (232) | CRM | C | 185.0 | 53 | 100% | $18,500 |  |
| Account A (232) | CRM | C | 210.0 | 81 | 100% | $21,000 |  |
| Account A (232) | DIS | P | 110.0 | 81 | 100% | $22,000 |  |
| Account A (232) | ETSY | C | 60.0 | 81 | 100% | $6,000 |  |
| Account A (232) | ETSY | P | 75.0 | 81 | 100% | $7,500 |  |
| Account A (232) | META | C | 650.0 | 81 | 100% | $65,000 | 🔄 STRANGLE LEG — roll to rebalance, don't close in isolation |
| Account A (232) | MP | P | 60.0 | 81 | 100% | $6,000 |  |
| Account A (232) | NFLX | P | 75.0 | 109 | 100% | $22,500 |  |
| Account A (232) | NFLX | P | 77.5 | 53 | 100% | $15,500 |  |
| Account A (232) | NFLX | P | 80.0 | 53 | 100% | $24,000 |  |
| Account A (232) | NVO | P | 50.0 | 81 | 100% | $5,000 |  |
| Account A (232) | OKTA | C | 140.0 | 53 | 100% | $14,000 |  |
| Account A (232) | PYPL | C | 47.5 | 109 | 100% | $9,500 |  |
_...and 83 more within 120 DTE (not shown)_

- **Worst case (all shown):** $3,469,000 across 108 positions
- **Realistic (>=30% prob):** $744,000 across 42 positions
- **Likely (>=50% prob):** $744,000 across 42 positions

No positions currently combine >=50% probability with RED heat on a truly naked (non-strangle) call, or an at-risk put.

**🔄 Strangle legs at >=50%/RED** (roll to rebalance, not exit candidates): 1

- META C 650.0 (Account A (232)) — 100% probability, RED heat


## Section 6.7: QUARTERLY PLAN STATUS


- ✅ Plan as of: 2026-08-30
- Exit discipline: calls close at 50% premium captured, puts at 70%
- Macro override: Primary de-risk gate for this 90-day window is the Phase-1 trigger firing (see the Circular Financing Playbook / Tier CR framework in .claude/skills/ai-capex-risk-review.md), NOT proactive margin-driven trimming.
- September target: margin equity >= 35, cash-to-trade >= 50000 by 2026-09-30
- Latest reading (2026-09-01): margin equity 37%, cash-to-trade $67,600, option req $746,000
- Standing rules this window: 5 in effect (see the plan file for full text)


## Section 6.8: SEEKING ALPHA WEEKLY THEMES


- ✅ Last scan: 2026-09-18 (10 days ago)
- **NFLX:** CONCRETE WEEKLY ACTION: Account A holds 2 ITM cash-secured NFLX puts right now -- $77.50P x2 (Nov 20) and $80P x3 (Nov 20), both already ITM at $72 spot, both already flagged separately as low-premium (<$500/contract) in this week's Account A cleanup pass. This new catalyst adds real downside conviction on top of an already-poor risk/reward. Recommend reviewing both for an early close/roll before assignment risk grows further, rather than waiting for expiry. The 2 naked NFLX calls ($80C x3 Nov 20, $85C x3 Jan 15) are UNAFFECTED negatively -- a decline moves them further OTM, reducing their risk.

- **MU:** Flag for next quarterly bucket review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET) -- conviction on the reclass is now stronger than 2026-09-01, not an immediate action. Note the 09-30 earnings date if sizing any near-dated MU options this cycle.

- **AVGO:** No Tier CR trigger -- no rating-agency action, structure is clearer but not worse than already tracked in the Circular Financing Playbook. Confirmation with real mechanical detail, not escalation -- worth folding the SPV structure detail into that document's Tier CR section at its next full review.

- **ALB:** No action -- existing ITM $120P (Feb 19) already reflects the known downside; JPMorgan's own long-term target ($140) still implies recovery above current spot. Fundamentals (revenue/EPS) intact.

- **CRM:** Carried forward from 2026-09-01 -- no update this cycle.
- Open items:
  - NFLX: review the 2 ITM Nov-20 cash-secured puts ($77.50P x2, $80P x3, Account A) for an early close/roll given the Wells Fargo downgrade -- new this cycle.
  - MU: reclass conviction strengthened for next quarterly bucket review -- not urgent.


## Section 6.9: ACTIVE DECISION TRACKER


**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 113.31778001403809
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

#### 1. Close Now 🔴 (1 positions)

- Why: Extended/overbought + structural risk. Act before deterioration.
- Gap Impact: Closing 1 RED positions saves ~$500/month drag; moves gap from $-15,900 to $-16,400 (-0.6% improvement)
- Names: PFE (full detail — put/call value, sector, suggestion — in Section 6)

#### 2. Monitor for Rolls 🟡 (1 positions at risk)

- Why: Approaching strike or extremes. Roll if thesis intact, close if thesis broken.
- Gap Impact: Preserve existing $1,000/month contribution from MODERATE conviction positions
- Names: SONO (full detail in Section 6)

#### 3. Let Run — Nothing Needed 🟢 (35 positions)

- Why: Attractive pricing (oversold) + adequate conviction. No action required.
- Gap Impact: 35 healthy positions contribute $35,000/month baseline (expected)
- ✅ 35 positions: Continue monitoring weekly

#### 4. Opportunity — High Conviction Entries 🟢 (7 names)

- Why: Conviction ≥8.0 + oversold/attractive. Consider adding on dips.
- Gap Impact: Adding 7 Tier 1 entries = $26,600/month; closes gap from $-15,900 to $-42,500 (29.6% closure)
  - APP: Conv 9.1/10 | RSI 45.6 | Value $310,750 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GOOGL: Conv 8.8/10 | RSI 54.0 | Value $137,568 ⚠️ Communication Services is HIGH-exposure to today's primary risk driver — adding here compounds it
  - GEV: Conv 8.4/10 | RSI 52.8 | Value $383,052
  - NKE: Conv 8.4/10 | RSI 27.4 | Value $25,025
  - KTOS: Conv 8.2/10 | RSI 38.3 | Value $9,124

**Portfolio Status & Gap Trajectory:**

- ✅ Total positions scanned: 92
- 🔴 Critical actions: 1 closes + 1 monitors
- 🟡 Yellow cautions: 47
- 🟢 Green healthy: 35
- 📊 Market regime: CAUTIOUS_BULL

**Gap Closure Summary:**

- Current gap: $-15,900 (-17.7% below target)
- After closes: $-16,400 (saves ~-0.6%)
- After new Tier 1 entries: $-42,500 (29.6% to gap closure)
- Path to target: Execute closes → add HIGH conviction Tier 1 → scale over 2-3 weeks

---
_Report generated: 2026-09-28 | Data source: OpenPositionsLoaderV2 + Yahoo Finance + Technical Analysis_