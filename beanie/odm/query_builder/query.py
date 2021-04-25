from abc import abstractmethod
from typing import Optional

from beanie.odm.cursor import Cursor
from beanie.odm.query_builder.operators.find.logical import AND


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
        return self.cursor.to_list(length=length)


class FindQuery(BaseCursorQuery):
    def __init__(self, document_class):
        self.document_class = document_class
        self.expressions = []

    def find_many(self, *args):
        self.expressions += args
        return self

    @property
    def cursor(self):
        filter_query = AND(*self.expressions).query
        cursor = self.document_class.get_motor_collection().find(
            filter=filter_query,
            projection=self.document_class._get_projection(),
        )
        return Cursor(motor_cursor=cursor, model=self.document_class)
