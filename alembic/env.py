import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Tüm modellerinin Alembic tarafından tespiti için import edildiğinden emin ol
import models  # noqa: F401
from alembic import context

# 1. Projedeki Base ve settings importları
from config import settings
from database import Base

# 2. Alembic Config nesnesi
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# 2. DATABASE_URL tanımını dinamik alma (Docker ortamındaki db:5432 adresini okur)
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)
print(f"--- ALEMBIC CONNECTING TO: {DATABASE_URL} ---")
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Offline migration çalıştırma."""
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
    # Sadece migration komutlarında (up/downgrade) yürüt, revision aşamasında çalıştırma
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Online (Async) migration çalıştırma."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
