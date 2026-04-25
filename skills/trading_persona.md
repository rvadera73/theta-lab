# Trading Persona — Rahul Vadera

**Generated:** 2026-04-25
**Source:** Schwab brokerage statements (Jan–Mar 2026), 1099 (2025), portfolio watchlists
**Status:** ACTIVE — use this file as the guardrail for all trade decisions

---

## Account Map

| Account | Holder | Type | Account # | Size (Mar 2026) |
|---------|--------|------|-----------|-----------------|
| Account A | Rahul Vadera | Schwab One® (Margin) | ****-*232 | ~$421K total value |
| Account B | Pinky Vadera | Contributory IRA | ****-*275 | ~$233K total value |

> **Important:** Account B (275) is a spouse's IRA. Both accounts are ACTIVELY trading options.
> Account B already has options enabled (Level 2 at minimum: CSPs + CCs confirmed active).
> The pilot focus should confirm authorization to automate on behalf of both account holders.

---

## Trader Profile: Core Principles

1. **Not married to any stock** — positions are vehicles for premium, not conviction bets
2. **Goal is to never own stock** — stock ownership is an accident of assignment, not intent
3. **If assigned, use as commodity** — immediately switch to covered calls, exit at first opportunity
4. **Short premium bias** — sells options, rarely buys; no long options observed in either account
5. **Income-first mindset** — theta decay is the engine; directional view is secondary

**Classification:** Pure Short Premium Income Trader / Systematic Wheel Operator

---

## Strategy Breakdown by Account

### Account A (232 — Rahul, Margin)
**Primary strategy:** Covered Calls on owned equities

- Holds equities, sells calls against them at multiple strikes and expirations
- Ladders strikes aggressively (example: ADBE calls at $300/$320/$330/$370 simultaneously)
- Multiple contracts per underlying (PYPL: 5 active call positions; AXON: 3; OKTA: 3)
- Stocks held: ADBE, APP, AXON, JD, LYFT, MRNA, NFLX, NKE, OKTA, PYPL, CRM, ZBH, INMD
- Prefers tech/growth names with elevated IV
- **Caution flag:** As of Feb 2026, unrealized options liability = $402K against $365K in equities.
  Several calls appear to be deep ITM (MRNA at $26/$35 strike; AXON at $560/$600). This is the
  "commodity stock" principle in action — but requires active management to avoid forced assignment.

### Account B (275 — Pinky, IRA)
**Primary strategy:** Wheel (Cash-Secured Puts → assignment → Covered Calls)

- Sells CSPs on stocks at OTM strikes; accepts assignment when needed
- When assigned, immediately sells CCs to reduce cost basis and exit
- Example cycle observed: LYFT CSP assigned → sold stock + CC assignment → exited Jan 2026
- DVN cycle: held 100 shares → sold CC at $35 → assigned away Mar 2026 (booked $608 loss, premium offset)
- FMC: still held 100 shares as of Mar 2026, selling CCs against it
- Wide universe of CSP tickers (35+ names) — diversified premium collection approach
- Bias toward longer-dated options (6–18 month expirations common)

---

## Active Ticker Universe

### Account A — Covered Call Stocks (confirmed held with active CCs)
| Ticker | Notes |
|--------|-------|
| ADBE | Most active; 4 CC strikes laddered |
| AXON | 3 CC strikes; high IV |
| PYPL | 5 CC positions; aggressive laddering |
| OKTA | 3 CC strikes |
| CRM | 3 CC positions; also in IRA as CSP |
| APP | Active CC; high-beta |
| MRNA | 2 CC positions; very high IV; monitor ITM risk |
| NFLX | 2 contracts CC |
| NKE | CC position |
| LYFT | 4 CC contracts; also appears in IRA |
| JD | 2 contracts CC |
| INMD | 5 contracts CC |
| ZBH | CC position |

### Account B — Active CSP Universe (confirmed trades Jan–Mar 2026)
| Ticker | Category |
|--------|----------|
| HOOD | Fintech; recurring |
| TSM | Semis; large premium, multiple rolls |
| CRWD | Cybersecurity; high IV |
| GEV | Industrials; large notional ($560 strike) |
| ASTS | Space/speculative; high IV |
| RKLB | Space/speculative |
| UBER | Mobility |
| BA | Aerospace; recovery play |
| FSLR | Solar/energy |
| NVO | Healthcare/pharma |
| NBIS | AI infrastructure |
| CCL | Consumer/leisure |
| QUBT / RGTI / QBTS | Quantum computing; small premium, speculative |
| DVN | Energy; assigned → became CC position |
| FMC | Assigned; running CC to exit |
| ACHR / JOBY | eVTOL/aviation; speculative |
| ALAB | Semis/AI |
| ETSY | E-commerce |
| ELF | Consumer beauty |
| SHOP | E-commerce |
| APLD | AI infrastructure |
| IONQ | Quantum computing |
| IBIT | Bitcoin ETF |
| EWZ / EWY | EM ETFs |
| MRK | Pharma |
| ZS | Cybersecurity |
| VST | Utilities/energy |
| LAC | Lithium/mining |
| CAVA | Restaurant/consumer |
| NU | Fintech |

---

## Performance Metrics (2026 YTD through Mar)

