import type { TodayPlan, AccountState } from "./types";

// Relative paths deliberately -- same real lesson as today.html's
// 2026-10-15 bug: this app can be served behind an unknown path prefix, and
// an absolute "/api/..." path would bypass that prefix and hit the wrong
// thing. BUT this app is served from /app/ (a real subdirectory -- see
// main.py's trailing-slash redirect, needed so its OWN relative asset
// paths resolve as children of /app/), one level deeper than the other
// pages (today.html etc. are flat files directly under the gateway
// prefix). The API lives at the theta-lab root, a SIBLING of /app, not a
// child of it -- "../" accounts for exactly that one level of nesting
// this app's own mount point introduces. Confirmed real bug 2026-10-16:
// a same-level relative path ("api/us") resolved to /app/api/us/... (a
// genuine 404) instead of the real .../api/us/... one level up.
const BASE = "../api/us";

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
