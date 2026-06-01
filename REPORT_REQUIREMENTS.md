# Unified Master Report — Implementation Summary & Future Requirements

## What Was Fixed (May 31, 2026)

### 1. **All 8 Accounts Now Visible in Reports**
- **Before:** Only Account A (232) and Account B (275) shown in detail  
- **After:** All 8 accounts now appear in SECTION 0 with balance, % of total, position count, notional exposure, and monthly target

Accounts included:
- Account A (232) — Rahul Margin, $2,732,234 (60%)
- Account B (275) — Pinky IRA, $320,000 (7%)
- Account C (634) — Designated Beneficiary, $267,289 (5.9%)
- Fidelity (Rahul) — $512,000 (11.2%)
- Fidelity (Rajul — Roth IRA) — $43,000 (0.9%)
- Fidelity (Rajul — Rollover IRA) — $129,000 (2.8%)
- Vanguard (Rahul) — $325,000 (7.1%)
- Robinhood (Individual) — $13,000 (0.3%)
- Robinhood (Traditional IRA) — $212,000 (4.7%)

### 2. **Live Data Instead of Hardcoded Values**

#### Monthly Report (Section 1: Actual vs Target)
- Now reads `ytd_net_options_income` and `month_to_date_premium` from `portfolio_snapshot.yaml`
- Automatically calculates variance and % variance based on live snapshot data
- No more hardcoded "$58,400" or "$112,100" figures

#### Biweekly Report (Section 1: YTD Pace)
- Now reads from snapshot instead of hardcoded May 15 snapshot
- Automatically calculates MTD averages, days remaining, projected month-end
- Works for any month, not just May

#### Monthly Report (Section 2: Account Performance)
- Now loops through all 8 accounts (instead of just A, B, C)
- Allocates YTD premium proportionally by account balance
- Calculates individual account targets and variances

### 3. **Robinhood Files Now Auto-Detected**
- **Before:** Hardcoded filenames `Robinhood_Account1_20260511.csv` and `Robinhood_Account2_20260511.csv`
- **After:** Glob patterns that pick the latest files automatically
  - `Robinhood_Account1_*.csv` → picks latest (e.g., May 31 version)
  - `Robinhood_Account2_*.csv` → picks latest

## How to Run the Reports (Going Forward)

```bash
cd /home/rahulvadera/projects/theta-lab
python3 mcp/reports/unified_master_report_production.py
```

Generates 4 files in `logs/`:
- `unified_master_report_YYYY-MM-DD_daily_production.txt`
- `unified_master_report_YYYY-MM-DD_weekly_production.txt`
- `unified_master_report_YYYY-MM-DD_biweekly_production.txt`
- `unified_master_report_YYYY-MM-DD_monthly_production.txt`

## What Information Is Required to Run Reports (Ongoing)

### 1. **Transaction CSV Files** (Already In Place)
Location: `/home/rahulvadera/projects/theta-lab/data/positions/`

Required files for each account:
- **Schwab (3 accounts):** Latest `*_Transactions_*.csv` files
  - `Individual_XXX232_Transactions_*.csv` (Account A)
  - `Contributory_XXX275_Transactions_*.csv` (Account B)
  - `Designated_Bene_Individual_XXX634_Transactions_*.csv` (Account C)
- **Fidelity (2 accounts):** Latest files matching patterns
  - `*Rahul*Fidelity*.csv` (Fidelity Rahul)
  - `*Rajul*Fidelity*.csv` (Fidelity Rajul)
- **Vanguard (1 account):** Latest file matching pattern
  - `*Vanguard*.csv` (Vanguard Rahul)
- **Robinhood (2 accounts):** Latest files matching patterns
  - `Robinhood_Account1_*.csv` (Traditional IRA)
  - `Robinhood_Account2_*.csv` (Individual)

**Action:** Export transaction history from each broker whenever you want to update the reports. The script will automatically pick the latest file.

### 2. **Portfolio Snapshot YAML File** ✅ (Now Live)
Location: `/home/rahulvadera/projects/theta-lab/data/portfolio_snapshot.yaml`

Required fields (used by reports):
```yaml
last_updated: "2026-05-30"
ytd_net_options_income: 292421          # Jan 1 to today
month_to_date_premium: 84215            # 1st of month to today
assigned_equity_book_value: 0
open_puts: [...]                        # Array of open put positions
```

**Action:** Update this file weekly with:
- `ytd_net_options_income` — cumulative premium from Jan 1 to today
- `month_to_date_premium` — cumulative premium from 1st of month to today
- `last_updated` — today's date

### 3. **Account Configuration** ✅ (Hardcoded, Update as Needed)
Location: `mcp/reports/unified_master_report_production.py` (lines 35-47)

Currently configured as:
```python
ACCOUNTS_CONFIG = {
    'Account A (232)': {'balance': 2732234, 'margin': True, 'monthly_target': 60000},
    'Account B (275)': {'balance': 320000, 'margin': False, 'monthly_target': 7040},
    'Account C (634)': {'balance': 267289, 'margin': False, 'monthly_target': 5880},
    ...
}
```

**Action:** Update account balances and monthly targets when accounts are funded/unfunded or targets change. This controls:
- Portfolio % calculations in Section 0
- Per-account monthly target allocation in monthly report Section 2

