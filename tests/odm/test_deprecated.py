import pytest

from beanie import init_beanie
from beanie.exceptions import Deprecation
from tests.odm.models import DocWithCollectionInnerClass


class TestDeprecations:
    async def test_doc_with_inner_collection_class_init(self, db):
        with pytest.raises(Deprecation):
            await init_beanie(
                database=db,
                document_models=[DocWithCollectionInnerClass],
            )
