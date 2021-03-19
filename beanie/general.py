import asyncio
from typing import List, Type

from motor.motor_asyncio import AsyncIOMotorDatabase

from beanie import Document


async def init_beanie(
    database: AsyncIOMotorDatabase, document_models: List[Type[Document]]
):
    await asyncio.gather(
        *[model.init_collection(database) for model in document_models]
    )
