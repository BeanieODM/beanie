from typing import ClassVar
from pydantic import BaseModel


class InheritanceInterface:
    children: ClassVar[dict[str, list[type['BaseModel']]]] = {}

    @classmethod
    def has_parent(cls):
        return cls.get_parent() is not cls

    @classmethod
    def is_part_of_inheritance(cls):
        return len(cls.get_children()) > 0 or cls.has_parent()

    @classmethod
    def get_parent(cls):
        """Returns the closest class to the Document, that name should be used as collection for all children"""
        ...

    @classmethod
    def get_children(cls):
        """Get a list of all child classes"""
        rv = []

        for c in cls.children.get(cls.__name__, []):
            rv.append(c)
            # build recursive flat list
            rv += c.get_children()

        return rv
