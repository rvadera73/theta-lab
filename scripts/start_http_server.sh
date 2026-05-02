#!/usr/bin/env bash
# Starts theta-lab MCP in HTTP/SSE mode, injecting Schwab credentials.
#
# Credential loading order (first source that provides SCHWAB_API_KEY wins):
#   1. Already set in environment (e.g. passed by systemd EnvironmentFile)
#   2. ~/.claude.json  mcpServers.theta-lab.env  (primary — managed by Claude CLI)
#   3. <project>/.env  (fallback for manual/dev runs)
#
# Usage: ./scripts/start_http_server.sh [port] [token]
#   port   - TCP port to bind (default: 8765)
#   token  - Bearer token for auth (default: value of THETA_LAB_TOKEN env var, or none)

set -euo pipefail

PORT=${1:-8765}
TOKEN=${2:-${THETA_LAB_TOKEN:-""}}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── 1. Free the port if anything is already holding it ───────────────────────
if lsof -ti tcp:"$PORT" &>/dev/null; then
    echo "[theta-lab] Port $PORT in use — freeing it before starting ..."
    fuser -k "${PORT}/tcp" 2>/dev/null || true
    sleep 2
fi

# ── 2. Load credentials (skip if already in environment) ─────────────────────
if [ -z "${SCHWAB_API_KEY:-}" ]; then
    CLAUDE_JSON="$HOME/.claude.json"
    ENV_FILE="$PROJECT_DIR/.env"

    if [ -f "$CLAUDE_JSON" ]; then
        echo "[theta-lab] Loading credentials from ~/.claude.json ..."
        eval "$(python3 -c "
import json, os, sys
try:
    cfg = json.load(open(os.path.expanduser('~/.claude.json')))
    env = cfg.get('mcpServers', {}).get('theta-lab', {}).get('env', {})
    if env:
        for k, v in env.items():
            print(f'export {k}={repr(v)}')
    else:
        sys.stderr.write('[theta-lab] WARNING: theta-lab entry missing in ~/.claude.json\n')
except Exception as e:
    sys.stderr.write(f'[theta-lab] WARNING: could not read ~/.claude.json: {e}\n')
")"
    fi

    # Fallback: .env file (covers dev runs and CI)
    if [ -z "${SCHWAB_API_KEY:-}" ] && [ -f "$ENV_FILE" ]; then
        echo "[theta-lab] Falling back to $ENV_FILE ..."
        set -o allexport
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set +o allexport
    fi
else
    echo "[theta-lab] Credentials already in environment — skipping load."
fi

# ── 3. Validate required credentials ─────────────────────────────────────────
MISSING=()
for VAR in SCHWAB_API_KEY SCHWAB_APP_SECRET SCHWAB_ACCOUNT_A_HASH SCHWAB_ACCOUNT_B_HASH; do
    [ -z "${!VAR:-}" ] && MISSING+=("$VAR")
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "[theta-lab] ⚠️  MISSING credentials: ${MISSING[*]}"
    echo "[theta-lab]    Add them to ~/.claude.json (mcpServers.theta-lab.env) or .env"
    echo "[theta-lab]    Server will start but live Schwab tools will be unavailable."
else
    echo "[theta-lab] ✅ All Schwab credentials loaded (API_KEY, APP_SECRET, A_HASH, B_HASH)"
fi

# ── 4. Start the server ───────────────────────────────────────────────────────
export THETA_LAB_TOKEN="$TOKEN"

echo "[theta-lab] Starting HTTP server on port $PORT ..."
if [ -n "$TOKEN" ]; then
    echo "[theta-lab] Bearer auth enabled"
else
    echo "[theta-lab] WARNING: No bearer token set — server is open. Set THETA_LAB_TOKEN=<secret> to secure."
fi

cd "$PROJECT_DIR"
exec python3 mcp/server.py --transport http --port "$PORT"
