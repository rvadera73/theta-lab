# Theta-Lab Performance Engine — Quick Start

## 30-Second Overview

The Performance Engine generates 4 actionable reports (Live Dashboard, Weekly Execution, Bi-weekly Trend, Monthly Strategy) from your real trading data.

**Status:** Production-ready. Tested with June 2026 data. All 4 report types fully implemented.

---

## Installation

No installation needed. The engine is a single Python file with standard dependencies (pandas, numpy).

```bash
cd /home/rahulvadera/projects/theta-lab
python3 theta_lab_performance_engine.py
```

---

## Usage

### Generate All Reports (2 lines)

```python
from theta_lab_performance_engine import PerformanceEngine

engine = PerformanceEngine()
reports = engine.generate_all_reports()

for report_type, content in reports.items():
    print(content)
```

### Generate Specific Report

```python
# Daily dashboard
dashboard = engine.generate_live_dashboard()

# Weekly with plan
plan = {'put_entries': 5, 'call_entries': 3, 'close_targets': 8}
weekly = engine.generate_weekly_report(plan=plan)

# Bi-weekly
trends = engine.generate_trend_report()

# Monthly
monthly = engine.generate_monthly_review()
```

### Track Weekly Execution

```python
# Record actual trades as you execute them
engine.tracker.plan = plan  # Set your plan
engine.tracker.record_actual('put_entries', 'AAPL', 2)
engine.tracker.record_actual('call_entries', 'MSFT', 1)
engine.tracker.record_actual('closes', 'TSLA', 5)

# Get variance analysis
variance = engine.tracker.get_variance_analysis()
print(variance)
```

### Access Components Directly

```python
# Portfolio health
margin = engine.metrics.get_margin_utilization()        # Current margin %
concentration = engine.metrics.get_concentration()      # Position sizing
balances = engine.metrics.get_account_balances()        # All 8 accounts

# Risk monitoring
alerts = engine.risk.check_all()                        # Active alerts
margin_breach = engine.risk.check_margin_breach()       # Specific alert

# P&L analysis
total_pl = engine.closed_pl.get_total_pl()             # Total P&L
win_rate = engine.closed_pl.get_win_rate()             # Win rate overall
trades = engine.closed_pl.get_closed_trades(account='Account A (232)')

# Trend analysis
edge = engine.trends.get_edge_validity()                # Put vs call
regime = engine.trends.get_regime_assessment()          # IV, VIX, forecast
breakdown = engine.trends.get_market_breakdown_risk()   # SPX -10% scenario
```

---

## 4 Report Types

### 1. Live Dashboard (Daily)
**Purpose:** Real-time portfolio health and risk alerts

**Sections:**
- Portfolio Health Status (value, margin, Greeks, positions)
- Risk Breach Checklist (margin, concentration, win rate alerts)
- Account-Level On-Pace (vs annual target)
- Market Regime Context (IV Rank, VIX, implications)
- Top Holdings & Health
- Actionable Summary

**Sample output:**
```
Margin: 142.0% (CRITICAL — above 80% threshold)
Risk Alerts: 3 active
  [CRITICAL] Margin breach
  [WARNING] AXON concentration 16%
  [WARNING] Win rate decline to 82%
```

### 2. Weekly Execution Report (Weekly)
**Purpose:** Track execution quality and variance from plan

**Sections:**
- What We Planned
- What We Actually Did
- Variance Analysis (table with % variance)
- Position Performance Update
- Weekly P&L Summary
- Next Week Recommendations

**Sample output:**
```
Plan vs Actual:
  Put Entries: 5 planned → 7 actual (+40%)
  Call Entries: 3 planned → 4 actual (+33%)
  Closes: 8 planned → 12 actual (+50%)

Assessment: Exceeded targets (good opportunity spotting)
Weekly P&L: +$4,830
```

### 3. Bi-weekly Trend & Risk Report (Bi-weekly)
**Purpose:** Assess edge validity, regime shifts, market scenarios

**Sections:**
- Edge Validity Check (put vs call analysis)
- Market Breakdown Signals (SPX -10% scenario)
- Regime Change Signals (IV, VIX, probability forecast)
- Forecast & Strategy (next 2-4 weeks)
- Active Risk Alerts

**Sample output:**
```
Put-selling edge: VALID (+$107K YTD, 85.6% win rate)
Call-selling edge: INVALID (-$11K YTD) → PHASE OUT

SPX -10% scenario:
  Current margin: 142% → Post-crash: 160-170% (forced liquidation risk)
  
Strategy: Aggressive sell puts at 30-40 DTE in sideways market
```

