from motor.motor_asyncio import (
    AsyncIOMotorCollection as AsyncIOMotorCollection,
    AsyncIOMotorDatabase as AsyncIOMotorDatabase,
)
from pydantic.main import BaseModel
from pymongo import IndexModel
from typing import List, Optional, Type
from beanie.odm.documents import DocType

class IndexModelField(IndexModel):
    @classmethod
    def __get_validators__(cls) -> None: ...
    @classmethod
    def validate(cls, v): ...

class CollectionInputParameters(BaseModel):
    name: str
    indexes: List[IndexModelField]
    class Config:
        arbitrary_types_allowed: bool

class CollectionMeta:
        name: str
        motor_collection: AsyncIOMotorCollection
        indexes: List

async def collection_factory(
    database: AsyncIOMotorDatabase,
    document_model: Type[DocType],
    allow_index_dropping: bool,
    collection_class: Optional[Type] = ...,
) -> CollectionMeta: ...
