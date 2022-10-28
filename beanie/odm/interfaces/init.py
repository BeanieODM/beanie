import inspect
from typing import TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel

from beanie.exceptions import (
    MongoDBVersionError,
    ViewHasNoSettings,
)
from beanie.odm.actions import (
    ActionRegistry,
)
from beanie.odm.cache import LRUCache
from beanie.odm.fields import (
    ExpressionField,
)
from beanie.odm.settings.document import DocumentSettings
from beanie.odm.settings.union_doc import UnionDocSettings
from beanie.odm.settings.view import ViewSettings
from beanie.odm.utils.relations import detect_link

if TYPE_CHECKING:
    pass


class DocumentInitInterface:
    @classmethod
    def set_collection(cls, collection):
        """
        Collection setter
        """
        cls._document_settings.motor_collection = collection

    @classmethod
    def set_database(cls, database):
        """
        Database setter
        """
        cls._document_settings.motor_db = database

    @classmethod
    def set_collection_name(cls, name: str):
        """
        Collection name setter
        """
        cls._document_settings.name = name


class ViewInitInterface:
    @classmethod
    async def init_view(cls, database, recreate_view: bool):
        cls.init_collection(database)
        cls.init_fields()

        collection_names = await database.list_collection_names()
        if recreate_view or cls._settings.name not in collection_names:
            if cls._settings.name in collection_names:
                await cls.get_motor_collection().drop()

            await database.command(
                {
                    "create": cls.get_settings().name,
                    "viewOn": cls.get_settings().source,
                    "pipeline": cls.get_settings().pipeline,
                }
            )

    @classmethod
    def init_fields(cls) -> None:
        """
        Init class fields
        :return: None
        """
        for k, v in cls.__fields__.items():
            path = v.alias or v.name
            setattr(cls, k, ExpressionField(path))

    @classmethod
    def init_settings(cls):
        settings_class = getattr(cls, "Settings", None)
        if settings_class is None:
            raise ViewHasNoSettings("View must have Settings inner class")

        cls._settings = ViewSettings.parse_obj(vars(settings_class))

    @classmethod
    def init_collection(cls, database):
        view_settings = cls.get_settings()

        if view_settings.name is None:
            view_settings.name = cls.__name__

        if inspect.isclass(view_settings.source):
            view_settings.source = view_settings.source.get_collection_name()

        view_settings.motor_db = database
        view_settings.motor_collection = database[view_settings.name]


class UnionDocInitInterface:
    @classmethod
    def init(cls, database: AsyncIOMotorDatabase):
        cls.init_collection(database)
        cls._is_inited = True

    @classmethod
    def init_collection(cls, database: AsyncIOMotorDatabase):
        if cls._settings.name is None:
            cls._settings.name = cls.__name__

        cls._settings.motor_db = database
        cls._settings.motor_collection = database[cls._settings.name]

    @classmethod
    def init_settings(cls):
        settings_class = getattr(cls, "Settings", None)
        cls._settings = UnionDocSettings.parse_obj(vars(settings_class))
