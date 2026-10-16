// Mirrors the real shapes services.get_today_plan() / account_state.py
// return -- kept intentionally loose (optional fields, `unknown` escape
// hatches) rather than over-modeled, since the backend is Python/dict-based
// and genuinely does omit fields in some branches (e.g. a composite-score
// "ref" has no `legs`, a position-heat "ref" has no `score`).

export interface AccountState {
  account: string;
  cash: number | null;
  cash_plus_borrowing: number | null;
  option_requirement: number | null;
  balance_subject_to_interest: number | null;
  equity_pct: number | null;
  notes?: string | null;
  updated_at: string;
  days_stale: number;
}

export interface Leg {
  symbol: string;
  type: "CALL" | "PUT";
  strike: number;
  expiry: string;
  dte: number;
  color: "RED" | "YELLOW" | "GREEN" | "UNKNOWN";
  action: string;
  reason: string;
  covered: boolean | null;
  covered_contracts: number | null;
  total_contracts: number | null;
  strangle: boolean;
  account: string;
  sector?: string;
  gates_fired?: string[];
}

export interface PositionGroupRef {
  symbol: string;
  account: string;
  sector: string;
  legs: Leg[];
  worst_color: string;
  worst_action: string;
  leg_count: number;
  total_cost_to_close: number;
}

export interface CompositeScoreRef {
  ticker: string;
  score: number;
  rank: number;
  population_size: number;
  yield_pct: number;
  conviction: number;
  iv_rank: number | null;
  real_put_yield_pct: number | null;
  real_call_yield_pct: number | null;
  beta: number | null;
  sector: string;
  gates_fired?: string[];
}

export interface PlanItem {
  section: "GATE" | "CASH RELIEF FIRST" | "MANAGE HARD STOPS" | "NEW ENTRY CANDIDATES";
  action: string;
  why: string;
  detail?: string;
  ref: PositionGroupRef | CompositeScoreRef;
}

export interface TodayPlan {
  account_state: AccountState | null;
  context_notes: string[];
  cash_or_equity_stressed: boolean;
  total_sequenced: number;
  plan: PlanItem[];
}

export function isPositionGroup(ref: PositionGroupRef | CompositeScoreRef): ref is PositionGroupRef {
  return Array.isArray((ref as PositionGroupRef).legs);
}
