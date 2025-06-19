import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from models import db

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = db.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        url = os.environ.get('DATABASE_URL')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
        # Fallback to command line argument
        configuration["sqlalchemy.url"] = context.get_x_argument(as_dictionary=True).get("db_url", "")
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
