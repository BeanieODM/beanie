from typing import TYPE_CHECKING, Any, Dict, List, Type

from beanie.odm.fields import LinkInfo, LinkTypes

if TYPE_CHECKING:
    from beanie import Document


# TODO: check if this is the most efficient way for
#  appending subqueries to the queries var


def construct_lookup_queries(cls: Type["Document"]) -> List[Dict[str, Any]]:
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
                        "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                        "localField": f"{link_info.lookup_field_name}.$id",
                        "foreignField": "_id",
                        "as": f"_link_{link_info.field_name}",
                    }
                },
                {
                    "$unwind": {
                        "path": f"$_link_{link_info.field_name}",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
                {
                    "$set": {
                        link_info.field_name: {
                            "$cond": {
                                "if": {
                                    "$ifNull": [
                                        f"$_link_{link_info.field_name}",
                                        False,
                                    ]
                                },
                                "then": f"$_link_{link_info.field_name}",
                                "else": f"${link_info.field_name}",
                            }
                        }
                    }
                },
                {"$unset": f"_link_{link_info.field_name}"},
            ]  # type: ignore
            if link_info.nested_links is not None:
                lookup_steps[0]["$lookup"]["pipeline"] = []  # type: ignore
                for nested_link in link_info.nested_links:
                    construct_query(
                        link_info=link_info.nested_links[nested_link],
                        queries=lookup_steps[0]["$lookup"]["pipeline"],  # type: ignore
                        database_major_version=database_major_version,
                    )
            queries += lookup_steps

        else:
            lookup_steps = [
                {
                    "$lookup": {
                        "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                        "let": {
                            "link_id": f"${link_info.lookup_field_name}.$id"
                        },
                        "as": f"_link_{link_info.field_name}",
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
                        "path": f"$_link_{link_info.field_name}",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
                {
                    "$set": {
                        link_info.field_name: {
                            "$cond": {
                                "if": {
                                    "$ifNull": [
                                        f"$_link_{link_info.field_name}",
                                        False,
                                    ]
                                },
                                "then": f"$_link_{link_info.field_name}",
                                "else": f"${link_info.field_name}",
                            }
                        }
                    }
                },
                {"$unset": f"_link_{link_info.field_name}"},
            ]
            for nested_link in link_info.nested_links:
                construct_query(
                    link_info=link_info.nested_links[nested_link],
                    queries=lookup_steps[0]["$lookup"]["pipeline"],  # type: ignore
                    database_major_version=database_major_version,
                )
            queries += lookup_steps

    elif link_info.link_type in [
        LinkTypes.BACK_DIRECT,
        LinkTypes.OPTIONAL_BACK_DIRECT,
    ]:
        if database_major_version >= 5 or link_info.nested_links is None:
            lookup_steps = [
                {
                    "$lookup": {
                        "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                        "localField": "_id",
                        "foreignField": f"{link_info.lookup_field_name}.$id",
                        "as": f"_link_{link_info.field_name}",
                    }
                },
                {
                    "$unwind": {
                        "path": f"$_link_{link_info.field_name}",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
                {
                    "$set": {
                        link_info.field_name: {
                            "$cond": {
                                "if": {
                                    "$ifNull": [
                                        f"$_link_{link_info.field_name}",
                                        False,
                                    ]
                                },
                                "then": f"$_link_{link_info.field_name}",
                                "else": f"${link_info.field_name}",
                            }
                        }
                    }
                },
                {"$unset": f"_link_{link_info.field_name}"},
            ]  # type: ignore
            if link_info.nested_links is not None:
                lookup_steps[0]["$lookup"]["pipeline"] = []  # type: ignore
                for nested_link in link_info.nested_links:
                    construct_query(
                        link_info=link_info.nested_links[nested_link],
                        queries=lookup_steps[0]["$lookup"]["pipeline"],  # type: ignore
                        database_major_version=database_major_version,
                    )
            queries += lookup_steps

        else:
            lookup_steps = [
                {
                    "$lookup": {
                        "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                        "let": {"link_id": "$_id"},
                        "as": f"_link_{link_info.field_name}",
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": [
                                            f"${link_info.lookup_field_name}.$id",
                                            "$$link_id",
                                        ]
                                    }
                                }
                            },
                        ],
                    }
                },
                {
                    "$unwind": {
                        "path": f"$_link_{link_info.field_name}",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
                {
                    "$set": {
                        link_info.field_name: {
                            "$cond": {
                                "if": {
                                    "$ifNull": [
                                        f"$_link_{link_info.field_name}",
                                        False,
                                    ]
                                },
                                "then": f"$_link_{link_info.field_name}",
                                "else": f"${link_info.field_name}",
                            }
                        }
                    }
                },
                {"$unset": f"_link_{link_info.field_name}"},
            ]
            for nested_link in link_info.nested_links:
                construct_query(
                    link_info=link_info.nested_links[nested_link],
                    queries=lookup_steps[0]["$lookup"]["pipeline"],  # type: ignore
                    database_major_version=database_major_version,
                )
            queries += lookup_steps

    elif link_info.link_type in [
        LinkTypes.LIST,
        LinkTypes.OPTIONAL_LIST,
    ]:
        if database_major_version >= 5 or link_info.nested_links is None:
            queries.append(
                {
                    "$lookup": {
                        "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                        "localField": f"{link_info.lookup_field_name}.$id",
                        "foreignField": "_id",
                        "as": link_info.field_name,
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
                    "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                    "let": {"link_id": f"${link_info.lookup_field_name}.$id"},
                    "as": link_info.field_name,
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

    elif link_info.link_type in [
        LinkTypes.BACK_LIST,
        LinkTypes.OPTIONAL_BACK_LIST,
    ]:
        if database_major_version >= 5 or link_info.nested_links is None:
            queries.append(
                {
                    "$lookup": {
                        "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                        "localField": "_id",
                        "foreignField": f"{link_info.lookup_field_name}.$id",
                        "as": link_info.field_name,
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
                    "from": link_info.document_class.get_motor_collection().name,  # type: ignore
                    "let": {"link_id": "$_id"},
                    "as": link_info.field_name,
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$in": [
                                        "$$link_id",
                                        f"${link_info.lookup_field_name}.$id",
                                    ]
                                }
                            }
                        }
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
