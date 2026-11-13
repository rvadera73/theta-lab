import type { HeatLeg, PositionGroupRef, Leg } from "../types";

// Must match the backend's services._POSITION_COLOR_RANK exactly: RED
// worst, then YELLOW, then UNKNOWN, then GREEN best. UNKNOWN ranks worse
// than GREEN because an unscored/needs-review leg is not the same as a
// confirmed-healthy one -- a prior mismatch here (GREEN ranked ahead of
// UNKNOWN) let the US dashboard show a reassuring GREEN worst_color for a
// group the backend's own grouping would treat as UNKNOWN (issue #50).
const SEVERITY_RANK: Record<string, number> = { RED: 0, YELLOW: 1, UNKNOWN: 2, GREEN: 3 };

// Mirrors the backend's services._group_positions_by_symbol_account()
// grouping (by symbol + account, worst color wins) so the US tab's full
// Position Heat review presents the same real per-leg data the same way
// the backend does.
export function groupHeatLegs(legs: HeatLeg[]): PositionGroupRef[] {
  const groups = new Map<string, { legs: Leg[]; account: string; symbol: string; sector: string }>();
  for (const lg of legs) {
    const key = `${lg.symbol}|${lg.account}`;
    if (!groups.has(key)) {
      groups.set(key, { legs: [], account: lg.account, symbol: lg.symbol, sector: lg.sector || "" });
    }
    groups.get(key)!.legs.push({
      symbol: lg.symbol,
      type: lg.type as "CALL" | "PUT",
      strike: lg.strike,
      expiry: lg.expiry,
      dte: lg.dte,
      color: lg.color,
      action: lg.action,
      reason: lg.reason,
      covered: lg.covered,
      covered_contracts: lg.covered_contracts,
      total_contracts: lg.total_contracts,
      strangle: lg.strangle,
      account: lg.account,
      sector: lg.sector,
      gates_fired: lg.gates_fired,
    });
  }

  const result: PositionGroupRef[] = [];
  for (const { legs: groupLegs, account, symbol, sector } of groups.values()) {
    const worst = [...groupLegs].sort((a, b) => SEVERITY_RANK[a.color] - SEVERITY_RANK[b.color])[0];
    const totalCost = groupLegs.reduce((sum, lg) => {
      const src = legs.find((l) => l.symbol === lg.symbol && l.account === lg.account && l.strike === lg.strike && l.expiry === lg.expiry && l.type === lg.type);
      return sum + (src?.cost_to_close || 0);
    }, 0);
    result.push({
      symbol,
      account,
      sector,
      legs: groupLegs,
      worst_color: worst.color,
      worst_action: worst.action,
      leg_count: groupLegs.length,
      total_cost_to_close: totalCost,
    });
  }
  return result.sort((a, b) => SEVERITY_RANK[a.worst_color] - SEVERITY_RANK[b.worst_color]);
}
