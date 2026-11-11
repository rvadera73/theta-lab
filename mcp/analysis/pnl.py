"""
Combined net P&L per position: stock cost basis + all option premiums collected/paid.
This is the metric that matters — not just options P&L in isolation.
"""

import csv
import io
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Optional


@dataclass
class OptionLeg:
    description: str
    strike: float
    expiry: str          # YYYY-MM-DD
    option_type: str     # PUT or CALL
    quantity: int        # negative = short
    premium_received: float   # positive = credit collected
    current_mark: float       # current market value (positive = cost to close)
    dte: int


@dataclass
class Position:
    symbol: str
    account: str         # "A" or "B"
    shares: int          # 0 if no stock
    stock_cost_basis: float   # per share
    current_price: float
    option_legs: list[OptionLeg] = field(default_factory=list)

    @property
    def stock_pnl(self) -> float:
        return (self.current_price - self.stock_cost_basis) * self.shares

    @property
    def total_premium_received(self) -> float:
        return sum(leg.premium_received for leg in self.option_legs)

    @property
    def total_cost_to_close_options(self) -> float:
        return sum(leg.current_mark for leg in self.option_legs)

    @property
    def net_options_pnl(self) -> float:
        """Premium collected minus current cost to close."""
        return self.total_premium_received - self.total_cost_to_close_options

    @property
    def combined_net_pnl(self) -> float:
        """The only number that matters: stock + all options combined."""
        return self.stock_pnl + self.net_options_pnl

    @property
    def profit_pct_of_max(self) -> Optional[float]:
        """How much of max premium has been captured (0-1)."""
        if self.total_premium_received == 0:
            return None
        captured = self.total_premium_received - self.total_cost_to_close_options
        return captured / self.total_premium_received

    def profit_take_signal(self, regime: str) -> dict:
        """Returns whether position should be closed based on regime profit target."""
        from config import PROFIT_TARGETS, Regime
        try:
            r = Regime(regime)
        except ValueError:
            r = Regime.BEAR_SIDEWAYS
        low, high = PROFIT_TARGETS[r]
        pct = self.profit_pct_of_max
        if pct is None:
            return {"signal": False, "reason": "no_premium_data"}
        at_target = pct >= low
        return {
            "signal": at_target,
            "pct_captured": round(pct * 100, 1),
            "target_range": f"{int(low*100)}-{int(high*100)}%",
            "regime": regime,
            "recommendation": "CLOSE — at profit target" if at_target else f"HOLD — {round(pct*100,1)}% captured, need {int(low*100)}%",
        }

    def roll_signal(self) -> dict:
        """Returns roll recommendation if any leg is near DTE threshold."""
        from config import RISK
        threshold = RISK["roll_dte_threshold"]
        urgent_legs = [leg for leg in self.option_legs if leg.dte <= threshold]
        if urgent_legs:
            return {
                "signal": True,
                "legs": [f"{leg.option_type} {leg.strike} exp {leg.expiry} ({leg.dte} DTE)"
                         for leg in urgent_legs],
                "recommendation": "ROLL — within 21 DTE",
            }
        return {"signal": False}

    def loss_flag(self) -> dict:
        """Flags if mark exceeds 2x premium received (persona rule)."""
        from config import RISK
        mult = RISK["flag_threshold_multiplier"]
        if self.total_premium_received == 0:
            return {"flag": False}
        if self.total_cost_to_close_options > self.total_premium_received * mult:
            return {
                "flag": True,
                "premium_received": round(self.total_premium_received, 2),
                "current_cost_to_close": round(self.total_cost_to_close_options, 2),
                "multiplier": round(self.total_cost_to_close_options / self.total_premium_received, 2),
                "action": "FLAG_AND_ASK — do not auto-close",
            }
        return {"flag": False}


