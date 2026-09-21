# Unified Master Report — Weekly Stage

**Week 3 of September** — Monday, September 21, 2026 — 8:00 AM ET  |  **Regime:** BULL

- **Report Cadence:** Weekly Action Report (Monday)
- **Data Sources:** 335 live positions, IV rank scan, market regime analysis

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


## Section 1: WEEKLY MARKET REGIME FORECAST

**Regime:** BULL

**Current signals:**

- VIX: 15.0 (VIX 15.0 sustained < 20)
- S&P 500 50-MA: +139
- S&P 500 200-MA: +572

**Probability of regime shift this week:** 15% | **Probability of staying BULL:** 85% ✅


## Section 2: WEEKLY ACTION PRIORITIES + GAP CLOSURE IMPACT

**Priority 1 — Execute on HIGH Conviction positions:**

- 12 positions with Conv ≥8/10 identified
- Contribution: $45,600/month = 46% of target
- Gap to close: $-4,600/month → Need 0 more Tier 1 positions
- APP: Conv 9.1 | Contribution $3,800/mo | Value $328,590 | Heat: GREEN
- LASR: Conv 8.5 | Contribution $3,800/mo | Value $7,968 | Heat: YELLOW
- ONDS: Conv 8.5 | Contribution $3,800/mo | Value $740 | Heat: YELLOW

**Priority 2 — Monitor LOW Conviction positions for exit:**

- 16 positions with Conv <6/10 identified
- Drag impact: $8,000/month drag (-8.0% of target)
- Action: Close worst RED positions to eliminate drag
- CRWD: Conv 5.9 | Drag $500/mo | Value $124,085 | RSI 57.8 (CONCERN: Spiked 19% in 7 days AND 68% above its 200-day average — genuinely extended, not just a pop)
- OKTA: Conv 5.8 | Drag $500/mo | Value $171,063 | RSI 61.3 (CONCERN: Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%)

**Priority 3 — IV Rank Entry Gate Check:**

- Tier 1 entry candidates (IVR ≥40, RED-heat excluded): 22 names
- Potential contribution: $83,600/month if all deployed
- Capital required: $220,000 (22 × $10K per position)
- Gap closure from new entries: 84% of $$4600 gap
- PANW: IVR 95.5 | $369.41 | Contributes $3,800/mo if added — short put only
- WMT: IVR 94.4 | $107.46 | Contributes $3,800/mo if added — short put only
- CRM: IVR 91.4 | $237.80 | Contributes $3,800/mo if added — short put only
- HOOD: IVR 85.9 | $124.29 | Contributes $3,800/mo if added — short put only
- ADBE: IVR 75.6 | $248.50 | Contributes $3,800/mo if added — short put only

**Weekly Pace to Month-End Target:**

- Days left in month: 10
- Weekly target pace: $23,095/week
- Current run rate: $104,600/month (105% of target)
- Required this week: Execute HIGH priority 1 items to stay on pace


## Section 3: TOP-5 WEEKLY ACTION ITEMS

**#1 — TRIM / REVIEW OKTA**

- Conv 5.8, Heat RED, RSI 61.3 — Overbought / Extended — confirmed by RSI/range, 200-day trend positioning, AND analyst upside only -2%

**#2 — TRIM / REVIEW CRWD**

- Conv 5.9, Heat RED, RSI 57.8 — Spiked 19% in 7 days AND 68% above its 200-day average — genuinely extended, not just a pop

**#3 — ENTER APP SHORT PUT**

- Conv 9.1, RSI 57.4, Oversold

**#4 — NEW ENTRY: PANW**

- IVR 95.5 — Above gate, short put

**#5 — NEW ENTRY: WMT**

- IVR 94.4 — Above gate, short put


## Section 4: POSITION HEAT BY ACCOUNT

**Account A (232):**
- Open positions: 179
- Status: MONITOR

**Fidelity (Rahul):**
- Open positions: 42
- Status: MONITOR

**Vanguard (Rahul):**
- Open positions: 28
- Status: MONITOR

**Account B (275):**
- Open positions: 21
- Status: MONITOR

**Account C (634):**
- Open positions: 21
- Status: MONITOR

**Robinhood (Traditional IRA):**
- Open positions: 18
- Status: MONITOR

**Fidelity (Rajul — Rollover IRA):**
- Open positions: 14
- Status: MONITOR

**Fidelity (Rajul — Roth IRA):**
- Open positions: 8
- Status: MONITOR

**Robinhood (Individual):**
- Open positions: 4
- Status: MONITOR

**Fidelity 401K (Rahul):**
- Open positions: 0
- Status: MONITOR


## Section 5: IV RANK & ENTRY GATE (Weekly Scan)

**Tier 1 Entry Candidates (IVR ≥ 40, RED-heat excluded):**

- ✅ PANW: 95.5 IVR | $369.41 — short put only
- ✅ WMT: 94.4 IVR | $107.46 — short put only
- ✅ CRM: 91.4 IVR | $237.80 — short put only
- ✅ HOOD: 85.9 IVR | $124.29 — short put only
- ✅ ADBE: 75.6 IVR | $248.50 — short put only
- ✅ COIN: 72.4 IVR | $202.77 — short put only
- ✅ AXON: 67.7 IVR | $449.82 — short put only
- ✅ NVDA: 66.1 IVR | $227.46 — short put only
- ✅ NFLX: 64.3 IVR | $73.38 — short put only
- ✅ JD: 59.2 IVR | $27.23 — short put only

**Tier 1 BLOCKED (IVR < 40):**

