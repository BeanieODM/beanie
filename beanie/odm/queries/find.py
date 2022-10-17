from typing import (
    Callable,
    TYPE_CHECKING,
    Any,
    Coroutine,
    Dict,
    Generator,
    Generic,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from pydantic import BaseModel
from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult

from pymongo import ReplaceOne

from beanie.exceptions import DocumentNotFound
from beanie.odm.cache import LRUCache
from beanie.odm.bulk import BulkWriter, Operation
from beanie.odm.enums import SortDirection
from beanie.odm.interfaces.aggregation_methods import AggregateMethods
from beanie.odm.interfaces.clone import CloneInterface
from beanie.odm.interfaces.session import SessionMethods
from beanie.odm.interfaces.update import UpdateMethods
from beanie.odm.operators.find.logical import And
from beanie.odm.queries.aggregation import AggregationQuery
from beanie.odm.queries.cursor import BaseCursorQuery
from beanie.odm.queries.delete import (
    DeleteMany,
    DeleteOne,
)
from beanie.odm.queries.update import (
    UpdateQuery,
    UpdateMany,
    UpdateOne,
)
from beanie.odm.utils.encoder import Encoder
from beanie.odm.utils.find import construct_lookup_queries
from beanie.odm.utils.parsing import parse_obj
from beanie.odm.utils.projection import get_projection
from beanie.odm.utils.relations import convert_ids

if TYPE_CHECKING:
    from beanie.odm.documents import DocType

FindQueryProjectionType = TypeVar("FindQueryProjectionType", bound=BaseModel)
FindQueryResultType = TypeVar("FindQueryResultType", bound=BaseModel)


class FindQuery(
    Generic[FindQueryResultType], UpdateMethods, SessionMethods, CloneInterface
):
    """
    Find Query base class

    Inherited from:

    - [SessionMethods](https://roman-right.github.io/beanie/api/interfaces/#sessionmethods)
    - [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods)
    """

    UpdateQueryType: Union[
        Type[UpdateQuery], Type[UpdateMany], Type[UpdateOne]
    ] = UpdateQuery
    DeleteQueryType: Union[Type[DeleteOne], Type[DeleteMany]] = DeleteMany
    AggregationQueryType = AggregationQuery

    def __init__(self, document_model: Type["DocType"]):
        self.document_model: Type["DocType"] = document_model
        self.find_expressions: List[Mapping[str, Any]] = []
        self.projection_model: Type[FindQueryResultType] = cast(
            Type[FindQueryResultType], self.document_model
        )
        self.session = None
        self.encoders: Dict[Any, Callable[[Any], Any]] = {}
        self.ignore_cache: bool = False
        self.encoders = self.document_model.get_bson_encoders()
        self.fetch_links: bool = False
        self.pymongo_kwargs: Dict[str, Any] = {}

    def prepare_find_expressions(self):
        if self.document_model.get_link_fields() is not None:
            for i, query in enumerate(self.find_expressions):
                self.find_expressions[i] = convert_ids(
                    query,
                    doc=self.document_model,
                    fetch_links=self.fetch_links,
                )

    def get_filter_query(self) -> Mapping[str, Any]:
        """

        Returns: MongoDB filter query

        """
        self.prepare_find_expressions()
        if self.find_expressions:
            return Encoder(custom_encoders=self.encoders).encode(
                And(*self.find_expressions).query
            )
        else:
            return {}

    def update(
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ):
        """
        Create Update with modifications query
        and provide search criteria there

        :param args: *Mapping[str,Any] - the modifications to apply.
        :param session: Optional[ClientSession]
        :param bulk_writer: Optional[BulkWriter]
        :return: UpdateMany query
        """
        self.set_session(session)
        return (
            self.UpdateQueryType(
                document_model=self.document_model,
                find_query=self.get_filter_query(),
            )
            .update(*args, bulk_writer=bulk_writer, **pymongo_kwargs)
            .set_session(session=self.session)
        )

    def upsert(
        self,
        *args: Mapping[str, Any],
        on_insert: "DocType",
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
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
            .upsert(
                *args,
                on_insert=on_insert,
                bulk_writer=bulk_writer,
                **pymongo_kwargs,
            )
            .set_session(session=self.session)
        )

    def delete(
        self,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
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
            bulk_writer=bulk_writer,
            **pymongo_kwargs,
        ).set_session(session=session)

    def project(self, projection_model):
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

    async def exists(self) -> bool:
        """
        If find query will return anything

        :return: bool
        """
        return await self.count() > 0


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
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
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
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
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
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
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
        :param ignore_cache: bool
        :param **pymongo_kwargs: pymongo native parameters for find operation (if Document class contains links, this parameter must fit the respective parameter of the aggregate MongoDB function)
        :return: FindMany - query instance
        """
        self.find_expressions += args  # type: ignore # bool workaround
        self.skip(skip)
        self.limit(limit)
        self.sort(sort)
        self.project(projection_model)
        self.set_session(session=session)
        self.ignore_cache = ignore_cache
        self.fetch_links = fetch_links
        self.pymongo_kwargs.update(pymongo_kwargs)
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
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
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
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
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
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
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
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
            **pymongo_kwargs,
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
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ) -> UpdateMany:
        """
        Provide search criteria to the
        [UpdateMany](https://roman-right.github.io/beanie/api/queries/#updatemany) query

        :param args: *Mappingp[str,Any] - the modifications to apply.
        :param session: Optional[ClientSession]
        :return: [UpdateMany](https://roman-right.github.io/beanie/api/queries/#updatemany) query
        """
        return cast(
            UpdateMany,
            self.update(
                *args,
                session=session,
                bulk_writer=bulk_writer,
                **pymongo_kwargs,
            ),
        )

    def delete_many(
        self,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ) -> DeleteMany:
        """
        Provide search criteria to the [DeleteMany](https://roman-right.github.io/beanie/api/queries/#deletemany) query

        :param session:
        :return: [DeleteMany](https://roman-right.github.io/beanie/api/queries/#deletemany) query
        """
        # We need to cast here to tell mypy that we are sure about the type.
        # This is because delete may also return a DeleteOne type in general, and mypy can not be sure in this case
        # See https://mypy.readthedocs.io/en/stable/common_issues.html#narrowing-and-inner-functions
        return cast(
            DeleteMany,
            self.delete(
                session=session, bulk_writer=bulk_writer, **pymongo_kwargs
            ),
        )

    @overload
    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: None = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> AggregationQuery[Dict[str, Any]]:
        ...

    @overload
    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: Type[FindQueryProjectionType],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> AggregationQuery[FindQueryProjectionType]:
        ...

    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: Optional[Type[FindQueryProjectionType]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
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
        :param ignore_cache: bool
        :return:[AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery)
        """
        self.set_session(session=session)
        return self.AggregationQueryType(
            aggregation_pipeline=aggregation_pipeline,
            document_model=self.document_model,
            projection_model=projection_model,
            find_query=self.get_filter_query(),
            ignore_cache=ignore_cache,
            **pymongo_kwargs,
        ).set_session(session=self.session)

    @property
    def _cache_key(self) -> str:
        return LRUCache.create_key(
            {
                "type": "FindMany",
                "filter": self.get_filter_query(),
                "sort": self.sort_expressions,
                "projection": get_projection(self.projection_model),
                "skip": self.skip_number,
                "limit": self.limit_number,
            }
        )

    def _get_cache(self):
        if (
            self.document_model.get_settings().use_cache
            and self.ignore_cache is False
        ):
            return self.document_model._cache.get(  # type: ignore
                self._cache_key
            )
        else:
            return None

    def _set_cache(self, data):
        if (
            self.document_model.get_settings().use_cache
            and self.ignore_cache is False
        ):
            return self.document_model._cache.set(  # type: ignore
                self._cache_key, data
            )

    @property
    def motor_cursor(self):
        if self.fetch_links:
            aggregation_pipeline: List[
                Dict[str, Any]
            ] = construct_lookup_queries(self.document_model)

            aggregation_pipeline.append({"$match": self.get_filter_query()})

            sort_pipeline = {
                "$sort": {i[0]: i[1] for i in self.sort_expressions}
            }
            if sort_pipeline["$sort"]:
                aggregation_pipeline.append(sort_pipeline)
            if self.skip_number != 0:
                aggregation_pipeline.append({"$skip": self.skip_number})
            if self.limit_number != 0:
                aggregation_pipeline.append({"$limit": self.limit_number})

            projection = get_projection(self.projection_model)

            if projection is not None:
                aggregation_pipeline.append({"$project": projection})

            return self.document_model.get_motor_collection().aggregate(
                aggregation_pipeline,
                session=self.session,
                **self.pymongo_kwargs,
            )

        return self.document_model.get_motor_collection().find(
            filter=self.get_filter_query(),
            sort=self.sort_expressions,
            projection=get_projection(self.projection_model),
            skip=self.skip_number,
            limit=self.limit_number,
            session=self.session,
            **self.pymongo_kwargs,
        )

    async def first_or_none(self) -> Optional[FindQueryResultType]:
        """
        Returns the first found element or None if no elements were found
        """
        res = await self.limit(1).to_list()
        if not res:
            return None
        return res[0]


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
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> "FindOne[FindQueryResultType]":
        ...

    @overload
    def find_one(
        self: "FindOne[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type[FindQueryProjectionType],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> "FindOne[FindQueryProjectionType]":
        ...

    def find_one(
        self: "FindOne[FindQueryResultType]",
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type[FindQueryProjectionType]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> Union[
        "FindOne[FindQueryResultType]", "FindOne[FindQueryProjectionType]"
    ]:
        """
        Find one document by criteria

        :param args: *Mapping[str, Any] - search criteria
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool
        :param **pymongo_kwargs: pymongo native parameters for find operation (if Document class contains links, this parameter must fit the respective parameter of the aggregate MongoDB function)
        :return: FindOne - query instance
        """
        self.find_expressions += args  # type: ignore # bool workaround
        self.project(projection_model)
        self.set_session(session=session)
        self.ignore_cache = ignore_cache
        self.fetch_links = fetch_links
        self.pymongo_kwargs.update(pymongo_kwargs)
        return self

    def update_one(
        self,
        *args: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ) -> UpdateOne:
        """
        Create [UpdateOne](https://roman-right.github.io/beanie/api/queries/#updateone) query using modifications and
        provide search criteria there
        :param args: *Mapping[str,Any] - the modifications to apply
        :param session: Optional[ClientSession] - PyMongo sessions
        :return: [UpdateOne](https://roman-right.github.io/beanie/api/queries/#updateone) query
        """
        return cast(
            UpdateOne,
            self.update(
                *args,
                session=session,
                bulk_writer=bulk_writer,
                **pymongo_kwargs,
            ),
        )

    def delete_one(
        self,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ) -> DeleteOne:
        """
        Provide search criteria to the [DeleteOne](https://roman-right.github.io/beanie/api/queries/#deleteone) query
        :param session: Optional[ClientSession] - PyMongo sessions
        :return: [DeleteOne](https://roman-right.github.io/beanie/api/queries/#deleteone) query
        """
        # We need to cast here to tell mypy that we are sure about the type.
        # This is because delete may also return a DeleteOne type in general, and mypy can not be sure in this case
        # See https://mypy.readthedocs.io/en/stable/common_issues.html#narrowing-and-inner-functions
        return cast(
            DeleteOne,
            self.delete(
                session=session, bulk_writer=bulk_writer, **pymongo_kwargs
            ),
        )

    async def replace_one(
        self,
        document: "DocType",
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
    ) -> Optional[UpdateResult]:
        """
        Replace found document by provided
        :param document: Document - document, which will replace the found one
        :param session: Optional[ClientSession] - PyMongo session
        :param bulk_writer: Optional[BulkWriter] - Beanie bulk writer
        :return: UpdateResult
        """
        self.set_session(session=session)
        if bulk_writer is None:
            result: UpdateResult = (
                await self.document_model.get_motor_collection().replace_one(
                    self.get_filter_query(),
                    Encoder(by_alias=True, exclude={"_id"}).encode(document),
                    session=self.session,
                )
            )

            if not result.raw_result["updatedExisting"]:
                raise DocumentNotFound
            return result
        else:
            bulk_writer.add_operation(
                Operation(
                    operation=ReplaceOne,
                    first_query=self.get_filter_query(),
                    second_query=Encoder(
                        by_alias=True, exclude={"_id"}
                    ).encode(document),
                    object_class=self.document_model,
                )
            )
            return None

    async def _find_one(self):
        if self.fetch_links:
            result = await self.document_model.find(
                *self.find_expressions,
                session=self.session,
                fetch_links=self.fetch_links,
                **self.pymongo_kwargs,
            ).to_list(length=1)
            if result:
                return result[0]
            else:
                return None
        return await self.document_model.get_motor_collection().find_one(
            filter=self.get_filter_query(),
            projection=get_projection(self.projection_model),
            session=self.session,
            **self.pymongo_kwargs,
        )

    def __await__(
        self,
    ) -> Generator[Coroutine, Any, Optional[FindQueryResultType]]:
        """
        Run the query
        :return: BaseModel
        """
        # projection = get_projection(self.projection_model)
        if (
            self.document_model.get_settings().use_cache
            and self.ignore_cache is False
        ):
            cache_key = LRUCache.create_key(
                "FindOne",
                self.get_filter_query(),
                self.projection_model,
                self.session,
                self.fetch_links,
            )
            document: Dict[str, Any] = self.document_model._cache.get(  # type: ignore
                cache_key
            )
            if document is None:
                document = yield from self._find_one().__await__()  # type: ignore
                self.document_model._cache.set(  # type: ignore
                    cache_key, document
                )
        else:
            document = yield from self._find_one().__await__()  # type: ignore
        if document is None:
            return None
        return cast(
            FindQueryResultType, parse_obj(self.projection_model, document)
        )
