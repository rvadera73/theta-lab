# ADR 0001: Decision Engine Foundation — From Monitoring to Deciding

**Status:** Accepted
**Date:** 2026-11-03

## Context

theta-lab classifies, flags, and ranks the current state of every position
(`heat_scanner.py`, `sequencer.py`, composite scores). That is monitoring.
Every recent real-money question that mattered this week was a *deciding*
question — "what do I do about the 11/20 cluster," "do I need the $50K
emergency draw," "is the naked-call cleanup actually urgent" — and theta-lab
has no model for that. The answers came from one-off scripts written against
`services.get_position_heat()` directly, and each one was wrong or
incomplete in a different way:

- A fixed-symbol naked-call list (`{LMT, ZS, CRM, PYPL, LLY, ULTA, NOC,
  CRWD}`) silently missed a newly-naked OKTA $140C because it filtered a
  list instead of a predicate (`covered == False and dte <= 21`).
- `sequencer.py`'s `_SEVERITY_RANK` has no entry for `CLOSE_RESTAGGER`, so it
  falls to the same default rank as `WATCH_CLOSE` — a time-bound, forced
  action ranked identically to a market-driven, non-urgent one.
- `services.get_cash_margin_forecast()` hardcodes `emergency_reserve =
  200000`; the real reserve is ~$140K and draining against the Dubai
  payment schedule (see `skills/options-trader/SKILL.md`). The tool's
  "reserve covers stress" verdict currently overstates safety by $60K+.

None of this is a data problem. The underlying pipelines are mostly real:
`report_utils.upcoming_earnings`, a real Black-Scholes Greeks calculator
(`scripts/greeks_calculator_from_market.py`, orphaned — zero imports from
`mcp/`/`dashboard/`), `iv_rank.get_iv_rank()` (real-IV param accepted, never
passed by any live caller), `symbol_context.py` (HIGH_LEVERAGE /
EARNINGS_RISK / ILLIQUID gates, genuinely wired). What's missing is a model
that turns that data into a decision:

1. **Declared constraints as data** — Account A's equity floor by regime,
   cash-to-trade policy, the $50-100K deposit guidance — all exist today
   only as prose in `SKILL.md`, read by me, not by any program.
2. **Per-symbol thesis** — "PYPL/MRNA: permanent exit, no new puts,"
   "AXON stagger: let each leg run independently" — also prose-only, no
   programmatic home.
3. **Comparison of alternatives, not independent per-leg verdicts** — a
   decision on one leg (e.g. closing a profitable put to free margin before
   a withdrawal) has to be evaluated against the other legs competing for
   the same cash/margin budget, not scored in isolation.
4. **Outcome tracking** — no record exists of what was recommended, what
   the user actually did, or whether it worked.

This has been attempted before. `thesis_state_tracker.py` and
`trade_recommendation_engine.py` (referenced in `ARCHITECTURE_MAP.md`, both
deleted from the repo) and `scripts/position_decision_analyzer.py` (still
present, unused, no margin/thesis awareness) were earlier tries at exactly
this. Per direct confirmation, they failed because they were ad hoc scripts
with no design or tests — not because the idea was wrong. This ADR exists so
the next attempt doesn't repeat that failure mode.

### External validation (what's standard practice vs. missing here)

| Practice | Status in theta-lab |
|---|---|
| 21-DTE / 40-70% profit-take rule | Aligned — already encoded in `heat_scanner.py` |
| Portfolio-level Greeks aggregation | Missing — Greeks computed per-leg nowhere, calculator orphaned |
| Reg-T margin estimate (~20% underlying − OTM + premium) | Missing — no formula anywhere; `weekly_combined_report.py:138`'s `sum(cost_to_close)` is a wrong lookalike, unused downstream |
| Dividend / early-exercise assignment risk on short calls | Missing — no gate |
| Flat 1-3%-per-trade or fractional-Kelly position sizing | Missing — sizing is "max N contracts per tier," not risk-budget-based |
| 5% single-name concentration, same-week expiry clustering | Partial — expiry clustering already checked by `get_cash_margin_forecast()` (reserve bug aside); concentration exists per-symbol only, no portfolio rollup |

## Decision

Build a **decision engine** as a new, tested module, not a script, following
the same ADR → design → TDD discipline used elsewhere
(`ai-foundry-engineering` skill). Two-phase roadmap:

- **Phase 1 — Advisor**: produces a ranked, budget-aware action plan a
  human still approves.
- **Phase 2 — Autonomous Executor**: staged autonomy gated on Phase 1's own
  outcome-tracking record. Not scoped further here.

### 1. Canonical schema — `LegDecisionRecord`

One record per leg, replacing ad hoc per-script field reconstruction:

