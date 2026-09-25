# Quarterly Portfolio Direction — US Accounts — Q3 2026 (Aug–Oct)

**Scope: US accounts only** (Account A/B/C, Fidelity x3, Vanguard, Robinhood x2) — the
$1.2M objective, US regime/crash-probability model, and US options-selling strategy
(CSP/covered call/strangle). India (ICICI Direct) is tracked as a fully separate portfolio
with its own market, regime, objective, and strategy shape — see the companion document
`logs/quarterly_portfolio_direction_india_2026-Q3.md`. The two are not blended anywhere in
this document; a candidate or action appearing here is a US-account decision only.

**Generated:** 2026-08-22. **Refreshed 2026-09-18. Refreshed again 2026-09-25**
(Sections 1, 2, and 6 updated against live data and this week's real infrastructure
fixes; Sections 3-4 carried forward unchanged — the strategy-attribution and
institutional-research findings haven't been re-run this pass and nothing below
contradicts them; Section 5's Month 1 status updated to reflect real, partial
progress, not yet complete).

This is the first of what should become a standing quarterly artifact — a forward-looking
3-month direction, not a backward-looking report. Sources: `mcp/analysis/macro_risk_analyzer.py`
(crash probability + sector sensitivity), `mcp/reports/sector_analysis.py` (current exposure),
`scripts/realized_pnl.py` (P&L vs the $1.2M objective), `scripts/strategy_attribution.py`
(YTD strategy performance), `scripts/portfolio1_monthly_review.py` (US candidate pipeline),
plus external research on institutional multi-strategy risk practices (sources at bottom).

---

## 1. Market Direction Call — Next 3 Months

**✅ Updated 2026-09-25 read: 30-day crash probability 15.2%, risk level GREEN, primary
driver "BREADTH elevated" (weak signal, see below).** A real, meaningful improvement from
the 2026-09-18 read:

> _As of 2026-09-18: 30-day crash probability 45.9%, risk level RED (2 indicators
> critical), primary driver "AD_RATIO critical."_
>
> _As of 2026-08-22: 90-day crash probability 28.6%, risk level GREEN, primary driver
> "BREADTH elevated."_

**What actually changed since 09-18:** AD_RATIO, the indicator that had flipped RED/critical
two weeks ago, is no longer the primary driver — the model's 30-day probability dropped from
45.9% to 15.2% and the risk level moved back to GREEN. Breadth is still the named driver, but
now reads as merely "elevated," not critical.

**This is where last week's work actually matters for how much to trust this read:** the
09-18 version of this document flagged a real internal inconsistency in the model (its
`action_trigger` text and its Rotation Playbook text gave two different severity framings
for the same run) and noted the sector-sensitivity map behind "which sectors are exposed"
had never been checked against real data. Both were addressed this week, not just noted —
`mcp/analysis/macro_risk_analyzer.py`'s `SECTOR_SENSITIVITY_MAP` was backtested against 5
years of real sector-ETF forward returns following real historical episodes of each driver
firing. Result: **AD_RATIO and YIELD_CURVE are backed by strong, consistent historical
evidence; BREADTH — today's actual driver — tested as a near statistical wash at the
10-day horizon** (high-sensitivity sectors averaged +0.61% vs. low-sensitivity's +0.57%,
essentially a coin flip). VIX_TERM's direction was found backwards and corrected; HYOAS had
too few real episodes in 5 years to confirm either way. Practical read: **today's GREEN/15.2%
is real, and the specific driver behind it (Breadth) is the weakest-evidenced one in the
whole model** — worth taking the improvement at face value, not worth reading heavy
conviction into it either way.

**Base case for the quarter, updated:** the picture has genuinely improved since 09-18's
scare, back toward (not quite all the way to) the Aug-22 baseline. Tier CR / circular-
financing complex (`logs/circular_financing_playbook.html`) has not been re-checked this
pass — that's a real open item, not folded into this read.

**Sector-level exposure to this specific risk (unchanged in composition, now correctly
computed):** Technology, Consumer Cyclical, Communication Services, and Basic Materials
remain the sectors the model flags as most exposed if breadth deteriorates further —
though per the confidence finding above, that flag currently carries "weak" historical
backing, not "strong." Utilities, Healthcare, Consumer Defensive, Energy, and Defense
remain the comparatively insulated set. (Also fixed this week: Bitcoin miners HUT/RIOT/CIFR
were previously misclassified under "Financial Services" — a real Yahoo Finance taxonomy
quirk, now a distinct "Crypto Mining" sector — and Arista Networks (ANET) was miscategorized
as "Non-AI" when it's one of the more AI-datacenter-levered names in the book; both are now
correctly classified, which changes the composition of the sector table in §2 below, not
just its labels.)

