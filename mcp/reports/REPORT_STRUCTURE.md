# Report Structure — canonical section map

Written 2026-09-01 as part of a report consolidation pass (see git history
around this date for the specific fixes). **Purpose: the earlier report
redesign this session had no persisted spec, only commit-message history —
that's confirmed to be why later additions (Section 6.6, 6.7, the Seeking
Alpha scan) got bolted on independently and drifted back into the same
duplication/contradiction problems the redesign was meant to fix. Check any
new section against this doc before adding it, and update this doc when you
do.**

## Output format

The Daily report (`generate_daily_report`) was fully converted to real
Markdown 2026-09-02 (trader-requested, decided against PDF for git-
diffability and zero rendering-step complexity) — `#`/`##`/`###`/`####`
headers, real `|` tables via `_md_table()`, `-` bullet lists. Its output
file is `.md`; weekly/biweekly/monthly are still the original ASCII
box-drawing/tree-line format and still write `.txt`, pending a separate
follow-up pass. Two shared sections (`_generate_account_health_section` /
Section 0, `_format_production_framework_section`) already render as
Markdown in ALL 4 report types as a side effect of being shared code —
don't be surprised to see real tables there even in an otherwise-ASCII
weekly/biweekly/monthly report; that's intentional, not a half-finished
conversion of those three.

**When adding to or editing the Daily report specifically:**
- Every standalone label/value or status line needs a `- ` prefix (or to be
  a table row) — Markdown collapses consecutive bare lines into one
  paragraph, which is not obvious until you actually render the output.
- Genuinely tabular data (same columns, N rows) → `self._md_table(headers, rows)`,
  not a hand-aligned f-string. It already escapes a literal `|` in any cell
  so derived text can't silently corrupt the table's column count (a real
  bug once — a suggestion string used `|` as a plain-text separator).
