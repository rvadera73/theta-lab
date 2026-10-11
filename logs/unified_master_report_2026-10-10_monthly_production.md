# Unified Master Report — Monthly Stage

**October 10, 2026** — 8:00 AM ET | October 2026 Performance & November Outlook

- **System Boot:** Monthly recalibration & moat strength update
- **Report Type:** MONTHLY STRATEGIC REVIEW
- **Data Window:** October 1-01, 2026 (current month)

## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,432,003
- **Total notional exposure:** $8,435,045
- **Total option requirement:** $2,860,000
- **Positions with short puts:** 84
- **Positions with short calls:** 53
- **YTD Net Premium:** $368,515 (live from transactions)
- **Month-to-Date Premium:** $27,025
- **Snapshot currency:** 2026-10-10

### Two Lenses on Monthly Performance

_(both derived from your transaction history)_

#### Lens 1 — Premium Income (cash flow) = what you COLLECT selling options [the $100K target]

| Account | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | YTD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Account A (232) | 10,255 | 12,483 | 23,800 | 20,880 | -1,244 | -2,884 | 20,362 | 50,309 | 67,164 | 15,954 | 217,079 |
| Account B (275) | 31 | 3,322 | 1,546 | 4,894 | 9,709 | 3,948 | 575 | 3,476 | 7,497 | 2,044 | 37,042 |
| Account C (634) | 31 | 934 | 449 | 1,959 | 4,435 | 1,321 | 2,286 | 6,028 | 6,308 | 0 | 23,751 |
| Fidelity (Rahul) | 17 | 1,824 | 1,231 | 5,580 | 4,947 | 10,629 | 5,151 | 3,339 | 11,763 | 5,080 | 49,561 |
| Fidelity (Rajul — Rollover IRA) | 0 | 0 | 0 | 944 | 932 | 0 | 667 | 3,508 | 280 | 3,947 | 10,278 |
| Fidelity (Rajul — Roth IRA) | 0 | 0 | 0 | 95 | 189 | 1,028 | 1,326 | 1,196 | 0 | 0 | 3,834 |
| Robinhood (Individual) | 0 | 107 | 0 | 0 | 205 | -9 | 0 | 609 | 350 | 0 | 1,262 |
| Robinhood (Traditional IRA) | 0 | 518 | 816 | 6,275 | 2,879 | 2,087 | 517 | 5,573 | 7,043 | 0 | 25,708 |
| **TOTAL** | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 100,405 | 27,025 | 368,515 |
| Gross SOLD (STO, opened this month) | 181,739 | 68,408 | 199,758 | 324,125 | 349,672 | 243,331 | 135,826 | 242,546 | 233,320 | 50,774 | 2,029,499 |
| Net REALIZED (FIFO, closed this month) | 10,334 | 19,188 | 27,842 | 40,627 | 22,052 | 16,120 | 30,884 | 74,038 | 100,405 | 27,025 | 368,515 |

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
| Account A (232) | $423,000 | 17.4% | $5,948,715 | $850,000 | Margin | 🔴 EMERGENCY | $33,186 | ✅ $-2,654 |
| Account B (275) | $316,000 | 13.0% | $377,875 | $316,450 | Cash-Sec | 🟠 COVERAGE GAP | $11,652 | ✅ $-932 |
| Account C (634) | $213,000 | 8.8% | $346,272 | $213,150 | Cash-Sec | 🟠 COVERAGE GAP | $7,854 | ✅ $-628 |
| Fidelity (Rahul) | $560,000 | 23.0% | $692,320 | $624,561 | Cash-Sec | 🟠 COVERAGE GAP | $20,649 | ✅ $-1,651 |
| Fidelity (Rajul — Roth IRA) | $44,000 | 1.8% | $53,909 | $51,939 | Cash-Sec | 🟠 COVERAGE GAP | $1,621 | ✅ $-130 |
| Fidelity (Rajul — Rollover IRA) | $140,000 | 5.8% | $177,344 | $163,200 | Cash-Sec | 🟠 COVERAGE GAP | $5,162 | ✅ $-412 |
| Vanguard (Rahul) | $306,000 | 12.6% | $470,058 | $419,931 | Cash-Sec | 🟠 COVERAGE GAP | $11,283 | ✅ $-902 |
| Robinhood (Individual) | $13,000 | 0.5% | $27,929 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $479 | ✅ $-38 |
| Robinhood (Traditional IRA) | $220,000 | 9.0% | $340,623 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,112 | ✅ $-648 |
| Fidelity 401K (Rahul) | $197,000 | 8.1% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,432,003 | 100.0% | $8,435,045 | $2,860,000 |  |  |  |  |

