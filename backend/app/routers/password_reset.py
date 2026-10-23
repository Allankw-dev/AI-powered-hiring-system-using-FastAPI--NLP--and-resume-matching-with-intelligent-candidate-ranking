import secrets
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dep import get_db
from app.core.limiter import limiter
from app.core.security import hash_password, hash_token, validate_password_strength
from app.core.timeutil import as_utc, utcnow
from app.models.user import User
from app.services.email_service import send_reset_email

router = APIRouter(prefix="/password", tags=["Password Reset"])

GENERIC_MESSAGE = "If an account with that email exists, a reset link has been sent."


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.strip().lower()


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_password_strength(v)


@router.post("/forgot")
@limiter.limit("3/minute")
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    # Admins cannot reset by email (they would bypass 2FA); same answer either way.
    if user and user.is_active and user.role != "admin":
        token = secrets.token_urlsafe(32)
        user.reset_token = hash_token(token)  # only the hash is stored
        user.reset_token_expiry = utcnow() + timedelta(hours=1)
        db.commit()

        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/?reset_token={token}"
        background_tasks.add_task(send_reset_email, user.email, reset_link)

    return {"message": GENERIC_MESSAGE}


@router.post("/reset")
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == hash_token(payload.token)).first()

    if not user or user.role == "admin" or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")

    if user.reset_token_expiry is None or utcnow() > as_utc(user.reset_token_expiry):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")

    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return {"message": "Password reset successfully"}
