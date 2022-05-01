from tests.odm.views import TestView


class TestViews:
    async def test_simple(self, documents):
        await documents(number=10)
        results = await TestView.all().to_list()
        assert results == 1
