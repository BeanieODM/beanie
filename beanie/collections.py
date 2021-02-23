import typing
from typing import Type, List, Union

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from pymongo.results import UpdateResult, DeleteResult

from beanie.cursor import Cursor
from beanie.exceptions import DocumentNotFound
from beanie.fields import PydanticObjectId

if typing.TYPE_CHECKING:
    from beanie.documents import Document


class Collection:
    def __init__(
        self,
        name: str,
        db: AsyncIOMotorDatabase,
        document_model: Type["Document"],
    ) -> None:
        """
        Collection initialization

        :param name: Collection's name
        :param db: AsyncIOMotorDatabase instance
        :param document_model: Subclass of Document to follow the structure
        """
        self.db = db
        self.document_model = document_model
        self.motor_collection = db[name]

        self.document_model.set_collection(self)

    async def insert_one(self, document: "Document") -> "Document":
        """
        Insert one document into the collection

        :param document: Document
        :return: Inserted document with updated id field
        """
        if not isinstance(document, self.document_model):
            raise TypeError(
                "Document must be object of the Document class"
            )
        result = await self.motor_collection.insert_one(
            document.dict(by_alias=True, exclude={"id"})
        )
        document.id = PydanticObjectId(result.inserted_id)
        return document

    async def replace_one(self, document: "Document") -> UpdateResult:
        """
        Replace already created (stored to the collection) document

        :param document: document
        :return: UpdateResult instance
        """
        if not isinstance(document, self.document_model):
            raise TypeError(
                "Document must be object of the Document class"
            )
        if document.id is None:
            raise ValueError("Document must have id")
        result = await self.motor_collection.replace_one(
            {"_id": document.id}, document.dict(by_alias=True)
        )
        if not result.raw_result["updatedExisting"]:
            raise DocumentNotFound
        return result

    async def update_one(
        self,
        document: "Document",
        update_query: dict,
        filter_query: dict = None,
    ) -> UpdateResult:
        """
        Partially update already created document

        :param document: Document
        :param update_query: The modifications to apply.
        :param filter_query: The selection criteria for the update. Optional.
        :return: UpdateResult instance
        """
        if not isinstance(document, self.document_model):
            raise TypeError(
                "Document must be object of the Document class"
            )
        if filter_query is None:
            return await self.motor_collection.update_one(
                {"_id": document.id}, update_query
            )
        else:
            return await self.motor_collection.update_one(
                filter_query, update_query
            )

    async def update_many(
        self, filter_query: dict, update_query: dict
    ) -> UpdateResult:
        """
        Partially update many documents

        :param filter_query: The modifications to apply.
        :param update_query: The selection criteria for the update.
        :return: UpdateResult instance
        """
        return await self.motor_collection.update_many(
            filter_query, update_query
        )

    async def delete_one(self, document: "Document") -> DeleteResult:
        """
        Delete the document

        :param document: Document to delete
        :return: DeleteResult instance
        """
        if not isinstance(document, self.document_model):
            raise TypeError(
                "Document must be object of the Document class"
            )
        return await self.motor_collection.delete_one({"_id": document.id})

    async def find_one(self, query: dict) -> Union["Document", None]:
        """
        Find one document by criteria

        :param query: The selection criteria
        :return: Document
        """
        document = await self.motor_collection.find_one(query)
        if document is None:
            return None
        return self.document_model(**document)

    async def get_one(
        self, document_id: PydanticObjectId
    ) -> Union["Document", None]:
        """
        Get one document by id

        :param document_id: Id of the document
        :return: Document
        """
        if not isinstance(document_id, PydanticObjectId):
            raise TypeError("Id must be of type PydanticObjectId")
        return await self.find_one({"_id": document_id})

    def find(self, query: dict) -> Cursor:
        """
        Find many documents by criteria

        :param query: The selection criteria.
        :return: AsyncGenerator of the documents
        """
        cursor = self.motor_collection.find(query)
        return Cursor(motor_cursor=cursor, model=self.document_model)

    def all(self) -> Cursor:
        """
        Get all the documents

        :return: AsyncGenerator of the documents
        """
        return self.find(query={})

    def aggregate(
        self, query: List[dict], item_model: Type[BaseModel] = None
    ) -> Cursor:
        """
        Aggregate

        :param query: Query with aggregation commands
        :param item_model: Model of item to return in the list of aggregations
        :return: AsyncGenerator of aggregated items
        """
        cursor = self.motor_collection.aggregate(query)
        return Cursor(motor_cursor=cursor, model=item_model)