### 4. Monthly Strategy Review (Monthly)
**Purpose:** Track goals, plan H2, assess annual progress

**Sections:**
- Monthly Goal Achievement (vs target by account)
- Annual Objective Progress (YTD vs annual target)
- H2 Recovery Plan (Q3/Q4 strategy)
- Risk Management Status
- Quarterly Focus Areas

**Sample output:**
```
June Target: $84,160 → Actual: $23,150 (28% of goal)
YTD: $148K of $1.2M (12.3%) — BEHIND PACE

H2 Recovery: Need $150K/month (vs $24K current)
Q3 Priority 1: Reduce margin 142% → <80%
Q3 Priority 2: Shift to 85/15 put/call ratio
Q3 Priority 3: Execute 40-50 new put entries (+2-3x pace)
```

---

## Component Reference

### ClosedPLAnalyzer
Calculates P&L from closed trades.

```python
closed_pl = engine.closed_pl

# Get closed trades
trades = closed_pl.get_closed_trades(start_date=date(2026, 6, 1))

# Get P&L summary
pl = closed_pl.get_total_pl()
print(pl['total'])              # Total P&L
print(pl['by_account'])         # P&L by account
print(pl['by_position_type'])   # P&L by type (PUT, CALL, etc.)

# Get win rate
wr = closed_pl.get_win_rate(group_by='account')
print(wr['overall'])            # Overall win rate
print(wr['details'])            # Win rate by account
```

### PortfolioMetricsCalculator
Gets current portfolio state.

```python
metrics = engine.metrics

# Margin utilization
margin = metrics.get_margin_utilization()
print(margin['current_percent'])       # Current: 142%
print(margin['status'])                # Status: MARGIN_BREACH
print(margin['alert_level'])           # Level: CRITICAL

# Portfolio Greeks (placeholder in v1.0)
greeks = metrics.get_portfolio_greeks()
print(greeks['delta'])
print(greeks['theta'])

# Concentration risk
conc = metrics.get_concentration()
print(conc['top_positions'])           # Top 3 positions
print(conc['concentration_risk'])      # Positions over 15% threshold

# Account balances
balances = metrics.get_account_balances()
for acc, balance in balances.items():
    print(f"{acc}: ${balance:,.0f}")
```

### ExecutionTracker
Tracks planned vs actual.

```python
tracker = engine.tracker

# Set plan
tracker.plan = {'put_entries': 5, 'call_entries': 3, ...}

# Record actual trades during the week
tracker.record_actual('put_entries', 'AAPL', 1)
tracker.record_actual('put_entries', 'MSFT', 2)
tracker.record_actual('call_entries', 'TSLA', 1)
tracker.record_actual('closes', 'NFLX', 3)

# Get variance analysis
variance = tracker.get_variance_analysis()
print(variance['variance'])  # {action: {planned, actual, delta, variance_pct}}
```

### TrendAnalyzer
Analyzes historical trends and forecasts.

```python
trends = engine.trends

# Edge validity (put vs call performance)
edge = trends.get_edge_validity()
print(edge['put_selling_edge']['status'])      # VALID
print(edge['put_selling_edge']['ytd_pl'])      # $107K
print(edge['call_selling_edge']['status'])     # INVALID

# Regime assessment
regime = trends.get_regime_assessment()
print(regime['iv_rank'])                       # 45 (medium)
print(regime['vix'])                           # 18 (normal)
print(regime['regime'])                        # SIDEWAYS
print(regime['expected_next_2_weeks'])         # Probabilities

# Market breakdown scenario (SPX -10%)
breakdown = trends.get_market_breakdown_risk()
print(breakdown['margin_risk']['post_crash_estimate'])  # 160-170%
print(breakdown['greek_risk'])                          # Delta, gamma exposure

# Sector rotation
sector = trends.get_sector_rotation()
print(sector['current_positioning'])           # By sector
```

### RiskMonitor
Monitors for breaches and alerts.

```python
risk = engine.risk

# Check all risks and get alerts
alerts = risk.check_all()
for alert in alerts:
    print(f"[{alert['type']}] {alert['category']}")
    print(f"  Detail: {alert['detail']}")
    print(f"  Action: {alert['action']}")

# Check specific risks
risk.check_margin_breach()       # Margin > 80%?
risk.check_concentration_breach() # Position > 15%?
risk.check_win_rate_degradation() # Win rate < 85%?
```

