import asyncio
import sys
from collections import OrderedDict
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

if sys.version_info >= (3, 8):
    from typing import get_args
else:
    from typing_extensions import get_args

from typing import OrderedDict as OrderedDictType

from bson import DBRef
from pydantic import BaseModel

from beanie.odm.operators.find.comparison import (
    In,
)
from beanie.odm.registry import DocsRegistry
from beanie.odm.utils.parsing import parse_obj
from beanie.odm.utils.pydantic import (
    IS_PYDANTIC_V2,
    get_field_type,
    get_model_fields,
    parse_object_as,
)

if IS_PYDANTIC_V2:
    from pydantic import (
        GetCoreSchemaHandler,
        TypeAdapter,
    )
    from pydantic_core import CoreSchema, core_schema
    from pydantic_core.core_schema import (
        ValidationInfo,
    )
else:
    from pydantic.fields import ModelField  # type: ignore
    from pydantic.json import ENCODERS_BY_TYPE

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


class DeleteRules(str, Enum):
    DO_NOTHING = "DO_NOTHING"
    DELETE_LINKS = "DELETE_LINKS"


class WriteRules(str, Enum):
    DO_NOTHING = "DO_NOTHING"
    WRITE = "WRITE"


class LinkTypes(str, Enum):
    DIRECT = "DIRECT"
    OPTIONAL_DIRECT = "OPTIONAL_DIRECT"
    LIST = "LIST"
    OPTIONAL_LIST = "OPTIONAL_LIST"

    BACK_DIRECT = "BACK_DIRECT"
    BACK_LIST = "BACK_LIST"
    OPTIONAL_BACK_DIRECT = "OPTIONAL_BACK_DIRECT"
    OPTIONAL_BACK_LIST = "OPTIONAL_BACK_LIST"


class LinkInfo(BaseModel):
    field_name: str
    lookup_field_name: str
    document_class: Type[BaseModel]  # Document class
    link_type: LinkTypes
    nested_links: Optional[Dict] = None


T = TypeVar("T")


