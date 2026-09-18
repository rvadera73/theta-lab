# Unified Master Report — Monthly Stage

**September 18, 2026** — 8:00 AM ET | September 2026 Performance & October Outlook

- **System Boot:** Monthly recalibration & moat strength update
- **Report Type:** MONTHLY STRATEGIC REVIEW
- **Data Window:** September 1-01, 2026 (current month)

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


## Section 1: MONTHLY ACTUAL VS TARGET — COMPLETE VARIANCE ANALYSIS

See Section 0's PERFORMANCE VS TARGET block for YTD actual/target/gap and this month's pace vs. the regime-adjusted target — not repeated here.

**Rest-of-Year Projection** (using the same regime-adjusted target as Section 0):

- Remaining months: 3 (as of September)
- Remaining target (est): $300,000 (3 × $100,000)
- Pace required to recover: $100,000/month (regime-adjusted)
- This month so far (MTD, live): $33,160


## Section 2: MONTHLY PERFORMANCE BY ACCOUNT (ALL 11)

| Account | Balance | % Portfolio | Target (mo) | Actual (MTD) | Actual (YTD) | Variance (MTD) | Open Positions | Status |
|---|---|---|---|---|---|---|---|---|
| Account A (232) | $403,000 | 17.2% | $28,615 | $27,916 | $111,568 | $-699 (-2.4%) | 169 | ✅ ON TARGET |
| Account B (275) | $261,000 | 11.1% | $10,669 | $385 | $24,410 | $-10,284 (-96.4%) | 21 | ⚠️ BELOW |
| Account C (634) | $266,000 | 11.4% | $10,874 | $4,523 | $15,938 | $-6,351 (-58.4%) | 21 | ⚠️ BELOW |
| Fidelity (Rahul) | $498,560 | 21.3% | $20,380 | $2,859 | $32,238 | $-17,521 (-86.0%) | 42 | ⚠️ BELOW |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $1,601 | $136 | $2,774 | $-1,465 (-91.5%) | 8 | ⚠️ BELOW |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $5,236 | $3,045 | $5,588 | $-2,191 (-41.8%) | 14 | ⚠️ BELOW |
| Vanguard (Rahul) | $320,492 | 13.7% | $13,101 | $0 | $0 | $-13,101 (-100.0%) | 28 | ⚠️ BELOW |
| Robinhood (Individual) | $13,000 | 0.6% | $531 | $0 | $302 | $-531 (-100.0%) | 4 | ⚠️ BELOW |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $8,993 | $4,718 | $17,809 | $-4,275 (-47.5%) | 18 | ⚠️ BELOW |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |

No option-level realized data for: Vanguard (Rahul), Fidelity 401K (Rahul) — see `realized_pnl.py`'s module docstring for why (e.g. Vanguard's option-side data is untracked).


## Section 3: MONTHLY PREMIUM vs TARGET (real)

Monthly net target (base): $100,000 | YTD actual: $274,245

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
| 2026-09 | 33,160 | 100,000 | -66,840 |

Per-driver attribution (regime / thesis / timing / slippage) requires trade-level tagging that is not captured yet — omitted rather than estimated.


## Section 4: MOAT RECALIBRATION & TIER ASSIGNMENTS

**Tier 1 — Strong Moat** (Conviction ≥7, 30+ day history, positive P&L)

| Symbol | Conv | Heat | Price | Value | RSI | 52W Range | Verdict |
|---|---|---|---|---|---|---|---|
| APP | 9.1 | GREEN | $316.11 | $316,105 | 49.1 | 4% | STRONG (Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning) |
| GOOGL | 8.8 | GREEN | $350.96 | $140,384 | 53.6 | 67% | STRONG (Neutral positioning) |
| IONQ | 8.5 | YELLOW | $38.09 | $22,854 | 46.4 | 21% | STRONG (Approaching extremes) |
| TSM | 8.5 | YELLOW | $432.17 | $172,868 | 59.4 | 78% | STRONG (Approaching extremes) |
| GEV | 8.4 | GREEN | $934.21 | $373,682 | 53.6 | 61% | STRONG (Neutral positioning) |

Tier 1 summary: 5 positions, quality improving

**Tier 2 — Moderate Moat** (Conviction 5-7)

- LYFT: 7.8/10 (YELLOW) | Value $9,156 — Approaching extremes
- ISRG: 7.8/10 (YELLOW) | Value $195,990 — Approaching extremes
- BROS: 7.8/10 (GREEN) | Value $3,953 — Dropped -12% in 7 days AND -30% below its 200-day average — genuinely beaten down

**Tier 3 & Exited:**

- CRWD: 5.9/10 (RED) — Watch for exit
- ZBH: 5.9/10 (GREEN) — Watch for exit

**Moat verdict:** Quality improving with framework. Tier 1 concentration rising.


## Section 5: PERFORMANCE PACE (real)

- YTD net premium (real): $274,245 (Jan–Sep)
- Average monthly pace: $30,472/month
- Annualized run-rate: $365,660
- Monthly net target (base): $100,000

Note: The prior Citadel/peer comparison used fabricated P&L figures and has been removed. Benchmark against external estimates manually if you want that view.


## Section 6: ACTIVE DECISION TRACKER


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



---
_Report generated: 2026-09-18 | Next Monthly Report: Thursday, October 01, 2026 8:00 AM ET_