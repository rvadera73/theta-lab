"""India F&O equivalent of premium_yield.py -- yield-on-capital for the
book's own index-only F&O universe (Nifty50/BankNifty/MidcapNifty per the
trader's explicit scope, confirmed 2026-09-25: India F&O activity is
index-level risk management, not individual-stock premium selling).

No free LIVE India option chain exists from this environment: NSE's live
option-chain API is Akamai-blocked here (confirmed 2026-09-25, 403 on the
homepage itself), and yfinance carries no NSE index option chains at all
(confirmed empty .options tuple for NIFTY/BANKNIFTY/MIDCPNIFTY). This
module instead uses NSE's own real, free, no-auth EOD bhavcopy archive
(confirmed working for 2026-09-22/23/24) -- end-of-day settlement data,
not live bid/ask. Real settlement column (SttlmPric) is NSE's own
theoretical/last settlement price, not necessarily a fillable live quote --
this is the honest free substitute, not a live equivalent, and every result
carries the bhavcopy date + each leg's real traded volume so a stale/
illiquid strike (0 volume, purely theoretical settlement) is visible rather
than silently treated as a real fill.

Default DTE window (20-45, centered ~30) mirrors this book's own observed
India F&O practice, not the US 90/120-day window -- the existing weekly
report already rolls/closes index legs "within 21 DTE" (see
india_weekly_report.py), implying entries are typically placed in the
30-45 DTE range for a monthly expiry cycle, not the longer-dated US style.
"""
import io
import zipfile
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Optional

import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; theta-lab-portfolio-tool/1.0)"}
_BHAVCOPY_URL = "https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"

INDIA_FNO_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "MIDCPNIFTY"]

DEFAULT_OTM_PCT = 0.10
DEFAULT_DTE_LOW = 20
DEFAULT_DTE_HIGH = 45
TARGET_DTE_MIDPOINT = 30
MAX_LOOKBACK_DAYS = 6  # weekend + up to a couple of holidays


@lru_cache(maxsize=8)
def _fetch_bhavcopy(ymd: str) -> Optional[list[dict]]:
    """Returns parsed rows for one real trading day, or None if that day
    has no published bhavcopy (weekend/holiday/not-yet-published) -- the
    caller walks backward from today until it finds a real file, same
    convention as any other "last trading day" lookup in this codebase.
    """
    url = _BHAVCOPY_URL.format(ymd=ymd)
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=30)
        if resp.status_code != 200 or len(resp.content) < 1000:
            return None
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        inner = z.namelist()[0]
        text = z.read(inner).decode("utf-8")
        lines = text.splitlines()
        header = lines[0].split(",")
        rows = []
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) != len(header):
                continue
            rows.append(dict(zip(header, parts)))
        return rows
    except Exception:
        return None


def _latest_bhavcopy(as_of: Optional[date] = None) -> tuple[Optional[list[dict]], Optional[date]]:
    as_of = as_of or date.today()
    d = as_of
    for _ in range(MAX_LOOKBACK_DAYS):
        rows = _fetch_bhavcopy(d.strftime("%Y%m%d"))
        if rows is not None:
            return rows, d
        d -= timedelta(days=1)
    return None, None


def get_yield_on_capital(
    underlying: str,
    otm_pct: float = DEFAULT_OTM_PCT,
    dte_low: int = DEFAULT_DTE_LOW,
    dte_high: int = DEFAULT_DTE_HIGH,
    as_of: Optional[date] = None,
) -> dict:
    """EOD put AND call yield-on-capital at the nearest ~otm_pct strike,
    nearest expiry inside [dte_low, dte_high] DTE, for one index underlying.
    Never raises -- returns an error key so a batch caller can skip a bad
    underlying, same convention as the US premium_yield.get_yield_on_capital.
    """
    if underlying not in INDIA_FNO_UNDERLYINGS:
        return {"underlying": underlying, "error": "not_in_india_fno_universe"}

    rows, bhav_date = _latest_bhavcopy(as_of)
    if rows is None:
        return {"underlying": underlying, "error": "bhavcopy_unavailable"}

    my_rows = [r for r in rows if r.get("TckrSymb") == underlying]
    if not my_rows:
        return {"underlying": underlying, "error": "no_rows_for_underlying", "bhavcopy_date": str(bhav_date)}

    underlying_price = float(my_rows[0]["UndrlygPric"])
    if underlying_price <= 0:
        return {"underlying": underlying, "error": "no_underlying_price", "bhavcopy_date": str(bhav_date)}

    today = bhav_date
    by_expiry: dict[str, int] = {}
    for r in my_rows:
        exp = r["XpryDt"]
        if exp not in by_expiry:
            exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            by_expiry[exp] = (exp_date - today).days

    candidates = {e: dte for e, dte in by_expiry.items() if dte_low <= dte <= dte_high}
    if not candidates:
        return {"underlying": underlying, "error": f"no_expiry_in_{dte_low}-{dte_high}_dte_window", "bhavcopy_date": str(bhav_date)}
    expiry = min(candidates, key=lambda e: abs(candidates[e] - TARGET_DTE_MIDPOINT))
    dte = candidates[expiry]

    puts = [r for r in my_rows if r["XpryDt"] == expiry and r["OptnTp"] == "PE"]
    calls = [r for r in my_rows if r["XpryDt"] == expiry and r["OptnTp"] == "CE"]
    if not puts or not calls:
        return {"underlying": underlying, "error": "no_options_at_expiry", "bhavcopy_date": str(bhav_date)}

    put_target = underlying_price * (1 - otm_pct)
    call_target = underlying_price * (1 + otm_pct)
    put_row = min(puts, key=lambda r: abs(float(r["StrkPric"]) - put_target))
    call_row = min(calls, key=lambda r: abs(float(r["StrkPric"]) - call_target))

    def _yield_for(row, capital):
        lot_size = int(row["NewBrdLotQty"])
        settle = float(row["SttlmPric"])
        premium = settle * lot_size
        annualized = (premium / capital) * (365 / dte) * 100 if capital > 0 else None
        return {
            "strike": float(row["StrkPric"]),
            "settle_price": settle,
            "lot_size": lot_size,
            "traded_volume": int(row["TtlTradgVol"]),
            "open_interest": int(row["OpnIntrst"]),
            "premium_inr": round(premium, 2),
            "capital_required_inr": round(capital, 2),
            "annualized_yield_pct": round(annualized, 2) if annualized is not None else None,
        }

    put_capital = float(put_row["StrkPric"]) * int(put_row["NewBrdLotQty"])
    call_capital = underlying_price * int(call_row["NewBrdLotQty"])

    return {
        "underlying": underlying,
        "underlying_price": round(underlying_price, 2),
        "bhavcopy_date": str(bhav_date),
        "expiry": expiry,
        "dte": dte,
        "put": _yield_for(put_row, put_capital),
        "call": _yield_for(call_row, call_capital),
    }


def batch_get_yield_on_capital(underlyings: Optional[list[str]] = None, **kwargs) -> dict[str, dict]:
    underlyings = underlyings or INDIA_FNO_UNDERLYINGS
    return {u: get_yield_on_capital(u, **kwargs) for u in underlyings}