- **Account A (232):** 184 option positions | Monthly target: $33,186 | Equity: ADBE 300sh, APP 100sh, AXON 200sh, COIN 200sh, CRCL 100sh +15 more
  - ℹ️ Opt Req shown ($850,000) is the real broker-confirmed figure (2026-10-02) — the live computed estimate (18% of notional) reads $1,070,769, 26% higher. Re-confirm live if this account's status matters for a decision.
- **Account B (275):** 19 option positions | Monthly target: $11,652 | Equity: CRM 100sh, NVO 100sh
- **Account C (634):** 21 option positions | Monthly target: $7,854 | Equity: ABNB 100sh, NKE 100sh, PL 100sh, TWLO 324sh
- **Fidelity (Rahul):** 42 option positions | Monthly target: $20,649 | Equity: FMC 100sh, LYFT 100sh, NKE 100sh, CRM 200sh
- **Fidelity (Rajul — Roth IRA):** 8 option positions | Monthly target: $1,622 | Equity: FMC 200sh, NKE 200sh, OKTA 100sh, SONO 400sh
- **Fidelity (Rajul — Rollover IRA):** 9 option positions | Monthly target: $5,162
- **Vanguard (Rahul):** 28 option positions | Monthly target: $11,283
- **Robinhood (Individual):** 4 option positions | Monthly target: $479 | Equity: RIOT 100sh, AAPL 0sh
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Robinhood (Traditional IRA):** 22 option positions | Monthly target: $8,112
  - ⚠️ Balance date UNCONFIRMED — this figure has no known verification date, re-confirm before trusting the ✅ FULLY COLLATERALIZED reading above
- **Fidelity 401K (Rahul):** No open positions | Monthly target: $0
- **Fidelity (Rahul — Roth IRA Minor):** No open positions | Monthly target: $0
  - ⚠️ Balance as of 2026-05-31 (132 days ago) — re-confirm if the ✅ FULLY COLLATERALIZED reading above matters for a decision

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
- Actual YTD: $368,515.0
- Gap to close: $631,485.0 (63.1%)
- Monthly average (YTD): $36,852
- Monthly average needed: $100,000
- Monthly gap: $-8,000

**Position tier distribution → gap closure:**

- Tier 1 (15 positions): $57,000/month (57% of $100,000 target)
- Tier 2 (58 positions): $58,000/month (58% of target)
- Tier 3 (14 positions): $-7,000/month (-7% drag)
- Current total: 87 positions = $108,000/month (108% of target)

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
| Account A (232) | $82,965 | $33,186 |
| Account B (275) | $29,130 | $11,652 |
| Account C (634) | $19,635 | $7,854 |
| Fidelity (Rahul) | $51,622 | $20,649 |
| Fidelity (Rajul — Roth IRA) | $4,055 | $1,622 |
| Fidelity (Rajul — Rollover IRA) | $12,905 | $5,162 |
| Vanguard (Rahul) | $28,207 | $11,283 |
| Robinhood (Individual) | $1,197 | $479 |
| Robinhood (Traditional IRA) | $20,280 | $8,112 |
| **TOTAL** | $249,996 | $99,999 |


## Section 1: MONTHLY ACTUAL VS TARGET — COMPLETE VARIANCE ANALYSIS

See Section 0's PERFORMANCE VS TARGET block for YTD actual/target/gap and this month's pace vs. the regime-adjusted target — not repeated here.

**Rest-of-Year Projection** (using the same regime-adjusted target as Section 0):

- Remaining months: 2 (as of October)
- Remaining target (est): $200,000 (2 × $100,000)
- Pace required to recover: $100,000/month (regime-adjusted)
- This month so far (MTD, live): $27,025


## Section 2: MONTHLY PERFORMANCE BY ACCOUNT (ALL 11)

