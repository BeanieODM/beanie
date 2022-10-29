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
    _class_id: ClassVar[str]

    @classmethod
    def add_child(cls, name: str, clas: Type):
        cls._children[name] = clas
        if cls._parent is not None:
            cls._parent.add_child(name, clas)
