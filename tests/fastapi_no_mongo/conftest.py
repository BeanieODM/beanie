import pytest
from fastapi.testclient import TestClient

from tests.fastapi_no_mongo.app import app
from tests.fastapi_no_mongo.dependencies import provide_windows_repository, provide_house_repository
from tests.fastapi_no_mongo.repositories import WindowRepository, HouseRepository


@pytest.fixture
def api_client():
    return TestClient(app)


@pytest.fixture
def fake_window_repository() -> WindowRepository:
    return WindowRepository()


@pytest.fixture
def fake_house_repository(fake_window_repository: WindowRepository) -> HouseRepository:
    return HouseRepository(fake_window_repository)


@pytest.fixture(autouse=True)
def override_window_repository_provider(fake_window_repository: WindowRepository):
    app.dependency_overrides[provide_windows_repository] = lambda: fake_window_repository


@pytest.fixture(autouse=True)
def override_house_repository_provider(fake_house_repository: HouseRepository):
    app.dependency_overrides[provide_house_repository] = lambda: fake_house_repository
