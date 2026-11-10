"""Database engine and migrations (ADR 0002: SQLite through SQLAlchemy, schema through Alembic)."""

from pathlib import Path
from typing import Any

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_db_engine(url: str) -> Engine:
    if make_url(url).get_backend_name() == "sqlite":
        _ensure_sqlite_directory(url)
        engine = create_engine(url)
        event.listen(engine, "connect", _sqlite_pragmas)
        return engine
    return create_engine(url)


def is_reachable(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True


def run_migrations(url: str) -> None:
    """Bring the schema to the latest revision; idempotent (spec 0001 R-1, AC-5)."""
    _ensure_sqlite_directory(url)
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    # configparser interpolation: a literal % in the URL must be doubled.
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(config, "head")


def _ensure_sqlite_directory(url: str) -> None:
    parsed = make_url(url)
    if parsed.get_backend_name() == "sqlite" and parsed.database not in (None, "", ":memory:"):
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)


def _sqlite_pragmas(dbapi_connection: Any, _record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # ADR 0002: concurrent readers, one writer
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
