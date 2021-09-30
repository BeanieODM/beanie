from dataclasses import dataclass

from beanie.odm.settings.collection import CollectionSettings
from beanie.odm.settings.model import ModelSettings


@dataclass
class DocumentSettings:
    model_settings: ModelSettings
    collection_settings: CollectionSettings

    @classmethod
    async def init(cls, database, document_model, allow_index_dropping):
        # Init collection settings
        collection_settings = await CollectionSettings.init(
            database=database,
            document_model=document_model,
            allow_index_dropping=allow_index_dropping,
        )

        # Init model settings

        model_settings = ModelSettings.init(document_model=document_model)
        return cls(
            model_settings=model_settings,
            collection_settings=collection_settings,
        )
