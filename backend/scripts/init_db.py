"""Create any missing tables (safe to run repeatedly; never drops anything).

    cd backend
    DATABASE_URL=postgresql://... python -m scripts.init_db
"""
import importlib

from app.core.database import Base, engine

importlib.import_module("app.models")  # registers all tables on Base.metadata


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tables ready:", ", ".join(sorted(Base.metadata.tables)))


if __name__ == "__main__":
    main()
