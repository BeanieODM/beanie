import pytest

from beanie.odm.utils.dump import get_dict
from beanie.odm.utils.parsing import parse_obj
from tests.odm.models import SampleLazyParsing


@pytest.fixture
async def docs():
    for i in range(10):
        await SampleLazyParsing(i=i, s=str(i)).insert()


class TestLazyParsing:
    async def test_find_all(self, docs):
        found_docs = await SampleLazyParsing.all(lazy_parse=True).to_list()
        saved_state = found_docs[0].get_saved_state()
        assert "_id" in saved_state
        del saved_state["_id"]
        assert found_docs[0].get_saved_state() == {}
        assert found_docs[0].i == 0
        assert found_docs[0].s == "0"
        assert found_docs[1]._store["i"] == 1
        assert found_docs[1]._store["s"] == "1"
        assert get_dict(found_docs[2])["i"] == 2
        assert get_dict(found_docs[2])["s"] == "2"

    async def test_find_many(self, docs):
        found_docs = await SampleLazyParsing.find(
            SampleLazyParsing.i <= 5, lazy_parse=True
        ).to_list()
        saved_state = found_docs[0].get_saved_state()
        assert "_id" in saved_state
        del saved_state["_id"]
        assert found_docs[0].get_saved_state() == {}
        assert found_docs[0].i == 0
        assert found_docs[0].s == "0"
        assert found_docs[1]._store["i"] == 1
        assert found_docs[1]._store["s"] == "1"
        assert get_dict(found_docs[2])["i"] == 2
        assert get_dict(found_docs[2])["s"] == "2"

    async def test_save_changes(self, docs):
        found_docs = await SampleLazyParsing.all(lazy_parse=True).to_list()
        doc = found_docs[0]
        doc.i = 1000
        await doc.save_changes()
        new_doc = await SampleLazyParsing.find_one(SampleLazyParsing.s == "0")
        assert new_doc.i == 1000

    async def test_default_list(self):
        res = parse_obj(SampleLazyParsing, {"i": 1, "s": 1})
        assert res.lst == []
