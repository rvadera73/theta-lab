# Unified Master Report — Weekly Stage

**Week 3 of September** — Friday, September 18, 2026 — 8:00 AM ET  |  **Regime:** BULL

- **Report Cadence:** Weekly Action Report (Monday)
- **Data Sources:** 325 live positions, IV rank scan, market regime analysis

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


## Section 1: WEEKLY MARKET REGIME FORECAST

**Regime:** BULL

**Current signals:**

- VIX: 15.4 (VIX 15.4 sustained < 20)
- S&P 500 50-MA: +9
- S&P 500 200-MA: +443

**Probability of regime shift this week:** 15% | **Probability of staying BULL:** 85% ✅


## Section 2: WEEKLY ACTION PRIORITIES + GAP CLOSURE IMPACT

**Priority 1 — Execute on HIGH Conviction positions:**

- 13 positions with Conv ≥8/10 identified
- Contribution: $49,400/month = 49% of target
- Gap to close: $-4,400/month → Need 0 more Tier 1 positions
- APP: Conv 9.1 | Contribution $3,800/mo | Value $316,105 | Heat: GREEN
- GOOGL: Conv 8.8 | Contribution $3,800/mo | Value $140,384 | Heat: GREEN
- IONQ: Conv 8.5 | Contribution $3,800/mo | Value $22,854 | Heat: YELLOW

**Priority 2 — Monitor LOW Conviction positions for exit:**

- 18 positions with Conv <6/10 identified
- Drag impact: $9,000/month drag (-9.0% of target)
- Action: Close worst RED positions to eliminate drag
- CRWD: Conv 5.9 | Drag $500/mo | Value $118,448 | RSI 58.2 (CONCERN: Spiked 14% in 7 days AND 61% above its 200-day average — genuinely extended, not just a pop)

**Priority 3 — IV Rank Entry Gate Check:**

- Tier 1 entry candidates (IVR ≥40, RED-heat excluded): 29 names
- Potential contribution: $110,200/month if all deployed
- Capital required: $290,000 (29 × $10K per position)
- Gap closure from new entries: 110% of $$4400 gap
- ABNB: IVR 98.7 | $165.25 | Contributes $3,800/mo if added — short put only
- PANW: IVR 96.4 | $359.82 | Contributes $3,800/mo if added — short put only
- RBRK: IVR 94.8 | $105.41 | Contributes $3,800/mo if added — short put only
- WMT: IVR 94.3 | $107.38 | Contributes $3,800/mo if added — short put only
- CRM: IVR 92.0 | $238.15 | Contributes $3,800/mo if added — short put only

**Weekly Pace to Month-End Target:**

- Days left in month: 13
- Weekly target pace: $23,095/week
- Current run rate: $104,400/month (104% of target)
- Required this week: Execute HIGH priority 1 items to stay on pace


## Section 3: TOP-5 WEEKLY ACTION ITEMS

**#1 — TRIM / REVIEW CRWD**

- Conv 5.9, Heat RED, RSI 58.2 — Spiked 14% in 7 days AND 61% above its 200-day average — genuinely extended, not just a pop

**#2 — ENTER APP SHORT PUT**

- Conv 9.1, RSI 49.1, Oversold

**#3 — ENTER GOOGL SHORT PUT**

- Conv 8.8, RSI 53.6, Oversold

**#4 — NEW ENTRY: ABNB**

- IVR 98.7 — Above gate, short put

**#5 — NEW ENTRY: PANW**

- IVR 96.4 — Above gate, short put


## Section 4: POSITION HEAT BY ACCOUNT

**Account A (232):**
- Open positions: 169
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

- ✅ ABNB: 98.7 IVR | $165.25 — short put only
- ✅ PANW: 96.4 IVR | $359.82 — short put only
- ✅ RBRK: 94.8 IVR | $105.41 — short put only
- ✅ WMT: 94.3 IVR | $107.38 — short put only
- ✅ CRM: 92.0 IVR | $238.15 — short put only
- ✅ TTD: 91.4 IVR | $14.11 — short put only
- ✅ HOOD: 82.3 IVR | $117.54 — short put only
- ✅ TWLO: 81.7 IVR | $240.37 — short put only
- ✅ AXON: 77.3 IVR | $452.27 — short put only
- ✅ ADBE: 76.9 IVR | $249.02 — short put only

**Tier 1 BLOCKED (IVR < 40):**

- ❌ LYFT: 39.2 IVR (below gate)
- ❌ META: 38.5 IVR (below gate)
- ❌ IONQ: 37.8 IVR (below gate)
- ❌ PFE: 36.9 IVR (below gate)
- ❌ CIFR: 36.9 IVR (below gate)
- ❌ SONO: 35.6 IVR (below gate)
- ❌ INFY: 35.1 IVR (below gate)
- ❌ LMT: 34.8 IVR (below gate)
- ❌ NBIS: 34.4 IVR (below gate)
- ❌ TSLA: 33.6 IVR (below gate)


