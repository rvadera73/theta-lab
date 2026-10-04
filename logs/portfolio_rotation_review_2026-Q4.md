# Portfolio Rotation Review — Q4 2026 (as of 2026-10-03)

Scope: every real option-OPENING transaction across Schwab (A/B/C), Fidelity
(Rahul + both Rajul sub-accounts), and Robinhood transaction histories in the
trailing 90 days (2026-07-05 through 2026-10-03). Vanguard carries no option
activity (equity-only account, per standing scope). Cross-referenced against
current open positions (90 unique tickers, confirmed via the CSV-based
reconciliation pipeline) and each name's live heat/conviction/yield/sector
data from today's report engine.

**This is a candidates list, not an action list.** Every name below gets
checked again as you make progress — nothing here is a standing order.

---

## 1. Trade Frequency — Top 20 Most-Actively-Managed Names (90d)

| Ticker | Opens (90d) | Heat | Conviction | Yield | Vertical(s) |
|---|---|---|---|---|---|
| NKE | 13 | GREEN | 6.4 | 15.1% | Global Brand |
| ALAB | 13 | YELLOW | 7.8 | 45.5% | AI/Pick-and-Shovel |
| CRWD | 12 | RED | 6.0 | 28.5% | AI/Security |
| APP | 11 | GREEN | 8.0 | 33.2% | — |
| ANET | 11 | YELLOW | 8.0 | 22.9% | AI/Data-Center-Infra |
| BE | 10 | YELLOW | 6.4 | 43.5% | — |
| COIN | 10 | YELLOW | 5.5 | 32.4% | Crypto |
| AXON | 10 | YELLOW | 7.2 | 32.7% | Defense/AI |
| OKTA | 9 | RED | 6.4 | 35.2% | AI/Security |
| TSM | 9 | YELLOW | 7.5 | 13.5% | AI/Pick-and-Shovel, Global Brand |
| CRM | 9 | YELLOW | 7.4 | 17.8% | AI/SaaS |
| ONDS | 9 | YELLOW | 8.4 | 57.8% | — |
| EXPE | 8 | YELLOW | 6.8 | 25.0% | — |
| IONQ | 8 | YELLOW | 8.0 | 38.0% | AI/Quantum |
| NVO | 8 | GREEN | 4.7 | 13.1% | GLP-1 |
| SMR | 8 | GREEN | 5.0 | 43.3% | AI/Nuclear-Power |
| MU | 7 | YELLOW | 8.6 | 25.0% | AI/Pick-and-Shovel |
| META | 7 | YELLOW | 6.0 | 15.2% | AI/Hyperscaler |
| LLY | 7 | YELLOW | 8.2 | 13.7% | GLP-1 |
| CRCL | 7 | YELLOW | 5.8 | 39.0% | Crypto |

Every one of the top 20 is currently held — high trade frequency here reflects
active rolling/management of existing positions, not churn into new names.
99 unique tickers saw at least one option open in the window (more than the
90 currently held), meaning some names were fully opened and closed inside
the 90 days: ELF, NBIS, APH, RGTI, TCOM, RKT, SPCX, CMG, DVN, DIS, BRKB,
EWY, XOM, STNE.

---

## 2. Drop / Reduce Candidates (toward a ~5%, 4-5 name quarterly trim)

Ranked by the combination that actually matters — high management frequency
+ weak conviction or real (not covered-call) risk — not heat color alone.
**Note on heat:** RED heat on a fully-covered call (see 2026-10-02's TWLO/SONO
fix) is not itself a problem; the names below are flagged because they carry
real naked/put-side risk or weak conviction on top of the heat, not RED heat
alone.

| Ticker | Why it's a candidate |
|---|---|
| **CRWD** | 2nd-most-traded name in the book (12 opens/90d) — real strangle (1 naked call + 4 short puts, confirmed live), conviction only 6.0 (low end), RED heat. Highest combination of management burden + weakest quality signal in the actively-traded set. |
| **PANW** | RED heat AND the lowest conviction (5.6) of any actively-traded RED name, still being actively traded (5 opens). Classic "churn without edge." |
| **COIN** | 10 opens/90d (6th-most-traded name overall) against conviction of only 5.5 — a lot of management attention for one of the weakest quality scores in the book. |
| **OKTA** | Not a full-name drop — 6 of its calls are fully covered (fine, same logic as TWLO/SONO) — but it carries 3 real, separate short puts (genuine assignment risk) and is actively managed (9 opens, RED heat). **Reduce the put side specifically, keep the covered calls.** |

Also worth a look but weaker case (flagging, not recommending): **NVO** (conviction
4.7, the single lowest in the top 20, though GREEN heat argues the market
disagrees) and **PFE** (lowest yield of any held name at 5.7%, thin premium
for the capital tied up).

