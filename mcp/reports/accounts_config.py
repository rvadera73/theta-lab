"""
Shared account configuration — balances, monthly/annual premium targets, and
the $1.2M/year objective's framework constants.

Extracted out of unified_master_report_production.py so that both the master
report AND scripts/realized_pnl.py (the corrected FIFO-based P&L engine) can
import this config without creating a circular import between the two
(realized_pnl.py needs these targets; unified_master_report_production.py
needs realized_pnl.py's numbers) — this module has no dependency on either.
"""

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION — ALL ACCOUNTS WITH BALANCES & MONTHLY TARGETS
# Balances refreshed 2026-07-31 from that month's exports where a cash/MM
# line is present in the file (Fidelity, Vanguard). Schwab exports here are
# POSITIONS ONLY (no cash/margin balance line), so summing them ~doubles the
# true net-liq for margin/short-option-heavy books — Account A/B/C and both
# Robinhood balances are left at their last manually-confirmed figures and
# are NOT independently verified by this month's data. Re-confirm from each
# broker's account-summary screen (not the positions export) if updating.
#
# monthly_target = round(weighting_basis / total_weighting_basis * $100K) —
# the $100K/month base pool (BULL-regime baseline; the report engine applies
# REGIME_ADJUSTMENTS on top of this at read time) is split across the 9
# OPTIONS-TRADING accounts only. The Fidelity 401K and the wound-down Minor
# Roth are passive/empty (per persona: "passive accounts... excluded from
# these caps") and get weighting_basis=0, never billed against the target.
#
# Account A is the ONLY margin-enabled account. Confirmed by the trader
# (2026-08) that its real, lockable margin buying power is $700,000 — not
# its $403,000 cash/net-liq balance. `capacity` overrides `balance` as the
# weighting basis for exactly this reason: every other account's target
# shifts down slightly as a result, since it's one shared $100K pool.
# `balance` itself stays at the true $403,000 net-liq figure for display
# and margin-utilization purposes — only the TARGET weighting uses capacity.
#
# monthly_target is now COMPUTED below, not hand-maintained. Previously this
# was a hardcoded literal per account (e.g. Account A: 28615) that a second,
# independently-maintained dict (the old ACCOUNT_TARGETS, removed) also
# tried to express as gross/net figures -- confirmed live 2026-08-25 that
# the two had drifted to different numbers ($17,211 dynamic vs $18,600 from
# that static dict) for the same account in the same report. Every consumer
# of ACCOUNTS_CONFIG[...]['monthly_target'] (this report engine AND
# scripts/realized_pnl.py, which reads it directly) now gets the same
# single computed number automatically -- no call site needed to change.
# ═══════════════════════════════════════════════════════════════════
ACCOUNTS_CONFIG = {
    'Account A (232)': {'balance': 403000, 'margin': True, 'capacity': 700000},
    'Account B (275)': {'balance': 261000, 'margin': False},
    'Account C (634)': {'balance': 266000, 'margin': False},
    'Fidelity (Rahul)': {'balance': 498560, 'margin': False},
    'Fidelity (Rajul — Roth IRA)': {'balance': 39158, 'margin': False},
    'Fidelity (Rajul — Rollover IRA)': {'balance': 128081, 'margin': False},
    'Vanguard (Rahul)': {'balance': 320492, 'margin': False},
    'Robinhood (Individual)': {'balance': 13000, 'margin': False},
    'Robinhood (Traditional IRA)': {'balance': 220000, 'margin': False},
    'Fidelity 401K (Rahul)': {'balance': 192200, 'margin': False, 'weighting_basis': 0},
    # The 5th Fidelity account (custodial "ROTH IRA for Minor", 258240575) —
    # previously untracked entirely (see scripts/update_snapshot.py's
    # _FIDELITY_ACCOUNT_LABELS). Confirmed real, had genuine 2026 option
    # activity, wound down / transferred out ~March-May 2026, now ~$3 cash —
    # weighting_basis=0 like the 401K since there's no capital left to trade,
    # not because it can't do options.
    'Fidelity (Rahul — Roth IRA Minor)': {'balance': 3, 'margin': False, 'weighting_basis': 0},
}

TOTAL_PORTFOLIO_BALANCE = sum(acc['balance'] for acc in ACCOUNTS_CONFIG.values())

# ═══════════════════════════════════════════════════════════════════
# PRODUCTION FRAMEWORK — 60% CLOSE COST RATIO TARGETS
# ═══════════════════════════════════════════════════════════════════
CLOSE_COST_RATIO = 0.60
MONTHLY_TARGET_NET_BASE = 100000
MONTHLY_TARGET_GROSS_BASE = int(MONTHLY_TARGET_NET_BASE / (1 - CLOSE_COST_RATIO))  # $250K gross

# Keyed to the exact 4 strings analysis/regime.py's Regime enum actually
# emits (confirmed via mcp/config.py) -- this dict previously had 'SIDEWAYS'
# and 'BEAR' instead of the real 'TRANSITIONING'/'BEAR_SIDEWAYS', so
# REGIME_ADJUSTMENTS.get(regime, 0.85) silently fell through to the 0.85
# default for both. Coincidentally harmless for TRANSITIONING (0.85 either
# way) but silently overstated every target by ~21% for BEAR_SIDEWAYS
# (should be 0.70) -- dormant only because the live regime has been BULL
# throughout this session. Default changed to 0.70 (the most conservative
# real value) rather than a number that was never actually correct for
# anything, so an unrecognized future regime string fails safe/low instead
# of failing high.
REGIME_ADJUSTMENTS = {
    'BULL': 1.00,
    'CAUTIOUS_BULL': 0.90,
    'TRANSITIONING': 0.85,
    'BEAR_SIDEWAYS': 0.70,
}

# weighting_basis: explicit override (0 for passive accounts) > capacity
# (Account A's real margin buying power) > balance (everyone else).
_TOTAL_WEIGHTING_BASIS = sum(
    acc.get('weighting_basis', acc.get('capacity', acc['balance']))
    for acc in ACCOUNTS_CONFIG.values()
)
for _acc in ACCOUNTS_CONFIG.values():
    _basis = _acc.get('weighting_basis', _acc.get('capacity', _acc['balance']))
    _acc['monthly_target'] = round(MONTHLY_TARGET_NET_BASE * _basis / _TOTAL_WEIGHTING_BASIS) if _TOTAL_WEIGHTING_BASIS else 0
del _acc, _basis

# ACCOUNT_TARGETS (a second, independently-hand-maintained gross/net dict)
# removed 2026-08-25 -- confirmed it had drifted from the computed
# monthly_target above (e.g. Account A: $18,600 net here vs $17,211 from
# the dynamic calc, same report, same day). Gross is always derivable from
# net via CLOSE_COST_RATIO, so there is no longer a second number to drift.
