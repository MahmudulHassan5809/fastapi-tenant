from starlette.requests import Request

from .settings import settings


class BaseResolver:
    async def resolve(self, request: Request) -> str | None:
        raise NotImplementedError


class HeaderResolver(BaseResolver):
    async def resolve(self, request: Request) -> str | None:
        return request.headers.get(settings.TENANT_HEADER)


class SubdomainResolver(BaseResolver):
    async def resolve(self, request: Request) -> str | None:
        if not settings.ENABLE_SUBDOMAIN_RESOLVER:
            return None
        host = request.url.hostname or ""
        parts = host.split(".")
        if len(parts) >= 3:
            return parts[0]
        return None


class PathResolver(BaseResolver):
    async def resolve(self, request: Request) -> str | None:
        # /t/{tenant}/...
        url_path = request.url.path
        prefix = settings.PATH_PREFIX.rstrip("/") + "/"
        if url_path.startswith(prefix):
            rest = url_path[len(prefix) :]
            return rest.split("/", 1)[0] or None
        return None
