from typing import TYPE_CHECKING, Optional, Set

from beanie.odm.utils.encoder import Encoder

if TYPE_CHECKING:
    from beanie.odm.documents import Document


def get_dict(
    document: "Document",
    to_db: bool = False,
    exclude: Optional[Set[str]] = None,
):
    if exclude is None:
        exclude = set()
    if document.id is None:
        exclude.add("_id")
    if not document.get_settings().use_revision:
        exclude.add("revision_id")
    return Encoder(by_alias=True, exclude=exclude, to_db=to_db).encode(
        document
    )
