"""Temporary lock-out after repeated wrong passwords.

Two counters, both in memory (fine for one server process; see SECURITY_AUDIT.md):
  * per (email, IP): LOGIN_MAX_FAILURES wrong passwords -> that IP is locked out for
    LOGIN_LOCKOUT_MINUTES for that account. A stranger cannot lock the real owner out,
    because the real owner comes from a different IP.
  * per email, all IPs together: 4x the limit -> the account is locked for everybody
    for a while. This stops a botnet that rotates IPs, at the price of a temporary
    nuisance lock-out for the owner.
Unknown emails are counted exactly like known ones, so the lock-out does not reveal
which accounts exist. The tables are size-capped so junk emails cannot fill memory.
"""
import threading
import time

from app.core.config import settings

_MAX_ENTRIES = 20_000
_GLOBAL_FACTOR = 4

_lock = threading.Lock()
_pair: dict[tuple[str, str], tuple[int, float]] = {}   # (email, ip) -> (failures, window_start)
_email: dict[str, tuple[int, float]] = {}              # email -> (failures, window_start)


def _window() -> float:
    return settings.LOGIN_LOCKOUT_MINUTES * 60


def _live(entry: tuple[int, float] | None, now: float) -> int:
    if not entry:
        return 0
    count, started = entry
    return count if now - started <= _window() else 0


def _evict(table: dict, now: float) -> None:
    if len(table) < _MAX_ENTRIES:
        return
    for key in [k for k, v in table.items() if now - v[1] > _window()]:
        table.pop(key, None)
    while len(table) >= _MAX_ENTRIES:  # still full: drop the oldest
        table.pop(next(iter(table)))


def seconds_locked(email: str, ip: str) -> int:
    """0 if the login may proceed, otherwise how many seconds remain locked."""
    now = time.time()
    with _lock:
        pair = _pair.get((email, ip))
        glob = _email.get(email)
        blocked = (
            _live(pair, now) >= settings.LOGIN_MAX_FAILURES
            or _live(glob, now) >= settings.LOGIN_MAX_FAILURES * _GLOBAL_FACTOR
        )
        if not blocked:
            return 0
        starts = [e[1] for e in (pair, glob) if e and _live(e, now)]
        return max(1, int(_window() - (now - min(starts))))


def record_failure(email: str, ip: str) -> None:
    now = time.time()
    with _lock:
        for table, key in ((_pair, (email, ip)), (_email, email)):
            _evict(table, now)
            count, started = table.get(key, (0, now))
            if now - started > _window():
                count, started = 0, now
            table[key] = (count + 1, started)


def record_success(email: str, ip: str) -> None:
    with _lock:
        _pair.pop((email, ip), None)


def reset_all() -> None:
    with _lock:
        _pair.clear()
        _email.clear()