---

## 3. Add Candidates (toward a ~5% quarterly addition)

Sourced from the live regime-aware screener (`run_screener`), cross-checked
against the verified holdings list (see Section 4 — the screener's own
"currently held" tag is NOT reliable right now).

**Thematically aligned with existing Hot Trends verticals (AI/Pick-and-Shovel,
AI/Data-Center-Infra) — the stronger fit for "hot trends"-sourced adds:**
- **DELL** — ENTER NOW, RSI 57, IVR 48, AI Infrastructure & Data Center sector. Real flag: LOW_MOAT/THIN_MARGINS (commodity hardware assembler) — size modestly per the screener's own guidance.
- **HPE** — ENTER NOW, RSI 85 (stretched overbought), IVR 72, same sector. Real flag: THIN_MARGINS/LOW_MOAT.

**Real signals, but a different theme (financials/energy, not AI/hot-trend) —
secondary diversification candidates, flagged with their real risk tags:**
- SCHW (RSI 22, oversold, no flags) — the cleanest signal of the group, just not thematically a "hot trend."
- BAC (RSI 16, deeply oversold) — LOW_MOAT flag.
- PBR (RSI 56) — COMMODITY_PRICE_RISK, REGULATORY_RISK, CHINA_EXPOSURE — real, meaningful flags.
- MUFG (RSI 38) — REGULATORY_RISK, LOW_MOAT.

NU was also returned by the screener but is **already held** (5 opens in the
last 90 days, Account B + Fidelity) — see the reliability note below.

---

## 4. Confirmed + fixed bug: live portfolio check was blind to every Schwab holding

While cross-checking Section 3's candidates, `run_screener` tagged both **NU**
and **AXON** as "not currently held." Both are real, currently-held positions
confirmed via the CSV-based reconciliation pipeline (NU: Account B + Fidelity,
5 opens/90d; AXON: Account A, 10 opens/90d, one of the most actively-traded
names in the entire book). 2 of the 8 candidates returned were wrong on this
exact dimension — a 25% error rate in this one sample.

**Root cause (corrected from this report's first draft, which initially
guessed a live Schwab API issue — that was wrong, there is no live API here):**
`mcp/reports/report_utils.py`'s `reconstruct_positions_from_transactions()`
(the file-based function `_load_live_portfolio()` actually calls, NOT a live
API) built `Position`/`OptionLeg` objects with 3 field names that had drifted
from `analysis.pnl`'s real dataclass schema (`cost_basis` instead of
`stock_cost_basis`, a `premium_received` kwarg `Position` never had, `qty`
instead of `quantity`). Every call raised `TypeError`, silently caught by a
bare `except Exception: return None` with zero logging — meaning **every**
Schwab-held position (not just AXON/NU) has been invisible to
`run_screener`/`scan_sector`/`screen_new_entries`'s "already held" check,
likely for a long time, with no visible error anywhere.

**Fixed and verified 2026-10-04** (commit `6e146c6`): `reconstruct_positions_from_transactions("A")`
now returns 53 real positions including AXON, `("B")` returns 19 including NU.
Confirmed live through `run_screener` itself post-restart.

**Still open, lower priority, not yet fixed:** the same live-check path also
depends on `.env` variables for Fidelity/Vanguard/Robinhood that are either
5 months stale (`FIDELITY_CSV_1/2`, `VANGUARD_CSV` all point at
`*May-03-2026*` snapshot files) or blank (`ROBINHOOD_INDIVIDUAL_CSV`,
`ROBINHOOD_IRA_CSV`) — so a Fidelity/Vanguard/Robinhood-only holding can still
show as falsely "not held" by this specific live-check path. Decision pending:
keep those env vars current each reconciliation, or retire this separate
parsing path entirely in favor of reusing `open_positions_loader_v2.py` (the
same pipeline every other tool already trusts).

---

## 5. Multi-factor check: premium + hot-trend/direction + quality + real execution

Sections 1-3 above leaned on technical signals (heat/RSI/conviction, itself
largely RSI-and-trend-range-driven). Trader-directed follow-up: re-evaluate on
premium (yield), hot-trend/direction, business quality (moat), and real
execution (actual recent earnings/guidance track record, not a technical
proxy) — applied here to four specific names.

| | PFE | SONO | PYPL | NKE |
|---|---|---|---|---|
| Yield | 5.7% (thin) | 19.7% (rich) | 15.7% | 15.2% |
| Hot-trend tag | none | none | none | **Global Brand** |
| Quality flag | none | none | **PERMANENT_EXIT** (`config.py` `PERMANENT_EXITS`) | none |
| Position | 10 short puts, 0 calls | 4 covered calls, 0 naked/puts | 11 covered + **1 naked call** + 3 puts | 7 covered calls, 0 naked/puts |
| 90d activity | 2 opens | 0 (untouched) | 2 opens | **13 opens** (most-traded name in the book) |

