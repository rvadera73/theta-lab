"""
Monte Carlo simulation for assignment probability.
Simulates stock price paths (GBM) and determines probability that
the total assigned equity book exceeds the danger zone threshold.

Practical use: run weekly before opening new put positions.
If P(book > danger zone) > 30%, throttle new put entries.
"""

import math
import random
from datetime import date, datetime
import yfinance as yf


# Danger zone threshold from strategy rules (bear regime = 25% of ~$1.5M active AUM)
DANGER_ZONE_DEFAULT = 375_000


def _fetch_vol_and_price(symbol: str) -> tuple[float, float]:
    """Returns (30-day annualized vol, current price) for a symbol."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="45d")
        closes = hist["Close"].tolist()
        if len(closes) < 31:
            return 0.40, closes[-1] if closes else 100.0
        current_price = closes[-1]
        returns = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
        recent = returns[-30:]
        mean_r = sum(recent) / len(recent)
        variance = sum((r - mean_r) ** 2 for r in recent) / (len(recent) - 1)
        annual_vol = math.sqrt(variance * 252)
        return annual_vol, current_price
    except Exception:
        return 0.40, 100.0


def simulate_assignment_probability(
    open_puts: list[dict],
    danger_zone: float = DANGER_ZONE_DEFAULT,
    n_simulations: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    Simulates total assigned equity book value across n_simulations paths.

    open_puts: list of dicts with keys:
        symbol (str), strike (float), dte (int), contracts (int)
        Optionally: current_price (float), annual_vol (float)

    Returns:
        probability of exceeding danger_zone
        distribution percentiles
        per-symbol assignment probability
        expected assigned equity under each scenario
    """
    random.seed(seed)

    # Fetch market data for each unique symbol
    symbols_data: dict[str, tuple[float, float]] = {}
    unique_syms = {p["symbol"] for p in open_puts}
    for sym in unique_syms:
        if "annual_vol" in open_puts[0] and "current_price" in open_puts[0]:
            # Use provided values
            for p in open_puts:
                if p["symbol"] == sym:
                    symbols_data[sym] = (p.get("annual_vol", 0.40), p.get("current_price", 100.0))
                    break
        else:
            symbols_data[sym] = _fetch_vol_and_price(sym)

    # Run simulations
    total_assigned_values = []
    per_symbol_assignments = {p["symbol"]: 0 for p in open_puts}

    for sim in range(n_simulations):
        # For each simulation, draw one terminal price per symbol
        sim_prices: dict[str, float] = {}
        for sym, (vol, price) in symbols_data.items():
            # Find max DTE for this symbol across all puts
            max_dte = max(
                (p["dte"] for p in open_puts if p["symbol"] == sym), default=45
            )
            t = max_dte / 252.0
            if t <= 0:
                sim_prices[sym] = price
                continue
            # GBM: drift = 0 (risk-neutral), use realized vol
            z = _box_muller()
            sim_price = price * math.exp(-0.5 * vol ** 2 * t + vol * math.sqrt(t) * z)
            sim_prices[sym] = sim_price

        # Compute assigned equity for this simulation
        sim_assigned = 0.0
        for put in open_puts:
            sym = put["symbol"]
            strike = put["strike"]
            contracts = put.get("contracts", 1)
            terminal_price = sim_prices.get(sym, symbols_data[sym][1])

            if terminal_price < strike:
                # Assigned: shares = contracts × 100, value at current market (not strike)
                assigned_value = terminal_price * contracts * 100
                sim_assigned += assigned_value

                if sim == 0:  # count for frequency (use all sims below)
                    pass

        total_assigned_values.append(sim_assigned)

    # Per-symbol assignment frequency (separate pass for accuracy)
    for put in open_puts:
        sym = put["symbol"]
        strike = put["strike"]
        contracts = put.get("contracts", 1)
        vol, price = symbols_data[sym]
        max_dte = put["dte"]
        t = max_dte / 252.0 if max_dte > 0 else 0.001
        count = sum(
            1 for _ in range(1000)
            if (price * math.exp(-0.5 * vol**2 * t + vol * math.sqrt(t) * _box_muller())) < strike
        )
        per_symbol_assignments[sym] = round(count / 10, 1)  # as percentage

    # Compute statistics
    total_assigned_values.sort()
    n = len(total_assigned_values)
    exceed_count = sum(1 for v in total_assigned_values if v > danger_zone)
    p_exceed = exceed_count / n

    pct10 = total_assigned_values[int(n * 0.10)]
    pct25 = total_assigned_values[int(n * 0.25)]
    pct50 = total_assigned_values[int(n * 0.50)]
    pct75 = total_assigned_values[int(n * 0.75)]
    pct90 = total_assigned_values[int(n * 0.90)]
    expected = sum(total_assigned_values) / n

    action = (
        "THROTTLE new puts — high probability of exceeding danger zone." if p_exceed > 0.40 else
        "CAUTION — meaningful chance of exceeding danger zone. Add selectively." if p_exceed > 0.20 else
        "LOW RISK — probability of danger zone breach is manageable. Normal entries OK."
    )

    return {
        "n_simulations": n_simulations,
        "danger_zone_threshold": danger_zone,
        "p_exceed_danger_zone": round(p_exceed * 100, 1),
        "expected_assigned_equity": round(expected, 0),
        "percentiles": {
            "p10": round(pct10, 0),
            "p25": round(pct25, 0),
            "p50": round(pct50, 0),
            "p75": round(pct75, 0),
            "p90": round(pct90, 0),
        },
        "per_symbol_assignment_pct": per_symbol_assignments,
        "open_puts_count": len(open_puts),
        "action": action,
        "signal": "THROTTLE" if p_exceed > 0.40 else ("CAUTION" if p_exceed > 0.20 else "NORMAL"),
    }


def _box_muller() -> float:
    """Generate a standard normal random variable using Box-Muller transform."""
    import math
    u1 = random.random()
    u2 = random.random()
    if u1 == 0:
        u1 = 1e-10
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


if __name__ == "__main__":
    # Demo with Account A's open puts (approximate from action report)
    demo_puts = [
        {"symbol": "AXON", "strike": 470, "dte": 54, "contracts": 1},
        {"symbol": "AXON", "strike": 660, "dte": 146, "contracts": 1},
        {"symbol": "AXON", "strike": 540, "dte": 237, "contracts": 1},
        {"symbol": "AXON", "strike": 420, "dte": 265, "contracts": 1},
        {"symbol": "APP",  "strike": 580, "dte": 118, "contracts": 1},
        {"symbol": "APP",  "strike": 460, "dte": 83, "contracts": 1},
        {"symbol": "ADBE", "strike": 310, "dte": 118, "contracts": 1},
        {"symbol": "MSFT", "strike": 420, "dte": 20, "contracts": 1},
        {"symbol": "META", "strike": 550, "dte": 237, "contracts": 1},
        {"symbol": "META", "strike": 520, "dte": 328, "contracts": 1},
    ]
    result = simulate_assignment_probability(demo_puts)
    print(f"P(exceed $375K danger zone): {result['p_exceed_danger_zone']}%")
    print(f"Expected assigned equity: ${result['expected_assigned_equity']:,.0f}")
    print(f"Percentiles: {result['percentiles']}")
    print(f"Action: {result['action']}")
