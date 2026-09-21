# Quarterly Portfolio Direction — US Accounts — Q3 2026 (Aug–Oct)

**Scope: US accounts only** (Account A/B/C, Fidelity x3, Vanguard, Robinhood x2) — the
$1.2M objective, US regime/crash-probability model, and US options-selling strategy
(CSP/covered call/strangle). India (ICICI Direct) is tracked as a fully separate portfolio
with its own market, regime, objective, and strategy shape — see the companion document
`logs/quarterly_portfolio_direction_india_2026-Q3.md`. The two are not blended anywhere in
this document; a candidate or action appearing here is a US-account decision only.

**Generated:** 2026-08-22. **Refreshed 2026-09-18** (Section 1 and 2 below updated
against fresh Sept 18 brokerage exports across Schwab/Fidelity/Vanguard — Robinhood
excluded from this ingest cycle per standing instruction; Sections 3-6 are carried
forward from the Aug-22 version and re-checked for anything materially outdated,
noted inline where it was).

This is the first of what should become a standing quarterly artifact — a forward-looking
3-month direction, not a backward-looking report. Sources: `mcp/analysis/macro_risk_analyzer.py`
(crash probability + sector sensitivity), `mcp/reports/sector_analysis.py` (current exposure),
`scripts/realized_pnl.py` (P&L vs the $1.2M objective), `scripts/strategy_attribution.py`
(YTD strategy performance), `scripts/portfolio1_monthly_review.py` (US candidate pipeline),
plus external research on institutional multi-strategy risk practices (sources at bottom).

---

## 1. Market Direction Call — Next 3 Months

**🔴 Updated 2026-09-18 read: 30-day crash probability 45.9%, risk level RED (2 indicators
critical), primary driver "AD_RATIO critical."** This is a real deterioration from the
Aug-22 read below (28.6%/GREEN) — kept for the record, not overwritten:

> _As of 2026-08-22: 90-day crash probability 28.6%, risk level GREEN, primary driver
> "BREADTH elevated."_

**What actually changed:** AD_RATIO (advance/decline ratio) flipped from the lead signal's
backup to RED/critical at 0.5625 (threshold: 0.8 = alert), and BREADTH itself slid further,
to 48.7% (RED, below the 50% alert line — Aug 22 had it YELLOW/elevated, not yet RED). VIX
term structure, credit spreads (270bps), put/call ratio, and yield curve are all still
GREEN — this is a breadth/participation deterioration specifically, not a broad-based
flight from every signal at once. The model's own 30-day trend line shows this has been
roughly flat over the last two-plus weeks (2026-09-01: 48% → 2026-09-18: 46%), i.e. the
RED reading isn't a sudden spike today, it's a level that's held since before this
document's original Aug-22 draft caught up to it.

**A real internal inconsistency in the model, flagged rather than silently resolved:** at
this same 45.9% 30-day reading, the model's own `action_trigger` text says "🟡 CAUTION:
reduce overbought positions by 20-25%," while its separate Rotation Playbook text says
"🔴 Stage 2-3 Rotation — close 50% of remaining overbought positions, reduce naked call
exposure 30% more, prepare for potential Stage 3 (emergency)." Two different severity
framings from the same model run. Treat the RED risk-level classification and the specific
indicator values (AD_RATIO/BREADTH critical, everything else green) as the reliable part;
treat the prescribed action text as advisory only until this gets reconciled in the model
itself.

**How much to trust this number:** still a single-model, heuristic read of 6 technical/macro
indicators, not a calibrated statistical forecast. 45.9%/RED means "breadth/participation
has meaningfully worsened since Aug 22," not a precise probability of an actual crash.

