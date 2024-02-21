import inspect
from functools import wraps
from typing import TYPE_CHECKING, Callable, TypeVar, overload

from typing_extensions import ParamSpec

from beanie.exceptions import StateManagementIsTurnedOff, StateNotSaved

if TYPE_CHECKING:
    from beanie.odm.documents import AsyncDocMethod, DocType, SyncDocMethod

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
    f: "AsyncDocMethod[DocType, P, R]",
) -> "AsyncDocMethod[DocType, P, R]":
    ...


@overload
def saved_state_needed(
    f: "SyncDocMethod[DocType, P, R]",
) -> "SyncDocMethod[DocType, P, R]":
    ...


def saved_state_needed(f: Callable) -> Callable:
    @wraps(f)
    def sync_wrapper(self: "DocType", *args, **kwargs):
        check_if_state_saved(self)
        return f(self, *args, **kwargs)

    @wraps(f)
    async def async_wrapper(self: "DocType", *args, **kwargs):
        check_if_state_saved(self)
        return await f(self, *args, **kwargs)

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
    f: "AsyncDocMethod[DocType, P, R]",
) -> "AsyncDocMethod[DocType, P, R]":
    ...


@overload
def previous_saved_state_needed(
    f: "SyncDocMethod[DocType, P, R]",
) -> "SyncDocMethod[DocType, P, R]":
    ...


def previous_saved_state_needed(f: Callable) -> Callable:
    @wraps(f)
    def sync_wrapper(self: "DocType", *args, **kwargs):
        check_if_previous_state_saved(self)
        return f(self, *args, **kwargs)

    @wraps(f)
    async def async_wrapper(self: "DocType", *args, **kwargs):
        check_if_previous_state_saved(self)
        return await f(self, *args, **kwargs)

    if inspect.iscoroutinefunction(f):
        return async_wrapper
    return sync_wrapper


def save_state_after(
    f: "AsyncDocMethod[DocType, P, R]",
) -> "AsyncDocMethod[DocType, P, R]":
    @wraps(f)
    async def wrapper(self: "DocType", *args: P.args, **kwargs: P.kwargs) -> R:
        result = await f(self, *args, **kwargs)
        self._save_state()
        return result

    return wrapper
