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

---

## Account B Strategy (Pinky — IRA — 12% target)

### Primary: Wheel (CSP → Assignment → CC → Exit)

**Entry (when regime allows):**
- IVR must be ≥ 40 (call `get_iv_rank` first)
- Tier 1/2 names only for new wheels; Tier 3 max 1 contract
- Sell CSP at delta 0.15-0.20 (80-85% PoP)
- DTE: 45-60 days (not the 6-18 month DTE of legacy positions)
- Strike: 10-15% OTM in bear, 5-7% OTM in bull

**When assigned (stock received):**
1. Do NOT panic — this is the wheel working
2. Immediately sell CC at delta 0.25-0.30 (ATM to slight OTM)
3. Target: recover full premium cost in 3-5 CC cycles
4. Accept CC assignment and exit when profitable; do not hold the stock

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
| Short put ITM, thesis intact | Roll down + out (lower strike, further DTE) | Net credit only — never pay to roll |
| Short put ITM, thesis broken | Close and redeploy | Exit cleanly |
| Short call ITM (CC) | Roll up + out (higher strike, further DTE) | Net credit or small debit OK if bull |
| Short call ITM (strangle leg) | Roll up aggressively to recapture delta | Keep strangle balanced |
| At 21 DTE with 50%+ profit | Roll out same strike for more premium | Collect additional credit |

**Roll golden rule:** Never pay a net debit to roll unless the position is being turned from loser to winner with strong conviction.

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
