from abc import abstractmethod
from typing import Type, Optional, List, Union

from pydantic.main import BaseModel


class BaseCursorQuery:
    """
    Cursor class. Wrapper over AsyncIOMotorCursor,
    which parse result with model
    """

    def init_cursor(self, return_model: Optional[Type[BaseModel]] = None):
        self.return_model = return_model
        self.cursor = None

    @property
    @abstractmethod
    def motor_cursor(self):
        ...

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.cursor is None:
            self.cursor = self.motor_cursor
        next_item = await self.cursor.__anext__()
        return (
            self.return_model.parse_obj(next_item)
            if self.return_model
            else next_item
        )

    async def to_list(
        self, length: Optional[int] = None
    ) -> Union[List["Document"], List[dict]]:  # noqa
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List["Document"], List[dict]]
        """
        motor_list = await self.motor_cursor.to_list(length)
        if self.return_model:
            return [self.return_model.parse_obj(i) for i in motor_list]
        return motor_list
