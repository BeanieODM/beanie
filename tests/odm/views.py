from beanie.odm.fields import Link
from beanie.odm.views import View
from tests.odm.models import DocumentTestModel, DocumentTestModelWithLink


class TestView(View):
    number: int
    string: str

    class Settings:
        view_name = "test_view"
        source = DocumentTestModel
        pipeline = [
            {"$match": {"$expr": {"$gt": ["$test_int", 8]}}},
            {"$project": {"number": "$test_int", "string": "$test_str"}},
        ]


class TestViewWithLink(View):
    link: Link[DocumentTestModel]

    class Settings:
        view_name = "test_view_with_link"
        source = DocumentTestModelWithLink
        pipeline = [{"$set": {"link": "$test_link"}}]
