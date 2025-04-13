"""Alembic migration environment configuration."""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.exc import OperationalError

from alembic import context

# Add parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from memory_management.config import get_config
from memory_management.db_models import Base

# Load memory management config
memory_config = get_config()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set sqlalchemy.url in alembic.ini dynamically
db_url = (
    f"sqlite:///{memory_config.DB_FILE_PATH}"
    if memory_config.DB_HOST.lower() == "sqlite"
    else f"postgresql://{memory_config.DB_USER}:{memory_config.DB_PASSWORD}"
         f"@{memory_config.DB_HOST}:{memory_config.DB_PORT}/{memory_config.DB_NAME}"
)
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Handle SQLite specific requirements
    is_sqlite = memory_config.DB_HOST.lower() == "sqlite"
    if is_sqlite:
        def _include_object(object, name, type_, reflected, compare_to):
            if type_ == "table":
                # Skip SQLite system tables
                return not name.startswith("sqlite_")
            return True

        # Ensure SQLite supports ALTER TABLE
        def run_migrations_with_sqlite(connection: Connection) -> None:
            # Enable foreign keys
            connection.execute('PRAGMA foreign_keys=ON')
            # Begin transaction
            with context.begin_transaction():
                context.configure(
                    connection=connection,
                    target_metadata=target_metadata,
                    include_object=_include_object,
                    render_as_batch=True  # Enable batch mode for SQLite
                )
                context.run_migrations()

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            if is_sqlite:
                run_migrations_with_sqlite(connection)
            else:
                context.configure(
                    connection=connection,
                    target_metadata=target_metadata,
                    compare_type=True  # Compare column types
                )
                with context.begin_transaction():
                    context.run_migrations()
    except OperationalError as e:
        print(f"Error running migrations: {e}")
        raise
    finally:
        connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()