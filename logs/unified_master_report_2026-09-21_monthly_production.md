# Unified Master Report — Monthly Stage

**September 21, 2026** — 8:00 AM ET | September 2026 Performance & October Outlook

- **System Boot:** Monthly recalibration & moat strength update
- **Report Type:** MONTHLY STRATEGIC REVIEW
- **Data Window:** September 1-01, 2026 (current month)

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


## Section 1: MONTHLY ACTUAL VS TARGET — COMPLETE VARIANCE ANALYSIS

See Section 0's PERFORMANCE VS TARGET block for YTD actual/target/gap and this month's pace vs. the regime-adjusted target — not repeated here.

**Rest-of-Year Projection** (using the same regime-adjusted target as Section 0):

- Remaining months: 3 (as of September)
- Remaining target (est): $300,000 (3 × $100,000)
- Pace required to recover: $100,000/month (regime-adjusted)
- This month so far (MTD, live): $43,535


## Section 2: MONTHLY PERFORMANCE BY ACCOUNT (ALL 11)

| Account | Balance | % Portfolio | Target (mo) | Actual (MTD) | Actual (YTD) | Variance (MTD) | Open Positions | Status |
|---|---|---|---|---|---|---|---|---|
| Account A (232) | $403,000 | 17.2% | $34,010 | $27,916 | $111,568 | $-6,094 (-17.9%) | 179 | ⚠️ BELOW |
| Account B (275) | $261,000 | 11.1% | $9,863 | $385 | $24,410 | $-9,478 (-96.1%) | 21 | ⚠️ BELOW |
| Account C (634) | $266,000 | 11.4% | $10,052 | $4,523 | $15,938 | $-5,529 (-55.0%) | 21 | ⚠️ BELOW |
| Fidelity (Rahul) | $498,560 | 21.3% | $18,840 | $2,859 | $32,238 | $-15,981 (-84.8%) | 42 | ⚠️ BELOW |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $1,480 | $136 | $2,774 | $-1,344 (-90.8%) | 8 | ⚠️ BELOW |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $4,840 | $3,045 | $5,588 | $-1,795 (-37.1%) | 14 | ⚠️ BELOW |
| Vanguard (Rahul) | $320,492 | 13.7% | $12,111 | $0 | $0 | $-12,111 (-100.0%) | 28 | ⚠️ BELOW |
| Robinhood (Individual) | $13,000 | 0.6% | $491 | $0 | $302 | $-491 (-100.0%) | 4 | ⚠️ BELOW |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $8,314 | $4,718 | $17,809 | $-3,596 (-43.3%) | 18 | ⚠️ BELOW |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | $0 | $0 (+0.0%) | 0 | — (no target) |

No option-level realized data for: Vanguard (Rahul), Fidelity 401K (Rahul) — see `realized_pnl.py`'s module docstring for why (e.g. Vanguard's option-side data is untracked).


## Section 3: MONTHLY PREMIUM vs TARGET (real)

Monthly net target (base): $100,000 | YTD actual: $284,620

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
| 2026-09 | 43,535 | 100,000 | -56,465 |

Per-driver attribution (regime / thesis / timing / slippage) requires trade-level tagging that is not captured yet — omitted rather than estimated.


## Section 4: MOAT RECALIBRATION & TIER ASSIGNMENTS

**Tier 1 — Strong Moat** (Conviction ≥7, 30+ day history, positive P&L)

| Symbol | Conv | Heat | Price | Value | RSI | 52W Range | Verdict |
|---|---|---|---|---|---|---|---|
| APP | 9.1 | GREEN | $328.59 | $328,590 | 57.4 | 7% | STRONG (Oversold / Attractive — confirmed by RSI/range AND 200-day trend positioning) |
| LASR | 8.5 | YELLOW | $39.84 | $7,968 | 42.3 | 20% | STRONG (Approaching extremes) |
| ONDS | 8.5 | YELLOW | $7.40 | $740 | 42.6 | 24% | STRONG (Approaching extremes) |
| JD | 8.4 | YELLOW | $27.23 | $16,335 | 36.4 | 22% | STRONG (Approaching extremes) |
| GOOGL | 8.4 | GREEN | $356.24 | $142,494 | 63.8 | 70% | STRONG (Neutral positioning) |

Tier 1 summary: 5 positions, quality improving

**Tier 2 — Moderate Moat** (Conviction 5-7)

- LLY: 7.9/10 (YELLOW) | Value $349,674 — Approaching extremes
- ANET: 7.8/10 (YELLOW) | Value $182,880 — Approaching extremes
- IONQ: 7.8/10 (YELLOW) | Value $32,504 — Approaching extremes

**Tier 3 & Exited:**

- CRWD: 5.9/10 (RED) — Watch for exit
- ZBH: 5.9/10 (GREEN) — Watch for exit

**Moat verdict:** Quality improving with framework. Tier 1 concentration rising.


## Section 5: PERFORMANCE PACE (real)

- YTD net premium (real): $284,620 (Jan–Sep)
- Average monthly pace: $31,624/month
- Annualized run-rate: $379,493
- Monthly net target (base): $100,000

Note: The prior Citadel/peer comparison used fabricated P&L figures and has been removed. Benchmark against external estimates manually if you want that view.


## Section 6: ACTIVE DECISION TRACKER


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



---
_Report generated: 2026-09-21 | Next Monthly Report: Thursday, October 01, 2026 8:00 AM ET_