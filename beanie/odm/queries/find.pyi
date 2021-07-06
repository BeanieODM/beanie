from beanie.exceptions import DocumentNotFound as DocumentNotFound
from beanie.odm.documents import DocType as DocType
from beanie.odm.enums import SortDirection as SortDirection
from beanie.odm.interfaces.aggregate import (
    AggregateMethods as AggregateMethods,
)
from beanie.odm.interfaces.session import SessionMethods as SessionMethods
from beanie.odm.interfaces.update import UpdateMethods as UpdateMethods
from beanie.odm.operators.find.logical import And as And
from beanie.odm.queries.aggregation import AggregationQuery as AggregationQuery
from beanie.odm.queries.cursor import BaseCursorQuery as BaseCursorQuery
from beanie.odm.queries.delete import (
    DeleteMany as DeleteMany,
    DeleteOne as DeleteOne,
    DeleteQuery as DeleteQuery,
)
from beanie.odm.queries.update import (
    UpdateMany as UpdateMany,
    UpdateOne as UpdateOne,
    UpdateQuery as UpdateQuery,
)
from beanie.odm.utils.projection import get_projection as get_projection
from pydantic import BaseModel
from pymongo.client_session import ClientSession as ClientSession
from pymongo.results import UpdateResult as UpdateResult
from typing import (
    Any,
    Coroutine,
    Dict,
    Generator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
    Generic,
)

FindQueryProjectionType = TypeVar("FindQueryProjectionType", bound=BaseModel)
FindQueryResultType = TypeVar("FindQueryResultType", bound=BaseModel)

class FindQuery(Generic[FindQueryResultType], UpdateMethods, SessionMethods):
    UpdateQueryType: Union[
        Type[UpdateQuery], Type[UpdateMany], Type[UpdateOne]
    ]
    DeleteQueryType: Union[
        Type[DeleteOne], Type[DeleteMany], Type[DeleteQuery]
    ]
    document_model: Any
    find_expressions: Any
    projection_model: Any
    session: Any
    def __init__(self, document_model: Type[DocType]) -> None: ...
    def get_filter_query(self) -> Mapping[str, Any]: ...
    def update(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = ...
    ): ...
    def upsert(
        self,
        *args: Mapping[str, Any],
        on_insert: DocType,
        session: Optional[ClientSession] = ...
    ): ...
    def delete(
        self, session: Optional[ClientSession] = ...
    ) -> Union[DeleteOne, DeleteMany]: ...
    def project(self, projection_model): ...
    def get_projection_model(self) -> Type[FindQueryResultType]: ...

class FindMany(
    FindQuery[FindQueryResultType],
    BaseCursorQuery[FindQueryResultType],
    AggregateMethods,
):
    UpdateQueryType: Any
    DeleteQueryType: Any
    sort_expressions: Any
    skip_number: int
    limit_number: int
    def __init__(self, document_model: Type[DocType]) -> None: ...
    @overload
    def find_many(
        self,
        *args: Union[Mapping[str, Any], Any],
        projection_model: None = ...,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = ...,
        session: Optional[ClientSession] = ...
    ) -> FindMany[FindQueryResultType]: ...
    @overload
    def find_many(
        self,
        *args: Union[Mapping[str, Any], Any],
        projection_model: Type[FindQueryProjectionType] = ...,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = ...,
        session: Optional[ClientSession] = ...
    ) -> FindMany[FindQueryProjectionType]: ...
    @overload
    def project(
        self, projection_model: None
    ) -> FindMany[FindQueryResultType]: ...
    @overload
    def project(
        self, projection_model: Type[FindQueryProjectionType]
    ) -> FindMany[FindQueryProjectionType]: ...
    @overload
    def find(
        self,
        *args: Union[Mapping[str, Any], Any],
        projection_model: None = ...,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = ...,
        session: Optional[ClientSession] = ...
    ) -> FindMany[FindQueryResultType]: ...
    @overload
    def find(
        self,
        *args: Union[Mapping[str, Any], Any],
        projection_model: Type[FindQueryProjectionType] = ...,
        skip: Optional[int] = ...,
        limit: Optional[int] = ...,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = ...,
        session: Optional[ClientSession] = ...
    ) -> FindMany[FindQueryProjectionType]: ...
    def sort(
        self,
        *args: Optional[
            Union[
                str, Tuple[str, SortDirection], List[Tuple[str, SortDirection]]
            ]
        ]
    ) -> FindMany[FindQueryResultType]: ...
    def skip(self, n: Optional[int]) -> FindMany[FindQueryResultType]: ...
    def limit(self, n: Optional[int]) -> FindMany[FindQueryResultType]: ...
    def update_many(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = ...
    ) -> UpdateMany: ...
    def delete_many(
        self, session: Optional[ClientSession] = ...
    ) -> DeleteMany: ...
    async def count(self) -> int: ...
    @overload
    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: None = ...,
        session: Optional[ClientSession] = ...,
    ) -> AggregationQuery[Dict[str, Any]]: ...
    @overload
    def aggregate(
        self,
        aggregation_pipeline: List[Any],
        projection_model: Type[FindQueryProjectionType],
        session: Optional[ClientSession] = ...,
    ) -> AggregationQuery[FindQueryProjectionType]: ...
    @property
    def motor_cursor(self): ...

class FindOne(FindQuery[FindQueryResultType]):
    UpdateQueryType: Any
    DeleteQueryType: Any
    @overload
    def project(
        self, projection_model: None = ...
    ) -> FindOne[FindQueryResultType]: ...
    @overload
    def project(
        self, projection_model: Type[FindQueryProjectionType]
    ) -> FindOne[FindQueryProjectionType]: ...
    @overload
    def find_one(
        self,
        *args: Union[Mapping[str, Any], Any],
        projection_model: None = ...,
        session: Optional[ClientSession] = ...
    ) -> FindOne[FindQueryResultType]: ...
    @overload
    def find_one(
        self,
        *args: Union[Mapping[str, Any], Any],
        projection_model: Type[FindQueryProjectionType],
        session: Optional[ClientSession] = ...
    ) -> FindOne[FindQueryProjectionType]: ...
    def update_one(
        self, *args: Mapping[str, Any], session: Optional[ClientSession] = ...
    ) -> UpdateOne: ...
    def delete_one(
        self, session: Optional[ClientSession] = ...
    ) -> DeleteOne: ...
    async def replace_one(
        self, document: DocType, session: Optional[ClientSession] = ...
    ) -> UpdateResult: ...
    def __await__(self) -> Generator[Coroutine, Any, FindQueryResultType]: ...
