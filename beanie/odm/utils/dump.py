from typing import TYPE_CHECKING

from beanie.odm.utils.encoder import bson_encoder

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def get_dict(document: "Document"):
    exclude = set()
    if document.id is None:
        exclude.add("id")
    if not document.get_settings().model_settings.use_revision:
        exclude.add("revision_id")
    return bson_encoder.encode(document, by_alias=True, exclude=exclude)
