from abc import abstractmethod
from typing import Optional, Union, List


class BaseCursorQuery:
    @property
    @abstractmethod
    def cursor(self):
        ...

    async def __anext__(self):
        return self.cursor.__anext__()

    async def to_list(
        self, length: Optional[int] = None
    ) -> Union[List["Document"], List[dict]]:  # noqa
        """
        Get list of documents

        :param length: Optional[int] - length of the list
        :return: Union[List["Document"], List[dict]]
        """
        return await self.cursor.to_list(length=length)
