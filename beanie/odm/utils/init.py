import importlib
import inspect
from typing import Optional, List, Type, Union

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import IndexModel
from yarl import URL

from beanie.exceptions import MongoDBVersionError
from beanie.odm.actions import ActionRegistry
from beanie.odm.cache import LRUCache
from beanie.odm.documents import DocType
from beanie.odm.documents import Document
from beanie.odm.fields import ExpressionField
from beanie.odm.interfaces.detector import ModelType
from beanie.odm.settings.document import DocumentSettings
from beanie.odm.settings.union_doc import UnionDocSettings
from beanie.odm.settings.view import ViewSettings
from beanie.odm.union_doc import UnionDoc
from beanie.odm.utils.relations import detect_link
from beanie.odm.views import View


class Output(BaseModel):
    class_name: str
    collection_name: str


class Initializer:
    def __init__(
        self,
        database: AsyncIOMotorDatabase = None,
        connection_string: Optional[str] = None,
        document_models: Optional[
            List[Union[Type["DocType"], Type["View"], str]]
        ] = None,
        allow_index_dropping: bool = False,
        recreate_views: bool = False,
    ):
        """
        Beanie initializer

        :param database: AsyncIOMotorDatabase - motor database instance
        :param connection_string: str - MongoDB connection string
        :param document_models: List[Union[Type[DocType], str]] - model classes
        or strings with dot separated paths
        :param allow_index_dropping: bool - if index dropping is allowed.
        Default False
        :return: None
        """
        self.inited_classes: List[Type] = []
        self.allow_index_dropping = allow_index_dropping
        self.recreate_views = recreate_views

        if (connection_string is None and database is None) or (
            connection_string is not None and database is not None
        ):
            raise ValueError(
                "connection_string parameter or database parameter must be set"
            )

        if document_models is None:
            raise ValueError("document_models parameter must be set")
        if connection_string is not None:
            database = AsyncIOMotorClient(connection_string)[
                URL(connection_string).path[1:]
            ]

        self.database: AsyncIOMotorDatabase = database

        sort_order = {
            ModelType.UnionDoc: 0,
            ModelType.Document: 1,
            ModelType.View: 2,
        }

        self.document_models: List[Union[Type[DocType], Type[View]]] = [
            self.get_model(model) if isinstance(model, str) else model
            for model in document_models
        ]

        self.document_models.sort(
            key=lambda val: sort_order[val.get_model_type()]
        )

    def __await__(self):
        for model in self.document_models:
            yield from self.init_class(model).__await__()

    # General

    @staticmethod
    def get_model(dot_path: str) -> Type["DocType"]:
        """
        Get the model by the path in format bar.foo.Model

        :param dot_path: str - dot seprated path to the model
        :return: Type[DocType] - class of the model
        """
        module_name, class_name = None, None
        try:
            module_name, class_name = dot_path.rsplit(".", 1)
            return getattr(importlib.import_module(module_name), class_name)

        except ValueError:
            raise ValueError(
                f"'{dot_path}' doesn't have '.' path, eg. path.to.your.model.class"
            )

        except AttributeError:
            raise AttributeError(
                f"module '{module_name}' has no class called '{class_name}'"
            )

    def init_settings(
        self, cls: Union[Type[Document], Type[View], Type[UnionDoc]]
    ):
        """
        Init Settings

        :param cls: Union[Type[Document], Type[View], Type[UnionDoc]] - Class
        to init settings
        :return: None
        """
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

    # Document

    @staticmethod
    def set_default_class_vars(cls: Type[Document]):
        """
        Set default class variables.

        :param cls: Union[Type[Document], Type[View], Type[UnionDoc]] - Class
        to init settings
        :return:
        """
        cls._children = dict()
        cls._parent = None
        cls._inheritance_inited = False
        cls._class_id = None

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
    def init_document_fields(cls) -> None:
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

    async def init_document_collection(self, cls):
        """
        Init collection for the Document-based class
        :param cls:
        :return:
        """
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
    async def init_indexes(cls, allow_index_dropping: bool = False):
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

    async def init_document(self, cls: Type[Document]) -> Optional[Output]:
        """
        Init Document-based class

        :param cls:
        :return:
        """
        if cls is Document:
            return None

        if cls not in self.inited_classes:
            self.set_default_class_vars(cls)
            self.init_settings(cls)

            bases = [b for b in cls.__bases__ if issubclass(b, Document)]
            if len(bases) > 1:
                return None
            parent = bases[0]
            output = await self.init_document(parent)
            if cls.get_settings().is_root and (
                parent is Document or not parent.get_settings().is_root
            ):
                if cls.get_collection_name() is None:
                    cls.set_collection_name(cls.__name__)
                output = Output(
                    class_name=cls.__name__,
                    collection_name=cls.get_collection_name(),
                )
                cls._class_id = cls.__name__
                cls._inheritance_inited = True
            elif output is not None:
                output.class_name = f"{output.class_name}.{cls.__name__}"
                cls._class_id = output.class_name
                cls.set_collection_name(output.collection_name)
                parent.add_child(cls._class_id, cls)
                cls._parent = parent
                cls._inheritance_inited = True

            await self.init_document_collection(cls)
            await self.init_indexes(cls, self.allow_index_dropping)
            self.init_document_fields(cls)
            self.init_cache(cls)
            self.init_actions(cls)

            self.inited_classes.append(cls)

            return output

        else:
            if cls._inheritance_inited is True:
                return Output(
                    class_name=cls._class_id,
                    collection_name=cls.get_collection_name(),
                )
            else:
                return None

    # Views

    @staticmethod
    def init_view_fields(cls) -> None:
        """
        Init class fields
        :return: None
        """
        for k, v in cls.__fields__.items():
            path = v.alias or v.name
            setattr(cls, k, ExpressionField(path))

    def init_view_collection(self, cls):
        """
        Init collection for View

        :param cls:
        :return:
        """
        view_settings = cls.get_settings()

        if view_settings.name is None:
            view_settings.name = cls.__name__

        if inspect.isclass(view_settings.source):
            view_settings.source = view_settings.source.get_collection_name()

        view_settings.motor_db = self.database
        view_settings.motor_collection = self.database[view_settings.name]

    async def init_view(self, cls: Type[View]):
        """
        Init View-based class

        :param cls:
        :return:
        """
        self.init_settings(cls)
        self.init_view_collection(cls)
        self.init_view_fields(cls)

        collection_names = await self.database.list_collection_names()
        if self.recreate_views or cls._settings.name not in collection_names:
            if cls._settings.name in collection_names:
                await cls.get_motor_collection().drop()

            await self.database.command(
                {
                    "create": cls.get_settings().name,
                    "viewOn": cls.get_settings().source,
                    "pipeline": cls.get_settings().pipeline,
                }
            )

    # Union Doc

    async def init_union_doc(self, cls: Type[UnionDoc]):
        """
        Init Union Doc based class

        :param cls:
        :return:
        """
        self.init_settings(cls)
        if cls._settings.name is None:
            cls._settings.name = cls.__name__

        cls._settings.motor_db = self.database
        cls._settings.motor_collection = self.database[cls._settings.name]
        cls._is_inited = True

    # Final

    async def init_class(
        self, cls: Union[Type[Document], Type[View], Type[UnionDoc]]
    ):
        """
        Init Document, View or UnionDoc based class.

        :param cls:
        :return:
        """
        if issubclass(cls, Document):
            await self.init_document(cls)

        if issubclass(cls, View):
            await self.init_view(cls)

        if issubclass(cls, UnionDoc):
            await self.init_union_doc(cls)


async def init_beanie(
    database: AsyncIOMotorDatabase = None,
    connection_string: Optional[str] = None,
    document_models: Optional[
        List[Union[Type["DocType"], Type["View"], str]]
    ] = None,
    allow_index_dropping: bool = False,
    recreate_views: bool = False,
):
    """
    Beanie initialization

    :param database: AsyncIOMotorDatabase - motor database instance
    :param connection_string: str - MongoDB connection string
    :param document_models: List[Union[Type[DocType], str]] - model classes
    or strings with dot separated paths
    :param allow_index_dropping: bool - if index dropping is allowed.
    Default False
    :return: None
    """

    await Initializer(
        database=database,
        connection_string=connection_string,
        document_models=document_models,
        allow_index_dropping=allow_index_dropping,
        recreate_views=recreate_views,
    )
