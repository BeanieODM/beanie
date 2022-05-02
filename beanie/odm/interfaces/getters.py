from motor.motor_asyncio import AsyncIOMotorCollection

from beanie.odm.settings.base import ItemSettings


class OtherGettersInterface:
    @classmethod
    def get_settings(cls) -> ItemSettings:
        pass

    @classmethod
    def get_motor_collection(cls) -> AsyncIOMotorCollection:
        return cls.get_settings().motor_collection

    @classmethod
    def get_collection_name(cls):
        input_class = getattr(cls, "Settings", None)
        if input_class is None or not hasattr(input_class, "name"):
            return cls.__name__
        return input_class.name

    @classmethod
    def get_bson_encoders(cls):
        return cls.get_settings().bson_encoders

    @classmethod
    def get_link_fields(cls):
        return None
