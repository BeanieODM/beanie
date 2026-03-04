from typing import TypeVar

from pydantic import BaseModel

from beanie.odm.documents import Document
from beanie.odm.union_doc import UnionDoc
from beanie.odm.utils.pydantic import get_config_value, get_model_fields

ProjectionModelType = TypeVar("ProjectionModelType", bound=BaseModel)


def get_projection(
    model: type[ProjectionModelType],
) -> dict[str, int] | None:
    if isinstance(model, UnionDoc) or (
        isinstance(model, Document) and model._inheritance_inited
    ):
        return None

    if hasattr(model, "Settings"):  # MyPy checks
        settings = model.Settings

        if hasattr(settings, "projection"):
            return settings.projection

    if get_config_value(model, "extra") == "allow":
        return None

    document_projection: dict[str, int] = {}

    for name, field in get_model_fields(model).items():
        document_projection[field.alias or name] = 1
    return document_projection
