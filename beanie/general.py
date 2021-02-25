from typing import List, Type

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie import Document


def init_beanie(database: AsyncIOMotorDatabase, document_models: List[Type[Document]]):
    for model in document_models:
        model._create_collection(database)
