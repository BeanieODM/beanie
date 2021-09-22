import inspect

from functools import wraps
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


def validate(self: "DocType"):
    if self.model_settings().validate_on_save:
        self.validate_self()


def validate_self_before(f: Callable):
    @wraps(f)
    def sync_wrapper(self: "DocType", *args, **kwargs):
        validate(self)
        return f(self, *args, **kwargs)

    @wraps(f)
    async def async_wrapper(self: "DocType", *args, **kwargs):
        validate(self)
        return await f(self, *args, **kwargs)

    if inspect.iscoroutinefunction(f):
        return async_wrapper
    return sync_wrapper
