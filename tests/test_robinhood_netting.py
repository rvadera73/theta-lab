"""
Regression tests for ADR 0003
(docs/design/adr/0003-robinhood-position-ingestion.md): the retired
parse_robinhood_csv() (mcp/analysis/pnl.py) required a "Symbol" header no
real Robinhood export has ever had -- every real export in this repo
(data/positions/robinhood_rahul_individual.csv,
data/positions/robinhood_rahul_traditional.csv, and every archived export)
is a transaction/activity log with header "Activity Date","Process Date",
"Settle Date","Instrument","Description","Trans Code","Quantity","Price",
"Amount" and codes STO/BTC/BTO/STC/OASGN/etc -- so parse_robinhood_csv()
always returned [] against them, and Robinhood accounts D/E (Individual +
Traditional IRA) contributed ZERO positions to load_us_positions().

This file proves, against a synthetic fixture matching the REAL export
format exactly (header + Trans Codes confirmed directly against the real
files):
  1. mcp/reports/robinhood_netting.py's parser + netter correctly nets
     STO/BTC/BTO/STC(+OASGN) sequences into real open positions with
     strike/expiry/option_type/premium -- including the real DKNG-style
     option-assignment edge case, an orphaned-close-only contract, a fully
     closed contract, and an expired contract, all correctly excluded.
  2. mcp/reports/report_utils.py's load_robinhood_positions() builds correct
     Position/OptionLeg objects from that netter's output.
  3. load_us_positions() now returns non-empty Robinhood positions with
     real per-leg detail (previously always empty for Robinhood).
  4. get_position_detail (mcp/server.py) surfaces that per-leg detail
     (strike/expiry/option_type/quantity/premium), not just a ticker.

No pytest dependency -- run directly: python3 tests/test_robinhood_netting.py
"""
import asyncio
import csv
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp"))
sys.path.insert(0, str(ROOT / "mcp" / "reports"))
sys.path.insert(0, str(ROOT / "mcp" / "analysis"))
sys.path.insert(0, str(ROOT / "scripts"))

import report_utils  # noqa: E402
import config  # noqa: E402
import robinhood_netting  # noqa: E402
from analysis.pnl import Position, OptionLeg  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# classify_action() -- the shared, broker-agnostic decision, ported from
# scripts/open_positions_loader_v2.py's _calculate_open_positions.
# ---------------------------------------------------------------------------
print("classify_action() -- shared netting decision")

delta, is_opening = robinhood_netting.classify_action("STO", 2)
check("STO: positive delta, opening", delta == 2 and is_opening, f"got {(delta, is_opening)}")

delta, is_opening = robinhood_netting.classify_action("BTC", 1)
check("BTC: negative delta, NOT opening", delta == -1 and not is_opening, f"got {(delta, is_opening)}")

delta, is_opening = robinhood_netting.classify_action("BTO", 1)
check("BTO: negative delta, opening (establishes a long)", delta == -1 and is_opening, f"got {(delta, is_opening)}")

delta, is_opening = robinhood_netting.classify_action("STC", 1)
check("STC: positive delta, NOT opening (closes a long)", delta == 1 and not is_opening, f"got {(delta, is_opening)}")

delta, is_opening = robinhood_netting.classify_action("Sell to Open", 1)
check("Schwab-style 'Sell to Open' also opens (same chain, both vocabularies)",
      delta == 1 and is_opening, f"got {(delta, is_opening)}")

delta, is_opening = robinhood_netting.classify_action("", -3)
check("no action text, negative qty -> falls back to short-direction delta",
      delta == 3 and not is_opening, f"got {(delta, is_opening)}")

# ---------------------------------------------------------------------------
# Synthetic fixture -- real header/Trans-Code format, confirmed directly
# against data/positions/robinhood_rahul_individual.csv. Expiries are all in
# 2027 (safely future) except one deliberately-expired contract; dates of
# the real DKNG assignment scenario (STO 1/14/2026, OASGN 10/14/2026, expiry
# 1/15/2027) are taken verbatim from the real file.
# ---------------------------------------------------------------------------
_HEADER = ["Activity Date", "Process Date", "Settle Date", "Instrument",
           "Description", "Trans Code", "Quantity", "Price", "Amount"]

