import type { TodayPlan, AccountState } from "./types";

// Relative paths (no leading slash) deliberately -- same real lesson as
// today.html's 2026-10-15 bug: this app can be served behind an unknown
// path prefix, and an absolute "/api/..." path would bypass that prefix
// and hit the wrong thing. A relative path resolves against wherever this
// app's own index.html is served from, matching the sibling "api/" path
// the FastAPI backend already serves everything else from.
const BASE = "api/us";

export async function getTodayPlan(): Promise<TodayPlan> {
  const r = await fetch(`${BASE}/today`);
  if (!r.ok) throw new Error(`GET ${BASE}/today failed: ${r.status}`);
  return r.json();
}

export async function getAccountState(account = "A"): Promise<AccountState | null> {
  const r = await fetch(`${BASE}/account-state?account=${account}`);
  if (!r.ok) throw new Error(`GET account-state failed: ${r.status}`);
  return r.json();
}

export async function setAccountState(body: Partial<AccountState> & { account: string }): Promise<TodayPlan> {
  const r = await fetch(`${BASE}/account-state`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`POST account-state failed: ${r.status}`);
  return r.json();
}
