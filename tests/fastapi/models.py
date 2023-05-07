from typing import List

from beanie import Document, Link, Indexed


class WindowAPI(Document):
    x: int
    y: int


class DoorAPI(Document):
    t: int = 10


class RoofAPI(Document):
    r: int = 100


class HouseAPI(Document):
    windows: List[Link[WindowAPI]]
    name: Indexed(str)
    height: Indexed(int) = 2
