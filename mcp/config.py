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
    Regime.BEAR_SIDEWAYS: (0.40, 0.60),  # close when 40-60% of max premium captured
    Regime.TRANSITIONING: (0.50, 0.60),
    Regime.CAUTIOUS_BULL: (0.55, 0.65),  # take profits sooner than full bull; respect macro risk
    Regime.BULL: (0.70, 0.70),
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
