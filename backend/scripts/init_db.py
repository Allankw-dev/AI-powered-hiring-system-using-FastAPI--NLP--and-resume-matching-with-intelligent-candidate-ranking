"""Create any missing tables (safe to run repeatedly; never drops anything).

    cd backend
    DATABASE_URL=postgresql://... python -m scripts.init_db
"""
from app.core.database import Base, engine
import app.models  # noqa: F401  (registers all tables)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tables ready:", ", ".join(sorted(Base.metadata.tables)))


if __name__ == "__main__":
    main()
