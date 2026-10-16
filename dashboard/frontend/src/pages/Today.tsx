import { useState, useEffect, useCallback } from "react";
import type { TodayPlan } from "../types";
import { getTodayPlan, setAccountState } from "../api";
import AccountStateCard from "../components/AccountStateCard";
import DetailPane from "../components/DetailPane";
import ItemList from "../components/ItemList";

export default function TodayPage() {
  const [plan, setPlan] = useState<TodayPlan | null>(null);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await getTodayPlan();
      setPlan(data);
      // Default to the single most urgent item on load, not an empty state.
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

  if (error) {
    return <p className="text-bad text-sm">Failed to load: {error}</p>;
  }

  if (!plan) {
    return <p className="text-gray-500 italic text-center py-8">Loading…</p>;
  }

  return (
    <div>
      <AccountStateCard state={plan.account_state} onSubmit={handleStateUpdate} />

      {plan.context_notes.map((note, i) => (
        <div key={i} className="bg-orange-50 border-l-4 border-warn px-3.5 py-2 text-[13px] text-amber-900 mb-2 rounded-sm">
          {note}
        </div>
      ))}

      <DetailPane item={selectedIdx !== null ? plan.plan[selectedIdx] : null} />

      <ItemList plan={plan.plan} selectedIdx={selectedIdx} onSelect={setSelectedIdx} />
    </div>
  );
}
