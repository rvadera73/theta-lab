import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

// Color discipline fixed against the real reference (Robinhood Legend,
// 2026-10-16): that screen reserves green/red STRICTLY for gain/loss
// direction, never for generic category labels. RED/YELLOW/GREEN here are
// genuine position-heat severity (a real directional signal, same family
// as P&L color), so they keep a color dot; the SECTION grouping (GATE,
// CASH RELIEF, etc.) is a category, not a direction -- it no longer gets
// its own arbitrary color, just a plain group header, same as "Positions"
// is a plain header in the reference, not color-coded.
const SEVERITY_HEX: Record<string, string> = { RED: "#ff5a5f", YELLOW: "#f7941d", GREEN: "#1ec47c", UNKNOWN: "#5c6578" };

function Dot({ color }: { color: string }) {
  return <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5" style={{ backgroundColor: color }} />;
}

export default function ItemList({
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

  const sections: { name: string; items: { item: PlanItem; idx: number }[] }[] = [];
  plan.forEach((item, idx) => {
    let bucket = sections.find((s) => s.name === item.section);
    if (!bucket) {
      bucket = { name: item.section, items: [] };
      sections.push(bucket);
    }
    bucket.items.push({ item, idx });
  });

  return (
    <div className="bg-panel border border-border rounded-md overflow-hidden">
      {sections.map((section, si) => (
        <div key={section.name}>
          <div className={`px-3 py-1.5 text-[10.5px] uppercase font-semibold tracking-wide text-muted bg-panelAlt ${si > 0 ? "border-t border-border" : ""}`}>
            {section.name} <span className="text-faint font-normal normal-case tracking-normal">({section.items.length})</span>
          </div>
          {section.items.map(({ item, idx }) => {
            const worstColor = isPositionGroup(item.ref) ? item.ref.worst_color : null;
            const isSelected = idx === selectedIdx;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => onSelect(idx)}
                className={`flex items-center w-full text-left px-3 py-[6px] text-[12.5px] border-t border-border/60 transition-colors ${
                  isSelected ? "bg-panelAlt" : "hover:bg-panelAlt/50"
                }`}
              >
                <span className={`truncate ${isSelected ? "text-ink font-medium" : "text-ink/90"}`}>{item.action}</span>
                {worstColor && (
                  <span className="ml-auto flex items-center text-[11px] text-muted shrink-0 pl-3 tabular-nums">
                    <Dot color={SEVERITY_HEX[worstColor] || SEVERITY_HEX.UNKNOWN} />
                    {worstColor}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}
