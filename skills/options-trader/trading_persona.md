# Trading Persona — Rahul Vadera

**Generated:** 2026-04-25
**Last Updated:** 2026-04-25 (session 3 — research model, exit criteria, profit targets incorporated)
**Source:** Schwab brokerage statements (Jan–Mar 2026), 1099 (2025), portfolio watchlists, trader input
**Status:** ACTIVE — use this file as the guardrail for all trade decisions

---

## Account Map

| Account | Holder | Type | Account # | Size (Mar 2026) | Return Target |
|---------|--------|------|-----------|-----------------|---------------|
| Account A | Rahul Vadera | Schwab One® (Margin) | ****-*232 | ~$421K total value | 20% annualized |
| Account B | Pinky Vadera | Contributory IRA | ****-*275 | ~$233K total value | 12% annualized |

**Account B authorization:** Confirmed. Rahul manages Pinky's IRA with full consent.
**Account B options level:** Level 2 confirmed active (CSPs + CCs). No margin, no naked positions.

---

## Trader Profile: Core Principles

1. **Not married to any stock** — positions are vehicles for premium collection, not conviction bets
2. **Goal is to never own stock** — stock ownership is an accident of assignment, not strategic intent
3. **If assigned, use stock as a commodity** — sell CCs immediately, reduce cost basis, exit at first opportunity
4. **Short premium bias only** — sells options exclusively; has never bought options in 5 years
5. **Income-first mindset** — theta decay is the engine; directional bias is input, not thesis
6. **Loss minimization, not stop-loss** — does not use hard stops; manages losses through rolling, time, and premium collection
7. **Macro-regime-driven DTE** — selects expiration based on market environment, not fixed rules
8. **Fundamentals + macro instinct is the research engine** — does not use technical indicators; selects stocks through fundamental research and macro read
9. **Wants technical analysis as a supplemental layer** — acknowledged gap; skill should provide technical signals as additional input, not as primary driver

**Classification:** Fundamentals-Driven Macro Trader | Short Premium Execution | Instinct-Based with Systematic Gaps

---

## Stock Selection Model (Research Layer)

This is the layer I initially missed. Options execution sits on top of a deliberate, tiered research process.

### The Three Tiers

**Tier 1 — Established Growth + Stable (Core book)**
Large-cap, proven business model, high conviction, larger position size, longer DTE
> NVDA, META, AMZN, GOOGL, TSLA, TSM, AXON, ADBE, CRM, MSFT, NFLX, UBER

**Tier 2 — Emerging Proven (Building conviction)**
Business model proving out, growing confidence from prior bets, moderate size
> HOOD, CRWD, SHOP, ZS, ALAB, GEV, VST, EXPE, COIN, ABNB

**Tier 3 — New Growth / Unproven (Small exploratory bets)**
1 contract CSPs only, learning the company while earning premium, watching for graduation signals
> ASTS, RKLB, ACHR, QUBT, RGTI, IONQ, QBTS, IBIT, SMR, OKLO, CIFR, HUT

### Graduation Criteria (Tier 3 → Tier 2 → Tier 1)
- Accumulation of successful bets on the name (premium collected, no major drawdowns)
- Growing personal confidence in the business trajectory
- Evidence of execution: revenue growth, contract wins, product milestones, management credibility
- No binary/governance risk flags
- **Not metric-driven** — experience-based pattern recognition over time

### Exit Signals (Fundamental Flags — when to stop betting on a name)

These are the signals that trigger removal from the universe, based on observed exits:

| Signal Type | Examples | Action |
|-------------|----------|--------|
| Execution / governance risk | SMCI (accounting fraud, auditor resignation) | Exit immediately, no roll |
| Geopolitical / macro event on name | INMD (Israel conflict + weak guidance) | Exit, reassess after 1 quarter |
| Repeated negative signals / thesis erosion | MRNA (pipeline failures, continued misses), PYPL (turnaround stalled) | Reduce to Tier 3 or exit entirely |
| Management credibility breakdown | Any name with repeated guidance misses | Downgrade or exit |

**What does NOT trigger exit:** Stock price drop alone, short-term volatility, broad market selloff.
The thesis must break — not just the price.

---

## Tier Reclassification — By Profitability, Not IVR/Conviction Score

**Merged 2026-07-20** from `skills/trading_persona.md` (the long-running hand-maintained
persona doc — see the India section at the bottom of this file for how it and this
canonical file diverged, and why only the reusable frameworks below were merged in).

**Problem this fixes:** tiering positions by IVR/conviction alone ignores whether the
position is actually working. A tier should reflect real P&L, not just how the position
was scored at entry.

| Tier | Equity P&L | Option Strategy | Position Size |
|------|---|---|---|
| **Tier 1 (Profitable)** | +0% to +100% | Sell 1-3 contracts CSPs/CCs per underlying; ladder strikes | Full allocation: 3-5 contracts max |
| **Tier 2 (Breakeven)** | -10% to 0% | Sell CSPs only; close existing short calls; hold for assignment | Reduced: 1-2 contracts max |
| **Tier 3 (Underwater -25%+)** | -25% to -100% | Exit equity OR close all options; do NOT scale options | Minimal: 1 contract exploratory only; do NOT add |

