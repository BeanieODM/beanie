import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    get_args,
)

from bson import DBRef, ObjectId
from bson.errors import InvalidId
from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    TypeAdapter,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from pydantic_core.core_schema import CoreSchema, ValidationInfo
from pymongo import ASCENDING, IndexModel

from beanie.odm.enums import SortDirection
from beanie.odm.operators.find.comparison import (
    GT,
    GTE,
    LT,
    LTE,
    NE,
    Eq,
    In,
)
from beanie.odm.registry import DocsRegistry
from beanie.odm.utils.parsing import parse_obj
from beanie.odm.utils.pydantic import get_model_fields

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


@dataclass(frozen=True)
class IndexedAnnotation:
    _indexed: tuple[int, dict[str, Any]]


def Indexed(typ=None, index_type=ASCENDING, **kwargs: Any):
    """
    If `typ` is defined, returns a subclass of `typ` with an extra attribute
    `_indexed` as a tuple:
    - Index 0: `index_type` such as `pymongo.ASCENDING`
    - Index 1: `kwargs` passed to `IndexModel`
    When instantiated the type of the result will actually be `typ`.

    When `typ` is not defined, returns an `IndexedAnnotation` instance, to be
    used as metadata in `Annotated` fields.

    Example:
    ```py
    # Both fields would have the same behavior
    class MyModel(BaseModel):
        field1: Indexed(str, unique=True)
        field2: Annotated[str, Indexed(unique=True)]
    ```
    """
    if typ is None:
        return IndexedAnnotation(_indexed=(index_type, kwargs))

    class NewType(typ):
        _indexed = (index_type, kwargs)

        def __new__(cls, *args: Any, **kwargs: Any):
            return typ.__new__(typ, *args, **kwargs)

        @classmethod
        def __get_pydantic_core_schema__(
            cls, _source_type: type[Any], _handler: GetCoreSchemaHandler
        ) -> CoreSchema:
            custom_type = getattr(typ, "__get_pydantic_core_schema__", None)
            if custom_type is not None:
                return custom_type(_source_type, _handler)

            return core_schema.no_info_after_validator_function(
                lambda v: v, core_schema.simple_ser_schema(typ.__name__)
            )

    NewType.__name__ = f"Indexed {typ.__name__}"
    return NewType


class PydanticObjectId(ObjectId):
    """
    Object Id field. Compatible with Pydantic.
    """

    @classmethod
    def _validate(cls, v):
        if isinstance(v, bytes):
            v = v.decode("utf-8")
        try:
            return PydanticObjectId(v)
        except (InvalidId, TypeError):
            raise ValueError("Id must be of type PydanticObjectId")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        definition = core_schema.definition_reference_schema(
            "PydanticObjectId"
        )  # used for deduplication

        return core_schema.definitions_schema(
            definition,
            [
                core_schema.json_or_python_schema(
                    python_schema=core_schema.no_info_plain_validator_function(
                        cls._validate
                    ),
                    json_schema=core_schema.no_info_after_validator_function(
                        cls._validate,
                        core_schema.str_schema(
                            pattern="^[0-9a-f]{24}$",
                            min_length=24,
                            max_length=24,
                        ),
                    ),
                    serialization=core_schema.plain_serializer_function_ser_schema(
                        lambda instance: str(instance), when_used="json"
                    ),
                    ref=definition["schema_ref"],
                )
            ],
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,  # type: ignore
    ) -> JsonSchemaValue:
        """
        Results such schema:
        ```json
        {
            "components": {
                "schemas": {
                    "Item": {
                        "properties": {
                            "id": {
                                "$ref": "#/components/schemas/PydanticObjectId"
                            }
                        },
                        "type": "object",
                        "title": "Item"
                    },
                    "PydanticObjectId": {
                        "type": "string",
                        "maxLength": 24,
                        "minLength": 24,
                        "pattern": "^[0-9a-f]{24}$",
                        "example": "5eb7cf5a86d9755df3a6c593"
                    }
                }
            }
        }
        ```
        """

        json_schema = handler(schema)
        schema_to_update = handler.resolve_ref_schema(json_schema)
        schema_to_update.update(example="5eb7cf5a86d9755df3a6c593")
        return json_schema


BeanieObjectId = PydanticObjectId


