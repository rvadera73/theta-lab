import { useState, useEffect, useMemo } from "react";
import type { AccountStatusRow, PnlTrendData, CashMarginForecast, PositionHeatData, PlanItem } from "../types";
import {
  getAccountStatus,
  getPnlTrend,
  getCashMarginForecast,
  getPositionHeat,
  getSectorHeat,
  getRiskMacro,
  getFrameworkStatus,
  getQuarterlyDirection,
} from "../api";
import { groupHeatLegs } from "../utils/groupHeat";
import Collapsible from "../components/Collapsible";
import ReportSection from "../components/ReportSection";
import DetailViewer from "../components/DetailViewer";

const SEVERITY_HEX: Record<string, string> = { RED: "#d03b3b", YELLOW: "#fab219", GREEN: "#0ca30c", UNKNOWN: "#9aa1ad" };
function Dot({ color }: { color: string }) {
  return <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5 shrink-0" style={{ backgroundColor: color }} />;
}

function fmtUsd(n: number | null | undefined): string {
  return n == null ? "—" : "$" + Math.round(n).toLocaleString();
}

function statusBorder(status: string): string {
  if (status.includes("\u{1F534}")) return "border-l-down";
  if (status.includes("\u{1F7E0}")) return "border-l-warn";
  if (status.includes("\u{1F7E2}")) return "border-l-up";
  return "border-l-border";
}

