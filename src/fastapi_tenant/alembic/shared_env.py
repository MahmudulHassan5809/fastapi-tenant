from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os



config = context.config
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    schema_translate_map = {None: "public"}

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            version_table_schema="public",
            include_schemas=True,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
            dialect_opts={"paramstyle": "named"},
            schema_translate_map=schema_translate_map
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()