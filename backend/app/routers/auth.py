from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dep import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, AdminOTPVerifyRequest
from app.schemas.user import UserOut
from app.services.otp_service import generate_otp, otp_expiration

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserOut)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    try:
        print("SIGNUP STEP 1: request received")

        existing = db.query(User).filter(User.email == payload.email).first()
        print("SIGNUP STEP 2: existing user check done")

        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        role = "admin" if payload.email == "allankamauw20@gmail.com" else "candidate"
        print("SIGNUP STEP 3: role decided ->", role)

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=role,
            is_active=True
        )
        print("SIGNUP STEP 4: password hashed and user object created")

        db.add(user)
        db.commit()
        db.refresh(user)
        print("SIGNUP STEP 5: user saved")

        return user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("SIGNUP ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        print("LOGIN STEP 1: request received")

        user = db.query(User).filter(User.email == payload.email).first()
        print("LOGIN STEP 2: user query done")

        if not user:
            print("LOGIN STEP 3: user not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        print("LOGIN STEP 4: starting password verification")
        password_ok = verify_password(payload.password, user.password_hash)
        print("LOGIN STEP 5: password verification finished ->", password_ok)

        if not password_ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        print("LOGIN STEP 6: creating token")
        token = create_access_token({
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        })

        print("LOGIN STEP 7: returning response")
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role
        }

    except HTTPException:
        raise
    except Exception as e:
        print("LOGIN ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/request-otp")
def admin_request_otp(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        print("ADMIN OTP STEP 1: request received")

        user = db.query(User).filter(User.email == payload.email).first()
        print("ADMIN OTP STEP 2: user query done")

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        print("ADMIN OTP STEP 3: starting password verification")
        password_ok = verify_password(payload.password, user.password_hash)
        print("ADMIN OTP STEP 4: password verification finished ->", password_ok)

        if not password_ok:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        otp = generate_otp()
        expiry = otp_expiration()

        user.otp_code = otp
        user.otp_expiry = expiry
        db.commit()

        print(f"\nADMIN OTP for {user.email}: {otp}\n")

        return {"message": "OTP generated. Check backend terminal."}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("ADMIN OTP ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/verify-otp", response_model=TokenResponse)
def admin_verify_otp(payload: AdminOTPVerifyRequest, db: Session = Depends(get_db)):
    try:
        print("ADMIN VERIFY STEP 1: request received")

        user = db.query(User).filter(User.email == payload.email).first()
        print("ADMIN VERIFY STEP 2: user query done")

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        if not user.otp_code or not user.otp_expiry:
            raise HTTPException(status_code=400, detail="No OTP requested")

        if user.otp_code != payload.otp_code:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        if datetime.utcnow() > user.otp_expiry:
            raise HTTPException(status_code=400, detail="OTP expired")

        user.otp_code = None
        user.otp_expiry = None
        db.commit()

        print("ADMIN VERIFY STEP 3: OTP cleared, creating token")
        token = create_access_token({
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        })

        print("ADMIN VERIFY STEP 4: returning response")
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("ADMIN VERIFY ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))