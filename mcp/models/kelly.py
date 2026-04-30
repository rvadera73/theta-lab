"""
Kelly Criterion for options position sizing.
Use half-Kelly in practice — full Kelly is too aggressive for options.

For a short put:
  p = probability of profit (≈ 1 - delta, or use Black-Scholes PoP)
  b = expected win / expected loss ratio
  Kelly % = p - (1-p) / b
  Practical size = half-Kelly × account size
"""

from dataclasses import dataclass


@dataclass
class KellyResult:
    symbol: str
    pop: float                    # probability of profit (0-1)
    premium_credit: float         # total credit collected ($)
    max_loss: float               # worst-case loss if assigned (before CC recovery)
    net_expected_loss: float      # max_loss minus CC recovery premium estimate
    full_kelly_pct: float         # full Kelly fraction (%)
    half_kelly_pct: float         # half-Kelly (recommended)
    dollar_risk: float            # dollar amount at risk (half-Kelly)
    max_contracts: int            # contracts at half-Kelly
    signal: str
    interpretation: str


def kelly_position_size(
    symbol: str,
    pop: float,
    premium_credit: float,
    strike: float,
    contracts_requested: int = 1,
    account_size: float = 429_659,
    cc_monthly_premium: float = 0.0,
    recovery_months: int = 12,
    expected_loss_pct_of_max: float = 0.35,
) -> KellyResult:
    """
    Computes Kelly-optimal position size for a short put entry.

    pop: probability of profit as decimal (0.85 = 85%). Use 1 - option delta.
    premium_credit: total credit per contract × number of contracts ($)
    strike: put strike price
    contracts_requested: how many contracts you want to open
    account_size: total net liquidation value of the account
    cc_monthly_premium: estimated monthly CC premium if assigned (reduces effective loss)
    recovery_months: months of CC recovery to factor into net loss
    expected_loss_pct_of_max: realistic assignment depth (0.35 = stock falls 35% of way
        from strike to zero on average — much less than max loss in most assignments).
    """
    if pop <= 0 or pop >= 1:
        return KellyResult(
            symbol=symbol, pop=pop, premium_credit=0, max_loss=0, net_expected_loss=0,
            full_kelly_pct=0, half_kelly_pct=0, dollar_risk=0, max_contracts=0,
            signal="INVALID", interpretation="PoP must be between 0 and 1."
        )

    premium_per_contract = premium_credit / max(contracts_requested, 1)
    max_loss_per_contract = (strike * 100) - premium_per_contract
    # Use expected loss (not max loss) — realistic assignment depth
    expected_loss_per_contract = max_loss_per_contract * expected_loss_pct_of_max

    # CC recovery reduces net expected loss
    cc_recovery = cc_monthly_premium * recovery_months
    net_loss_per_contract = max(0, expected_loss_per_contract - cc_recovery)

    if net_loss_per_contract <= 0:
        return KellyResult(
            symbol=symbol, pop=pop, premium_credit=premium_credit,
            max_loss=max_loss_per_contract, net_expected_loss=0,
            full_kelly_pct=100.0, half_kelly_pct=50.0,
            dollar_risk=0, max_contracts=contracts_requested,
            signal="POSITIVE EV — CC covers full expected loss",
            interpretation=f"{symbol}: CC recovery exceeds expected assignment loss. Any size is mathematically justified. Cap at per-name concentration limit."
        )

    # Kelly formula: f* = p - (1-p) / b where b = win/loss ratio
    b = premium_per_contract / net_loss_per_contract
    kelly_f = pop - (1 - pop) / b

    if kelly_f <= 0:
        return KellyResult(
            symbol=symbol, pop=pop, premium_credit=premium_credit,
            max_loss=max_loss_per_contract, net_expected_loss=net_loss_per_contract,
            full_kelly_pct=0, half_kelly_pct=0, dollar_risk=0, max_contracts=0,
            signal="NEGATIVE EV — do not trade",
            interpretation=(
                f"{symbol}: Kelly is negative ({kelly_f*100:.1f}%). Expected value is negative "
                f"even at PoP={pop*100:.0f}%. Widen strike or skip."
            )
        )

    full_kelly_pct = kelly_f * 100
    half_kelly_pct = full_kelly_pct / 2

    # Dollar risk at half-Kelly = half-Kelly % × account size
    dollar_risk = account_size * (half_kelly_pct / 100)
    max_contracts = max(1, int(dollar_risk / expected_loss_per_contract))

    # Cap at account concentration limits (max 10% of account per name from per-name cap)
    concentration_limit = account_size * 0.10
    if dollar_risk > concentration_limit:
        dollar_risk = concentration_limit
        max_contracts = max(1, int(dollar_risk / expected_loss_per_contract))
        signal = "CAPPED — concentration limit"
    elif kelly_f >= 0.25:
        signal = "STRONG"
    elif kelly_f >= 0.10:
        signal = "MODERATE"
    else:
        signal = "SMALL"

    interpretation = (
        f"{symbol}: PoP={pop*100:.0f}%, Premium=${premium_per_contract:,.0f}, "
        f"Net loss if assigned=${net_loss_per_contract:,.0f}. "
        f"Full Kelly={full_kelly_pct:.1f}% → Half-Kelly={half_kelly_pct:.1f}% "
        f"= ${dollar_risk:,.0f} max risk → {max_contracts} contract(s)."
    )

    return KellyResult(
        symbol=symbol, pop=pop,
        premium_credit=premium_credit,
        max_loss=round(max_loss_per_contract, 0),
        net_expected_loss=round(net_loss_per_contract, 0),
        full_kelly_pct=round(full_kelly_pct, 1),
        half_kelly_pct=round(half_kelly_pct, 1),
        dollar_risk=round(dollar_risk, 0),
        max_contracts=max_contracts,
        signal=signal,
        interpretation=interpretation,
    )


def batch_kelly(
    candidates: list[dict],
    account_size: float = 429_659,
) -> list[dict]:
    """
    Run Kelly sizing for a list of potential entries.
    candidates: list of dicts with keys matching kelly_position_size args.
    Returns sorted list (highest half-Kelly % first) with POSITIVE EV only.
    """
    results = []
    for c in candidates:
        r = kelly_position_size(
            symbol=c["symbol"],
            pop=c.get("pop", 0.80),
            premium_credit=c.get("premium_credit", 500),
            strike=c.get("strike", 100),
            contracts_requested=c.get("contracts", 1),
            account_size=account_size,
            cc_monthly_premium=c.get("cc_monthly_premium", 0),
            recovery_months=c.get("recovery_months", 12),
        )
        if r.full_kelly_pct > 0:
            results.append({
                "symbol": r.symbol,
                "pop": r.pop,
                "half_kelly_pct": r.half_kelly_pct,
                "max_contracts": r.max_contracts,
                "dollar_risk": r.dollar_risk,
                "signal": r.signal,
                "interpretation": r.interpretation,
            })

    results.sort(key=lambda x: x["half_kelly_pct"], reverse=True)
    return results


if __name__ == "__main__":
    # Demo: UBER $68P — 85% PoP, $400 credit, $6800 max loss
    r = kelly_position_size(
        symbol="UBER",
        pop=0.85,
        premium_credit=400,
        strike=68,
        account_size=429_659,
        cc_monthly_premium=150,
        recovery_months=6,
    )
    print(r.interpretation)
    print(f"Signal: {r.signal}")
