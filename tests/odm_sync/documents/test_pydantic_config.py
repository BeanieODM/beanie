import pytest
from pydantic import ValidationError

from tests.odm_sync.models import SyncDocumentWithPydanticConfig


def test_pydantic_config():
    doc = SyncDocumentWithPydanticConfig(num_1=2)
    with pytest.raises(ValidationError):
        doc.num_1 = "wrong"
