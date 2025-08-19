from logging.config import fileConfig

from alembic import context
from example.org_models import Base

from fastapi_tenant.alembic.env import run_migrations_online

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


run_migrations_online(Base.metadata)
