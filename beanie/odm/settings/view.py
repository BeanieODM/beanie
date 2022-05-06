from inspect import isclass
from typing import List, Dict, Any, Union, Type

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie.exceptions import ViewHasNoSettings
from beanie.odm.settings.base import ItemSettings


class ViewSettings(ItemSettings):
    source: Union[str, Type]
    pipeline: List[Dict[str, Any]]

    @classmethod
    async def init(
        cls, view_class: Type, database: AsyncIOMotorDatabase
    ) -> "ViewSettings":
        settings_class = getattr(view_class, "Settings", None)
        if settings_class is None:
            raise ViewHasNoSettings("View must have Settings inner class")

        view_settings = cls.parse_obj(vars(settings_class))

        if view_settings.name is None:
            view_settings.name = view_class.__name__

        if isclass(view_settings.source):
            view_settings.source = view_settings.source.get_collection_name()

        view_settings.motor_db = database
        view_settings.motor_collection = database[view_settings.name]

        return view_settings
