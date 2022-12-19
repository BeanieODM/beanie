import inspect
from typing import Optional, Any, Dict

from pydantic.fields import ModelField
from pydantic.typing import get_origin

from beanie.odm.fields import LinkTypes, LinkInfo, Link, ExpressionField

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beanie import Document


def detect_link(field: ModelField) -> Optional[LinkInfo]:
    """
    It detects link and returns LinkInfo if any found.

    :param field: ModelField
    :return: Optional[LinkInfo]
    """
    if field.type_ == Link:
        if field.allow_none is True:
            return LinkInfo(
                field=field.name,
                model_class=field.sub_fields[0].type_,  # type: ignore
                link_type=LinkTypes.OPTIONAL_DIRECT,
            )
        return LinkInfo(
            field=field.name,
            model_class=field.sub_fields[0].type_,  # type: ignore
            link_type=LinkTypes.DIRECT,
        )
    if (
        inspect.isclass(get_origin(field.outer_type_))
        and issubclass(get_origin(field.outer_type_), list)  # type: ignore
        and len(field.sub_fields) == 1  # type: ignore
    ):
        internal_field = field.sub_fields[0]  # type: ignore
        if internal_field.type_ == Link:
            if field.allow_none is True:
                return LinkInfo(
                    field=field.name,
                    model_class=internal_field.sub_fields[0].type_,  # type: ignore
                    link_type=LinkTypes.OPTIONAL_LIST,
                )
            return LinkInfo(
                field=field.name,
                model_class=internal_field.sub_fields[0].type_,  # type: ignore
                link_type=LinkTypes.LIST,
            )
    return None


def convert_ids(
    query: Dict[str, Any], doc: "Document", fetch_links: bool
) -> Dict[str, Any]:
    # TODO add all the cases
    new_query = {}
    for k, v in query.items():
        k_splitted = k.split(".")
        if (
            isinstance(k, ExpressionField)
            and doc.get_link_fields() is not None
            and len(k_splitted) == 2
            and k_splitted[0] in doc.get_link_fields().keys()  # type: ignore
            and k_splitted[1] == "id"
        ):
            if fetch_links:
                new_k = f"{k_splitted[0]}._id"
            else:
                new_k = f"{k_splitted[0]}.$id"
        else:
            new_k = k

        if isinstance(v, dict):
            new_v = convert_ids(v, doc, fetch_links)
        else:
            new_v = v

        new_query[new_k] = new_v
    return new_query
