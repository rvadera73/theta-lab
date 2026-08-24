# Quarterly Portfolio Direction — US Accounts — Q3 2026 (Aug–Oct)

**Scope: US accounts only** (Account A/B/C, Fidelity x3, Vanguard, Robinhood x2) — the
$1.2M objective, US regime/crash-probability model, and US options-selling strategy
(CSP/covered call/strangle). India (ICICI Direct) is tracked as a fully separate portfolio
with its own market, regime, objective, and strategy shape — see the companion document
`logs/quarterly_portfolio_direction_india_2026-Q3.md`. The two are not blended anywhere in
this document; a candidate or action appearing here is a US-account decision only.

**Generated:** 2026-08-22. Data currency: live regime/crash/sector figures as of today;
P&L figures reflect the most recent brokerage exports (dated 2026-08-14 — re-run
`scripts/update_snapshot.py` after dropping fresher statements to update this
before acting on the P&L numbers specifically).

This is the first of what should become a standing quarterly artifact — a forward-looking
3-month direction, not a backward-looking report. Sources: `mcp/analysis/macro_risk_analyzer.py`
(crash probability + sector sensitivity), `mcp/reports/sector_analysis.py` (current exposure),
`scripts/realized_pnl.py` (P&L vs the $1.2M objective), `scripts/strategy_attribution.py`
(YTD strategy performance), `scripts/portfolio1_monthly_review.py` (US candidate pipeline),
plus external research on institutional multi-strategy risk practices (sources at bottom).

---

## 1. Market Direction Call — Next 3 Months

**Current read: 90-day crash probability 28.6%, risk level GREEN, primary driver "BREADTH elevated."**

This has genuinely improved since the acute reading two weeks ago (AD_RATIO was critical,
90-day probability 72-76%). Breadth (the % of S&P 500 above its 50-day MA) is now the lead
signal, at a YELLOW/elevated level rather than RED — meaning the earlier concern (a narrow
set of leaders propping up the index while most stocks lag) has partially resolved, not
disappeared.

**How much to trust this number:** the crash-probability model was rebuilt this session to
scale continuously with how far an indicator is past its threshold (it used to freeze at a
flat number regardless of severity — confirmed empirically on this same AD_RATIO signal).
It is still a single-model, heuristic read of 6 technical/macro indicators, not a calibrated
statistical forecast — treat 28.6% as "meaningfully lower risk than two weeks ago," not as a
precise probability.

**Base case for the quarter:** continuation of a choppy-but-not-broken bull tape — VIX
contango, credit spreads and put/call ratio both green, yield curve normal. The one real
soft spot is breadth: index-level strength sitting on top of a market where participation is
narrower than the headline suggests. That pattern historically resolves one of two ways —
broadens back out (the bullish resolution) or the leaders roll over and drag the index down
with them (the bearish resolution) — and it's genuinely a coin-flip which one happens first
without a clearer signal.

**Sector-level exposure to this specific risk:** Technology, Consumer Cyclical, Communication
Services, and Basic Materials are the sectors most exposed if the bearish resolution plays
out (concentrated, high-beta, momentum-sensitive names). Utilities, Healthcare, Consumer
Defensive, Energy, and Defense are comparatively insulated.

---

## 2. Portfolio Current State

**Objective tracking:** $210,631 YTD realized (as of the 08-14 statement window) = **17.6%
of the $1.2M objective**, on pace for ~$316K/year at the current rate — well below target,
consistent with every prior check this quarter. This is a volume/capacity problem more than
a strategy problem (see §4).

**Account A capacity — still the binding constraint:** option requirement $720,280 against
your agreed $700K ceiling. Marginally improved from $728,746 two weeks ago, but still over.
This is the single most important number to fix before adding any new exposure anywhere in
that account.

**Sector concentration (real, all accounts):**