```python
@dataclass
class LegDecisionRecord:
    # Identity
    symbol: str
    account: str
    option_type: str          # PUT | CALL
    strike: float
    expiry: str
    dte: int
    contracts: int

    # Coverage — explicit enum, replacing the covered bool/None overload
    # (today None means "PUT, concept doesn't apply" per services.py:331 —
    # never "unknown"; this enum removes the ambiguity entirely)
    coverage: Literal["NAKED", "COVERED", "PARTIAL", "CASH_SECURED_PUT", "NA_LONG"]

    # Economics
    premium_received: float
    cost_to_close: float | None
    loss_multiple: float | None
    pnl_pct: float | None
    current_price: float | None
    distance_pct: float | None

    # Margin — always labeled as an estimate, never trusted as exact
    est_margin_requirement: float | None
    margin_source: Literal["REG_T_ESTIMATE", "UNAVAILABLE"]

    # Assignment path
    itm: bool
    assignment_cash_impact: float | None        # + = cash received, - = cash required
    assignment_resulting_position: str | None    # e.g. "uncovered short stock"

    # Time axis — independent of severity
    time_bound: bool
    forcing_event: str | None                    # "EXPIRY" | "EARNINGS" | "EX_DIV" | None
    days_to_forcing_event: int | None

    # Severity axis
    severity: str                                 # existing heat_scanner color/action vocabulary
    gates_fired: list[str]                        # existing symbol_context.py gates

    # Decision
    recommended_action: str
    rule_citation: str                            # e.g. "heat_scanner.py:161 loss_cut_multiplier"
```

`time_bound`/`forcing_event`/`days_to_forcing_event` exist specifically to
fix the `CLOSE_RESTAGGER` bug class: severity and time-boundedness are
different axes and must never collapse into one rank.

### 2. Engine — `mcp/analysis/decision_engine.py`

One pure function: `build_decisions(positions, policy, theses) ->
list[LegDecisionRecord]`. Implemented as a **data-driven rule table**, not
nested if/elif — each rule is `(predicate, action, citation)`, iterated in
priority order, first match wins. This is what makes completeness a
test-coverage question instead of a memory question: a missing rule shows up
as a failing fixture, not a silently-skipped symbol.

**First tests, before engine logic**: real fixtures already surfaced this
session —
- OKTA $140C (naked call missed by the old fixed-list check)
- ANET $200P, 11/13 expiry (assignment cash impact, net surplus case)
- The 11/20 cluster (OKTA $140C, PYPL $42.5C/$45C, CRM $185C, plus six ITM
  short puts) — multiple time-bound, naked/ITM legs competing for the same
  margin budget in one window

A rule is not done until it has a test from this list.

### 3. Policy layer — `trading_policy.yaml`

Consolidates scattered thresholds that today live only as prose in
`skills/options-trader/SKILL.md` or as literals inside `heat_scanner.py`/
`config.py`: `loss_cut_multiplier`, `profit_target_pct`, `RED_DTE_WINDOW`,
Account A's equity-floor-by-regime table, the cash-to-trade action table,
`_SEVERITY_RANK` order. Extraction is mechanical and behavior-preserving —
move values, not logic, verified by parity tests against current output
before any rule is changed.

### 4. Goals/constraints — read, not duplicated

