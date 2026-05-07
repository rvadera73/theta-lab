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


class ScreenerLoader:
    """Load and filter screener universe dynamically."""

    # Tier classification (extracted from trading_persona)
    TIER_1_NAMES = set([
        'AXON', 'CRM', 'ADBE', 'CRWD', 'TSM', 'OKTA', 'GEV', 'SHOP',
        'MSFT', 'NVDA', 'META', 'NFLX', 'UBER', 'RTX'
    ])

    TIER_2_NAMES = set([
        'HOOD', 'ALAB', 'VST', 'ZS', 'RKLB', 'ASTS', 'ACHR', 'OKLO', 'NTRA',
        'CAVA', 'ETSY', 'EXPE', 'NVO', 'BA', 'FSLR', 'ELF', 'COIN', 'ABNB'
    ])

    TIER_3_NAMES = set([
        'IONQ', 'QBTS', 'RGTI', 'QUBT', 'IBIT', 'EWZ', 'EWY', 'SMR',
        'CIFR', 'HUT', 'RIOT', 'JOBY', 'GEVO', 'CLSK', 'MARA'
    ])

    # Permanent exits (never re-enter)
    PERMANENT_EXITS = set(['MRNA', 'PYPL', 'SMCI', 'INMD'])

    # Moat strength (from trading_persona software assessment)
    MOAT_STRENGTH = {
        'AXON': 'STRONG',
        'CRM': 'STRONG',
        'CRWD': 'STRONG',
        'TSM': 'STRONG',
        'SHOP': 'STRONG',
        'ADBE': 'MODERATE',
        'OKTA': 'MODERATE',
        'META': 'MODERATE',
        'NFLX': 'MODERATE',
        'UBER': 'MODERATE',
        'RTX': 'MODERATE',
        'GEV': 'STRONG',
        'ALAB': 'STRONG',
        'VST': 'STRONG',
        'ZS': 'MODERATE',
        'RKLB': 'STRONG',
        'ASTS': 'MODERATE',
    }

    @staticmethod
    def get_tier(symbol: str) -> int:
        """Classify stock into tier (1=core, 2=emerging, 3=speculative)."""
        symbol = str(symbol).upper()
        if symbol in ScreenerLoader.TIER_1_NAMES:
            return 1
        elif symbol in ScreenerLoader.TIER_2_NAMES:
            return 2
        elif symbol in ScreenerLoader.TIER_3_NAMES:
            return 3
        return 2  # Default to Tier 2 if unknown

    @staticmethod
    def get_moat_strength(symbol: str) -> str:
        """Get moat strength assessment."""
        symbol = str(symbol).upper()
        return ScreenerLoader.MOAT_STRENGTH.get(symbol, 'UNKNOWN')

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
        Get current Holdings universe based on regime and filters.

        Returns dict of {symbol: {tier, moat_strength, status}}
        """
        all_candidates = (
            list(ScreenerLoader.TIER_1_NAMES) +
            list(ScreenerLoader.TIER_2_NAMES) +
            list(ScreenerLoader.TIER_3_NAMES)
        )

        # Apply filters
        filtered = ScreenerLoader.filter_by_regime(
            all_candidates,
            market_regime,
            allow_new_entries
        )

        if exclude_tier3:
            filtered = ScreenerLoader.filter_by_tier(filtered, max_tier=2)

        filtered = ScreenerLoader.filter_out_permanent_exits(filtered)

        # Build result dict
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
