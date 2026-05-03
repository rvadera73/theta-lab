"""Bootstrap credential loading for the Theta-Lab MCP server."""

import json
import os
from pathlib import Path


def load_credentials() -> list[str]:
    """
    Load credentials from ~/.claude.json mcpServers.theta-lab.env into os.environ.

    Returns a list of keys injected into the environment. Safe to call multiple
    times — existing environment variables are preserved.
    """
    if os.environ.get("SCHWAB_API_KEY"):
        return []

    claude_json = Path.home() / ".claude.json"
    if not claude_json.exists():
        return []

    try:
        data = json.loads(claude_json.read_text())
        env_block = data.get("mcpServers", {}).get("theta-lab", {}).get("env", {})
        injected: list[str] = []
        for key, value in env_block.items():
            if value and not os.environ.get(key):
                os.environ[key] = str(value)
                injected.append(key)
        return injected
    except Exception:
        return []
