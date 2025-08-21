# FastAPI Tenant

**Multi-tenant FastAPI setup with Alembic migrations for shared and tenant schemas.**

Provides:

* Middleware-based tenant detection
* SQLAlchemy session per tenant
* Shared and tenant-specific tables
* Easy Alembic migrations per schema

---

## 🔹 Features

* Multi-tenant support via middleware
* Shared tables and tenant-specific tables
* Tenant-scoped SQLAlchemy sessions
* CLI for managing migrations per tenant (`fastapi-tenant`)
* Fully production-ready

---

## 🔹 Installation

```bash
pip install -i https://test.pypi.org/simple/ fastapi-tenant
pip install fastapi sqlalchemy alembic
```

---

## 🔹 FastAPI Setup

```python
from fastapi import FastAPI, Depends
from sqlalchemy import text

from fastapi_tenant import TenantMiddlewareChain, Tenants, tenant_dep

app = FastAPI()
app.add_middleware(TenantMiddlewareChain)

@app.get("/")
async def root(session=Depends(tenant_dep)):
    result = await session.execute(text("SELECT * FROM customers LIMIT 1"))
    rows = result.mappings().all()
    return {
        "message": "Hello World",
        "result": rows,
        "tenant": Tenants.current(),
    }
```

---

## 🔹 Database Models

**Tenant models (`models.py`)**

```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

**Shared models (`org_models.py`)**

```python
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

---

## 🔹 Alembic Setup (`env.py`)

```python
import os
from pathlib import Path
from example.models import Base as TenantBase
from example.org_models import Base as SharedBase

from alembic import context
from fastapi_tenant.alembic.env import run_migrations_online

# Determine scope: shared or tenant
scope = os.environ.get("ALEMBIC_SCOPE", "shared")
script = context.script

# Migration version folder
script.__dict__.pop('_version_locations', None)
migrations_root = Path(__file__).resolve().parent.parent / "migrations" / scope
script.version_locations = [str(migrations_root)]

# Choose metadata
target_metadata = SharedBase.metadata if scope == "shared" else TenantBase.metadata

# Run migrations online
run_migrations_online(target_metadata)
```

---

## 🔹 CLI Commands

### Shared schema

```bash
fastapi-tenant revision "initial" --schema shared --scope shared
fastapi-tenant upgrade --schema shared --scope shared
```

### Tenant schemas

```bash
fastapi-tenant revision "initial" --schema tenant1 --scope tenant
fastapi-tenant upgrade --schema tenant1 --scope tenant

fastapi-tenant upgrade --schema tenant2 --scope tenant
```

* `--schema` → name of the schema
* `--scope` → `shared` or `tenant` (decides which metadata to use)

Migration files are stored in:

```
migrations/shared/versions
migrations/tenant/versions
```

---

## 🔹 Best Practices

1. Use **shared** tables for global data (organization, settings)
2. Use **tenant** tables for tenant-specific data
3. Always access DB via `tenant_dep` for correct tenant session
4. Separate migrations by schema using `--scope`
5. Keep `ALEMBIC_SCOPE` environment variable in sync when running migration commands

---

## 🔹 Summary

This setup gives you:

* A **robust multi-tenant FastAPI app**
* Automatic tenant session handling
* Clear separation of shared and tenant tables
* Easy Alembic migration CLI for multiple tenants
