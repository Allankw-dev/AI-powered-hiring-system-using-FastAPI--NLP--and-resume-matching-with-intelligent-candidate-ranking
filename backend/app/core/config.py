from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    SQL_SERVER: str = r"localhost\SQLEXPRESS"
    SQL_DATABASE: str = "AIHiringDB"
    SQL_DRIVER: str = "ODBC Driver 17 for SQL Server"

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