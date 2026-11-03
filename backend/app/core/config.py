"""Application settings.

Everything is read through pydantic-settings (environment variables first,
then a local ``.env`` file). Nothing in the codebase should call
``os.environ`` directly - import ``settings`` instead.

Secrets (keys, passwords, the database URL) are ``SecretStr`` so they print as
``**********`` in logs, tracebacks and ``repr(settings)``. Call
``.get_secret_value()`` only at the exact place the value is used.
"""
import logging
import secrets
from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_KNOWN_WEAK_KEYS = {"", "fallback-local-key-only", "changeme", "secret", "your-secret-key", "change-me"}
_DEV_ENVIRONMENTS = {"development", "dev", "test"}
_PROD_ENVIRONMENTS = {"production", "prod", "staging"}
_SSL_MODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
_LOCAL_DEV_ORIGINS = ["http://localhost:8501", "http://127.0.0.1:8501"]
MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── General ──
    ENVIRONMENT: str = "production"  # production | development | test
    ENABLE_DOCS: bool | None = None  # /docs + /openapi.json. Default: only outside production.

    # ── Auth ──
    SECRET_KEY: SecretStr = SecretStr("")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOGIN_MAX_FAILURES: int = 5       # wrong passwords per (email + IP) before a temporary lock
    LOGIN_LOCKOUT_MINUTES: int = 15

    # ── Database ──
    DATABASE_URL: SecretStr = SecretStr("")
    DB_SSLMODE: str = "require"       # applied to non-local Postgres when the URL has no sslmode
    DB_STATEMENT_TIMEOUT_MS: int = 0  # 0 = off. Do NOT enable behind PgBouncer/Supabase pooler (it rejects "options").

    # ── Email ──
    ADMIN_EMAIL: str = ""             # SMTP login / default sender
    ADMIN_EMAIL_PASSWORD: SecretStr = SecretStr("")   # SMTP password (Gmail app password)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    RESEND_API_KEY: SecretStr = SecretStr("")         # if set, email goes over HTTPS via Resend
    EMAIL_FROM: str = ""              # e.g. "AI Hiring <noreply@yourdomain.com>"

    # ── Admin 2FA ──
    OTP_DELIVERY: str = "email"       # email | log  (log = print code to server logs)

    # ── Files ──
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 5
    MAX_PICTURE_MB: int = 2
    MAX_JSON_BODY_KB: int = 256       # every non-upload request body is capped at this

    # ── Web ──
    FRONTEND_URL: str = "https://ai-powered-hiring-system.streamlit.app"
    API_PUBLIC_URL: str = ""          # public https URL of THIS API (enables one-click unsubscribe headers in emails)
    CORS_ORIGINS: str = ""            # comma separated. Empty = only FRONTEND_URL (+ localhost in dev)
    ALLOWED_HOSTS: str = ""           # optional comma separated Host allow-list, e.g. "api.example.com"
    TRUSTED_PROXY_HOPS: int = 1       # proxies in front of the app (for rate-limit IPs)
    HSTS_ENABLED: bool = True         # Strict-Transport-Security (only sent in production)

    # ── Who runs the service (shown in the legal pages and in email footers) ──
    OPERATOR_NAME: str = "Allan Kamau"
    OPERATOR_LOCATION: str = "Nairobi, Kenya"
    CONTACT_EMAIL: str = ""           # privacy / support contact. Set this before you go live.

    # ── Chat assistant (Claude is used first, Gemini is the fallback) ──
    ANTHROPIC_API_KEY: SecretStr = SecretStr("")
    ANTHROPIC_MODEL: str = "claude-haiku-5-5"
    GEMINI_API_KEY: SecretStr = SecretStr("")
    GEMINI_MODEL: str = "gemini-3.8-flash"   # override with the GEMINI_MODEL env var if Google renames it
    CHAT_DAILY_LIMIT: int = 1000      # hard cap on chat calls per day, all visitors together
    CHAT_PER_IP_DAILY_LIMIT: int = 60 # per visitor, so one person cannot use up everybody's share

    @model_validator(mode="after")
    def _validate(self):
        env = self.ENVIRONMENT.strip().lower()
        if env not in _DEV_ENVIRONMENTS | _PROD_ENVIRONMENTS:
            raise ValueError("ENVIRONMENT must be one of: production, development, test.")
        self.ENVIRONMENT = env
        dev_like = env in _DEV_ENVIRONMENTS

        # Always name the driver explicitly. A bare "postgresql://" means psycopg2
        # on SQLAlchemy <= 2.0 but psycopg (v3) on 2.1+, and we ship psycopg2.
        # URLs that already name a driver (postgresql+xxx://) are left alone.
        url = self.DATABASE_URL.get_secret_value().strip()
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg2://" + url[len("postgresql://"):]
        if not url:
            raise ValueError("DATABASE_URL is not set.")
        self.DATABASE_URL = SecretStr(url)

        key = self.SECRET_KEY.get_secret_value()
        if key in _KNOWN_WEAK_KEYS:
            if dev_like:
                self.SECRET_KEY = SecretStr(secrets.token_urlsafe(48))
                logger.warning("SECRET_KEY not set - using a random key (tokens die on restart).")
            else:
                raise ValueError(
                    "SECRET_KEY is missing or a known weak value. "
                    "Set a long random SECRET_KEY (python -c \"import secrets; print(secrets.token_urlsafe(48))\")."
                )
        elif len(key) < MIN_SECRET_KEY_LENGTH:
            if dev_like:
                logger.warning("SECRET_KEY is shorter than %s characters.", MIN_SECRET_KEY_LENGTH)
            else:
                raise ValueError(
                    f"SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )

        if self.ALGORITHM not in {"HS256", "HS384", "HS512"}:
            raise ValueError("ALGORITHM must be HS256, HS384 or HS512.")
        if not 1 <= self.ACCESS_TOKEN_EXPIRE_MINUTES <= 1440:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 1440.")
        if self.LOGIN_MAX_FAILURES < 1 or self.LOGIN_LOCKOUT_MINUTES < 1:
            raise ValueError("LOGIN_MAX_FAILURES and LOGIN_LOCKOUT_MINUTES must be at least 1.")
        if self.DB_STATEMENT_TIMEOUT_MS < 0:
            raise ValueError("DB_STATEMENT_TIMEOUT_MS cannot be negative.")
        if self.DB_SSLMODE not in _SSL_MODES:
            raise ValueError(f"DB_SSLMODE must be one of: {', '.join(sorted(_SSL_MODES))}.")
        if self.TRUSTED_PROXY_HOPS < 0:
            raise ValueError("TRUSTED_PROXY_HOPS cannot be negative.")
        if not 1 <= self.MAX_UPLOAD_MB <= 25 or not 1 <= self.MAX_PICTURE_MB <= 10:
            raise ValueError("MAX_UPLOAD_MB must be 1-25 and MAX_PICTURE_MB must be 1-10.")

        if self.API_PUBLIC_URL and not self.API_PUBLIC_URL.startswith(("https://", "http://localhost")):
            raise ValueError("API_PUBLIC_URL must start with https://")
        if self.CONTACT_EMAIL and "@" not in self.CONTACT_EMAIL:
            raise ValueError("CONTACT_EMAIL must be an email address.")
        if not dev_like and not self.CONTACT_EMAIL:
            logger.warning("CONTACT_EMAIL is not set: users have no email address for privacy requests.")

        if self.OTP_DELIVERY not in {"email", "log"}:
            raise ValueError("OTP_DELIVERY must be 'email' or 'log'.")
        if self.OTP_DELIVERY == "log" and not dev_like:
            logger.warning("OTP_DELIVERY=log in production: admin codes will appear in server logs.")

        if not dev_like and "*" in self.cors_origin_list:
            logger.warning("CORS_ORIGINS contains '*' in production: any website can call this API from a browser.")
        return self

    # ── Helpers ──
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT in _PROD_ENVIRONMENTS

    @property
    def docs_enabled(self) -> bool:
        return (not self.is_production) if self.ENABLE_DOCS is None else self.ENABLE_DOCS

    @property
    def cors_origin_list(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if raw:
            return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
        # Default: the browser may only call us from our own frontend.
        parts = urlsplit(self.FRONTEND_URL.strip())
        origins = [f"{parts.scheme}://{parts.netloc}"] if parts.scheme and parts.netloc else []
        if not self.is_production:
            origins += _LOCAL_DEV_ORIGINS
        return origins

    @property
    def allowed_host_list(self) -> list[str]:
        return [h.strip() for h in (self.ALLOWED_HOSTS or "").split(",") if h.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024

    @property
    def max_picture_bytes(self) -> int:
        return self.MAX_PICTURE_MB * 1024 * 1024

    @property
    def max_json_body_bytes(self) -> int:
        return self.MAX_JSON_BODY_KB * 1024

    @property
    def email_configured(self) -> bool:
        return bool(self.RESEND_API_KEY or (self.ADMIN_EMAIL and self.ADMIN_EMAIL_PASSWORD))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
