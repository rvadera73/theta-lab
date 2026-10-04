"""Global, cross-process rate limiter for every yfinance call in this
project -- not a per-module cache, a real shared budget.

Confirmed live 2026-10-04: enhanced_metrics.py's batch cache (10-min TTL,
0.35s inter-ticker pacing) and premium_yield.py's daily cache each work
correctly WITHIN their own batch call, but neither coordinates with the
other, with sector_analysis.py (found with zero throttling of its own,
same day -- a wall of "Too Many Requests" warnings in one run), or across
the several SEPARATE OS PROCESSES that all independently hit Yahoo on a
busy day: the dashboard container, the MCP server process, and any ad-hoc
verification script. Yahoo's real rate limit is IP/session-level and
cumulative across all of them -- four well-behaved individual throttles
still collectively blew past it.

Fixes this by patching the single HTTP choke point every yfinance call
funnels through (yfinance.data.YfData.get, confirmed via direct traceback
inspection the same day) so EVERY call from EVERY module, in EVERY
process, waits on one shared, file-lock-based minimum-interval gate --
a true global budget, not another local one. Import this module (for its
side effect) BEFORE `import yfinance` anywhere yfinance is used; the patch
installs once per process and is a no-op on any later import.

Usage: `import yahoo_throttle  # noqa: F401` as the first import, before
`import yfinance as yf`, in any file that calls yfinance.
"""
import os
import sys
import time
import fcntl

_MIN_INTERVAL_SECONDS = 0.35  # same pacing already chosen for enhanced_metrics.py


def _find_data_dir() -> str:
    """Self-locating: walks up from this file looking for a sibling "data"
    directory next to "mcp" -- works identically on the host
    (/home/rahulvadera/projects/theta-lab) and inside the dashboard
    container (/app), since both preserve the same relative project
    structure, without hardcoding either absolute root."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(5):
        candidate = os.path.join(root, "data")
        if os.path.isdir(candidate):
            return candidate
        root = os.path.dirname(root)
    # Fall back to a directory next to this file if no project "data" dir
    # is found (e.g. this module copied somewhere unexpected) -- never
    # crash the caller over where to put a lock file.
    return here


_DATA_DIR = _find_data_dir()
_STATE_FILE = os.path.join(_DATA_DIR, ".yahoo_rate_limiter_state")
_LOCK_FILE = os.path.join(_DATA_DIR, ".yahoo_rate_limiter.lock")


def throttle() -> None:
    """Blocks the calling process until at least _MIN_INTERVAL_SECONDS have
    elapsed since ANY process last made a yfinance call, via a file lock +
    shared last-call timestamp -- real cross-process mutual exclusion, not
    an in-memory lock that only coordinates within one process."""
    try:
        with open(_LOCK_FILE, "a+") as lockf:
            fcntl.flock(lockf, fcntl.LOCK_EX)
            try:
                last = 0.0
                if os.path.exists(_STATE_FILE):
                    try:
                        with open(_STATE_FILE) as f:
                            last = float(f.read().strip() or 0)
                    except (ValueError, OSError):
                        last = 0.0
                now = time.time()
                wait = _MIN_INTERVAL_SECONDS - (now - last)
                if wait > 0:
                    time.sleep(wait)
                with open(_STATE_FILE, "w") as f:
                    f.write(repr(time.time()))
            finally:
                fcntl.flock(lockf, fcntl.LOCK_UN)
    except OSError:
        # Never let a lock-file problem (permissions, read-only FS, etc.)
        # take down a real data fetch -- this is a courtesy throttle, not
        # a correctness requirement.
        pass


def _install() -> None:
    if getattr(sys.modules[__name__], "_installed", False):
        return
    try:
        import yfinance.data as _yf_data
    except ImportError:
        return

    _original_get = _yf_data.YfData.get

    def _throttled_get(self, *args, **kwargs):
        throttle()
        return _original_get(self, *args, **kwargs)

    _yf_data.YfData.get = _throttled_get
    sys.modules[__name__]._installed = True


_install()
