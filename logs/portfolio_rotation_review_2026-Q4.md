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

## 4. Confirmed bug, separate from today's earlier MCP fixes: live portfolio check is unreliable

While cross-checking Section 3's candidates, `run_screener` tagged both **NU**
and **AXON** as "not currently held." Both are real, currently-held positions
confirmed via the CSV-based reconciliation pipeline (NU: Account B + Fidelity,
5 opens/90d; AXON: Account A, 10 opens/90d, one of the most actively-traded
names in the entire book). 2 of the 8 candidates returned were wrong on this
exact dimension — a 25% error rate in this one sample.

Root cause (confirmed via `mcp/server.py`'s `_load_live_portfolio()`): the
screener/`scan_sector`/`screen_new_entries` tools build their "currently held"
set from a **live Schwab API call** (`_load_positions_all`, wraps
open-stocks-mcp), completely separate from the CSV-reconciliation pipeline
every other report/dashboard tool in this project uses. That live path is
disagreeing with reality for at least these two Schwab-account names. This is
a real, separate issue from today's two earlier MCP fixes (the startup crash
and the `scan_roll_candidates` div-by-zero) — worth its own investigation
(likely a stale/expired Schwab API token or an account-filter gap in
`_load_positions_all`), not fixed in this pass. Until resolved, don't trust
"not currently held" from `run_screener`/`scan_sector`/`screen_new_entries`
without cross-checking against the real holdings list the way this report did.

---

## 5. Is "trim ~5% / add ~5% per quarter" a good discipline?

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
