from .shared_env import run_migrations_online as run_shared_migrations
from .tenant_env import run_migrations_for_schema as run_tenant_migrations

__all__ = [
    "run_shared_migrations",
    "run_tenant_migrations",
]