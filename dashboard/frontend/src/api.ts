import type {
  TodayPlan,
  AccountState,
  CompositeScoresData,
  WatchlistRow,
  AccountStatusRow,
  PnlTrendData,
  CashMarginForecast,
  PositionHeatData,
} from "./types";

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
const API_ROOT = "../api";
const BASE = `${API_ROOT}/us`;
const INDIA_BASE = `${API_ROOT}/india`;

async function getJson<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`GET ${url} failed: ${r.status}`);
  return r.json();
}

async function getText(url: string): Promise<string> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`GET ${url} failed: ${r.status}`);
  return r.text();
}

export async function getTodayPlan(): Promise<TodayPlan> {
  return getJson(`${BASE}/today`);
}

export async function getAccountState(account = "A"): Promise<AccountState | null> {
  return getJson(`${BASE}/account-state?account=${account}`);
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

// ---- US tab ---------------------------------------------------------------

export async function getAccountStatus(): Promise<{ data: AccountStatusRow[]; as_of: string }> {
  return getJson(`${BASE}/account-status`);
}

export async function getPnlTrend(): Promise<{ data: PnlTrendData; as_of: string }> {
  return getJson(`${BASE}/pnl-trend`);
}

export async function getCashMarginForecast(): Promise<{ data: CashMarginForecast; as_of: string }> {
  return getJson(`${BASE}/cash-margin-forecast`);
}

export async function getPositionHeat(): Promise<{ data: PositionHeatData; as_of: string }> {
  return getJson(`${BASE}/position-heat`);
}

export async function getSectorHeat(): Promise<{ text: string; as_of: string }> {
  return getJson(`${BASE}/sector-heat`);
}

export async function getRiskMacro(): Promise<{ text: string; as_of: string }> {
  return getJson(`${BASE}/risk-macro`);
}

export async function getFrameworkStatus(): Promise<{ text: string; as_of: string }> {
  return getJson(`${BASE}/framework-status`);
}

export async function getQuarterlyDirection(market: "us" | "india"): Promise<string> {
  return getText(`${API_ROOT}/${market}/quarterly-direction`);
}

// ---- India tab --------------------------------------------------------------

export async function getIndiaMarketSignals(): Promise<{ text: string; as_of: string }> {
  return getJson(`${INDIA_BASE}/market-signals`);
}

export async function getIndiaSixMonthCheck(): Promise<{ text: string; as_of: string }> {
  return getJson(`${INDIA_BASE}/6month-check`);
}

export async function getIndiaReport(): Promise<{ text: string; as_of: string }> {
  return getJson(`${INDIA_BASE}/report`);
}

// ---- Watchlist / composite scores (merged tab) -----------------------------

export async function getCompositeScores(): Promise<{ data: CompositeScoresData; as_of: string }> {
  return getJson(`${BASE}/composite-scores`);
}

export async function getWatchlist(): Promise<WatchlistRow[]> {
  return getJson(`${API_ROOT}/watchlist`);
}

export async function addWatchlistSymbol(symbol: string, notes = ""): Promise<void> {
  const r = await fetch(`${API_ROOT}/watchlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, notes }),
  });
  if (!r.ok) throw new Error(`POST watchlist failed: ${r.status}`);
}

export async function setWatchlistTracked(symbol: string, tracked: boolean): Promise<void> {
  const r = await fetch(`${API_ROOT}/watchlist/${symbol}/tracked`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tracked }),
  });
  if (!r.ok) throw new Error(`POST watchlist/tracked failed: ${r.status}`);
}
