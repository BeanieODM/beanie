from typing import ClassVar

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from beanie.exceptions import ViewWasNotInitialized
from beanie.odm.interfaces.find import FindInterface
from beanie.odm.interfaces.getters import OtherGettersInterface
from beanie.odm.settings.view import ViewSettings


class View(BaseModel, FindInterface, OtherGettersInterface):
    """
    What is needed:

    Source collection or view
    pipeline

    """

    _settings: ClassVar[ViewSettings]

    @classmethod
    async def init_view(cls, database, recreate_view: bool):
        await cls.init_settings(database)
        if (
                recreate_view
                or not cls._settings.name
                       in await database.list_collection_names()
        ):
            await database.command(
                {
                    "create": cls.get_settings().name,
                    "viewOn": cls.get_settings().source,
                    "pipeline": cls.get_settings().pipeline,
                }
            )

    @classmethod
    async def init_settings(cls, database: AsyncIOMotorDatabase) -> None:
        cls._settings = await ViewSettings.init(database=database,
                                                view_class=cls)

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
