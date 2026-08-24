# Quarterly Portfolio Direction — India Accounts — Q3 2026 (Aug–Oct)

**Scope: India (ICICI Direct) only** — the NSE/NFO equity + F&O book. Different market,
different regime model, different objective, different strategy shape than the US
portfolio — this document does not blend anything from `quarterly_portfolio_direction_us_2026-Q3.md`,
and nothing here should be read as a US-account recommendation. India's priority is staged
**equity accumulation** at target entry zones (₹10L over 6-12 months, per the documented
India strategy), not a premium-selling wheel — the F&O activity that exists is index-level
(NIFTY/BANKNIFTY/NIFSEL) risk management, not individual-stock options income the way the
US book runs it. Treating the two as one portfolio would blur two genuinely different jobs.

**Generated:** 2026-08-23, from `mcp/reports/india_weekly_report.py`,
`scripts/india_stock_list_review.py`, and `data/india_config.yaml`, using the equity + F&O
statements dropped 2026-08-14 (`7500069840_PortFolioEqtAll.xls`,
`7510078170_FNOPortfolioDetails.csv`) and the `indian-stock-list.xlsx` market-watch export.
Re-run the weekly report after dropping fresher statements before acting on P&L specifics.

**Honest gap:** India does not yet have an equivalent to the US book's 6-indicator,
magnitude-aware crash-probability model — the direction call below relies on
`analysis/india_regime.py`'s simpler VIX + Nifty 50/200-day-MA regime classifier
(BULL/CAUTIOUS_BULL/TRANSITIONING/BEAR_SIDEWAYS, same four-tier scale as the US model, less
instrumented). Worth building a matching sector-sensitivity/crash-probability layer for
India if this quarterly exercise proves useful — not done here.

---

## 1. Market Direction Call — Next 3 Months

**Regime: TRANSITIONING** (trader override active via `INDIA_REGIME_OVERRIDE`) — India VIX
11.3 (sustained <15, genuinely low fear), Nifty 50 above its 50-day MA but below its 200-day
MA. New entries are allowed under this regime, at reduced/Tier-1-only sizing per the
documented regime-driven rules, not full-throttle deployment.

**Base case for the quarter:** the override to TRANSITIONING (rather than the technical
BULL the VIX reading alone might suggest) reflects a deliberate, cautious trader judgment
call already in place — nothing in this review argues for overriding the override. Revisit
whether TRANSITIONING still fits once Nifty reclaims its 200-day MA, which is the
documented technical trigger for a BULL upgrade.

---

## 2. Portfolio Current State

**F&O — action needed now, not a quarter-out concern.** Three index positions were within
21 DTE as of the last weekly check and at profit-target: **CNXBAN, NIFSEL, NIFTY** — all
flagged for roll or close. This is immediate, not a Q3-planning item; resolve before this
quarter's other actions.

**Exit trigger live: YATHOS.** Price 845.50 vs. the 820 trigger, +8% profit on ~150 shares —
genuinely actionable now per the phased exit plan in `data/india_config.yaml`.

**Watch for profit-taking, not new capital:** several current holdings are sitting at the
top of their 52-week range — **SOLARINDS, PARAS, AUROPHARMA, IDEA** all in the 88-96%
range-position band. These aren't in trouble, but they're priced for a lot of good news
already; this is the opposite problem from the US book's concentration risk — here it's
"don't mistake an extended existing winner for a reason to add more."

**New-entry candidates, both sources checked:**
- **KAYNES** (curated `india_config.yaml` watchlist) — trading below its planned ₹3,800-4,000
  entry zone at ₹3,660; thesis is India EMS/AI-hardware supply chain, defence electronics.
  Planned strategy already defined: 2 tranches, 10 shares near 4,000, 10 more on a dip to 3,800.
- **ITC** (broader `indian-stock-list.xlsx` scan) — 2% of its 52-week range, RSI 38, not
  currently held at all. The strongest technical signal found this quarter across either
  source.
- **POWERGRID** (same scan, already held) — 18% of range, RSI 20 — a real add-more signal on
  an existing position, not a fresh name.

---

## 3. What's Different About This Book (vs. the US Quarterly Plan)

- **No strategy-attribution equivalent exists yet.** The US book's "which strategy actually
  worked" analysis (short puts vs. covered/naked calls vs. strangles) doesn't map cleanly
  here — India F&O is index-level hedging, not a stock-by-stock premium-selling engine, so
  there isn't a comparable per-name strategy classification to run. If that changes (e.g.
  individual-stock F&O activity grows), this is a real gap worth closing.
- **No sector-concentration figure has been computed for the India equity book** the way the
  US quarterly plan tracks Technology at 36%. The documented India strategy is explicitly
  thematic (Defense, Power, Healthcare, Banking, Infrastructure, Consumer/Fintech) — worth
  checking actual current ₹ concentration by theme before assuming the intended
  diversification is what's actually held.
- **The objective itself is different in kind.** The US side has one number ($1.2M/year) and
  a live realized-P&L tracker. India's stated target is a 25% annualized return via staged
  deployment — there's no equivalent "% of $1.2M objective, on pace for $X/year" tracker for
  India in this codebase yet.

---

## 4. The 3-Month Phased Plan

**Month 1 (August–September): clear the F&O queue, take the live exit, start staged entries.**
- Roll or close CNXBAN, NIFSEL, NIFTY (all within 21 DTE, at profit target) — this is
  overdue, not a month-1 target.
- Execute the YATHOS exit trigger.
- Begin the KAYNES 2-tranche entry (10 shares near current price, since it's already below
  the 4,000 leg of the plan) and open a position in ITC given the strength of its oversold
  signal.
- Do NOT add to SOLARINDS, PARAS, AUROPHARMA, or IDEA this month — extended, not attractive
  entries regardless of conviction in the underlying thesis.

**Month 2 (September–October): confirm the regime call, add POWERGRID, check theme balance.**
- Re-check whether Nifty has reclaimed its 200-day MA — if so, this is the trigger to
  reconsider the TRANSITIONING override toward BULL sizing.
- Add to POWERGRID per its add-more signal, sized within whatever the regime allows that month.
- Do the ₹-by-theme concentration check flagged in §3 — confirm the actual book still matches
  the intended Defense/Power/Healthcare/Banking/Infrastructure spread, not just the stated plan.
- Re-run `scripts/india_stock_list_review.py` fresh against a new market-watch export — this
  quarter's ITC/KAYNES signals will have moved.

**Month 3 (October–November): reassess the ₹10L staged-deployment pace.**
- Check actual capital deployed this quarter against the 6-12 month ₹10L plan — behind,
  on track, or ahead changes what month 4-6 should look like.
- Revisit SOLARINDS/PARAS/AUROPHARMA/IDEA specifically — if they're still at 52-week highs,
  that's a genuine profit-take conversation, not just a "don't add" one.
- Re-run this process for Q4, and consider whether it's worth building the sector-
  concentration and strategy-attribution equivalents flagged as gaps in §3.

---

## 5. Open Items / Not Yet Built

- No India equivalent of the crash-probability/sector-sensitivity model exists — flagged in
  the header, repeated here since it's the single biggest structural gap versus the US side.
- No ₹-denominated theme-concentration tracker exists for the equity book.
- No India strategy-attribution equivalent exists (not clearly needed yet, given the
  index-level-only F&O activity, but worth revisiting if that changes).
