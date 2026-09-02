# Unified Master Report — Monthly Stage

**September 02, 2026** — 8:00 AM ET | September 2026 Performance & October Outlook

- **System Boot:** Monthly recalibration & moat strength update
- **Report Type:** MONTHLY STRATEGIC REVIEW
- **Data Window:** September 1-01, 2026 (current month)

## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $6,910,127
- **Total option requirement:** $2,591,778
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
| Account A (232) | $403,000 | 17.2% | $4,533,403 | $816,013 | Margin | 🔴 OVER CAP | $25,753 | ⚠️ $4,407 |
| Account B (275) | $261,000 | 11.1% | $351,496 | $291,950 | Cash-Sec | 🔴 COVERAGE GAP | $9,602 | ⚠️ $1,643 |
| Account C (634) | $266,000 | 11.4% | $327,441 | $214,450 | Cash-Sec | ⚠️ WATCH | $9,786 | ⚠️ $1,674 |
| Fidelity (Rahul) | $498,560 | 21.3% | $661,962 | $627,800 | Cash-Sec | 🔴 COVERAGE GAP | $18,342 | ⚠️ $3,139 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $52,371 | $51,682 | Cash-Sec | 🔴 COVERAGE GAP | $1,440 | ⚠️ $246 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $170,855 | $161,150 | Cash-Sec | 🔴 COVERAGE GAP | $4,712 | ⚠️ $806 |
| Vanguard (Rahul) | $320,492 | 13.7% | $493,955 | $428,733 | Cash-Sec | 🔴 COVERAGE GAP | $11,790 | ⚠️ $2,017 |
| Robinhood (Individual) | $13,000 | 0.6% | $23,759 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $477 | ⚠️ $81 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $294,885 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,093 | ⚠️ $1,385 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $6,910,127 | $2,591,778 |  |  |  |  |