**Professional reasoning (not emotional):** a position deep underwater on the equity leg
is a broken position, not a "sell more premium to average down" opportunity. Scaling
options on a name to offset an equity loss locks in the loss while compounding risk.
Right approach: exit the losing equity, close the associated losing options, redeploy
into positions with positive equity P&L. This is a **principle**, not a one-time snapshot
— re-apply it to whatever the current live P&L shows, not the dated example numbers this
was originally written against.

---

## Professional Technical Decision Framework — 5-Gate Entry Analysis

**Merged 2026-07-20** from `skills/trading_persona.md`. Supplemental to fundamentals-first
research (per Trader Profile principle 8-9) — use to size/time an entry the fundamental
thesis has already justified, not to originate one.

### Gate 1: IV Rank (Mechanical Filter) — PRIMARY objective gate, all positions pass this first

| IVR | Status | Action |
|-----|--------|--------|
| **≥60%** | ✅ PASS | Proceed to Gates 2-5 |
| **40-59%** | ✅ PASS | Proceed to Gates 2-5 |
| **<40%** | ❌ BLOCK | Do NOT proceed; insufficient premium density |

If IVR <40, position is automatically blocked regardless of Gates 2-5.

### Gates 2-5: Red & Green Flag Analysis (after passing Gate 1)

**Gate 2 — Technical Strength:** Green = price above 50-day MA, RSI 40-60, 3+ day uptrend.
Yellow = price near 50-day MA (±2%), RSI 30-40/60-70, choppy. Red = price below 50-day MA
3+ days, RSI <30 or >75, 5+ day downtrend.

**Gate 3 — Momentum & Relative Strength:** Green = +20% to +100% recent, beating sector,
earnings beat + guidance raise. Yellow = 0-20% recent, in-line with sector. Red = -10% to
-50% recent, trailing sector by 10%+, guidance cut/miss.

**Gate 4 — Volatility Quality & Premium Density:** Green = IV percentile >70%, IVR >70%
(peak but not crush-risk), premium >20% capital/45-DTE. Yellow = IV percentile 50-70%, IVR
60-70%, premium 15-20%. Red = IV percentile <50%, IVR >80% (imminent crush risk), premium
<10% (weak).

**Gate 5 — Risk/Reward & Greeks:** Green = delta 0.15-0.20 (80-85% PoP), theta 3-5% daily
decay, DTE 45-60, Tier 1/2 conviction. Yellow = delta 0.10-0.15 or 0.20-0.25, DTE 30-45 or
60-90, Tier 2 mixed. Red = delta <0.10 or >0.30, DTE <30 or >180 (inefficient capital),
Tier 3 or thesis broken.

### Final Recommendation Logic (Gates 1-5 Combined)

| Gate 1 | Gates 2-5 | Decision | Action |
|---|---|---|---|
| PASS (IVR ≥40) | 3+ GREEN | ✅ ENTER FULL SIZE | Deploy full allocation |
| PASS (IVR ≥40) | 2 GREEN, 1-2 YELLOW | 🟡 CONDITIONAL | Reduce size 50%; wait for confirmation |
| PASS (IVR ≥40) | 1+ RED | ❌ DEFER/SKIP | Wait for conditions to improve |
| BLOCK (IVR <40) | anything | ❌ HARD BLOCK | Do not enter; exit any existing position |

---

## Macro Risk Framework — 7-Layer Crash Detection

**Merged 2026-07-20** from `skills/trading_persona.md`. Ties macro risk signals to
actionable position-reduction decisions rather than "market feels risky" intuition.

### The 7 Layers

1. **Breadth (% S&P 500 above 50-day MA):** GREEN >60% | YELLOW 50-60% | RED <50%
2. **Advance-Decline Ratio:** GREEN >1.0 | YELLOW 0.8-1.0 | RED <0.8
3. **VIX Term Structure:** GREEN contango (normal) | YELLOW flat | RED backwardation
4. **Credit Spreads (HY OAS):** GREEN <400bps | YELLOW 400-450bps | RED >450bps
5. **Put/Call Ratio:** GREEN <1.0 | YELLOW 1.0-1.2 | RED >1.2
6. **Yield Curve (10Y-2Y):** GREEN >0.5% | YELLOW 0.1-0.5% | RED <0.1% (inverted)
7. **Earnings Quality (qualitative):** guidance beats/misses, revenue realization, management credibility

### Probability Model → Staged Response

Base rate ~6% monthly crash probability; each RED signal adds +15% to 30-day probability,
each YELLOW adds +5%.

