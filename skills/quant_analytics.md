# Quant Analytics — Theta-Lab

Model and metric reference for the premium-selling strategy.
All models live in `mcp/models/` and `mcp/analysis/metrics.py`.
Weekly email delivery via `mcp/routines/weekly_dashboard.py`.

---

## Dashboard Metrics

### Monthly Target Tracker — $100K Combined
**Goal:** $100K/month net = premium income + equity value change (realized + unrealized).
**Current pace (Apr 2026):** ~$114K/month on options premium alone; ~$60-70K/month net after stock drag.
**Path to target:** Accelerate assigned stock exits (reduces drag) + maintain current premium rate.

```python
from analysis.metrics import monthly_target_tracker
result = monthly_target_tracker(transactions, unrealized_equity_change=-15000)
```

Signal: ON TRACK ≥80% | WATCH 50-79% | BEHIND <50%

---

### Premium Capture Rate
**What:** % of sold premium actually kept = (STO credits − BTC debits) / STO credits.
**Target:** 65-70%. Current YTD: ~59% ($459K of $780K kept).
**Below 60%:** Too many assignments, early closes, or oversized losers.

```python
from analysis.metrics import premium_capture_rate
result = premium_capture_rate(transactions)
```

Signal: GOOD ≥65% | WATCH 55-64% | POOR <55%

---

### Profit Factor
**What:** Gross winning trades / Gross losing trades on closed options.
**Target:** >2.0 (excellent). Winners should be 2x bigger than losers.
**Not the same as win rate** — a 90% win rate with catastrophic losers gives PF < 1.

```python
from analysis.metrics import profit_factor
result = profit_factor(transactions)
```

Signal: EXCELLENT ≥2.0 | GOOD 1.5-2.0 | WATCH 1.0-1.5 | POOR <1.0

---

### Sortino Ratio
**What:** Risk-adjusted return penalizing ONLY downside months (not upside variance).
**Better than Sharpe** for options selling — Sharpe penalizes large winning months.
**Target:** Annualized Sortino >2.0 for an aggressive premium strategy.

```python
from analysis.metrics import sortino_ratio
result = sortino_ratio(monthly_pnl_list)  # list of monthly net P&L in dollars
```

Signal: EXCELLENT ≥2.0 annualized | GOOD 1.0-2.0 | WATCH <1.0

---

### Breakeven Velocity
**What:** Monthly CC premium as % of remaining unrealized loss. Shows recovery speed.
**Fast:** ≤12 months to breakeven. **On Track:** 12-24 months. **SLOW:** 24-36 months.
**Consider Exit:** >36 months — capital works better deployed as new CSPs.

```python
from analysis.metrics import breakeven_velocity
result = breakeven_velocity("PYPL", unrealized_loss=106000, monthly_cc_premium=1800, premium_already_recovered=15000)
```

---

### Cost of Carry
**What:** CC yield on assigned stock vs. what that capital would earn as new CSPs (~2-3%/month).
If CC yield < benchmark: exit is more valuable than wheeling.

```python
from analysis.metrics import cost_of_carry
result = cost_of_carry("PYPL", shares=1000, cost_basis=132, current_price=50, monthly_cc_premium=1800)
```

---

## Models

### VIX Term Structure (vix_regime.py)
**What:** VIX / VIX3M ratio. The single best timing signal for premium sellers.

| Ratio | Regime | Action |
|-------|--------|--------|
| ≥1.15 | Extreme fear / backwardation | Open puts aggressively — premium is at peak richness |
| 1.0–1.15 | Elevated fear | Good entries at IVR ≥ 40 |
| 0.90–1.0 | Neutral contango | Selective — highest conviction only |
| <0.90 | Deep contango | Hold existing; no new short premium |

```python
from models.vix_regime import get_vix_term_structure
vix = get_vix_term_structure()
print(vix["ratio"], vix["signal"], vix["action"])
```

---

### Realized vs. Implied Spread (vix_regime.py)
**What:** IV minus 30-day realized vol. Your fundamental premium-selling edge.
Sell when IV > realized by 4+ points. Do NOT sell when realized > implied.

| Spread (pts) | Signal | Action |
|-------------|--------|--------|
| ≥8 | RICH | Strong entry — you're getting paid well above fair value |
| 4–8 | ELEVATED | Good entry if IVR ≥ 40 |
| 0–4 | FAIR | Selective only |
| <0 | CHEAP | Do NOT sell premium — market moves exceed pricing |

```python
from models.vix_regime import realized_vs_implied_spread
result = realized_vs_implied_spread("AXON")
```

---

### Entry Timing Score (vix_regime.py)
Composite 0-100 score combining VIX term structure + IVR + IV/realized spread.
Score ≥70 = strong entry. 50-69 = acceptable at 50% size. <50 = wait.

```python
from models.vix_regime import entry_timing_score
score = entry_timing_score("UBER", iv_rank=55)
```