@dataclass(frozen=True)
class FieldResolution:
    """Immutable metadata attached to ExpressionField for query-time
    path resolution.

    Tracks the nested model class (for alias resolution during field
    access) and whether the path crosses a Link/BackLink boundary
    (for DBRef translation at query time).
    """

    model_class: type | None = None
    is_link: bool = False


class ExpressionField(str):
    """A string subclass used to build type-safe MongoDB query expressions.

    Instances are created automatically when you access a field on a
    :class:`~beanie.Document` class (e.g. ``Product.price``).  Attribute
    access chains are translated into dot-notation paths (e.g.
    ``Product.category.name`` → ``"category.name"``), and Pydantic field
    aliases are resolved automatically.

    Comparison operators (``==``, ``>``, ``>=``, ``<``, ``<=``, ``!=``)
    return the appropriate :mod:`beanie.odm.operators.find` objects so
    they can be passed directly to ``find()`` / ``find_one()``.

    Unary ``+`` / ``-`` return ``(field, SortDirection)`` tuples accepted
    by ``sort()``.

    Example::

        # Field access
        Product.category.name        # ExpressionField("category.name")

        # Query operators
        Product.find(Product.price > 10)
        Product.find(Product.name == "Chocolate")

        # Sorting
        Product.find().sort(+Product.price)
        Product.find().sort(-Product.price)
    """

    def __new__(cls, path, field_resolution=None):
        instance = super().__new__(cls, path)
        instance._field_resolution = (
            field_resolution
            if field_resolution is not None
            else FieldResolution()
        )
        return instance

    @staticmethod
    def _resolve_field(annotation) -> FieldResolution:
        """Resolve a field annotation to a :class:`FieldResolution`.

        Unwraps ``Optional[X]``, ``Union[X, ...]``, ``List[X]`` and
        similar generic wrappers to find the nested ``BaseModel``
        subclass.  ``Link[X]`` and ``BackLink[X]`` are resolved to
        the linked model **and** flagged with ``is_link=True`` so that
        the query layer can perform DBRef path translation at runtime.
        """
        if annotation is None:
            return FieldResolution()

        # Direct BaseModel subclass (embedded document)
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return FieldResolution(model_class=annotation)

        origin = getattr(annotation, "__origin__", None)
        args = getattr(annotation, "__args__", None)

        # Link[X] / BackLink[X] — resolve to X but mark as link
        if origin is not None and (
            origin is Link
            or origin is BackLink
            or (
                isinstance(origin, type)
                and issubclass(origin, (Link, BackLink))
            )
        ):
            if args:
                for arg in args:
                    if arg is type(None):
                        continue
                    if isinstance(arg, type) and issubclass(arg, BaseModel):
                        return FieldResolution(model_class=arg, is_link=True)
                    nested = ExpressionField._resolve_field(arg)
                    if nested.model_class is not None:
                        return FieldResolution(
                            model_class=nested.model_class, is_link=True
                        )
            return FieldResolution(is_link=True)

        # Other generics: Optional, Union, List, etc.
        if args:
            for arg in args:
                if arg is type(None):
                    continue
                if isinstance(arg, type) and issubclass(arg, BaseModel):
                    return FieldResolution(model_class=arg)
                nested = ExpressionField._resolve_field(arg)
                if nested.model_class is not None:
                    return nested

        return FieldResolution()

    def __getitem__(self, item):
        """
        Get sub field

        :param item: name of the subfield
        :return: ExpressionField
        """
        return ExpressionField(
            f"{self}.{item}",
            field_resolution=FieldResolution(
                is_link=self._field_resolution.is_link
            ),
        )

    def __getattr__(self, item):
        """Get sub field, resolving aliases from nested Pydantic models.

        Alias resolution is performed through the model class carried
        in ``_field_resolution``.  The ``is_link`` flag is propagated
        from parent to child so that downstream query code can
        translate DBRef paths at runtime.
        """
        if item.startswith("_"):
            raise AttributeError(item)

        resolution = self._field_resolution
        if resolution.model_class is not None:
            fields = get_model_fields(resolution.model_class)
            if item in fields:
                field_info = fields[item]
                alias = field_info.alias if field_info.alias else item
                annotation = getattr(field_info, "annotation", None)
                child = ExpressionField._resolve_field(annotation)
                # Propagate is_link from parent when child is not
                # itself a new link boundary.
                if resolution.is_link and not child.is_link:
                    child = FieldResolution(
                        model_class=child.model_class, is_link=True
                    )
                return ExpressionField(
                    f"{self}.{alias}", field_resolution=child
                )

        return ExpressionField(
            f"{self}.{item}",
            field_resolution=FieldResolution(is_link=resolution.is_link),
        )

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        """Return an equality filter expression, or delegate to str.__eq__ when comparing two ExpressionFields."""
        if isinstance(other, ExpressionField):
            return super().__eq__(other)
        return Eq(field=self, other=other)

    def __gt__(self, other):
        """Return a greater-than filter expression."""
        return GT(field=self, other=other)

    def __ge__(self, other):
        """Return a greater-than-or-equal filter expression."""
        return GTE(field=self, other=other)

    def __lt__(self, other):
        """Return a less-than filter expression."""
        return LT(field=self, other=other)

    def __le__(self, other):
        """Return a less-than-or-equal filter expression."""
        return LTE(field=self, other=other)

    def __ne__(self, other):
        """Return a not-equal filter expression."""
        return NE(field=self, other=other)

    def __pos__(self):
        """Return an ascending sort tuple ``(field, SortDirection.ASCENDING)``."""
        return self, SortDirection.ASCENDING

    def __neg__(self):
        """Return a descending sort tuple ``(field, SortDirection.DESCENDING)``."""
        return self, SortDirection.DESCENDING

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


