from beanie.odm_sync.views import View
from tests.odm_sync.models import SyncDocumentTestModel


class TestView(View):
    number: int
    string: str

    class Settings:
        view_name = "test_view"
        source = SyncDocumentTestModel
        pipeline = [
            {"$match": {"$expr": {"$gt": ["$test_int", 8]}}},
            {"$project": {"number": "$test_int", "string": "$test_str"}},
        ]
