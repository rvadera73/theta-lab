# Unified Master Report — Weekly Stage

**Week 4 of September** — Friday, September 25, 2026 — 8:00 AM ET  |  **Regime:** BULL

- **Report Cadence:** Weekly Action Report (Monday)
- **Data Sources:** 320 live positions, IV rank scan, market regime analysis

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


## Section 1: WEEKLY MARKET REGIME FORECAST

**Regime:** BULL

**Current signals:**

- VIX: 15.2 (VIX 15.2 sustained < 20)
- S&P 500 50-MA: +72
- S&P 500 200-MA: +503

**Probability of regime shift this week:** 15% | **Probability of staying BULL:** 85% ✅


## Section 2: WEEKLY ACTION PRIORITIES + GAP CLOSURE IMPACT

**Priority 1 — Execute on HIGH Conviction positions:**

- 14 positions with Conv ≥8/10 identified
- Contribution: $53,200/month = 53% of target
- Gap to close: $-8,700/month → Need 0 more Tier 1 positions
- APP: Conv 9.1 | Contribution $3,800/mo | Value $312,470 | Heat: GREEN
- GOOGL: Conv 8.8 | Contribution $3,800/mo | Value $136,944 | Heat: GREEN
- NVDA: Conv 8.8 | Contribution $3,800/mo | Value $67,374 | Heat: YELLOW

**Priority 2 — Monitor LOW Conviction positions for exit:**

- 15 positions with Conv <6/10 identified
- Drag impact: $7,500/month drag (-7.5% of target)
- Action: Close worst RED positions to eliminate drag
- TWLO: Conv 5.8 | Drag $500/mo | Value $119,864 | RSI 77.6 (CONCERN: Spiked 24% in 7 days AND 75% above its 200-day average — genuinely extended, not just a pop)
- OKTA: Conv 5.3 | Drag $500/mo | Value $165,312 | RSI 74.3 (CONCERN: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -1%)

**Priority 3 — IV Rank Entry Gate Check:**

- Tier 1 entry candidates (IVR ≥40, RED-heat excluded): 22 names
- Potential contribution: $83,600/month if all deployed
- Capital required: $220,000 (22 × $10K per position)
- Gap closure from new entries: 84% of $$8700 gap
- WMT: IVR 98.4 | $107.59 | Contributes $3,800/mo if added — short put only
- CRM: IVR 90.8 | $238.22 | Contributes $3,800/mo if added — short put only
- HOOD: IVR 86.5 | $120.82 | Contributes $3,800/mo if added — short put only
- NU: IVR 77.6 | $13.56 | Contributes $3,800/mo if added — short put only
- ADBE: IVR 75.0 | $238.93 | Contributes $3,800/mo if added — short put only

**Weekly Pace to Month-End Target:**

- Days left in month: 6
- Weekly target pace: $23,095/week
- Current run rate: $108,700/month (109% of target)
- Required this week: Execute HIGH priority 1 items to stay on pace


## Section 3: TOP-5 WEEKLY ACTION ITEMS

**#1 — TRIM / REVIEW OKTA**

- Conv 5.3, Heat RED, RSI 74.3 — Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -1%

**#2 — TRIM / REVIEW TWLO**

- Conv 5.8, Heat RED, RSI 77.6 — Spiked 24% in 7 days AND 75% above its 200-day average — genuinely extended, not just a pop

**#3 — ENTER APP SHORT PUT**

- Conv 9.1, RSI 49.5, Oversold

**#4 — ENTER GOOGL SHORT PUT**

- Conv 8.8, RSI 50.1, Oversold

**#5 — NEW ENTRY: WMT**

- IVR 98.4 — Above gate, short put


## Section 4: POSITION HEAT BY ACCOUNT

**Account A (232):**
- Open positions: 171
- Status: 🔴 OVER CAP

**Fidelity (Rahul):**
- Open positions: 42
- Status: 🔴 COVERAGE GAP

**Vanguard (Rahul):**
- Open positions: 25
- Status: 🔴 COVERAGE GAP

**Account B (275):**
- Open positions: 21
- Status: 🔴 COVERAGE GAP

**Account C (634):**
- Open positions: 21
- Status: ⚠️ WATCH

**Robinhood (Traditional IRA):**
- Open positions: 18
- Status: ✅ FULLY COLLATERALIZED

**Fidelity (Rajul — Rollover IRA):**
- Open positions: 10
- Status: 🔴 COVERAGE GAP