**Base case for the quarter, updated:** the "coin-flip" framing from Aug 22 has resolved
partway toward the bearish side — breadth has not broadened back out, it's worsened. The
credit side of the book (Tier CR / circular-financing complex, tracked separately in
`logs/circular_financing_playbook.html`) shows the same pattern independently: CoreWeave
-15.4% and Nebius -10.8% over the last 7 days, both now diverging >10 percentage points
from the S&P 500 — a genuine change from earlier in the quarter, when credit spreads were
already stressed (Oracle CDS 145→215bps) but the underlying equities hadn't cracked yet.
No confirmed rating-agency action beyond the known Oracle downgrade, so the Tier CR gate
itself has still not fired — but two independent signals (price-breadth internals, and
credit-adjacent equity underperformance) are now pointing the same direction at the same
time, which wasn't true on Aug 22.

**Sector-level exposure to this specific risk (unchanged in composition):** Technology,
Consumer Cyclical, Communication Services, and Basic Materials remain the sectors most
exposed if the bearish resolution plays out. Utilities, Healthcare, Consumer Defensive,
Energy, and Defense remain comparatively insulated.

---

## 2. Portfolio Current State

**Objective tracking, updated:** $274,245 YTD realized (live, from transactions, as of
2026-09-18) = **22.9% of the $1.2M objective** through ~8.5 months, on pace for ~$366K/year
at the current rate. Real improvement from the Aug-22 read ($210,631 / 17.6% / ~$316K/yr
pace) — the run-rate has picked up, but is still well below the $100K/month target. Still a
volume/capacity problem more than a strategy problem (see §4).

**Account A capacity — worse, not better, and now the single most urgent number in the
whole book:** option requirement **$934,203** against the $700K ceiling this document
originally used — **133.5% margin utilization, EMERGENCY level**, up from 99% on 2026-09-10
and 127.6% on the prior check. This has moved in the wrong direction over the exact window
this document was meant to track. The Active Decision Tracker's `march_strangle_entry_gate`
(BLOCKED — requires margin <85% AND macro risk ≤YELLOW) reflects this; both conditions are
currently failing, and the macro side got worse in the same window (§1).

**Sector concentration — high/low-sensitivity view (all accounts, live 2026-09-18):**

| Bucket | Sectors | Notional | % of ~$7.64M total |
|---|---|---|---|
| 🔴 HIGH exposure (crash-sensitive) | Technology, Communication Services, Consumer Cyclical, Basic Materials | $4,381,110 | 57.3% |
| 🟢 LOW exposure (defensive) | Utilities, Healthcare, Consumer Defensive, Energy, Defense | ~$1,090,000 | 14.3% |
| Everything else (Industrials, Financials, etc.) | not re-broken-out this pass | ~$2,171,750 | ~28.4% (residual) |

_Not a re-run of the full 12-row Aug-22 sector table — that would need `sector_analysis.py`
re-invoked directly, not yet done this pass. The high/low-sensitivity split above is the
more decision-relevant cut anyway (it's what §1's AD_RATIO/breadth risk actually maps to),
and it shows the same story: Technology-led HIGH exposure is now 57.3% of the book, not 36%
— a materially larger share than the Aug-22 snapshot showed under the old 12-sector framing
(which measured Technology alone at 35.9%; the 57.3% here also folds in Communication
Services/Consumer Cyclical/Basic Materials, so the two numbers aren't directly comparable,
but the concentration point stands either way)._

The concentration risk flagged on Aug 22 hasn't been addressed — if anything the picture
is less granular right now, not better. Re-running the full sector breakdown for a clean
apples-to-apples comparison is a real open item, not done in this refresh.

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

**🔴 Status check, 2026-09-18: Month 1's core objective — fix Account A capacity — has not
been achieved and has moved the wrong way.** Option requirement went from $720,280 (Aug 22)
to $934,203 (Sept 18); margin utilization is 133.5%/EMERGENCY, not under the $700K ceiling.
The Active Decision Tracker (`data/active_decisions.yaml`) is now carrying this as a live,
self-checking gate (`march_strangle_entry_gate`) rather than a plan bullet — it re-evaluates
against real position data on every report run instead of waiting for the next quarterly
check-in. Separately, the naked-call cleanup items below (PYPL 12 contracts, CRCL 1
contract) are Account A's own naked-call exposure directly contributing to that capacity
number — closing those is now the same task as "fix capacity," not a separate one.

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
