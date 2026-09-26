"""India equivalent of sector_analysis.py's Yahoo Finance sector fallback --
Yahoo/yfinance carries essentially no fundamentals/sector data for NSE-
listed tickers (confirmed live 2026-09-25 while checking option-chain
feasibility for the same names). Screener.in is a real, free, no-login
Indian stock research site with a stable, clean "Broad Sector"/"Broad
Industry" classification per stock -- confirmed live 2026-09-25 (HFCL
correctly returns Sector "Telecommunication", Industry "Telecom -
Services" via a plain labeled anchor tag, not fragile/obfuscated markup).

Real Position objects (india_statement_parser.py) carry ICICI Direct's own
internal short codes (BILGAR, HDFBAN, STABAN, ...), not real NSE tickers --
confirmed live 2026-09-25 by querying the actual held portfolio. These are
translated via report_utils.yf_symbol()'s existing _INDIA_SYMBOL_MAP before
querying Screener.in (which needs the bare NSE symbol, no ".NS" suffix).

NIFTY/CNXBAN/NIFSEL are index-level F&O codes with no equity leg and no
Screener.in page -- excluded up front rather than fetched and failing.
"""
import re
import sys
from functools import lru_cache
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "reports"))
from report_utils import yf_symbol  # noqa: E402

SCREENER_URL = "https://www.screener.in/company/{symbol}/consolidated/"

_SECTOR_RE = re.compile(r'title="Broad Sector"[^>]*>([^<]+)<')
_INDUSTRY_RE = re.compile(r'title="Broad Industry"[^>]*>([^<]+)<')

# Index-only F&O underlyings held as Position objects (india_statement_parser.py
# creates one per open index leg) -- no equity, no Screener.in page.
INDEX_ONLY_CODES = {"NIFTY", "NIFSEL", "CNXBAN", "BANKNIFTY", "MIDCPNIFTY", "FINNIFTY"}


@lru_cache(maxsize=256)
def get_india_sector(icici_symbol: str) -> dict:
    """Returns {"sector": str|None, "industry": str|None, "source": "screener.in"}.
    Takes an ICICI Direct symbol (as stored on Position objects) and
    translates it to the real NSE ticker via yf_symbol() before querying.
    Cached per-process (lru_cache) -- this is a real webpage fetch, not a
    fast API call; a report run shouldn't re-fetch the same symbol twice.
    Never raises -- returns Unknown/None on any failure, same convention
    as sector_analysis.py's yfinance fallback.
    """
    if icici_symbol in INDEX_ONLY_CODES:
        return {"sector": "Index / F&O", "industry": None, "source": "n/a"}
    nse_symbol = yf_symbol(icici_symbol, india=True).removesuffix(".NS")
    try:
        resp = requests.get(
            SCREENER_URL.format(symbol=nse_symbol),
            headers={"User-Agent": "Mozilla/5.0 (compatible; theta-lab-portfolio-tool/1.0)"},
            timeout=10,
        )
        if resp.status_code != 200:
            return {"sector": None, "industry": None, "source": "screener.in", "error": f"HTTP {resp.status_code}"}
        html = resp.text
        sector_m = _SECTOR_RE.search(html)
        industry_m = _INDUSTRY_RE.search(html)
        return {
            "sector": sector_m.group(1).strip() if sector_m else None,
            "industry": industry_m.group(1).strip() if industry_m else None,
            "source": "screener.in",
        }
    except Exception as e:
        return {"sector": None, "industry": None, "source": "screener.in", "error": str(e)}


def batch_get_india_sectors(symbols: list[str]) -> dict[str, dict]:
    return {s: get_india_sector(s) for s in symbols}
