import base64

import pybase64
from fastapi import APIRouter
from pydantic import BaseModel

from beanie import PydanticObjectId, WriteRules
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.fastapi.models import BinAPI, HouseAPI, WindowAPI

house_router = APIRouter()
if not IS_PYDANTIC_V2:
    from fastapi.encoders import ENCODERS_BY_TYPE
    from pydantic.json import ENCODERS_BY_TYPE as PYDANTIC_ENCODERS_BY_TYPE

    ENCODERS_BY_TYPE.update(PYDANTIC_ENCODERS_BY_TYPE)

    class BinInput(BaseModel):
        binary: bytes

        class Config:
            json_encoders = {
                bytes: lambda v: pybase64.standard_b64encode(v).decode("utf-8")
            }


else:
    from pydantic import Base64Bytes

    class BinInput(BaseModel):
        binary: Base64Bytes


class WindowInput(BaseModel):
    id: PydanticObjectId


@house_router.post("/windows/", response_model=WindowAPI)
async def create_window(window: WindowAPI):
    await window.create()
    return window


@house_router.post("/windows_2/")
async def create_window_2(window: WindowAPI):
    return await window.save()


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


@house_router.post("/bytes/", response_model=BinAPI)
async def create_bytes(binary: BinInput):
    binary = binary.binary
    if isinstance(binary, str):
        binary = base64.b64decode(binary)

    return await BinAPI(binary=binary).insert()
