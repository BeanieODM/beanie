from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def get_dict(document: "Document"):
    exclude = None if document.id is not None else {"id"}
    return document.dict(by_alias=True, exclude=exclude)
