import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

// Reuses the good/warning/critical pair from the dataviz skill's validated
// status palette (contrast-checked via validate_palette.js earlier this
// session), not a re-pick for the light theme.
const SEVERITY_HEX: Record<string, string> = { RED: "#d03b3b", YELLOW: "#fab219", GREEN: "#0ca30c", UNKNOWN: "#9aa1ad" };

function Dot({ color }: { color: string }) {
  return <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5 shrink-0" style={{ backgroundColor: color }} />;
}

// Real fix (2026-10-16, trader correction): removed the separate "selected
// row -> preview pane below" indirection entirely -- a real per-row action
// (like Robinhood's own row-level actions) is the direct, standard pattern,
// not an intermediate selection state. Clicking "Details" opens the full
// viewer immediately; there is no compact in-between pane anymore.
export default function ItemsTable({ plan, onViewFull }: { plan: PlanItem[]; onViewFull: (idx: number) => void }) {
  if (!plan.length) {
    return <p className="text-faint italic text-center py-8 text-sm">Nothing actionable right now.</p>;
  }

  // Real fix (2026-10-16, trader correction): a NEW ENTRY CANDIDATES row has
  // no severity/legs/cost-to-close (those three columns showed bare dashes)
  // but DOES carry a real composite score + IV rank -- surface those in the
  // same columns instead of hiding them behind "Details" for this row type.
  function rowMeta(item: PlanItem) {
    const { ref } = item;
    if (isPositionGroup(ref)) {
      return {
        severity: (
          <span className="inline-flex items-center text-muted">
            <Dot color={SEVERITY_HEX[ref.worst_color] || SEVERITY_HEX.UNKNOWN} />
            {ref.worst_color}
          </span>
        ),
        legs: String(ref.leg_count),
        costToClose: ref.total_cost_to_close != null ? "$" + ref.total_cost_to_close.toLocaleString() : "—",
        extra: ref.account,
      };
    }
    return {
      severity: (
        <span className="tabular-nums text-ink/90">
          score {ref.score ?? "—"} <span className="text-faint">(#{ref.rank ?? "—"})</span>
        </span>
      ),
      legs: ref.iv_rank != null ? `IVR ${ref.iv_rank}` : "—",
      costToClose: "—",
      extra: ref.sector,
    };
  }

  return (
    <div className="bg-panel border border-border rounded-md overflow-hidden overflow-x-auto">
      <table className="w-full text-[12.5px] border-collapse">
        <thead>
          <tr className="text-left text-muted uppercase text-[10px] bg-panelAlt">
            <th className="px-3 py-2 font-semibold">Section</th>
            <th className="px-3 py-2 font-semibold">Action</th>
            <th className="px-3 py-2 font-semibold">Severity / score</th>
            <th className="px-3 py-2 font-semibold text-right">Legs / IVR</th>
            <th className="px-3 py-2 font-semibold text-right">Cost to close</th>
            <th className="px-3 py-2 font-semibold">Account / sector</th>
            <th className="px-3 py-2 font-semibold text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {plan.map((item, idx) => {
            const meta = rowMeta(item);
            return (
              <tr key={idx} className="border-t border-border/60 hover:bg-panelAlt/50 transition-colors">
                <td className="px-3 py-[7px] text-faint whitespace-nowrap">{item.section}</td>
                <td className="px-3 py-[7px] text-ink/90 truncate max-w-[280px]">{item.action}</td>
                <td className="px-3 py-[7px]">{meta.severity}</td>
                <td className="px-3 py-[7px] text-right tabular-nums text-muted">{meta.legs}</td>
                <td className="px-3 py-[7px] text-right tabular-nums text-muted">{meta.costToClose}</td>
                <td className="px-3 py-[7px] text-faint whitespace-nowrap">{meta.extra || "—"}</td>
                <td className="px-3 py-[7px] text-right">
                  <button onClick={() => onViewFull(idx)} className="text-accent text-[12px] font-medium hover:underline">
                    Details
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
