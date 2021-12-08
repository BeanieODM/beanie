import asyncio
import inspect
from typing import (
    Dict,
    Optional,
    List,
    Type,
    Union,
    Tuple,
    Mapping,
    TypeVar,
    Any,
    overload,
    Set,
)
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from bson import ObjectId, DBRef
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import (
    ValidationError,
    parse_obj_as,
    PrivateAttr,
    validator,
    Field,
)
from pydantic.main import BaseModel
from pydantic.types import ClassVar
from pymongo import InsertOne
from pymongo.client_session import ClientSession
from pymongo.results import (
    DeleteResult,
    InsertManyResult,
)

from beanie.exceptions import (
    CollectionWasNotInitialized,
    ReplaceError,
    DocumentNotFound,
    RevisionIdWasChanged,
    DocumentWasNotSaved,
    NotSupported,
)
from beanie.odm.actions import EventTypes, wrap_with_actions, ActionRegistry
from beanie.odm.bulk import BulkWriter, Operation
from beanie.odm.cache import LRUCache
from beanie.odm.enums import SortDirection
from beanie.odm.fields import (
    PydanticObjectId,
    ExpressionField,
    Link,
    LinkInfo,
    LinkTypes,
    WriteRules,
    DeleteRules,
)
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.models import (
    InspectionResult,
    InspectionStatuses,
    InspectionError,
)
from beanie.odm.operators.find.comparison import In
from beanie.odm.queries.aggregation import AggregationQuery
from beanie.odm.queries.find import FindOne, FindMany
from beanie.odm.queries.update import UpdateMany
from beanie.odm.settings.general import DocumentSettings
from beanie.odm.utils.dump import get_dict
from beanie.odm.utils.self_validation import validate_self_before
from beanie.odm.utils.state import saved_state_needed, save_state_after

from pydantic.typing import get_origin

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny, DictStrAny

DocType = TypeVar("DocType", bound="Document")
DocumentProjectionType = TypeVar("DocumentProjectionType", bound=BaseModel)


