from typing import Type

from motor.motor_asyncio import AsyncIOMotorCursor
from pydantic.main import BaseModel


class Cursor:
    def __init__(
        self, motor_cursor: AsyncIOMotorCursor, model: Type[BaseModel] = None
    ):
        self.motor_cursor = motor_cursor
        self.model = model

    def __aiter__(self):
        return self

    async def __anext__(self):
        next_item = await self.motor_cursor.__anext__()
        return self.model.parse_obj(next_item) if self.model else next_item

    async def to_list(self, length=None):
        motor_list = await self.motor_cursor.to_list(length)
        if self.model:
            return [self.model.parse_obj(i) for i in motor_list]
        return motor_list
