import motor.motor_asyncio
from starlite import Starlite

from beanie import init_beanie
from tests.conftest import Settings
from tests.starlite.models import HouseAPI, WindowAPI, DoorAPI, RoofAPI
from tests.starlite.routes import UserOrderController


async def app_init():
    # CREATE MOTOR CLIENT
    client = motor.motor_asyncio.AsyncIOMotorClient(Settings().mongodb_dsn)

    # INIT BEANIE
    await init_beanie(
        client.beanie_db,
        document_models=[HouseAPI, WindowAPI, DoorAPI, RoofAPI],
    )


app = Starlite(route_handlers=[UserOrderController], on_startup=[app_init])
