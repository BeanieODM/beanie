import asyncio
import inspect
from typing import ClassVar, AbstractSet
from typing import (
    Dict,
    Optional,
    List,
    Type,
    Union,
    Mapping,
    TypeVar,
    Any,
    Set,
)
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from bson import ObjectId, DBRef
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import (
    ValidationError,
    PrivateAttr,
    Field,
    parse_obj_as,
)
from pydantic.main import BaseModel
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
from beanie.odm.actions import (
    EventTypes,
    wrap_with_actions,
    ActionRegistry,
    ActionDirections,
)
from beanie.odm.bulk import BulkWriter, Operation
from beanie.odm.cache import Cache
from beanie.odm.fields import (
    PydanticObjectId,
    ExpressionField,
    Link,
    LinkInfo,
    LinkTypes,
    WriteRules,
    DeleteRules,
)
from beanie.odm.interfaces.aggregate import AggregateInterface
from beanie.odm.interfaces.detector import ModelType
from beanie.odm.interfaces.find import FindInterface
from beanie.odm.interfaces.getters import OtherGettersInterface
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.models import (
    InspectionResult,
    InspectionStatuses,
    InspectionError,
)
from beanie.odm.operators.find.comparison import In
from beanie.odm.queries.update import UpdateMany

# from beanie.odm.settings.general import DocumentSettings
from beanie.odm.settings.document import DocumentSettings
from beanie.odm.utils.dump import get_dict
from beanie.odm.utils.relations import detect_link
from beanie.odm.utils.self_validation import validate_self_before
from beanie.odm.utils.state import (
    saved_state_needed,
    save_state_after,
    swap_revision_after,
)

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny, DictStrAny

DocType = TypeVar("DocType", bound="Document")
DocumentProjectionType = TypeVar("DocumentProjectionType", bound=BaseModel)


