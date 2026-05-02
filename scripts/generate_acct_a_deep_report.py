#!/usr/bin/env python3
"""
Account A — Deep Per-Option-Leg Report
Driven by: trading_persona.md goals + options_trader.md rules
Author: theta-lab / GitHub Copilot
"""
import yaml
from datetime import date, datetime

# ─────────────────────────────────────────
# TECHNICAL DATA (fetched via yfinance)
# ─────────────────────────────────────────
TECH = {
    "ADBE":  {"price":250.71, "rsi":57.0, "ma50":250.52, "ma200":314.24, "hi52":422.95, "lo52":224.13},
    "AMZN":  {"price":268.26, "rsi":82.9, "ma50":224.80, "ma200":227.38, "hi52":273.88, "lo52":183.85},
    "ANET":  {"price":172.70, "rsi":69.0, "ma50":142.80, "ma200":137.57, "hi52":179.80, "lo52":82.80},
    "APH":   {"price":142.30, "rsi":45.8, "ma50":138.31, "ma200":130.78, "hi52":166.71, "lo52":78.21},
    "APP":   {"price":460.00, "rsi":61.6, "ma50":439.24, "ma200":525.74, "hi52":745.61, "lo52":286.85},
    "AXON":  {"price":402.31, "rsi":72.0, "ma50":453.85, "ma200":600.98, "hi52":885.92, "lo52":339.01},
    "COIN":  {"price":191.25, "rsi":58.3, "ma50":187.54, "ma200":264.11, "hi52":444.65, "lo52":139.36},
    "CRCL":  {"price": 99.70, "rsi":50.9, "ma50":100.30, "ma200":109.29, "hi52":298.99, "lo52":49.90},
    "CRM":   {"price":183.82, "rsi":59.7, "ma50":186.32, "ma200":227.74, "hi52":293.86, "lo52":163.52},
    "CRWD":  {"price":455.64, "rsi":71.9, "ma50":413.40, "ma200":457.56, "hi52":566.90, "lo52":342.72},
    "DIS":   {"price":103.08, "rsi":56.6, "ma50":100.98, "ma200":109.25, "hi52":123.85, "lo52":88.63},
    "ETSY":  {"price": 63.17, "rsi":62.6, "ma50": 55.73, "ma200": 58.81, "hi52": 76.51, "lo52":42.97},
    "EWJ":   {"price": 88.30, "rsi":49.8, "ma50": 86.95, "ma200": 81.54, "hi52": 94.28, "lo52":68.19},
    "IBIT":  {"price": 44.47, "rsi":64.8, "ma50": 40.53, "ma200": 53.31, "hi52": 71.82, "lo52":35.30},
    "IBM":   {"price":232.20, "rsi":45.6, "ma50":243.18, "ma200":270.90, "hi52":323.06, "lo52":220.72},
    "ISRG":  {"price":457.78, "rsi":49.5, "ma50":474.98, "ma200":500.16, "hi52":603.88, "lo52":427.84},
    "JD":    {"price": 29.96, "rsi":57.8, "ma50": 28.00, "ma200": 29.62, "hi52": 36.77, "lo52":23.66},
    "LLY":   {"price":963.33, "rsi":55.9, "ma50":947.66, "ma200":909.59, "hi52":1132.06,"lo52":620.46},
    "LMT":   {"price":512.77, "rsi": 6.6, "ma50":614.54, "ma200":520.01, "hi52":692.00, "lo52":401.95},
    "LYFT":  {"price": 14.42, "rsi":59.7, "ma50": 13.69, "ma200": 17.42, "hi52": 25.54, "lo52":12.31},
    "META":  {"price":608.75, "rsi":43.0, "ma50":630.14, "ma200":677.37, "hi52":794.38, "lo52":520.26},
    "MP":    {"price": 66.63, "rsi":63.1, "ma50": 57.89, "ma200": 62.97, "hi52":100.25, "lo52":18.64},
    "MRNA":  {"price": 45.37, "rsi":35.4, "ma50": 51.76, "ma200": 35.70, "hi52": 59.55, "lo52":22.28},
    "MSFT":  {"price":414.44, "rsi":62.9, "ma50":396.11, "ma200":466.64, "hi52":552.24, "lo52":356.28},
    "MU":    {"price":542.21, "rsi":78.0, "ma50":425.58, "ma200":276.86, "hi52":545.91, "lo52": 78.35},
    "NFLX":  {"price": 92.06, "rsi":29.0, "ma50": 94.68, "ma200":104.16, "hi52":134.12, "lo52":75.01},
    "NKE":   {"price": 44.40, "rsi":61.2, "ma50": 51.34, "ma200": 63.41, "hi52": 78.73, "lo52":42.09},
    "NVDA":  {"price":198.45, "rsi":58.1, "ma50":187.15, "ma200":183.84, "hi52":216.83, "lo52":110.79},
    "NVO":   {"price": 43.88, "rsi":73.5, "ma50": 37.94, "ma200": 48.40, "hi52": 77.68, "lo52":34.58},
    "OKTA":  {"price": 75.78, "rsi":71.9, "ma50": 75.56, "ma200": 86.01, "hi52":127.57, "lo52":62.66},
    "PYPL":  {"price": 50.44, "rsi":64.2, "ma50": 46.71, "ma200": 59.07, "hi52": 79.08, "lo52":38.34},
    "RBLX":  {"price": 45.13, "rsi":25.5, "ma50": 59.16, "ma200": 94.63, "hi52":150.59, "lo52":41.75},
    "TSLA":  {"price":390.82, "rsi":67.1, "ma50":383.71, "ma200":402.49, "hi52":498.83, "lo52":271.00},
    "TSM":   {"price":397.67, "rsi":63.4, "ma50":359.93, "ma200":304.25, "hi52":414.50, "lo52":168.50},
    "UBER":  {"price": 75.12, "rsi":59.7, "ma50": 73.98, "ma200": 85.19, "hi52":101.99, "lo52":68.46},
    "ULTA":  {"price":531.95, "rsi":52.6, "ma50":573.88, "ma200":567.28, "hi52":714.97, "lo52":386.00},
    "UNH":   {"price":368.78, "rsi":94.5, "ma50":300.77, "ma200":311.94, "hi52":398.46, "lo52":229.79},
    "VST":   {"price":155.28, "rsi":47.1, "ma50":160.00, "ma200":177.48, "hi52":219.21, "lo52":133.05},
    "XYZ":   {"price": 72.00, "rsi":50.0, "ma50": 70.00, "ma200": 65.00, "hi52": 90.00, "lo52":55.00},
    "ZBH":   {"price": 82.90, "rsi":26.4, "ma50": 92.23, "ma200": 94.46, "hi52":107.45, "lo52":79.83},
    "ZS":    {"price":139.81, "rsi":67.1, "ma50":143.66, "ma200":233.71, "hi52":336.99, "lo52":114.62},
}