- A pre-formatted, multi-level string from ANOTHER module (e.g. macro_
  risk_analyzer.py's rotation playbook — its own indented bullets/numbered
  sub-lists/sub-headers) → a fenced ` ``` ` code block, not a blanket
  `f"- {line}"` per line — that mangles the original structure (confirmed
  broken this way once, fixed by fencing it instead).
- When touching `_generate_account_health_section` or `_format_production_
  framework_section` (shared across all 4 reports), keep them Markdown —
  don't reintroduce ASCII dividers just because the report type calling
  them (weekly/biweekly/monthly) is still ASCII elsewhere.

## Shared computation — use these, don't re-derive

- **`_compute_account_status()`** — the single source of truth for
  per-account balance, requirement, utilization, status label, target,
  actual, gap. Cached on `self._account_status_cache` per report run. Any
  section showing account-level financial data should read from this, not
  re-iterate `ACCOUNTS_CONFIG.items()` independently. Status labeling is
  account-type-aware: margin accounts (only Account A) get real margin-call
  language (OVER CAP/EMERGENCY/ALERT/OK); cash-secured accounts (everyone
  else) get coverage language (FULLY COLLATERALIZED/WATCH/COVERAGE GAP) —
  they cannot be margin-called, so presenting the same crisis wording for
  both is a bug, not a style choice.
- **`_classify_positions_for_action()`** — the single source of truth for
  CLOSE/TRIM/ENTER position classification (RED heat + conviction, or HIGH
  conviction + GREEN heat). Cached on `self._action_classification_cache`.
  Any section recommending a position action should read from this, not
  re-code its own heat/conviction/RSI thresholds — that's exactly how
  Section 3 and the Weekly Execution Plan disagreed on the same ticker
  before this fix.
- **`_get_quarterly_plan_exit_discipline()`** — real put/call profit-take
  percentages from `data/us_quarterly_plan_2026_q4.yaml`, not a hardcoded
  constant. Any section stating a profit-take target should call this.
- **`_get_macro_risk_analysis()`** — cached wrapper around `analyze_macro_risk()`.
  Any section needing crash probability / sector sensitivity should read
  this, not call `analyze_macro_risk()` again independently — that's what
  let Section 6 (per-symbol) and Section 6.5 (macro detail) go out of sync
  before this fix. `_log_macro_risk_history()` (writes `data/macro_risk_history.yaml`,
  once per calendar day) and `_render_macro_risk_trend()` (reads it back as
  an ASCII sparkline) are the trend-tracking pair built on top of this.
- **`_build_sector_position_table()`** — produces Section 6, the canonical
  per-symbol table. See the Presentation principle below for when to use
  this instead of a new per-ticker block.
- **`self.snapshot['ytd_net_options_income']` / `['month_to_date_premium']`**
  — set in `_load_portfolio_snapshot()`, overlaid with the LIVE FIFO-realized
  computation from `monthly_premium.compute_monthly_premium()` at load time
  (falls back to the `data/portfolio_snapshot.yaml` literal only if live
  computation fails). Read these two keys for any YTD/MTD premium figure —
  don't call `compute_monthly_premium()` again independently. Before this
  fix (2026-09-02) the daily report's own Section 0 headline (live) and its
  PERFORMANCE VS TARGET block a few lines below (stale snapshot literal)
  could show two different numbers for the same YTD figure; the Monthly
  report had the same bug in its own Section 1 vs. Section 0 with an
  additional twist — Section 1 used the flat, non-regime-adjusted target
  while Section 0 used the regime-adjusted one. Both fixed by reading one
  overlaid value everywhere and, in Monthly's case, reusing `_calculate_
  gap_to_target()`'s `adjusted_monthly_target` instead of a second target
  constant.
- **State-file pattern** (tier_cr_state.yaml precedent) — for anything that
  needs live web research judgment and can't run inside this Python
  pipeline: a Claude-driven skill writes a dated YAML state file to
  `data/`, this report reads it every run and self-flags staleness past a
  threshold. Three examples: `tier_cr_state.yaml` (Section 6.6),
  `us_quarterly_plan_2026_q4.yaml` (Section 6.8),
  `seekingalpha_theme_state.yaml` (Section 6.9). **Don't manually append
  findings into a dated log file instead** — that's the mistake the Seeking
  Alpha scan made originally, and it's silently lost on the next
  regeneration.

## Presentation principle — table-first, not per-item text blocks

Trader-requested 2026-09-01 across all four report types: favor one
consolidated table over a multi-line text block repeated per ticker/sector.
Confirmed and fixed multiple real instances of the anti-pattern this session
(daily Section 2's conviction listing, the old Section 6 flat critical/
monitor/healthy list, sector_analysis.py's per-sector "DETAILED SECTOR
BREAKDOWN," monthly's Moat Recalibration Tier 1 block) — each was a
2-5-line hand-formatted block repeated for every ticker/sector, and each
was also substantially redundant with a table that already existed
elsewhere in the same report (usually Section 6's sector position table,
sometimes a compact summary table directly above the verbose block).

**Before adding new per-ticker or per-sector output, ask:**
1. Is this already shown in Section 6's table (ticker, put/call/total
   value, heat, conviction, suggestion, grouped by sector)? If yes, don't
   repeat it — reference "see Section 6" and show only what's genuinely new
   (e.g. a $ contribution figure Section 6 doesn't carry).
2. Does this need to be per-item at all, or does a name-list + one
   aggregate number communicate the same decision (e.g. "Names: X, Y, Z
   +2 more" instead of a 3-line block per name)?
3. Is there a real, repeating time series (crash probability, account
   balance, premium pace)? Use an ASCII sparkline (`_render_macro_risk_trend`
   is the reference implementation — `▁▂▃▄▅▆▇█` blocks, same visual
   language as Section 5's existing `█` position-distribution bars) rather
   than a wall of dated numbers.
4. If it's genuinely tabular data (one row per ticker/sector/period, same
   columns every row), render it as an actual aligned table with a header
   row — not a `├─`/`└─` tree block per item. Tree formatting reads fine
   for a single item's sub-detail (e.g. one account's equity list under
   its row); it doesn't scale to N repeated items.

## Daily report (`generate_daily_report`)

| # | Title | Purpose |
|---|---|---|
| 0 | ACCOUNT HEALTH, FRAMEWORK STATUS & GAP ANALYSIS | Consolidated per-account table (via `_compute_account_status`) + 60% close-cost framework |
| supp. | PRODUCTION FRAMEWORK — 60% CLOSE COST RATIO TARGETS | Regime-adjusted gross/net targets — cross-references Section 0's Target column, doesn't re-derive balance/status |
| 1 | SYSTEM STATUS & PORTFOLIO SNAPSHOT | Headline counts |
| 2 | CONVICTION UPDATES + FRAMEWORK CONTRIBUTION | Per-tier $ contribution table (ticker/conv/contribution/%target) — put/call detail lives in Section 6, not repeated here |
| 3 | POSITION HEAT DISTRIBUTION | Green/yellow/red counts |
| 4 | MARKET REGIME & SIGNALS | VIX/MA regime detection |
| 4.5 | SECTOR ANALYSIS & ROTATION | Sector-level snapshot table + rotation-priority grouping — per-symbol drill-down is Section 6, not repeated |
| 5 | POSITION DISTRIBUTION BY ACCOUNT | Position counts per account (not financial detail — that's Section 0) |
| 6 | POSITION HEAT MATRIX BY SECTOR | **The** per-symbol table: sector → symbol, put/call/total value, heat, conviction, suggestion (put/call-directional, macro-exposure-tagged). Built by `_build_sector_position_table()`. Most other sections should reference this rather than re-listing tickers. |
| 6.5 | CRASH EARLY WARNING — 7-LAYER MACRO RISK ANALYSIS | Risk level, probability (30/60/90d), 90-day trend sparkline, historical magnitude reference, sector sensitivity (consumed by Section 6's macro-exposure tags via `_get_macro_risk_analysis()`) |
| 6.6 | AI CAPEX RISK TRACKER — CIRCULAR FINANCING PLAYBOOK | Reads `tier_cr_state.yaml` |
| 6.7 | ASSIGNMENT / EXERCISE PROBABILITY (ALL ACCOUNTS, <=120 DTE) | Per-position Black-Scholes probability + EXIT CANDIDATE flag |
| 6.8 | QUARTERLY PLAN STATUS | Reads `us_quarterly_plan_2026_q4.yaml` |
| 6.9 | SEEKING ALPHA WEEKLY THEMES | Reads `seekingalpha_theme_state.yaml` |
| 7 | ACTION FRAMEWORK — PRIORITIZED EXECUTION + GAP CLOSURE IMPACT | Uses `_classify_positions_for_action()` |

## Weekly report (`generate_weekly_report`)

| # | Title | Purpose |
|---|---|---|
| 1 | WEEKLY MARKET REGIME FORECAST | |
| 2 | WEEKLY ACTION PRIORITIES + GAP CLOSURE IMPACT | |
| 3 | TOP-5 WEEKLY ACTION ITEMS | Uses `_classify_positions_for_action()` — same buckets as the Weekly Execution Plan tail, cannot disagree by construction |
| 4 | POSITION HEAT BY ACCOUNT | |
| 5 | IV RANK & ENTRY GATE (Weekly Scan) | Sort-before-truncate, RED-heat excluded — confirmed working, don't regress |
| 6 | WEEKLY CASH & MARGIN FORECAST | |
| 7 | WEEKLY THETA & P&L TRACKING | |
| 8 | RISK & GUARDRAILS (Weekly Check) | |
| 9 | DECISION TREE — END-OF-WEEK | |
| 10 | FRAMEWORK STATUS & AUTOMATION | |
| tail | WEEKLY EXECUTION PLAN | Uses `_classify_positions_for_action()` for REDUCE/MANAGE; `_get_quarterly_plan_exit_discipline()` for the put/call % targets; LET-RUN (RSI-driven) and the DTE/sector blocks are genuinely separate signals, not required to unify further |

## Biweekly report (`generate_biweekly_report`)

Sections 1-7: rolling 3-month pace, conviction trend, tier evolution, realized
premium trend, win-rate/Greeks, sector concentration, premium-vs-target.
Trend/history-focused — does not currently duplicate Section 0's account
table; keep it that way (link to Section 0 rather than re-listing balances
if a future addition needs per-account detail here).

## Monthly report (`generate_monthly_report`)

| # | Title | Purpose |
|---|---|---|
| 1 | MONTHLY ACTUAL VS TARGET — COMPLETE VARIANCE ANALYSIS | Actual/target/gap is Section 0's PERFORMANCE VS TARGET block (pointer only, not repeated); this section adds the genuinely new part — the rest-of-year projection, using the same regime-adjusted target as Section 0 |
| 2 | MONTHLY PERFORMANCE BY ACCOUNT (ALL N) | **Still a separate per-account loop** (MTD/YTD variance) — per the approved consolidation approach, this is intentionally kept as extra columns/detail on top of the same `_compute_account_status()` data, not a re-derivation. If this section is touched again, pull its balance/status fields from `_compute_account_status()` rather than recomputing. |
| 3 | MONTHLY PREMIUM vs TARGET (real) | |
| 4 | MOAT RECALIBRATION & TIER ASSIGNMENTS | |
| 5 | PERFORMANCE PACE (real) | |

## Adding a new section — checklist

1. Does it show per-account balance/status/target data? → read from
   `_compute_account_status()`, don't add a 6th independent loop.
2. Does it recommend closing/trimming/entering a position? → read from
   `_classify_positions_for_action()`, don't add new heat/conviction/RSI
   thresholds.
3. Does it need live web research (news, ratings actions, thematic
   screens)? → it can't run in this pipeline. Use the state-file pattern:
   a skill writes a dated YAML to `data/`, this report reads it with a
   staleness self-flag. Don't manually edit a specific dated log file.
4. States a profit-take/exit target? → read from
   `_get_quarterly_plan_exit_discipline()` (or the quarterly plan YAML
   directly for other fields), don't hardcode a percentage that can drift
   out of sync with the trader's actual current discipline.
5. Update this file's section table for whichever report type(s) you
   touched.
