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
# Account A is the ONLY margin-enabled account. The $700,000 figure below
# WAS the trader-confirmed (2026-08) real capacity, but that's now stale —
# superseded 2026-09-21 after a live walk-through of the account's actual
# Schwab "Margin Details" / "Available Funds" screen:
#   - Margin Equity: $1,000,000 | SMA (Reg-T initial-margin buying power): $1,600,000
#   - Cash + Borrowing available: $102,000 | Balance subject to interest: $0
#   - No margin/maintenance requirement violation showing, no call active.
# "Equity Percent" also read 29% that session -- confirmed NOT the binding
# constraint here: that ratio governs traditional debit-balance maintenance
# calls, and this account carries $0 debit balance (zero margin interest),
# so that mechanism doesn't apply. The real constraint for an options-heavy,
# no-stock-loan margin account is the options margin requirement itself
# (Opt Req, computed live from real positions) against SMA/equity headroom
# -- not a stock-margin equity ratio. Capacity set to $900,000 as the
# YELLOW-macro-regime working ceiling (SMA showed real room for more; this
# is deliberately short of maxing it out given the still-elevated 30-day
# crash probability at the time). Regime dial agreed with the trader
# 2026-09-21: RED -> $700-750K, YELLOW -> $900K-$1M (this value), GREEN ->
# $1.1-1.2M. Re-derive this figure directly from a fresh Schwab SMA/Equity
# read periodically -- it is not a fixed constant, it moves with the
# account's real market value the same way SMA does.
# `capacity` overrides `balance` as the weighting basis for exactly this
# reason: every other account's target shifts down slightly as a result,
# since it's one shared $100K pool. `balance` itself stays at the true
# $403,000 net-liq figure for display and margin-utilization purposes —
# only the TARGET weighting uses capacity.
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
# balance_as_of: None means genuinely unconfirmed (no date this figure was
# last verified against) -- confirmed via direct account-status
# investigation (2026-09-01) that Account B/C's "over cap"/"coverage gap"
# readings are NOT a calculation bug (their covered/naked call detection is
# correct) but ARE explained by these balances being stale -- Schwab's
# position export has no cash/NLV line at all, so there is currently no way
# to derive these live; they need a direct re-confirmation from the trader.
ACCOUNTS_CONFIG = {
    'Account A (232)': {'balance': 403000, 'margin': True, 'capacity': 900000, 'balance_as_of': None, 'capacity_as_of': '2026-09-21'},
    'Account B (275)': {'balance': 261000, 'margin': False, 'balance_as_of': None},
    'Account C (634)': {'balance': 256067, 'margin': False, 'balance_as_of': '2026-09-25'},  # real Schwab balance export -- Cash Secured Put Requirement $213,150 against $213,203 cash, only $52.94 actually free to trade
    # Fidelity balances derived from the position file's own money-market cash
    # line + its "% of account" column (Cash / pct = total account value) --
    # a real, live figure computable from every fresh export, not a manually
    # re-confirmed number that goes stale. Fixed 2026-09-25 after the trader
    # flagged reports still showing the 2026-07-31 balance_as_of date despite
    # regular fresh ingests -- this field just wasn't being recomputed from
    # data that was already sitting in the position files the whole time.
    'Fidelity (Rahul)': {'balance': 563432, 'margin': False, 'balance_as_of': '2026-09-25'},  # $522,516.06 cash / 92.73%
    'Fidelity (Rajul — Roth IRA)': {'balance': 44942, 'margin': False, 'balance_as_of': '2026-09-25'},  # $34,469.22 cash / 76.71%
    'Fidelity (Rajul — Rollover IRA)': {'balance': 141349, 'margin': False, 'balance_as_of': '2026-09-25'},  # $163,364.18 cash / 115.58% (>100% because this account's naked-put book carries negative net option value, pulling the account total below the cash line)
    'Vanguard (Rahul)': {'balance': 320492, 'margin': False, 'balance_as_of': '2026-07-31'},
    'Robinhood (Individual)': {'balance': 13000, 'margin': False, 'balance_as_of': None},
    'Robinhood (Traditional IRA)': {'balance': 220000, 'margin': False, 'balance_as_of': None},
    'Fidelity 401K (Rahul)': {'balance': 192200, 'margin': False, 'weighting_basis': 0, 'balance_as_of': '2026-07-31'},
    # The 5th Fidelity account (custodial "ROTH IRA for Minor", 258240575) —
    # previously untracked entirely (see scripts/update_snapshot.py's
    # _FIDELITY_ACCOUNT_LABELS). Confirmed real, had genuine 2026 option
    # activity, wound down / transferred out ~March-May 2026, now ~$3 cash —
    # weighting_basis=0 like the 401K since there's no capital left to trade,
    # not because it can't do options.
    'Fidelity (Rahul — Roth IRA Minor)': {'balance': 3, 'margin': False, 'weighting_basis': 0, 'balance_as_of': '2026-05-31'},
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
