"""
Weekly Dashboard Orchestrator.
Reads latest Schwab CSV exports, runs all metrics and models,
formats HTML email, sends to ravjdpr@gmail.com.

Run manually:  python3 mcp/routines/weekly_dashboard.py
Run via cron:  see scripts/setup_cron.sh
"""

import os
import sys
import glob
import csv
import re
from datetime import datetime, date

# Allow imports from mcp/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

from analysis.metrics import (
    load_transactions, premium_capture_rate, profit_factor,
    breakeven_velocity, monthly_target_tracker,
)
from models.vix_regime import get_vix_term_structure, entry_timing_score
from models.monte_carlo import simulate_assignment_probability
from models.kelly import batch_kelly
from models.ev_model import batch_ev
from analysis.regime import detect_regime
from routines.email_report import build_html_email, send_email as send_email_fn


# ---------------------------------------------------------------------------
# Config — edit these to match your setup
# ---------------------------------------------------------------------------

TO_EMAIL = "ravjdpr@gmail.com"
FROM_EMAIL = "onboarding@resend.dev"   # Resend's built-in sender, no domain needed
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "statements"
)
LOGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
)

# Known assigned positions (update weekly from Account A)
ASSIGNED_POSITIONS = [
    {"symbol": "PYPL",  "shares": 1300, "cost_basis": 132.0, "monthly_cc": 1800,  "recovered": 15000},
    {"symbol": "ADBE",  "shares": 300,  "cost_basis": 495.0, "monthly_cc": 2200,  "recovered": 8000},
    {"symbol": "AXON",  "shares": 200,  "cost_basis": 628.0, "monthly_cc": 3500,  "recovered": 12000},
    {"symbol": "CRM",   "shares": 200,  "cost_basis": 302.0, "monthly_cc": 1200,  "recovered": 5000},
    {"symbol": "OKTA",  "shares": 600,  "cost_basis": 91.0,  "monthly_cc": 1800,  "recovered": 6000},
    {"symbol": "NKE",   "shares": 100,  "cost_basis": 86.0,  "monthly_cc": 300,   "recovered": 1000},
    {"symbol": "LYFT",  "shares": 400,  "cost_basis": 30.0,  "monthly_cc": 200,   "recovered": 500},
    {"symbol": "MRNA",  "shares": 400,  "cost_basis": 96.0,  "monthly_cc": 1200,  "recovered": 4000},
    {"symbol": "UNH",   "shares": 100,  "cost_basis": 390.0, "monthly_cc": 1500,  "recovered": 3000},
]

# Open puts for Monte Carlo (update weekly)
OPEN_PUTS = [
    {"symbol": "AXON", "strike": 470, "dte": 54,  "contracts": 1},
    {"symbol": "AXON", "strike": 660, "dte": 146, "contracts": 1},
    {"symbol": "AXON", "strike": 540, "dte": 237, "contracts": 1},
    {"symbol": "AXON", "strike": 420, "dte": 265, "contracts": 1},
    {"symbol": "APP",  "strike": 580, "dte": 118, "contracts": 1},
    {"symbol": "APP",  "strike": 460, "dte": 83,  "contracts": 1},
    {"symbol": "ADBE", "strike": 310, "dte": 118, "contracts": 1},
    {"symbol": "META", "strike": 550, "dte": 237, "contracts": 1},
    {"symbol": "META", "strike": 520, "dte": 328, "contracts": 1},
    {"symbol": "ZS",   "strike": 180, "dte": 237, "contracts": 1},
    {"symbol": "IBM",  "strike": 270, "dte": 174, "contracts": 1},
    {"symbol": "LMT",  "strike": 520, "dte": 328, "contracts": 1},
    {"symbol": "OKTA", "strike": 70,  "dte": 118, "contracts": 1},
]

