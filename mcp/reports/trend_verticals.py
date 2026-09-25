"""Hot Trend Verticals -- a cross-cutting tag layer on top of
sector_analysis.py's GICS-style sectors. A ticker keeps exactly ONE sector
(unchanged) but can carry MULTIPLE vertical tags, since real thematic
exposure cuts across sector boundaries: e.g. RKLB is both Space and
Defense/Dual-Use; TSM is both AI/Pick-and-Shovel and Global/EM Exposure;
AMZN is AI/Hyperscaler while sitting in the Consumer Cyclical sector.

V1, defined 2026-09-25 via a real, ticker-by-ticker review of the actual
92-ticker portfolio (grep the live report engine's own ticker_sector_map,
not invented in the abstract) and externally validated the same day, not
just reasoned about internally:
  - "Picks and shovels" AI infrastructure is a real, widely-used industry
    term (VanEck, MarketWise, multiple ETFs like SMH/SOXX/DTCR/GRID) --
    current market coverage explicitly names Vertiv (VRT) and Arista
    Networks (ANET) together as the standard AI-infrastructure pair
    (Arista sells AI-cluster switches with Meta/Microsoft as anchor
    customers), which is what surfaced ANET's real misclassification as
    "Brand-Quality (Non-AI)" in sector_analysis.py -- fixed the same day.
  - GLP-1 is a real, actively-tracked pharma investing theme (Lilly vs.
    Novo Nordisk tracked side by side across financial media), not a
    theme this codebase invented.
  - GICS's own 163 sub-industries include a distinct "Cybersecurity"
    category, separate from general "Application Software" -- confirms
    AI/Security as a real, recognized split from AI/SaaS, not an
    arbitrary one.
  - Crypto confirmed as a real, standing trend directly by the trader.

This is intentionally a flat, hand-maintained V1 (same pattern as
sector_analysis.py's CUSTOM_SECTOR_MAP) -- no attempt yet to auto-derive
verticals from a live source the way sector falls back to yfinance, since
"which trend a ticker belongs to" is a judgment call this taxonomy exists
specifically to make explicit, not something to infer mechanically.
Revisit whichever category needs it as the real portfolio changes.
"""

TREND_VERTICALS: dict[str, list[str]] = {
    # ---- AI (the dominant real theme in this portfolio; real sub-verticals) ----
    'AI/Pick-and-Shovel': ['NVDA', 'MU', 'TSM', 'AMKR', 'ALAB', 'LITE'],
    'AI/Data-Center-Infra': ['VRT', 'CRWV', 'NBIS', 'GEV', 'ANET'],
    'AI/Security': ['CRWD', 'ZS', 'PANW', 'OKTA'],
    'AI/SaaS': ['CRM', 'ADBE', 'TWLO', 'PLTR'],
    'AI/Nuclear-Power': ['CEG', 'OKLO', 'VST', 'SMR', 'BWXT', 'CCJ'],
    'AI/Hyperscaler': ['GOOGL', 'META', 'AMZN', 'MSFT'],
    'AI/Quantum': ['IONQ', 'QUBT'],

    # ---- Other real hot trends, distinct from the AI theme ----
    'Space': ['ASTS', 'RKLB', 'PL'],
    'GLP-1': ['NVO', 'LLY'],
    'Global Brand': ['NKE', 'SBUX'],
    'Crypto': ['COIN', 'CRCL', 'HUT', 'RIOT', 'CIFR'],
    'Global/EM Exposure': ['BABA', 'JD', 'INFY', 'NU', 'MMYT', 'TSM'],
    'Defense/Dual-Use': ['LMT', 'NOC', 'BA', 'KTOS', 'AXON', 'RKLB'],
}


def get_verticals_for_ticker(ticker: str) -> list[str]:
    """Every vertical tag a ticker carries -- usually 0-1, sometimes 2+
    (e.g. RKLB carries both Space and Defense/Dual-Use; TSM carries both
    AI/Pick-and-Shovel and Global/EM Exposure)."""
    return [v for v, tickers in TREND_VERTICALS.items() if ticker in tickers]


def get_vertical_membership() -> dict[str, list[str]]:
    """Ticker -> list of verticals, for every ticker that has at least one
    tag (a ticker with zero tags is simply absent, not listed with [])."""
    result: dict[str, list[str]] = {}
    for vertical, tickers in TREND_VERTICALS.items():
        for t in tickers:
            result.setdefault(t, []).append(vertical)
    return result


def get_ai_thesis_tickers() -> set[str]:
    """Every ticker tagged under any AI/* sub-vertical -- the real
    "AI exposure" set this portfolio's crash-scenario/macro-exposure
    checks should reference, since it correctly spans Technology,
    Utilities, Industrials, Energy, Communication Services, and Consumer
    Cyclical rather than assuming AI exposure means "Technology sector."
    """
    return {t for v, tickers in TREND_VERTICALS.items() if v.startswith('AI/') for t in tickers}
