from typing import Any, Type, Union, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def parse_obj(
    model: Union[Type[BaseModel], Type["Document"]], data: Any
) -> BaseModel:
    if hasattr(model, "_parse_obj_saving_state"):
        return model._parse_obj_saving_state(data)  # type: ignore
    return model.parse_obj(data)
