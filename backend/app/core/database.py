from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

_url = settings.DATABASE_URL.get_secret_value()
_parsed = make_url(_url)
_kwargs: dict = {"echo": False, "future": True, "pool_pre_ping": True}
_LOCAL_HOSTS = {None, "", "localhost", "127.0.0.1", "::1"}

if _url.startswith("sqlite"):
    # Used by the test-suite only.
    _kwargs["connect_args"] = {"check_same_thread": False}
else:
    _connect_args: dict = {}
    if settings.DB_STATEMENT_TIMEOUT_MS:
        # Opt-in: a runaway query is cancelled by the database instead of hanging a worker.
        _connect_args["options"] = f"-c statement_timeout={settings.DB_STATEMENT_TIMEOUT_MS}"
    # Encrypt the connection to the database unless it is a local dev database
    # or the URL already says what to do.
    if settings.is_production and "sslmode" not in _parsed.query and _parsed.host not in _LOCAL_HOSTS:
        _connect_args["sslmode"] = settings.DB_SSLMODE
    _kwargs.update(
        connect_args=_connect_args,
        pool_size=5,        # connections kept open
        max_overflow=10,    # extra connections under load
        pool_timeout=30,    # seconds to wait for a connection
        pool_recycle=1800,  # recycle connections every 30 minutes
    )

engine = create_engine(_url, **_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
