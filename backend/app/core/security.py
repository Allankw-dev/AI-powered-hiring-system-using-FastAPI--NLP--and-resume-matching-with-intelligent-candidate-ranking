"""Password hashing and access tokens.

Passwords
  * New hashes use Argon2id (memory-hard, the current OWASP first choice).
  * Existing bcrypt hashes keep working. When a user with a bcrypt hash logs in
    successfully, the router re-hashes the password with Argon2id (see
    ``password_needs_rehash``), so the database upgrades itself over time.
  * Argon2 sees the whole password. (bcrypt silently ignores everything past
    72 bytes; that quirk is kept ONLY for verifying legacy bcrypt hashes.)

Tokens
  * PyJWT, HMAC only (algorithm is fixed by config, never read from the token).
  * Required claims: exp, iat, iss. Each token also carries a random ``jti`` and a
    ``pwv`` fingerprint of the password hash, so changing/resetting the password
    signs out every device that still holds an old token.
"""
import hashlib
import hmac
import re
import uuid
from datetime import timedelta

import bcrypt
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import settings
from app.core.timeutil import utcnow

TOKEN_ISSUER = "ai-hiring-platform"  # nosec B105
_LEEWAY_SECONDS = 10  # tolerated clock drift between servers

_ph = PasswordHasher()  # argon2-cffi defaults = RFC 9106 "low memory" profile (Argon2id)

# bcrypt only looks at the first 72 BYTES of a password (legacy hashes only).
_BCRYPT_MAX_BYTES = 72


def _bcrypt_prep(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        if hashed_password.startswith("$argon2"):
            return _ph.verify(hashed_password, plain_password)
        if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(_bcrypt_prep(plain_password), hashed_password.encode("utf-8"))
    except (VerificationError, InvalidHashError, ValueError):
        return False
    return False


def password_needs_rehash(hashed_password: str) -> bool:
    """True for legacy bcrypt hashes and for Argon2 hashes made with outdated parameters."""
    if not hashed_password.startswith("$argon2"):
        return True
    try:
        return _ph.check_needs_rehash(hashed_password)
    except InvalidHashError:
        return True


# A real hash used to burn the same CPU time when the email is unknown,
# so response time does not reveal which emails are registered.
DUMMY_PASSWORD_HASH = hash_password("not-a-real-password-for-timing-only")


def hash_token(token: str) -> str:
    """SHA-256 of a high-entropy token (reset links). Stored instead of the token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def password_fingerprint(password_hash: str) -> str:
    """Short, non-reversible tag of the current password hash (goes into the JWT as ``pwv``)."""
    return hashlib.sha256(("pwv:" + password_hash).encode("utf-8")).hexdigest()[:16]


# Passwords that pass the character rules but are in every cracking list.
_COMMON_PASSWORDS = {
    "password1", "password12", "password123", "password1!", "passw0rd", "p@ssw0rd", "p@ssword1",
    "qwerty123", "qwerty1234", "qwertyuiop1", "qwerty12345", "abc12345", "abcd1234", "abcd12345",
    "welcome1", "welcome123", "welcome12", "letmein123", "iloveyou1", "iloveyou123", "admin123",
    "admin1234", "administrator1", "changeme1", "changeme123", "monkey123", "dragon123", "football1",
    "football123", "baseball1", "superman1", "trustno1", "sunshine1", "princess1", "123456789a",
    "1q2w3e4r5t", "1qaz2wsx", "zaq12wsx", "kenya2020", "kenya2024", "kenya2025", "nairobi123",
}


def password_problems(password: str) -> list[str]:
    """Return a list of reasons a password is too weak (empty list = OK)."""
    problems = []
    if len(password) < 8:
        problems.append("at least 8 characters")
    if len(password) > 128:
        problems.append("at most 128 characters")
    if not re.search(r"[A-Z]", password):
        problems.append("one uppercase letter")
    if not re.search(r"[a-z]", password):
        problems.append("one lowercase letter")
    if not re.search(r"\d", password):
        problems.append("one number")
    if not problems and password.lower() in _COMMON_PASSWORDS:
        problems.append("to not be a commonly used password")
    return problems


def validate_password_strength(password: str) -> str:
    problems = password_problems(password)
    if problems:
        raise ValueError("Password needs " + ", ".join(problems))
    return password


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = utcnow()
    to_encode.update({
        "iss": TOKEN_ISSUER,
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    })
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)


def decode_token(token: str):
    """Return the verified claims, or None for anything wrong (bad signature, expired, wrong issuer...)."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],  # never trust the token's own "alg" header
            issuer=TOKEN_ISSUER,
            leeway=_LEEWAY_SECONDS,
            options={"require": ["exp", "iat", "iss"]},
        )
    except jwt.PyJWTError:
        return None


_UNSUBSCRIBE_PURPOSE = "unsubscribe"
_UNSUBSCRIBE_DAYS = 365


def create_unsubscribe_token(email: str) -> str:
    """Signed link token that can do exactly one thing: unsubscribe this address.
    It carries no ``user_id``/``pwv``, so it can never be used as a login token."""
    now = utcnow()
    return jwt.encode(
        {"purpose": _UNSUBSCRIBE_PURPOSE, "email": email, "iss": TOKEN_ISSUER, "iat": now,
         "exp": now + timedelta(days=_UNSUBSCRIBE_DAYS)},
        settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM,
    )


def decode_unsubscribe_token(token: str) -> str | None:
    """Return the email address in a valid unsubscribe token, else None."""
    claims = decode_token(token)
    if not claims or claims.get("purpose") != _UNSUBSCRIBE_PURPOSE:
        return None
    email = claims.get("email")
    return email if isinstance(email, str) and "@" in email else None


def password_fingerprint_matches(claim: object, password_hash: str) -> bool:
    return isinstance(claim, str) and hmac.compare_digest(claim, password_fingerprint(password_hash))
