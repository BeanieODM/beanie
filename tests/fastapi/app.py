import motor.motor_asyncio
from beanie import init_beanie
from fastapi import FastAPI

from tests.conftest import Settings
from tests.fastapi.models import HouseAPI, WindowAPI, DoorAPI, RoofAPI
from tests.fastapi.routes import house_router

app = FastAPI()


@app.on_event("startup")
async def app_init():
    # CREATE MOTOR CLIENT
    client = motor.motor_asyncio.AsyncIOMotorClient(Settings().mongodb_dsn)

    # INIT BEANIE
    await init_beanie(
        client.beanie_db,
        document_models=[HouseAPI, WindowAPI, DoorAPI, RoofAPI],
    )

    # ADD ROUTES
    app.include_router(house_router, prefix="/v1", tags=["house"])
