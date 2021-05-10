from abc import abstractmethod
from typing import Optional, List, Union


class BaseCursorQuery:
    """
    BaseCursorQuery class. Wrapper over AsyncIOMotorCursor,
    which parse result with model
    """

    @property
    @abstractmethod
    def motor_cursor(self):
        ...

    def __aiter__(self):
        return self

    async def __anext__(self):
        if getattr(self, "cursor", None) is None:
            self.cursor = self.motor_cursor
        next_item = await self.cursor.__anext__()
        return (
            self.projection_model.parse_obj(next_item)
            if getattr(self, "projection_model", None) is not None
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
        if getattr(self, "projection_model", None) is not None:
            return [self.projection_model.parse_obj(i) for i in motor_list]
        return motor_list
