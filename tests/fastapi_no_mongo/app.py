from fastapi import FastAPI

from tests.fastapi_no_mongo.routes import house_router

app = FastAPI()

app.include_router(house_router, prefix="/v1", tags=["house"])