| 30-Day Prob | Stage | Action |
|---|---|---|
| <20% | GREEN | Proceed with full sizing |
| 20-40% | YELLOW-1 | Close 20% of lowest-conviction positions (Tier 3 first, conviction <6/10); no rolling, just exit; cash 10%→15% |
| 40-60% | YELLOW-2 | Close all overbought Tier 1/2 (RSI >70); reduce major positions to 75% size; new entries defensive-sector only; cash 10%→20-25% |
| 60-70% | RED-Emerging | Close 50% of gross exposure; emergency protocol |
| >70% | RED-Critical | 70% cash, 30% defensive only; close ALL naked calls or hedge with long puts |

**Replaces "I feel like the market might crash, let me close 30%" with a specific,
signal-driven stage and a matching playbook** — same principle as the India regime
detector (`detect_india_regime()`) added this session: compute the signal, don't guess it.

---

---

## Strategy Architecture (Confirmed by Trader)

### Account A (232 — Rahul, Margin) — Short Strangle Engine
**Key insight confirmed:** Account A is NOT just covered calls. It runs **short strangles** — simultaneously selling both puts AND calls on the same underlying. The naked calls are hedged by the short puts (and vice versa), collecting premium on both sides.

- Where stock is owned: Covered calls against long equity (traditional CC leg)
- Where stock is NOT owned: Naked calls sold alongside cash-secured puts = short strangle
- This explains the $402K unrealized options liability — short strangles on volatile names (AXON, MRNA, APP) with stocks moving significantly
- Margin account enables naked call positions that Account B cannot replicate

**Risk characteristic:** Short strangle exposure means unlimited upside risk on calls AND downside risk on puts. The "hedge" is that premium collected on both sides widens the break-even range.

### Account B (275 — Pinky, IRA) — Pure Wheel
- Sells CSPs only (no naked calls, no margin)
- Accepts assignment when thesis intact; immediately sells CCs to reduce cost basis
- Exits stock position via CC assignment or buyback when profitable
- 12% annualized target is achievable with pure CSP/CC wheel in this account size

---

## Macro Sector Thesis (as of Apr 2026)

This is the fundamental research layer that drives stock universe selection. Sectors are not equal — within each sector, the trader applies a **pick-and-shovel filter**: prefer enabling infrastructure over direct plays.

### Active Sector Views

**AI — Pick and Shovel Only**
- Conviction: HIGH. But selective — NOT betting on AI model companies or data center operators directly
- "Pick and shovel" preference: companies enabling AI (connectivity chips, cybersecurity, power infrastructure, AI-powered software tools)
- Semis: Cautious — "probably behind" (NVDA has run; TSM still valid as foundry pick/shovel)
- Data centers: Skeptical on direct plays (operators like APLD may underperform vs enablers)
- **Sweet spot:** ALAB (AI optical connectivity), AXON (AI-powered public safety), CRWD/OKTA/ZS (AI security infrastructure), GEV/VST (AI power infrastructure)

**Defense — Bullish**
- Conviction: HIGH for next 12 months
- Geopolitical tailwinds, defense budget expansion
- Prefers defense-tech crossover (AXON), aerospace (RTX), rare earth supply chain (MP)
- Space defense overlap: ASTS, RKLB qualify here as dual-use

**Healthcare — Bullish**
- Conviction: MEDIUM-HIGH for next 12 months
- Pharma: selectively bullish (MRK, ABBV — dividend + pipeline); cautious on weight-loss narrative (NVO ITM position reflects this)
- MedTech/diagnostics: NTRA (genomics), GEHC (imaging)
- Avoids pure biotech speculation

**Space — Emerging, Building Conviction**
- Conviction: MEDIUM, actively increasing scrutiny
- Transition from Tier 3 toward Tier 2 for proven names
- Commercial launch (RKLB), direct-to-satellite mobile (ASTS), eVTOL adjacent (ACHR, JOBY)
- Nuclear power for space/defense adjacent: OKLO, SMR
- "Looking very seriously" = increased research, not yet full conviction

**Utilities — Pick and Shovel, Not Original Utilities**
- Does NOT favor traditional utility companies (NEE, Duke) for this cycle
- Favors power enablers: GEV (turbines/grid for AI data centers), VST (competitive power gen)
- Nuclear new-build: SMR, OKLO as emerging speculative plays

**Crypto — Bullish, High Conviction**
- Confirmed high conviction on crypto for next 6-12 months
- Post-halving cycle + institutional adoption + regulatory tailwinds
- Best expressions: COIN (exchange, direct revenue play), HOOD (crypto + retail fintech), IBIT (cleanest BTC exposure for IRA CSPs), HUT/CIFR/RIOT (Tier 3 high-beta miners)
- Trigger to scale: Bitcoin sustained above $100K = add CSPs on COIN and HOOD

**Value Opportunism — Jumps When Seen**
- Restaurants/Consumer: CCL (cruise recovery), CAVA, BROS — jumped in on recent value dip
- International ETFs: EWZ (Brazil), EWY (South Korea) — emerging market value when dislocated
- India financials: HDB, IBN — long-term EM growth at reasonable premium
- China e-commerce: JD, BABA — value plays when sentiment is negative

### The Pick-and-Shovel Filter (Apply to Any New Sector)