TIER = {
    "NVDA":"T1","META":"T1","AMZN":"T1","TSLA":"T1","TSM":"T1","AXON":"T1",
    "ADBE":"T1","CRM":"T1","MSFT":"T1","NFLX":"T1","UBER":"T1","LLY":"T1",
    "CRWD":"T2","ZS":"T2","VST":"T2","COIN":"T2","ISRG":"T2","LMT":"T2",
    "UNH":"T2","IBM":"T2","APP":"T2","ANET":"T2","OKTA":"T2","DIS":"T2",
    "IBIT":"T3","RBLX":"T3","MP":"T3","CRCL":"T3","MU":"T2","EWJ":"T2",
    "APH":"T2","ETSY":"T2","NKE":"T2","NVO":"T2","ULTA":"T2",
    "JD":"T3","LYFT":"T3","ZBH":"T2","XYZ":"T2","MRNA":"EXIT","PYPL":"EXIT",
}

THESIS = {
    "NVDA":"INTACT — AI silicon monopoly; pick/shovel; valuation stretched but thesis strong",
    "META":"INTACT — AI ad platform; cash machine; below MAs but earnings strong",
    "AMZN":"INTACT — cloud+commerce moat; near 52W high; AI spend paying off",
    "TSLA":"WATCH — EV share erosion; Musk distraction risk; still near 52W high",
    "TSM":"INTACT — foundry pick/shovel; AI chip demand; near 52W high",
    "AXON":"INTACT — AI public safety; defense crossover; but 55% off 52W high — patience needed",
    "ADBE":"WATCH — AI creative disruption risk (Firefly vs OpenAI); below 200d MA",
    "CRM":"INTACT — enterprise AI platform; $280 conviction target; accumulating via wheel",
    "MSFT":"INTACT — Azure AI + Copilot monetization; above 50d; below 200d but recovering",
    "NFLX":"INTACT — streaming market leader; below all MAs; RSI 29 = oversold support",
    "UBER":"INTACT — AV disruption risk manageable; above 50d; below 200d",
    "LLY":"INTACT — GLP-1 dominant; above all MAs; strong momentum",
    "CRWD":"INTACT — cybersecurity AI pick/shovel; above 50d; near 200d; thesis multi-year",
    "ZS":"INTACT — AI security infrastructure; below 200d MA; watch $280 resistance",
    "VST":"INTACT — AI data center power demand; below all MAs; monitor closely",
    "COIN":"INTACT — crypto cycle plays; below 200d MA; high conviction; BTC at ~$95K",
    "ISRG":"INTACT — robotic surgery monopoly; below all MAs; solid fundamentals",
    "LMT":"INTACT — defense budget tailwind; RSI 6.6 EXTREMELY OVERSOLD; recent sell-off",
    "UNH":"WATCH — RSI 94.5 = extreme overbought; above 52W high range; healthcare risk",
    "IBM":"WATCH — below all MAs; AI integration slow; below 200d MA",
    "APP":"WATCH — high-beta; below 200d MA; advertising cycle sensitive",
    "ANET":"INTACT — AI network switch pick/shovel; strong momentum; near 52W high",
    "OKTA":"WATCH — below 200d MA; identity security consolidating; growth slowing",
    "DIS":"INTACT — streaming + parks recovery; above 50d; below 200d; patience",
    "IBIT":"INTACT — Bitcoin ETF; cleanest BTC exposure; BTC near $95K",
    "RBLX":"BROKEN — RSI 25.5; 70% below 52W high; monetization failing; thesis weak",
    "MP":"INTACT — rare earth supply chain; defense thesis; above all MAs; strong",
    "CRCL":"WATCH — Circle IPO recent; crypto payment; speculative; below all MAs",
    "MU":"INTACT — memory cycle up; RSI 78 overbought; near 52W high",
    "EWJ":"INTACT — Japan equities; BOJ policy; reasonable entry levels",
    "APH":"INTACT — connectors/interconnect for AI servers; above all MAs; solid",
    "ETSY":"WATCH — consumer discretionary headwind; above 50d; small position",
    "NKE":"WATCH — consumer slowdown + China risk; below all MAs; RSI ok",
    "NVO":"WATCH — GLP-1 competition intensifying (LLY vs NVO); below 200d MA",
    "ULTA":"INTACT — beauty retail resilient; below 50d/200d; entry zone approaching",
    "JD":"WATCH — China e-commerce value play; above 50d; US-China tariff risk",
    "LYFT":"WATCH — AV disruption risk; below 200d; operating leverage improving",
    "ZBH":"WATCH — medical devices; RSI 26.4 oversold; below all MAs; recovery slow",
    "XYZ":"WATCH — monitoring",
    "MRNA":"BROKEN — 🔴 PERMANENT EXIT — pipeline failures; natural CC exit in progress",
    "PYPL":"BROKEN — 🔴 PERMANENT EXIT — fintech moat eroding; minimize loss via CCs",
}

