import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from tests.fastapi.app import app
from tests.fastapi.models import HouseAPI, WindowAPI, DoorAPI, RoofAPI


@pytest.fixture(autouse=True)
async def api_client(clean_db):
    """api client fixture."""
    async with LifespanManager(app, startup_timeout=100, shutdown_timeout=100):
        server_name = "https://localhost"
        async with AsyncClient(app=app, base_url=server_name) as ac:
            yield ac


@pytest.fixture(autouse=True)
async def clean_db(db):
    models = [HouseAPI, WindowAPI, DoorAPI, RoofAPI]
    yield None

    for model in models:
        await model.get_motor_collection().drop()
        await model.get_motor_collection().drop_indexes()
