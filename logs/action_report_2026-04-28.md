# Weekly Action Report — April 28, 2026

**Generated:** 2026-04-25 (for week of Apr 28)
**Regime:** Bear/Sideways | VIX elevated
**Account A:** $429,659 balance | 49% equity | $75,695 cash to trade | $654,067 option req
**Account B:** $255,910 cash balance
**Emergency fund:** $200K available — keep separate unless cash < $75K AND VIX expanding

---

## Monday Morning Pre-Flight (Do This Before Any Order)

```
1. Check Account A cash to trade
   ≥ $125K  → Execute mandatory + AXON calls only. Stand down on conditionals.
   $75–124K → Execute mandatory + AXON calls + conditional META/LLY closes
   < $75K   → Execute all + deposit $50K from emergency fund

2. Check VIX direction
   Compressing → cash will recover; do not force conditional closes
   Expanding   → cash will worsen; execute conditionals immediately

3. Check Bitcoin price
   > $90K sustained → Roll COIN May; HOLD all crypto positions
   < $90K           → Close COIN May instead of rolling

4. Run dry_run_order on COIN and MSFT rolls before submitting live orders
```

---

## ACCOUNT A (XXX232 — Rahul Margin)

---

### MANDATORY — Execute Regardless of Cash Level (Time-Driven)

---

**[COIN $250P May 15] — Account A — ROLL or CLOSE**
- Current position: Short 1 put, mark $52.82, P&L -$2,508 (-90%)
- Trigger: 20 DTE. COIN ≈ $197–200. Put is $53 ITM. Assignment near-certain if no action.
- Proposed action:
  - Bitcoin > $90K sustained → Roll to Jul 17 $210P for net credit (lower strike $40, extend 63 days)
  - Bitcoin < $90K → Close. Accept -$2,508 loss. No forced holds on thesis-uncertain positions.
- Expected credit on roll: $0.50–$1.50 net
- Risk if wrong: COIN continues falling below $210 through July
- Pre-flight: `dry_run_order` on the roll before submitting
- Decision: **DECIDE MONDAY — Bitcoin price determines direction**

---

**[MSFT $420P May 15] — Account A — ROLL**
- Current position: Short 1 put, mark $14.55, P&L -$588 (-68%)
- Trigger: 20 DTE. MSFT ≈ $405–415. At or near ITM.
- Proposed action: Roll to Jul 17 $405P for net credit. Lower strike $15, extend 83 DTE.
- Expected credit: $0.50–$2.00 net
- Risk if wrong: MSFT slides further; tech under pressure in bear regime
- Pre-flight: `dry_run_order` before submitting
- Decision: **PROCEED — quality name, thesis intact**

---

**[PYPL $45C May 15 — 3 contracts] — Account A — ACCEPT ASSIGNMENT**
- Current position: Short 3 calls, mark $6.22, P&L -$1,318 (-241%). PYPL at $50.48.
- Trigger: 20 DTE. Deeply ITM ($5.48). 300 shares called away at $45. Permanent exit name.
- Proposed action: Let assignment happen. 300 shares removed from 1,300.
- Immediately after assignment: Sell new CCs on remaining 1,000 shares at $55–60 strike, Jun–Jul DTE, delta 0.25–0.30.
- Expected P&L impact: -$1,318 options loss realized; stock position reduced toward exit
- Risk: None — assignment is the goal for permanent exits
- Decision: **PROCEED — do not roll, let assignment execute**

---

### TIER 1 CLOSES — Above 50% Profit Threshold (Execute Regardless of Cash Level)

---

**[AXON $600C Dec 18] — Account A — CLOSE (BTC)**
- Current position: Short 1 call, mark $31.45, P&L +$4,103 (56.6%)
- Trigger: Above 50% profit threshold for bear regime. Rule says close.
- Proposed action: Buy to Close. Lock in $4,103 realized.
- Cash impact: BTC cost $3,145; far OTM call — modest margin release
- Risk if closed: AXON falls further and call would have profited more. Acceptable — threshold rule is firm.
- Pre-flight: `dry_run_order` before submitting
- Decision: **PROCEED**

---

**[AXON $620C Jan 27] — Account A — CLOSE (BTC)**
- Current position: Short 1 call, mark $31.77, P&L +$3,653 (53.5%)
- Trigger: Above 50% profit threshold.
- Proposed action: Buy to Close. Lock in $3,653 realized.
- Cash impact: BTC cost $3,177
- Pre-flight: `dry_run_order` before submitting
- Decision: **PROCEED**