_ROWS = [
    # NFLX -- STO only, still open short put (qty 2)
    ["1/5/2026", "1/5/2026", "1/6/2026", "NFLX", "NFLX 3/20/2027 Put $400.00", "STO", "2", "$5.00", "$998.00"],

    # AAPL -- STO then full BTC: closed out, must NOT appear
    ["1/2/2026", "1/2/2026", "1/3/2026", "AAPL", "AAPL 2/20/2027 Call $200.00", "STO", "1", "$3.00", "$300.00"],
    ["1/20/2026", "1/20/2026", "1/21/2026", "AAPL", "AAPL 2/20/2027 Call $200.00", "BTC", "1", "$1.00", "($100.00)"],

    # MSFT -- STO 3, BTC 1 (partial close): still open short, net qty 2
    ["1/3/2026", "1/3/2026", "1/4/2026", "MSFT", "MSFT 4/17/2027 Put $350.00", "STO", "3", "$3.00", "$900.00"],
    ["1/25/2026", "1/25/2026", "1/26/2026", "MSFT", "MSFT 4/17/2027 Put $350.00", "BTC", "1", "$1.50", "($150.00)"],

    # TSLA -- BTO only: still open LONG call (positive quantity)
    ["2/2/2026", "2/2/2026", "2/3/2026", "TSLA", "TSLA 6/19/2027 Call $300.00", "BTO", "1", "$5.00", "($500.00)"],

    # DKNG -- real assignment scenario from the real individual-account
    # export: STO then OASGN (assigned) -- must net to CLOSED, not double-
    # counted as still open. The accompanying multi-line-description stock
    # "Buy" row (real artifact of an option assignment) must not be
    # misparsed as an option row.
    ["1/14/2026", "1/14/2026", "1/15/2026", "DKNG", "DKNG 1/15/2027 Put $35.00", "STO", "1", "$6.35", "$634.95"],
    ["10/14/2026", "10/14/2026", "10/15/2026", "DKNG", "DKNG 1/15/2027 Put $35.00", "OASGN", "1", "", ""],
    ["10/14/2026", "10/14/2026", "10/15/2026", "DKNG",
     "DraftKings\nCUSIP: 26142V105\n1 DKNG Option Assigned", "Buy", "100", "$35.00", "($3,500.00)"],

    # ORCL -- BTC only, no opening leg in this file: orphaned close, must
    # NOT appear (classic partial/YTD-export symptom).
    ["3/1/2026", "3/1/2026", "3/2/2026", "ORCL", "ORCL 5/15/2027 Put $100.00", "BTC", "1", "$2.00", "($200.00)"],

    # IBM -- STO only, but EXPIRED: must NOT appear regardless of net qty.
    ["1/4/2020", "1/4/2020", "1/5/2020", "IBM", "IBM 1/15/2020 Put $100.00", "STO", "1", "$2.00", "$200.00"],

    # Non-option noise row -- must be skipped safely, not raise.
    ["1/10/2026", "1/10/2026", "1/11/2026", "", "ACH Deposit", "ACH", "", "", ""],
]

_tmp_dir = Path(tempfile.mkdtemp())
_csv_path = _tmp_dir / "robinhood_test_individual.csv"
with open(_csv_path, "w", newline="", encoding="utf-8") as _fh:
    _writer = csv.writer(_fh, quoting=csv.QUOTE_ALL)
    _writer.writerow(_HEADER)
    _writer.writerows(_ROWS)

# ---------------------------------------------------------------------------
# parse_robinhood_transaction_csv() -- real CSV parsing
# ---------------------------------------------------------------------------
print("\nparse_robinhood_transaction_csv() -- real transaction-log parsing")

parsed_rows = robinhood_netting.parse_robinhood_transaction_csv(str(_csv_path))
check("parses exactly the 10 real option-contract rows (noise/ACH/equity-Buy rows skipped)",
      len(parsed_rows) == 10, f"got {len(parsed_rows)}")
