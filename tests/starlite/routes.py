from pydantic import BaseModel
from starlite import post, Controller

from beanie import WriteRules, PydanticObjectId
from tests.starlite.models import HouseAPI, WindowAPI


class WindowInput(BaseModel):
    id: PydanticObjectId


class UserOrderController(Controller):
    path = "/v1"

    @post(path="/windows/")
    async def create_window(self, data: WindowAPI) -> WindowAPI:
        await data.create()
        return data

    @post(path="/houses/")
    async def create_house(self, data: WindowAPI) -> HouseAPI:
        house = HouseAPI(name="test_name", windows=[data])
        await house.insert(link_rule=WriteRules.WRITE)
        return house

    @post(path="/houses_with_window_link/")
    async def create_houses_with_window_link(
        self, data: WindowInput
    ) -> HouseAPI:
        house = HouseAPI.parse_obj(
            dict(name="test_name", windows=[WindowAPI.link_from_id(data.id)])
        )
        await house.insert(link_rule=WriteRules.WRITE)
        return house

    @post(path="/houses_2/")
    async def create_houses_2(self, data: HouseAPI) -> HouseAPI:
        await data.insert(link_rule=WriteRules.WRITE)
        return data
