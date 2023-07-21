from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from beanie.odm.fields.pydantic_v2 import (
        Indexed,
        PydanticObjectId,
        Link,
        BackLink,
        ExpressionField,
        DeleteRules,
        WriteRules,
        LinkInfo,
        LinkTypes,
        IndexModelField,
    )
else:
    from beanie.odm.fields.pydantic_v1 import (  # type: ignore
        Indexed,  # type: ignore
        PydanticObjectId,  # type: ignore
        Link,  # type: ignore
        BackLink,  # type: ignore
        ExpressionField,  # type: ignore
        DeleteRules,  # type: ignore
        WriteRules,  # type: ignore
        LinkInfo,  # type: ignore
        LinkTypes,  # type: ignore
        IndexModelField,  # type: ignore
    )


__all__ = [
    "Indexed",
    "PydanticObjectId",
    "Link",
    "BackLink",
    "ExpressionField",
    "DeleteRules",
    "WriteRules",
    "LinkInfo",
    "LinkTypes",
    "IndexModelField",
]
