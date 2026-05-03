"""
Theta-lab configuration — persona guardrails and account parameters.
All thresholds derived from trading_persona.md.
"""

from dataclasses import dataclass, field
from enum import Enum


class Regime(str, Enum):
    BEAR_SIDEWAYS = "BEAR_SIDEWAYS"
    TRANSITIONING = "TRANSITIONING"
    CAUTIOUS_BULL = "CAUTIOUS_BULL"   # Technical bull + elevated macro caution (VIX 16-20 or SPX stretched)
    BULL = "BULL"


class Tier(int, Enum):
    CORE = 1
    EMERGING = 2
    SPECULATIVE = 3


# ---------------------------------------------------------------------------
# Account definitions
# ---------------------------------------------------------------------------

ACCOUNT_A = {
    "label": "Rahul — Schwab One Margin",
    "type": "margin",
    "target_annual_return": 0.40,    # $100K/month combined across all accounts
    "target_weekly_pnl": 5769,       # $300K/yr ÷ 52 (Account A share of $100K/mo target)
    "max_contracts_by_tier": {1: 5, 2: 3, 3: 1},
    "margin_alert_pct": 0.80,
    "strategies": ["covered_call", "short_strangle"],
}

ACCOUNT_B = {
    "label": "Pinky — Schwab IRA",
    "type": "ira",
    "target_annual_return": 0.15,
    "target_weekly_pnl": 962,        # $50K/yr ÷ 52
    "max_contracts_by_tier": {1: 1, 2: 1, 3: 1},
    "no_margin": True,
    "no_naked_calls": True,
    "speculative_max_pct": 0.10,
    "strategies": ["cash_secured_put", "covered_call"],
}

ACCOUNT_C = {
    "label": "Designated Beneficiary — Schwab (account 8634)",
    "type": "designated_beneficiary",  # No naked calls; Level 1/2 options
    "target_annual_return": 0.12,
    "target_weekly_pnl": 500,          # ~$26K/yr ÷ 52 (smaller account)
    "max_contracts_by_tier": {1: 1, 2: 1, 3: 1},
    "no_margin": True,
    "no_naked_calls": True,
    "speculative_max_pct": 0.10,
    "token_path": "~/.tokens/schwab_token_c.json",
    "strategies": ["cash_secured_put", "covered_call"],
    # Universe includes value/recovery names not in A or B
    "extra_names": ["ATEN", "NIO", "CMG", "TWLO", "LYFT", "BABA", "ABNB", "ANET"],
}

ACCOUNT_D = {
    "label": "Robinhood IRA",
    "broker": "robinhood",
    "type": "ira",
    "target_annual_return": 0.15,
    "target_weekly_pnl": 500,          # adjust once account size is known
    "max_contracts_by_tier": {1: 1, 2: 1, 3: 1},
    "no_margin": True,
    "no_naked_calls": True,
    "speculative_max_pct": 0.10,
    "token_path": "~/.tokens/robinhood.pickle",
    "strategies": ["cash_secured_put", "covered_call"],
}

