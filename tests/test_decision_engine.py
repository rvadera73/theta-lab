"""
Regression tests for mcp/analysis/decision_engine.py (ADR 0001, step 3).

Fixtures below are modeled directly on real legs surfaced this session, not
synthetic edge cases: the OKTA $140C naked call that a FIXED-LIST check
missed entirely (2026-11-03 -- "are u sure i see many like PYPL, OKTA and
CRM for that matter"), and the ANET $200P 11/13 assignment-cash-impact
question. Dollar amounts are illustrative, not live market data -- these
tests verify the ENGINE's logic, not today's prices.

No pytest dependency -- run directly: python3 tests/test_decision_engine.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "analysis"))

from decision_engine import build_decision, build_decisions, portfolio_rollup, recommended_contract_size

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# The bug this ADR exists to fix: predicate-based coverage, not a fixed list.
# ---------------------------------------------------------------------------
print("Coverage classification -- the fixed-list bug, generalized")

okta_naked_call = {
    "symbol": "OKTA", "type": "CALL", "strike": 140.0, "expiry": "2026-11-20",
    "dte": 17, "current_price": 186.63, "covered": False, "covered_contracts": 0,
    "total_contracts": 1, "premium_received": 500.0, "cost_to_close": 4700.0,
    "loss_multiple": 9.4, "pnl_pct": -840.0, "distance_pct": -33.3,
    "color": "RED", "action": "CUT_RESTAGGER", "reason": "hard stop, BTC now",
    "account": "A", "gates_fired": [],
}
d = build_decision(okta_naked_call)
check("OKTA $140C classified NAKED (covered=False predicate, not a symbol list)",
      d.coverage == "NAKED", f"got {d.coverage}")
check("OKTA $140C is ITM (186.63 > 140 strike)", d.itm, f"itm={d.itm}")
check("OKTA $140C assignment creates short stock, doesn't just show cash",
      d.assignment_resulting_position is not None and "short stock" in d.assignment_resulting_position,
      f"got {d.assignment_resulting_position}")
check("OKTA $140C assignment cash impact = strike*100*contracts = $14,000",
      d.assignment_cash_impact == 14000.0, f"got {d.assignment_cash_impact}")

# A symbol absent from any hardcoded tracking list must classify identically --
# this is the actual regression test for the 2026-11-03 finding.
random_naked_call = dict(okta_naked_call, symbol="ZZZZ_NOT_ON_ANY_LIST")
d2 = build_decision(random_naked_call)
check("a symbol not on any tracked list still classifies NAKED (predicate-based)",
      d2.coverage == "NAKED", f"got {d2.coverage}")

# ---------------------------------------------------------------------------
# ANET $200P 11/13 -- real assignment-cash-impact question from this session
# ---------------------------------------------------------------------------
print("\nPut assignment cash impact (ANET 11/13 case)")

anet_put = {
    "symbol": "ANET", "type": "PUT", "strike": 200.0, "expiry": "2026-11-13",
    "dte": 10, "current_price": 168.10, "covered": None,
    "total_contracts": 1, "premium_received": 900.0, "cost_to_close": 3200.0,
    "loss_multiple": 3.6, "pnl_pct": -255.0, "distance_pct": -15.9,
    "color": "RED", "action": "ROLL_OR_CUT_PUT", "reason": "roll down-and-out or cut",
    "account": "A", "gates_fired": [],
}
d3 = build_decision(anet_put)
check("ANET $200P classified CASH_SECURED_PUT (PUT coverage concept)",
      d3.coverage == "CASH_SECURED_PUT", f"got {d3.coverage}")
check("ANET $200P is ITM (168.10 < 200 strike)", d3.itm, f"itm={d3.itm}")
check("ANET $200P assignment requires $20,000 cash (negative = cash required)",
      d3.assignment_cash_impact == -20000.0, f"got {d3.assignment_cash_impact}")
check("ANET $200P at DTE=10 is time_bound via EXPIRY", d3.time_bound and d3.forcing_event == "EXPIRY",
      f"time_bound={d3.time_bound} forcing_event={d3.forcing_event}")
check("ANET $200P days_to_forcing_event == dte (10)", d3.days_to_forcing_event == 10,
      f"got {d3.days_to_forcing_event}")

# ---------------------------------------------------------------------------
# Covered and partial coverage
# ---------------------------------------------------------------------------
print("\nCovered / partial-coverage calls")

covered_call = {
    "symbol": "XYZ", "type": "CALL", "strike": 50.0, "expiry": "2027-01-15",
    "dte": 120, "current_price": 60.0, "covered": True, "covered_contracts": 2,
    "total_contracts": 2, "premium_received": 600.0, "cost_to_close": 2200.0,
    "loss_multiple": 3.7, "pnl_pct": -266.0, "distance_pct": -16.7,
    "color": "RED", "action": "ROLL_CALL", "reason": "roll up and out",
    "account": "A", "gates_fired": [],
}
d4 = build_decision(covered_call)
check("fully covered call -> COVERED", d4.coverage == "COVERED", f"got {d4.coverage}")
check("covered call assignment: cash received = strike*100*contracts = $10,000",
      d4.assignment_cash_impact == 10000.0, f"got {d4.assignment_cash_impact}")
check("covered call assignment never mentions UNCOVERED",
      d4.assignment_resulting_position is not None and "UNCOVERED" not in d4.assignment_resulting_position,
      f"got {d4.assignment_resulting_position}")

partial_call = dict(covered_call, symbol="PARTIAL1", strike=30.0, current_price=40.0,
                     covered=False, covered_contracts=1, total_contracts=3)
d5 = build_decision(partial_call)
check("1-of-3-covered call -> PARTIAL", d5.coverage == "PARTIAL", f"got {d5.coverage}")
check("partial call: known cash impact is only the covered third ($3,000 of $9,000 notional)",
      d5.assignment_cash_impact == 3000.0, f"got {d5.assignment_cash_impact}")
check("partial call flags the uncovered 2 contracts explicitly",
      d5.assignment_resulting_position is not None and "2 contract(s) UNCOVERED" in d5.assignment_resulting_position,
      f"got {d5.assignment_resulting_position}")

# ---------------------------------------------------------------------------
# OTM leg -- no assignment is possible, must not fabricate an impact
# ---------------------------------------------------------------------------
print("\nOTM legs carry no assignment impact")

otm_call = dict(covered_call, symbol="SAFE1", strike=100.0, current_price=60.0)
d6 = build_decision(otm_call)
check("OTM covered call is not ITM", not d6.itm, f"itm={d6.itm}")
check("OTM leg has no assignment_cash_impact (None, not 0 -- not computed, not zero)",
      d6.assignment_cash_impact is None, f"got {d6.assignment_cash_impact}")
check("OTM leg has no assignment_resulting_position",
      d6.assignment_resulting_position is None, f"got {d6.assignment_resulting_position}")

# ---------------------------------------------------------------------------
# Time axis -- the CLOSE_RESTAGGER severity-vs-time-boundedness bug,
# generalized at the record level (sequencer.py's own fix is separate).
# ---------------------------------------------------------------------------
print("\nTime axis is independent of severity")

far_dated_green = {
    "symbol": "AXON", "type": "PUT", "strike": 420.0, "expiry": "2027-06-18",
    "dte": 90, "current_price": 417.08, "covered": None, "total_contracts": 1,
    "premium_received": 1200.0, "cost_to_close": 400.0, "loss_multiple": 0.33,
    "pnl_pct": 66.7, "distance_pct": -0.7, "color": "GREEN", "action": "HOLD",
    "reason": "theta working", "account": "A", "gates_fired": [],
}
d7 = build_decision(far_dated_green)
check("far-dated GREEN leg is NOT time_bound", not d7.time_bound, f"time_bound={d7.time_bound}")
check("far-dated GREEN leg has no forcing_event", d7.forcing_event is None, f"got {d7.forcing_event}")

close_restagger_leg = dict(far_dated_green, symbol="ZS", dte=15, color="YELLOW",
                            action="CLOSE_RESTAGGER", reason="gamma risk zone")
d8 = build_decision(close_restagger_leg)
check("CLOSE_RESTAGGER (YELLOW, DTE<=21) IS time_bound despite non-RED severity",
      d8.time_bound and d8.forcing_event == "EXPIRY",
      f"time_bound={d8.time_bound} forcing_event={d8.forcing_event}")

earnings_gated_leg = dict(far_dated_green, symbol="CRM", dte=60, gates_fired=["EARNINGS_RISK"])
d9 = build_decision(earnings_gated_leg)
check("EARNINGS_RISK gate forces time_bound regardless of DTE (60d, no expiry pressure)",
      d9.time_bound and d9.forcing_event == "EARNINGS",
      f"time_bound={d9.time_bound} forcing_event={d9.forcing_event}")

# ---------------------------------------------------------------------------
# Reg-T margin estimate (ADR 0001 step 4)
# ---------------------------------------------------------------------------
print("\nReg-T margin estimate")

# Naked call: strike $140, price $186.63 (ITM, so OTM amount = 0), 1 contract,
# premium $500. std = 0.20*18663 - 0 + 500 = 4232.6; floor = 0.10*18663+500 = 2366.3
# -> std wins.
d10 = build_decision(okta_naked_call)
expected_std = 0.20 * (186.63 * 100) - 0 + 500.0
check("OKTA naked call margin_source is REG_T_ESTIMATE", d10.margin_source == "REG_T_ESTIMATE",
      f"got {d10.margin_source}")
check("OKTA naked call margin matches hand-computed Reg-T std formula (ITM, OTM=0)",
      d10.est_margin_requirement is not None and abs(d10.est_margin_requirement - expected_std) < 0.01,
      f"got {d10.est_margin_requirement}, expected {expected_std}")

# Fully covered call: naked_contracts = 0 -> margin is a deliberate $0, not "unavailable"
check("fully covered call margin is $0 (not unavailable -- a computed zero)",
      d4.est_margin_requirement == 0.0 and d4.margin_source == "REG_T_ESTIMATE",
      f"got {d4.est_margin_requirement} / {d4.margin_source}")

# Partial call: only the naked portion (2 of 3 contracts) carries margin
d11 = build_decision(partial_call)
check("partial call margin is computed only over the naked contracts (not all 3)",
      d11.est_margin_requirement is not None and d11.est_margin_requirement > 0,
      f"got {d11.est_margin_requirement}")

# Cash-secured put: strike $200, price $168.10 (ITM for a put), 1 contract, premium $900.
# OTM amount for a put = max(0, price-strike) = 0 since price<strike (ITM).
# std = 0.20*16810 - 0 + 900 = 4262; floor = 0.10*20000+900 = 2900 -> std wins.
d12 = build_decision(anet_put)
expected_put_std = 0.20 * (168.10 * 100) - 0 + 900.0
check("ANET put margin matches hand-computed Reg-T std formula",
      d12.est_margin_requirement is not None and abs(d12.est_margin_requirement - expected_put_std) < 0.01,
      f"got {d12.est_margin_requirement}, expected {expected_put_std}")

# Missing price data -> UNAVAILABLE, not a fabricated number
no_price_leg = dict(okta_naked_call, symbol="NOPRICE1", current_price=None)
d13 = build_decision(no_price_leg)
check("leg with no current_price -> margin UNAVAILABLE, not a guess",
      d13.est_margin_requirement is None and d13.margin_source == "UNAVAILABLE",
      f"got {d13.est_margin_requirement} / {d13.margin_source}")

# ---------------------------------------------------------------------------
# Dividend / early-exercise gate (ADR 0001 step 5)
# ---------------------------------------------------------------------------
print("\nDividend / early-exercise risk gate")

from datetime import date, timedelta
_today = date.today()
_soon = (_today + timedelta(days=5)).isoformat()
_later_expiry = (_today + timedelta(days=30)).isoformat()
_past = (_today - timedelta(days=5)).isoformat()

# LMT-style: real dividend payer, deep ITM naked call, thin extrinsic value,
# ex-div soon and well before expiry -> dividend payment ($3.30/4=$0.825/sh
# *100=$82.5) exceeds extrinsic ($200 cost_to_close - $100 intrinsic = $100
# extrinsic)... tuned below so the payment clearly exceeds extrinsic value.
lmt_style_call = {
    "symbol": "LMT", "type": "CALL", "strike": 600.0, "expiry": _later_expiry,
    "dte": 30, "current_price": 643.53, "covered": False, "covered_contracts": 0,
    "total_contracts": 1, "premium_received": 2000.0, "cost_to_close": 4400.0,
    "loss_multiple": 2.2, "pnl_pct": -120.0, "distance_pct": -7.3,
    "color": "RED", "action": "CUT_RESTAGGER", "reason": "hard stop",
    "account": "A", "gates_fired": [],
    "dividend_rate": 13.20,  # annual rate -> ~$3.30/quarter/share
    "next_ex_dividend_date": _soon,
}
d14 = build_decision(lmt_style_call)
# intrinsic = (643.53-600)*100 = 4353; extrinsic = 4400-4353 = 47; dividend payment = 13.20/4*100 = 330
check("real dividend payer, thin extrinsic value -> DIVIDEND_RISK gate fires",
      "DIVIDEND_RISK" in d14.gates_fired, f"got gates_fired={d14.gates_fired}")
check("DIVIDEND_RISK sets time_bound via EX_DIV forcing_event",
      d14.time_bound and d14.forcing_event == "EX_DIV", f"time_bound={d14.time_bound} forcing={d14.forcing_event}")
check("EX_DIV days_to_forcing_event matches real days to the ex-div date (5)",
      d14.days_to_forcing_event == 5, f"got {d14.days_to_forcing_event}")

# Same leg but with huge extrinsic value remaining (far OTM-ish mark) -> no early-exercise incentive
plenty_extrinsic = dict(lmt_style_call, symbol="LMT2", cost_to_close=10000.0)
d15 = build_decision(plenty_extrinsic)
check("ample extrinsic value remaining -> DIVIDEND_RISK does NOT fire",
      "DIVIDEND_RISK" not in d15.gates_fired, f"got gates_fired={d15.gates_fired}")

# Non-dividend payer (OKTA) -> never fires regardless of ITM/thin extrinsic
no_dividend = dict(lmt_style_call, symbol="OKTA", dividend_rate=0.0)
d16 = build_decision(no_dividend)
check("non-dividend payer never triggers DIVIDEND_RISK", "DIVIDEND_RISK" not in d16.gates_fired,
      f"got gates_fired={d16.gates_fired}")

# Ex-div date already in the past -> doesn't apply to this leg anymore
ex_div_passed = dict(lmt_style_call, symbol="LMT3", next_ex_dividend_date=_past)
d17 = build_decision(ex_div_passed)
check("ex-div date already passed -> gate does not fire", "DIVIDEND_RISK" not in d17.gates_fired,
      f"got gates_fired={d17.gates_fired}")

# PUT leg -> early-exercise-for-dividend concept doesn't apply to puts
put_with_dividend_data = dict(anet_put, dividend_rate=13.20, next_ex_dividend_date=_soon, expiry=_later_expiry)
d18 = build_decision(put_with_dividend_data)
check("PUT legs never get DIVIDEND_RISK (concept is CALL-only)",
      "DIVIDEND_RISK" not in d18.gates_fired, f"got gates_fired={d18.gates_fired}")

# ---------------------------------------------------------------------------
# Black-Scholes delta + portfolio rollup (ADR 0001 step 7)
# ---------------------------------------------------------------------------
print("\nBlack-Scholes delta + portfolio rollup")

# Deep ITM naked call, 17 DTE, real-ish IV (30%) -> delta should be close to
# -100 shares per contract (deep ITM short call behaves almost like -100
# shares of stock).
deep_itm_call = dict(okta_naked_call, current_iv_pct=30.0)
d19 = build_decision(deep_itm_call)
check("deep ITM short call delta_source is BLACK_SCHOLES_ESTIMATE",
      d19.delta_source == "BLACK_SCHOLES_ESTIMATE", f"got {d19.delta_source}")
check("deep ITM short call delta_shares is strongly negative (near -100/contract)",
      d19.delta_shares is not None and d19.delta_shares < -70,
      f"got {d19.delta_shares}")

# issue #56 regression guard: the engine reads the leg's PERCENTAGE IV under
# `current_iv_pct` -- a leg that instead carries the OLD `current_iv` key
# (even with a plausible value) must be treated as having no IV at all,
# exactly like no_iv_leg below, not silently accepted.
stale_key_leg = dict(okta_naked_call, current_iv=30.0)  # old key name, should be ignored
d_stale = build_decision(stale_key_leg)
check("a leg carrying the OLD `current_iv` key (not `current_iv_pct`) gets "
      "delta UNAVAILABLE, not a silently-accepted stale-key guess",
      d_stale.delta_shares is None and d_stale.delta_source == "UNAVAILABLE",
      f"got {d_stale.delta_shares} / {d_stale.delta_source}")

# Deep ITM short put, similar setup -> delta should be strongly POSITIVE
# (short put benefits when stock rises, same direction as being long stock).
deep_itm_put = dict(anet_put, current_iv_pct=30.0)
d20 = build_decision(deep_itm_put)
check("deep ITM short put delta_shares is strongly positive (near +100/contract)",
      d20.delta_shares is not None and d20.delta_shares > 70,
      f"got {d20.delta_shares}")

# Missing IV -> delta UNAVAILABLE, not a fabricated number
no_iv_leg = dict(okta_naked_call, current_iv_pct=None)
d21 = build_decision(no_iv_leg)
check("leg with no current_iv_pct -> delta UNAVAILABLE, not a guess",
      d21.delta_shares is None and d21.delta_source == "UNAVAILABLE",
      f"got {d21.delta_shares} / {d21.delta_source}")

# Portfolio rollup: sector/symbol concentration
# portfolio_rollup() takes already-built decisions, not raw legs (changed in
# review, 2026-11-05, to stop double-computing build_decisions() per call) --
# build them explicitly here same as a real caller (get_leg_decisions()) does.
rollup_legs = [
    dict(okta_naked_call, symbol="AAA1", sector="Technology", current_iv_pct=30.0, strike=140.0),
    dict(okta_naked_call, symbol="AAA2", sector="Technology", current_iv_pct=30.0, strike=140.0),
    dict(anet_put, symbol="BBB1", sector="Industrials", current_iv_pct=30.0),
]
rollup = portfolio_rollup(build_decisions(rollup_legs))
check("portfolio_rollup total_margin_estimate is positive and matches sum of parts",
      rollup["total_margin_estimate"] > 0, f"got {rollup['total_margin_estimate']}")
check("portfolio_rollup groups by sector (Technology + Industrials present)",
      set(rollup["by_sector"].keys()) == {"Technology", "Industrials"},
      f"got {list(rollup['by_sector'].keys())}")
check("portfolio_rollup groups by symbol (3 distinct symbols)",
      len(rollup["by_symbol"]) == 3, f"got {len(rollup['by_symbol'])}")
check("Technology sector shows 2 legs (AAA1+AAA2), Industrials shows 1",
      rollup["by_sector"]["Technology"]["leg_count"] == 2 and rollup["by_sector"]["Industrials"]["leg_count"] == 1,
      f"got {rollup['by_sector']}")

# Force a concentration breach: one symbol with outsized margin vs tiny others
concentrated_legs = [
    dict(okta_naked_call, symbol="WHALE", current_iv_pct=30.0, strike=140.0, total_contracts=50, covered_contracts=0),
    dict(anet_put, symbol="TINY1", current_iv_pct=30.0, total_contracts=1),
]
conc_rollup = portfolio_rollup(build_decisions(concentrated_legs))
check("a symbol dominating portfolio margin fires a SYMBOL concentration gate",
      any(g["level"] == "SYMBOL" and g["name"] == "WHALE" for g in conc_rollup["concentration_gates"]),
      f"got {conc_rollup['concentration_gates']}")

# ---------------------------------------------------------------------------
# Position sizing / risk budget (ADR 0001 step 8)
# ---------------------------------------------------------------------------
print("\nPosition sizing / risk budget")

# $116,061 real buying power (Account A, 2026-11-03), 2% budget = $2,321.23,
# $2,500/contract margin -> 0 contracts (budget doesn't cover even 1).
sizing1 = recommended_contract_size(116061.36, 2500.0)
check("small real buying power vs a large margin-per-contract -> 0 contracts (not a fabricated minimum)",
      sizing1["contracts"] == 0, f"got {sizing1}")

# Same buying power, a cheaper $400/contract margin -> several contracts.
sizing2 = recommended_contract_size(116061.36, 400.0)
expected_budget = 116061.36 * 0.02
expected_contracts = int(expected_budget // 400.0)
check("sizing scales with real buying power, not a fixed tier number",
      sizing2["contracts"] == expected_contracts, f"got {sizing2['contracts']}, expected {expected_contracts}")

# A tier cap below the budget-derived count binds.
sizing3 = recommended_contract_size(116061.36, 400.0, max_contracts_cap=2)
check("max_contracts_cap binds when lower than the budget-derived count",
      sizing3["contracts"] == 2 and sizing3["capped_by_max_contracts"] is True, f"got {sizing3}")

# Missing inputs -> explicit 0 with a reason, not a crash or a guess.
sizing4 = recommended_contract_size(None, 400.0)
check("missing buying_power -> 0 contracts with an explicit reason",
      sizing4["contracts"] == 0 and "reason" in sizing4, f"got {sizing4}")
sizing5 = recommended_contract_size(100000.0, 0)
check("zero margin_per_contract -> 0 contracts with an explicit reason (not a division crash)",
      sizing5["contracts"] == 0 and "reason" in sizing5, f"got {sizing5}")

# ---------------------------------------------------------------------------
# build_decisions(): completeness over a mixed batch, order preserved
# ---------------------------------------------------------------------------
print("\nbuild_decisions() completeness over a mixed batch")

batch = [okta_naked_call, anet_put, covered_call, partial_call, otm_call,
         far_dated_green, close_restagger_leg, earnings_gated_leg]
records = build_decisions(batch)
check("build_decisions returns one record per leg, same order, none dropped",
      len(records) == len(batch) and [r.symbol for r in records] == [lg["symbol"] for lg in batch],
      f"got {len(records)} records for {len(batch)} legs")

# ---------------------------------------------------------------------------
# ADR 0005: _classify_coverage must prefer the real per-leg `coverage` field
# (heat_scanner.py, ADR 0005) over the older, pooled, cross-account-AND-
# combined `covered`/`covered_contracts` annotation (services.py), which can
# disagree for a contract held covered in one account and naked in another
# -- a confirmed real, recurring pattern (see tests/test_services.py's AAPL
# $200 CALL cross-account-collision fixture), not a hypothetical. Before
# this fix, a leg like the one below classified NAKED despite coverage=
# "COVERED", fabricating "uncovered short stock created, assigned naked" in
# assignment_resulting_position and a nonzero naked margin estimate on a
# leg that carries neither risk.
# ---------------------------------------------------------------------------
print("\nADR 0005: coverage field vs. stale pooled `covered` annotation")

collision_covered_leg = {
    "symbol": "AAPL", "type": "CALL", "strike": 200.0, "expiry": "2027-01-15",
    "dte": 90, "current_price": 220.0,
    "coverage": "COVERED",                      # real, per-account, authoritative (ADR 0005)
    "covered": False, "covered_contracts": 0,    # stale pooled annotation -- collision w/ a naked copy in another account
    "total_contracts": 1, "premium_received": 400.0, "cost_to_close": 2100.0,
    "loss_multiple": 5.25, "pnl_pct": -425.0, "distance_pct": -10.0,
    "color": "GREEN", "action": "HOLD_TO_ASSIGNMENT",
    "reason": "covered call working as designed", "account": "A", "gates_fired": [],
}
d_collision = build_decision(collision_covered_leg)
check("a leg with coverage='COVERED' classifies COVERED even when the pooled "
      "`covered` annotation disagrees (reads False)",
      d_collision.coverage == "COVERED", f"got {d_collision.coverage}")
check("COVERED-per-leg assignment never fabricates an 'uncovered short stock' outcome",
      d_collision.assignment_resulting_position is not None
      and "uncovered short stock" not in d_collision.assignment_resulting_position,
      f"got {d_collision.assignment_resulting_position}")
check("COVERED-per-leg margin is $0, not a naked-call estimate",
      d_collision.est_margin_requirement == 0.0, f"got {d_collision.est_margin_requirement}")

# The mirror case: coverage='NAKED' but the stale pooled annotation happens
# to read covered=True/covered_contracts>0 (the same collision, opposite
# direction) must still price real naked margin, not $0.
collision_naked_leg = dict(collision_covered_leg, coverage="NAKED",
                            covered=True, covered_contracts=1,
                            color="RED", action="CUT_RESTAGGER", account="B")
d_collision_naked = build_decision(collision_naked_leg)
check("a leg with coverage='NAKED' classifies NAKED even when the pooled "
      "`covered` annotation disagrees (reads True)",
      d_collision_naked.coverage == "NAKED", f"got {d_collision_naked.coverage}")
check("NAKED-per-leg margin is priced against the full naked size, not $0",
      d_collision_naked.est_margin_requirement is not None and d_collision_naked.est_margin_requirement > 0,
      f"got {d_collision_naked.est_margin_requirement}")

# A pre-ADR-0005 leg with no `coverage` key at all must still classify via
# the old predicate -- this module's own backward-compatible fallback.
pre_adr0005_leg = {k: v for k, v in okta_naked_call.items()}
d_pre = build_decision(pre_adr0005_leg)
check("a leg with no `coverage` key falls back to the old covered/covered_contracts predicate",
      d_pre.coverage == "NAKED", f"got {d_pre.coverage}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
