"""
Position Heat Scanner
=====================
Scans all open short option legs and assigns a traffic light based on:
  - Distance of current stock price to strike (primary trigger)
  - Cost-to-close as a multiple of premium received (loss amplification)
  - DTE remaining (gamma risk zone)

Management rules derived from Account A transaction history (195 matched trades):
  - Calls ROLLED when stock falls (repriced cheap): harvest + re-sell at lower strike
  - Puts CUT at loss when stock falls through strike; immediately re-open at new level
  - AI/momentum bull protocol: tighten call monitoring, scale back new strangles
  - Profit target: 40-50% of premium (median 44% from data, NOT 55-70%)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

from config import HEAT_THRESHOLDS, HEAT_REGIME_ACTIONS

HeatColor = Literal["GREEN", "YELLOW", "RED", "UNKNOWN"]


@dataclass
class LegContract:
    """Position-identity fields for a single short option leg (excludes dte,
    which is time-varying rather than identity, and is kept on LegHeat itself
    so both this and LegPricing stay at <=4 required fields)."""
    symbol: str
    option_type: Literal["CALL", "PUT"]
    strike: float
    expiry: str


@dataclass
class LegPricing:
    """Pricing fields for a single short option leg."""
    premium_received: float    # credit when opened
    cost_to_close: float       # current ask/mark to BTC (positive = debit)
    current_price: float       # stock price now


@dataclass
class LegHeat:
    contract: LegContract
    pricing: LegPricing
    dte: int

    color: HeatColor = field(init=False)
    distance_pct: float = field(init=False)   # % buffer to strike
    pnl_pct: float = field(init=False)        # % of premium captured so far
    loss_multiple: float = field(init=False)  # cost_to_close / premium_received
    action: str = field(init=False)
    reason: str = field(init=False)

    def __post_init__(self) -> None:
        # Flatten the grouped contract/pricing inputs onto the instance so the
        # rest of this class (and every external reader of a LegHeat) keeps
        # using the same plain attribute names as before the 4-param-max
        # constructor refactor. (dte is already a flat field -- see above.)
        self.symbol = self.contract.symbol
        self.option_type = self.contract.option_type
        self.strike = self.contract.strike
        self.expiry = self.contract.expiry
        self.premium_received = self.pricing.premium_received
        self.cost_to_close = self.pricing.cost_to_close
        self.current_price = self.pricing.current_price

        if self._apply_unknown_price_state():
            return

        self.distance_pct = self._compute_distance_pct()
        self.pnl_pct, self.loss_multiple = self._compute_pnl_and_loss_multiple()
        self.color = self._determine_color()
        self._set_action()

    def _apply_unknown_price_state(self) -> bool:
        """
        Legs with no live price can't be assessed — this is NOT the same as
        "safe". Surfacing them as GREEN was hiding real risk (e.g. SMR/OKLO
        puts sat unassessed for months while displaying as healthy). Use a
        distinct UNKNOWN color so they're visibly separate from verified-safe.

        Returns True (and sets all UNKNOWN-state fields) when there is no
        usable live price; returns False otherwise.
        """
        if not self.current_price or self.current_price <= 0:
            self.distance_pct = 0.0
            self.pnl_pct = 0.0
            self.loss_multiple = 0.0
            self.color = "UNKNOWN"
            self.action = "NO_PRICE"
            self.reason = "No live price available — NOT assessed, do not treat as safe"
            self.stagger_dte = max(180, self.dte + 75)
            return True
        return False

    def _compute_distance_pct(self) -> float:
        """Distance to strike (always positive)."""
        if self.option_type == "CALL":
            # How far stock is BELOW the call strike
            return (self.strike - self.current_price) / self.current_price
        # How far stock is ABOVE the put strike
        return (self.current_price - self.strike) / self.current_price

    def _compute_pnl_and_loss_multiple(self) -> tuple[float, float]:
        pr = self.premium_received
        ctc = self.cost_to_close
        pnl_pct = (pr - ctc) / pr if pr > 0 else 0.0
        loss_multiple = ctc / pr if pr > 0 else 0.0
        return pnl_pct, loss_multiple

    def _determine_color(self) -> HeatColor:
        red_dist    = HEAT_THRESHOLDS[self.option_type.lower()]["red"]
        yellow_dist = HEAT_THRESHOLDS[self.option_type.lower()]["yellow"]
        loss_cut    = HEAT_THRESHOLDS["loss_cut_multiplier"]
        early_warn  = HEAT_THRESHOLDS["early_warning_multiple"]
        profit_tgt  = HEAT_THRESHOLDS["profit_target_pct"]

        # Real bug found 2026-10-15: strike-proximity (distance_pct) and the
        # hard loss-cut (loss_multiple) fired RED regardless of DTE, even
        # when 90-180+ days remained -- directly contradicting this
        # trader's own documented Roll Decision Framework ("Short put ITM,
        # thesis intact, DTE > 45 -> HOLD, do not roll -- time is working").
        # Confirmed live: 89 of 130 RED legs had 91+ DTE remaining, with only
        # 2 inside 21 days -- the color was flagging "far-dated and merely
        # close to strike" exactly as urgently as "expiring this week," which
        # made the whole Position Heat view read as a portfolio-wide
        # emergency when it wasn't one. loss_cut (hard stop, cost-to-close
        # already a real multiple of premium) stays DTE-independent --- a
        # genuine hard-stop loss is urgent regardless of time left. Strike
        # proximity alone is not: it only becomes RED-urgent within the same
        # "time is working" window this trader already uses for roll
        # decisions.
        RED_DTE_WINDOW = 45
        if self.dte <= 7:
            return "RED"
        if self.loss_multiple >= loss_cut:
            return "RED"
        if self.distance_pct < red_dist and self.dte <= RED_DTE_WINDOW:
            return "RED"
        if self.distance_pct < red_dist:
            # Strike-proximity stress with real time still on the clock --
            # matches "time is working," not yet an action-now signal.
            return "YELLOW"
        if self.pnl_pct >= profit_tgt:
            # Profit target hit → YELLOW (action: harvest and redeploy)
            return "YELLOW"
        if self.loss_multiple >= early_warn:
            return "YELLOW"
        if self.distance_pct < yellow_dist:
            return "YELLOW"
        if self.dte <= 21:
            return "YELLOW"
        return "GREEN"

    def _set_action(self) -> None:
        reentry_dte = max(180, self.dte + 75)

        if self.color == "GREEN":
            self._set_green_action()
        elif self.color == "YELLOW":
            self._set_yellow_action(reentry_dte)
        else:  # RED
            self._set_red_action(reentry_dte)

    def _set_green_action(self) -> None:
        dist = self.distance_pct * 100
        self.action = "HOLD"
        self.reason = f"{dist:.0f}% cushion to strike, {self.dte}d DTE — theta working"

    def _set_yellow_action(self, reentry_dte: int) -> None:
        dist = self.distance_pct * 100
        pnl  = self.pnl_pct * 100
        mult = self.loss_multiple
        lm   = HEAT_THRESHOLDS["loss_cut_multiplier"]
        pt   = HEAT_THRESHOLDS["profit_target_pct"] * 100

        if pnl >= pt:
            self.action = "HARVEST_RESTAGGER"
            self.reason = (
                f"{pnl:.0f}% profit captured — BTC for ${self.cost_to_close:,.0f}. "
                f"Re-open SAME NAME at {reentry_dte}d DTE (current+75d), same/slightly lower strike. "
                f"Re-entry within 1 week. Data: you re-stagger median 10d after harvest."
            )
        elif mult >= HEAT_THRESHOLDS["early_warning_multiple"]:
            self.action = "WATCH_CLOSE"
            self.reason = f"Cost-to-close is {mult:.1f}x premium — approaching loss threshold ({lm:.0f}x)"
        elif self.dte <= 21:
            self.action = "CLOSE_RESTAGGER"
            self.reason = (
                f"{self.dte}d DTE — gamma risk zone. "
                f"BTC for ${self.cost_to_close:,.0f}, re-open at {reentry_dte}d DTE to keep premium engine running."
            )
        else:
            self.action = "PREPARE_ROLL"
            self.reason = (
                f"Only {dist:.0f}% cushion to ${self.strike:.0f} {self.option_type} strike — "
                f"prepare to roll {'higher and further out' if self.option_type == 'CALL' else 'lower and further out'}"
            )

    def _set_red_action(self, reentry_dte: int) -> None:
        pr   = self.premium_received
        dist = self.distance_pct * 100
        mult = self.loss_multiple
        lm   = HEAT_THRESHOLDS["loss_cut_multiplier"]

        if mult >= lm:
            self.action = "CUT_RESTAGGER"
            self.reason = (
                f"Cost-to-close ${self.cost_to_close:,.0f} = {mult:.1f}x premium ${pr:,.0f} — "
                f"hard stop. BTC now. Re-enter fresh at {reentry_dte}d DTE only after name stabilises (wait 5-10d)."
            )
        elif self.dte <= 7:
            self.action = "CLOSE_NOW"
            self.reason = f"{self.dte}d DTE — close immediately to avoid pin/assignment risk"
        elif self.option_type == "CALL":
            self.action = "ROLL_CALL"
            self.reason = (
                f"Only {dist:.0f}% below ${self.strike:.0f} CALL — "
                f"ROLL: BTC ${self.cost_to_close:,.0f}, sell new CALL at higher strike + {reentry_dte}d DTE for net credit. "
                f"If AI bull melt-up: CUT and pause calls on this name."
            )
        else:
            self.action = "ROLL_OR_CUT_PUT"
            self.reason = (
                f"Only {dist:.0f}% above ${self.strike:.0f} PUT — "
                f"If thesis intact: roll down-and-out to {reentry_dte}d DTE for credit. "
                f"If thesis broken: CUT at ${self.cost_to_close:,.0f} and re-enter fresh after 5-10d."
            )


def _build_heat_legs(legs: list[dict]) -> list[LegHeat]:
    """Construct a LegHeat per raw leg dict (see assess_portfolio_heat's docstring
    for the expected keys)."""
    heat_legs = []
    for lg in legs:
        contract = LegContract(
            symbol=lg["symbol"], option_type=lg["option_type"], strike=lg["strike"],
            expiry=lg["expiry"],
        )
        pricing = LegPricing(
            premium_received=lg["premium_received"],
            cost_to_close=lg["cost_to_close"],
            current_price=lg["current_price"],
        )
        heat_legs.append(LegHeat(contract=contract, pricing=pricing, dte=lg["dte"]))
    return heat_legs


def _bucket_by_color(heat_legs: list[LegHeat]) -> dict[str, list[LegHeat]]:
    by_color: dict[str, list[LegHeat]] = {"RED": [], "YELLOW": [], "GREEN": [], "UNKNOWN": []}
    for leg in heat_legs:
        by_color[leg.color].append(leg)

    # Sort RED by urgency (loss multiple desc, then distance asc)
    by_color["RED"].sort(key=lambda x: (-x.loss_multiple, x.distance_pct))
    return by_color


def _apply_call_tighten(by_color: dict[str, list[LegHeat]], regime_cfg: dict) -> None:
    """Regime-specific call tightening: in AI bull, demote YELLOW calls to RED."""
    if not regime_cfg["call_tighten"]:
        return

    newly_red = []
    for leg in by_color["YELLOW"][:]:
        if leg.option_type == "CALL" and leg.distance_pct < 0.12:
            leg.color = "RED"
            leg.action = "ROLL_CALL"
            leg.reason = (
                f"⚡ AI-bull tighten: {leg.distance_pct*100:.0f}% to ${leg.strike:.0f} CALL. "
                f"In momentum rally, calls face melt-up risk. Roll before heat increases."
            )
            newly_red.append(leg)
    for leg in newly_red:
        by_color["YELLOW"].remove(leg)
        by_color["RED"].append(leg)


def _build_protocol_message(by_color: dict[str, list[LegHeat]], regime: str, regime_cfg: dict) -> str:
    scale_back = regime_cfg["scale_back_strangles"]
    red_calls  = [l for l in by_color["RED"]    if l.option_type == "CALL"]
    red_puts   = [l for l in by_color["RED"]    if l.option_type == "PUT"]
    yell_calls = [l for l in by_color["YELLOW"] if l.option_type == "CALL"]

    protocol_parts = []
    if scale_back and (red_calls or yell_calls):
        protocol_parts.append(
            f"⚡ {regime} protocol: PAUSE new strangles until {len(red_calls)+len(yell_calls)} "
            f"call(s) are rolled/harvested. Recycle puts first to free up premium budget."
        )
    if red_calls:
        protocol_parts.append(
            f"🔴 {len(red_calls)} call(s) need immediate action (AI melt-up risk)."
        )
    if red_puts:
        protocol_parts.append(
            f"🔴 {len(red_puts)} put(s) need action."
        )
    if not by_color["RED"]:
        protocol_parts.append("✅ No RED positions. Monitor YELLOW legs.")
    return " ".join(protocol_parts)


def _build_top_actions(by_color: dict[str, list[LegHeat]]) -> list[dict]:
    top_actions = []
    for leg in by_color["RED"] + by_color["YELLOW"]:
        top_actions.append({
            "color":        leg.color,
            "symbol":       leg.symbol,
            "option_type":  leg.option_type,
            "strike":       leg.strike,
            "expiry":       leg.expiry,
            "dte":          leg.dte,
            "pnl_pct":      round(leg.pnl_pct * 100, 1),
            "distance_pct": round(leg.distance_pct * 100, 1),
            "loss_multiple": round(leg.loss_multiple, 2),
            "action":       leg.action,
            "reason":       leg.reason,
        })
    return top_actions


def _build_stagger_capacity(heat_legs: list[LegHeat]) -> dict[str, str]:
    """
    Stagger deployment gate: how many calls can you add right now?
    Rule from data: can carry 2-3 simultaneous calls per name as long as ALL are GREEN.
    Stop adding when ANY call is RED; be cautious when YELLOW.
    """
    all_calls = [l for l in heat_legs if l.option_type == "CALL"]
    calls_by_sym: dict[str, list[LegHeat]] = {}
    for lg in all_calls:
        calls_by_sym.setdefault(lg.symbol, []).append(lg)

    stagger_capacity: dict[str, str] = {}
    for sym, sym_legs in calls_by_sym.items():
        reds    = [l for l in sym_legs if l.color == "RED"]
        yellows = [l for l in sym_legs if l.color == "YELLOW"]
        greens  = [l for l in sym_legs if l.color == "GREEN"]
        if reds:
            stagger_capacity[sym] = f"STOP — {len(reds)} RED call(s). Roll/cut first."
        elif len(sym_legs) >= 3:
            stagger_capacity[sym] = f"FULL ({len(sym_legs)} calls) — harvest a YELLOW before adding."
        elif yellows:
            stagger_capacity[sym] = (
                f"HARVEST_FIRST — {len(yellows)} call(s) at profit target. "
                f"BTC those, then re-stagger at longer DTE."
            )
        else:
            stagger_capacity[sym] = f"OPEN — {len(greens)} call(s) GREEN. Can add 1 more stagger leg."
    return stagger_capacity


def assess_portfolio_heat(
    legs: list[dict],
    regime: str,
) -> dict:
    """
    Assess heat across all open short legs.

    Parameters
    ----------
    legs : list of dicts with keys:
        symbol, option_type, strike, dte, expiry,
        premium_received, cost_to_close, current_price
    regime : current regime string e.g. "CAUTIOUS_BULL"

    Returns
    -------
    dict with:
        - by_color: {"RED": [...], "YELLOW": [...], "GREEN": [...]}
        - regime_protocol: string describing action priorities
        - scale_back: bool — should pause new strangles
        - top_actions: ordered list of most urgent items
    """
    heat_legs = _build_heat_legs(legs)
    regime_cfg = HEAT_REGIME_ACTIONS.get(regime, HEAT_REGIME_ACTIONS["BULL"])

    by_color = _bucket_by_color(heat_legs)
    _apply_call_tighten(by_color, regime_cfg)

    protocol = _build_protocol_message(by_color, regime, regime_cfg)
    top_actions = _build_top_actions(by_color)
    stagger_capacity = _build_stagger_capacity(heat_legs)

    return {
        "by_color": {
            "RED":     [_leg_summary(l) for l in by_color["RED"]],
            "YELLOW":  [_leg_summary(l) for l in by_color["YELLOW"]],
            "GREEN":   [_leg_summary(l) for l in by_color["GREEN"]],
            "UNKNOWN": [_leg_summary(l) for l in by_color["UNKNOWN"]],
        },
        "counts": {k: len(v) for k, v in by_color.items()},
        "regime": regime,
        "scale_back_new_entries": regime_cfg["scale_back_strangles"],
        "protocol": protocol,
        "top_actions": top_actions,
        "stagger_capacity": stagger_capacity,
    }


def _leg_summary(leg: LegHeat) -> dict:
    return {
        "symbol":       leg.symbol,
        "type":         leg.option_type,
        "strike":       leg.strike,
        "expiry":       leg.expiry,
        "dte":          leg.dte,
        "current_price": leg.current_price,
        "distance_pct": round(leg.distance_pct * 100, 1),
        "pnl_pct":      round(leg.pnl_pct * 100, 1),
        "loss_multiple": round(leg.loss_multiple, 2),
        "color":        leg.color,
        "action":       leg.action,
        "reason":       leg.reason,
    }


# ---------------------------------------------------------------------------
# Helpers for report integration
# ---------------------------------------------------------------------------

def heat_from_positions(positions: list, regime: str) -> dict:
    """
    Build heat assessment directly from a list of Position objects
    (analysis.pnl.Position). Shared by weekly/monthly/research flows.
    """
    legs = []
    for pos in positions:
        for lg in pos.option_legs:
            pr  = getattr(lg, "premium_received", 0) or 0
            ctc = getattr(lg, "current_mark", 0) or 0
            if pr <= 0:
                continue
            legs.append({
                "symbol":           pos.symbol,
                "option_type":      lg.option_type,
                "strike":           lg.strike,
                "dte":              lg.dte,
                "expiry":           lg.expiry,
                "premium_received": pr,
                "cost_to_close":    ctc,
                "current_price":    pos.current_price,
            })
    if not legs:
        # Real bug found while writing characterization tests (2026-11-09):
        # this shortcut dict omitted the "UNKNOWN" bucket that
        # assess_portfolio_heat() always includes (by_color + counts), and
        # omitted "stagger_capacity"/"regime" too. format_heat_block() and
        # format_heat_html() both index heat["by_color"]["UNKNOWN"] directly
        # (no .get/default) -- and both real call sites (weekly_report.py,
        # monthly_objectives_report.py) call heat_from_positions() and pipe
        # the result straight into one of those formatters. Any no-open-legs
        # week (a real, unremarkable case, not a hypothetical) crashed report
        # generation with KeyError: 'UNKNOWN'. Shape now matches
        # assess_portfolio_heat()'s return exactly so both formatters (and
        # any other consumer) see a consistent dict whether or not there are
        # open legs.
        return {"counts": {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0},
                "by_color": {"RED": [], "YELLOW": [], "GREEN": [], "UNKNOWN": []},
                "regime": regime,
                "scale_back_new_entries": False,
                "protocol": "No open legs to assess.",
                "top_actions": [],
                "stagger_capacity": {}}
    return assess_portfolio_heat(legs, regime)


def format_heat_block(heat: dict, title: str = "Portfolio Heat") -> str:
    """
    Compact text block for embedding inside weekly/monthly/research text reports.
    Shows RED/YELLOW legs with actions, stagger capacity per name, GREEN count summarised.
    """
    c = heat["counts"]
    emoji_map = {"RED": "🔴", "YELLOW": "🟡", "UNKNOWN": "⚪"}
    unknown_ct = c.get("UNKNOWN", 0)
    lines = [
        f"### 🌡️ {title}",
        f"**{c['RED']} RED · {c['YELLOW']} YELLOW · {c['GREEN']} GREEN"
        f"{f' · {unknown_ct} UNKNOWN (no price — not assessed)' if unknown_ct else ''}**   "
        f"{'⛔ Scale back new strangles.' if heat['scale_back_new_entries'] else ''}",
        heat["protocol"],
        "",
    ]
    for color in ("RED", "YELLOW", "UNKNOWN"):
        items = heat["by_color"][color]
        if not items:
            continue
        lines.append(f"**{emoji_map[color]} {color}**")
        for it in items:
            lines.append(
                f"- {it['symbol']} {it['type']} ${it['strike']:.0f} "
                f"exp {it['expiry']} ({it['dte']}d) | "
                f"price=${it['current_price']:,.2f} | "
                f"{it['distance_pct']:.0f}% to strike | "
                f"{it['pnl_pct']:.0f}% P&L captured | "
                f"**{it['action']}** — {it['reason']}"
            )
        lines.append("")

    stagger = heat.get("stagger_capacity", {})
    if stagger:
        lines.append("**📊 Stagger Capacity per Name**")
        for sym, status in sorted(stagger.items()):
            icon = "🔴" if "STOP" in status else ("🟡" if "HARVEST" in status else ("✅" if "OPEN" in status else "⏸️"))
            lines.append(f"- {icon} **{sym}**: {status}")
        lines.append("")

    return "\n".join(lines)


def format_heat_html(heat: dict) -> str:
    """
    HTML fragment for embedding inside monthly report email.
    """
    c = heat["counts"]
    scale_msg = (
        "<b>⛔ Scale back new strangles until RED/YELLOW calls are resolved.</b><br>"
        if heat["scale_back_new_entries"] else ""
    )
    color_map = {"RED": "#c0392b", "YELLOW": "#e67e22", "GREEN": "#27ae60", "UNKNOWN": "#7f8c8d"}
    rows = []
    for color in ("RED", "YELLOW", "GREEN", "UNKNOWN"):
        items = heat["by_color"][color]
        for it in items:
            bg = color_map[color]
            rows.append(
                f"<tr style='background:{bg}20'>"
                f"<td><b style='color:{bg}'>{color}</b></td>"
                f"<td>{it['symbol']}</td>"
                f"<td>{it['type']} ${it['strike']:.0f}</td>"
                f"<td>{it['expiry']} ({it['dte']}d)</td>"
                f"<td>${it['current_price']:,.2f}</td>"
                f"<td>{it['distance_pct']:.0f}%</td>"
                f"<td>{it['pnl_pct']:.0f}%</td>"
                f"<td><b>{it['action']}</b></td>"
                f"<td style='font-size:0.85em'>{it['reason']}</td>"
                f"</tr>"
            )
    rows_html = "\n".join(rows) if rows else "<tr><td colspan='9'>No open legs.</td></tr>"
    return f"""
<div style="margin:20px 0">
  <h3>🌡️ Portfolio Heat — {c['RED']} RED · {c['YELLOW']} YELLOW · {c['GREEN']} GREEN · {c.get('UNKNOWN', 0)} UNKNOWN</h3>
  <p>{heat['protocol']}<br>{scale_msg}</p>
  <table border='1' cellpadding='5' cellspacing='0' style='border-collapse:collapse;width:100%;font-size:0.9em'>
    <thead style='background:#2c3e50;color:white'>
      <tr>
        <th>Heat</th><th>Symbol</th><th>Leg</th><th>Expiry</th>
        <th>Price</th><th>% to Strike</th><th>P&L%</th><th>Action</th><th>Reason</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>"""
