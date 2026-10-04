"""Real, realized (FIFO-matched) P&L per ticker over a trailing window --
built 2026-10-04 to answer a direct question: which stock actually
performed best, by real captured premium, and how does that compare to
what the composite score model's technical/quality read says about it
right now. Deliberately a SEPARATE result from compute_composite_scores()
(composite_score.py) -- past realized outcome and current forward-looking
score answer different questions and must never be silently blended into
one ranked list; the caller renders them side by side, not merged.

Reuses realized_pnl.py's own event-gathering functions (schwab_events,
fidelity_events, robinhood_events) and per-broker key parsers so there is
only ever one place that knows how to read these files -- aggregates by
ticker (via the parsed FIFO key) instead of by calendar month, which is
the only thing realized_pnl.py's own fifo_realize() does differently.
"""
import sys
from collections import defaultdict, deque
from datetime import date, timedelta

sys.path.insert(0, "/".join(__file__.split("/")[:-3]) + "/scripts")
import realized_pnl as _rp
from update_snapshot import (
    find_schwab_transactions, find_fidelity_transactions, find_robinhood_transactions,
)


def realized_pnl_by_ticker(days: int = 90, today: date | None = None) -> dict:
    """Returns {"cutoff": iso-date, "ranked": [(ticker, realized_pnl, closed_count), ...]}
    sorted descending by realized P&L, for every ticker with at least one
    FIFO-matched close in the trailing `days` days across Schwab/Fidelity/
    Robinhood option transaction history (Vanguard carries no option
    activity, consistent with the rest of this project's standing scope)."""
    today = today or date.today()
    cutoff = today - timedelta(days=days)

    events_by_key = defaultdict(list)

    def collect(events, ticker_fn):
        for d, key, side, qty, amount in events:
            if d < cutoff:
                continue
            parsed = ticker_fn(key)
            ticker = parsed[0] if parsed else key.split()[0]
            events_by_key[key].append((d, ticker, side, qty, amount))

    for _label, path in find_schwab_transactions().items():
        opt_ev, _eq_ev = _rp.schwab_events(path)
        collect(opt_ev, _rp._parse_schwab_key)

    for _person, path in find_fidelity_transactions().items():
        for _acct, (opt_ev, _eq_ev) in _rp.fidelity_events(path).items():
            collect(opt_ev, _rp._parse_fidelity_key)

    for _label, path in find_robinhood_transactions().items():
        opt_ev, _eq_ev = _rp.robinhood_events(path)
        collect(opt_ev, _rp._parse_robinhood_key)

    realized_by_ticker = defaultdict(float)
    closed_count_by_ticker = defaultdict(int)
    queues = defaultdict(deque)

    for key, evs in events_by_key.items():
        evs.sort(key=lambda e: (e[0], 0 if e[2] == "open" else 1))
        for _d, ticker, side, qty, amount in evs:
            if qty <= 0:
                continue
            per_unit = amount / qty
            if side == "open":
                queues[key].append([qty, per_unit, ticker])
            else:
                remaining = qty
                while remaining > 1e-9 and queues[key]:
                    lot = queues[key][0]
                    take = min(remaining, lot[0])
                    realized_by_ticker[ticker] += (lot[1] + per_unit) * take
                    lot[0] -= take
                    remaining -= take
                    if lot[0] <= 1e-9:
                        queues[key].popleft()
                closed_count_by_ticker[ticker] += 1

    ranked = sorted(
        ((t, round(pnl, 2), closed_count_by_ticker[t]) for t, pnl in realized_by_ticker.items()),
        key=lambda x: -x[1],
    )
    return {"cutoff": cutoff.isoformat(), "days": days, "ranked": ranked}