function AccountHealthSection() {
  const [rows, setRows] = useState<AccountStatusRow[] | null>(null);
  const [forecast, setForecast] = useState<CashMarginForecast | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getAccountStatus(), getCashMarginForecast()])
      .then(([acct, cm]) => {
        setRows(acct.data);
        setForecast(cm.data);
      })
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  if (error) return <p className="text-sm text-down">Failed to load: {error}</p>;
  if (!rows) return <p className="text-faint italic text-sm py-4">Loading…</p>;

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 mb-4">
        {rows.map((a) => (
          <div key={a.account} className={`bg-panelAlt border border-border ${statusBorder(a.status)} border-l-[3px] rounded-md p-3`}>
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <span className="text-[12.5px] font-semibold text-ink">{a.account}</span>
              <span className="text-[11px] text-muted whitespace-nowrap">{a.status}</span>
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11.5px] text-muted tabular-nums">
              <div>Balance <span className="text-ink/90 float-right">{fmtUsd(a.balance)}</span></div>
              <div>Opt req <span className="text-ink/90 float-right">{fmtUsd(a.opt_req)}</span></div>
              <div>Utilization <span className="text-ink/90 float-right">{a.utilization.toFixed(0)}%</span></div>
              <div>Positions <span className="text-ink/90 float-right">{a.position_count}</span></div>
              <div>MTD target <span className="text-ink/90 float-right">{fmtUsd(a.target)}</span></div>
              <div>MTD actual <span className="text-ink/90 float-right">{fmtUsd(a.actual)}</span></div>
            </div>
            <div className={`text-[11px] mt-1.5 tabular-nums ${a.gap >= 0 ? "text-up" : "text-down"}`}>
              Gap {a.gap >= 0 ? "+" : ""}{fmtUsd(a.gap)} ({a.pct_gap.toFixed(1)}%)
            </div>
          </div>
        ))}
      </div>

      {forecast && (
        <div className="border-t border-border pt-3">
          <p className="text-[12px] font-semibold text-ink mb-2">Account A margin &amp; crash-scenario forecast</p>
          <div className="flex flex-wrap gap-x-6 gap-y-1.5 text-[12px] text-muted mb-2.5 tabular-nums">
            <span>Stress cash need <strong className="text-ink">{fmtUsd(forecast.stress_low)}–{fmtUsd(forecast.stress_high)}</strong></span>
            <span>Emergency reserve <strong className="text-ink">{fmtUsd(forecast.emergency_reserve)}</strong></span>
            <span className={forecast.reserve_covers_stress ? "text-up" : "text-down"}>
              {forecast.reserve_covers_stress ? "Reserve covers stress scenario" : "Reserve does NOT cover stress scenario"}
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5 mb-2.5">
            {forecast.dte_buckets.map((b) => (
              <span
                key={b.label}
                className={`text-[11px] px-2 py-1 rounded ${
                  b.status === "ok" ? "bg-up/10 text-up" : b.status === "heavy" ? "bg-down/10 text-down" : "bg-warn/15 text-ink/80"
                }`}
              >
                {b.label}: {b.pct.toFixed(1)}% (target {b.target_lo}-{b.target_hi}%)
              </span>
            ))}
          </div>
          <div className="text-[11.5px] text-muted">
            Top expiry concentration:{" "}
            {forecast.top_expiry_dates.slice(0, 3).map((d, i) => (
              <span key={d.date} className={d.status === "edge" ? "text-down" : "text-ink/80"}>
                {i > 0 && ", "}
                {d.date} ({d.pct.toFixed(1)}%)
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function PnlSection() {
  const [data, setData] = useState<PnlTrendData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPnlTrend()
      .then((r) => setData(r.data))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  if (error) return <p className="text-sm text-down">Failed to load: {error}</p>;
  if (!data) return <p className="text-faint italic text-sm py-4">Loading…</p>;

  const entries = Object.entries(data.per_account || {});

  return (
    <div>
      <div className="mb-3">
        <span className="text-[11px] uppercase tracking-wide text-muted">Portfolio QTD realized</span>{" "}
        <span className="text-[16px] font-semibold text-ink tabular-nums">{fmtUsd(data.portfolio_qtd_realized)}</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-[12.5px] border-collapse">
          <thead>
            <tr className="text-left text-muted uppercase text-[10px]">
              <th className="py-1.5 pr-3">Account</th>
              <th className="py-1.5 pr-3 text-right">YTD realized</th>
              <th className="py-1.5 pr-3 text-right">MTD realized</th>
              <th className="py-1.5 pr-3 text-right">Annual target</th>
              <th className="py-1.5 pr-3 text-right">Pace</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([label, row]) => {
              const pace = row.annual_target > 0 ? (row.ytd_realized / row.annual_target) * 100 : null;
              return (
                <tr key={label} className="border-t border-border/60">
                  <td className="py-1.5 pr-3 text-ink/90 whitespace-nowrap">{label}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums text-ink/90">{fmtUsd(row.ytd_realized)}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums text-muted">{fmtUsd(row.mtd_realized)}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums text-muted">{fmtUsd(row.annual_target)}</td>
                  <td className={`py-1.5 pr-3 text-right tabular-nums ${pace != null && pace >= 100 ? "text-up" : "text-muted"}`}>
                    {pace != null ? pace.toFixed(0) + "%" : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const COLOR_ORDER = ["RED", "YELLOW", "GREEN", "UNKNOWN"] as const;

function PositionHeatSection() {
  const [heat, setHeat] = useState<PositionHeatData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState<Record<string, boolean>>({ RED: true, YELLOW: true, GREEN: false, UNKNOWN: false });
  const [viewerItem, setViewerItem] = useState<PlanItem | null>(null);

  useEffect(() => {
    getPositionHeat()
      .then((r) => setHeat(r.data))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  const groups = useMemo(() => {
    if (!heat) return [];
    const legs = COLOR_ORDER.filter((c) => active[c]).flatMap((c) => heat.by_color[c] || []);
    return groupHeatLegs(legs);
  }, [heat, active]);

  if (error) return <p className="text-sm text-down">Failed to load: {error}</p>;
  if (!heat) return <p className="text-faint italic text-sm py-4">Loading…</p>;

  return (
    <div>
      <div className="flex flex-wrap gap-1.5 mb-3">
        {COLOR_ORDER.map((c) => (
          <button
            key={c}
            onClick={() => setActive({ ...active, [c]: !active[c] })}
            className={`text-[11px] px-2.5 py-1 rounded font-medium inline-flex items-center ${
              active[c] ? "bg-panelAlt text-ink border border-border" : "text-faint border border-transparent"
            }`}
          >
            <Dot color={SEVERITY_HEX[c]} />
            {c} ({heat.counts[c] ?? 0})
          </button>
        ))}
        <span className="text-[11px] text-faint self-center ml-1">regime: {heat.regime}</span>
      </div>

      {!groups.length ? (
        <p className="text-faint italic text-sm py-4">No legs in the selected colors.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12.5px] border-collapse">
            <thead>
              <tr className="text-left text-muted uppercase text-[10px]">
                <th className="py-1.5 pr-3">Symbol</th>
                <th className="py-1.5 pr-3">Worst action</th>
                <th className="py-1.5 pr-3">Severity</th>
                <th className="py-1.5 pr-3 text-right">Legs</th>
                <th className="py-1.5 pr-3 text-right">Cost to close</th>
                <th className="py-1.5 pr-3">Account / sector</th>
                <th className="py-1.5 pr-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((g, i) => (
                <tr key={`${g.symbol}-${g.account}-${i}`} className="border-t border-border/60 hover:bg-panelAlt/50">
                  <td className="py-1.5 pr-3 font-medium text-ink whitespace-nowrap">{g.symbol}</td>
                  <td className="py-1.5 pr-3 text-ink/90">{g.worst_action}</td>
                  <td className="py-1.5 pr-3">
                    <span className="inline-flex items-center text-muted">
                      <Dot color={SEVERITY_HEX[g.worst_color] || SEVERITY_HEX.UNKNOWN} />
                      {g.worst_color}
                    </span>
                  </td>
                  <td className="py-1.5 pr-3 text-right tabular-nums text-muted">{g.leg_count}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums text-muted">{fmtUsd(g.total_cost_to_close)}</td>
                  <td className="py-1.5 pr-3 text-faint whitespace-nowrap">{g.account}{g.sector ? ` · ${g.sector}` : ""}</td>
                  <td className="py-1.5 pr-3 text-right">
                    <button
                      onClick={() => setViewerItem({ section: "GATE", action: `${g.symbol} (${g.account})`, why: g.worst_action, ref: g })}
                      className="text-accent text-[12px] font-medium hover:underline"
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <DetailViewer item={viewerItem} onClose={() => setViewerItem(null)} />
    </div>
  );
}

export default function USPage() {
  return (
    <div>
      <Collapsible title="Account Health & Margin" defaultOpen>
        <AccountHealthSection />
      </Collapsible>
      <Collapsible title="P&L vs Target" defaultOpen>
        <PnlSection />
      </Collapsible>
      <Collapsible title="Position Heat (full — all colors)" defaultOpen>
        <PositionHeatSection />
      </Collapsible>
      <Collapsible title="Sector Heat (technical)">
        <ReportSection fetcher={getSectorHeat} />
      </Collapsible>
      <Collapsible title="Risk & Macro">
        <ReportSection fetcher={getRiskMacro} />
      </Collapsible>
      <Collapsible title="Quarterly Portfolio Direction">
        <ReportSection fetcher={() => getQuarterlyDirection("us").then((text) => ({ text }))} />
      </Collapsible>
      <Collapsible title="Framework & automation detail">
        <ReportSection fetcher={getFrameworkStatus} />
      </Collapsible>
    </div>
  );
}
