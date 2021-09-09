from typing import Any, Type

from pydantic import BaseModel


def parse_obj(model: Type[BaseModel], data: Any) -> BaseModel:
    if hasattr(model, "_parse_obj_saving_state"):
        return model._parse_obj_saving_state(data)
    return model.parse_obj(data)
