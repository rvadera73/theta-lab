"""
Regression tests for the Schwab snapshot-vs-transactions source selection
in mcp/reports/report_utils.py.

Real bug this guards against (found 2026-10-13): a raw mtime comparison
flipped to "transactions" whenever the transactions file happened to be
written a few seconds after its same-batch snapshot (Account C, TWLO) --
reconstruct_positions_from_transactions() has no equity-share tracking, so
it silently reported 324 real shares as 0, misclassifying a covered call
as naked. The original mtime check was built for the opposite case (a
transactions file genuinely stale by days, e.g. OKTA/Account A) and must
keep catching that case too.

No pytest dependency -- run directly: python3 tests/test_schwab_source_selection.py
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "reports"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp" / "analysis"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from report_utils import schwab_source_choice, load_us_positions

failures = []


def check(label, condition, detail):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


DAY = 86400.0
now = time.time()

print("schwab_source_choice() unit cases")

# Real bug case: same reconciliation batch, snapshot written 31s BEFORE
# the transactions file. Must still prefer the snapshot.
check(
    "same-day batch, snapshot seconds older -> snapshot",
    schwab_source_choice(now, now + 31) == "snapshot",
    "flipped to transactions on a same-day, sub-minute mtime gap",
)

# Real original case the mtime check exists for: OKTA/Account A, txn file
# 10 days stale vs a same-day snapshot. Must prefer the snapshot.
check(
    "txn file 10 days stale, snapshot fresh -> snapshot",
    schwab_source_choice(now, now - 10 * DAY) == "snapshot",
    "did not prefer the fresher snapshot over a stale transactions file",
)

# Inverse: txn file genuinely newer by a full day (real trades happened
# since the last snapshot) -> must fall back to transactions.
check(
    "txn file one full day newer -> transactions",
    schwab_source_choice(now - DAY - 3600, now) == "transactions",
    "did not fall back when transactions are genuinely a day newer",
)

# No snapshot file at all -> must fall back to transactions.
check(
    "no snapshot (-1 sentinel) -> transactions",
    schwab_source_choice(-1, now) == "transactions",
    "did not fall back when snapshot is missing",
)

# No transactions file at all (0 sentinel) -> must use snapshot.
check(
    "no transactions (0 sentinel) -> snapshot",
    schwab_source_choice(now, 0) == "snapshot",
    "did not use the snapshot when no transactions file exists",
)

print("\nload_us_positions() golden-value regression (real current data)")

us_data = asyncio.run(load_us_positions())
positions = us_data.get("positions", [])
sources = us_data.get("account_sources", {})

print("  account_sources:", sources)
for label in ("A", "B", "C"):
    check(
        f"account {label} uses snapshot source",
        sources.get(label, {}).get("source") == "snapshot",
        f"account {label} fell back to transactions: {sources.get(label)}",
    )

GOLDEN = {
    # symbol: (account, min_shares, option_legs)
    "TWLO": ("C", 324, 2),
    "OKTA": ("A", 600, 6),
}
for symbol, (account, min_shares, legs) in GOLDEN.items():
    matches = [p for p in positions if p.symbol == symbol and p.account == account]
    if not matches:
        check(f"{symbol} ({account}) present", False, "no Position object found at all")
        continue
    pos = matches[0]
    check(
        f"{symbol} ({account}) shares >= {min_shares}",
        pos.shares >= min_shares,
        f"got shares={pos.shares}",
    )
    check(
        f"{symbol} ({account}) has {legs} option legs",
        len(pos.option_legs) == legs,
        f"got {len(pos.option_legs)} legs",
    )

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
