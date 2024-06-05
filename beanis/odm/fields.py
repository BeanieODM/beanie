import asyncio
import sys
from collections import OrderedDict
from dataclasses import dataclass
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
from typing import Tuple

from pydantic import BaseModel

from beanis.odm.operators.find.comparison import (
    GT,
    GTE,
    LT,
    LTE,
    NE,
    Eq,
    In,
)
from beanis.odm.registry import DocsRegistry
from beanis.odm.utils.parsing import parse_obj
from beanis.odm.utils.pydantic import (
    IS_PYDANTIC_V2,
    get_field_type,
    get_model_fields,
    parse_object_as,
)

if IS_PYDANTIC_V2:
    from pydantic import (
        GetCoreSchemaHandler,
        GetJsonSchemaHandler,
        TypeAdapter,
    )
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import CoreSchema, core_schema
    from pydantic_core.core_schema import (
        ValidationInfo,
        simple_ser_schema,
        str_schema,
    )
else:
    from pydantic.fields import ModelField  # type: ignore
    from pydantic.json import ENCODERS_BY_TYPE

if TYPE_CHECKING:
    from beanis.odm.documents import DocType


@dataclass(frozen=True)
class IndexedAnnotation:
    _indexed: Tuple[int, Dict[str, Any]]


class ExpressionField(str):
    def __getitem__(self, item):
        """
        Get sub field

        :param item: name of the subfield
        :return: ExpressionField
        """
        return ExpressionField(f"{self}.{item}")

    def __getattr__(self, item):
        """
        Get sub field

        :param item: name of the subfield
        :return: ExpressionField
        """
        return ExpressionField(f"{self}.{item}")

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, ExpressionField):
            return super(ExpressionField, self).__eq__(other)
        return Eq(field=self, other=other)

    def __gt__(self, other):
        return GT(field=self, other=other)

    def __ge__(self, other):
        return GTE(field=self, other=other)

    def __lt__(self, other):
        return LT(field=self, other=other)

    def __le__(self, other):
        return LTE(field=self, other=other)

    def __ne__(self, other):
        return NE(field=self, other=other)

    def __pos__(self):
        return self, 1

    def __neg__(self):
        return self, 1

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


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
    is_fetchable: bool = True


T = TypeVar("T")
