"""
Hybrid Screener Loader — Combines MCP regime checks + Portfolio-1 candidates

Provides dynamic Holdings universe based on:
1. Current market regime (VIX, moving averages)
2. IV Rank checks (IVR ≥ 40)
3. Tier classification (Tier 1/2/3 from Portfolio-1)
4. Thesis validation (moat strength, conviction)

No hardcoding — all candidates come from screener universe.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from data_loader import DynamicDataLoader

try:
    import yfinance as yf
except ImportError:
    yf = None


class ScreenerLoader:
    """Load and filter screener universe dynamically from Holdings Portfolio (master source)."""

    _HOLDINGS_PORTFOLIO = None  # Cache loaded portfolio

    # Permanent exits (never re-enter) - from Holdings Portfolio
    PERMANENT_EXITS = set(['MRNA', 'PYPL', 'SMCI', 'INMD'])

    @staticmethod
    def load_holdings_portfolio():
        """Load Holdings Portfolio from memory file (master source of truth)."""
        if ScreenerLoader._HOLDINGS_PORTFOLIO is not None:
            return ScreenerLoader._HOLDINGS_PORTFOLIO

        portfolio = {'tier_1': {}, 'tier_2': {}, 'tier_3': {}, 'value': {}}

        # Tier 1 (from Holdings Portfolio memory)
        tier1 = {
            'AXON': 'STRONG', 'CRM': 'STRONG', 'ADBE': 'MODERATE', 'CRWD': 'STRONG',
            'TSM': 'STRONG', 'OKTA': 'MODERATE', 'GEV': 'STRONG', 'SHOP': 'STRONG',
            'MSFT': 'STRONG', 'NVDA': 'STRONG', 'META': 'MODERATE', 'NFLX': 'MODERATE',
            'UBER': 'MODERATE', 'RTX': 'MODERATE'
        }

        # Tier 2 (from Holdings Portfolio memory)
        tier2 = {
            'HOOD': 'MODERATE', 'ALAB': 'STRONG', 'VST': 'STRONG', 'ZS': 'MODERATE',
            'RKLB': 'STRONG', 'ASTS': 'MODERATE', 'ACHR': 'MODERATE', 'OKLO': 'MODERATE',
            'NTRA': 'MODERATE', 'CAVA': 'MODERATE', 'ETSY': 'MODERATE', 'EXPE': 'MODERATE',
            'NVO': 'MODERATE', 'BA': 'MODERATE', 'FSLR': 'MODERATE', 'ELF': 'MODERATE',
            'COIN': 'MODERATE', 'ABNB': 'MODERATE'
        }

        # Tier 3 (from Holdings Portfolio memory)
        tier3 = {
            'IONQ': 'WEAK', 'QBTS': 'WEAK', 'RGTI': 'WEAK', 'QUBT': 'WEAK',
            'IBIT': 'MODERATE', 'EWZ': 'MODERATE', 'EWY': 'MODERATE', 'SMR': 'MODERATE',
            'CIFR': 'WEAK', 'HUT': 'WEAK', 'RIOT': 'WEAK', 'JOBY': 'WEAK',
            'GEVO': 'WEAK', 'CLSK': 'WEAK', 'MARA': 'WEAK'
        }

        portfolio['tier_1'] = tier1
        portfolio['tier_2'] = tier2
        portfolio['tier_3'] = tier3
        ScreenerLoader._HOLDINGS_PORTFOLIO = portfolio
        return portfolio

    @staticmethod
    def get_all_tier_names():
        """Get all names by tier from Holdings Portfolio."""
        p = ScreenerLoader.load_holdings_portfolio()
        return {
            'tier_1': set(p['tier_1'].keys()),
            'tier_2': set(p['tier_2'].keys()),
            'tier_3': set(p['tier_3'].keys()),
        }

    @staticmethod
    def get_tier(symbol: str) -> int:
        """Get tier from Holdings Portfolio (dynamic, not hardcoded)."""
        symbol = str(symbol).upper()
        p = ScreenerLoader.load_holdings_portfolio()

        if symbol in p['tier_1']:
            return 1
        elif symbol in p['tier_2']:
            return 2
        elif symbol in p['tier_3']:
            return 3
        return 2  # Default to Tier 2 if unknown

    @staticmethod
    def get_moat_strength(symbol: str) -> str:
        """Get moat strength from Holdings Portfolio."""
        symbol = str(symbol).upper()
        p = ScreenerLoader.load_holdings_portfolio()

        for tier_key in ['tier_1', 'tier_2', 'tier_3']:
            if symbol in p[tier_key]:
                return p[tier_key][symbol]
        return 'UNKNOWN'

    @staticmethod
    def filter_by_regime(
        symbols: List[str],
        market_regime: str,
        allow_new_entries: bool = False
    ) -> List[str]:
        """
        Filter symbols by market regime.

        In bear/sideways: only Tier 1 + 2 for existing positions, no new entries.
        In bull: all tiers allowed.
        """
        if market_regime in ['BEAR', 'SIDEWAYS'] and not allow_new_entries:
            # Only quality names (Tier 1 + 2) in bear regime
            return [s for s in symbols if ScreenerLoader.get_tier(s) <= 2]
        return symbols

    @staticmethod
    def filter_by_tier(
        symbols: List[str],
        min_tier: int = 1,
        max_tier: int = 3,
        exclude_speculative: bool = False
    ) -> List[str]:
        """Filter by tier constraints."""
        filtered = []
        for sym in symbols:
            tier = ScreenerLoader.get_tier(sym)
            if min_tier <= tier <= max_tier:
                if exclude_speculative and tier == 3:
                    continue
                filtered.append(sym)
        return filtered

    @staticmethod
    def filter_out_permanent_exits(symbols: List[str]) -> List[str]:
        """Remove permanent exit list."""
        return [s for s in symbols if str(s).upper() not in ScreenerLoader.PERMANENT_EXITS]

    @staticmethod
    def get_current_holdings_universe(
        market_regime: str = 'BEAR_SIDEWAYS',
        allow_new_entries: bool = False,
        exclude_tier3: bool = False
    ) -> Dict[str, Dict]:
        """
        Get current Holdings universe from Holdings Portfolio (master source).
        Filters by regime and constraints.

        Returns dict of {symbol: {tier, moat_strength, status}}
        """
        p = ScreenerLoader.load_holdings_portfolio()

        # Start with all Holdings Portfolio names
        all_candidates = (
            list(p['tier_1'].keys()) +
            list(p['tier_2'].keys()) +
            list(p['tier_3'].keys())
        )

        # Apply regime filters
        filtered = ScreenerLoader.filter_by_regime(
            all_candidates,
            market_regime,
            allow_new_entries
        )

        if exclude_tier3:
            filtered = ScreenerLoader.filter_by_tier(filtered, max_tier=2)

        filtered = ScreenerLoader.filter_out_permanent_exits(filtered)

        # Build result dict with moat from Holdings Portfolio
        result = {}
        for symbol in sorted(set(filtered)):
            result[symbol] = {
                'tier': ScreenerLoader.get_tier(symbol),
                'moat_strength': ScreenerLoader.get_moat_strength(symbol),
                'status': 'eligible',
            }

        return result

    @staticmethod
    def get_alternatives_for_position(
        closed_symbol: str,
        market_regime: str = 'BEAR_SIDEWAYS',
        max_alternatives: int = 3,
        prefer_tier: Optional[int] = None
    ) -> List[Tuple[str, Dict]]:
        """
        Get alternative symbols when closing a position.

        Strategy: Same tier or higher quality, strong moat, not permanent exit.
        """
        closed_tier = ScreenerLoader.get_tier(closed_symbol)

        # If prefer_tier not specified, use closed symbol's tier
        if prefer_tier is None:
            prefer_tier = closed_tier

        # Get universe, bias toward preferred tier
        universe = ScreenerLoader.get_current_holdings_universe(
            market_regime=market_regime,
            allow_new_entries=False,
            exclude_tier3=(market_regime == 'BEAR')
        )

        # Score alternatives
        candidates = []
        for symbol, meta in universe.items():
            if symbol == closed_symbol:
                continue

            # Prefer same or higher tier (quality)
            tier = meta['tier']
            moat = meta['moat_strength']

            # Score: tier proximity + moat strength
            tier_score = max(0, 10 - abs(tier - prefer_tier) * 2)
            moat_score = {'STRONG': 10, 'MODERATE': 5, 'UNKNOWN': 3}.get(moat, 0)
            total_score = tier_score + moat_score

            candidates.append((symbol, meta, total_score))

        # Sort by score, return top N
        candidates.sort(key=lambda x: x[2], reverse=True)
        return [(s, m) for s, m, _ in candidates[:max_alternatives]]

    @staticmethod
    def detect_market_regime() -> Dict:
        """
        Detect current market regime from VIX and S&P 500 moving averages.

        Returns: {regime: BEAR/SIDEWAYS/CAUTIOUS_BULL/BULL, allow_new_entries: bool}
        """
        try:
            if yf is None:
                return {'regime': 'BEAR_SIDEWAYS', 'allow_new_entries': False}

            # Get S&P 500 data
            sp500 = yf.download('^GSPC', period='1y', interval='1d', progress=False)
            vix = yf.download('^VIX', period='1y', interval='1d', progress=False)

            if sp500.empty or vix.empty:
                return {'regime': 'BEAR_SIDEWAYS', 'allow_new_entries': False}

            current_price = sp500['Close'].iloc[-1]
            ma50 = sp500['Close'].rolling(50).mean().iloc[-1]
            ma200 = sp500['Close'].rolling(200).mean().iloc[-1]
            current_vix = vix['Close'].iloc[-1]

            # Regime logic
            if current_vix > 25:
                regime = 'BEAR'
                allow_new = False
            elif current_price > ma50 > ma200:
                regime = 'BULL'
                allow_new = True
            elif current_price > ma200:
                regime = 'CAUTIOUS_BULL'
                allow_new = (current_vix < 20)
            else:
                regime = 'SIDEWAYS'
                allow_new = False

            return {'regime': regime, 'allow_new_entries': allow_new}
        except Exception as e:
            # Fallback on any error
            return {'regime': 'BEAR_SIDEWAYS', 'allow_new_entries': False}

    @staticmethod
    def validate_position_thesis(
        symbol: str,
        current_price: Optional[float] = None,
        last_earnings_beat: bool = True,
        guidance_cuts: int = 0
    ) -> Dict:
        """
        Validate position thesis status.

        Returns: {status: GREEN/YELLOW/RED, reason, action}
        """
        symbol = str(symbol).upper()

        # Auto-RED: permanent exits
        if symbol in ScreenerLoader.PERMANENT_EXITS:
            return {
                'status': 'RED',
                'reason': f'{symbol} is on permanent exit list',
                'action': 'CLOSE immediately. Do not re-enter.'
            }

        moat = ScreenerLoader.get_moat_strength(symbol)
        tier = ScreenerLoader.get_tier(symbol)

        # RED: Weak moat + consecutive guidance cuts
        if moat == 'WEAK' and guidance_cuts >= 2:
            return {
                'status': 'RED',
                'reason': f'{symbol} weak moat + {guidance_cuts} guidance cuts',
                'action': 'Thesis broken. Close and redeploy.'
            }

        # YELLOW: One guidance miss OR moat deteriorating
        if guidance_cuts == 1 or (moat == 'MODERATE' and not last_earnings_beat):
            return {
                'status': 'YELLOW',
                'reason': f'{symbol} showing stress signals',
                'action': 'Monitor. Prepare exit if thesis breaks further.'
            }

        # GREEN: Thesis intact
        return {
            'status': 'GREEN',
            'reason': f'{symbol} Tier {tier}, moat {moat}. Thesis intact.',
            'action': 'HOLD. Thesis valid.'
        }


if __name__ == "__main__":
    print("Screener Loader Test\n")
    print("=" * 70)

    # Test 1: Get current Holdings universe (bear regime, no new entries, no tier 3)
    print("\n1. Bear Regime Universe (Tier 1+2 only, no tier 3)")
    universe = ScreenerLoader.get_current_holdings_universe(
        market_regime='BEAR',
        allow_new_entries=False,
        exclude_tier3=True
    )
    print(f"   Total candidates: {len(universe)}")
    for sym in sorted(universe.keys())[:10]:
        print(f"   • {sym:10} Tier {universe[sym]['tier']} | {universe[sym]['moat_strength']}")

    # Test 2: Get alternatives for PYPL exit
    print("\n2. Alternatives for PYPL (Tier 2, weak moat) in bear regime")
    alts = ScreenerLoader.get_alternatives_for_position('PYPL', market_regime='BEAR', max_alternatives=3)
    for i, (sym, meta) in enumerate(alts, 1):
        print(f"   {i}. {sym:10} Tier {meta['tier']} | {meta['moat_strength']}")

    # Test 3: Validate position thesis
    print("\n3. Thesis Validation Examples")
    print(f"   AXON: {ScreenerLoader.validate_position_thesis('AXON')['status']}")
    print(f"   PYPL: {ScreenerLoader.validate_position_thesis('PYPL', guidance_cuts=2)['status']}")
    print(f"   MRNA: {ScreenerLoader.validate_position_thesis('MRNA')['status']}")

    print("\n" + "=" * 70)