# ---------------------------------------------------------------------------
# Account registry — single source of truth for all brokers.
# To add a new account: add one entry here. No other code changes needed.
# ---------------------------------------------------------------------------
ACCOUNTS: dict[str, dict] = {
    "A":  {**ACCOUNT_A, "broker": "schwab",       "hash_env": "SCHWAB_ACCOUNT_A_HASH"},
    "B":  {**ACCOUNT_B, "broker": "schwab",       "hash_env": "SCHWAB_ACCOUNT_B_HASH"},
    "C":  {**ACCOUNT_C, "broker": "schwab",       "hash_env": "SCHWAB_ACCOUNT_C_HASH"},
    "D":  {**ACCOUNT_D, "broker": "robinhood_csv", "csv_path_env": "ROBINHOOD_INDIVIDUAL_CSV", "label": "Robinhood Individual"},
    # Robinhood Traditional IRA — CSV export (API does not support IRA; app MFA too disruptive)
    "E":  {**ACCOUNT_D, "broker": "robinhood_csv", "csv_path_env": "ROBINHOOD_IRA_CSV",        "label": "Robinhood Traditional IRA", "type": "ira"},
    # Fidelity CSV 1: two accounts in same file
    "F1": {"label": "Fidelity Traditional IRA",   "broker": "fidelity_csv",  "csv_path_env": "FIDELITY_CSV_1",          "fidelity_account_number": "225798148", "type": "ira",      "no_margin": True, "no_naked_calls": True},
    "F2": {"label": "Fidelity ROTH IRA (Minor)",  "broker": "fidelity_csv",  "csv_path_env": "FIDELITY_CSV_1",          "fidelity_account_number": "258240575", "type": "roth_ira", "no_margin": True, "no_naked_calls": True},
    # Fidelity CSV 2: two accounts in same file
    "G1": {"label": "Fidelity ROTH IRA",          "broker": "fidelity_csv",  "csv_path_env": "FIDELITY_CSV_2",          "fidelity_account_number": "233461172", "type": "roth_ira", "no_margin": True, "no_naked_calls": True},
    "G2": {"label": "Fidelity Rollover IRA",      "broker": "fidelity_csv",  "csv_path_env": "FIDELITY_CSV_2",          "fidelity_account_number": "263508923", "type": "ira",      "no_margin": True, "no_naked_calls": True},
    # To add a new account: one entry here, zero other file changes needed.
}

# ---------------------------------------------------------------------------
# Portfolio-level targets ($3M across all 14 accounts)
# ---------------------------------------------------------------------------

PORTFOLIO = {
    "total_aum": 3_000_000,
    "target_monthly_combined": 100_000,   # $100K/month = premium + equity appreciation
    "target_annual_return": 0.40,          # $1.2M/year = 40% of $3M
    "historical_annual_return": 0.30,      # 3-year average
    "active_options_aum_estimate": 1_500_000,  # Schwab A+B + RH IRA + Fidelity active
    # Assigned equity caps
    "assigned_equity_cap_bull": 0.15,      # 15% of active options AUM
    "assigned_equity_cap_sideways": 0.20,  # 20%
    "assigned_equity_cap_bear": 0.25,      # 25% = ~$375K at current AUM estimate
    "assigned_equity_danger_zone": 0.30,   # >30% = freeze new puts
    "per_name_cap_dollars": 100_000,       # $100K max per assigned name
    "per_name_cap_shares": 2_000,          # 2,000 shares max per name
    "deliberate_equity_cap": 0,            # $0 — never buy stock intentionally
}

# ---------------------------------------------------------------------------
# Profit-take targets by regime
# ---------------------------------------------------------------------------

PROFIT_TARGETS = {
    # Source: Account A 195 matched trades.
    # Median profit% at close = 44%, mean = 41% — NOT the 55-70% range previously set.
    # Strategy: sell long DTE, close at ~40-45% profit in ~35-37 days, redeploy immediately.
    # Bear/cautious: close faster (market volatile — lock in gains, redeploy when IV still high).
    Regime.BEAR_SIDEWAYS: (0.40, 0.50),   # close 40-50% — IV elevated, redeploy fast
    Regime.TRANSITIONING: (0.40, 0.50),
    Regime.CAUTIOUS_BULL: (0.40, 0.50),   # same — median 44% is the actual behavior
    Regime.BULL: (0.50, 0.60),            # bull has lower IV; hold slightly longer for more capture
}

# ---------------------------------------------------------------------------
# DTE targets by regime
# ---------------------------------------------------------------------------

DTE_TARGETS = {
    # Source: Account A 195 matched trades.
    # Sweet spot: 200-300 DTE = 100% win rate, $666 avg P&L/trade.
    # Avg HOLD = 35-37 days regardless — open long DTE for cushion, close at 50% profit quickly.
    # BEAR is NOT no-entry — Mar/Apr 2026 (bear) generated $100K via strangles at elevated IV.
    Regime.BEAR_SIDEWAYS: (180, 300),
    Regime.TRANSITIONING: (150, 280),
    Regime.CAUTIOUS_BULL: (180, 300),
    Regime.BULL: (90, 180),
}

