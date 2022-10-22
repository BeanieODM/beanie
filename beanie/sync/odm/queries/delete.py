from typing import (
    Type,
    TYPE_CHECKING,
    Any,
    Mapping,
    Optional,
    Dict,
    Union,
)

from pymongo.results import DeleteResult

from beanie.sync.odm.bulk import BulkWriter, Operation
from beanie.sync.odm.interfaces.run import RunInterface
from beanie.sync.odm.interfaces.session import SessionMethods
from pymongo import DeleteOne as DeleteOnePyMongo
from pymongo import DeleteMany as DeleteManyPyMongo

if TYPE_CHECKING:
    from beanie.sync.odm.documents import DocType


class DeleteQuery(SessionMethods, RunInterface):
    """
    Deletion Query
    """

    def __init__(
        self,
        document_model: Type["DocType"],
        find_query: Mapping[str, Any],
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs
    ):
        self.document_model = document_model
        self.find_query = find_query
        self.session = None
        self.bulk_writer = bulk_writer
        self.pymongo_kwargs: Dict[str, Any] = pymongo_kwargs


class DeleteMany(DeleteQuery):
    def run(self) -> Union[DeleteResult, None, Optional[DeleteResult]]:
        """
        Run the query
        :return:
        """
        if self.bulk_writer is None:
            return self.document_model.get_motor_collection().delete_many(
                self.find_query, session=self.session, **self.pymongo_kwargs
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=DeleteManyPyMongo,
                    first_query=self.find_query,
                    object_class=self.document_model,
                )
            )
            return None


class DeleteOne(DeleteQuery):
    def run(self) -> Union[DeleteResult, None, Optional[DeleteResult]]:
        """
        Run the query
        :return:
        """
        if self.bulk_writer is None:
            return self.document_model.get_motor_collection().delete_one(
                self.find_query, session=self.session, **self.pymongo_kwargs
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=DeleteOnePyMongo,
                    first_query=self.find_query,
                    object_class=self.document_model,
                )
            )
            return None
