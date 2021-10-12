from abc import abstractmethod


from beanie.odm.bulk import BulkWriter, Operation
from beanie.odm.utils.encoder import bson_encoder
from typing import (
    Callable,
    List,
    Type,
    TYPE_CHECKING,
    Optional,
    Mapping,
    Any,
    Dict,
    Union,
    Generator,
)

from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult, InsertOneResult

from beanie.odm.interfaces.session import SessionMethods
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.operators.update import BaseUpdateOperator
from pymongo import UpdateOne as UpdateOnePyMongo
from pymongo import UpdateMany as UpdateManyPyMongo

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


class UpdateQuery(UpdateMethods, SessionMethods):
    """
    Update Query base class

    Inherited from:

    - [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/#sessionmethods)
    - [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods)
    """

    def __init__(
        self,
        document_model: Type["DocType"],
        find_query: Mapping[str, Any],
    ):
        self.document_model = document_model
        self.find_query = find_query
        self.update_expressions: List[Mapping[str, Any]] = []
        self.session = None
        self.is_upsert = False
        self.upsert_insert_doc: Optional["DocType"] = None
        self.encoders: Dict[Any, Callable[[Any], Any]] = {}
        self.bulk_writer: Optional[BulkWriter] = None
        collection_class = getattr(self.document_model, "Collection", None)
        if collection_class:
            self.encoders = vars(collection_class).get("bson_encoders", {})

    @property
    def update_query(self) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        for expression in self.update_expressions:
            if isinstance(expression, BaseUpdateOperator):
                query.update(expression.query)
            elif isinstance(expression, dict):
                query.update(expression)
            else:
                raise TypeError("Wrong expression type")
        return bson_encoder.encode(query, custom_encoder=self.encoders)

    def update(
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **kwargs,
    ) -> "UpdateQuery":
        """
        Provide modifications to the update query.

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: Optional[ClientSession]
        :param bulk_writer: Optional[BulkWriter]
        :return: UpdateMany query
        """
        self.set_session(session=session)
        self.update_expressions += args
        if bulk_writer:
            self.bulk_writer = bulk_writer
        return self

    def upsert(
        self,
        *args: Mapping[str, Any],
        on_insert: "DocType",
        session: Optional[ClientSession] = None,
    ) -> "UpdateQuery":
        """
        Provide modifications to the upsert query.

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param on_insert: DocType - document to insert if there is no matched
        document in the collection
        :param session: Optional[ClientSession]
        :return: UpdateMany query
        """
        self.upsert_insert_doc = on_insert  # type: ignore
        self.update(*args, session=session)
        return self

    @abstractmethod
    async def _update(self) -> UpdateResult:
        ...

    def __await__(
        self,
    ) -> Generator[Any, None, Union[UpdateResult, InsertOneResult]]:
        """
        Run the query
        :return:
        """

        update_result = yield from self._update().__await__()
        if self.upsert_insert_doc is None:
            return update_result
        else:
            if update_result is not None and update_result.matched_count == 0:
                return (
                    yield from self.document_model.insert_one(
                        document=self.upsert_insert_doc,
                        session=self.session,
                        bulk_writer=self.bulk_writer,
                    ).__await__()
                )
            else:
                return update_result


class UpdateMany(UpdateQuery):
    """
    Update Many query class

    Inherited from:

    - [UpdateQuery](https://roman-right.github.io/beanie/api/queries/#updatequery)
    """

    def update_many(
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
    ):
        """
        Provide modifications to the update query

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: Optional[ClientSession]
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :return: UpdateMany query
        """
        return self.update(*args, session=session, bulk_writer=bulk_writer)

    async def _update(self):
        if self.bulk_writer is None:
            return (
                await self.document_model.get_motor_collection().update_many(
                    self.find_query, self.update_query, session=self.session
                )
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=UpdateManyPyMongo,
                    first_query=self.find_query,
                    second_query=self.update_query,
                    object_class=self.document_model,
                )
            )


class UpdateOne(UpdateQuery):
    """
    Update One query class

    Inherited from:

    - [UpdateQuery](https://roman-right.github.io/beanie/api/queries/#updatequery)
    """

    def update_one(
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
    ):
        """
        Provide modifications to the update query. The same as `update()`

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: Optional[ClientSession]
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :return: UpdateMany query
        """
        return self.update(*args, session=session, bulk_writer=bulk_writer)

    async def _update(self):
        if not self.bulk_writer:
            return await self.document_model.get_motor_collection().update_one(
                self.find_query, self.update_query, session=self.session
            )
        else:
            self.bulk_writer.add_operation(
                Operation(
                    operation=UpdateOnePyMongo,
                    first_query=self.find_query,
                    second_query=self.update_query,
                    object_class=self.document_model,
                )
            )
