from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from bson import DBRef

from beanie.odm.fields import (
    ExpressionField,
    LinkInfo,
)

if TYPE_CHECKING:
    from beanie import Document

# Operators whose values should be wrapped in DBRef.
# Others ($exists, $type, etc.) expect non-DBRef values.
_COMPARISON_OPS = frozenset(
    {"$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"}
)


def _to_dbref(value: Any, collection: str) -> Any:
    """Wrap a single value or list of values in DBRef."""
    if isinstance(value, list):
        return [DBRef(collection, v) for v in value]
    return DBRef(collection, value)


def _convert_value_to_dbref(value: Any, collection: str) -> Any:
    """Convert query values to DBRef, respecting operator semantics."""
    if isinstance(value, Mapping):
        return {
            op: _to_dbref(val, collection) if op in _COMPARISON_OPS else val
            for op, val in value.items()
        }
    return _to_dbref(value, collection)


def _resolve_link_key_value(
    key_str: str,
    value: Any,
    link_fields: dict[str, LinkInfo] | None,
    fetch_links: bool,
) -> tuple[str, Any]:
    """Transform a Link field's key and value for MongoDB query."""
    if fetch_links:
        return key_str, value

    if link_fields and key_str.endswith("._id"):
        field_name = key_str[:-4]  # strip "._id"
        link_info = link_fields.get(field_name)
        if link_info is not None:
            collection = link_info.document_class.get_collection_name()
            return field_name, _convert_value_to_dbref(value, collection)

    # Fallback: legacy $id notation
    return key_str.replace("._id", ".$id"), value


def _resolve_value(value: Any, doc: "Document", fetch_links: bool) -> Any:
    """Recurse into nested query structures ($or, $and lists, etc.)."""
    if isinstance(value, Mapping):
        return resolve_query_paths(value, doc, fetch_links)
    if isinstance(value, list):
        return [
            resolve_query_paths(e, doc, fetch_links)
            if isinstance(e, Mapping)
            else e
            for e in value
        ]
    return value


def resolve_query_paths(
    query: Mapping[str, Any],
    doc: "Document",
    fetch_links: bool,
) -> dict[str, Any]:
    """Resolve ExpressionField paths for Link fields in a MongoDB query.

    When ``fetch_links`` is ``False``, converts Link id queries to full
    DBRef matches so MongoDB can use the index on the Link field (#1131).
    When ``True``, keeps ``_id`` notation for the ``$lookup`` pipeline.
    """
    new_query: dict[str, Any] = {}
    link_fields = doc.get_link_fields()

    for k, v in query.items():
        if isinstance(k, ExpressionField) and k._field_resolution.is_link:
            # str.__str__ avoids ExpressionField.__getitem__ intercepting slices
            key_str = str.__str__(k)
            new_k, new_v = _resolve_link_key_value(
                key_str, v, link_fields, fetch_links
            )
        else:
            new_k = k
            new_v = _resolve_value(v, doc, fetch_links)

        new_query[new_k] = new_v
    return new_query


def convert_ids(
    query: Mapping[str, Any], doc: "Document", fetch_links: bool
) -> dict[str, Any]:
    """Deprecated -- use :func:`resolve_query_paths` instead."""
    return resolve_query_paths(query, doc, fetch_links)
