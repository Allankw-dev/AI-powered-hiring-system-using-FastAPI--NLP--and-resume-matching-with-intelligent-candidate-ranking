from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    DATABASE_URL: str = "postgresql://postgres.vfwuvlkdhffrvpshgbar:t%2Fdhnk9smCS%25H%236@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
    ADMIN_EMAIL: str = "allankamau20@gmail.com"
    ADMIN_EMAIL_PASSWORD: str = "your_app_password_here"

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()