# Seeking Alpha Weekly Theme Scan

**Cadence:** Every Friday. Manual/Claude-driven — like `/ai-capex-risk-review`,
this needs live web research judgment and cannot run inside the automated
Python report pipeline.

## Process

1. `WebFetch` https://seekingalpha.com/ — pull trending/most-active tickers,
   featured sectors, and headline stories.
2. For each theme/ticker that is EITHER already held (any account) OR
   plausibly investable under the standing screen (quality + momentum,
   index/liquid names, no long options), run 1-2 `WebSearch` queries to get
   real substance behind the headline, not just the headline itself.
3. Cross-reference every finding against the current quarterly plan
   (`data/us_quarterly_plan_2026_q4.yaml`) and the AI Capex Risk Tracker
   buckets (Section 6.6 of the daily report: HIGH_RISK_BUCKET, QUALITY_AI_BUCKET,
   AVOID_LIST) — a theme only becomes an action if it changes something in
   one of those, not just because it's trending.
4. Classify each relevant finding into one of three outcomes:
   - **No action** — consistent with existing tracking (e.g. AI capex
     headline numbers matching the Circular Financing Playbook's own
     baseline — confirmation, not escalation).
   - **Flag for next quarterly review** — a structural shift worth
     reconsidering at the next bucket rebalance, not urgent enough to act
     on immediately off one data point (e.g. a name's risk-bucket
     classification looking stale given new fundamentals).
   - **Concrete weekly action, sized** — something actually actionable this
     week, given in realistic percentage-point terms against available
     capacity (e.g. "5-6 of 10 available covered-call contracts," not
     "buy MU").
5. Write the week's findings to `data/seekingalpha_theme_state.yaml`
   (same pattern as `data/tier_cr_state.yaml` for the AI Capex Risk
   Tracker): `last_check_date` (today), a `findings` list (one entry per
   relevant ticker/theme: `ticker`, `summary`, `action`), and
   `action_items_open` (anything still pending). `unified_master_report_production.py`'s
   Section 6.9 reads this file on every scheduled run and self-flags
   staleness after 10 days — this is what makes a finding persist across
   report regenerations instead of living only in one week's dated log
   file (the prior approach, confirmed lost the moment that report
   regenerated). Also append to this skill's own running log below, for
   the narrative history a flat YAML doesn't carry well.
6. Never let this override the standing rules already in force (net-put
   freeze status, no naked calls outside Account A's covered book, Tier-CR
   exclusion list) — a trending theme is an input to weigh, not a reason to
   bypass an active constraint.

## Running Log

### 2026-09-01 (first run)

- **CRM** — Salesforce/Anthropic "Claudeforce" partnership (Aug 26-27):
  $5B invested in Anthropic, $300M planned 2026 token spend, Claude
  becoming Salesforce's default reasoning engine, open beta launching
  Sept 2026. Real structural catalyst on an already-held name (Account A,
  200sh, several calls under active management). **Action: no new low-strike
  calls this week — let existing ITM calls execute as planned, don't cap
  upside into a real catalyst.**
- **AI capex exhaustion** — hyperscaler spend $775-800B in 2026, ~$1.15T
  cumulative 2025-27, matching (not exceeding) the Circular Financing
  Playbook's existing figures. "Four buyers control a capex pool larger
  than the entire semiconductor industry's annual capex" — real pricing
  power now, real cliff risk if one buyer pulls back. **No Tier CR trigger
  this week — confirmation, not escalation. Standing avoid-list unchanged
  (CRWV, ORCL, HUT, RIOT).**
- **MU** — HBM4 in high-volume production, entire 2026 HBM supply sold out
  with pricing locked, capex raised 25% to $25B+, 16 take-or-pay contracts
  through 2030 (~$100B minimum revenue). Structural shift from
  cyclical/commodity toward contracted revenue — attacks MU's classic
  memory-bust downside risk directly. Currently sits in HIGH_RISK_BUCKET
  (30% target, with ALAB/LITE/PLTR) rather than QUALITY_AI_BUCKET.
  **Flag for next quarterly bucket review — not an immediate reclass off
  one data point. Existing MU 720P (Nov 2026) short put looks
  better-supported, not worse.**