| Metric | Account A (232) | Account B (275) |
|--------|-----------------|-----------------|
| YTD Realized Gain (through Feb) | $58,974.91 | — |
| Jan 2026 Net | — | $1,192.10 |
| Mar 2026 Net | — | $4,113.06 |
| Unrealized Options Liability | $(402,318.98) | $(16,587.07) |
| Cash/Sweep Balance | $328,678 (Feb) | $272,932 (Mar) |
| Equity Holdings | $365,518 (Feb) | $1,722 (Mar) |

> Account A's YTD of ~$59K on ~$421K deployed = ~14% annualized pace (Jan-Feb only).
> Account B's $5.3K realized on ~$233K in 3 months = ~9% annualized pace.
> Combined target pace needed: 20% annualized on total deployed capital.

---

## Trading Style Fingerprint

| Dimension | Observed Behavior |
|-----------|-------------------|
| Option type | Short only — puts and calls; no long options seen |
| DTE preference | 1–18 months; mix of near-term (3 mo) and LEAPS-style (12-18 mo) |
| Strike selection | OTM to slight OTM; not deep OTM (premium not worth it) |
| Position sizing | 1–5 contracts per position; Account A more aggressive |
| Rolling behavior | Active roller — closes and re-opens at new strikes/expirations |
| Assignment response | Accepts assignment when thesis intact; sells CC immediately |
| Diversification | Very wide (35+ tickers in B; 13+ in A); low concentration per name |
| Sector bias | Tech, fintech, semis, AI/quantum, energy, pharma |
| Speculative tolerance | High — ASTS, RKLB, QUBT, RGTI, ACHR in IRA |

---

## Risk Flags (Requires Attention)

1. **Account A deep ITM calls** — MRNA ($26/$35 strikes), AXON ($560/$600) — if stocks rallied, these
   are capped gains; if stocks dropped, stock loss with no premium offset. Track delta weekly.

2. **Account B CRWD put at $430** — As of Mar 2026, CRWD at ~$448, put at $430 is near-the-money.
   Mark-to-market loss of $2,895. Monitor for roll or close decision.

3. **Account B CRM put at $220** — $3,453 mark-to-market loss as of Mar. CRM trading ~$178.
   Significantly ITM. Needs roll-down or acceptance of assignment + CC strategy.

4. **Account B NVO put at $55** — NVO trading ~$44 (based on watchlist). Deep ITM. Assignment likely.

5. **No explicit stop-loss protocol observed** — positions are held through significant drawdowns.
   Skill must enforce stop rules the trader currently lacks.

6. **No IV rank filter observed** — trades appear to be placed without systematic IV screening.
   Skill must add IVR gate before entries.

---

## Guardrails for the Skill (Derived from Persona)

```yaml
account_a:
  strategy: covered_call
  max_contracts_per_ticker: 5
  preferred_dte_range: [30, 180]
  roll_trigger: profit_pct >= 0.50 or dte <= 21
  assignment_response: immediate_cc_at_atm_or_otm

account_b:
  strategy: wheel
  max_contracts_per_ticker: 1
  preferred_dte_range: [45, 365]
  iv_rank_minimum: 40
  roll_trigger: profit_pct >= 0.50 or dte <= 21
  assignment_response: immediate_cc_cost_basis_reduction
  speculative_ticker_max_pct: 0.10  # Cap on QUBT/RGTI/ASTS type names

shared_rules:
  never_buy_options: true
  max_position_pct_of_account: 0.05
  earnings_blackout_days: 7
  vix_pause_above: 35
  stop_loss_multiplier: 2.5x  # Close if mark exceeds 2.5x premium received
```

---

## Recommended 10-Stock Core Universe

Based on frequency of appearance, liquidity, and IV characteristics:

| Rank | Ticker | Account | Rationale |
|------|--------|---------|-----------|
| 1 | AXON | A | High IV, recurring, 3 positions active |
| 2 | PYPL | A | Most active (5 positions); liquid; elevated IV |
| 3 | CRM | A + B | Appears in both; large-cap; good premium |
| 4 | ADBE | A | 4-strike ladder; consistent premium |
| 5 | HOOD | B | Recurring; fintech; high IV |
| 6 | CRWD | B | Recurring; cybersecurity; high IV |
| 7 | TSM | B | Large notional; semis; multiple rolls |
| 8 | UBER | B | Recurring; mobility; good premium |
| 9 | OKTA | A | 3 CC positions; consistent |
| 10 | GEV | B | Large premium per contract; industrial AI |

**Satellite universe** (higher-risk, lower allocation): ASTS, RKLB, HOOD, RGTI, IONQ, SHOP

---

## Open Questions for Trader Confirmation

1. **Account 275 authorization** — This is PINKYVADERA's IRA. Confirm you have authority to automate
   trades in this account on her behalf.

2. **ITM position strategy** — MRNA, CRWD, CRM, NVO positions are significantly ITM. What is the
   current exit/roll plan? Do you want the skill to flag these for immediate action?

3. **IV filter** — Do you want to add an IV Rank minimum (e.g., IVR > 40) before the skill suggests
   new entries? You appear to sell in all IV environments currently.

4. **DTE target** — You use a wide range (1 month to 18 months). Should the skill default to a specific
   range (e.g., 45-90 DTE for Account B CSPs)?

5. **Stop loss** — No stop protocol observed. Confirm: should the skill enforce a 2x premium stop,
   or do you prefer to roll rather than close at a loss?
