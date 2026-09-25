"""File-drop detection (docs/DASHBOARD_PLAN.md Phase E, built 2026-09-25):
polls data/positions/ and data/statements/ for new/changed files every 2
minutes and triggers an immediate cache.refresh_all() the moment one shows
up, instead of waiting up to 30 minutes for the next scheduled interval --
the trader's own stated need ("this should be done after each transaction
files upload happens").

Polling, not inotify/watchdog -- deliberately. Filesystem-change-event
libraries are unreliable across the WSL <-> Windows <-> Docker bind-mount
chain this project runs on (a write on the Windows side doesn't always
generate a clean inotify event inside the Linux container); checking
mtimes on a short interval is slower by at most that interval but actually
works in this real environment.

Also runs the Quarterly Direction "review due" check on the same
cadence -- see quarterly_review_check.py. That doc needs real judgment to
rewrite (a live job can't do that), so this never touches its content;
it only flags, via a real Action Tracker item, that a human+AI review is
warranted.
"""
import os
import glob

from .services import DATA_ROOT
from . import cache
from . import quarterly_review_check

WATCHED_GLOBS = [
    os.path.join(DATA_ROOT, "data", "positions", "*"),
    os.path.join(DATA_ROOT, "data", "statements", "*"),
]

_last_seen_mtime = None


def _max_watched_mtime():
    latest = 0.0
    for pattern in WATCHED_GLOBS:
        for path in glob.glob(pattern):
            if os.path.isfile(path):
                latest = max(latest, os.path.getmtime(path))
    return latest


def check_for_new_files_and_refresh():
    """Called on a short interval (see main.py). Cheap on the common case
    (no new file) -- just an mtime scan, no live price/report computation
    unless something actually changed.
    """
    global _last_seen_mtime
    current_max = _max_watched_mtime()
    if _last_seen_mtime is None:
        _last_seen_mtime = current_max  # first run: baseline, don't refresh
        return
    if current_max > _last_seen_mtime:
        _last_seen_mtime = current_max
        cache.refresh_all()
        quarterly_review_check.check_and_flag_if_due()
