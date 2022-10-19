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

    if getattr(model.Config, "extra", None) == "allow":
        return None

    document_projection: Dict[str, int] = {}

    if hasattr(model, "Settings"):  # MyPy checks
        settings = getattr(model, "Settings")
        if hasattr(settings, "projection"):
            return getattr(settings, "projection")

        if getattr(settings, 'single_root_inheritance', False):
            # include class_id if model has children or is child of some parent
            if model.is_part_of_inheritance():
                document_projection['_class_id'] = 1

            # include also all possible fields of any children
            for child in model.get_children():
                for name, field in child.__fields__.items():
                    if field.alias not in document_projection:
                        document_projection[field.alias] = 1

    for name, field in model.__fields__.items():
        document_projection[field.alias] = 1

    return document_projection
