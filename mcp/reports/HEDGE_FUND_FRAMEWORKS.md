# Hedge Fund Frameworks for Unified Reporting

## Overview

Professional hedge funds use complementary frameworks beyond position-level conviction scoring. These frameworks provide macro-level portfolio analysis, risk attribution, and alpha measurement that enhance decision-making. This document identifies which frameworks are most relevant for theta-lab's short premium strategy and how to integrate them.

## Framework Selection Criteria

For theta-lab's approach (short premium, strangles, covered calls, wheels), frameworks must:
1. **Work with options portfolios** — handle Greeks, time decay, volatility exposure
2. **Measure income vs capital gains** — theta strategy separates yield from directional P&L
3. **Identify concentration risk** — avoid overleveraging single factors
4. **Enable sector rotation** — track and execute rotations programmatically
5. **Be calculable from live data** — no special proprietary data feeds required

## Recommended Frameworks for Integration

### 1. Greeks Attribution to P&L (PRIORITY 1)

**What it measures:** How much portfolio returns come from theta decay vs gamma vs vega exposure.

**Why relevant:** Short premium strategy's return sources are: theta (decay), vega (IV drop), gamma (realized vol lower than sold vol). Understanding the split reveals which edge is working.

**Implementation:**
```
Portfolio Greeks (daily):
- Total delta: Sum of position deltas
- Total theta: Sum of position theta (premium decay per day)
- Total vega: Sum of position vega (P&L per 1% IV change)
- Total gamma: Sum of position gamma (P&L from realized move)

Attribution (daily):
- Theta captured: Realized theta from positions closed for profit
- Vega captured: Realized vega (IV rank drops, short vega benefits)
- Gamma realized: Realized gamma (bid-ask delta from underlying moves)
- Realized P&L = Theta + Vega + Gamma + [Carry costs]
```

**Integration:**
- **Daily Report**: Show portfolio Greeks summary + realized attribution from closed positions
- **Weekly Report**: Greek trend (theta accelerating as expiry nears? vega captured from IV rank compression?)
- **Monthly Report**: Attribution pie chart (% of returns from each Greek)

**Data sources:**
- Greeks already calculated in `enhanced_metrics.py` (delta approximation)
- Extend to include vega, gamma via Black-Scholes
- Track realized P&L by Greek from closed positions

---

### 2. Factor Exposure Analysis (PRIORITY 2)

**What it measures:** Portfolio sensitivity to macro factors (tech vs commodities vs consumer, growth vs value, momentum vs mean-reversion).

**Why relevant:** Short premium strategy benefits from factor *rotation*, not directional conviction. Understanding exposure helps avoid concentration in one factor.

**Implementation:**
```
Factor Definitions (for this portfolio):
1. **Tech Factor**: Weight of NFLX, MSFT, NVDA, ASML, CRWD, QBTS (≈40% of portfolio)
   - Short tech calls = collect from tech rallies
   - Benefit: Tech volatility high → premium elevated
   - Risk: Tech drawdown → many calls assigned simultaneously
   
2. **Finance Factor**: Weight of COIN, HOOD, CRM, PYPL (≈12% of portfolio)
   - Crypto-sensitive + IPO/fintech names
   - Benefit: High IV when risk-off
   - Risk: Tight correlations in stress
   
3. **Consumer Factor**: Weight of NKE, ULTA, ELF, CAVA (≈20% of portfolio)
   - Value/discount segment
   - Benefit: Stable earnings, high wheel premium
   - Risk: Rate-sensitive
   
4. **Industrial Factor**: Weight of BA, NOC, RTX, GEV, LMT (≈15% of portfolio)
   - Cyclical + defense
   - Benefit: Multiple expansion in bull markets
   - Risk: War/budget cuts downsides
   
5. **Energy Factor**: Weight of XOM, CCJ, DVN (≈2% of portfolio)
   - Macro commodity play
   - Benefit: High IV in geopolitical stress
   - Risk: Structural headwinds (energy transition)

Factor Exposure Summary (% notional):
- Tech: 40% (HIGH - concentration risk)
- Consumer: 20% (MODERATE)
- Industrial: 15% (MODERATE)
- Finance: 12% (MODERATE)
- Energy: 2% (LOW)
- Healthcare/Other: 11% (DIVERSIFIED)

Rebalancing Trigger:
- If single factor exceeds 50% notional → reduce or rotate
- If single factor <30% and has HIGH conviction → add to (if gate passes)
```