def _parse_osi_symbol(symbol: str) -> tuple[str, str, float]:
    """Parse OSI option symbol into (expiry YYYY-MM-DD, option_type PUT/CALL, strike float).

    OSI format: {underlying 6 chars}{YYMMDD}{C/P}{strike * 1000, 8 digits}
    Example:    'AXON  260618P00470000' → ('2026-06-18', 'PUT', 470.0)
    """
    s = symbol.strip()
    if len(s) < 15:
        return "", "", 0.0
    # Find where the date starts: scan right-to-left for the 6-digit date block
    # OSI = last 15 chars are always {YYMMDD}{C/P}{8-digit strike}
    body = s[-15:]  # YYMMDDX00000000
    yymmdd = body[:6]
    opt_char = body[6]
    strike_str = body[7:]
    try:
        yy, mm, dd = int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:6])
        year = 2000 + yy
        expiry = f"{year:04d}-{mm:02d}-{dd:02d}"
        option_type = "CALL" if opt_char.upper() == "C" else "PUT"
        strike = int(strike_str) / 1000.0
        return expiry, option_type, strike
    except (ValueError, IndexError):
        return "", "", 0.0


# ---------------------------------------------------------------------------
# Shared parser helpers -- every broker-specific parser below builds its own
# equity_map / option-legs-by-underlying accumulators from broker-specific
# rows, but all of them converge on the same two final steps: computing a
# leg's days-to-expiry (defaulting to 0 on an unparsable date) and merging
# option legs onto the equity map (creating a zero-share stub Position for
# any underlying with no equity holding at that broker). Factored out once
# here rather than re-implemented five times below.
# ---------------------------------------------------------------------------

def _dte_from_expiry(expiry: str, today: date) -> int:
    """Days remaining to an ISO ('YYYY-MM-DD') expiry string; 0 if unparsable."""
    try:
        return (date.fromisoformat(expiry) - today).days
    except (ValueError, TypeError):
        return 0


def _merge_option_legs_into_equity_map(
    equity_map: dict[str, Position],
    legs_by_underlying: dict[str, list[OptionLeg]],
    account_label: str,
    current_price_lookup: Optional[Callable[[str], float]] = None,
) -> None:
    """
    Attach parsed option legs onto equity_map in place, creating a
    zero-share stub Position for any underlying that has no equity holding
    at this broker.

    current_price_lookup, if given, is called with the underlying symbol to
    seed a stub Position's current_price (Schwab looks this up from live
    quotes; every other broker parser below has no equivalent and defaults
    to 0).
    """
    for underlying, legs in legs_by_underlying.items():
        if underlying not in equity_map:
            current_price = current_price_lookup(underlying) if current_price_lookup else 0.0
            equity_map[underlying] = Position(
                symbol=underlying,
                account=account_label,
                shares=0,
                stock_cost_basis=0.0,
                current_price=current_price,
            )
        equity_map[underlying].option_legs.extend(legs)


# ---------------------------------------------------------------------------
# Schwab
# ---------------------------------------------------------------------------

def _schwab_equity_position(pos: dict, instrument: dict, account_label: str, quotes: dict) -> Position:
    """Build a Position from one raw Schwab EQUITY position row."""
    symbol = instrument.get("symbol", "")
    qty = pos.get("longQuantity", 0) - pos.get("shortQuantity", 0)
    avg_price = pos.get("averagePrice", 0)
    current_price = quotes.get(symbol, {}).get("lastPrice", avg_price)
    return Position(
        symbol=symbol,
        account=account_label,
        shares=int(qty),
        stock_cost_basis=avg_price,
        current_price=current_price,
    )


