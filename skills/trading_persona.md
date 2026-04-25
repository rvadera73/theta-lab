# Trading Persona — Rahul Vadera

**Generated:** 2026-04-25
**Last Updated:** 2026-04-25 (session 2 — trader confirmations incorporated)
**Source:** Schwab brokerage statements (Jan–Mar 2026), 1099 (2025), portfolio watchlists, trader input
**Status:** ACTIVE — use this file as the guardrail for all trade decisions

---

## Account Map

| Account | Holder | Type | Account # | Size (Mar 2026) | Return Target |
|---------|--------|------|-----------|-----------------|---------------|
| Account A | Rahul Vadera | Schwab One® (Margin) | ****-*232 | ~$421K total value | 20% annualized |
| Account B | Pinky Vadera | Contributory IRA | ****-*275 | ~$233K total value | 12% annualized |

**Account B authorization:** Confirmed. Rahul manages Pinky's IRA with full consent.
**Account B options level:** Level 2 confirmed active (CSPs + CCs). No margin, no naked positions.

---

## Trader Profile: Core Principles

1. **Not married to any stock** — positions are vehicles for premium collection, not conviction bets
2. **Goal is to never own stock** — stock ownership is an accident of assignment, not strategic intent
3. **If assigned, use stock as a commodity** — sell CCs immediately, reduce cost basis, exit at first opportunity
4. **Short premium bias only** — sells options exclusively; has never bought options in 5 years
5. **Income-first mindset** — theta decay is the engine; directional bias is input, not thesis
6. **Loss minimization, not stop-loss** — does not use hard stops; manages losses through rolling, time, and premium collection
7. **Macro-regime-driven DTE** — selects expiration based on market environment, not fixed rules

**Classification:** Systematic Short Premium Income Trader | Short Strangle + Wheel Operator

---

## Strategy Architecture (Confirmed by Trader)

### Account A (232 — Rahul, Margin) — Short Strangle Engine
**Key insight confirmed:** Account A is NOT just covered calls. It runs **short strangles** — simultaneously selling both puts AND calls on the same underlying. The naked calls are hedged by the short puts (and vice versa), collecting premium on both sides.

- Where stock is owned: Covered calls against long equity (traditional CC leg)
- Where stock is NOT owned: Naked calls sold alongside cash-secured puts = short strangle
- This explains the $402K unrealized options liability — short strangles on volatile names (AXON, MRNA, APP) with stocks moving significantly
- Margin account enables naked call positions that Account B cannot replicate

**Risk characteristic:** Short strangle exposure means unlimited upside risk on calls AND downside risk on puts. The "hedge" is that premium collected on both sides widens the break-even range.

### Account B (275 — Pinky, IRA) — Pure Wheel
- Sells CSPs only (no naked calls, no margin)
- Accepts assignment when thesis intact; immediately sells CCs to reduce cost basis
- Exits stock position via CC assignment or buyback when profitable
- 12% annualized target is achievable with pure CSP/CC wheel in this account size

---

## Current Market Regime (Trader View — as of Apr 2026)

**Regime:** Bear to Sideways
**Duration:** ~6 months out (through Oct/Nov 2026)
**Implication for new positions:** NO new sell entries until regime shifts to bullish

### Regime-Driven Behavior Rules

| Regime | New Entries | DTE Target | Strategy |
|--------|------------|------------|----------|
| Bear/Sideways (current) | None — reducing existing | N/A | Let time decay work, close profitable positions, roll losers |
| Transition (watch signals) | Selective, small size | 45-90 DTE | Restart with core universe only |
| Bull (2023-2025 style) | Active | 3-12 months | Full strangle + wheel deployment |

**Regime shift signals to watch:**
- VIX sustained below 20 for 10+ days
- S&P 500 reclaims 50-day and 200-day MA on volume
- Put/Call ratio normalizing below 0.8

---

## Open ITM Position Plans (Trader Confirmed)

| Position | Account | Status | Trader Plan |
|----------|---------|--------|-------------|
| MRNA calls ($26/$35) | A (232) | Deep ITM; stock above strikes | Natural exit via CC assignment in 2-3 months. Do not intervene. |
| NVO put ($55) | B (275) | ITM; stock ~$44-55 range | Similar to MRNA — let CC cycle complete the exit naturally |
| CRM put ($220) | B (275) | ITM; stock ~$178 | Conviction: stock returns to $280. Maximize CC premium while waiting. Roll put down if needed. |
| CRWD put ($430) | B (275) | Near ATM | Monitor; standard roll management |
| BA put ($190) | B (275) | Watch stock recovery | Standard wheel management |

**General rule confirmed:** Do NOT force-close losers unless account cash flow is impaired. IRA has no margin = no cash flow pressure. Account A has margin capacity. Roll, wait, collect premium.

---

## DTE Selection Logic (Regime-Driven)

```
IF regime == BEAR_SIDEWAYS:
    new_entries = FALSE
    existing_positions: let run, take profits at 50%+, roll losers to avoid assignment

IF regime == TRANSITIONING:
    new_entries = selective (core 10 universe only)
    dte_target = 45-90 days
    size = 50% of normal

IF regime == BULL:
    new_entries = active
    dte_target = 90-360 days (3-12 months)
    size = full per risk_params.yaml
```

