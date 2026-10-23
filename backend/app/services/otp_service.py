"""Admin one-time codes.

Codes are 6 digits, valid for 5 minutes and compared in constant time.
Failed attempts are counted in memory (per email); after MAX_ATTEMPTS the code
is destroyed and a new one must be requested. (The OTP columns are only 10
chars wide, so we store the short-lived code as-is rather than a hash - a
6-digit code can be brute-forced offline from any hash anyway.)
"""
import hmac
import secrets
import threading
import time
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.timeutil import as_utc, utcnow
from app.models.user import User

OTP_TTL_MINUTES = 5
MAX_ATTEMPTS = 5

_lock = threading.Lock()
_failures: dict[str, tuple[int, float]] = {}  # email -> (count, first_failure_ts)


def generate_otp() -> str:
    """Secure 6-digit code (100000-999999)."""
    return f"{secrets.randbelow(900000) + 100000}"


def save_otp(db: Session, user: User) -> str:
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expiry = utcnow() + timedelta(minutes=OTP_TTL_MINUTES)
    db.commit()
    reset_failures(user.email)
    return otp


def clear_otp(db: Session, user: User) -> None:
    user.otp_code = None
    user.otp_expiry = None
    db.commit()
    reset_failures(user.email)


def otp_matches(user: User, otp_code: str) -> bool:
    """True only if a code exists, has not expired and matches."""
    if not user.otp_code or not user.otp_expiry:
        return False
    if utcnow() > as_utc(user.otp_expiry):
        return False
    return hmac.compare_digest(user.otp_code.encode(), (otp_code or "").strip().encode())


def register_failure(email: str) -> int:
    """Record a wrong code; returns the number of failures in the last TTL window."""
    now = time.time()
    with _lock:
        count, first = _failures.get(email, (0, now))
        if now - first > OTP_TTL_MINUTES * 60:
            count, first = 0, now
        count += 1
        _failures[email] = (count, first)
        return count


def reset_failures(email: str) -> None:
    with _lock:
        _failures.pop(email, None)
