# Portfolio-1 Monthly Review — August 2026

**Source:** `data/positions/arch/Portfolio-1 2026-06-26 (1).xlsx` (73 names) — the canonical `data/portfolio/` copy is stale (2026-04-25); this newer file was sitting unpromoted in the archive folder. Recommend moving it to `data/portfolio/` as the new canonical copy.

**Data pulled live 2026-08-01:** current price, 1yr RSI(14), 52-week range position, sector, P/E, IV Rank — via `scripts/portfolio1_monthly_review.py`. BRK.B failed to fetch (Yahoo ticker format issue, needs `BRK-B`) — 72/73 names covered.

---

## 1. Regime Filter

**Current regime: BULL** (VIX sustained <20, S&P 500 above both 50d and 200d MA). Per the Entry Strategy by Regime table, BULL allows active entries across all tiers — the binding constraint this cycle is the **IV Rank ≥40 gate**, not tier restriction.

Of 72 valid names: **47 pass Gate 1 (IVR ≥40)**, 25 are blocked (IVR too low right now — OKLO 18.6, MP 22.4, CCJ 6.0, ALB 7.0, LAC 2.7, RGTI 30.5, STNE 4.6, TWLO 19.1, PL 29.1, ROKU 0.0, and others).

## 2. 52-Week Range Positioning (bottom 25% = potential entries)

19 names sit in the bottom quartile of their own 52-week range:

| Ticker | Pos-in-range | RSI | IVR | Gate | Already held? |
|---|---|---|---|---|---|
| SPCX | 0.0% | 19.2 | n/a | no data | No |
| OKLO | 1.4% | 36.7 | 18.6 | ❌ blocked | No |
| COIN | 2.1% | 44.1 | 47.2 | ✅ pass | **Yes — already sector-heavy** |
| KTOS | 3.1% | 49.3 | 46.6 | ✅ pass | **Yes — already Tier 1 held** |
| LAC | 4.3% | 38.5 | 2.7 | ❌ blocked | No |
| RGTI | 4.7% | 48.1 | 30.5 | ❌ blocked | No |
| MP | 5.4% | 32.8 | 22.4 | ❌ blocked | No |
| HDB | 5.9% | 27.9 | 50.0 | ✅ pass | No — **new candidate** |
| TSLA | 6.7% | 18.1 | 96.3 | ✅ pass | No — **new candidate** |
| NFLX | 7.0% | 43.4 | 69.0 | ✅ pass | Yes — already held |
| APP | 7.9% | 32.8 | 28.5 | ❌ blocked | Yes — already held |
| META | 11.7% | 22.9 | 96.2 | ✅ pass | Yes — already held |
| UBER | 12.9% | 39.4 | 78.9 | ✅ pass | Yes — already held |
| QBTS | 16.0% | 47.9 | 49.0 | ✅ pass | Yes — already held |
| IONQ | 17.7% | 44.2 | 40.3 | ✅ pass | Yes — already held |
| STNE | 18.0% | 55.0 | 4.6 | ❌ blocked | No |
| TCOM | 18.3% | **72.2** | 67.6 | ✅ pass technically | No — **caution, see below** |
| RKLB | 23.0% | 36.5 | 46.8 | ✅ pass | Yes — already held |
| CCJ | 25.0% | 43.2 | 6.0 | ❌ blocked | Yes — already held |

**Notable divergence — TCOM:** sits in the bottom-quartile by 52-week range but its 14-day RSI is 72.2 (overbought) — it fell hard earlier in the year and has since rallied sharply in recent weeks. The range position alone would flag it as "cheap," but current momentum says it's run hot short-term. Matches the same caution flag from yesterday's direct check.

## 3. Thesis Changes / Flags

- **PYPL is still sitting in this universe file** despite being on your `PERMANENT_EXITS` list (thesis broken, no re-entry). This is a data-hygiene gap, not a new thesis change — flagging for removal below.
- No other names in this universe match `PERMANENT_EXITS` (MRNA, SMCI, INMD not present in this list).
- Fundamental/earnings-trend data (analyst ratings, quant scores) were blank in the source file — this review is technical/IVR-based only. A full thesis-quality pass would need an actual data refresh from wherever this export normally comes from.

## 4. Top New-Entry Candidates (bottom-quartile range + IVR≥40, not already held)