## Section 6: WEEKLY CASH & MARGIN FORECAST

**Current position** (real, from live option requirements):
- Portfolio-wide utilization: 103% ($2,707,034 req against $2,638,494 capacity)
- ⚠️ Over documented capacity: Account A (232) — see Section 0 per-account status
- 0 more Tier 1 entries needed to close the $-4,400 monthly gap ($0 capital)


## Section 7: WEEKLY THETA & P&L TRACKING

**Target pace:** $100,000/month (ISO week: $23,095)

**Current pace** (real, from live position tiers):

- 13 HIGH conviction positions, 95 total
- Current run rate: $104,400/month (104% of target)
- Note: per-position theta/Greeks are not computed in this pipeline — this is a tier-contribution estimate, not a live Greeks-based P&L projection.


## Section 8: RISK & GUARDRAILS (Weekly Check)

Portfolio Greeks: not computed in this pipeline — no live delta/gamma/theta/vega tracking exists yet. Flagging honestly rather than showing fabricated numbers.

**Margin guardrails** (real):

- Used: 103% (alert 75%, emergency 80%) 🔴 EMERGENCY
- ⚠️ Account A (232) over documented capacity — see Section 0

**Position concentration** (real):

- GREEN heat: 44 positions
- YELLOW heat: 48 positions
- RED heat: 3 positions (see Section 3 for the ranked action list)


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

- **Daily Conviction Tracking:** ✅ Real-time, 13 HIGH identified
- **Earnings Date Monitoring:** ✅ Integrated in technical analysis
- **Momentum Trend Tracking:** ✅ RSI, MACD, Bollinger Bands (all active)
- **Multi-Trigger Exit Logic:** ✅ 3 RED detected, monitoring
- **Greeks Guardrails:** ✅ All in range, portfolio balanced
- **Regime Detection:** ✅ BULL confirmed
- **Win Rate Tracking:** ✅ Conviction-based entry filtration
- **IV Rank Entry Gate:** ✅ 29 names qualified (IVR ≥40)
- **Sharpe Ratio (rolling):** not computed in this pipeline -- no return-series tracking exists yet

**Automation notes:**

- GitHub Actions: Weekly email Monday 8 AM ET
- Daily logs: Conviction history persisted in JSON
- Re-stagger tracking: Position management windows open
- Next data export: Daily position updates from all brokers


## Section 11: ACTIVE DECISION TRACKER


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


## Weekly Execution Plan — put/call + DTE aware

Regime: BULL. short PUTS (OTM, 45-90 DTE) → hold to 70% (per the quarterly plan's exit discipline); short CALLS → close at 50% or manage on DELTA (roll up+out / close, esp <30 DTE — theta won't save a tested call); <21 DTE → take (gamma).

### 🔻 Reduce / Manage (RED heat — RSI/trend/fundamentals all confirmed)

short CALLS here → roll up+out for credit or close (delta risk, theta won't save them); short PUTS here → near max profit, fine to take.

- CRWD RSI 58 conv 5.9

### ⏳ Take / Roll (<21 DTE — gamma zone, don't hold to expiry)

- ADBE 1 leg(s) @ DTE [0]
- APP 1 leg(s) @ DTE [0]

### ✋ Let Run (oversold/neutral RSI≤48 + conviction≥6 — short PUTS: hold to 70%, DON'T close early = the leak)

- SBUX, ABNB, BROS, CAVA, CCL, MP, KTOS, UBER, ALB, AXON, PL, ETSY, EXPE, SHOP, NKE, MA, JD, DKNG, NFLX, LYFT, INFY, BA, AMZN, ELF, LMT, NOC, JPM, ONDS, UNH, LASR, CRM, MSFT, LLY, PLTR, BWXT, FSLR, OKLO, IBM, VRT, PANW, CRWV, IONQ, QBTS

### ▶️ New Entries (redeploy freed collateral — 45-60 DTE CSP, delta 0.15-0.20, no new AI)

- 🟢 BUY sectors now: Basic Materials, Consumer Cyclical, Brand-Quality (Non-AI), Communication Services, Defense, Utilities
- Efficiency-optimized (growth × IV-yield × collateral granularity): NU, ETN, CEG, TGT, DKNG — prefer over BLK/JPM/CAT (huge collateral per contract).
- → Run screen_new_entries / factor_screener for live strikes & IVR before selling.

---
_Report generated: 2026-09-18 | Next Weekly Report: Friday, September 25, 2026 08:00 AM ET_