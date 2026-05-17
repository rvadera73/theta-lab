# Theta-Lab Project Instructions

## Working Directory
**Always run commands from `/home/rahulvadera/projects/theta-lab`.**
This directory contains all data files, logs, and configuration needed for the options-trader skill and MCP tools.

## Auto-Approved Commands
The following commands are pre-approved and do not require per-call confirmation:
- All `cd /home/rahulvadera/projects/theta-lab` and subdirectory operations
- All read/write operations within this project directory
- `python3 scripts/*` (analysis and reporting scripts)
- `npm run *` (if applicable)

## Environment Setup
When working with the options-trader skill:
1. All MCP tool calls (`generate_unified_master_report`, `get_portfolio_pnl`, etc.) assume working directory is `/home/rahulvadera/projects/theta-lab`
2. Data files are located at `./data/` (positions, statements, snapshots)
3. Logs are saved to `./logs/` (reports, scheduler runs, analysis)
4. Scripts are in `./scripts/` and `./mcp/reports/`

## MCP Server: theta-lab
The skill uses the `theta-lab` MCP server which provides:
- `generate_unified_master_report` — generate daily/weekly/biweekly/monthly reports
- `get_portfolio_pnl` — fetch combined P&L per position
- `get_iv_rank` — IV volatility screening
- `scan_profit_take_candidates` — identify positions ready to close
- All other trading analysis tools

**Key requirement:** All MCP tool calls must execute from `/home/rahulvadera/projects/theta-lab` to find data files and configuration.

## Behavior Preferences
- Generate reports with `save_to_file: true` to persist to `./logs/`
- Always verify working directory with `pwd` before running report generators
- When reports fail due to permission errors on `data/` folder, it's always a working directory issue
- No unsolicited refactoring — only changes related to trading logic
- Terse responses — skip summaries, let diffs speak for themselves
