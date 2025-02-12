from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from beanie import init_beanie
from tests.conftest import Settings
from tests.fastapi.models import (
    DoorAPI,
    House,
    HouseAPI,
    Person,
    RoofAPI,
    WindowAPI,
)
from tests.fastapi.routes import house_router

MODELS = [House, Person, HouseAPI, WindowAPI, DoorAPI, RoofAPI]


async def clean_db():
    for model in MODELS:
        await model.get_pymongo_collection().drop()
        await model.get_pymongo_collection().drop_indexes()


@asynccontextmanager
async def live_span(_: FastAPI):
    client = None
    try:
        client = AsyncMongoClient(Settings().mongodb_dsn)
        await init_beanie(client.beanie_db, document_models=MODELS)

        yield
    finally:
        await clean_db()
        if client:
            await client.close()


app = FastAPI(lifespan=live_span)

# ADD ROUTES
app.include_router(house_router, prefix="/v1", tags=["house"])
