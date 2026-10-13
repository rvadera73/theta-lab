"""One real, ranked priority list across the whole book -- replaces the
three independently-gated Action Tracker sources (priority_actions,
position_heat, and implicitly the composite score's own unranked table)
with a single sequenced answer to "what do I do, in what order."

Built 2026-10-12 directly off the trader's own framing: gates fire first
regardless of score ("address before anything else, not subtract a few
tenths of a point"); existing positions in trouble outrank new entries
(managing a real loss beats deploying new capital); new entries are ranked
by composite score with IV Rank as a tie-breaker, among names that actually
pass the gates. See docs/RECONCILIATION_PROCESS.md's sibling design note
and the approved plan this was built from for the full rationale.

Every row keeps its full current numbers -- tier/rank decides ORDER, it
must never hide the data behind it. This is a thin orchestrator: it calls
services.get_position_heat() and services.get_composite_scores() (both
already real, already tested) and merges their output into one sequence; it
computes no new facts of its own beyond the tiering/sort keys.
"""
from . import services

# Position Heat's own action strings, ranked by real urgency -- matches the
# trader's own stated severity order (cut-now > roll-or-cut > watch > harvest).
_SEVERITY_RANK = {
    "CUT_RESTAGGER": 0, "CLOSE_NOW": 0,
    "ROLL_OR_CUT_PUT": 1, "ROLL_CALL": 1,
    "WATCH_CLOSE": 2,
    "HARVEST_RESTAGGER": 3,
    "PREPARE_ROLL": 3,
}
_COVERAGE_RANK = {False: 0, None: 1, True: 2}  # naked < cash-secured-put/unknown < covered


_COMPOSITE_FIELDS = ("score", "yield_pct", "conviction", "rank", "population_size", "iv_rank", "iv_entry_signal")


def _is_actionable_leg(leg: dict) -> bool:
    """A leg needs attention now: RED/YELLOW and not a fully-covered call
    (a covered call's risk is capped by assignment, not the same urgency as
    naked -- see services.get_position_heat()). Used both to decide whether
    a (symbol, account) position group belongs in Tier 1 at all, and to pick
    the group's worst leg for severity/coverage ranking."""
    return leg.get("color") in ("RED", "YELLOW") and not (
        leg.get("type") == "CALL" and leg.get("covered") is True
    )


def _tier1_rows():
    """Existing positions needing management -- one row per real (symbol,
    account) position, not per leg (real gap found 2026-10-13: a deliberate
    multi-leg 'stagger' campaign like ZS's 3-leg structure or ANET's 8 legs
    across 2 accounts was surfacing as N disconnected-looking alerts instead
    of one position managed as a unit). Each row carries every leg's full
    numbers in "legs" plus the symbol's composite score/IV Rank if it's held
    and scored -- the point of one sequenced list is the full current
    picture per position, not the heat verdict with the score stripped out.
    A group is included only if at least one leg is actionable; severity/
    coverage ranking comes from the worst actionable leg, but every leg
    (including a fine GREEN sibling) stays visible in "legs" for context."""
    heat = services.get_position_heat()
    held_by_ticker = {r["ticker"]: r for r in services.get_composite_scores().get("held", [])}

    rows = []
    for group in heat.get("positions", []):
        actionable = [lg for lg in group["legs"] if _is_actionable_leg(lg)]
        if not actionable:
            continue
        worst = min(
            actionable,
            key=lambda lg: (_SEVERITY_RANK.get(lg.get("action"), 2), _COVERAGE_RANK.get(lg.get("covered"), 1)),
        )
        row = dict(group)
        row["tier_source"] = "position_heat"
        row["severity_rank"] = _SEVERITY_RANK.get(worst.get("action"), 2)
        row["coverage_rank"] = _COVERAGE_RANK.get(worst.get("covered"), 1)
        comp = held_by_ticker.get(group["symbol"])
        if comp:
            for f in _COMPOSITE_FIELDS:
                row[f] = comp.get(f)
        rows.append(row)
    rows.sort(key=lambda r: (r["severity_rank"], r["coverage_rank"]))
    return rows


def _tier2_rows():
    """New-entry candidates -- watchlist rows (is_new=True) from the
    composite score, ranked by score with IV Rank as the tiebreak. Gate
    filtering happens in build_priority_sequence() (a gated name still shows
    up, just promoted to Tier 0 instead of appearing here), not here."""
    scores = services.get_composite_scores()
    rows = []
    for row in scores.get("watchlist", []):
        r = dict(row)
        r["tier_source"] = "composite_score"
        rows.append(r)
    rows.sort(key=lambda r: (-(r.get("score") or -999), -(r.get("iv_rank") or -1)))
    return rows


def build_priority_sequence() -> list[dict]:
    """The one sequence: Tier 0 (any gate fired, from either source) ->
    Tier 1 (existing position management, by severity) -> Tier 2 (gate-clear
    new entries, by score+IV Rank). Every row keeps every field its source
    already computed -- tier/rank decide order, nothing is stripped."""
    t1_all = _tier1_rows()
    t2_all = _tier2_rows()

    tier0 = []
    tier1 = []
    tier2 = []

    for row in t1_all:
        if row.get("gates_fired"):
            row["tier"] = 0
            tier0.append(row)
        else:
            row["tier"] = 1
            tier1.append(row)

    for row in t2_all:
        if row.get("gates_fired"):
            row["tier"] = 0
            tier0.append(row)
        else:
            row["tier"] = 2
            tier2.append(row)

    sequence = tier0 + tier1 + tier2
    for i, row in enumerate(sequence):
        row["rank_in_sequence"] = i + 1
    return sequence


def top_actions(n: int = 10) -> list[dict]:
    """A genuine prefix of build_priority_sequence() -- not a separately
    filtered or re-sorted list, so it can never drift from the full
    sequence it's a condensed view of."""
    return build_priority_sequence()[:n]