When evaluating a new trend, ask:
1. Who sells the picks and shovels to the gold rush participants?
2. Who enables the trend vs who is a direct commodity participant?
3. Which enabling companies have pricing power and recurring revenue?

> Examples: AI gold rush → ALAB (connectivity), not data center operators
> Utility AI demand → GEV (turbines), not NEE (regulated utility)
> Space race → RKLB (launch infrastructure), not satellite operators

---

## Current Market Regime (Trader View — as of Apr 2026)

**Regime:** Bear to Sideways
**Duration:** ~6 months out (through Oct/Nov 2026)
**Implication for new positions:** NO new sell entries until regime shifts to bullish

### Regime-Driven Behavior Rules

| Regime | New Entries | DTE Target | Profit Take | Strategy |
|--------|------------|------------|-------------|----------|
| Bear/Sideways (current) | None — reducing existing | N/A | 40-60% of max premium | Let decay work; close winners early; roll losers |
| Transition (watch signals) | Selective, small size | 45-90 DTE | 50-60% of max premium | Restart with Tier 1 universe only |
| Bull (2023-2025 style) | Active | 3-12 months | 70% of max premium | Full strangle + wheel deployment |

**Regime shift signals to watch:**
- VIX sustained below 20 for 10+ days
- S&P 500 reclaims 50-day and 200-day MA on volume
- Put/Call ratio normalizing below 0.8

---

## Open ITM Position Plans (Trader Confirmed)

| Position | Account | Status | Trader Plan |
|----------|---------|--------|-------------|
| MRNA calls ($26/$35) | A (232) | Deep ITM — **actively exiting** | Natural CC assignment in progress. COMPLETE EXIT. Do not re-enter. |
| PYPL calls + stock | A (232) | **Thesis broken — minimize loss exit** | Fintech, not growth. Selling CCs aggressively to reduce cost basis. Exit fully when breakeven or near. Do not re-enter. |
| NVO put ($55) | B (275) | ITM; stock ~$44 range | Roll down to $45-47 while IV elevated. Natural exit cycle. |
| CRM put ($220) | B (275) | ITM; stock ~$178 | Conviction: stock returns to $280. Maximize CC premium while waiting. |
| CRWD put ($430) | B (275) | Near ATM; watch $440 | Monitor; roll if CRWD closes below $440 two consecutive days. |
| BA put ($190) | B (275) | Watch stock recovery | Standard wheel management. |

**General rule confirmed:** Do NOT force-close losers unless account cash flow is impaired.

### Permanent Exits (Do Not Re-Enter)

| Ticker | Reason | Status |
|--------|--------|--------|
| MRNA | Continued execution failures; pipeline misses; thesis broken | Exiting via natural CC assignment |
| PYPL | Fintech, not growth; losing competitive moat to Apple Pay/Stripe; no path to premium valuation | Minimize loss exit via CC; will not re-enter |
| SMCI | Governance fraud — immediate exit trigger | Already exited |
| INMD | Israel conflict + execution disappointment | Already exited |

---

## DTE Selection Logic (Regime-Driven)

```
IF regime == BEAR_SIDEWAYS:
    new_entries = FALSE
    existing_positions: let run, take profits at 50%+, roll losers to avoid assignment

IF regime == TRANSITIONING:
    new_entries = selective (core 10 universe only)
    dte_target = 45-90 days
    size = 50% of normal

IF regime == BULL:
    new_entries = active
    dte_target = 90-360 days (3-12 months)
    size = full per risk_params.yaml
```

---

## Stop-Loss Protocol (Confirmed)

**Hard automatic stops: NEVER**

The trader has not used a hard stop in 5 years of live trading. Loss management is done through:
- Rolling (extending DTE, adjusting strikes)
- Premium collection on both sides (strangle structure buffers drawdowns)
- Time — "the market always comes back to fair value on quality names"
- Cash flow management (if margin call risk emerges in Account A — only scenario for forced close)

**Skill behavior on losing positions:**
1. Flag any position where mark-to-market loss exceeds 2x premium received
2. Present roll options (same strike + later DTE, or lower/higher strike)
3. Ask trader for decision — NEVER auto-close
4. Exception: If Account A margin utilization exceeds 80%, escalate with urgency

---

## Performance Metrics (2026 YTD through Mar)

| Metric | Account A (232) | Account B (275) |
|--------|-----------------|-----------------|
| YTD Realized Gain (through Feb) | $58,974.91 | — |
| Jan 2026 Net | — | $1,192.10 |
| Mar 2026 Net | — | $4,113.06 |
| Unrealized Options Liability | $(402,318.98) | $(16,587.07) |
| Cash/Sweep Balance | $328,678 (Feb) | $272,932 (Mar) |
| Target annualized | 20% (~$84K/yr) | 12% (~$28K/yr) |

> Note: Account A's $59K in 2 months is ahead of the 20% pace. Current bear regime will slow
> new premium collection — the existing book must carry returns through Oct/Nov.

---

## Active Ticker Universe

