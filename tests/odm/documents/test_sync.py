import pytest

from beanie.exceptions import ApplyChangesException
from beanie.odm.documents import MergeStrategy
from tests.odm.models import DocumentToTestSync


class TestSync:
    async def test_merge_remote(self):
        doc = DocumentToTestSync()
        await doc.insert()

        doc2 = await DocumentToTestSync.get(doc.id)
        doc2.s = "foo"

        doc.i = 100
        await doc.save()

        await doc2.sync()

        assert doc2.s == "TEST"
        assert doc2.i == 100

    async def test_merge_local(self):
        doc = DocumentToTestSync(d={"option_1": {"s": "foo"}})
        await doc.insert()

        doc2 = await DocumentToTestSync.get(doc.id)
        doc2.s = "foo"
        doc2.n.option_1.s = "bar"
        doc2.d["option_1"]["s"] = "bar"

        doc.i = 100
        await doc.save()

        await doc2.sync(merge_strategy=MergeStrategy.local)

        assert doc2.s == "foo"
        assert doc2.n.option_1.s == "bar"
        assert doc2.d["option_1"]["s"] == "bar"

        assert doc2.i == 100

    async def test_merge_local_impossible_apply_changes(self):
        doc = DocumentToTestSync(d={"option_1": {"s": "foo"}})
        await doc.insert()

        doc2 = await DocumentToTestSync.get(doc.id)
        doc2.d["option_1"]["s"] = {"foo": "bar"}

        doc.d = {"option_1": "nothing"}
        await doc.save()
        with pytest.raises(ApplyChangesException):
            await doc2.sync(merge_strategy=MergeStrategy.local)