**Integration:**
- **Daily Report**: Factor exposure summary (pie chart or bar)
- **Weekly Report**: Factor rotation signals (which factors are extended vs attractive?)
- **Monthly Report**: Factor performance attribution (which factors drove returns?)

**Data sources:**
- Sector classifications from sector analysis (map to factors)
- Notional calculations already in place

---

### 3. Relative Value vs Benchmark (PRIORITY 3)

**What it measures:** Portfolio alpha (outperformance) vs SPY/QQQ benchmark.

**Why relevant:** Confirms that the strategy is earning premium on top of market returns, not just beta exposure.

**Implementation:**
```
Benchmark Comparison (weekly):
- Portfolio YTD return: [from trade history]
- SPY YTD return: [from Yahoo Finance]
- QQQ YTD return: [from Yahoo Finance]
- Alpha: Portfolio return - (Beta × Benchmark return)
- Information Ratio: (Portfolio return - Benchmark return) / Tracking error

Relative to SPY (traditional benchmark):
- Expected in BULL: Portfolio underperforms (short calls on rallies)
- Expected in BEAR: Portfolio outperforms (short puts on dips)
- Current regime (CAUTIOUS_BULL): Expect slight SPY underperformance, QQQ outperformance

Rolling Metrics (13-week):
- Correlation to SPY: Should be <0.7 (diversified from market beta)
- Beta to SPY: Should be 0.3-0.6 (delta-hedged, not fully exposed)
- Sharpe ratio: [Return / Volatility]
```

**Integration:**
- **Weekly Report**: Benchmark comparison + alpha calculation
- **Monthly Report**: Sharpe ratio trend, correlation analysis
- **Quarterly Report**: Relative value summary (are we earning alpha?)

**Data sources:**
- Historical returns from trade records (future enhancement)
- Benchmark prices from Yahoo Finance
- Beta calculation from historical correlation

---

### 4. Concentration Risk (Herfindahl Index) (PRIORITY 2)

**What it measures:** Portfolio concentration in single positions / sectors / tickers.

**Why relevant:** Concentration amplifies both upside and downside. Theta strategy needs diversification to avoid correlated losses.

**Implementation:**
```
Concentration Metrics:

1. Ticker Concentration (Herfindahl-Hirschman Index):
   HHI = Sum of (ticker_notional / total_notional)²
   
   HHI interpretation:
   - <0.15: Well-diversified (good)
   - 0.15-0.25: Moderate concentration (acceptable)
   - >0.25: High concentration (risk)
   
   Current portfolio (example):
   - ASML: $447K / $9.5M = 4.7% → (0.047)² = 0.00221
   - MU: $440K / $9.5M = 4.6% → (0.046)² = 0.00212
   - NFLX: $353K / $9.5M = 3.7% → (0.037)² = 0.00137
   - [137 more tickers...]
   - HHI = sum of all = ~0.008 (HIGHLY DIVERSIFIED ✓)

2. Sector Concentration:
   Same calculation by sector
   Current: Tech 36%, Fin 5%, Consumer 9%, Industrial 21%, Other 29%
   - Tech heavy but diversified within sector ✓

3. Greeks Concentration:
   - Delta concentration: If 80% of delta in 3 tickers → high risk
   - Theta concentration: If 80% of theta in Tech → sector rotation risk
   - Vega concentration: If 80% of vega short → bad if IV spikes
```

**Integration:**
- **Daily Report**: HHI score + concentration heat (GREEN if <0.15, YELLOW if 0.15-0.25, RED if >0.25)
- **Weekly Report**: Concentration by ticker, sector, Greek
- **Monthly Report**: Concentration trend (are we drifting into concentration?)

---

### 5. Correlation & Hedge Effectiveness (PRIORITY 3)

**What it measures:** How correlated are portfolio positions? Are short puts effectively hedging long calls?

