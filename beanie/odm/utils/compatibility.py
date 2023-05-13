from beanie.odm.utils.general import DatabaseVersion


def supports_timeseries(database_version: DatabaseVersion) -> bool:
    return database_version.major >= 5


def supports_nested_links(database_version: DatabaseVersion) -> bool:
    return database_version.major > 4 or (
        database_version.major == 4 and database_version.minor >= 4
    )
