from typing import ClassVar

from pydantic import BaseModel
from pymongo.database import Database

from beanie.exceptions import ViewWasNotInitialized
from beanie.odm.fields import ExpressionField
from beanie.sync.odm.interfaces.aggregate import AggregateInterface
from beanie.sync.odm.interfaces.detector import DetectionInterface, ModelType
from beanie.sync.odm.interfaces.find import FindInterface
from beanie.sync.odm.interfaces.getters import OtherGettersInterface
from beanie.sync.odm.settings.view import ViewSettings


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
    def init_view(cls, database, recreate_view: bool):
        cls.init_settings(database)
        cls.init_fields()

        collection_names = database.list_collection_names()
        if recreate_view or cls._settings.name not in collection_names:
            if cls._settings.name in collection_names:
                cls.get_motor_collection().drop()

            database.command(
                {
                    "create": cls.get_settings().name,
                    "viewOn": cls.get_settings().source,
                    "pipeline": cls.get_settings().pipeline,
                }
            )

    @classmethod
    def init_settings(cls, database: Database) -> None:
        cls._settings = ViewSettings.init(database=database, view_class=cls)

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
