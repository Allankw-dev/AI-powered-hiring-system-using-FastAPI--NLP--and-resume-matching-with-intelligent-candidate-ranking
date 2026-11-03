from pydantic import model_validator, BaseModel, EmailStr, Field, field_validator

from app.core.sanitize import clean_line
from app.core.security import validate_password_strength


class SignupRequest(BaseModel):
    full_name: str = Field(max_length=300)
    email: EmailStr
    password: str = Field(max_length=256)
    # Both boxes are unticked by default in the form and must be ticked on purpose.
    accepted_terms: bool = False   # Terms of Service + Privacy Policy
    confirm_adult: bool = False    # "I am 18 or older"
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
        v = clean_line(v)  # no HTML, no control characters, single line
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

    @model_validator(mode="after")
    def consents_were_given(self):
        if not self.accepted_terms:
            raise ValueError("You must accept the Terms of Service and the Privacy Policy to create an account")
        if not self.confirm_adult:
            raise ValueError("You must be 18 or older to create an account")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=256)

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.strip().lower()


class AdminOTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=1, max_length=10, pattern=r"^\s*\d{4,10}\s*$")

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
