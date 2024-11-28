from fastapi.openapi.utils import get_openapi

from tests.fastapi.app import app


def test_openapi_schema_generation():
    get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes,
    )
