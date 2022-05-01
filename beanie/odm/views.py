from inspect import isclass
from typing import ClassVar

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel

from beanie.exceptions import ViewWasNotInitialized, ViewHasNoSettings
from beanie.odm.interfaces.find import FindInterface
from beanie.odm.settings.view import ViewSettings, ViewSettingsInput


class View(BaseModel, FindInterface):
    """
    What is needed:

    Source collection or view
    pipeline

    """

    _view_settings: ClassVar[ViewSettings]

    @classmethod
    async def init_view(cls, database, recreate_view: bool):
        cls.init_settings(database)
        if (
            recreate_view
            or not cls._view_settings.view_name
            in await database.list_collection_names()
        ):
            await database.command(
                {
                    "create": cls._view_settings.view_name,
                    "viewOn": cls._view_settings.source,
                    "pipeline": cls._view_settings.pipeline,
                }
            )

    @classmethod
    def init_settings(cls, database: AsyncIOMotorDatabase) -> None:

        settings_class = getattr(cls, "Settings", None)
        if settings_class is None:
            raise ViewHasNoSettings("View must have Settings inner class")

        input_params = ViewSettingsInput.parse_obj(vars(settings_class))
        if input_params.view_name is None:
            input_params.view_name = cls.__name__

        if isclass(input_params.source):
            input_params.source = input_params.source.get_collection_name()

        cls._view_settings = ViewSettings(
            db=database,
            view=database[input_params.view_name],
            **input_params.dict()
        )

    @classmethod
    def get_settings(cls) -> ViewSettings:
        """
        Get document settings, which was created on
        the initialization step

        :return: DocumentSettings class
        """
        if cls._view_settings is None:
            raise ViewWasNotInitialized
        return cls._view_settings

    @classmethod
    def get_motor_collection(cls) -> AsyncIOMotorCollection:
        return cls.get_settings().view

    @classmethod
    def get_collection_name(cls):
        input_class = getattr(cls, "Settings", None)
        if input_class is None or not hasattr(input_class, "view_name"):
            return cls.__name__
        return input_class.view_name

    @classmethod
    def get_bson_encoders(cls):
        return cls.get_settings().bson_encoders

    @classmethod
    def get_link_fields(cls):
        return None
