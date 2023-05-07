import pytest
from tests.fastapi_no_mongo.models import WindowAPI
from tests.fastapi_no_mongo.repositories import WindowRepository


def test_create_window(api_client):
    payload = {"x": 10, "y": 20}
    resp = api_client.post("/v1/windows/", json=payload)
    resp_json = resp.json()
    assert resp_json["x"] == 10
    assert resp_json["y"] == 20


def test_create_house(api_client):
    payload = {"x": 10, "y": 20}
    resp = api_client.post("/v1/houses/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1


def test_create_house_with_window_link(api_client):
    payload = {"x": 10, "y": 20}
    resp = api_client.post("/v1/windows/", json=payload)

    window_id = resp.json()["_id"]

    payload = {"id": window_id}
    resp = api_client.post("/v1/houses_with_window_link/", json=payload)
    resp_json = resp.json()
    assert resp_json["windows"][0]["collection"] == "WindowAPI"


@pytest.mark.asyncio
async def test_create_house_2(api_client, window_respositry: WindowRepository):
    window = WindowAPI(x=10, y=10)
    await window_respositry.create(window)
    payload = {"name": "TEST", "windows": [str(window.id)]}
    resp = api_client.post("/v1/houses_2/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1
