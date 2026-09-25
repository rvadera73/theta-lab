# Local Dashboards — Build Plan (US + India, separate)

## Objective (revised after real usage feedback)

Two separate dashboards — US and India — not one merged view. Confirmed
by real section-header analysis (below) that the underlying report
engines already produce mostly duplicated content per market: the fix is
consolidation into ONE real section per concept, not a report-type
selector that just moves the duplication into a dropdown (which is what
Phase 1 shipped and was correctly rejected).

Each dashboard must cover everything currently spread across that
market's report cadence AND its standalone portfolio-analysis document —
nothing dropped, nothing re-shown twice. Sections are labeled **customer**
(the actual decision content: what to do, current state, risk) or
**admin** (framework mechanics, automation status, staleness/technical
notes) — customer sections are the default view; admin is a secondary,
clearly separated area, not interleaved.

Built with USWDS (matching personal-assistant's ADR 0025 exactly —
CDN-pinned `@uswds/uswds@3.14.0`) and real semantic/accessible HTML — real
`<table>`s, heading hierarchy, ARIA where needed — not a `<pre>` dump of
markdown source. That was tried (see "Rejected approaches" below) and
correctly called out as not a real dashboard.

## Real duplication found (grounds for consolidation, not a guess)

Pulled and diffed the actual `generate_{daily,weekly,biweekly,monthly}
_report()` output on 2026-09-25:

- **"Section 0: Account Health, Framework Status & Gap Analysis"** — byte-
  for-byte the same structure (Portfolio Snapshot, Per-Account Breakdown,
  Close-Cost-Ratio Framework) in all 4 US reports.
- **"Active Decision Tracker"** — same `active_decisions.yaml` content,
  rendered identically in all 4 (daily §6.9, weekly §11, biweekly §8,
  monthly §6).
- **Competing action lists** (the real Section 2/4/11 problem): daily §7
  (Close Now/Monitor/Let Run/Opportunity) and weekly §2 (Action
  Priorities), §3 (Top-5 Actions), §9 (Decision Tree) are four
  independently-computed "what to do" views that can disagree.
- **One metric, three cadences**: premium-vs-target appears in weekly §7,
  biweekly §4+§7, monthly §3 — same underlying number, re-rendered per
  cadence instead of one real-time trend with a period selector.
- **Sector data**: daily §4.5+§6 (live) and biweekly §6 ("current, live")
  — the biweekly version is redundant with daily's.

## Consolidated section model

### US Dashboard (`/theta-lab/us/`)

**Customer:**
1. **Account Health** — dedup of Section 0 across all 4 reports.
   Live via `_compute_account_status()` (already wired).
2. **Today's Actions** — ONE reconciled action list (Close Now / Roll /
   Let Run / New Entries), replacing daily §7 + weekly §2/§3/§9's four
   separate computations. **Not yet built** — needs real reconciliation
   logic, the single biggest remaining piece (see Phase A below).
3. **Cash & Margin Forecast** — real-time, not report-gated. The
   crash-scenario cash requirement + expiry-curve concentration tables
   already computed ad hoc this session (weekly §6) — promote to a live
   endpoint.
4. **P&L vs Target** — one trend view (MTD/QTD/YTD selector) replacing
   weekly §7 + biweekly §4/§7 + monthly §3. Backed by
   `realized_pnl.get_realized_summary()`/`get_realized_monthly_by_account()`
   (already wired).
5. **Sector Heat** — dedup of daily §4.5/§6 + biweekly §6, one live view.
6. **Risk & Macro** — daily §6.5 (Crash Early Warning, AI Capex/Circular
   Financing Tracker) + weekly §8 (Risk & Guardrails).
