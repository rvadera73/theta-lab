# Theta-Lab Copilot Instructions

These rules apply to every code change in this repository. Read and follow them before writing any code.

---

## 1. Extensibility First — Never Hardcode

**The single most important rule.** Before implementing any feature, ask: *"If scope grows by one, does this require changes in more than one place?"* If yes, redesign.

### Account / Broker Pattern
- All accounts live in the `ACCOUNTS` registry in `config.py`. That is the **only** place account metadata is defined.
- Adding a new account = one new dict entry in `ACCOUNTS`. Zero other file changes required.
- Any function that iterates accounts must read from `ACCOUNTS` dynamically — never from a hardcoded list like `["A", "B"]`.
- Broker dispatch logic (Schwab vs Robinhood vs future) lives in **one** function: `_load_positions_all()`. New broker = one `elif` block there, nowhere else.

```python
# WRONG — hardcoded, breaks every time scope grows
acct_map = {"A": hash_a, "B": hash_b}

# RIGHT — dynamic, registry-driven
acct_map = _get_configured_accounts()
```

### Sector / Universe Pattern
- Screener universes live in `screener_universe.py`. New sector = one entry there.
- Sector weights live in the regime config block. Never embed weights as magic numbers inside scoring logic.

### Report / Tool Pattern
- Any new data source plugs into `load_us_positions()` or `load_india_positions()`. All downstream reports get it automatically.
- Tool handlers in `server.py` call shared loaders — they never fetch data directly.

---

## 2. Single Source of Truth

Every piece of configuration has exactly one home:

| What | Where |
|------|-------|
| Account metadata | `config.py` → `ACCOUNTS` |
| Regime thresholds | `config.py` → `REGIME_THRESHOLDS` |
| Profit/DTE targets | `config.py` → `PROFIT_TARGETS`, `DTE_TARGETS` |
| Permanent exit list | `config.py` → `PERMANENT_EXITS` |
| Screener universe | `screener_universe.py` |
| Position loading | `report_utils.py` → `load_us_positions()` |
| Broker dispatch | `server.py` → `_load_positions_all()` |

If you find yourself duplicating a value, stop and refactor to reference the canonical source.

---

## 3. No Cascading Refactors

- If a small scope change (e.g., "add one more account") would require touching 5+ files, the original design was wrong.
- **Before implementing**, think through: what does adding the next instance of this thing require? If the answer is "edit N files", redesign to N=1.
- Prefer adding to a registry/config over adding new code paths.

---

## 4. Coding Standards for This Project

- **Async**: MCP tool handlers are async. Any sync I/O (Robinhood, CSV) runs in `asyncio.get_event_loop().run_in_executor(None, fn)`.
- **Position model**: Always use `Position` and `OptionLeg` from `analysis/pnl.py`. Never create ad-hoc dicts to represent positions.
- **Error handling**: External API calls (Schwab, Robinhood, Breeze) must be non-fatal — catch exceptions, log, continue. Never let one broker failure crash a report.
- **Reports**: All reports output HTML saved to `logs/`. Use `maybe_send()` for email. Never print raw data as the final output.
- **Heat scanner**: Use `heat_from_positions()` → `format_heat_html()` everywhere. Never re-implement traffic-light logic inline.

---

## 5. Before Writing Any Code

Ask yourself:
1. Is there already a canonical function/config for this? (Check the table above.)
2. Will adding the *next* instance of this thing require touching this file again?
3. Am I duplicating logic that belongs in one place?
4. Does this change require updating tool schemas, enums, or hardcoded lists anywhere?

If any answer is "yes" to 2–4, solve the structural problem first.

---

## 6. Commit Discipline

- Commit after each logical unit of work, not at end of session.
- Commit message: what changed and why (not just "fix bug").
- Always include: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`

---

## Project Context

- **Goal**: $100K/month premium income from theta strategies across Schwab (A/B/C), Robinhood (D), India/Breeze.
- **Persona**: Sell puts/strangles on high-IVR names, 30-45 DTE, regime-gated. No directional bets.
- **Stack**: Python 3.11, MCP server (stdio), `schwab-py`, `robin_stocks`, `breeze_connect`, FastAPI-style tool handlers.
- **Reports**: Weekly action (Monday), Bimonthly technical (15th/end), Monthly objectives (1st).