# Entry candidates for Kelly + EV screening
ENTRY_CANDIDATES = [
    {"symbol": "UBER",  "pop": 0.85, "premium_credit": 400, "strike": 68, "current_price": 74.64, "cc_monthly_premium": 150, "recovery_months": 6},
    {"symbol": "MSFT",  "pop": 0.83, "premium_credit": 900, "strike": 390,"current_price": 424.62,"cc_monthly_premium": 800, "recovery_months": 12},
    {"symbol": "META",  "pop": 0.84, "premium_credit": 1800,"strike": 620,"current_price": 675.03,"cc_monthly_premium": 1500,"recovery_months": 12},
    {"symbol": "OKTA",  "pop": 0.82, "premium_credit": 500, "strike": 70, "current_price": 75.98, "cc_monthly_premium": 300, "recovery_months": 12},
    {"symbol": "AXON",  "pop": 0.80, "premium_credit": 1200,"strike": 370,"current_price": 397.12,"cc_monthly_premium": 2000,"recovery_months": 18},
    {"symbol": "COIN",  "pop": 0.82, "premium_credit": 800, "strike": 175,"current_price": 199.77,"cc_monthly_premium": 500, "recovery_months": 6},
    {"symbol": "PLTR",  "pop": 0.83, "premium_credit": 500, "strike": 95, "current_price": 110.0, "cc_monthly_premium": 400, "recovery_months": 12},
]

ACCOUNT_A_SIZE = 429_659

SNAPSHOT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "portfolio_snapshot.yaml"
)


def load_snapshot() -> dict:
    """Load portfolio_snapshot.yaml — the manually-updated weekly state file."""
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE) as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# CSV Parsers
# ---------------------------------------------------------------------------

def find_latest_file(pattern: str) -> str | None:
    files = glob.glob(os.path.join(DATA_DIR, pattern))
    return max(files, key=os.path.getmtime) if files else None


def parse_position_csv(filepath: str) -> list[dict]:
    """Parse Schwab position export CSV into list of position dicts."""
    positions = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Skip the title row and find the header row
    header_idx = None
    for i, line in enumerate(lines):
        if '"Symbol"' in line or 'Symbol' in line and 'Description' in line:
            header_idx = i
            break

    if header_idx is None:
        return positions

    reader = csv.DictReader(lines[header_idx:])
    for row in reader:
        symbol = row.get("Symbol", "").strip().strip('"')
        if not symbol or symbol.startswith("Account"):
            continue
        asset_type = row.get("Asset Type", "").strip().strip('"')
        try:
            qty = float(str(row.get("Qty (Quantity)", "0")).strip().strip('"').replace(",", ""))
            price_str = str(row.get("Price", "0")).strip().strip('"').replace("$", "").replace(",", "")
            price = float(price_str) if price_str else 0.0
            cost_str = str(row.get("Cost Basis", "0")).strip().strip('"').replace("$", "").replace(",", "")
            cost = float(cost_str) if cost_str else 0.0
            mkt_str = str(row.get("Mkt Val (Market Value)", "0")).strip().strip('"').replace("$", "").replace(",", "")
            mkt_val = float(mkt_str) if mkt_str else 0.0
        except (ValueError, AttributeError):
            continue

        positions.append({
            "symbol": symbol,
            "asset_type": asset_type,
            "quantity": qty,
            "price": price,
            "cost_basis": cost,
            "market_value": mkt_val,
        })

    return positions


def compute_assigned_book_value(positions: list[dict]) -> float:
    """Sum market value of all equity positions (assigned stock)."""
    return sum(
        p["market_value"] for p in positions
        if p.get("asset_type", "").lower() in ("equity", "stock")
        and p.get("market_value", 0) > 0
    )


# ---------------------------------------------------------------------------
# Top Actions Builder (manual until live API)
# ---------------------------------------------------------------------------

TOP_ACTIONS = [
    {"symbol": "COIN $250P May 15", "action": "Roll to Jul $210P or Close", "condition": "BTC > $90K → Roll; else Close", "priority": "URGENT"},
    {"symbol": "MSFT $420P May 15", "action": "Roll to Jul $405P",         "condition": "Unconditional",                 "priority": "URGENT"},
    {"symbol": "PYPL $45C May 15",  "action": "Accept assignment; sell new CCs on 1,000 shares", "condition": "Unconditional", "priority": "URGENT"},
    {"symbol": "AXON $600C Dec 18", "action": "Buy to Close (56.6% profit)", "condition": "Unconditional",               "priority": "STRONG"},
    {"symbol": "AXON $620C Jan 27", "action": "Buy to Close (53.5% profit)", "condition": "Unconditional",               "priority": "STRONG"},
    {"symbol": "META $550P + $520P","action": "Close if cash improves margin", "condition": "Cash < $125K",              "priority": "WATCH"},
    {"symbol": "LYFT shares",       "action": "Close all shares",            "condition": "Q2 2026 exit",                "priority": "WATCH"},
]


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------

