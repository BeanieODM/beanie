from functools import wraps
from typing import TYPE_CHECKING, TypeVar, cast

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from beanie import Document
    from beanie.odm.documents import AsyncDocMethod

P = ParamSpec("P")
R = TypeVar("R")


def validate_self_before(
    f: "AsyncDocMethod[P, R]",
) -> "AsyncDocMethod[P, R]":
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = cast(Document, args[0])
        await self.validate_self()
        return await f(*args, **kwargs)

    return wrapper
