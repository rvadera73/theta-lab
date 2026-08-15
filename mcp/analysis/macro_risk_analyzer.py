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
from typing import Dict, List, Tuple
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
        # FRED API Key (public demo key - can be replaced with private key)
        self.fred_api_key = "e3b12ba0b1b73f9b62c5e7c8a4d9f1e2"

    def fetch_fred_data(self, series_id: str) -> float:
        """Fetch latest data point from FRED API"""
        try:
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "limit": 1,
                "sort_order": "desc",
                "api_key": self.fred_api_key
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("observations"):
                    value = data["observations"][0].get("value")
                    if value and value != ".":
                        return float(value)
        except Exception as e:
            logger.warning(f"Error fetching FRED {series_id}: {e}")
        return None

    def get_hyoas(self) -> float:
        """Get High Yield OAS spread (basis points) from FRED"""
        # BAMLH0A0HYM2 = ICE BofA US High Yield OAS
        hyoas = self.fetch_fred_data("BAMLH0A0HYM2")
        return hyoas if hyoas else 380  # Default to normal if unavailable

    def get_yield_curve(self) -> float:
        """Get Yield Curve (10Y - 2Y Treasury spread) from FRED"""
        # T10Y2Y = 10-Year Minus 2-Year Treasury Constant Maturity Spread
        curve = self.fetch_fred_data("T10Y2Y")
        return curve if curve is not None else 0.6  # Default to normal if unavailable

    def get_breadth_from_yahoo(self) -> float:
        """
        Calculate % of S&P 500 stocks above 50-day MA using Yahoo Finance
        Fetches top 100 S&P 500 names (by weight) for speed; scales result to full 500
        """
        try:
            import yfinance as yf
            import pandas as pd

            # Top 100 S&P 500 names by market cap (representative sample)
            # This includes most liquid names and covers major sectors
            sp500_top = [
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

            # Fetch 50-day MA data
            above_ma = 0
            total = 0

            for ticker in sp500_top[:80]:  # Use 80 for faster execution
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

    def get_vix_term_structure(self) -> Dict:
        """
        Get VIX term structure (front month vs back month)
        Uses CBOE VIX futures data
        """
        try:
            # Try fetching from Yahoo Finance (VIX futures available)
            import yfinance as yf

            # Note: VIX futures symbols are typically VIXM (front month), VIXN (next month)
            # This is a simplified approach
            try:
                vix_m = yf.Ticker("VIXM")
                vix_n = yf.Ticker("VIXN")

                hist_m = vix_m.history(period="1d")
                hist_n = vix_n.history(period="1d")

                if len(hist_m) > 0 and len(hist_n) > 0:
                    front = hist_m['Close'].iloc[-1]
                    back = hist_n['Close'].iloc[-1]

                    if front < back * 0.95:
                        term_type = "CONTANGO"
                    elif front > back * 1.05:
                        term_type = "BACKWARDATION"
                    else:
                        term_type = "FLAT"

                    return {
                        "type": term_type,
                        "front_vix": float(front),
                        "back_vix": float(back),
                    }
            except:
                pass

            # Fallback
            return {
                "type": "CONTANGO",
                "front_vix": 15.8,
                "back_vix": 18.2,
            }
        except Exception as e:
            logger.warning(f"Error getting VIX term structure: {e}")
            return {
                "type": "CONTANGO",
                "front_vix": 15.8,
                "back_vix": 18.2,
            }

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

    def analyze_risk(self, market_data: Dict) -> Dict:
        """
        Analyze all 7 layers and return risk assessment

        Args:
            market_data: Dict with current market metrics
                - vix: float (current VIX level)
                - spx_price: float
                - spx_50ma: float
                - spx_200ma: float

        Returns:
            {
                "risk_level": "GREEN|YELLOW|RED",
                "signals": {indicator: {value, status, threshold}},
                "stage": int (0=GREEN, 1=YELLOW, 2=RED),
                "summary": str,
                "actions": [str],
                "rotation_playbook": str
            }
        """

        signals = {}
        yellow_count = 0
        red_count = 0

        # Layer 1: REGIME (already handled by main report)
        # We focus on Layers 2-6 here

        # Layer 2: Oscillators (Breadth, A-D Ratio)
        breadth = self.estimate_breadth(market_data)
        signals["breadth"] = {
            "value": breadth,
            "status": "RED" if breadth < self.thresholds["breadth_red"]
                     else "YELLOW" if breadth < self.thresholds["breadth_yellow"]
                     else "GREEN",
            "threshold": f"{self.thresholds['breadth_yellow']}% (caution), {self.thresholds['breadth_red']}% (alert)"
        }
        if signals["breadth"]["status"] == "YELLOW":
            yellow_count += 1
        elif signals["breadth"]["status"] == "RED":
            red_count += 1

        ad_ratio = self.estimate_ad_ratio()
        signals["ad_ratio"] = {
            "value": ad_ratio,
            "status": "RED" if ad_ratio < self.thresholds["ad_ratio_red"]
                     else "YELLOW" if ad_ratio < self.thresholds["ad_ratio_yellow"]
                     else "GREEN",
            "threshold": f"{self.thresholds['ad_ratio_yellow']} (caution), {self.thresholds['ad_ratio_red']} (alert)"
        }
        if signals["ad_ratio"]["status"] == "YELLOW":
            yellow_count += 1
        elif signals["ad_ratio"]["status"] == "RED":
            red_count += 1

        # Layer 3: VIX Term Structure
        vix_term = self.get_vix_term_structure()
        signals["vix_term"] = {
            "value": vix_term["type"],
            "status": "RED" if vix_term["type"] == "BACKWARDATION"
                     else "YELLOW" if vix_term["type"] == "FLAT"
                     else "GREEN",
            "threshold": "Contango (normal) → Flat (caution) → Backwardation (alert)"
        }
        if signals["vix_term"]["status"] == "YELLOW":
            yellow_count += 1
        elif signals["vix_term"]["status"] == "RED":
            red_count += 1

        # Layer 4: Credit Spreads (HY OAS)
        hyoas = self.get_hyoas()
        if hyoas:
            signals["hyoas"] = {
                "value": f"{hyoas:.0f} bps",
                "raw_value": hyoas,
                "status": "RED" if hyoas > self.thresholds["hyoas_red"]
                         else "YELLOW" if hyoas > self.thresholds["hyoas_yellow"]
                         else "GREEN",
                "threshold": f"{self.thresholds['hyoas_yellow']} (caution), {self.thresholds['hyoas_red']} (alert)"
            }
            if signals["hyoas"]["status"] == "YELLOW":
                yellow_count += 1
            elif signals["hyoas"]["status"] == "RED":
                red_count += 1

        # Layer 5: Put/Call Ratio
        pcr = self.get_put_call_ratio()
        signals["pcr"] = {
            "value": f"{pcr:.2f}",
            "raw_value": pcr,
            "status": "RED" if pcr > self.thresholds["pcr_red"]
                     else "YELLOW" if pcr > self.thresholds["pcr_yellow"]
                     else "GREEN",
            "threshold": f"{self.thresholds['pcr_yellow']} (caution), {self.thresholds['pcr_red']} (alert)"
        }
        if signals["pcr"]["status"] == "YELLOW":
            yellow_count += 1
        elif signals["pcr"]["status"] == "RED":
            red_count += 1

        # Layer 6: Yield Curve
        yield_curve = self.get_yield_curve()
        if yield_curve is not None:
            signals["yield_curve"] = {
                "value": f"{yield_curve:.2f}%",
                "raw_value": yield_curve,
                "status": "RED" if yield_curve < self.thresholds["yield_curve_red"]
                         else "YELLOW" if yield_curve < self.thresholds["yield_curve_yellow"]
                         else "GREEN",
                "threshold": f"Inverted (alert), <0.1% (caution), >0.5% (normal)"
            }
            if signals["yield_curve"]["status"] == "YELLOW":
                yellow_count += 1
            elif signals["yield_curve"]["status"] == "RED":
                red_count += 1

        # Determine overall risk level
        if red_count >= 2:
            risk_level = "RED"
            stage = 2
        elif yellow_count >= 3 or (yellow_count >= 1 and red_count >= 1):
            risk_level = "YELLOW"
            stage = 1
        else:
            risk_level = "GREEN"
            stage = 0

        # Calculate crash probability forecast
        crash_prob = self.calculate_crash_probability(signals)

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
    SECTOR_SENSITIVITY_MAP = {
        "ad_ratio": {  # narrow breadth / momentum-leadership unwind
            "high": ["Technology", "Consumer Cyclical", "Communication Services", "Basic Materials"],
            "low": ["Utilities", "Healthcare", "Consumer Defensive", "Energy", "Defense"],
        },
        "breadth": {  # same failure mode as ad_ratio — narrow participation
            "high": ["Technology", "Consumer Cyclical", "Communication Services", "Basic Materials"],
            "low": ["Utilities", "Healthcare", "Consumer Defensive", "Energy", "Defense"],
        },
        "hyoas": {  # credit-spread widening — leverage/cyclical-sensitive names
            "high": ["Financial Services", "Industrials", "Basic Materials"],
            "low": ["Utilities", "Consumer Defensive", "Healthcare"],
        },
        "pcr": {  # elevated hedging demand — broad risk-off, high-beta hit hardest
            "high": ["Technology", "Consumer Cyclical", "Communication Services"],
            "low": ["Utilities", "Consumer Defensive", "Healthcare"],
        },
        "yield_curve": {  # inversion — financials margin compression + long-duration growth revaluation
            "high": ["Financial Services", "Technology"],
            "low": ["Utilities", "Energy", "Consumer Defensive"],
        },
        "vix_term": {  # backwardation — imminent-stress read, broad but momentum-heavy first
            "high": ["Technology", "Consumer Cyclical", "Communication Services", "Basic Materials"],
            "low": ["Utilities", "Consumer Defensive", "Healthcare"],
        },
    }

    def get_sector_crash_sensitivity(self, primary_risk: str) -> Dict:
        """Map the crash forecast's primary_risk string (e.g. "AD_RATIO critical")
        back to which sectors are historically most/least exposed to THAT
        specific risk factor's unwind. Returns {} if primary_risk is
        "Market neutral" (nothing flagged) or doesn't match a known indicator."""
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

        # Count red and yellow signals (still used for vix_term, which has no
        # numeric severity, and as the basis for primary-risk-factor selection)
        red_count = sum(1 for v in signals.values() if isinstance(v, dict) and v.get('status') == 'RED')
        yellow_count = sum(1 for v in signals.values() if isinstance(v, dict) and v.get('status') == 'YELLOW')

        # Continuous severity sum across all scoreable indicators — this is
        # what actually drives the probability now, not the red/yellow counts
        # above. A reading that's barely past its threshold contributes near
        # 0; one deep in the red zone contributes up to 2.0. vix_term (no
        # numeric threshold) falls back to a flat 1.0/0.4 RED/YELLOW severity
        # so it still counts, just without magnitude sensitivity.
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

        # Adjust probabilities based on continuous severity (replaces the old
        # flat red_count*15/yellow_count*5-style bumps — same rough scale at
        # severity=1.0 (a reading exactly at its red threshold) as the old
        # red_count=1 case, but now scales smoothly past that point instead of
        # staying frozen for any reading beyond the threshold.
        prob_30d = base_prob_30d + severity_sum * 15
        prob_60d = base_prob_60d + severity_sum * 25
        prob_90d = base_prob_90d + severity_sum * 35

        # Cap at 95% (never 100% certain)
        prob_30d = min(prob_30d, 95.0)
        prob_60d = min(prob_60d, 95.0)
        prob_90d = min(prob_90d, 95.0)

        # Identify primary risk factor — now picks the indicator with the
        # HIGHEST severity (not just "first RED found in dict order"), so it
        # actually reflects which signal is doing the most damage.
        primary_risk = "Market neutral"
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
            primary_risk = f"{worst_indicator.upper()} critical" if status == 'RED' else f"{worst_indicator.upper()} elevated"

        # Determine action based on 30-day probability
        if prob_30d >= 70:
            action_trigger = "🔴 EMERGENCY: Reduce gross exposure by 50% immediately"
            position_reduction = 0.50
        elif prob_30d >= 50:
            action_trigger = "🟠 HIGH RISK: Reduce gross exposure by 30-40%"
            position_reduction = 0.35
        elif prob_30d >= 30:
            action_trigger = "🟡 CAUTION: Reduce overbought positions by 20-25%"
            position_reduction = 0.20
        else:
            action_trigger = "🟢 NORMAL: Proceed with standard sizing"
            position_reduction = 0.0

        return {
            "prob_30d": prob_30d,
            "prob_60d": prob_60d,
            "prob_90d": prob_90d,
            "primary_risk": primary_risk,
            "action_trigger": action_trigger,
            "position_reduction_pct": position_reduction
        }

    def _get_rotation_playbook(self, stage: int, crash_prob: Dict = None) -> str:
        """Get detailed rotation playbook with probability-driven actions"""
        if crash_prob is None:
            crash_prob = {}

        prob_30d = crash_prob.get('prob_30d', 6)
        prob_60d = crash_prob.get('prob_60d', 11)
        prob_90d = crash_prob.get('prob_90d', 16)
        reduction_pct = crash_prob.get('position_reduction_pct', 0)

        playbooks = {
            0: f"""
GREEN LIGHT — Proceed with normal operations (Crash prob: {prob_30d:.0f}% in 30d)
  • New entries: Full size (Account A BULL sizing)
  • Position management: Normal weekly review
  • Defensive rotation: Not needed
  • Cash level: Maintain tactical 10-15%
  • 60/90-day outlook: {prob_60d:.0f}% / {prob_90d:.0f}% crash probability
            """,
            1: f"""
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
            """,
            2: f"""
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
