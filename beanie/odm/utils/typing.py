import inspect
from typing import Any, Optional, get_args, get_origin

from beanie.odm.fields import IndexedAnnotation

from .pydantic import IS_PYDANTIC_V2, get_field_type


def extract_id_class(annotation) -> type[Any]:
    if get_origin(annotation) is not None:
        try:
            annotation = next(arg for arg in get_args(annotation) if arg is not type(None))
        except StopIteration:
            annotation = None
    if inspect.isclass(annotation):
        return annotation
    raise ValueError(f"Unknown annotation: {annotation}")


def get_index_attributes(field) -> Optional[tuple[int, dict[str, Any]]]:
    """Gets the index attributes from the field, if it is indexed.

    :param field: The field to get the index attributes from.

    :return: The index attributes, if the field is indexed. Otherwise, None.
    """
    # For fields that are directly typed with `Indexed()`, the type will have
    # an `_indexed` attribute.
    field_type = get_field_type(field)
    if hasattr(field_type, "_indexed"):
        return getattr(field_type, "_indexed", None)

    # For fields that are use `Indexed` within `Annotated`, the field will have
    # metadata that might contain an `IndexedAnnotation` instance.
    if IS_PYDANTIC_V2:
        # In Pydantic 2, the field has a `metadata` attribute with
        # the annotations.
        metadata = getattr(field, "metadata", None)
    elif hasattr(field, "annotation") and hasattr(field.annotation, "__metadata__"):
        # In Pydantic 1, the field has an `annotation` attribute with the
        # type assigned to the field. If the type is annotated, it will
        # have a `__metadata__` attribute with the annotations.
        metadata = field.annotation.__metadata__
    else:
        return None

    if metadata is None:
        return None

    try:
        iter(metadata)
    except TypeError:
        return None

    indexed_annotation = next(
        (annotation for annotation in metadata if isinstance(annotation, IndexedAnnotation)),
        None,
    )

    return getattr(indexed_annotation, "_indexed", None)


def is_generic_alias(obj: Any) -> bool:
    """Check if the object is a typing or built-in generic alias (e.g., list[str], List[int]).

    :param obj: An object instance.

    :return: True if obj is a typing or built-in generic alias, False otherwise.
    """

    # Check built-in generic aliases (e.g. list[str])
    try:
        from types import GenericAlias

        if isinstance(obj, GenericAlias):
            return True
    except ImportError:
        pass  # Python < 3.9

    # Check legacy typing generics (e.g. typing.List[str])
    try:
        from typing import _GenericAlias  # type: ignore[attr-defined]

        if isinstance(obj, _GenericAlias):
            return True
    except ImportError:
        pass

    return False
