import { Fragment } from "react";
import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

// Validated status palette (dataviz skill, references/palette.md) -- exact
// hex, not approximated by a Tailwind preset. A status color always ships
// with its text label beside it (never hue alone), per the skill's rule.
const STATUS = { critical: "#d03b3b", warning: "#fab219", serious: "#ec835a", good: "#0ca30c", muted: "#898781" };
const COLOR_HEX: Record<string, string> = { RED: STATUS.critical, YELLOW: STATUS.warning, GREEN: STATUS.good, UNKNOWN: STATUS.muted };
const SECTION_HEX: Record<string, string> = {
  GATE: STATUS.critical,
  "CASH RELIEF FIRST": STATUS.warning,
  "MANAGE HARD STOPS": STATUS.serious,
  "NEW ENTRY CANDIDATES": STATUS.good,
};

function fmtUsd(v: number | null | undefined): string {
  return v == null ? "—" : "$" + v.toLocaleString();
}

function Tag({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
      style={{ backgroundColor: `${color}1a`, color }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
      {children}
    </span>
  );
}

export default function DetailPane({ item }: { item: PlanItem | null }) {
  if (!item) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-5 mb-4 border-t-4 border-t-gray-300 min-h-[110px] flex items-center">
        <p className="text-gray-400 italic text-sm">Select an item below to see its full detail here.</p>
      </div>
    );
  }

  const { ref } = item;

  return (
    <div className="bg-white rounded-lg shadow-sm p-5 md:p-6 mb-4 border-t-4" style={{ borderTopColor: SECTION_HEX[item.section] || "#c3c2b7" }}>
      <div className="text-[11px] uppercase font-bold tracking-wide text-muted mb-1.5">{item.section}</div>
      <div className="text-xl font-bold text-ink mb-2 tracking-tight">{item.action}</div>
      <p className="text-sm text-[#3d4551] mb-2">{item.why}</p>
      {item.detail && <p className="text-[12.5px] text-faint mb-2.5">{item.detail}</p>}

      {isPositionGroup(ref) ? (
        <>
          <table className="w-full text-[12.5px] border-collapse mb-2">
            <thead>
              <tr className="text-left text-muted text-[11px] uppercase">
                <th className="pr-2 pb-1 border-b border-border font-semibold">Color</th>
                <th className="pr-2 pb-1 border-b border-border font-semibold">Leg</th>
                <th className="pr-2 pb-1 border-b border-border font-semibold">Expiry</th>
                <th className="pr-2 pb-1 border-b border-border font-semibold">Action</th>
                <th className="pr-2 pb-1 border-b border-border font-semibold">Coverage</th>
              </tr>
            </thead>
            <tbody>
              {ref.legs.map((lg, i) => (
                <Fragment key={i}>
                  <tr>
                    <td className="py-1 pr-2">
                      <Tag color={COLOR_HEX[lg.color] || STATUS.muted}>{lg.color}</Tag>
                    </td>
                    <td className="py-1 pr-2">
                      {lg.type} ${lg.strike}
                    </td>
                    <td className="py-1 pr-2">
                      {lg.expiry} ({lg.dte}d)
                    </td>
                    <td className="py-1 pr-2">{lg.action}</td>
                    <td className="py-1 pr-2">
                      {lg.covered === true
                        ? "covered"
                        : lg.covered === false
                        ? lg.strangle
                          ? "naked (strangle-paired)"
                          : "naked"
                        : lg.type === "PUT"
                        ? "cash-secured"
                        : "-"}
                    </td>
                  </tr>
                  <tr>
                    <td colSpan={5} className="text-faint text-xs pb-2">
                      {lg.reason}
                    </td>
                  </tr>
                </Fragment>
              ))}
            </tbody>
          </table>
          <div className="text-[12.5px] text-[#3d4551]">
            Sector: {ref.sector || "-"} · Total cost-to-close: {fmtUsd(ref.total_cost_to_close)} · {ref.leg_count} leg(s) total
          </div>
        </>
      ) : (
        <div className="text-[12.5px] text-[#3d4551]">
          score={ref.score ?? "-"} (rank {ref.rank ?? "-"}/{ref.population_size ?? "-"}) · yield={ref.yield_pct ?? "-"}% · conviction=
          {ref.conviction ?? "-"} · iv_rank={ref.iv_rank ?? "-"} · real put/call yield={ref.real_put_yield_pct ?? "-"}%/
          {ref.real_call_yield_pct ?? "-"}% · beta={ref.beta ?? "-"} · sector={ref.sector ?? "-"}
          {ref.gates_fired && ref.gates_fired.length > 0 && (
            <div className="mt-1">
              <Tag color={STATUS.critical}>Gates: {ref.gates_fired.join(", ")}</Tag>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
