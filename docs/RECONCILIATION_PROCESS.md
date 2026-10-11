# Reconciliation — Definition & Process

## What reconciliation means here

Reconciliation is the job that takes newly provided broker files and brings
**every data artifact and decision point** in theta-lab into agreement with
them — not just copying files into a folder. It operates on three layers,
and it is not complete until all three are updated and every ambiguity has
either a real trader answer or an explicitly flagged open question.

This document is the spec. `scripts/reconcile.py` (not yet built — see
Status below) should implement it; until then, this is the checklist a
manual reconciliation pass is run against.

## The three layers

### Layer 1 — Data

Verify each provided file by real content (the account number *inside* the
file, never the filename alone), archive the canonical file it replaces to
`arch/{name}_{YYYYMMDD}_prev.{ext}`, copy the new one into place. Covers:
Schwab Account A/B/C positions + transactions (`data/positions/`), Fidelity
Rahul/Rajul positions + `Accounts_History` (`data/positions/`), Vanguard
(`data/positions/vanguard_rahul.csv`), India equity + F&O statements
(`data/statements/`, matched by account number + newest mtime), Robinhood
when provided. Then rebuild `data/portfolio_snapshot.yaml` via
`scripts/update_snapshot.py` so every downstream consumer reads from one
freshly-built source.

### Layer 2 — Analysis

Regenerate everything derived from Layer 1, so what's **displayed** matches
the **data**, not a stale computation from the last cycle:
- All 4 US report types (`generate_unified_master_report`:
  DAILY/WEEKLY/BIWEEKLY/MONTHLY)
- The India weekly report (`generate_india_weekly_report`)
- The dashboard cache, both markets (`dashboard/backend/app/cache.py`'s
  `refresh_all()`)
- **A staleness/sanity check against the prior run's output** — diff each
  report's text and flag any line that is byte-identical despite a live
  input (price, RSI, regime, a trigger's own stated price) having changed.
  This is the direct fix for the YATHOS class of bug (see Incidents below):
  a hand-written action string in `data/india_config.yaml`'s
  `exit_triggers` that repeated verbatim — "price 845.50 above the 820
  trigger" — across every report from 2026-08-04 through 2026-10-10,
  because nothing ever re-evaluated it against real current holdings.

### Layer 3 — Decisions

The layer that was actually missing on 2026-10-10. Every tracked
decision/trigger gets **re-evaluated** against the new data, not left as-is:
- `data/active_decisions.yaml` gates (`account_a_margin_utilization_pct`,
  `macro_risk_level`, leg-count checks) — recomputed, not just re-displayed
- India's `exit_triggers` (`data/india_config.yaml`) — cross-checked
  against real current holdings in the freshly-reconciled position files,
  not just re-printed from a static `action:` string
- The cross-market Action Tracker ledger
  (`dashboard/backend/app/ledger.py`) — items whose underlying condition
  resolved (an option expired, a position closed) get surfaced for
  resolution instead of sitting OPEN indefinitely (`_upsert_new_only` never
  auto-resolves; a human or an explicit reconciliation step must)
- The quarterly direction docs
  (`logs/quarterly_portfolio_direction_{us,india}_2026-Q3.md`) — flagged
  once they cross an age threshold (14 days) so staleness is visible
  instead of silently reaching 48 days, as the India doc did

## The required step: ask

Reconciliation stops and asks the trader — rather than silently assuming —
whenever:
- An expected account has **no fresh file at all** (e.g. Account C's gap on
  2026-10-10)
- **Two files could plausibly represent the same account** (e.g. the
  duplicate Contributory/275 downloads 44 seconds apart on 2026-10-10)
- A decision's real current status **can't be determined from files alone**
  (Account A's Margin Equity %, Cash to Trade, SMA — Schwab-screen-only
  data, never in any CSV export)
- A tracked trigger's underlying position **can't be confirmed** in the
  newly reconciled data (the YATHOS case, in hindsight)

**Default policy (confirmed 2026-10-11): queue, don't block.** Proceed
through every unambiguous part of the job; collect open questions and
present them together at the end, rather than halting the whole
reconciliation on the first ambiguity. A specific run may be told to fully
block instead if the trader wants that for something especially sensitive.

An open question is itself tracked, not just asked once and forgotten — it
carries forward into the next reconciliation cycle with its own status
until it has a real answer, the same way `active_decisions.yaml` entries do.

## What reconciliation is NOT

- Not "copy the newest files in" — that is one Layer-1 sub-step, not the
  whole job
- Not "regenerate reports" alone, without checking whether any Layer-3
  decision actually needs to change as a result
- Not analysis or commentary — a risk/portfolio write-up is something done
  *with* reconciled output afterward, not part of reconciling itself

## Incidents this definition is grounded in

- **2026-10-10 Account C gap**: flagged as a question ("let me confirm with
  you how to handle Account C") but never actually asked through — the
  reconciliation proceeded silently on stale Oct-2 data. Root cause for the
  "ask" step above being mandatory, not optional.
- **YATHOS static trigger**: `data/india_config.yaml`'s `exit_triggers`
  entry for YATHOS contained a hand-written sentence with a literal price
  ("845.50") that was never recalculated — confirmed identical across 6+
  reports spanning 2026-08-04 to 2026-10-10, and confirmed by the trader to
  not even appear in the real India transaction files. Root cause for
  Layer 2's staleness-diff step and Layer 3's trigger-vs-real-holdings
  cross-check.

## Status

- This document: written 2026-10-11, reflects the agreed definition.
- `scripts/reconcile.py` orchestrating all three layers: **not yet built**.
- The staleness-diff check (Layer 2) and the trigger-vs-holdings cross-check
  (Layer 3): **not yet built**.
- Until built, a manual reconciliation pass should be run against this
  document's checklist directly.
