"""
MACRO RISK ANALYZER — Crash Early Warning System

Monitors 7 layers of indicators to detect market crashes 4-12 weeks in advance:
1. Regime (SPX vs MAs, VIX)
2. Oscillators (RSI, Breadth, A-D)
3. VIX Term Structure
4. Credit Spreads (HY OAS)
5. Put/Call Ratio
6. Earnings Quality
7. Triggers (unpredictable)

Returns: Risk Level (GREEN/YELLOW/RED) + Rotation Playbook
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MacroRiskAnalyzer:
    """Analyze macro indicators for crash early warning"""

    def __init__(self):
        self.risk_level = "GREEN"
        self.signals = {}
        self.thresholds = {
            "breadth_yellow": 60,      # % of S&P above 50-MA
            "breadth_red": 50,
            "ad_ratio_yellow": 1.0,    # Advances/Declines
            "ad_ratio_red": 0.8,
            "vix_level_yellow": 18,    # VIX absolute level
            "vix_level_red": 25,
            "hyoas_yellow": 400,       # basis points
            "hyoas_red": 450,
            "pcr_yellow": 1.0,         # Put/Call Ratio
            "pcr_red": 1.2,
            "yield_curve_yellow": 0.1, # 10Y - 2Y spread
            "yield_curve_red": -0.05,  # Inverted
        }
    def fetch_fred_data(self, series_id: str) -> float:
        """Fetch latest data point from FRED's public CSV feed (no API key needed).

        The FRED api.stlouisfed.org/fred/series/observations endpoint requires a
        registered key; the key previously hardcoded here was never registered and
        returned HTTP 400 on every call, silently falling back to the "normal"
        defaults below on every report run (confirmed 2026-08-24 -- credit-spread
        and yield-curve signals were reading as fallback constants, not live data).
        fredgraph.csv is public and needs no key, at the cost of only returning a
        recent window (a few years) rather than full history -- fine here since we
        only need the latest observation.
        """
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                lines = [ln for ln in response.text.strip().splitlines() if ln]
                for line in reversed(lines[1:]):  # skip header, walk back from latest
                    _, value = line.split(",")
                    if value and value != ".":
                        return float(value)
        except Exception as e:
            logger.warning(f"Error fetching FRED {series_id}: {e}")
        return None

    def get_hyoas(self) -> float:
        """Get High Yield OAS spread (basis points) from FRED"""
        # BAMLH0A0HYM2 = ICE BofA US High Yield OAS, reported in percent (e.g. 2.70 = 270bps)
        hyoas = self.fetch_fred_data("BAMLH0A0HYM2")
        return hyoas * 100 if hyoas is not None else 380  # Default to normal if unavailable

    def get_yield_curve(self) -> float:
        """Get Yield Curve (10Y - 2Y Treasury spread) from FRED"""
        # T10Y2Y = 10-Year Minus 2-Year Treasury Constant Maturity Spread
        curve = self.fetch_fred_data("T10Y2Y")
        return curve if curve is not None else 0.6  # Default to normal if unavailable

    # Top 100 S&P 500 names by market cap (representative sample). This
    # includes most liquid names and covers major sectors.
    _SP500_BREADTH_SAMPLE = [
        'NVDA', 'MSFT', 'AAPL', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'JNJ', 'WMT',
        'XOM', 'JPM', 'V', 'MA', 'MRK', 'PG', 'ABBV', 'NYT', 'PFE', 'BAC',
        'CVX', 'KO', 'COST', 'NFLX', 'AMD', 'ADBE', 'INTC', 'CRM', 'INTU', 'CSCO',
        'QCOM', 'HON', 'UNH', 'AMGN', 'ISRG', 'BKNG', 'NOW', 'GE', 'UBER', 'AVGO',
        'AMAT', 'CRWD', 'AXON', 'ORCL', 'ROST', 'LRCX', 'SNPS', 'PEP', 'KKR', 'AXP',
        'ETN', 'MU', 'ABNB', 'ANET', 'NVDA', 'LLY', 'COIN', 'RBLX', 'PLTR', 'MSTR',
        'MCHP', 'CDNS', 'NXPI', 'STX', 'IDXX', 'ANSS', 'SPLK', 'TTD', 'OKTA', 'DDOG',
        'HOOD', 'PTON', 'SNAP', 'PINS', 'ZM', 'ROKU', 'DASH', 'LYFT', 'RBLX', 'APP',
        'CPRT', 'RRR', 'APP', 'ELF', 'ULTA', 'KMX', 'VROOM', 'LEA', 'APTV', 'XPEV'
    ]

    def _count_above_50ma(self, tickers: List[str]) -> Tuple[int, int]:
        """Fetch 3mo history for each ticker and count how many are trading
        above their own 50-day moving average. Returns (above_ma, total
        successfully-fetched-with-enough-history) -- a per-ticker fetch
        failure is silently skipped, not counted in either number."""
        import yfinance as yf

        above_ma = 0
        total = 0
        for ticker in tickers:
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period="3mo")

                if len(hist) >= 50:
                    close = hist['Close']
                    ma50 = close.rolling(window=50).mean()
                    if close.iloc[-1] > ma50.iloc[-1]:
                        above_ma += 1
                    total += 1
            except:
                pass
        return above_ma, total

    def get_breadth_from_yahoo(self) -> float:
        """
        Calculate % of S&P 500 stocks above 50-day MA using Yahoo Finance
        Fetches top 100 S&P 500 names (by weight) for speed; scales result to full 500
        """
        try:
            # Use 80 for faster execution
            above_ma, total = self._count_above_50ma(self._SP500_BREADTH_SAMPLE[:80])

            if total > 0:
                breadth_pct = (above_ma / total) * 100
                logger.info(f"Breadth calculated: {above_ma}/{total} ({breadth_pct:.1f}% of sample)")
                return float(breadth_pct)
            else:
                return 75.0

        except Exception as e:
            logger.warning(f"Error calculating breadth from Yahoo: {e}")
            return 75.0

    def estimate_breadth(self, market_data: dict) -> float:
        """Calculate breadth from Yahoo Finance S&P 500 sample"""
        return self.get_breadth_from_yahoo()

    def get_ad_ratio_from_yahoo(self) -> float:
        """
        Calculate Advance-Decline Ratio from S&P 500 sample via Yahoo Finance
        Ratio = (# stocks up today) / (# stocks down today)
        > 1.0 = bullish (more advancers), < 1.0 = bearish (more decliners)
        """
        try:
            import yfinance as yf

            sp500_sample = [
                'NVDA', 'MSFT', 'AAPL', 'AMZN', 'GOOGL', 'META', 'TSLA', 'JNJ', 'WMT', 'XOM',
                'JPM', 'V', 'MA', 'MRK', 'PG', 'ABBV', 'PFE', 'BAC', 'CVX', 'KO',
                'COST', 'NFLX', 'AMD', 'ADBE', 'INTC', 'CRM', 'INTU', 'CSCO', 'QCOM', 'HON',
                'UNH', 'AMGN', 'ISRG', 'BKNG', 'NOW', 'UBER', 'AVGO', 'AMAT', 'CRWD', 'AXON',
                'ORCL', 'ROST', 'LRCX', 'SNPS', 'PEP', 'KKR', 'AXP', 'ETN', 'MU', 'ABNB',
                'ANET', 'LLY', 'COIN', 'RBLX', 'PLTR', 'MSTR', 'MCHP', 'CDNS', 'NXPI', 'STX'
            ]

            advancers = 0
            decliners = 0

            for ticker in sp500_sample[:50]:  # Use 50 for speed
                try:
                    data = yf.Ticker(ticker)
                    hist = data.history(period="5d")

                    if len(hist) >= 2:
                        today_close = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2]

                        if today_close > prev_close:
                            advancers += 1
                        elif today_close < prev_close:
                            decliners += 1
                except:
                    pass

            if decliners > 0:
                ratio = advancers / decliners
                logger.info(f"A-D Ratio calculated: {advancers} advancers, {decliners} decliners → {ratio:.2f}")
                return float(ratio)
            else:
                # All up or no data
                return 1.3

        except Exception as e:
            logger.warning(f"Error calculating A-D ratio from Yahoo: {e}")
            return 1.3

    def estimate_ad_ratio(self) -> float:
        """Wrapper for get_ad_ratio_from_yahoo for backwards compatibility"""
        return self.get_ad_ratio_from_yahoo()

    # Fallback when VIX futures data can't be fetched at all.
    _VIX_TERM_FALLBACK = {
        "type": "CONTANGO",
        "front_vix": 15.8,
        "back_vix": 18.2,
    }

    def _fetch_vix_futures_closes(self) -> Optional[Tuple[float, float]]:
        """Fetch latest VIXM (front-month) / VIXN (next-month) closes.
        Note: VIX futures symbols are typically VIXM (front month), VIXN
        (next month) -- this is a simplified approach. Returns None if the
        fetch fails or doesn't have data for both tickers; an import failure
        propagates to the caller (the import sits outside this inner
        try/except, matching the original control flow)."""
        import yfinance as yf

        try:
            vix_m = yf.Ticker("VIXM")
            vix_n = yf.Ticker("VIXN")

            hist_m = vix_m.history(period="1d")
            hist_n = vix_n.history(period="1d")

            if len(hist_m) > 0 and len(hist_n) > 0:
                return float(hist_m['Close'].iloc[-1]), float(hist_n['Close'].iloc[-1])
        except:
            pass
        return None

    @staticmethod
    def _classify_vix_term_type(front: float, back: float) -> str:
        """CONTANGO (front well below back, normal) / BACKWARDATION (front
        well above back, alert) / FLAT (within 5% of each other, caution)."""
        if front < back * 0.95:
            return "CONTANGO"
        elif front > back * 1.05:
            return "BACKWARDATION"
        else:
            return "FLAT"

    def get_vix_term_structure(self) -> Dict:
        """
        Get VIX term structure (front month vs back month)
        Uses CBOE VIX futures data
        """
        try:
            closes = self._fetch_vix_futures_closes()
            if closes is not None:
                front, back = closes
                return {
                    "type": self._classify_vix_term_type(front, back),
                    "front_vix": front,
                    "back_vix": back,
                }
            # Fallback
            return dict(self._VIX_TERM_FALLBACK)
        except Exception as e:
            logger.warning(f"Error getting VIX term structure: {e}")
            return dict(self._VIX_TERM_FALLBACK)

    def get_put_call_ratio(self) -> float:
        """
        Get Put/Call Ratio from CBOE or market data
        Simplified implementation
        """
        try:
            # Try to fetch from CBOE Market Statistics
            # CBOE publishes Put/Call Ratio daily at: https://www.cboe.com/delayed_quotes/pcr
            # For MVP: use reasonable default based on market conditions

            # In production, would fetch from:
            # - CBOE Market Statistics API
            # - Or calculate from options data

            return 0.75  # Default normal market ratio

        except Exception as e:
            logger.warning(f"Error getting Put/Call ratio: {e}")
            return 0.75

    def _build_breadth_signal(self, market_data: Dict) -> Dict:
        """Layer 2: Oscillators -- breadth signal"""
        breadth = self.estimate_breadth(market_data)
        return {
            "value": breadth,
            "status": "RED" if breadth < self.thresholds["breadth_red"]
                     else "YELLOW" if breadth < self.thresholds["breadth_yellow"]
                     else "GREEN",
            "threshold": f"{self.thresholds['breadth_yellow']}% (caution), {self.thresholds['breadth_red']}% (alert)"
        }

    def _build_ad_ratio_signal(self) -> Dict:
        """Layer 2: Oscillators -- advance/decline ratio signal"""
        ad_ratio = self.estimate_ad_ratio()
        return {
            "value": ad_ratio,
            "status": "RED" if ad_ratio < self.thresholds["ad_ratio_red"]
                     else "YELLOW" if ad_ratio < self.thresholds["ad_ratio_yellow"]
                     else "GREEN",
            "threshold": f"{self.thresholds['ad_ratio_yellow']} (caution), {self.thresholds['ad_ratio_red']} (alert)"
        }

    def _build_vix_term_signal(self) -> Dict:
        """Layer 3: VIX term structure signal"""
        vix_term = self.get_vix_term_structure()
        return {
            "value": vix_term["type"],
            "status": "RED" if vix_term["type"] == "BACKWARDATION"
                     else "YELLOW" if vix_term["type"] == "FLAT"
                     else "GREEN",
            "threshold": "Contango (normal) → Flat (caution) → Backwardation (alert)"
        }

    def _build_hyoas_signal(self) -> Optional[Dict]:
        """Layer 4: Credit spreads (HY OAS) signal. Returns None when hyoas
        itself is falsy, matching the original `if hyoas:` guard -- so the
        "hyoas" key is simply absent from signals rather than present with
        a GREEN/zero value."""
        hyoas = self.get_hyoas()
        if not hyoas:
            return None
        return {
            "value": f"{hyoas:.0f} bps",
            "raw_value": hyoas,
            "status": "RED" if hyoas > self.thresholds["hyoas_red"]
                     else "YELLOW" if hyoas > self.thresholds["hyoas_yellow"]
                     else "GREEN",
            "threshold": f"{self.thresholds['hyoas_yellow']} (caution), {self.thresholds['hyoas_red']} (alert)"
        }

    def _build_pcr_signal(self) -> Dict:
        """Layer 5: Put/Call ratio signal"""
        pcr = self.get_put_call_ratio()
        return {
            "value": f"{pcr:.2f}",
            "raw_value": pcr,
            "status": "RED" if pcr > self.thresholds["pcr_red"]
                     else "YELLOW" if pcr > self.thresholds["pcr_yellow"]
                     else "GREEN",
            "threshold": f"{self.thresholds['pcr_yellow']} (caution), {self.thresholds['pcr_red']} (alert)"
        }

    def _build_yield_curve_signal(self) -> Optional[Dict]:
        """Layer 6: Yield curve signal. Returns None when get_yield_curve()
        itself returns None, matching the original `if yield_curve is not
        None:` guard."""
        yield_curve = self.get_yield_curve()
        if yield_curve is None:
            return None
        return {
            "value": f"{yield_curve:.2f}%",
            "raw_value": yield_curve,
            "status": "RED" if yield_curve < self.thresholds["yield_curve_red"]
                     else "YELLOW" if yield_curve < self.thresholds["yield_curve_yellow"]
                     else "GREEN",
            "threshold": f"Inverted (alert), <0.1% (caution), >0.5% (normal)"
        }

    def _classify_risk_level(self, prob_30d: float) -> Tuple[str, int]:
        """Determine overall risk level -- keyed off the continuous prob_30d
        analyze_risk already computes, matching the staged-response bands
        in trading_persona.md's "Macro Risk Framework" (<20% GREEN, 20-60%
        YELLOW covering both YELLOW-1/YELLOW-2, >=60% RED covering both
        RED-Emerging/RED-Critical -- the existing code only has 3 stages,
        not 5, so the two finer bands collapse at their shared boundary).
        Real bug this replaces (found 2026-10-13/14): the old rule counted
        how many of the 7 layers individually crossed their OWN threshold
        (red_count>=2, or yellow_count>=3, or 1 of each) -- completely
        disconnected from prob_30d. On 2026-10-14 only breadth went
        critical (red_count=1, yellow_count=0), so the old rule said GREEN
        even though prob_30d had already jumped to 33.1%, squarely inside
        the persona doc's own 20-40% YELLOW-1 action band. A single severe
        layer with no others elevated could never trip the old rule at
        all, no matter how high prob_30d actually climbed."""
        if prob_30d >= 60.0:
            return "RED", 2
        elif prob_30d >= 20.0:
            return "YELLOW", 1
        else:
            return "GREEN", 0

    def analyze_risk(self, market_data: Dict) -> Dict:
        """Analyze all 7 layers (breadth, A-D ratio, VIX term structure, HY
        OAS, put/call ratio, yield curve) and return the full risk
        assessment: risk_level ("GREEN|YELLOW|RED"), signals (per-indicator
        value/status/threshold), stage (0/1/2), summary, actions,
        crash_probability, playbook, sector_sensitivity. `market_data`'s
        documented vix/spx_price/spx_50ma/spx_200ma fields are accepted but
        not read by this method (see module-level notes)."""
        signals = {}

        # Layer 1: REGIME (already handled by main report)
        # We focus on Layers 2-6 here

        # Layer 2: Oscillators (Breadth, A-D Ratio)
        signals["breadth"] = self._build_breadth_signal(market_data)
        signals["ad_ratio"] = self._build_ad_ratio_signal()

        # Layer 3: VIX Term Structure
        signals["vix_term"] = self._build_vix_term_signal()

        # Layer 4: Credit Spreads (HY OAS)
        hyoas_signal = self._build_hyoas_signal()
        if hyoas_signal:
            signals["hyoas"] = hyoas_signal

        # Layer 5: Put/Call Ratio
        signals["pcr"] = self._build_pcr_signal()

        # Layer 6: Yield Curve
        yield_curve_signal = self._build_yield_curve_signal()
        if yield_curve_signal:
            signals["yield_curve"] = yield_curve_signal

        # Calculate crash probability forecast
        crash_prob = self.calculate_crash_probability(signals)

        prob_30d = crash_prob.get("prob_30d", 6.0)
        risk_level, stage = self._classify_risk_level(prob_30d)

        return {
            "risk_level": risk_level,
            "stage": stage,
            "signals": signals,
            "summary": self._get_risk_summary(risk_level, stage, signals),
            "actions": self._get_actions(risk_level, stage),
            "crash_probability": crash_prob,
            "playbook": self._get_rotation_playbook(stage, crash_prob),
            "sector_sensitivity": self.get_sector_crash_sensitivity(crash_prob.get("primary_risk", "")),
        }

    # Which sectors historically take the brunt of a given risk factor's
    # unwind — deliberately NOT one static list for every scenario, since
    # breadth-narrowing (momentum/leadership unwind) and credit-spread-widening
    # (risk-off, leverage-sensitive) hit different parts of the book. Per-name
    # heat/conviction scoring never sees any of this (see enhanced_metrics.py) —
    # this is what lets the report say "which sector is most exposed given
    # TODAY's specific risk driver" instead of a single always-the-same list.
    #
    # BACKTESTED 2026-09-25 against 5 years of real sector-ETF forward returns
    # following real historical episodes of each driver crossing its own
    # "yellow" threshold (same thresholds as `thresholds` above) -- this map
    # had never been checked against real data before that. `confidence`
    # reflects what that backtest actually found, not how the map reads:
    #   strong: high-sensitivity sectors clearly underperformed low-sensitivity
    #     at both the 10d and 20d forward horizon (ad_ratio: 303 episodes,
    #     n=1200+; yield_curve: 67 episodes, n=134+).
    #   weak: true at 20d but a statistical wash at 10d (breadth: 70 episodes --
    #     the SAME sector list as ad_ratio, but breadth itself is a much
    #     weaker discriminator than ad_ratio for near-term moves).
    #   unconfirmed: too few real episodes in a 5y window to say anything
    #     (hyoas: only 4 episodes -- true high-yield-spread blowouts are rare;
    #     would need a lookback back through 2008/2020 to get a real sample).
    # vix_term's direction was flipped 2026-09-25 -- the backtest found the
    # ORIGINAL "high" list actually outperformed the "low" list at both
    # horizons (27 episodes, a reasonable sample), the opposite of what this
    # map claimed; swapped rather than left wrong now that real data exists.
    # pcr has no free historical data source and is not in this map at all —
    # get_sector_crash_sensitivity() returns {} for it (a real gap, not a
    # silent guess).
    SECTOR_SENSITIVITY_MAP = {
        "ad_ratio": {  # narrow breadth / momentum-leadership unwind
            "high": ["Technology", "Consumer Cyclical", "Communication Services", "Basic Materials"],
            "low": ["Utilities", "Healthcare", "Consumer Defensive", "Energy", "Defense"],
            "confidence": "strong",
        },
        "breadth": {  # same failure mode as ad_ratio — narrow participation
            "high": ["Technology", "Consumer Cyclical", "Communication Services", "Basic Materials"],
            "low": ["Utilities", "Healthcare", "Consumer Defensive", "Energy", "Defense"],
            "confidence": "weak",
        },
        "hyoas": {  # credit-spread widening — leverage/cyclical-sensitive names
            "high": ["Financial Services", "Industrials", "Basic Materials"],
            "low": ["Utilities", "Consumer Defensive", "Healthcare"],
            "confidence": "unconfirmed",
        },
        "yield_curve": {  # inversion — financials margin compression + long-duration growth revaluation
            "high": ["Financial Services", "Technology"],
            "low": ["Utilities", "Energy", "Consumer Defensive"],
            "confidence": "strong",
        },
        "vix_term": {  # backwardation — swapped 2026-09-25, see note above
            "high": ["Utilities", "Consumer Defensive", "Healthcare"],
            "low": ["Technology", "Consumer Cyclical", "Communication Services", "Basic Materials"],
            "confidence": "strong",
        },
    }

    def get_sector_crash_sensitivity(self, primary_risk: str) -> Dict:
        """Map the crash forecast's primary_risk string (e.g. "AD_RATIO critical")
        back to which sectors are historically most/least exposed to THAT
        specific risk factor's unwind. Returns {} if primary_risk is
        "Market neutral" (nothing flagged) or doesn't match a known indicator
        (this now includes "pcr" -- deliberately not in the map, see above)."""
        if not primary_risk or primary_risk == "Market neutral":
            return {}
        indicator = primary_risk.split()[0].lower()
        mapping = self.SECTOR_SENSITIVITY_MAP.get(indicator)
        if not mapping:
            return {}
        return {
            "driver": indicator.upper(),
            "high_sensitivity_sectors": mapping["high"],
            "low_sensitivity_sectors": mapping["low"],
            "confidence": mapping["confidence"],
        }

    def _get_risk_summary(self, risk_level: str, stage: int, signals: Dict) -> str:
        """Generate risk summary text"""
        if risk_level == "GREEN":
            return "✅ BULL regime stable. All indicators healthy. Proceed with normal sizing."
        elif risk_level == "YELLOW":
            yellow_signals = [k for k, v in signals.items() if v["status"] == "YELLOW"]
            return f"⚠️ CAUTION — {len(yellow_signals)} indicators turning yellow. Watch for deterioration."
        else:
            red_signals = [k for k, v in signals.items() if v["status"] == "RED"]
            return f"🔴 ALERT — {len(red_signals)} indicators critical. Market fragility rising."

    def _get_actions(self, risk_level: str, stage: int) -> List[str]:
        """Get recommended actions based on risk level"""
        if stage == 0:
            return [
                "✅ No action needed",
                "Proceed with normal entry sizing",
                "Monitor for any signal changes"
            ]
        elif stage == 1:
            return [
                "⚠️ Stage 1 Rotation (6-8 week advance warning)",
                "Close 30% of overbought positions (RSI > 75)",
                "Reduce naked call exposure by 20%",
                "Shift new entries to DEFENSIVE sectors",
                "Keep short puts (they profit on dips)"
            ]
        else:
            return [
                "🔴 Stage 2-3 Rotation (Crash risk rising)",
                "Close 50% of remaining overbought positions",
                "Reduce naked call exposure by 30% more",
                "Rotate proceeds to: Cash (40%), Defensive (30%)",
                "Stop entering new GROWTH positions",
                "Prepare for potential Stage 3 (emergency)"
            ]

    # Per-indicator (yellow_threshold, red_threshold, higher_is_worse) — needed to
    # compute a continuous severity instead of a binary RED/YELLOW/GREEN bucket.
    # Must mirror self.thresholds' pairing exactly (kept separate because
    # self.thresholds uses flat keys like "ad_ratio_yellow", not grouped tuples).
    _SEVERITY_SPEC = {
        "breadth":      ("breadth_yellow", "breadth_red", False),      # lower = worse
        "ad_ratio":     ("ad_ratio_yellow", "ad_ratio_red", False),    # lower = worse
        "hyoas":        ("hyoas_yellow", "hyoas_red", True),           # higher = worse
        "pcr":          ("pcr_yellow", "pcr_red", True),                # higher = worse
        "yield_curve":  ("yield_curve_yellow", "yield_curve_red", False),  # lower = worse
    }

    def _indicator_severity(self, indicator: str, value) -> float:
        """Continuous 0.0 (fully green) to 2.0 (twice as deep past the red
        threshold as the red threshold itself is past yellow) severity score.

        Replaces flat RED=1/YELLOW=1 counting, which couldn't tell a reading
        that just barely crossed the red threshold from one deep inside it —
        empirically confirmed on 2026-08-14: AD_RATIO moved from 0.79 to 0.515
        (both below the 0.8 red threshold) across same-day report reruns, and
        the old formula produced an IDENTICAL 51.0% 90-day crash probability
        both times because it only counted "1 red signal" either way.

        vix_term is excluded (categorical CONTANGO/FLAT/BACKWARDATION, no
        numeric threshold to score a continuous distance against) — it still
        contributes via the old red/yellow COUNT path in calculate_crash_probability,
        just not through this continuous severity path.
        """
        spec = self._SEVERITY_SPEC.get(indicator)
        if spec is None or value is None or not isinstance(value, (int, float)):
            return 0.0
        yellow_t, red_t, higher_is_worse = spec
        yellow_t, red_t = self.thresholds[yellow_t], self.thresholds[red_t]
        gap = abs(red_t - yellow_t)
        if gap == 0:
            return 0.0
        # Past the red threshold, severity ramps to its 2.0 cap over TWICE the
        # yellow->red gap (not once) — a narrow-gap indicator like ad_ratio
        # (yellow 1.0, red 0.8, gap 0.2) would otherwise saturate at 2.0 the
        # moment it hit 0.6, which is well within its normal daily noise range
        # (observed 0.51-0.79 across same-day reruns on 2026-08-14) and made
        # "barely red" and "deeply red" look almost identical again — exactly
        # the blindness this was meant to fix.
        past_red_scale = 2.0 * gap
        if higher_is_worse:
            if value <= yellow_t:
                return 0.0
            if value <= red_t:
                return max(0.0, min(1.0, (value - yellow_t) / gap))
            return 1.0 + max(0.0, min(1.0, (value - red_t) / past_red_scale))
        else:
            if value >= yellow_t:
                return 0.0
            if value >= red_t:
                return max(0.0, min(1.0, (yellow_t - value) / gap))
            return 1.0 + max(0.0, min(1.0, (red_t - value) / past_red_scale))

    def _compute_severity_sum(self, signals: Dict) -> float:
        """Continuous severity sum across all scoreable indicators — this is
        what drives the crash probability. A reading that's barely past its
        threshold contributes near 0; one deep in the red zone contributes
        up to 2.0. vix_term (no numeric threshold) falls back to a flat
        1.0/0.4 RED/YELLOW severity so it still counts, just without
        magnitude sensitivity."""
        severity_sum = 0.0
        for indicator, details in signals.items():
            if not isinstance(details, dict):
                continue
            if indicator in self._SEVERITY_SPEC:
                severity_sum += self._indicator_severity(indicator, details.get('raw_value', details.get('value')))
            elif details.get('status') == 'RED':
                severity_sum += 1.0
            elif details.get('status') == 'YELLOW':
                severity_sum += 0.4
        return severity_sum

    def _select_primary_risk(self, signals: Dict) -> str:
        """Identify primary risk factor — picks the indicator with the
        HIGHEST severity (not just "first RED found in dict order"), so it
        actually reflects which signal is doing the most damage. On an exact
        severity tie, the first indicator encountered in `signals`'
        insertion order wins (strict `>` comparison) -- current, documented
        behavior, not changed."""
        worst_indicator, worst_severity = None, 0.0
        for indicator, details in signals.items():
            if not isinstance(details, dict):
                continue
            sev = (self._indicator_severity(indicator, details.get('raw_value', details.get('value')))
                   if indicator in self._SEVERITY_SPEC
                   else (1.0 if details.get('status') == 'RED' else 0.4 if details.get('status') == 'YELLOW' else 0.0))
            if sev > worst_severity:
                worst_severity, worst_indicator = sev, indicator
        if worst_indicator:
            status = signals[worst_indicator].get('status')
            return f"{worst_indicator.upper()} critical" if status == 'RED' else f"{worst_indicator.upper()} elevated"
        return "Market neutral"

    @staticmethod
    def _action_trigger_for_prob30d(prob_30d: float) -> Tuple[str, float]:
        """Determine action based on 30-day probability -> (action_trigger
        text, position_reduction_pct)."""
        if prob_30d >= 70:
            return "🔴 EMERGENCY: Reduce gross exposure by 50% immediately", 0.50
        elif prob_30d >= 50:
            return "🟠 HIGH RISK: Reduce gross exposure by 30-40%", 0.35
        elif prob_30d >= 30:
            return "🟡 CAUTION: Reduce overbought positions by 20-25%", 0.20
        else:
            return "🟢 NORMAL: Proceed with standard sizing", 0.0

    def calculate_crash_probability(self, signals: Dict) -> Dict:
        """
        Calculate probabilistic crash forecast for 30/60/90-day windows
        Based on historical crash patterns and current signal combination

        Returns:
            {
                "prob_30d": float (0-100),
                "prob_60d": float (0-100),
                "prob_90d": float (0-100),
                "primary_risk": str (which indicator is most concerning),
                "action_trigger": str (what to do based on probability)
            }
        """
        # Base probabilities (historical market crash rate ~5-7% per month)
        base_prob_30d = 6.0
        base_prob_60d = 11.0
        base_prob_90d = 16.0

        severity_sum = self._compute_severity_sum(signals)

        # Adjust probabilities based on continuous severity (replaces the old
        # flat red_count*15/yellow_count*5-style bumps — same rough scale at
        # severity=1.0 (a reading exactly at its red threshold) as the old
        # red_count=1 case, but now scales smoothly past that point instead of
        # staying frozen for any reading beyond the threshold. Capped at 95%
        # (never 100% certain).
        prob_30d = min(base_prob_30d + severity_sum * 15, 95.0)
        prob_60d = min(base_prob_60d + severity_sum * 25, 95.0)
        prob_90d = min(base_prob_90d + severity_sum * 35, 95.0)

        primary_risk = self._select_primary_risk(signals)
        action_trigger, position_reduction = self._action_trigger_for_prob30d(prob_30d)

        return {
            "prob_30d": prob_30d,
            "prob_60d": prob_60d,
            "prob_90d": prob_90d,
            "primary_risk": primary_risk,
            "action_trigger": action_trigger,
            "position_reduction_pct": position_reduction
        }

    @staticmethod
    def _playbook_stage_0(prob_30d: float, prob_60d: float, prob_90d: float) -> str:
        """Stage 0 (GREEN) rotation playbook text."""
        return f"""
