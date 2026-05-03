# Copilot Session Context — Rahul Vadera / Theta-Lab

> **READ THIS FIRST before any implementation.**
> This file is the memory layer for GitHub Copilot across sessions.
> Update it when new preferences, constraints, or decisions are confirmed.

---

## 🔑 Before You Start ANY Task — Ask These First

Before writing a single line of code, confirm:

1. **Integration contract**: "Should this go through the MCP server only, or can it also run as a standalone script?"
2. **Data source**: "Should this use live Schwab API, fallback snapshot, or both with a warning banner?"
3. **Output format**: "Who reads this — you in terminal, HTML email, or Claude chat response?"
4. **Definition of done**: "What does working look like — what will you check?"
5. **Constraints**: "Any capital limits, sectors to avoid, accounts to exclude, or risk rules?"

Do NOT assume. Ask. One question at a time using ask_user tool.

---

## 👤 Owner

**Rahul Vadera** — theta/premium-selling options trader
- Email: ravjdpr@gmail.com
- Goal: $100K/month / $1.2M/year from options premium
- Style: Not prescriptive — gives examples as direction, not hard requirements
- Feedback style: Direct. Will call out generic advice immediately.

---

## 🏗️ Architecture Decisions (Locked)

| Decision | Choice | Reason |
|----------|--------|--------|
| Single integration point | **MCP server only** | All tools, reports, ad-hoc queries go through MCP |
| Credential source | `~/.claude.json` → `mcpServers.theta-lab.env` | Loaded at server startup via `scripts/start_http_server.sh` |
| Credential bootstrap | `mcp/bootstrap.py` → called from `server.py` BEFORE imports | So schwab_client gets real env vars at import time |
| Live data primary | Schwab API via `schwab_client.py` → `_get_accounts_direct()` | Works without MCP broker registry |
| Live data fallback | `data/portfolio_snapshot.yaml` + Schwab CSVs | Always show ⚠️ banner if using fallback |
| Report delivery | HTML email via Resend → ravjdpr@gmail.com | FROM: onboarding@resend.dev |
| Server startup | `scripts/start_http_server.sh` ONLY | Never `nohup python3 mcp/server.py` |

---

## 📊 Portfolio Structure

| Account | Type | Strategy | Hash Env Var |
|---------|------|----------|-------------|
| **A** (232) | Schwab Margin | Naked strangles, CSP+CC wheel | `SCHWAB_ACCOUNT_A_HASH` |
| **B** (275) | Schwab IRA (Pinky) | Pure wheel CSP→CC only | `SCHWAB_ACCOUNT_B_HASH` |
| **C** (634) | Schwab Designated Beneficiary | CSP+CC only, NO naked calls | `SCHWAB_ACCOUNT_C_HASH` |
| **India** | ICICI Breeze NSE FNO | Index + stock F&O | Breeze API |

**NEVER use** `data/statements/2026-01-01 thru 2026-04-25 transactions.csv` — this is an
Empower consolidated export mixing 14+ accounts in a different format.

---

## 🎯 Income Targets

| Period | Target |
|--------|--------|
| Daily | $5,000 |
| Weekly | $20,000 |
| Monthly | $100,000 |
| Annual | $1,200,000 |

Track against these in ALL reports. Never use different numbers.

---

## 📅 Report Schedule

| Report | When | Cron (UTC) | File |
|--------|------|------------|------|
| Weekly Combined | Sunday 8:30 PM ET | `30 0 * * 1` | `weekly_combined.yml` |
| Bi-monthly Technical | 15th 8:30 PM ET | `30 0 16 * *` | `bimonthly_technical.yml` |
| Monthly Objectives | 1st 8:30 PM ET | `30 0 2 * *` | `monthly_objectives.yml` |

---

## 🧠 Trading Persona Rules

- **IVR ≥ 40** required for any new entry
- **Tier 1**: Blue chip CSP+CC wheel (SPY, QQQ, AAPL, MSFT level)
- **Tier 2**: Growth CSP or spreads (CRWD, ALAB, VRT level)
- **Tier 3**: Speculative, small size only (RKLB, RBRK level)
- **Permanent exits**: PYPL (1300 sh), MRNA (400 sh) — run CC to exit, no new puts
- **Earnings blackout**: No new entries within 7 days of earnings
- **Bear/sideways regime**: Defense/energy/financials float up; suppress pure tech/AI new entries
- **Target capture rate**: 65–70% of max premium

---

## 📈 Sector Preferences & Watch Themes

> These are EXAMPLES of direction, not a static list. The screener should find names dynamically.

| Theme | Why |
|-------|-----|
| Nuclear & Clean Energy | AI data center power demand; non-correlated to tech |
| Defense & Aerospace | Geopolitical tailwind; macro hedge vs AI selloff |
| AI Infrastructure (hardware) | VRT, APH — monetize AI capex without chip risk |
| Cybersecurity | Structural growth; CRWD already works well |
| Financials | Rate environment tailwind |
| India NSE | Separate macro drivers; PSU/defense/banking cycle |

**Current concern**: Portfolio ~80% AI/tech + biotech — diversification is a priority.
**AI/tech view**: Overpriced, risky. Do not add more pure AI/chip exposure.

---

## 🇮🇳 India Market Rules

- India VIX drives regime independently from US VIX
- NSE monthly expiry cycle (not weekly)
- Yield measured per rupee of SPAN margin blocked
- India-specific macro: RBI policy, FII flows, Union Budget, monsoon
- PSU cycle (HAL, NTPC, BEL) behaves differently from IT/pharma

---

## 🚫 What NOT to Do

- **Never give generic sector advice** — Rahul gives examples as direction; go deeper with actual research
- **Never hardcode watchlists** — screeners must be dynamic and regime-aware
- **Never build HTML reports without showing a sketch/wireframe first**
- **Never start implementation without confirming architecture** (MCP-only? script? both?)
- **Never assume the data source is correct** — validate live API works before building on top
- **Never use the Empower consolidated CSV** for premium calculations
- **Never commit with secrets** in code

---

## ✅ Session Start Checklist

Before any new feature/task:

- [ ] Read this file
- [ ] Confirm MCP server is running: `systemctl --user status theta-lab-mcp`
- [ ] Confirm live data works: test `get_live_positions` MCP tool
- [ ] Ask architecture question if it's a new component
- [ ] Ask output format question if it produces user-visible output
- [ ] Ask constraint question if it involves capital, risk, or new positions

---

## 📝 Decision Log

| Date | Decision | Context |
|------|----------|---------|
| 2026-04-28 | MCP server = single integration point | Reports were running both as scripts and via MCP, causing credential confusion |
| 2026-04-28 | Credential bootstrap in `bootstrap.py`, called from `server.py` before imports | `schwab_client` was reading empty env vars at import time |
| 2026-04-28 | `_get_accounts_direct()` for ALL accounts | Account A was using `open_stocks_mcp` broker registry which only works in MCP context |
| 2026-04-28 | Dynamic screener, not hardcoded watchlist | Rahul wants the system to find opportunities, not repeat his examples |
| 2026-04-28 | YTD + gap closure in monthly report | Monthly report must show annual progress and HOW to close the gap, not just current month |
| 2026-04-28 | $20K/week / $5K/day targets | Earlier reports had wrong weekly target ($6,731) |
| 2026-05-02 | India screener uses own VIX/regime, independent of US | India and US macro drivers diverge frequently |