class DeleteRules(str, Enum):
    """Controls what happens to linked documents when the parent is deleted.

    Pass as the ``link_rule`` argument to :meth:`~beanie.Document.delete`.

    - ``DO_NOTHING`` *(default)* — linked documents are left untouched.
    - ``DELETE_LINKS`` — each linked document is also deleted recursively.

    Example::

        await article.delete(link_rule=DeleteRules.DELETE_LINKS)
    """

    DO_NOTHING = "DO_NOTHING"
    DELETE_LINKS = "DELETE_LINKS"


class WriteRules(str, Enum):
    """Controls whether linked documents are persisted when the parent is saved.

    Pass as the ``link_rule`` argument to
    :meth:`~beanie.Document.insert`, :meth:`~beanie.Document.save`,
    :meth:`~beanie.Document.replace`, etc.

    - ``DO_NOTHING`` *(default)* — linked documents are **not** written;
      only the DBRef is stored on the parent.
    - ``WRITE`` — each linked document is upserted to the database before
      the parent is written.

    Example::

        await article.insert(link_rule=WriteRules.WRITE)
    """

    DO_NOTHING = "DO_NOTHING"
    WRITE = "WRITE"


class LinkTypes(str, Enum):
    """Internal classification of relation field variants.

    Used by Beanie's initialisation logic to determine how a
    :class:`Link` or :class:`BackLink` field should be fetched and
    serialised.  You will not normally need to reference these values
    directly — they are set automatically when a document class is
    initialised.
    """

    DIRECT = "DIRECT"
    OPTIONAL_DIRECT = "OPTIONAL_DIRECT"
    LIST = "LIST"
    OPTIONAL_LIST = "OPTIONAL_LIST"

    BACK_DIRECT = "BACK_DIRECT"
    BACK_LIST = "BACK_LIST"
    OPTIONAL_BACK_DIRECT = "OPTIONAL_BACK_DIRECT"
    OPTIONAL_BACK_LIST = "OPTIONAL_BACK_LIST"


class LinkInfo(BaseModel):
    """Runtime metadata describing a relation field on a document class.

    Populated automatically by Beanie's initialisation step and stored
    on ``Document._link_fields``.  Used internally to resolve fetch
    queries and to apply :class:`WriteRules` / :class:`DeleteRules`.
    """

    field_name: str
    lookup_field_name: str
    document_class: type[BaseModel]  # Document class
    link_type: LinkTypes
    nested_links: dict | None = None
    is_fetchable: bool = True


T = TypeVar("T")


