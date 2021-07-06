from typing import (
    Generator,
    Union,
    Optional,
    List,
    Tuple,
    Type,
    Mapping,
    TYPE_CHECKING,
    Dict,
    Any,
    cast,
    Generic,
    Coroutine,
    overload,
    TypeVar,
)

from pydantic import BaseModel
from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult

from beanie.exceptions import DocumentNotFound
from beanie.odm.enums import SortDirection
from beanie.odm.interfaces.aggregate import AggregateMethods
from beanie.odm.interfaces.session import SessionMethods
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.operators.find.logical import And
from beanie.odm.queries.aggregation import AggregationQuery
from beanie.odm.queries.cursor import BaseCursorQuery
from beanie.odm.queries.delete import (
    DeleteQuery,
    DeleteMany,
    DeleteOne,
)
from beanie.odm.queries.update import (
    UpdateQuery,
    UpdateMany,
    UpdateOne,
)
from beanie.odm.utils.projection import get_projection

if TYPE_CHECKING:
    from beanie.odm.documents import DocType

FindQueryProjectionType = TypeVar("FindQueryProjectionType", bound=BaseModel)
FindQueryResultType = TypeVar("FindQueryResultType", bound=BaseModel)


class FindQuery(Generic[FindQueryResultType], UpdateMethods, SessionMethods):
    """
    Find Query base class

    Inherited from:

    - [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/#sessionmethods)
    - [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods)
    """

    UpdateQueryType: Union[
        Type[UpdateQuery], Type[UpdateMany], Type[UpdateOne]
    ] = UpdateQuery
    DeleteQueryType: Union[
        Type[DeleteOne], Type[DeleteMany], Type[DeleteQuery]
    ] = DeleteQuery

    def __init__(self, document_model: Type["DocType"]):
        self.document_model: Type["DocType"] = document_model
        self.find_expressions: List[Mapping[str, Any]] = []
        self.projection_model: Type[FindQueryResultType] = cast(
            Type[FindQueryResultType], self.document_model
        )
        self.session = None

    def get_filter_query(self) -> Mapping[str, Any]:
        if self.find_expressions:
            return And(*self.find_expressions)
        else:
            return {}

    def update(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = None
    ):
        """
        Create Update with modifications query
        and provide search criteria there

        :param args: *Mapping[str,Any] - the modifications to apply.
        :param session: Optional[ClientSession]
        :return: UpdateMany query
        """
        self.set_session(session)
        return (
            self.UpdateQueryType(
                document_model=self.document_model,
                find_query=self.get_filter_query(),
            )
            .update(*args)
            .set_session(session=self.session)
        )

    def upsert(
        self,
        *args: Mapping[str, Any],
        on_insert: "DocType",
        session: Optional[ClientSession] = None,
    ):
        """
        Create Update with modifications query
        and provide search criteria there

        :param args: *Mapping[str,Any] - the modifications to apply.
        :param on_insert: DocType - document to insert if there is no matched
        document in the collection
        :param session: Optional[ClientSession]
        :return: UpdateMany query
        """
        self.set_session(session)
        return (
            self.UpdateQueryType(
                document_model=self.document_model,
                find_query=self.get_filter_query(),
            )
            .upsert(*args, on_insert=on_insert)
            .set_session(session=self.session)
        )

    def delete(
        self, session: Optional[ClientSession] = None
    ) -> Union[DeleteOne, DeleteMany]:
        """
        Provide search criteria to the Delete query

        :param session: Optional[ClientSession]
        :return: Union[DeleteOne, DeleteMany]
        """
        self.set_session(session=session)
        return self.DeleteQueryType(
            document_model=self.document_model,
            find_query=self.get_filter_query(),
        ).set_session(session=session)

    def project(
        self,
        projection_model,
    ):
        """
        Apply projection parameter
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :return: self
        """
        if projection_model is not None:
            self.projection_model = projection_model
        return self

    def get_projection_model(self) -> Type[FindQueryResultType]:
        return self.projection_model