def run_weekly_dashboard(send_email: bool = True, save_log: bool = True) -> dict:
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Starting weekly dashboard...")

    # 1. Load snapshot (always available — committed to repo)
    snapshot = load_snapshot()
    if snapshot:
        print(f"  Loaded portfolio snapshot (last updated: {snapshot.get('last_updated', '?')})")
        # Override hardcoded values with snapshot data
        snap_positions = snapshot.get("assigned_positions", [])
        snap_puts = snapshot.get("open_puts", [])
        assigned_positions = [
            {**p, "recovered": p.get("recovered", 0)} for p in snap_positions
        ] if snap_positions else ASSIGNED_POSITIONS
        # Compute DTE at runtime from expiry dates — never stale
        open_puts_list = []
        for p in (snap_puts if snap_puts else OPEN_PUTS):
            put = dict(p)
            if "expiry" in put and "dte" not in put:
                try:
                    exp = datetime.strptime(put["expiry"], "%Y-%m-%d").date()
                    put["dte"] = max(0, (exp - date.today()).days)
                except Exception:
                    put["dte"] = put.get("dte", 45)
            open_puts_list.append(put)
    else:
        print("  No snapshot file found — using hardcoded defaults.")
        assigned_positions = ASSIGNED_POSITIONS
        open_puts_list = OPEN_PUTS

    # 2. Load local CSVs if available (local runs only — not in GitHub Actions)
    txn_file = find_latest_file("*Transactions*.csv") or find_latest_file("*transactions*.csv")
    pos_file = find_latest_file("Individual-Positions*.csv")

    transactions = load_transactions(txn_file) if txn_file else []
    positions = parse_position_csv(pos_file) if pos_file else []

    print(f"  CSVs: {len(transactions)} transactions, {len(positions)} position rows.")

    # 3. Compute metrics (from CSVs if available, else from snapshot)
    if transactions:
        capture = premium_capture_rate(transactions)
        pf = profit_factor(transactions)
        mt = monthly_target_tracker(
            transactions,
            unrealized_equity_change=snapshot.get("month_to_date_equity_change", -15000),
            target_monthly=100_000,
        )
    else:
        # Fallback to snapshot values when no CSV available (GitHub Actions)
        capture = {
            "capture_rate": snapshot.get("ytd_premium_capture_rate", "—"),
            "signal": "WATCH" if snapshot.get("ytd_premium_capture_rate", 65) < 65 else "GOOD",
            "interpretation": f"YTD capture rate: {snapshot.get('ytd_premium_capture_rate', '—')}% (from snapshot)",
        }
        pf = {
            "profit_factor": snapshot.get("ytd_profit_factor", "—"),
            "signal": "GOOD",
            "win_count": "—", "loss_count": "—",
            "interpretation": f"Profit factor: {snapshot.get('ytd_profit_factor', '—')} (from snapshot)",
        }
        mtd_premium = snapshot.get("month_to_date_premium", 0)
        mtd_equity = snapshot.get("month_to_date_equity_change", 0)
        combined = mtd_premium + mtd_equity
        pct = combined / 100_000 * 100
        mt = {
            "pct_of_target": round(pct, 1),
            "combined_total": combined,
            "net_options_premium": mtd_premium,
            "unrealized_equity_change": mtd_equity,
            "target_monthly": 100_000,
            "remaining_to_target": max(0, 100_000 - combined),
            "signal": "ON TRACK" if pct >= 80 else ("WATCH" if pct >= 50 else "BEHIND"),
            "interpretation": f"MTD: ${combined:,.0f} of $100,000 target ({pct:.1f}%). From snapshot.",
        }

    # 4. Breakeven velocities
    bev_results = []
    for pos in assigned_positions:
        # Compute unrealized loss
        current_price = next(
            (p["price"] for p in positions
             if p["symbol"] == pos["symbol"] and p["asset_type"].lower() == "equity"),
            None
        )
        if current_price is None:
            # Use cost basis as fallback — no current price found
            unrealized = pos["shares"] * pos["cost_basis"] * 0.25  # rough estimate
        else:
            unrealized = max(0, (pos["cost_basis"] - current_price) * pos["shares"])

        if unrealized > 0:
            bev = breakeven_velocity(
                symbol=pos["symbol"],
                unrealized_loss=unrealized,
                monthly_cc_premium=pos["monthly_cc"],
                premium_already_recovered=pos.get("recovered", 0),
            )
            bev_results.append(bev)

    # Sort by months to breakeven (longest first = most urgent to watch)
    bev_results.sort(key=lambda x: x.get("months_to_breakeven") or 999, reverse=True)

    # 4. Regime + VIX
    regime = detect_regime()
    vix_term = get_vix_term_structure()
    print(f"  VIX: {vix_term.get('vix', '?')} | Term structure: {vix_term.get('ratio', '?')}")

    # 5. Monte Carlo
    print("  Running Monte Carlo simulation...")
    mc_result = simulate_assignment_probability(open_puts_list, n_simulations=5000)
    print(f"  P(exceed danger zone): {mc_result['p_exceed_danger_zone']}%")

    # 6. Kelly + EV for entry candidates
    kelly_results = batch_kelly(ENTRY_CANDIDATES, account_size=ACCOUNT_A_SIZE)
    ev_results = batch_ev(ENTRY_CANDIDATES)

    # 7. Portfolio health summary
    assigned_book = compute_assigned_book_value(positions)
    if assigned_book == 0:
        assigned_book = 401_000  # fallback from last known value

    book_signal = (
        "THROTTLE" if assigned_book > 450_000 else
        "WATCH" if assigned_book > 375_000 else
        "GOOD"
    )

    dashboard_data = {
        "monthly_target": mt,
        "regime": regime,
        "vix_term": vix_term,
        "metrics": {
            "premium_capture": capture,
            "profit_factor": pf,
        },
        "portfolio_health": {
            "assigned_book": round(assigned_book, 0),
            "danger_zone": 375_000,
            "book_signal": book_signal,
            "ytd_net_premium": 457_547,  # from YTD analysis; update periodically
        },
        "monte_carlo": mc_result,
        "top_actions": TOP_ACTIONS,
        "breakeven_tracker": bev_results,
        "kelly_candidates": kelly_results,
    }

    # 8. Build HTML
    report_date = datetime.now().strftime("%B %d, %Y")
    html = build_html_email(dashboard_data, report_date)

    # 9. Save markdown log
    if save_log:
        log_path = os.path.join(LOGS_DIR, f"dashboard_{date.today()}.md")
        with open(log_path, "w") as f:
            f.write(f"# Dashboard Snapshot — {report_date}\n\n")
            f.write(f"## Monthly Target\n{mt.get('interpretation', '')}\n\n")
            f.write(f"## VIX Term Structure\n{vix_term.get('action', '')}\n\n")
            f.write(f"## Monte Carlo\n{mc_result.get('action', '')}\n\n")
            f.write(f"## Premium Capture\n{capture.get('interpretation', '')}\n\n")
            f.write(f"## Profit Factor\n{pf.get('interpretation', '')}\n\n")
            f.write("## Breakeven Tracker\n")
            for b in bev_results:
                f.write(f"- {b.get('interpretation', '')}\n")
            f.write("\n## Top Kelly Entries\n")
            for k in kelly_results[:3]:
                f.write(f"- {k.get('interpretation', '')}\n")
        print(f"  Saved log: {log_path}")

    # 10. Send email
    subject = f"Theta-Lab Dashboard — {report_date} | Target: {mt.get('pct_of_target', 0):.0f}%"
    if send_email and RESEND_API_KEY:
        result = send_email_fn(TO_EMAIL, subject, html, FROM_EMAIL, RESEND_API_KEY)
        if result["success"]:
            print(f"  Email sent to {TO_EMAIL}")
        else:
            print(f"  Email failed: {result['error']}")
    elif send_email:
        print("  Email skipped — RESEND_API_KEY not set in .env")

    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Dashboard complete.")
    return dashboard_data


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-email", action="store_true", help="Skip sending email")
    parser.add_argument("--no-log",   action="store_true", help="Skip saving log file")
    args = parser.parse_args()
    run_weekly_dashboard(send_email=not args.no_email, save_log=not args.no_log)
