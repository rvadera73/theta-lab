"""
Regression tests for scripts/open_positions_loader_v2.py's
_capture_fidelity_equity_from_position_files() (2026-11-13 fix).

Real bug: Fidelity equity (stock) holdings were invisible to live-data
loading entirely -- _track_equity_positions() only recognizes shares that
arrived via option ASSIGNMENT ('BOUGHT ASSIGNED PUTS'/'SOLD ASSIGNED
CALLS'), and Fidelity's position-file export has no 'action' column at
all, so a directly-purchased equity position (e.g. SONO, bought outright)
was never captured live -- every Fidelity account fell back to the
static, stale portfolio_equity_positions.yaml snapshot unconditionally,
for every ticker, forever.

This fix re-reads the raw Fidelity position-file CSVs directly, with
index_col=False -- these exports end every data row with a trailing
comma (one more field than the header has), and without that flag pandas
infers the extra field as an implicit row index, which shifts every
NAMED column's values one field to the right of where they belong. Not
handling this was also the exact reason an earlier 2026-09-01 attempt at
this same equity capture was reverted (it reused the shifted 'Symbol'
column and got Description text instead of the real ticker).

No pytest dependency -- run directly: python3 tests/test_capture_fidelity_equity.py
"""
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from open_positions_loader_v2 import OpenPositionsLoaderV2  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


HEADER = (
    "Account number,Account name,Symbol,Description,Quantity,Last price,"
    "Last price change,Current value,Today's gain/loss dollar,"
    "Today's gain/loss percent,Total gain/loss dollar,Total gain/loss percent,"
    "Percent of account,Cost basis total,Average cost basis,Type"
)

# Every real Fidelity export row ends with a trailing comma (17 fields
# against the header's 16) -- the fixture must reproduce that exactly, or
# this test would not actually exercise the index_col=False fix at all.
ROWS_RAHUL = [
    # Real equity holding: SONO, 400 shares, same account as its covered call below.
    '225798148,Traditional IRA,SONO,SONOS INC COM,400,$16.17,-$1.29,$6468.00,-$516.00,-7.39%,-$4190.75,-39.32%,1.19%,$10658.75,$26.65,Cash,',
    # Option row on the SAME ticker -- must NOT be captured as an equity row.
    '225798148,Traditional IRA, -SONO261218C10,SONO DEC 18 2026 $10 CALL,-4,$6.33,-$1.23,-$2532.00,+$492.00,+16.26%,-$1818.72,-254.98%,-0.47%,$713.28,$1.78,Cash,',
    # A second real equity holding, same account.
    '225798148,Traditional IRA,NKE,NIKE INC CLASS B COM NPV,200,$38.67,+$0.25,$7734.00,+$50.00,+0.65%,-$8702.40,-52.95%,1.42%,$16436.40,$82.18,Cash,',
    # Money-market sweep row -- blank Quantity, must not crash or be captured.
    '225798148,Traditional IRA,FDRXX**,HELD IN MONEY MARKET,,,,,,,,,,,,Cash,',
    # Summary row with no ticker-shaped Symbol at all.
    '225798148,Traditional IRA,Pending activity,,,,,-$100.00,,,,,,,,,',
    # 401K mutual-fund holding (different account, fractional shares) -- must not be captured.
    '3741R,PRECISE SOFTWARE SOL,FAPCX,FID INTL CAP APPR K6,6.374,$17.18,-$0.54,$109.51,-$3.44,-3.04%,-$2.54,-2.27%,0.06%,$112.05,$17.58,,',
]

ACCOUNT_MAP = {
    'Traditional IRA': 'Fidelity (Rahul)',
    'PRECISE SOFTWARE SOL': 'Fidelity 401K (Rahul)',
}

tmpdir = Path(tempfile.mkdtemp(prefix="theta_lab_fidelity_equity_test_"))
try:
    csv_path = tmpdir / "fidelity_rahul.csv"
    csv_path.write_text(HEADER + "\n" + "\n".join(ROWS_RAHUL) + "\n", encoding="utf-8-sig")

    loader = OpenPositionsLoaderV2(data_dir=str(tmpdir))
    loader._fidelity_account_patterns = [
        (['fidelity_rahul.csv'], None, ACCOUNT_MAP, ['ROTH IRA for Minor']),
    ]
    from collections import defaultdict
    loader.equity_from_position_files = defaultdict(lambda: defaultdict(int))
    loader._capture_fidelity_equity_from_position_files()

    print("Real equity holdings are captured under the mapped account name")
    rahul = loader.equity_from_position_files.get('Fidelity (Rahul)', {})
    check("SONO: 400 shares captured", rahul.get('SONO') == 400, f"got {rahul.get('SONO')}")
    check("NKE: 200 shares captured", rahul.get('NKE') == 200, f"got {rahul.get('NKE')}")

    print("\nOption rows, money-market sweeps, and summary rows are excluded")
    check("no 'SONO DEC...' / option-derived junk ticker leaked in",
          set(rahul.keys()) == {'SONO', 'NKE'}, f"got keys={set(rahul.keys())}")
    check("FDRXX (money market) was not captured as a ticker",
          'FDRXX' not in rahul, f"got {rahul}")

    print("\n401K mutual-fund holdings (fractional shares, different account) are excluded")
    fund_401k = loader.equity_from_position_files.get('Fidelity 401K (Rahul)', {})
    check("FAPCX (fractional-share mutual fund) was not captured",
          'FAPCX' not in fund_401k, f"got {fund_401k}")

    print("\nEnd-to-end: the real column-shift bug (trailing comma -> pandas "
          "implicit index) does not corrupt the ticker the way the reverted "
          "2026-09-01 attempt's approach did")
    check("ticker is the real 'SONO', not 'SONOS' (parsed from shifted Description text)",
          'SONOS' not in rahul and rahul.get('SONO') == 400,
          f"got keys={set(rahul.keys())}")
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
