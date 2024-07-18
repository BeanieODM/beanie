import pybase64
import pytest

from tests.fastapi.models import WindowAPI


async def test_create_window(api_client):
    payload = {"x": 10, "y": 20}
    resp = await api_client.post("/v1/windows/", json=payload)
    resp_json = resp.json()
    assert resp_json["x"] == 10
    assert resp_json["y"] == 20


async def test_create_house(api_client):
    payload = {"x": 10, "y": 20}
    resp = await api_client.post("/v1/houses/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1


async def test_create_house_with_window_link(api_client):
    payload = {"x": 10, "y": 20}
    resp = await api_client.post("/v1/windows/", json=payload)

    window_id = resp.json()["_id"]

    payload = {"id": window_id}
    resp = await api_client.post("/v1/houses_with_window_link/", json=payload)
    resp_json = resp.json()
    assert resp_json["windows"][0]["collection"] == "WindowAPI"


async def test_create_house_2(api_client):
    window = WindowAPI(x=10, y=10)
    await window.insert()
    payload = {"name": "TEST", "windows": [str(window.id)]}
    resp = await api_client.post("/v1/houses_2/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1


async def test_revision_id(api_client):
    payload = {"x": 10, "y": 20}
    resp = await api_client.post("/v1/windows_2/", json=payload)
    resp_json = resp.json()
    assert "revision_id" not in resp_json
    assert resp_json == {"x": 10, "y": 20, "_id": resp_json["_id"]}


@pytest.mark.parametrize(
    "test_data",
    [
        b"\xed\xa0\x80",  # Start of a surrogate pair without continuation
        b"\xf0\x82\x82\xac",  # Overlong encoding of U+0020AC
        b"\xed\xa0\x80\xed\xbf\xbf",  # Encoded surrogate pair
        b"\xc0\xaf",  # Overlong encoding of '/'
        b"\xe0\x80\xaf",  # Overlong encoding of '/'
        b"\xf0\x8f\xbf\xbf",  # Beyond Unicode range
    ],
)
async def test_binary(api_client, test_data):
    payload = {
        "binary": pybase64.standard_b64encode(test_data).decode("utf-8")
    }
    resp = await api_client.post("/v1/bytes/", json=payload)
    resp = resp.json()
    assert resp["binary"] == pybase64.standard_b64encode(test_data).decode(
        "utf-8"
    )
