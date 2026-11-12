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
  // ADR 0005: the per-leg classification heat_scanner.py now scores color/
  // action from directly -- `covered` below is a separate, older, pooled
  // cross-account display annotation (see services.py) and can legitimately
  // read `false` on a leg whose own `coverage` here is "COVERED", when an
  // identical contract is held naked in a different account.
  coverage?: "NAKED" | "COVERED" | "PARTIAL" | "CASH_SECURED_PUT";
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

// ---- Watchlist / composite-scores tab (merged, 2026-10-16) --------------

export interface CompositeScoreRow {
  ticker: string;
  tail_risk: boolean;
  error?: string;
  flags: string[];
  yield_pct: number | null;
  conviction: number | null;
  target_upside_pct: number | null;
  sector: string;
  verticals: string[];
  invested: number | null;
  heat: string | null;
  rsi: number | null;
  price: number | null;
  is_new: boolean;
  score: number | null;
  iv_rank: number | null;
  real_put_yield_pct: number | null;
  real_call_yield_pct: number | null;
  beta: number | null;
  yield_rank: number | null;
  conviction_rank: number | null;
  rank: number | null;
  population_size: number | null;
  gates_fired?: string[];
  valuation_penalty?: number;
  notes?: string;
}

export interface RealizedRow {
  ticker: string;
  realized_pnl_90d: number;
  closed_count_90d: number;
  composite_rank: number | null;
  tail_risk: boolean;
  conviction: number | null;
  conviction_rank: number | null;
  yield_pct: number | null;
  yield_rank: number | null;
  flags: string[];
}

export interface CompositeScoresData {
  held: CompositeScoreRow[];
  watchlist: CompositeScoreRow[];
  regime: string;
  macro_stage: string;
  severity_smoothed: number;
  high_exposure_sectors: string[];
  sensitivity_confidence: string;
  realized_top_performers_90d: RealizedRow[];
  realized_losses_90d: RealizedRow[];
  realized_no_activity_90d: RealizedRow[];
  realized_cutoff: string;
}

export interface WatchlistRow {
  symbol: string;
  tracked: number | boolean;
  notes: string;
  added_at: string;
  updated_at: string;
}

// ---- US tab ---------------------------------------------------------------

export interface AccountStatusRow {
  account: string;
  balance: number;
  pct: number;
  account_type: string;
  is_margin: boolean;
  notional: number;
  opt_req: number;
  utilization: number;
  status: string;
  opt_req_real: number | null;
  opt_req_real_as_of: string | null;
  has_positions: boolean;
  position_count: number;
  target: number;
  actual: number;
  gap: number;
  pct_gap: number;
  balance_as_of: string;
  balance_days_stale: number;
}

export interface PnlAccountRow {
  ytd_realized: number;
  mtd_realized: number;
  annual_target: number;
  unmatched_amount: number;
  unmatched_count: number;
}

export interface PnlTrendData {
  as_of: string;
  per_account: Record<string, PnlAccountRow>;
  portfolio_qtd_realized: number;
  [key: string]: unknown;
}

export interface CashMarginForecast {
  as_of: string;
  total_notional: number;
  opt_req: number;
  stress_low: number;
  stress_high: number;
  operating_cash_target: number;
  emergency_reserve: number;
  reserve_covers_stress: boolean;
  capacity: number;
  capacity_as_of: string;
  dte_buckets: { label: string; pct: number; target_lo: number; target_hi: number; status: string }[];
  top_expiry_dates: { date: string; notional: number; pct: number; status: string }[];
}

export interface HeatLeg {
  symbol: string;
  type: string;
  strike: number;
  expiry: string;
  dte: number;
  current_price: number | null;
  distance_pct: number | null;
  pnl_pct: number | null;
  loss_multiple: number | null;
  color: "RED" | "YELLOW" | "GREEN" | "UNKNOWN";
  action: string;
  reason: string;
  coverage?: "NAKED" | "COVERED" | "PARTIAL" | "CASH_SECURED_PUT";  // ADR 0005
  covered: boolean | null;
  covered_contracts: number | null;
  total_contracts: number | null;
  strangle: boolean;
  account: string;
  sector?: string;
  gates_fired?: string[];
  cost_to_close: number;
}

export interface PositionHeatData {
  by_color: Record<string, HeatLeg[]>;
  counts: Record<string, number>;
  regime: string;
  sector_rollup: Record<string, { RED: number; YELLOW: number; GREEN: number; UNKNOWN: number; red_cost_to_close: number }>;
}