### Account A — Core Holdings + Strangle Names
| Ticker | Strategy | Notes |
|--------|----------|-------|
| ADBE | CC + strangle | 4 active call strikes; most sophisticated position |
| AXON | CC + strangle | 3 CC strikes; high IV; deep ITM risk |
| PYPL | CC + strangle | 5 active call positions; most active name |
| OKTA | CC + strangle | 3 strikes laddered |
| CRM | CC + strangle | Long-term bull conviction ($280 target) |
| APP | CC + strangle | High-beta; aggressive |
| MRNA | CC (exiting) | Deep ITM; natural exit in 2-3 months |
| NFLX | CC | 2 contracts |
| NKE | CC | 1 contract |
| LYFT | CC | 4 contracts; recurring |
| JD | CC | 2 contracts |
| INMD | CC | 5 contracts; small-cap |
| ZBH | CC | 1 contract |

### Account B — Active Wheel Universe
| Tier | Tickers | Notes |
|------|---------|-------|
| Core (recurring) | HOOD, TSM, CRWD, GEV, AXON, UBER, BA, FSLR, NVO, CRM | High frequency, multiple rolls seen |
| Active (occasional) | ASTS, RKLB, ALAB, SHOP, ZS, VST, IONQ, ELF, ETSY | Medium frequency |
| Speculative (small size) | QUBT, RGTI, QBTS, ACHR, IBIT, EWZ, EWY | Cap at 10% of account B |

---

## Recommended Core Universe (Sector-Aligned)

Organized by macro thesis fit, not just activity frequency.

### Tier 1 — Core Book (Established Growth, High Conviction)

| Ticker | Sector Thesis | Account | Notes |
|--------|--------------|---------|-------|
| AXON | AI pick/shovel + Defense | A | AI-powered public safety; defense crossover; highest IV; most active |
| CRM | AI pick/shovel (enterprise) | A + B | Enterprise AI platform; $280 conviction; active in both accounts |
| ADBE | AI pick/shovel (creative) | A | AI-powered creative tools; 4-strike ladder; consistent premium |
| CRWD | AI pick/shovel (security) | B | Cybersecurity infrastructure; high IV; recurring |
| TSM | AI pick/shovel (foundry) | B | Semiconductor foundry; largest pick/shovel for all chip demand |
| OKTA | AI pick/shovel (identity) | A | Identity security for AI era; 3 CC positions |
| GEV | AI power pick/shovel | B | Grid/turbine infrastructure for AI data centers; large premium |

### Tier 2 — Emerging Conviction (Building Position)

| Ticker | Sector Thesis | Account | Notes |
|--------|--------------|---------|-------|
| HOOD | Fintech AI | B | Retail brokerage + crypto infrastructure; high IV |
| ALAB | AI connectivity pick/shovel | B | Optical interconnects for AI data centers; proving out |
| VST | AI power pick/shovel | B | Competitive power generation for data center demand |
| SHOP | AI commerce infrastructure | B | Emerging AI tools layer on commerce |
| ZS | AI security pick/shovel | B | Cloud security infrastructure |
| RTX | Defense | A | Aerospace + defense; premium name |
| NTRA | Healthcare / genomics | A | Genetic diagnostics; recurring revenue |

### Tier 3 — Speculative / Exploratory (1 contract max, watching)

| Ticker | Sector Thesis | Notes |
|--------|--------------|-------|
| ASTS | Space + Defense | Direct-to-satellite; dual-use potential; building conviction |
| RKLB | Space launch infrastructure | Pick/shovel for space economy |
| ACHR | eVTOL / Air mobility | Early; watching FAA certification progress |
| OKLO | Nuclear / Space power | Small modular reactor; long thesis |
| IONQ | Quantum computing | Watching for commercial proof points |
| QBTS / RGTI / QUBT | Quantum computing | Very speculative; small bets only |
| EWZ / EWY | International value ETFs | Opportunistic; not thesis-driven |
| IBIT | Bitcoin / Crypto infrastructure | Trend exposure only |

### Value Opportunism (Ad-hoc, not universe-permanent)

Tickers the trader enters when value appears regardless of sector thesis:
> CCL, CAVA, BROS (restaurants/consumer), HDB/IBN (India financials), JD/BABA (China value), EXPE (travel)

---

## Software Sector — Moat Reassessment (Apr 2026)

**Trader thesis update:** Software no longer has the blanket margin and moat it had in 2020-2023.
AI is compressing margins in generic software. The question is not "is it software?" but
"does this company have a defensible moat that AI cannot easily replicate?"

### Moat Assessment by Name