def _schwab_option_leg(pos: dict, instrument: dict) -> tuple[str, OptionLeg]:
    """Build (underlying, OptionLeg) from one raw Schwab OPTION position row."""
    symbol = instrument.get("symbol", "")
    qty = pos.get("longQuantity", 0) - pos.get("shortQuantity", 0)
    avg_price = pos.get("averagePrice", 0)

    underlying = instrument.get("underlyingSymbol") or symbol.split()[0]
    # putCall is present in the instrument; strike/expiry come from the OSI symbol
    osi_expiry, osi_type, osi_strike = _parse_osi_symbol(symbol)
    option_type = instrument.get("putCall", osi_type) or osi_type
    strike = osi_strike
    expiry = osi_expiry
    dte = _dte_from_expiry(expiry, date.today())

    short_qty = int(pos.get("shortQuantity", 0))
    is_short = short_qty > 0
    # averageShortPrice = per-share credit received when position was opened
    avg_short_price = pos.get("averageShortPrice", avg_price)
    # marketValue is the current total value (negative for short positions in Schwab)
    market_val = abs(pos.get("marketValue", 0))
    premium = avg_short_price * 100 * short_qty if is_short else 0
    mark = market_val if is_short else 0

    leg = OptionLeg(
        description=f"{option_type} {strike} {expiry}",
        strike=strike,
        expiry=expiry,
        option_type=option_type,
        quantity=-short_qty if is_short else int(qty),
        premium_received=premium,
        current_mark=mark,
        dte=dte,
    )
    return underlying, leg


def parse_schwab_positions(raw_positions: list[dict], account_label: str, quotes: dict) -> list[Position]:
    """
    Convert raw Schwab position data into Position objects.
    raw_positions: from get_schwab_accounts(include_positions=True)
    quotes: symbol -> quote dict
    """
    equity_map: dict[str, Position] = {}
    option_legs: dict[str, list[OptionLeg]] = {}

    for pos in raw_positions:
        instrument = pos.get("instrument", {})
        asset_type = instrument.get("assetType", "")

        if asset_type == "EQUITY":
            eq_pos = _schwab_equity_position(pos, instrument, account_label, quotes)
            equity_map[eq_pos.symbol] = eq_pos
        elif asset_type == "OPTION":
            underlying, leg = _schwab_option_leg(pos, instrument)
            option_legs.setdefault(underlying, []).append(leg)

    # Merge option legs into positions (create equity position if no shares held)
    _merge_option_legs_into_equity_map(
        equity_map, option_legs, account_label,
        current_price_lookup=lambda u: quotes.get(u, {}).get("lastPrice", 0),
    )
    return list(equity_map.values())


# ---------------------------------------------------------------------------
# Fidelity / generic CSV parser
# ---------------------------------------------------------------------------

_FIDELITY_OPT_RE = re.compile(r"^([A-Z]+)(\d{2})(\d{2})(\d{2})([CP])([\d.]+)$")


def _parse_fidelity_symbol(raw: str):
    """Parse Fidelity option symbol e.g. ' -INFY270115C18' → (underlying, expiry, type, strike) or None."""
    s = raw.strip().lstrip("-").strip()
    m = _FIDELITY_OPT_RE.match(s)
    if not m:
        return None
    underlying, yy, mm, dd, cp, strike_s = m.groups()
    expiry = f"20{yy}-{mm}-{dd}"
    option_type = "CALL" if cp == "C" else "PUT"
    return underlying, expiry, option_type, float(strike_s)


def _locate_fidelity_header_index(lines: list[str]) -> Optional[int]:
    """Row index of the real header line, found by prefix match rather than
    exact casing.

    Header casing isn't stable across Fidelity export vintages -- confirmed
    2026-11-04: the current real export uses "Account number"/"Last price"/
    "Cost basis total" (sentence case) while this parser was originally
    written against an older "Account Number"/"Last Price"/"Cost Basis
    Total" (title case) export. A case-sensitive match on the header line
    silently returned {} for every row with no error -- match
    case-insensitively instead of assuming one vintage. Returns None if no
    header line is found at all.
    """
    return next(
        (i for i, l in enumerate(lines) if l.strip().lower().startswith("account number")), None
    )


