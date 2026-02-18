from typing import (
    ClassVar,
    Optional,
)

from typing_extensions import Self


class InheritanceInterface:
    _children: ClassVar[dict[str, type[Self]]]
    _parent: ClassVar[Optional[type[Self]]]
    _inheritance_inited: ClassVar[bool]
    _class_id: ClassVar[Optional[str]] = None

    @classmethod
    def add_child(cls, name: str, clas: type[Self]):
        cls._children[name] = clas
        if cls._parent is not None:
            cls._parent.add_child(name, clas)
