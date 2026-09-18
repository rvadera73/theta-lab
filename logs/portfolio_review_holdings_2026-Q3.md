# Holdings Quarterly Review — Q3 2026

_Generated 2026-09-18. Source watchlist: `data/portfolio/Holdings-Portfolio 2026-04-25.xlsx` (11 names) — cross-referenced against live broker position data since the watchlist file itself carries no cost-basis/share data (see Data Quality Notes)._

## Data Quality Notes — read before trusting any number below

1. **The Holdings-Portfolio.xlsx template is empty of real data.** Its "Holdings" sheet has Shares/Cost/Value columns, but every row is a blank placeholder (`-` or `NaN`) — it was never populated. All Shares/Cost/Value figures in this review come from your actual broker exports instead, not this file. The file is also stale (dated 2026-04-25, ~5 months old) and should be re-populated or retired as the source of truth for this review going forward.
2. **FMC's live price came back as $0.00** from the pricing pipeline this run — a real data-fetch bug, not a real price. I verified directly: FMC (NYSE) is still actively trading, **currently ~$11.32**, after a June 2026 capital raise (Tessenderlo Group took a ~20% stake at a $13.30 issue price). Used the verified $11.32 below instead of the broken $0.00.
3. **FMC's share count is unreliable.** The live loader reports 300 shares (100 in Fidelity Rahul, 200 in Fidelity Rajul Roth IRA), but I could not find a current FMC equity row in either account's fresh position file to confirm this directly — the figure may be coming from a stale fallback file rather than today's real export. Confirm your actual FMC position on your broker's site before acting on anything below.
4. **A real discrepancy on NKE:** the live equity summary says Fidelity (Rahul) holds 100 NKE shares, but the raw Fidelity Rahul position file shows 200 shares directly. I don't have a clean explanation for the 100-share gap — flagging rather than guessing. Portfolio-wide NKE could be 700 or 800 shares depending on which is right.
5. **Vanguard's cost basis isn't available from the current export** — it's a transaction/OFX-style file, not a position snapshot with cost-basis columns, so ABNB/CRM/LYFT/NKE recovery-vs-breakeven can't be computed for the Vanguard-held lots specifically.
6. **PYPL: 0 shares currently held anywhere.** Consistent with your standing permanent-exit rule for this name (minimize-loss exit via CC, no re-entry) — already fully executed.

## Per-Name Review

| Symbol | Total Shares (all accounts) | Current Price | Heat | Conv | Thesis Check |
|---|---|---|---|---|---|
| UNH | 100 (Account A) | $373.80 | 🟢 GREEN | 6.2 | Neutral — holding fine |
| AXON | 200 (Account A) | $451.11 | 🟢 GREEN | 7.2 | Oversold/Attractive — thesis intact, strong |
| FMC | ~300 (unverified — see note 3) | $11.32 (verified) | 🟢 GREEN | 5.1 | **Genuinely beaten down** — real fundamental deterioration, not a data artifact |
| NKE | 700 or 800 (see note 4) | $36.36 | 🟢 GREEN | 7.3 | Oversold/Attractive — thesis intact |
| ABNB | 100 (Account C) | $165.46 | 🟡 YELLOW | 6.8 | Extended vs. 200-day — verify before adding |
| CRM | 500 (Fidelity Rahul 200, Account A 200, Account B 100) | $239.15 | 🟡 YELLOW | 6.5 | Approaching extremes |
| ADBE | 400 (Account A) | $249.04 | 🟡 YELLOW | 5.8 | Approaching extremes, conviction cooling |
| PYPL | 0 | $52.74 | — | — | Fully exited — permanent-exit rule executed |
| OKTA | 700 (Account A 600, Fidelity Rajul Roth 100) | $182.75 | 🔴 RED | 6.4 | **Overbought/extended, only +1% analyst upside** — weakest thesis in the group |
| TWLO | 324 (Account C) | $240.19 | 🟡 YELLOW | 7.3 | Approaching extremes |
| LYFT | 500 (Fidelity Rahul 100, Account A 400) | $15.23 | 🟡 YELLOW | 7.8 | Approaching extremes, decent conviction |

## Recovery vs. Breakeven — only where real cost basis is confirmed (Fidelity Rahul / Traditional IRA)

| Symbol | Shares | Cost Basis (total) | Avg Cost/Share | Current Value | Unrealized | % |
|---|---|---|---|---|---|---|
| NKE | 200 | $16,436.40 | $82.18 | $7,271.00 | **-$9,165.40** | **-55.8%** |
| ADBE | 100 | $47,536.75 | $475.37 | $24,935.00 | **-$22,601.75** | **-47.6%** |
| OKTA | 100 | $13,999.68 | $140.00 | $18,358.60 | **+$4,358.92** | **+31.1%** |

These are the only three lots I have real, verified cost-basis data for. NKE and ADBE are both deeply underwater — real, large unrealized losses, not marginal. OKTA is your one genuine winner in this account.

**At current wheel/CC pace**, closing the gap on NKE and ADBE through premium collection alone would take a long time — these losses are large relative to typical monthly CC premium on these names. The more relevant question per your own framework ([[Tier Reclassification — By Profitability]]) is whether NKE/ADBE still qualify as Tier 1 (profitable) positions, or whether they've drifted to Tier 2/3 territory where the rule is CSPs only / no scaling, not "sell more premium to average down."

## Q4 2026 Targets & Triggers

- **OKTA** — heat is RED and analyst upside is only +1%. This is the name most likely to need a real exit decision this quarter, not just a hold. Watch for a second consecutive quarter of weak guidance as the trigger to downgrade its tier.
- **NKE, ADBE** — both deeply underwater in the one account I can verify. Trigger for Q4: confirm whether these are still Tier 1 by your profitability rule; if either shows a 3rd consecutive quarter without recovery progress, that's the signal to stop compounding and reassess rather than continue CC-ing through it.
- **FMC** — re-verify the real position (shares + cost basis) directly on your broker before Q4 starts. Given the real price is $11.32 (not the $14.88 on the stale watchlist, and down further from the $13.30 capital-raise price), if you do hold ~300 shares, this is very likely deeply underwater — worth confirming urgently, not next quarter.
- **AXON** — thesis strongest in the group (oversold, GREEN, conviction 7.2). No action needed; let it run.
- **ABNB, CRM, TWLO, LYFT** — all YELLOW/approaching-extremes, none flagged for exit. Standard quarterly hold, re-check next cycle.

## Recommended immediate follow-ups (not just Q4)

1. Confirm your real FMC position directly with your broker — both the price ($0.00 in my pipeline is definitely wrong) and the share count need verification outside this system.
2. Reconcile the NKE 100-vs-200-share discrepancy in Fidelity (Rahul) before trusting any portfolio-wide NKE total.
3. Consider re-populating the Holdings-Portfolio.xlsx template with real cost-basis data (or retiring it in favor of pulling straight from the live broker exports, the way this review just did) — as it stands, it can't answer the "recovery vs. breakeven" question it exists for.
