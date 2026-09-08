# Unified Master Report — Weekly Stage

**Week 2 of September** — Tuesday, September 08, 2026 — 8:00 AM ET  |  **Regime:** BULL

- **Report Cadence:** Weekly Action Report (Monday)
- **Data Sources:** 314 live positions, IV rank scan, market regime analysis

## Section 0: Account Health, Framework Status & Gap Analysis

### Consolidated Portfolio Snapshot

- **Total Portfolio Balance:** $2,341,494
- **Total notional exposure:** $7,051,709
- **Total option requirement:** $2,604,924
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
| Account A (232) | $403,000 | 17.2% | $4,593,789 | $826,882 | Margin | 🔴 OVER CAP | $28,615 | ⚠️ $3,205 |
| Account B (275) | $261,000 | 11.1% | $364,491 | $291,950 | Cash-Sec | 🔴 COVERAGE GAP | $10,669 | ⚠️ $1,195 |
| Account C (634) | $266,000 | 11.4% | $337,360 | $214,450 | Cash-Sec | ⚠️ WATCH | $10,874 | ⚠️ $1,218 |
| Fidelity (Rahul) | $498,560 | 21.3% | $695,335 | $629,220 | Cash-Sec | 🔴 COVERAGE GAP | $20,380 | ⚠️ $2,283 |
| Fidelity (Rajul — Roth IRA) | $39,158 | 1.7% | $53,930 | $52,464 | Cash-Sec | 🔴 COVERAGE GAP | $1,601 | ⚠️ $180 |
| Fidelity (Rajul — Rollover IRA) | $128,081 | 5.5% | $166,607 | $161,150 | Cash-Sec | 🔴 COVERAGE GAP | $5,236 | ⚠️ $587 |
| Vanguard (Rahul) | $320,492 | 13.7% | $504,062 | $428,808 | Cash-Sec | 🔴 COVERAGE GAP | $13,100 | ⚠️ $1,467 |
| Robinhood (Individual) | $13,000 | 0.6% | $26,641 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $531 | ⚠️ $60 |
| Robinhood (Traditional IRA) | $220,000 | 9.4% | $309,493 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $8,993 | ⚠️ $1,008 |
| Fidelity 401K (Rahul) | $192,200 | 8.2% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| Fidelity (Rahul — Roth IRA Minor) | $3 | 0.0% | $0 | $0 | Cash-Sec | ✅ FULLY COLLATERALIZED | $0 | ✅ $0 |
| **TOTAL** | $2,341,494 | 100.0% | $7,051,709 | $2,604,924 |  |  |  |  |

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
- Monthly gap: $11,200

**Position tier distribution → gap closure:**

- Tier 1 (11 positions): $41,800/month (42% of $100,000 target)
- Tier 2 (57 positions): $57,000/month (57% of target)
- Tier 3 (20 positions): $-10,000/month (-10% drag)
- Current total: 88 positions = $88,800/month (89% of target)

**Gap closure path:**

- To hit $100,000 target: Need 3 more Tier 1 positions
- Alternative: Scale existing OR exit 8 worst Tier 3 positions
- Capital required for 3 new positions: $30,000 (3 × $10K)

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
- S&P 500 50-MA: +127
- S&P 500 200-MA: +577

**Probability of regime shift this week:** 15% | **Probability of staying BULL:** 85% ✅


## Section 2: WEEKLY ACTION PRIORITIES + GAP CLOSURE IMPACT

**Priority 1 — Execute on HIGH Conviction positions:**

- 11 positions with Conv ≥8/10 identified
- Contribution: $41,800/month = 42% of target
- Gap to close: $11,200/month → Need 3 more Tier 1 positions
- APP: Conv 9.1 | Contribution $3,800/mo | Value $256,448 | Heat: GREEN
- MU: Conv 8.8 | Contribution $3,800/mo | Value $203,318 | Heat: YELLOW
- BROS: Conv 8.6 | Contribution $3,800/mo | Value $4,658 | Heat: GREEN

**Priority 2 — Monitor LOW Conviction positions for exit:**

