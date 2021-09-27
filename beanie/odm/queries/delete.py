from typing import Generator, Type, TYPE_CHECKING, Any, Mapping

from pymongo.results import DeleteResult

from beanie.odm.interfaces.session import SessionMethods

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


class DeleteQuery(SessionMethods):
    """
    Deletion Query
    """

    def __init__(
        self,
        document_model: Type["DocType"],
        find_query: Mapping[str, Any],
    ):
        self.document_model = document_model
        self.find_query = find_query
        self.session = None


class DeleteMany(DeleteQuery):
    def __await__(self) -> Generator[DeleteResult, None, None]:
        """
        Run the query
        :return:
        """
        yield from self.document_model.get_motor_collection().delete_many(
            self.find_query, session=self.session
        )


class DeleteOne(DeleteQuery):
    def __await__(self) -> Generator[DeleteResult, None, None]:
        """
        Run the query
        :return:
        """
        yield from self.document_model.get_motor_collection().delete_one(
            self.find_query, session=self.session
        )
