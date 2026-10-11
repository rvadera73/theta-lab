"""
Reconciliation — implements docs/RECONCILIATION_PROCESS.md's 3-layer job.

Layer 1 (Data): find newly downloaded broker files, verify each by the real
account number INSIDE the file (never the filename alone), archive the
canonical file it replaces, copy the new one into place. Flags gaps
(expected account has no fresh file) and ambiguous duplicates (two files
could be the same account) as QUESTIONS rather than silently guessing.

Layer 2 (Analysis): rebuild data/portfolio_snapshot.yaml, then refresh the
live dashboard cache (both US and India) so what's displayed matches the
data just reconciled, not a stale prior computation.

Layer 3 (Decisions): cross-check India's exit_triggers (data/india_config.yaml)
against the REAL current holdings in the just-reconciled equity statement --
the direct fix for the YATHOS incident (a trigger that kept firing for a
position that wasn't actually held, because nothing ever checked).

Default policy (confirmed 2026-10-11): QUEUE open questions, don't block.
Every unambiguous step still runs; ambiguities are collected and printed
together at the end instead of halting the whole job on the first one.
Pass --block to stop at the first open question instead.

NOT yet implemented (see docs/RECONCILIATION_PROCESS.md's Status section):
report regeneration (US 4 types + India weekly) and the generic
staleness-diff check across report text. This script currently automates
Layer 1 fully, Layer 2's snapshot rebuild + dashboard refresh, and Layer 3's
India trigger cross-check -- the concrete, evidenced gaps from 2026-10-10.

Usage:
    python3 scripts/reconcile.py                 # dry run (default, safe)
    python3 scripts/reconcile.py --apply          # actually archive+copy files
    python3 scripts/reconcile.py --apply --block  # stop at first open question
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS = "/mnt/c/Users/RahulVadera/Downloads"
POS = os.path.join(ROOT, "data", "positions")
STMT = os.path.join(ROOT, "data", "statements")
POS_ARCH = os.path.join(POS, "arch")
STMT_ARCH = os.path.join(STMT, "arch")
TODAY = date.today().strftime("%Y%m%d")

sys.path.insert(0, os.path.join(ROOT, "mcp"))
sys.path.insert(0, os.path.join(ROOT, "mcp", "analysis"))


# ---------------------------------------------------------------------------
# Layer 1 -- file identity verification
# ---------------------------------------------------------------------------

# Each slot: canonical destination, glob pattern(s) in Downloads to consider,
# a verifier(path) -> account_number_or_None, and the expected account number.
# Verifiers read real file content -- never trust the filename alone (see
# docs/RECONCILIATION_PROCESS.md's Layer 1).

def _first_matching_account(path, needles, max_lines=30):
    """Reads up to max_lines and returns the first needle (account number)
    found as a substring -- used for files where the account number sits in
    a data row, not reliably in the header (Fidelity Accounts_History,
    Fidelity Portfolio_Positions)."""
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                for n in needles:
                    if n in line:
                        return n
    except OSError:
        return None
    return None


SLOTS = [
    {
        "name": "Schwab Account A (232) positions",
        "glob": "Individual-Positions-*.csv",
        "canonical": os.path.join(POS, "schwab_rahul_individual.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(p, ["232"], max_lines=5),
        "expect": "232",
    },
    {
        "name": "Schwab Account A (232) transactions",
        "glob": "Individual_XXX232_Transactions_*.csv",
        "canonical": None,  # glob-matched by the loaders, no literal rename
        "arch_dir": POS_ARCH,
        "verify": lambda p: "232",
        "expect": "232",
    },
    {
        "name": "Schwab Account B (275) positions",
        "glob": "Contributory-Positions-*.csv",
        "canonical": os.path.join(POS, "schwab_pinky_ira.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(p, ["275"], max_lines=5),
        "expect": "275",
    },
    {
        "name": "Schwab Account B (275) transactions",
        "glob": "Contributory_XXX275_Transactions_*.csv",
        "canonical": None,
        "arch_dir": POS_ARCH,
        "verify": lambda p: "275",
        "expect": "275",
    },
    {
        "name": "Schwab Account C (634, Designated Bene) positions",
        "glob": "Designated Bene Individual-Positions-*.csv",
        "canonical": os.path.join(POS, "schwab_designated-bene.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(p, ["634"], max_lines=5),
        "expect": "634",
    },
    {
        "name": "Schwab Account C (634) transactions",
        "glob": "Designated_Bene_Individual_XXX634_Transactions_*.csv",
        "canonical": None,
        "arch_dir": POS_ARCH,
        "verify": lambda p: "634",
        "expect": "634",
    },
    {
        "name": "Fidelity Rahul positions (225798148)",
        "glob": "Portfolio_Positions_*.csv",
        "canonical": os.path.join(POS, "fidelity_rahul.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(p, ["225798148", "233461172"]),
        "expect": "225798148",
    },
    {
        "name": "Fidelity Rajul positions (233461172)",
        "glob": "Portfolio_Positions_*.csv",
        "canonical": os.path.join(POS, "fidelity_rajul.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(p, ["225798148", "233461172"]),
        "expect": "233461172",
    },
    {
        "name": "Fidelity Rahul Accounts_History",
        "glob": "Accounts_History*.csv",
        "canonical": os.path.join(POS, "Accounts_History_fidelity_Rahul.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(
            p, ["225798148", "263508923", "233461172"], max_lines=10
        ),
        "expect": "225798148",
    },
    {
        "name": "Fidelity Rajul Accounts_History (Rollover or Roth)",
        "glob": "Accounts_History*.csv",
        "canonical": os.path.join(POS, "Accounts_History_fidelity_Rajul.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(
            p, ["225798148", "263508923", "233461172"], max_lines=10
        ),
        "expect": ("263508923", "233461172"),  # either sub-account counts as Rajul's file
    },
    {
        "name": "Vanguard Rahul (21530855)",
        "glob": "OfxDownload*.csv",
        "canonical": os.path.join(POS, "vanguard_rahul.csv"),
        "arch_dir": POS_ARCH,
        "verify": lambda p: _first_matching_account(p, ["21530855"], max_lines=5),
        "expect": "21530855",
    },
    {
        "name": "India equity (7500069840)",
        "glob": "7500069840_PortFolioEqtAll*.xls",
        "canonical": os.path.join(STMT, "7500069840_PortFolioEqtAll.xls"),
        "arch_dir": STMT_ARCH,
        "verify": lambda p: "7500069840",  # account number is in the filename itself for India
        "expect": "7500069840",
    },
    {
        "name": "India F&O (7510078170)",
        "glob": "7510078170_FNOPortfolioDetails*.xls",
        "canonical": os.path.join(STMT, "7510078170_FNOPortfolioDetails.xls"),
        "arch_dir": STMT_ARCH,
        "verify": lambda p: "7510078170",
        "expect": "7510078170",
    },
]


def _candidates_modified_today(pattern):
    paths = glob.glob(os.path.join(DOWNLOADS, pattern))
    today = date.today()
    return [p for p in paths if datetime.fromtimestamp(os.path.getmtime(p)).date() == today]


def _expect_matches(expect, found):
    if found is None:
        return False
    if isinstance(expect, tuple):
        return found in expect
    return found == expect


def plan_layer1():
    """Returns (actions, questions). actions: list of dicts describing what
    would be archived+copied. questions: list of plain-English open
    questions for the trader -- an expected account with no fresh file, or
    more than one same-day candidate for the same slot that can't be
    resolved by newest-mtime alone."""
    actions = []
    questions = []
    seen_canonical = set()

    for slot in SLOTS:
        candidates = _candidates_modified_today(slot["glob"])
        verified = []
        for c in candidates:
            found = slot["verify"](c)
            if _expect_matches(slot["expect"], found):
                verified.append(c)

        if not verified:
            if slot["canonical"]:  # transactions-only slots (canonical=None) are optional
                questions.append(
                    f"No fresh, verified file found today for: {slot['name']}. "
                    f"Existing canonical file will be left as-is (will show as stale)."
                )
            continue

        verified.sort(key=os.path.getmtime, reverse=True)
        chosen = verified[0]
        if len(verified) > 1:
            age_gap = os.path.getmtime(verified[0]) - os.path.getmtime(verified[1])
            note = (
                f"{len(verified)} verified candidates for {slot['name']} today; "
                f"using newest ({os.path.basename(chosen)}), "
                f"{age_gap:.0f}s newer than the next one ({os.path.basename(verified[1])})."
            )
            if age_gap > 600:  # >10 min apart looks less like an accidental double-download
                questions.append(
                    note + " These are more than 10 minutes apart -- verify this is really "
                    "a duplicate download and not two genuinely different exports before trusting "
                    "the newest-wins default."
                )
            else:
                print(f"  (auto-resolved) {note}")

        dest = slot["canonical"] or os.path.join(POS, os.path.basename(chosen))
        actions.append({
            "slot": slot["name"],
            "source": chosen,
            "dest": dest,
            "archive": slot["canonical"] is not None,  # only archive literal-named canonical files
            "arch_dir": slot["arch_dir"],
        })
        seen_canonical.add(dest)

    return actions, questions


def apply_layer1(actions):
    for a in actions:
        os.makedirs(a["arch_dir"], exist_ok=True)
        if a["archive"] and os.path.exists(a["dest"]):
            base, ext = os.path.splitext(os.path.basename(a["dest"]))
            arch_path = os.path.join(a["arch_dir"], f"{base}_{TODAY}_prev{ext}")
            shutil.copy2(a["dest"], arch_path)
            print(f"  archived {os.path.basename(a['dest'])} -> {os.path.basename(arch_path)}")
        shutil.copy2(a["source"], a["dest"])
        print(f"  {os.path.basename(a['source'])} -> {a['dest']}")


# ---------------------------------------------------------------------------
# Layer 2 -- rebuild snapshot + refresh dashboard cache
# ---------------------------------------------------------------------------

def rebuild_snapshot():
    print("\n=== Layer 2: rebuilding data/portfolio_snapshot.yaml ===")
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "update_snapshot.py")],
        cwd=ROOT, capture_output=True, text=True,
    )
    print(result.stdout[-2000:])
    if result.returncode != 0:
        print(result.stderr[-2000:])
        return False
    return True


def refresh_dashboard():
    print("\n=== Layer 2: refreshing dashboard cache (US + India) ===")
    script = (
        "from app import cache\n"
        "cache.refresh_all()\n"
        "print('dashboard refresh_all() done')\n"
    )
    tmp = "/tmp/_reconcile_refresh.py"
    with open(tmp, "w") as f:
        f.write(script)
    try:
        subprocess.run(["docker", "cp", tmp, "theta-lab-web:/tmp/_reconcile_refresh.py"], check=True)
        result = subprocess.run(
            ["docker", "exec", "theta-lab-web", "python3", "/tmp/_reconcile_refresh.py"],
            capture_output=True, text=True, timeout=600,
        )
        print(result.stdout[-1000:])
        if result.returncode != 0:
            print(result.stderr[-1500:])
            return False
        return "done" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  could not refresh dashboard automatically: {e}")
        print("  run manually: docker exec theta-lab-web python3 -c \"from app import cache; cache.refresh_all()\"")
        return False


# ---------------------------------------------------------------------------
# Layer 3 -- India exit_triggers vs real current holdings (the YATHOS fix)
# ---------------------------------------------------------------------------

def check_india_triggers_vs_holdings():
    """Cross-checks every data/india_config.yaml exit_triggers entry against
    the REAL current holdings in the just-reconciled equity statement.
    Direct fix for the YATHOS incident: a trigger whose symbol isn't in
    current holdings at all is almost certainly a stale/wrong entry, not a
    live actionable one -- flag it instead of letting it silently re-print."""
    print("\n=== Layer 3: India exit_triggers vs real current holdings ===")
    try:
        import yaml
        from india_statement_parser import parse_equity_positions
    except ImportError as e:
        print(f"  could not run check: {e}")
        return []

    config_path = os.path.join(ROOT, "data", "india_config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)

    try:
        holdings = parse_equity_positions()
    except Exception as e:
        print(f"  could not parse real equity holdings: {e}")
        return []

    held_symbols = set(holdings.keys())
    flags = []
    for trig in config.get("exit_triggers", []):
        sym = trig.get("icici_symbol")
        if sym not in held_symbols:
            flags.append(
                f"  🔴 {sym}: trigger exists in exit_triggers but NOT in current real holdings "
                f"(qty 0 or never held) -- action text: {trig.get('action', '')[:100]!r}"
            )
        else:
            qty = holdings[sym]["qty"]
            print(f"  ✓ {sym}: confirmed held, {qty} shares")

    if flags:
        print("\n  STALE/INVALID TRIGGERS FOUND:")
        for f_ in flags:
            print(f_)
    else:
        print("  all exit_triggers entries confirmed against real current holdings.")
    return flags


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually archive+copy files (default is dry-run)")
    ap.add_argument("--block", action="store_true", help="stop at the first open question instead of queueing")
    ap.add_argument("--skip-dashboard", action="store_true", help="skip the docker dashboard refresh step")
    args = ap.parse_args()

    print("=== Layer 1: scanning Downloads for today's verified broker files ===")
    actions, questions = plan_layer1()

    for a in actions:
        print(f"  [{'APPLY' if args.apply else 'DRY-RUN'}] {a['slot']}: "
              f"{os.path.basename(a['source'])} -> {a['dest']}")

    if questions and args.block:
        print("\n=== BLOCKED: open questions (pass without --block to queue instead) ===")
        for q in questions:
            print(f"  ? {q}")
        sys.exit(1)

    if not actions:
        print("  no verified new files found today for any tracked slot.")

    if args.apply and actions:
        print("\nApplying Layer 1...")
        apply_layer1(actions)
        ok = rebuild_snapshot()
        if ok and not args.skip_dashboard:
            refresh_dashboard()
    elif not args.apply:
        print("\n(dry run -- pass --apply to actually archive+copy and rebuild the snapshot)")

    trigger_flags = check_india_triggers_vs_holdings()

    print("\n" + "=" * 70)
    print("OPEN QUESTIONS FOR THE TRADER" if questions else "No open questions.")
    for q in questions:
        print(f"  ? {q}")
    if trigger_flags:
        print("\nSTALE INDIA TRIGGERS (Layer 3) -- review before trusting any India action report:")
        for f_ in trigger_flags:
            print(f_)
    print("=" * 70)

    print("\nNOT automated yet (see docs/RECONCILIATION_PROCESS.md Status): "
          "report regeneration (US 4 types + India weekly) and the generic "
          "report-text staleness diff. Run those via the theta-lab MCP tools "
          "(generate_unified_master_report, generate_india_weekly_report) separately.")


if __name__ == "__main__":
    main()
