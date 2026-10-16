import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

const SEVERITY_HEX: Record<string, string> = { RED: "#ff5a5f", YELLOW: "#f7941d", GREEN: "#1ec47c", UNKNOWN: "#5c6578" };

function Dot({ color }: { color: string }) {
  return <span className="inline-block w-1.5 h-1.5 rounded-full mr-1" style={{ backgroundColor: color }} />;
}

export default function DetailPane({ item, onViewFull }: { item: PlanItem | null; onViewFull: () => void }) {
  if (!item) {
    return (
      <div className="bg-panel border border-border rounded-md px-4 py-3 mb-3 min-h-[64px] flex items-center">
        <p className="text-faint italic text-[13px]">Select a row below to preview it here.</p>
      </div>
    );
  }

  const { ref } = item;
  const legColorCounts: Record<string, number> = {};
  if (isPositionGroup(ref)) {
    for (const lg of ref.legs) legColorCounts[lg.color] = (legColorCounts[lg.color] || 0) + 1;
  }

  return (
    <div className="bg-panel border border-border rounded-md px-4 py-3 mb-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-[10px] uppercase font-semibold tracking-wide text-muted mb-0.5">{item.section}</div>
          <div className="text-[14px] font-semibold text-ink mb-1 truncate">{item.action}</div>
          <p className="text-[12.5px] text-muted line-clamp-2">{item.why}</p>
          {isPositionGroup(ref) && (
            <div className="mt-1.5 text-[11px] text-muted">
              {Object.entries(legColorCounts).map(([color, n]) => (
                <span key={color} className="mr-3 tabular-nums">
                  <Dot color={SEVERITY_HEX[color] || SEVERITY_HEX.UNKNOWN} />
                  {n} {color.toLowerCase()}
                </span>
              ))}
            </div>
          )}
        </div>
        <button onClick={onViewFull} className="shrink-0 text-[12px] font-medium text-accent hover:underline whitespace-nowrap">
          View full details →
        </button>
      </div>
    </div>
  );
}
