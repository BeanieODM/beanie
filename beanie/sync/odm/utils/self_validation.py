from functools import wraps
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from beanie.sync.odm.documents import DocType


def validate_self_before(f: Callable):
    @wraps(f)
    def wrapper(self: "DocType", *args, **kwargs):
        self.validate_self(*args, **kwargs)
        return f(self, *args, **kwargs)

    return wrapper