# ---------------------------------------------------------------------------
# Regime detection thresholds
# ---------------------------------------------------------------------------

REGIME_SIGNALS = {
    "vix_bull_threshold": 20.0,          # VIX sustained below = bullish
    "vix_pause_threshold": 35.0,         # VIX above = pause all entries
    "put_call_ratio_bull": 0.80,
    "ma_days": [50, 200],
}

# ---------------------------------------------------------------------------
# Position heat management triggers
# ---------------------------------------------------------------------------
# Based on Account A behavior analysis (195 matched trades):
# - Calls are ROLLED (not cut) when stock FALLS (repriced cheap, harvest + re-sell lower)
# - Puts are CUT at loss when stock FALLS through strike; immediately re-opened at new level
# - "AI bull protocol": when market rallies, calls approach strikes — scale back new positions,
#   roll threatened calls first, harvest puts at 40%+ and recycle
#
# Traffic light system based on distance of stock price to strike:
HEAT_THRESHOLDS = {
    # SHORT CALL thresholds: stock rising toward call strike
    "call": {
        "green":  0.15,   # stock < 85% of strike  (>15% cushion) — theta working, hold
        "yellow": 0.08,   # stock 85-92% of strike (8-15% cushion) — prepare to roll or harvest
        "red":    0.08,   # stock > 92% of strike  (<8% cushion) — act now: roll or cut
    },
    # SHORT PUT thresholds: stock falling toward put strike
    "put": {
        "green":  0.15,   # stock > 115% of strike — hold
        "yellow": 0.08,   # stock 108-115% of strike — prepare
        "red":    0.08,   # stock < 108% of strike — act now
    },
    # P&L thresholds (cost-to-close as multiple of premium received)
    "loss_cut_multiplier":    2.0,   # BTC at 2x premium — hard stop
    "early_warning_multiple": 1.5,   # Flag at 1.5x — monitor closely
    # Profit take (from actual data: median close at 44%)
    "profit_target_pct":      0.40,  # Close at 40% of premium captured — fast recycle
    "profit_ideal_pct":       0.50,  # Ideal: 50% capture before redeployment
}

# Regime-specific action on heat:
# CAUTIOUS_BULL / AI bull rally: tighten call monitoring, scale back new strangles
HEAT_REGIME_ACTIONS = {
    "BULL":          {"call_tighten": False, "scale_back_strangles": False, "priority": "balanced"},
    "CAUTIOUS_BULL": {"call_tighten": True,  "scale_back_strangles": True,  "priority": "calls_first"},
    "TRANSITIONING": {"call_tighten": True,  "scale_back_strangles": True,  "priority": "calls_first"},
    "BEAR_SIDEWAYS": {"call_tighten": False, "scale_back_strangles": False, "priority": "puts_first"},
}

TRADING_RULES = {
    "stop_loss": "flag_and_ask",         # Never auto-close
    "flag_threshold_multiplier": 2.0,    # Flag when mark > 2x premium received
    "roll_dte_threshold": 21,            # Roll or close when DTE <= 21
    "iv_rank_min_new_entry": 40,         # IVR minimum for new entries
    "earnings_blackout_days": 7,
    "min_open_interest": 500,
    "max_bid_ask_spread_pct": 0.10,
}

# Backward-compat alias used by report_utils.py
RISK = TRADING_RULES

# ---------------------------------------------------------------------------
# Stock universe by tier
# ---------------------------------------------------------------------------

UNIVERSE = {
    Tier.CORE: [
        "AXON", "CRM", "ADBE", "CRWD", "TSM", "OKTA", "GEV",
        "NVDA", "META", "AMZN", "GOOGL", "MSFT",
    ],
    Tier.EMERGING: [
        "HOOD", "ALAB", "VST", "SHOP", "ZS", "RTX", "NTRA",
        "COIN", "ABNB", "EXPE", "UBER", "APP", "AXON",
    ],
    Tier.SPECULATIVE: [
        "ASTS", "RKLB", "ACHR", "OKLO", "IONQ", "QBTS",
        "RGTI", "QUBT", "EWZ", "EWY", "IBIT", "HUT", "CIFR", "RIOT",
    ],
}

