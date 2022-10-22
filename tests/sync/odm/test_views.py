from tests.sync.odm.views import TestView


class TestViews:
    def test_simple(self, documents):
        documents(number=15)
        results = TestView.all().to_list()
        assert len(results) == 6

    def test_aggregate(self, documents):
        documents(number=15)
        results = TestView.aggregate(
            [
                {"$set": {"test_field": 1}},
                {"$match": {"$expr": {"$lt": ["$number", 12]}}},
            ]
        ).to_list()
        assert len(results) == 3
        assert results[0]["test_field"] == 1