class Link(Generic[T]):
    """A lazy reference to another :class:`~beanie.Document`.

    Stored in MongoDB as a ``DBRef`` (``{"$ref": ..., "$id": ...}``).
    The referenced document is **not** loaded from the database until
    :meth:`fetch` (or a higher-level helper such as
    :meth:`~beanie.Document.fetch_link`) is awaited.

    Declare a relation field using ``Link[T]`` as the type annotation::

        class Article(Document):
            author: Link[Author]
            # Optional relation
            editor: Link[Author] | None = None
            # List of relations
            tags: list[Link[Tag]] = []

    Insert behaviour is controlled by :class:`WriteRules` and delete
    behaviour by :class:`DeleteRules`.

    To resolve the reference, either:

    - ``await article.fetch_link(Article.author)`` — fetches one field
    - ``await article.fetch_all_links()`` — fetches all link fields
    - Pass ``fetch_links=True`` to ``find()`` / ``find_one()`` / ``get()``
    """

    def __init__(self, ref: DBRef, document_class: type[T]):
        self.ref = ref
        self.document_class = document_class

    async def fetch(self, fetch_links: bool = False) -> "T | Link[T]":
        """Fetch the referenced document from the database.

        :param fetch_links: If ``True``, also resolve link fields on the
            fetched document.
        :return: The resolved document, or ``self`` if not found.
        """
        result = await self.document_class.get(  # type: ignore
            self.ref.id, with_children=True, fetch_links=fetch_links
        )
        return result or self

    @classmethod
    async def fetch_one(cls, link: "Link[T]"):
        """Fetch a single link. Convenience wrapper around :meth:`fetch`."""
        return await link.fetch()

    @classmethod
    async def fetch_list(
        cls,
        links: list["Link[T] | DocType"],
        fetch_links: bool = False,
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
        for _doc_id, link in data.items():
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
        links: list["Link[T] | DocType"],
    ) -> OrderedDict[Any, Any]:
        """Convert a mixed list of Link objects and resolved documents into an
        OrderedDict keyed by document id, preserving insertion order."""
        result = OrderedDict()
        for link in links:
            if isinstance(link, Link):
                result[link.ref.id] = link
            else:
                result[link.id] = link
        return result

    @classmethod
    async def fetch_many(cls, links: list["Link[T]"]) -> list["T | Link[T]"]:
        """Fetch multiple links concurrently using ``asyncio.gather``.

        Unlike :meth:`fetch_list`, this method issues one database
        round-trip per link rather than a single batched query.
        """
        coros = []
        for link in links:
            coros.append(link.fetch())
        return await asyncio.gather(*coros)

    @staticmethod
    def serialize(value: "Link[T] | BaseModel"):
        if isinstance(value, Link):
            return value.to_dict()
        return value.model_dump(mode="json")

    @classmethod
    def wrapped_validate(
        cls, source_type: type[Any], handler: GetCoreSchemaHandler
    ):
        def validate(
            v: "Link[T] | T | DBRef | dict[str, Any]",
            validation_info: ValidationInfo,
        ) -> "Link[T] | T":
            document_class = DocsRegistry.evaluate_fr(  # type: ignore
                get_args(source_type)[0]
            )

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
            if isinstance(v, (dict, BaseModel)):
                return parse_obj(document_class, v)

            # Default fallback case for unknown type
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
        cls, source_type: type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(
                cls.wrapped_validate(source_type, handler)
            ),
            json_schema=core_schema.union_schema(
                [
                    core_schema.typed_dict_schema(
                        {
                            "id": core_schema.typed_dict_field(
                                core_schema.str_schema()
                            ),
                            "collection": core_schema.typed_dict_field(
                                core_schema.str_schema()
                            ),
                        }
                    ),
                    core_schema.dict_schema(
                        keys_schema=core_schema.str_schema(),
                        values_schema=core_schema.any_schema(),
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                function=lambda instance: cls.serialize(instance),
                when_used="json-unless-none",
            ),
        )

    def to_ref(self):
        """Return the underlying :class:`~bson.DBRef` for this link."""
        return self.ref

    def to_dict(self):
        """Serialise the link as ``{"id": str, "collection": str}``."""
        return {"id": str(self.ref.id), "collection": self.ref.collection}


class BackLink(Generic[T]):
    """A virtual back-reference from a child document to its parent.

    ``BackLink`` fields are **not** stored in MongoDB — they are resolved
    at query time by searching the referenced collection for documents
    whose :class:`Link` field points back to the current document.

    Declare a back-reference using ``BackLink[T]`` as the type
    annotation and set the ``original_field`` extra to the name of the
    forward-``Link`` field on the related model::

        from beanie import Document, Link, BackLink
        from pydantic import Field

        class Author(Document):
            name: str
            # Each Author can see all Articles that reference it
            articles: list[BackLink["Article"]] = Field(
                original_field="author", default=[]
            )

        class Article(Document):
            title: str
            author: Link[Author]

    Back-references are resolved lazily.  Call
    :meth:`~beanie.Document.fetch_link` or
    :meth:`~beanie.Document.fetch_all_links` to populate them, or pass
    ``fetch_links=True`` to ``find()`` / ``find_one()``.
    """

    def __init__(self, document_class: type[T]):
        self.document_class = document_class

    @classmethod
    def wrapped_validate(
        cls, source_type: type[Any], handler: GetCoreSchemaHandler
    ):
        def validate(
            v: T | dict[str, Any], validation_info: ValidationInfo
        ) -> "BackLink[T] | T":
            document_class = DocsRegistry.evaluate_fr(  # type: ignore
                get_args(source_type)[0]
            )
            if isinstance(v, (dict, BaseModel)):
                return parse_obj(document_class, v)
            return cls(document_class=document_class)

        return validate

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # NOTE: BackLinks are only virtual fields, they shouldn't be serialized nor appear in the schema.
        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(
                cls.wrapped_validate(source_type, handler)
            ),
            json_schema=core_schema.dict_schema(
                keys_schema=core_schema.str_schema(),
                values_schema=core_schema.any_schema(),
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: cls.to_dict(instance),
                return_schema=core_schema.dict_schema(),
                when_used="json-unless-none",
            ),
        )

    def to_dict(self) -> dict[str, str]:
        document_class = DocsRegistry.evaluate_fr(
            getattr(self, "document_class", self.__class__)
        )
        return {"collection": document_class.get_collection_name()}


