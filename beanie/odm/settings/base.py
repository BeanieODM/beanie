from datetime import timedelta
from typing import Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel, Field


class ItemSettings(BaseModel):
    name: Optional[str]

    use_cache: bool = False
    cache_capacity: int = 32
    cache_expiration_time: timedelta = timedelta(minutes=10)
    bson_encoders: Dict[Any, Any] = Field(default_factory=dict)
    projection: Optional[Dict[str, Any]] = None

    motor_db: Optional[AsyncIOMotorDatabase]
    motor_collection: Optional[AsyncIOMotorCollection] = None

    multi_model: bool = False

    class Config:
        arbitrary_types_allowed = True
