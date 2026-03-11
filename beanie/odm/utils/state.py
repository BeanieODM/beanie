import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar, cast, overload

from typing_extensions import ParamSpec

from beanie.exceptions import StateManagementIsTurnedOff, StateNotSaved

if TYPE_CHECKING:
    from beanie import Document
    from beanie.odm.documents import AnyDocMethod, AsyncDocMethod, DocType

P = ParamSpec("P")
R = TypeVar("R")


def check_if_state_saved(self: "DocType"):
    if not self.use_state_management():
        raise StateManagementIsTurnedOff(
            "State management is turned off for this document"
        )
    if self._saved_state is None:
        raise StateNotSaved("No state was saved")


@overload
def saved_state_needed(
    f: "AsyncDocMethod[P, R]",
) -> "AsyncDocMethod[P, R]": ...
@overload
def saved_state_needed(
    f: "AnyDocMethod[P, R]",
) -> "AnyDocMethod[P, R]": ...


def saved_state_needed(
    f: "AnyDocMethod[P, Any]",
) -> "AnyDocMethod[P, Any]":
    @wraps(f)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        self = cast("Document", args[0])
        check_if_state_saved(self)
        return f(*args, **kwargs)

    @wraps(f)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        self = cast("Document", args[0])
        check_if_state_saved(self)
        return await f(*args, **kwargs)

    if inspect.iscoroutinefunction(f):
        return async_wrapper
    return sync_wrapper


def check_if_previous_state_saved(self: "DocType"):
    if not self.use_state_management():
        raise StateManagementIsTurnedOff(
            "State management is turned off for this document"
        )
    if not self.state_management_save_previous():
        raise StateManagementIsTurnedOff(
            "State management's option to save previous state is turned off for this document"
        )


@overload
def previous_saved_state_needed(
    f: "AsyncDocMethod[P, R]",
) -> "AsyncDocMethod[P, R]": ...
@overload
def previous_saved_state_needed(
    f: "AnyDocMethod[P, R]",
) -> "AnyDocMethod[P, R]": ...


def previous_saved_state_needed(
    f: "AnyDocMethod[P, Any]",
) -> "AnyDocMethod[P, Any]":
    @wraps(f)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        self = cast("Document", args[0])
        check_if_previous_state_saved(self)
        return f(*args, **kwargs)

    @wraps(f)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        self = cast("Document", args[0])
        check_if_previous_state_saved(self)
        return await f(*args, **kwargs)

    if inspect.iscoroutinefunction(f):
        return async_wrapper
    return sync_wrapper


def save_state_after(
    f: "AsyncDocMethod[P, R]",
) -> "AsyncDocMethod[P, R]":
    @wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = cast("Document", args[0])
        result = await f(*args, **kwargs)
        self._save_state()
        return result

    return wrapper
