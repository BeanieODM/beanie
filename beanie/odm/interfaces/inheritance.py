from typing import (
    Type,
    Optional,
    TYPE_CHECKING,
    Dict,
    ClassVar,
)

from pydantic import BaseModel

if TYPE_CHECKING:
    pass


class Output(BaseModel):
    class_name: str
    collection_name: str


class InheritanceInterface:
    _children: ClassVar[Dict[str, Type]]
    _parent: ClassVar[Optional[Type]]
    _inheritance_inited: ClassVar[bool]
    _class_name: ClassVar[str]