def _fidelity_numeric(row: dict, key: str) -> str:
    """Strip $ , + from a numeric Fidelity CSV cell; row is already
    lower-cased by key, so key is matched case-insensitively."""
    return row.get(key.lower(), "").replace("$", "").replace(",", "").replace("+", "").strip()


def _fidelity_row_numbers(row: dict) -> Optional[tuple[float, float, float, float]]:
    """Parses (quantity, last_price, cost_basis_total, average_cost_basis)
    from one Fidelity CSV row; None if any of them fails to parse."""
    try:
        qty = float(_fidelity_numeric(row, "Quantity")) if _fidelity_numeric(row, "Quantity") else 0.0
        price = float(_fidelity_numeric(row, "Last Price")) if _fidelity_numeric(row, "Last Price") else 0.0
        cost_total = float(_fidelity_numeric(row, "Cost Basis Total")) if _fidelity_numeric(row, "Cost Basis Total") else 0.0
        avg_cost = float(_fidelity_numeric(row, "Average Cost Basis")) if _fidelity_numeric(row, "Average Cost Basis") else 0.0
    except ValueError:
        return None
    return qty, price, cost_total, avg_cost


def _build_fidelity_option_leg(
    symbol_fields: tuple[str, str, str, float],
    row_numbers: tuple[float, float, float, float],
    today: date,
) -> Optional[OptionLeg]:
    """symbol_fields = (underlying, expiry, option_type, strike) from
    _parse_fidelity_symbol(); row_numbers = (qty, price, cost_total,
    avg_cost) from _fidelity_row_numbers(). Returns None if the contract is
    already expired (not an open position)."""
    underlying, expiry, option_type, strike = symbol_fields
    qty, price, cost_total, _avg_cost = row_numbers
    dte = _dte_from_expiry(expiry, today)
    if dte < 0:
        return None
    contracts = int(abs(qty))
    is_short = qty < 0
    return OptionLeg(
        description=f"{option_type} {strike} {expiry}",
        strike=strike,
        expiry=expiry,
        option_type=option_type,
        quantity=-contracts if is_short else contracts,
        premium_received=abs(cost_total) if is_short else 0.0,
        current_mark=price * 100 * contracts,
        dte=dte,
    )


def _build_fidelity_equity_position(
    raw_sym: str, acct_num: str, row_numbers: tuple[float, float, float, float],
) -> Position:
    """row_numbers = (qty, price, cost_total, avg_cost) from
    _fidelity_row_numbers()."""
    qty, price, _cost_total, avg_cost = row_numbers
    symbol = raw_sym.lstrip("-").strip()
    return Position(
        symbol=symbol,
        account=acct_num,
        shares=int(abs(qty)) if qty else 0,
        stock_cost_basis=avg_cost,
        current_price=price,
    )


def _process_fidelity_row(raw_row: dict, account_filter: str | None, today: date):
    """Parse one raw Fidelity CSV row into (account_number, kind, payload),
    where kind is "option" (payload = (underlying, OptionLeg)) or "equity"
    (payload = Position). Returns None if the row should be skipped
    entirely: wrong/filtered account, a money-market row, unparsable
    numeric fields, or an already-expired option contract."""
    row = {(k or "").strip().lower(): v for k, v in raw_row.items()}
    acct_num = row.get("account number", "").strip()
    if not acct_num or not acct_num.isdigit():
        return None
    if account_filter and acct_num != account_filter:
        return None

    raw_sym = row.get("symbol", "").strip()
    if not raw_sym or raw_sym.endswith("**"):
        return None  # skip money market rows

    row_numbers = _fidelity_row_numbers(row)
    if row_numbers is None:
        return None

    parsed = _parse_fidelity_symbol(raw_sym)
    if parsed:
        leg = _build_fidelity_option_leg(parsed, row_numbers, today)
        if leg is None:
            return None  # already expired -- not an open position
        return acct_num, "option", (parsed[0], leg)

    pos = _build_fidelity_equity_position(raw_sym, acct_num, row_numbers)
    return acct_num, "equity", pos


