from beanie.exceptions import (
    CollectionWasNotInitialized as CollectionWasNotInitialized,
    DocumentNotFound as DocumentNotFound,
    ReplaceError as ReplaceError,
)
from beanie.odm.enums import SortDirection as SortDirection
from beanie.odm.fields import (
    ExpressionField as ExpressionField,
    PydanticObjectId as PydanticObjectId,
)
from beanie.odm.interfaces.update import UpdateMethods as UpdateMethods
from beanie.odm.models import (
    InspectionError as InspectionError,
    InspectionResult as InspectionResult,
    InspectionStatuses as InspectionStatuses,
)
from beanie.odm.operators.find.comparison import In as In
from beanie.odm.queries.aggregation import AggregationQuery as AggregationQuery
from beanie.odm.queries.find import FindMany as FindMany, FindOne as FindOne
from beanie.odm.queries.update import UpdateMany as UpdateMany
from beanie.odm.utils.collection import (
    collection_factory as collection_factory,
)
from beanie.odm.utils.dump import get_dict as get_dict
from motor.motor_asyncio import (
    AsyncIOMotorCollection as AsyncIOMotorCollection,
    AsyncIOMotorDatabase as AsyncIOMotorDatabase,
)
from pydantic.main import BaseModel
from pymongo.client_session import ClientSession as ClientSession
from pymongo.results import (
    DeleteResult as DeleteResult,
    InsertManyResult as InsertManyResult,
    InsertOneResult as InsertOneResult,
)
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

DocType = TypeVar("DocType", bound="Document")
DocumentProjectionType = TypeVar("DocumentProjectionType", bound=BaseModel)

class Document(BaseModel, UpdateMethods):
    id: Optional[PydanticObjectId]

    def __init__(self, *args, **kwargs) -> None: ...

    async def insert(
        self, session: Optional[ClientSession] = None
    ) -> DocType: ...

    async def create(
        self, session: Optional[ClientSession] = None
    ) -> DocType: ...

    @classmethod
    async def insert_one(
        cls: Type[DocType], document: DocType, session: Optional[ClientSession] = None
    ) -> InsertOneResult: ...

    @classmethod
    async def insert_many(
        cls: Type[DocType], documents: List[DocType], session: Optional[ClientSession] = None
    ) -> InsertManyResult: ...

    @classmethod
    async def get(
        cls: Type[DocType],
        document_id: PydanticObjectId,
        session: Optional[ClientSession] = None,
    ) -> Optional[DocType]: ...

    @overload
    @classmethod
    def find_one(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], Any],
        projection_model: None = None,
        session: Optional[ClientSession] = None
    ) -> FindOne[DocType]: ...
    @overload
    @classmethod
    def find_one(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], Any],
        projection_model: Type[DocumentProjectionType],
        session: Optional[ClientSession] = None
    ) -> FindOne[DocumentProjectionType]: ...

    @overload
    @classmethod
    def find_many(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], Any],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None
    ) -> FindMany[DocType]: ...
    @overload
    @classmethod
    def find_many(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], Any],
        projection_model: Type[DocumentProjectionType] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None
    ) -> FindMany[DocumentProjectionType]: ...

    @overload
    @classmethod
    def find(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], Any],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None
    ) -> FindMany[DocType]: ...
    @overload
    @classmethod
    def find(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], Any],
        projection_model: Type[DocumentProjectionType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None
    ) -> FindMany[DocumentProjectionType]: ...

    @overload
    @classmethod
    def find_all(
        cls: Type[DocType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: None = None,
        session: Optional[ClientSession] = None,
    ) -> FindMany[DocType]: ...
    @overload
    @classmethod
    def find_all(
        cls: Type[DocType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        session: Optional[ClientSession] = None,
    ) -> FindMany[DocumentProjectionType]: ...

    @overload
    @classmethod
    def all(
        cls: Type[DocType],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> FindMany[DocType]: ...
    @overload
    @classmethod
    def all(
        cls: Type[DocType],
        projection_model: Type[DocumentProjectionType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
    ) -> FindMany[DocumentProjectionType]: ...

    async def replace(
        self, session: Optional[ClientSession] = None
    ) -> DocType: ...

    async def save(
        self, session: Optional[ClientSession] = None
    ) -> DocType: ...

    @classmethod
    async def replace_many(
        cls: Type[DocType], documents: List[DocType], session: Optional[ClientSession] = None
    ) -> None: ...

    async def update(
        self, *args, session: Optional[ClientSession] = None
    ) -> None: ...

    @classmethod
    def update_all(
        cls: Type[DocType],
        *args: Union[dict, Mapping],
        session: Optional[ClientSession] = None
    ) -> UpdateMany: ...

    async def delete(
        self, session: Optional[ClientSession] = None
    ) -> DeleteResult: ...

    @classmethod
    async def delete_all(
        cls: Type[DocType], session: Optional[ClientSession] = None
    ) -> DeleteResult: ...

    @overload
    @classmethod
    def aggregate(
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: None = None,
        session: Optional[ClientSession] = None,
    ) -> AggregationQuery[Dict[str, Any]]: ...

    @overload
    @classmethod
    def aggregate(
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: Type[DocumentProjectionType],
        session: Optional[ClientSession] = None,
    ) -> AggregationQuery[DocumentProjectionType]: ...

    @classmethod
    async def count(cls) -> int: ...

    @classmethod
    async def init_collection(
        cls: Type[DocType], database: AsyncIOMotorDatabase, allow_index_dropping: bool
    ) -> None: ...

    @classmethod
    def get_motor_collection(cls) -> AsyncIOMotorCollection: ...

    @classmethod
    async def inspect_collection(
        cls: Type[DocType], session: Optional[ClientSession] = None
    ) -> InspectionResult: ...

    class Config:
        json_encoders: Any
        allow_population_by_field_name: bool
        fields: Any
