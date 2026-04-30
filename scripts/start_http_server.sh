#!/usr/bin/env bash
# Starts theta-lab MCP in HTTP/SSE mode, injecting Schwab credentials from ~/.claude.json
# Usage: ./scripts/start_http_server.sh [port] [token]
#   port   - TCP port to bind (default: 8765)
#   token  - Bearer token for auth (default: value of THETA_LAB_TOKEN env var, or none)

set -euo pipefail

PORT=${1:-8765}
TOKEN=${2:-${THETA_LAB_TOKEN:-""}}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "[theta-lab] Loading credentials from ~/.claude.json ..."

# Extract all env vars for the theta-lab MCP server from ~/.claude.json
eval "$(python3 -c "
import json, os, sys
cfg = json.load(open(os.path.expanduser('~/.claude.json')))
env = cfg.get('mcpServers', {}).get('theta-lab', {}).get('env', {})
if not env:
    sys.stderr.write('ERROR: theta-lab server not found in ~/.claude.json\n')
    sys.exit(1)
for k, v in env.items():
    print(f'export {k}={repr(v)}')
")"

export THETA_LAB_TOKEN="$TOKEN"

echo "[theta-lab] Starting HTTP server on port $PORT ..."
if [ -n "$TOKEN" ]; then
    echo "[theta-lab] Bearer auth enabled"
else
    echo "[theta-lab] WARNING: No bearer token set — server is open. Set THETA_LAB_TOKEN=<secret> to secure."
fi

cd "$PROJECT_DIR"
exec python3 mcp/server.py --transport http --port "$PORT"
