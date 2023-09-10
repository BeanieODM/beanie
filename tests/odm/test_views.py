from tests.odm.views import ViewForTest, ViewForTestWithLink


class TestViews:
    async def test_simple(self, documents):
        await documents(number=15)
        results = await ViewForTest.all().to_list()
        assert len(results) == 6

    async def test_aggregate(self, documents):
        await documents(number=15)
        results = await ViewForTest.aggregate(
            [
                {"$set": {"test_field": 1}},
                {"$match": {"$expr": {"$lt": ["$number", 12]}}},
            ]
        ).to_list()
        assert len(results) == 3
        assert results[0]["test_field"] == 1

    async def test_link(self, documents_with_links):
        await documents_with_links()
        results = await ViewForTestWithLink.all().to_list()
        for document in results:
            await document.fetch_all_links()

        for i, document in enumerate(results):
            assert document.link.test_int == i
