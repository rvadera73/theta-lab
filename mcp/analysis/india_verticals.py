"""India equivalent of trend_verticals.py -- cross-cutting thematic tags
independent of GICS-style sector, sourced from NSE Indices Limited's own
official Thematic Indices constituent CSVs (niftyindices.com), not a
hand-picked list. A held ticker can belong to more than one vertical.

Real, verified-live (2026-09-25) CSV URLs -- note two different base paths
(IndexConstituent vs Index_Statistics) and one irregular filename
(ind_niftyconsumptionlist.csv has no underscore before "list", unlike the
other four) -- both confirmed by fetching each index's own page and reading
its real embedded download link, not guessed from the URL pattern.
"""
import re
from functools import lru_cache

import requests

INDIA_VERTICAL_SOURCES = {
    "AI/Digital": "https://www.niftyindices.com/IndexConstituent/ind_niftyindiadigital_list.csv",
    "Defence": "https://www.niftyindices.com/IndexConstituent/ind_niftyindiadefence_list.csv",
    "Manufacturing": "https://www.niftyindices.com/IndexConstituent/ind_niftyindiamanufacturing_list.csv",
    "Consumption": "https://www.niftyindices.com/IndexConstituent/ind_niftyconsumptionlist.csv",
    "EV/New-Age Auto": "https://www.niftyindices.com/Index_Statistics/ind_niftyEv_NewAgeAutomotive_list.csv",
}

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; theta-lab-portfolio-tool/1.0)"}


@lru_cache(maxsize=1)
def _load_all_verticals() -> dict[str, set[str]]:
    """Returns {vertical_name: {real NSE symbol, ...}}. Fetched once per
    process (lru_cache) -- these are official index rebalance lists, not
    intraday data; re-fetching every call would be wasteful and the
    constituent set only changes on NSE's own periodic rebalance schedule.
    Never raises -- a source that fails to fetch just contributes an empty
    set for that vertical rather than crashing the whole module.
    """
    result: dict[str, set[str]] = {}
    for vertical, url in INDIA_VERTICAL_SOURCES.items():
        symbols: set[str] = set()
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=15)
            if resp.status_code == 200:
                lines = resp.text.splitlines()
                for line in lines[1:]:
                    parts = line.split(",")
                    if len(parts) >= 3:
                        symbols.add(parts[2].strip())
        except Exception:
            pass
        result[vertical] = symbols
    return result


def get_verticals_for_nse_symbol(nse_symbol: str) -> list[str]:
    """nse_symbol is the real NSE ticker (e.g. "HFCL", "PAYTM"), NOT the
    ICICI internal code -- translate via report_utils.yf_symbol() first
    and strip ".NS" before calling this.
    """
    all_verticals = _load_all_verticals()
    return sorted(v for v, symbols in all_verticals.items() if nse_symbol in symbols)


def batch_get_verticals(nse_symbols: list[str]) -> dict[str, list[str]]:
    return {s: get_verticals_for_nse_symbol(s) for s in nse_symbols}
