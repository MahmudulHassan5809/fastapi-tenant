from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .settings import settings
from .tenant_context import Tenants

Base = declarative_base()


engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _set_search_path(session: AsyncSession, tenant: str):
    await session.execute(text(f'SET search_path TO "{tenant}", public'))


@asynccontextmanager
async def tenant_session(tenant: str | None = None) -> AsyncIterator[AsyncSession]:
    tenant = tenant or Tenants.current() or settings.DEFAULT_SCHEMA
    async with SessionLocal() as session:
        try:
            await _set_search_path(session, tenant)
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def tenant_session_dependency(tenant: str | None = None) -> AsyncIterator[AsyncSession]:
    async with tenant_session(tenant) as session:
        yield session
