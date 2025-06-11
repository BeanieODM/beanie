from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Optional,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from motor.motor_asyncio import (
        AsyncIOMotorCommandCursor,
        AsyncIOMotorCursor,
    )
from pydantic.main import BaseModel

from beanie.odm.utils.parsing import parse_obj

CursorResultType = TypeVar("CursorResultType")


class BaseCursorQuery(Generic[CursorResultType]):
    """
    BaseCursorQuery class. Wrapper over AsyncIOMotorCursor,
    which parse result with model
    """

    cursor = None
    lazy_parse = False

    @abstractmethod
    def get_projection_model(self) -> Optional[type[BaseModel]]: ...

    @property
    @abstractmethod
    def motor_cursor(
        self,
    ) -> Optional[
        Union[
            "AsyncIOMotorCommandCursor[dict[str, Any]]",
            "AsyncIOMotorCursor[dict[str, Any]]",
        ]
    ]: ...

    def _cursor_params(self): ...

    def __aiter__(self):
        if self.cursor is None:
            self.cursor = self.motor_cursor
        return self

    async def __anext__(self) -> CursorResultType:
        if self.cursor is None:
            raise RuntimeError("cursor was not set")
        next_item = await self.cursor.__anext__()
        projection = self.get_projection_model()
        if projection is None:
            return next_item
        return parse_obj(projection, next_item, lazy_parse=self.lazy_parse)  # type: ignore

    @abstractmethod
    def _get_cache(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def _set_cache(self, data): ...

    async def to_list(self, length: Optional[int] = None) -> list[CursorResultType]:
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List[BaseModel], List[Dict[str, Any]]]
        """
        cursor = self.motor_cursor
        if cursor is None:
            raise RuntimeError("self.motor_cursor was not set")
        motor_list: list[dict[str, Any]] = self._get_cache()

        if motor_list is None:
            motor_list = await cursor.to_list(length)
            self._set_cache(motor_list)
        projection = self.get_projection_model()
        if projection is not None:
            return cast(
                list[CursorResultType],
                [parse_obj(projection, i, lazy_parse=self.lazy_parse) for i in motor_list],
            )
        return cast(list[CursorResultType], motor_list)
