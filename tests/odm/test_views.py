from tests.odm.views import TestView


class TestViews:
    async def test_simple(self, documents):
        await documents(number=15)
        results = await TestView.all().to_list()
        assert len(results) == 6

    async def test_aggregate(self, documents):
        await documents(number=15)
        results = await TestView.aggregate(
            [
                {"$set": {"test_field": 1}},
                {"$match": {"$expr": {"$lt": ["$number", 12]}}},
            ]
        ).to_list()
        assert len(results) == 3
        assert results[0]["test_field"] == 1
