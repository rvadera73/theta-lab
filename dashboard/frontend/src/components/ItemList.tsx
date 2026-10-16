import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

// Validated status palette (dataviz skill, references/palette.md) -- same
// exact values as DetailPane/SectionChart, applied consistently across the
// whole app rather than three slightly-different ad-hoc color sets.
const STATUS = { critical: "#d03b3b", warning: "#fab219", serious: "#ec835a", good: "#0ca30c", muted: "#898781" };
const COLOR_HEX: Record<string, string> = { RED: STATUS.critical, YELLOW: STATUS.warning, GREEN: STATUS.good, UNKNOWN: STATUS.muted };
const SECTION_HEX: Record<string, string> = {
  GATE: STATUS.critical,
  "CASH RELIEF FIRST": STATUS.warning,
  "MANAGE HARD STOPS": STATUS.serious,
  "NEW ENTRY CANDIDATES": STATUS.good,
};

function ColorTag({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <span className="ml-auto inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ backgroundColor: `${color}1a`, color }}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
      {children}
    </span>
  );
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
    return <p className="text-gray-500 italic text-center py-8">Nothing actionable right now.</p>;
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
    <>
      {sections.map((section) => (
        <div key={section.name}>
          <div className="text-xs uppercase font-bold tracking-wide text-muted mt-5 mb-2">
            {section.name} <span className="text-gray-400 font-normal normal-case tracking-normal">({section.items.length})</span>
          </div>
          {section.items.map(({ item, idx }) => {
            const worstColor = isPositionGroup(item.ref) ? item.ref.worst_color : null;
            const isSelected = idx === selectedIdx;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => onSelect(idx)}
                className={`flex items-center gap-2.5 w-full text-left bg-white rounded-md px-3.5 py-2.5 mb-1.5 border-l-[3px] text-[13.5px] shadow-sm transition-colors ${
                  isSelected ? "bg-blue-50 font-semibold" : "hover:bg-[#f9f9f7]"
                }`}
                style={{ borderLeftColor: SECTION_HEX[item.section] || "#c3c2b7" }}
              >
                <span>{item.action}</span>
                {worstColor && <ColorTag color={COLOR_HEX[worstColor] || STATUS.muted}>{worstColor}</ColorTag>}
              </button>
            );
          })}
        </div>
      ))}
    </>
  );
}