---

## 2. Portfolio Current State

**Objective tracking, updated:** $321,033 YTD realized (live, from transactions, as of
2026-09-25) = **26.8% of the $1.2M objective** through ~9 months. Real, continued
improvement — 22.9% on 09-18, 17.6% on 08-22 — the run-rate keeps picking up, though still
below the $100K/month pace needed to hit the full-year target (see §5's honest read on this).

**Account A capacity — genuinely improved on the metric that matters day-to-day, but the
raw dollar number the trader is exposed to actually grew, not shrank; both facts are real
and worth holding at once:**
- Option requirement is now **$1,019,895** — up from $934,203 on 09-18 and $720,280 on
  08-22. In absolute dollars, the book has gotten *more* exposed, not less.
- Margin utilization reads **113.3%, still OVER CAP** — down from 133.5%/EMERGENCY on 09-18.
  This improvement is *not* because the option requirement shrank; it's because the
  capacity denominator was raised from $700K to $900K on 2026-09-21 after a real
  Schwab Margin Details walk-through confirmed genuine headroom existed (SMA $1.6M,
  Margin Equity $1.0M, $0 debit balance — a different real constraint than a
  traditional debit-balance maintenance call). The $900K ceiling is real and
  trader-confirmed, not a cosmetic change to make the percentage look better — but the
  underlying exposure this document should be tracking is the $1.02M option requirement
  itself, which is still climbing.
- The Active Decision Tracker's `march_strangle_entry_gate` (BLOCKED — requires margin
  <85% AND macro risk ≤YELLOW) is still failing on the margin leg even against the raised
  $900K ceiling (113% > 85%), though the macro leg now passes cleanly (§1: GREEN).

**Sector concentration — high/low-sensitivity view (all accounts, live 2026-09-25, using
this week's corrected sector map):**

| Bucket | Sectors | Notional | % of $8.11M total |
|---|---|---|---|
| 🔴 HIGH exposure (per §1's driver) | Technology, Communication Services, Consumer Cyclical, Basic Materials | $4,477,209 | 55.2% |
| 🟢 LOW exposure (defensive) | Utilities, Healthcare, Consumer Defensive, Energy, Defense | $1,515,894 | 18.7% |
| Everything else (Industrials, Financial Services, Defense, Brand-Quality, Crypto Mining) | not exposure-flagged either way | $2,114,774 | 26.1% |

**Full sector breakdown, real numbers this time (the 09-18 refresh explicitly skipped
re-running this):**

| Sector | Notional | % of book |
|---|---|---|
| Technology | $2,852,461 | 35.2% |
| Industrials | $1,175,632 | 14.5% |
| Communication Services | $1,065,319 | 13.1% |
| Healthcare | $999,910 | 12.3% |
| Financial Services | $696,901 | 8.6% |
| Consumer Cyclical | $452,082 | 5.6% |
| Defense | $368,412 | 4.5% |
| Brand-Quality (Non-AI) | $217,513 | 2.7% |
| Utilities | $123,264 | 1.5% |
| Basic Materials | $107,348 | 1.3% |
| Crypto Mining (new sector, see §1) | $24,728 | 0.3% |
| Energy | $13,509 | 0.2% |
| Consumer Defensive | $10,798 | 0.1% |

Technology alone at 35.2% is essentially unchanged from the Aug-22 baseline (35.9%) — the
concentration flagged at the start of the quarter has neither worsened nor improved; it has
simply persisted through two months of otherwise-active portfolio management. Note
Brand-Quality (Non-AI) is now materially smaller (2.7%, down from whatever it read
pre-correction) since ANET — one of its larger positions — was reclassified to Technology
this week as a real fix, not a reshuffle for its own sake (§1).

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
tie the account's new-entry sizing directly to how far over/under the $900K ceiling it is
(raised from $700K on 2026-09-21 — see §2),
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

**🟡 Status check, 2026-09-25: Month 1's core objective — fix Account A capacity — is
partially, honestly progressed, not achieved.** Option requirement kept climbing in dollar
terms ($720,280 Aug-22 → $934,203 Sep-18 → $1,019,895 today) — the underlying exposure this
plan was meant to bring down has not come down. Margin utilization reads better (113.3%,
down from 133.5%/EMERGENCY) only because the capacity ceiling itself was raised to $900K on
09-21 after a real, trader-confirmed review of actual Schwab headroom — a legitimate
re-basing, not the capacity problem being solved. The gate is still BLOCKED (113% > the 85%
target) even against the new, higher ceiling.

What *has* genuinely progressed this window, separate from the capacity number itself: the
PYPL naked-call tracking bug and the AXON equity-assignment gap (200 real shares from a real
put assignment were invisible to every risk calculation until this week) are both fixed,
which means Account A's naked-call exposure and its real coverage are now correctly measured
for the first time — a precondition for actually fixing capacity with confidence, not the
fix itself. The `march_strangle_entry_gate` in `data/active_decisions.yaml` continues to
self-check against live data on every report run.

**Month 1 (August–September): fix capacity, don't add exposure.**
- Reduce Account A's option requirement below $765K (85% of the current $900K ceiling —
  the gate's real target, updated from the original $700K bullet since the ceiling itself
  was re-based 09-21) before opening anything new there — prioritize closing/rolling the
  highest-margin-consuming, lowest-conviction positions first. Currently $1,019,895 — still
  well above this target even against the higher ceiling.
- Stop new naked call entries on OKTA, CRWD, LLY, UNH, MSFT (§3). Existing positions can run
  their course; no new ones.
- No new Technology exposure anywhere in the portfolio — it's already 36% of the book and
  the most crash-sensitive sector; adding here compounds a known concentration, not a fresh
  decision.
- BROS (screened 08-22) not re-verified this pass — it doesn't appear in this week's live
  priority list below, so treat it as stale until re-screened rather than still-current.
- **Current real, live priority actions (2026-09-25, from the report engine's own gated
  classification — RED-heat/low-conviction for close/trim, top-3 HIGH-conviction GREEN-heat
  for enter, not a separate quarterly screen)**:
  - 🟢 ENTER APP (Communication Services): sell put, 45-60 DTE, delta 0.15-0.20
  - 🟢 ENTER GOOGL (Communication Services): sell put, 45-60 DTE, delta 0.15-0.20 —
    note both new-entry candidates sit in the §1-flagged HIGH-exposure sector; consistent
    with "no new Technology" below only in the narrow sense that neither is literally
    Technology, not in the broader concentration-avoidance spirit of that bullet.
  - 🔴 CLOSE PFE put
  - 🔴 TRIM SONO call
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

**Resolved since the 09-18 refresh (real fixes, not just re-statements):**
- The Section 1 model-inconsistency flag and the never-validated sector-sensitivity map are
  both addressed — backtested against 5 years of real data; results folded into §1 above.
- The PYPL naked-call tracking bug and AXON's missing equity-assignment position (200 real
  shares) are both fixed — naked-vs-covered call counts across the book are now trustworthy
  for the first time this quarter.