*Combined AXON call closes: +$7,756 locked, $6,322 cost. AXON position becomes four-legged put stagger only — correct structure for bullish thesis on fallen AI name.*

---

### CONDITIONAL CLOSES — Execute Only If Cash < $125K Monday Morning

*Puts free more margin than calls. These are the right closes if cash improvement is needed.*

---

**[META $550P Dec 18] — Account A — CLOSE if cash < $125K**
- Current position: Short 1 put, mark $28.35, P&L +$1,084 (27.7%)
- Below 40% target but puts free significant collateral — cash improvement justifies early close
- Pre-flight: `dry_run_order`
- Decision: **CONDITIONAL**

**[META $520P Mar 27] — Account A — CLOSE if cash < $125K**
- Current position: Short 1 put, mark $29.43, P&L +$1,073 (26.7%)
- Pair with $550P close above — same session
- Decision: **CONDITIONAL**

**[LLY $1070C Jan 27] — Account A — CLOSE if cash < $125K**
- Current position: Short 1 call, mark $57.42, P&L +$2,664 (31.7%)
- 32% profit captured; reduce LLY exposure; modestly frees call margin
- Decision: **CONDITIONAL**

---

*Execute these two only if cash to trade is < $100K Monday:*

**[CRWD $340P Dec 18]** — P&L +$613 (20.9%) — BTC $2,321 — **CONDITIONAL (< $100K only)**

**[AMZN $250P Dec 18]** — P&L +$687 (24.6%) — BTC $2,103 — **CONDITIONAL (< $100K only)**

---

### HOLD — No Action This Week

*All DTE > 45. All thesis intact. Stagger legs run independently — do not unwind.*

| Position | P&L | DTE | Why Hold |
|----------|-----|-----|---------|
| AXON $470P Jun 18 | -$6,160 | 54 | Stagger leg — bullish AI thesis |
| AXON $660P Sep 18 | -$19,041 | 146 | Stagger leg — largest loss but thesis intact |
| AXON $540P Dec 18 | -$10,557 | 237 | Stagger leg |
| AXON $420P Jan 27 | -$5,077 | 265 | Stagger leg — closest to OTM |
| APP $580P Aug 21 | -$8,314 | 118 | Stagger leg |
| APP $460P Jul 17 | -$1,235 | 83 | Stagger leg |
| APP $450P Jun 18 | -$203 | 54 | Nearly flat — let it run |
| ADBE $310P Aug 21 | -$5,035 | 118 | Wheeling — hold |
| ZS $180P Dec 18 | -$4,193 | 237 | Thesis intact — hold |
| CRM $220P Aug 21 | -$3,524 | 118 | Wheeling — hold |
| IBM $270P Oct 16 | -$3,261 | 174 | Hold |
| LMT $520P Mar 27 | -$2,943 | 328 | Hold |
| LLY $840P Oct 16 | -$2,440 | 174 | Hold |
| NKE $65P Jun 18 | -$1,532 | 54 | Hold — flag if NKE thesis weakens |
| RBLX $80P/$70P Jul 17 | -$2,853 | 83 | Hold |
| ISRG $495P Jul 17 | -$1,692 | 83 | Hold |
| UNH $330C Dec 18 | -$2,898 | — | ITM CC — debit roll not justified; 7% above $330; revisit Oct |
| UNH $340C Mar 27 | -$2,278 | — | More time — hold |
| MRNA $26C + $35C Jun 18 | -$6,723 | 54 | Permanent exit — let Jun assignment complete |
| All other healthy OTM positions | positive | — | Let run to target |

---

### Account A — Action Summary

| Priority | Position | Action | Condition |
|---------|----------|--------|-----------|
| 1 | COIN $250P May 15 | Roll Jul $210P or Close | BTC > $90K → Roll; else Close |
| 2 | MSFT $420P May 15 | Roll Jul $405P | Unconditional |
| 3 | PYPL $45C May 15 | Accept assignment | Unconditional |
| 4 | AXON $600C Dec 18 | BTC — close | Unconditional (above threshold) |
| 5 | AXON $620C Jan 27 | BTC — close | Unconditional (above threshold) |
| 6 | META $550P + $520P | BTC — close | Cash < $125K |
| 7 | LLY $1070C Jan 27 | BTC — close | Cash < $125K |
| 8 | CRWD $340P + AMZN $250P | BTC — close | Cash < $100K |
| — | All 19 stagger/hold positions | HOLD | No condition needed |

---

## ACCOUNT B (XXX275 — Pinky IRA)