PERMANENT_EXITS = ["MRNA", "PYPL", "SMCI", "INMD"]

# ---------------------------------------------------------------------------
# Legacy exit classification rules  — no hardcoded positions, these are
# screener parameters that run against live position data at runtime.
#
# Three exit categories detected dynamically:
#
#   BINARY_EXIT          Flags that make the thesis un-recoverable regardless of loss.
#                        Examples: SMCI (auditor resignation + DOJ), any going-concern.
#                        Action: exit at market same day, no rolling, no managing.
#
#   URGENT_RESTRUCTURE   Position trapped by options that make the exit worse than
#                        crystallising the loss now. Classic pattern: deep ITM covered
#                        calls below cost basis — you'll be forced to sell at a worse
#                        price than today. Action: BTC calls first, then sell stock.
#
#   SLOW_EXIT            Originally Tier 1, thesis eroded gradually (competitive /
#                        business model). Can work down over years via structured CCs
#                        strictly above current price. No new puts ever.
# ---------------------------------------------------------------------------

LEGACY_EXIT_RULES = {

    # ── Triggers for BINARY_EXIT ────────────────────────────────────────────
    # Any position carrying one of these flags = exit at market, no discussion.
    "binary_exit_flags": {"ACCOUNTING_RISK", "DELISTING_RISK", "GOING_CONCERN", "PERMANENT_EXIT"},

    # ── Triggers for URGENT_RESTRUCTURE ────────────────────────────────────
    # Covered call is deep ITM: waiting gets called away at a worse price than selling now.
    "cc_itm_threshold_pct": 0.05,        # call strike < current_price * (1 - 0.05) = ITM by >5%

    # Call strike below cost basis: no recovery scenario — you'd be forced out at a loss
    # even if the stock rallied back to where you bought it.
    "cc_below_cost_basis": True,         # flag if short call strike < position cost_basis

    # ── Triggers for SLOW_EXIT ──────────────────────────────────────────────
    # Stock is deeply below assignment price with no binary event — orderly exit.
    "slow_exit_decline_pct": 0.30,       # stock >30% below cost_basis triggers SLOW_EXIT flag

    # Double-assignment: assigned on same name twice within this window → forced thesis review.
    "double_assignment_days": 90,        # two assignments within 90 days = thesis check required

    # ── CC rules enforced on SLOW_EXIT names ───────────────────────────────
    # The PYPL/MRNA trap: small CC income ($400/mo) on a massive loss ($100K+) while
    # generating only 0.3% monthly yield. Enforced at dry_run_order time.
    "min_cc_strike_pct_above_price": 0.05,   # calls must be at least 5% OTM above current price
    "block_cc_below_cost_basis": True,        # hard block: never sell call below cost_basis
    "block_new_puts_on_slow_exit": True,      # no new put exposure — only CCs to work down

    # ── Recovery velocity threshold ─────────────────────────────────────────
    # If monthly CC income / unrealized_loss < this, the exit path is unrealistic.
    # Flag it so the weekly report surfaces "you need X years at current rate."
    "min_recovery_velocity_pct": 0.02,   # at least 2%/mo of loss recovered — else flag as trapped

}

# ---------------------------------------------------------------------------
# India Account (ICICI Breeze)
# ---------------------------------------------------------------------------
INDIA_ACCOUNT = {
    "label": "Rahul — ICICI Direct",
    "type": "margin",
    "target_weekly_pnl": 25000,   # ₹25,000/week target (~₹13L/yr)
    "max_contracts_by_tier": {1: 5, 2: 3, 3: 1},
    "strategies": ["covered_call", "short_strangle", "cash_secured_put"],
}

INDIA_PERMANENT_EXITS: list[str] = []   # populate as needed

INDIA_REGIME_THRESHOLDS = {
    "indiavix_bull_threshold": 15.0,
    "indiavix_pause_threshold": 25.0,
    "ma_days": [50, 200],
}
