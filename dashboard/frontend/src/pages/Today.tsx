import { useState, useEffect, useCallback, useMemo } from "react";
import type { TodayPlan } from "../types";
import { getTodayPlan, setAccountState } from "../api";
import AccountStateCard from "../components/AccountStateCard";
import DetailPane from "../components/DetailPane";
import DetailViewer from "../components/DetailViewer";
import ItemList from "../components/ItemList";

const SECTION_SHORT: Record<string, string> = {
  GATE: "gates",
  "CASH RELIEF FIRST": "relief",
  "MANAGE HARD STOPS": "hard stops",
  "NEW ENTRY CANDIDATES": "entries",
};

export default function TodayPage() {
  const [plan, setPlan] = useState<TodayPlan | null>(null);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [viewerIdx, setViewerIdx] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await getTodayPlan();
      setPlan(data);
      setSelectedIdx(data.plan.length ? 0 : null);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleStateUpdate(fields: Record<string, number>) {
    try {
      const data = await setAccountState({ account: "A", ...fields });
      setPlan(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  const sectionCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const item of plan?.plan || []) counts[item.section] = (counts[item.section] || 0) + 1;
    return counts;
  }, [plan]);

  if (error) {
    return <p className="text-sm text-down">Failed to load: {error}</p>;
  }

  if (!plan) {
    return <p className="text-faint italic text-center py-8 text-sm">Loading…</p>;
  }

  return (
    <div>
      <AccountStateCard state={plan.account_state} onSubmit={handleStateUpdate} />

      {plan.context_notes.map((note, i) => (
        <div key={i} className="bg-accent/10 border-l-2 border-accent px-3 py-1.5 text-[12.5px] text-ink/90 mb-2 rounded-sm">
          {note}
        </div>
      ))}

      {/* Plain, un-colored stat line -- category counts are not a
          direction/severity signal, so (per the Robinhood Legend
          reference) they don't get color, just numbers. */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-[12.5px] text-muted mb-3 tabular-nums">
        {Object.entries(sectionCounts).map(([section, n]) => (
          <span key={section}>
            <strong className="text-ink font-semibold mr-1">{n}</strong>
            {SECTION_SHORT[section]}
          </span>
        ))}
      </div>

      <DetailPane item={selectedIdx !== null ? plan.plan[selectedIdx] : null} onViewFull={() => setViewerIdx(selectedIdx)} />

      <ItemList plan={plan.plan} selectedIdx={selectedIdx} onSelect={setSelectedIdx} />

      <DetailViewer item={viewerIdx !== null ? plan.plan[viewerIdx] : null} onClose={() => setViewerIdx(null)} />
    </div>
  );
}
