import type { PlanItem } from "../types";

// Validated status palette (dataviz skill, references/palette.md) -- used
// exactly as specified, not approximated. These are reserved status colors
// (good/warning/serious/critical), never themed, never reused as a generic
// series color.
const STATUS = {
  critical: "#d03b3b",
  warning: "#fab219",
  serious: "#ec835a",
  good: "#0ca30c",
};

const SECTION_COLOR: Record<string, string> = {
  GATE: STATUS.critical,
  "CASH RELIEF FIRST": STATUS.warning,
  "MANAGE HARD STOPS": STATUS.serious,
  "NEW ENTRY CANDIDATES": STATUS.good,
};

const SECTION_LABEL: Record<string, string> = {
  GATE: "Gates fired",
  "CASH RELIEF FIRST": "Cash relief",
  "MANAGE HARD STOPS": "Hard stops",
  "NEW ENTRY CANDIDATES": "New entries",
};

const ORDER = ["GATE", "CASH RELIEF FIRST", "MANAGE HARD STOPS", "NEW ENTRY CANDIDATES"];

// Plain SVG horizontal bar chart, built directly per the dataviz skill's
// component philosophy (no chart library for a chart this simple). Each bar
// is directly labeled with its own category + count, so no legend box is
// needed (a bar chart's own axis labels already carry identity) -- status
// colors always ship with their text label alongside, per the skill's rule
// that a status color never carries meaning by hue alone.
export default function SectionChart({ plan }: { plan: PlanItem[] }) {
  const counts: Record<string, number> = {};
  for (const item of plan) counts[item.section] = (counts[item.section] || 0) + 1;

  const rows = ORDER.filter((s) => counts[s] > 0).map((s) => ({
    section: s,
    label: SECTION_LABEL[s],
    count: counts[s],
    color: SECTION_COLOR[s],
  }));
  if (!rows.length) return null;

  const max = Math.max(...rows.map((r) => r.count));
  const barHeight = 22;
  const gap = 14;
  const leftColW = 118;
  const chartW = 360;
  const height = rows.length * (barHeight + gap);

  return (
    <div className="bg-white rounded-lg shadow-sm p-5 mb-4">
      <div className="text-[13px] font-semibold text-ink mb-3">Today's action breakdown</div>
      <svg width="100%" viewBox={`0 0 ${leftColW + chartW + 50} ${height}`} role="img" aria-label="Count of today's actions by category">
        {rows.map((r, i) => {
          const y = i * (barHeight + gap);
          const w = Math.max(4, (r.count / max) * chartW);
          return (
            <g key={r.section}>
              <text x={0} y={y + barHeight / 2 + 4} fontSize="12.5" fill="#52514e">
                {r.label}
              </text>
              <rect x={leftColW} y={y} width={chartW} height={barHeight} rx={4} fill="#e1e0d9" />
              <rect x={leftColW} y={y} width={w} height={barHeight} rx={4} fill={r.color} />
              <text x={leftColW + w + 8} y={y + barHeight / 2 + 4} fontSize="13" fontWeight={700} fill="#0b0b0b">
                {r.count}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
