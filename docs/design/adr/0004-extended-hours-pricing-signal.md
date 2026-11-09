# ADR 0004: Extended-Hours Pricing Signal and Staleness-Field Parity

**Status:** Accepted
**Date:** 2026-11-09

## Context

On 2026-11-05 the trader caught a stale-price risk live: AppLovin (APP)
gapped +22% pre-market on an earnings beat-and-raise, but every pricing path
in this codebase (`scan_position_heat`, `get_live_positions`,
`get_position_detail`) still showed the prior regular-session close, with no
signal anywhere distinguishing "fresh but stale-relative-to-an-overnight-move"
from "actually current." ADR 0002
(`docs/design/adr/0002-cache-freshness-and-loader-visibility.md`) already
fixed the narrower bug this same incident surfaced that day — `_history_cache()`
had no expiry at all and served the same frozen Nov-4 price through the whole
move — by adding a 15-minute TTL (`_PRICE_CACHE_TTL_SECONDS`). That ADR
explicitly considered and rejected session-boundary/pre-post-market pricing
awareness as unnecessary complexity for what the real incident needed: a
bounded staleness window, not session-awareness. The TTL fix bounds *how
stale* a regular-session price can get; it does nothing to tell a caller that
the stock has since moved overnight by a figure large enough to matter before
the next regular-session close is even available.

