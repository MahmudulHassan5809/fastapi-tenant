from logging.config import fileConfig

from alembic import context

from fastapi_tenant.alembic.env import run_tenant_migrations

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


run_tenant_migrations()
