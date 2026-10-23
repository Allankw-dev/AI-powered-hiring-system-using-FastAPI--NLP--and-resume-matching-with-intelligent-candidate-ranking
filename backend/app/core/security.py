import hashlib
import re
from datetime import timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.timeutil import utcnow

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt only looks at the first 72 BYTES of a password.
_BCRYPT_MAX_BYTES = 72


def _prep(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return pwd_context.hash(_prep(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(_prep(plain_password), hashed_password)
    except ValueError:
        return False


# A real bcrypt hash used to burn the same CPU time when the email is unknown,
# so response time does not reveal which emails are registered.
DUMMY_PASSWORD_HASH = hash_password("not-a-real-password-for-timing-only")


def hash_token(token: str) -> str:
    """SHA-256 of a high-entropy token (reset links). Stored instead of the token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


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
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
