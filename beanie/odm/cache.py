import collections
import datetime
from datetime import timedelta, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

CachedValueType = TypeVar("CachedValueType", bound=Any)


class CachedItem(BaseModel, Generic[CachedValueType]):
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=timezone.utc)
    )
    value: CachedValueType


class LRUCache:
    def __init__(self, capacity: int, expiration_time: timedelta):
        self.capacity: int = capacity
        self.expiration_time: timedelta = expiration_time
        self.cache: collections.OrderedDict[Any, CachedItem[Any]] = (
            collections.OrderedDict()
        )

    def get(self, key: Any) -> CachedItem[Any] | None:
        try:
            item: CachedItem[Any] = self.cache.pop(key)
            if (
                datetime.datetime.now(tz=timezone.utc) - item.timestamp
                > self.expiration_time
            ):
                return None
            self.cache[key] = item
            return item.value
        except KeyError:
            return None

    def set(self, key: Any, value: Any) -> None:
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = CachedItem(value=value)

    @staticmethod
    def create_key(*args: Any):
        return str(args)  # TODO think about this
