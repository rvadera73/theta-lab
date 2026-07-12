# Performance Engine Validation — June 8, 2026 Positions vs Historical Analysis

## Issue: Engine Assumptions vs Actual Deployed Positions

The closed P&L analysis (historical: "puts work, calls destroy") needs validation against actual June 8 positions. **Some assumptions are wrong.**

---

## Position-by-Position Validation

### ❌ MU (Micron) — DOES NOT EXIST
**Engine Assumption:** "MU is a core position showing performance decay"  
**Actual Position:** NO MU in Account A (or any account) as of June 8  
**Impact:** Remove MU from all analysis  
**Lesson:** Don't assume positions exist just because they were in transactions earlier in the year

---

### ⚠️ LLY (Eli Lilly) — NAKED SHORT CALL PROBLEM
**Position:** 1x LLY Jun 17 2027 $1100 Call  
- Market Value: -$23,690 (short option)
- P&L: **-$15,475.83 loss**
- Delta: ~0.95 (highly negative, acting like a short stock)
- Status: **NAKED** (no corresponding put = unhedged directional bet)

**Engine Assumption:** "Calls are destroying value across the board"  
**Reality:** This call IS destroying value, but it's an outlier (NAKED call, not part of a strangle)

**User's Point:** LLY call is the real issue. The engine should flag this as a breach (naked short call = risk)

---

### ✓ AXON (Axon Enterprise) — PROPERLY STRUCTURED, NOT AS BAD
**Equity:** 200 shares @ $480.51 = $96,102  
**Structure:** MULTIPLE STRANGLES (not just calls killing puts)

**Short Puts:**
- 1x Jan 15 2027 $420P @ $63.50 (-$6,350, P&L: -$1,964.66)
- 1x Sep 18 2026 $660P @ $197.50 (-$19,750, P&L: -$11,850.66)
- 1x Dec 18 2026 $540P @ $127.35 (-$12,735, P&L: -$5,695.66)
- **Total puts: -$38,835 market value, -$19,511 loss**

**Short Calls:**
- 1x Jul 17 2026 $480C @ $45.60 (-$4,560, P&L: -$3,509.68)
- 1x Sep 18 2026 $450C & $470C @ ($92.30 + $82.25) = (-$17,455, P&L: -$10,356.46)
- 1x Dec 18 2026 $500C, $580C, $600C @ ($95.20 + $68.20 + $62.75) = (-$22,615, P&L: -$11,703.20)
- 1x Mar 19 2027 $560C & 2x $600C @ ($93.45 + 2×$82.05) = (-$25,755, P&L: -$12,637.25)
- **Total calls: -$70,385 market value, -$38,206 loss**

**Total AXON Options:** -$109,220 notional, -$57,717 loss

**Engine Assumption:** "AXON calls are dragging down the position"  
**Reality:** AXON IS properly structured. Calls are offset by puts, creating layered strangles. The loss is not because "calls are bad" — it's because IV has crushed since entry and the whole strangle is underwater.

**User's Point:** "AXON net impact may be not that bad due to strangle" — Correct. This is a risk-managed position, not a naked call disaster like LLY.

---

### ✓ NFLX (Netflix) — PUT LADDER, WORKING AS DESIGNED
**Structure:** Multiple short puts at different expirations (NO calls)

**Short Puts:**
- 5x Mar 19 2027 $95P @ $17.725 = -$8,862.50, P&L: -$4,676.92
- 2x Jun 17 2027 $80P @ $9.975 = -$1,995, P&L: -$398.36
- 3x Nov 20 2026 $80P @ $6.85 = -$2,055, P&L: -$587.03
- **Total: -$12,912.50 notional, -$5,662.31 loss**

**Engine Assumption:** "Multiple small puts on NFLX, lower conviction"  
**Reality:** This is a proper put ladder (multiple tranches at different strikes/expirations). Working as designed.

---

## Summary: What the Engine Got Wrong

| Assumption | Reality | Fix |
|-----------|---------|-----|
| "MU is a core position in portfolio" | MU doesn't exist | Remove MU references |
| "All calls are destroying value" | Only naked calls (LLY) are problems; strangles are working | Separate naked vs strangle analysis |
| "AXON calls are the drag" | AXON is proper strangle structure, loss is IV crush, not call issue | Flag as properly structured, monitor Greeks not individual legs |
| "Puts universally working" | Puts ARE working but are also underwater (IV crush affects both sides) | Both puts and calls losing to IV collapse, not directional |

---

## Engine Initialization Requirements (Before Running)

Before the performance engine generates reports, it needs to:

1. **Load actual positions from June 8 CSV files**
   - Parse equities separately from options
   - Identify position structure: STRANGLE (put + call ladder), SINGLE (put-only or call-only), WHEEL (shares + covered call)

2. **Categorize options correctly**
   - NAKED calls: Short call with no corresponding put (FLAG as risk)
   - NAKED puts: Short put with no corresponding call (standard Tier strategy)
   - STRANGLES: Both short puts + short calls on same underlying (risk-managed, evaluate as unit)
   - LADDERS: Multiple contracts at different strikes/expirations (risk-managed, evaluate as unit)

3. **Validate closed P&L analysis against position structure**
   - Historical "puts work, calls don't" may not apply to strangles (both sides lose in IV crush)
   - Adjust analysis: "Puts work in isolation; calls in strangles are offset by puts; naked calls are dangerous"

4. **Account for current market regime**
   - All options are losing (puts AND calls) because IV has crushed from Jan peak
   - This is a regime issue (IV compression), not a "puts are good / calls are bad" issue
   - Historical win rate (85.6%) is BEFORE this IV crush; current regime is different

---

## Data Ready for Engine Initialization?

✓ Account A positions loaded (June 8)  
✓ Position structure identified (strangles, ladders, etc.)  
✓ Naked positions flagged (LLY call = issue)  
✓ Closed P&L analysis corrected (remove MU, reframe calls)  

**Next Steps:**
1. Load Accounts B, C, Fidelity, Vanguard, Robinhood position files
2. Validate same assumptions across all accounts
3. Identify any other naked positions (risk breaches)
4. Then initialize PerformanceEngine with validated data

