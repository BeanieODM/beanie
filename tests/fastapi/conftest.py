import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from tests.fastapi.app import app


@pytest.fixture()
async def api_client():
    """api client fixture."""
    async with LifespanManager(app, startup_timeout=100, shutdown_timeout=100):
        server_name = "http://localhost"
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url=server_name
        ) as ac:
            yield ac
