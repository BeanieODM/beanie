from fastapi import APIRouter, Depends
from pydantic import BaseModel

from beanie import PydanticObjectId
from tests.fastapi_no_mongo.dependencies import provide_windows_repository, provide_house_repository
from tests.fastapi_no_mongo.models import HouseAPI, WindowAPI

house_router = APIRouter()


class WindowInput(BaseModel):
    id: PydanticObjectId


@house_router.post("/windows/", response_model=WindowAPI)
async def create_window(window: WindowAPI, window_repository=Depends(provide_windows_repository)):
    await window_repository.create(window)
    return window


@house_router.post("/houses/", response_model=HouseAPI)
async def create_house(window: WindowAPI, house_repository=Depends(provide_house_repository)):
    house = HouseAPI(name="test_name", windows=[window])
    await house_repository.create(house)
    return house


@house_router.post("/houses_with_window_link/", response_model=HouseAPI)
async def create_houses_with_window_link(window: WindowInput, window_repository=Depends(provide_windows_repository), house_repository=Depends(provide_house_repository)):
    house = dict(name="test_name", windows=[window_repository.get_by_id(window.id)])
    house_repository.create_house_from_dict(house)
    return house


@house_router.post("/houses_2/", response_model=HouseAPI)
async def create_houses_2(house: HouseAPI, house_repository=Depends(provide_house_repository)):
    house_repository.create(house)
    return house
