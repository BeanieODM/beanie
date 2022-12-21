from typing import TYPE_CHECKING, Any, Dict, List, Type

from beanie.exceptions import NotSupported
from beanie.odm.fields import LinkInfo, LinkTypes
from beanie.odm.interfaces.detector import ModelType

if TYPE_CHECKING:
    from beanie import Document

# TODO: check if this is the most efficient way for
#  appending subqueries to the queries var


def construct_lookup_queries(cls: Type["Document"]) -> List[Dict[str, Any]]:
    if cls.get_model_type() == ModelType.UnionDoc:
        raise NotSupported("UnionDoc doesn't support link fetching")
    queries: List = []
    link_fields = cls.get_link_fields()
    if link_fields is not None:
        for link_info in link_fields.values():
            construct_query(
                link_info=link_info,
                queries=queries,
                database_major_version=cls._database_major_version,
            )
    return queries


def construct_query(
    link_info: LinkInfo,
    queries: List,
    database_major_version: int,
):
    if link_info.link_type in [
        LinkTypes.DIRECT,
        LinkTypes.OPTIONAL_DIRECT,
    ]:
        if database_major_version >= 5 or link_info.nested_links is None:
            lookup_steps = [
                {
                    "$lookup": {
                        "from": link_info.model_class.get_motor_collection().name,
                        # type: ignore
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
            if link_info.nested_links is not None:
                lookup_steps[0]["$lookup"]["pipeline"] = []
                for nested_link in link_info.nested_links:
                    construct_query(
                        link_info=link_info.nested_links[nested_link],
                        queries=lookup_steps[0]["$lookup"]["pipeline"],
                        database_major_version=database_major_version,
                    )
            queries += lookup_steps

        else:
            lookup_steps = [
                {
                    "$lookup": {
                        "from": link_info.model_class.get_motor_collection().name,
                        "let": {"link_id": f"${link_info.field}.$id"},
                        "as": f"_link_{link_info.field}",
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {"$eq": ["$_id", "$$link_id"]}
                                }
                            },
                        ],
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
            ]
            for nested_link in link_info.nested_links:
                construct_query(
                    link_info=link_info.nested_links[nested_link],
                    queries=lookup_steps[0]["$lookup"]["pipeline"],
                    database_major_version=database_major_version,
                )
            queries += lookup_steps

    else:
        if database_major_version >= 5 or link_info.nested_links is None:
            queries.append(
                {
                    "$lookup": {
                        "from": link_info.model_class.get_motor_collection().name,
                        # type: ignore
                        "localField": f"{link_info.field}.$id",
                        "foreignField": "_id",
                        "as": link_info.field,
                    }
                }
            )

            if link_info.nested_links is not None:
                queries[-1]["$lookup"]["pipeline"] = []
                for nested_link in link_info.nested_links:
                    construct_query(
                        link_info=link_info.nested_links[nested_link],
                        queries=queries[-1]["$lookup"]["pipeline"],
                        database_major_version=database_major_version,
                    )
        else:
            lookup_step = {
                "$lookup": {
                    "from": link_info.model_class.get_motor_collection().name,
                    "let": {"link_id": f"${link_info.field}.$id"},
                    "as": link_info.field,
                    "pipeline": [
                        {"$match": {"$expr": {"$in": ["$_id", "$$link_id"]}}},
                    ],
                }
            }

            for nested_link in link_info.nested_links:
                construct_query(
                    link_info=link_info.nested_links[nested_link],
                    queries=lookup_step["$lookup"]["pipeline"],
                    database_major_version=database_major_version,
                )
            queries.append(lookup_step)
    return queries
