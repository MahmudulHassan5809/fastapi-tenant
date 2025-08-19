import os
from logging.config import fileConfig
from collections.abc import Iterable
from alembic.environment import MigrationContext
from alembic import context
from alembic.operations import MigrationScript
from sqlalchemy import engine_from_config, pool, text


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Missing required environment variable: DATABASE_URL")

TENANT_SCHEMA = os.environ.get("TENANT_SCHEMA")
if not TENANT_SCHEMA:
    raise RuntimeError("Missing required environment variable: TENANT_SCHEMA")




config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)



if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_online(target_metadata):
    print(target_metadata.tables)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def process_revision_directives(
        context: MigrationContext,
        revision: str | Iterable[str | None] | Iterable[str],
        directives: list[MigrationScript],
    ):
        assert config.cmd_opts is not None
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            assert script.upgrade_ops is not None
            if script.upgrade_ops.is_empty():
                directives[:] = []

    with connectable.connect() as connection:
        if connection.dialect.name == "postgresql":
            connection.execute(text(f'SET search_path TO "{TENANT_SCHEMA}"'))
            connection.commit()
        elif connection.dialect.name in ("mysql", "mariadb"):
            connection.execute(text(f"USE {TENANT_SCHEMA}"))

        connection.dialect.default_schema_name = TENANT_SCHEMA

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,

        )

        with context.begin_transaction():
            context.run_migrations()
