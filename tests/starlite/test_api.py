from tests.starlite.models import WindowAPI


async def test_create_window(starlite_client):
    payload = {"x": 10, "y": 20}
    resp = await starlite_client.post("/v1/windows/", json=payload)
    resp_json = resp.json()
    assert resp_json["x"] == 10
    assert resp_json["y"] == 20
    assert "_id" in resp_json


async def test_create_house(starlite_client):
    payload = {"x": 10, "y": 20}
    resp = await starlite_client.post("/v1/houses/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1


async def test_create_house_with_window_link(starlite_client):
    payload = {"x": 10, "y": 20}
    resp = await starlite_client.post("/v1/windows/", json=payload)

    window_id = resp.json()["_id"]

    payload = {"id": window_id}
    resp = await starlite_client.post(
        "/v1/houses_with_window_link/", json=payload
    )
    resp_json = resp.json()
    assert resp_json["windows"][0]["collection"] == "WindowAPI"


async def test_create_house_2(starlite_client):
    window = WindowAPI(x=10, y=10)
    await window.insert()
    payload = {"name": "TEST", "windows": [str(window.id)]}
    resp = await starlite_client.post("/v1/houses_2/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1