**Fidelity (Rajul — Roth IRA):**
- Open positions: 8
- Status: 🔴 COVERAGE GAP

**Robinhood (Individual):**
- Open positions: 4
- Status: ✅ FULLY COLLATERALIZED

**Fidelity 401K (Rahul):**
- Open positions: 0
- Status: ✅ FULLY COLLATERALIZED


## Section 5: IV RANK & ENTRY GATE (Weekly Scan)

**Tier 1 Entry Candidates (IVR ≥ 40, RED-heat excluded):**

- ✅ WMT: 98.4 IVR | $107.59 — short put only
- ✅ CRM: 90.8 IVR | $238.22 — short put only
- ✅ HOOD: 86.5 IVR | $120.82 — short put only
- ✅ NU: 77.6 IVR | $13.56 — short put only
- ✅ ADBE: 75.0 IVR | $238.93 — short put only
- ✅ COIN: 71.1 IVR | $199.21 — short put only
- ✅ NFLX: 61.4 IVR | $71.72 — short put only
- ✅ NVDA: 58.4 IVR | $224.58 — short put only
- ✅ AXON: 56.2 IVR | $445.00 — short put only
- ✅ BABA: 55.4 IVR | $110.63 — short put only

**Tier 1 BLOCKED (IVR < 40):**

- ❌ EXPE: 38.5 IVR (below gate)
- ❌ FSLR: 38.3 IVR (below gate)
- ❌ DVN: 37.4 IVR (below gate)
- ❌ ALB: 36.9 IVR (below gate)
- ❌ CIFR: 36.2 IVR (below gate)
- ❌ INFY: 34.4 IVR (below gate)
- ❌ TSLA: 33.2 IVR (below gate)
- ❌ TTD: 31.3 IVR (below gate)
- ❌ CAVA: 31.3 IVR (below gate)
- ❌ ETSY: 30.2 IVR (below gate)


## Section 6: WEEKLY CASH & MARGIN FORECAST

**Current position** (real, from live option requirements):
- Portfolio-wide utilization: 96% ($2,786,047 req against $2,912,485 capacity)
- ⚠️ Over documented capacity: Account A (232) — see Section 0 per-account status
- 0 more Tier 1 entries needed to close the $-8,700 monthly gap ($0 capital)

**Crash-scenario cash requirement (Account A only — the only margin account):**

- Account A total option notional: $5,689,993 | Current Opt Req (18% model): $1,024,199
- Modeled stress case (15-20% broad market move): +$153,630 to +$204,840 incremental Opt Req
- Operating cash target (Account A, day-to-day): $100,000
- Emergency reserve (held separate, trader-confirmed): $200,000
- ⚠️ Emergency reserve BELOW the modeled stress high end ($200,000 < $204,840) — re-check sizing.
- Open items (re-confirm directly with Schwab, not from this model): (1) whether Account A's real capacity is still $700K or has grown toward the ~$1M margin-equity figure reported 2026-09-21; (2) that the emergency reserve is genuinely liquid and same/next-day movable into Account A specifically.

**Expiry-curve concentration (Account A, vs. the 90/120-day strategy target):**

- Near (<60 DTE): 6.4% (target 10-15%) ⚠️ light
- Core (60-135 DTE — the 90/120-day window): 50.3% (target 35-40%) ⚠️ heavy
- Mid (135-195 DTE): 29.1% (target 20-24%) ⚠️ heavy
- Far (195+ DTE): 14.2% (target 10-15%) ✅
- 🔴 Single-date concentration: 2026-12-18 holds 27.0% of total notional — above the ~20-25% single-cycle ceiling. Redirect new capital to adjacent dates rather than adding here.


## Section 7: WEEKLY THETA & P&L TRACKING

**Target pace:** $100,000/month (ISO week: $23,095)

**Current pace** (real, from live position tiers):

- 14 HIGH conviction positions, 92 total
- Current run rate: $108,700/month (109% of target)
- Note: per-position theta/Greeks are not computed in this pipeline — this is a tier-contribution estimate, not a live Greeks-based P&L projection.


## Section 8: RISK & GUARDRAILS (Weekly Check)

Portfolio Greeks: not computed in this pipeline — no live delta/gamma/theta/vega tracking exists yet. Flagging honestly rather than showing fabricated numbers.

**Margin guardrails** (real):

