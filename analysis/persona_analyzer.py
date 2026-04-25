"""
Parses trade history CSV and computes trading persona metrics.
Run after placing your Schwab export in data/trade_history.csv.

Usage:
    python analysis/persona_analyzer.py --file data/trade_history.csv
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def load_trades(filepath: str) -> list[dict]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Trade history not found: {filepath}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def compute_metrics(trades: list[dict]) -> dict:
    """
    Expects columns (Schwab export format — adjust if different):
    Date, Symbol, Description, Quantity, Price, Amount, Type
    """
    wins, losses, pnl_list = 0, 0, []
    ticker_counts = defaultdict(int)
    strategy_counts = defaultdict(int)
    hold_days = []

    for trade in trades:
        try:
            amount = float(str(trade.get("Amount", "0")).replace(",", "").replace("$", ""))
            symbol = trade.get("Symbol", "").strip().upper()
            description = trade.get("Description", "").lower()

            if symbol:
                ticker_counts[symbol] += 1

            if amount > 0:
                wins += 1
                pnl_list.append(amount)
            elif amount < 0:
                losses += 1
                pnl_list.append(amount)

            # Rough strategy classification from description
            if "put" in description and "sold" in description:
                strategy_counts["cash_secured_put"] += 1
            elif "call" in description and "sold" in description:
                strategy_counts["covered_call"] += 1
            elif "spread" in description:
                strategy_counts["spread"] += 1
            elif "put" in description:
                strategy_counts["long_put"] += 1
            elif "call" in description:
                strategy_counts["long_call"] += 1

        except (ValueError, KeyError):
            continue

    total_trades = wins + losses
    win_rate = wins / total_trades if total_trades > 0 else 0
    total_pnl = sum(pnl_list)
    avg_win = sum(p for p in pnl_list if p > 0) / wins if wins > 0 else 0
    avg_loss = sum(p for p in pnl_list if p < 0) / losses if losses > 0 else 0
    risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0

    top_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 4),
        "wins": wins,
        "losses": losses,
        "total_pnl": round(total_pnl, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "risk_reward_ratio": round(risk_reward, 2),
        "top_tickers": top_tickers,
        "strategy_mix": dict(strategy_counts),
    }


def generate_persona_report(metrics: dict) -> str:
    lines = [
        "# Trading Persona Analysis",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d')}",
        "\n## Performance Metrics",
        f"- Total Trades Analyzed: {metrics['total_trades']}",
        f"- Win Rate: {metrics['win_rate']*100:.1f}%",
        f"- Total P&L: ${metrics['total_pnl']:,.2f}",
        f"- Average Win: ${metrics['avg_win']:,.2f}",
        f"- Average Loss: ${metrics['avg_loss']:,.2f}",
        f"- Risk/Reward Ratio: {metrics['risk_reward_ratio']:.2f}x",
        "\n## Strategy Mix",
    ]
    for strategy, count in sorted(metrics["strategy_mix"].items(), key=lambda x: x[1], reverse=True):
        lines.append(f"- {strategy}: {count} trades")

    lines += ["\n## Top Tickers by Activity"]
    for ticker, count in metrics["top_tickers"]:
        lines.append(f"- {ticker}: {count} trades")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze trade history and generate persona report")
    parser.add_argument("--file", required=True, help="Path to trade history CSV")
    parser.add_argument("--output", default="skills/trading_persona.md", help="Output path for persona report")
    args = parser.parse_args()

    print(f"Loading trades from {args.file}...")
    trades = load_trades(args.file)
    print(f"Found {len(trades)} rows.")

    metrics = compute_metrics(trades)
    report = generate_persona_report(metrics)

    print("\n--- Persona Summary ---")
    print(json.dumps(metrics, indent=2))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(f"\nPersona report written to {out_path}")


if __name__ == "__main__":
    main()