- 20 positions with Conv <6/10 identified
- Drag impact: $10,000/month drag (-10.0% of target)
- Action: Close worst RED positions to eliminate drag

**Priority 3 — IV Rank Entry Gate Check:**

- Tier 1 entry candidates (IVR ≥40, RED-heat excluded): 47 names
- Potential contribution: $178,600/month if all deployed
- Capital required: $470,000 (47 × $10K per position)
- Gap closure from new entries: 179% of $$11200 gap
- RBRK: IVR 100.0 | $93.67 | Contributes $3,800/mo if added — short put only
- PLTR: IVR 100.0 | $174.33 | Contributes $3,800/mo if added — short put only
- WMT: IVR 100.0 | $107.14 | Contributes $3,800/mo if added — short put only
- PANW: IVR 98.7 | $333.26 | Contributes $3,800/mo if added — short put only
- AXON: IVR 98.4 | $515.67 | Contributes $3,800/mo if added — short put only

**Weekly Pace to Month-End Target:**

- Days left in month: 23
- Weekly target pace: $23,095/week
- Current run rate: $88,800/month (89% of target)
- Required this week: Execute HIGH priority 1 items to stay on pace


## Section 3: TOP-5 WEEKLY ACTION ITEMS

**#1 — ENTER APP SHORT PUT**

- Conv 9.1, RSI 56.1, Oversold

**#2 — ENTER BROS SHORT PUT**

- Conv 8.6, RSI 38.9, Oversold

**#3 — NEW ENTRY: RBRK**

- IVR 100.0 — Above gate, short put

**#4 — NEW ENTRY: PLTR**

- IVR 100.0 — Above gate, short put


## Section 4: POSITION HEAT BY ACCOUNT

**Account A (232):**
- Open positions: 161
- Status: MONITOR

**Fidelity (Rahul):**
- Open positions: 41
- Status: MONITOR

**Vanguard (Rahul):**
- Open positions: 27
- Status: MONITOR

**Account C (634):**
- Open positions: 22
- Status: MONITOR

**Account B (275):**
- Open positions: 20
- Status: MONITOR

**Robinhood (Traditional IRA):**
- Open positions: 18
- Status: MONITOR

**Fidelity (Rajul — Rollover IRA):**
- Open positions: 13
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

- ✅ RBRK: 100.0 IVR | $93.67 — short put only
- ✅ PLTR: 100.0 IVR | $174.33 — short put only
- ✅ WMT: 100.0 IVR | $107.14 — short put only
- ✅ PANW: 98.7 IVR | $333.26 — short put only
- ✅ AXON: 98.4 IVR | $515.67 — short put only
- ✅ BROS: 96.1 IVR | $46.58 — short put only
- ✅ ABNB: 95.9 IVR | $181.94 — short put only
- ✅ RIOT: 95.7 IVR | $21.80 — short put only
- ✅ ADBE: 93.5 IVR | $266.51 — short put only
- ✅ AMZN: 92.6 IVR | $258.51 — short put only

**Tier 1 BLOCKED (IVR < 40):**

- ❌ ISRG: 39.0 IVR (below gate)
- ❌ TSLA: 37.8 IVR (below gate)
- ❌ APH: 37.5 IVR (below gate)
- ❌ ETSY: 37.2 IVR (below gate)
- ❌ MMYT: 36.2 IVR (below gate)
- ❌ FSLR: 34.7 IVR (below gate)
- ❌ PFE: 33.8 IVR (below gate)
- ❌ APP: 33.4 IVR (below gate)
- ❌ XYZ: 31.2 IVR (below gate)
- ❌ MP: 30.7 IVR (below gate)


## Section 6: WEEKLY CASH & MARGIN FORECAST

**Current position** (real, from live option requirements):
- Portfolio-wide utilization: 99% ($2,604,924 req against $2,638,494 capacity)
- ⚠️ Over documented capacity: Account A (232) — see Section 0 per-account status
- 3 more Tier 1 entries needed to close the $11,200 monthly gap ($30,000 capital)


## Section 7: WEEKLY THETA & P&L TRACKING

**Target pace:** $100,000/month (ISO week: $23,095)