- HUT/RIOT/CIFR and ANET's sector misclassifications are fixed — §2's sector table above is
  the first accurate one this quarter.
- This document itself now has an automated staleness/drift check (Action Tracker item
  auto-created if 7+ days pass without a refresh, or if Account A's margin utilization moves
  15+ points between checks) — it still can't write the judgment sections for itself, but it
  no longer goes silently stale without at least a flag.

**Still genuinely open:**
- The soft-stop/hard-stop margin-based sizing rule (§4) is a real recommendation, not yet
  wired into any report — would need a concrete formula (e.g., new-entry size scales down
  linearly as Account A's margin utilization approaches/exceeds the $900K ceiling).
- No single-name concentration cap currently exists at the position level (only the sector
  view is tracked) — worth adding if any one underlying's notional share becomes large
  enough to matter.
- The tail-hedge idea is a recommendation from research, not a position — needs an explicit
  decision (size, instrument, monetization trigger) before it does anything.
- HYOAS's sector-sensitivity direction is still unconfirmed either way — only 4 real
  historical episodes in a 5-year window; would need a lookback through 2008/2020 to get a
  real sample, not attempted this pass.
- Tier CR / circular-financing complex (`logs/circular_financing_playbook.html`) was not
  re-checked this refresh — §1's improved read doesn't account for it either way.

---

**Sources:**
[^1]: [How Multi-Manager Hedge Funds Actually Work Internally](https://youngandcalculated.substack.com/p/how-multi-manager-hedge-funds-actually); [Citadel Hedge Fund Interview Guide](https://www.techinterview.org/companies/citadel-hedge-fund-interview-guide/)
[^2]: [Pod Shop Risk Limits: Drawdown Stop-Outs Explained](https://hedgefundinterview.com/pod-shop-risk-limits)
[^3]: [Risk Practices in Hedge Funds — The Hedge Fund Journal](https://thehedgefundjournal.com/risk-practices-in-hedge-funds/)
[^4]: [Strategic Tail-Risk Hedging: Building Antifragility into Institutional Portfolios — Resonanz Capital](https://resonanzcapital.com/insights/strategic-tail-risk-hedging-building-antifragility-into-institutional-portfolios); [Enhancing global equity returns with trend-following and tail risk hedging overlays](https://www.tandfonline.com/doi/full/10.1080/10293523.2025.2553254)
