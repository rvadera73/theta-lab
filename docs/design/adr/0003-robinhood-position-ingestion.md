# ADR 0003: Robinhood Position Ingestion — Replace the Broken Symbol-Field Parser with the Real Transaction-Log Netter

**Status:** Accepted
**Date:** 2026-11-09

## Context

`parse_robinhood_csv()` (`mcp/analysis/pnl.py`, originally lines 409-493) is
the sole Robinhood ingestion path wired into `load_us_positions()`
(`mcp/reports/report_utils.py`, originally lines 1139-1151, for accounts D
and E — "Robinhood Individual" and "Robinhood Traditional IRA" per
`mcp/config.py` lines 92 and 94). It requires a header line containing
`"Symbol"` plus `"Quantity"`/`"Average Cost"`, and expects option exposure
encoded directly in a `Symbol` field, e.g. `"AAPL 01/17/2025 Call $200.00"`.

The REAL Robinhood exports this repo has ever had — `data/positions/
robinhood_rahul_individual.csv`, `data/positions/robinhood_rahul_traditional
.csv`, and every archived export (e.g. `data/positions/arch/
Robinhood_Account1_20260511.csv`) — are **transaction/activity logs**, not
position snapshots, with the real header:

```
"Activity Date","Process Date","Settle Date","Instrument","Description","Trans Code","Quantity","Price","Amount"
```

and `Trans Code` values `STO`/`BTC`/`BTO`/`STC`/`OASGN`/`ACH`/`INT`/`CDIV`/etc.
No `"Symbol"` column exists in any real file (confirmed by inspecting the
real individual and traditional-IRA exports directly). Because header
detection in `parse_robinhood_csv()` requires `"Symbol"`, the function
returns `[]` against every real Robinhood export this repo has ever had —
not just options, equities too — so Robinhood accounts D and E have
contributed **zero** positions to `load_us_positions()` for as long as this
parser has existed.