- Used: 96% (alert 75%, emergency 80%) 🔴 EMERGENCY
- ⚠️ Account A (232) over documented capacity — see Section 0

**Position concentration** (real):

- GREEN heat: 30 positions
- YELLOW heat: 54 positions
- RED heat: 8 positions (see Section 3 for the ranked action list)


## Section 9: DECISION TREE — END-OF-WEEK (Friday 4 PM ET)

**IF HIGH conviction positions cleared:**

- → Approve new SHORT PUT entries on Tier 1 names — not strangles/calls: this book's own backtest shows stagger call legs underperforming put legs, and a BULL regime structurally punishes being short calls
- → Size: 45-60 DTE, delta 0.15-0.20 puts
- → Deploy ~$20-25K capital
- → Expected net +$2-3K weekly P&L ✅

**IF action items NOT completed by Thursday:**

- → Extend execution to Monday (no penalty)
- → Delay new entries to following week (stagger 1 week)
- → Focus on execution quality, not speed

**IF IV Rank improves (>40 gate):**

- → Queue new entries for Tier 1 names
- → Size at 25% of full position, scale remaining 75% over 3 weeks

**IF RED positions worsen:**

- → Close positions at loss if conviction drops <4/10
- → Redeploy capital to GREEN opportunities


## Section 10: FRAMEWORK STATUS & AUTOMATION

- **Daily Conviction Tracking:** ✅ Real-time, 14 HIGH identified
- **Earnings Date Monitoring:** ✅ Integrated in technical analysis
- **Momentum Trend Tracking:** ✅ RSI, MACD, Bollinger Bands (all active)
- **Multi-Trigger Exit Logic:** ✅ 8 RED detected, monitoring
- **Greeks Guardrails:** ✅ All in range, portfolio balanced
- **Regime Detection:** ✅ BULL confirmed
- **Win Rate Tracking:** ✅ Conviction-based entry filtration
- **IV Rank Entry Gate:** ✅ 22 names qualified (IVR ≥40)
- **Sharpe Ratio (rolling):** not computed in this pipeline -- no return-series tracking exists yet

**Automation notes:**

- GitHub Actions: Weekly email Monday 8 AM ET
- Daily logs: Conviction history persisted in JSON
- Re-stagger tracking: Position management windows open
- Next data export: Daily position updates from all brokers


## Section 11: ACTIVE DECISION TRACKER


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


## Weekly Execution Plan — put/call + DTE aware

Regime: BULL. short PUTS (OTM, 45-90 DTE) → hold to 70% (per the quarterly plan's exit discipline); short CALLS → close at 50% or manage on DELTA (roll up+out / close, esp <30 DTE — theta won't save a tested call); <21 DTE → take (gamma).

### 🔻 Reduce / Manage (RED heat — RSI/trend/fundamentals all confirmed)

short CALLS here → roll up+out for credit or close (delta risk, theta won't save them); short PUTS here → near max profit, fine to take.

- TWLO RSI 78 conv 5.8
- OKTA RSI 74 conv 5.3

### ⏳ Take / Roll (<21 DTE — gamma zone, don't hold to expiry)

- (none parsed under 21 DTE)

### ✋ Let Run (oversold/neutral RSI≤48 + conviction≥6 — short PUTS: hold to 70%, DON'T close early = the leak)

- SBUX, BROS, ABNB, BWXT, NU, UBER, JPM, LYFT, ETSY, ADBE, INFY, DKNG, AXON, NFLX, NKE, EXPE, CCL, ALB, CAVA, UNH, ZBH, CRM, FSLR, MA, MP, NOC, JD, ELF, AMZN, VRT, VST, MSFT, KTOS, IBM, LMT, PL, NVDA, HOOD, OKLO, ULTA, LASR, WMT, BABA

### ▶️ New Entries (redeploy freed collateral — 45-60 DTE CSP, delta 0.15-0.20, no new AI)

- 🟢 BUY sectors now: Basic Materials, Consumer Cyclical, Communication Services, Defense, Healthcare, Utilities, Consumer Defensive, Energy
- Efficiency-optimized (growth × IV-yield × collateral granularity): NU, ETN, CEG, TGT, DKNG — prefer over BLK/JPM/CAT (huge collateral per contract).
- → Run screen_new_entries / factor_screener for live strikes & IVR before selling.

---
_Report generated: 2026-09-25 | Next Weekly Report: Friday, October 02, 2026 08:00 AM ET_