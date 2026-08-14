# Portfolio-1 Monthly Review — August 2026 (88 names)

**Source:** `data/portfolio/Portfolio-1 2026-08-14.xlsx` (88 names, now canonical — the June file has been promoted/superseded per last review's recommendation). **Data pulled live 2026-08-14** via `scripts/portfolio1_monthly_review.py` → `logs/_p1_merged.csv`. BRK.B failed to fetch (recurring Yahoo ticker-format gap — needs `BRK-B`, not fixable here) — **87/88 real coverage**.

---

## 1. Regime Filter

**Current regime: BULL**, confirmed live via `mcp/analysis/regime.py` `detect_regime()` (same function the MCP `check_market_regime` tool wraps): VIX 14.5 (sustained <20), S&P 500 7792 above both 50d MA (7513) and 200d MA (7075), 3 bull signals / 0 bear signals, no CAUTIOUS_BULL downgrade triggered (SPX is 10.1% above 200d MA, under the 12% stretch threshold). Same regime call as June — no change.

Binding constraint is still the **IVR ≥40 gate**, not tier restriction. Of 85 names with usable IVR data (SPCX and SKHY have none — Yahoo/options-chain gap), **56 pass Gate 1**, 29 are blocked.

## 2. 52-Week Range Positioning (bottom quartile = pos_in_range < 25)

**14 names** sit in the bottom quartile (vs. 19 of 73 in June — a smaller *share* of a larger universe). "Already held?" is **not answerable from this file** — it needs cross-reference against actual open positions, not a guess. Where June explicitly named a ticker as held, that's carried forward as a note; everything else is unconfirmed.

| Ticker | Pos-in-range | RSI | IVR | Gate |
|---|---|---|---|---|
| STNE | 0.0% | 30.4 | 20.6 | ❌ blocked |
| HDB | 1.6% | 50.5 | 89.5 | ✅ pass |
| COIN | 3.0% | 34.9 | 30.5 | ❌ blocked |
| APP | 3.7% | 28.3 | 47.6 | ✅ pass |
| SMR | 4.5% | 59.3 | 40.5 | ✅ pass |
| OKLO | 6.7% | 56.4 | 39.0 | ❌ blocked |
| LAC | 10.7% | 75.8 | 6.6 | ❌ blocked |
| TCOM | 12.9% | 50.7 | 18.3 | ❌ blocked |
| RGTI | 14.0% | 65.7 | 33.7 | ❌ blocked |
| NFLX | 17.7% | 72.2 | 50.9 | ✅ pass |
| BROS | 18.7% | 21.1 | 91.9 | ✅ pass |
| BWXT | 19.1% | 46.7 | 43.9 | ✅ pass |
| TSLA | 22.7% | 70.2 | 75.8 | ✅ pass |
| KTOS | 23.7% | 76.6 | 44.6 | ✅ pass |

Known-held per June's own notes: **NFLX, APP, COIN, KTOS**. **STNE, SMR, OKLO, LAC, TCOM, RGTI, BROS, BWXT, TSLA, HDB** — held status genuinely unknown from this file; needs the account position export.

## 3. Notable Swings vs. June (the important part)

| Ticker | June (pos/RSI/IVR/gate) | Now (pos/RSI/IVR/gate) | What changed |
|---|---|---|---|
| **TSLA** | 6.7% / 18.1 / 96.3 / pass | 22.7% / 70.2 / 75.8 / pass | **Full RSI reversal** — deeply oversold → overbought. IVR still rich but down ~21pts. The "oversold bounce" thesis that made TSLA June's cleanest candidate no longer applies. |
| **HDB** | 5.9% / 27.9 / 50.0 / pass (passed on, thin premium) | 1.6% / 50.5 / 89.5 / pass | **IVR nearly doubled** (50→89.5) while still bottom-quartile. RSI cooled from oversold to neutral. Worth re-underwriting the $/contract math that killed it last time. |
| **TCOM** | 18.3% / 72.2 / 67.6 / pass-technically (overbought caution) | 12.9% / 50.7 / 18.3 / blocked | RSI cooled exactly as flagged ("revisit if RSI cools") — but **IVR collapsed** 67.6→18.3, crossing below the gate. Cooled and now un-tradeable; net no better as a candidate. |
| **COIN** | 2.1% / 44.1 / 47.2 / pass | 3.0% / 34.9 / 30.5 / blocked | **Gate reversal** — lost IVR≥40. |
| **KTOS** | 3.1% / 49.3 / 46.6 / pass | 23.7% / 76.6 / 44.6 / pass | RSI flipped neutral→overbought (49.3→76.6) while nominally still bottom-quartile — same TCOM-style contradiction: cheap by range, but has run hot. |

Additional gate-crossings found scanning the rest of the June-cited set: **MP** (IVR 22.4→40.3, blocked→**pass**; RSI 32.8→77.3, now overbought), **APP** (IVR 28.5→47.6, blocked→pass), **RKLB** (IVR 46.8→32.7, pass→blocked). **STNE** now sits at literally **0.0%** of its range (new 52-week low), RSI cooling toward oversold (55.0→30.4) but IVR still thin (4.6→20.6, still blocked). **JD** — the June "CLOSE NOW" name (RSI 88.6, most extreme in the whole universe) — has cooled hard to RSI 37.5 and dropped from 71.2% to 34.2% of range, consistent with that call having been acted on. **BABA** is roughly flat (65.4→63.2 RSI).

## 4. Universe Growth: 73 → 88 (+15, 0 removed)

Confirmed by direct diff of both source files via `pd.ExcelFile(path, engine='calamine').parse('Summary')`. **Added:** ASML, ASTS, BA, BLK, BMY, CRWV, ETN, JPM, MA, MPC, NBIS, REGN, SKHY, SLB, WMT. **Removed: none** — this is pure net growth, not turnover. None of the 15 new names are currently bottom-quartile; **ASTS** is the one to watch (47.5% off its high, IVR-blocked at 28.8).

## 5. Top New-Entry Candidates

Filter: bottom-quartile + IVR≥40 + not already known-held (§2). That leaves HDB, SMR, BWXT, TSLA, BROS — but not all clear the same bar on quality:

- **BROS** — $52, RSI **21.1** (the only sub-25 RSI in the entire 88-name universe), IVR 91.9, 18.7% of range. Genuinely strong, fresh candidate.
- **HDB** — $23, RSI 50.5 (neutral, no longer oversold), IVR 89.5 (nearly 2x June's 50.0). Worth a fresh trader look at premium-vs-collateral now that richness has changed materially — not an automatic yes, needs the same $/contract check that killed it in June.
- **TSLA** — technically still passes but RSI flipped to overbought (70.2); the thesis that made it June's candidate is gone. Watch, not enter.
- **SMR / BWXT** — IVR barely clears the gate (40.5 / 43.9), RSI neutral not oversold. Weak conviction technically, not compelling entries.

**2 real candidates this cycle: BROS (new) and a re-look at HDB** — not 5. TSLA is a watch-only carryover, downgraded from June's top pick.

## 6. Names to Reconsider/Remove

- **PYPL** — still in the universe file, and now correctly flagged `permanent_exit=True` in the data itself (June's "data-hygiene gap" appears fixed at the source). Same call as June: keep tracked until fully exited, then remove — needs trader confirmation of current PYPL position status.
- **STNE** — now at an outright 52-week low (0.0% range position) with IVR still only 20.6 — can't even generate meaningful income while waiting. Two converging technical negatives, but no thesis/analyst data in this file to confirm a real break — flag for a manual thesis check, not an automatic remove.
- **LAC** — IVR 6.6 now vs. 2.7 in June: two straight reviews with near-zero options-premium interest despite a large RSI swing (38.5→75.8). This reads less like "wait for a thesis catalyst" and more like a structural question of whether LAC belongs in an income-options universe at all.
- No hard removals recommended — same standard as June: technical weakness alone isn't sufficient without a thesis-break or analyst-data confirmation this file doesn't carry.

---

## Summary for Turnover Tracking

- **Remove list:** none confirmed — PYPL pending post-exit removal (unchanged from June); STNE/LAC flagged for manual thesis review.
- **Add list (new watch, act-ready):** BROS (new). HDB re-opened for a fresh premium look. TSLA downgraded to watch-only (thesis broken by RSI reversal).
- **Watchlist:** KTOS/TCOM (range-cheap but overbought — same contradiction pattern), MP/APP (newly crossed above the IVR gate), OKLO/RGTI/COIN (still IVR-blocked).
- **Housekeeping:** exact +15/-0 ticker diff confirmed against June's source file; "already held" status for 10 of 14 bottom-quartile names still needs the account position export — don't guess it from this file.
