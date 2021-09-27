from typing import TYPE_CHECKING

from beanie.odm.utils.encoder import bson_encoder

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def get_dict(document: "Document"):
    exclude = None if document.id is not None else {"id"}
    return bson_encoder.encode(document, by_alias=True, exclude=exclude)
