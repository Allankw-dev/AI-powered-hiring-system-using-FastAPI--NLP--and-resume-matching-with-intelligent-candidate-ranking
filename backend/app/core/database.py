from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

_url = settings.DATABASE_URL
_kwargs: dict = {"echo": False, "future": True, "pool_pre_ping": True}

if _url.startswith("sqlite"):
    # Used by the test-suite only.
    _kwargs["connect_args"] = {"check_same_thread": False}
else:
    _kwargs.update(
        pool_size=5,        # connections kept open
        max_overflow=10,    # extra connections under load
        pool_timeout=30,    # seconds to wait for a connection
        pool_recycle=1800,  # recycle connections every 30 minutes
    )

engine = create_engine(_url, **_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
