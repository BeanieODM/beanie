from typing import (
    List,
    Type,
    TYPE_CHECKING,
    Optional,
    Mapping,
    Any,
    Dict,
    Union,
)

from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult, InsertOneResult

from beanie.odm.interfaces.session import SessionMethods
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.operators.update import BaseUpdateOperator

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
        self.on_insert_doc: Optional["DocType"] = None

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
        return query

    def update(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = None
    ) -> "UpdateQuery":
        """
        Provide modifications to the update query.

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: Optional[ClientSession]
        :return: UpdateMany query
        """
        self.set_session(session=session)
        self.update_expressions += args
        return self

    def upsert(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = None
    ) -> "UpdateQuery":
        """
        Provide modifications to the upsert query.

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: Optional[ClientSession]
        :return: UpdateMany query
        """
        self.update(*args, session=session)
        self.is_upsert = True
        return self

    def on_insert(self, document: "DocType") -> "UpdateQuery":
        self.on_insert_doc = document
        return self


class UpdateMany(UpdateQuery):
    """
    Update Many query class

    Inherited from:

    - [UpdateQuery](https://roman-right.github.io/beanie/api/queries/#updatequery)
    """

    def update_many(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = None
    ):
        """
        Provide modifications to the update query

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: Optional[ClientSession]
        :return: UpdateMany query
        """
        return self.update(*args, session=session)

    def __await__(self) -> Union[UpdateResult, InsertOneResult]:
        """
        Run the query
        :return:
        """
        if self.is_upsert:
            if self.on_insert_doc is None:
                raise ValueError("Set the document to insert")
            if not isinstance(self.on_insert_doc, self.document_model):
                raise TypeError(
                    "Inserting document type must be the same as "
                    "original document class"
                )

        update_result = (
            yield from self.document_model.get_motor_collection().update_many(
                self.find_query, self.update_query, session=self.session
            )
        )
        if not self.is_upsert:
            return update_result
        else:
            if self.on_insert_doc is None:
                raise ValueError("Set the document to insert")
            if update_result.matched_count != 0:
                return update_result
            if update_result.matched_count == 0:
                print("HERE")
                return (
                    yield from self.document_model.insert_one(
                        document=self.on_insert_doc, session=self.session
                    ).__await__()
                )


class UpdateOne(UpdateQuery):
    """
    Update One query class

    Inherited from:

    - [UpdateQuery](https://roman-right.github.io/beanie/api/queries/#updatequery)
    """

    def update_one(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = None
    ):
        """
        Provide modifications to the update query. The same as `update()`

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: Optional[ClientSession]
        :return: UpdateMany query
        """
        return self.update(*args, session=session)

    def __await__(self) -> UpdateResult:
        """
        Run the query
        :return:
        """
        yield from self.document_model.get_motor_collection().update_one(
            self.find_query, self.update_query, session=self.session
        )
