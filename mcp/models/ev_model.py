"""
Expected Value model for each short put entry.
EV must be positive AFTER accounting for CC recovery if assigned.
This catches entries that look attractive on premium alone but are negative EV.
"""


def trade_ev(
    symbol: str,
    pop: float,
    premium_credit: float,
    strike: float,
    current_price: float,
    cc_monthly_premium: float = 0.0,
    recovery_months: int = 12,
    contracts: int = 1,
    expected_loss_pct_of_max: float = 0.35,
) -> dict:
    """
    Computes raw EV and recovery-adjusted EV for a short put entry.

    pop: probability of profit (1 - delta, as decimal)
    premium_credit: total credit received ($, all contracts combined)
    strike: put strike price
    current_price: underlying stock current price
    cc_monthly_premium: expected monthly CC premium if assigned ($, per position)
    recovery_months: how many months of CC premium to include in recovery
    contracts: number of contracts
    expected_loss_pct_of_max: when assigned, stock typically falls 30-40% below strike
        (not 100%). Default 0.35 = stock falls to ~65% of strike on average at expiry.
        Use 0.20 for tight strikes; 0.50 for very deep ITM scenarios.

    Raw EV    = PoP × premium − (1−PoP) × expected_loss
    Adj EV    = Raw EV + (1−PoP) × cc_recovery
    EV/risk   = Adj EV / expected_loss  [return on risk]

    Note: max_loss (strike × 100 − premium) is the worst case.
    Expected loss uses expected_loss_pct_of_max to reflect realistic assignment depth.
    """
    max_loss = (strike * 100 * contracts) - premium_credit
    # Expected actual loss if assigned = partial loss, not max loss
    expected_loss = max_loss * expected_loss_pct_of_max
    prob_loss = 1 - pop
    cc_recovery = cc_monthly_premium * recovery_months

    raw_ev = pop * premium_credit - prob_loss * expected_loss
    adj_ev = raw_ev + prob_loss * cc_recovery

    # EV per dollar of risk (at-risk capital = expected loss)
    ev_per_dollar = adj_ev / expected_loss if expected_loss > 0 else 0

    # Expected assignment depth: how far below strike does stock need to go?
    # Using current price as reference
    itm_if_assigned_pct = (strike - current_price) / current_price * 100

    if adj_ev > 0:
        if ev_per_dollar >= 0.05:
            signal = "STRONG GO"
        else:
            signal = "GO"
    elif adj_ev > -premium_credit * 0.5:
        signal = "MARGINAL — verify assumptions"
    else:
        signal = "NO GO — negative EV even with CC recovery"

    return {
        "symbol": symbol,
        "contracts": contracts,
        "pop": round(pop * 100, 1),
        "premium_credit": round(premium_credit, 0),
        "max_loss": round(max_loss, 0),
        "expected_loss": round(expected_loss, 0),
        "cc_recovery_estimate": round(cc_recovery, 0),
        "raw_ev": round(raw_ev, 0),
        "recovery_adjusted_ev": round(adj_ev, 0),
        "ev_per_dollar_risk": round(ev_per_dollar * 100, 2),
        "itm_depth_pct": round(itm_if_assigned_pct, 1),
        "signal": signal,
        "go": adj_ev > 0,
        "interpretation": (
            f"{symbol} {contracts}x ${strike}P: "
            f"PoP={pop*100:.0f}%, Credit=${premium_credit:,.0f}, "
            f"Exp loss if assigned=${expected_loss:,.0f} ({expected_loss_pct_of_max*100:.0f}% of max), "
            f"Raw EV=${raw_ev:,.0f}, Adj EV (with CC)=${adj_ev:,.0f} → {signal}. "
            f"EV/risk: {ev_per_dollar*100:.2f}c per $1 expected risk."
        ),
    }


def batch_ev(candidates: list[dict]) -> list[dict]:
    """
    Run EV model for a list of potential entries.
    Returns sorted by recovery-adjusted EV (highest first), GO trades only.
    """
    results = []
    for c in candidates:
        r = trade_ev(
            symbol=c["symbol"],
            pop=c.get("pop", 0.80),
            premium_credit=c.get("premium_credit", 500),
            strike=c.get("strike", 100),
            current_price=c.get("current_price", 110),
            cc_monthly_premium=c.get("cc_monthly_premium", 0),
            recovery_months=c.get("recovery_months", 12),
            contracts=c.get("contracts", 1),
        )
        results.append(r)

    results.sort(key=lambda x: x["recovery_adjusted_ev"], reverse=True)
    return results


if __name__ == "__main__":
    # Demo: UBER $68P — 85% PoP, $400 credit, $6800 max assignment loss
    r = trade_ev(
        symbol="UBER",
        pop=0.85,
        premium_credit=400,
        strike=68,
        current_price=74.64,
        cc_monthly_premium=150,
        recovery_months=6,
    )
    print(r["interpretation"])
    print(f"EV/risk: {r['ev_per_dollar_risk']}¢ per $1 at risk")

    # Demo: PYPL $45P — would have been negative EV
    r2 = trade_ev(
        symbol="PYPL (historical)",
        pop=0.72,
        premium_credit=800,
        strike=45,
        current_price=50,
        cc_monthly_premium=200,
        recovery_months=24,
    )
    print(r2["interpretation"])
