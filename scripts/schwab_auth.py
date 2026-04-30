"""
One-time Schwab OAuth setup for WSL2.

Uses client_from_manual_flow — no local server needed, no browser/WSL2 port issues.
Run once per Schwab login. Token auto-refreshes for 7 days.

Usage:
    SCHWAB_API_KEY="..." SCHWAB_APP_SECRET="..." python3 scripts/schwab_auth.py
"""

import os
import json
import sys
from pathlib import Path

API_KEY      = os.getenv("SCHWAB_API_KEY", "")
APP_SECRET   = os.getenv("SCHWAB_APP_SECRET", "")
CALLBACK_URL = "https://127.0.0.1:8182/"

TOKEN_DIR = Path.home() / ".tokens"
TOKEN_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNT_TOKENS = {
    "1": ("Rahul (232 + any linked accounts)", TOKEN_DIR / "schwab_token.json"),
    "2": ("Pinky IRA (275)",                   TOKEN_DIR / "schwab_token_b.json"),
    "3": ("Third account",                      TOKEN_DIR / "schwab_token_c.json"),
}


def main():
    if not API_KEY or not APP_SECRET:
        print("ERROR: set SCHWAB_API_KEY and SCHWAB_APP_SECRET before running.")
        sys.exit(1)

    from schwab import auth

    print("=" * 60)
    print("Which Schwab login are you authenticating?")
    print()
    for key, (label, path) in ACCOUNT_TOKENS.items():
        print(f"  {key}) {label}")
        print(f"     token → {path}")
    print()
    choice = input("Enter 1, 2, or 3: ").strip()
    if choice not in ACCOUNT_TOKENS:
        print("Invalid choice.")
        sys.exit(1)

    label, token_path = ACCOUNT_TOKENS[choice]
    print(f"\nAuthenticating: {label}")
    print(f"Token will be saved to: {token_path}\n")

    print("=" * 60)
    print("IMPORTANT: You have ~90 seconds after the URL appears to")
    print("complete login and paste the redirect URL back here.")
    print("Have your Schwab credentials ready before continuing.")
    print("=" * 60)
    input("\nPress Enter when ready...")

    client = auth.client_from_manual_flow(
        api_key=API_KEY,
        app_secret=APP_SECRET,
        callback_url=CALLBACK_URL,
        token_path=str(token_path),
    )

    print(f"\nToken saved: {token_path}")
    print()

    print("Fetching account numbers and hashes...")
    try:
        resp = client.get_account_numbers()
        accounts = resp.json()
        print(f"\nFound {len(accounts)} account(s) on this login:\n")
        for acct in accounts:
            number = acct.get("accountNumber", "???")
            hash_val = acct.get("hashValue", "???")
            tail = number[-4:] if len(number) >= 4 else number
            note = ""
            if tail == "232": note = "  ← SCHWAB_ACCOUNT_A_HASH"
            elif tail == "275": note = "  ← SCHWAB_ACCOUNT_B_HASH"
            print(f"  Account ...{tail}  hash: {hash_val}{note}")
        print()
        print("Copy the hashes above into ~/.claude/settings.json")
        print("under the theta-lab mcpServer env block, then restart Claude Code.")
    except Exception as e:
        print(f"Auth succeeded but could not fetch accounts: {e}")
        print(f"Token is saved. Run again or check the token file at {token_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
