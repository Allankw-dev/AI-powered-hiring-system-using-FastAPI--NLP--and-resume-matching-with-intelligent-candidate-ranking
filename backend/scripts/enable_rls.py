"""Lock every table against Supabase's public REST API (Postgres only).

Supabase publishes the `public` schema through an HTTP API that anyone holding your
project's (public) "anon" key can call. Tables WITHOUT row level security are readable
and writable through it - including the users table. This backend talks to Postgres
directly as the table owner (which bypasses RLS), so turning RLS on with no policies
blocks the REST API without affecting the app.

    python -m scripts.enable_rls            # show the SQL that would run (dry run)
    python -m scripts.enable_rls --apply    # run it

Safe to run repeatedly.
"""
import importlib
import sys

from sqlalchemy import text

from app.core.database import Base, engine
from app.core.db_setup import rls_statements

importlib.import_module("app.models")  # registers every table on Base.metadata


def statements() -> list[str]:
    return rls_statements(list(Base.metadata.tables))


def main() -> int:
    if engine.dialect.name != "postgresql":
        print("This only applies to PostgreSQL databases.")
        return 1
    stmts = statements()
    if "--apply" not in sys.argv:
        print("Dry run. Add --apply to execute:\n")
        print("\n".join(stmts))
        return 0
    with engine.begin() as conn:
        for stmt in stmts:
            conn.execute(text(stmt))
    print(f"Done: row level security enabled on {len(Base.metadata.tables)} tables.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