- ~~**NIO** — identified covered-call gap (1,000sh, Account C + Fidelity,
  zero calls written), recommended writing covered calls on 5-6 of 10
  contracts.~~ **RETRACTED 2026-09-01: false.** The 1,000sh figure came
  from `data/positions/portfolio_equity_positions.yaml`, a static
  reference file dated 2026-05-31 (three months stale) that the equity
  loader (`open_positions_loader_v2.py::_load_equity_positions_from_yaml`)
  reads FIRST, ahead of any live transaction data -- confirmed by the
  trader that neither account actually holds NIO shares or puts. Fixed by
  removing the two stale NIO entries from that YAML. Root-cause note: the
  live-computation fallback (`_track_equity_positions`) that's supposed to
  kick in when the YAML is absent returns EMPTY for Account A entirely
  (tested directly) -- so the YAML, despite being stale, is still the only
  working equity data source for that account. Any other entry in that
  file could be similarly stale; this was only caught because the trader
  spot-checked one name. Treat every equity-derived finding from before
  2026-09-01 (covered-call gap scans, coverage checks) with that in mind.

### 2026-09-18 (second run -- 17 days late, missed the 09-08/09-15 cadence)

- **NFLX** -- Wells Fargo downgraded to Underweight, PT $80 -> $57, citing
  engagement decline (-8% viewing hours) and a weak content slate (-21% YoY
  top-100-originals hours). Real, credible catalyst -- 4th straight down
  session, 3rd consecutive weekly decline. **Concrete action, sized:**
  Account A's 2 ITM cash-secured NFLX puts ($77.50P x2 Nov 20, $80P x3 Nov
  20) -- already flagged separately this week as low-premium (<$500/contract)
  -- now carry a real fresh bearish catalyst on top of already-poor
  risk/reward. Recommended an early close/roll review rather than waiting
  for expiry. The naked NFLX calls in the same account move further OTM on
  this news, not worse.
- **MU** -- confirms and strengthens the 09-01 flag: HBM4 capacity sold out
  through 2027 (likely 2028), $100B+ logged orders, demand ~50% over
  capacity per the CEO. Stock +~200% YTD, $1.1T market cap. Q4 earnings
  2026-09-30 is a real near-term event. **Flag for next quarterly bucket
  review (HIGH_RISK_BUCKET -> QUALITY_AI_BUCKET), conviction now stronger.**
- **AVGO** -- the $370B AI-chip debt-financing risk flagged 08-14 (BofA) is
  now reported with real mechanical detail: an SPV buying chips and leasing
  them back to customers (incl. Anthropic), ~$30B junior + $60-70B
  Broadcom-guaranteed senior debt, guaranteed exposure to ~$370B by 2029.
  Stock actually rose on the financing/optimism news this week despite
  broader semi weakness. **No Tier CR trigger -- confirmation with detail,
  not escalation. Fold the SPV mechanics into the Circular Financing
  Playbook's Tier CR section at its next full review.**
- **ALB** -- JPMorgan cut its lithium price forecast (PT $140 Dec-2027,
  down from $160 Dec-2026), Neutral maintained -- short-term commodity
  pricing (China lithium carbonate prices down Q3 vs Q2), not a structural
  call. Q2 revenue +31.1% YoY, EPS beat intact. Stock -3.51% on 09-17,
  in line with the broader lithium-sector pullback. **No action -- existing
  ITM $120P already prices in the known downside; JPMorgan's own long-term
  target still implies recovery above current spot.**
- **CRM** -- not re-checked this pass; 09-01 finding (Claudeforce
  partnership) carried forward with no new contradicting headline.
