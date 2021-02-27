from typing import List

from pydantic import BaseModel

from beanie import Document


class SubDocument(BaseModel):
    test_str: str


class DocumentTestModel(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str


class DocumentTestModelWithCustomCollection(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class DocumentMeta:
        collection_name = "custom"
