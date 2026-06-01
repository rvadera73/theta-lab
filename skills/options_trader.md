# Options Trader Skill — Theta-Lab

**Persona file:** `~/.claude/skills/trading_persona.md` (load first on every invocation)
**MCP server:** `theta-lab` (provides live Schwab data and analysis tools)
**Status:** ACTIVE

---

## Invocation

This skill activates when the user asks about:
- Trade decisions, position reviews, weekly report
- "What should I do this week?"
- "What's my P&L on X?"
- "Should I close / roll / enter X?"
- Any option-related decision on Accounts A or B

---

## Weekly Data Pipeline

**Sources (two files from Empower + Schwab):**
- `data/statements/Individual-Positions*.csv` — Schwab Account A (232) positions, cost basis, open options
- `data/statements/YYYY-MM-DD thru YYYY-MM-DD transactions.csv` — Empower unified export, all 14 accounts

**Weekly prep (do before Monday email):**
1. Export Schwab positions CSV → drop in `data/statements/`
2. Export Empower transactions CSV (YTD range) → drop in `data/statements/`
3. `python3 scripts/update_snapshot.py`
4. Set `month_to_date_equity_change` manually in `data/portfolio_snapshot.yaml`
5. `git add data/portfolio_snapshot.yaml && git commit -m 'Weekly snapshot' && git push`

**Email automation:** GitHub Actions runs every Monday 8AM ET via `mcp/routines/weekly_dashboard.py`. Sends to ravjdpr@gmail.com via Resend API. Secret: `RESEND_API_KEY` in GitHub repo secrets.

**Account B gap:** No positions CSV for XXX275 yet — export separately from Schwab IRA account to get accurate Account B open positions and trade recommendations.

---

## Mandatory Pre-Flight Protocol (Every Session)

1. Load `trading_persona.md` — confirm regime, profit targets, permanent exits
2. Call `check_market_regime` — get current VIX + MA signals
3. If any live order is being proposed → call `dry_run_order` first, always

---

## Weekly Report (Monday)

**Trigger:** User asks "what should I do this week" or it is Monday

```
1. Call generate_weekly_action_report
2. Save to logs/action_report_YYYY-MM-DD.md
3. Present Top-5 with clear recommendations
4. Ask: "Which of these do you want to act on?"
5. For any action → dry_run_order → present result → user decides
```

---

## Account A Strategy (Rahul — Margin — 20% target)

### Primary: Short Strangles
- Sell PUT at delta ~0.15 (85% PoP) + CALL at delta ~0.20 (80% PoP)
- Bear/sideways: call slightly closer OTM than put (more bearish bias)
- Target: 1-3% monthly premium on notional
- DTE: 45-90 days when regime allows entries
- Close: 40-60% profit captured (bear) / 70% (bull)

### Secondary: Covered Calls on Assigned Shares
- When stock assigned from put: immediately sell CC at delta 0.20-0.30
- Roll CC up if stock rallies past strike (collect credit, extend DTE)
- Target: reduce cost basis by 2-3% per month until exit

### Optimization Rules
- Max 5 contracts per Tier 1 name, 3 Tier 2, 1 Tier 3
- Never open new strangle on a name already at max contracts
- Ladder strikes: do not sell all contracts at same strike — space by $5-10
- When strangle threatened on one side: roll that side only (not whole position)
- MRNA: let natural CC assignment complete. Do not re-enter.
- PYPL: sell CCs on any bounce. No re-entry after exit.
- **SOFTWARE THESIS BROKEN (May 22):** Do NOT enter new positions on CRM, OKTA, CRWD, ADBE, SHOP (except long-DTE decay plays already initiated). AI margin compression + moat erosion. Let existing staggers run to profit-take at 70%, exit, deprioritize re-entry.

### Account A — Margin and Cash Management

**Ideal equity % by regime (never a static number):**
| Regime | Target Equity % | Hard Floor |
|--------|----------------|-----------|
| Bull | 55–60% | 45% |
| Sideways | 60–65% | 50% |
| CAUTIOUS_BULL (current, May 22) | 60–65% | 50% |

**Option requirement ratio:** Target below 80% of net liq in bear regime. Above 100% is alert territory; above 130% is structural risk requiring active reduction over time.

