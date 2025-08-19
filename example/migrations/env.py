import os
from example.models import Base as TenantBase
from example.org_models import Base as SharedBase


from fastapi_tenant.alembic.env import run_migrations_online


branch = os.environ.get("ALEMBIC_BRANCH", "shared")
if branch == "shared":
    target_metadata = SharedBase.metadata
else:
    target_metadata = TenantBase.metadata

run_migrations_online(target_metadata)
