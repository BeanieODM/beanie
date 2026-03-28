import warnings
from functools import lru_cache
from typing import Any, TypeVar

from pydantic import BaseModel, create_model

from beanie.odm.interfaces.detector import ModelType
from beanie.odm.utils.pydantic import get_config_value, get_model_fields

ProjectionModelType = TypeVar("ProjectionModelType", bound=BaseModel)


def get_projection(
    model: type[ProjectionModelType],
) -> dict[str, int] | None:
    if hasattr(model, "get_model_type") and (
        model.get_model_type() is ModelType.UnionDoc  # type: ignore
        or (  # type: ignore
            model.get_model_type() is ModelType.Document  # type: ignore
            and model._inheritance_inited  # type: ignore
        )
    ):  # type: ignore
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


@lru_cache(maxsize=64)
def get_exclusion_model(
    base_model: type[ProjectionModelType],
    exclude_fields: tuple[str, ...],
) -> type[ProjectionModelType]:
    """Create a cached model variant where excluded fields become
    ``Optional[<original_type>] = None``.

    *exclude_fields* must contain **Python field names** (not MongoDB
    aliases).  Callers are expected to normalise user input before
    calling this function.

    This allows ``model_validate`` to succeed when MongoDB omits
    excluded fields from the response.  The returned model is a
    subclass of *base_model*, so ``isinstance`` checks still pass.
    """
    fields = get_model_fields(base_model)

    field_overrides: dict[str, Any] = {}
    for name in exclude_fields:
        if name in fields:
            field_overrides[name] = (
                fields[name].annotation | None,  # type: ignore[operator]
                None,
            )

    if not field_overrides:
        return base_model  # type: ignore[return-value]

    with warnings.catch_warnings():
        # Suppress Pydantic "shadows an attribute in parent" warning
        # that fires when we override fields in the derived model.
        warnings.filterwarnings(
            "ignore", message="Field name.*shadows an attribute"
        )
        return create_model(  # type: ignore[return-value]
            f"{base_model.__name__}__Exclusion",
            __base__=base_model,
            **field_overrides,
        )