check("OASGN row normalized to the closing bucket",
      any(r["ticker"] == "DKNG" and r["raw_trans_code"] == "OASGN" and r["trans_code"] == "BTC" for r in parsed_rows),
      f"got {[r for r in parsed_rows if r['ticker'] == 'DKNG']}")

# ---------------------------------------------------------------------------
# net_robinhood_option_legs() -- the actual netting
# ---------------------------------------------------------------------------
print("\nnet_robinhood_option_legs() -- STO/BTC/BTO/STC(+OASGN) netting")

legs = robinhood_netting.net_robinhood_option_legs(parsed_rows)
by_ticker = {leg["ticker"]: leg for leg in legs}

check("exactly 3 open legs (NFLX, MSFT, TSLA) -- AAPL/DKNG/ORCL/IBM all correctly excluded",
      set(by_ticker.keys()) == {"NFLX", "MSFT", "TSLA"}, f"got {sorted(by_ticker.keys())}")

if "NFLX" in by_ticker:
    nflx = by_ticker["NFLX"]
    check("NFLX: strike/expiry/option_type correct",
          (nflx["strike"], nflx["expiry"], nflx["option_type"]) == (400.0, "2027-03-20", "PUT"),
          f"got {nflx}")
    check("NFLX: net short 2 contracts (negative quantity)", nflx["quantity"] == -2, f"got {nflx['quantity']}")
    check("NFLX: net premium is the real $998.00 (single STO row)", nflx["net_credit"] == 998.00, f"got {nflx}")

if "MSFT" in by_ticker:
    msft = by_ticker["MSFT"]
    check("MSFT: partial close nets to short 2 (3 sold, 1 bought back)", msft["quantity"] == -2, f"got {msft}")
    check("MSFT: net premium reflects the partial close (900 - 150 = 750)",
          msft["net_credit"] == 750.00, f"got {msft}")

if "TSLA" in by_ticker:
    tsla = by_ticker["TSLA"]
    check("TSLA: BTO-only nets to a net LONG position (positive quantity)",
          tsla["quantity"] == 1, f"got {tsla}")

# ---------------------------------------------------------------------------
# report_utils.load_robinhood_positions() -- Position/OptionLeg construction
# ---------------------------------------------------------------------------
print("\nload_robinhood_positions() -- Position/OptionLeg construction")

with mock.patch.object(report_utils, "_fill_current_marks") as mocked_fill_marks:
    positions = report_utils.load_robinhood_positions(str(_csv_path), account_label="TESTRH2")

check("_fill_current_marks was called (live cost-to-close backfill wired in)",
      mocked_fill_marks.called, "not called")
check("returns exactly 3 Position objects (NFLX, MSFT, TSLA)",
      {p.symbol for p in positions} == {"NFLX", "MSFT", "TSLA"}, f"got {[p.symbol for p in positions]}")
check("every Position is tagged with the account label passed in",
      all(p.account == "TESTRH2" for p in positions), f"got {[p.account for p in positions]}")

_nflx_pos = next((p for p in positions if p.symbol == "NFLX"), None)
if _nflx_pos is not None and _nflx_pos.option_legs:
    leg = _nflx_pos.option_legs[0]
    check("NFLX OptionLeg: strike/expiry/option_type/quantity/premium all correct",
          (leg.strike, leg.expiry, leg.option_type, leg.quantity, leg.premium_received)
          == (400.0, "2027-03-20", "PUT", -2, 998.0),
          f"got {leg}")
else:
    check("NFLX Position has an option leg", False, f"got positions={positions}")

_tsla_pos = next((p for p in positions if p.symbol == "TSLA"), None)
if _tsla_pos is not None and _tsla_pos.option_legs:
    leg = _tsla_pos.option_legs[0]
    check("TSLA OptionLeg: net-long leg has positive quantity",
          leg.quantity == 1, f"got {leg}")
