# India Stock-List Review — 2026-08-15 (35 names)

**Source:** `indian-stock-list.xlsx`. Cross-referenced against actual current equity holdings + open F&O underlyings. Entry criterion is 52-week-range positioning + RSI (this trader's India strategy is staged equity accumulation at target entry zones, not individual-stock options selling — India F&O activity here is index-level only, so there is no IV-rank/options-yield check as there is on the US scanner.

**Symbol-matching:** held-status uses `report_utils.py`'s `_INDIA_SYMBOL_MAP` (ICICI transaction code -> standard NSE ticker) with a reverse lookup, since ICICI's own codes frequently differ from the standard symbol (e.g. `HDFBAN`/HDFCBANK, `LEMTRE`/LEMONTREE, `ZOMLIM`/ETERNAL) — plain exact-string matching would silently miss most real holdings. A stock held under a code NOT yet in that map would still be missed here; add it to `_INDIA_SYMBOL_MAP` if a held-status result looks wrong.

---

## Full Scan Results

| Scrip | Price | Sector | 52w Range % | RSI | Held (equity/F&O) | Verdict | Reason |
|---|---|---|---|---|---|---|---|
| HDFCBANK | 727.0 | Financial Services | 1% | 40 | equity | 🟡 | Bottom-quartile range (1%) but RSI 40 not confirming oversold |
| ITC | 278.2 | Consumer Defensive | 2% | 38 | not held | ✅ | Near 52w low (2% range) AND oversold (RSI 38) |
| RVNL | 227.35 | Industrials | 4% | 55 | not held | 🟡 | Bottom-quartile range (4%) but RSI 55 not confirming oversold |
| LEMONTREE | 108.92 | Consumer Cyclical | 11% | 49 | equity | 🟡 | Bottom-quartile range (11%) but RSI 49 not confirming oversold |
| RELIANCE | 1310.0 | Energy | 15% | 58 | equity | 🟡 | Bottom-quartile range (15%) but RSI 58 not confirming oversold |
| SWIGGY | 276.3 | Consumer Cyclical | 17% | 62 | not held | 🟡 | Bottom-quartile range (17%) but RSI 62 not confirming oversold |
| POWERGRID | 266.05 | Utilities | 18% | 20 | equity | ✅ | Near 52w low (18% range) AND oversold (RSI 20) |
| RAILTEL | 282.15 | Communication Services | 23% | 43 | not held | 🟡 | Bottom-quartile range (23%) but RSI 43 not confirming oversold |
| NTPC | 340.0 | Utilities | 23% | 39 | equity | 🟡 | Bottom-quartile range (23%) but RSI 39 not confirming oversold |
| INFY | 1169.2 | Technology | 26% | 70 | not held | ⚪ | 26% of range, RSI 70 — mid-range, no clear entry signal |
| DRREDDY | 1200.0 | Healthcare | 27% | 66 | not held | ⚪ | 27% of range, RSI 66 — mid-range, no clear entry signal |
| ICRA | 5265.6 | Financial Services | 27% | 79 | not held | ⚪ | 27% of range, RSI 79 — mid-range, no clear entry signal |
| PFC | 376.0 | Financial Services | 28% | 17 | not held | ⚪ | 28% of range, RSI 17 — mid-range, no clear entry signal |
| VBL | 435.0 | Consumer Defensive | 33% | 36 | equity | ⚪ | 33% of range, RSI 36 — mid-range, no clear entry signal |
| SUZLON | 47.1 | Industrials | 36% | 14 | not held | ⚪ | 36% of range, RSI 14 — mid-range, no clear entry signal |
| COCHINSHIP | 1496.5 | Industrials | 41% | 70 | not held | ⚪ | 41% of range, RSI 70 — mid-range, no clear entry signal |
| BEL | 410.8 | Industrials | 45% | 54 | equity | ⚪ | 45% of range, RSI 54 — mid-range, no clear entry signal |
| LUPIN | 2235.0 | Healthcare | 55% | 22 | equity | ⚪ | 55% of range, RSI 22 — mid-range, no clear entry signal |
| MAZDOCK | 2580.0 | Industrials | 55% | 80 | not held | ⚪ | 55% of range, RSI 80 — mid-range, no clear entry signal |
| DLF | 665.0 | Real Estate | 57% | 56 | equity | ⚪ | 57% of range, RSI 56 — mid-range, no clear entry signal |
| M&M | 3428.3 | Consumer Cyclical | 57% | 65 | not held | ⚪ | 57% of range, RSI 65 — mid-range, no clear entry signal |
| SBIN | 1067.7 | Financial Services | 62% | 65 | equity | ⚪ | 62% of range, RSI 65 — mid-range, no clear entry signal |
| HEROMOTOCO | 5790.0 | Consumer Cyclical | 66% | 79 | not held | ⚪ | 66% of range, RSI 79 — mid-range, no clear entry signal |
| ADANIPOWER | 205.25 | Utilities | 67% | 33 | equity | ⚪ | 67% of range, RSI 33 — mid-range, no clear entry signal |
| ADANIPORTS | 1700.0 | Industrials | 69% | 36 | equity | ⚪ | 69% of range, RSI 36 — mid-range, no clear entry signal |
| MCX | 2911.5 | Financial Services | 73% | 61 | not held | ⚪ | 73% of range, RSI 61 — mid-range, no clear entry signal |
| CONCOR | 527.0 | Industrials | 74% | 60 | not held | ⚪ | 74% of range, RSI 60 — mid-range, no clear entry signal |
| ETERNAL | 318.5 | Consumer Cyclical | 74% | 67 | equity | ⚪ | 74% of range, RSI 67 — mid-range, no clear entry signal |
| CGPOWER | 890.15 | Industrials | 81% | 53 | not held | ⚪ | 81% of range, RSI 53 — mid-range, no clear entry signal |
| ADANIENT | 3035.1 | Energy | 88% | 50 | not held | ❌ | Near 52w high (88% range) |
| IDEA | 14.11 | Communication Services | 90% | 71 | equity | ❌ | Near 52w high (90% range) |
| AUROPHARMA | 1622.1 | Healthcare | 93% | 62 | equity | ❌ | Near 52w high (93% range) |
| SOLARINDS | 19969.0 | Basic Materials | 96% | 67 | equity | ❌ | Near 52w high (96% range) |
| PARAS | 1377.5 | Industrials | 96% | 73 | equity | ❌ | Near 52w high (96% range) |
| ABB | 7649.0 | Industrials | 97% | 66 | not held | ❌ | Near 52w high (97% range) |
