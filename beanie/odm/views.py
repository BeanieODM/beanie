from typing import ClassVar

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from beanie.exceptions import ViewWasNotInitialized
from beanie.odm.fields import ExpressionField
from beanie.odm.interfaces.aggregate import AggregateInterface
from beanie.odm.interfaces.detector import DetectionInterface, ModelType
from beanie.odm.interfaces.find import FindInterface
from beanie.odm.interfaces.getters import OtherGettersInterface
from beanie.odm.settings.view import ViewSettings


class View(
    BaseModel,
    FindInterface,
    AggregateInterface,
    OtherGettersInterface,
    DetectionInterface,
):
    """
    What is needed:

    Source collection or view
    pipeline

    """

    _settings: ClassVar[ViewSettings]

    @classmethod
    async def init_view(cls, database, recreate_view: bool):
        await cls.init_settings(database)
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
    async def init_settings(cls, database: AsyncIOMotorDatabase) -> None:
        cls._settings = await ViewSettings.init(
            database=database, view_class=cls
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
    def get_settings(cls) -> ViewSettings:
        """
        Get view settings, which was created on
        the initialization step

        :return: ViewSettings class
        """
        if cls._settings is None:
            raise ViewWasNotInitialized
        return cls._settings

    @classmethod
    def get_model_type(cls) -> ModelType:
        return ModelType.View
