from typing import List

import pymongo
from pydantic import BaseModel
from pymongo import IndexModel

from beanie import Document, Indexed


class SubDocument(BaseModel):
    test_str: str


class DocumentTestModel(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str


class DocumentTestModelWithCustomCollectionName(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "custom"


class DocumentTestModelWithSimpleIndex(Document):
    test_int: Indexed(int)
    test_list: List[SubDocument]
    test_str: Indexed(str, index_type=pymongo.TEXT)


class DocumentTestModelWithComplexIndex(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "docs_with_index"
        indexes = [
            "test_int",
            [
                ("test_int", pymongo.ASCENDING),
                ("test_str", pymongo.DESCENDING),
            ],
            IndexModel(
                [("test_str", pymongo.DESCENDING)],
                name="test_string_index_DESCENDING",
            ),
        ]


class DocumentTestModelWithDroppedIndex(Document):
    test_int: int
    test_list: List[SubDocument]
    test_str: str

    class Collection:
        name = "docs_with_index"
        indexes = [
            "test_int",
        ]


class DocumentTestModelStringImport(Document):
    test_int: int


class DocumentTestModelFailInspection(Document):
    test_int_2: int

    class Collection:
        name = "DocumentTestModel"
