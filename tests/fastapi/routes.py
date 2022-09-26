from fastapi import APIRouter
from pydantic import BaseModel

from beanie import WriteRules, PydanticObjectId
from tests.fastapi.models import HouseAPI, WindowAPI

house_router = APIRouter()


class WindowInput(BaseModel):
    id: PydanticObjectId


@house_router.post("/windows/", response_model=WindowAPI)
async def create_window(window: WindowAPI):
    await window.create()
    return window


@house_router.post("/houses/", response_model=HouseAPI)
async def create_house(window: WindowAPI):
    house = HouseAPI(name="test_name", windows=[window])
    await house.insert(link_rule=WriteRules.WRITE)
    return house


@house_router.post("/houses_with_window_link/", response_model=HouseAPI)
async def create_houses_with_window_link(window: WindowInput):
    house = HouseAPI.parse_obj(
        dict(name="test_name", windows=[WindowAPI.link_from_id(window.id)])
    )
    await house.insert(link_rule=WriteRules.WRITE)
    return house


@house_router.post("/houses_2/", response_model=HouseAPI)
async def create_houses_2(house: HouseAPI):
    await house.insert(link_rule=WriteRules.WRITE)
    return house
