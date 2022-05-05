from beanie.exceptions import NotSupported
from beanie.odm.fields import LinkTypes
from typing import TYPE_CHECKING, List, Dict, Any, Type

from beanie.odm.interfaces.detector import ModelType

if TYPE_CHECKING:
    from beanie import Document


def construct_lookup_queries(cls: Type["Document"]) -> List[Dict[str, Any]]:
    if cls.get_model_type() == ModelType.UnionDoc:
        raise NotSupported("UnionDoc doesn't support link fetching")
    queries = []
    link_fields = cls.get_link_fields()
    if link_fields is not None:
        for link_info in link_fields.values():
            if link_info.link_type in [
                LinkTypes.DIRECT,
                LinkTypes.OPTIONAL_DIRECT,
            ]:
                queries += [
                    {
                        "$lookup": {
                            "from": link_info.model_class.get_motor_collection().name,  # type: ignore
                            "localField": f"{link_info.field}.$id",
                            "foreignField": "_id",
                            "as": f"_link_{link_info.field}",
                        }
                    },
                    {
                        "$unwind": {
                            "path": f"$_link_{link_info.field}",
                            "preserveNullAndEmptyArrays": True,
                        }
                    },
                    {
                        "$set": {
                            link_info.field: {
                                "$cond": {
                                    "if": {
                                        "$ifNull": [
                                            f"$_link_{link_info.field}",
                                            False,
                                        ]
                                    },
                                    "then": f"$_link_{link_info.field}",
                                    "else": f"${link_info.field}",
                                }
                            }
                        }
                    },
                ]  # type: ignore
            else:
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
    return queries
