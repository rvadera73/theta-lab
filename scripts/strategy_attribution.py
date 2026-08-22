"""
Strategy Attribution — which of Short Put / Covered Call / Naked Call /
Stagger(strangle) has actually worked this year, by dollar P&L and win rate,
cross-tabulated against the market regime in effect when each trade closed.

Built on top of realized_pnl.py's already-corrected FIFO engine (same
per-broker parsers, same key format) — NOT a separate re-parse of the raw
files. This module adds:
  1. fifo_realize_detailed(): individual matched trades (not just monthly
     aggregates) with open_date/close_date per trade, needed for regime
     tagging and equity-coverage-at-open-time classification.
  2. Equity-coverage tracking: walks each account+ticker's equity FIFO state
     chronologically so a CALL's open date can be checked against shares
     actually held THEN (not today) — a call sold naked in March and covered
     by a later April purchase is naked, not covered, at the moment it was
     actually sold.
  3. Stagger detection: an underlying+account has a "stagger" (short
     strangle) if a PUT and a CALL were both open on the same underlying in
     the same account on any overlapping day range — matches Account A's
     documented strategy architecture (skills/options-trader/
     trading_persona.md: "short strangle engine").
  4. A historical regime timeline, replicating analysis/regime.py's exact
     BULL/CAUTIOUS_BULL/TRANSITIONING/BEAR_SIDEWAYS logic but computed AS OF
     each month-end this year (not just today), from the same VIX/SPX
     history — so each trade's close month can be tagged with the regime
     that was actually in effect then, not today's regime.
"""
import os
import sys
from collections import defaultdict, deque
from datetime import date

import yfinance as yf

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, os.path.join(_ROOT, "mcp"))
sys.path.insert(0, os.path.join(_ROOT, "mcp", "reports"))
sys.path.insert(0, os.path.join(_ROOT, "mcp", "analysis"))

from update_snapshot import (
    find_schwab_transactions, find_fidelity_transactions, find_robinhood_transactions,
)
from realized_pnl import (
    schwab_events, fidelity_events, robinhood_events,
    _parse_schwab_key, _parse_fidelity_key, _parse_robinhood_key,
    _TARGET_LABEL_ALIASES,
)
from config import REGIME_SIGNALS, Regime


# ---------------------------------------------------------------------------
# 1. Detailed (per-trade, not monthly-aggregated) FIFO
# ---------------------------------------------------------------------------

def fifo_realize_detailed(events):
    """Same matching logic/tie-break as realized_pnl.fifo_realize(), but
    returns individual trade records instead of monthly sums — needed to
    tag each trade with its own close-month's regime and to build per-key
    open/close interval lists for stagger detection."""
    events = sorted(events, key=lambda e: (e[0], 0 if e[2] == "open" else 1))
    queues = defaultdict(deque)  # key -> deque of [remaining_qty, per_unit, open_date]
    trades = []  # {key, open_date, close_date, qty, realized_pnl}

    for d, key, side, qty, amount in events:
        if qty <= 0:
            continue
        per_unit = amount / qty
        if side == "open":
            queues[key].append([qty, per_unit, d])
        else:
            remaining = qty
            while remaining > 1e-9 and queues[key]:
                lot = queues[key][0]
                take = min(remaining, lot[0])
                trades.append({
                    "key": key, "open_date": lot[2], "close_date": d,
                    "qty": take, "realized_pnl": (lot[1] + per_unit) * take,
                })
                lot[0] -= take
                remaining -= take
                if lot[0] <= 1e-9:
                    queues[key].popleft()

    open_lots = [(key, lot[0], lot[1], lot[2]) for key, q in queues.items() for lot in q]
    return trades, open_lots


# ---------------------------------------------------------------------------
# 2. Equity coverage — was N shares actually held on a given date?
# ---------------------------------------------------------------------------

def build_equity_share_timeline(equity_events):
    """{ticker: [(date, cumulative_shares_after_this_event)]} sorted by date,
    walked chronologically (opens=+qty, closes=-qty) so a later query can
    binary-search 'how many shares were held as of date D' without assuming
    today's holding applies retroactively."""
    by_ticker = defaultdict(list)
    events = sorted(equity_events, key=lambda e: (e[0], 0 if e[2] == "open" else 1))
    running = defaultdict(float)
    for d, ticker, side, qty, amount in events:
        running[ticker] += qty if side == "open" else -qty
        by_ticker[ticker].append((d, running[ticker]))
    return dict(by_ticker)


def shares_held_on(timeline, ticker, as_of_date):
    rows = timeline.get(ticker, [])
    held = 0.0
    for d, cum in rows:
        if d <= as_of_date:
            held = cum
        else:
            break
    return held


# ---------------------------------------------------------------------------
# 3. Stagger detection — did this underlying+account have overlapping
#    open PUT and CALL intervals at any point?
# ---------------------------------------------------------------------------

