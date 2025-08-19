from logging.config import fileConfig

from alembic import context
from example.models import (
    Base,  # noqa
    Customer,  # noqa
)

from fastapi_tenant.alembic.env import run_migrations_online

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
run_migrations_online(target_metadata)
