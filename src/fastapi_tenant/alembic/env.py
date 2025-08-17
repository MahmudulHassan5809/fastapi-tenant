from alembic import context
from sqlalchemy import engine_from_config, pool, create_engine, text
from logging.config import fileConfig
import os



config = context.config
fileConfig(config.config_file_name)



def run_shared_migrations():
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
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




def run_schema_migrations():
    schema = os.environ["TENANT_SCHEMA"]
    db_url = os.environ["DATABASE_URL"]
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

