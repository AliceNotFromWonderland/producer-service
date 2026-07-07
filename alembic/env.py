"""
Alembic environment configuration — async template.

Two things make this different from Alembic's default (sync) env.py:

1. `sqlalchemy.url` is overridden at runtime from the DATABASE_URL
   environment variable, so it always matches whatever the app itself is
   using (docker-compose, local .env, CI, etc.) instead of a hardcoded
   value in alembic.ini.
2. Migrations run through an async engine (asyncpg), via
   `connection.run_sync(...)`, since the rest of this project is async
   end-to-end. No separate sync driver (e.g. psycopg2) is needed just for
   Alembic.
"""
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import Base *and* app.models — importing the models package is what
# actually registers every model class on Base's registry. Without this
# import, Base.metadata would be empty and autogenerate would think every
# existing table needs to be dropped.
from app.database import Base
from app import models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/mtm_db"),
)


def run_migrations_offline() -> None:
    """Generate SQL script without a live DB connection (`alembic upgrade head --sql`)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
