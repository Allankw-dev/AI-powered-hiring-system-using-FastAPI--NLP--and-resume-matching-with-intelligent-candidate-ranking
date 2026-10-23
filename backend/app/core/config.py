"""Application settings.

Everything is read through pydantic-settings (environment variables first,
then a local ``.env`` file). Nothing in the codebase should call
``os.environ`` directly - import ``settings`` instead.
"""
import logging
import secrets
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_KNOWN_WEAK_KEYS = {"", "fallback-local-key-only", "changeme", "secret", "your-secret-key"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── General ──
    ENVIRONMENT: str = "production"  # production | development | test

    # ── Auth ──
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Database ──
    DATABASE_URL: str = ""

    # ── Email ──
    ADMIN_EMAIL: str = ""             # SMTP login / default sender
    ADMIN_EMAIL_PASSWORD: str = ""    # SMTP password (Gmail app password)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    RESEND_API_KEY: str = ""          # if set, email is sent over HTTPS via Resend
    EMAIL_FROM: str = ""              # e.g. "AI Hiring <noreply@yourdomain.com>"

    # ── Admin 2FA ──
    OTP_DELIVERY: str = "email"       # email | log  (log = print code to server logs)

    # ── Files ──
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 5
    MAX_PICTURE_MB: int = 2

    # ── Web ──
    FRONTEND_URL: str = "https://ai-powered-hiring-system.streamlit.app"
    CORS_ORIGINS: str = "*"           # comma separated, or * (bearer tokens, no cookies)
    TRUSTED_PROXY_HOPS: int = 1       # proxies in front of the app (for rate-limit IPs)

    # ── Chat assistant (Claude is used first, Gemini is the fallback) ──
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-haiku-5-5"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    CHAT_DAILY_LIMIT: int = 1000      # hard cap on chat calls per day (cost control)

    @model_validator(mode="after")
    def _validate(self):
        # Heroku/Render style URLs: SQLAlchemy 2 wants "postgresql://"
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = "postgresql://" + self.DATABASE_URL[len("postgres://"):]

        dev_like = self.ENVIRONMENT.lower() in {"development", "dev", "test"}

        if self.SECRET_KEY in _KNOWN_WEAK_KEYS:
            if dev_like:
                self.SECRET_KEY = secrets.token_urlsafe(48)
                logger.warning("SECRET_KEY not set - using a random key (tokens die on restart).")
            else:
                raise ValueError(
                    "SECRET_KEY is missing or a known weak value. "
                    "Set a long random SECRET_KEY (python -c \"import secrets; print(secrets.token_urlsafe(48))\")."
                )
        elif len(self.SECRET_KEY) < 32:
            logger.warning("SECRET_KEY is shorter than 32 characters - please use a longer one.")

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set.")

        if self.OTP_DELIVERY not in {"email", "log"}:
            raise ValueError("OTP_DELIVERY must be 'email' or 'log'.")
        if self.OTP_DELIVERY == "log" and not dev_like:
            logger.warning("OTP_DELIVERY=log in production: admin codes will appear in server logs.")
        return self

    # ── Helpers ──
    @property
    def cors_origin_list(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "*").strip()
        if raw == "*":
            return ["*"]
        return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024

    @property
    def max_picture_bytes(self) -> int:
        return self.MAX_PICTURE_MB * 1024 * 1024

    @property
    def email_configured(self) -> bool:
        return bool(self.RESEND_API_KEY or (self.ADMIN_EMAIL and self.ADMIN_EMAIL_PASSWORD))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
