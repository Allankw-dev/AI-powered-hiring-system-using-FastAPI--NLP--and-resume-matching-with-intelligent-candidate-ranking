from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import validate_password_strength


class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    # No longer collected (not used for scoring, and a hiring tool should not
    # need it). Old clients may still send it - it is accepted and ignored.
    sex: str | None = Field(default=None, exclude=True)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_password_strength(v)

    @field_validator("full_name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters")
        if len(v) > 255:
            raise ValueError("Full name is too long")
        if any(c.isdigit() for c in v):
            raise ValueError("Full name cannot contain numbers")
        return v

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.strip().lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=256)

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.strip().lower()


class AdminOTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=1, max_length=10)

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
