"""
Characterization tests for mcp/analysis/pnl.py, written BEFORE the Bolt
b17-pnl-refactor modularity refactor (file was 611 lines with several
>50-line parser functions and >4-field Position/OptionLeg dataclasses).

Purpose: lock in CURRENT, real behavior of every function this Bolt intends
to touch, so the subsequent phase-extraction refactor can be verified to be
behavior-preserving rather than assumed to be. Every fixture below mirrors
the real broker data shapes this module already parses in production:
  - Schwab: raw_positions list of dicts from get_schwab_accounts(
    include_positions=True) -- instrument.assetType/symbol/underlyingSymbol/
    putCall, longQuantity/shortQuantity, averagePrice/averageShortPrice,
    marketValue (see parse_schwab_positions's own docstring/body).
  - Fidelity: the same "Account number,...,Last price,...,Cost basis
    total,..." sentence-case header as tests/test_parse_fidelity_csv.py's
    real fixture, extended here with option rows (" -SYM YYMMDDC/Pstrike"
    OSI-ish Fidelity format) and a money-market/expired-option row --
    branches test_parse_fidelity_csv.py's own fixture does NOT exercise.
  - Vanguard: the "SYMBOL price $chg %chg qty unreal$ unreal% balance" PDF/
    CSV row format already documented above _parse_vanguard_row.

Every expected value below was captured by RUNNING the current (pre-refactor)
code and reading back its real output -- not derived by hand -- per this
Bolt's Step 2 instructions.

No pytest dependency -- run directly: python3 tests/test_pnl_module.py
"""
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "mcp"))
sys.path.insert(0, str(_ROOT / "mcp" / "analysis"))

import pnl  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + ("" if condition else f" -- {detail}"))
    if not condition:
        failures.append(label)


def legs_tuple(position):
    """Order-stable summary of a Position's option legs for assertions."""
    return [
        (leg.option_type, leg.strike, leg.expiry, leg.quantity,
         leg.premium_received, leg.current_mark)
        for leg in position.option_legs
    ]


# ---------------------------------------------------------------------------
# _parse_osi_symbol -- Schwab OSI option symbol parsing
# ---------------------------------------------------------------------------
print("_parse_osi_symbol()")

check("parses a well-formed OSI PUT symbol",
      pnl._parse_osi_symbol("AXON  260618P00470000") == ("2026-06-18", "PUT", 470.0),
      f"got {pnl._parse_osi_symbol('AXON  260618P00470000')}")

check("parses a well-formed OSI CALL symbol",
      pnl._parse_osi_symbol("AAPL  271218C00200000") == ("2027-12-18", "CALL", 200.0),
      f"got {pnl._parse_osi_symbol('AAPL  271218C00200000')}")

check("too-short symbol returns the ('', '', 0.0) sentinel, not an exception",
      pnl._parse_osi_symbol("short") == ("", "", 0.0),
      f"got {pnl._parse_osi_symbol('short')}")

# ---------------------------------------------------------------------------
# _parse_fidelity_symbol -- Fidelity option symbol parsing
# ---------------------------------------------------------------------------
print("\n_parse_fidelity_symbol()")

check("parses the docstring's own CALL example (' -INFY270115C18')",
      pnl._parse_fidelity_symbol(" -INFY270115C18") == ("INFY", "2027-01-15", "CALL", 18.0),
      f"got {pnl._parse_fidelity_symbol(' -INFY270115C18')}")

check("parses a PUT-shaped symbol with a leading-dash and 2-digit strike dollars",
      pnl._parse_fidelity_symbol(" -AXON271218C00470") == ("AXON", "2027-12-18", "CALL", 470.0),
      f"got {pnl._parse_fidelity_symbol(' -AXON271218C00470')}")

check("a bare equity ticker (no option suffix) returns None",
      pnl._parse_fidelity_symbol("AAPL") is None, "expected None")

check("empty string returns None, not an exception",
      pnl._parse_fidelity_symbol("") is None, "expected None")

# ---------------------------------------------------------------------------
# _parse_vanguard_row -- Vanguard PDF/CSV row parsing (today injected so
# dte is deterministic regardless of the day this test runs)
# ---------------------------------------------------------------------------
print("\n_parse_vanguard_row()")

from datetime import date  # noqa: E402

_VG_TODAY = date(2026, 11, 10)

_vg_equity = pnl._parse_vanguard_row(
    "AAPL 150.00 2.50 1.69% 100 5000.00 50.00% 15000.00", _VG_TODAY)
