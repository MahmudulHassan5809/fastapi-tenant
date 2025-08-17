from contextvars import ContextVar

_current: ContextVar[str | None] = ContextVar("tenant", default=None)


class Tenants:
    @staticmethod
    def set(value: str | None):
        _current.set(value)

    @staticmethod
    def current() -> str | None:
        return _current.get()

    @staticmethod
    def require() -> str:
        v = _current.get()
        if not v:
            raise RuntimeError("No tenant resolved for this request")
        return v
