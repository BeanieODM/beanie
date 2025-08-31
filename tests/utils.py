from functools import cache

from pymongo import MongoClient

from .conftest import Settings


@cache
def is_mongo_version_5_or_higher():
    settings = Settings()
    client = MongoClient(settings.mongodb_dsn)
    try:
        server_info = client.server_info()
        mongo_version = server_info["version"]
        major_version = int(mongo_version.split(".")[0])
        return major_version >= 5
    finally:
        client.close()
