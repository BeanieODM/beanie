from abc import abstractmethod
from collections.abc import Mapping
from typing import Any

from pymongo.asynchronous.collection import AsyncCollection

from beanie.odm.settings.base import ItemSettings


class OtherGettersInterface:
    @classmethod
    @abstractmethod
    def get_settings(cls) -> ItemSettings:
        pass

    @classmethod
    def get_pymongo_collection(cls) -> AsyncCollection[Mapping[str, Any]]:
        return cls.get_settings().pymongo_collection  # type: ignore[return-value]

    @classmethod
    def get_collection_name(cls) -> str:
        return cls.get_settings().name  # type: ignore

    @classmethod
    def get_bson_encoders(cls):
        return cls.get_settings().bson_encoders

    @classmethod
    def get_link_fields(cls):
        return None