def detect_staggers(option_trades_by_key, key_parser):
    """Returns set of (underlying) tickers where a put-interval and a
    call-interval overlapped in time — the hallmark of the documented
    Account A short-strangle pattern, not a coincidence of two unrelated
    single-sided trades months apart."""
    intervals_by_underlying_type = defaultdict(lambda: {"P": [], "C": []})
    for key, trades in option_trades_by_key.items():
        parsed = key_parser(key)
        if not parsed:
            continue
        underlying, expiry, strike, opt_type = parsed
        opt_type = "C" if str(opt_type).upper() in ("C", "CALL") else "P"
        for t in trades:
            intervals_by_underlying_type[underlying][opt_type].append((t["open_date"], t["close_date"]))

    staggered = set()
    for underlying, by_type in intervals_by_underlying_type.items():
        puts, calls = by_type["P"], by_type["C"]
        for p_open, p_close in puts:
            for c_open, c_close in calls:
                if p_open <= c_close and c_open <= p_close:
                    staggered.add(underlying)
                    break
            if underlying in staggered:
                break
    return staggered


# ---------------------------------------------------------------------------
# 4. Historical regime timeline — analysis/regime.py's exact logic, computed
#    as of each month-end this year from the same VIX/SPX history.
# ---------------------------------------------------------------------------

def historical_regime_by_month(year=2026):
    vix = yf.Ticker("^VIX").history(period="2y")["Close"]
    spx = yf.Ticker("^GSPC").history(period="2y")["Close"]
    vix.index = vix.index.tz_localize(None)
    spx.index = spx.index.tz_localize(None)

    regimes = {}
    today = date.today()
    for month in range(1, 13):
        month_end = date(year, month, 28)
        if month_end > today:
            break
        # last actual trading day on/before this month-end
        vix_slice = vix[vix.index.date <= month_end]
        spx_slice = spx[spx.index.date <= month_end]
        if vix_slice.empty or spx_slice.empty:
            continue
        current_vix = float(vix_slice.iloc[-1])
        vix_5d = float(vix_slice.iloc[-5:].mean()) if len(vix_slice) >= 5 else current_vix
        spx_current = float(spx_slice.iloc[-1])
        spx_ma50 = float(spx_slice.iloc[-50:].mean()) if len(spx_slice) >= 50 else 0.0
        spx_ma200 = float(spx_slice.iloc[-200:].mean()) if len(spx_slice) >= 200 else 0.0

        bull_signals = bear_signals = 0
        if vix_5d < REGIME_SIGNALS["vix_bull_threshold"]:
            bull_signals += 1
        elif current_vix > REGIME_SIGNALS["vix_pause_threshold"]:
            bear_signals += 2

        if spx_current and spx_ma50 and spx_ma200:
            above_50, above_200 = spx_current > spx_ma50, spx_current > spx_ma200
            ma_signal = "BULL" if (above_50 and above_200) else "BEAR" if (not above_50 and not above_200) else "MIXED"
            if ma_signal == "BULL":
                bull_signals += 2
            elif ma_signal == "BEAR":
                bear_signals += 2
            else:
                bear_signals += 1

        if bull_signals >= 3 and bear_signals == 0:
            tech_regime = Regime.BULL
        elif bear_signals >= 3:
            tech_regime = Regime.BEAR_SIDEWAYS
        elif bull_signals > bear_signals:
            tech_regime = Regime.TRANSITIONING
        else:
            tech_regime = Regime.BEAR_SIDEWAYS

        final_regime = tech_regime
        if tech_regime == Regime.BULL:
            stretched = spx_ma200 and (spx_current / spx_ma200 - 1) * 100 > 12.0
            if current_vix >= 16.0 or stretched:
                final_regime = Regime.CAUTIOUS_BULL

        regimes[f"{year}-{month:02d}"] = final_regime.value
    return regimes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def classify_and_aggregate():
    accounts = []  # list of (broker, label, option_trades_by_key, equity_timeline, key_parser)

    for label, path in find_schwab_transactions().items():
        opt_ev, eq_ev = schwab_events(path)
        trades, _ = fifo_realize_detailed(opt_ev)
        by_key = defaultdict(list)
        for t in trades:
            by_key[t["key"]].append(t)
        eq_timeline = build_equity_share_timeline(eq_ev)
        accounts.append(("SCHWAB", label, by_key, eq_timeline, _parse_schwab_key))

    for person, path in find_fidelity_transactions().items():
        for acct, (opt_ev, eq_ev) in fidelity_events(path).items():
            trades, _ = fifo_realize_detailed(opt_ev)
            by_key = defaultdict(list)
            for t in trades:
                by_key[t["key"]].append(t)
            eq_timeline = build_equity_share_timeline(eq_ev)
            accounts.append(("FIDELITY", acct, by_key, eq_timeline, _parse_fidelity_key))

    for label, path in find_robinhood_transactions().items():
        opt_ev, eq_ev = robinhood_events(path)
        trades, _ = fifo_realize_detailed(opt_ev)
        by_key = defaultdict(list)
        for t in trades:
            by_key[t["key"]].append(t)
        eq_timeline = build_equity_share_timeline(eq_ev)
        accounts.append(("ROBINHOOD", label, by_key, eq_timeline, _parse_robinhood_key))

    regime_by_month = historical_regime_by_month()
    print("Historical regime by month (2026 YTD):")
    for m, r in regime_by_month.items():
        print(f"  {m}: {r}")
    print()

    # Classify every trade: strategy bucket + ticker + regime
    records = []  # {broker, account, ticker, strategy, realized_pnl, close_month, regime, stagger}
    for broker, label, by_key, eq_timeline, key_parser in accounts:
        staggered_underlyings = detect_staggers(by_key, key_parser)
        for key, trades in by_key.items():
            parsed = key_parser(key)
            if not parsed:
                continue
            underlying, expiry, strike, opt_type = parsed
            is_call = str(opt_type).upper() in ("C", "CALL")
            is_stagger = underlying in staggered_underlyings

            for t in trades:
                if is_call:
                    covered_shares = shares_held_on(eq_timeline, underlying, t["open_date"])
                    contracts_covered_by = covered_shares / 100 if covered_shares else 0
                    strategy = "Covered Call" if contracts_covered_by >= t["qty"] else "Naked Call"
                else:
                    strategy = "Short Put"

                # Collateral proxy for ROI: strike x 100 x qty for BOTH puts and
                # naked calls (same basis for both, even though a naked call's
                # REAL margin usage in Account A is far less under the 18%-of-
                # notional formula found earlier this session — using full
                # strike-based collateral consistently makes the cross-strategy
                # comparison apples-to-apples on "if this required full cash
                # collateral," not a claim about actual margin dollars used).
                # Covered calls have ~$0 INCREMENTAL capital (stock already
                # owned for another reason) so ROI-on-new-capital is undefined;
                # excluded from the ROI view, kept in the $ and count views.
                collateral = strike * 100 * t["qty"] if strike else None
                holding_days = max((t["close_date"] - t["open_date"]).days, 1)

                records.append({
                    "broker": broker, "account": label, "ticker": underlying,
                    "strategy": strategy, "stagger": is_stagger, "is_call": is_call,
                    "realized_pnl": t["realized_pnl"], "qty": t["qty"],
                    "collateral": collateral, "holding_days": holding_days,
                    "close_month": t["close_date"].strftime("%Y-%m"),
                    "regime": regime_by_month.get(t["close_date"].strftime("%Y-%m"), "unknown"),
                })

    return records, regime_by_month


