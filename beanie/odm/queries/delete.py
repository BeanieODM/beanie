from typing import Generator, Type, TYPE_CHECKING, Any, Mapping, Optional

from pymongo.results import DeleteResult

from beanie.odm.bulk import BulkWriter, Operation
from beanie.odm.interfaces.session import SessionMethods
from pymongo import DeleteOne as DeleteOnePyMongo
from pymongo import DeleteMany as DeleteManyPyMongo

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
        bulk_writer: Optional[BulkWriter] = None,
    ):
        self.document_model = document_model
        self.find_query = find_query
        self.session = None
        self.bulk_writer = bulk_writer


class DeleteMany(DeleteQuery):
    def __await__(self) -> Generator[DeleteResult, None, None]:
        """
        Run the query
        :return:
        """
        if self.bulk_writer is None:
            yield from self.document_model.get_motor_collection().delete_many(
                self.find_query, session=self.session
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=DeleteManyPyMongo,
                    first_query=self.find_query,
                    object_class=self.document_model,
                )
            )


class DeleteOne(DeleteQuery):
    def __await__(self) -> Generator[DeleteResult, None, None]:
        """
        Run the query
        :return:
        """
        if self.bulk_writer is None:
            yield from self.document_model.get_motor_collection().delete_one(
                self.find_query, session=self.session
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=DeleteOnePyMongo,
                    first_query=self.find_query,
                    object_class=self.document_model,
                )
            )