**Emergency fund ($200K):** Keep separate from trading account. Deploy only if cash to trade drops below $75K AND VIX is elevated simultaneously. Not a source for new positions.

**Cash to trade — weekly policy (check every Monday morning):**
| Cash to Trade | Action |
|--------------|--------|
| ≥ $125K | No action — let all positions run |
| $100K–$124K | Monitor; close profitable puts ≥ 40% only if VIX elevated (not compressing) |
| $75K–$99K | Close profitable puts ≥ 40%; consider $50K emergency fund deposit |
| $50K–$74K | Close profitable puts ≥ 30%; deposit $75–100K from emergency fund |
| < $50K | Emergency — close what you can; deploy emergency fund immediately |

**Current Status (May 22):** Account A margin requirement = $650K, utilization = 60%, cash-to-trade = $96K. Status: HEALTHY. Awaiting PYPL closure (~5 contracts) to rebalance Tier 1.

**Why cash fluctuates without structural change:** Cash to trade = Total equity − Option requirement used. Both sides move daily. A VIX spike inflates option marks and requirement simultaneously, pulling $30–60K from available cash in a single week. When VIX normalizes, cash returns. Do NOT force closes to solve a temporary VIX-driven cash drop — closing at the bottom of a VIX spike gives away earned premium.

**Calls vs puts on margin impact:** Far OTM short calls carry low margin requirement — closing them locks in profit but has minimal effect on cash to trade. Short puts (closer to ATM) carry much larger margin requirement — closing puts meaningfully frees pledged collateral and improves available cash. Prioritize put closes when cash improvement is the goal.

---

## Account B Strategy (Pinky — IRA — 12% target)

### Primary: Wheel (CSP → Assignment → CC → Exit)

**Entry (when regime allows):**
- IVR must be ≥ 40 (call `get_iv_rank` first) — this gate applies to NEW entries only; existing positions are held regardless of current IVR
- Tier 1/2 names only for new wheels; Tier 3 max 1 contract
- Sell CSP at delta 0.15-0.20 (80-85% PoP)
- DTE: 45-60 days (not the 6-18 month DTE of legacy positions)
- Strike: 10-15% OTM in bear, 5-7% OTM in bull

**When assigned (stock received):**
1. Do NOT panic — this is the wheel working
2. Assignment in Schwab is automatic — no action needed to accept; focus immediately on the CC
3. Immediately sell CC at delta 0.25-0.30 (ATM to slight OTM)
4. Target: recover full premium cost in 3-5 CC cycles
5. Accept CC assignment and exit when profitable; do not hold the stock

**Profit take:**
- Bear: close CSP at 40-60% of max premium — redeploy into next CSP
- Bull: let run to 70%
- Never hold to expiration — gamma risk near expiry is not worth the last 20%

**IRA-specific rules (non-negotiable):**
- NO naked calls — CCs only against owned shares
- NO margin use
- NO spreads requiring margin
- Max 1 contract per position regardless of tier
- Speculative names (Tier 3): max 10% of account B total value combined

### Crypto Sub-Strategy (Account B)
- COIN, HOOD CSPs when IVR ≥ 40 and Bitcoin > $90K sustained
- IBIT CSPs: cleanest BTC exposure for IRA; max 1 contract
- HUT/CIFR/RIOT: Tier 3 only; max 1 contract; high-beta to Bitcoin
- Scale trigger: Bitcoin sustained above $100K → add CSPs on COIN and HOOD

### Account B Current Deployment (May 22, 2026)
- **BWXT** 160P Jan 27, 2027 (239d) @ $11.13 = $1,113 credit — nuclear/energy infrastructure play (diversified with GEV, BE, OKLO, SMR)
- **SHOP** 90P Jun 27, 2027 (392d) @ $15.85 = $1,585 credit — collect-decay strategy at long DTE (let theta work)
- **NEE** 82.50P Dec 18, 2026 (211d) @ $4.40 = $440 credit — opportunistic value on DVN merger dislocation
- **Total premium:** $3,138 collected; $27K buffer remaining for staggering or assignment equity

---

