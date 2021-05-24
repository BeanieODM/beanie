from abc import abstractmethod
from typing import Optional, List, Union, TypeVar, Type, Dict, Any

from pydantic.main import BaseModel

ProjectionModelType = TypeVar("ProjectionModelType", bound=BaseModel)


class BaseCursorQuery:
    """
    BaseCursorQuery class. Wrapper over AsyncIOMotorCursor,
    which parse result with model
    """

    @abstractmethod
    def get_projection_model(self) -> Type[ProjectionModelType]:
        ...

    @property
    @abstractmethod
    def motor_cursor(self):
        ...

    def __aiter__(self):
        return self

    async def __anext__(self) -> Union[ProjectionModelType, Dict[str, Any]]:
        if getattr(self, "cursor", None) is None:
            self.cursor = self.motor_cursor
        next_item = await self.cursor.__anext__()
        return (
            self.get_projection_model().parse_obj(next_item)
            if self.get_projection_model() is not None
            else next_item
        )

    async def to_list(
        self, length: Optional[int] = None
    ) -> Union[List[ProjectionModelType], List[Dict[str, Any]]]:  # noqa
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List[ProjectionModelType], List[Dict[str, Any]]]
        """
        motor_list = await self.motor_cursor.to_list(length)
        if self.get_projection_model() is not None:
            return [
                self.get_projection_model().parse_obj(i) for i in motor_list
            ]
        return motor_list
