import inspect
from typing import Optional, Any, Dict, get_origin

from pydantic.fields import FieldInfo

# from pydantic.fields import ModelField
# from pydantic.typing import get_origin

from beanie.odm.fields import (
    LinkTypes,
    LinkInfo,
    Link,
    ExpressionField,
    BackLink,
)

from typing import TYPE_CHECKING

from beanie.odm.utils.typing import get_annotation_type

if TYPE_CHECKING:
    from beanie import Document


def detect_link(field: FieldInfo, field_name: str) -> Optional[LinkInfo]:
    """
    It detects link and returns LinkInfo if any found.

    :param field: ModelField
    :return: Optional[LinkInfo]
    """
    annotation_type = get_annotation_type(field.annotation)
    if annotation_type is None:
        return None

    if annotation_type.is_list is False:
        if annotation_type.base_class == Link:
            if annotation_type.is_optional is True:
                return LinkInfo(
                    field_name=field_name,
                    lookup_field_name=field_name,
                    document_class=annotation_type.generic_type,  # type: ignore
                    link_type=LinkTypes.OPTIONAL_DIRECT,
                )
            print(annotation_type.generic_type)
            return LinkInfo(
                field_name=field_name,
                lookup_field_name=field_name,
                document_class=annotation_type.generic_type,  # type: ignore
                link_type=LinkTypes.DIRECT,
            )
        if annotation_type.base_class == BackLink:
            if annotation_type.is_optional is True:
                return LinkInfo(
                    field_name=field_name,
                    lookup_field_name=field.json_schema_extra["original_field"],
                    document_class=annotation_type.generic_type,  # type: ignore
                    link_type=LinkTypes.OPTIONAL_BACK_DIRECT,
                )
            return LinkInfo(
                field_name=field_name,
                lookup_field_name=field.json_schema_extra["original_field"],
                document_class=field.sub_fields[0].type_,  # type: ignore
                link_type=LinkTypes.BACK_DIRECT,
            )
    else:
        if annotation_type.base_class == Link:
            if annotation_type.is_optional is True:
                return LinkInfo(
                    field_name=field_name,
                    lookup_field_name=field_name,
                    document_class=annotation_type.generic_type,  # type: ignore
                    link_type=LinkTypes.OPTIONAL_LIST,
                )
            return LinkInfo(
                field_name=field_name,
                lookup_field_name=field_name,
                document_class=annotation_type.generic_type,  # type: ignore
                link_type=LinkTypes.LIST,
            )
        if annotation_type.base_class == BackLink:
            if annotation_type.is_optional is True:
                return LinkInfo(
                    field_name=field_name,
                    lookup_field_name=field.json_schema_extra["original_field"],
                    document_class=annotation_type.generic_type,  # type: ignore
                    link_type=LinkTypes.OPTIONAL_BACK_LIST,
                )
            return LinkInfo(
                field_name=field_name,
                lookup_field_name=field.json_schema_extra["original_field"],
                document_class=annotation_type.generic_type,  # type: ignore
                link_type=LinkTypes.BACK_LIST,
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