else:
    check("TSLA Position has an option leg", False, f"got positions={positions}")

# ---------------------------------------------------------------------------
# load_us_positions() -- end-to-end: previously ALWAYS returned zero
# Robinhood positions against this real file format; now must return real
# per-leg detail for accounts wired to broker="robinhood_csv".
# ---------------------------------------------------------------------------
print("\nload_us_positions() -- Robinhood accounts now contribute real positions")

_fake_accounts = {
    "TESTRH2": {"broker": "robinhood_csv", "csv_path_env": "TEST_ROBINHOOD_CSV_PATH_2", "label": "Robinhood Test"},
}
os.environ["TEST_ROBINHOOD_CSV_PATH_2"] = str(_csv_path)

with mock.patch.object(config, "ACCOUNTS", _fake_accounts), \
     mock.patch.object(report_utils, "_snapshot_holdings", return_value=set()), \
     mock.patch.object(report_utils, "current_price", return_value=123.45), \
     mock.patch.object(report_utils, "_fill_current_marks"):
    us_data = asyncio.run(report_utils.load_us_positions())

rh_positions = [p for p in us_data.get("positions", []) if p.account == "TESTRH2"]
check("load_us_positions() returns non-empty Robinhood positions (was ALWAYS [] before this fix)",
      len(rh_positions) > 0, f"got {len(rh_positions)} positions, warning={us_data.get('warning')}")
check("the 3 real open contracts (NFLX/MSFT/TSLA) all made it through load_us_positions()",
      {p.symbol for p in rh_positions} == {"NFLX", "MSFT", "TSLA"},
      f"got {[p.symbol for p in rh_positions]}")
check("account_sources is populated for the Robinhood account (ADR 0004 parity preserved)",
      us_data.get("account_sources", {}).get("TESTRH2", {}).get("source") == "robinhood_csv",
      f"got {us_data.get('account_sources')}")

# ---------------------------------------------------------------------------
# get_position_detail (mcp/server.py) -- surfaces real per-leg detail
# (strike/expiry/option_type/quantity/premium), not just a ticker.
# ---------------------------------------------------------------------------
print("\nget_position_detail -- real Robinhood per-leg detail surfaced")

import server  # noqa: E402 -- imported late so the sys.path setup above is in place
from reports import report_utils as server_report_utils  # noqa: E402 -- see test_extended_hours_pricing.py's
                                                           # note: server.py imports "reports.report_utils", a
                                                           # separate sys.modules entry from this file's flat
                                                           # "report_utils" import above.

_fake_us_data = {
    "positions": rh_positions,
    "account_sources": {"TESTRH2": {"source": "robinhood_csv", "as_of": "2026-11-08", "days_stale": 1}},
}

with mock.patch.object(server_report_utils, "load_us_positions", return_value=_fake_us_data), \
     mock.patch.object(server_report_utils, "get_cached_extended_hours_quote",
                        return_value={"symbol": "NFLX", "live_price": 850.0, "live_price_source": "regular"}):
    text_result = asyncio.run(server.call_tool("get_position_detail", {"symbol": "NFLX"}))
    detail = json.loads(text_result[0].text)

nflx_account = detail.get("accounts", {}).get("TESTRH2")
check("get_position_detail finds the Robinhood-sourced NFLX position at all",
      nflx_account is not None, f"got accounts={list(detail.get('accounts', {}).keys())}")
if nflx_account is not None:
    legs_out = nflx_account.get("open_option_legs", [])
    check("get_position_detail surfaces full per-leg detail, not just a ticker",
          len(legs_out) == 1
          and legs_out[0]["strike"] == 400.0
          and legs_out[0]["expiry"] == "2027-03-20"
          and legs_out[0]["option_type"] == "PUT"
          and legs_out[0]["quantity"] == -2
          and legs_out[0]["premium_received"] == 998.0,
          f"got {legs_out}")
    check("get_position_detail's data_source for this account is the real robinhood_csv source",
          nflx_account.get("data_source") == "robinhood_csv", f"got {nflx_account.get('data_source')}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
