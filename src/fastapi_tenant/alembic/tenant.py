import functools
from collections.abc import Callable
from sqlalchemy import text
from alembic import op


def for_each_tenant_schema(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped():
        
        func("customer1")

    return wrapped