A working transaction-log netter for exactly this format already exists:
`scripts/open_positions_loader_v2.py`'s `_calculate_open_positions()`
(originally lines 638-944, with the actual per-contract netting decision at
lines ~854-883 and the `_contract_id`/groupby logic at lines ~802-823). Its
own comment at line 859 already notes "Robinhood uses 'Trans Code' (STO/BTC/
BTO/STC)". But this pipeline is only consumed, via `OpenPositionsLoaderV2
.load_all_data()`, by `_snapshot_holdings()` (`mcp/reports/report_utils.py`,
originally lines 701-736) to build a bare ticker-only filter set — no
strike/expiry/premium/mark ever reaches per-leg detail in
`get_position_heat`/`get_position_detail`/`scan_position_heat`/
`get_live_positions`.

This exact problem, and this exact fix direction, is already recorded for a
related code path in `logs/portfolio_rotation_review_2026-Q4.md` (lines
122-130): Fidelity/Vanguard/Robinhood env-var-driven parsing was found to be
unreliable, with the decision explicitly deferred as "keep those env vars
current each reconciliation, or retire this separate parsing path entirely
in favor of reusing `open_positions_loader_v2.py` (the same pipeline every
other tool already trusts)." This ADR takes the latter option, for Robinhood
specifically.

Two unrelated functions share a confusingly similar name and must not be
conflated with the above: `analysis.pnl.parse_robinhood_positions()` (a
converter for the LIVE `robin_stocks` API path, unused by `load_us_positions
()`, untouched by this ADR) and `scripts/update_snapshot.py`'s own, separate
`parse_robinhood_positions()` (also untouched). Only `parse_robinhood_csv()`
is in scope.

## Decision

Extract the core netting *decision* — classifying one transaction row's
effect on a contract's net open quantity (opening vs. closing, by action
text or Trans Code) — out of `open_positions_loader_v2.py`'s inline chain
into a new shared module, **`mcp/reports/robinhood_netting.py`**:

- `classify_action(action, qty, source="") -> (delta, is_opening)` is a
  byte-for-byte port of the original inline chain (same token lists, same
  sign convention), so there is exactly one implementation of "does this
  action open or close a contract, and by how much" — not two. This
  function already handles Schwab/Fidelity/Vanguard English action strings
  ("Sell to Open", "Buy to Close", ...) and Robinhood's Trans Code
  abbreviations (STO/BTC/BTO/STC) in the same chain, because the original
  code already did — it genuinely is broker-agnostic, not just
  Robinhood-specific.
- `open_positions_loader_v2.py`'s `_calculate_open_positions()` now imports
  and calls `classify_action()` instead of inlining the chain, preserving
  its exact existing behavior (same ticker-only output, same callers, same
  `_snapshot_holdings()` consumer) — parity is structural, since the ported
  code is unchanged token-for-token.
- The new Robinhood-specific layer lives in the same module:
  `parse_robinhood_transaction_csv(csv_path) -> list[dict]` (real
  multi-line-quoted-field-safe CSV parsing, option-description regex for
  `"TICKER M/D/YYYY Put/Call $STRIKE"`, and Trans Code normalization — see
  "Robinhood-specific extension" below for `OASGN`), and
  `net_robinhood_option_legs(rows) -> list[dict]`, which groups by
  (ticker, strike, expiry, option_type), calls `classify_action()` per row,
  and additionally tracks **net cash flow** (Robinhood's own `Amount` column
  is already signed — credit positive, debit negative — so summing it per
  contract gives real net premium collected/paid without needing Schwab's
  `max(0, amount)` heuristic) and **open date** (earliest opening row),
  producing full per-leg detail: symbol, strike, expiry, option_type, signed
  quantity, premium received, and open date — not just a ticker.
- `mcp/reports/report_utils.py` gets a new `load_robinhood_positions(csv_path,
  account_label) -> list[Position]`, modeled directly on the existing,
  already-proven `reconstruct_positions_from_transactions()` pattern in the
  same file (per-contract dict accumulation, `OptionLeg` construction with a
  `current_mark=0` placeholder, then a live cost-to-close backfill via the
  existing `_fill_current_marks()` helper — reused as-is, not reinvented).
  This is wired into `load_us_positions()`'s `robinhood_csv` branch,
  replacing the `parse_robinhood_csv()` call.
- `parse_robinhood_csv()` is deleted entirely from `mcp/analysis/pnl.py` —
  its only production caller is the one being replaced, and its only other
  reference is a test mock, updated to mock the new function instead (see
  Step 3 of the implementation).
- `_snapshot_holdings()` is **not** changed to make a second, direct call to
  the shared function — it already fully delegates to
  `OpenPositionsLoaderV2.load_all_data()`, which (per the point above) now
  itself calls `classify_action()` internally. It therefore already uses
  the one shared implementation transitively; it never had a separate,
  duplicate reduced netting path of its own to remove.

### File-location judgment call

The task description left the exact file location open ("a new small module
... or directly in `report_utils.py`"). A brand-new `mcp/reports/
robinhood_netting.py` was chosen over inlining into `report_utils.py`
because: (1) `classify_action()` must be importable from `scripts/
open_positions_loader_v2.py`, a different top-level directory with no
existing dependency on `mcp/reports/report_utils.py`'s much larger import
surface (yfinance, routines.email_report, bootstrap credential loading,
etc.) — a small, dependency-free module is safe for `scripts/` to import;
`report_utils.py` itself is not. (2) It keeps the Robinhood-specific
CSV/regex/Trans-Code parsing — logic no other broker needs — out of the
already-1400-line `report_utils.py`, matching the existing precedent of
broker-specific parsers living in their own place (`analysis/pnl.py`'s
per-broker functions). `report_utils.py` only gains the one new orchestration
function, `load_robinhood_positions()`, that bridges the shared module's
output into the `Position`/`OptionLeg` shape every other broker already
produces.

### Robinhood-specific extension beyond the ported chain

The real individual-account export contains a live edge case the original
`classify_action()` token list does not cover: an **option assignment**
(`Trans Code` `OASGN`), e.g. a DKNG $35 put sold-to-open 1/14/2026, then
assigned (`OASGN`, 10/14/2026, no price/amount — the resulting 100-share
stock purchase appears as a separate `Buy` row with a multi-line
`Description`). `OASGN` matches none of `classify_action()`'s existing
tokens, so it would silently fall into the default "treat as an opening
add" branch — double-counting an assigned (and therefore closed) contract
as if it were still open. `parse_robinhood_transaction_csv()` normalizes
`OASGN` (and `ASSIGN`/`EXPIRE`/`EXERCISE` variants) to the closing (`BTC`)
bucket before handing rows to `classify_action()`. This is a Robinhood-
transaction-log-specific normalization step, not a change to
`classify_action()` itself (which stays byte-for-byte identical to the
original chain, preserving `open_positions_loader_v2.py`'s existing
behavior for all 8 accounts).

Equity shares arriving via option assignment/exercise (the `Buy`/`Sell` rows
that accompany an `OASGN`) are out of scope for this ADR — this fix targets
the option-leg break the background section describes; Robinhood-side
equity-share netting from the transaction log is not implemented and
remains a follow-on if it's ever found to matter (accounts D/E are
configured for `cash_secured_put`/`covered_call` strategies only, per
`mcp/config.py`'s `ACCOUNT_D`).

## Alternatives considered

- **Wire `load_us_positions()` directly to `OpenPositionsLoaderV2` (the
  pandas, all-8-account pipeline) instead of writing a new, lighter
  Robinhood-only path.** Rejected — that pipeline only ever produces an
  abs() net quantity and a ticker, by design (that's all `_snapshot_holdings
  ()` has ever needed); teaching it to also carry signed quantity/premium/
  open-date for every broker risked destabilizing the one thing every
  report in this repo already trusts it for. A focused Robinhood-only
  per-leg path, sharing only the core classification decision, is smaller
  and safer.
- **Fix the env-var staleness problem instead (the other option
  `portfolio_rotation_review_2026-Q4.md` left open).** Rejected — the env
  vars being stale/blank is a real but separate problem from the parser
  requiring a `"Symbol"` header that no real export has ever had; fixing
  the env vars alone would still return `[]` against the real file format.
- **Leave `parse_robinhood_csv()` in place as a second, inert parser "in
  case a true position-snapshot-style Robinhood export ever shows up."**
  Rejected per the task's explicit direction and basic hygiene — two
  parsers for the same account types is exactly the duplicate-code-path
  problem this ADR exists to retire, and no such export has ever existed in
  this repo's history.

## Consequences

- Robinhood accounts D (Individual) and E (Traditional IRA) now show up in
  `get_position_heat`/`get_position_detail`/`scan_position_heat`/
  `get_live_positions` with real per-leg data (strike, expiry, option_type,
  signed quantity, premium received) for the first time — previously zero
  contribution from these two accounts.
- `_snapshot_holdings()`'s ticker list becomes, more clearly than before, a
  byproduct of the one shared classification function rather than a
  separately-reasoned-about computation — though its own call path
  (`OpenPositionsLoaderV2`) is structurally unchanged.
- This is a real (small) refactor, not a pure bugfix: a new module, a new
  `report_utils.py` function, and one deleted function — but it avoids a
  permanent second, duplicate netting implementation, per the direction
  already recorded in `logs/portfolio_rotation_review_2026-Q4.md`.
- `OASGN`/assignment handling is now correct for Robinhood specifically;
  `open_positions_loader_v2.py`'s own generic chain is untouched and may
  still mis-handle an `OASGN`-style row the same way it always has for any
  broker — out of scope here, not newly introduced by this change.

## Open questions

- Whether Robinhood equity-share positions (outside of option
  assignment/exercise) ever need their own transaction-log netting path —
  not implemented here; revisit only if accounts D/E are ever used for
  outright stock, which their current strategy configuration
  (`cash_secured_put`/`covered_call` only) does not anticipate.
- Whether `open_positions_loader_v2.py`'s own generic `classify_action()`
  chain should eventually get the same `OASGN`/assignment-normalization fix
  for all brokers (currently Robinhood-only, applied before the shared
  function is called) — deferred, since the ticker-only consumer
  (`_snapshot_holdings()`) tolerates the existing imprecision and this ADR's
  scope is Robinhood per-leg detail, not a correctness audit of the
  all-broker pipeline.
