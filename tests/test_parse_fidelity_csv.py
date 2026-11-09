"""
Regression test for mcp/analysis/pnl.py's parse_fidelity_csv() header-casing
fix -- unrelated-but-legitimate bug fix bundled into this Bolt. Real Fidelity
CSV exports now use sentence-case headers ("Account number", "Last price",
"Cost basis total") instead of the title-case ("Account Number", "Last
Price", "Cost Basis Total") the parser was originally written against. The
old case-sensitive match on both the header-detection line and the
DictReader keys silently returned {} for EVERY row -- no exception, no
error key, just a quietly empty result. Fixed by lower-casing both sides of
every header comparison.

Uses an in-memory/temp CSV fixture with the real, mixed-casing header row
from the bug report ("Account number", "Account Name", "Symbol", "Quantity",
"Last price", "Cost basis total", "Average Cost Basis") -- deliberately
mixed case per column (not all-lowercase, not all-sentence-case) to prove
the fix is genuinely case-INSENSITIVE, not just re-tuned to one new vintage.

No pytest dependency -- run directly: python3 tests/test_parse_fidelity_csv.py
"""
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))

from pnl import parse_fidelity_csv  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# Mixed, realistic casing -- "Account number"/"Last price"/"Cost basis total"
# sentence-case (the real current export), "Account Name" left title-case,
# matching the module docstring's own description of the mixed-casing case.
_CSV_CONTENT = (
    "This export reflects your account information as of some disclaimer line.\n"
    "Account number,Account Name,Symbol,Quantity,Last price,Cost basis total,Average Cost Basis\n"
    "12345678,Individual,AAPL,100,275.50,20000.00,200.00\n"
    "12345678,Individual,MSFT,50,410.25,18000.00,360.00\n"
    "\n"
    "The data and information in this document does not constitute tax advice.\n"
)


def _write_fixture():
    fd, path = tempfile.mkstemp(suffix=".csv", prefix="test_fidelity_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(_CSV_CONTENT)
    return path


fixture_path = _write_fixture()
try:
    result = parse_fidelity_csv(fixture_path)

    check("parse_fidelity_csv() returns a non-empty dict (previously silently returned {} for every row)",
          bool(result), f"got {result}")
    check("the one real account number (12345678) is present as a key",
          "12345678" in result, f"got keys={list(result.keys())}")

    positions = result.get("12345678", [])
    symbols = {p.symbol for p in positions}
    check("both real equity rows (AAPL, MSFT) were parsed into positions",
          symbols == {"AAPL", "MSFT"}, f"got symbols={symbols}")

    aapl = next((p for p in positions if p.symbol == "AAPL"), None)
    check("AAPL position has the correct share count (100) parsed from the Quantity column",
          aapl is not None and aapl.shares == 100, f"got {aapl}")
    check("AAPL position has the correct per-share cost basis (200.00) parsed from Average Cost Basis",
          aapl is not None and aapl.stock_cost_basis == 200.00, f"got {aapl}")
    check("AAPL position has the correct current price (275.50) parsed from the sentence-case 'Last price' column",
          aapl is not None and aapl.current_price == 275.50, f"got {aapl}")

    print("\naccount_filter still works with the new case-insensitive matching")
    filtered = parse_fidelity_csv(fixture_path, account_filter="12345678")
    check("account_filter='12345678' returns the same two positions",
          {p.symbol for p in filtered.get("12345678", [])} == {"AAPL", "MSFT"},
          f"got {filtered}")
    filtered_none = parse_fidelity_csv(fixture_path, account_filter="99999999")
    check("account_filter for a non-matching account returns no positions for it",
          "99999999" not in filtered_none, f"got keys={list(filtered_none.keys())}")

finally:
    os.remove(fixture_path)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