Only **3 names** genuinely clear both filters as *fresh* (not already in your book) — most of the bottom-quartile list is either IVR-blocked or already held:

**TSLA** — $311, RSI 18 (deeply oversold), IVR 96 (richest in the whole universe)
- CSP $260P / 92 DTE, ~$1,801/contract (2.26%/mo), timing 61/100
- ⚠️ 3 flags: THIN_MARGINS, LOW_MOAT, CHINA_EXPOSURE — size at half or less per your own flag-response rule

**HDB** (HDFC Bank ADR) — $24, RSI 28 (oversold), IVR 50 — **passed on.** ~$60/contract (0.83%/mo) doesn't clear the collateral-vs-premium bar; trader call, dropped.

**TCOM** — WATCH only, not ENTER NOW (RSI 72 overbought despite low 52w-range position + CHINA_EXPOSURE flag). Not a real candidate this cycle — noted for next month if RSI cools. See China-exposure basket note below.

Only TSLA is a genuinely new, currently-actionable candidate this cycle — not a "Top 5," because the data doesn't support 5 real candidates. Padding the list would misrepresent what's actually there.

## 5. Names to Remove from Universe

- **PYPL — keep tracked, do not remove yet.** Per trader: stays in the universe until all PYPL positions are fully exited, then remove. Matches the existing persona rule ("accelerate exit via CCs, remove from active tracking after full exit") — this review's earlier "remove now" recommendation was premature.

No other names confirmed for removal — the "loser identification" criteria (thesis broken / >40% below 52w high with no catalyst / 3+ quarters underperformance / better name available) need earnings-trend and analyst data this file doesn't currently carry. Several names (OKLO -77.7% off high, SMR -84.2%, KTOS -64.3%, COIN -62.2%) are deep off their highs, but per your own rule price alone isn't a removal trigger — would need a second criterion confirmed before recommending removal.

---

## Summary for turnover tracking

- **Remove list:** none yet — PYPL pending removal after full position exit (not this cycle)
- **Add list (new watch, act-ready):** TSLA (HDB passed on — premium didn't clear the bar)
- **Watchlist (promising but blocked/cautioned):** TCOM (overbought caution), OKLO/MP/RGTI/LAC (IVR-blocked, revisit if premium richens)
- **Housekeeping:** promote the 2026-06-26 file to `data/portfolio/` as canonical; source file needs a refresh — analyst/quant rating columns were empty

## China-Exposure Basket — Divergence Check (2026-08-01)

Trader's idea: rather than treating CHINA_EXPOSURE as a uniform red flag, look at relative divergence across China-linked names for a signal. Checked BABA, JD, TCOM, and CXMT.

**CXMT is not tradeable in this system** — no Yahoo/US quote data at all (tried CXMT, CXMTF). This is almost certainly ChangXin Memory Technologies, listed on Shanghai's STAR Market — no US ADR, no US options. Can't be part of an actionable options strategy here. If the intent was China-semiconductor exposure specifically, a US-listed proxy (e.g., an ETF with fab/memory exposure) would need separate vetting — flag if you want that checked.

**BABA vs JD vs TCOM — the divergence is real:**

| Ticker | Held? | 52W range position | RSI(14) | Read |
|---|---|---|---|---|
| JD | Yes (call) | 71.2% (near highs) | **88.6** (highest RSI in the entire 72-name universe scan) | Most extended by far — already flagged CLOSE NOW today independently |
| BABA | Yes (put) | 29.0% (lower in range) | 65.4 (mild) | Overbought but nowhere near JD's extreme |
| TCOM | No | 18.3% (bottom quartile) | 72.2 (overbought) | Cheap by range, but recently ran hard — matches yesterday's WATCH-only call |

**Verdict: yes, this makes sense, and it's not a new finding — it's independent confirmation of what today's heat scan already flagged.** JD's RSI 88.6 is the single most extreme reading across the whole universe pull; it's already sitting in your CLOSE NOW list for exactly that reason. BABA is overbought but far milder — a hold, not an action item. TCOM's low range-position looks attractive on the surface but its RSI says it already ran — same caution as before, not a new entry today. The basket logic checks out: JD is the one actually needing action, and the shared China exposure isn't creating a hidden opportunity so much as confirming JD is the outlier worth prioritizing over the other two.
