from typing import ClassVar

from pydantic import BaseModel

from beanie.exceptions import ViewWasNotInitialized
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
