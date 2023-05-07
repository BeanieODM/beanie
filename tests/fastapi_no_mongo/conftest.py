import pytest
from httpx import AsyncClient

from tests.fastapi.app import app
from tests.fastapi.models import HouseAPI, WindowAPI, DoorAPI, RoofAPI


@pytest.fixture(autouse=True)
async def api_client():
    """api client fixture."""
    server_name = "https://localhost"
    async with AsyncClient(app=app, base_url=server_name) as ac:
        yield ac
