# Local Dashboard + Action Planner — Build Plan

## Objective

Replace the weekly/biweekly/monthly report trio's overlapping, disconnected
action lists (Section 2 vs. 4 vs. 11 disagreement, no real week-over-week
delta) with one local dashboard: a YTD panel, a single Action Planner with
full history per item, and searchable past reports. Coexists with
`personal-assistant` behind the shared gateway (`~/local-gateway`, port
9000) as the second tool in a growing local-tools set — same port for the
*set*, this app gets its own internal port like personal-assistant does.

**No existing data is discarded.** `active_decisions.yaml`,
`macro_risk_history.yaml`, `seekingalpha_theme_state.yaml`,
`tier_cr_state.yaml`, `india_6month_plan.yaml`, and every historical
`logs/*.md`/`.txt` report stay exactly where they are and keep being
written by the existing report engine. The dashboard reads them; it does
not replace them until a later phase explicitly says so.

## Architecture decisions

- **Lives in this repo**, `theta-lab/dashboard/` — not a new repo. The
  report engine, data files, and YAMLs it reads are all here already;
  splitting it out buys nothing and adds a second place to keep in sync.
- **FastAPI + SQLite**, same stack as `personal-assistant` — known-good,
  no new tooling to learn, and the two projects can eventually share
  patterns (not code) without fighting different frameworks.
- **Container name `theta-lab-web`, internal port 8000**, host port 8020
  (checked against every port already in use on this machine — 8000,
  8004, 8005, 8007, 8010, 8080, 8100, 3001, 5433, 9000 are all taken).
  Reachable directly at `localhost:8020/` and, once wired into
  `~/local-gateway/Caddyfile` (Phase 1 exit), at
  `localhost:9000/theta-lab/` — same `container_name` + optional
  `docker-compose.gateway.yml` overlay + relative-`fetch()` convention
  ADR 0018 established for personal-assistant.
- **No new report-generation logic.** The dashboard calls the existing
  `UnifiedReportProduction`/`realized_pnl.py`/`india_weekly_report.py`
  functions directly (same process or a thin subprocess call) rather than
  reimplementing anything they already compute correctly.

## Data model — the actual gap being fixed

`active_decisions.yaml` (and the India equivalents) store *current status
only* — no history of how an item got there. The dashboard's core new
piece is an append-only ledger:

- `action_items`: id, source (`active_decisions` / `india_6month_plan` /
  manual), category, title, status (open/blocked/resolved), created_at.
- `action_item_events`: id, action_item_id, event_type (created /
  status_change / note / resolved), timestamp, detail (free text +
  whatever live values triggered it, e.g. a metric_gate's computed %).

A one-time, read-only migration script seeds this from the existing YAMLs
(one `created` event per item, backdated to its earliest known mention
where derivable). The YAMLs remain the system of record for the report
engine; the dashboard's DB is additive until a later phase (not this one)
considers flipping that.

## Phases

### Phase 1: Read-only dashboard (MVP)
**Objective:** One page showing YTD P&L (via `realized_pnl.py`), today's
account-health snapshot (via `_compute_account_status`), and the current
`active_decisions.yaml` items — no new data entry yet.
- FastAPI skeleton, SQLite file, Dockerfile, `docker-compose.yml` (+
  optional gateway overlay, matching ADR 0018's pattern).
- Wire into `~/local-gateway/Caddyfile` (`/theta-lab/` block, template
  already left there as a comment).
- **Exit criteria:** page loads real live data, both directly on 8020 and
  through the gateway on 9000; no report-generation code duplicated.

### Phase 2: Action ledger + migration
**Objective:** The append-only ledger above, backed by a real migration
of every existing YAML's current items.
- Migration script (one-off, re-runnable, idempotent — re-running never
  duplicates an already-migrated item).
- Dashboard can mark an item resolved/blocked with a note; write goes to
  the ledger, not back to the YAML (one-way for now).
- **Exit criteria:** every currently-open item from `active_decisions.yaml`
  + `india_6month_plan.yaml` visible with correct status; resolving one in
  the dashboard doesn't affect the YAML-driven reports at all (no
  regression in the existing report engine).

### Phase 3: History + search
**Objective:** Browse past reports and past ledger events, matching
personal-assistant's `/history` pattern (SQLite `LIKE`, not FTS5 — same
proportionate choice, not over-built for a single-user tool).
- Index `logs/*.md`/`.txt` by date + report type at ingest time (a
  filesystem watch or a scan-on-startup, whichever is simpler to get right
  first).
- **Exit criteria:** can find "what did the weekly report say about AXON
  on 2026-09-10" without opening a file by hand.

### Phase 4: Schedulers
**Objective:** Two independent triggers, matching the two real cadences
this project already has:
- **File-drop detection**: watch `data/positions/`, `data/statements/`
  for new exports → auto-regenerate reports (replaces "the user manually
  says 'I've downloaded fresh files, regenerate everything'").
- **Market-hours refresh**: periodic price/status refresh on the dashboard
  itself (not a full report regen) during trading hours only.
- **Exit criteria:** dropping a fresh Schwab export into `data/positions/`
  updates the dashboard without a manual regenerate request.

### Phase 5 (not scoped yet): Section 2/4/11 consolidation
Real fix for the weekly/monthly redundancy and the three-independent-
action-list problem — deliberately deferred past the dashboard's first
working version. Revisit once Phases 1-4 are live and it's clear whether
the dashboard itself makes the redundancy moot (single Action Planner
replacing all three) or whether the report engine's own Section
generation still needs surgery independent of the dashboard.

## Explicitly out of scope for now

- No rewrite of `unified_master_report_production.py`'s report text.
- No change to how `active_decisions.yaml` etc. are written today.
- No attempt to make the dashboard the system of record before Phase 2's
  migration is proven correct on real data.