Portfolio-level goals/constraints come from personal-assistant's existing
Objectives system (`get_objectives`, e.g. "Master Financial Blueprint") —
**read at decision time, never re-stored in theta-lab.** Objectives are
free text today; the engine needs a structured subset (cash floor, equity
floor by regime, Account A's role). Until a structured-extraction path
exists on the personal-assistant side, this ADR scopes it as a manual,
versioned mapping inside `trading_policy.yaml` that cites which Objective
text it was extracted from — not a parallel source of truth.

### 5. Thesis store — new, theta-lab-local

Per-symbol belief/conviction has no home in either system today
(Objectives are flat, not per-ticker). New small store modeled directly on
`account_state.py`'s existing get/set pattern — same proven shape, not a new
design: `thesis_state.get('PYPL') -> {"conviction": ..., "permanent_exit":
True, "notes": "..."}`. Minimum viable schema only: conviction score,
permanent-exit flag, free-text notes, last-updated. Expand later if the
engine needs more.

### 6. Sequencing — order of implementation

Independent bug fixes (do regardless of this ADR's adoption pace):
1. `sequencer.py`: add `CLOSE_RESTAGGER` to `_SEVERITY_RANK`.
2. `services.get_cash_margin_forecast()`: replace hardcoded `200000` with a
   value sourced from `account_state`/policy, not a literal.

Engine build-out, in order:
3. `LegDecisionRecord` + `decision_engine.py` core, migrating today's
   `heat_scanner.py`/`sequencer.py` rules in verbatim (parity-tested against
   current live output — no new behavior yet).
4. Reg-T margin formula (≈20% underlying − OTM + premium, floor
   10%+premium), populating `est_margin_requirement`/`margin_source`.
5. Dividend/ex-date assignment-risk gate on short calls (new accessor —
   do not import the orphaned `greeks_calculator_from_market.py`, write a
   fresh throttle-safe one per the existing `symbol_context.py` pattern).
6. Fix `iv_rank` call sites to pass real IV instead of the silent HV-proxy
   fallback.
7. Portfolio-level Greeks/sector/concentration rollup (reuse
   `symbol_context.py`'s per-symbol sector; new aggregation only).
8. Formal position-sizing/risk-budget rule (flat % or fractional-Kelly),
   replacing "max N contracts per tier."
9. Persist one `LegDecisionRecord` snapshot per refresh via existing
   `cache.py` infra (`computed_cache` table) — enables history/diffing,
   first step toward outcome tracking.
10. Advisor surface: `GET /api/decisions` (dashboard) + new MCP tool
    `get_leg_decisions`, with Accept/Defer/Reject feedback closing the loop
    into the outcome record.

## Alternatives considered

- **Separate microservice.** Rejected — single-user, tightly coupled to
  theta-lab's own data; unjustified operational overhead.
- **Another standalone script.** Rejected — this is exactly the failure
  mode `thesis_state_tracker.py`/`trade_recommendation_engine.py` already
  demonstrated.
- **New goals/constraints store inside theta-lab.** Rejected — duplicates
  personal-assistant's Objectives system; wrong system boundary.
- **Point-fix each surfaced gap independently** (calendar field, naked-call
  audit tool, margin reserve constant) with no shared schema. Rejected per
  repeated explicit feedback this session — fixes a symptom, not the
  missing model; the same incompleteness recurs on the next question asked
  a different way.

## Consequences

- Phase 1 is purely additive: `decision_engine.py` runs parallel to
  existing `heat_scanner.py`/`sequencer.py` output until parity-tested; no
  existing dashboard behavior changes until a rule is verified.
- Every future "should I do X" question gets answered by inspecting
  `LegDecisionRecord` output and, if the answer is wrong, fixing a rule or
  adding a fixture — not by writing a new one-off script.
- `trading_policy.yaml` becomes the one place thresholds live; changing a
  threshold is a one-line diff reviewable on its own, not a hunt through
  `SKILL.md` prose and `config.py` literals.
- Does not address Phase 2 (autonomous execution) at all — intentionally
  deferred until Phase 1 has a real outcome-tracking history to gate on.

## Open questions

- Exact structured-extraction mechanism from personal-assistant Objectives
  (manual mapping now; automated extraction is a personal-assistant-side
  change, out of scope here).
- Whether `thesis_state` should eventually move into personal-assistant
  once/if it gains per-ticker structure — revisit after Phase 1 ships.

## Deferred

Verified 2026-11-09 against Section 6's own sequencing list: steps 1-2
(sequencer `CLOSE_RESTAGGER` severity fix + ledger `priority` column/
`decision_note` wiring — the real-world equivalent of the
`get_cash_margin_forecast` literal, now sourced from `account_state`'s new
`emergency_reserve` column), 3-8 (`decision_engine.py`'s already-committed,
tested coverage/margin/dividend-gate/Greeks-rollup/position-sizing logic),
and 9 (`cache.py`'s `us_leg_decisions` snapshot persisted every refresh,
confirmed at `dashboard/backend/app/cache.py:83`) are all genuinely done,
each with passing test coverage.

Step 10 is only HALF done. The Advisor surface itself exists and is real:
the `get_leg_decisions` MCP tool (`mcp/analysis/leg_decisions_tool.py`) and
`GET /api/us/leg-decisions` (`dashboard/backend/app/main.py:253`) both call
`services.get_leg_decisions()`, which is a straight projection through
`decision_engine.py` — tested in `tests/test_leg_decisions_tool.py`.

What's NOT built is the second half of step 10: the **Accept/Defer/Reject
feedback loop that closes into an outcome record**. Confirmed via
`grep -rni "accept\|defer\|reject" dashboard/backend/app/main.py
dashboard/backend/app/ledger.py` — the only hit is a comment in
`ledger.py` describing the intent, not an implementation. There is no
mutation endpoint, no outcome-record table, and nothing that captures
what the trader actually did with a recommendation versus what the engine
suggested. This is tracked as explicit follow-up work, not silently
dropped — Phase 1's own "Consequences" section already anticipated that
outcome-tracking history is a prerequisite for Phase 2, so this gap blocks
that transition until it's closed.