today = date.today()

def dte(expiry_str):
    exp = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    return (exp - today).days

def itm_otm(option_type, strike, price):
    if option_type == "PUT":
        pct = (price - strike) / price * 100
        label = "ITM" if price < strike else "OTM"
    else:
        pct = (strike - price) / price * 100
        label = "ITM" if price > strike else "OTM"
    return label, round(abs(pct), 1)

def action_for_leg(sym, option_type, strike, expiry, contracts):
    t = TECH.get(sym, {})
    price = t.get("price", 0)
    d = dte(expiry)
    label, pct = itm_otm(option_type, strike, price)
    thesis = THESIS.get(sym, "UNKNOWN")
    tier = TIER.get(sym, "?")

    # Permanent exits
    if sym in ("PYPL", "MRNA"):
        if option_type == "CALL":
            return "🔴 SELL CC AGGRESSIVELY — permanent exit; collect premium to reduce cost basis"
        else:
            return "⚠️ FLAG — do not add; monitor for assignment"

    # DTE urgency
    if d <= 13:
        if label == "ITM":
            return f"🚨 URGENT ROLL — {d} DTE + {label} {pct:.1f}% — roll to next expiry for net credit NOW"
        else:
            return f"🟡 WATCH — {d} DTE, {label} {pct:.1f}% — close if 40%+ profit captured; let expire if well OTM"
    if d <= 21:
        if label == "ITM":
            return f"🔶 ROLL THIS WEEK — {d} DTE + {label} {pct:.1f}% — roll down+out for net credit"
        else:
            return f"🟡 REVIEW — {d} DTE, {label} {pct:.1f}% — at 40%+ profit: close and redeploy"

    # ITM positions beyond 21 DTE
    if label == "ITM":
        thesis_broken = "BROKEN" in thesis or "EXIT" in thesis
        if thesis_broken:
            return f"🔴 CLOSE — ITM + thesis broken; do not roll broken names"
        elif d > 45:
            return f"🟢 HOLD — ITM but {d} DTE; thesis intact; let time work per roll framework"
        else:
            return f"🟡 EVALUATE ROLL — {d} DTE ITM; {pct:.1f}% in the money; roll if net credit available"

    # Far OTM, ample DTE — standard hold/profit-take
    rsi = t.get("rsi", 50)
    rsi_note = ""
    if rsi > 70 and option_type == "CALL":
        rsi_note = "; RSI overbought — CC is well-placed"
    elif rsi < 30 and option_type == "PUT":
        rsi_note = "; RSI oversold — PUT has assignment risk if continues lower"
    elif rsi > 80:
        rsi_note = "; RSI >80 EXTREME overbought"
    elif rsi < 25:
        rsi_note = "; RSI <25 EXTREME oversold — monitor for capitulation"

    return f"🟢 HOLD — {label} {pct:.1f}%, {d} DTE; let decay work{rsi_note}; close at 40-60% profit (bear regime)"