---

## Stop-Loss Protocol (Confirmed)

**Hard automatic stops: NEVER**

The trader has not used a hard stop in 5 years of live trading. Loss management is done through:
- Rolling (extending DTE, adjusting strikes)
- Premium collection on both sides (strangle structure buffers drawdowns)
- Time — "the market always comes back to fair value on quality names"
- Cash flow management (if margin call risk emerges in Account A — only scenario for forced close)

**Skill behavior on losing positions:**
1. Flag any position where mark-to-market loss exceeds 2x premium received
2. Present roll options (same strike + later DTE, or lower/higher strike)
3. Ask trader for decision — NEVER auto-close
4. Exception: If Account A margin utilization exceeds 80%, escalate with urgency

---

## Performance Metrics (2026 YTD through Mar)

| Metric | Account A (232) | Account B (275) |
|--------|-----------------|-----------------|
| YTD Realized Gain (through Feb) | $58,974.91 | — |
| Jan 2026 Net | — | $1,192.10 |
| Mar 2026 Net | — | $4,113.06 |
| Unrealized Options Liability | $(402,318.98) | $(16,587.07) |
| Cash/Sweep Balance | $328,678 (Feb) | $272,932 (Mar) |
| Target annualized | 20% (~$84K/yr) | 12% (~$28K/yr) |

> Note: Account A's $59K in 2 months is ahead of the 20% pace. Current bear regime will slow
> new premium collection — the existing book must carry returns through Oct/Nov.

---

## Active Ticker Universe

### Account A — Core Holdings + Strangle Names
| Ticker | Strategy | Notes |
|--------|----------|-------|
| ADBE | CC + strangle | 4 active call strikes; most sophisticated position |
| AXON | CC + strangle | 3 CC strikes; high IV; deep ITM risk |
| PYPL | CC + strangle | 5 active call positions; most active name |
| OKTA | CC + strangle | 3 strikes laddered |
| CRM | CC + strangle | Long-term bull conviction ($280 target) |
| APP | CC + strangle | High-beta; aggressive |
| MRNA | CC (exiting) | Deep ITM; natural exit in 2-3 months |
| NFLX | CC | 2 contracts |
| NKE | CC | 1 contract |
| LYFT | CC | 4 contracts; recurring |
| JD | CC | 2 contracts |
| INMD | CC | 5 contracts; small-cap |
| ZBH | CC | 1 contract |

### Account B — Active Wheel Universe
| Tier | Tickers | Notes |
|------|---------|-------|
| Core (recurring) | HOOD, TSM, CRWD, GEV, AXON, UBER, BA, FSLR, NVO, CRM | High frequency, multiple rolls seen |
| Active (occasional) | ASTS, RKLB, ALAB, SHOP, ZS, VST, IONQ, ELF, ETSY | Medium frequency |
| Speculative (small size) | QUBT, RGTI, QBTS, ACHR, IBIT, EWZ, EWY | Cap at 10% of account B |

---

## Recommended 10-Stock Core Universe

| Rank | Ticker | Account | Rationale |
|------|--------|---------|-----------|
| 1 | AXON | A | Highest IV, recurring, 3 positions active |
| 2 | PYPL | A | Most active name (5 positions); liquid |
| 3 | CRM | A + B | Both accounts; bull conviction; good premium |
| 4 | ADBE | A | 4-strike sophistication; consistent |
| 5 | HOOD | B | Recurring; high IV; fintech |
| 6 | CRWD | B | Cybersecurity; high IV; recurring |
| 7 | TSM | B | Large premium; semis; multiple rolls |
| 8 | UBER | B | Recurring; mobility; liquid |
| 9 | OKTA | A | 3 CC positions; consistent |
| 10 | GEV | B | Large per-contract premium; industrial AI |

---

## Guardrails for the Skill

```yaml
accounts:
  account_a:
    target_return_annualized: 0.20
    strategy: [covered_call, short_strangle]
    max_contracts_per_ticker: 5
    margin_utilization_alert_pct: 0.80
    stop_loss: flag_and_ask  # Never auto-close

  account_b:
    target_return_annualized: 0.12
    strategy: [cash_secured_put, covered_call]  # Wheel only
    max_contracts_per_ticker: 1
    no_naked_calls: true
    no_margin: true
    speculative_names_max_pct: 0.10
    stop_loss: flag_and_ask  # Never auto-close

regime_gates:
  current_regime: BEAR_SIDEWAYS
  new_entries_allowed: false  # Until Oct/Nov 2026 or regime shift confirmed
  bull_entry_triggers:
    - vix_sustained_below: 20
    - sp500_above_50d_and_200d_ma: true
    - put_call_ratio_below: 0.80

dte_by_regime:
  BEAR_SIDEWAYS: null  # No new entries
  TRANSITIONING: [45, 90]
  BULL: [90, 360]

loss_management:
  hard_stop: false
  flag_threshold: 2.0x_premium_received
  roll_preference: true
  force_close_only_if: margin_utilization_above_80pct

itm_positions:
  MRNA: natural_exit_via_assignment
  NVO: natural_exit_via_assignment
  CRM: hold_and_maximize_cc_premium
  CRWD: standard_roll_management
```
