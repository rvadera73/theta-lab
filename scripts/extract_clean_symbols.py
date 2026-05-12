"""Extract clean ticker symbols from positions data"""

import pandas as pd
import sys
sys.path.insert(0, '/home/rahulvadera/projects/theta-lab/scripts')

from data_loader import DynamicDataLoader

# Load positions
positions_df, _ = DynamicDataLoader.load_all_data(
    positions_dir="data/positions",
    statements_dir="data/statements",
    use_live_positions=True
)

# Extract unique symbols
symbols = positions_df['symbol'].dropna().unique()

# Clean: Extract base ticker (first token, all caps, 1-5 chars)
clean_symbols = set()
for sym in symbols:
    # Extract first word/token
    token = str(sym).split()[0].upper()
    # Keep only if it looks like a ticker (2-5 uppercase letters, no special chars except . or -) 
    if 2 <= len(token) <= 5 and token.replace('.', '').replace('-', '').isalpha():
        clean_symbols.add(token)

clean_symbols = sorted(clean_symbols)
print(f"✅ Found {len(clean_symbols)} valid ticker symbols:")
print(f"  Sample: {clean_symbols[:20]}")
print(f"\n  Full list: {', '.join(clean_symbols)}")
print(f"\nTotal valid tickers: {len(clean_symbols)}")
