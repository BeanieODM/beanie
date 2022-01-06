import inspect
from typing import Optional

from pydantic.fields import ModelField
from pydantic.typing import get_origin

from beanie.odm.fields import LinkTypes, LinkInfo, Link


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
            if internal_field.allow_none is True:
                return None
            return LinkInfo(
                field=field.name,
                model_class=internal_field.sub_fields[0].type_,  # type: ignore
                link_type=LinkTypes.LIST,
            )
    return None