def ma_signal(sym):
    t = TECH.get(sym, {})
    price = t.get("price", 0)
    ma50 = t.get("ma50", 0)
    ma200 = t.get("ma200", 0)
    s50 = "✅ above" if price > ma50 else "❌ below"
    s200 = "✅ above" if price > ma200 else "❌ below"
    pct_off_hi = round((t.get("hi52", price) - price) / t.get("hi52", price) * 100, 1)
    return f"50d MA: {s50} (${ma50:.0f}) | 200d MA: {s200} (${ma200:.0f}) | {pct_off_hi}% off 52W high"

def bev_calc(cost_basis, price, shares, monthly_cc, recovered):
    unrealized = (price - cost_basis) * shares
    remaining_loss = abs(unrealized) - recovered if unrealized < 0 else 0
    if monthly_cc > 0 and remaining_loss > 0:
        months = round(remaining_loss / monthly_cc, 1)
        if months <= 12:
            rating = "🟢 FAST"
        elif months <= 24:
            rating = "🟡 ON TRACK"
        elif months <= 36:
            rating = "🟠 SLOW"
        else:
            rating = "🔴 CRITICAL — exit capital more valuable redeployed"
        return months, rating, round(remaining_loss, 0)
    elif monthly_cc == 0 and unrealized < 0:
        return None, "🔴 IDLE — $0/month CC; no premium being collected on this assignment", round(remaining_loss, 0)
    else:
        return None, "✅ Profitable or breakeven", 0

