from collections.abc import Mapping
from datetime import timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


class ItemSettings(BaseModel):
    name: str | None = None

    use_cache: bool = False
    cache_capacity: int = 32
    cache_expiration_time: timedelta = timedelta(minutes=10)
    bson_encoders: dict[Any, Any] = Field(default_factory=dict)
    projection: dict[str, Any] | None = None

    pymongo_db: AsyncDatabase[Mapping[str, Any]] | None = None
    pymongo_collection: AsyncCollection[Mapping[str, Any]] | None = None

    union_doc: type | None = None
    union_doc_alias: str | None = None
    class_id: str = "_class_id"

    is_root: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