def parse_fidelity_csv(csv_path: str, account_filter: str | None = None) -> dict[str, list["Position"]]:
    """
    Parse a Fidelity Portfolio Positions CSV export.
    One CSV can contain multiple accounts — returns dict {account_number: [Position]}.
    Pass account_filter to restrict to one account number (string).

    CSV columns: Account Number, Account Name, Symbol, Quantity,
                 Last Price, Cost Basis Total, Average Cost Basis
    """
    today = date.today()
    # per-account accumulators
    equity_maps: dict[str, dict[str, Position]] = {}
    option_legs: dict[str, dict[str, list[OptionLeg]]] = {}

    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        # Skip disclaimer rows until we hit the header
        lines = fh.readlines()

    header_idx = _locate_fidelity_header_index(lines)
    if header_idx is None:
        return {}

    raw_reader = csv.DictReader(io.StringIO("".join(lines[header_idx:])))

    for raw_row in raw_reader:
        row_result = _process_fidelity_row(raw_row, account_filter, today)
        if row_result is None:
            continue
        acct_num, kind, payload = row_result
        equity_maps.setdefault(acct_num, {})
        option_legs.setdefault(acct_num, {})
        if kind == "option":
            underlying, leg = payload
            option_legs[acct_num].setdefault(underlying, []).append(leg)
        else:
            equity_maps[acct_num][payload.symbol] = payload

    # Merge legs into positions, per account
    result: dict[str, list[Position]] = {}
    all_accts = set(equity_maps) | set(option_legs)
    for acct_num in all_accts:
        eq = equity_maps.get(acct_num, {})
        _merge_option_legs_into_equity_map(eq, option_legs.get(acct_num, {}), acct_num)
        result[acct_num] = list(eq.values())

    return result


# ---------------------------------------------------------------------------
# Robinhood CSV ingestion -- retired (ADR 0003,
# docs/design/adr/0003-robinhood-position-ingestion.md). The old
# parse_robinhood_csv() here required a "Symbol" header no real Robinhood
# export has ever had (real exports are transaction logs: "Activity Date",
# "Process Date", "Settle Date", "Instrument", "Description", "Trans Code",
# "Quantity", "Price", "Amount") and always returned [] in production.
# Replaced by mcp/reports/report_utils.py's load_robinhood_positions(),
# which nets the real transaction-log format via the shared
# mcp/reports/robinhood_netting.py helpers.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Vanguard PDF + CSV parser
# PDF format (Holdings | Vanguard page export):
#   SYMBOL YYMMDD C/P STRIKE  price  $chg  %chg  qty  unreal$  unreal%  cur_balance
# Cost basis derived: abs_cost = unreal_dollar / (unreal_pct / 100)
#   equity   → stock_cost_basis_per_share = abs_cost / shares
#   short opt → premium_received = abs_cost
# ---------------------------------------------------------------------------

_VANGUARD_OPT_RE = re.compile(
    r"^([A-Z]+)\s+(\d{2})(\d{2})(\d{2})\s+([CP])\s+([\d.]+)$"
)

_VANGUARD_ROW_RE = re.compile(
    r"^([A-Z][\w \.]+?)\s+"          # symbol (may contain spaces for options)
    r"\$?([\d,]+\.?\d*)\s+"          # price
    r"\$?([\d,]+\.?\d*)\s+"          # $ change
    r"([\d.]+)%\s+"                  # % change (today)
    r"(-?[\d,]+\.?\d*)\s+"           # quantity
    r"\$?([\d,]+\.?\d*)\s+"          # unrealized $ (absolute)
    r"([\d.]+)%\s+"                  # unrealized % (absolute)
    r"(-?\$?[\d,]+\.?\d*)"           # current balance
)


def _vanguard_numeric(s: str) -> float:
    """Strip $ , - from a Vanguard PDF numeric cell; '' -> 0.0."""
    return float(s.replace(",", "").replace("$", "").replace("-", "").strip() or "0")


