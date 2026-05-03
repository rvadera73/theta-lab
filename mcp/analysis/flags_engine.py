"""
Dynamic flag evaluation engine.

Flags are evaluated from live data sources (yfinance fundamentals, SEC EDGAR API,
yfinance news) and cached with per-flag TTLs. Stale flags are re-evaluated on access.

Cache: data/flags_cache.json
Seed: mcp/reports/screener_universe.py US_FLAGS_BY_SYMBOL (bootstrap only)
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
import yfinance as yf

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE_PATH = os.path.join(_REPO_ROOT, "data", "flags_cache.json")

# ─── TTL per flag (days). 0 = always re-evaluate (portfolio-state flags). ────
FLAG_TTL_DAYS: dict[str, int] = {
    "ACCOUNTING_RISK": 30,
    "DELISTING_RISK": 30,
    "GOING_CONCERN": 30,
    "HALTED": 1,
    "REGULATORY_RISK": 30,
    "BINARY_EVENT_RISK": 14,
    "THIN_MARGINS": 90,
    "HIGH_DEBT": 90,
    "LOW_MOAT": 90,
    "CHINA_EXPOSURE": 30,
    "COMMODITY_PRICE_RISK": 60,
    "SPECULATIVE_STORY": 90,
    "RECENT_DILUTION": 30,
    "LOW_OPTIONS_LIQUIDITY": 14,
    "TURNAROUND_UNPROVEN": 60,
    "AI_CONCENTRATION": 0,
    "OVERWEIGHT_SECTOR": 0,
    "IDLE_CC_AVAILABLE": 0,
    "PERMANENT_EXIT": 3650,   # effectively permanent — only manual override
}

HARD_BLOCK_FLAG_KEYS = {
    "ACCOUNTING_RISK", "DELISTING_RISK", "GOING_CONCERN", "HALTED", "PERMANENT_EXIT",
}


# ─── Cache helpers ────────────────────────────────────────────────────────────

def _load_cache() -> dict[str, Any]:
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2, default=str)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _flag_entry(flag: str, confidence: float, source: str, notes: str = "") -> dict:
    now = _utcnow()
    ttl = FLAG_TTL_DAYS.get(flag, 30)
    expires = (now + timedelta(days=ttl)) if ttl > 0 else now
    return {
        "flag": flag,
        "confidence": round(confidence, 2),
        "source": source,
        "notes": notes,
        "is_hard_block": flag in HARD_BLOCK_FLAG_KEYS,
        "evaluated_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    }


def _is_stale(entry: dict) -> bool:
    ttl = FLAG_TTL_DAYS.get(entry["flag"], 30)
    if ttl == 0:
        return True  # portfolio-state: always re-evaluate
    expires = datetime.fromisoformat(entry["expires_at"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return _utcnow() > expires


# ─── Evaluators ───────────────────────────────────────────────────────────────

def _evaluate_yfinance(symbol: str) -> list[dict]:
    """Structural flags from yfinance fundamentals. TTL 90 days."""
    flags: list[dict] = []
    try:
        info = yf.Ticker(symbol).info

        op_margins = info.get("operatingMargins")
        if op_margins is not None and op_margins < 0.05:
            flags.append(_flag_entry(
                "THIN_MARGINS", 0.95,
                f"yfinance operatingMargins={op_margins:.1%}",
                f"Operating margin {op_margins:.1%} < 5% — price-taker / commodity assembler"
            ))

        gross = info.get("grossMargins")
        if gross is not None and gross < 0.20:
            flags.append(_flag_entry(
                "LOW_MOAT", 0.75,
                f"yfinance grossMargins={gross:.1%}",
                f"Gross margin {gross:.1%} — limited pricing power, easily substituted"
            ))

        dte = info.get("debtToEquity")  # yfinance returns as %, e.g. 300 = D/E 3.0x
        if dte is not None and dte > 300:
            flags.append(_flag_entry(
                "HIGH_DEBT", 0.90,
                f"yfinance debtToEquity={dte/100:.1f}x",
                f"D/E {dte/100:.1f}x > 3x threshold"
            ))

        cash = info.get("totalCash") or 0
        fcf = info.get("freeCashflow") or 0
        if fcf < 0 and cash > 0:
            months_runway = (cash / abs(fcf)) * 12
            if months_runway < 12:
                flags.append(_flag_entry(
                    "GOING_CONCERN", 0.85,
                    f"yfinance cash={cash/1e9:.1f}B, FCF={fcf/1e9:.1f}B/yr",
                    f"Only {months_runway:.0f} months cash runway"
                ))

        shares_issued = info.get("sharesOutstanding") or 0
        float_shares = info.get("floatShares") or shares_issued
        if shares_issued and float_shares and shares_issued > 0:
            dilution = (shares_issued - float_shares) / shares_issued if shares_issued > float_shares else 0
            # simpler: check if sharesPercentInsidersOwnership drastically changed — use implicit heuristic
            # yfinance doesn't give us YoY shares, skip RECENT_DILUTION here

        revenue_by_geo = info.get("revenueGrowth")  # no direct China revenue in yfinance basic info
        # Use country + business description as heuristic
        country = info.get("country", "")
        long_biz = (info.get("longBusinessSummary") or "").lower()
        if "china" in long_biz and any(k in long_biz for k in ["revenue", "sales", "market"]):
            flags.append(_flag_entry(
                "CHINA_EXPOSURE", 0.60,
                "yfinance business summary mentions China revenue/sales",
                "Verify: >30% China revenue exposure to tariff/ban risk"
            ))

    except Exception:
        pass  # don't block if yfinance is down

    return flags


def _evaluate_sec_edgar(symbol: str) -> list[dict]:
    """
    Check SEC EDGAR for recent 8-K / NT 10-K / NT 10-Q filings that indicate
    ACCOUNTING_RISK or DELISTING_RISK. Uses the free EDGAR full-text search API.
    """
    flags: list[dict] = []
    try:
        r = requests.get(
            f"https://efts.sec.gov/LATEST/search-index?q=%22{symbol}%22&forms=8-K,NT+10-K,NT+10-Q&dateRange=custom&startdt=2024-01-01",
            timeout=8,
            headers={"User-Agent": "theta-lab-mcp flags-engine@theta-lab (research only)"},
        )
        if r.status_code != 200:
            return flags

        data = r.json()
        hits = data.get("hits", {}).get("hits", [])

        accounting_keywords = [
            "auditor resigned", "auditor withdrawal", "restatement",
            "material weakness", "internal control", "going concern",
            "non-reliance", "10-k withdrawal",
        ]
        delisting_keywords = [
            "nasdaq", "nyse", "listing requirements", "delisting", "non-compliance"
        ]

        for hit in hits[:20]:
            src = hit.get("_source", {})
            form = src.get("form_type", "")
            period = src.get("period_of_report", "")
            entities = src.get("entity_name", "").upper()

            if symbol.upper() not in entities:
                continue

            display_names = src.get("display_names", "")
            file_date = src.get("file_date", "")

            # NT 10-K / NT 10-Q = late filing = potential accounting issue
            if form in ("NT 10-K", "NT 10-Q"):
                flags.append(_flag_entry(
                    "ACCOUNTING_RISK", 0.70,
                    f"SEC EDGAR: {form} late filing filed {file_date}",
                    f"Late {form} filing — potential accounting issues"
                ))

            # 8-K with accounting keywords in description
            desc = (src.get("description") or src.get("display_names") or "").lower()
            if any(k in desc for k in accounting_keywords):
                flags.append(_flag_entry(
                    "ACCOUNTING_RISK", 0.80,
                    f"SEC EDGAR 8-K: {src.get('description','')[:80]} filed {file_date}",
                    "8-K mentions accounting issue, auditor change, or restatement"
                ))
            if any(k in desc for k in delisting_keywords):
                flags.append(_flag_entry(
                    "DELISTING_RISK", 0.75,
                    f"SEC EDGAR 8-K mentions listing/compliance: {src.get('description','')[:80]}",
                    "8-K references Nasdaq/NYSE compliance or delisting risk"
                ))

    except Exception:
        pass

    # Deduplicate — keep highest confidence per flag
    best: dict[str, dict] = {}
    for f in flags:
        key = f["flag"]
        if key not in best or f["confidence"] > best[key]["confidence"]:
            best[key] = f
    return list(best.values())


def _evaluate_yfinance_news(symbol: str) -> list[dict]:
    """
    Check yfinance recent news headlines for event-driven red flags.
    Low confidence — used to CONFIRM or PROMPT human review, not auto-block.
    """
    flags: list[dict] = []
    try:
        ticker = yf.Ticker(symbol)
        news_items = ticker.news or []

        accounting_kw = ["sec investigation", "doj probe", "fraud", "accounting", "restatement",
                         "auditor", "material weakness", "going concern", "bankruptcy", "chapter 11"]
        delisting_kw = ["delisting", "nasdaq non-compliance", "nyse non-compliance", "compliance notice"]
        regulatory_kw = ["antitrust", "ftc", "doj lawsuit", "class action", "regulatory probe",
                         "congressional hearing", "tariff", "export ban"]

        for item in news_items[:15]:
            title = (item.get("title") or "").lower()
            pub_date = item.get("providerPublishTime", 0)

            # Only look at news from last 90 days
            if pub_date:
                age_days = (_utcnow().timestamp() - pub_date) / 86400
                if age_days > 90:
                    continue

            if any(k in title for k in accounting_kw):
                flags.append(_flag_entry(
                    "ACCOUNTING_RISK", 0.55,
                    f"yfinance news: '{item.get('title','')[:80]}'",
                    "Recent news headline suggests accounting or legal issues — verify"
                ))
            if any(k in title for k in delisting_kw):
                flags.append(_flag_entry(
                    "DELISTING_RISK", 0.55,
                    f"yfinance news: '{item.get('title','')[:80]}'",
                    "Recent news headline mentions delisting risk — verify"
                ))
            if any(k in title for k in regulatory_kw):
                flags.append(_flag_entry(
                    "REGULATORY_RISK", 0.50,
                    f"yfinance news: '{item.get('title','')[:80]}'",
                    "Recent news headline mentions regulatory risk — verify"
                ))

    except Exception:
        pass

    # Deduplicate
    best: dict[str, dict] = {}
    for f in flags:
        key = f["flag"]
        if key not in best or f["confidence"] > best[key]["confidence"]:
            best[key] = f
    return list(best.values())


# ─── Main entry point ─────────────────────────────────────────────────────────

def check_flags_live(symbol: str, seed_flags: list[str] | None = None) -> dict:
    """
    Evaluate flags for a symbol. Uses cache with TTL-based refresh.

    seed_flags: bootstrap flags from screener_universe — planted on first run,
                expire per FLAG_TTL_DAYS and are then re-evaluated dynamically.

    Returns:
        {
          "hard_blocks": [{"flag", "confidence", "source", "notes", "expires_at"}, ...],
          "warnings":    [...],
          "stale_flags_refreshed": [flag_name, ...],  # flags that were re-evaluated this call
          "evaluated_at": ISO string,
        }
    """
    symbol = symbol.upper()
    cache = _load_cache()
    symbol_cache = cache.get(symbol, {"flags": []})
    existing: list[dict] = symbol_cache.get("flags", [])

    # Separate into fresh and stale
    fresh = [f for f in existing if not _is_stale(f)]
    stale = [f for f in existing if _is_stale(f)]
    stale_names = [f["flag"] for f in stale]
    refreshed_flags: list[str] = []

    # ── Seed: plant flags from screener_universe if not in cache at all ──
    if seed_flags:
        known_flags = {f["flag"] for f in fresh + stale}
        for sf in seed_flags:
            if sf not in known_flags:
                fresh.append(_flag_entry(
                    sf, 0.80,
                    "screener_universe seed (human research — will expire and re-evaluate)",
                    ""
                ))

    # ── PERMANENT_EXIT: never auto-clear, but refresh its TTL each call ──
    pe_fresh = [f for f in fresh if f["flag"] == "PERMANENT_EXIT"]
    pe_stale = [f for f in stale if f["flag"] == "PERMANENT_EXIT"]
    if pe_stale:
        # Just re-plant with full TTL — PERMANENT_EXIT is only cleared by explicit update_flag call
        for pf in pe_stale:
            new_entry = _flag_entry("PERMANENT_EXIT", pf["confidence"], pf["source"], pf.get("notes", ""))
            fresh.append(new_entry)
            stale = [f for f in stale if f["flag"] != "PERMANENT_EXIT"]
        refreshed_flags.append("PERMANENT_EXIT")

    # ── Re-evaluate structural flags (THIN_MARGINS, HIGH_DEBT, LOW_MOAT, GOING_CONCERN) ──
    structural = {"THIN_MARGINS", "HIGH_DEBT", "LOW_MOAT", "GOING_CONCERN", "CHINA_EXPOSURE"}
    stale_structural = [f["flag"] for f in stale if f["flag"] in structural]
    if stale_structural:
        yf_flags = _evaluate_yfinance(symbol)
        yf_flag_keys = {f["flag"] for f in yf_flags}
        # Remove stale structural flags from working set, replace with fresh evals
        fresh = [f for f in fresh if f["flag"] not in stale_structural]
        fresh.extend(yf_flags)
        refreshed_flags.extend(stale_structural)
        # Structural flags that were stale but yfinance now shows clean → they're gone (not re-added)

    # ── Re-evaluate event-driven flags (ACCOUNTING_RISK, DELISTING_RISK, REGULATORY_RISK) ──
    event_driven = {"ACCOUNTING_RISK", "DELISTING_RISK", "REGULATORY_RISK"}
    stale_event = [f["flag"] for f in stale if f["flag"] in event_driven]
    if stale_event:
        sec_flags = _evaluate_sec_edgar(symbol)
        news_flags = _evaluate_yfinance_news(symbol)
        # For event-driven: take highest confidence result per flag across sources
        combined: dict[str, dict] = {}
        for f in sec_flags + news_flags:
            key = f["flag"]
            if key not in combined or f["confidence"] > combined[key]["confidence"]:
                combined[key] = f
        # Remove stale event-driven entries, add fresh ones
        fresh = [f for f in fresh if f["flag"] not in stale_event]
        fresh.extend(combined.values())
        refreshed_flags.extend(stale_event)
        # Note: if SEC EDGAR and news find nothing → the flag is cleared (resolved)

    # ── Always re-evaluate yfinance fundamentals if nothing stale (first run or after gap) ──
    fund_flag_keys = {"THIN_MARGINS", "HIGH_DEBT", "LOW_MOAT", "GOING_CONCERN", "CHINA_EXPOSURE"}
    if not existing:  # first time this symbol hits the engine
        yf_flags = _evaluate_yfinance(symbol)
        fresh.extend(yf_flags)

    # ── Save updated cache ──
    cache[symbol] = {
        "flags": fresh,
        "last_updated": _utcnow().isoformat(),
    }
    _save_cache(cache)

    hard_blocks = [f for f in fresh if f["flag"] in HARD_BLOCK_FLAG_KEYS and float(f.get("confidence", 0)) >= 0.60]
    warnings = [f for f in fresh if f not in hard_blocks]

    return {
        "hard_blocks": hard_blocks,
        "warnings": warnings,
        "stale_flags_refreshed": refreshed_flags,
        "evaluated_at": _utcnow().isoformat(),
    }


def update_flag(symbol: str, flag: str, action: str, reason: str, confidence: float = 0.90) -> dict:
    """
    Manually add or remove a flag (e.g., after web research confirms SMCI resolved accounting issues).

    action: 'add' | 'remove' | 'extend'  (extend resets TTL without changing confidence)
    """
    symbol = symbol.upper()
    cache = _load_cache()
    symbol_cache = cache.get(symbol, {"flags": []})
    flags = symbol_cache.get("flags", [])

    if action == "add":
        flags = [f for f in flags if f["flag"] != flag]  # remove any existing
        flags.append(_flag_entry(flag, confidence, f"manual override: {reason}", reason))
    elif action == "remove":
        flags = [f for f in flags if f["flag"] != flag]
        # Log the removal in a separate audit trail
        symbol_cache["removed_flags"] = symbol_cache.get("removed_flags", [])
        symbol_cache["removed_flags"].append({
            "flag": flag,
            "removed_at": _utcnow().isoformat(),
            "reason": reason,
        })
    elif action == "extend":
        for f in flags:
            if f["flag"] == flag:
                ttl = FLAG_TTL_DAYS.get(flag, 30)
                f["expires_at"] = (_utcnow() + timedelta(days=ttl)).isoformat()
                f["notes"] = reason

    symbol_cache["flags"] = flags
    cache[symbol] = symbol_cache
    _save_cache(cache)

    return {"symbol": symbol, "flag": flag, "action": action, "reason": reason, "ok": True}


def get_flag_status(symbol: str) -> dict:
    """Return current cached flags for a symbol with freshness info."""
    symbol = symbol.upper()
    cache = _load_cache()
    symbol_cache = cache.get(symbol, {})
    flags = symbol_cache.get("flags", [])
    removed = symbol_cache.get("removed_flags", [])

    result = []
    for f in flags:
        stale = _is_stale(f)
        result.append({**f, "is_stale": stale})

    return {
        "symbol": symbol,
        "flags": result,
        "removed_flags": removed,
        "last_updated": symbol_cache.get("last_updated", "never"),
    }


def review_all_stale(universe_symbols: list[str]) -> dict:
    """
    Batch re-evaluation of all stale flags across the universe.
    Called by the weekly report scheduler and 'refresh_flags_cache' MCP tool.
    Returns summary of what changed.
    """
    summary = {"refreshed": [], "cleared": [], "new_flags": [], "errors": []}
    cache = _load_cache()

    for symbol in universe_symbols:
        try:
            symbol_cache = cache.get(symbol, {"flags": []})
            stale = [f for f in symbol_cache.get("flags", []) if _is_stale(f)]
            if not stale:
                continue
            # Get seed flags from screener_universe for this symbol
            try:
                from reports.screener_universe import QUALITY_FLAGS_BY_SYMBOL
                seeds = QUALITY_FLAGS_BY_SYMBOL.get(symbol.upper(), [])
            except ImportError:
                seeds = []

            before_flags = {f["flag"] for f in symbol_cache.get("flags", []) if not _is_stale(f)}
            result = check_flags_live(symbol, seed_flags=seeds)
            after_flags = {f["flag"] for f in result["hard_blocks"] + result["warnings"]}

            cleared = before_flags - after_flags
            new_flags = after_flags - before_flags

            if cleared:
                summary["cleared"].append({"symbol": symbol, "flags": list(cleared)})
            if new_flags:
                summary["new_flags"].append({"symbol": symbol, "flags": list(new_flags)})
            if result["stale_flags_refreshed"]:
                summary["refreshed"].append({"symbol": symbol, "flags": result["stale_flags_refreshed"]})
        except Exception as e:
            summary["errors"].append({"symbol": symbol, "error": str(e)})

    return summary
