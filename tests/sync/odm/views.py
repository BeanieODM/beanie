from beanie.sync.odm.views import View
from tests.sync.models import DocumentTestModel


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
