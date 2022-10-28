import inspect
from typing import Optional, TYPE_CHECKING, List, Type, Union

from pydantic import BaseModel
from pymongo import IndexModel

from beanie.odm.union_doc import UnionDoc
from beanie.exceptions import MongoDBVersionError
from beanie.odm.actions import ActionRegistry
from beanie.odm.cache import LRUCache
from beanie.odm.documents import Document
from beanie.odm.fields import ExpressionField
from beanie.odm.settings.document import DocumentSettings
from beanie.odm.settings.union_doc import UnionDocSettings
from beanie.odm.settings.view import ViewSettings
from beanie.odm.utils.relations import detect_link
from beanie.odm.views import View


class Output(BaseModel):
    class_name: str
    collection_name: str


class Initializer:
    inited_classes: List[Type] = list()

    def __init__(
        self, database, allow_index_dropping, recreate_view, document_models
    ):
        self.database = database
        self.allow_index_dropping = allow_index_dropping
        self.recreate_view = recreate_view
        self.document_models = document_models

    def __await__(self):
        for model in self.document_models:
            yield from self.init(model).__await__()

    @staticmethod
    def init_cache(cls) -> None:
        """
        Init model's cache
        :return: None
        """
        if cls.get_settings().use_cache:
            cls._cache = LRUCache(
                capacity=cls.get_settings().cache_capacity,
                expiration_time=cls.get_settings().cache_expiration_time,
            )

    @staticmethod
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

    @staticmethod
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

    async def init_collection(self, cls):
        cls.set_database(self.database)

        document_settings = cls.get_settings()

        # register in the Union Doc

        if document_settings.union_doc is not None:
            document_settings.name = document_settings.union_doc.register_doc(
                cls
            )

        # set a name

        if not document_settings.name:
            document_settings.name = cls.__name__

        # check mongodb version
        build_info = await self.database.command({"buildInfo": 1})
        mongo_version = build_info["version"]
        major_version = int(mongo_version.split(".")[0])

        if document_settings.timeseries is not None and major_version < 5:
            raise MongoDBVersionError(
                "Timeseries are supported by MongoDB version 5 and higher"
            )

        # create motor collection
        if (
            document_settings.timeseries is not None
            and document_settings.name
            not in await self.database.list_collection_names()
        ):

            collection = await self.database.create_collection(
                **document_settings.timeseries.build_query(
                    document_settings.name
                )
            )
        else:
            collection = self.database[document_settings.name]

        cls.set_collection(collection)

    @staticmethod
    async def init_async_indexes(cls, allow_index_dropping: False):
        """
        Async indexes initializer
        """
        collection = cls.get_motor_collection()
        document_settings = cls.get_settings()

        old_indexes = (await collection.index_information()).keys()
        new_indexes = ["_id_"]

        # Indexed field wrapped with Indexed()
        found_indexes = [
            IndexModel(
                [
                    (
                        fvalue.alias,
                        fvalue.type_._indexed[0],
                    )
                ],
                **fvalue.type_._indexed[1],
            )
            for _, fvalue in cls.__fields__.items()
            if hasattr(fvalue.type_, "_indexed") and fvalue.type_._indexed
        ]

        # get indexes from the Collection class
        if document_settings.indexes:
            found_indexes += document_settings.indexes

        # create indices
        if found_indexes:
            new_indexes += await collection.create_indexes(found_indexes)

        # delete indexes
        # Only drop indexes if the user specifically allows for it
        if allow_index_dropping:
            for index in set(old_indexes) - set(new_indexes):
                await collection.drop_index(index)

    @staticmethod
    def set_default_class_vars(cls: Type[Document]):
        cls._children = dict()
        cls._parent = None
        cls._inheritance_inited = False
        cls._class_name = ""

    def init_settings(
        self, cls: Union[Type[Document], Type[View], Type[UnionDoc]]
    ):
        settings_class = getattr(cls, "Settings", None)
        settings_vars = (
            {} if settings_class is None else dict(vars(settings_class))
        )
        if issubclass(cls, Document):
            cls._document_settings = DocumentSettings.parse_obj(settings_vars)
        if issubclass(cls, View):
            cls._settings = ViewSettings.parse_obj(settings_vars)
        if issubclass(cls, UnionDoc):
            cls._settings = UnionDocSettings.parse_obj(settings_vars)

    async def init_document(self, cls: Type[Document]) -> Optional[Output]:
        if cls is Document:
            return None

        if cls not in self.inited_classes:
            self.set_default_class_vars(cls)
            self.init_settings(cls)

            bases = [b for b in cls.__bases__]
            if len(bases) > 1:
                return None
            if cls.get_settings().is_root:
                return Output(
                    class_name=cls.__name__,
                    collection_name=cls.get_collection_name(),
                )
            parent = bases[0]
            output = await self.init_document(parent)
            if output is None:
                return None
            output.class_name = f"{output.class_name}.{cls.__name__}"
            cls._class_name = output.class_name
            cls.set_collection_name(output.collection_name)
            parent._children[cls._class_name] = cls
            cls._parent = parent
            cls._inheritance_inited = True

            await self.init_collection(cls)
            await self.init_async_indexes(cls)
            self.init_fields(cls)
            self.init_cache(cls)
            self.init_actions(cls)

            self.inited_classes.append(cls)

            return output

        else:
            return Output(
                class_name=cls._class_name,
                collection_name=cls.get_collection_name(),
            )

    async def init_view(self, cls: Type[View]):
        self.init_settings(cls)
        cls.init_collection(self.database)
        cls.init_fields()

        collection_names = await self.database.list_collection_names()
        if self.recreate_view or cls._settings.name not in collection_names:
            if cls._settings.name in collection_names:
                await cls.get_motor_collection().drop()

            await self.database.command(
                {
                    "create": cls.get_settings().name,
                    "viewOn": cls.get_settings().source,
                    "pipeline": cls.get_settings().pipeline,
                }
            )

    async def init_union_doc(self, cls: Type[UnionDoc]):
        self.init_settings(cls)
        cls.init_collection(self.database)
        cls._is_inited = True

    async def init(
        self, cls: Union[Type[Document], Type[View], Type[UnionDoc]]
    ):
        if issubclass(cls, Document):
            await self.init_document(cls)

        if issubclass(cls, View):
            await self.init_view(cls)

        if issubclass(cls, UnionDoc):
            await self.init_union_doc(cls)