## Loss Management Protocol (Never Auto-Close)

When `loss_flag` fires (mark > 2x premium received):

```
1. Present to trader: "Position X has mark at {N}x premium received"
2. Show 3 options:
   A. Roll — calculate net credit of rolling to next expiry + adjusted strike
   B. Hold — if DTE > 45 and thesis intact, time is still working
   C. Close — only if thesis is fundamentally broken (not just price move)
3. Wait for trader decision. Do NOT auto-execute any of the above.
4. If trader says close → dry_run_order → confirm → execute
```

**Exceptions (escalate with HIGH urgency, still ask):**
- Governance fraud news on a holding
- Account A margin utilization > 80%

---

## Roll Decision Framework

When approaching 21 DTE or position goes ITM:

| Situation | Roll Action | Target |
|-----------|------------|--------|
| Short put ITM, thesis intact, DTE > 45 | **HOLD** — do not roll | Time is working; rolling down when bullish surrenders premium for no reason |
| Short put ITM, thesis intact, DTE ≤ 21 | Roll down + out (lower strike, further DTE) | Net credit only — never pay to roll |
| Short put ITM, thesis broken | Close and redeploy | Exit cleanly |
| Short call ITM (CC) | Roll up + out (higher strike, further DTE) | Net credit or small debit OK if bull |
| Short call ITM (strangle leg) | Roll up aggressively to recapture delta | Keep strangle balanced |
| At 21 DTE with 50%+ profit | Roll out same strike for more premium | Collect additional credit |

**Roll golden rule:** Never pay a net debit to roll unless the position is being turned from loser to winner with strong conviction.

**Hold vs Roll test:** Before recommending a roll on an ITM put, ask — am I bullish on the underlying? If yes and DTE > 45, the answer is always hold. Rolling down when bullish = locking in a realized loss + collecting less future premium. That is an emotional trade, not a strategic one.

---

## Stagger vs Roll — Critical Distinction

**Stagger IS the strategy.** Stagger = selling the same underlying at different strikes and different expiries across time, creating a ladder of exposure. Each leg matures independently. This is intentional risk distribution — not a problem to fix. Do NOT unwind a stagger by rolling legs into each other.

**Roll is for a single contract in a specific situation** — approaching ≤21 DTE, assignment risk, or thesis broken. Rolling is a single-contract adjustment, not a stagger-wide operation.

**When you see AXON $470P Jun / $660P Sep / $540P Dec / $420P Jan — that is a stagger. Let each leg run on its own schedule.**

**Profit close thresholds are independent per leg.** Each leg of a stagger is evaluated individually against the profit close target. Closing one leg does not require closing others.

---

## Technical Overlay (Supplemental Only)

When evaluating any entry or roll, optionally provide:
- **RSI(14):** >70 = overbought (don't add calls); <30 = oversold (don't add puts)
- **50/200-day MA:** is stock above or below? Informs directional bias
- **Support/Resistance:** nearest levels relative to proposed strike
- **IV Rank:** always show from `get_iv_rank` before new entries

These are inputs, not overrides. Trader makes the final call.

---

## Sector-Specific Rules

**AI pick/shovel names (ALAB, GEV, VST, AXON, CRWD):**
- Core positions — can ladder strikes, maximize contract count within limits
- Do not exit just because market is down; thesis is multi-year

**Space (ASTS, RKLB, ACHR):**
- Tier 3 — 1 contract only
- Watch for Tier 2 graduation triggers: commercial revenue, launch milestone, analyst upgrade
- If graduation trigger fires: present to trader before increasing size

**Crypto (COIN, HOOD, IBIT):**
- Scale with Bitcoin price: use Bitcoin > $100K as signal to add exposure
- IRA (Account B): IBIT CSPs preferred (cleanest, no exchange risk)
- Margin (Account A): COIN strangles when IVR elevated

**Recovery bets (beaten-down consumer/value names):**
- Pattern: stock down 50%+ from 52W high, near 52W low, value segment that benefits from consumer trade-down in bear/sideways markets
- Strategy: hold the CSP, accept assignment, wheel out with CCs — elevated HV from the slide means CC premiums are fat
- Do NOT roll down just because it's ITM — that surrenders the recovery premium
- Example: ELF at $66 vs 52W high $147 — value beauty gains share when consumers trade down from premium brands
- IVR < 40 on these names is fine for holding; do not use as a reason to close or roll