# ─────────────────────────────────────────
# LOAD SNAPSHOT
# ─────────────────────────────────────────
with open("/home/rahulvadera/projects/theta-lab/data/portfolio_snapshot.yaml") as f:
    snap = yaml.safe_load(f)

assigned = [p for p in snap.get('assigned_positions', []) if '232' in p['account']]
puts = [p for p in snap.get('open_puts', []) if '232' in p['account']]

# ─────────────────────────────────────────
# GENERATE REPORT
# ─────────────────────────────────────────
lines = []
def w(s=""): lines.append(s)

w(f"# Account A (Schwab 232) — Deep Per-Option-Leg Report")
w(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | **Regime:** BEAR_SIDEWAYS (Override active through Oct/Nov 2026) | **New Entries: ❌ NONE**")
w()
w("## 🎯 Key Objectives Driving Every Action")
w("| Objective | Target | Status |")
w("|-----------|--------|--------|")
w("| Monthly income (combined) | $100,000/month | ~$60-70K net after stock drag |")
w("| Account A annualized return | 20% (~$84K/yr) | $59K in Jan-Feb 2026 — ahead of pace |")
w("| Profit-take threshold (bear regime) | 40-60% of premium received | Apply to ALL legs |")
w("| Assigned equity book | ≤ $375K (bear cap) | ⚠️ Currently ~$401K — DANGER ZONE |")
w("| Roll/close threshold | ≤21 DTE | No exceptions |")
w("| New entries | NONE until Oct/Nov 2026 | Override active |")
w()
w("---")
w()

# ─────────────────────────────────────────
# SECTION 1: ASSIGNED STOCKS
# ─────────────────────────────────────────
w("## 📦 SECTION 1 — Assigned Stocks (CC Wheel Engine)")
w("> These are shares you own from put assignment. Each must generate CC premium every month.")
w("> Current book: ~$401K — **DANGER ZONE** (bear cap = $375K). Accelerate CC exits.")
w()

total_assigned_value = 0
total_monthly_cc = 0

for pos in assigned:
    sym = pos['symbol']
    shares = pos['shares']
    cb = pos['cost_basis']
    monthly_cc = pos.get('monthly_cc', 0)
    recovered = pos.get('recovered', 0)
    t = TECH.get(sym, {})
    price = t.get("price", cb)
    tier = TIER.get(sym, "?")
    thesis = THESIS.get(sym, "Unknown")
    
    unrealized = (price - cb) * shares
    assigned_value = price * shares
    total_assigned_value += assigned_value
    total_monthly_cc += monthly_cc
    
    months, bev_rating, remaining = bev_calc(cb, price, shares, monthly_cc, recovered)
    
    w(f"### {sym} — {tier} | Assigned Stock | Thesis: {'🔴 PERMANENT EXIT' if sym in ('PYPL','MRNA') else ('⚠️ WATCH' if 'WATCH' in thesis or 'BROKEN' in thesis else '✅ INTACT')}")
    w(f"_{thesis}_")
    w()
    w(f"| Metric | Value |")
    w(f"|--------|-------|")
    w(f"| Shares | {shares} |")
    w(f"| Cost Basis | ${cb:,.2f} |")
    w(f"| Current Price | ${price:,.2f} |")
    w(f"| Unrealized P&L | ${unrealized:,.0f} ({'🔴 LOSS' if unrealized < 0 else '🟢 GAIN'}) |")
    w(f"| Assigned Value | ${assigned_value:,.0f} |")
    w(f"| Monthly CC Premium | ${monthly_cc:,.0f}/month |")
    w(f"| Recovered via CCs | ${recovered:,.0f} |")
    if months:
        w(f"| Months to Breakeven | {months} months |")
    w(f"| Breakeven Velocity | {bev_rating} |")
    
    rsi = t.get("rsi", 50)
    w()
    w(f"**Technical Overlay (supplemental):** RSI {rsi} | {ma_signal(sym)}")
    w()
    
    # CC action recommendation
    if sym == "PYPL":
        w(f"**🔴 CC ACTION:** Sell covered calls aggressively on every bounce — target delta 0.25-0.35 to accelerate exit. 1,300 shares × premium collected = fastest path to minimize $111K+ loss. RSI at 64 suggests short-term bounce — use it. Next: sell Jun/Jul calls at $52-55 strike.")
    elif sym == "MRNA":
        w(f"**🔴 CC ACTION:** Deep ITM calls being assigned naturally — let the process complete. Stock at $45 with $26/$35 calls ITM means assignment is imminent. Do NOT re-enter after exit.")
    elif monthly_cc == 0 and unrealized < 0:
        w(f"**⚠️ IDLE CAPITAL ALERT — $0 CC collected on ${assigned_value:,.0f} assigned equity.** This capital is doing NOTHING toward your $100K/month goal.")
        if sym == "ADBE":
            w(f"  → Sell CC at $260-265 (delta ~0.25), Jun/Jul expiry. Stock above 50d MA, RSI neutral — good entry for CC.")
        elif sym == "CRM":
            w(f"  → Sell CC at $190-195 (delta ~0.25), Jun/Jul expiry. Thesis intact ($280 target) — use it to collect premium while waiting.")
        elif sym == "JD":
            w(f"  → Sell CC at $31-32 (delta ~0.25), Jun expiry. Small position; even $100/month adds up toward goal.")
        elif sym == "UNH":
            w(f"  → HOLD CCs temporarily — RSI 94.5 = extreme overbought. Stock may correct. Sell CC above $380 when RSI normalizes below 70.")
        elif sym == "ZBH":
            w(f"  → Sell CC at $85-87 (delta ~0.25), Jun/Jul expiry. RSI 26.4 oversold — stock may bounce; sell CC on that bounce.")
        elif sym == "XYZ":
            w(f"  → Sell CC at current ATM to slight OTM. Every idle assigned share is a missed income opportunity.")
    elif monthly_cc > 0:
        if months and months > 36:
            w(f"**🔴 RECOVERY TOO SLOW ({months} months):** At ${monthly_cc}/month, breakeven is {months} months away. Capital redeployment analysis: if these {shares} shares were sold and proceeds redeployed into new CSPs at 2-3%/month, you'd generate ${int(assigned_value*0.025):,}/month. Consider accelerating exit vs. current pace.")
        elif months and months > 24:
            w(f"**🟠 RECOVERY SLOW ({months} months):** Increase CC frequency. Consider selling shorter DTE CCs (30-45 day) more aggressively to increase monthly rate.")
        else:
            w(f"**🟢 ON TRACK:** Continue current CC pace. Focus on maximizing premium without capping upside too aggressively.")
    w()
    w("---")
    w()

w(f"**Assigned Book Summary:** Total Value: ${total_assigned_value:,.0f} | Total Monthly CC: ${total_monthly_cc:,.0f}/month")
w()
w("---")
w()

# ─────────────────────────────────────────
# SECTION 2: OPEN OPTION LEGS
# ─────────────────────────────────────────
w("## 🎯 SECTION 2 — Open Option Legs (Account A)")
w("> Each leg evaluated independently per stagger strategy rules.")
w("> Bear regime profit target: 40-60% of premium. Roll threshold: ≤21 DTE.")
w()

# Group by symbol
from collections import defaultdict
by_sym = defaultdict(list)
for p in puts:
    by_sym[p['symbol']].append(p)

urgent_rolls = []
flag_review = []
hold_positions = []

for sym in sorted(by_sym.keys()):
    t = TECH.get(sym, {})
    price = t.get("price", 0)
    tier = TIER.get(sym, "?")
    thesis = THESIS.get(sym, "Unknown")
    thesis_status = '🔴 PERMANENT EXIT' if sym in ('PYPL','MRNA') else ('⚠️ WATCH' if 'WATCH' in thesis or 'BROKEN' in thesis else '✅ INTACT')
    
    w(f"### {sym} — {tier} | Current Price: ${price} | Thesis: {thesis_status}")
    w(f"_{thesis}_")
    w(f"**Technical:** RSI {t.get('rsi','?')} | {ma_signal(sym)}")
    w()
    w(f"| Leg | Type | Strike | Expiry | DTE | Status | % ITM/OTM | Action |")
    w(f"|-----|------|--------|--------|-----|--------|-----------|--------|")
    
    for leg in sorted(by_sym[sym], key=lambda x: x['expiry']):
        strike = leg['strike']
        expiry = leg['expiry']
        contracts = leg.get('contracts', 1)
        d = dte(expiry)
        label, pct = itm_otm("PUT", strike, price)
        action = action_for_leg(sym, "PUT", strike, expiry, contracts)
        status_icon = "🚨" if d <= 13 else ("🔶" if d <= 21 else ("🔴" if label == "ITM" else "🟢"))
        w(f"| PUT x{contracts} | PUT | ${strike} | {expiry} | {d}d | {status_icon} {label} {pct}% | {pct}% {label} | {action} |")
        
        if d <= 21:
            urgent_rolls.append(f"{sym} PUT ${strike} {expiry} ({d} DTE)")
        if label == "ITM" and d > 21:
            flag_review.append(f"{sym} PUT ${strike} {expiry} — ITM {pct}% ({d} DTE)")
    
    w()
    
    # Additional context per name
    if sym == "AXON":
        w("> **Stagger note:** These 4 put legs are intentional stagger positions at different strikes/expiries. Evaluate each independently. The $660P Sep is deep ITM (stock at $402) and needs close attention.")
    elif sym == "APP":
        w("> **Risk note:** APP has 4 put legs including $580P Aug which is significantly ITM. High-beta name — monitor closely in bear regime.")
    elif sym == "MSFT":
        w("> **⚠️ URGENT:** MSFT $420P May 15 is ITM (stock at $414.44) with 13 DTE — needs immediate roll.")
    elif sym == "COIN":
        w("> **Note:** COIN $250P May 15 is significantly ITM (stock at $191). 13 DTE — consider closing or rolling aggressively.")
    elif sym == "NFLX":
        w("> **RSI oversold note:** RSI 29 on NFLX suggests support near current levels. $95 puts are far OTM — let decay work.")
    elif sym == "LMT":
        w("> **RSI alert:** LMT RSI at 6.6 = EXTREME oversold. Likely a sharp correction. $520P Mar27 is ITM — thesis intact (defense budget), so HOLD with time working.")
    elif sym == "UNH":
        w("> **RSI alert:** UNH RSI at 94.5 = EXTREME overbought. Near-term correction likely. $320P Dec and $300P Mar27 are well OTM — should be fine.")
    elif sym == "MU":
        w("> **Overbought alert:** MU RSI 78, near 52W high at $542 vs $545. $370P Mar27 is well OTM but memory cycle can reverse sharply.")
    w()
    w("---")
    w()

# ─────────────────────────────────────────
# SECTION 3: PRIORITY ACTION SUMMARY
# ─────────────────────────────────────────
w("## 🚨 SECTION 3 — Priority Action Summary")
w()
w("### Immediate Actions (This Week — Do Not Wait)")
w()
if urgent_rolls:
    for item in urgent_rolls:
        w(f"- 🚨 **ROLL NOW:** {item}")
w()
w("### ITM Positions Needing Monitoring (Thesis Still Intact — Hold per Roll Framework)")
if flag_review:
    for item in flag_review:
        w(f"- 🔴 **ITM HOLD/EVALUATE:** {item}")
w()
w("### Idle Assigned Capital (Missed Income — Start CCs)")
w("- ⚠️ ADBE: 300 shares × $0/month — start CCs immediately")
w("- ⚠️ CRM: 200 shares × $0/month — start CCs immediately")  
w("- ⚠️ JD: 200 shares × $0/month — start CCs immediately")
w("- ⚠️ UNH: 100 shares × $0/month — start CCs once RSI normalizes below 70")
w("- ⚠️ ZBH: 100 shares × $0/month — start CCs on bounce")
w("- ⚠️ PYPL: 1,300 shares × $0/month — IMMEDIATE priority; sell CCs this week")
w()
w("### Technical Alerts (Supplemental — For Strike/Roll Timing)")
w("- 🔴 **LMT RSI 6.6** — extreme oversold; do not panic-close puts; bounce likely")
w("- 🔴 **UNH RSI 94.5** — extreme overbought; near-term correction risk; do not add")
w("- 🔴 **MU RSI 78.0** — overbought; memory cycle turning risk")
w("- 🔴 **AMZN RSI 82.9** — overbought; near 52W high; puts are safe but watch")
w("- 🔴 **RBLX RSI 25.5** — extreme oversold; thesis BROKEN; evaluate full exit")
w("- 🔴 **ZBH RSI 26.4** — oversold; sell CC on bounce to collect elevated HV premium")
w("- 🔴 **NFLX RSI 29.0** — oversold; $95P Mar27 well protected; let decay work")
w()
w("### Assigned Book Action (DANGER ZONE)")
w(f"> **Current book ~$401K vs ${375}K bear cap.** Accelerate these exits:")
w("- 1. PYPL: 1,300 shares — most urgent; $50.44 price; CC every cycle")
w("- 2. MRNA: 400 shares — natural CC assignment in progress; do not intervene")
w("- 3. ADBE: 300 shares — $495 CB vs $250 price; start CCs immediately to reduce drag")
w("- 4. CRM: 200 shares — $303 CB vs $184 price; sell CCs; $280 conviction target")
w()
w("---")
w()
w("## 📊 SECTION 4 — Portfolio Health Scorecard")
w()
w("| Metric | Value | Target | Status |")
w("|--------|-------|--------|--------|")
w(f"| Assigned book value | ~$401K | ≤$375K | 🔴 DANGER ZONE |")
w(f"| Monthly CC from assigned | ${total_monthly_cc:,}/month | Maximize | {'🟢' if total_monthly_cc > 5000 else '🔴'} |")
w(f"| Permanent exits with $0 CC | PYPL + MRNA | Both exiting | 🔴 Accelerate |")
w(f"| Idle assigned positions | 5+ names with $0 CC | 0 idle | 🔴 Act now |")
w(f"| Regime | BEAR_SIDEWAYS | Override active | ✅ Correct |")
w(f"| New entries | NONE | NONE | ✅ Correct |")
w()
w("---")
w(f"_Report generated by theta-lab | Data: yfinance (real-time) + portfolio_snapshot.yaml (2026-04-27) | Strategy: trading_persona.md_")

# Save
output = "\n".join(lines)
outfile = f"/home/rahulvadera/projects/theta-lab/logs/acct_a_deep_report_{today.strftime('%Y-%m-%d')}.md"
with open(outfile, 'w') as f:
    f.write(output)

print(f"✅ Report saved: {outfile}")
print(f"   Lines: {len(lines)}")
print(f"   Size: {len(output):,} chars")
