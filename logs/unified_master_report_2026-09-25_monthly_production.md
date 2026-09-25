# Unified Master Report — Monthly Stage

**September 25, 2026** — 8:00 AM ET | September 2026 Performance & October Outlook

- **System Boot:** Monthly recalibration & moat strength update
- **Report Type:** MONTHLY STRATEGIC REVIEW
- **Data Window:** September 1-01, 2026 (current month)

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


## Section 1: MONTHLY ACTUAL VS TARGET — COMPLETE VARIANCE ANALYSIS

See Section 0's PERFORMANCE VS TARGET block for YTD actual/target/gap and this month's pace vs. the regime-adjusted target — not repeated here.

**Rest-of-Year Projection** (using the same regime-adjusted target as Section 0):

- Remaining months: 3 (as of September)
- Remaining target (est): $300,000 (3 × $100,000)
- Pace required to recover: $100,000/month (regime-adjusted)
- This month so far (MTD, live): $79,950


## Section 2: MONTHLY PERFORMANCE BY ACCOUNT (ALL 11)

| Account | Balance | % Portfolio | Target (mo) | Actual (MTD) | Actual (YTD) | Variance (MTD) | Open Positions | Status |
|---|---|---|---|---|---|---|---|---|
| Account A (232) | $403,000 | 16.7% | $33,085 | $27,916 | $111,568 | $-5,169 (-15.6%) | 171 | ⚠️ BELOW |
| Account B (275) | $261,000 | 10.8% | $9,595 | $385 | $24,410 | $-9,210 (-96.0%) | 21 | ⚠️ BELOW |
| Account C (634) | $256,067 | 10.6% | $9,413 | $4,523 | $15,938 | $-4,890 (-51.9%) | 21 | ⚠️ BELOW |
| Fidelity (Rahul) | $563,432 | 23.3% | $20,712 | $2,859 | $32,238 | $-17,853 (-86.2%) | 42 | ⚠️ BELOW |
| Fidelity (Rajul — Roth IRA) | $44,942 | 1.9% | $1,652 | $136 | $2,774 | $-1,516 (-91.8%) | 8 | ⚠️ BELOW |
| Fidelity (Rajul — Rollover IRA) | $141,349 | 5.9% | $5,196 | $3,045 | $5,588 | $-2,151 (-41.4%) | 10 | ⚠️ BELOW |
| Vanguard (Rahul) | $320,492 | 13.3% | $11,782 | $0 | $0 | $-11,782 (-100.0%) | 25 | ⚠️ BELOW |
| Robinhood (Individual) | $13,000 | 0.5% | $478 | $0 | $302 | $-478 (-100.0%) | 4 | ⚠️ BELOW |
| Robinhood (Traditional IRA) | $220,000 | 9.1% | $8,087 | $4,718 | $17,809 | $-3,369 (-41.7%) | 18 | ⚠️ BELOW |
| Fidelity 401K (Rahul) | $192,200 | 8.0% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |

No option-level realized data for: Vanguard (Rahul), Fidelity 401K (Rahul) — see `realized_pnl.py`'s module docstring for why (e.g. Vanguard's option-side data is untracked).


## Section 3: MONTHLY PREMIUM vs TARGET (real)

Monthly net target (base): $100,000 | YTD actual: $321,035

| Month | Actual | Target | Variance |
|---|---|---|---|
| 2026-01 | 10,334 | 100,000 | -89,666 |
| 2026-02 | 19,188 | 100,000 | -80,812 |
| 2026-03 | 27,842 | 100,000 | -72,158 |
| 2026-04 | 40,627 | 100,000 | -59,373 |
| 2026-05 | 22,052 | 100,000 | -77,948 |
| 2026-06 | 16,120 | 100,000 | -83,880 |
| 2026-07 | 30,884 | 100,000 | -69,116 |
| 2026-08 | 74,038 | 100,000 | -25,962 |
| 2026-09 | 79,950 | 100,000 | -20,050 |

Per-driver attribution (regime / thesis / timing / slippage) requires trade-level tagging that is not captured yet — omitted rather than estimated.


## Section 4: MOAT RECALIBRATION & TIER ASSIGNMENTS

**Tier 1 — Strong Moat** (Conviction ≥7, 30+ day history, positive P&L)

| Symbol | Conv | Heat | Price | Value | RSI | 52W Range | Verdict |
|---|---|---|---|---|---|---|---|
| APP | 9.1 | GREEN | $312.47 | $312,470 | 49.5 | 3% | STRONG (Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning) |
| GOOGL | 8.8 | GREEN | $342.36 | $136,944 | 50.1 | 62% | STRONG (Neutral positioning) |
| NVDA | 8.8 | YELLOW | $224.58 | $67,374 | 45.8 | 84% | STRONG (Approaching extremes) |
| CAVA | 8.8 | YELLOW | $53.51 | $5,351 | 29.0 | 18% | STRONG (Approaching extremes) |
| KTOS | 8.5 | GREEN | $47.02 | $9,404 | 43.5 | 4% | STRONG (Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning) |

Tier 1 summary: 5 positions, quality improving

**Tier 2 — Moderate Moat** (Conviction 5-7)

- LLY: 7.9/10 (YELLOW) | Value $472,756 — Approaching extremes
- LITE: 7.8/10 (YELLOW) | Value $371,616 — Approaching extremes
- ASTS: 7.8/10 (YELLOW) | Value $18,318 — Approaching extremes

**Tier 3 & Exited:**

- CRCL: 5.8/10 (GREEN) — Watch for exit
- TWLO: 5.8/10 (RED) — Watch for exit

**Moat verdict:** Quality improving with framework. Tier 1 concentration rising.


## Section 5: PERFORMANCE PACE (real)

- YTD net premium (real): $321,035 (Jan–Sep)
- Average monthly pace: $35,671/month
- Annualized run-rate: $428,047
- Monthly net target (base): $100,000

Note: The prior Citadel/peer comparison used fabricated P&L figures and has been removed. Benchmark against external estimates manually if you want that view.


## Section 6: ACTIVE DECISION TRACKER


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



---
_Report generated: 2026-09-25 | Next Monthly Report: Thursday, October 01, 2026 8:00 AM ET_