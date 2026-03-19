import inspect
from typing import Any, get_args, get_origin

from beanie.odm.fields import IndexedAnnotation

from .pydantic import get_field_type


def extract_id_class(annotation) -> type[Any]:
    if get_origin(annotation) is not None:
        try:
            annotation = next(
                arg for arg in get_args(annotation) if arg is not type(None)
            )
        except StopIteration:
            annotation = None
    if inspect.isclass(annotation):
        return annotation
    raise ValueError(f"Unknown annotation: {annotation}")


def get_index_attributes(field) -> tuple[int, dict[str, Any]] | None:
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
    # In Pydantic 2, the field has a `metadata` attribute with
    # the annotations.
    metadata = getattr(field, "metadata", None)

    if metadata is None:
        return None

    try:
        iter(metadata)
    except TypeError:
        return None

    indexed_annotation = next(
        (
            annotation
            for annotation in metadata
            if isinstance(annotation, IndexedAnnotation)
        ),
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
