from typing import Optional

from fastapi import APIRouter, Body, status
from pydantic import BaseModel

from beanie import PydanticObjectId, WriteRules
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.fastapi.models import House, HouseAPI, Person, WindowAPI

house_router = APIRouter()
if not IS_PYDANTIC_V2:
    from fastapi.encoders import ENCODERS_BY_TYPE
    from pydantic.json import ENCODERS_BY_TYPE as PYDANTIC_ENCODERS_BY_TYPE

    ENCODERS_BY_TYPE.update(PYDANTIC_ENCODERS_BY_TYPE)


class WindowInput(BaseModel):
    id: PydanticObjectId


@house_router.post("/windows/", response_model=WindowAPI)
async def create_window(window: WindowAPI):
    await window.create()
    return window


@house_router.post("/windows_2/")
async def create_window_2(window: WindowAPI):
    return await window.save()


@house_router.get("/windows/{id}", response_model=Optional[WindowAPI])
async def get_window(id: PydanticObjectId):
    return await WindowAPI.get(id)


@house_router.post("/houses/", response_model=HouseAPI)
async def create_house(window: WindowAPI):
    house = HouseAPI(name="test_name", windows=[window])
    await house.insert(link_rule=WriteRules.WRITE)
    return house


@house_router.post("/houses_with_window_link/", response_model=HouseAPI)
async def create_houses_with_window_link(window: WindowInput):
    validator = (
        HouseAPI.model_validate if IS_PYDANTIC_V2 else HouseAPI.parse_obj
    )
    house = validator(
        dict(name="test_name", windows=[WindowAPI.link_from_id(window.id)])
    )
    await house.insert(link_rule=WriteRules.WRITE)
    return house


@house_router.post("/houses_2/", response_model=HouseAPI)
async def create_houses_2(house: HouseAPI):
    await house.insert(link_rule=WriteRules.WRITE)
    return house


@house_router.post(
    "/house",
    response_model=House,
    status_code=status.HTTP_201_CREATED,
)
async def create_house_new(house: House = Body(...)):
    person = Person(name="Bob")
    house.owner = person
    await house.save(link_rule=WriteRules.WRITE)
    await house.sync()
    return house