def _vanguard_option_leg(
    opt_m: re.Match, fields: tuple[float, float, float, float], today: date,
) -> Optional[tuple[str, OptionLeg]]:
    """fields = (qty, unreal_dollar, unreal_pct, cur_bal). Returns
    (underlying, OptionLeg), or None if the contract is already expired."""
    qty, unreal_dollar, unreal_pct, cur_bal = fields
    underlying, yy, mm, dd, cp, strike_s = opt_m.groups()
    expiry = f"20{yy}-{mm}-{dd}"
    dte = _dte_from_expiry(expiry, today)
    if dte < 0:
        return None
    abs_cost = (unreal_dollar / unreal_pct) if unreal_pct > 0 else 0.0
    contracts = int(abs(qty))
    is_short = qty < 0
    leg = OptionLeg(
        description=f"{'CALL' if cp=='C' else 'PUT'} {strike_s} {expiry}",
        strike=float(strike_s),
        expiry=expiry,
        option_type="CALL" if cp == "C" else "PUT",
        quantity=-contracts if is_short else contracts,
        premium_received=abs_cost if is_short else 0.0,
        current_mark=abs(cur_bal),
        dte=dte,
    )
    return underlying, leg


def _vanguard_equity_position(
    sym_raw: str, fields: tuple[float, float, float, float], price: float,
) -> tuple[str, str, Position]:
    """fields = (qty, unreal_dollar, unreal_pct, cur_bal) -- cur_bal is
    unused here but kept for symmetry with _vanguard_option_leg's fields
    tuple (both are built from the same regex-matched row)."""
    qty, unreal_dollar, unreal_pct, _cur_bal = fields
    abs_cost = (unreal_dollar / unreal_pct) if unreal_pct > 0 else 0.0
    shares = int(abs(qty)) if qty else 0
    cost_per_share = (abs_cost / shares) if shares > 0 else 0.0
    return ("equity", sym_raw, Position(
        symbol=sym_raw,
        account="",   # filled in by caller
        shares=shares,
        stock_cost_basis=cost_per_share,
        current_price=price,
    ))


def _parse_vanguard_row(line: str, today):
    """Parse one Vanguard holdings row. Returns (symbol, is_option, data_dict) or None."""
    line = line.replace("Transact", "").strip()
    m = _VANGUARD_ROW_RE.match(line)
    if not m:
        return None

    sym_raw, price_s, _, _, qty_s, unreal_s, unreal_pct_s, bal_s = m.groups()
    sym_raw = sym_raw.strip()

    try:
        price = _vanguard_numeric(price_s)
        qty = float(qty_s.replace(",", ""))
        unreal_dollar = _vanguard_numeric(unreal_s)
        unreal_pct = _vanguard_numeric(unreal_pct_s) / 100.0
        cur_bal = float(bal_s.replace(",", "").replace("$", ""))
    except ValueError:
        return None

    fields = (qty, unreal_dollar, unreal_pct, cur_bal)

    opt_m = _VANGUARD_OPT_RE.match(sym_raw)
    if opt_m:
        leg_result = _vanguard_option_leg(opt_m, fields, today)
        if leg_result is None:
            return None  # already expired — not an open position
        underlying, leg = leg_result
        return ("option", underlying, leg)

    return _vanguard_equity_position(sym_raw, fields, price)


def parse_vanguard_pdf(pdf_path: str, account_label: str) -> list["Position"]:
    """
    Parse a Vanguard 'Holdings | Vanguard' PDF export into Position objects.
    Derives cost basis from unrealized gain/loss columns.
    Falls back to CSV if pdfplumber unavailable.
    """
    import pdfplumber
    equity_map: dict[str, "Position"] = {}
    option_legs: dict[str, list["OptionLeg"]] = {}
    today = date.today()

    def _apply_line(line: str) -> None:
        """Parse one PDF text line and, if it's a position row, merge it
        into the enclosing equity_map/option_legs in place."""
        result = _parse_vanguard_row(line.strip(), today)
        if not result:
            return
        kind = result[0]
        if kind == "equity":
            _, sym, pos = result
            pos.account = account_label
            equity_map[sym] = pos
        elif kind == "option":
            _, underlying, leg = result
            option_legs.setdefault(underlying, []).append(leg)

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                _apply_line(line)

    _merge_option_legs_into_equity_map(equity_map, option_legs, account_label)
    return list(equity_map.values())


