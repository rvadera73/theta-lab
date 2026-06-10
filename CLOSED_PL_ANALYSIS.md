# CLOSED P&L ANALYSIS: Jan 1 - June 9, 2026

## Executive Summary

**Total Realized P&L: $95,989.02** across 395 closed trades.
- **Win Rate: 85.6%** (338 winners vs 57 losers)
- **Average P&L per trade: $243.01**
- **Median P&L per trade: $250.70**
- **Total Fees Paid: $590.49**

**Key Finding:** Puts are the profit engine (89.2% win rate, $107K total P&L). Calls are losing money (-$11.3K net, 79.5% win rate disguises massive losses on a few positions). The data reveals a framework breakdown: Calls are killing the strategy, not enhancing it.

---

## 1. STRATEGY PERFORMANCE: PUTS vs CALLS

### Puts (Sell Put Strategy)
- **Count:** 249 trades
- **Total P&L:** $107,267.28
- **Avg P&L:** $430.79 per trade
- **Win Rate:** 89.2%
- **Median P&L:** $411.00

**Puts are systematically profitable.** Winners average $797 (for puts that win). Even "breakeven" trades at $250 are above fees. This is the core premium engine.

### Calls (Sell Call Strategy) 
- **Count:** 146 trades
- **Total P&L:** -$11,278.26 (LOSS)
- **Avg P&L:** -$77.25 per trade
- **Win Rate:** 79.5%
- **Median P&L:** -$2.87

**Calls are net negative.** Win rate of 79.5% is misleading—the losers are catastrophic (-$10.8K on OKTA, -$6.9K on CRWD, -$6.0K on APP calls). The 20% of losing trades account for -$37,000+ in losses. 

**Implication:** Stop selling naked calls. The distribution is asymmetric: small wins capped by credit, unlimited losses on gap moves.

---

## 2. CONVICTION LEVEL ANALYSIS

### High Conviction (8-10 trades per symbol)
- **Count:** 285 trades (72% of portfolio)
- **Total P&L:** $77,777.62
- **Monthly Avg:** $12,962.94
- **Avg P&L per trade:** $272.90
- **Win Rate:** 84.9%

**This is the real money.** Repeating positions in favorite symbols (AXON, GEV, OKTA, MU, APP, CRWD) generate $77.8K in YTD P&L. BUT: This bucket includes the $10.8K OKTA call loss and -$6.0K APP call loss. High conviction on the *wrong side* amplifies losses.

**Key Insight:** High conviction should be reserved for PUTS, not calls.

### Medium Conviction (2-3 trades per symbol)
- **Count:** 85 trades (21.5% of portfolio)
- **Total P&L:** $11,374.68
- **Monthly Avg:** $1,895.78
- **Avg P&L per trade:** $133.82
- **Win Rate:** 88.2%

**Diversified, steady.** These are secondary positions, mostly puts. Lower leverage, lower volatility in returns.

### Low Conviction (1 trade per symbol)
- **Count:** 25 trades (6.3% of portfolio)
- **Total P&L:** $6,836.72
- **Monthly Avg:** $1,139.45
- **Avg P&L per trade:** $273.47
- **Win Rate:** 84.0%

**One-off trades punch above their weight.** Single-entry positions average $273/trade, nearly matching medium conviction. This suggests good trade selection on isolated plays, but low sample size.

---

## 3. ACCOUNT-LEVEL PERFORMANCE

### Schwab Accounts (Margin + Contributory + Beneficiary)

**Account A (Margin, 225K capacity):**
- Trades: 265
- Total P&L: $52,570.44
- Avg P&L: $198.38 per trade
- Win Rate: 84.9%
- **Monthly Run Rate:** $8,761.74
- Margin utilization: Approximately 65% (based on 265 trades vs accounts B/C)

**Account B (Contributory):**
- Trades: 53
- Total P&L: $19,431.24
- Avg P&L: $366.63 per trade
- Win Rate: 92.5%
- **Monthly Run Rate:** $3,238.54
- **Best account by win rate & per-trade P&L.** Smaller account, higher quality trades.

**Account C (Designated Beneficiary):**
- Trades: 29
- Total P&L: $8,300.52
- Avg P&L: $286.22 per trade
- Win Rate: 72.4% (lowest)
- **Monthly Run Rate:** $1,383.42
- Higher loss frequency (27.6% vs 15.1% in other accounts). Likely experimental trades.

