from typing import Type

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie.odm.settings.base import ItemSettings


class UnionDocSettings(ItemSettings):
    @classmethod
    def init(
        cls, doc_class: Type, database: AsyncIOMotorDatabase
    ) -> "UnionDocSettings":
        settings_class = getattr(doc_class, "Settings", None)

        multi_doc_settings = cls.parse_obj(vars(settings_class))

        if multi_doc_settings.name is None:
            multi_doc_settings.name = doc_class.__name__

        multi_doc_settings.motor_db = database
        multi_doc_settings.motor_collection = database[multi_doc_settings.name]

        return multi_doc_settings
