# ADR 0005: Coverage-Aware Position Heat Severity

**Status:** Accepted
**Date:** 2026-11-12

## Context

On 2026-11-12 the trader directly challenged the Position Heat scanner's RED
count (88 raw legs / 61 real `(symbol, account)` position-groups out of 132),
specifically on 3 OKTA covered calls (strikes $80/$82.50/$140, 127/127/8 DTE)
flagged `CUT_RESTAGGER` ("BTC now... re-enter fresh after name stabilises")
at up to 10.8x loss-multiple and -57% distance-to-strike. `get_position_detail`
confirmed the real combined position: `stock_pnl +$112,236` vs.
`net_options_pnl -$55,432.18` = `combined_net_pnl +$56,803.82` -- a net
*profitable* position despite 4 RED legs, because the calls are deep ITM
purely because the underlying stock rallied past the strikes on shares the
trader already owns.

Reading `mcp/analysis/heat_scanner.py` directly confirmed the root cause:
`_determine_color()`/`_set_red_action()` take `option_type`, `strike`,
`expiry`, `premium_received`, `cost_to_close`, `current_price`, `dte` -- and
nothing else. Coverage (`covered`/`covered_contracts`) is computed in
`dashboard/backend/app/services.py` and merged onto the OUTPUT rows **after**
`assess_portfolio_heat()` has already scored color/action -- a covered call
and a naked call with identical premium/cost-to-close/DTE score identically.
The `loss_multiple >= 2.0x` hard stop -- `_set_red_action`'s `CUT_RESTAGGER`
branch -- fires the same generic "hard stop, BTC now, wait 5-10d, re-enter
fresh" text regardless of whether a real naked loss exists or the leg is
simply a covered call doing exactly what a covered call is supposed to do
(cap upside, deliver shares at the strike on assignment). The trader's own
`options-trader/SKILL.md` documents the opposite prescription for this exact
case: *"Roll CC up if stock rallies past strike (collect credit, extend
DTE)"* -- never "cut at a loss and sit out."

A follow-up decomposition of the real book (`/api/us/leg-decisions`, 206 open
legs) quantified the gap precisely, not by estimate:

| Bucket | Legs | Why RED today |
|---|---|---|
| COVERED calls hit by the hard stop | 21 (11 position-groups) | Loss-multiple blind to coverage |
| NAKED/CASH_SECURED_PUT/PARTIAL, DTE > 45 | 42 | Same hard stop, blind to time-horizon |
| NAKED/CASH_SECURED_PUT/PARTIAL, DTE <= 45 | **19** | Genuinely time-pressured -- the real action list |

