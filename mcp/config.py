"""
Theta-lab configuration — persona guardrails and account parameters.
All thresholds derived from trading_persona.md.
"""

from dataclasses import dataclass, field
from enum import Enum


class Regime(str, Enum):
    BEAR_SIDEWAYS = "BEAR_SIDEWAYS"
    TRANSITIONING = "TRANSITIONING"
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
    "target_annual_return": 0.20,
    "target_weekly_pnl": 1619,       # $84K/yr ÷ 52
    "max_contracts_by_tier": {1: 5, 2: 3, 3: 1},
    "margin_alert_pct": 0.80,
    "strategies": ["covered_call", "short_strangle"],
}

ACCOUNT_B = {
    "label": "Pinky — Schwab IRA",
    "type": "ira",
    "target_annual_return": 0.12,
    "target_weekly_pnl": 537,        # $28K/yr ÷ 52
    "max_contracts_by_tier": {1: 1, 2: 1, 3: 1},
    "no_margin": True,
    "no_naked_calls": True,
    "speculative_max_pct": 0.10,
    "strategies": ["cash_secured_put", "covered_call"],
}

# ---------------------------------------------------------------------------
# Profit-take targets by regime
# ---------------------------------------------------------------------------

PROFIT_TARGETS = {
    Regime.BEAR_SIDEWAYS: (0.40, 0.60),  # close when 40-60% of max premium captured
    Regime.TRANSITIONING: (0.50, 0.60),
    Regime.BULL: (0.70, 0.70),
}

# ---------------------------------------------------------------------------
# DTE targets by regime
# ---------------------------------------------------------------------------

DTE_TARGETS = {
    Regime.BEAR_SIDEWAYS: None,          # No new entries
    Regime.TRANSITIONING: (45, 90),
    Regime.BULL: (90, 360),
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
# Risk management
# ---------------------------------------------------------------------------

RISK = {
    "stop_loss": "flag_and_ask",         # Never auto-close
    "flag_threshold_multiplier": 2.0,    # Flag when mark > 2x premium received
    "roll_dte_threshold": 21,            # Roll or close when DTE <= 21
    "iv_rank_min_new_entry": 40,         # IVR minimum for new entries
    "earnings_blackout_days": 7,
    "min_open_interest": 500,
    "max_bid_ask_spread_pct": 0.10,
}

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

ITM_POSITION_PLANS = {
    "CRM":  "hold_maximize_cc_premium",
    "NVO":  "natural_exit_via_assignment",
    "MRNA": "natural_exit_complete",
    "CRWD": "standard_roll_management",
}
