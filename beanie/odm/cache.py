import abc
import collections
import datetime
import pickle
from datetime import timedelta
from typing import Any, Optional, Sequence, Union

import msgpack
from pydantic import BaseModel, Field


class CachedItem(BaseModel):
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )
    value: Any


class Cache(abc.ABC):
    @abc.abstractmethod
    def set(self, key: str, value: Any) -> None:
        ...

    @abc.abstractmethod
    def get(self, key: str) -> Optional[CachedItem]:
        ...

    @abc.abstractmethod
    def invalidate(self) -> None:
        ...

    @staticmethod
    def create_key(*args):
        return str(args)  # TODO think about this


class LRUCache(Cache):
    def __init__(self, capacity: int, expiration_time: timedelta):
        self.capacity: int = capacity
        self.expiration_time: timedelta = expiration_time
        self.cache: collections.OrderedDict = collections.OrderedDict()

    def get(self, key) -> Optional[CachedItem]:
        try:
            item = self.cache.pop(key)
            if (
                datetime.datetime.utcnow() - item.timestamp
                > self.expiration_time
            ):
                return None
            self.cache[key] = item
            return item.value
        except KeyError:
            return None

    def set(self, key, value) -> None:
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = CachedItem(value=value)

    def invalidate(self) -> None:
        self.cache.clear()


class RedisCache(Cache):
    def __init__(
        self,
        redis_client,
        ttl: Optional[Union[int, timedelta]] = None,
        key_prefix: str = "cache",
        serializer=pickle,
    ):
        self.redis_client = redis_client
        self.key_prefix = key_prefix
        self.ttl = self._normalize_ttl(ttl)
        self.serializer = serializer

    def _normalize_object_ids(self, value):
        if isinstance(value, dict):
            if "_id" in value:
                value["_id"] = str(value["_id"])
        elif isinstance(value, Sequence):
            for row in value:
                self._normalize_object_ids(row)
        return value

    def _serialize(self, value):
        if not value:
            return None
        if self.serializer is not pickle:
            # Turn ObjectId to string for those serializer that can't
            # serialize ObjectId, like: msgpack and json
            value = self._normalize_object_ids(value)
        return self.serializer.dumps(value)

    def _deserialize(self, value):
        try:
            loaded = self.serializer.loads(value)
            return loaded
        except (
            TypeError,
            pickle.UnpicklingError,
            UnicodeDecodeError,
            msgpack.exceptions.UnpackException,
            msgpack.exceptions.ExtraData,
        ):
            return None

    def _get_key(self, key):
        return f"{self.key_prefix}:{self.serializer.__name__}:{key}"

    @staticmethod
    def _normalize_ttl(ttl: Optional[Union[int, timedelta]]) -> Optional[int]:
        if isinstance(ttl, timedelta):
            return ttl.seconds
        elif isinstance(ttl, int) and ttl >= 0:
            return ttl
        return None

    def get(self, key) -> Optional[CachedItem]:
        key = self._get_key(key)
        redis_data = self.redis_client.get(key)
        data = self._deserialize(redis_data)
        return data if data else None

    def set(self, key, value) -> None:
        value = self._serialize(value)
        key = self._get_key(key)
        self.redis_client.set(key, value, ex=self.ttl)

    def invalidate(self) -> None:
        self.redis_client.flushdb()
