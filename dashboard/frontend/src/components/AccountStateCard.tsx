import { useState, useEffect, FormEvent } from "react";
import type { AccountState } from "../types";

function fmtUsd(v: number | null): string {
  return v == null ? "—" : "$" + v.toLocaleString();
}

export default function AccountStateCard({
  state,
  onSubmit,
}: {
  state: AccountState | null;
  onSubmit: (fields: Record<string, number>) => void;
}) {
  const [form, setForm] = useState({ cash: "", cash_plus_borrowing: "", option_requirement: "", equity_pct: "" });

  useEffect(() => {
    if (state) {
      setForm({
        cash: state.cash?.toString() ?? "",
        cash_plus_borrowing: state.cash_plus_borrowing?.toString() ?? "",
        option_requirement: state.option_requirement?.toString() ?? "",
        equity_pct: state.equity_pct?.toString() ?? "",
      });
    }
  }, [state]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const fields: Record<string, number> = {};
    for (const [k, v] of Object.entries(form)) {
      if (v !== "") fields[k] = parseFloat(v);
    }
    onSubmit(fields);
  }

  const stats = [
    { label: "Cash", value: fmtUsd(state?.cash ?? null) },
    { label: "Cash + borrowing", value: fmtUsd(state?.cash_plus_borrowing ?? null) },
    { label: "Option requirement", value: fmtUsd(state?.option_requirement ?? null) },
    { label: "Equity %", value: state?.equity_pct == null ? "—" : `${state.equity_pct}%` },
  ];

  return (
    <section className="bg-white rounded-lg shadow-sm p-5 md:px-6 mb-4">
      {!state && <p className="text-sm text-faint mb-2">No account state on file yet — enter it below.</p>}
      <div className="flex flex-wrap gap-8 mb-4">
        {stats.map((s) => (
          <div key={s.label}>
            <div className="text-[11px] uppercase tracking-wide text-muted mb-0.5">{s.label}</div>
            <div className="text-2xl font-bold text-ink tracking-tight tabular-nums">{s.value}</div>
          </div>
        ))}
        {state && state.days_stale > 0 && (
          <span
            className="inline-flex items-center self-start gap-1 rounded-full text-[10px] font-bold px-2 py-0.5"
            style={{ backgroundColor: "#d03b3b1a", color: "#d03b3b" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#d03b3b]" />
            {state.days_stale}d old
          </span>
        )}
      </div>
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-2 items-end">
        {(["cash", "cash_plus_borrowing", "option_requirement", "equity_pct"] as const).map((key) => (
          <div key={key} className="flex flex-col gap-0.5">
            <label htmlFor={`f-${key}`} className="text-[10.5px] text-muted">
              {key.replace(/_/g, " ")}
            </label>
            <input
              id={`f-${key}`}
              type="number"
              step="0.01"
              value={form[key]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              className="text-[12.5px] px-2 py-1 border border-gray-300 rounded w-[105px]"
            />
          </div>
        ))}
        <button type="submit" className="text-[12.5px] px-3.5 py-1.5 rounded bg-accent text-white">
          Update
        </button>
      </form>
    </section>
  );
}