### Position Status — All Fresh, All Hold

All positions were opened April 14–24 (2–11 days old). None are near the 40% bear-regime profit target. Primary posture: **HOLD everything.**

| Position | Opened | Thesis | Action |
|----------|--------|--------|--------|
| NVDA $175P | Apr 17 | Tier 1 AI | HOLD |
| TSM $300P | Apr 14 | Tier 1 semiconductor | HOLD |
| ELF $55P | Apr 20 | Recovery bet — value beauty | HOLD |
| HOOD $70P | Apr 20 | Bullish crypto adjacent | HOLD |
| CCL $25P | Apr 17 | Consumer stagger leg | HOLD |
| CCL $23P | Apr 24 | Consumer stagger leg | HOLD |
| ROKU $85P | Apr 14 | Streaming | HOLD |
| BE $165P | Apr 14 | Clean energy | HOLD |
| RKLB $60P | Apr 21 | Tier 3 space — 1 contract | HOLD |
| HUT $50P | Apr 14 | Tier 3 crypto — 1 contract | HOLD |
| RIOT $13P | Apr 24 | Tier 3 crypto — 1 contract | HOLD |
| COIN $145P | Apr 24 | Crypto — BTC dependent | HOLD |
| USAR $17P | Apr 21 | Small position | HOLD |

---

### CONDITIONAL — New Entries Account B

**No new entries unless all three gates pass:**
1. IVR ≥ 40 on the specific name (`get_iv_rank`)
2. Tier 1 or 2 only; Tier 3 already at max (HUT, RIOT, RKLB each at 1 contract)
3. For crypto names: Bitcoin > $90K sustained

**Names to screen if gates pass:**
- IBIT CSP — cleanest IRA BTC exposure; CSP at delta 0.15–0.20 if IVR ≥ 40
- Do not add second COIN position this week (already have $145P from Apr 24)

---

### Account B — Specific Watches

**ELF $55P — Recovery Bet**
Stock at $66, strike $55, $11 OTM. Thesis: value beauty trade-down in consumer bear market. ELF down 55% from 52W high.
- If ELF drops toward $55: HOLD — accept assignment and immediately sell CC at $60–65 strike
- If ELF rallies to $80+: check profit % — if ≥ 40%, close and redeploy
- Do NOT close due to low IVR — IVR gate is for new entries only

**HOOD $70P — Bullish Thesis**
Rolled from $60P to $70P in April. Thesis intact.
- If Bitcoin > $100K: HOOD is well-positioned; do not disturb
- HOLD regardless of short-term P&L

**CCL — Two Legs**
$25P (Apr 17) and $23P (Apr 24) are a stagger on the same name. Both 1 contract. Fine for IRA.
- Let each leg run independently. HOLD both.

---

### Account B — Action Summary

| Category | Count | Action |
|----------|-------|--------|
| Positions to hold | 13 | All — too fresh for profit targets |
| New entries | 0 | No entries unless IVR ≥ 40 + gates pass |
| Assignments expected | 0 | None this week |
| Emergency action needed | 0 | Account fully funded, no margin pressure |

---

## Combined Week Checklist

```
MONDAY MORNING:
[ ] Account A: check cash to trade → determine which close tier applies
[ ] Account A: check VIX direction → compressing or expanding?
[ ] Check Bitcoin → determines COIN May decision
[ ] Account A: dry_run_order COIN $250P May 15 roll (or close)
[ ] Account A: dry_run_order MSFT $420P May 15 roll
[ ] Account A: BTC AXON $600C Dec 18 (no condition — do it)
[ ] Account A: BTC AXON $620C Jan 27 (no condition — do it)
[ ] Account A: conditional META/LLY closes if cash < $125K
[ ] Account A: after PYPL $45C assignment → sell new CCs on 1,000 remaining shares
[ ] Account B: scan IVR on IBIT if Bitcoin > $90K
[ ] Account B: no other action needed

FRIDAY REVIEW:
[ ] Did PYPL assignment execute? New CCs sold on 1,000 shares?
[ ] Did COIN/MSFT rolls execute at net credit?
[ ] Cash to trade — which band after week's moves?
[ ] Any Account B position approaching 40% profit? (unlikely — all fresh)
[ ] Note any new names approaching IVR ≥ 40 for next week screen
```

---

*Report covers live positions as of 2026-04-25 21:43 ET.*
*Cash to trade fluctuates with VIX — verify Monday morning before executing any conditional closes.*
*Next report: 2026-05-04*