check("equity row: kind == 'equity', symbol == 'AAPL'",
      _vg_equity is not None and _vg_equity[0] == "equity" and _vg_equity[1] == "AAPL",
      f"got {_vg_equity}")
if _vg_equity is not None:
    _eq_pos = _vg_equity[2]
    check("equity row: shares=100, cost-basis-per-share derived from unreal$/unreal% (5000/0.50/100=100.0), current_price=150.0",
          (_eq_pos.shares, _eq_pos.stock_cost_basis, _eq_pos.current_price) == (100, 100.0, 150.0),
          f"got {_eq_pos}")

_vg_transact = pnl._parse_vanguard_row(
    "Transact AAPL 150.00 2.50 1.69% 100 5000.00 50.00% 15000.00", _VG_TODAY)
check("a 'Transact ' prefix is stripped and parses identically to the bare row",
      _vg_transact is not None and _vg_transact[2].shares == 100,
      f"got {_vg_transact}")

_vg_option = pnl._parse_vanguard_row(
    "AXON 271218 C 470.00 5.00 0.50 11.11% -2 1000.00 50.00% -500.00", _VG_TODAY)
check("option row: kind == 'option', underlying == 'AXON'",
      _vg_option is not None and _vg_option[0] == "option" and _vg_option[1] == "AXON",
      f"got {_vg_option}")
if _vg_option is not None:
    _vg_leg = _vg_option[2]
    check("option row: CALL 470.0 2027-12-18, net short 2 contracts, "
          "premium_received derived from unreal$/unreal% (1000/0.50=2000.0), "
          "current_mark = abs(balance) = 500.0",
          (_vg_leg.option_type, _vg_leg.strike, _vg_leg.expiry, _vg_leg.quantity,
           _vg_leg.premium_received, _vg_leg.current_mark) ==
          ("CALL", 470.0, "2027-12-18", -2, 2000.0, 500.0),
          f"got {_vg_leg}")

check("an already-expired option row (expiry in the past relative to 'today') is dropped (returns None)",
      pnl._parse_vanguard_row(
          "AXON 230618 C 470.00 5.00 0.50 11.11% -2 1000.00 50.00% -500.00", _VG_TODAY) is None,
      "expected None for an expired contract")

check("a non-matching garbage line returns None, not an exception",
      pnl._parse_vanguard_row("not a matching row at all", _VG_TODAY) is None,
      "expected None")

# ---------------------------------------------------------------------------
# parse_schwab_positions
# ---------------------------------------------------------------------------
print("\nparse_schwab_positions()")

_schwab_raw = [
    {
        "instrument": {"assetType": "EQUITY", "symbol": "AAPL"},
        "longQuantity": 100, "shortQuantity": 0,
        "averagePrice": 150.0, "marketValue": 17500.0,
    },
    {
        # short CALL against AAPL equity
        "instrument": {"assetType": "OPTION", "symbol": "AAPL  271218C00200000",
                       "underlyingSymbol": "AAPL", "putCall": "CALL"},
        "longQuantity": 0, "shortQuantity": 2,
        "averagePrice": 3.0, "averageShortPrice": 4.5,
        "marketValue": -600.0,
    },
    {
        # short PUT on an underlying with NO equity holding -> stub Position
        "instrument": {"assetType": "OPTION", "symbol": "MSFT  271218P00300000",
                       "underlyingSymbol": "MSFT", "putCall": "PUT"},
        "longQuantity": 0, "shortQuantity": 1,
        "averagePrice": 2.0, "averageShortPrice": 5.0,
        "marketValue": -300.0,
    },
    {
        # LONG option leg (not short) -> premium=0, mark=0 per current logic
        "instrument": {"assetType": "OPTION", "symbol": "NVDA  271218C00900000",
                       "underlyingSymbol": "NVDA", "putCall": "CALL"},
        "longQuantity": 1, "shortQuantity": 0,
        "averagePrice": 10.0, "marketValue": 1200.0,
    },
]
_schwab_quotes = {"AAPL": {"lastPrice": 175.0}, "MSFT": {"lastPrice": 310.0}}

_schwab_positions = {p.symbol: p for p in pnl.parse_schwab_positions(_schwab_raw, "A", _schwab_quotes)}

check("returns exactly 3 positions (AAPL, MSFT stub, NVDA stub)",
      set(_schwab_positions.keys()) == {"AAPL", "MSFT", "NVDA"},
      f"got {sorted(_schwab_positions.keys())}")

