from typing import List
from unittest.mock import MagicMock

from pydantic import BaseModel

from beanie import Link, Document
from beanie.odm.utils.parsing import merge_models


class StringPropertyModel(BaseModel):
    string_property: str = ""


class IntPropertyModel(BaseModel):
    int_property: int = 0


class FloatPropertyModel(BaseModel):
    float_property: float = 0.0


class ListPropertyModel(BaseModel):
    list_property: list = []


class NestedModel(BaseModel):
    str_model: StringPropertyModel = StringPropertyModel()
    int_model: IntPropertyModel = IntPropertyModel()
    float_model: FloatPropertyModel = FloatPropertyModel()
    list_model: ListPropertyModel = ListPropertyModel()


class ListOfBaseModel(BaseModel):
    model_list: List[StringPropertyModel] = []


class MyDocument(Document, BaseModel):
    sample: int = 1


class ListOfLinkModel(BaseModel):
    model_list: List[Link["MyDocument"]] = []


def test_should_update_string_property():
    left = StringPropertyModel()
    right = StringPropertyModel(string_property="test")
    merge_models(left, right)
    assert left.string_property == "test"


def test_should_update_int_property():
    left = IntPropertyModel()
    right = IntPropertyModel(int_property=1)
    merge_models(left, right)
    assert left.int_property == 1


def test_should_update_float_property():
    left = FloatPropertyModel()
    right = FloatPropertyModel(float_property=1.0)
    merge_models(left, right)
    assert left.float_property == 1.0


def test_should_update_list_property():
    left = ListPropertyModel()
    right = ListPropertyModel(list_property=[1, 2, 3])
    merge_models(left, right)
    assert left.list_property == [1, 2, 3]


def test_should_update_nested_model():
    left = NestedModel()
    right = NestedModel(
        str_model=StringPropertyModel(string_property="test"),
        int_model=IntPropertyModel(int_property=1),
        float_model=FloatPropertyModel(float_property=1.0),
        list_model=ListPropertyModel(list_property=[1, 2, 3]),
    )
    merge_models(left, right)
    assert left.str_model.string_property == "test"
    assert left.int_model.int_property == 1
    assert left.float_model.float_property == 1.0
    assert left.list_model.list_property == [1, 2, 3]


def test_should_update_list_of_base_model():
    left = ListOfBaseModel()
    right = ListOfBaseModel(
        model_list=[
            StringPropertyModel(string_property="test"),
            StringPropertyModel(string_property="test2"),
        ]
    )
    merge_models(left, right)
    assert left.model_list[0].string_property == "test"
    assert left.model_list[1].string_property == "test2"


def test_should_not_update_list_of_link_model():
    left = ListOfLinkModel()
    right = ListOfLinkModel(model_list=[MagicMock(spec=Link)])
    merge_models(left, right)
    assert len(left.model_list) == 0
