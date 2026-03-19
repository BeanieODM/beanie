from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from beanie.odm.documents import Document


class InheritanceInterface:
    _children: ClassVar[dict[str, type["Document"]]]
    _parent: ClassVar["Document | None"]
    _inheritance_inited: ClassVar[bool]
    _class_id: ClassVar[str | None] = None

    @classmethod
    def add_child(cls, name: str, clas: type["Document"]) -> None:
        cls._children[name] = clas
        if cls._parent is not None:
            cls._parent.add_child(name, clas)