class Link(Generic[T]):
    def __init__(self, ref: DBRef, document_class: Type[T]):
        self.ref = ref
        self.document_class = document_class

    async def fetch(self, fetch_links: bool = False) -> Union[T, "Link"]:
        result = await self.document_class.get(  # type: ignore
            self.ref.id, with_children=True, fetch_links=fetch_links
        )
        return result or self

    @classmethod
    async def fetch_one(cls, link: "Link"):
        return await link.fetch()

    @classmethod
    async def fetch_list(
        cls, links: List[Union["Link", "DocType"]], fetch_links: bool = False
    ):
        """
        Fetch list that contains links and documents
        :param links:
        :param fetch_links:
        :return:
        """
        data = Link.repack_links(links)  # type: ignore
        ids_to_fetch = []
        document_class = None
        for doc_id, link in data.items():
            if isinstance(link, Link):
                if document_class is None:
                    document_class = link.document_class
                else:
                    if document_class != link.document_class:
                        raise ValueError(
                            "All the links must have the same model class"
                        )
                ids_to_fetch.append(link.ref.id)

        if ids_to_fetch:
            fetched_models = await document_class.find(  # type: ignore
                In("_id", ids_to_fetch),
                with_children=True,
                fetch_links=fetch_links,
            ).to_list()

            for model in fetched_models:
                data[model.id] = model

        return list(data.values())

    @staticmethod
    def repack_links(
        links: List[Union["Link", "DocType"]]
    ) -> OrderedDictType[Any, Any]:
        result = OrderedDict()
        for link in links:
            if isinstance(link, Link):
                result[link.ref.id] = link
            else:
                result[link.id] = link
        return result

    @classmethod
    async def fetch_many(cls, links: List["Link"]):
        coros = []
        for link in links:
            coros.append(link.fetch())
        return await asyncio.gather(*coros)

    if IS_PYDANTIC_V2:

        @staticmethod
        def serialize(value: Union["Link", BaseModel]):
            if isinstance(value, Link):
                return value.to_dict()
            return value.model_dump()

        @classmethod
        def build_validation(cls, handler, source_type):
            def validate(v: Union[DBRef, T], validation_info: ValidationInfo):
                document_class = DocsRegistry.evaluate_fr(get_args(source_type)[0])  # type: ignore  # noqa: F821

                if isinstance(v, DBRef):
                    return cls(ref=v, document_class=document_class)
                if isinstance(v, Link):
                    return v
                if isinstance(v, dict) and v.keys() == {"id", "collection"}:
                    return cls(
                        ref=DBRef(
                            collection=v["collection"],
                            id=TypeAdapter(
                                document_class.model_fields["id"].annotation
                            ).validate_python(v["id"]),
                        ),
                        document_class=document_class,
                    )
                if isinstance(v, dict) or isinstance(v, BaseModel):
                    return parse_obj(document_class, v)
                new_id = TypeAdapter(
                    document_class.model_fields["id"].annotation
                ).validate_python(v)
                ref = DBRef(
                    collection=document_class.get_collection_name(), id=new_id
                )
                return cls(ref=ref, document_class=document_class)

            return validate

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
        ) -> CoreSchema:  # type: ignore
            return core_schema.json_or_python_schema(
                python_schema=core_schema.general_plain_validator_function(
                    cls.build_validation(handler, source_type)
                ),
                json_schema=core_schema.typed_dict_schema(
                    {
                        "id": core_schema.typed_dict_field(
                            core_schema.str_schema()
                        ),
                        "collection": core_schema.typed_dict_field(
                            core_schema.str_schema()
                        ),
                    }
                ),
                serialization=core_schema.plain_serializer_function_ser_schema(  # type: ignore
                    lambda instance: cls.serialize(instance)  # type: ignore
                ),
            )
            return core_schema.general_plain_validator_function(
                cls.build_validation(handler, source_type)
            )

    else:

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v: Union[DBRef, T], field: ModelField):
            document_class = field.sub_fields[0].type_  # type: ignore
            if isinstance(v, DBRef):
                return cls(ref=v, document_class=document_class)
            if isinstance(v, Link):
                return v
            if isinstance(v, dict) or isinstance(v, BaseModel):
                return parse_obj(document_class, v)
            new_id = parse_object_as(
                get_field_type(get_model_fields(document_class)["id"]), v
            )
            ref = DBRef(
                collection=document_class.get_collection_name(), id=new_id
            )
            return cls(ref=ref, document_class=document_class)

    def to_ref(self):
        return self.ref

    def to_dict(self):
        return {"id": str(self.ref.id), "collection": self.ref.collection}


if not IS_PYDANTIC_V2:
    ENCODERS_BY_TYPE[Link] = lambda o: o.to_dict()


class BackLink(Generic[T]):
    """Back reference to a document"""

    def __init__(self, document_class: Type[T]):
        self.document_class = document_class

    if IS_PYDANTIC_V2:

        @classmethod
        def build_validation(cls, handler, source_type):
            def validate(v: Union[DBRef, T], field):
                document_class = DocsRegistry.evaluate_fr(get_args(source_type)[0])  # type: ignore  # noqa: F821
                if isinstance(v, dict) or isinstance(v, BaseModel):
                    return parse_obj(document_class, v)
                return cls(document_class=document_class)

            return validate

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
        ) -> CoreSchema:  # type: ignore
            return core_schema.general_plain_validator_function(
                cls.build_validation(handler, source_type)
            )

    else:

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v: Union[DBRef, T], field: ModelField):
            document_class = field.sub_fields[0].type_  # type: ignore
            if isinstance(v, dict) or isinstance(v, BaseModel):
                return parse_obj(document_class, v)
            return cls(document_class=document_class)

    def to_dict(self):
        return {"collection": self.document_class.get_collection_name()}


if not IS_PYDANTIC_V2:
    ENCODERS_BY_TYPE[BackLink] = lambda o: o.to_dict()
