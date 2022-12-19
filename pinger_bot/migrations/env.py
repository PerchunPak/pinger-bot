"""Additional configuration for the alembic environment."""
import asyncio
import logging.config

import alembic
import sqlalchemy
from sqlalchemy.ext import asyncio as sqlalchemy_asyncio

from pinger_bot.config import config as pinger_bot_config
from pinger_bot.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = alembic.context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    logging.config.fileConfig(config.config_file_name)  # skipcq: PY-A6006

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata  # type: ignore[attr-defined]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# get sqlalchemy URL from config
config.set_main_option("sqlalchemy.url", pinger_bot_config.db_uri)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    alembic.context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


def do_run_migrations(connection) -> None:
    """Just run migrations."""
    alembic.context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = sqlalchemy_asyncio.AsyncEngine(
        sqlalchemy.engine_from_config(  # type: ignore[arg-type] # incorrect type annotation in alembic
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=sqlalchemy.pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if alembic.context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