if "AAPL" in _schwab_positions:
    p = _schwab_positions["AAPL"]
    check("AAPL: equity fields correct (shares/cost-basis/current_price), account tagged, one short CALL leg attached",
          (p.account, p.shares, p.stock_cost_basis, p.current_price) == ("A", 100, 150.0, 175.0)
          and legs_tuple(p) == [("CALL", 200.0, "2027-12-18", -2, 900.0, 600.0)],
          f"got {p}, legs={legs_tuple(p)}")

if "MSFT" in _schwab_positions:
    p = _schwab_positions["MSFT"]
    check("MSFT: stub equity Position (0 shares, 0 cost-basis) created from quote lookup for current_price, with the short PUT leg attached",
          (p.shares, p.stock_cost_basis, p.current_price) == (0, 0, 310.0)
          and legs_tuple(p) == [("PUT", 300.0, "2027-12-18", -1, 500.0, 300.0)],
          f"got {p}, legs={legs_tuple(p)}")

if "NVDA" in _schwab_positions:
    p = _schwab_positions["NVDA"]
    check("NVDA: long (not short) option leg gets premium_received=0 and current_mark=0 under current logic",
          legs_tuple(p) == [("CALL", 900.0, "2027-12-18", 1, 0, 0)],
          f"got legs={legs_tuple(p)}")

# ---------------------------------------------------------------------------
# parse_fidelity_csv -- extends tests/test_parse_fidelity_csv.py's
# equity-only, single-account, case-insensitive-header fixture with the
# OPTION row branch, an expired-option skip, a money-market skip, and a
# second account -- none of which that file's fixture exercises.
# ---------------------------------------------------------------------------
print("\nparse_fidelity_csv() -- option rows, expired rows, multi-account")

_fid_csv = (
    "This export reflects your account information as of some disclaimer line.\n"
    "Account number,Account Name,Symbol,Quantity,Last price,Cost basis total,Average Cost Basis\n"
    "12345678,Individual,AAPL,100,275.50,20000.00,200.00\n"
    "12345678,Individual, -AXON271218C00470,-2,12.50,1800.00,0.00\n"
    "12345678,Individual, -EXPD230101P00100,-1,5.00,500.00,0.00\n"
    "12345678,Individual,SPAXX**,500,1.00,500.00,1.00\n"
    "87654321,Other,MSFT,50,410.25,18000.00,360.00\n"
    "\n"
    "The data and information in this document does not constitute tax advice.\n"
)
_fid_fd, _fid_path = tempfile.mkstemp(suffix=".csv", prefix="test_pnl_fidelity_")
with os.fdopen(_fid_fd, "w", encoding="utf-8") as f:
    f.write(_fid_csv)

try:
    _fid_result = pnl.parse_fidelity_csv(_fid_path)

    check("returns both account numbers as keys",
          set(_fid_result.keys()) == {"12345678", "87654321"}, f"got {list(_fid_result.keys())}")

    _acct1 = {p.symbol: p for p in _fid_result.get("12345678", [])}
    check("account 12345678: AAPL equity + AXON option stub only -- "
          "the expired EXPD put and the SPAXX** money-market row are both excluded",
          set(_acct1.keys()) == {"AAPL", "AXON"}, f"got {sorted(_acct1.keys())}")

    if "AAPL" in _acct1:
        p = _acct1["AAPL"]
        check("AAPL: shares/cost-basis/current_price parsed correctly, tagged with its own account number",
              (p.account, p.shares, p.stock_cost_basis, p.current_price) == ("12345678", 100, 200.0, 275.50),
              f"got {p}")

    if "AXON" in _acct1:
        p = _acct1["AXON"]
        check("AXON: stub equity Position (0 shares) with the short CALL leg attached -- "
              "premium_received = abs(cost basis total) since short, current_mark = price*100*contracts",
              (p.shares, p.stock_cost_basis, p.current_price) == (0, 0.0, 0.0)
              and legs_tuple(p) == [("CALL", 470.0, "2027-12-18", -2, 1800.0, 2500.0)],
              f"got {p}, legs={legs_tuple(p)}")

    _acct2 = {p.symbol: p for p in _fid_result.get("87654321", [])}
    check("account 87654321 (second account in the same CSV) parsed independently: MSFT only",
          set(_acct2.keys()) == {"MSFT"}, f"got {sorted(_acct2.keys())}")
finally:
    os.remove(_fid_path)

# ---------------------------------------------------------------------------
# parse_vanguard_csv
# ---------------------------------------------------------------------------
print("\nparse_vanguard_csv()")

