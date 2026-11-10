"""Migrations — spec 0001 AC-5."""

import pytest
from sqlalchemy import create_engine, inspect, text

from app.shared.db import run_migrations

pytestmark = pytest.mark.integration


def _snapshot(database_url: str) -> tuple[list[str], str]:
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            tables = sorted(inspect(connection).get_table_names())
            version = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
    finally:
        engine.dispose()
    return tables, version


def test_upgrade_head_on_empty_db_is_repeatable(database_url: str) -> None:
    run_migrations(database_url)
    first = _snapshot(database_url)

    run_migrations(database_url)

    assert _snapshot(database_url) == first
    assert first[1] == "0001"
