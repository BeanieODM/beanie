from typing import TYPE_CHECKING

from beanie.odm.utils.encoder import bson_encoder

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def get_dict(document: "Document", to_db: bool = False):
    exclude = set()
    if document.id is None:
        exclude.add("_id")
    if not document.get_settings().model_settings.use_revision:
        exclude.add("revision_id")
    return bson_encoder.encode(
        document, by_alias=True, exclude=exclude, to_db=to_db
    )
