from abc import abstractmethod

from redis import Redis

from beanis.odm.settings.base import ItemSettings


class OtherGettersInterface:
    @classmethod
    @abstractmethod
    def get_settings(cls) -> ItemSettings:
        pass

    @classmethod
    def get_motor_collection(cls) -> Redis:
        return cls.get_settings().motor_db

    @classmethod
    def get_collection_name(cls):
        return cls.get_settings().name

    @classmethod
    def get_bson_encoders(cls):
        return cls.get_settings().bson_encoders

    @classmethod
    def get_link_fields(cls):
        return None
