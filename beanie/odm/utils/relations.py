from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Dict
from typing import Mapping as MappingType

from beanie.odm.fields import (
    ExpressionField,
)

if TYPE_CHECKING:
    from beanie import Document


def _translate_link_key(key: str, fetch_links: bool) -> str:
    """Translate an ExpressionField path that crosses a Link boundary.

    When the path was built through :pymethod:`ExpressionField.__getattr__`,
    Pydantic alias resolution converts the ``id`` field to ``_id``.  In
    MongoDB, however, an unfetched Link is stored as a **DBRef** whose
    identifier field is ``$id``, not ``_id``.

    This function performs the conversion at query time so that:

    * ``fetch_links=False`` →  ``door._id``  becomes ``door.$id``
    * ``fetch_links=True``  →  ``door._id``  is kept as-is (the
      ``$lookup`` stage replaces the DBRef with the full document).
    """
    if fetch_links:
        return key
    return key.replace("._id", ".$id")


def resolve_query_paths(
    query: MappingType[str, Any],
    doc: "Document",
    fetch_links: bool,
) -> Dict[str, Any]:
    """Resolve :class:`ExpressionField` paths for a MongoDB query.

    Replaces the legacy ``convert_ids`` helper with a metadata-driven
    approach: each :class:`ExpressionField` carries a
    :class:`~beanie.odm.fields.FieldResolution` that records whether
    the path crosses a ``Link`` / ``BackLink`` boundary.  When it does,
    the ``_id`` ↔ ``$id`` translation is applied based on whether the
    query will use ``$lookup`` (``fetch_links``).
    """
    new_query: Dict[str, Any] = {}
    for k, v in query.items():
        if isinstance(k, ExpressionField) and k._field_resolution.is_link:
            new_k = _translate_link_key(k, fetch_links)
        else:
            new_k = k

        new_v: Any
        if isinstance(v, Mapping):
            new_v = resolve_query_paths(v, doc, fetch_links)
        elif isinstance(v, list):
            new_v = [
                resolve_query_paths(ele, doc, fetch_links)
                if isinstance(ele, Mapping)
                else ele
                for ele in v
            ]
        else:
            new_v = v

        new_query[new_k] = new_v
    return new_query


def convert_ids(
    query: MappingType[str, Any], doc: "Document", fetch_links: bool
) -> Dict[str, Any]:
    """Deprecated — use :func:`resolve_query_paths` instead."""
    return resolve_query_paths(query, doc, fetch_links)
