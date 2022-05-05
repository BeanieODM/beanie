from typing import Dict, Type, TypeVar, Optional

from pydantic import BaseModel

from beanie.odm.interfaces.detector import ModelType

ProjectionModelType = TypeVar("ProjectionModelType", bound=BaseModel)


def get_projection(
    model: Type[ProjectionModelType],
) -> Optional[Dict[str, int]]:
    if (
        hasattr(model, "get_model_type")
        and model.get_model_type() == ModelType.UnionDoc
    ):
        return None
    if hasattr(model, "Settings"):  # MyPy checks
        settings = getattr(model, "Settings")
        if hasattr(settings, "projection"):
            return getattr(settings, "projection")
    document_projection: Dict[str, int] = {}
    for name, field in model.__fields__.items():
        document_projection[field.alias] = 1
    return document_projection
