from contextlib import asynccontextmanager

from fastapi import FastAPI
from mongomock_motor import AsyncMongoMockClient as AsyncMongoClient

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


@asynccontextmanager
async def live_span(_: FastAPI):
    # CREATE ASYNC PYMONGO CLIENT
    client = AsyncMongoClient(Settings().mongodb_dsn)

    # INIT BEANIE
    await init_beanie(
        client.beanie_db,
        document_models=[House, Person, HouseAPI, WindowAPI, DoorAPI, RoofAPI],
    )

    yield


app = FastAPI(lifespan=live_span)

# ADD ROUTES
app.include_router(house_router, prefix="/v1", tags=["house"])
