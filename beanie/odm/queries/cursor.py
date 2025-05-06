from abc import abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic.main import BaseModel
from pymongo.asynchronous.command_cursor import AsyncCommandCursor
from pymongo.asynchronous.cursor import AsyncCursor

from beanie.odm.utils.parsing import parse_obj

CursorResultType = TypeVar("CursorResultType")
CursorType = Union[
    AsyncCursor[Dict[str, Any]], AsyncCommandCursor[Dict[str, Any]]
]


class BaseCursorQuery(Generic[CursorResultType]):
    """
    BaseCursorQuery class. Wrapper over AsyncCursor,
    which parse result with model
    """

    cursor = None
    lazy_parse = False

    @abstractmethod
    def get_projection_model(self) -> Optional[Type[BaseModel]]: ...

    @abstractmethod
    async def get_cursor(
        self,
    ) -> CursorType: ...

    def __aiter__(self):
        return self

    async def __anext__(self) -> Any:
        if self.cursor is None:
            self.cursor = await self.get_cursor()
        next_item = await self.cursor.__anext__()
        projection = self.get_projection_model()
        if projection is None:
            return next_item
        return parse_obj(projection, next_item, lazy_parse=self.lazy_parse)

    @abstractmethod
    def _get_cache(self) -> Optional[Any]: ...

    @abstractmethod
    def _set_cache(self, data: Any) -> None: ...

    async def to_list(
        self, length: Optional[int] = None
    ) -> List[CursorResultType]:
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: List[CursorResultType]
        """
        cursor = await self.get_cursor()
        pymongo_list = self._get_cache()

        if pymongo_list is None:
            pymongo_list = await cursor.to_list(length)
            self._set_cache(pymongo_list)
        projection = self.get_projection_model()
        if projection is not None:
            return cast(
                List[CursorResultType],
                [
                    parse_obj(projection, i, lazy_parse=self.lazy_parse)
                    for i in pymongo_list
                ],
            )
        return cast(List[CursorResultType], pymongo_list)