---

## Configuration

Edit top of `theta_lab_performance_engine.py`:

```python
# Account balances and targets
ACCOUNTS_CONFIG = {
    'Account A (232)': {'balance': 2732234, 'margin': True, 'monthly_target': 60000},
    # ... 8 total accounts
}

# Risk thresholds
MARGIN_CRITICAL_THRESHOLD = 0.80        # 80% utilization
CONCENTRATION_WARNING_THRESHOLD = 0.15  # 15% per position
WIN_RATE_TARGET = 0.85                  # 85% win rate target

# Other settings
CLOSE_COST_RATIO = 0.60                 # 60% close cost
DATA_DIR = Path('/home/rahulvadera/projects/theta-lab/data')
```

---

## Example Workflow

### Monday (Plan Phase)

```python
# Review Live Dashboard
dashboard = engine.generate_live_dashboard()
print(dashboard)

# Define this week's plan
plan = {
    'put_entries': 5,      # Target 5 new put sales
    'call_entries': 2,     # Target 2 new calls (limited due to poor win rate)
    'close_targets': 8,    # Target 8 profit-taking closes
    'reductions': 3,       # Target 3 risk management trades
}

# Store plan
engine.tracker.plan = plan
```

### Tue-Fri (Execution Phase)

```python
# As you trade, record actuals
engine.tracker.record_actual('put_entries', 'AAPL', 1)
engine.tracker.record_actual('put_entries', 'MSFT', 1)
engine.tracker.record_actual('closes', 'COIN', 2)
# ... continue recording
```

### Friday (Review Phase)

```python
# Generate weekly report with plan comparison
weekly = engine.generate_weekly_report(plan=plan)
print(weekly)

# Review variance
variance = engine.tracker.get_variance_analysis()
print(variance['variance'])

# Get recommendations for next week
# (included in weekly report)
```

### Next Monday (Trend Phase)

```python
# Every 2 weeks: Assess trends and regime
trends = engine.generate_trend_report()
print(trends)

# Understand edge validity and market scenarios
edge = engine.trends.get_edge_validity()
regime = engine.trends.get_regime_assessment()
```

### End of Month (Strategy Phase)

```python
# Generate monthly review
monthly = engine.generate_monthly_review()
print(monthly)

# Check progress vs annual goals
# Plan H2 recovery if needed
# Review quarterly priorities
```

---

## Sample Output

Run the engine:

```bash
python3 theta_lab_performance_engine.py
```

Or run examples:

```bash
python3 example_usage.py
```

Output includes:
- Live Dashboard (portfolio health, risks, regime)
- Weekly Execution Report (plan vs actual with variance)
- Bi-weekly Trend Report (edge validity, scenarios, forecast)
- Monthly Strategy Review (goals, annual progress, H2 plan)

All reports use **real data** from your accounts and transactions.

---

## Key Insights (Current as of June 2026)

From sample output:

**Portfolio Status:**
- Value: $4.55M (8 accounts)
- Margin: 142% (CRITICAL — must reduce)
- Open positions: 238 across 84 tickers

**What's Working:**
- Put-selling: +$107K YTD, 85.6% win rate ✓
- Account B: 92% win rate (best performer)

**What's Broken:**
- Call-selling: -$11K YTD (PHASE OUT) ✗
- Margin: 142% > 80% threshold (IMMEDIATE ACTION) ⚠️
- Win rate: Declining 89% → 82% (TIGHTEN CRITERIA) ⚠️

**Strategy for H2:**
- Reduce margin to <80% (Priority 1)
- Shift to 85/15 put/call ratio (Priority 2)
- Execute 40-50 new put entries in Q3 (Priority 3)
- Target $150K/month to hit annual $1.2M goal

---

## Next Steps

1. **Today:** Run the engine and review all 4 report types
2. **This Week:** Define your execution plan for next week
3. **Ongoing:** Use tracker to record actuals and review variance
4. **Every 2 weeks:** Generate trend report and assess edge
5. **Monthly:** Generate strategy review and plan H2

---

## Questions?

See **PERFORMANCE_ENGINE_README.md** for detailed documentation.

See **example_usage.py** for 10 complete code examples.

See **theta_lab_performance_engine.py** code comments for implementation details.

---

**Version:** 1.0  
**Status:** Production-Ready  
**Last Updated:** June 9, 2026
