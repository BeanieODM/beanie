
import pytest
from pymongo.errors import DuplicateKeyError
from beanie.exceptions import RevisionIdWasChanged
from tests.odm.models import DocumentTestModelWithIndexFlags

async def test_update_duplicate_key_error(documents):
    # Create two documents
    doc1 = DocumentTestModelWithIndexFlags(test_int=1, test_str="unique_1")
    await doc1.insert()
    
    doc2 = DocumentTestModelWithIndexFlags(test_int=2, test_str="unique_2")
    await doc2.insert()
    
    # Try to update doc2 to have the same unique field as doc1
    doc2.test_str = "unique_1"
    
    # Expect DuplicateKeyError, NOT RevisionIdWasChanged
    with pytest.raises(DuplicateKeyError):
        await doc2.save()

async def test_replace_duplicate_key_error(documents):
    # Create two documents
    doc1 = DocumentTestModelWithIndexFlags(test_int=1, test_str="unique_1")
    await doc1.insert()
    
    doc2 = DocumentTestModelWithIndexFlags(test_int=2, test_str="unique_2")
    await doc2.insert()
    
    # Try to replace doc2 to have the same unique field as doc1
    doc2.test_str = "unique_1"
    
    # Expect DuplicateKeyError, NOT RevisionIdWasChanged
    with pytest.raises(DuplicateKeyError):
        await doc2.replace()
