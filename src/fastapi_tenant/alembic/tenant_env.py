import os
from alembic import context
from sqlalchemy import create_engine, pool, text
from logging.config import fileConfig


config = context.config
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

def run_migrations_for_schema(schema: str, db_url: str):
    connectable = create_engine(db_url, poolclass=pool.NullPool, echo=True)
    schema_translate_map = {None: schema}

    with connectable.connect() as connection:
        # Create schema if it doesn't exist BEFORE configuring context
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        connection.commit()
        
        connection.execution_options(schema_translate_map=schema_translate_map)
        context.configure(
            connection=connection,
            version_table_schema=schema,
            include_schemas=True,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
            dialect_opts={"paramstyle": "named"},
            schema_translate_map=schema_translate_map,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    raise NotImplementedError("Offline mode not supported for tenants")
else:
    schema = os.environ["TENANT_SCHEMA"]
    db_url = os.environ["DATABASE_URL"]
    if not schema:
        raise Exception("TENANT_SCHEMA not set")
    run_migrations_for_schema(schema, db_url)