Separately, the existing `data_source`/`data_as_of`/`days_stale` fields
(added by ADR 0002's `account_sources` mechanism) track file-snapshot age —
when the position CSV/snapshot was last updated — never live price
staleness, and today they are populated only inside `load_us_positions()`'s
Schwab loop (`mcp/reports/report_utils.py`). The CSV-broker loop for
Fidelity/Vanguard/Robinhood never writes to `account_sources` at all, so
these fields come back `None` for every non-Schwab account — roughly half
the book. And `get_position_detail`'s own JSON output (`mcp/server.py`)
doesn't expose these fields at all — only the dashboard's
`get_position_heat` (`dashboard/backend/app/services.py`) does.

## Decision

This ADR does **not** reopen ADR 0002's cache-invalidation scope. The
regular-session close price (`current_price()` / `pos.current_price`) stays
the one authoritative figure for every margin/Opt-Req/notional/P&L
calculation, preserving the Schwab Opt-Req dollar-parity ADR 0002
established — nothing that already produces a dollar figure changes. Instead
this adds a separate, purely additive extended-hours *signal*:

1. **A new cached helper, `get_extended_hours_quote(symbol)`**
   (`mcp/reports/report_utils.py`), using yfinance to get the current
   extended-hours price. Verified live 2026-11-09 against AAPL and APP
   during regular trading hours: yfinance's `fast_info` has no
   `preMarketPrice`/`postMarketPrice`/`marketState` keys in its schema at
   all — it structurally cannot distinguish a pre/post-market quote from a
   regular one. `Ticker.info`, by contrast, carries `marketState` ("PRE",
   "POST", "REGULAR", "CLOSED", …) plus real `preMarketPrice`/
   `postMarketPrice`/`regularMarketPrice` fields that Yahoo only populates
   outside regular hours. `get_extended_hours_quote` therefore uses `.info`,
   not `fast_info` or a second `prepost=True` history call (which would
   require re-deriving the same pre/post classification from raw minute-bar
   timestamps instead of reading Yahoo's own classification directly).
   Cached via `get_cached_extended_hours_quote`, a same-day JSON disk cache
   mirroring `mcp/analysis/premium_yield.py`'s `get_cached_batch_yield`
   convention exactly (date-keyed file, an `_is_usable`-style filter so a
   stale/failed entry is never reused just because it shares today's date) —
   this codebase's established same-day caching pattern, not a new one.
2. **Three new fields surfaced wherever per-leg/per-symbol pricing is
   already returned**: `live_price`, `live_price_source` (one of
   `"regular"`, `"pre_market"`, `"after_hours"`), `overnight_move_pct` (the
   live price vs. the regular-close price already used for margin math).
   Computed once via a shared `extended_hours_context(symbol,
   regular_close_price)` helper so the shape can't drift between call sites,
   and wired into: `dashboard/backend/app/services.py`'s
   `get_position_heat()` (per leg), `mcp/server.py`'s `get_position_detail`
   (per symbol — previously missing staleness/extended-hours fields
   entirely), `scan_position_heat` (its own separate per-leg output path,
   does not share code with `get_position_heat`), and `get_live_positions`
   (its own separate per-symbol equities/options output).
3. **`data_source`/`data_as_of`/`days_stale` parity for Fidelity/Vanguard/
   Robinhood**, populated into `account_sources` by the CSV-broker loop in
   `load_us_positions()` the same way the Schwab loop already does — source
   name (the broker key, e.g. `"fidelity_csv"`), `as_of` (the backing CSV/PDF
   file's mtime date), `days_stale` (today minus that date).
4. **A new `OVERNIGHT_MOVE` gate**: when `abs(overnight_move_pct)` exceeds
   `OVERNIGHT_MOVE_GATE_PCT` (`mcp/config.py`, default 10.0 — a conservative,
   named floor below the real APP +22% incident, not a tuned guess), add
   `"OVERNIGHT_MOVE"` to that leg/symbol's `gates_fired` list.
   `mcp/analysis/symbol_context.py` already established the `gates_fired`
   convention (a flat `list[str]`, appended to as each gate's predicate
   fires — see `HIGH_LEVERAGE`/`EARNINGS_RISK`/`ILLIQUID`) for unrelated
   prior work (the composite-score/Position-Heat gate bundle); this reuses
   that exact shape rather than introducing a second gate framework.

## Alternatives considered

- **Reopen ADR 0002 and add session-boundary awareness to the price cache
  itself.** Rejected — ADR 0002 already made this call deliberately; this
  signal is additive precisely so that decision doesn't need to be revisited,
  and so no existing dollar figure is put at risk of drifting between a
  "regular" and an "extended-hours" basis mid-calculation.
- **`fast_info` for the live quote.** Rejected after live verification —
  its schema has no pre/post-market fields at all, so it cannot express
  `live_price_source`.
- **A `prepost=True` minute-bar history call, classifying rows by
  timestamp against the exchange calendar.** Rejected — `.info`'s
  `marketState`/`preMarketPrice`/`postMarketPrice` already carry Yahoo's own
  classification; re-deriving it from raw bars is strictly more code for the
  same answer.
- **A new cross-cutting gate framework.** Rejected — `symbol_context.py`'s
  existing `gates_fired: list[str]` convention already does exactly this job
  for `HIGH_LEVERAGE`/`EARNINGS_RISK`/`ILLIQUID`; `OVERNIGHT_MOVE` is one more
  entry in the same list, not a new mechanism.

## Consequences

- One extra yfinance call per symbol per refresh cycle, same-day cached —
  the same cost shape `get_cached_batch_yield` and `get_cached_symbol_context`
  already accept for comparable per-symbol enrichment data.
- No existing dollar figure anywhere changes — `current_price()`/
  `pos.current_price` remains the only input to margin/Opt-Req/notional/P&L
  math; `live_price`/`overnight_move_pct` are read-only context alongside it.
- Staleness-field parity across all 4 broker types is bundled into this same
  Bolt since both changes touch the same per-leg annotation code path
  (`load_us_positions()`'s `account_sources`, consumed by the same
  per-leg/per-symbol output functions this ADR already has to touch for the
  extended-hours fields).
- `OVERNIGHT_MOVE` firing does not itself force any action (no auto-roll,
  no auto-close) — same "advisory signal, human decides" posture as every
  other gate in `symbol_context.py` and `heat_scanner.py`.

## Open questions

- Whether `OVERNIGHT_MOVE_GATE_PCT` should vary by symbol volatility/sector
  (a 10% move means something different for a mega-cap index name than for
  a speculative small-cap) — out of scope here; revisit if a false-positive/
  false-negative pattern shows up in practice, same posture ADR 0002 took on
  `_OPTION_CHAIN_CACHE`/`_EARNINGS_CACHE`.
- Whether the same-day cache granularity (adequate for a per-refresh-cycle
  signal) needs to tighten if refresh cycles are ever run more than a
  handful of times per day — not a real problem yet, no caller currently
  refreshes more often than that.