- **Account A (232):** 161 option positions | Monthly target: $28,615 | Equity: ADBE 400sh, APP 100sh, AXON 100sh, COIN 100sh, CRM 300sh +13 more
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 OVER CAP reading above
- **Account B (275):** 20 option positions | Monthly target: $10,669 | Equity: CRM 100sh, NVO 100sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the 🔴 COVERAGE GAP reading above
- **Account C (634):** 22 option positions | Monthly target: $10,874 | Equity: ABNB 100sh, NKE 100sh, TWLO 324sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ⚠️ WATCH reading above
- **Fidelity (Rahul):** 41 option positions | Monthly target: $20,380 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
  - ⚠️ Balance as of 2026-07-31 (33 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,601 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
  - ⚠️ Balance as of 2026-07-31 (33 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Fidelity (Rajul — Rollover IRA):** 13 option positions | Monthly target: $5,236
  - ⚠️ Balance as of 2026-07-31 (33 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Vanguard (Rahul):** 27 option positions | Monthly target: $13,101
  - ⚠️ Balance as of 2026-07-31 (33 days ago) — re-confirm if the 🔴 COVERAGE GAP reading above matters for a decision
- **Robinhood (Individual):** 4 option positions | Monthly target: $531 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 18 option positions | Monthly target: $8,993
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-07-31 (33 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (94 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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
- Actual YTD: $231,189.0
- Gap to close: $578,811.0 (71.5%)
- Monthly average (YTD): $25,688
- Monthly average needed: $90,000
- Monthly gap: $15,400

**Position tier distribution → gap closure:**

- Tier 1 (7 positions): $26,600/month (30% of $90,000 target)
- Tier 2 (59 positions): $59,000/month (66% of target)
- Tier 3 (22 positions): $-11,000/month (-12% drag)
- Current total: 88 positions = $74,600/month (83% of target)

**Gap closure path:**

- To hit $90,000 target: Need 5 more Tier 1 positions
- Alternative: Scale existing OR exit 8 worst Tier 3 positions
- Capital required for 5 new positions: $50,000 (5 × $10K)

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


## Section 1: MONTHLY ACTUAL VS TARGET — COMPLETE VARIANCE ANALYSIS

See Section 0's PERFORMANCE VS TARGET block for YTD actual/target/gap and this month's pace vs. the regime-adjusted target — not repeated here.

**Rest-of-Year Projection** (using the same regime-adjusted target as Section 0):

- Remaining months: 3 (as of September)
- Remaining target (est): $270,000 (3 × $90,000)
- Pace required to recover: $90,000/month (regime-adjusted)
- This month so far (MTD, live): $-11


## Section 2: MONTHLY PERFORMANCE BY ACCOUNT (ALL 11)

| Account | Balance | % Portfolio | Target (mo) | Actual (MTD) | Actual (YTD) | Variance (MTD) | Open Positions | Status |
|---|---|---|---|---|---|---|---|---|
| Account A (232) | $403,000 | 17.2% | $28,615 | $27,916 | $111,568 | $-699 (-2.4%) | 161 | ✅ ON TARGET |
| Account B (275) | $261,000 | 11.1% | $10,669 | $385 | $24,410 | $-10,284 (-96.4%) | 20 | ⚠️ BELOW |
| Account C (634) | $266,000 | 11.4% | $10,874 | $4,523 | $15,938 | $-6,351 (-58.4%) | 22 | ⚠️ BELOW |
| Fidelity (Rahul) | $498,560 | 21.3% | $20,380 | $2,859 | $32,238 | $-17,521 (-86.0%) | 41 | ⚠️ BELOW |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $1,601 | $136 | $2,774 | $-1,465 (-91.5%) | 8 | ⚠️ BELOW |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $5,236 | $3,045 | $5,588 | $-2,191 (-41.8%) | 13 | ⚠️ BELOW |
| Vanguard (Rahul) | $320,492 | 13.7% | $13,101 | $0 | $0 | $-13,101 (-100.0%) | 27 | ⚠️ BELOW |
| Robinhood (Individual) | $13,000 | 0.6% | $531 | $0 | $302 | $-531 (-100.0%) | 4 | ⚠️ BELOW |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $8,993 | $4,718 | $17,809 | $-4,275 (-47.5%) | 18 | ⚠️ BELOW |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |

No option-level realized data for: Vanguard (Rahul), Fidelity 401K (Rahul) — see `realized_pnl.py`'s module docstring for why (e.g. Vanguard's option-side data is untracked).


## Section 3: MONTHLY PREMIUM vs TARGET (real)

Monthly net target (base): $100,000 | YTD actual: $231,189

| Month | Actual | Target | Variance |
|---|---|---|---|
| 2026-01 | 10,334 | 100,000 | -89,666 |
| 2026-02 | 19,188 | 100,000 | -80,812 |
| 2026-03 | 27,842 | 100,000 | -72,158 |
| 2026-04 | 39,588 | 100,000 | -60,412 |
| 2026-05 | 20,931 | 100,000 | -79,069 |
| 2026-06 | 15,092 | 100,000 | -84,908 |
| 2026-07 | 28,891 | 100,000 | -71,109 |
| 2026-08 | 69,334 | 100,000 | -30,666 |
| 2026-09 | -11 | 100,000 | -100,011 |

Per-driver attribution (regime / thesis / timing / slippage) requires trade-level tagging that is not captured yet — omitted rather than estimated.


## Section 4: MOAT RECALIBRATION & TIER ASSIGNMENTS

**Tier 1 — Strong Moat** (Conviction ≥7, 30+ day history, positive P&L)

| Symbol | Conv | Heat | Price | Value | RSI | 52W Range | Verdict |
|---|---|---|---|---|---|---|---|
| APP | 9.1 | GREEN | $311.74 | $249,392 | 45.1 | 3% | STRONG (Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning) |
| BROS | 9.0 | GREEN | $46.31 | $4,631 | 40.6 | 6% | STRONG (Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning) |
| MU | 8.8 | YELLOW | $933.44 | $186,688 | 53.1 | 72% | STRONG (Approaching extremes) |
| META | 8.5 | YELLOW | $578.54 | $289,270 | 49.9 | 22% | STRONG (Approaching extremes) |
| SKHY | 8.5 | GREEN | $160.78 | $32,156 | 54.8 | 51% | STRONG (Neutral positioning) |

Tier 1 summary: 5 positions, quality improving

**Tier 2 — Moderate Moat** (Conviction 5-7)

- RBLX: 7.8/10 (GREEN) | Value $32,536 — Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning
- UNH: 7.7/10 (GREEN) | Value $118,890 — Neutral positioning
- ALAB: 7.6/10 (GREEN) | Value $223,928 — Neutral positioning

**Tier 3 & Exited:**

- RIOT: 5.9/10 (GREEN) — Watch for exit
- ZS: 5.9/10 (YELLOW) — Watch for exit

**Moat verdict:** Quality improving with framework. Tier 1 concentration rising.


## Section 5: PERFORMANCE PACE (real)

- YTD net premium (real): $231,189 (Jan–Sep)
- Average monthly pace: $25,688/month
- Annualized run-rate: $308,252
- Monthly net target (base): $100,000

Note: The prior Citadel/peer comparison used fabricated P&L figures and has been removed. Benchmark against external estimates manually if you want that view.

---
_Report generated: 2026-09-02 | Next Monthly Report: Thursday, October 01, 2026 8:00 AM ET_