from beanie.odm.utils.merge import merge_models
from tests.odm.models import (
    DocumentWithTurnedOnStateManagement,
    InternalDoc,
    DocumentWithTurnedOffStateManagement,
)


class TestUtils:
    def test_merge_same_models(self):
        left = DocumentWithTurnedOnStateManagement(
            num_1=1, num_2=2, internal=InternalDoc()
        )
        right = DocumentWithTurnedOnStateManagement(
            num_1=3, num_2=4, internal=InternalDoc()
        )
        left.internal.change_private()
        merge_models(left, right)
        assert left.num_1 == 3
        assert left.num_2 == 4
        assert left.internal._private_field == "PRIVATE_CHANGED"

    def test_merge_different_models(self):
        left = DocumentWithTurnedOnStateManagement(
            num_1=1, num_2=2, internal=InternalDoc()
        )
        right = DocumentWithTurnedOffStateManagement(
            num_1=3,
            num_2=4,
        )
        left.internal.change_private()
        merge_models(left, right)
        assert left.num_1 == 3
        assert left.num_2 == 4
        assert left.internal._private_field == "PRIVATE_CHANGED"

        left = DocumentWithTurnedOffStateManagement(num_1=1, num_2=2)
        right = DocumentWithTurnedOnStateManagement(
            num_1=3, num_2=4, internal=InternalDoc()
        )
        merge_models(left, right)
        assert left.num_1 == 3
        assert left.num_2 == 4
