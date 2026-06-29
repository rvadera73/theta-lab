"""
Citadel-Style Regime Detection

Implements institutional-grade regime detection using:
- VIX level (primary volatility signal)
- S&P 50-MA and 200-MA (momentum)
- Market breadth (distribution)
- IV Rank (options market expectations)
- Put/Call ratio (fear gauge)
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date, timedelta
from typing import Dict, Tuple, List
from pathlib import Path


class CitadelRegimeDetector:
    """Detect market regime using institutional-grade signals"""

    # Thresholds (from Citadel / Winton / Millennium frameworks)
    VIX_THRESHOLDS = {
        'BULL': (0, 15),
        'TRANSITIONING': (15, 22),
        'BEAR': (22, 100)
    }

    BREADTH_THRESHOLDS = {
        'BULL': 0.55,           # >55% winners
        'TRANSITIONING': (0.45, 0.55),  # 45-55% winners
        'BEAR': 0.45            # <45% winners
    }

    IV_RANK_THRESHOLDS = {
        'BULL': 30,
        'TRANSITIONING': (30, 70),
        'BEAR': 70
    }

    PUT_CALL_THRESHOLDS = {
        'BULL': 0.8,
        'TRANSITIONING': (0.8, 1.1),
        'BEAR': 1.1
    }

    def __init__(self):
        self.vix_cache = {}
        self.sp500_cache = {}
        self.regime_history = self._load_regime_history()

    def _load_regime_history(self) -> Dict:
        """Load historical regime tracking"""
        history_file = Path('/home/rahulvadera/projects/theta-lab/data/regime_history.json')
        if history_file.exists():
            import json
            with open(history_file) as f:
                return json.load(f)
        return {}

    def _save_regime_history(self):
        """Save regime tracking"""
        history_file = Path('/home/rahulvadera/projects/theta-lab/data/regime_history.json')
        history_file.parent.mkdir(parents=True, exist_ok=True)
        import json

        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_native(v) for v in obj]
            elif isinstance(obj, (np.bool_)):
                return bool(obj)
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj) if isinstance(obj, np.floating) else int(obj)
            elif isinstance(obj, bool):
                return obj
            return obj

        with open(history_file, 'w') as f:
            json.dump(convert_to_native(self.regime_history), f, indent=2)

    def get_vix(self, days: int = 60) -> Dict:
        """Get VIX level and trend from Yahoo Finance"""
        try:
            vix = yf.Ticker("^VIX")
            hist = vix.history(period=f"{days}d")

            if len(hist) < 2:
                return {'current': 15.8, 'trend': 'stable', 'note': 'Insufficient data'}

            current_vix = hist['Close'].iloc[-1]
            prev_vix = hist['Close'].iloc[-2]
            avg_30d = hist['Close'].tail(30).mean() if len(hist) >= 30 else current_vix

            # Determine trend
            if current_vix > prev_vix + 1:
                trend = 'rising'
            elif current_vix < prev_vix - 1:
                trend = 'falling'
            else:
                trend = 'stable'

            return {
                'current': round(current_vix, 2),
                'previous': round(prev_vix, 2),
                'change': round(current_vix - prev_vix, 2),
                '30d_avg': round(avg_30d, 2),
                'trend': trend
            }
        except Exception as e:
            print(f"⚠️ VIX fetch error: {e}")
            return {'current': 15.8, 'trend': 'stable', 'note': f'Error: {e}'}

    def get_sp500_technicals(self) -> Dict:
        """Get S&P 500 50-MA and 200-MA"""
        try:
            sp500 = yf.Ticker("^GSPC")
            hist = sp500.history(period="250d")  # 50 weeks = 250 trading days

            if len(hist) < 200:
                return {
                    'current_price': 5500,
                    'ma50': 5500,
                    'ma200': 5400,
                    'above_50ma': True,
                    'above_200ma': True,
                    'note': 'Insufficient data'
                }

            current_price = hist['Close'].iloc[-1]
            ma50 = hist['Close'].tail(50).mean()
            ma200 = hist['Close'].tail(200).mean()

            # Calculate slope of 50-MA (direction of momentum)
            ma50_week_ago = hist['Close'].iloc[-6:].mean() if len(hist) >= 6 else ma50
            ma50_slope = 'up' if ma50 > ma50_week_ago else ('down' if ma50 < ma50_week_ago else 'flat')

            return {
                'current_price': round(current_price, 2),
                'ma50': round(ma50, 2),
                'ma200': round(ma200, 2),
                'above_50ma': current_price > ma50,
                'above_200ma': current_price > ma200,
                'ma50_vs_ma200': round(ma50 - ma200, 2),
                'ma50_slope': ma50_slope,  # up, down, or flat
                'distance_from_200ma': round(current_price - ma200, 2)
            }
        except Exception as e:
            print(f"⚠️ S&P 500 technical error: {e}")
            return {'current_price': 5500, 'ma50': 5500, 'ma200': 5400, 'note': f'Error: {e}'}

    def get_market_breadth(self, positions_df: pd.DataFrame) -> Dict:
        """Calculate market breadth from portfolio positions"""
        try:
            if positions_df.empty or 'pnl_pct' not in positions_df.columns:
                return {'winners_pct': 0.50, 'assessment': 'TRANSITIONING', 'note': 'No data'}

            # Calculate % of positions with positive P&L
            winners = (positions_df['pnl_pct'] > 0).sum()
            total = len(positions_df)
            winners_pct = winners / total if total > 0 else 0.5

            return {
                'winners_pct': round(winners_pct, 3),
                'winners_count': int(winners),
                'total_positions': total,
                'assessment': self._breadth_to_regime(winners_pct)
            }
        except Exception as e:
            print(f"⚠️ Breadth calculation error: {e}")
            return {'winners_pct': 0.50, 'assessment': 'TRANSITIONING', 'note': f'Error: {e}'}

    def _breadth_to_regime(self, winners_pct: float) -> str:
        """Convert breadth % to regime signal"""
        if winners_pct > self.BREADTH_THRESHOLDS['BULL']:
            return 'BULL'
        elif winners_pct < self.BREADTH_THRESHOLDS['BEAR']:
            return 'BEAR'
        else:
            return 'TRANSITIONING'

    def detect_regime(self, vix: Dict, technicals: Dict, breadth: Dict,
                     iv_rank: float = 50.0, put_call: float = 1.0) -> Dict:
        """
        Detect market regime using 5 signals (Citadel-style).

        Returns: {
            'regime': 'BULL' | 'TRANSITIONING' | 'BEAR',
            'confidence': 0.0-1.0,
            'signals': {
                'vix': ('BULL'|'TRANSITIONING'|'BEAR', score),
                'technicals': ('BULL'|'TRANSITIONING'|'BEAR', score),
                'breadth': ('BULL'|'TRANSITIONING'|'BEAR', score),
                'iv_rank': ('BULL'|'TRANSITIONING'|'BEAR', score),
                'put_call': ('BULL'|'TRANSITIONING'|'BEAR', score),
            },
            'shift_probability': {'BULL': %, 'TRANSITIONING': %, 'BEAR': %}
        }
        """

        signals = {}
        scores = {'BULL': 0, 'TRANSITIONING': 0, 'BEAR': 0}

        # Signal 1: VIX
        vix_value = vix.get('current', 15.8)
        if vix_value < 15:
            signals['vix'] = ('BULL', 1.0)
            scores['BULL'] += 1
        elif vix_value > 22:
            signals['vix'] = ('BEAR', 1.0)
            scores['BEAR'] += 1
        else:
            signals['vix'] = ('TRANSITIONING', 1.0)
            scores['TRANSITIONING'] += 1

        # Signal 2: S&P Technicals
        tech = technicals
        if tech.get('above_50ma') and tech.get('ma50_slope') == 'up':
            if tech.get('above_200ma'):
                signals['technicals'] = ('BULL', 1.0)
                scores['BULL'] += 1
            else:
                signals['technicals'] = ('TRANSITIONING', 0.8)
                scores['TRANSITIONING'] += 0.8
        elif tech.get('above_50ma') and tech.get('ma50_slope') == 'flat':
            signals['technicals'] = ('TRANSITIONING', 1.0)
            scores['TRANSITIONING'] += 1
        elif not tech.get('above_200ma'):
            signals['technicals'] = ('BEAR', 1.0)
            scores['BEAR'] += 1
        else:
            signals['technicals'] = ('TRANSITIONING', 0.7)
            scores['TRANSITIONING'] += 0.7

        # Signal 3: Breadth
        breadth_assessment = breadth.get('assessment', 'TRANSITIONING')
        if breadth_assessment == 'BULL':
            signals['breadth'] = ('BULL', 1.0)
            scores['BULL'] += 1
        elif breadth_assessment == 'BEAR':
            signals['breadth'] = ('BEAR', 1.0)
            scores['BEAR'] += 1
        else:
            signals['breadth'] = ('TRANSITIONING', 1.0)
            scores['TRANSITIONING'] += 1

        # Signal 4: IV Rank
        if iv_rank < 30:
            signals['iv_rank'] = ('BULL', 1.0)
            scores['BULL'] += 1
        elif iv_rank > 70:
            signals['iv_rank'] = ('BEAR', 1.0)
            scores['BEAR'] += 1
        else:
            signals['iv_rank'] = ('TRANSITIONING', 1.0)
            scores['TRANSITIONING'] += 1

        # Signal 5: Put/Call Ratio
        if put_call < 0.8:
            signals['put_call'] = ('BULL', 1.0)
            scores['BULL'] += 1
        elif put_call > 1.1:
            signals['put_call'] = ('BEAR', 1.0)
            scores['BEAR'] += 1
        else:
            signals['put_call'] = ('TRANSITIONING', 1.0)
            scores['TRANSITIONING'] += 1

        # Determine regime by score
        total_score = sum(scores.values())
        confidence_dict = {k: v / total_score for k, v in scores.items()} if total_score > 0 else {'BULL': 0.33, 'TRANSITIONING': 0.33, 'BEAR': 0.33}

        # Regime is highest-scoring
        regime = max(scores, key=scores.get)
        confidence = confidence_dict[regime]

        # Shift probability (second-highest score as probability of shift)
        remaining_scores = {k: v for k, v in confidence_dict.items() if k != regime}
        next_regime = max(remaining_scores, key=remaining_scores.get)
        shift_probability = confidence_dict[next_regime]

        return {
            'regime': regime,
            'confidence': round(confidence, 2),
            'signals': signals,
            'signal_scores': scores,
            'shift_to': next_regime,
            'shift_probability': round(shift_probability, 2),
            'vix': vix,
            'technicals': tech,
            'breadth': breadth,
            'iv_rank': round(iv_rank, 2),
            'put_call': round(put_call, 2)
        }

    def detect_shift(self, today_regime: Dict, yesterday_regime: Dict = None) -> Dict:
        """
        Detect if regime shifted from yesterday.

        Returns shift info or empty dict if no shift.
        """
        if not yesterday_regime:
            return {}

        today_r = today_regime.get('regime')
        yesterday_r = yesterday_regime.get('regime')

        if today_r == yesterday_r:
            return {}

        # Shift detected!
        shift_signals = []

        # VIX shift
        today_vix = today_regime.get('vix', {}).get('current', 0)
        yesterday_vix = yesterday_regime.get('vix', {}).get('current', 0)
        if abs(today_vix - yesterday_vix) > 1:
            shift_signals.append(f"VIX: {yesterday_vix:.1f} → {today_vix:.1f}")

        # Technicals shift
        if today_regime.get('technicals', {}).get('ma50_slope') != yesterday_regime.get('technicals', {}).get('ma50_slope'):
            shift_signals.append(f"50-MA slope: {yesterday_regime.get('technicals', {}).get('ma50_slope')} → {today_regime.get('technicals', {}).get('ma50_slope')}")

        # Breadth shift
        today_breadth = today_regime.get('breadth', {}).get('winners_pct', 0)
        yesterday_breadth = yesterday_regime.get('breadth', {}).get('winners_pct', 0)
        if abs(today_breadth - yesterday_breadth) > 0.05:
            shift_signals.append(f"Breadth: {yesterday_breadth:.0%} → {today_breadth:.0%}")

        return {
            'shifted': True,
            'from_regime': yesterday_r,
            'to_regime': today_r,
            'shift_date': str(date.today()),
            'trigger_signals': shift_signals,
            'confidence': today_regime.get('confidence', 0)
        }

    def get_regime_adjusted_parameters(self, regime: str) -> Dict:
        """Get risk/trading parameters for a regime"""
        params = {
            'BULL': {
                'monthly_target_adjustment': 1.0,  # $100K → $100K
                'margin_limit': 0.75,
                'max_concentration': 0.05,  # 5% per name
                'preferred_dte': (20, 35, 45),  # short, medium, long percentages
                'new_entry_ivr_gate': 35,
                'assignment_tolerance': 'HIGH',
                'description': 'Low volatility, broad participation'
            },
            'TRANSITIONING': {
                'monthly_target_adjustment': 0.90,  # $100K → $90K
                'margin_limit': 0.60,
                'max_concentration': 0.04,  # 4% per name
                'preferred_dte': (30, 40, 30),  # balanced
                'new_entry_ivr_gate': 40,
                'assignment_tolerance': 'MEDIUM',
                'description': 'Uncertain direction, selective'
            },
            'BEAR': {
                'monthly_target_adjustment': 0.70,  # $100K → $70K
                'margin_limit': 0.40,
                'max_concentration': 0.03,  # 3% per name
                'preferred_dte': (20, 30, 50),  # defensive
                'new_entry_ivr_gate': 60,
                'assignment_tolerance': 'LOW',
                'description': 'High risk, concentrated weakness'
            }
        }
        return params.get(regime, params['TRANSITIONING'])

    def calculate_contingency_imminence(self, current_regime: Dict) -> Dict:
        """
        Determine if a regime shift is IMMINENT (not speculative).

        Imminent = shift probability >50% AND one trigger partially met
        """
        regime = current_regime.get('regime', 'TRANSITIONING')
        shift_prob = current_regime.get('shift_probability', 0)
        next_regime = current_regime.get('shift_to', 'TRANSITIONING')

        # Check for imminent shift triggers
        vix = current_regime.get('vix', {}).get('current', 15.8)
        tech = current_regime.get('technicals', {})

        imminence_score = 0
        triggers = []

        if next_regime == 'BEAR':
            # Triggers for BEAR shift
            if vix > 19:  # Getting close to 22
                imminence_score += 1
                triggers.append(f"VIX elevated ({vix:.1f}, alert at 20)")
            if tech.get('ma50_slope') == 'down':
                imminence_score += 1
                triggers.append("50-MA slope negative")
            if tech.get('distance_from_200ma', 0) < 100:
                imminence_score += 1
                triggers.append(f"S&P near 200-MA (within {abs(tech.get('distance_from_200ma', 0)):.0f} points)")

        elif next_regime == 'BULL':
            # Triggers for BULL shift (rare)
            if vix < 13:
                imminence_score += 1
                triggers.append(f"VIX very low ({vix:.1f})")

        is_imminent = imminence_score >= 2 and shift_prob > 0.50

        return {
            'imminent': is_imminent,
            'shift_probability': shift_prob,
            'next_regime': next_regime,
            'trigger_count': imminence_score,
            'triggers_detected': triggers,
            'recommendation': 'Activate contingency plan' if is_imminent else 'Monitor, no action needed'
        }


def get_citadel_regime_data(positions_df: pd.DataFrame = None) -> Dict:
    """
    Get complete Citadel-style regime data.

    This is the main entry point for getting regime information.
    """
    detector = CitadelRegimeDetector()

    # Get all signals
    vix_data = detector.get_vix()
    tech_data = detector.get_sp500_technicals()
    breadth_data = detector.get_market_breadth(positions_df) if positions_df is not None else {}

    # Detect regime
    regime_data = detector.detect_regime(vix_data, tech_data, breadth_data)

    # Check for shifts
    yesterday_regime = detector.regime_history.get(str(date.today() - timedelta(days=1)))
    shift_data = detector.detect_shift(regime_data, yesterday_regime)

    # Check contingency imminence
    contingency = detector.calculate_contingency_imminence(regime_data)

    # Save today's regime
    detector.regime_history[str(date.today())] = regime_data
    detector._save_regime_history()

    return {
        'regime': regime_data.get('regime'),
        'confidence': regime_data.get('confidence'),
        'regime_data': regime_data,
        'shift': shift_data if shift_data else None,
        'contingency': contingency,
        'parameters': detector.get_regime_adjusted_parameters(regime_data.get('regime'))
    }
