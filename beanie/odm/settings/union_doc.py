from typing import Type

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie.odm.settings.base import ItemSettings


class UnionDocSettings(ItemSettings):
    ...