class FindMany(
    FindQuery[FindQueryResultType],
    BaseCursorQuery[FindQueryResultType],
    AggregateMethods,
):
    """
    Find Many query class

    Inherited from:

    - [FindQuery](https://roman-right.github.io/beanie/api/queries/#findquery)
    - [BaseCursorQuery](https://roman-right.github.io/beanie/api/queries/#basecursorquery) - async generator
    - [AggregateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods)

    """

    UpdateQueryType = UpdateMany
    DeleteQueryType = DeleteMany

    def __init__(self, document_model: Type["DocType"]):
        super(FindMany, self).__init__(document_model=document_model)
        self.sort_expressions: List[Tuple[str, SortDirection]] = []
        self.skip_number: int = 0
        self.limit_number: int = 0

    @overload
    def find_many(
        self: "FindMany[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> "FindMany[FindQueryResultType]":
        ...

    @overload
    def find_many(
        self: "FindMany[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type[FindQueryProjectionType] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> "FindMany[FindQueryProjectionType]":
        ...

    def find_many(
        self: "FindMany[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type[FindQueryProjectionType]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> Union[
        "FindMany[FindQueryResultType]", "FindMany[FindQueryProjectionType]"
    ]:
        """
        Find many documents by criteria

        :param args: *Mapping[str, Any] - search criteria
        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key
        or a list of (key, direction) pairs specifying the sort order
        for this query.
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session
        :return: FindMany - query instance
        """
        self.find_expressions += args  # type: ignore # bool workaround
        self.skip(skip)
        self.limit(limit)
        self.sort(sort)
        self.project(projection_model)
        self.set_session(session=session)
        return self

    # TODO probably merge FindOne and FindMany to one class to avoid this
    #  code duplication

    @overload
    def project(
        self: "FindMany",
        projection_model: None,
    ) -> "FindMany[FindQueryResultType]":
        ...

    @overload
    def project(
        self: "FindMany",
        projection_model: Type[FindQueryProjectionType],
    ) -> "FindMany[FindQueryProjectionType]":
        ...

    def project(
        self: "FindMany",
        projection_model: Optional[Type[FindQueryProjectionType]],
    ) -> Union[
        "FindMany[FindQueryResultType]", "FindMany[FindQueryProjectionType]"
    ]:
        """
        Apply projection parameter

        :param projection_model: Optional[Type[BaseModel]] - projection model
        :return: self
        """
        super().project(projection_model)
        return self

    @overload
    def find(
        self: "FindMany[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> "FindMany[FindQueryResultType]":
        ...

    @overload
    def find(
        self: "FindMany[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type[FindQueryProjectionType] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> "FindMany[FindQueryProjectionType]":
        ...

    def find(
        self: "FindMany[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type[FindQueryProjectionType]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> Union[
        "FindMany[FindQueryResultType]", "FindMany[FindQueryProjectionType]"
    ]:
        """
        The same as `find_many(...)`
        """
        return self.find_many(
            *args,
            skip=skip,
            limit=limit,
            sort=sort,
            projection_model=projection_model,
            session=session,
        )

    def sort(
        self,
        *args: Optional[
            Union[
                str, Tuple[str, SortDirection], List[Tuple[str, SortDirection]]
            ]
        ],
    ) -> "FindMany[FindQueryResultType]":
        """
        Add sort parameters
        :param args: Union[str, Tuple[str, SortDirection],
        List[Tuple[str, SortDirection]]] - A key or a tuple (key, direction)
        or a list of (key, direction) pairs specifying
        the sort order for this query.
        :return: self
        """
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, list):
                self.sort(*arg)
            elif isinstance(arg, tuple):
                self.sort_expressions.append(arg)
            elif isinstance(arg, str):
                if arg.startswith("+"):
                    self.sort_expressions.append(
                        (arg[1:], SortDirection.ASCENDING)
                    )
                elif arg.startswith("-"):
                    self.sort_expressions.append(
                        (arg[1:], SortDirection.DESCENDING)
                    )
                else:
                    self.sort_expressions.append(
                        (arg, SortDirection.ASCENDING)
                    )
            else:
                raise TypeError("Wrong argument type")
        return self

    def skip(self, n: Optional[int]) -> "FindMany[FindQueryResultType]":
        """
        Set skip parameter
        :param n: int
        :return: self
        """
        if n is not None:
            self.skip_number = n
        return self

    def limit(self, n: Optional[int]) -> "FindMany[FindQueryResultType]":
        """
        Set limit parameter
        :param n: int
        :return:
        """
        if n is not None:
            self.limit_number = n
        return self

    def update_many(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = None
    ) -> UpdateMany:
        """
        Provide search criteria to the
        [UpdateMany](https://roman-right.github.io/beanie/api/queries/#updatemany) query

        :param args: *Mappingp[str,Any] - the modifications to apply.
        :param session: Optional[ClientSession]
        :return: [UpdateMany](https://roman-right.github.io/beanie/api/queries/#updatemany) query
        """
        return cast(UpdateMany, self.update(*args, session=session))

    def delete_many(
        self, session: Optional[ClientSession] = None
    ) -> DeleteMany:
        """
        Provide search criteria to the [DeleteMany](https://roman-right.github.io/beanie/api/queries/#deletemany) query

        :param session:
        :return: [DeleteMany](https://roman-right.github.io/beanie/api/queries/#deletemany) query
        """
        # We need to cast here to tell mypy that we are sure about the type.
        # This is because delete may also return a DeleteOne type in general, and mypy can not be sure in this case
        # See https://mypy.readthedocs.io/en/stable/common_issues.html#narrowing-and-inner-functions
        return cast(DeleteMany, self.delete(session=session))

    async def count(self) -> int:
        """
        Number of found documents
        :return: int
        """
        return (
            await self.document_model.get_motor_collection().count_documents(
                self.get_filter_query()
            )
        )

    @overload
    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: None = None,
        session: Optional[ClientSession] = None,
    ) -> AggregationQuery[Dict[str, Any]]:
        ...

    @overload
    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: Type[FindQueryProjectionType],
        session: Optional[ClientSession] = None,
    ) -> AggregationQuery[FindQueryProjectionType]:
        ...

    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: Optional[Type[FindQueryProjectionType]] = None,
        session: Optional[ClientSession] = None,
    ) -> Union[
        AggregationQuery[Dict[str, Any]],
        AggregationQuery[FindQueryProjectionType],
    ]:
        """
        Provide search criteria to the [AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery)

        :param aggregation_pipeline: list - aggregation pipeline. MongoDB doc:
        <https://docs.mongodb.com/manual/core/aggregation-pipeline/>
        :param projection_model: Type[BaseModel] - Projection Model
        :param session: Optional[ClientSession] - PyMongo session
        :return:[AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery)
        """
        self.set_session(session=session)
        return AggregationQuery(
            aggregation_pipeline=aggregation_pipeline,
            document_model=self.document_model,
            projection_model=projection_model,
            find_query=self.get_filter_query(),
        ).set_session(session=self.session)

    @property
    def motor_cursor(self):
        return self.document_model.get_motor_collection().find(
            filter=self.get_filter_query(),
            sort=self.sort_expressions,
            projection=get_projection(self.projection_model),
            skip=self.skip_number,
            limit=self.limit_number,
            session=self.session,
        )


