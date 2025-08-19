from fastapi import Depends, FastAPI
from sqlalchemy import text

from fastapi_tenant import TenantMiddlewareChain, Tenants, tenant_dep

app = FastAPI()


# settings.ENABLE_SUBDOMAIN_RESOLVER = True

app.add_middleware(TenantMiddlewareChain)


@app.get("/")
async def root(session=Depends(tenant_dep)):
    result = await session.execute(text("SELECT * from customers where id=1"))
    rows = result.mappings().first()

    name = "Alice"

    # Insert query
    await session.execute(
        text(
            """
            INSERT INTO customers (name)
            VALUES (:name)
            """
        ),
        {"name": name},
    )

    await session.commit()

    return {
        "message": "Hello World",
        "result": rows,
        "tenant": Tenants.current(),
    }
