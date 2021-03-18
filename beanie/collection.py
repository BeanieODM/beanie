from typing import List, Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic.main import BaseModel
from pymongo import IndexModel


class IndexModelField(IndexModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, IndexModel):
            return v
        else:
            return IndexModel(v)


class CollectionInputParameters(BaseModel):
    name: str = None
    indexes: List[IndexModelField] = []

    class Config:
        arbitrary_types_allowed = True


async def collection_factory(
    database: AsyncIOMotorDatabase,
    document_class: Type,
    collection_class: Optional[Type] = None,
) -> Type:
    """
    Collection factory.
    Creates internal CollectionMeta class for the Document on the init step,

    :param database: Motor database instance
    :param document_class: a class, inherited from Document class
    :param collection_class: Collection, which was set up by user
    :return: Collection class
    """
    # parse collection parameters
    if collection_class:
        collection_parameters = CollectionInputParameters.parse_obj(
            vars(collection_class)
        )
    else:
        collection_parameters = CollectionInputParameters()

    # set collection name
    if not collection_parameters.name:
        collection_parameters.name = document_class.__name__

    # create motor collection
    collection = database[collection_parameters.name]

    # create indexes
    if collection_parameters.indexes:
        await collection.create_indexes(collection_parameters.indexes)

    # create internal CollectionMeta class for the Document
    class CollectionMeta:
        name: str = collection_parameters.name
        motor_collection: AsyncIOMotorCollection = collection
        indexes: List = collection_parameters.indexes

    return CollectionMeta