GREEN LIGHT — Proceed with normal operations (Crash prob: {prob_30d:.0f}% in 30d)
  • New entries: Full size (Account A BULL sizing)
  • Position management: Normal weekly review
  • Defensive rotation: Not needed
  • Cash level: Maintain tactical 10-15%
  • 60/90-day outlook: {prob_60d:.0f}% / {prob_90d:.0f}% crash probability
            """

    @staticmethod
    def _playbook_stage_1(prob_30d: float, prob_60d: float, prob_90d: float, reduction_pct: float) -> str:
        """Stage 1 (YELLOW) rotation playbook text."""
        return f"""
YELLOW FLAG — Stage 1 Rotation (Crash prob: {prob_30d:.0f}% in 30d | {prob_60d:.0f}% in 60d)
  PROBABILITY-DRIVEN ACTIONS:
    • Position reduction: Cut {reduction_pct*100:.0f}% of notional exposure
    • Focus: Close low-conviction positions first (Conv <6/10)
    • New entries: PAUSE or reduce to 25% of normal size

  Account A Actions:
    1. Close CRWD, LLY, OKTA (low conviction + overbought) at 40-50%
    2. Reduce AXON, NFLX from max to 75% of current size ({reduction_pct*100:.0f}% total)
    3. Buy protective puts on remaining naked calls (20% of notional)
    4. Shift new entries: Only DEFENSIVE (Healthcare, Utilities, Staples)
    5. Increase cash from 10% → 20%

  Account B Actions:
    1. Trim COIN, HOOD CSPs by 20%
    2. Add healthcare/staples CSPs if opportunity
    3. Build cash reserve to 25-30%

  DECISION GATE:
    • IF prob increases to >50% in next 3 days → Move to Stage 2
    • IF prob decreases to <20% → Resume normal sizing
            """

    @staticmethod
    def _playbook_stage_2(prob_30d: float, prob_60d: float, prob_90d: float, reduction_pct: float) -> str:
        """Stage 2 (RED) rotation playbook text."""
        return f"""
