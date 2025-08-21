# tests/test_fastapi_tenant.py
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from src.fastapi_tenant import db
from src.fastapi_tenant.middleware import (
    HeaderResolver,
    PathResolver,
    SubdomainResolver,
    TenantMiddlewareChain,
)
from src.fastapi_tenant.tenant_context import Tenants


# Patch settings and SessionLocal for all tests
@pytest.fixture(autouse=True)
def patch_settings_and_session():
    with (
        patch.object(
            db.settings, "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/testdb"
        ),
        patch.object(db, "SessionLocal", return_value=AsyncMock()) as mock_session,
    ):
        yield mock_session


@pytest.mark.asyncio
async def test_tenant_context_set_and_get():
    assert Tenants.current() is None
    Tenants.set("tenant1")
    assert Tenants.current() == "tenant1"


@pytest.mark.asyncio
async def test_set_search_path_calls_execute():
    session = AsyncMock()
    await db._set_search_path(session, "tenant1")
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_tenant_session_yields_session():
    session_mock = AsyncMock()
    # Make async context manager return session_mock
    session_cm = AsyncMock()
    session_cm.__aenter__.return_value = session_mock
    with patch.object(db, "SessionLocal", return_value=session_cm):
        async with db.tenant_session("tenant1") as session:
            # Now session is session_mock
            assert session == session_mock


@pytest.mark.asyncio
async def test_header_resolver_returns_header_value():
    req = MagicMock(Request)
    req.headers = {"X-Tenant-ID": "tenant-header"}
    resolver = HeaderResolver()
    tenant = await resolver.resolve(req)
    assert tenant == "tenant-header"


@pytest.mark.asyncio
async def test_path_resolver_returns_tenant_from_path():
    req = MagicMock(Request)
    req.url.path = "/t/tenant123/some/other"
    resolver = PathResolver()
    tenant = await resolver.resolve(req)
    assert tenant == "tenant123"


@pytest.mark.asyncio
async def test_subdomain_resolver_returns_subdomain(monkeypatch):
    class DummyRequest:
        url = type("Url", (), {"hostname": "tenant.example.com"})

    monkeypatch.setattr(db.settings, "ENABLE_SUBDOMAIN_RESOLVER", True)
    resolver = SubdomainResolver()
    tenant = await resolver.resolve(DummyRequest())
    assert tenant == "tenant"


@pytest.mark.asyncio
async def test_tenant_middleware_chain_sets_tenant():
    call_next = AsyncMock()
    req = MagicMock(Request)
    req.headers = {"X-Tenant-ID": "tenant1"}

    middleware = TenantMiddlewareChain(lambda r: None)
    await middleware.dispatch(req, call_next)
    assert Tenants.current() == "tenant1"
