from typing import ClassVar

from beanie.odm.settings.document import DocumentSettings


class SettersInterface:
    _document_settings: ClassVar[DocumentSettings | None]

    @classmethod
    def set_collection(cls, collection):
        """
        Collection setter
        """
        cls._document_settings.pymongo_collection = collection

    @classmethod
    def set_database(cls, database):
        """
        Database setter
        """
        cls._document_settings.pymongo_db = database

    @classmethod
    def set_collection_name(cls, name: str):
        """
        Collection name setter
        """
        cls._document_settings.name = name  # type: ignore