| Ticker | Moat Type | Moat Strength | AI Threat | Verdict |
|--------|-----------|---------------|-----------|---------|
| AXON | Data network + monopoly-like in law enforcement | **STRONG** | Low — government switching costs are extreme | **Core. Not software risk.** |
| CRM | Deep enterprise integrations + data network effects | **STRONG** | Medium — Copilot/AI rivals, but switching cost is 3-5 years | **Hold. $280 conviction intact.** |
| CRWD | Falcon platform + security telemetry data moat | **STRONG** | Low — security data is proprietary; AI enhances not replaces | **Core. AI pick/shovel play.** |
| OKTA | Identity infrastructure + enterprise integrations | **MODERATE** | Medium — Microsoft Entra competes; but multi-cloud identity sticky | **Hold. Watch MSFT pressure.** |
| ADBE | Creative tools + enterprise contracts | **MODERATE→WEAK** | HIGH — Canva, Midjourney, Firefly eroding consumer; enterprise stickier | **Reassess. Still earning premium; watch margin trends.** |
| SHOP | Merchant ecosystem + payments network + long tail | **STRONG** | Low — commerce infrastructure is sticky; AI enhances Shopify | **Emerging core. Pick/shovel for commerce.** |
| PYPL | Payment network | **WEAK** | Medium — but Apple Pay, Stripe, Block already winning | **EXIT. Not growth. Not value moat.** |
| TWLO | Communication APIs | **WEAK** | High — API layer commoditizing rapidly | **Not in active universe.** |
| NFLX | Content library + personalization | **MODERATE** | Medium — content moat but competition fierce | **Hold for premium; not conviction core.** |

### Software Decision Rule

> Before selling a new CC or strangle on any software name, ask:
> "Does this company charge more per user/seat every year AND are customers getting locked in deeper?"
> If YES → moat likely intact. If NO or unclear → treat as value play with exit plan, not core hold.

---

## Where the Skill Must Add Value (Trader's Acknowledged Gaps)

The trader operates on fundamentals + macro instinct. These are the systematic gaps the skill must fill:

| Gap | What Skill Provides |
|-----|---------------------|
| Technical analysis | RSI, 50/200-day MA, support/resistance levels as supplemental context on new entries and rolls |
| IV Rank screening | Flag when IVR is too low to justify new premium sales (even when regime allows entries) |
| Profit-take triggers | Alert at regime-appropriate threshold (40-60% bear / 70% bull) — trader decides, skill flags |
| Fundamental flag monitoring | Scan for earnings misses, guidance cuts, governance news on active positions — surface weekly |
| Position P&L tracking | Combined net P&L per position (stock cost basis + all premiums collected), not options P&L alone |
| Regime shift detection | Technical + macro signals to alert when bear→sideways→bull transition is occurring |

---

## Guardrails for the Skill

```yaml
accounts:
  account_a:
    target_return_annualized: 0.20
    strategy: [covered_call, short_strangle]
    max_contracts_per_ticker: 5
    tier1_max_contracts: 5
    tier2_max_contracts: 3
    tier3_max_contracts: 1
    margin_utilization_alert_pct: 0.80
    stop_loss: flag_and_ask  # Never auto-close

  account_b:
    target_return_annualized: 0.12
    strategy: [cash_secured_put, covered_call]  # Wheel only
    max_contracts_per_ticker: 1
    no_naked_calls: true
    no_margin: true
    tier3_names_max_pct_of_account: 0.10
    stop_loss: flag_and_ask  # Never auto-close

profit_targets_by_regime:
  BEAR_SIDEWAYS: [0.40, 0.60]  # Close when 40-60% of max premium captured
  TRANSITIONING: [0.50, 0.60]
  BULL: 0.70                   # Close when 70% of max premium captured

regime_gates:
  current_regime: BEAR_SIDEWAYS
  new_entries_allowed: false  # Until Oct/Nov 2026 or confirmed shift
  bull_entry_triggers:
    vix_sustained_below_20: true
    sp500_above_50d_and_200d_ma: true
    put_call_ratio_below: 0.80

dte_by_regime:
  BEAR_SIDEWAYS: null  # No new entries
  TRANSITIONING: [45, 90]
  BULL: [90, 360]      # 3-12 months

loss_management:
  hard_stop: false
  flag_threshold: 2.0x_premium_received
  roll_preference: true
  force_close_only_if: margin_utilization_above_80pct

fundamental_exit_triggers:
  auto_flag:
    - accounting_or_governance_event
    - auditor_resignation_or_restatement
    - geopolitical_event_directly_affecting_company
    - consecutive_guidance_cuts: 2
    - management_credibility_breakdown
  auto_exit: false  # Always flag and ask; never auto-exit on fundamental signal
  exception: governance_fraud  # Flag with highest urgency immediately

itm_position_plans:
  MRNA: natural_exit_via_cc_assignment  # Do not intervene
  NVO: natural_exit_via_cc_assignment   # Do not intervene
  CRM: hold_maximize_cc_premium         # Bull conviction to $280; roll puts as needed
  CRWD: standard_roll_management        # Monitor weekly

technical_overlay:  # Supplemental only — never overrides fundamental decision
  provide_on_request: [rsi, ma_50_200, support_resistance, iv_rank, iv_percentile]
  flag_divergence: true  # Alert when technical picture contradicts fundamental thesis
```

---

## Unified Master Reports (May 11, 2026 — Operational Framework)

