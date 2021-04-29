from typing import Dict, Optional, List, Type, Union, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import Field, ValidationError
from pydantic.main import BaseModel
from pymongo.client_session import ClientSession
from pymongo.results import DeleteResult, UpdateResult, InsertOneResult

from beanie.exceptions import (
    DocumentWasNotSaved,
    DocumentAlreadyCreated,
    CollectionWasNotInitialized,
    ReplaceError,
)
from beanie.odm.collection import collection_factory
from beanie.odm.fields import PydanticObjectId, CollectionField
from beanie.odm.interfaces.update import (
    UpdateMethods,
)
from beanie.odm.models import (
    InspectionResult,
    InspectionStatuses,
    InspectionError,
    SortDirection,
)
from beanie.odm.queries.aggregation import AggregationPipeline
from beanie.odm.queries.find import FindOne, FindMany


class Document(BaseModel, UpdateMethods):
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

    def _pass_update_expression(self, expression):
        return self.update(expression)

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

    async def insert(self, session: ClientSession = None) -> "Document":
        """
        Insert the document to the database
        :return: Document
        """
        if self.id is not None:
            raise DocumentAlreadyCreated
        result = await self.get_motor_collection().insert_one(
            self.dict(by_alias=True, exclude={"id"}), session=session
        )
        self.id = PydanticObjectId(result.inserted_id)
        return self

    async def create(self, session: ClientSession = None) -> "Document":
        """
        Insert the document to the database. The same as self.insert()
        :return: Document
        """
        return await self.insert(session=session)

    @classmethod
    def find_one(cls, *args, session: ClientSession = None) -> FindOne:
        """
        Find one document by criteria

        :return: Union["Document", None]
        """
        return FindOne(document_model=cls).find_one(*args)

    @classmethod
    def find_many(
        cls,
        *args,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: ClientSession = None,
    ) -> FindMany:
        """
        Find many documents by criteria

        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key
        or a list of (key, direction) pairs specifying the sort order
        for this query.
        :param session: ClientSession - pymongo session
        :return: Cursor - AsyncGenerator of the documents
        """
        return FindMany(document_model=cls).find_many(
            *args, sort=sort, skip=skip, limit=limit
        )

    @classmethod
    def find_all(
        cls,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: ClientSession = None,
    ) -> FindMany:
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
            {}, skip=skip, limit=limit, sort=sort, session=session
        )

    @classmethod
    def all(
        cls,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: ClientSession = None,
    ) -> FindMany:
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
        return cls.find_all(skip=skip, limit=limit, sort=sort, session=session)

    @classmethod
    def find(
        cls,
        *args,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: ClientSession = None,
    ) -> FindMany:
        return cls.find_many(
            *args, skip=skip, limit=limit, sort=sort, session=session
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

        await self.find_one({"_id": self.id}).replace_one(self)
        return self

    @classmethod
    def update_all(cls, *args, session: ClientSession = None) -> UpdateResult:
        """
        Partially update all the documents

        :param update_query: dict - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :return: UpdateResult - pymongo UpdateResult instance
        """
        return cls.find_all().update_many(*args)

    async def update(self, *args, session: ClientSession = None) -> None:
        """
        Partially update the document in the database

        :param update_query: dict - the modifications to apply.
        :param session: ClientSession - pymongo session.
        :return: None
        """
        await self.find_one({"_id": self.id}).update(*args)
        await self._sync()

    @classmethod
    async def delete_all(cls, session: ClientSession = None) -> DeleteResult:
        """
        Delete all the documents

        :param session: ClientSession - pymongo session.
        :return: DeleteResult - pymongo DeleteResult instance.
        """
        return await cls.find_all().delete()

    async def delete(self, session: ClientSession = None) -> DeleteResult:
        """
        Delete the document

        :param session: ClientSession - pymongo session.
        :return: DeleteResult - pymongo DeleteResult instance.
        """
        return await self.find_one({"_id": self.id}).delete()

    @classmethod
    def aggregate(
        cls,
        aggregation_pipeline,
        aggregation_model: Type[BaseModel] = None,
        session: ClientSession = None,
    ) -> AggregationPipeline:
        return cls.find_all().aggregate(
            aggregation_pipeline=aggregation_pipeline,
            aggregation_model=aggregation_model,
        )

    @classmethod
    async def count(cls) -> int:
        """
        Number of documents in the collections

        :return: int
        """
        return await cls.find_all().count()

    # Projections
    @classmethod
    def _init_projection(cls) -> Dict[str, int]:
        """
        Initializes the projection dictionary, this will be done only once

        :return: Dict[str, int] - The projection dict
        """
        document_projection: Dict[str, int] = {}
        for name, field in cls.__fields__.items():
            if field.alias:
                document_projection[field.alias] = 1
            else:
                document_projection[name] = 1
        setattr(cls, "_projection", document_projection)
        return document_projection

    @classmethod
    def _get_projection(cls) -> Dict[str, int]:
        """
        Get the projection dictionary or create it if it has
        not been built yet.

        :return: Dict[str, int] - The projection dict
        """
        document_projection: Dict[str, int] = getattr(cls, "_projection", None)
        if document_projection is None:
            document_projection = cls._init_projection()

        return document_projection

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
            document_model=cls,
            allow_index_dropping=allow_index_dropping,
            collection_class=collection_class,
        )
        setattr(cls, "CollectionMeta", collection_meta)

        for k, v in cls.__fields__.items():
            path = v.alias or v.name
            setattr(cls, k, CollectionField(path))

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
        async for json_document in cls.get_motor_collection().find_many(
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
