import { useState, useEffect, useCallback, useMemo, FormEvent } from "react";
import type { CompositeScoresData, CompositeScoreRow, WatchlistRow } from "../types";
import { getCompositeScores, getWatchlist, addWatchlistSymbol, setWatchlistTracked } from "../api";
import Collapsible from "../components/Collapsible";

function fmtPct(n: number | null | undefined): string {
  return n == null ? "—" : n.toFixed(1) + "%";
}
function fmtNum(n: number | null | undefined): string {
  return n == null ? "—" : n.toFixed(2);
}
function fmtUsd(n: number | null | undefined): string {
  return n == null ? "—" : "$" + Math.round(n).toLocaleString();
}

const HEAT_COLOR: Record<string, string> = { RED: "#d03b3b", YELLOW: "#fab219", GREEN: "#0ca30c" };

type SortKey = "rank" | "score" | "yield_pct" | "conviction" | "target_upside_pct" | "invested" | "beta";
const DESC_FIRST = new Set<SortKey>(["score", "yield_pct", "conviction", "invested", "target_upside_pct"]);

function Tag({ children, variant = "default" }: { children: string; variant?: "default" | "gate" | "flag" | "new" }) {
  const styles: Record<string, string> = {
    default: "bg-panelAlt text-muted",
    gate: "bg-down/10 text-down",
    flag: "bg-warn/15 text-ink/80",
    new: "bg-accent/10 text-accent",
  };
  return <span className={`inline-block text-[10px] font-medium px-1.5 py-0.5 rounded mr-1 mb-1 ${styles[variant]}`}>{children}</span>;
}