class IndexModelField:
    """Wrapper around :class:`~pymongo.IndexModel` used internally by Beanie.

    Provides equality comparison (by field key + options) and utility
    helpers for diffing and merging index lists during collection
    initialisation.  Not part of the public API — use
    :func:`Indexed` or ``Document.Settings.indexes`` to declare indexes.
    """

    def __init__(self, index: IndexModel):
        self.index = index
        self.name = index.document["name"]

        self.fields = tuple(sorted(self.index.document["key"]))
        self.options = tuple(
            sorted(
                (k, v)
                for k, v in self.index.document.items()
                if k not in ["key", "v"]
            )
        )

    def __eq__(self, other):
        return self.fields == other.fields and self.options == other.options

    def __repr__(self):
        return f"IndexModelField({self.name}, {self.fields}, {self.options})"

    @staticmethod
    def list_difference(
        left: list["IndexModelField"], right: list["IndexModelField"]
    ):
        result = []
        for index in left:
            if index not in right:
                result.append(index)
        return result

    @staticmethod
    def list_to_index_model(left: list["IndexModelField"]):
        return [index.index for index in left]

    @classmethod
    def from_pymongo_index_information(cls, index_info: dict):
        result = []
        for name, details in index_info.items():
            fields = details["key"]
            if ("_id", 1) in fields:
                continue

            options = {k: v for k, v in details.items() if k != "key"}
            index_model = IndexModelField(
                IndexModel(fields, name=name, **options)
            )
            result.append(index_model)
        return result

    def same_fields(self, other: "IndexModelField"):
        return self.fields == other.fields

    @staticmethod
    def find_index_with_the_same_fields(
        indexes: list["IndexModelField"], index: "IndexModelField"
    ):
        for i in indexes:
            if i.same_fields(index):
                return i
        return None

    @staticmethod
    def merge_indexes(
        left: list["IndexModelField"], right: list["IndexModelField"]
    ):
        left_dict = {index.fields: index for index in left}
        right_dict = {index.fields: index for index in right}
        left_dict.update(right_dict)
        return list(left_dict.values())

    @classmethod
    def _validate(cls, v: Any) -> "IndexModelField":
        if isinstance(v, IndexModel):
            return IndexModelField(v)
        else:
            return IndexModelField(IndexModel(v))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(cls._validate)