The middle bucket matters as much as the covered-call bucket: this
trader's own Roll Decision Framework already states *"Short put ITM, thesis
intact, DTE > 45 -> HOLD, do not roll -- time is working."* The hard stop
(`loss_multiple >= 2.0x`, kept explicitly DTE-independent by a 2026-10-15 fix
comment in `heat_scanner.py`, on the theory that "a genuine hard-stop loss is
urgent regardless of time left") directly contradicts that documented rule
whenever real time remains. The 2026-10-15 fix already extended DTE-gating to
strike-proximity (`distance_pct`) for exactly this reason; it just never
extended the same gating to `loss_multiple`.

Net effect verified against the real book (84 RED legs / 61 RED
position-groups before): **19 RED legs / 18 RED position-groups after** --
confirmed directly by re-running both the full `tests/` suite and a
standalone re-score of all 206 real legs under the new logic (not
estimated).

## Decision

`heat_scanner.py` now takes `coverage` (`NAKED | COVERED | PARTIAL |
CASH_SECURED_PUT`) as a genuine per-leg SCORING input, computed once
upstream from real owned-shares/contracts data and threaded through, never
guessed inside `heat_scanner.py` itself:

1. **`LegContract.coverage`** (`mcp/analysis/heat_scanner.py`), optional,
   default `"NAKED"` (keeps the dataclass at 4 required fields; a caller that
   doesn't compute coverage gets the pre-ADR-0005 naked-ladder behavior for
   every leg, unchanged -- this is why `heat_from_positions()` below and
   every pre-existing `tests/test_heat_scanner.py` fixture needed no
   coverage argument to keep working).

2. **Two severity ladders**, selected by `coverage`, both in
   `_determine_color()`/`_set_action()`:
   - **`COVERED`** (fully covered call -- real owned shares fully back every
     contract): bypasses `loss_multiple`/`distance_pct` entirely. Urgency is
     purely the same gamma/roll-decision DTE windows every other leg already
     uses -- `dte<=7` RED (`CLOSE_OR_ASSIGN`), `dte<=21` YELLOW
     (`ROLL_CALL_OR_ASSIGN`), else GREEN (`HOLD_TO_ASSIGNMENT`). A deep-ITM,
     high-loss-multiple covered call with real time left is the strategy
     working, not an emergency.
   - **`NAKED`/`CASH_SECURED_PUT`/`PARTIAL`** (the existing "naked ladder"):
     the hard stop (`loss_multiple >= 2.0x`) now shares the exact same
     `RED_DTE_WINDOW` (45d) that `distance_pct` already used --
     `(loss_multiple >= loss_cut OR distance_pct < red_dist) AND dte <=
     45` -> RED; the same condition with `dte > 45` -> YELLOW/`THESIS_WATCH`
     ("past the hard-stop level, but DTE remaining -- re-check thesis before
     cutting on multiple alone") instead of an immediate cut. PARTIAL
     coverage stays on this ladder deliberately -- the uncovered contracts
     still carry real naked risk.

3. **Computed once, fed through, never re-derived separately for scoring**:
   `dashboard/backend/app/services.py`'s `_process_position_legs()` already
   computes per-call coverage (`_leg_coverage_and_strangle_expiries`) before
   this ADR, for the POST-HOC display annotation; that computation is now
   *also* classified into the `coverage` string and included directly in the
   `legs` dict `assess_portfolio_heat()` scores, from the same per-position
   `cov` data, in the same loop iteration -- so the leg that gets SCORED and
   the leg that gets DISPLAYED can never disagree about whether it's
   covered. `heat_scanner.heat_from_positions()` (the weekly/monthly text
   report path) gets its own equivalent `_call_coverage_by_id()` helper,
   mirroring the same shares-remaining/strike-ascending allocation.
   `decision_engine.py`'s own independent `_classify_coverage()` (used for
   `LegDecisionRecord.coverage`) is untouched -- it re-derives the identical
   classification from the same underlying `covered`/`covered_contracts`
   data for its own purposes, so the two stay consistent without a shared
   dependency.

4. **Regime call-tightening exemption**: `_apply_call_tighten()` (AI-bull
   demotion of near-strike YELLOW calls to RED) now excludes `COVERED` calls.
   That demotion exists for naked melt-up/margin risk, which a covered call
   doesn't carry -- a covered call only reaches YELLOW via its own `dte<=21`
   rung, not `distance_pct`, so letting the regime tighten still apply to it
   would reintroduce exactly the false urgency this ADR removes elsewhere.
   PARTIAL stays eligible (its uncovered contracts are real naked exposure).

5. **`sequencer.py`'s `_SEVERITY_RANK`** gets explicit entries for
   `THESIS_WATCH` (rank 3, same as `WATCH_CLOSE` -- past the hard stop but
   not time-bound) and the three COVERED actions, named explicitly rather
   than left to the rank-2 default -- the exact bug class a 2026-11-03 fix
   already called out for `CLOSE_RESTAGGER`. `_is_actionable_leg()`'s
   existing carve-out (excludes fully-covered CALLs from Tier 1 entirely)
   already independently reached the same conclusion this ADR formalizes at
   the scoring layer; the two now agree system-wide instead of only
   matching inside the sequencer.

## Alternatives considered

- **Just raise the loss-cut multiplier for covered calls (e.g. 2.0x ->
  5.0x) instead of a separate ladder.** Rejected -- there is no multiplier
  that's correct for a covered call, since the "loss" is structurally the
  mirror image of a stock gain this engine doesn't see at all. Any
  multiplier threshold still treats a covered call as a smaller version of a
  naked loss instead of a fundamentally different risk shape.
- **Feed combined stock+options P&L into `heat_scanner.py` instead of a
  DTE-only coverage ladder.** Rejected for this iteration -- `get_position_
  detail`'s `combined_net_pnl` is the right number conceptually, but
  depends on `stock_cost_basis`, which this same investigation found is
  suspiciously `$0` for the real OKTA position (exactly equal to
  `shares * current_price`, suggesting a missing-cost-basis data gap, not a
  real zero-cost lot). Scoring real money decisions off an unverified number
  would trade one wrong signal for a differently-wrong one. DTE-only is
  conservative and uses only verified inputs; revisit once cost-basis
  integrity is confirmed (see Open Questions).
- **Leave the naked-ladder hard stop DTE-independent and only fix
  covered calls.** Rejected -- the real-book decomposition showed the
  long-DTE naked/CSP bucket (42 legs) was larger than the covered-call
  bucket (21 legs) and traced to the identical root cause (one signal
  conflated with urgency) already half-fixed for `distance_pct` in the
  2026-10-15 change; fixing only the coverage half would leave the larger
  bucket's false urgency in place.

## Consequences

- RED count on the real live book drops from 84 legs / 61 position-groups
  to 19 legs / 18 position-groups (verified, not estimated -- both the full
  `tests/` suite and a standalone re-score of all 206 real legs confirm
  this).
- A small, intentional side effect: a handful of real legs (5, in the
  standalone re-score) flip GREEN -> YELLOW -- a **far-OTM, safely-covered**
  call nearing its own expiry (`dte<=21`) now surfaces as YELLOW
  (`ROLL_CALL_OR_ASSIGN`) purely because *any* covered call approaching its
  own expiry is a real roll/assign decision point, even a safely-OTM one,
  mirroring the existing `CLOSE_RESTAGGER` gamma-window concept for naked
  legs. This is a deliberate consequence of DTE being the covered ladder's
  only signal, not a regression.
- The pooled, cross-account `covered`/`covered_contracts` DISPLAY annotation
  (`services.py`'s conservative AND-combine across every account holding an
  identical contract) is unchanged and, for a contract held both covered in
  one account and naked in another, can now show a GREEN row and a RED row
  both annotated with the same blended `covered: false` -- a known, accepted
  cosmetic mismatch (see `tests/test_services.py`'s updated fixture
  assertions) out of this ADR's scope. The SCORING was never wrong here --
  each account's own leg is scored with its own real per-account coverage;
  only the shared DISPLAY annotation blends across accounts, as it already
  did before this ADR.
- `tests/test_heat_scanner.py`'s long-standing characterization of the
  loss-cut hard stop as "DTE-independent" is deliberately superseded here,
  with the old fixture (`cut_leg`, originally `dte=90`) moved to `dte=30`
  (still inside the 45d window, still genuinely RED) and a new dedicated
  `thesis_watch_leg` fixture added to characterize the >45 DTE downgrade
  explicitly.
- No change to any dollar figure, margin estimate, or assignment-cash-impact
  calculation anywhere -- this ADR only changes which color/action a leg is
  assigned, never any of the underlying economics `decision_engine.py`
  computes independently.

## Open questions

- `stock_cost_basis` reading `$0` for real held shares (confirmed on the
  OKTA position this ADR's investigation started from) looks like a data
  gap, not a real zero-cost lot -- worth its own investigation. If
  confirmed and fixed, a future ADR could extend the COVERED ladder to
  weigh real combined stock+options P&L instead of DTE alone, which would
  let it distinguish "covered call, stock gain more than offsets it" from
  "covered call, stock cost basis also underwater" -- a real scenario
  this ADR's DTE-only ladder cannot currently distinguish.
- The pooled cross-account display-annotation mismatch (Consequences,
  above) could be resolved by annotating `covered`/`covered_contracts` per
  real per-account leg instead of AND-combining across accounts, but that
  changes `multi_account_contract` display semantics other dashboard
  surfaces may depend on -- out of scope here, flagged for its own Bolt if
  it proves confusing in practice.
