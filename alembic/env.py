from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import Base
import app.models  # noqa

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Allow the database URL to be overridden by the environment (e.g. when
# running locally outside of docker-compose, where the "db" hostname in
# alembic.ini does not resolve). Falls back to the value in alembic.ini.
_database_url = os.environ.get("DATABASE_URL")
if not _database_url:
    try:
        from app.core.config import settings

        _database_url = settings.DATABASE_URL
    except Exception:
        _database_url = None
if _database_url:
    config.set_main_option("sqlalchemy.url", _database_url)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
