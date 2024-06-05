import importlib
import json
import uuid
import warnings
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    Iterable,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from lazy_model import LazyModel
from pydantic import (
    ConfigDict,
    Field,
)
from pydantic.main import BaseModel
from typing_extensions import Concatenate, ParamSpec, TypeAlias

from beanis.exceptions import (
    CollectionWasNotInitialized,
)
from beanis.odm.actions import (
    EventTypes,
    wrap_with_actions,
)
from beanis.odm.interfaces.detector import ModelType
from beanis.odm.interfaces.getters import OtherGettersInterface
from beanis.odm.interfaces.inheritance import InheritanceInterface
from beanis.odm.interfaces.setters import SettersInterface
from beanis.odm.settings.base import ItemSettings
from beanis.odm.utils.dump import get_dict
from beanis.odm.utils.parsing import merge_models, parse_obj
from beanis.odm.utils.pydantic import (
    IS_PYDANTIC_V2,
    get_extra_field_info,
    get_model_dump,
    get_model_fields,
    parse_model,
)
from beanis.odm.utils.state import (
    previous_saved_state_needed,
    saved_state_needed,
)

if IS_PYDANTIC_V2:
    pass

if TYPE_CHECKING:
    pass

FindType = TypeVar("FindType", bound=Union["Document", "View"])
DocType = TypeVar("DocType", bound="Document")
P = ParamSpec("P")
R = TypeVar("R")
# can describe both sync and async, where R itself is a coroutine
AnyDocMethod: TypeAlias = Callable[Concatenate[DocType, P], R]
# describes only async
AsyncDocMethod: TypeAlias = Callable[
    Concatenate[DocType, P], Coroutine[Any, Any, R]
]
DocumentProjectionType = TypeVar("DocumentProjectionType", bound=BaseModel)


def json_schema_extra(schema: Dict[str, Any], model: Type["Document"]) -> None:
    # remove excluded fields from the json schema
    properties = schema.get("properties")
    if not properties:
        return
    for k, field in get_model_fields(model).items():
        k = field.alias or k
        if k not in properties:
            continue
        field_info = field if IS_PYDANTIC_V2 else field.field_info
        if field_info.exclude:
            del properties[k]


class MergeStrategy(str, Enum):
    local = "local"
    remote = "remote"


