from datetime import timedelta
from typing import Optional, Dict, Any, Type

from beanie.odm.cache import Cache, LRUCache
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel, Field


class ItemSettings(BaseModel):
    name: Optional[str]

    use_cache: bool = False
    cache_system: Cache = LRUCache(
        capacity=32, expiration_time=timedelta(minutes=10)
    )
    bson_encoders: Dict[Any, Any] = Field(default_factory=dict)
    projection: Optional[Dict[str, Any]] = None

    motor_db: Optional[AsyncIOMotorDatabase]
    motor_collection: Optional[AsyncIOMotorCollection] = None

    union_doc: Optional[Type] = None

    class Config:
        arbitrary_types_allowed = True
