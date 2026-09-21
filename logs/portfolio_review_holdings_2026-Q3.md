# Holdings Quarterly Review — Q3 2026

_Generated 2026-09-18. Source watchlist: `data/portfolio/Holdings-Portfolio 2026-04-25.xlsx` (11 names) — cross-referenced against live broker position data since the watchlist file itself carries no cost-basis/share data (see Data Quality Notes)._

## Data Quality Notes — read before trusting any number below

_Update 2026-09-18: items 2-4 below were resolved by grepping the raw broker exports/transaction histories directly — see "Corrected 2026-09-18" below each. The root cause of both was the same: the equity totals this review originally pulled from came from `portfolio_equity_positions.yaml`, a hand-maintained fallback file that had drifted out of sync with the real, fresh account exports — not the live position CSVs themselves._

1. **The Holdings-Portfolio.xlsx template is empty of real data.** Its "Holdings" sheet has Shares/Cost/Value columns, but every row is a blank placeholder (`-` or `NaN`) — it was never populated. All Shares/Cost/Value figures in this review come from your actual broker exports instead, not this file. The file is also stale (dated 2026-04-25, ~5 months old) and should be re-populated or retired as the source of truth for this review going forward. **Still open** — see Recommended Follow-ups below.
2. **FMC's live price came back as $0.00** from the pricing pipeline this run — a real data-fetch bug, not a real price. **Corrected 2026-09-18: this is moot — FMC has been fully sold in every account.** See item 3.
3. **FMC's share count — RESOLVED, 2026-09-18: zero shares, fully exited.** The "300 shares" figure was stale/wrong. Direct transaction-history confirmation: Fidelity (Rahul) sold its 200 shares 2026-06-01 ($13.41/sh, $2,681.94 proceeds); Fidelity (Rajul — Roth IRA) sold its 100 shares 2026-06-23 ($11.20/sh, $1,119.97 proceeds); Vanguard (Rahul) sold its 100 shares 2026-06-01 ($13.39/sh, $1,339.33 proceeds). All three accounts exited within the same 3-week window in June. FMC should be dropped from this watchlist entirely — there is no position left to review, and the "verify urgently, may be deeply underwater" flag from the last version of this report was based on the stale figure and can be disregarded.
4. **NKE discrepancy — RESOLVED, 2026-09-18.** Confirmed directly against the raw position files in all 4 accounts that actually hold NKE: Fidelity (Rahul / Traditional IRA) **200 shares** (not 100 — the stale fallback undercounted this lot), Account A (232) 300 shares, Account C (634) 100 shares, Vanguard (Rahul) 100 shares. **Fidelity (Rajul — Roth IRA) holds zero NKE shares** — the "200 shares" the fallback file showed there doesn't exist in that account's real export at all. **True portfolio-wide total: 700 shares** (not the "700 or 800" range previously reported). Full corrected recovery-vs-breakeven table below.
5. **Vanguard's cost basis isn't available from the current export** in the same columnar form as the others, but its own transaction history does show the entry lots directly (e.g., NKE 100sh @ $44.37 = $4,437.00) — added to the table below since it was findable after all, just not in the position-snapshot file.
6. **PYPL: 0 shares currently held anywhere.** Consistent with your standing permanent-exit rule for this name (minimize-loss exit via CC, no re-entry) — already fully executed.

## Per-Name Review

| Symbol | Total Shares (all accounts) | Current Price | Heat | Conv | Thesis Check |
|---|---|---|---|---|---|
| UNH | 100 (Account A) | $373.80 | 🟢 GREEN | 6.2 | Neutral — holding fine |
| AXON | 200 (Account A) | $451.11 | 🟢 GREEN | 7.2 | Oversold/Attractive — thesis intact, strong |
| FMC | **0 — fully exited, June 2026** (see note 3) | $11.32 (verified) | — | — | No longer a position; drop from watchlist |
| NKE | **700 — confirmed** (see note 4) | $36.30 | 🟢 GREEN | 7.3 | Oversold/Attractive — thesis intact |
| ABNB | 100 (Account C) | $165.46 | 🟡 YELLOW | 6.8 | Extended vs. 200-day — verify before adding |
| CRM | 500 (Fidelity Rahul 200, Account A 200, Account B 100) | $239.15 | 🟡 YELLOW | 6.5 | Approaching extremes |
| ADBE | 400 (Account A) | $249.04 | 🟡 YELLOW | 5.8 | Approaching extremes, conviction cooling |
| PYPL | 0 | $52.74 | — | — | Fully exited — permanent-exit rule executed |
| OKTA | 700 (Account A 600, Fidelity Rajul Roth 100) | $182.75 | 🔴 RED | 6.4 | **Overbought/extended, only +1% analyst upside** — weakest thesis in the group |
| TWLO | 324 (Account C) | $240.19 | 🟡 YELLOW | 7.3 | Approaching extremes |
| LYFT | 500 (Fidelity Rahul 100, Account A 400) | $15.23 | 🟡 YELLOW | 7.8 | Approaching extremes, decent conviction |

