import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

const SECTION_BORDER: Record<string, string> = {
  GATE: "border-l-bad",
  "CASH RELIEF FIRST": "border-l-warn",
  "MANAGE HARD STOPS": "border-l-muted",
  "NEW ENTRY CANDIDATES": "border-l-good",
};

const COLOR_TAG: Record<string, string> = {
  RED: "bg-red-100 text-bad",
  YELLOW: "bg-yellow-100 text-amber-800",
  GREEN: "bg-green-100 text-good",
  UNKNOWN: "bg-gray-100 text-muted",
};

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
          <div className="text-xs uppercase font-bold tracking-wide text-muted mt-4 mb-1.5">
            {section.name} <span className="text-gray-400 font-normal normal-case tracking-normal">({section.items.length})</span>
          </div>
          {section.items.map(({ item, idx }) => {
            const worstColor = isPositionGroup(item.ref) ? item.ref.worst_color : null;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => onSelect(idx)}
                className={`flex items-center gap-2.5 w-full text-left bg-white rounded px-3.5 py-2 mb-1 border-l-[3px] text-[13.5px] ${
                  SECTION_BORDER[item.section] || "border-l-gray-300"
                } ${idx === selectedIdx ? "bg-blue-50 font-semibold" : "hover:bg-[#f4f8fc]"}`}
              >
                <span>{item.action}</span>
                {worstColor && (
                  <span className={`ml-auto inline-block px-2 py-0.5 rounded-full text-[10px] font-bold ${COLOR_TAG[worstColor] || "bg-gray-100"}`}>
                    {worstColor}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      ))}
    </>
  );
}
