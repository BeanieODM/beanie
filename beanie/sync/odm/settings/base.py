from datetime import timedelta
from typing import Optional, Dict, Any, Type

from pydantic import BaseModel, Field
from pymongo.collection import Collection
from pymongo.database import Database


class ItemSettings(BaseModel):
    name: Optional[str]

    use_cache: bool = False
    cache_capacity: int = 32
    cache_expiration_time: timedelta = timedelta(minutes=10)
    bson_encoders: Dict[Any, Any] = Field(default_factory=dict)
    projection: Optional[Dict[str, Any]] = None

    motor_db: Optional[Database]
    motor_collection: Optional[Collection] = None

    union_doc: Optional[Type] = None

    class Config:
        arbitrary_types_allowed = True
