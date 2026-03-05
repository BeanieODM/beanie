import asyncio
from typing import Any, ClassVar

from pydantic import BaseModel

from beanie.exceptions import ViewWasNotInitialized
from beanie.odm.cache import LRUCache
from beanie.odm.fields import Link, LinkInfo
from beanie.odm.interfaces.aggregate import AggregateInterface
from beanie.odm.interfaces.find import FindInterface
from beanie.odm.interfaces.getters import OtherGettersInterface
from beanie.odm.settings.view import ViewSettings


class View(
    BaseModel,
    FindInterface,
    AggregateInterface,
    OtherGettersInterface,
):
    """
    What is needed:

    Source collection or view
    pipeline

    """

    # Database
    _database_major_version: ClassVar[int] = 4

    # Relations
    _link_fields: ClassVar[dict[str, LinkInfo] | None] = None

    # Settings
    _settings: ClassVar[ViewSettings]

    # Cache
    _cache: ClassVar[LRUCache | None] = None

    @classmethod
    def get_settings(cls) -> ViewSettings:
        """
        Get view settings, which was created on
        the initialization step

        :return: ViewSettings class
        """
        if cls._settings is None:
            raise ViewWasNotInitialized
        return cls._settings

    async def fetch_link(self, field: str | Any):
        ref_obj = getattr(self, field, None)
        if isinstance(ref_obj, Link):
            value = await ref_obj.fetch(fetch_links=True)
            setattr(self, field, value)
        if isinstance(ref_obj, list) and ref_obj:
            values = await Link.fetch_list(ref_obj, fetch_links=True)
            setattr(self, field, values)

    async def fetch_all_links(self):
        link_fields = self.get_link_fields()
        if link_fields is not None:
            coros = [
                self.fetch_link(ref.field_name) for ref in link_fields.values()
            ]
            if coros:
                await asyncio.gather(*coros)

    @classmethod
    def get_link_fields(cls) -> dict[str, LinkInfo] | None:
        return cls._link_fields