7. **Quarterly Portfolio Direction** — the standalone strategic doc
   (`logs/quarterly_portfolio_direction_us_2026-Q3.md`, hand-authored per
   quarter, not auto-regenerated like the 4 cadence reports). Rendered in
   full; its "Open Items / Not Yet Built" section feeds the Action
   Tracker (#8) instead of living only in a static file.
8. **Action Tracker** — dedup of "Active Decision Tracker" (all 4
   reports) into the real append-only ledger from the original plan
   (Phase 2, still needed, now scoped under Phase B).

**Admin:**
- Framework Status & Automation (weekly §10).
- Production Framework technical sub-block (Section 0's supplementary
  detail — the customer view keeps the summary numbers, this keeps the
  full computation).
- Moat Recalibration & Tier Assignment mechanics (monthly §4) — the
  *result* (current tier per position) surfaces in Today's Actions/Sector
  Heat; the recalibration mechanics stay admin.
- Win-Rate & Greeks Drift raw diagnostics (biweekly §5).
- Data staleness warnings, IV Rank/Entry Gate raw screen (weekly §5 —
  feeds Today's Actions' "Opportunity" bucket as an input, not a
  standalone customer section).

### India Dashboard (`/theta-lab/india/`)

**Customer:**
1. **Portfolio Snapshot** — equity + F&O positions, current values.
2. **6-Month Plan Tracker** — already built (`_check_6month_plan`),
   promote to a live panel instead of report-text-only.
3. **Regime & Risk Signals** — Nifty/India VIX/sector regime.
4. **Quarterly Portfolio Direction** —
   `logs/quarterly_portfolio_direction_india_2026-Q3.md`, same treatment
   as the US version; its Open Items feed the India Action Tracker.
5. **Action Tracker** — India has no `active_decisions.yaml`-style ledger
   today (confirmed gap from earlier this session) — this dashboard is
   what finally gives India the same tracked-decision discipline the US
   side has had since this session's earlier work.

**Admin:**
- Breeze API credential/session status (inert-until-configured, matching
  `_no_breeze_credentials_message()`'s existing convention).
- Data source notes (statement-derived vs. live Breeze).

## Rejected approaches (so this isn't re-tried)

- **Report-type dropdown showing raw report text** (what Phase 1 shipped
  as a stopgap): rejected — moves the duplication into a dropdown instead
  of removing it, and unformatted markdown-as-`<pre>` isn't a dashboard.
- **One merged US+India dashboard**: rejected — no shared data model
  (different brokers, currencies, account structures, strategies); a
  merged view would force artificial parallels that don't exist.

## No existing data is discarded

`active_decisions.yaml`, `macro_risk_history.yaml`,
`seekingalpha_theme_state.yaml`, `tier_cr_state.yaml`,
`india_6month_plan.yaml`, both quarterly portfolio-direction docs, and
every historical `logs/*.md`/`.txt`/`.html` report stay exactly where they
are. The report engine keeps writing them exactly as today; the
dashboards are additive consumers, not a replacement, until a later phase
explicitly says otherwise.

## Phases (revised)

### Phase A: US customer dashboard, real sections (in progress)
USWDS-based rebuild of `/theta-lab/us/`: Account Health, Cash & Margin
Forecast, P&L vs Target, Sector Heat, Risk & Macro, Quarterly Portfolio
Direction — all real structured HTML, not raw text. Today's Actions
reconciliation and the Action Tracker ledger are the two pieces requiring
new logic (not just new UI) and are called out separately below rather
than rushed into this phase.
- **Exit criteria:** every customer section above renders as real USWDS
  components with correct live data; zero raw markdown/`<pre>` dumps for
  US content; admin content present but visually separated (e.g. a
  collapsed/secondary tab).

### Phase B: Action Tracker (ledger) + Today's Actions reconciliation
The two hardest, most valuable pieces:
- Append-only ledger (`action_items`/`action_item_events`, as originally
  scoped) seeded from `active_decisions.yaml` (US) — India gets a ledger
  from day one, not a migration, since it never had one.
- A single reconciliation function replacing daily §7 + weekly §2/§3/§9:
  needs an explicit tie-breaking rule set (which existing computation
  wins when two disagree) — written up as its own short design note
  before coding, since "which list is authoritative" is a real decision,
  not a UI question.
- **Exit criteria:** one action list, one ledger, per market; no
  dashboard section still computing its own independent "what to do"
  view.

### Phase C: India dashboard (real sections)
Same USWDS treatment as Phase A, applied to India's section model above.
Requires wrapping `india_weekly_report.py`'s existing functions
(`_check_6month_plan`, position/regime loading) the same read-only way
Phase 1 wrapped the US report engine.
- **Exit criteria:** India dashboard live at `/theta-lab/india/` with the
  same real-section standard as Phase A, no raw-text fallback.

### Phase D: History + search (both markets)
Browse past reports/quarterly docs and past ledger events, matching
personal-assistant's `/history` pattern (SQLite `LIKE`).

### Phase E: Schedulers (both markets)
File-drop detection (new Schwab/Fidelity/ICICI exports trigger a
refresh) + market-hours live-price refresh, per market's own trading
hours.

## Explicitly out of scope for now

- No rewrite of the underlying report engines' text output — the
  dashboards consume the same functions, they don't replace them.
- No attempt to unify US and India into shared UI beyond the common
  USWDS/WCAG shell and navigation between the two.
