"""Shared same-day cache helpers for live market-data fetches (an option
chain, a dividend/earnings/sector bundle, an extended-hours quote, a yield-
on-capital pull) that are expensive or rate-limit-risky to re-fetch on every
report/refresh cycle but only need to be fresh once per calendar day.

Generalizes premium_yield.get_cached_batch_yield -- the original, most
mature implementation of this pattern, hardened over several live bug fixes
(see that function's own docstring) -- so symbol_context.py and
report_utils.py's own same-day caches (get_cached_symbol_context,
get_cached_extended_hours_quote) stop independently hand-rolling the
identical read-filter-fetch-merge-write skeleton, each with its own subtly
different edge cases waiting to happen.

Deliberately NOT used for report_utils.py's `_US_PRICE_CACHE` /
`_INDIA_PRICE_CACHE` (a genuinely different mechanism -- an N-seconds TTL,
not a calendar-day boundary; found live 2026-11-05 that this cache needs to
expire within a single session because a regular-session price can go
stale through an overnight move in minutes, not once a day -- unifying it
into calendar-day semantics would silently reintroduce that exact fixed
bug) nor for `_SNAPSHOT_HOLDINGS_CACHE` (already correctly implements this
file's own day-boundary convention, single-value, with a "don't cache a
transient failure" rule and a dedicated regression test pinned to its exact
internal shape -- no real duplication left to remove there).
"""
import json
import os
from typing import Any, Callable


def same_day_json_cache(
    cache_path,
    today: str,
    keys: list,
    loader_fn: Callable[[list], dict],
    is_usable: Callable[[Any], bool] = lambda _v: True,
) -> dict:
    """File-backed same-day cache for a batch of string keys.

    Semantics (unchanged from the original premium_yield.py implementation):
    a stored cache file is trusted ONLY if its "date" field equals `today`
    (a real calendar-day boundary -- a cache from any earlier day, even one
    second before midnight, is never reused). `loader_fn(missing_keys) ->
    {key: value}` is called ONCE with every key not already usably cached
    for today -- a batch caller (premium_yield's batch_get_yield_on_capital)
    gets one real batch fetch; a single-key caller just passes a 1-element
    `keys` list and a loader that returns a 1-entry dict for that key (see
    symbol_context.get_cached_symbol_context and
    report_utils.get_cached_extended_hours_quote).

    An entry is written to disk only if `is_usable(value)` accepts it -- an
    entry that failed structurally (an explicit error) OR came back a
    hollow "successful" non-result (e.g. a Yahoo bid=ask=0.0 data gap, or a
    structurally-fine-but-empty bundle) is never persisted, so a transient
    failure cached earlier today never blocks a retry later the same day.
    The in-memory result returned to the immediate caller still includes
    this call's own fresh entries even when NOT usable (it was never a
    failure for the original caller to see what actually came back -- only
    a LATER day's cache read should never see it).
    """
    cache: dict = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                stored = json.load(f)
            if stored.get("date") == today:
                cache = {k: v for k, v in stored.get("data", {}).items() if is_usable(v)}
        except Exception:
            pass

    missing = [k for k in keys if k not in cache]
    if missing:
        fresh = loader_fn(missing)
        cacheable = {k: v for k, v in fresh.items() if is_usable(v)}
        if cacheable:
            try:
                cache_dir = os.path.dirname(cache_path)
                if cache_dir:
                    os.makedirs(cache_dir, exist_ok=True)
                with open(cache_path, "w") as f:
                    json.dump({"date": today, "data": {**cache, **cacheable}}, f)
            except Exception:
                pass
        cache.update(fresh)

    return {k: cache[k] for k in keys if k in cache}


def ensure_same_day(dict_cache: dict, date_holder: list, today: str) -> None:
    """In-process counterpart for a plain module-level dict cache that is
    NOT file-backed (report_utils._OPTION_CHAIN_CACHE, _EARNINGS_CACHE --
    found, while reading every cache in that file for this unification, to
    have NO staleness check at all: a dict that memoizes for the entire life
    of the process, the same unbounded-cache bug class already fixed live
    2026-11-05 for _US_PRICE_CACHE and _SNAPSHOT_HOLDINGS_CACHE in that same
    file). Clears `dict_cache` IN PLACE (so the caller's existing
    module-level dict object stays valid -- no rebinding needed, which a
    plain reassignment can't do across module boundaries anyway) the first
    time this is called on a new calendar day, then updates `date_holder[0]`
    (a 1-element list standing in for a mutable "last reset date" cell,
    since a bare str/None module global can't be rebound from inside this
    helper the way a mutable container can).
    """
    if date_holder[0] != today:
        dict_cache.clear()
        date_holder[0] = today