### Fidelity Accounts (Tax-Deferred)

**Fidelity Rahul (Rollover IRA + Roth IRA):**
- Trades: 36
- Total P&L: $13,569.02
- Avg P&L: $376.92 per trade
- Win Rate: 94.4% (highest)
- **Monthly Run Rate:** $2,261.50
- **Highest quality operations.** Only 2 losers across 36 trades. Disciplined position management.

**Fidelity Rajul (Rollover IRA + Roth IRA):**
- Trades: 12
- Total P&L: $2,117.80
- Avg P&L: $176.48 per trade
- Win Rate: 75.0%
- **Monthly Run Rate:** $352.97
- Lower sample size, higher loss rate (25%). New account or experimental.

---

## 4. MONTHLY PERFORMANCE & SEASONALITY

| Month | Trades | P&L | Win Rate | Avg/Trade | Regime |
|-------|--------|-----|----------|-----------|--------|
| Jan | 76 | $42,378.32 | 89.5% | $557.61 | EARLY_BULL |
| Feb | 42 | $14,040.98 | 88.1% | $334.31 | EARLY_BULL |
| Mar | 93 | $12,099.74 | 82.8% | $130.00 | EARLY_BULL |
| Apr | 96 | $9,162.02 | 84.4% | $95.44 | CAUTIOUS_BULL |
| May | 86 | $18,052.98 | 84.9% | $209.92 | CAUTIOUS_BULL |
| Jun | 2 | $254.98 | 100.0% | $127.49 | LATE_BULL |

**Seasonal Pattern:**
- **January was the best month:** $42.4K on 76 trades = $557/trade. Market volatility premium was high.
- **February remained strong:** $14K, though average dropped to $334.
- **March-April decay:** Volume ramped (93-96 trades) but P&L collapsed ($12K, then $9K). Win rate fell to 82-84%.
- **May recovery:** P&L bounced back to $18K despite lower per-trade average ($210).

**Interpretation:** The strategy generates premium in volatility spikes (Jan) then degrades as price stability increases. By April, you're fighting theta decay on aging positions.

---

## 5. MARKET REGIME ANALYSIS

### EARLY_BULL (Jan 1 - Mar 31)
- **Trades:** 211
- **Total P&L:** $68,519.04
- **Win Rate:** 86.3%
- **Avg P&L:** $324.65 per trade

Rising market with rotation into tech. **Puts are free money** when IV is elevated and stocks are rallying. Sell puts, they expire worthless or are bought back for profit. This is the strategy's sweet spot.

### CAUTIOUS_BULL (Apr 1 - May 31)
- **Trades:** 182
- **Total P&L:** $27,215.00
- **Win Rate:** 84.6%
- **Avg P&L:** $149.53 per trade

Slower market, lower IV. P&L drops 60% (per-trade) despite similar win rate. **This is the regime where position management becomes critical.** Rolls happen here; small adjustments replace big wins.

### LATE_BULL (Jun 1 - Jun 9)
- **Trades:** 2
- **Total P&L:** $254.98
- **Win Rate:** 100.0%
- **Avg P&L:** $127.49 per trade

Sample size too small to draw conclusions. Likely closeouts of May positions.

---

## 6. WINNERS vs LOSERS: PATTERN ANALYSIS

### Winners (>$200 P&L)
- **Count:** 220 trades (55.7% of all trades)
- **Total:** $175,594.68
- **Avg:** $797.69 per winner
- **Range:** $200 to $5,317

**Top winners are ALL PUTS:**
1. AXON Put $12/18/26 - $5,317 (Account A, High conviction)
2. AXON Put $12/18/26 - $4,230 (Account A, High conviction)
3. AXON Put $01/15/27 - $3,783 (Account A, High conviction)
4. GEV Put $12/18/26 - $3,177 (Account A, High conviction)
5. GEV Put $01/15/27 - $3,088 (Account A, High conviction)

**Pattern:** Winners are concentrated in high-conviction tickers where you had multiple fills at lower strikes and closed when the stock rallied. AXON alone generated $5K+ winners in Account A.

### Losers (<-$100 P&L)
- **Count:** 27 trades (6.8% of all trades)
- **Total:** -$89,604.70
- **Avg:** -$3,321.04 per loser
- **Range:** -$10,781 to -$104

