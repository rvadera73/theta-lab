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
class LegHeat:
    symbol: str
    option_type: Literal["CALL", "PUT"]
    strike: float
    dte: int
    expiry: str
    premium_received: float    # credit when opened
    cost_to_close: float       # current ask/mark to BTC (positive = debit)
    current_price: float       # stock price now

    color: HeatColor = field(init=False)
    distance_pct: float = field(init=False)   # % buffer to strike
    pnl_pct: float = field(init=False)        # % of premium captured so far
    loss_multiple: float = field(init=False)  # cost_to_close / premium_received
    action: str = field(init=False)
    reason: str = field(init=False)

    def __post_init__(self) -> None:
        pr = self.premium_received
        ctc = self.cost_to_close

        # Legs with no live price can't be assessed — this is NOT the same as
        # "safe". Surfacing them as GREEN was hiding real risk (e.g. SMR/OKLO
        # puts sat unassessed for months while displaying as healthy). Use a
        # distinct UNKNOWN color so they're visibly separate from verified-safe.
        if not self.current_price or self.current_price <= 0:
            self.distance_pct = 0.0
            self.pnl_pct = 0.0
            self.loss_multiple = 0.0
            self.color = "UNKNOWN"
            self.action = "NO_PRICE"
            self.reason = "No live price available — NOT assessed, do not treat as safe"
            self.stagger_dte = max(180, self.dte + 75)
            return

        # Distance to strike (always positive)
        if self.option_type == "CALL":
            # How far stock is BELOW the call strike
            self.distance_pct = (self.strike - self.current_price) / self.current_price
        else:
            # How far stock is ABOVE the put strike
            self.distance_pct = (self.current_price - self.strike) / self.current_price

        self.pnl_pct     = (pr - ctc) / pr if pr > 0 else 0.0
        self.loss_multiple = ctc / pr if pr > 0 else 0.0

        # ── Traffic light ───────────────────────────────────────────────
        red_dist   = HEAT_THRESHOLDS[self.option_type.lower()]["red"]
        yellow_dist = HEAT_THRESHOLDS[self.option_type.lower()]["yellow"]
        loss_cut   = HEAT_THRESHOLDS["loss_cut_multiplier"]
        early_warn = HEAT_THRESHOLDS["early_warning_multiple"]
        profit_tgt = HEAT_THRESHOLDS["profit_target_pct"]

        if self.dte <= 7:
            self.color = "RED"
        elif self.loss_multiple >= loss_cut:
            self.color = "RED"
        elif self.distance_pct < red_dist:
            self.color = "RED"
        elif self.pnl_pct >= profit_tgt:
            # Profit target hit → YELLOW (action: harvest and redeploy)
            self.color = "YELLOW"
        elif self.loss_multiple >= early_warn:
            self.color = "YELLOW"
        elif self.distance_pct < yellow_dist:
            self.color = "YELLOW"
        elif self.dte <= 21:
            self.color = "YELLOW"
        else:
            self.color = "GREEN"

        self._set_action()

    def _set_action(self) -> None:
        pr   = self.premium_received
        typ  = self.option_type
        dte  = self.dte
        dist = self.distance_pct * 100
        pnl  = self.pnl_pct * 100
        mult = self.loss_multiple
        lm   = HEAT_THRESHOLDS["loss_cut_multiplier"]
        pt   = HEAT_THRESHOLDS["profit_target_pct"] * 100

        # Stagger re-entry DTE: when harvesting, re-open at current DTE + 60-90d minimum 180d.
        # Data: harvest 86-134 DTE → re-open 200-344 DTE. harvest 50 DTE → re-open 148-267 DTE.
        reentry_dte = max(180, dte + 75)

        if self.color == "GREEN":
            self.action = "HOLD"
            self.reason = f"{dist:.0f}% cushion to strike, {dte}d DTE — theta working"

        elif self.color == "YELLOW":
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
            elif dte <= 21:
                self.action = "CLOSE_RESTAGGER"
                self.reason = (
                    f"{dte}d DTE — gamma risk zone. "
                    f"BTC for ${self.cost_to_close:,.0f}, re-open at {reentry_dte}d DTE to keep premium engine running."
                )
            else:
                self.action = "PREPARE_ROLL"
                self.reason = (
                    f"Only {dist:.0f}% cushion to ${self.strike:.0f} {typ} strike — "
                    f"prepare to roll {'higher and further out' if typ == 'CALL' else 'lower and further out'}"
                )

        else:  # RED
            if mult >= lm:
                self.action = "CUT_RESTAGGER"
                self.reason = (
                    f"Cost-to-close ${self.cost_to_close:,.0f} = {mult:.1f}x premium ${pr:,.0f} — "
                    f"hard stop. BTC now. Re-enter fresh at {reentry_dte}d DTE only after name stabilises (wait 5-10d)."
                )
            elif dte <= 7:
                self.action = "CLOSE_NOW"
                self.reason = f"{dte}d DTE — close immediately to avoid pin/assignment risk"
            elif typ == "CALL":
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
    heat_legs = [LegHeat(**lg) for lg in legs]
    regime_cfg = HEAT_REGIME_ACTIONS.get(regime, HEAT_REGIME_ACTIONS["BULL"])

    by_color: dict[str, list[LegHeat]] = {"RED": [], "YELLOW": [], "GREEN": [], "UNKNOWN": []}
    for leg in heat_legs:
        by_color[leg.color].append(leg)

    # Sort RED by urgency (loss multiple desc, then distance asc)
    by_color["RED"].sort(key=lambda x: (-x.loss_multiple, x.distance_pct))

    # Regime-specific call tightening: in AI bull, demote YELLOW calls to RED
    if regime_cfg["call_tighten"]:
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

    # Build protocol message
    priority = regime_cfg["priority"]
    scale_back = regime_cfg["scale_back_strangles"]
    red_calls   = [l for l in by_color["RED"]  if l.option_type == "CALL"]
    red_puts    = [l for l in by_color["RED"]  if l.option_type == "PUT"]
    yell_calls  = [l for l in by_color["YELLOW"] if l.option_type == "CALL"]

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

    # Stagger deployment gate: how many calls can you add right now?
    # Rule from data: can carry 2-3 simultaneous calls per name as long as ALL are GREEN
    # Stop adding when ANY call is RED; be cautious when YELLOW
    all_calls = [l for l in heat_legs if l.option_type == "CALL"]
    all_puts  = [l for l in heat_legs if l.option_type == "PUT"]
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

    return {
        "by_color": {
            "RED":     [_leg_summary(l) for l in by_color["RED"]],
            "YELLOW":  [_leg_summary(l) for l in by_color["YELLOW"]],
            "GREEN":   [_leg_summary(l) for l in by_color["GREEN"]],
            "UNKNOWN": [_leg_summary(l) for l in by_color["UNKNOWN"]],
        },
        "counts": {k: len(v) for k, v in by_color.items()},
        "regime": regime,
        "scale_back_new_entries": scale_back,
        "protocol": " ".join(protocol_parts),
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
        return {"counts": {"RED": 0, "YELLOW": 0, "GREEN": 0},
                "by_color": {"RED": [], "YELLOW": [], "GREEN": []},
                "scale_back_new_entries": False,
                "protocol": "No open legs to assess.",
                "top_actions": []}
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

