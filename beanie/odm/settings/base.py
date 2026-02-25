from datetime import timedelta
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


class ItemSettings(BaseModel):
    name: Optional[str] = None

    use_cache: bool = False
    cache_capacity: int = 32
    cache_expiration_time: timedelta = timedelta(minutes=10)
    bson_encoders: dict[Any, Any] = Field(default_factory=dict)
    projection: Optional[dict[str, Any]] = None

    pymongo_db: Optional[AsyncDatabase] = None
    pymongo_collection: Optional[AsyncCollection] = None

    union_doc: Optional[type] = None
    union_doc_alias: Optional[str] = None
    class_id: str = "_class_id"

    is_root: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