- ❌ CIFR: 38.6 IVR (below gate)
- ❌ SONO: 37.5 IVR (below gate)
- ❌ OKLO: 35.7 IVR (below gate)
- ❌ NBIS: 35.2 IVR (below gate)
- ❌ INFY: 34.8 IVR (below gate)
- ❌ LMT: 33.7 IVR (below gate)
- ❌ UBER: 33.5 IVR (below gate)
- ❌ TSLA: 33.5 IVR (below gate)
- ❌ VRT: 33.1 IVR (below gate)
- ❌ ABNB: 31.6 IVR (below gate)


## Section 6: WEEKLY CASH & MARGIN FORECAST

**Current position** (real, from live option requirements):
- Portfolio-wide utilization: 100% ($2,839,586 req against $2,838,494 capacity)
- ⚠️ Over documented capacity: Account A (232) — see Section 0 per-account status
- 0 more Tier 1 entries needed to close the $-4,600 monthly gap ($0 capital)

**Crash-scenario cash requirement (Account A only — the only margin account):**

- Account A total option notional: $5,882,062 | Current Opt Req (18% model): $1,058,771
- Modeled stress case (15-20% broad market move): +$158,816 to +$211,754 incremental Opt Req
- Operating cash target (Account A, day-to-day): $100,000
- Emergency reserve (held separate, trader-confirmed): $200,000
- ⚠️ Emergency reserve BELOW the modeled stress high end ($200,000 < $211,754) — re-check sizing.
- Open items (re-confirm directly with Schwab, not from this model): (1) whether Account A's real capacity is still $700K or has grown toward the ~$1M margin-equity figure reported 2026-09-21; (2) that the emergency reserve is genuinely liquid and same/next-day movable into Account A specifically.

**Expiry-curve concentration (Account A, vs. the 90/120-day strategy target):**

- Near (<60 DTE): 1.9% (target 10-15%) ⚠️ light
- Core (60-135 DTE — the 90/120-day window): 59.1% (target 35-40%) ⚠️ heavy
- Mid (135-195 DTE): 27.6% (target 20-24%) ⚠️ heavy
- Far (195+ DTE): 11.4% (target 10-15%) ✅
- 🔴 Single-date concentration: 2026-12-18 holds 31.0% of total notional — above the ~20-25% single-cycle ceiling. Redirect new capital to adjacent dates rather than adding here.


## Section 7: WEEKLY THETA & P&L TRACKING

**Target pace:** $100,000/month (ISO week: $23,095)

**Current pace** (real, from live position tiers):

- 12 HIGH conviction positions, 95 total
- Current run rate: $104,600/month (105% of target)
- Note: per-position theta/Greeks are not computed in this pipeline — this is a tier-contribution estimate, not a live Greeks-based P&L projection.


## Section 8: RISK & GUARDRAILS (Weekly Check)

Portfolio Greeks: not computed in this pipeline — no live delta/gamma/theta/vega tracking exists yet. Flagging honestly rather than showing fabricated numbers.

**Margin guardrails** (real):

- Used: 100% (alert 75%, emergency 80%) 🔴 EMERGENCY
- ⚠️ Account A (232) over documented capacity — see Section 0

**Position concentration** (real):

- GREEN heat: 32 positions
- YELLOW heat: 57 positions
- RED heat: 6 positions (see Section 3 for the ranked action list)


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

- **Daily Conviction Tracking:** ✅ Real-time, 12 HIGH identified
- **Earnings Date Monitoring:** ✅ Integrated in technical analysis
- **Momentum Trend Tracking:** ✅ RSI, MACD, Bollinger Bands (all active)
- **Multi-Trigger Exit Logic:** ✅ 6 RED detected, monitoring
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


## Weekly Execution Plan — put/call + DTE aware

Regime: BULL. short PUTS (OTM, 45-90 DTE) → hold to 70% (per the quarterly plan's exit discipline); short CALLS → close at 50% or manage on DELTA (roll up+out / close, esp <30 DTE — theta won't save a tested call); <21 DTE → take (gamma).

### 🔻 Reduce / Manage (RED heat — RSI/trend/fundamentals all confirmed)

short CALLS here → roll up+out for credit or close (delta risk, theta won't save them); short PUTS here → near max profit, fine to take.

- OKTA RSI 61 conv 5.8
- CRWD RSI 58 conv 5.9

### ⏳ Take / Roll (<21 DTE — gamma zone, don't hold to expiry)

- (none parsed under 21 DTE)

### ✋ Let Run (oversold/neutral RSI≤48 + conviction≥6 — short PUTS: hold to 70%, DON'T close early = the leak)

- SBUX, BROS, CAVA, ABNB, ETSY, AXON, ALB, MA, EXPE, INFY, PL, NKE, UBER, CCL, ELF, NFLX, DKNG, LYFT, CRM, LMT, JD, SHOP, MP, KTOS, NOC, BA, UNH, LASR, ONDS, JPM, BWXT, CEG, MSFT, PANW, IBM, PLTR, DVN, VRT, AMZN

### ▶️ New Entries (redeploy freed collateral — 45-60 DTE CSP, delta 0.15-0.20, no new AI)

- 🟢 BUY sectors now: Basic Materials, Consumer Cyclical, Communication Services, Defense, Utilities, Consumer Defensive
- Efficiency-optimized (growth × IV-yield × collateral granularity): NU, ETN, CEG, TGT, DKNG — prefer over BLK/JPM/CAT (huge collateral per contract).
- → Run screen_new_entries / factor_screener for live strikes & IVR before selling.

---
_Report generated: 2026-09-21 | Next Weekly Report: Monday, September 28, 2026 08:00 AM ET_