**Real execution, from actual recent earnings (not a technical proxy):**
- **PFE** — Q3 2025 beat, but revenue -7% YoY as COVID-era products unwind; raised/narrowed full-year EPS guidance, non-COVID portfolio +4%. Core business executing fine; the real gap is thin premium and no trend story to justify a 10-put allocation. [Pfizer Q3 2025 release](https://www.nasdaq.com/press-release/pfizer-reports-solid-third-quarter-2025-results-raises-and-narrows-2025-eps-guidance)
- **SONO** — a genuine, real turnaround: Q4 FY25 revenue +13% YoY (near high end of guidance), EBITDA above midpoint, 12% headcount cut + $60-70M run-rate savings, reduced China production exposure. CEO: "restored the quality of our software." [Sonos FY25 results](https://www.businesswire.com/news/home/20251105034045/en/sonos-reports-fourth-quarter-and-fiscal-2025-results/)
- **PYPL** — Q4 2025 **missed** estimates, weak 2026 guidance, shares -9.6% on the print. Branded-checkout growth decelerated sharply (1% vs 5% prior quarter). Management's own words: "execution has not been where it needs to be" — the board replaced the CEO over it. [PYPL Q4 2025 miss](https://www.nasdaq.com/articles/pypl-falls-96-despite-earnings-growth-stock-hold-or-fold)
- **NKE** — EPS beat by 41%, but flat sales, operating margin compressed to 8.1% from 11.2%, same-store sales -3%. CEO: still in the "middle innings" of an unfinished turnaround. [Nike turnaround status](https://www.barchart.com/story/news/36718028/nke-q4-deep-dive-flat-sales-margin-pressures-and-a-focus-on-turnaround)

**What this changes versus the technical-only list in Section 2:**
- **PYPL is the clearest drop case in the whole book** — stronger than CRWD/PANW/COIN. It reads fine on pure technicals (GREEN heat, decent yield) — exactly the blind spot this exercise was meant to catch. It is already on `config.py`'s `PERMANENT_EXITS` list, carries a real naked call (uncapped risk), and the real-world execution story just got worse, not better — the company's own board replaced its CEO over acknowledged execution failure. **Open question for the trader, not decided here:** a real option-open on PYPL in the last 90 days (adding a premium-maximizing naked call to an already-covered position) directly contradicts the standing `PERMANENT_EXIT` flag. Maximizing premium on a name you're supposedly winding down increases exposure in the wrong direction if the thesis is still intact — either the flag is now stale and should be updated/removed, or the position should actually be heading toward closed, not added to. Needs a decision, not an assumption.
- **SONO upgrades from a neutral WATCH to a real continue/add candidate** — the turnaround has real numbers behind it now, the position is fully covered, and yield is rich. Reinforces the 2026-10-02 suggestion to add a strangle put here.
- **PFE** is not a quality problem, just a weak premium/trend case for its size (10 puts on a thin-yield, no-trend name) — worth trimming the put count, not a full exit.
- **NKE**'s brand/trend case is real, but it is also the single most actively-managed name in the entire book (13 opens across 3 accounts) while its own CEO says the turnaround isn't finished — worth flagging as a concentration/bandwidth question even though the thesis itself isn't broken.

---

## 6. Composite risk-adjusted score model (replaces the staged-gate approach)

Trader pushback on the Section 5 four-stage gate model: it didn't align with
the book's actual objective (risk-adjusted premium income, not equity-quality
investing) and would produce real false positives/negatives — a `LOW_MOAT`
flag shouldn't veto a name the way a "leadership" gate implies, and a
single-day RSI/IVR read is exactly the kind of noisy signal already fixed
once for the macro-risk stage. Rebuilt as a **composite score**, modeled on
how actual quant/multi-strategy shops (Citadel's pod model, factor-investing
funds) rank candidates — score every name on several factors at once, rank,
rebalance on a schedule — rather than gating pass/fail on any single one.

**Scoring formula** (per currently-held ticker):
- **Tail-risk gate (binary, only this disqualifies):** `GOING_CONCERN`,
  `ACCOUNTING_RISK`, `DELISTING_RISK`, `PERMANENT_EXIT` (from `config.py`'s
  `RISK["binary_exit_flags"]` and `PERMANENT_EXITS`) — about capital
  destruction, not business quality.
- **Risk-adjusted premium** = yield × (conviction / 10). Conviction is
  already a smoothed, composite RSI/range/200-day-trend score, not a raw
  single-day technical read — reused deliberately instead of re-introducing
  that noise.
- **Hot-trend/industry bonus**: +3 if the ticker carries a real
  `trend_verticals.py` tag.
- **Crash-risk alignment penalty**: -5 if the ticker's sector is a
  confirmed (`strong`-confidence) high-crash-sensitivity sector AND the
  macro stage is YELLOW/RED. Today's macro sector-sensitivity read is only
  `weak` confidence, so this never fired this run — correctly conservative.
- **Quality-as-sizing**: `LOW_MOAT`/`THIN_MARGINS`/`COMMODITY_PRICE_RISK`/etc.
  reduce a suggested size multiplier (floor 0.5x) and modestly dock score —
  never an exclusion, matching how the live screener already treats these
  flags ("reduce to half-size," not "avoid").

**Global context at run time (2026-10-04):** Regime **BULL**, macro stage
**GREEN** (severity_smoothed 0.86, only a 5-day window so far since the
hysteresis fix started logging) — a supportive backdrop for new entries,
read alongside the sector-sensitivity list (Basic Materials, Communication
Services, Consumer Cyclical, Technology — weak confidence only).

### Tail-risk disqualified — the headline finding

| Ticker | Flags | Yield | Conviction | 90d opens |
|---|---|---|---|---|
| **BE** | `GOING_CONCERN`, `SPECULATIVE_STORY` | **43.9%** | 6.4 | **10** |
| PYPL | `PERMANENT_EXIT` | 15.7% | 5.6 | 2 |

**BE is a bigger, more urgent finding than PYPL.** It is the 6th-most-actively-
traded name in the entire 90-day window, carrying the richest yield of any
name evaluated in this review — exactly the "too-good premium hiding real
risk" trap this model was built to catch. A `GOING_CONCERN` flag means an
auditor-level survival question, not a preference call like `PERMANENT_EXIT`.
This should be looked at before anything else in this report.

### Bottom 10 by composite score (capital-efficiency drop candidates)

LMT, REGN, GOOGL, BA, UNH, WMT, TSLA, JPM, MA, PFE — notably, **none of
Section 2's technical-only picks (CRWD/PANW/COIN/OKTA) appear here.** Their
yields (27-35%) are rich enough to outscore these large, stable, low-premium
names (LMT 7.4%, JPM 6.2%, MA 5.8%) even with mediocre conviction. This list
is driven by capital efficiency — these names tie up capital and attention
for comparatively little premium — not technical weakness, and is the more
objective-aligned answer of the two.

### Top 15 by composite score (where the real income engine of the book lives)

ONDS (58.4% yield), HUT/CIFR (Crypto), AMKR/ALAB/IONQ/LITE (AI/Pick-and-Shovel,
AI/Quantum), ASTS/PL/RKLB (Space), CRWV (AI/Data-Center-Infra), OKLO
(AI/Nuclear-Power), KTOS (Defense/AI), MMYT (Global Brand). Several carry
real quality flags (ALAB, LASR, RKLB) but those only reduced score/sizing,
never excluded — the model working as designed.

**This section supersedes Section 2's drop list** for the purpose of the
~5%/5% quarterly review — Section 2 is left in place above as the "before"
picture so the shift in reasoning stays visible, not because both are still
equally valid.

---

## 7. Is "trim ~5% / add ~5% per quarter" a good discipline?

Short answer: yes as a standing **review** habit, not as a mechanical quota
that must be filled every quarter regardless of what the data says.

**Why it's sound:** a 90-name book is large enough that inertia is a real
risk — a name stays just because closing it was never prioritized, not
because it's still earning its place. A quarterly forced review (not a
forced TRADE) keeps every position periodically re-underwritten, and 4-5
names in/out of 90 is a genuinely manageable cadence, not disruptive
turnover.

**Where to be careful:** don't treat 5%/5% as a target that must be hit.
Today's own exercise is the proof — Section 2 found exactly 4 real drop
candidates this quarter, not because I was filling a quota but because
those 4 are the ones where frequency + weak conviction or real risk actually
line up. A quarter where the book is genuinely healthy should drop fewer
than 5%, not be forced down to make the number. This is the same principle
behind yesterday's TWLO/SONO fix: a name being actively traded or showing
RED heat is not itself a reason to exit — covered-call assignment on an
overbought name is often the intended, profitable outcome, not a problem to
solve. An index can use a mechanical reconstitution quota because its
inclusion criteria are objective; this book already has a continuous,
judgment-driven quality signal (heat/conviction/yield/verticals/qualitative
flags) running every day, and a rigid turnover quota bolted on top risks
fighting that system rather than reinforcing it.

**Recommended framing:** treat 5%/5% as a quarterly **ceiling/budget** to
review against ("look hard for your weakest ~5% and best new ~5%, sized to
keep the book from drifting"), not a floor that must be filled. Keep the
actual trigger evidence-based, exactly as this report did.
