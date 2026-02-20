import asyncio
from typing import Any, ClassVar, Dict, Optional, Union

from pydantic import BaseModel

from beanie.exceptions import ViewWasNotInitialized
from beanie.odm.fields import Link, LinkInfo
from beanie.odm.interfaces.aggregate import AggregateInterface
from beanie.odm.interfaces.detector import DetectionInterface, ModelType
from beanie.odm.interfaces.find import FindInterface
from beanie.odm.interfaces.getters import OtherGettersInterface
from beanie.odm.settings.view import ViewSettings


class View(
    BaseModel,
    FindInterface,
    AggregateInterface,
    OtherGettersInterface,
    DetectionInterface,
):
    """
    What is needed:

    Source collection or view
    pipeline

    """

    # Relations
    _link_fields: ClassVar[Optional[Dict[str, LinkInfo]]] = None

    # Settings
    _settings: ClassVar[ViewSettings]

    # Lazy init metadata caching
    _metadata_initialized: ClassVar[bool] = False

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

    @classmethod
    async def ensure_view(cls) -> None:
        """Create or replace the MongoDB view for this class on demand.

        Useful after ``init_beanie(lazy=True)`` when view recreation was
        skipped during initialization.
        """
        settings = cls.get_settings()
        db = settings.pymongo_db
        if db is None:
            raise ViewWasNotInitialized
        collection_names = await db.list_collection_names(
            authorizedCollections=True, nameOnly=True
        )
        if settings.name in collection_names:
            await cls.get_pymongo_collection().drop()

        await db.command(
            {
                "create": settings.name,
                "viewOn": settings.source,
                "pipeline": settings.pipeline,
            }
        )

    async def fetch_link(self, field: Union[str, Any]):
        ref_obj = getattr(self, field, None)
        if isinstance(ref_obj, Link):
            value = await ref_obj.fetch(fetch_links=True)
            setattr(self, field, value)
        if isinstance(ref_obj, list) and ref_obj:
            values = await Link.fetch_list(ref_obj, fetch_links=True)
            setattr(self, field, values)

    async def fetch_all_links(self):
        coros = []
        link_fields = self.get_link_fields()
        if link_fields is not None:
            for ref in link_fields.values():
                coros.append(self.fetch_link(ref.field_name))  # TODO lists
        await asyncio.gather(*coros)

    @classmethod
    def get_link_fields(cls) -> Optional[Dict[str, LinkInfo]]:
        return cls._link_fields

    @classmethod
    def get_model_type(cls) -> ModelType:
        return ModelType.View
