from beanie.odm.fields import LinkTypes
from typing import TYPE_CHECKING, List, Dict, Any, Type

if TYPE_CHECKING:
    from beanie import Document


def construct_lookup_queries(cls: Type["Document"]) -> List[Dict[str, Any]]:
    queries = []
    link_fields = cls.get_link_fields()
    if link_fields is not None:
        for link_info in link_fields.values():
            queries.append(
                {
                    "$lookup": {
                        "from": link_info.model_class.get_motor_collection().name,  # type: ignore
                        "localField": f"{link_info.field}.$id",
                        "foreignField": "_id",
                        "as": link_info.field,
                    }
                }
            )
            if link_info.link_type in [
                LinkTypes.DIRECT,
                LinkTypes.OPTIONAL_DIRECT,
            ]:
                queries.append(
                    {
                        "$unwind": {
                            "path": f"${link_info.field}",
                            "preserveNullAndEmptyArrays": True,
                        }
                    }
                )  # type: ignore
    return queries
