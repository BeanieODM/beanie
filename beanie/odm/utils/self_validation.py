from functools import wraps
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


def validate_self_before(f: Callable):
    @wraps(f)
    async def wrapper(self: "DocType", *args, **kwargs):
        await self.validate_self(*args, **kwargs)
        return await f(self, *args, **kwargs)

    return wrapper
