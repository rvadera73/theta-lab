# ADR 0002: Cache Freshness and Loader Error Visibility

**Status:** Accepted
**Date:** 2026-11-05

## Context

A live trading session this day found two real, confirmed bugs in
`mcp/reports/report_utils.py`, both instances of the same underlying
pattern: a module-level, in-process cache with **no expiry at all**, read by
a long-running MCP server process (container uptime since 2026-11-04 17:04
UTC).

1. **`_US_PRICE_CACHE` / `_history_cache()`.** Once a symbol's price was
   fetched, it was cached forever for the life of the process. AppLovin
   (APP) reported earnings after the 2026-11-04 close and rallied further
   pre-market the next morning; `get_position_detail`'s technical snapshot
   kept returning a frozen mid-session Nov-4 price ($236.94) through the
   entire move, confirmed wrong against a direct live yfinance pull showing
   the real price was $331+.
2. **`_SNAPSHOT_HOLDINGS_CACHE` / `_snapshot_holdings()`.** Same shape, same
   missing expiry. `get_position_detail` filters through this ground-truth
   holdings set; it missed a real Fidelity (F1) position that a brand-new
   process (no cache yet) found immediately — the leading explanation being
   that the position entered the snapshot after this process's cache had
   already been populated, and nothing ever invalidated it.

A third, related issue in the same function: `load_us_positions()`'s
per-account loading is intentionally non-fatal (`except Exception: pass`) so
one broken account never blocks the other 7 — but a transient real failure
and a genuine "this account doesn't hold the symbol" result were
indistinguishable to every caller, and the function's own `"warning"` field
was hardcoded to `None`, never actually populated.

## Decision

- `_history_cache()` gets a **time-based TTL** (`_PRICE_CACHE_TTL_SECONDS =
  900`, 15 minutes): a cache entry is re-fetched once it's older than the
  TTL, bounding the worst case to "one refresh cycle" instead of "the life
  of the process." A full market-session-boundary-aware invalidation was
  considered and rejected as unnecessary complexity for what the real
  incident needed — a bounded staleness window, not session-awareness.
- `_snapshot_holdings()` gets a **same-day cache** instead of a time-based
  TTL, matching `symbol_context.py`'s existing `get_cached_symbol_context`
  convention: holdings only change when the trader exports a new snapshot,
  not intra-day, so a day boundary is the right granularity, not minutes.
- `load_us_positions()`'s per-account failures are now recorded via a new
  `_record_account_failure()` helper: logged immediately (visible in server
  logs regardless of whether a caller inspects the result) and collected
  into the function's own `"warning"` field, which is no longer hardcoded to
  `None`. Still fully non-fatal — one bad account still never blocks the
  other 7 — but a real failure is no longer silently indistinguishable from
  a genuine absence.
- Both new clock-like seams (`_now()` for time, `_today()` for the date) are
  isolated as their own one-line functions specifically so tests can
  freeze/advance them without real sleeping or waiting for a day to pass.

## Alternatives considered

- **Remove caching entirely, always fetch live.** Rejected — both caches
  exist for a real reason (avoiding a live Yahoo/snapshot-loader fetch on
  every single call); the bug was the *missing expiry*, not the existence
  of a cache.
- **One shared generic TTL-cache utility for both.** Considered, but the two
  caches have genuinely different correct granularity (minutes vs. a
  calendar day) and different existing precedent to match
  (`_history_cache` has none yet; `_snapshot_holdings` should match
  `symbol_context.py`'s same-day convention) — a shared abstraction would
  have to parameterize away the one thing that actually matters here.
  Two small, explicit fixes were judged clearer than one generic mechanism
  for two call sites.

## Consequences

- A price or holdings lookup is now, at worst, one TTL/day-boundary behind
  reality instead of indefinitely behind reality for the life of a
  long-running process — this does not eliminate staleness, it bounds it.
- `load_us_positions()`'s `"warning"` field is now a real signal callers can
  surface (e.g. in a dashboard banner or a Position Heat annotation) instead
  of a field that always read `None`. No caller was updated to surface it in
  this change — that's a follow-on UI/consumer change, not part of this fix.
- Restarting the MCP server process remains the correct action whenever code
  itself changes (unrelated to this ADR) — this fix only bounds *data*
  staleness within a single process's lifetime, not code staleness.

## Open questions

- Whether `_OPTION_CHAIN_CACHE` and `_EARNINGS_CACHE` (same module, same
  unbounded-cache shape, not touched by this ADR) need the same treatment —
  earnings dates and listed option chains change far less dynamically than
  price/holdings, so they were judged lower-priority and out of scope here,
  not exempted on principle. Worth a follow-up tech-debt pass if either is
  ever found to produce a stale real-world decision the way price/holdings
  did today.