class Document(
    LazyModel,
    SettersInterface,
    InheritanceInterface,
    OtherGettersInterface,
):
    """
    Document Mapping class.

    Fields:

    Mapped to the PydanticObjectId class
    """

    if IS_PYDANTIC_V2:
        model_config = ConfigDict(
            json_schema_extra=json_schema_extra,
            populate_by_name=True,
        )
    else:

        class Config:
            json_encoders = {}
            allow_population_by_field_name = True
            fields = {"id": "_id"}
            schema_extra = staticmethod(json_schema_extra)

    id: Optional[str] = Field(default=None, description="Document id")
    # Settings
    _document_settings: ClassVar[Optional[ItemSettings]] = None

    # Database
    _database_major_version: ClassVar[int] = 4

    def __init__(self, *args, **kwargs) -> None:
        super(Document, self).__init__(*args, **kwargs)
        self.get_motor_collection()

    @classmethod
    async def get(
        cls: Type["DocType"],
        document_id: Any,
    ) -> Optional["DocType"]:
        """
        Get document by id, returns None if document does not exist

        :param document_id: PydanticObjectId - document id
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool - ignore cache (if it is turned on)
        :param **pymongo_kwargs: pymongo native parameters for find operation
        :return: Union["Document", None]
        """

        loaded_data = json.loads(cls.get_settings().motor_db.get(document_id))
        module_name, class_name = loaded_data["class_name"].rsplit(".", 1)
        module = importlib.import_module(module_name)

        cls_loaded = getattr(module, class_name)

        del loaded_data["class_name"]

        return cast(type(cls_loaded), parse_obj(cls_loaded, loaded_data))

    @classmethod
    async def find(cls, document_id):

        return await cls.get(document_id=document_id)

    async def insert(self: DocType) -> DocType:
        """
        Insert the document (self) to the collection
        :return: Document
        """

        return await Document.insert_one(self)

    @classmethod
    async def insert_one(
        cls: Type[DocType], document: DocType
    ) -> Optional[DocType]:
        """
        Insert one document to the collection
        :param document: Document - document to insert
        :return: DocType
        """
        if not isinstance(document, cls):
            raise TypeError(
                "Inserting document must be of the original document class"
            )
        if document.id is None:
            # TODO is ok to generate like that?
            generated_id = str(uuid.uuid4())
            document.id = generated_id
        to_save_dict = get_dict(
            document,
            to_db=True,
            keep_nulls=document.get_settings().keep_nulls,
        )
        to_save_dict["class_name"] = (
            document.__module__ + "." + document.__class__.__name__
        )
        document.get_settings().motor_db.set(
            document.id,
            json.dumps(to_save_dict),
        )
        return document

    @classmethod
    def insert_many(
        cls: Type[DocType],
        documents: Iterable[DocType],
        **pymongo_kwargs,
    ):
        """
        Insert many documents to the collection

        :param documents:  List["Document"] - documents to insert
        :return: InsertManyResult
        """
        raise Exception("NOT IMPLEMENTED")

    def save(self: DocType) -> DocType:
        """
        Update an existing model in the database or
        insert it if it does not yet exist.
        :return: None
        """

        return self.insert()

    @wrap_with_actions(EventTypes.DELETE)
    def delete(self):
        """
        Delete the document

        """

        self.get_settings().motor_db.delete(self.id)

    @classmethod
    def delete_all(
        cls,
        **pymongo_kwargs,
    ):
        """
        Delete all the documents


        :return: Optional[DeleteResult] - pymongo DeleteResult instance.
        """
        raise Exception("Not implemented")

    # State management

    @classmethod
    def use_state_management(cls) -> bool:
        """
        Is state management turned on
        :return: bool
        """
        return cls.get_settings().use_state_management

    @classmethod
    def state_management_save_previous(cls) -> bool:
        """
        Should we save the previous state after a commit to database
        :return: bool
        """
        return cls.get_settings().state_management_save_previous

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
        if self.use_state_management() and self.id is not None:
            if self.state_management_save_previous():
                self._previous_saved_state = self._saved_state

            self._saved_state = get_dict(
                self,
                to_db=True,
                keep_nulls=self.get_settings().keep_nulls,
                exclude={"revision_id"},
            )

    def get_saved_state(self) -> Optional[Dict[str, Any]]:
        """
        Saved state getter. It is protected property.
        :return: Optional[Dict[str, Any]] - saved state
        """
        return self._saved_state

    def get_previous_saved_state(self) -> Optional[Dict[str, Any]]:
        """
        Previous state getter. It is a protected property.
        :return: Optional[Dict[str, Any]] - previous state
        """
        return self._previous_saved_state

    @property
    @saved_state_needed
    def is_changed(self) -> bool:
        if self._saved_state == get_dict(
            self,
            to_db=True,
            keep_nulls=self.get_settings().keep_nulls,
            exclude={"revision_id"},
        ):
            return False
        return True

    @property
    @saved_state_needed
    @previous_saved_state_needed
    def has_changed(self) -> bool:
        if (
            self._previous_saved_state is None
            or self._previous_saved_state == self._saved_state
        ):
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
        if old_dict.keys() - new_dict.keys():
            updates = new_dict
        else:
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
            self._saved_state,  # type: ignore
            get_dict(
                self,
                to_db=True,
                keep_nulls=self.get_settings().keep_nulls,
                exclude={"revision_id"},
            ),
        )

    @saved_state_needed
    @previous_saved_state_needed
    def get_previous_changes(self) -> Dict[str, Any]:
        if self._previous_saved_state is None:
            return {}

        return self._collect_updates(
            self._previous_saved_state,
            self._saved_state,  # type: ignore
        )

    @classmethod
    def get_settings(cls) -> ItemSettings:
        """
        Get document settings, which was created on
        the initialization step

        :return: DocumentSettings class
        """
        if cls._document_settings is None:
            raise CollectionWasNotInitialized
        return cls._document_settings

    @classmethod
    def check_hidden_fields(cls):
        hidden_fields = [
            (name, field)
            for name, field in get_model_fields(cls).items()
            if get_extra_field_info(field, "hidden") is True
        ]
        if not hidden_fields:
            return
        warnings.warn(
            f"{cls.__name__}: 'hidden=True' is deprecated, please use 'exclude=True'",
            DeprecationWarning,
        )
        if IS_PYDANTIC_V2:
            for name, field in hidden_fields:
                field.exclude = True
                del field.json_schema_extra["hidden"]
            cls.model_rebuild(force=True)
        else:
            for name, field in hidden_fields:
                field.field_info.exclude = True
                del field.field_info.extra["hidden"]
                cls.__exclude_fields__[name] = True

    @wrap_with_actions(event_type=EventTypes.VALIDATE_ON_SAVE)
    async def validate_self(self, *args, **kwargs):
        # TODO: it can be sync, but needs some actions controller improvements
        if self.get_settings().validate_on_save:
            new_model = parse_model(self.__class__, get_model_dump(self))
            merge_models(self, new_model)

    @classmethod
    def get_model_type(cls) -> ModelType:
        return ModelType.Document
