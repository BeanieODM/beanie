from tests.fastapi.models import WindowAPI


async def test_create_window(api_client):
    payload = {"x": 10, "y": 20}
    resp = await api_client.post("/v1/windows/", json=payload)
    resp_json = resp.json()
    assert resp_json["x"] == 10
    assert resp_json["y"] == 20


async def test_get_window(api_client):
    payload = {"x": 10, "y": 20}
    data1 = (
        (await api_client.post("/v1/windows/", json=payload))
        .raise_for_status()
        .json()
    )
    window_id = data1["_id"]
    data2 = (
        (await api_client.get(f"/v1/windows/{window_id}"))
        .raise_for_status()
        .json()
    )
    assert data2 == data1


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


async def test_create_house_new(api_client):
    payload = {
        "name": "FreshHouse",
        "owner": {"name": "will_be_overridden_to_Bob"},
    }
    resp = await api_client.post("/v1/house", json=payload)
    resp_json = resp.json()

    assert resp_json["name"] == payload["name"]
    assert resp_json["owner"]["name"] == payload["owner"]["name"][-3:]
    assert resp_json["owner"]["house"]["collection"] == "House"
