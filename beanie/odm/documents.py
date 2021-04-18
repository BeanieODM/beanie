from typing import Optional, List, Type, Union, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import Field, ValidationError
from pydantic.main import BaseModel
from pymongo.client_session import ClientSession
from pymongo.results import DeleteResult, UpdateResult, InsertOneResult

from beanie.odm.collection import collection_factory
from beanie.odm.cursor import Cursor
from beanie.exceptions import (
    DocumentWasNotSaved,
    DocumentNotFound,
    DocumentAlreadyCreated,
    CollectionWasNotInitialized,
    ReplaceError,
)
from beanie.odm.fields import PydanticObjectId
from beanie.odm.models import (
    InspectionResult,
    InspectionStatuses,
    InspectionError,
    SortDirection,
    FindOperationKWARGS,
)


class Document(BaseModel):
    """
    Document Mapping class.

    Inherited from Pydantic BaseModel ß includes all the respective methods.
    Contains id filed - MongoDB document ObjectID "_id" field
    """

    id: Optional[PydanticObjectId] = Field(None, alias="_id")

    def __init__(self, *args, **kwargs):
        """
        Initialization

        :param args:
        :param kwargs:
        """
        super(Document, self).__init__(*args, **kwargs)
        self.get_motor_collection()

    async def _sync(self) -> None:
        """
        Update local document from the database
        :return: None
        """
        new_instance = await self.get(self.id)
        for key, value in dict(new_instance).items():
            setattr(self, key, value)

    @classmethod
    async def insert_one(
        cls, document: "Document", session: ClientSession = None
    ) -> InsertOneResult:
        """
        Insert one document to the collection
        :param document: Document - document to insert
        :param session: ClientSession - pymongo session
        :return: Document
        """
        return await cls.get_motor_collection().insert_one(
            document.dict(by_alias=True, exclude={"id"}), session=session
        )

    @classmethod
    async def insert_many(
        cls,
        documents: List["Document"],
        keep_ids: bool = False,
        session: ClientSession = None,
    ):

        """
        Insert many documents to the collection

        :param documents:  List["Document"] - documents to insert
        :param keep_ids: bool - should it insert documents with ids
        or ignore it? Default False - ignore
        :param session: ClientSession - pymongo session
        :return: Document
        """
        if keep_ids:
            documents_list = [
                document.dict(by_alias=True) for document in documents
            ]
        else:
            documents_list = [
                document.dict(by_alias=True, exclude={"id"})
                for document in documents
            ]
        return await cls.get_motor_collection().insert_many(
            documents_list,
            session=session,
        )

    async def create(self, session: ClientSession = None) -> "Document":
        """
        Create the document in the database
        :return: Document
        """
        if self.id is not None:
            raise DocumentAlreadyCreated
        result = await self.get_motor_collection().insert_one(
            self.dict(by_alias=True, exclude={"id"}), session=session
        )
        self.id = PydanticObjectId(result.inserted_id)
        return self

    @classmethod
    async def find_one(
        cls, filter_query: dict, session: ClientSession = None
    ) -> Union["Document", None]:
        """
        Find one document by criteria

        :param filter_query: dict - The selection criteria
        :return: Union["Document", None]
        """
        document = await cls.get_motor_collection().find_one(
            filter_query, session=session
        )
        if document is None:
            return None
        return cls.parse_obj(document)

    @classmethod
    def find_many(
        cls,
        filter_query: dict,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: ClientSession = None,
    ) -> Cursor:
        """
        Find many documents by criteria

        :param filter_query: dict - The selection criteria.
        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key
        or a list of (key, direction) pairs specifying the sort order
        for this query.
        :param session: ClientSession - pymongo session
        :return: Cursor - AsyncGenerator of the documents
        """
        kwargs = FindOperationKWARGS(skip=skip, limit=limit, sort=sort).dict(
            exclude_none=True
        )
        cursor = cls.get_motor_collection().find(
            filter_query, session=session, **kwargs
        )
        return Cursor(motor_cursor=cursor, model=cls)

    @classmethod
    def find_all(
        cls,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: ClientSession = None,
    ) -> Cursor:
        """
        Get all the documents

        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key
        or a list of (key, direction) pairs specifying the sort order
        for this query.
        :param session: ClientSession - pymongo session
        :return: Cursor - AsyncGenerator of the documents
        """
        return cls.find_many(
            filter_query={}, skip=skip, limit=limit, sort=sort, session=session
        )

    @classmethod
    async def get(
        cls, document_id: PydanticObjectId, session: ClientSession = None
    ) -> Union["Document", None]:
        """
        Get document by id

        :return: Union["Document", None]
        """
        return await cls.find_one({"_id": document_id}, session=session)

    @classmethod
    async def replace_one(
        cls,
        filter_query: dict,
        document: "Document",
        session: ClientSession = None,
    ):
        """
        Fully update one document in the database

        :param filter_query: dict - the selection criteria.
        :param document: Document - the document which will replace the found
        one.
        :param session: ClientSession - pymongo session.
        :return: None
        """
        result = await cls.get_motor_collection().replace_one(
            filter_query,
            document.dict(by_alias=True, exclude={"id"}),
            session=session,
        )
        if not result.raw_result["updatedExisting"]:
            raise DocumentNotFound
        return result

    @classmethod
    async def replace_many(
        cls, documents: List["Document"], session: ClientSession = None
    ) -> None:
        """

        :param documents: List["Document"]
        :param session: ClientSession - pymongo session.
        :return: None
        """
        ids_list = [document.id for document in documents]
        if await cls.count_documents({"_id": {"$in": ids_list}}) != len(
            ids_list
        ):
            raise ReplaceError(
                "Some of the documents are not exist in the collection"
            )
        await cls.delete_many({"_id": {"$in": ids_list}}, session=session)
        await cls.insert_many(documents, keep_ids=True, session=session)

    async def replace(self, session: ClientSession = None) -> "Document":
        """
        Fully update the document in the database

        :param session: ClientSession - pymongo session.
        :return: None
        """
        if self.id is None:
            raise DocumentWasNotSaved

        await self.replace_one({"_id": self.id}, self, session=session)
        return self

    @classmethod
    async def update_one(
        cls,
        filter_query: dict,
        update_query: dict,
        session: ClientSession = None,
    ) -> UpdateResult:
        """
        Partially update already created document

        :param filter_query: dict - the modifications to apply.
        :param update_query: dict - the selection criteria for the update.
        :param session: ClientSession - pymongo session.
        :return: UpdateResult - pymongo UpdateResult instance
        """
        return await cls.get_motor_collection().update_one(
            filter_query, update_query, session=session
        )

    @classmethod
    async def update_many(
        cls,
        filter_query: dict,
        update_query: dict,
        session: ClientSession = None,
    ) -> UpdateResult:
        """
        Partially update many documents

        :param filter_query: dict - the selection criteria for the update.
        :param update_query: dict - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :return: UpdateResult - pymongo UpdateResult instance
        """
        return await cls.get_motor_collection().update_many(
            filter_query, update_query, session=session
        )

    @classmethod
    async def update_all(
        cls, update_query: dict, session: ClientSession = None
    ) -> UpdateResult:
        """
        Partially update all the documents

        :param update_query: dict - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :return: UpdateResult - pymongo UpdateResult instance
        """
        return await cls.update_many({}, update_query, session=session)

    async def update(
        self, update_query: dict, session: ClientSession = None
    ) -> None:
        """
        Partially update the document in the database

        :param update_query: dict - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :return: None
        """
        await self.update_one(
            {"_id": self.id}, update_query=update_query, session=session
        )
        await self._sync()

    @classmethod
    async def delete_one(
        cls, filter_query: dict, session: ClientSession = None
    ) -> DeleteResult:
        """
        Delete one document

        :param filter_query: dict - the selection criteria
        :param session: ClientSession - pymongo session.
        :return: DeleteResult - pymongo DeleteResult instance
        """
        return await cls.get_motor_collection().delete_one(
            filter_query, session=session
        )

    @classmethod
    async def delete_many(
        cls, filter_query: dict, session: ClientSession = None
    ) -> DeleteResult:
        """
        Delete many documents

        :param filter_query: dict - the selection criteria.
        :param session: ClientSession - pymongo session.
        :return: DeleteResult - pymongo DeleteResult instance.
        """
        return await cls.get_motor_collection().delete_many(
            filter_query, session=session
        )

    @classmethod
    async def delete_all(cls, session: ClientSession = None) -> DeleteResult:
        """
        Delete all the documents

        :param session: ClientSession - pymongo session.
        :return: DeleteResult - pymongo DeleteResult instance.
        """
        return await cls.delete_many({}, session=session)

    async def delete(self, session: ClientSession = None) -> DeleteResult:
        """
        Delete the document

        :param session: ClientSession - pymongo session.
        :return: DeleteResult - pymongo DeleteResult instance.
        """
        return await self.delete_one({"_id": self.id}, session=session)

    @classmethod
    def aggregate(
        cls,
        aggregation_query: List[dict],
        item_model: Type[BaseModel] = None,
        session: ClientSession = None,
    ) -> Cursor:
        """
        Aggregate

        :param aggregation_query: List[dict] - query with aggregation commands
        :param item_model: Type[BaseModel] - model of item to return in the
        list of aggregations
        :param session: ClientSession - pymongo session.
        :return: Cursor - AsyncGenerator of aggregated items
        """
        cursor = cls.get_motor_collection().aggregate(
            aggregation_query, session=session
        )
        return Cursor(motor_cursor=cursor, model=item_model)

    @classmethod
    async def count_documents(cls, filter_query: Optional[dict] = None) -> int:
        """
        Number of documents in the collections

        :param filter_query: dict - the selection criteria
        :return: int
        """
        if filter_query is None:
            filter_query = {}
        return await cls.get_motor_collection().count_documents(filter_query)

    # Collections

    @classmethod
    async def init_collection(
        cls, database: AsyncIOMotorDatabase, allow_index_dropping: bool
    ) -> None:
        """
        Internal CollectionMeta class creator

        :param database: AsyncIOMotorDatabase - motor database instance
        :param allow_index_dropping: bool - if index dropping is allowed
        :return: None
        """
        collection_class = getattr(cls, "Collection", None)
        collection_meta = await collection_factory(
            database=database,
            document_class=cls,
            allow_index_dropping=allow_index_dropping,
            collection_class=collection_class,
        )
        setattr(cls, "CollectionMeta", collection_meta)

    @classmethod
    def _get_collection_meta(cls) -> Type:
        """
        Get internal CollectionMeta class, which was created on
        the collection initialization step

        :return: CollectionMeta class
        """
        collection_meta = getattr(cls, "CollectionMeta", None)
        if collection_meta is None:
            raise CollectionWasNotInitialized
        return collection_meta

    @classmethod
    def get_motor_collection(cls) -> AsyncIOMotorCollection:
        """
        Get Motor Collection to access low level control

        :return: AsyncIOMotorCollection
        """
        collection_meta = cls._get_collection_meta()
        return collection_meta.motor_collection

    @classmethod
    async def inspect_collection(
        cls, session: ClientSession = None
    ) -> InspectionResult:
        """
        Check, if documents, stored in the MongoDB collection
        are compatible with the Document schema

        :return: InspectionResult
        """
        inspection_result = InspectionResult()
        async for json_document in cls.get_motor_collection().find(
            {}, session=session
        ):
            try:
                cls.parse_obj(json_document)
            except ValidationError as e:
                if inspection_result.status == InspectionStatuses.OK:
                    inspection_result.status = InspectionStatuses.FAIL
                inspection_result.errors.append(
                    InspectionError(
                        document_id=json_document["_id"], error=str(e)
                    )
                )
        return inspection_result

    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
        }
        allow_population_by_field_name = True
