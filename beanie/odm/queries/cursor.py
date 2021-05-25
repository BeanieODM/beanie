from abc import abstractmethod
from typing import Optional, List, Union, Type, Dict, Any

from pydantic.main import BaseModel


class BaseCursorQuery:
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

    async def __anext__(self) -> Union[BaseModel, Dict[str, Any]]:
        if getattr(self, "cursor", None) is None:
            self.cursor = self.motor_cursor
        next_item = await self.cursor.__anext__()
        projection = self.get_projection_model()
        return (
            projection.parse_obj(next_item)
            if projection is not None
            else next_item
        )

    async def to_list(
        self, length: Optional[int] = None
    ) -> Union[List[BaseModel], List[Dict[str, Any]]]:  # noqa
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List[BaseModel], List[Dict[str, Any]]]
        """
        motor_list: List[Dict[str, Any]] = await self.motor_cursor.to_list(
            length
        )
        projection = self.get_projection_model()
        if projection is not None:
            return [projection.parse_obj(i) for i in motor_list]
        return motor_list