class Document(
    BaseModel,
    UpdateMethods,
    FindInterface,
    AggregateInterface,
    OtherGettersInterface,
):
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
    _cache: ClassVar[Optional[Cache]] = None

    # Settings
    _document_settings: ClassVar[Optional[DocumentSettings]] = None

    # Other
    _hidden_fields: ClassVar[Set[str]] = set()

    def swap_revision(self):
        self._previous_revision_id = self.revision_id
        self.revision_id = uuid4()

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

    @classmethod
    async def get(
        cls: Type["DocType"],
        document_id: PydanticObjectId,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> Optional["DocType"]:
        """
        Get document by id, returns None if document does not exist

        :param document_id: PydanticObjectId - document id
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool - ignore cache (if it is turned on)
        :param **pymongo_kwargs: pymongo native parameters for find operation
        :return: Union["Document", None]
        """
        if not isinstance(document_id, cls.__fields__["id"].type_):
            document_id = parse_obj_as(cls.__fields__["id"].type_, document_id)
        return await cls.find_one(
            {"_id": document_id},
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
            **pymongo_kwargs,
        )

    @wrap_with_actions(EventTypes.INSERT)
    @save_state_after
    @swap_revision_after
    @validate_self_before
    async def insert(
        self: DocType,
        *,
        link_rule: WriteRules = WriteRules.DO_NOTHING,
        session: Optional[ClientSession] = None,
        skip_actions: Optional[List[Union[ActionDirections, str]]] = None,
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
                    if field_info.link_type in [
                        LinkTypes.DIRECT,
                        LinkTypes.OPTIONAL_DIRECT,
                    ]:
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
        **pymongo_kwargs,
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
            documents_list, session=session, **pymongo_kwargs
        )

    @wrap_with_actions(EventTypes.REPLACE)
    @save_state_after
    @swap_revision_after
    @validate_self_before
    async def replace(
        self: DocType,
        ignore_revision: bool = False,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        link_rule: WriteRules = WriteRules.DO_NOTHING,
        skip_actions: Optional[List[Union[ActionDirections, str]]] = None,
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
                    if field_info.link_type in [
                        LinkTypes.DIRECT,
                        LinkTypes.OPTIONAL_DIRECT,
                    ]:
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

        use_revision_id = self.get_settings().use_revision
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
        **kwargs,
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
                    if field_info.link_type in [
                        LinkTypes.DIRECT,
                        LinkTypes.OPTIONAL_DIRECT,
                    ]:
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
            return await self.replace(session=session, **kwargs)
        except (ValueError, DocumentNotFound):
            return await self.insert(session=session, **kwargs)

    @saved_state_needed
    @wrap_with_actions(EventTypes.SAVE_CHANGES)
    @validate_self_before
    async def save_changes(
        self,
        ignore_revision: bool = False,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        skip_actions: Optional[List[Union[ActionDirections, str]]] = None,
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
        **pymongo_kwargs,
    ) -> None:
        """
        Partially update the document in the database

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :param ignore_revision: bool - force update. Will update even if revision id is not the same, as stored
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :param **pymongo_kwargs: pymongo native parameters for update operation
        :return: None
        """
        use_revision_id = self.get_settings().use_revision

        find_query: Dict[str, Any] = {"_id": self.id}

        if use_revision_id and not ignore_revision:
            find_query["revision_id"] = self._previous_revision_id

        result = await self.find_one(find_query).update(
            *args, session=session, bulk_writer=bulk_writer, **pymongo_kwargs
        )

        if (
            use_revision_id
            and not ignore_revision
            and result.matched_count == 0
        ):
            raise RevisionIdWasChanged
        await self._sync()

    @classmethod
    def update_all(
        cls,
        *args: Union[dict, Mapping],
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ) -> UpdateMany:
        """
        Partially update all the documents

        :param args: *Union[dict, Mapping] - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :param **pymongo_kwargs: pymongo native parameters for find operation
        :return: UpdateMany query
        """
        return cls.find_all().update_many(
            *args, session=session, bulk_writer=bulk_writer, **pymongo_kwargs
        )

    @wrap_with_actions(EventTypes.DELETE)
    async def delete(
        self,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        link_rule: DeleteRules = DeleteRules.DO_NOTHING,
        skip_actions: Optional[List[Union[ActionDirections, str]]] = None,
        **pymongo_kwargs,
    ) -> Optional[DeleteResult]:
        """
        Delete the document

        :param session: Optional[ClientSession] - pymongo session.
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :param link_rule: DeleteRules - rules for link fields
        :param **pymongo_kwargs: pymongo native parameters for delete operation
        :return: Optional[DeleteResult] - pymongo DeleteResult instance.
        """

        if link_rule == DeleteRules.DELETE_LINKS:
            link_fields = self.get_link_fields()
            if link_fields is not None:
                for field_info in link_fields.values():
                    value = getattr(self, field_info.field)
                    if field_info.link_type in [
                        LinkTypes.DIRECT,
                        LinkTypes.OPTIONAL_DIRECT,
                    ]:
                        if isinstance(value, Document):
                            await value.delete(
                                link_rule=DeleteRules.DELETE_LINKS,
                                **pymongo_kwargs,
                            )
                    if field_info.link_type == LinkTypes.LIST:
                        for obj in value:
                            if isinstance(obj, Document):
                                await obj.delete(
                                    link_rule=DeleteRules.DELETE_LINKS,
                                    **pymongo_kwargs,
                                )

        return await self.find_one({"_id": self.id}).delete(
            session=session, bulk_writer=bulk_writer, **pymongo_kwargs
        )

    @classmethod
    async def delete_all(
        cls,
        session: Optional[ClientSession] = None,
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs,
    ) -> Optional[DeleteResult]:
        """
        Delete all the documents

        :param session: Optional[ClientSession] - pymongo session.
        :param bulk_writer: "BulkWriter" - Beanie bulk writer
        :param **pymongo_kwargs: pymongo native parameters for delete operation
        :return: Optional[DeleteResult] - pymongo DeleteResult instance.
        """
        return await cls.find_all().delete(
            session=session, bulk_writer=bulk_writer, **pymongo_kwargs
        )

    # State management

    @classmethod
    def use_state_management(cls) -> bool:
        """
        Is state management turned on
        :return: bool
        """
        return cls.get_settings().use_state_management

    @classmethod
    def state_management_replace_objects(cls) -> bool:
        """
        Should objects be replaced when using state management
        :return: bool
        """
        return cls.get_settings().state_management_replace_objects

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
        result.swap_revision()
        return result

    @property  # type: ignore
    @saved_state_needed
    def is_changed(self) -> bool:
        if self._saved_state == get_dict(self, to_db=True):
            return False
        return True

    def _collect_updates(
        self, old_dict: Dict[str, Any], new_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compares old_dict with new_dict and returns field paths that have been updated
        Args:
            old_dict: dict1
            new_dict: dict2

        Returns: dictionary with updates

        """
        updates = {}

        for field_name, field_value in new_dict.items():
            if field_value != old_dict.get(field_name):
                if not self.state_management_replace_objects() and (
                    isinstance(field_value, dict)
                    and isinstance(old_dict.get(field_name), dict)
                ):
                    if old_dict.get(field_name) is None:
                        updates[field_name] = field_value
                    elif isinstance(field_value, dict) and isinstance(
                        old_dict.get(field_name), dict
                    ):

                        field_data = self._collect_updates(
                            old_dict.get(field_name),  # type: ignore
                            field_value,
                        )

                        for k, v in field_data.items():
                            updates[f"{field_name}.{k}"] = v
                else:
                    updates[field_name] = field_value

        return updates

    @saved_state_needed
    def get_changes(self) -> Dict[str, Any]:
        return self._collect_updates(
            self._saved_state, get_dict(self, to_db=True)  # type: ignore
        )

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
        if cls.get_settings().use_cache:
            cls._cache = cls.get_settings().cache_system

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

            link_info = detect_link(v)
            if link_info is not None:
                cls._link_fields[v.name] = link_info

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
        exclude_hidden: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        """
        Overriding of the respective method from Pydantic
        Hides fields, marked as "hidden
        """
        if exclude_hidden:
            if isinstance(exclude, AbstractSet):
                exclude = {*self._hidden_fields, *exclude}
            elif isinstance(exclude, Mapping):
                exclude = dict(
                    {k: True for k in self._hidden_fields}, **exclude
                )  # type: ignore
            elif exclude is None:
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
    async def validate_self(self, *args, **kwargs):
        # TODO it can be sync, but needs some actions controller improvements
        if self.get_settings().validate_on_save:
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

    @classmethod
    def get_model_type(cls) -> ModelType:
        return ModelType.Document

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

    @classmethod
    async def distinct(
            cls,
            key: str,
            filter: Optional[Mapping[str, Any]] = None,
            session: Optional[ClientSession] = None,
            **kwargs: Any
    ) -> list:
        return await cls.get_motor_collection().distinct(key, filter, session, **kwargs)
