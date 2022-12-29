from beanie.odm.settings.base import ItemSettings


class UnionDocSettings(ItemSettings):
    class_id: str = "_class_id"
    ...
