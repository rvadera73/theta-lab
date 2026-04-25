# Schwab API Setup Guide

The MCP server pulls live data from Schwab via open-stocks-mcp.
This requires a Schwab Developer account and API credentials (approval takes 2-5 business days).

## Step 1: Register at Schwab Developer Portal

1. Go to: https://developer.schwab.com
2. Sign in with your regular Schwab credentials
3. Click "Create App"
4. Fill in:
   - **App Name:** theta-lab
   - **Callback URL:** https://127.0.0.1:8182/
   - **Products:** Select "Accounts and Trading Production"
5. Submit — approval email arrives in 2-5 business days

## Step 2: Get Your Credentials

After approval, in the developer portal:
- Copy **API Key** (this is SCHWAB_API_KEY)
- Copy **App Secret** (this is SCHWAB_APP_SECRET)

## Step 3: Create .env File

```bash
cp /home/rahulvadera/projects/theta-lab/.env.example /home/rahulvadera/projects/theta-lab/.env
```

Edit `.env` and fill in your values:
```
SCHWAB_API_KEY=your_api_key_here
SCHWAB_APP_SECRET=your_app_secret_here
SCHWAB_CALLBACK_URL=https://127.0.0.1:8182/
SCHWAB_TOKEN_PATH=~/.tokens/schwab_token.json
ENABLED_BROKERS=schwab
```

## Step 4: Get Account Hashes

Run this once to get your account hashes:
```bash
cd /home/rahulvadera/projects/theta-lab
source .venv/bin/activate  # if using venv
python3 -c "
from open_stocks_mcp.tools.schwab_account_tools import get_schwab_account_numbers
result = get_schwab_account_numbers()
print(result)
"
```

Look for the hash values in the output — they correspond to your account numbers ending in 232 and 275.
Add them to your `.env`:
```
SCHWAB_ACCOUNT_A_HASH=hash_for_account_232
SCHWAB_ACCOUNT_B_HASH=hash_for_account_275
```

## Step 5: First OAuth Login

The first run triggers OAuth authentication:
```bash
python3 mcp/server.py
```

A browser window opens → log in with Schwab credentials → authorize → token saved to `~/.tokens/schwab_token.json`.
Subsequent runs use the saved token (auto-refreshed).

## Step 6: Configure Claude Desktop MCP

Add to `~/.claude/claude_desktop_config.json` (or equivalent):
```json
{
  "mcpServers": {
    "theta-lab": {
      "command": "python3",
      "args": ["/home/rahulvadera/projects/theta-lab/mcp/server.py"],
      "env": {
        "SCHWAB_API_KEY": "your_key",
        "SCHWAB_APP_SECRET": "your_secret",
        "SCHWAB_ACCOUNT_A_HASH": "hash_232",
        "SCHWAB_ACCOUNT_B_HASH": "hash_275",
        "ENABLED_BROKERS": "schwab"
      }
    }
  }
}
```

## Step 7: Test

In Claude, try:
```
generate_weekly_action_report
```

If credentials work, you get live positions and a full Top-5 report.
If not, you get the setup instructions message.

## Interim: Manual Mode

Until API is approved, generate reports using brokerage statements:
```bash
python3 analysis/persona_analyzer.py --file data/statements/your_export.csv
```