**Why relevant:** Stagger positions (puts + calls on same name) should behave like iron condors — hedged on both sides. Full correlation = no hedge benefit.

**Implementation:**
```
Correlation Matrix (weekly):
- Calculate rolling 20-day correlation between top 20 tickers
- Color-code: RED if >0.8 (highly correlated), YELLOW if 0.6-0.8, GREEN if <0.6

Hedge Effectiveness (per stagger position):
- AXON example: 6 short puts + 8 short calls
  - If AXON drops 5%, puts lose premium (bad)
  - If AXON rises 5%, calls lose premium (bad)
  - But puts are 0.15 delta and calls are 0.20 delta
  - Net delta ≈ -(0.15×6) + (0.20×8) ≈ 0.10 (slightly bullish)
  - Hedge effectiveness: Not perfect (theta decay helps both sides)

Portfolio Hedge Ratio (overall):
- Total short put delta vs total short call delta
- Should be roughly balanced (50/50) unless regime-biased
```

**Integration:**
- **Weekly Report**: Top 5 correlations (watch for >0.85 pairs)
- **Stagger Dashboard**: Per-position hedge effectiveness score
- **Monthly Report**: Correlation trend + systemic risk assessment

---

### 6. Greeks Marginal Contribution to Risk (PRIORITY 3)

**What it measures:** Which positions contribute most to portfolio Greeks? Which positions are "disproportionate risk"?

**Why relevant:** Identifies positions that should be sized down (contributing too much vega/gamma) or thesis-challenged.

**Implementation:**
```
Marginal Greeks Contribution:

Example (tech sector):
- NVDA: $218.80 × 3 contracts × 100 = $65,640 notional
  - Delta: -0.15 (short 3 puts) = -45 delta
  - Theta: +0.35 per day × 3 = +1.05/day
  - Vega: -2.50 × 3 = -7.50 (short vega)
  
- ASML: $1,493 × 1 contract × 100 = $149,300 notional
  - Delta: -0.20 (short 1 put) = -20 delta
  - Theta: +0.42 per day × 1 = +0.42/day
  - Vega: -3.00 × 1 = -3.00

Ranking by Theta Contribution:
- NVDA: +1.05/day (2.5% of portfolio theta)
- ASML: +0.42/day (1.0% of portfolio theta)
- [...]
- Top 10 positions: 45% of portfolio theta

Ranking by Short Vega:
- NFLX: -42 contracts = -105 vega (largest short vega)
- AXON: -14 contracts = -35 vega
- [...]
- Concentration in vega: If top 3 = 60% of short vega → risk
```

**Integration:**
- **Daily Report**: Top 10 positions by theta, delta, vega (ranking)
- **Weekly Report**: Greeks trend (vega concentration rising? theta accelerating?)
- **Risk Dashboard**: Marginal Greeks heatmap (which positions carry outsized risk?)

---

### 7. Risk Metrics (Sharpe, Information Ratio, Sortino) (OPTIONAL)

**What it measures:** Return-per-unit-of-risk. Sharpe ratio = (return - risk-free rate) / volatility.

**Why relevant:** Confirms strategy is efficient (earning returns with minimal volatility).

**Implementation:**
```
Calculation (requires trade history, not implemented yet):
- Historical returns: [daily P&L from closed positions]
- Volatility: Standard deviation of daily returns
- Sharpe = (Avg daily return - risk-free rate) / Daily volatility
- Sortino = (Avg daily return - risk-free rate) / Downside volatility

Interpretation:
- Sharpe > 1.0: Excellent risk-adjusted returns
- Sharpe 0.5-1.0: Good
- Sharpe < 0.5: Poor

Current portfolio (estimated from thesis):
- Target Sharpe: 1.5-2.0 (short premium should be lower volatility than equities)
```

**Integration:**
- **Monthly Report**: Sharpe ratio + rolling Sortino
- **Quarterly Report**: Risk metrics trend

**Blocker:** Requires historical P&L data (future enhancement)

---

## Framework Integration Timeline

### Phase 1 (Immediate) — Now
- ✓ **Sector Analysis** (already integrated)
- 🟡 **Greeks Attribution** (add vega/gamma calculations)
- 🟡 **Factor Exposure** (use sector grouping)
- 🟡 **Concentration Risk** (HHI calculation)

