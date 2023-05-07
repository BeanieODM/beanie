from fastapi import FastAPI

from tests.fastapi.routes import house_router

app = FastAPI()

app.include_router(house_router, prefix="/v1", tags=["house"])
