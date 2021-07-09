from abc import abstractmethod
from pydantic.main import BaseModel as BaseModel
from typing import List, Optional, Type, TypeVar, Generic

CursorResultType = TypeVar("CursorResultType")


class BaseCursorQuery(Generic[CursorResultType]):
    @property
    @abstractmethod
    def motor_cursor(
        self: "BaseCursorQuery"[CursorResultType]
    ):
        ...

    @abstractmethod
    def get_projection_model(
        self: "BaseCursorQuery"[CursorResultType]
    ) -> Optional[Type[BaseModel]]:
        ...

    def __aiter__(
        self: "BaseCursorQuery"[CursorResultType]
    ) -> "BaseCursorQuery"[CursorResultType]:
        ...

    async def __anext__(
        self: "BaseCursorQuery"[CursorResultType]
    ) -> CursorResultType:
        ...

    async def to_list(
        self: "BaseCursorQuery"[CursorResultType],
        length: Optional[int] = None
    ) -> List[CursorResultType]:
        ...
