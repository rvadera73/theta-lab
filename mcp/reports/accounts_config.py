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
# monthly_target = round(weighted_basis / total_weighted_basis * 100,000) —
# the $100K/month base pool is split across the 9 OPTIONS-TRADING accounts
# only. The Fidelity 401K is a passive, options-free account (per persona:
# "passive accounts... excluded from these caps") and gets monthly_target=0,
# never billed against the premium-income target.
#
# Account A is the ONLY margin-enabled account. Confirmed by the trader
# (2026-08) that its real, lockable margin buying power is $700,000 — not
# its $403,000 cash/net-liq balance. monthly_target below is weighted
# against that $700K capacity (not the $403K balance) so the target
# reflects what the account can actually support; every other account's
# target shifted down slightly as a result, since it's one shared pool.
# `balance` itself is left at the true $403,000 net-liq figure — do not
# use it as the target-weighting basis for Account A, only monthly_target
# already reflects the $700K adjustment.
# ═══════════════════════════════════════════════════════════════════
ACCOUNTS_CONFIG = {
    'Account A (232)': {'balance': 403000, 'margin': True, 'monthly_target': 28615},  # weighted on $700K margin capacity, not the $403K balance shown here
    'Account B (275)': {'balance': 261000, 'margin': False, 'monthly_target': 10669},
    'Account C (634)': {'balance': 266000, 'margin': False, 'monthly_target': 10874},
    'Fidelity (Rahul)': {'balance': 498560, 'margin': False, 'monthly_target': 20380},
    'Fidelity (Rajul — Roth IRA)': {'balance': 39158, 'margin': False, 'monthly_target': 1601},
    'Fidelity (Rajul — Rollover IRA)': {'balance': 128081, 'margin': False, 'monthly_target': 5236},
    'Vanguard (Rahul)': {'balance': 320492, 'margin': False, 'monthly_target': 13101},
    'Robinhood (Individual)': {'balance': 13000, 'margin': False, 'monthly_target': 531},
    'Robinhood (Traditional IRA)': {'balance': 220000, 'margin': False, 'monthly_target': 8993},
    'Fidelity 401K (Rahul)': {'balance': 192200, 'margin': False, 'monthly_target': 0},
    # The 5th Fidelity account (custodial "ROTH IRA for Minor", 258240575) —
    # previously untracked entirely (see scripts/update_snapshot.py's
    # _FIDELITY_ACCOUNT_LABELS). Confirmed real, had genuine 2026 option
    # activity, wound down / transferred out ~March-May 2026, now ~$3 cash —
    # monthly_target=0 like the 401K since there's no capital left to trade,
    # not because it can't do options.
    'Fidelity (Rahul — Roth IRA Minor)': {'balance': 3, 'margin': False, 'monthly_target': 0},
}

TOTAL_PORTFOLIO_BALANCE = sum(acc['balance'] for acc in ACCOUNTS_CONFIG.values())

# ═══════════════════════════════════════════════════════════════════
# PRODUCTION FRAMEWORK — 60% CLOSE COST RATIO TARGETS
# ═══════════════════════════════════════════════════════════════════
CLOSE_COST_RATIO = 0.60
MONTHLY_TARGET_NET_BASE = 100000
MONTHLY_TARGET_GROSS_BASE = int(MONTHLY_TARGET_NET_BASE / (1 - CLOSE_COST_RATIO))  # $250K gross

REGIME_ADJUSTMENTS = {
    'BULL': 1.00,
    'CAUTIOUS_BULL': 0.90,
    'SIDEWAYS': 0.85,
    'BEAR': 0.70,
}

ACCOUNT_TARGETS = {
    'Account A (232)': {'gross': 46500, 'net': 18600},
    'Account B (275)': {'gross': 30250, 'net': 12100},
    'Account C (634)': {'gross': 30750, 'net': 12300},
    'Fidelity (Rahul)': {'gross': 57750, 'net': 23100},
    'Fidelity (Rajul — Roth IRA)': {'gross': 5750, 'net': 2300},
    'Fidelity (Rajul — Rollover IRA)': {'gross': 15000, 'net': 6000},
    'Vanguard (Rahul)': {'gross': 37250, 'net': 14900},
    'Robinhood (Individual)': {'gross': 1500, 'net': 600},
    'Robinhood (Traditional IRA)': {'gross': 25500, 'net': 10200},
}
