import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import logging
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

# Logger for migration environment
logger = logging.getLogger('alembic.env')

# Central URL resolver with fallback
DEFAULT_SQLITE_PATH = os.path.join(project_root, 'lait_enhanced.db')

def resolve_database_url():
    # Priority: explicit x argument > env var > sqlite fallback
    x_args = context.get_x_argument(as_dictionary=True)
    explicit = x_args.get('db_url') if x_args else None
    env_url = os.environ.get('DATABASE_URL') or os.environ.get('DB_URL')
    final_url = explicit or env_url
    if not final_url:
        final_url = f"sqlite:///{DEFAULT_SQLITE_PATH}"
        logger.warning(f"DATABASE_URL not provided – using fallback {final_url}")
    else:
        logger.info(f"Using database URL: {final_url}")
    return final_url

# Optional include / exclude hook (placeholder for future filtering)
EXCLUDE_TABLES = set(os.environ.get('ALEMBIC_EXCLUDE_TABLES', '').split(',')) if os.environ.get('ALEMBIC_EXCLUDE_TABLES') else set()

def include_object(object, name, type_, reflected, compare_to):  # noqa: D401
    if type_ == 'table' and name in EXCLUDE_TABLES:
        return False
    return True

# Use unified Base metadata
target_metadata = Base.metadata

# Enable batch mode for SQLite schema changes & autogenerate improvements
render_as_batch = True


def run_migrations_offline():
    url = resolve_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=render_as_batch,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = resolve_database_url()
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
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
