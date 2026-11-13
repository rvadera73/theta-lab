"""
Decision Engine -- ADR 0001
============================
Turns Position Heat's per-leg monitoring output into per-leg decisions: one
LegDecisionRecord per leg, with an explicit coverage enum, an assignment-
cash-impact calculation, and a time axis kept independent of severity.

This exists because every ad hoc script written against
services.get_position_heat() this session made the same mistake in a
different shape: a FIXED-LIST naked-call check missed a newly-naked OKTA
$140C because it filtered a symbol list instead of a predicate
(`covered is False`); sequencer.py's severity rank had no entry for the
CLOSE_RESTAGGER action, so a forced near-expiry close silently ranked the
same as a merely-watched position. Both are instances of the same bug
class: completeness checked by memory instead of by a predicate over every
leg. This module's job is to make "is every leg covered" a property
PROVEN by tests/test_decision_engine.py, not re-verified by eye each time.

Phase 1 scope (see docs/design/adr/0001-decision-engine-foundation.md):
this wraps heat_scanner.py's existing severity/action verdict verbatim
(parity, not a new ruleset yet) and adds the axes heat_scanner.py has no
concept of -- explicit coverage classification, assignment-cash-impact,
a Reg-T margin estimate (step 4), and a dividend/early-exercise gate on
short calls (step 5, forcing_event "EX_DIV"). margin_source is always
explicit ("REG_T_ESTIMATE" or "UNAVAILABLE" when price/strike data is
missing) so a caller can tell "computed, here's the number" from "not
computed," and never mistakes this estimate for the real Balances-export
Option Requirement figure.

Input: one leg dict exactly as produced by
dashboard/backend/app/services.get_position_heat()'s "positions[*].legs"
(same shape as "by_color"/"top_actions" rows -- see that function's
_leg_summary()/_annotate() for the authoritative field list). This module
takes plain dicts, not that package's types, so it has no import-time
dependency on the dashboard app and can be unit-tested standalone.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import date as _date
from typing import Literal

Coverage = Literal["NAKED", "COVERED", "PARTIAL", "CASH_SECURED_PUT", "NA_LONG"]

# DTE threshold mirrored from heat_scanner.py's own _set_action() (CLOSE_RESTAGGER
# fires at dte<=21) -- NOT re-derived independently, so this module's notion of
# "forced by expiry" never drifts from the action verdict it annotates.
_EXPIRY_FORCING_DTE = 21


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

    # Coverage -- replaces the covered bool/None overload (None on a PUT
    # means "concept doesn't apply," per services.py:331 -- never "unknown")
    coverage: Coverage

    # Economics
    premium_received: float
    cost_to_close: float | None
    loss_multiple: float | None
    pnl_pct: float | None
    current_price: float | None
    distance_pct: float | None

    # Margin -- always an estimate, never trusted as exact; UNAVAILABLE
    # until ADR 0001 step 4 (Reg-T formula) lands.
    est_margin_requirement: float | None
    margin_source: Literal["REG_T_ESTIMATE", "UNAVAILABLE"]

    # Assignment path
    itm: bool
    assignment_cash_impact: float | None        # + = cash received, - = cash required
    assignment_resulting_position: str | None

    # Time axis -- independent of severity (the CLOSE_RESTAGGER bug class,
    # generalized: a forced near-term event must never be ranked/read as
    # equal to a merely market-driven one just because severity matches).
    time_bound: bool
    forcing_event: Literal["EXPIRY", "EARNINGS", "EX_DIV"] | None
    days_to_forcing_event: int | None

    # Severity axis -- reused verbatim from heat_scanner.py, not recomputed
    severity: str
    sector: str | None = None

    # Portfolio-rollup inputs (ADR 0001 step 7): per-leg Black-Scholes delta
    # in share-equivalents, ESTIMATED from current_iv_pct (real if a caller
    # upstream supplied one per step 6, else iv_rank's HV-proxy fallback) --
    # same "estimate, not exact" discipline as margin/dividend above. Signed
    # for a SHORT position (every leg this engine sees): a short call's
    # delta is negative, a short put's is positive, matching real portfolio
    # risk direction.
    delta_shares: float | None = None
    delta_source: Literal["BLACK_SCHOLES_ESTIMATE", "UNAVAILABLE"] = "UNAVAILABLE"

    gates_fired: list[str] = field(default_factory=list)

    # Decision
    recommended_action: str = ""
    rule_citation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _opt_type(leg: dict) -> str | None:
    return leg.get("type") or leg.get("option_type")


def _classify_coverage(leg: dict) -> Coverage:
    """Prefers the real, per-account `coverage` field heat_scanner.py now
    scores every leg with (ADR 0005) over the older `covered`/
    `covered_contracts` pair below, which is a POOLED, cross-account-
    AND-combined display annotation (services.py) that can disagree with
    the real per-leg coverage for a contract held covered in one account
    and naked in another -- confirmed live, not hypothetical (see
    tests/test_services.py's AAPL $200 CALL fixture). Falling back to the
    old predicate only for legs that predate ADR 0005 and never set
    `coverage` at all (e.g. a caller this module was unit-tested against
    before that field existed) keeps this module's own promise, stated in
    its module docstring, of not re-deriving a classification some other
    layer already computed."""
    coverage = leg.get("coverage")
    if coverage in ("NAKED", "COVERED", "PARTIAL", "CASH_SECURED_PUT"):
        return coverage
    if _opt_type(leg) == "PUT":
        return "CASH_SECURED_PUT"
    covered = leg.get("covered")
    if covered is True:
        return "COVERED"
    covered_ct = leg.get("covered_contracts") or 0
    if covered is False and covered_ct > 0:
        return "PARTIAL"
    return "NAKED"


def _is_itm(leg: dict) -> bool:
    price = leg.get("current_price")
    strike = leg.get("strike")
    if price is None or strike is None:
        return False
    return price < strike if _opt_type(leg) == "PUT" else price > strike


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _black_scholes_delta(opt_type: str, price: float | None, strike: float | None,
                          dte: int | None, iv_pct: float | None) -> float | None:
    """Standard long-option Black-Scholes delta (call in [0,1], put in
    [-1,0]) -- ADR 0001 step 7, for the portfolio Greeks rollup. Uses a
    0% risk-free rate for simplicity (no rate is tracked anywhere in this
    codebase, and its effect on delta at realistic DTE/strike distances is
    small) -- an explicit approximation, same discipline as margin/dividend
    above, not a precise pricing model. iv_pct is a percentage (e.g. 35.2),
    matching iv_rank.py's own `current_iv_pct` output convention (issue #56).
    """
    if not price or not strike or not dte or not iv_pct or price <= 0 or strike <= 0 or dte <= 0 or iv_pct <= 0:
        return None
    sigma = iv_pct / 100.0
    t = dte / 365.0
    try:
        d1 = (math.log(price / strike) + 0.5 * sigma * sigma * t) / (sigma * math.sqrt(t))
    except (ValueError, ZeroDivisionError):
        return None
    n_d1 = _norm_cdf(d1)
    return n_d1 if opt_type == "CALL" else n_d1 - 1.0


def _reg_t_margin(leg: dict, coverage: Coverage) -> float | None:
    """Reg-T naked-equity-option margin estimate (ADR 0001 step 4): for a
    CALL, the greater of (20% of underlying - OTM amount) or 10% of
    underlying, plus premium received; for a PUT, the same except the floor
    uses the strike (exercise) price instead of the underlying -- matches
    the formula brokers (Schwab included) publish for uncovered equity
    options. An ESTIMATE only: real broker margin can carry account-level
    risk-based add-ons this doesn't model, and this is never a substitute
    for the real Balances-export Option Requirement account_state.py
    already carries -- cross-check against that, don't trust this alone.

    Covered contracts carry no incremental margin (backed by owned shares)
    -- only a CALL's naked portion, or a PUT's full size (no cash-secured-
    put exemption assumed for a margin account), is priced here.
    """
    price = leg.get("current_price")
    strike = leg.get("strike")
    if not price or not strike or price <= 0 or strike <= 0:
        return None

    total_contracts = leg.get("total_contracts") or leg.get("contracts") or 1
    premium = leg.get("premium_received") or 0.0

    if _opt_type(leg) == "CALL":
        # Prefer the already-classified `coverage` enum over re-reading the
        # leg dict's own `covered_contracts` here -- that field is the same
        # pooled, cross-account-AND-combined annotation _classify_coverage()
        # above was just fixed to stop trusting (ADR 0005), and this
        # function previously re-introduced the identical bug independently:
        # a COVERED leg with stale covered_contracts=0 (from a same-contract
        # collision with a naked position in a different account) priced a
        # full naked margin estimate on a position that carries none. PARTIAL
        # has no better per-leg count available from coverage alone, so it
        # still falls back to the leg dict's count for that one case.
        if coverage == "COVERED":
            naked_contracts = 0
        elif coverage == "NAKED":
            naked_contracts = total_contracts
        else:
            naked_contracts = total_contracts - (leg.get("covered_contracts") or 0)
        if naked_contracts <= 0:
            return 0.0
        underlying_value = price * 100 * naked_contracts
        otm_amount = max(0.0, strike - price) * 100 * naked_contracts
        # Premium is reported as a total across all contracts on the leg;
        # only the naked portion's share offsets its own margin.
        premium_share = premium * naked_contracts / total_contracts if total_contracts else premium
        std = 0.20 * underlying_value - otm_amount + premium_share
        floor = 0.10 * underlying_value + premium_share
        return round(max(std, floor), 2)

    # PUT -- this engine only produces CASH_SECURED_PUT for puts; a margin
    # account still carries Reg-T naked-put margin against the full size.
    underlying_value = price * 100 * total_contracts
    strike_value = strike * 100 * total_contracts
    otm_amount = max(0.0, price - strike) * 100 * total_contracts
    std = 0.20 * underlying_value - otm_amount + premium
    floor = 0.10 * strike_value + premium
    return round(max(std, floor), 2)


def _assignment_impact(leg: dict, coverage: Coverage, itm: bool) -> tuple[float | None, str | None]:
    """What happens to cash/position if this leg is assigned today. Mirrors
    the math already used ad hoc this session (the 11/13 ANET assignment
    check) -- now a tested, reusable rule instead of a one-off script."""
    if not itm:
        return None, None

    strike = leg.get("strike")
    contracts = leg.get("total_contracts") or leg.get("contracts") or 1
    symbol = leg.get("symbol")
    notional = strike * 100 * contracts

    if _opt_type(leg) == "PUT":
        # Cash-secured put assigned -> buy shares at strike: cash required.
        return -notional, f"+{100 * contracts} {symbol} shares (put assigned)"

    if coverage == "COVERED":
        # Covered call assigned -> sell owned shares at strike: cash in, shares gone.
        return notional, f"-{100 * contracts} {symbol} shares (covered call assigned, shares delivered)"

    if coverage == "PARTIAL":
        covered_ct = leg.get("covered_contracts") or 0
        naked_ct = contracts - covered_ct
        # The covered portion's cash impact is known (strike x shares); the
        # naked portion must be bought at market to deliver, which depends
        # on a price not knowable from strike alone -- flagged, not guessed.
        covered_impact = notional * covered_ct / contracts if contracts else None
        return covered_impact, (
            f"-{100 * covered_ct} {symbol} shares delivered; "
            f"{naked_ct} contract(s) UNCOVERED -- must buy {100 * naked_ct} shares at market to deliver"
        )

    # NAKED call assigned -> cash received at strike, but a short-stock
    # position results; the resulting position matters as much as the cash.
    return notional, f"-{100 * contracts} {symbol} shares (uncovered short stock created, assigned naked)"


def _dividend_risk(leg: dict, itm: bool) -> tuple[bool, int | None]:
    """Early-exercise assignment risk on a short CALL (ADR 0001 step 5):
    when the dividend a holder would capture by exercising early exceeds
    the option's remaining extrinsic (time) value, exercising early is
    economically rational for the holder -- a real, documented risk this
    book had no gate for before this. Applies to NAKED, PARTIAL, and
    COVERED calls alike: the risk being flagged is an unplanned EARLY
    assignment (before the trader expected it), not whether assignment
    itself is harmful.

    dividend_rate is yfinance's trailing ANNUAL indicated rate; a single
    payment is approximated as rate/4 (most payers are quarterly) since the
    real next-payment amount isn't available without a dividend-history
    fetch this module doesn't make -- a labeled approximation, same
    discipline as the Reg-T margin estimate above, not treated as exact.
    """
    if _opt_type(leg) != "CALL" or not itm:
        return False, None
    ex_div = leg.get("next_ex_dividend_date")
    expiry = leg.get("expiry")
    dividend_rate = leg.get("dividend_rate") or 0.0
    if not ex_div or not expiry or dividend_rate <= 0:
        return False, None
    try:
        ex_div_date = _date.fromisoformat(str(ex_div)[:10])
        expiry_date = _date.fromisoformat(str(expiry)[:10])
    except (ValueError, TypeError):
        return False, None

    today = _date.today()
    if not (today <= ex_div_date <= expiry_date):
        return False, None  # ex-div already passed, or falls after this leg expires -- not this leg's risk

    contracts = leg.get("total_contracts") or leg.get("contracts") or 1
    strike = leg.get("strike") or 0.0
    price = leg.get("current_price") or 0.0
    cost_to_close = leg.get("cost_to_close") or 0.0
    intrinsic = max(0.0, price - strike) * 100 * contracts
    extrinsic = cost_to_close - intrinsic
    est_dividend_payment = (dividend_rate / 4) * 100 * contracts

    if est_dividend_payment > extrinsic:
        return True, (ex_div_date - today).days
    return False, None


def _time_axis(leg: dict, gates_fired: list[str], days_to_ex_div: int | None) -> tuple[bool, str | None, int | None]:
    dte = leg.get("dte")
    if "DIVIDEND_RISK" in gates_fired and days_to_ex_div is not None:
        return True, "EX_DIV", days_to_ex_div
    if "EARNINGS_RISK" in gates_fired:
        return True, "EARNINGS", dte
    if dte is not None and dte <= _EXPIRY_FORCING_DTE:
        return True, "EXPIRY", dte
    return False, None, dte


def build_decision(leg: dict) -> LegDecisionRecord:
    """Pure function: one leg dict in, one LegDecisionRecord out. No I/O, no
    live lookups -- everything needed must already be on the leg dict (see
    services.get_position_heat()'s _leg_summary()/_annotate())."""
    coverage = _classify_coverage(leg)
    itm = _is_itm(leg)
    cash_impact, resulting_position = _assignment_impact(leg, coverage, itm)

    dividend_risk, days_to_ex_div = _dividend_risk(leg, itm)
    gates_fired = list(leg.get("gates_fired") or [])
    if dividend_risk and "DIVIDEND_RISK" not in gates_fired:
        gates_fired.append("DIVIDEND_RISK")

    time_bound, forcing_event, days_to_forcing = _time_axis(leg, gates_fired, days_to_ex_div)
    margin = _reg_t_margin(leg, coverage)
    margin_source: Literal["REG_T_ESTIMATE", "UNAVAILABLE"] = "REG_T_ESTIMATE" if margin is not None else "UNAVAILABLE"

    contracts = leg.get("total_contracts") or leg.get("contracts") or 1
    option_delta = _black_scholes_delta(
        _opt_type(leg), leg.get("current_price"), leg.get("strike"), leg.get("dte"), leg.get("current_iv_pct")
    )
    delta_shares = -option_delta * 100 * contracts if option_delta is not None else None
    delta_source: Literal["BLACK_SCHOLES_ESTIMATE", "UNAVAILABLE"] = (
        "BLACK_SCHOLES_ESTIMATE" if option_delta is not None else "UNAVAILABLE"
    )

    severity = leg.get("action", "UNKNOWN")
    # Phase 1: reuse heat_scanner.py's own verdict verbatim (parity, not a
    # new ruleset) -- its "reason" field already states the action in plain
    # language. Replaced by a real rule table in ADR 0001 steps 4-5 once
    # margin/dividend-aware rules exist that heat_scanner.py has no concept of.
    recommended_action = leg.get("reason") or severity
    rule_citation = f"heat_scanner.py::_set_action() action={severity}"

    return LegDecisionRecord(
        symbol=leg.get("symbol"),
        account=leg.get("account"),
        option_type=_opt_type(leg),
        strike=leg.get("strike"),
        expiry=leg.get("expiry"),
        dte=leg.get("dte"),
        contracts=contracts,
        coverage=coverage,
        premium_received=leg.get("premium_received") or 0.0,
        cost_to_close=leg.get("cost_to_close"),
        loss_multiple=leg.get("loss_multiple"),
        pnl_pct=leg.get("pnl_pct"),
        current_price=leg.get("current_price"),
        distance_pct=leg.get("distance_pct"),
        est_margin_requirement=margin,
        margin_source=margin_source,
        itm=itm,
        assignment_cash_impact=cash_impact,
        assignment_resulting_position=resulting_position,
        time_bound=time_bound,
        forcing_event=forcing_event,
        days_to_forcing_event=days_to_forcing,
        severity=severity,
        sector=leg.get("sector"),
        delta_shares=delta_shares,
        delta_source=delta_source,
        gates_fired=gates_fired,
        recommended_action=recommended_action,
        rule_citation=rule_citation,
    )


def build_decisions(legs: list[dict]) -> list[LegDecisionRecord]:
    """Every leg -> one LegDecisionRecord, same order as given. No
    filtering: completeness is the point (see module docstring) -- a
    caller that wants only actionable legs filters the result, not this
    function."""
    return [build_decision(lg) for lg in legs]


# ---------------------------------------------------------------------------
# Portfolio-level rollup (ADR 0001 step 7)
# ---------------------------------------------------------------------------

# Cited directly from the ADR's own established-practice research (a ~5%
# single-name concentration cap is standard for an equity portfolio);
# applied here against MARGIN usage, not equity value, since margin is the
# actual constrained resource in a margin account. A default worth revisiting
# once trading_policy.yaml consolidates thresholds -- not fixed policy.
SINGLE_NAME_MARGIN_CONCENTRATION_CAP_PCT = 15.0
SECTOR_MARGIN_CONCENTRATION_CAP_PCT = 30.0


def portfolio_rollup(decisions: list[LegDecisionRecord]) -> dict:
    """Aggregates build_decisions() output by sector and symbol: total Reg-T
    margin estimate, total portfolio delta (share-equivalents, signed), and
    concentration gates when one symbol or sector accounts for an outsized
    share of total margin in use. Takes the ALREADY-BUILT decisions list
    (from build_decisions()), not raw legs -- a caller that has both legs and
    decisions (e.g. get_leg_decisions()) would otherwise pay for coverage
    classification, Reg-T margin, dividend-gate date parsing, and the
    Black-Scholes delta a second time for every leg on every call, for no
    reason (found in review, 2026-11-05). A caller with only legs can still
    get a rollup via `portfolio_rollup(build_decisions(legs))`.
    """
    total_margin = sum(d.est_margin_requirement or 0.0 for d in decisions)
    total_delta_shares = sum(d.delta_shares or 0.0 for d in decisions)

    by_sector: dict[str, dict] = {}
    by_symbol: dict[str, dict] = {}
    for d in decisions:
        sector = d.sector or "Unknown"
        s = by_sector.setdefault(sector, {"margin": 0.0, "delta_shares": 0.0, "leg_count": 0})
        s["margin"] += d.est_margin_requirement or 0.0
        s["delta_shares"] += d.delta_shares or 0.0
        s["leg_count"] += 1

        sym = by_symbol.setdefault(d.symbol, {"margin": 0.0, "delta_shares": 0.0, "leg_count": 0})
        sym["margin"] += d.est_margin_requirement or 0.0
        sym["delta_shares"] += d.delta_shares or 0.0
        sym["leg_count"] += 1

    concentration_gates = []
    for name, bucket in by_symbol.items():
        pct = round(bucket["margin"] / total_margin * 100, 1) if total_margin else 0.0
        bucket["margin_pct_of_total"] = pct
        if pct > SINGLE_NAME_MARGIN_CONCENTRATION_CAP_PCT:
            concentration_gates.append({
                "level": "SYMBOL", "name": name, "margin_pct_of_total": pct,
                "cap_pct": SINGLE_NAME_MARGIN_CONCENTRATION_CAP_PCT,
            })

    for sector, bucket in by_sector.items():
        pct = round(bucket["margin"] / total_margin * 100, 1) if total_margin else 0.0
        bucket["margin_pct_of_total"] = pct
        if pct > SECTOR_MARGIN_CONCENTRATION_CAP_PCT:
            concentration_gates.append({
                "level": "SECTOR", "name": sector, "margin_pct_of_total": pct,
                "cap_pct": SECTOR_MARGIN_CONCENTRATION_CAP_PCT,
            })

    return {
        "total_margin_estimate": round(total_margin, 2),
        "total_delta_shares_estimate": round(total_delta_shares, 2),
        "by_sector": {k: {**v, "margin": round(v["margin"], 2), "delta_shares": round(v["delta_shares"], 2)}
                      for k, v in by_sector.items()},
        "by_symbol": {k: {**v, "margin": round(v["margin"], 2), "delta_shares": round(v["delta_shares"], 2)}
                      for k, v in by_symbol.items()},
        "concentration_gates": concentration_gates,
    }


# ---------------------------------------------------------------------------
# Position sizing / risk budget (ADR 0001 step 8)
# ---------------------------------------------------------------------------

# A flat 1-3%-of-buying-power risk budget per new trade is the cited
# established-practice range (ADR 0001 context); 2% is the midpoint, a
# judgment call pending trading_policy.yaml, not a derived constant.
DEFAULT_RISK_PCT_PER_TRADE = 2.0


def recommended_contract_size(buying_power: float | None, est_margin_per_contract: float | None,
                               risk_pct_per_trade: float = DEFAULT_RISK_PCT_PER_TRADE,
                               max_contracts_cap: int | None = None) -> dict:
    """Flat-%-of-buying-power position sizing -- replaces
    trading_persona.md's static "max 5 contracts Tier 1 / 3 Tier 2 / 1 Tier
    3" rule (a fixed historical number) with one that scales to the
    account's ACTUAL current buying power, re-evaluated every time it's
    called rather than hardcoded. `est_margin_per_contract` should come from
    _reg_t_margin() (or the real thing, once available) for the specific
    strike/strategy being sized -- this function does no margin estimation
    of its own, it only turns a margin-per-contract figure into a contract
    count against a risk budget. `max_contracts_cap`, if given (e.g. a
    tier-based cap that still has real value as a diversification limit,
    not a capital-sizing one) is applied as an upper bound on top of the
    budget-derived count, never a substitute for it.
    """
    if not buying_power or buying_power <= 0 or not est_margin_per_contract or est_margin_per_contract <= 0:
        return {
            "contracts": 0,
            "reason": "insufficient data: buying_power or est_margin_per_contract missing/zero",
        }
    risk_budget = buying_power * (risk_pct_per_trade / 100.0)
    contracts = int(risk_budget // est_margin_per_contract)
    capped = max_contracts_cap is not None and contracts > max_contracts_cap
    if capped:
        contracts = max_contracts_cap
    return {
        "contracts": max(0, contracts),
        "risk_budget": round(risk_budget, 2),
        "risk_pct_per_trade": risk_pct_per_trade,
        "est_margin_per_contract": round(est_margin_per_contract, 2),
        "buying_power": buying_power,
        "capped_by_max_contracts": capped,
    }
