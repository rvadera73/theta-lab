"""
Shared position-priority helpers used by both the US (reports/weekly_report.py)
and India (reports/india_weekly_report.py) Monday weekly-action reports, plus
the DTE helper also used internally by this package's own pnl.py broker
position parsers.

Extracted per GitHub issue #61 -- three near-identical copies were found:

  - `_dte_label()` was 100% identical between weekly_report.py and
    india_weekly_report.py.

  - `_priority()`'s first ~10 lines (loss flag -> DTE urgency -> profit
    target -> roll signal) were identical between the two files, before
    India's version layered its own permanent-exit-list check and two extra
    WEAK/EXTENDED verdict branches on top. That shared prefix now lives here
    as `priority_prefix()`, returning None the moment none of its own
    conditions match so each market's own `_priority()` can keep applying
    its market-specific checks (its own permanent-exits set, India's verdict
    branches) before falling back to its own final WATCH default.

  - `_dte_from_expiry()` in india_weekly_report.py duplicated the same
    ISO-parse-and-subtract logic already in pnl.py (used there by every
    broker position parser -- Schwab/Fidelity/Vanguard), under a trivially
    different signature (india_weekly_report.py's version took only
    `expiry` and defaulted `today` to `date.today()` internally, instead of
    taking it as a parameter). pnl.py's two-parameter version is the one
    kept here as the single canonical implementation; pnl.py and
    india_weekly_report.py both now import it from here instead of each
    defining their own copy.

A DTE-threshold or urgency-label change made to only one of these call
sites used to silently desync US and India weekly action priorities -- see
issue #61 for the original finding. Any future change to this logic now
only needs to happen once.
"""

from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover -- type-checking only, no runtime import
    from analysis.pnl import Position


def _dte_label(dte: int) -> str:
    if dte <= 7:   return f"⚠️ {dte}d — URGENT"
    if dte <= 21:  return f"🔶 {dte}d — act soon"
    if dte <= 45:  return f"🟡 {dte}d — watch"
    return f"🟢 {dte}d"


def _dte_from_expiry(expiry: str, today: date) -> int:
    """Days remaining to an ISO ('YYYY-MM-DD') expiry string; 0 if unparsable."""
    try:
        return (date.fromisoformat(expiry) - today).days
    except (ValueError, TypeError):
        return 0


def priority_prefix(position: "Position", regime_str: str) -> Optional[tuple[int, str, str]]:
    """Shared prefix of both markets' `_priority()`: loss flag -> DTE
    urgency -> profit target -> roll signal.

    Returns (priority 1-5, label, reason) the moment one of these
    conditions matches, or None if none of them do -- in that case the
    caller should continue with its own remaining market-specific checks
    (permanent-exit list, India's WEAK/EXTENDED verdict branches) before
    falling back to its own final WATCH default. Keeping that None-vs-tuple
    contract (rather than this function picking a default itself) is what
    lets each market still own its own fallback behavior unchanged.
    """
    roll = position.roll_signal()
    loss = position.loss_flag()
    profit = position.profit_take_signal(regime_str)

    if loss["flag"]:
        return 1, "URGENT", f"Mark {loss['multiplier']}x premium — flag and review"
    for leg in position.option_legs:
        if leg.dte <= 7:
            return 1, "URGENT", f"Expires in {leg.dte} days — decide now"
    if any(leg.dte <= 21 for leg in position.option_legs):
        return 2, "URGENT", "Within 21 DTE — roll or close"
    if profit["signal"]:
        return 2, "REVIEW", f"At profit target ({profit['pct_captured']}% captured)"
    if roll["signal"]:
        return 3, "MONITOR", "Approaching roll threshold"
    return None
