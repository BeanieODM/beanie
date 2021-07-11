from typing import TYPE_CHECKING

from .encoder import bsonable_encoder

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def get_dict(document: "Document"):
    exclude = None if document.id is not None else {"id"}
    return bsonable_encoder(document, by_alias=True, exclude=exclude)
