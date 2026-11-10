"""Alembic environment. Modules add their metadata to TARGET_METADATA as they gain tables."""

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
TARGET_METADATA = None


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=TARGET_METADATA,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # render_as_batch: SQLite cannot ALTER most constraints in place (ADR 0002).
        context.configure(
            connection=connection, target_metadata=TARGET_METADATA, render_as_batch=True
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