---

### Monte Carlo — Assignment Probability (monte_carlo.py)
**What:** Simulates 10K stock price paths (GBM) for all open puts.
Outputs probability that total assigned equity book exceeds the $375K danger zone.

**Use before opening any new put:** If P(exceed $375K) > 30%, throttle new entries.

```python
from models.monte_carlo import simulate_assignment_probability
result = simulate_assignment_probability(open_puts_list)
print(result["p_exceed_danger_zone"], result["action"])
```

| P(exceed danger zone) | Signal | Action |
|-----------------------|--------|--------|
| >40% | THROTTLE | No new puts until book reduces |
| 20-40% | CAUTION | Add selectively; 1 contract max per name |
| <20% | NORMAL | Normal entry pace |

---

### Kelly Criterion — Position Sizing (kelly.py)
**What:** Mathematically optimal fraction of capital to risk per trade.
**Always use half-Kelly** — full Kelly is theoretically correct but too aggressive.

Formula: `Kelly % = PoP − (1−PoP) / (premium / net_loss)`
Practical: `half_kelly_pct × account_size = max dollar risk per trade`

```python
from models.kelly import kelly_position_size
result = kelly_position_size(
    symbol="UBER", pop=0.85, premium_credit=400, strike=68,
    account_size=429659, cc_monthly_premium=150, recovery_months=6
)
print(result.half_kelly_pct, result.max_contracts, result.interpretation)
```

Kelly < 0 = Negative EV — do not trade regardless of gut feeling.

---

### Expected Value Model (ev_model.py)
**What:** EV = PoP × premium − (1−PoP) × (assignment loss − CC recovery).
**Use before any new entry.** If adj_EV < 0, widen strike or skip.

```python
from models.ev_model import trade_ev
result = trade_ev(
    symbol="UBER", pop=0.85, premium_credit=400, strike=68,
    current_price=74.64, cc_monthly_premium=150, recovery_months=6
)
print(result["recovery_adjusted_ev"], result["signal"])
```

EV > 0 → GO. EV < 0 → NO GO — do not let conviction override math.

---

## Weekly Email Dashboard

### Setup
1. Copy `.env.example` to `.env`
2. Fill in `SCHWAB_*` keys
3. Generate Gmail App Password: Google Account → Security → 2-Step Verification → App passwords
4. Add to `.env`: `GMAIL_ADDRESS=ravjdpr@gmail.com` and `GMAIL_APP_PASSWORD=...`

### Run manually
```bash
cd /home/rahulvadera/projects/theta-lab
python3 mcp/routines/weekly_dashboard.py
```

### Skip email (dry run)
```bash
python3 mcp/routines/weekly_dashboard.py --no-email
```

### Schedule (every Monday 7AM)
```bash
bash scripts/setup_cron.sh
```

WSL cron note: WSL does not auto-start cron. Either:
- Add `sudo service cron start` to your WSL startup
- Or run `python3 mcp/routines/weekly_dashboard.py` manually each Monday

### Email sections
1. **Monthly Target** — $100K combined progress bar
2. **VIX Term Structure** — premium environment quality
3. **Portfolio Health** — capture rate, profit factor, assigned book
4. **Monte Carlo** — P(exceed danger zone) with percentile table
5. **Top Actions** — 7 prioritized actions for the week
6. **Breakeven Tracker** — recovery velocity per assigned position
7. **Kelly Candidates** — sized entry candidates for available cash

### What to update weekly (in weekly_dashboard.py)
- `ASSIGNED_POSITIONS` — update `monthly_cc` and `recovered` as CCs execute
- `OPEN_PUTS` — add/remove as positions change (update `dte` each week)
- `ENTRY_CANDIDATES` — adjust strikes and premiums based on current quotes
- `unrealized_equity_change` in `run_weekly_dashboard()` — enter actual week's equity change

---

## Folder Structure

```
mcp/
├── analysis/
│   ├── iv_rank.py      — IV Rank calculation
│   ├── metrics.py      — Dashboard metrics (capture rate, profit factor, sortino, BEV)
│   ├── pnl.py          — Position P&L tracking
│   └── regime.py       — Market regime detection
├── models/
│   ├── ev_model.py     — Expected value per trade
│   ├── kelly.py        — Kelly criterion position sizing
│   ├── monte_carlo.py  — Assignment probability simulation
│   └── vix_regime.py   — VIX term structure + realized vs. implied spread
├── routines/
│   ├── email_report.py    — HTML email builder + Gmail sender
│   └── weekly_dashboard.py — Main orchestrator
└── reports/
    └── weekly_report.py   — Existing Schwab API report generator

logs/                   — Report output (action_report, portfolio reviews, dashboard snapshots)
skills/
├── options_trader.md   — Strategy rules and decision framework
└── quant_analytics.md  — This file — model reference
```