def main():
    records, regime_by_month = classify_and_aggregate()

    print(f"\n{'='*100}\nSTRATEGY ATTRIBUTION — {len(records)} closed trades, 2026 YTD\n{'='*100}\n")

    # --- By strategy ---
    by_strategy = defaultdict(lambda: {"pnl": 0.0, "n": 0, "wins": 0})
    for r in records:
        b = by_strategy[r["strategy"]]
        b["pnl"] += r["realized_pnl"]
        b["n"] += 1
        b["wins"] += 1 if r["realized_pnl"] > 0 else 0
    print("BY STRATEGY:")
    print(f"  {'Strategy':<18}{'Realized $':>14}{'Trades':>9}{'Win Rate':>11}{'Avg $/trade':>14}")
    for strat, b in sorted(by_strategy.items(), key=lambda kv: -kv[1]["pnl"]):
        wr = b["wins"] / b["n"] * 100 if b["n"] else 0
        avg = b["pnl"] / b["n"] if b["n"] else 0
        print(f"  {strat:<18}{b['pnl']:>14,.0f}{b['n']:>9}{wr:>10.0f}%{avg:>14,.0f}")

    # --- ROI on collateral (annualized), not just $ and count ---
    # Covered calls excluded: ~$0 incremental capital, ROI-on-new-capital is
    # undefined for them, not "zero" or "infinite."
    by_strategy_roi = defaultdict(lambda: {"pnl": 0.0, "collateral_days": 0.0, "n": 0})
    for r in records:
        if r["strategy"] == "Covered Call" or not r["collateral"]:
            continue
        b = by_strategy_roi[r["strategy"]]
        b["pnl"] += r["realized_pnl"]
        b["collateral_days"] += r["collateral"] * r["holding_days"]
        b["n"] += 1
    print("\nROI ON COLLATERAL (annualized — same full-strike-collateral basis for both,")
    print("even though Account A's REAL naked-call margin usage is far less; this answers")
    print("'per dollar of capital tied up,' which trade-count alone can't tell you):")
    print(f"  {'Strategy':<16}{'Realized $':>14}{'Trades':>9}{'Ann. ROI %':>14}")
    for strat, b in sorted(by_strategy_roi.items(), key=lambda kv: -kv[1]["pnl"]):
        # Dollar-days-weighted annualized return: sum(pnl) / sum(collateral*days) * 365
        ann_roi = (b["pnl"] / b["collateral_days"] * 365 * 100) if b["collateral_days"] else 0
        print(f"  {strat:<16}{b['pnl']:>14,.0f}{b['n']:>9}{ann_roi:>13.1f}%")

    # --- Net strangle economics by (account, ticker) — the corrected view:
    # sum BOTH legs together instead of judging the call leg in isolation,
    # since a losing naked call paired with a winning put on the same
    # underlying is one strangle position, not two unrelated bets.
    net_stagger = defaultdict(lambda: {"pnl": 0.0, "n": 0, "put_pnl": 0.0, "call_pnl": 0.0})
    for r in records:
        if not r["stagger"]:
            continue
        key = (r["account"], r["ticker"])
        b = net_stagger[key]
        b["pnl"] += r["realized_pnl"]
        b["n"] += 1
        if r["is_call"]:
            b["call_pnl"] += r["realized_pnl"]
        else:
            b["put_pnl"] += r["realized_pnl"]
    print("\nNET STRANGLE ECONOMICS BY UNDERLYING (put leg + call leg combined —")
    print("the number that actually matters for a strangle position, not either leg alone):")
    print(f"  {'Account':<16}{'Ticker':<8}{'Put $':>12}{'Call $':>12}{'NET $':>12}{'Trades':>8}")
    for (acct, ticker), b in sorted(net_stagger.items(), key=lambda kv: kv[1]["pnl"]):
        print(f"  {acct:<16}{ticker:<8}{b['put_pnl']:>12,.0f}{b['call_pnl']:>12,.0f}{b['pnl']:>12,.0f}{b['n']:>8}")

    # --- Stagger vs non-stagger ---
    by_stagger = defaultdict(lambda: {"pnl": 0.0, "n": 0, "wins": 0})
    for r in records:
        key = "Stagger (put+call same underlying)" if r["stagger"] else "Single-sided"
        b = by_stagger[key]
        b["pnl"] += r["realized_pnl"]
        b["n"] += 1
        b["wins"] += 1 if r["realized_pnl"] > 0 else 0
    print("\nBY STAGGER PATTERN:")
    print(f"  {'Pattern':<36}{'Realized $':>14}{'Trades':>9}{'Win Rate':>11}")
    for k, b in sorted(by_stagger.items(), key=lambda kv: -kv[1]["pnl"]):
        wr = b["wins"] / b["n"] * 100 if b["n"] else 0
        print(f"  {k:<36}{b['pnl']:>14,.0f}{b['n']:>9}{wr:>10.0f}%")

    # --- By strategy x regime ---
    by_strat_regime = defaultdict(lambda: {"pnl": 0.0, "n": 0})
    for r in records:
        by_strat_regime[(r["strategy"], r["regime"])]["pnl"] += r["realized_pnl"]
        by_strat_regime[(r["strategy"], r["regime"])]["n"] += 1
    print("\nBY STRATEGY x REGIME (close-month regime):")
    print(f"  {'Strategy':<16}{'Regime':<16}{'Realized $':>14}{'Trades':>9}")
    for (strat, regime), b in sorted(by_strat_regime.items(), key=lambda kv: (kv[0][0], -kv[1]['pnl'])):
        print(f"  {strat:<16}{regime:<16}{b['pnl']:>14,.0f}{b['n']:>9}")

    # --- By strategy x ticker (winners/losers) ---
    by_strat_ticker = defaultdict(lambda: {"pnl": 0.0, "n": 0})
    for r in records:
        by_strat_ticker[(r["strategy"], r["ticker"])]["pnl"] += r["realized_pnl"]
        by_strat_ticker[(r["strategy"], r["ticker"])]["n"] += 1
    print("\nTOP 10 WINNERS by strategy+ticker:")
    winners = sorted(by_strat_ticker.items(), key=lambda kv: -kv[1]["pnl"])[:10]
    for (strat, ticker), b in winners:
        print(f"  {strat:<14}{ticker:<8}${b['pnl']:>10,.0f}  ({b['n']} trades)")
    print("\nTOP 10 LOSERS by strategy+ticker:")
    losers = sorted(by_strat_ticker.items(), key=lambda kv: kv[1]["pnl"])[:10]
    for (strat, ticker), b in losers:
        print(f"  {strat:<14}{ticker:<8}${b['pnl']:>10,.0f}  ({b['n']} trades)")


if __name__ == "__main__":
    main()