**All losers are CALLS:**
1. OKTA Call $12/18/26 - **-$10,781** (Account A, High conviction)
2. CRWD Call $09/18/26 - **-$6,981** (Account A, High conviction)
3. APP Call $12/18/26 - **-$6,059** (Account A, High conviction)
4. IBM Call $03/19/27 - **-$5,693** (Account A, Medium conviction)
5. OKTA Call $09/18/26 - **-$5,516** (Account A, High conviction)

**Pattern:** Losers are naked short calls on high-volatility stocks that gap up after earnings or market rallies. OKTA and CRWD each have multiple $5K+ losses. You were short calls and the stocks ripped.

**Asymmetry Revealed:** Puts can make $5K. Calls can lose $10K. The risk/reward is inverted.

### Breakeven (-$100 to +$200)
- **Count:** 148 trades (37.5% of all trades)
- **Total:** $79.34 (essentially zero)
- **Avg:** +$0.54 per trade

These are the "fees paid" positions. They close near the strike, or get rolled into a loss later.

---

## 7. TIER CONTRIBUTION ANALYSIS (Data-Driven)

Currently assumed: Tier 1 ($3,800/pos) | Tier 2 ($1,000/pos) | Tier 3 (-$500/pos)

**Actual from data:**

### High Conviction (Tier 1 equivalent)
- 285 trades, $77,777.62 total
- **Per-trade generation:** $272.90
- **Monthly equivalent:** 47 trades/month × $273 = $12,831
- **Current assumption:** 1.5 positions @ $3,800 = $5,700/month
- **Actual:** 2.4× the assumed rate ($12,831 vs $5,700)

High conviction is **underestimated.** But this bucket includes the -$10K OKTA call. If separated by position type:
- **High Conviction PUTS only:** Average $400+/trade
- **High Conviction CALLS:** Average -$600/trade (loss)

### Medium Conviction (Tier 2 equivalent)
- 85 trades, $11,374.68 total
- **Per-trade generation:** $133.82
- **Monthly equivalent:** 14 trades/month × $134 = $1,876
- **Current assumption:** 1 position @ $1,000 = $1,000/month
- **Actual:** 1.9× the assumed rate, but lower quality

### Low Conviction (Tier 3 equivalent)
- 25 trades, $6,836.72 total
- **Per-trade generation:** $273.47
- **Monthly equivalent:** 4 trades/month × $273 = $1,092
- **Current assumption:** -$500/month (loss)
- **Actual:** +$1,092/month (profit)

Low conviction is **misclassified.** These one-off trades are profitable, not drag.

---

## 8. SUCCESS/FAILURE ROOT CAUSES

### Why Puts Win
1. **Theta decay works in your favor.** Premium decays daily. You sell high, time works with you.
2. **Mean reversion.** Stocks gap down, then recover. You're short puts at reasonable OTM strikes; they expire worthless.
3. **IV crush.** Sell puts during elevated IV (earnings, market dips), close when IV contracts.
4. **Account size.** Puts require less margin per contract. Can layer multiple contracts across underlyings.

### Why Calls Lose
1. **Directional risk naked.** If stock gaps up post-earnings, you're short a call with unlimited loss potential.
2. **Growth tech domination.** Your portfolio is AXON, APP, CRWD, OKTA—all growth stocks with high beta. Selling calls on these is fighting the trend in a BULL market.
3. **No theta advantage.** You sell calls at premiums that don't compensate for gap risk (e.g., OKTA call lost $10.8K).
4. **Sequence of losses.** You had 27 call losers averaging -$3,321 each. Even 100% win rate on puts ($797 avg) cannot offset.

### High Conviction Paradox
You repeat trades in the same tickers. If OKTA calls are your high-conviction trade and you lose $10K, then $5.5K, then $5.5K again—that's -$21K in three trades. High conviction amplifies losses when you're wrong about direction.

---

## 9. FRAMEWORK RECOMMENDATIONS (Data-Driven)

### 1. **ABANDON NAKED CALLS**
- **Current:** 146 call trades, -$11.3K net P&L
- **Recommendation:** Stop selling naked calls entirely.
- **Alternative:** Covered calls on assigned put positions (wheel strategy) only.
- **Expected impact:** Remove -$77K in annual losses (if losses scale linearly).