| Account | Balance | % Portfolio | Target (mo) | Actual (MTD) | Actual (YTD) | Variance (MTD) | Open Positions | Status |
|---|---|---|---|---|---|---|---|---|
| Account A (232) | $423,000 | 17.4% | $33,186 | $15,953 | $217,078 | $-17,233 (-51.9%) | 184 | ⚠️ BELOW |
| Account B (275) | $316,000 | 13.0% | $11,652 | $2,044 | $37,042 | $-9,608 (-82.5%) | 19 | ⚠️ BELOW |
| Account C (634) | $213,000 | 8.8% | $7,854 | $0 | $23,750 | $-7,854 (-100.0%) | 21 | ⚠️ BELOW |
| Fidelity (Rahul) | $560,000 | 23.0% | $20,649 | $5,079 | $49,560 | $-15,570 (-75.4%) | 42 | ⚠️ BELOW |
| Fidelity (Rajul — Roth IRA) | $44,000 | 1.8% | $1,622 | $0 | $3,833 | $-1,622 (-100.0%) | 8 | ⚠️ BELOW |
| Fidelity (Rajul — Rollover IRA) | $140,000 | 5.8% | $5,162 | $3,946 | $10,278 | $-1,216 (-23.6%) | 9 | ⚠️ BELOW |
| Vanguard (Rahul) | $306,000 | 12.6% | $11,283 | $0 | $0 | $-11,283 (-100.0%) | 28 | ⚠️ BELOW |
| Robinhood (Individual) | $13,000 | 0.5% | $479 | $0 | $1,260 | $-479 (-100.0%) | 4 | ⚠️ BELOW |
| Robinhood (Traditional IRA) | $220,000 | 9.0% | $8,112 | $0 | $25,707 | $-8,112 (-100.0%) | 22 | ⚠️ BELOW |
| Fidelity 401K (Rahul) | $197,000 | 8.1% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |

No option-level realized data for: Vanguard (Rahul), Fidelity 401K (Rahul) — see `realized_pnl.py`'s module docstring for why (e.g. Vanguard's option-side data is untracked).


## Section 3: MONTHLY PREMIUM vs TARGET (real)

Monthly net target (base): $100,000 | YTD actual: $368,515

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
| 2026-09 | 100,405 | 100,000 | 405 |
| 2026-10 | 27,025 | 100,000 | -72,975 |

Per-driver attribution (regime / thesis / timing / slippage) requires trade-level tagging that is not captured yet — omitted rather than estimated.


## Section 4: MOAT RECALIBRATION & TIER ASSIGNMENTS

**Tier 1 — Strong Moat** (Conviction ≥7, 30+ day history, positive P&L)

| Symbol | Conv | Heat | Price | Value | RSI | 52W Range | Verdict |
|---|---|---|---|---|---|---|---|
| BROS | 9.0 | GREEN | $38.05 | $3,805 | 43.1 | 2% | STRONG (Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning) |
| GOOGL | 8.8 | GREEN | $351.66 | $210,996 | 46.9 | 66% | STRONG (Neutral positioning) |
| NVDA | 8.8 | YELLOW | $229.28 | $68,784 | 52.8 | 82% | STRONG (82% of 52-week range approaching the high extreme (90%+)) |
| UBER | 8.6 | YELLOW | $71.51 | $42,906 | 52.8 | 18% | STRONG (17% of 52-week range approaching the low extreme (10%-)) |
| JD | 8.6 | YELLOW | $27.09 | $16,254 | 47.7 | 24% | STRONG (24% of 52-week range approaching the low extreme (10%-)) |

Tier 1 summary: 5 positions, quality improving

**Tier 2 — Moderate Moat** (Conviction 5-7)

- RBLX: 7.9/10 (YELLOW) | Value $52,899 — Spiked 14% in 7 days but only -12% vs its 200-day average — short-term move, not structurally extended
- LLY: 7.9/10 (YELLOW) | Value $353,781 — 78% of 52-week range approaching the high extreme (90%+)
- NFLX: 7.8/10 (GREEN) | Value $154,660 — Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning

**Tier 3 & Exited:**

- CEG: 5.9/10 (YELLOW) — Watch for exit
- BE: 5.8/10 (YELLOW) — Watch for exit

**Moat verdict:** Quality improving with framework. Tier 1 concentration rising.


## Section 5: PERFORMANCE PACE (real)

- YTD net premium (real): $368,515 (Jan–Oct)
- Average monthly pace: $36,852/month
- Annualized run-rate: $442,218
- Monthly net target (base): $100,000

Note: The prior Citadel/peer comparison used fabricated P&L figures and has been removed. Benchmark against external estimates manually if you want that view.


## Section 6: ACTIVE DECISION TRACKER


**⏳ march_strangle_entry_gate** — BLOCKED

Hold off on new March-2027-expiry strangle entries (including adding to AXON's existing March legs) until BOTH: (1) Account A margin utilization back under 85% (was 99%/EMERGENCY on 2026-09-10), and (2) portfolio crash-risk level back to YELLOW or better (was RED, 53.9% 30-day, on 2026-09-10). Resolve axon_sept18_roll_450c and pypl_naked_calls_cleanup first -- don't stack a third naked-call layer while those two are still open.
  - Live: account_a_margin_utilization_pct = 94.44444444444444
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



---
_Report generated: 2026-10-10 | Next Monthly Report: Sunday, November 01, 2026 8:00 AM ET_