**Permanent exits (MRNA, PYPL):**
- Sell CCs aggressively to recover premium
- Do NOT open any new puts on these names
- After full exit: remove from active tracking

---

## Monthly Macro Scan (First Monday of Month)

```
1. Call check_market_regime
2. Review sector thesis from trading_persona.md
3. Generate macro_scan_YYYY-MM.md in logs/
4. Highlight: any regime shift signals? Any sector thesis changes?
5. Update profit-take targets if regime shifted
6. Review upcoming earnings for all active positions
```

---

## Portfolio Tracking System

Three watchlist portfolios are maintained alongside the options accounts. These are pre-deployment analysis pipelines — when cash becomes available, the reports tell you exactly what to buy and at what price.

### Portfolio Definitions

| Portfolio | File | Names | Review Cadence | Purpose |
|-----------|------|-------|---------------|---------|
| Portfolio-1 | `Portfolio-1 2026-04-25.xlsx` | 66 names | **Monthly** | Full investment universe; regime-filtered entry candidates |
| Holdings (Q1-2025) | `Holdings-Portfolio 2026-04-25.xlsx` | 11 names | **Quarterly** | Actual held positions across all accounts; recovery tracking |
| 10-Year | `10-Year Portfolio 2026-04-25.xlsx` | 13 names | **Semi-annual** | Long-term conviction holds; accumulation thesis check |

### Report Cadence and Log Files

```
Portfolio-1 (monthly):   logs/portfolio_review_P1_YYYY-MM.md
Holdings (quarterly):    logs/portfolio_review_holdings_YYYY-QN.md
10-Year (semi-annual):   logs/portfolio_review_10yr_YYYY-HN.md
```

### Report Structure for Each Portfolio

**Portfolio-1 Monthly:**
1. Regime filter — which names qualify under current regime (bear = Tier 1/2 only, IVR ≥ 40 for options)
2. 52W range positioning — flag names in bottom 25% of range as potential entries
3. Thesis changes — any names where the investment thesis has shifted
4. Top-5 deployment candidates — specific entry prices, options vs outright buy recommendation
5. Names to remove from universe — thesis broken or no longer fits strategy

**Holdings Quarterly:**
1. Current price vs cost basis for each held name
2. Recovery progress — how far from breakeven? At current CC/wheel pace, when is breakeven?
3. Thesis check — is the original reason for holding still valid?
4. Next quarter targets — what price action or events would change the hold/exit decision

**10-Year Semi-annual:**
1. Price vs 52W range position for each name
2. Thesis validation — is the 10-year thesis still intact (technology shift, market leadership)?
3. Accumulation zones — at what price is this a compelling add vs a hold
4. Risk flags — any existential threats to the thesis (regulation, competition, leadership)?
5. Position sizing guidance — given current regime, how to size an entry

### Entry Strategy by Regime

| Regime | Entry Method | Sizing | Timing |
|--------|-------------|--------|--------|
| Bull | Buy shares directly or sell ATM puts | Full position | On breakout or dip |
| Sideways | Sell puts 5-10% OTM | 50% of target | On IV spikes |
| **Bear (current)** | **Sell puts 10-15% OTM; never buy outright** | **25% of target per tranche** | **Wait for VIX > 25 to sell puts (higher premium)** |

**Bear regime deployment rule:** Do not buy any position outright in a bear/sideways regime. Sell puts instead — this sets a lower effective entry price AND collects premium. If the put expires worthless, keep premium and repeat. If assigned, you own at a discount.

**Cash deployment sequence (when cash becomes available):**
1. Check current regime — confirms strategy
2. Check IVR for target names — ≥ 40 required before opening puts
3. Open at 25% of target position size — do not deploy all at once
4. Stage remaining 75% across 3-6 months via new puts as regime confirms

### Loser Identification (Remove from Portfolios)

