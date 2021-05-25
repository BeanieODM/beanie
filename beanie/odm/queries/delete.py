from typing import Type, TYPE_CHECKING, Union, Dict, Any, Mapping

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
        find_query: Union[Dict[str, Any], Mapping[str, Any]],
    ):
        self.document_model = document_model
        self.find_query = find_query
        self.session = None


class DeleteMany(DeleteQuery):
    def __await__(self) -> DeleteResult:
        """
        Run the query
        :return:
        """
        yield from self.document_model.get_motor_collection().delete_many(
            self.find_query, session=self.session
        )


class DeleteOne(DeleteQuery):
    def __await__(self) -> DeleteResult:
        """
        Run the query
        :return:
        """
        yield from self.document_model.get_motor_collection().delete_one(
            self.find_query, session=self.session
        )