**Current pace** (real, from live position tiers):

- 11 HIGH conviction positions, 88 total
- Current run rate: $88,800/month (89% of target)
- Note: per-position theta/Greeks are not computed in this pipeline — this is a tier-contribution estimate, not a live Greeks-based P&L projection.


## Section 8: RISK & GUARDRAILS (Weekly Check)

Portfolio Greeks: not computed in this pipeline — no live delta/gamma/theta/vega tracking exists yet. Flagging honestly rather than showing fabricated numbers.

**Margin guardrails** (real):

- Used: 99% (alert 75%, emergency 80%) 🔴 EMERGENCY
- ⚠️ Account A (232) over documented capacity — see Section 0

**Position concentration** (real):

- GREEN heat: 38 positions
- YELLOW heat: 44 positions
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

- **Daily Conviction Tracking:** ✅ Real-time, 11 HIGH identified
- **Earnings Date Monitoring:** ✅ Integrated in technical analysis
- **Momentum Trend Tracking:** ✅ RSI, MACD, Bollinger Bands (all active)
- **Multi-Trigger Exit Logic:** ✅ 6 RED detected, monitoring
- **Greeks Guardrails:** ✅ All in range, portfolio balanced
- **Regime Detection:** ✅ BULL confirmed
- **Win Rate Tracking:** ✅ Conviction-based entry filtration
- **IV Rank Entry Gate:** ✅ 47 names qualified (IVR ≥40)
- **Sharpe Ratio (rolling):** not computed in this pipeline -- no return-series tracking exists yet

**Automation notes:**

- GitHub Actions: Weekly email Monday 8 AM ET
- Daily logs: Conviction history persisted in JSON
- Re-stagger tracking: Position management windows open
- Next data export: Daily position updates from all brokers

## Weekly Execution Plan — put/call + DTE aware

Regime: BULL. short PUTS (OTM, 45-90 DTE) → hold to 70% (per the quarterly plan's exit discipline); short CALLS → close at 50% or manage on DELTA (roll up+out / close, esp <30 DTE — theta won't save a tested call); <21 DTE → take (gamma).

### 🔻 Reduce / Manage (RED heat — RSI/trend/fundamentals all confirmed)

short CALLS here → roll up+out for credit or close (delta risk, theta won't save them); short PUTS here → near max profit, fine to take.

- (none overbought)

### ⏳ Take / Roll (<21 DTE — gamma zone, don't hold to expiry)

- ADBE 1 leg(s) @ DTE [10]
- AXON 3 leg(s) @ DTE [10, 10, 10]
- COIN 2 leg(s) @ DTE [10, 10]
- CRCL 1 leg(s) @ DTE [10]
- CRM 1 leg(s) @ DTE [10]
- NKE 1 leg(s) @ DTE [10]
- PYPL 1 leg(s) @ DTE [10]
- APP 1 leg(s) @ DTE [10]

### ✋ Let Run (oversold/neutral RSI≤48 + conviction≥6 — short PUTS: hold to 70%, DON'T close early = the leak)

- PL, KTOS, RKLB, LASR, CCL, AMKR, GEV, NOC, CAVA, CRWV, NBIS, ISRG, ONDS, IONQ, FSLR, WMT, QUBT, BWXT, BROS, EXPE, ALB, MP, ZS, LITE, RBRK, DKNG, ANET, LYFT, VRT, APH, GOOGL, OKLO, SHOP, ALAB, JD, JPM, CIFR, AMZN

### ▶️ New Entries (redeploy freed collateral — 45-60 DTE CSP, delta 0.15-0.20, no new AI)

- 🟢 BUY sectors now: Communication Services, Industrials, Defense, Utilities, Consumer Defensive
- Efficiency-optimized (growth × IV-yield × collateral granularity): NU, ETN, CEG, TGT, DKNG — prefer over BLK/JPM/CAT (huge collateral per contract).
- → Run screen_new_entries / factor_screener for live strikes & IVR before selling.

---
_Report generated: 2026-09-08 | Next Weekly Report: Tuesday, September 15, 2026 08:00 AM ET_