A name is a loser to remove when **two or more** of these apply:
- Thesis broken: company-specific headwind that wasn't present at entry (regulatory, competitive displacement, management failure)
- Price > 40% below 52W high with no recovery catalyst visible within 6 months
- 3+ consecutive quarters of underperformance vs sector ETF without explanation
- Better name available in the same theme (remove the weaker, keep the stronger)
- Position has reached terminal stage (e.g., acquisition closed, permanent exit completed)

**Not a loser:** Being near 52W low alone is not a removal trigger — it is often a buying opportunity if thesis is intact.

### Portfolio-1 Turnover Rules (15-20% Annually)

With 66 names: target 10-13 rotations per year = 2-4 names per quarter (removed + added).

| Review | Target Removals | Target Additions |
|--------|----------------|-----------------|
| Monthly | Flag candidates | Flag replacements |
| Quarterly | Execute 2-4 removals | Add 2-4 replacements |
| Annual | Full portfolio audit | Rebalance to 60-70 names |

Monthly report must include: **Remove list** (names leaving), **Add list** (names entering), **Watchlist** (names on probation — one more bad quarter triggers removal).

### Holdings Portfolio Rules (Q1-2025)

**Core principle:** Never deliberately hold equity. Options premium is the strategy. Equity is only acceptable as an involuntary byproduct of put assignment. All assigned positions must be exited via CC wheel as the priority.

Two separate equity buckets — governed independently:

---

**Bucket 1 — Deliberate Equity (intentional stock purchases)**

**Hard cap: $0**

Never buy stock outright in an active options account. All exposure enters via put selling only. If you want a name, sell a put — do not buy shares. No exceptions without explicit conscious authorization for a stated reason.

---

**Bucket 2 — Assigned Equity (CC wheel byproduct)**

**Per-name cap:** $100K OR 2,000 shares — whichever hits first. Applies to every assigned position regardless of how bullish the thesis.

**Total assigned book cap — regime-dependent** (anchored to active options accounts AUM ≈ $1.0–1.5M combined: Account A, Account B, Robinhood IRA, active Fidelity accounts):

| Regime | Assigned Equity Cap | Action Trigger |
|--------|--------------------|----|
| Bull | 15% of active options AUM ≈ $150–225K | Exits are fast; keep tight |
| Sideways | 20% of active options AUM ≈ $200–300K | CCs work normally; monitor weekly |
| **Bear (current)** | **25% of active options AUM ≈ $250–375K** | High assignment rate; CC exits mandatory |
| Danger zone | >30% of active options AUM | Freeze new puts on ALL assigned names; accelerate every CC exit |

**Current bear target:** ≤$300–375K total assigned book across all active options accounts.
**Current state (Apr 2026):** ~$401K in Account A alone — in danger zone; CC exits in progress.

**Rules for assigned equity:**
- Accelerate CC exits when total book approaches the regime cap
- Do not open new puts on any name that already has an assigned position, until that name's CC exit completes
- If any single name exceeds $100K or 2,000 shares: only CCs allowed on that name — no new puts
- Quarterly close candidates: any assigned name where thesis has broken — do not wheel a broken thesis; take the loss and redeploy

---

**Passive accounts (401K, Vanguard funds, minor Roth IRA) are excluded from these caps** — equity is the strategy in those accounts and these rules do not apply there.

---

## MCP Tool Reference

| Tool | When to Use |
|------|------------|
| `generate_weekly_action_report` | Every Monday — full Top-5 report |
| `check_market_regime` | Start of every session |
| `get_iv_rank` | Before any new entry |
| `get_portfolio_pnl` | Weekly P&L review |
| `scan_profit_take_candidates` | Mid-week check |
| `scan_roll_candidates` | Friday — upcoming expirations |
| `dry_run_order` | Before EVERY live order |
| `screen_new_entries` | When regime shifts to BULL or TRANSITIONING |

---

## Output Format for Recommendations

Always present trade recommendations in this format:

```
**[SYMBOL] — [Account A/B] — [Action]**
- Current position: [describe]
- Trigger: [why acting now]
- Proposed action: [specific trade]
- Expected premium / P&L impact: [$X]
- Risk if wrong: [describe]
- Pre-flight: [dry_run result]
- Decision: [PROCEED / HOLD / MODIFY]
```