| Sector | Notional | Signal | Crash-sensitive? |
|---|---|---|---|
| Technology | $2,262,808 (35.9% of book) | Neutral | 🔴 Yes |
| Industrials | $1,455,706 (23.1%) | Neutral | No |
| Communication Services | $696,537 (11.1%) | 🟢 BUY, rich premium | 🔴 Yes |
| Financial Services | $532,660 (8.5%) | 🔴 REDUCE | No |
| Healthcare | $408,000 (6.5%) | Neutral | No |
| Consumer Cyclical | $404,262 (6.4%) | Neutral | 🔴 Yes |
| Brand-Quality (Non-AI) | $252,732 (4.0%) | Neutral | No |
| Defense | $131,626 (2.1%) | Neutral | No |
| Basic Materials | $81,320 (1.3%) | 🔴 REDUCE | 🔴 Yes |
| Energy | $57,084 (0.9%) | 🔴 REDUCE | No |
| Utilities | $35,660 (0.6%) | Thin premium | No |
| Consumer Defensive | $10,370 (0.2%) | 🟢 BUY, rich premium | No |

Technology at 36% of the book, sitting in the crash-sensitive bucket, remains the single
largest concentration risk — unchanged in character from two weeks ago even as the acute
signal has calmed. Financial Services newly shows REDUCE this cycle (RSI 65.9, wasn't
flagged before) — worth a look, not yet urgent.

---

## 3. Strategy Discipline — What's Actually Working (YTD)

From the full strategy-attribution study this quarter:

- **Short puts are dramatically more capital-efficient than the naked/stagger call legs** —
  26.4% annualized ROI on collateral vs. 1.5% for calls, on the same collateral basis. This
  is the strongest, cleanest finding of the quarter.
- **The strangle structure itself is not broken** — 18 of 27 staggered names net positive
  (AXON +$27,148, ADBE +$15,935, COIN +$9,267, GEV +$8,069 lead), but there is a specific,
  identifiable losing cluster: **OKTA, CRWD, LLY, UNH, MSFT**, net -$28,065 combined. This is
  a name-selection problem within the strangle book, not a structural one.
- **Action for Q3:** stop opening new naked call legs on the 5 losing names specifically
  (short-put-only or defined-risk call spreads there instead); keep running full strangles on
  the proven cluster; redirect incremental capital toward short puts generally given the ROI
  gap.

---

## 4. What Institutional Multi-Strategy Funds Do Differently

Quick research pass this session on how firms like Citadel manage risk at scale — not to
replicate their infrastructure, but to check which principles are cheaply adaptable here.

**Position sizing discipline.** Citadel reportedly caps single-trade exposure at roughly 1%
of portfolio to protect overall performance, and pods that lose substantially see capital
cut or the pod closed outright — risk reduction is automatic and fast, not discretionary
after the fact.[^1] Adaptable version: no single underlying should exceed a fixed % of total
notional (Technology at 36% of your *entire book* is an order of magnitude past anything a
multi-strategy shop would tolerate at the sector level, let alone single-name).

**Progressive risk-budget tightening on drawdown, not a single hard stop.** Multi-manager
risk desks commonly run a soft-stop/hard-stop structure — e.g., at -5% MTD, the risk budget
(VaR limit) drops sharply for the rest of the period; at -10% MTD, it drops to zero for new
risk until the period resets.[^2] Adaptable version: Account A being over its margin ceiling
should trigger a **mechanical size reduction on new entries**, not just a flagged warning —
tie the account's new-entry sizing directly to how far over/under the $700K ceiling it is,
so the constraint is self-enforcing rather than something to remember to check.

**Sector/industry concentration limits are standard practice**, used by roughly 70% of
surveyed hedge funds (excluding dedicated sector funds) specifically to prevent the failure
mode that has historically forced liquidations — LTCM's Russian bond concentration, Marin
Capital's GM debt concentration.[^3] You don't currently have an explicit cap on Technology's
36% share; every other institutional practice found this session assumes one exists.

**Tail-risk hedging as a small, disciplined line item — not a reaction to fear.**
Institutional programs typically spend 50-150bps annually on convex, far-OTM protection,
with pre-committed rules to monetize the hedge in tranches as VIX crosses specific
thresholds — converting a volatility spike into cash for redeployment at depressed prices,
rather than either going fully unhedged or panic-buying protection after a selloff has
already started.[^4] Adaptable version, sized for this book: a small, standing allocation to
far-OTM SPY or QQQ puts (a few basis points of total notional, not a meaningful drag on
premium income) specifically as insurance against the Technology-concentration/breadth-risk
combination flagged in §1-2 — with a pre-set rule for when to take profit on the hedge (e.g.,
VIX crossing 25 or 30) rather than deciding in the moment.

