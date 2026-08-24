# AI Capex Risk Review Skill

Re-runs the two-phase (2000-style valuation crack → 2007-style credit unwind)
AI capex stress analysis against the *current* portfolio and *current* market
conditions, and republishes the Circular Financing Playbook artifact with an
updated dial. Not cron-schedulable like `weekly-actions` — it needs live web
research judgment (credit spreads, IPO status, private-credit news), not just
a script re-run. Run it on demand, ideally at the checkpoint dates already
listed in the playbook's Section 08 tracking table.

## Invocation

```
/ai-capex-risk-review
```

## What it does

Refreshes every input the playbook's probability ladder and 90-day capital
dial depend on, then decides which of the four dial states currently applies
(base case 30/70, Tier 1 fired 15/85, trigger delayed 35-40/60-65, Tier 2
fired 0/100) and republishes the artifact reflecting that.

## Source artifact

- **Local file:** `logs/circular_financing_playbook.html`
- **Published URL:** https://claude.ai/code/artifact/37ec3109-b6f8-46ca-b939-66ef96aca184
- Always update via `Artifact` with `url` set to the link above so it
  redeploys to the same URL — never republish without `url` from a fresh
  session, or it creates a duplicate artifact instead of updating this one.

## Execution flow

1. **Re-pull the current portfolio.** Run the latest `unified_master_report_production.py`
   (or read the most recent `logs/unified_master_report_*_daily_production.txt`)
   to get current balances, position count, sector concentration (Technology
   %), and conviction tiers. Confirm whether ALAB/LITE/MU/PLTR/TSM/ASML/APH
   positions still match Section 06/08's assumed sizes — note any drift.

2. **Re-check the macro model, with the known caveat.** Pull live SPX/VIX and
   run `MacroRiskAnalyzer.analyze_risk()` from `mcp/analysis/macro_risk_analyzer.py`.
   Its FRED API key is dead (HTTP 400) — always cross-check real HY OAS via
   `https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2` (value ×
   100 = bps) rather than trusting the model's own credit-spread signal.

3. **Re-check the four Tier-1 leading indicators** (WebSearch, not scripted):
   - Oracle / CoreWeave credit spread or rating news
   - Anthropic IPO status (pricing, delay, valuation chatter) — the closer to
     its October 2026 date, the more this matters
   - NBIS/CRWV relative performance vs. NVDA/broader semis
   - Breadth level (from the macro model) vs. the 50% alert line

4. **Re-check the two Tier-2 gate conditions** (WebSearch): CoreWeave (already
   Ba3/junk) taking a further downgrade, breaching a covenant, or failing a
   refinancing, or a private-credit fund (Blackstone, Blue Owl, Apollo, Ares)
   gating redemptions or marking down data-center loan NAVs. If either
   fires, the dial goes straight to 0/100 regardless of what Tier 1 shows.

4b. **Re-check the Tier CR portfolio-wide credit exit gate** (WebSearch).
   This is independent of the Phase 1/2 dial and can fire on any of the 92
   held tickers, not just the AI-adjacent ones. The trigger is an ACTUAL
   rating-agency action (a downgrade or a formal negative-outlook
   placement) — NOT a thematic warning or watch-list mention. Confirmed
   example of the distinction (2026-08-24): Moody's named Microsoft,
   Amazon, Alphabet, Meta, Oracle, and CoreWeave as credit-quality "under
   threat," but Moody's itself said the first four are unlikely under
   imminent downgrade threat, and only Oracle has an actual rating action.
   That commentary was NOT this gate firing. Actively check every review:
   the Moody's six, the neocloud cluster (NBIS, HUT, RIOT), and AVGO. For
   the rest of the book, no dedicated ratings feed exists — treat a sharp
   conviction/analyst-rating drop on any position as a cue to check for a
   credit angle specifically, rather than assuming routine drag. If this
   gate fires on ANY ticker: stop new premium there immediately, close or
   don't-renew existing short puts rather than holding to expiry, and if
   equity is held via assignment, reassess the thesis against the
   downgrade's specific rationale.

5. **Re-verify fundamentals drift** on the eight named tickers (ALAB, LITE,
   MU, PLTR, TSM, ASML, APH, plus the avoid-list names NBIS/CRWV/RKLB/OKLO/SPCX)
   via yfinance — PE/forward PE, D/E, RSI, 52-week range position, analyst
   upside. Flag anything that has moved out of the risk tier it was assigned
   last review (e.g., MU's CXMT caveat resolving one way or the other after
   an earnings print).

6. **Decide the dial state** from steps 2-4: base case / Tier 1 fired /
   delayed-favorable / Tier 2 fired. State the reasoning plainly — which
   specific indicator(s) drove the call.

7. **Update `logs/circular_financing_playbook.html`**: append a new evidence
   ledger row for anything materially new, update the probability ladder if
   the evidence has shifted, fill in the next open row of the Section 08
   tracking table (actual split, deviation, premium collected, action), and
   adjust Section 08's bucket composition table if the dial state changed.

8. **Republish** via `Artifact` with `url` pointing to the link above.

## Standing rules this skill must not violate

- **No long options, ever.** Every structure is a cash-secured short put.
  Never suggest long puts/calls or short call credit spreads as a "hedge" —
  both were tried and explicitly rejected this session. Protection happens
  through name selection, delta, size, and DTE only.
- **Bull-regime bias against calls.** Do not reintroduce call-selling of any
  kind (naked or spread) while the regime reads BULL — this book's own data
  shows call legs underperforming put legs.
- **ORCL stays off the list entirely** — too binary/already-moved to trade in
  either direction, not just restructured.
- **Phase 2 never gets funded speculatively.** Aggressive-bucket sizing or
  new AI-adjacent quality positions only expand on evidence (Tier 1 easing),
  never in anticipation of it.
