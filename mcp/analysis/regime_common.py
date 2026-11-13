"""
Shared primitives for market-regime detection.

`analysis/regime.py` (US: VIX + S&P 500) and `analysis/india_regime.py`
(India: India VIX + Nifty 50) each run the exact same mechanics on
different symbols/thresholds:

  - fetching historical closes for a symbol (_get_closes)
  - computing a simple moving average (_moving_average)
  - turning accumulated bull/bear signal counts into a base technical
    regime via one classification tree (classify_tech_regime)

Those three pieces used to be copy-pasted character-for-character into
both files (see GitHub issue #60). Keeping them here means a change to
thresholds/logic can't be applied to only one market by accident --
fix it once, both regimes pick it up.

Deliberately NOT included here (these are genuine, non-duplicated
differences between the two markets and must stay local to each file):
  - regime.py's CAUTIOUS_BULL downgrade (VIX 16-20 / SPX >12% extended)
  - india_regime.py's INDIA_REGIME_OVERRIDE env-var trader override
"""

import yahoo_throttle  # noqa: F401 -- installs the global cross-process Yahoo rate limiter, must run before any yfinance call
import yfinance as yf
from config import Regime


def get_closes(symbol: str, period: str = "1y") -> list[float]:
    """Fetch historical daily closes for `symbol` over `period`.

    Returns [] on any fetch error (network issue, bad symbol, etc.)
    rather than raising, so callers can treat "no data" uniformly.
    """
    try:
        hist = yf.Ticker(symbol).history(period=period)
        return hist["Close"].tolist()
    except Exception:
        return []


def moving_average(closes: list[float], window: int) -> float:
    """Simple moving average of the last `window` closes.

    Returns 0.0 if there isn't yet enough history (len(closes) < window).
    """
    if len(closes) < window:
        return 0.0
    return sum(closes[-window:]) / window


def classify_tech_regime(bull_signals: int, bear_signals: int) -> Regime:
    """Shared bull/bear-signal classification tree, identical in both
    detect_regime() (US) and detect_india_regime() (India):

        bull_signals >= 3 and bear_signals == 0  -> BULL
        bear_signals >= 3                        -> BEAR_SIDEWAYS
        bull_signals > bear_signals              -> TRANSITIONING
        else                                     -> BEAR_SIDEWAYS

    This is the BASE technical regime -- each market's own module may
    still layer a further downgrade/override on top (US's CAUTIOUS_BULL
    check, India's env-var trader override).
    """
    if bull_signals >= 3 and bear_signals == 0:
        return Regime.BULL
    elif bear_signals >= 3:
        return Regime.BEAR_SIDEWAYS
    elif bull_signals > bear_signals:
        return Regime.TRANSITIONING
    else:
        return Regime.BEAR_SIDEWAYS
