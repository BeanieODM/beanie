from typing import Dict, Type, TypeVar, Optional

from pydantic import BaseModel

from beanie.odm.interfaces.detector import ModelType

ProjectionModelType = TypeVar("ProjectionModelType", bound=BaseModel)


def get_projection(
    model: Type[ProjectionModelType],
) -> Optional[Dict[str, int]]:
    if hasattr(model, "get_model_type") and (
        model.get_model_type() == ModelType.UnionDoc  # type: ignore
        or (  # type: ignore
            model.get_model_type() == ModelType.Document  # type: ignore
            and model._inheritance_inited  # type: ignore
        )
    ):  # type: ignore
        return None

    if hasattr(model, "Settings"):  # MyPy checks
        settings = getattr(model, "Settings")

        if hasattr(settings, "projection"):
            return getattr(settings, "projection")

    if model.model_config.get("extra") == "allow":
        return None

    document_projection: Dict[str, int] = {}

    for name, field in model.model_fields.items():
        document_projection[field.alias or name] = 1
    return document_projection
