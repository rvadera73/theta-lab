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
5. Append the week's findings to that week's daily/weekly report file
   under a "SEEKING ALPHA WEEKLY THEME SCAN" section, and to this skill's
   own running log below so the history persists across weeks.
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
