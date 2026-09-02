import warnings
from copy import copy
from functools import lru_cache
from types import UnionType
from typing import Any, Optional, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel, create_model

from beanie.odm.interfaces.detector import ModelType
from beanie.odm.utils.pydantic import get_config_value, get_model_fields

ProjectionModelType = TypeVar("ProjectionModelType", bound=BaseModel)

_SEQUENCE_ORIGINS = (list, set, frozenset)


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


def _split_exclusion_paths(
    exclude_fields: tuple[str, ...],
) -> tuple[set[str], dict[str, tuple[str, ...]]]:
    """Split dotted exclusion paths into whole-field and nested groups.

    ``("a", "b.c", "b.d")`` becomes ``({"a"}, {"b": ("c", "d")})``.
    A whole-field exclusion always wins over nested paths below it.
    """
    whole: set[str] = set()
    nested: dict[str, list[str]] = {}
    for path in exclude_fields:
        head, _, rest = path.partition(".")
        if rest:
            nested.setdefault(head, []).append(rest)
        else:
            whole.add(head)
    return whole, {
        head: tuple(paths)
        for head, paths in nested.items()
        if head not in whole
    }


def _descend_annotation(
    annotation: Any,
    sub_paths: tuple[str, ...],
    owner_name: str,
    field_name: str,
) -> Any:
    """Rebuild *annotation* so that *sub_paths* are excluded inside it.

    Supports models, optional models and sequences of models, including
    combinations such as ``list[Item] | None``.  Anything else (links,
    mappings, unions of several models, ...) raises ``ValueError`` --
    silently ignoring the path would make MongoDB strip the subfield
    while Pydantic still required it.
    """
    origin = get_origin(annotation)

    if origin in (Union, UnionType):
        variants = [a for a in get_args(annotation) if a is not type(None)]
        if len(variants) == 1:
            return Optional[  # noqa: UP045
                _descend_annotation(
                    variants[0], sub_paths, owner_name, field_name
                )
            ]
    elif origin in _SEQUENCE_ORIGINS:
        args = get_args(annotation)
        if len(args) == 1:
            return origin[
                _descend_annotation(args[0], sub_paths, owner_name, field_name)
            ]
    elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return get_exclusion_model(annotation, sub_paths)

    raise ValueError(
        f"Cannot exclude nested field(s) "
        f"{', '.join(f'{field_name}.{p}' for p in sub_paths)!r} on "
        f"{owner_name}: field {field_name!r} is annotated as "
        f"{annotation!r}, which beanie cannot rebuild as an exclusion "
        f"model. Exclude the whole {field_name!r} field instead, or use "
        f"a projection model."
    )


@lru_cache(maxsize=128)
def get_exclusion_model(
    base_model: type[ProjectionModelType],
    exclude_fields: tuple[str, ...],
) -> type[ProjectionModelType]:
    """Create a cached model variant where excluded fields become
    ``Optional[<original_type>] = None``.

    *exclude_fields* must contain **Python field names** (not MongoDB
    aliases), optionally as dotted paths into embedded models.  Callers
    are expected to normalise user input before calling this function.

    This allows ``model_validate`` to succeed when MongoDB omits
    excluded fields from the response.  The returned model is a
    subclass of *base_model*, so ``isinstance`` checks still pass.

    Every inherited field is re-declared explicitly, even the ones that
    are not excluded.  That is deliberate: ``init_beanie`` installs
    ``ExpressionField`` class attributes on document models, and when
    Pydantic builds a subclass it picks those up as field *defaults*
    unless the field is re-declared.  Without this, every field would
    silently default to the string of its own name.
    """
    fields = get_model_fields(base_model)
    whole, nested = _split_exclusion_paths(exclude_fields)
    whole &= fields.keys()
    nested = {k: v for k, v in nested.items() if k in fields}

    if not whole and not nested:
        return base_model  # type: ignore[return-value]

    field_overrides: dict[str, Any] = {}
    for name, field_info in fields.items():
        if name in whole:
            annotation = (
                Any if field_info.annotation is None else field_info.annotation
            )
            field_overrides[name] = (Optional[annotation], None)  # noqa: UP045
        elif name in nested:
            field_overrides[name] = (
                _descend_annotation(
                    field_info.annotation,
                    nested[name],
                    base_model.__name__,
                    name,
                ),
                copy(field_info),
            )
        else:
            # Re-declared unchanged so Pydantic does not fall back to the
            # ExpressionField class attribute as this field's default.
            field_overrides[name] = (field_info.annotation, copy(field_info))

    with warnings.catch_warnings():
        # Suppress Pydantic "shadows an attribute in parent" warning
        # that fires when we override fields in the derived model.
        warnings.filterwarnings(
            "ignore", message="Field name.*shadows an attribute"
        )
        exclusion_model = create_model(
            f"{base_model.__name__}__Exclusion",
            __base__=base_model,
            **field_overrides,
        )

    # Marks the model as partially loaded. Whole-document writes check
    # this and refuse, so that excluded fields cannot be silently
    # written back as None.
    type.__setattr__(
        exclusion_model, "_beanie_exclusion_fields", exclude_fields
    )
    return exclusion_model  # type: ignore[return-value]
