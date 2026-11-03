"""Create tables that do not exist yet (never changes or drops an existing table).

On PostgreSQL every table created here also gets row-level security switched on and is
closed to Supabase's public REST roles, so a new table is never briefly readable through
Supabase's public API. (Run `python -m scripts.enable_rls --apply` once for the older tables.)
"""
import importlib
import logging

from sqlalchemy import inspect, text

from app.core.database import Base, engine

importlib.import_module("app.models")  # make sure every table is registered before we look at Base.metadata

logger = logging.getLogger(__name__)


def rls_statements(table_names: list[str]) -> list[str]:
    names = sorted(table_names)
    stmts = [f'ALTER TABLE public."{n}" ENABLE ROW LEVEL SECURITY;' for n in names]  # nosec B608
    quoted = ", ".join(f'public."{n}"' for n in names)
    stmts.append(
        "DO $$ BEGIN "
        "IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN "
        f"EXECUTE 'REVOKE ALL ON {quoted} FROM anon'; END IF; "  # nosec B608
        "IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN "
        f"EXECUTE 'REVOKE ALL ON {quoted} FROM authenticated'; END IF; END $$;"
    )
    return stmts


def ensure_tables() -> list[str]:
    existing = set(inspect(engine).get_table_names())
    missing = [t for t in Base.metadata.sorted_tables if t.name not in existing]
    if not missing:
        return []
    Base.metadata.create_all(bind=engine, tables=missing)
    created = [t.name for t in missing]
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            for stmt in rls_statements(created):
                conn.execute(text(stmt))
    logger.info("Created missing tables: %s", ", ".join(created))
    return created
