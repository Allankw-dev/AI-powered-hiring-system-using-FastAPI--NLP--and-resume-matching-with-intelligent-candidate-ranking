from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token, password_fingerprint_matches
from app.models.user import User

security = HTTPBearer()

_UNAUTHORIZED = {"WWW-Authenticate": "Bearer"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers=_UNAUTHORIZED)

    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload", headers=_UNAUTHORIZED)

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive", headers=_UNAUTHORIZED)

    # A token is only valid for the password it was issued under: changing or
    # resetting the password signs out every older session.
    if not password_fingerprint_matches(payload.get("pwv"), user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired. Please sign in again.", headers=_UNAUTHORIZED)
    return user


def require_admin(current_user: User = Depends(get_current_user)):
    """The role is read from the database on every request, never trusted from the token."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