**Status:** Production system; 4 reports integrated with options-trader skill and MCP server.

### Report Cadence & Triggers
- **Daily** (6 AM ET): Market snapshot, conviction updates, position heat, OODA framework
- **Weekly** (Monday 8 AM ET): Action priorities, top-5 items, IV rank entry gates, decision tree
- **Biweekly** (1st & 15th, 4 PM ET): 3-month trends, tier evolution, Greeks drift, sector rotation
- **Monthly** (1st, 8 AM ET): Variance analysis, account performance, moat recalibration, Citadel comparison

### Key Metrics Included in All Reports

**Conviction Scoring (1-10 scale)**
- RSI(14) contribution: <30 +2 points (oversold bullish), >70 -1 (overbought bearish)
- MACD histogram: Positive trend +1.5, negative -1.0
- Valuation: P/E 15-30 +0.5 (fair), >40 -0.5 (expensive)
- 52-week positioning: <25% of range +1.5 (near lows), >85% -1.0 (near highs)
- Clamp to 1-10 range always

**Position Heat Classification (Risk Signal)**
- 🟢 GREEN (Attractive): RSI <30 or position <10% of 52W range
- 🟡 YELLOW (Neutral): Approaching extremes, RSI 30-70, position 25-75%
- 🔴 RED (Extended): RSI >75 or position >90% of 52W range

**Position Value (Notional Exposure)**
- Formula: `Price × Contracts × 100` (standard options notional)
- Example: NKE $42.59 × 18 contracts × 100 = $76,662 notional
- Shown in all conviction sections for capital allocation visibility
- **For staggers (puts + calls same ticker):** ✅ NOW SEPARATED
  ```
  NKE: Stagger: 1 puts ($4,253) + 7 calls ($29,774)
  AXON: Stagger: 6 puts ($229,872) + 8 calls ($306,496)
  ```

### Account Health Metrics (IMPLEMENTED — All Reports)

✅ **Now included** in all 4 reports as **Section 0: Account Health & Margin Status**

The reports include a mandatory **Account Health & Margin Status** section per account:

**Account A (232 — Margin)**
- Total notional exposure (sum of all position values)
- Premium collected YTD vs premium at risk
- Available cash to trade (target: >$75K in bear regime)
- Margin utilization % (target: ≤70% bear, ≤60% bull, hard floor 50%)
- Option requirement / buying power impact
- Account equity trend (weekly change)
- Risk flags: cash drop >$50K/week, margin utilization spike >80%

**Account B (275 — IRA)**
- Total notional CSP exposure (no margin, no naked calls)
- Premium collected per position
- Target pace to 12% annualized ($28K/year = $2,333/month)
- Shares held from assignment (cap $100K per position, $375K total in bear)
- Cash available (no margin lines, but shows sweep balance)

**Account C (634 — Tactical)**
- Notional exposure vs account size
- Premium collected vs target pace (6% = $7.7K target on ~$128K AUM)
- Role: Rebalancing during market extremes only; holds steady otherwise

### MCP Tool Integration
- **generate_daily_report_tool()**: Called when user asks market-related questions
- **generate_weekly_report_tool()**: Called Monday or when user asks "what should I do this week?"
- **generate_biweekly_report_tool()**: Called on 15th or when user asks progress check
- **generate_monthly_report_tool()**: Called on 1st or when user asks monthly review
- **generate_all_reports_tool()**: Called to generate all 4 reports at once

### Framework Status Signals
Reports should flag:
- ✅ Framework working: win rate >70%, conviction accuracy improving, variance shrinking
- ⚠️ Framework stress: margin >75%, available cash <$75K, new entries gate closed (IVR <40)
- 🚨 Emergency mode: margin >80%, available cash <$50K, forced reduction required

### Data Sources
- **Live prices**: Yahoo Finance (106/107 tickers fetched daily)
- **Position data**: OpenPositionsLoaderV2 (438 open positions across 8 accounts)
- **Conviction metrics**: enhanced_metrics.py (RSI, MACD, Bollinger Bands, technical + fundamental scoring)
- **Greeks**: Black-Scholes calculations (delta, gamma, theta, vega)
- **Market regime**: Regime detection (BULL, CAUTIOUS_BULL, BEAR_SIDEWAYS based on VIX + S&P 50/200d MAs)
- **IV Rank**: Computed for top 25 tickers (entry gate: IVR ≥40)

### Known Limitations (May 2026)
- **Missing:** Premium collected/at risk per position (requires transaction-level data extraction)
- **Missing:** Account margin utilization % and available cash (requires broker API or manual export)
- **Missing:** Separated puts/calls breakdown for staggers (currently shows combined notional)
- **Data gap:** BRKB delisted; handled gracefully but flagged

---

## India Equity + F&O Reporting — 2026-07-20 Architecture Update

**Status:** Production. `mcp/routines/india_us_evening_report.py`, runs Sun-Thu 8 PM IST via
GitHub Actions (`--no-email` locally saves HTML to `logs/` instead of sending). Reads
`7500069840_*.csv` (equity transactions) and `7510078170_*.csv` (F&O open positions) from
`data/statements/` — drop new ICICI Direct exports there (newest by mtime wins).