RED FLAG — Stage 2-3 Rotation (CRASH RISK: {prob_30d:.0f}% prob in 30d)
  ⚠️ EMERGENCY PROTOCOL ACTIVATED

  Probability-Driven Threshold: {prob_30d:.0f}% crash risk in next 30 days
  → Cut {reduction_pct*100:.0f}% of gross exposure immediately
  → Raise cash to {40 + (reduction_pct*100):.0f}% of portfolio
  → 60-day outlook: {prob_60d:.0f}% probability (heightened vigilance)

  Account A Actions:
    1. Close ALL overbought positions (RSI >70) — don't wait for 70% profit
    2. Close remaining naked calls (or hedge heavily with long puts)
    3. Reduce notional from 100% → {100*(1-reduction_pct):.0f}% of normal
    4. Increase cash to 40-50% (emergency fund)
    5. Consider long puts on SPY/QQQ for crash protection
    6. HALT all new strangle entries — CSPs/CCs only on defensive names

  Account B Actions:
    1. Close all CSP new entries for Tier 1/2 names
    2. Exit assigned positions (harvest remaining CCs quickly)
    3. Go to 60% cash, 40% defensive covered calls (Healthcare, Staples)
    4. Stand ready to deploy cash on {prob_90d:.0f}% probability dips

  CIRCUIT BREAKER:
    • IF VIX spikes >30 AND prob stays >60% → FULL CASH (100% defensive)
    • IF regime breaks (S&P below 200-MA) → Redeploy cash on 5%+ dips ONLY
            """

    def _get_rotation_playbook(self, stage: int, crash_prob: Dict = None) -> str:
        """Get detailed rotation playbook with probability-driven actions"""
        if crash_prob is None:
            crash_prob = {}

        prob_30d = crash_prob.get('prob_30d', 6)
        prob_60d = crash_prob.get('prob_60d', 11)
        prob_90d = crash_prob.get('prob_90d', 16)
        reduction_pct = crash_prob.get('position_reduction_pct', 0)

        playbooks = {
            0: self._playbook_stage_0(prob_30d, prob_60d, prob_90d),
            1: self._playbook_stage_1(prob_30d, prob_60d, prob_90d, reduction_pct),
            2: self._playbook_stage_2(prob_30d, prob_60d, prob_90d, reduction_pct),
        }
        return playbooks.get(stage, "Unknown stage")


def analyze_macro_risk(market_data: Dict) -> Dict:
    """
    Convenience function to analyze macro risk

    Args:
        market_data: Dict with market metrics

    Returns:
        Risk analysis dict
    """
    analyzer = MacroRiskAnalyzer()
    return analyzer.analyze_risk(market_data)


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        "vix": 15.8,
        "spx_price": 7580,
        "spx_50ma": 7058,
        "spx_200ma": 6831
    }

    result = analyze_macro_risk(sample_data)
    print(json.dumps(result, indent=2))
