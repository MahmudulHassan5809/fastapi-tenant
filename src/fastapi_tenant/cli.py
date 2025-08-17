import asyncio

import typer
from sqlalchemy import text

from .db import engine
from .settings import settings

app = typer.Typer(add_completion=False, help="FastAPI Tenant management CLI")


@app.command()
def create(tenant_id: str):
    """Create a tenant schema and insert into public.tenants."""

    async def _run():
        async with engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {tenant_id}"))
            await conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS public.tenants (
                  id varchar(64) primary key,
                  created_at timestamptz not null default now(),
                  is_active boolean not null default true
                )
            """)
            )
            await conn.execute(
                text("INSERT INTO public.tenants (id) VALUES (:t) ON CONFLICT DO NOTHING"),
                {"t": tenant_id},
            )

    asyncio.run(_run())


@app.command()
def drop(tenant_id: str, yes: bool = typer.Option(False, help="Confirm drop")):
    if not yes:
        typer.echo("Use --yes to confirm drop")
        raise typer.Exit(code=1)

    async def _run():
        async with engine.begin() as conn:
            await conn.execute(text(f"DROP SCHEMA IF EXISTS {tenant_id} CASCADE"))
            await conn.execute(text("DELETE FROM public.tenants WHERE id=:t"), {"t": tenant_id})

    asyncio.run(_run())


@app.command("migrate")
def migrate_one(tenant_id: str):
    """Run Alembic tenant migrations for a single tenant."""
    import os
    import subprocess

    env = {**os.environ, "TENANT": tenant_id, "DATABASE_URL": settings.DATABASE_URL}
    subprocess.check_call(["alembic", "-x", f"tenant={tenant_id}", "upgrade", "head"], env=env)
