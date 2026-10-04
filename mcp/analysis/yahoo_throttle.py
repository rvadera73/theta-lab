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
process, waits on one shared gate -- a true global budget, not another
local one. Import this module (for its side effect) BEFORE `import
yfinance` anywhere yfinance is used; the patch installs once per process
and is a no-op on any later import.

v2 (same day): the first version enforced strict one-at-a-time
serialization (a single min-interval timestamp, zero concurrency). Real
test: a full cold-cache dashboard refresh (~95 tickers x 3-4 distinct
yfinance calls each for price/metrics/yield/sector, plus the macro-risk
analysis's own market-wide symbol calls -- 400-600+ total HTTP calls) took
over 10 minutes and still hadn't finished, versus ~2-3 minutes before this
fix existed. Strict serialization was real protection but an unusable
regression -- the old per-module throttles at least let different
subsystems overlap in wall-clock time even while each paced itself
internally; forcing literally everything through one call-at-a-time gate
lost all of that overlap.

Replaced with a bounded CONCURRENCY POOL (_MAX_CONCURRENT=3 simultaneous
in-flight calls, cross-process, via N lock-file "slots") plus a shorter
minimum spacing between call starts (_MIN_INTERVAL_SECONDS=0.15, down
from 0.35 -- concurrency now does part of the smoothing work the stricter
interval did alone before). This keeps real protection against the kind
of uncoordinated flooding that caused the original rate-limit lockout
(no more than 3 requests in flight to Yahoo at once, from any process)
while recovering most of the lost wall-clock time versus strict
serialization. A slot-acquire timeout (120s) means a genuinely stuck
request can never block the rest of the system forever -- it just
proceeds unthrottled as a last resort rather than hanging.

Usage: `import yahoo_throttle  # noqa: F401` as the first import, before
`import yfinance as yf`, in any file that calls yfinance.
"""
import os
import sys
import time
import fcntl

_MIN_INTERVAL_SECONDS = 0.15
_MAX_CONCURRENT = 3
_SLOT_ACQUIRE_TIMEOUT_SECONDS = 120


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
_PACING_LOCK_FILE = os.path.join(_DATA_DIR, ".yahoo_rate_limiter.pacing.lock")
_SLOT_FILES = [os.path.join(_DATA_DIR, f".yahoo_rate_limiter.slot{i}.lock") for i in range(_MAX_CONCURRENT)]


def _pace() -> None:
    """Enforces a short minimum gap between call STARTS, cross-process --
    cheap, brief (never held across the real network call), just smooths
    bursts. The concurrency pool below does the heavier lifting."""
    try:
        with open(_PACING_LOCK_FILE, "a+") as lockf:
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
        pass


def _acquire_slot():
    """Blocks (briefly polling) until one of _MAX_CONCURRENT cross-process
    concurrency slots is free, and returns the open file handle holding
    that slot's lock -- caller must pass it to _release_slot when the real
    call finishes. Gives up after _SLOT_ACQUIRE_TIMEOUT_SECONDS and returns
    None (the caller proceeds unthrottled) rather than risk hanging the
    whole system over a lock that never frees."""
    deadline = time.time() + _SLOT_ACQUIRE_TIMEOUT_SECONDS
    while time.time() < deadline:
        for path in _SLOT_FILES:
            try:
                fd = open(path, "a+")
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd
            except OSError:
                try:
                    fd.close()
                except Exception:
                    pass
                continue
        time.sleep(0.05)
    return None


def _release_slot(fd) -> None:
    if fd is None:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass
    try:
        fd.close()
    except OSError:
        pass


def throttle() -> None:
    """Back-compat entry point (older call sites may still call this
    directly) -- just the pacing half; the concurrency pool is applied in
    the patched YfData.get wrapper below, around the actual network call."""
    _pace()


def _install() -> None:
    if getattr(sys.modules[__name__], "_installed", False):
        return
    try:
        import yfinance.data as _yf_data
    except ImportError:
        return

    _original_get = _yf_data.YfData.get

    def _throttled_get(self, *args, **kwargs):
        _pace()
        slot = _acquire_slot()
        try:
            return _original_get(self, *args, **kwargs)
        finally:
            _release_slot(slot)

    _yf_data.YfData.get = _throttled_get
    sys.modules[__name__]._installed = True


_install()