_vcsv_content = (
    "Symbol,Shares,Share Price\n"
    "AAPL,100,175.00\n"
    "AXON 271218 C 470.00,-2,12.50\n"
    "\n"
)
_vcsv_fd, _vcsv_path = tempfile.mkstemp(suffix=".csv", prefix="test_pnl_vanguard_")
with os.fdopen(_vcsv_fd, "w", encoding="utf-8") as f:
    f.write(_vcsv_content)

try:
    _vcsv_positions = {p.symbol: p for p in pnl.parse_vanguard_csv(_vcsv_path, "V")}

    check("returns both AAPL equity and an AXON option stub",
          set(_vcsv_positions.keys()) == {"AAPL", "AXON"}, f"got {sorted(_vcsv_positions.keys())}")

    if "AAPL" in _vcsv_positions:
        p = _vcsv_positions["AAPL"]
        check("AAPL: shares=100, current_price=175.0, cost-basis is 0.0 "
              "(parse_vanguard_csv has no cost-basis data per its own docstring)",
              (p.account, p.shares, p.stock_cost_basis, p.current_price) == ("V", 100, 0.0, 175.0),
              f"got {p}")

    if "AXON" in _vcsv_positions:
        p = _vcsv_positions["AXON"]
        check("AXON: stub equity (0 shares), short CALL leg with premium_received=0.0 "
              "(parse_vanguard_csv never sets premium, unlike the PDF parser) "
              "and a positive dte",
              (p.shares, p.stock_cost_basis, p.current_price) == (0, 0.0, 0.0)
              and len(p.option_legs) == 1
              and (p.option_legs[0].option_type, p.option_legs[0].strike, p.option_legs[0].expiry,
                   p.option_legs[0].quantity, p.option_legs[0].premium_received, p.option_legs[0].current_mark)
              == ("CALL", 470.0, "2027-12-18", -2, 0.0, 2500.0)
              and p.option_legs[0].dte > 0,
              f"got {p}, legs={legs_tuple(p)}")
finally:
    os.remove(_vcsv_path)

# ---------------------------------------------------------------------------
# parse_vanguard_pdf -- mocks pdfplumber.open() (no real PDF needed) to
# exercise the page-text-extraction + per-line parsing + merge path.
# ---------------------------------------------------------------------------
print("\nparse_vanguard_pdf()")

_vpdf_text = (
    "AAPL 150.00 2.50 1.69% 100 5000.00 50.00% 15000.00\n"
    "AXON 271218 C 470.00 5.00 0.50 11.11% -2 1000.00 50.00% -500.00\n"
    "some disclaimer line that does not match\n"
)


class _FakePage:
    def extract_text(self):
        return _vpdf_text


class _FakePdf:
    def __enter__(self):
        self.pages = [_FakePage()]
        return self

    def __exit__(self, *_a):
        return False


with mock.patch("pdfplumber.open", return_value=_FakePdf()):
    _vpdf_positions = {p.symbol: p for p in pnl.parse_vanguard_pdf("fake.pdf", "V")}

check("returns both AAPL equity and an AXON option stub",
      set(_vpdf_positions.keys()) == {"AAPL", "AXON"}, f"got {sorted(_vpdf_positions.keys())}")

if "AAPL" in _vpdf_positions:
    p = _vpdf_positions["AAPL"]
    check("AAPL: shares=100, cost-basis-per-share derived from unreal$/unreal% (100.0), current_price=150.0",
          (p.account, p.shares, p.stock_cost_basis, p.current_price) == ("V", 100, 100.0, 150.0),
          f"got {p}")

if "AXON" in _vpdf_positions:
    p = _vpdf_positions["AXON"]
    check("AXON: stub equity, short CALL leg with premium_received derived from unreal$/unreal% (2000.0)",
          (p.shares, p.stock_cost_basis, p.current_price) == (0, 0.0, 0.0)
          and legs_tuple(p) == [("CALL", 470.0, "2027-12-18", -2, 2000.0, 500.0)],
          f"got {p}, legs={legs_tuple(p)}")

# ---------------------------------------------------------------------------
# Position / OptionLeg computed properties and signal methods -- these are
# NOT being refactored in this Bolt, but every parser above constructs
# Position/OptionLeg objects, so a light characterization of their
# downstream-consumed computed fields is cheap insurance.
# ---------------------------------------------------------------------------
print("\nPosition computed properties + signal methods")

