from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    cast,
)

if TYPE_CHECKING:
    from pymongo.asynchronous.command_cursor import AsyncCommandCursor
    from pymongo.asynchronous.cursor import AsyncCursor

from pydantic.main import BaseModel

from beanie.odm.utils.parsing import parse_obj

CursorResultType = TypeVar("CursorResultType")


class BaseCursorQuery(Generic[CursorResultType]):
    """
    BaseCursorQuery class. Wrapper over AsyncCursor,
    which parse result with model
    """

    cursor = None
    lazy_parse = False

    @abstractmethod
    def get_projection_model(self) -> type[BaseModel] | None: ...

    @abstractmethod
    async def get_cursor(
        self,
    ) -> "AsyncCommandCursor[dict[str, Any]] | AsyncCursor[dict[str, Any]] | None": ...

    def __aiter__(self):
        return self

    async def __anext__(self) -> CursorResultType:
        if self.cursor is None:
            self.cursor = await self.get_cursor()
            self._projection = self.get_projection_model()

        assert self.cursor is not None
        next_item = await self.cursor.__anext__()
        if self._projection is None:
            return next_item
        return parse_obj(
            self._projection, next_item, lazy_parse=self.lazy_parse
        )  # type: ignore

    @abstractmethod
    def _get_cache(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def _set_cache(self, data): ...

    async def to_list(
        self, length: int | None = None
    ) -> list[CursorResultType]:
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List[BaseModel], List[Dict[str, Any]]]
        """
        cursor = await self.get_cursor()
        pymongo_list: list[dict[str, Any]] = self._get_cache()

        if pymongo_list is None:
            pymongo_list = await cursor.to_list(length)
            self._set_cache(pymongo_list)
        projection = self.get_projection_model()
        if projection is not None:
            return cast(
                list[CursorResultType],
                [
                    parse_obj(projection, i, lazy_parse=self.lazy_parse)
                    for i in pymongo_list
                ],
            )
        return cast(list[CursorResultType], pymongo_list)
