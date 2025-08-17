from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .resolvers import BaseResolver, HeaderResolver, PathResolver, SubdomainResolver
from .settings import settings
from .tenant_context import Tenants


class TenantMiddlewareChain(BaseHTTPMiddleware):
    def __init__(self, app, resolvers: list[BaseResolver] | None = None):
        super().__init__(app)
        self.resolvers = resolvers or [
            HeaderResolver(),
            SubdomainResolver(),
            PathResolver(),
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        tenant = None
        for r in self.resolvers:
            tenant = await r.resolve(request)
            if tenant:
                break
        Tenants.set(tenant or settings.DEFAULT_SCHEMA)
        return await call_next(request)
