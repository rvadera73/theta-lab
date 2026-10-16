import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

const SEVERITY_HEX: Record<string, string> = { RED: "#ff5a5f", YELLOW: "#f7941d", GREEN: "#1ec47c", UNKNOWN: "#5c6578" };

function Dot({ color }: { color: string }) {
  return <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5 shrink-0" style={{ backgroundColor: color }} />;
}

// Real layout fix (2026-10-16): the prior version was a single narrow
// column of buttons regardless of how it was themed -- same structure as
// the very first iteration, just recolored. The reference (Robinhood
// Legend) uses a WIDE, multi-column table as its primary surface (Symbol,
// Qty, Mkt val, Mark, Avg price, Last, P&L...), not a narrow list. This
// mirrors that: one real table, real columns, right-aligned tabular
// numbers, severity as a dot in its own column (never a whole-row tint).
export default function ItemsTable({
  plan,
  selectedIdx,
  onSelect,
}: {
  plan: PlanItem[];
  selectedIdx: number | null;
  onSelect: (idx: number) => void;
}) {
  if (!plan.length) {
    return <p className="text-faint italic text-center py-8 text-sm">Nothing actionable right now.</p>;
  }

  function rowMeta(item: PlanItem) {
    const { ref } = item;
    if (isPositionGroup(ref)) {
      return {
        severity: ref.worst_color,
        legs: ref.leg_count,
        costToClose: ref.total_cost_to_close,
        extra: ref.account,
      };
    }
    return {
      severity: null as string | null,
      legs: null as number | null,
      costToClose: null as number | null,
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
            <th className="px-3 py-2 font-semibold">Severity</th>
            <th className="px-3 py-2 font-semibold text-right">Legs</th>
            <th className="px-3 py-2 font-semibold text-right">Cost to close</th>
            <th className="px-3 py-2 font-semibold">Account / sector</th>
          </tr>
        </thead>
        <tbody>
          {plan.map((item, idx) => {
            const meta = rowMeta(item);
            const isSelected = idx === selectedIdx;
            return (
              <tr
                key={idx}
                onClick={() => onSelect(idx)}
                className={`cursor-pointer border-t border-border/60 transition-colors ${isSelected ? "bg-panelAlt" : "hover:bg-panelAlt/50"}`}
              >
                <td className="px-3 py-[7px] text-faint whitespace-nowrap">{item.section}</td>
                <td className={`px-3 py-[7px] truncate max-w-[280px] ${isSelected ? "text-ink font-medium" : "text-ink/90"}`}>{item.action}</td>
                <td className="px-3 py-[7px]">
                  {meta.severity ? (
                    <span className="inline-flex items-center text-muted">
                      <Dot color={SEVERITY_HEX[meta.severity] || SEVERITY_HEX.UNKNOWN} />
                      {meta.severity}
                    </span>
                  ) : (
                    <span className="text-faint">—</span>
                  )}
                </td>
                <td className="px-3 py-[7px] text-right tabular-nums text-muted">{meta.legs ?? "—"}</td>
                <td className="px-3 py-[7px] text-right tabular-nums text-muted">
                  {meta.costToClose != null ? "$" + meta.costToClose.toLocaleString() : "—"}
                </td>
                <td className="px-3 py-[7px] text-faint whitespace-nowrap">{meta.extra || "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
