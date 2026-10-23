import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dep import get_db
from app.core.limiter import limiter
from app.core.security import DUMMY_PASSWORD_HASH, create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import AdminOTPVerifyRequest, LoginRequest, SignupRequest, TokenResponse
from app.schemas.user import UserOut
from app.services import otp_service
from app.services.email_service import EmailError, send_otp_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

ADMIN_2FA_REQUIRED = "Admin accounts must sign in with two-factor authentication (Admin 2FA login)."
BAD_CREDENTIALS = "Invalid email or password"
BAD_OTP = "Invalid or expired code"


def _check_credentials(db: Session, email: str, password: str) -> User:
    """Constant-time-ish credential check (same work whether or not the email exists)."""
    user = db.query(User).filter(User.email == email).first()
    stored_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    password_ok = verify_password(password, stored_hash)
    if not user or not password_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=BAD_CREDENTIALS)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been disabled")
    return user


def _token_for(user: User) -> dict:
    token = create_access_token({"user_id": user.id, "email": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}


@router.post("/signup", response_model=UserOut)
@limiter.limit("3/minute")
def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Self-service signup can only ever create candidates. Admins are created
    # or promoted with `python -m scripts.manage_admin` (needs server access).
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="candidate",
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = _check_credentials(db, payload.email, payload.password)

    # A password alone must never be enough for an admin.
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ADMIN_2FA_REQUIRED)

    return _token_for(user)


@router.post("/admin/request-otp")
@limiter.limit("3/minute")
def admin_request_otp(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = _check_credentials(db, payload.email, payload.password)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    otp = otp_service.save_otp(db, user)

    if settings.OTP_DELIVERY == "log":
        logger.warning("ADMIN OTP for %s: %s", user.email, otp)
        return {"message": "Code generated. Check the server log."}

    try:
        send_otp_email(user.email, otp)
    except EmailError:
        logger.exception("Could not deliver the admin OTP email")
        otp_service.clear_otp(db, user)
        raise HTTPException(status_code=503, detail="Could not send the sign-in code. Check the email settings.")

    return {"message": "A 6-digit code has been sent to your email address."}


@router.post("/admin/verify-otp", response_model=TokenResponse)
@limiter.limit("10/minute")
def admin_verify_otp(request: Request, payload: AdminOTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Same message for every failure so nothing about the account leaks.
    if not user or user.role != "admin" or not user.is_active:
        raise HTTPException(status_code=400, detail=BAD_OTP)

    if not otp_service.otp_matches(user, payload.otp_code):
        if otp_service.register_failure(user.email) >= otp_service.MAX_ATTEMPTS:
            otp_service.clear_otp(db, user)
            raise HTTPException(status_code=400, detail="Too many wrong codes. Request a new code.")
        raise HTTPException(status_code=400, detail=BAD_OTP)

    otp_service.clear_otp(db, user)
    return _token_for(user)
