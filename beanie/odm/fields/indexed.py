from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

from pymongo import ASCENDING, IndexModel

from beanie.odm.utils.pydantic import (
    IS_PYDANTIC_V2,
)

if IS_PYDANTIC_V2:
    from pydantic import (
        GetCoreSchemaHandler,
    )
    from pydantic_core import CoreSchema, core_schema
    from pydantic_core.core_schema import (
        simple_ser_schema,
    )
else:
    pass  # type: ignore


@dataclass(frozen=True)
class IndexedAnnotation:
    _indexed: Tuple[int, Dict[str, Any]]


def Indexed(typ=None, index_type=ASCENDING, **kwargs):
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

        def __new__(cls, *args, **kwargs):
            return typ.__new__(typ, *args, **kwargs)

        if IS_PYDANTIC_V2:

            @classmethod
            def __get_pydantic_core_schema__(
                cls, _source_type: Any, _handler: GetCoreSchemaHandler
            ) -> core_schema.CoreSchema:
                custom_type = getattr(
                    typ, "__get_pydantic_core_schema__", None
                )
                if custom_type is not None:
                    return custom_type(_source_type, _handler)

                return core_schema.no_info_after_validator_function(
                    lambda v: v,
                    simple_ser_schema(typ.__name__),
                )

    NewType.__name__ = f"Indexed {typ.__name__}"
    return NewType


class IndexModelField:
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
        left: List["IndexModelField"], right: List["IndexModelField"]
    ):
        result = []
        for index in left:
            if index not in right:
                result.append(index)
        return result

    @staticmethod
    def list_to_index_model(left: List["IndexModelField"]):
        return [index.index for index in left]

    @classmethod
    def from_motor_index_information(cls, index_info: dict):
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
        indexes: List["IndexModelField"], index: "IndexModelField"
    ):
        for i in indexes:
            if i.same_fields(index):
                return i
        return None

    @staticmethod
    def merge_indexes(
        left: List["IndexModelField"], right: List["IndexModelField"]
    ):
        left_dict = {index.fields: index for index in left}
        right_dict = {index.fields: index for index in right}
        left_dict.update(right_dict)
        return list(left_dict.values())

    if IS_PYDANTIC_V2:

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
        ) -> CoreSchema:  # type: ignore
            def validate(v, _):
                if isinstance(v, IndexModel):
                    return IndexModelField(v)
                else:
                    return IndexModelField(IndexModel(v))

            return core_schema.general_plain_validator_function(validate)

    else:

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v):
            if isinstance(v, IndexModel):
                return IndexModelField(v)
            else:
                return IndexModelField(IndexModel(v))
