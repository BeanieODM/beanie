from json import dumps

from fastapi.openapi.utils import get_openapi

from tests.fastapi.app import app


def test_openapi_schema_generation():
    openapi_schema_json_str = dumps(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ),
    )

    assert openapi_schema_json_str is not None
