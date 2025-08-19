import os
from pathlib import Path
from example.models import Base as TenantBase
from example.org_models import Base as SharedBase

from alembic import context
from fastapi_tenant.alembic.env import run_migrations_online





scope = os.environ.get("ALEMBIC_SCOPE", "shared")

script = context.script


script.__dict__.pop('_version_locations', None)
migrations_root = Path(__file__).resolve().parent.parent / "migrations" / scope
script.version_locations = [str(migrations_root)]


if scope == "shared":
    target_metadata = SharedBase.metadata
else:
    target_metadata = TenantBase.metadata

run_migrations_online(target_metadata)