### 4. **Framework Modules** ✅ (Auto-Loaded, No Action)
These are loaded automatically and generate conviction, heat, RSI, etc. from Yahoo Finance:
- `enhanced_metrics.py` — conviction from technical indicators (RSI, MACD, BB, 52W range)
- `iv_rank.py` — IVR gate for new entries
- `sector_analysis.py` — sector rotation breakdown
- `regime.py` — market regime detection (BULL, SIDEWAYS, BEAR, etc.)

## The 4 Report Types — What They Show

### Daily Report
- **Section 0:** Account health & margin status (all 8 accounts)
- **Section 1:** System status (position count, ticker count, account count)
- **Section 2:** Conviction updates by bucket (HIGH/MODERATE/LOW)
- **Section 3:** Heat distribution (GREEN/YELLOW/RED)
- **Section 4:** Market regime analysis
- **Section 4.5:** Sector analysis & rotation
- **Section 5:** Position distribution by account
- **Section 6:** Top 20 positions by open contracts
- **Section 7:** OODA framework (Observe-Orient-Decide-Act)

### Weekly Report
- **Section 0:** Account health & margin status
- **Section 1:** Market regime forecast
- **Section 2:** Weekly action priorities
- **Section 3:** Top-5 action items
- **Section 4:** Position heat by account
- **Section 5:** IV Rank & entry gate
- **Section 6:** Cash & margin forecast
- **Section 7:** Theta & P&L tracking
- **Section 8:** Risk & guardrails weekly check
- **Section 9:** Decision tree (end-of-week conditions)
- **Section 10:** Framework status & automation

### Biweekly Report (Mid-Month Checkpoint)
- **Section 0:** Account health & margin status
- **Section 1:** YTD Pace & monthly target tracking *(NOW READS FROM SNAPSHOT)*
- **Section 2:** Three-month conviction trend
- **Section 3:** Three-month tier distribution evolution
- **Section 4:** Three-month win rate trend
- **Section 5:** Three-month Greeks drift & risk management
- **Section 6:** Three-month sector rotation trend
- **Section 7:** Monthly variance root cause analysis

### Monthly Report
- **Section 0:** Account health & margin status
- **Section 1:** Actual vs Target variance analysis *(NOW READS FROM SNAPSHOT)*
- **Section 2:** Performance by account (all 8, proportionally allocated) *(NOW DYNAMIC)*
- **Section 3:** Variance root cause analysis
- **Section 4:** Moat recalibration & tier assignments
- **Section 5:** Citadel comparison & framework evolution

## Key Data Flow

```
Transaction CSV Files (8 brokers)
    ↓
OpenPositionsLoaderV2
    ├─ Auto-picks latest files via glob patterns
    ├─ Nets STO minus BTC to get true open positions
    ├─ Extracts tickers via broker-specific logic
    └─ Returns open_positions DataFrame + prices dict
    ↓
Yahoo Finance (Live)
    ├─ batch_get_metrics() → Conviction from RSI/MACD/BB/52W
    ├─ batch_iv_rank() → IVR gate for entries
    └─ batch_get_sector_analysis() → Sector rotation
    ↓
Portfolio Snapshot YAML (Manual Update)
    ├─ ytd_net_options_income
    ├─ month_to_date_premium
    └─ (used for YTD/MTD report sections)
    ↓
UnifiedReportProduction
    ├─ generate_daily_report()
    ├─ generate_weekly_report()
    ├─ generate_biweekly_report()
    └─ generate_monthly_report()
    ↓
4 Report Files (logs/)
```

## What Happens If Data Is Missing

| Data Missing | Impact | Workaround |
|---|---|---|
| Transaction CSV file not updated | Old positions still shown | Export new CSV from broker |
| Robinhood CSV filename changed | Account not loaded | Rename to match glob pattern `Robinhood_Account*_*.csv` |
| `portfolio_snapshot.yaml` not updated | YTD/MTD sections use old data | Update YAML with latest figures |
| Account balance in ACCOUNTS_CONFIG wrong | % of total portfolio incorrect | Update balance in script (lines 35-47) |
| Snapshot missing fields | Report sections may error | Ensure YAML has all required fields (see above) |

## Monthly Update Checklist

**By 1st of following month (to generate accurate reports):**

- [ ] Export transaction history from all 8 brokers into `data/positions/`
- [ ] Update `portfolio_snapshot.yaml`:
  - [ ] `last_updated: YYYY-MM-DD` (today's date)
  - [ ] `ytd_net_options_income: <sum of all net premium Jan 1 to yesterday>`
  - [ ] `month_to_date_premium: <sum of net premium from 1st of previous month to yesterday>`
- [ ] Run `python3 mcp/reports/unified_master_report_production.py`
- [ ] Check output files in `logs/` for all 4 report types
- [ ] Verify Section 0 shows all 8 accounts with correct position counts
- [ ] Verify monthly Section 2 shows proportional targets for all 8 accounts

## Integration with Skill (options-trader)

The `/options-trader` skill can invoke these reports on demand via the MCP server:

```python
generate_unified_master_report(report_type="DAILY|WEEKLY|BIWEEKLY|MONTHLY")
```

The skill will:
1. Call the report generator
2. Read the generated `.txt` file from `logs/`
3. Present it to the user with context

No additional setup needed — the data flow above handles everything.
