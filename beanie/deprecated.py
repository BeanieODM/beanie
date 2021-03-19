import warnings
from typing import Optional, Type


def get_collection_class_from_document_meta_class(cls) -> Optional[Type]:
    document_meta = getattr(cls, "DocumentMeta", None)
    if document_meta is not None:
        warnings.warn(
            "Class DocumentMeta is deprecated. "
            "It will not be supported after 0.4.0. "
            "Please use class Collection instead. "
            "https://roman-right.github.io/beanie/#collection-setup",
            category=DeprecationWarning,
        )
        collection_name = getattr(document_meta, "collection_name", None)
        if collection_name is not None:

            class Collection:
                name = collection_name

            return Collection
    return None