class Document(BaseModel, UpdateMethods):
    """
    Document Mapping class.

    Fields:

    - `id` - MongoDB document ObjectID "_id" field.
    Mapped to the PydanticObjectId class

    Inherited from:

    - Pydantic BaseModel
    - [UpdateMethods](https://roman-right.github.io/beanie/api/interfaces/#aggregatemethods)
    """

    id: Optional[PydanticObjectId] = None

    # State
    revision_id: Optional[UUID] = Field(default=None, hidden=True)
    _previous_revision_id: Optional[UUID] = PrivateAttr(default=None)
    _saved_state: Optional[Dict[str, Any]] = PrivateAttr(default=None)

    # Relations
    _link_fields: ClassVar[Optional[Dict[str, LinkInfo]]] = None

    # Cache
    _cache: ClassVar[Optional[LRUCache]] = None

    # Settings
    _document_settings: ClassVar[Optional[DocumentSettings]] = None

    # Customization
    # Query builders could be replaced in the inherited classes
    _find_one_query_class: ClassVar[Type] = FindOne
    _find_many_query_class: ClassVar[Type] = FindMany

    # Other
    _hidden_fields: ClassVar[Set[str]] = set()

    @validator("revision_id")
    def set_revision_id(cls, revision_id):
        if not cls.get_settings().model_settings.use_revision:
            return None
        return revision_id or uuid4()

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.get_motor_collection()

    async def _sync(self) -> None:
        """
        Update local document from the database
        :return: None
        """
        if self.id is None:
            raise ValueError("Document has no id")
        new_instance: Optional[Document] = await self.get(self.id)
        if new_instance is None:
            raise DocumentNotFound(
                "Can not sync. The document is not in the database anymore."
            )
        for key, value in dict(new_instance).items():
            setattr(self, key, value)
        if self.use_state_management():
            self._save_state()

    @wrap_with_actions(EventTypes.INSERT)
    @save_state_after
    @validate_self_before
    async def insert(
        self: DocType,
        *,
        link_rule: WriteRules = WriteRules.DO_NOTHING,
        session: Optional[ClientSession] = None,
    ) -> DocType:
        """
        Insert the document (self) to the collection
        :return: Document
        """
        if link_rule == WriteRules.WRITE:
            link_fields = self.get_link_fields()
            if link_fields is not None:
                for field_info in link_fields.values():
                    value = getattr(self, field_info.field)
                    if field_info.link_type == LinkTypes.DIRECT:
                        if isinstance(value, Document):
                            await value.insert(link_rule=WriteRules.WRITE)
                    if field_info.link_type == LinkTypes.LIST:
                        for obj in value:
                            if isinstance(obj, Document):
                                await obj.insert(link_rule=WriteRules.WRITE)

        result = await self.get_motor_collection().insert_one(
            get_dict(self, to_db=True), session=session
        )
        new_id = result.inserted_id
        if not isinstance(new_id, self.__fields__["id"].type_):
            new_id = self.__fields__["id"].type_(new_id)
        self.id = new_id
        return self

    async def create(
        self: DocType,
        session: Optional[ClientSession] = None,
    ) -> DocType:
        """
        The same as self.insert()
        :return: Document
        """
        return await self.insert(session=session)

    @classmethod
    async def insert_one(
        cls: Type[DocType],
        document: DocType,
        session: Optional[ClientSession] = None,
        bulk_writer: "BulkWriter" = None,
        link_rule: WriteRules = WriteRules.DO_NOTHING,
    ) -> Optional[DocType]:
        """
        Insert one document to the collection
        :param document: Document - document to insert
        :param session: ClientSession - pymongo session
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :param link_rule: InsertRules - hot to manage link fields
        :return: DocType
        """
        if not isinstance(document, cls):
            raise TypeError(
                "Inserting document must be of the original document class"
            )
        if bulk_writer is None:
            return await document.insert(link_rule=link_rule, session=session)
        else:
            if link_rule == WriteRules.WRITE:
                raise NotSupported(
                    "Cascade insert with bulk writing not supported"
                )
            bulk_writer.add_operation(
                Operation(
                    operation=InsertOne,
                    first_query=get_dict(document, to_db=True),
                    object_class=type(document),
                )
            )
            return None

    @classmethod
    async def insert_many(
        cls: Type[DocType],
        documents: List[DocType],
        session: Optional[ClientSession] = None,
        link_rule: WriteRules = WriteRules.DO_NOTHING,
    ) -> InsertManyResult:

        """
        Insert many documents to the collection

        :param documents:  List["Document"] - documents to insert
        :param session: ClientSession - pymongo session
        :param link_rule: InsertRules - how to manage link fields
        :return: InsertManyResult
        """
        if link_rule == WriteRules.WRITE:
            raise NotSupported(
                "Cascade insert not supported for insert many method"
            )
        documents_list = [
            get_dict(document, to_db=True) for document in documents
        ]
        return await cls.get_motor_collection().insert_many(
            documents_list,
            session=session,
        )

    @classmethod
    async def get(
        cls: Type[DocType],
        document_id: PydanticObjectId,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> Optional[DocType]:
        """
        Get document by id, returns None if document does not exist

        :param document_id: PydanticObjectId - document id
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool - ignore cache (if it is turned on)
        :return: Union["Document", None]
        """
        if not isinstance(document_id, cls.__fields__["id"].type_):
            document_id = parse_obj_as(cls.__fields__["id"].type_, document_id)
        return await cls.find_one(
            {"_id": document_id},
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
        )

    @overload
    @classmethod
    def find_one(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> FindOne[DocType]:
        ...

    @overload
    @classmethod
    def find_one(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type[DocumentProjectionType],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> FindOne[DocumentProjectionType]:
        ...

    @classmethod
    def find_one(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> Union[FindOne[DocType], FindOne[DocumentProjectionType]]:
        """
        Find one document by criteria.
        Returns [FindOne](https://roman-right.github.io/beanie/api/queries/#findone) query object.
        When awaited this will either return a document or None if no document exists for the search criteria.

        :param args: *Mapping[str, Any] - search criteria
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session instance
        :param ignore_cache: bool
        :return: [FindOne](https://roman-right.github.io/beanie/api/queries/#findone) - find query instance
        """
        return cls._find_one_query_class(document_model=cls).find_one(
            *args,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
        )

    @overload
    @classmethod
    def find_many(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> FindMany[DocType]:
        ...

    @overload
    @classmethod
    def find_many(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type[DocumentProjectionType] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> FindMany[DocumentProjectionType]:
        ...

    @classmethod
    def find_many(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> Union[FindMany[DocType], FindMany[DocumentProjectionType]]:
        """
        Find many documents by criteria.
        Returns [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) query object

        :param args: *Mapping[str, Any] - search criteria
        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key or a list of (key, direction) pairs specifying the sort order for this query.
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool
        :return: [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) - query instance
        """
        return cls._find_many_query_class(document_model=cls).find_many(
            *args,
            sort=sort,
            skip=skip,
            limit=limit,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
        )

    @overload
    @classmethod
    def find(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> FindMany[DocType]:
        ...

    @overload
    @classmethod
    def find(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type[DocumentProjectionType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> FindMany[DocumentProjectionType]:
        ...

    @classmethod
    def find(
        cls: Type[DocType],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
    ) -> Union[FindMany[DocType], FindMany[DocumentProjectionType]]:
        """
        The same as find_many
        """
        return cls.find_many(
            *args,
            skip=skip,
            limit=limit,
            sort=sort,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
        )

    @overload
    @classmethod
    def find_all(
        cls: Type[DocType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: None = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> FindMany[DocType]:
        ...

    @overload
    @classmethod
    def find_all(
        cls: Type[DocType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> FindMany[DocumentProjectionType]:
        ...

    @classmethod
    def find_all(
        cls: Type[DocType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> Union[FindMany[DocType], FindMany[DocumentProjectionType]]:
        """
        Get all the documents

        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key or a list of (key, direction) pairs specifying the sort order for this query.
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session
        :return: [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) - query instance
        """
        return cls.find_many(
            {},
            skip=skip,
            limit=limit,
            sort=sort,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
        )

    @overload
    @classmethod
    def all(
        cls: Type[DocType],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> FindMany[DocType]:
        ...

    @overload
    @classmethod
    def all(
        cls: Type[DocType],
        projection_model: Type[DocumentProjectionType],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> FindMany[DocumentProjectionType]:
        ...

    @classmethod
    def all(
        cls: Type[DocType],
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> Union[FindMany[DocType], FindMany[DocumentProjectionType]]:
        """
        the same as find_all
        """
        return cls.find_all(
            skip=skip,
            limit=limit,
            sort=sort,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
        )

    @wrap_with_actions(EventTypes.REPLACE)
    @save_state_after
    @validate_self_before
    async def replace(
        self: DocType,
        ignore_revision: bool = False,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        link_rule: WriteRules = WriteRules.DO_NOTHING,
    ) -> DocType:
        """
        Fully update the document in the database

        :param session: Optional[ClientSession] - pymongo session.
        :param ignore_revision: bool - do force replace.
            Used when revision based protection is turned on.
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :return: self
        """
        if self.id is None:
            raise ValueError("Document must have an id")

        if bulk_writer is not None and link_rule != WriteRules.DO_NOTHING:
            raise NotSupported

        if link_rule == WriteRules.WRITE:
            link_fields = self.get_link_fields()
            if link_fields is not None:
                for field_info in link_fields.values():
                    value = getattr(self, field_info.field)
                    if field_info.link_type == LinkTypes.DIRECT:
                        if isinstance(value, Document):
                            await value.replace(
                                link_rule=link_rule,
                                bulk_writer=bulk_writer,
                                ignore_revision=ignore_revision,
                                session=session,
                            )
                    if field_info.link_type == LinkTypes.LIST:
                        for obj in value:
                            if isinstance(obj, Document):
                                await obj.replace(
                                    link_rule=link_rule,
                                    bulk_writer=bulk_writer,
                                    ignore_revision=ignore_revision,
                                    session=session,
                                )

        use_revision_id = self.get_settings().model_settings.use_revision
        find_query: Dict[str, Any] = {"_id": self.id}

        if use_revision_id and not ignore_revision:
            find_query["revision_id"] = self._previous_revision_id
        try:
            await self.find_one(find_query).replace_one(
                self,
                session=session,
                bulk_writer=bulk_writer,
            )
        except DocumentNotFound:
            if use_revision_id and not ignore_revision:
                raise RevisionIdWasChanged
            else:
                raise DocumentNotFound
        return self

    async def save(
        self: DocType,
        session: Optional[ClientSession] = None,
        link_rule: WriteRules = WriteRules.DO_NOTHING,
    ) -> DocType:
        """
        Update an existing model in the database or insert it if it does not yet exist.

        :param session: Optional[ClientSession] - pymongo session.
        :return: None
        """
        if link_rule == WriteRules.WRITE:
            link_fields = self.get_link_fields()
            if link_fields is not None:
                for field_info in link_fields.values():
                    value = getattr(self, field_info.field)
                    if field_info.link_type == LinkTypes.DIRECT:
                        if isinstance(value, Document):
                            await value.save(
                                link_rule=link_rule, session=session
                            )
                    if field_info.link_type == LinkTypes.LIST:
                        for obj in value:
                            if isinstance(obj, Document):
                                await obj.save(
                                    link_rule=link_rule, session=session
                                )

        try:
            return await self.replace(session=session)
        except (ValueError, DocumentNotFound):
            return await self.insert(session=session)

    @saved_state_needed
    @wrap_with_actions(EventTypes.SAVE_CHANGES)
    @validate_self_before
    async def save_changes(
        self,
        ignore_revision: bool = False,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
    ) -> None:
        """
        Save changes.
        State management usage must be turned on

        :param ignore_revision: bool - ignore revision id, if revision is turned on
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :return: None
        """
        if not self.is_changed:
            return None
        changes = self.get_changes()
        await self.set(
            changes,  # type: ignore #TODO fix typing
            ignore_revision=ignore_revision,
            session=session,
            bulk_writer=bulk_writer,
        )

    @classmethod
    async def replace_many(
        cls: Type[DocType],
        documents: List[DocType],
        session: Optional[ClientSession] = None,
    ) -> None:
        """
        Replace list of documents

        :param documents: List["Document"]
        :param session: Optional[ClientSession] - pymongo session.
        :return: None
        """
        ids_list = [document.id for document in documents]
        if await cls.find(In(cls.id, ids_list)).count() != len(ids_list):
            raise ReplaceError(
                "Some of the documents are not exist in the collection"
            )
        await cls.find(In(cls.id, ids_list), session=session).delete()
        await cls.insert_many(documents, session=session)

    @save_state_after
    async def update(
        self,
        *args,
        ignore_revision: bool = False,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
    ) -> None:
        """
        Partially update the document in the database

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :param ignore_revision: bool - force update. Will update even if revision id is not the same, as stored
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :return: None
        """
        use_revision_id = self.get_settings().model_settings.use_revision

        find_query: Dict[str, Any] = {"_id": self.id}

        if use_revision_id and not ignore_revision:
            find_query["revision_id"] = self._previous_revision_id

        result = await self.find_one(find_query).update(
            *args, session=session, bulk_writer=bulk_writer
        )

        if (
            use_revision_id
            and not ignore_revision
            and result.modified_count == 0
        ):
            raise RevisionIdWasChanged
        await self._sync()

    @classmethod
    def update_all(
        cls,
        *args: Union[dict, Mapping],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
    ) -> UpdateMany:
        """
        Partially update all the documents

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :return: UpdateMany query
        """
        return cls.find_all().update_many(
            *args, session=session, bulk_writer=bulk_writer
        )

    async def delete(
        self,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        link_rule: DeleteRules = DeleteRules.DO_NOTHING,
    ) -> Optional[DeleteResult]:
        """
        Delete the document

        :param session: Optional[ClientSession] - pymongo session.
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :param link_rule: DeleteRules - rules for link fields
        :return: Optional[DeleteResult] - pymongo DeleteResult instance.
        """

        if link_rule == DeleteRules.DELETE_LINKS:
            link_fields = self.get_link_fields()
            if link_fields is not None:
                for field_info in link_fields.values():
                    value = getattr(self, field_info.field)
                    if field_info.link_type == LinkTypes.DIRECT:
                        if isinstance(value, Document):
                            await value.delete(
                                link_rule=DeleteRules.DELETE_LINKS
                            )
                    if field_info.link_type == LinkTypes.LIST:
                        for obj in value:
                            if isinstance(obj, Document):
                                await obj.delete(
                                    link_rule=DeleteRules.DELETE_LINKS
                                )

        return await self.find_one({"_id": self.id}).delete(
            session=session, bulk_writer=bulk_writer
        )

    @classmethod
    async def delete_all(
        cls,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
    ) -> Optional[DeleteResult]:
        """
        Delete all the documents

        :param session: Optional[ClientSession] - pymongo session.
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :return: Optional[DeleteResult] - pymongo DeleteResult instance.
        """
        return await cls.find_all().delete(
            session=session, bulk_writer=bulk_writer
        )

    @overload
    @classmethod
    def aggregate(
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: None = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> AggregationQuery[Dict[str, Any]]:
        ...

    @overload
    @classmethod
    def aggregate(
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: Type[DocumentProjectionType],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> AggregationQuery[DocumentProjectionType]:
        ...

    @classmethod
    def aggregate(
        cls: Type[DocType],
        aggregation_pipeline: list,
        projection_model: Optional[Type[DocumentProjectionType]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
    ) -> Union[
        AggregationQuery[Dict[str, Any]],
        AggregationQuery[DocumentProjectionType],
    ]:
        """
        Aggregate over collection.
        Returns [AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery) query object
        :param aggregation_pipeline: list - aggregation pipeline
        :param projection_model: Type[BaseModel]
        :param session: Optional[ClientSession]
        :param ignore_cache: bool
        :return: [AggregationQuery](https://roman-right.github.io/beanie/api/queries/#aggregationquery)
        """
        return cls.find_all().aggregate(
            aggregation_pipeline=aggregation_pipeline,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
        )

    @classmethod
    async def count(cls) -> int:
        """
        Number of documents in the collections
        The same as find_all().count()

        :return: int
        """
        return await cls.find_all().count()

    # State management

    @classmethod
    def use_state_management(cls) -> bool:
        """
        Is state management turned on
        :return: bool
        """
        return cls.get_settings().model_settings.use_state_management

    def _save_state(self) -> None:
        """
        Save current document state. Internal method
        :return: None
        """
        if self.use_state_management():
            self._saved_state = get_dict(self)

    def get_saved_state(self) -> Optional[Dict[str, Any]]:
        """
        Saved state getter. It is protected property.
        :return: Optional[Dict[str, Any]] - saved state
        """
        return self._saved_state

    @classmethod
    def _parse_obj_saving_state(cls: Type[DocType], obj: Any) -> DocType:
        """
        Parse object and save state then. Internal method.
        :param obj: Any
        :return: DocType
        """
        result: DocType = cls.parse_obj(obj)
        result._save_state()
        return result

    @property  # type: ignore
    @saved_state_needed
    def is_changed(self) -> bool:
        if self._saved_state == get_dict(self, to_db=True):
            return False
        return True

    @saved_state_needed
    def get_changes(self) -> Dict[str, Any]:
        #  TODO search deeply
        changes = {}
        if self.is_changed:
            current_state = get_dict(self, to_db=True)
            for k, v in self._saved_state.items():  # type: ignore
                if v != current_state[k]:
                    changes[k] = current_state[k]
        return changes

    @saved_state_needed
    def rollback(self) -> None:
        if self.is_changed:
            for key, value in self._saved_state.items():  # type: ignore
                if key == "_id":
                    setattr(self, "id", value)
                else:
                    setattr(self, key, value)

    # Initialization

    @classmethod
    def init_cache(cls) -> None:
        """
        Init model's cache
        :return: None
        """
        if cls.get_settings().model_settings.use_cache:
            cls._cache = LRUCache(
                capacity=cls.get_settings().model_settings.cache_capacity,
                expiration_time=cls.get_settings().model_settings.cache_expiration_time,
            )

    @classmethod
    def init_fields(cls) -> None:
        """
        Init class fields
        :return: None
        """
        if cls._link_fields is None:
            cls._link_fields = {}
        for k, v in cls.__fields__.items():
            path = v.alias or v.name
            setattr(cls, k, ExpressionField(path))

            if inspect.isclass(v.type_) and issubclass(v.type_, Link):
                cls._link_fields[v.name] = LinkInfo(
                    field=v.name,
                    model_class=v.sub_fields[0].type_,  # type: ignore
                    link_type=LinkTypes.DIRECT,
                )
            if (
                inspect.isclass(get_origin(v.type_))
                and inspect.isclass(get_origin(v.outer_type_))
                and issubclass(get_origin(v.type_), Link)
                and issubclass(get_origin(v.outer_type_), list)
            ):
                cls._link_fields[v.name] = LinkInfo(
                    field=v.name,
                    model_class=v.sub_fields[0].sub_fields[0].type_,  # type: ignore
                    link_type=LinkTypes.LIST,
                )

        cls._hidden_fields = cls.get_hidden_fields()

    @classmethod
    async def init_settings(
        cls, database: AsyncIOMotorDatabase, allow_index_dropping: bool
    ) -> None:
        """
        Init document settings (collection and models)

        :param database: AsyncIOMotorDatabase - motor database
        :param allow_index_dropping: bool
        :return: None
        """
        # TODO looks ugly a little. Too many parameters transfers.
        cls._document_settings = await DocumentSettings.init(
            database=database,
            document_model=cls,
            allow_index_dropping=allow_index_dropping,
        )

    @classmethod
    def init_actions(cls):
        """
        Init event-based actions
        """
        ActionRegistry.clean_actions(cls)
        for attr in dir(cls):
            f = getattr(cls, attr)
            if inspect.isfunction(f):
                if hasattr(f, "has_action"):
                    ActionRegistry.add_action(
                        document_class=cls,
                        event_types=f.event_types,  # type: ignore
                        action_direction=f.action_direction,  # type: ignore
                        funct=f,
                    )

    @classmethod
    async def init_model(
        cls, database: AsyncIOMotorDatabase, allow_index_dropping: bool
    ) -> None:
        """
        Init wrapper
        :param database: AsyncIOMotorDatabase
        :param allow_index_dropping: bool
        :return: None
        """
        await cls.init_settings(
            database=database, allow_index_dropping=allow_index_dropping
        )
        cls.init_fields()
        cls.init_cache()
        cls.init_actions()

    # Other

    @classmethod
    def get_settings(cls) -> DocumentSettings:
        """
        Get document settings, which was created on
        the initialization step

        :return: DocumentSettings class
        """
        if cls._document_settings is None:
            raise CollectionWasNotInitialized
        return cls._document_settings

    @classmethod
    def get_motor_collection(cls) -> AsyncIOMotorCollection:
        """
        Get Motor Collection to access low level control

        :return: AsyncIOMotorCollection
        """
        collection_meta = cls.get_settings().collection_settings
        return collection_meta.motor_collection

    @classmethod
    async def inspect_collection(
        cls, session: Optional[ClientSession] = None
    ) -> InspectionResult:
        """
        Check, if documents, stored in the MongoDB collection
        are compatible with the Document schema

        :return: InspectionResult
        """
        inspection_result = InspectionResult()
        async for json_document in cls.get_motor_collection().find(
            {}, session=session
        ):
            try:
                cls.parse_obj(json_document)
            except ValidationError as e:
                if inspection_result.status == InspectionStatuses.OK:
                    inspection_result.status = InspectionStatuses.FAIL
                inspection_result.errors.append(
                    InspectionError(
                        document_id=json_document["_id"], error=str(e)
                    )
                )
        return inspection_result

    @classmethod
    def get_hidden_fields(cls):
        return set(
            attribute_name
            for attribute_name, model_field in cls.__fields__.items()
            if model_field.field_info.extra.get("hidden") is True
        )

    def dict(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        """
        Overriding of the respective method from Pydantic
        Hides fields, marked as "hidden
        """
        if exclude is None:
            exclude = self._hidden_fields
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    @wrap_with_actions(event_type=EventTypes.VALIDATE_ON_SAVE)
    async def validate_self(self):
        # TODO it can be sync, but needs some actions controller improvements
        if self.get_settings().model_settings.validate_on_save:
            self.parse_obj(self)

    def to_ref(self):
        if self.id is None:
            raise DocumentWasNotSaved("Can not create dbref without id")
        return DBRef(self.get_motor_collection().name, self.id)

    async def fetch_link(self, field: Union[str, Any]):
        ref_obj = getattr(self, field, None)
        if isinstance(ref_obj, Link):
            value = await ref_obj.fetch()
            setattr(self, field, value)
        if isinstance(ref_obj, list) and ref_obj:
            values = await Link.fetch_list(ref_obj)
            setattr(self, field, values)

    async def fetch_all_links(self):
        coros = []
        link_fields = self.get_link_fields()
        if link_fields is not None:
            for ref in link_fields.values():
                coros.append(self.fetch_link(ref.field))  # TODO lists
        await asyncio.gather(*coros)

    @classmethod
    def get_link_fields(cls) -> Optional[Dict[str, LinkInfo]]:
        return cls._link_fields

    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
        }
        allow_population_by_field_name = True
        fields = {"id": "_id"}

        @staticmethod
        def schema_extra(
            schema: Dict[str, Any], model: Type["Document"]
        ) -> None:
            for field_name in model._hidden_fields:
                schema.get("properties", {}).pop(field_name, None)
