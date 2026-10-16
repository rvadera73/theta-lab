import { Fragment, useEffect } from "react";
import type { PlanItem } from "../types";
import { isPositionGroup } from "../types";

const SEVERITY_HEX: Record<string, string> = { RED: "#ff5a5f", YELLOW: "#f7941d", GREEN: "#1ec47c", UNKNOWN: "#5c6578" };

function Dot({ color }: { color: string }) {
  return <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5" style={{ backgroundColor: color }} />;
}

export default function DetailViewer({ item, onClose }: { item: PlanItem | null; onClose: () => void }) {
  useEffect(() => {
    if (!item) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [item, onClose]);

  if (!item) return null;
  const { ref } = item;

  return (
    <div className="fixed inset-0 z-50 flex items-start md:items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div
        className="bg-panel border border-border rounded-lg shadow-xl max-w-2xl w-full max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={item.action}
      >
        <div className="flex items-start justify-between px-5 py-4 border-b border-border">
          <div>
            <div className="text-[10.5px] uppercase font-semibold tracking-wide text-muted mb-0.5">{item.section}</div>
            <div className="text-[15px] font-semibold text-ink">{item.action}</div>
          </div>
          <button onClick={onClose} aria-label="Close" className="text-muted hover:text-ink text-xl leading-none px-1">
            ×
          </button>
        </div>

        <div className="px-5 py-4">
          <p className="text-[13px] text-muted mb-3">{item.why}</p>
          {item.detail && <p className="text-xs text-faint mb-3">{item.detail}</p>}

          {isPositionGroup(ref) ? (
            <>
              <table className="w-full text-xs border-collapse mb-3">
                <thead>
                  <tr className="text-left text-muted uppercase text-[10.5px]">
                    <th className="pr-2 pb-1.5 border-b border-border font-semibold">Color</th>
                    <th className="pr-2 pb-1.5 border-b border-border font-semibold">Leg</th>
                    <th className="pr-2 pb-1.5 border-b border-border font-semibold">Expiry</th>
                    <th className="pr-2 pb-1.5 border-b border-border font-semibold">Action</th>
                    <th className="pr-2 pb-1.5 border-b border-border font-semibold">Coverage</th>
                  </tr>
                </thead>
                <tbody>
                  {ref.legs.map((lg, i) => (
                    <Fragment key={i}>
                      <tr className="border-b border-border/50">
                        <td className="py-1.5 pr-2 text-ink">
                          <Dot color={SEVERITY_HEX[lg.color] || SEVERITY_HEX.UNKNOWN} />
                          {lg.color}
                        </td>
                        <td className="py-1.5 pr-2 tabular-nums text-ink">
                          {lg.type} ${lg.strike}
                        </td>
                        <td className="py-1.5 pr-2 tabular-nums text-muted">
                          {lg.expiry} ({lg.dte}d)
                        </td>
                        <td className="py-1.5 pr-2 text-ink">{lg.action}</td>
                        <td className="py-1.5 pr-2 text-muted">
                          {lg.covered === true
                            ? "covered"
                            : lg.covered === false
                            ? lg.strangle
                              ? "naked (strangle)"
                              : "naked"
                            : lg.type === "PUT"
                            ? "cash-secured"
                            : "-"}
                        </td>
                      </tr>
                      <tr>
                        <td colSpan={5} className="text-faint text-[11px] pb-2.5 pt-0.5">
                          {lg.reason}
                        </td>
                      </tr>
                    </Fragment>
                  ))}
                </tbody>
              </table>
              <div className="text-xs text-muted">
                Sector: {ref.sector || "-"} · Total cost-to-close: {ref.total_cost_to_close != null ? "$" + ref.total_cost_to_close.toLocaleString() : "-"} ·{" "}
                {ref.leg_count} leg(s) total
              </div>
            </>
          ) : (
            <div className="text-xs text-muted space-y-1 tabular-nums">
              <div>
                score={ref.score ?? "-"} (rank {ref.rank ?? "-"}/{ref.population_size ?? "-"})
              </div>
              <div>
                yield={ref.yield_pct ?? "-"}% · conviction={ref.conviction ?? "-"} · iv_rank={ref.iv_rank ?? "-"}
              </div>
              <div>
                real put/call yield={ref.real_put_yield_pct ?? "-"}%/{ref.real_call_yield_pct ?? "-"}% · beta={ref.beta ?? "-"}
              </div>
              <div>sector={ref.sector ?? "-"}</div>
              {ref.gates_fired && ref.gates_fired.length > 0 && (
                <div className="pt-1 text-down">
                  <Dot color="#ff5a5f" />
                  Gates: {ref.gates_fired.join(", ")}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
