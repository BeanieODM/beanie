from collections.abc import Mapping
from typing import Any, ClassVar

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from beanie.odm.settings.document import DocumentSettings


class SettersInterface:
    _document_settings: ClassVar[DocumentSettings | None]

    @classmethod
    def set_collection(cls, collection: AsyncCollection[Mapping[str, Any]]):
        """
        Collection setter
        """
        cls._document_settings.pymongo_collection = collection  # type: ignore[union-attr]

    @classmethod
    def set_database(cls, database: AsyncDatabase[Mapping[str, Any]]):
        """
        Database setter
        """
        cls._document_settings.pymongo_db = database  # type: ignore[union-attr]

    @classmethod
    def set_collection_name(cls, name: str):
        """
        Collection name setter
        """
        cls._document_settings.name = name  # type: ignore[union-attr]