### Phase 2 (This Month)
- 🟡 **Relative Value vs SPY/QQQ** (pull benchmark returns)
- 🟡 **Correlation Matrix** (rolling correlation on top 20)
- 🟡 **Hedge Effectiveness** (per-stagger analysis)

### Phase 3 (Next Month)
- 🟡 **Greeks Marginal Contribution** (ranking by Greeks)
- 🟡 **Risk Dashboard** (Greeks heatmap)

### Phase 4 (Next Quarter)
- 🔴 **Sharpe/Sortino** (requires P&L history)

---

## Suggested Report Structure (Enhanced)

### Daily Report (Current)
1. Account Health & Margin
2. Conviction Analysis (by heat bucket)
3. Heat Distribution
4. Market Regime
5. **NEW: Sector Analysis & Rotation**
6. Account Distribution
7. Top 20 Positions

### Weekly Report (Enhanced)
1. Account Health & Margin
2. Market Regime Forecast
3. **NEW: Factor Exposure Summary** (pie chart)
4. **NEW: Greeks Attribution Trend**
5. **NEW: Concentration Risk (HHI)**
6. Sector Analysis & Rotation
7. **NEW: Relative Value vs SPY/QQQ**
8. Top Action Items

### Monthly Report (Enhanced)
1. Account Health & Margin
2. Performance vs Target (Actual vs Expected)
3. **NEW: Sharpe Ratio & Risk Metrics**
4. **NEW: Factor Performance Attribution**
5. **NEW: Correlation Analysis**
6. Sector Rotation Performance
7. Concentration Risk Trend
8. Framework Updates

---

## Implementation Notes

### Greeks Calculation Enhancement
Current `enhanced_metrics.py` uses delta approximation. Extend with full Black-Scholes:
- `vega(S, K, T, r, sigma)` — already in `BlackScholesGreeks`
- `gamma(S, K, T, r, sigma)` — already in `BlackScholesGreeks`
- Use contract DTE from open_positions, implied vol from IV rank

### Factor Grouping
Map sectors to factors:
```
Tech Factor: Technology
Finance Factor: Financial Services
Consumer Factor: Consumer Cyclical + Consumer Defensive
Industrial Factor: Industrials + Basic Materials
Energy Factor: Energy
Healthcare Factor: Healthcare
```

### Benchmark Data
Fetch weekly from Yahoo Finance:
```python
spy = yf.Ticker("SPY")
qqq = yf.Ticker("QQQ")
spy_returns = spy.history(period="1y")["Close"].pct_change()
qqq_returns = qqq.history(period="1y")["Close"].pct_change()
```

### P&L Attribution (Future)
Store closed position P&L in CSV:
```
date, ticker, premium_collected, theta_realized, vega_realized, days_held, profit_loss
2026-05-12, NFLX, 1250, 890, -50, 14, 1090
```

Then calculate attribution per Greek source.

---

## Success Criteria

Frameworks are successfully integrated when:
1. **Concentration identified early** — HHI flags before risk > threshold
2. **Factor rotation executed** — Framework recommends sector shifts, trader confirms
3. **Greeks understood** — Can distinguish theta-driven vs vega-driven returns
4. **Benchmark tracked** — Know alpha generation rate
5. **Risk transparent** — Sharpe ratio and marginal risk visible daily

---

## Frameworks NOT Recommended (Yet)

❌ **Machine Learning Predictions** — adds complexity without edge; strategy is rules-based
❌ **Value at Risk (VaR)** — options Greeks already capture downside (delta/gamma)
❌ **Monte Carlo Simulations** — overkill for short premium (already hedged)
❌ **Overnight Gap Risk** — thesis-based, not quantifiable without proprietary data
❌ **Commodity Correlations** — portfolio is mostly equities/crypto, not commodity-heavy

---

## References

- **Black-Scholes Greeks**: Already implemented in `enhanced_metrics.py`
- **Sector Analysis**: Already integrated in daily/weekly reports
- **Concentration Index**: Herfindahl calculation, standard finance metric
- **Sharpe Ratio**: Industry-standard risk metric
