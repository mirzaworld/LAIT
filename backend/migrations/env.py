import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
# Ensure backend parent directory is on sys.path for 'models' package
# Adjust path: ensure current working directory (backend) is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
project_root = os.path.abspath(os.path.join(backend_dir, '..'))
for p in {backend_dir, project_root}:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from models.db_models import Base
except ModuleNotFoundError:
    # Fallback attempt using relative import
    raise

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use unified Base metadata
target_metadata = Base.metadata

# Enable batch mode for SQLite schema changes & autogenerate improvements
render_as_batch = True


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        url = os.environ.get('DATABASE_URL')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=render_as_batch,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        configuration["sqlalchemy.url"] = database_url
    else:
        configuration["sqlalchemy.url"] = context.get_x_argument(as_dictionary=True).get("db_url", "")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=render_as_batch,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