class FindOne(FindQuery[FindQueryResultType]):
    """
    Find One query class

    Inherited from:

    - [FindQuery](https://roman-right.github.io/beanie/api/queries/#findquery)
    """

    UpdateQueryType = UpdateOne
    DeleteQueryType = DeleteOne

    @overload
    def project(
        self: "FindOne[FindQueryResultType]",
        projection_model: None = None,
    ) -> "FindOne[FindQueryResultType]":
        ...

    @overload
    def project(
        self: "FindOne[FindQueryResultType]",
        projection_model: Type[FindQueryProjectionType],
    ) -> "FindOne[FindQueryProjectionType]":
        ...

    # TODO probably merge FindOne and FindMany to one class to avoid this
    #  code duplication

    def project(
        self: "FindOne[FindQueryResultType]",
        projection_model: Optional[Type[FindQueryProjectionType]] = None,
    ) -> Union[
        "FindOne[FindQueryResultType]", "FindOne[FindQueryProjectionType]"
    ]:
        """
        Apply projection parameter
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :return: self
        """
        super().project(projection_model)
        return self

    @overload
    def find_one(
        self: "FindOne[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        session: Optional[ClientSession] = None,
    ) -> "FindOne[FindQueryResultType]":
        ...

    @overload
    def find_one(
        self: "FindOne[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type[FindQueryProjectionType],
        session: Optional[ClientSession] = None,
    ) -> "FindOne[FindQueryProjectionType]":
        ...

    def find_one(
        self: "FindOne[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type[FindQueryProjectionType]] = None,
        session: Optional[ClientSession] = None,
    ) -> Union[
        "FindOne[FindQueryResultType]", "FindOne[FindQueryProjectionType]"
    ]:
        """
        Find one document by criteria

        :param args: *Mapping[str, Any] - search criteria
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session
        :return: FindOne - query instance
        """
        self.find_expressions += args  # type: ignore # bool workaround
        self.project(projection_model)
        self.set_session(session=session)
        return self

    def update_one(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = None
    ) -> UpdateOne:
        """
        Create [UpdateOne](https://roman-right.github.io/beanie/api/queries/#updateone) query using modifications and
        provide search criteria there
        :param args: *Mapping[str,Any] - the modifications to apply
        :param session: Optional[ClientSession] - PyMongo sessions
        :return: [UpdateOne](https://roman-right.github.io/beanie/api/queries/#updateone) query
        """
        return cast(UpdateOne, self.update(*args, session=session))

    def delete_one(self, session: Optional[ClientSession] = None) -> DeleteOne:
        """
        Provide search criteria to the [DeleteOne](https://roman-right.github.io/beanie/api/queries/#deleteone) query
        :param session: Optional[ClientSession] - PyMongo sessions
        :return: [DeleteOne](https://roman-right.github.io/beanie/api/queries/#deleteone) query
        """
        # We need to cast here to tell mypy that we are sure about the type.
        # This is because delete may also return a DeleteOne type in general, and mypy can not be sure in this case
        # See https://mypy.readthedocs.io/en/stable/common_issues.html#narrowing-and-inner-functions
        return cast(DeleteOne, self.delete(session=session))

    async def replace_one(
        self,
        document: "DocType",
        session: Optional[ClientSession] = None,
    ) -> UpdateResult:
        """
        Replace found document by provided
        :param document: Document - document, which will replace the found one
        :param session: Optional[ClientSession] - PyMongo session
        :return: UpdateResult
        """
        self.set_session(session=session)
        result: UpdateResult = (
            await self.document_model.get_motor_collection().replace_one(
                self.get_filter_query(),
                document.dict(by_alias=True, exclude={"id"}),
                session=self.session,
            )
        )

        if not result.raw_result["updatedExisting"]:
            raise DocumentNotFound
        return result

    def __await__(
        self,
    ) -> Generator[Coroutine, Any, Optional[FindQueryResultType]]:
        """
        Run the query
        :return: BaseModel
        """
        projection = get_projection(self.projection_model)
        document: Dict[str, Any] = (
            yield from self.document_model.get_motor_collection().find_one(
                filter=self.get_filter_query(),
                projection=projection,
                session=self.session,
            )
        )
        if document is None:
            return None
        return cast(
            FindQueryResultType, self.projection_model.parse_obj(document)
        )