_pos = pnl.Position(
    symbol="AAPL", account="A", shares=100, stock_cost_basis=150.0, current_price=175.0,
    option_legs=[
        pnl.OptionLeg(description="CALL 200 2027-12-18", strike=200.0, expiry="2027-12-18",
                      option_type="CALL", quantity=-2, premium_received=900.0, current_mark=600.0, dte=403),
        pnl.OptionLeg(description="PUT 150 2027-12-18", strike=150.0, expiry="2027-12-18",
                      option_type="PUT", quantity=-1, premium_received=300.0, current_mark=900.0, dte=10),
    ],
)

check("stock_pnl = (current_price - cost_basis) * shares = 2500.0", _pos.stock_pnl == 2500.0, f"got {_pos.stock_pnl}")
check("total_premium_received = sum of both legs = 1200.0", _pos.total_premium_received == 1200.0,
      f"got {_pos.total_premium_received}")
check("total_cost_to_close_options = sum of both marks = 1500.0", _pos.total_cost_to_close_options == 1500.0,
      f"got {_pos.total_cost_to_close_options}")
check("net_options_pnl = premium - cost_to_close = -300.0", _pos.net_options_pnl == -300.0,
      f"got {_pos.net_options_pnl}")
check("combined_net_pnl = stock_pnl + net_options_pnl = 2200.0", _pos.combined_net_pnl == 2200.0,
      f"got {_pos.combined_net_pnl}")
check("profit_pct_of_max = -0.25 (cost_to_close exceeds premium received)", _pos.profit_pct_of_max == -0.25,
      f"got {_pos.profit_pct_of_max}")

_sig_bear = _pos.profit_take_signal("BEAR_SIDEWAYS")
check("profit_take_signal(BEAR_SIDEWAYS): HOLD, not at 40% target, target_range '40-50%'",
      _sig_bear == {"signal": False, "pct_captured": -25.0, "target_range": "40-50%",
                    "regime": "BEAR_SIDEWAYS", "recommendation": "HOLD — -25.0% captured, need 40%"},
      f"got {_sig_bear}")

_sig_bad_regime = _pos.profit_take_signal("NOT_A_REGIME")
check("profit_take_signal() falls back to BEAR_SIDEWAYS targets for an unrecognized regime string",
      _sig_bad_regime["target_range"] == "40-50%" and _sig_bad_regime["regime"] == "NOT_A_REGIME",
      f"got {_sig_bad_regime}")

_roll = _pos.roll_signal()
check("roll_signal(): the 10-DTE PUT leg triggers a roll signal",
      _roll == {"signal": True, "legs": ["PUT 150.0 exp 2027-12-18 (10 DTE)"],
                "recommendation": "ROLL — within 21 DTE"},
      f"got {_roll}")

check("loss_flag(): 1500/1200 = 1.25x premium, below the 2x flag threshold -> not flagged",
      _pos.loss_flag() == {"flag": False}, f"got {_pos.loss_flag()}")

_pos_no_premium = pnl.Position(symbol="MSFT", account="A", shares=0, stock_cost_basis=0, current_price=0)
check("profit_pct_of_max is None when no premium has ever been received",
      _pos_no_premium.profit_pct_of_max is None, f"got {_pos_no_premium.profit_pct_of_max}")
check("profit_take_signal() reports no_premium_data instead of crashing on a divide-by-zero",
      _pos_no_premium.profit_take_signal("BULL") == {"signal": False, "reason": "no_premium_data"},
      f"got {_pos_no_premium.profit_take_signal('BULL')}")
check("roll_signal() with no option legs at all returns signal: False",
      _pos_no_premium.roll_signal() == {"signal": False}, f"got {_pos_no_premium.roll_signal()}")
check("loss_flag() with no premium received returns flag: False (not a divide-by-zero)",
      _pos_no_premium.loss_flag() == {"flag": False}, f"got {_pos_no_premium.loss_flag()}")

_pos_big_loss = pnl.Position(
    symbol="NVDA", account="A", shares=0, stock_cost_basis=0, current_price=0,
    option_legs=[pnl.OptionLeg(description="PUT 900 2027-12-18", strike=900.0, expiry="2027-12-18",
                                option_type="PUT", quantity=-1, premium_received=500.0,
                                current_mark=1500.0, dte=100)],
)
check("loss_flag(): cost-to-close at 3x premium received triggers FLAG_AND_ASK",
      _pos_big_loss.loss_flag() == {"flag": True, "premium_received": 500.0, "current_cost_to_close": 1500.0,
                                     "multiplier": 3.0, "action": "FLAG_AND_ASK — do not auto-close"},
      f"got {_pos_big_loss.loss_flag()}")

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) -- {failures}")
    sys.exit(1)
print("All checks passed.")
