# theta-lab

A Claude-powered options trading skill for systematic, risk-managed income generation.

## Target
20% annualized return across two Schwab accounts using a phased, AI-assisted approach.

## Accounts
- **Account A** — Schwab margin account: vertical spreads, iron condors, directional plays
- **Account B** — Schwab IRA: Wheel strategy (Cash-Secured Puts → Covered Calls), Level 1/2 only

## Deployment Phases

| Phase | Days | Mode | Scope |
|-------|------|------|-------|
| Mock | 1–30 | Paper trading | All signals logged, no real orders |
| Alpha | 31–60 | Live, capped | $100k cap, Account A only |
| Scale | 61–90 | Live, full | Full capital, Account A |
| Retirement | 91–120 | Live | Enable Account B automation |

## Structure

```
skills/              Claude skill files (.md) — symlinked to ~/.claude/skills/
analysis/            Persona analyzer, universe selector scripts
config/              Risk parameters (accounts.yaml is gitignored)
data/                Trade history CSVs (gitignored — stays local only)
logs/                Paper and live trade logs (gitignored)
docs/                Architecture decisions and phase plan
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Link skills to Claude
./scripts/link-skills.sh

# Run persona analysis (after placing trade history CSV in data/)
python analysis/persona_analyzer.py --file data/trade_history.csv
```

## Security
No credentials, account numbers, API keys, or trade data are committed to this repo.
See `.gitignore` for the full exclusion list.