## Recovery vs. Breakeven — real cost basis confirmed directly against raw broker files

_Updated 2026-09-18: NKE now shown per-lot across all 4 accounts that hold it (previously only the Fidelity Rahul lot was confirmed). ADBE/OKTA are still Fidelity (Rahul) / Traditional IRA only — no discrepancy was found there, not re-checked this pass._

| Symbol | Account | Shares | Cost Basis (total) | Avg Cost/Share | Current Value | Unrealized | % |
|---|---|---|---|---|---|---|---|
| NKE | Fidelity (Rahul) | 200 | $16,436.40 | $82.18 | $7,271.00 | **-$9,165.40** | **-55.8%** |
| NKE | Account A (232) | 300 | $20,260.98 | $67.54 | $10,854.00 | **-$9,406.98** | **-46.4%** |
| NKE | Account C (634) | 100 | $6,480.66 | $64.81 | $3,636.00 | **-$2,844.66** | **-43.9%** |
| NKE | Vanguard (Rahul) | 100 | $4,437.00 | $44.37 | $3,629.50 | **-$807.50** | **-18.2%** |
| **NKE total** | **all 4** | **700** | **$47,615.04** | **$68.02** | **$25,390.50** | **-$22,224.54** | **-46.7%** |
| ADBE | Fidelity (Rahul) | 100 | $47,536.75 | $475.37 | $24,935.00 | **-$22,601.75** | **-47.6%** |
| OKTA | Fidelity (Rahul) | 100 | $13,999.68 | $140.00 | $18,358.60 | **+$4,358.92** | **+31.1%** |

NKE is underwater in every single account that holds it — not an isolated lot, a portfolio-wide -46.7% blended position on $47.6K of cost basis. ADBE is deeply underwater too. OKTA remains the one genuine winner in the account where it's tracked.

**At current wheel/CC pace**, closing the gap on NKE and ADBE through premium collection alone would take a long time — these losses are large relative to typical monthly CC premium on these names. The more relevant question per your own framework ([[Tier Reclassification — By Profitability]]) is whether NKE/ADBE still qualify as Tier 1 (profitable) positions, or whether they've drifted to Tier 2/3 territory where the rule is CSPs only / no scaling, not "sell more premium to average down."

## Q4 2026 Targets & Triggers

- **OKTA** — heat is RED and analyst upside is only +1%. This is the name most likely to need a real exit decision this quarter, not just a hold. Watch for a second consecutive quarter of weak guidance as the trigger to downgrade its tier.
- **NKE** — deeply underwater in all 4 accounts that hold it (-46.7% blended, confirmed 2026-09-18). Trigger for Q4: confirm whether it's still Tier 1 by your profitability rule; if it shows a 3rd consecutive quarter without recovery progress, that's the signal to stop compounding and reassess rather than continue CC-ing through it.
- **ADBE** — deeply underwater (Fidelity Rahul lot). Same trigger as NKE.
- **FMC** — **removed from this watchlist.** Confirmed 2026-09-18: fully exited in all 3 accounts that held it (June 2026). No position, no action.
- **AXON** — thesis strongest in the group (oversold, GREEN, conviction 7.2). No action needed; let it run.
- **ABNB, CRM, TWLO, LYFT** — all YELLOW/approaching-extremes, none flagged for exit. Standard quarterly hold, re-check next cycle.

## Recommended immediate follow-ups

1. ~~Confirm your real FMC position directly with your broker~~ — **done 2026-09-18**: zero shares, fully exited in June. Drop from the watchlist going forward.
2. ~~Reconcile the NKE 100-vs-200-share discrepancy in Fidelity (Rahul)~~ — **done 2026-09-18**: 200 shares confirmed, plus the full 4-account picture (700 total, all underwater).
3. Consider re-populating the Holdings-Portfolio.xlsx template with real cost-basis data, or — better, given what today's check found — retiring both it **and** `portfolio_equity_positions.yaml` as fallback sources in favor of always pulling straight from the live broker exports the way today's correction did. The fallback file is now confirmed to drift out of sync silently (wrong on both FMC and NKE) rather than erroring, which is the more dangerous failure mode.
