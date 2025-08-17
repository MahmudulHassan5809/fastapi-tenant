from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .settings import settings
from .tenant_context import Tenants

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _set_search_path(session: AsyncSession, tenant: str):
    await session.execute(text(f"SET LOCAL search_path TO {tenant}, public"))


@asynccontextmanager
async def tenant_session(tenant: str | None = None) -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        async with session.begin():
            await _set_search_path(session, tenant or Tenants.current() or settings.DEFAULT_SCHEMA)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class _Deps:
    async def session(self):
        async with tenant_session() as s:
            yield s


tenant_session_dependency = _Deps()
