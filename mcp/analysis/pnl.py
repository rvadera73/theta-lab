"""
Combined net P&L per position: stock cost basis + all option premiums collected/paid.
This is the metric that matters — not just options P&L in isolation.
"""

from dataclasses import dataclass, field
from typing import Optional


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
        symbol = instrument.get("symbol", "")
        qty = pos.get("longQuantity", 0) - pos.get("shortQuantity", 0)
        avg_price = pos.get("averagePrice", 0)
        current_price = quotes.get(symbol, {}).get("lastPrice", avg_price)

        if asset_type == "EQUITY":
            equity_map[symbol] = Position(
                symbol=symbol,
                account=account_label,
                shares=int(qty),
                stock_cost_basis=avg_price,
                current_price=current_price,
            )

        elif asset_type == "OPTION":
            underlying = instrument.get("underlyingSymbol") or symbol.split()[0]
            # putCall is present in the instrument; strike/expiry come from OSI symbol
            osi_expiry, osi_type, osi_strike = _parse_osi_symbol(symbol)
            option_type = instrument.get("putCall", osi_type) or osi_type
            strike = osi_strike
            expiry = osi_expiry

            from datetime import date
            try:
                exp_date = date.fromisoformat(expiry)
                dte = (exp_date - date.today()).days
            except Exception:
                dte = 0

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
            option_legs.setdefault(underlying, []).append(leg)

    # Merge option legs into positions (create equity position if no shares held)
    for underlying, legs in option_legs.items():
        if underlying not in equity_map:
            current_price = quotes.get(underlying, {}).get("lastPrice", 0)
            equity_map[underlying] = Position(
                symbol=underlying,
                account=account_label,
                shares=0,
                stock_cost_basis=0,
                current_price=current_price,
            )
        equity_map[underlying].option_legs.extend(legs)

    return list(equity_map.values())