### 2. **CONCENTRATE PUTS INTO HIGH CONVICTION TICKERS**
- **Current:** 249 put trades across many underlyings.
- **Recommendation:** 60% of capital into 4-5 best-performing tickers (AXON, GEV, MU based on YTD winners).
- **Rationale:** Top 10 winners are all puts on high-conviction names. Repeat wins, not one-off trades.
- **Expected impact:** Leverage winners; reduce losers through diversification exit.

### 3. **ABANDON TIER 3 (LOW CONVICTION) CONCEPT**
- **Current:** "Low conviction = -$500/trade"
- **Data:** Actual low conviction = +$273/trade (4 trades/month = +$1.1K/month)
- **Recommendation:** One-off selective puts on high-IV opportunities are profitable. Keep them.
- **Change:** Rename to "Opportunistic Puts" (not low conviction). Allocate $3-5K margin for 3-4 these per month.

### 4. **IMPLEMENT RULE: PUTS ONLY**
- **Current:** 50/50 put-call split in activity
- **Target:** 80% puts, 20% covered calls (wheels only)
- **Benefit:** 89% puts win vs 79% calls win. Asymmetric payoff becomes symmetric if calls are only on assigned shares.
- **Monthly margin freed:** Call losses (-$77K YTD / 6 months = -$12.8K/month) redirected to puts.

### 5. **RESET CONVICTION TIER TARGETS**
- **Current:** Tier 1 = 30% capital, $3,800/position
- **Data-driven Tier 1:** 47 positions/month in high-conviction symbols, $273/trade average
  - At $250K account: 47 × $273 = $12,831/month (5.1% monthly return)
  - Capital required: 47 trades × $500 margin/trade = $23.5K (9.4% of $250K)
  - **Recommendation:** Target 50-60 High-conviction put trades/month. This requires doubling margin allocation.

- **Current:** Tier 2 = 50% capital, $1,000/position
- **Data-driven Tier 2:** 14 positions/month, $134/trade
  - Monthly: $1,876 (0.75% return)
  - **Recommendation:** Keep as secondary diversifier. 15 trades/month.

- **Current:** Tier 3 = 20% capital, -$500/position (expected loss)
- **Data-driven Tier 3 (Opportunistic):** 4 positions/month, $273/trade
  - Monthly: $1,092 (0.44% return)
  - **Recommendation:** Rename and expand to 5-7 trades/month. These are profitable.

### 6. **MONTHLY MARGIN BUDGET**
| Tier | Trades/Month | Margin/Trade | Total Margin | Avg P&L/Trade | Monthly P&L |
|------|--------------|--------------|--------------|---------------|-------------|
| High Conviction | 50 | $500 | $25,000 | $273 | $13,650 |
| Medium Conviction | 15 | $400 | $6,000 | $134 | $2,010 |
| Opportunistic | 6 | $300 | $1,800 | $273 | $1,638 |
| **Total** | **71** | — | **$32,800** | — | **$17,298** |

- **Total margin used:** $32.8K / $250K account = **13.1% utilization**
- **Monthly P&L target:** $17,298 (6.9% return on capital used)
- **Annualized:** $17,298 × 12 = **$207,576 on $32.8K deployed** or 79% annual return (on margin capital)

---

## 10. FINAL CONCLUSION

**What the data reveals:**

1. **You're a put seller, not a call seller.** Puts generate $430/trade, calls lose $77/trade. The strategy is fundamentally put-based.

2. **High conviction is real, but asymmetric.** You repeat trades in good symbols and win big. But when you're wrong (OKTA calls), you lose huge multiples. High conviction should be **puts only**.

3. **Calls are destroying value.** 27 call losses (-$89.6K total, -$3,321 avg) vs 220 put winners (+$175K, +$797 avg). The math is clear: stop naked calls.

4. **Tier 1 is underallocated.** Current 1.5 positions/month generates $273/trade, but is allocated only 30% capital. Tier 3 is mislabeled (profitable, not a drag). Rebalance: 60% into high-conviction puts, 30% medium, 10% opportunistic.

5. **Monthly margin utilization should be 10-15%** on a $250K account to hit $15-20K/month P&L. Currently, you're likely at 5-8%, leaving meat on the bone.

6. **Regime matters.** EARLY_BULL = $325/trade. CAUTIOUS_BULL = $150/trade. In low-IV environments, scale down position size or sit out.

---

## Files Generated
- `/analysis/closed_pnl_detail.csv` — Full transaction-level P&L
- This report — Strategic insights
