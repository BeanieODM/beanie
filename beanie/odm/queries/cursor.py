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

    def __aiter__(self):
        return self

    async def __anext__(self) -> CursorResultType:
        if self.motor_cursor is None:
            raise RuntimeError("self.motor_cursor was not set")
        if getattr(self, "cursor", None) is None:
            self.cursor = self.motor_cursor
        next_item = await self.cursor.__anext__()
        projection = self.get_projection_model()
        return (
            projection.parse_obj(next_item)
            if projection is not None
            else next_item
        )  # type: ignore

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
        motor_list: List[Dict[str, Any]] = await self.motor_cursor.to_list(
            length
        )
        projection = self.get_projection_model()
        if projection is not None:
            return cast(
                List[CursorResultType],
                [projection.parse_obj(i) for i in motor_list],
            )
        return cast(List[CursorResultType], motor_list)
