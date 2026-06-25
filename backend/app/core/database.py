from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

DATABASE_URL = (
    f"mssql+pyodbc://{settings.SQL_SERVER}/{settings.SQL_DATABASE}"
    f"?driver={settings.SQL_DRIVER.replace(' ', '+')}"
    f"&trusted_connection=yes"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()