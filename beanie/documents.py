from typing import Optional, List, Type

from bson import ObjectId
from pydantic import Field
from pydantic.main import BaseModel

from beanie.collections import Collection
from beanie.cursor import Cursor
from beanie.exceptions import DocumentAlreadyCreated, DocumentWasNotSaved
from beanie.fields import PydanticObjectId


class Document(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    _collection_storage = {}

    @classmethod
    def collection(cls) -> Collection:
        """
        Get the collection, which is associated with this document model

        :return: collection
        """
        return cls._collection_storage.get(cls.__name__, None)

    @classmethod
    def set_collection(cls, collection: Collection):
        cls._collection_storage[cls.__name__] = collection

    def __init__(self, *args, **kwargs):
        """
        Initialization

        :param args:
        :param kwargs:
        """
        super(Document, self).__init__(*args, **kwargs)
        if self.collection() is None:
            raise AttributeError(
                "No collection is associated with this document model"
            )

    async def _sync(self) -> None:
        """
        Update local document from the database
        :return: None
        """
        new_instance = await self.get(self.id)
        for key, value in dict(new_instance).items():
            setattr(self, key, value)

    async def create(self) -> "Document":
        """
        Create the document in the database
        :return: Document
        """
        if self.id is not None:
            raise DocumentAlreadyCreated
        await self.collection().insert_one(self)
        return self

    async def replace(self) -> None:
        """
        Fully update the document in the database
        :return: None
        """
        if self.id is None:
            raise DocumentWasNotSaved
        await self.collection().replace_one(self)

    async def update(
        self, update_query: dict, filter_query: dict = None
    ) -> None:
        """
        Partially update the document in the database

        :param update_query: The modifications to apply.
        :param filter_query: The selection criteria for the update. Optional.
        :return: None
        """
        await self.collection().update_one(
            self, update_query=update_query, filter_query=filter_query
        )
        await self._sync()

    async def delete(self) -> None:
        """
        Delete the document

        :return: None
        """
        await self.collection().delete_one(self)
        self.id = None

    @classmethod
    async def get(cls, document_id) -> "Document":
        """
        Get the document bu id

        :param document_id: Id of the documnt
        :return: Document
        """
        return await cls.collection().get_one(document_id)

    @classmethod
    async def find_one(cls, query: dict) -> "Document":
        """
        Find one document

        :param query: The search criteria
        :return: Document
        """
        return await cls.collection().find_one(query)

    @classmethod
    def all(cls) -> Cursor:
        """
        Get all the documents
        :return: AsyncGenerator of the documents
        """
        return cls.collection().all()

    @classmethod
    def find(cls, query) -> Cursor:
        """
        Find many documents by criteria

        :param query: The search criteria
        :return: List of the documents
        """
        return cls.collection().find(query=query)

    @classmethod
    def aggregate(
        cls, query: List[dict], item_model: Type[BaseModel] = None
    ) -> Cursor:
        """
        Aggregate

        :param query: Query with the aggregation commands
        :param item_model: Model of item to return in the list of aggregations
        :return: AsyncGenerator of aggregated items
        """
        return cls.collection().aggregate(query=query, item_model=item_model)

    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
        }
        allow_population_by_field_name = True