def _vanguard_csv_row_numbers(row: dict) -> Optional[tuple[float, float]]:
    """Parses (shares, price) from one Vanguard CSV row; None on bad data."""
    def _f(key):
        return row.get(key, "").replace("$", "").replace(",", "").strip()
    try:
        shares = float(_f("Shares")) if _f("Shares") else 0.0
        price = float(_f("Share Price")) if _f("Share Price") else 0.0
    except ValueError:
        return None
    return shares, price


def _vanguard_csv_option_leg(
    opt_m: re.Match, shares: float, price: float, today: date,
) -> Optional[tuple[str, OptionLeg]]:
    """No cost-basis data in this CSV format (unlike the PDF parser) --
    premium_received is always 0.0 here. Returns (underlying, OptionLeg), or
    None if the contract is already expired."""
    underlying, yy, mm, dd, cp, strike_s = opt_m.groups()
    expiry = f"20{yy}-{mm}-{dd}"
    dte = _dte_from_expiry(expiry, today)
    if dte < 0:
        return None
    contracts = int(abs(shares))
    is_short = shares < 0
    leg = OptionLeg(
        description=f"{'CALL' if cp=='C' else 'PUT'} {strike_s} {expiry}",
        strike=float(strike_s),
        expiry=expiry,
        option_type="CALL" if cp == "C" else "PUT",
        quantity=-contracts if is_short else contracts,
        premium_received=0.0,
        current_mark=price * 100 * contracts,
        dte=dte,
    )
    return underlying, leg


def _vanguard_csv_row_result(
    symbol_raw: str, row_numbers: tuple[float, float], account_label: str, today: date,
):
    """Dispatches one already-numeric-parsed Vanguard CSV row to either the
    option or equity path. Returns ("option", (underlying, OptionLeg)),
    ("equity", Position), or None if an option-shaped row is already
    expired (not an open position)."""
    shares, price = row_numbers
    opt_m = _VANGUARD_OPT_RE.match(symbol_raw)
    if not opt_m:
        return "equity", Position(
            symbol=symbol_raw,
            account=account_label,
            shares=int(abs(shares)) if shares else 0,
            stock_cost_basis=0.0,
            current_price=price,
        )
    leg_result = _vanguard_csv_option_leg(opt_m, shares, price, today)
    if leg_result is None:
        return None  # already expired -- not an open position
    return "option", leg_result


def parse_vanguard_csv(csv_path: str, account_label: str) -> list["Position"]:
    """
    Parse a Vanguard positions CSV (no cost basis available).
    Use parse_vanguard_pdf() instead when the Holdings PDF is available.
    """
    equity_map: dict[str, "Position"] = {}
    option_legs: dict[str, list["OptionLeg"]] = {}
    today = date.today()

    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            symbol_raw = row.get("Symbol", "").strip()
            if not symbol_raw:
                continue

            row_numbers = _vanguard_csv_row_numbers(row)
            if row_numbers is None:
                continue

            dispatched = _vanguard_csv_row_result(symbol_raw, row_numbers, account_label, today)
            if dispatched is None:
                continue
            kind, payload = dispatched
            if kind == "option":
                underlying, leg = payload
                option_legs.setdefault(underlying, []).append(leg)
            else:
                equity_map[symbol_raw] = payload

    _merge_option_legs_into_equity_map(equity_map, option_legs, account_label)
    return list(equity_map.values())
