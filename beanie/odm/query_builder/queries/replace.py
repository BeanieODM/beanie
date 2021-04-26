from typing import Type, TYPE_CHECKING

from beanie.exceptions import DocumentNotFound

if TYPE_CHECKING:
    from beanie.odm.documents import Document


class ReplaceOne:
    def __init__(self, document_class: Type["Document"], filter_query=None):
        self.document_class = document_class
        self.filter_query = filter_query
        self.document_to_replace = None

    def replace_one(self, document: "Document"):
        self.document_to_replace = document
        return self

    def __await__(self):
        result = (
            yield from self.document_class.get_motor_collection().replace_one(
                self.filter_query,
                self.document_to_replace.dict(by_alias=True, exclude={"id"}),
            )
        )
        if not result.raw_result["updatedExisting"]:
            raise DocumentNotFound
        return result