// Real fix (2026-10-16, trader decision): Watchlist (list management) and
// Scores (the ranked analysis of that same list) merged into one tab -- the
// trader asked "do we need two tabs for one dataset." List add/remove is
// now an inline header action here instead of a separate page; the ranked
// table (plus tail-risk/realized-performance/laggards context) is the main
// view.
export default function WatchlistPage() {
  const [scores, setScores] = useState<CompositeScoresData | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistRow[]>([]);
  const [asOf, setAsOf] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "held" | "watchlist">("all");
  const [sortKey, setSortKey] = useState<SortKey>("rank");
  const [sortAsc, setSortAsc] = useState(true);
  const [newSymbol, setNewSymbol] = useState("");
  const [newNotes, setNewNotes] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [cs, wl] = await Promise.all([getCompositeScores(), getWatchlist()]);
      setScores(cs.data);
      setAsOf(cs.as_of);
      setWatchlist(wl);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleAdd(e: FormEvent) {
    e.preventDefault();
    if (!newSymbol.trim()) return;
    setBusy(true);
    try {
      await addWatchlistSymbol(newSymbol.trim().toUpperCase(), newNotes.trim());
      setNewSymbol("");
      setNewNotes("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(symbol: string) {
    setBusy(true);
    try {
      await setWatchlistTracked(symbol, false);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(!DESC_FIRST.has(key));
    }
  }

  const { tailRisk, rows, errors } = useMemo(() => {
    if (!scores) return { tailRisk: [] as CompositeScoreRow[], rows: [] as CompositeScoreRow[], errors: [] as CompositeScoreRow[] };
    const held = scores.held || [];
    const watch = scores.watchlist || [];
    const tailRisk = [...held, ...watch].filter((r) => r.tail_risk);
    const errors = watch.filter((r) => r.tail_risk == null && r.error);
    let combined = [...held.filter((r) => !r.tail_risk), ...watch.filter((r) => !r.tail_risk && r.score != null)];
    if (filter === "held") combined = combined.filter((r) => !r.is_new);
    if (filter === "watchlist") combined = combined.filter((r) => r.is_new);

    const getVal = (r: CompositeScoreRow): number | string => {
      switch (sortKey) {
        case "rank": return r.rank ?? 999;
        case "score": return r.score ?? -999;
        case "yield_pct": return r.yield_pct ?? -999;
        case "conviction": return r.conviction ?? -999;
        case "target_upside_pct": return r.target_upside_pct ?? -999;
        case "invested": return r.invested ?? -1;
        case "beta": return r.beta ?? -999;
      }
    };
    combined.sort((a, b) => {
      const av = getVal(a), bv = getVal(b);
      const cmp = typeof av === "number" && typeof bv === "number" ? av - bv : String(av).localeCompare(String(bv));
      return sortAsc ? cmp : -cmp;
    });
    return { tailRisk, rows: combined, errors };
  }, [scores, filter, sortKey, sortAsc]);

  if (error) return <p className="text-sm text-down">Failed to load: {error}</p>;
  if (!scores) return <p className="text-faint italic text-center py-8 text-sm">Loading…</p>;

  const popSize = rows[0]?.population_size ?? scores.held.length;
  const isTracked = (symbol: string) => watchlist.find((w) => w.symbol === symbol);

  function SortTh({ sortKey: k, label, right }: { sortKey: SortKey; label: string; right?: boolean }) {
    const active = sortKey === k;
    return (
      <th
        onClick={() => toggleSort(k)}
        className={`px-2.5 py-2 font-semibold cursor-pointer select-none hover:text-ink ${right ? "text-right" : "text-left"} ${active ? "text-ink" : ""}`}
      >
        {label} {active ? (sortAsc ? "▴" : "▾") : ""}
      </th>
    );
  }

  return (
    <div>
      {/* Header: context strip + inline add-symbol form */}
      <section className="bg-panel border border-border rounded-md p-4 mb-3 flex flex-wrap items-end justify-between gap-4">
        <div className="flex flex-wrap gap-6">
          <div>
            <div className="text-[10.5px] uppercase tracking-wide text-muted mb-0.5">Regime</div>
            <div className="text-[14px] font-semibold text-ink">{scores.regime || "—"}</div>
          </div>
          <div>
            <div className="text-[10.5px] uppercase tracking-wide text-muted mb-0.5">
              Macro stage (severity {fmtNum(scores.severity_smoothed)})
            </div>
            <div className="text-[14px] font-semibold text-ink">{scores.macro_stage || "—"}</div>
          </div>
          <div>
            <div className="text-[10.5px] uppercase tracking-wide text-muted mb-0.5">
              Crash-sensitive sectors ({scores.sensitivity_confidence} confidence)
            </div>
            <div className="text-[13px] text-ink/90">{(scores.high_exposure_sectors || []).join(", ") || "none"}</div>
          </div>
          <div className="text-[11px] text-faint self-end">as of {asOf}</div>
        </div>
        <form onSubmit={handleAdd} className="flex gap-2 items-end">
          <div className="flex flex-col gap-0.5">
            <label htmlFor="new-symbol" className="text-[10px] text-faint">symbol</label>
            <input
              id="new-symbol"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              placeholder="e.g. COST"
              className="text-[12.5px] px-2 py-1 bg-panelAlt border border-border rounded text-ink w-[90px] focus:outline-none focus:border-accent"
            />
          </div>
          <div className="flex flex-col gap-0.5">
            <label htmlFor="new-notes" className="text-[10px] text-faint">notes (optional)</label>
            <input
              id="new-notes"
              value={newNotes}
              onChange={(e) => setNewNotes(e.target.value)}
              placeholder="why this candidate"
              className="text-[12.5px] px-2 py-1 bg-panelAlt border border-border rounded text-ink w-[220px] focus:outline-none focus:border-accent"
            />
          </div>
          <button disabled={busy} type="submit" className="text-[12.5px] px-3.5 py-1.5 rounded bg-accent text-surface font-medium disabled:opacity-50">
            Add to watchlist
          </button>
        </form>
      </section>

      {errors.length > 0 && (
        <div className="bg-warn/10 border-l-2 border-warn px-3 py-1.5 text-[12.5px] text-ink/90 mb-3 rounded-sm">
          Could not score: {errors.map((e) => `${e.ticker} (${e.error})`).join(", ")}
        </div>
      )}

      {tailRisk.length > 0 && (
        <Collapsible title="⚠ Tail-risk disqualified — not scored below, needs a real decision" defaultOpen badge={<Tag variant="gate">{String(tailRisk.length)}</Tag>}>
          <table className="w-full text-[12.5px] border-collapse mt-2">
            <thead>
              <tr className="text-left text-muted uppercase text-[10px]">
                <th className="py-1.5 pr-2">Ticker</th>
                <th className="py-1.5 pr-2">Flags</th>
                <th className="py-1.5 pr-2 text-right">Yield</th>
                <th className="py-1.5 pr-2 text-right">Conviction</th>
                <th className="py-1.5 pr-2 text-right">Invested</th>
              </tr>
            </thead>
            <tbody>
              {tailRisk.map((r) => (
                <tr key={r.ticker} className="border-t border-border/60">
                  <td className="py-1.5 pr-2 font-medium text-ink">
                    {r.ticker} {r.is_new && <Tag variant="new">watchlist</Tag>}
                  </td>
                  <td className="py-1.5 pr-2">{(r.flags || []).map((f) => <Tag key={f} variant="flag">{f}</Tag>)}</td>
                  <td className="py-1.5 pr-2 text-right tabular-nums">{fmtPct(r.yield_pct)}</td>
                  <td className="py-1.5 pr-2 text-right tabular-nums">{fmtNum(r.conviction)}</td>
                  <td className="py-1.5 pr-2 text-right tabular-nums">{r.is_new ? "—" : fmtUsd(r.invested)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Collapsible>
      )}

      {scores.realized_top_performers_90d?.length > 0 && (
        <Collapsible title="Real performance — top 15 by realized P&L, trailing 90 days" badge={<span className="text-[11px] text-faint">as of {scores.realized_cutoff}</span>}>
          <p className="text-[12px] text-muted mt-2 mb-2">
            Real, FIFO-matched closed-trade P&L vs. each name's current forward-looking score — never blended into the composite ranking.
          </p>
          <RealizedTable rows={scores.realized_top_performers_90d} popSize={popSize} />
        </Collapsible>
      )}

      {(scores.realized_losses_90d?.length > 0 || scores.realized_no_activity_90d?.length > 0) && (
        <Collapsible title="Laggards — real losses and zero-activity names, trailing 90 days">
          <p className="text-[12px] text-muted mt-2 mb-2">
            Realized losses (an actual closed trade that lost money), and separately, held names with zero realized closes yet.
          </p>
          {scores.realized_losses_90d?.length > 0 && (
            <>
              <p className="text-[12px] font-semibold text-ink mt-2 mb-1">Real losses ({scores.realized_losses_90d.length})</p>
              <RealizedTable rows={scores.realized_losses_90d} popSize={popSize} loss />
            </>
          )}
          {scores.realized_no_activity_90d?.length > 0 && (
            <>
              <p className="text-[12px] font-semibold text-ink mt-3 mb-1">
                Zero realized activity ({scores.realized_no_activity_90d.length} of {popSize} held)
              </p>
              <RealizedTable rows={scores.realized_no_activity_90d} popSize={popSize} />
            </>
          )}
        </Collapsible>
      )}

      {/* Main ranked table */}
      <div className="flex gap-1 mb-2">
        {(["all", "held", "watchlist"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`text-[12px] px-3 py-1 rounded font-medium capitalize ${filter === f ? "bg-accent text-surface" : "bg-panelAlt text-muted hover:text-ink"}`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="bg-panel border border-border rounded-md overflow-hidden overflow-x-auto">
        <table className="w-full text-[12.5px] border-collapse">
          <thead>
            <tr className="text-left text-muted uppercase text-[10px] bg-panelAlt">
              <SortTh sortKey="rank" label="Rank" />
              <th className="px-2.5 py-2 font-semibold">Ticker</th>
              <SortTh sortKey="score" label="Score" right />
              <SortTh sortKey="yield_pct" label="Yield (rank)" right />
              <th className="px-2.5 py-2 font-semibold text-right">Real P/C</th>
              <SortTh sortKey="beta" label="Beta" right />
              <SortTh sortKey="conviction" label="Conviction (rank)" right />
              <SortTh sortKey="target_upside_pct" label="Analyst upside" right />
              <SortTh sortKey="invested" label="Invested" right />
              <th className="px-2.5 py-2 font-semibold">Heat</th>
              <th className="px-2.5 py-2 font-semibold">Verticals</th>
              <th className="px-2.5 py-2 font-semibold">Gates &amp; flags</th>
              <th className="px-2.5 py-2 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.ticker} className="border-t border-border/60 hover:bg-panelAlt/50 transition-colors">
                <td className="px-2.5 py-[7px] text-faint tabular-nums whitespace-nowrap">
                  #{r.rank}{r.population_size ? ` / ${r.population_size}` : ""}
                </td>
                <td className="px-2.5 py-[7px] font-medium text-ink whitespace-nowrap">
                  {r.ticker} {r.is_new && <Tag variant="new">watchlist</Tag>}
                </td>
                <td className="px-2.5 py-[7px] text-right tabular-nums font-medium text-ink">{fmtNum(r.score)}</td>
                <td className="px-2.5 py-[7px] text-right tabular-nums text-muted">
                  {fmtPct(r.yield_pct)} <span className="text-faint">(#{r.yield_rank ?? "—"})</span>
                </td>
                <td className="px-2.5 py-[7px] text-right tabular-nums text-muted" title="Real live option-chain premium">
                  {r.real_put_yield_pct != null || r.real_call_yield_pct != null
                    ? `P ${fmtPct(r.real_put_yield_pct)} / C ${fmtPct(r.real_call_yield_pct)}`
                    : "—"}
                </td>
                <td className="px-2.5 py-[7px] text-right tabular-nums text-muted">{r.beta != null ? r.beta.toFixed(2) : "—"}</td>
                <td className="px-2.5 py-[7px] text-right tabular-nums text-muted">
                  {fmtNum(r.conviction)} <span className="text-faint">(#{r.conviction_rank ?? "—"})</span>
                </td>
                <td className="px-2.5 py-[7px] text-right tabular-nums text-muted">
                  {r.target_upside_pct != null ? r.target_upside_pct.toFixed(0) + "%" : "—"}
                  {r.valuation_penalty ? " ⚠" : ""}
                </td>
                <td className="px-2.5 py-[7px] text-right tabular-nums text-muted">{r.is_new ? "—" : fmtUsd(r.invested)}</td>
                <td className="px-2.5 py-[7px]">
                  {r.heat ? (
                    <span className="inline-flex items-center text-muted">
                      <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5" style={{ backgroundColor: HEAT_COLOR[r.heat] || "#9aa1ad" }} />
                      {r.heat}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="px-2.5 py-[7px]">{(r.verticals || []).map((v) => <Tag key={v}>{v}</Tag>) || "—"}</td>
                <td className="px-2.5 py-[7px]">
                  {(r.gates_fired || []).map((g) => <Tag key={g} variant="gate">{g}</Tag>)}
                  {(r.flags || []).map((f) => <Tag key={f} variant="flag">{f}</Tag>)}
                </td>
                <td className="px-2.5 py-[7px] text-right">
                  {isTracked(r.ticker) && (
                    <button
                      disabled={busy}
                      onClick={() => handleRemove(r.ticker)}
                      className="text-down text-[11px] font-medium hover:underline disabled:opacity-50"
                    >
                      Remove
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RealizedTable({ rows, popSize, loss }: { rows: import("../types").RealizedRow[]; popSize: number; loss?: boolean }) {
  return (
    <table className="w-full text-[12.5px] border-collapse">
      <thead>
        <tr className="text-left text-muted uppercase text-[10px]">
          <th className="py-1.5 pr-2">Ticker</th>
          <th className="py-1.5 pr-2 text-right">Realized P&amp;L (90d)</th>
          <th className="py-1.5 pr-2 text-right">Closes</th>
          <th className="py-1.5 pr-2 text-right">Composite rank now</th>
          <th className="py-1.5 pr-2 text-right">Conviction</th>
          <th className="py-1.5 pr-2 text-right">Yield</th>
          <th className="py-1.5 pr-2">Flags</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => {
          const rankText = r.tail_risk ? "disqualified" : r.composite_rank ? `#${r.composite_rank}/${popSize}` : "unranked";
          return (
            <tr key={r.ticker} className="border-t border-border/60">
              <td className="py-1.5 pr-2 font-medium text-ink">{r.ticker}</td>
              <td className={`py-1.5 pr-2 text-right tabular-nums ${loss ? "text-down" : "text-up"}`}>
                {loss ? "$" + r.realized_pnl_90d.toLocaleString(undefined, { maximumFractionDigits: 0 }) : "no closes"}
              </td>
              <td className="py-1.5 pr-2 text-right tabular-nums text-muted">{loss ? r.closed_count_90d : "—"}</td>
              <td className="py-1.5 pr-2 text-right tabular-nums text-muted">{rankText}</td>
              <td className="py-1.5 pr-2 text-right tabular-nums text-muted">
                {fmtNum(r.conviction)}{r.conviction_rank ? ` (#${r.conviction_rank})` : ""}
              </td>
              <td className="py-1.5 pr-2 text-right tabular-nums text-muted">
                {fmtPct(r.yield_pct)}{r.yield_rank ? ` (#${r.yield_rank})` : ""}
              </td>
              <td className="py-1.5 pr-2">{(r.flags || []).map((f) => <Tag key={f} variant="flag">{f}</Tag>) || "—"}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