---

## 5. The 3-Month Phased Plan

**Month 1 (August–September): fix capacity, don't add exposure.**
- Reduce Account A's option requirement below $700K before opening anything new there —
  prioritize closing/rolling the highest-margin-consuming, lowest-conviction positions first.
- Stop new naked call entries on OKTA, CRWD, LLY, UNH, MSFT (§3). Existing positions can run
  their course; no new ones.
- No new Technology exposure anywhere in the portfolio — it's already 36% of the book and
  the most crash-sensitive sector; adding here compounds a known concentration, not a fresh
  decision.
- Deploy fresh capital into the verified US candidate already screened: **BROS**
  (~13-22% annualized depending on strike, genuinely oversold).
- Decide on the tail-hedge allocation (§4) — even a small position now costs little given
  where VIX/crash-probability sit, and is far cheaper to put on calm than after a breadth
  breakdown starts.

**Month 2 (September–October): rebalance toward the proven cluster, re-check breadth.**
- Re-run the crash-probability and sector-sensitivity check monthly, not just at
  quarter-start — breadth is the lead signal this quarter and can move faster than a
  90-day view suggests.
- If Account A capacity is fixed, resume strangle deployment on the proven winners
  (AXON/ADBE/COIN/GEV-style names), sized against the 1%-of-book discipline from §4 rather
  than by feel.
- Re-run `scripts/portfolio1_monthly_review.py` fresh — this quarter's candidate (BROS)
  will have moved; don't act on a stale screen into month 2.
- Re-check Financial Services' new REDUCE signal — if it persists two checks running, treat
  it the way Basic Materials/Energy are already being treated.

**Month 3 (October–November): reassess the objective pace and the hedge.**
- At ~17.6% of the $1.2M objective through month 8, hitting the full-year target is already
  off the table; the realistic question for month 3 is what run-rate is achievable for the
  remainder of the year given fixed capacity constraints — revisit the per-account target
  allocation (`mcp/reports/accounts_config.py`) if Account A's true sustainable capacity is
  durably below what the current target assumes.
- Decide whether to monetize the tail hedge (per its pre-set VIX trigger) or roll it forward
  into Q4 — don't let it become a "set and forget, never revisit" position.
- Re-run this whole quarterly process for Q4 — this document should be a recurring artifact,
  not a one-time analysis.

---

## 6. Open Items / Not Yet Built

- The soft-stop/hard-stop margin-based sizing rule (§4) is a real recommendation, not yet
  wired into any report — would need a concrete formula (e.g., new-entry size scales down
  linearly as Account A's margin utilization approaches/exceeds the $700K ceiling).
- No single-name concentration cap currently exists at the position level (only the sector
  view is tracked) — worth adding if any one underlying's notional share becomes large
  enough to matter.
- The tail-hedge idea is a recommendation from research, not a position — needs an explicit
  decision (size, instrument, monetization trigger) before it does anything.

---

**Sources:**
[^1]: [How Multi-Manager Hedge Funds Actually Work Internally](https://youngandcalculated.substack.com/p/how-multi-manager-hedge-funds-actually); [Citadel Hedge Fund Interview Guide](https://www.techinterview.org/companies/citadel-hedge-fund-interview-guide/)
[^2]: [Pod Shop Risk Limits: Drawdown Stop-Outs Explained](https://hedgefundinterview.com/pod-shop-risk-limits)
[^3]: [Risk Practices in Hedge Funds — The Hedge Fund Journal](https://thehedgefundjournal.com/risk-practices-in-hedge-funds/)
[^4]: [Strategic Tail-Risk Hedging: Building Antifragility into Institutional Portfolios — Resonanz Capital](https://resonanzcapital.com/insights/strategic-tail-risk-hedging-building-antifragility-into-institutional-portfolios); [Enhancing global equity returns with trend-following and tail risk hedging overlays](https://www.tandfonline.com/doi/full/10.1080/10293523.2025.2553254)
