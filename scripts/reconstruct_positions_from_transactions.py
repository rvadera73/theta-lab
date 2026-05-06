"""
Reconstruct current positions from transaction history (transactions-only mode).
Use when Schwab position CSVs are stale and you have current transaction exports.

Use case: May 6 report needs current positions but April 25 CSV is 11 days old.
Solution: Parse all transactions from Jan 1-May 6, calculate net position state.

Usage: python3 reconstruct_positions_from_transactions.py
Output: Reconstructed positions suitable for snapshot generation
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "statements"


def find_latest_transactions() -> str | None:
    """Find most recent Individual_XXX232 transaction CSV (Account A). Falls back to Empower consolidated."""
    candidates = list(DATA_DIR.glob("*XXX232*Transactions*.csv"))
    if candidates:
        return str(max(candidates, key=lambda x: x.stat().st_mtime))

    # Fallback to Empower consolidated
    candidates = list(DATA_DIR.glob("*.csv"))
    for f in sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True):
        name = f.name
        if re.search(r"\d{4}-\d{2}-\d{2}.*thru.*\d{4}-\d{2}-\d{2}", name, re.IGNORECASE):
            if "transaction" in name.lower():
                return str(f)
    return None


def reconstruct_from_transactions(txn_file: str) -> dict:
    """
    Rebuild position state from transaction history.
    Returns dict of {symbol: {qty, first_date, last_date, transactions}}
    """
    positions = defaultdict(lambda: {
        "qty": 0,
        "contracts": defaultdict(lambda: {"qty": 0, "txns": []}),
        "first_txn": None,
        "last_txn": None,
    })

    with open(txn_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row.get("Date", "").strip('"')
            action = row.get("Action", "").strip('"')
            symbol = row.get("Symbol", "").strip('"')
            qty_str = row.get("Quantity", "").strip('"')

            if not qty_str or not symbol:
                continue

            try:
                qty = int(qty_str)
            except ValueError:
                continue

            # Parse option symbol (skip equity)
            opt_match = re.match(r"^(\w+)\s+(\d{2}/\d{2}/\d{4})\s+([\d.]+)\s+([CP])$", symbol)
            if not opt_match:
                continue

            underlying = opt_match.group(1)

            # Track transaction for this contract
            if "Sell to Open" in action or "STO" in action:
                positions[underlying]["contracts"][symbol]["qty"] += qty
                positions[underlying]["contracts"][symbol]["txns"].append(f"{date_str} STO {qty}")
            elif "Buy to Close" in action or "BTC" in action:
                positions[underlying]["contracts"][symbol]["qty"] -= qty
                positions[underlying]["contracts"][symbol]["txns"].append(f"{date_str} BTC {qty}")

            # Track dates
            if positions[underlying]["first_txn"] is None:
                positions[underlying]["first_txn"] = date_str
            positions[underlying]["last_txn"] = date_str

    # Filter to live positions and calculate totals
    result = {}
    for underlying in sorted(positions.keys()):
        pos = positions[underlying]
        live_contracts = {
            sym: data for sym, data in pos["contracts"].items() if data["qty"] != 0
        }
        if live_contracts:
            total_qty = sum(data["qty"] for data in live_contracts.values())
            result[underlying] = {
                "total_contracts": total_qty,
                "contracts": live_contracts,
                "first_txn_date": pos["first_txn"],
                "last_txn_date": pos["last_txn"],
            }

    return result


def main():
    txn_file = find_latest_transactions()
    if not txn_file:
        print("ERROR: No transaction CSV found")
        sys.exit(1)

    print(f"Reconstructing positions from: {Path(txn_file).name}")
    positions = reconstruct_from_transactions(txn_file)

    total_contracts = sum(p["total_contracts"] for p in positions.values())
    print(f"✓ Reconstructed {len(positions)} symbols with {total_contracts} open contracts")
    print(f"\nLive positions by symbol:")
    print("=" * 80)

    for symbol in sorted(positions.keys()):
        pos = positions[symbol]
        print(f"\n{symbol}: {pos['total_contracts']:+d} contracts (first: {pos['first_txn_date']} — last: {pos['last_txn_date']})")
        for contract_sym, contract_data in sorted(pos["contracts"].items()):
            if contract_data["qty"] != 0:
                print(f"  {contract_sym}: {contract_data['qty']:+d}")


if __name__ == "__main__":
    main()
