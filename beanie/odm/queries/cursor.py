from abc import abstractmethod
from typing import (
    Optional,
    List,
    TypeVar,
    Type,
    Dict,
    Any,
    Generic,
    cast,
)

from pydantic.main import BaseModel
from beanie.odm.utils.parsing import parse_obj

CursorResultType = TypeVar("CursorResultType")


class BaseCursorQuery(Generic[CursorResultType]):
    """
    BaseCursorQuery class. Wrapper over AsyncIOMotorCursor,
    which parse result with model
    """

    @abstractmethod
    def get_projection_model(self) -> Optional[Type[BaseModel]]:
        ...

    @property
    @abstractmethod
    def motor_cursor(self):
        ...

    def _cursor_params(self):
        ...

    def __aiter__(self):
        return self

    async def __anext__(self) -> CursorResultType:
        if self.motor_cursor is None:
            raise RuntimeError("self.motor_cursor was not set")
        if getattr(self, "cursor", None) is None:
            self.cursor = self.motor_cursor
        next_item = await self.cursor.__anext__()
        projection = self.get_projection_model()
        if projection is None:
            return next_item
        return parse_obj(projection, next_item)  # type: ignore

    def _get_cache(self) -> List[Dict[str, Any]]:
        ...

    def _set_cache(self, data):
        ...

    async def to_list(
        self, length: Optional[int] = None
    ) -> List[CursorResultType]:  # noqa
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List[BaseModel], List[Dict[str, Any]]]
        """
        if self.motor_cursor is None:
            raise RuntimeError("self.motor_cursor was not set")
        motor_list: List[Dict[str, Any]] = self._get_cache()
        if motor_list is None:
            motor_list = await self.motor_cursor.to_list(length)
            self._set_cache(motor_list)
        projection = self.get_projection_model()
        if projection is not None:
            return cast(
                List[CursorResultType],
                [parse_obj(projection, i) for i in motor_list],
            )
        return cast(List[CursorResultType], motor_list)