**Root problem found and fixed this session:** the report's "regime" and every equity
KEEP/WATCH tag were driven by hand-set text and a static `exit_triggers` price list in
`data/india_config.yaml`, none of it re-checked after being written (much of it back to
April 2026). A same-day audit found triggers wrong in **both directions** — DRREDD's
trigger cited "-14% earnings growth" while actual earnings had collapsed -86% YoY, and
STABAN's trigger cited "-43% loss" while the real position was +12% profitable. The regime
line ("FII net sellers 18+ months") was hardcoded and never connected to any live data at
all — same corner-cutting pattern to check for anywhere else in this codebase.

**What changed:**
- **Regime**: now calls `analysis/india_regime.py:detect_india_regime()` (VIX + Nifty
  50/200-day MA signals) instead of printing static text. Supports `INDIA_REGIME_OVERRIDE`
  env var (`.env`) for a trader call when the technical tie-break default (ties resolve to
  BEAR_SIDEWAYS) looks too conservative — e.g. sustained VIX compression the formula
  under-weights. Set 2026-07-20 to TRANSITIONING; **revisit ~2026-10-17** or sooner if
  signals reverse.
- **Equity verdicts**: static core-list/price-trigger tagging replaced with a **live
  conviction score**, fundamentals-weighted as PRIMARY (revenue/earnings growth, analyst
  rating, target-price upside) with technicals (RSI/MACD/PE/52-week position) as
  SUPPLEMENTAL — matching this persona's stated philosophy ("fundamentals + macro instinct
  is the research engine... technicals are supplemental, not primary"), which the
  technical-only version of the US formula had actually been violating. Fixed in the
  **shared** `mcp/reports/enhanced_metrics.py:get_ticker_metrics()` — the US reports use
  this too, so the fix and its 5-field output (`revenue_growth`, `earnings_growth`,
  `analyst_rating`, `target_upside_pct`, plus existing technicals) apply to both markets.
  Verdict bands: **WEAK** (conviction <4, or YELLOW heat + conviction <5 — fundamentals
  genuinely bad), **EXTENDED** (RED heat/technically overbought regardless of conviction —
  a good business can still be a trim candidate, this is NOT the same as WEAK), **MONITOR**
  (YELLOW heat + ok conviction, or GREEN heat + low conviction — value-trap check), **LET
  RUN** (GREEN heat + ok conviction). Every row shows its own plain-English reason
  (`_verdict_reason()`) — don't ship a verdict without a driver explanation again.
- **Sector & market-cap momentum** (`check_sector_themes()`): recomputed every run against
  17 NSE sector/cap-segment indices (Nifty 50, Next 50, Midcap 100, Nifty 500, Pharma, IT,
  Auto, Realty, Energy, Bank, PSU Bank, FMCG, Metal, Infra, PSE, Media, Consumption — no
  reliable Yahoo ticker found for Nifty Smallcap 100, Private Bank, Commodities, or
  Manufacturing as of this date). Flags COOLING (a core theme's sector underperforming
  Nifty 50 on both 3mo and 6mo) and RECONSIDER (a non-core sector outperforming by 10+ pts
  on both windows). Caught Pharma outperforming 4 of the then-5 core themes while being
  the stated reason to exit DRREDD — added as a 6th core theme via AURPHA (Aurobindo
  Pharma, NOT Dr Reddy's — DRREDD's problem is company-specific, the sector strength
  doesn't offset an 86% earnings collapse). Defense/PSU flagged softer (-6.1% 3mo, still
  +1.7% 6mo — not yet a sustained COOLING signal, worth another look next run).
- **New Entry Candidates** (`check_watchlist()`): `data/india_config.yaml`'s `watchlist`
  section (target entry zones for stocks not yet owned) is now live-checked every run —
  current price + fresh conviction vs. the planned entry zone, gated on
  `regime.new_entries_allowed`. Previously only checked manually when asked.
- `data/india_config.yaml`'s `core_portfolio` list is now **informational only** (a
  thematic tag shown in reports) — it no longer determines any verdict.

**Known gaps (2026-07-20):**
- NIFSEL F&O contracts aren't recognized by the Black-Scholes underlying-index map and get
  silently dropped from the F&O table — cross-check against the raw ICICI statement's own
  realized/unrealized P&L for that underlying if it's open.
- Hospitals has no clean standalone NSE sector index on Yahoo — theme validation for that
  bucket relies on stock-level conviction only (APOHOS, YATHOS), not a sector-momentum check.
- `_format_research_card` in `mcp/server.py` was broken (function body present, `def` line
  missing — call sites had been silently failing on `research_symbol`/`run_screener`/
  `scan_sector` for both US and India). Fixed and syntax-validated 2026-07-20, but the
  running MCP server process needs a restart to load it — check it actually works before
  trusting those three tools again.

---
